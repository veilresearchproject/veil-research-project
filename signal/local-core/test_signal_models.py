"""Model selection acceptance: real local HTTP, fake inventory, no Ollama/audio."""
import io
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib import request, error

import signal_core
import signal_desktop
import signal_models


class InventoryTests(unittest.TestCase):
    def inventory(self, data):
        response = io.BytesIO(json.dumps(data).encode())
        return signal_models.installed_models(lambda *a, **kw: response)

    def test_inventory_is_local_bounded_and_filters_remote_entries(self):
        opener = Mock(return_value=io.BytesIO(json.dumps({'models': [
            {'name': 'tiny:1b'}, {'name': 'tiny:1b'}, {'name': 'big:cloud'},
            {'name': 'alias:latest', 'remote_host': 'remote.example'},
            {'name': 'remote:latest', 'remote_model': 'remote'},
            {'name': '<script>'}, None]}).encode()))
        self.assertEqual(signal_models.installed_models(opener), ['tiny:1b'])
        self.assertEqual(opener.call_args.args[0].full_url, signal_models.TAGS_URL)
        self.assertEqual(opener.call_args.args[0].method, 'GET')

    def test_malformed_inventory_never_becomes_empty_success(self):
        for data in [None, [], {'models': None}, {'models': 'wrong'}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.inventory(data)

    def test_oversize_inventory_fails(self):
        with self.assertRaises(ValueError):
            signal_models.installed_models(lambda *a, **kw: io.BytesIO(b' ' * (signal_models.MAX_BYTES + 1)))


class SelectionHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.server, self.state = signal_desktop.make_server(signal_core.LocalModel('old:3b'))
        self.state.bot.memories = signal_core.Memories(self.temp.name)
        self.state.bot.voice = Mock(enabled=False, _process=None)
        self.state.bot.history = [{'role': 'user', 'content': 'old question'},
                                  {'role': 'assistant', 'content': 'old answer'}]
        self.state.bot.loaded_mtc = {'session_id': 'old'}
        self.state.bot.loaded_review = {'old': True}
        self.inventory = patch.object(signal_models, 'installed_models', return_value=['old:3b', 'tiny:1b'])
        self.probe = self.inventory.start()
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.worker.join(2)
        self.inventory.stop(); self.temp.cleanup()

    def call(self, payload=None, token=True, origin=None):
        headers = {'Content-Type': 'application/json'}
        if token: headers['X-SIGNAL-Token'] = self.state.token
        if origin: headers['Origin'] = origin
        req = request.Request(self.base + '/api/models', headers=headers,
                              data=None if payload is None else json.dumps(payload).encode())
        try:
            with request.urlopen(req, timeout=3) as resp: return resp.status, json.load(resp)
        except error.HTTPError as exc: return exc.code, json.load(exc)

    def test_list_is_read_only_and_token_required(self):
        self.assertEqual(self.call(token=False)[0], 403)
        self.probe.assert_not_called()
        code, data = self.call()
        self.assertEqual((code, data['selected']), (200, 'old:3b'))
        self.assertEqual(len(self.state.bot.history), 2)
        self.state.bot.voice.stop.assert_not_called()
        self.assertEqual(self.state.listener.status()['state'], 'idle')

    def test_confirmed_switch_resets_active_context_without_writing_files(self):
        sentinel = Path(self.temp.name) / 'source.wav'
        sentinel.write_bytes(b'original evidence bytes')
        code, data = self.call({'model': 'tiny:1b', 'confirm_reset': True})
        self.assertEqual((code, data['changed']), (200, True))
        self.assertEqual(self.state.bot.model.model, 'tiny:1b')
        self.assertEqual(self.state.bot.history, [])
        self.assertIsNone(self.state.bot.loaded_mtc)
        self.assertIsNone(self.state.bot.loaded_review)
        self.state.bot.voice.stop.assert_called_once()
        self.assertEqual(sentinel.read_bytes(), b'original evidence bytes')
        self.assertEqual(list(Path(self.temp.name).iterdir()), [sentinel])

    def test_invalid_missing_confirmation_and_uninstalled_preserve_context(self):
        for payload in [{'model': 'tiny:1b'}, {'model': 'tiny:1b', 'confirm_reset': 'true'},
                        {'model': 'missing:1b', 'confirm_reset': True},
                        {'model': '<script>', 'confirm_reset': True}]:
            with self.subTest(payload=payload):
                self.assertEqual(self.call(payload)[0], 422)
                self.assertEqual(self.state.bot.model.model, 'old:3b')
                self.assertEqual(len(self.state.bot.history), 2)
                self.assertIsNotNone(self.state.bot.loaded_mtc)
        self.state.bot.voice.stop.assert_not_called()

    def test_same_model_does_not_erase_chat(self):
        code, data = self.call({'model': 'old:3b'})
        self.assertEqual((code, data['changed']), (200, False))
        self.assertEqual(len(self.state.bot.history), 2)

    def test_busy_and_listening_cannot_change_model(self):
        with self.state.lock:
            self.assertEqual(self.call({'model': 'tiny:1b', 'confirm_reset': True})[0], 409)
            self.assertEqual(self.call()[0], 409)
        with patch.object(self.state.listener, 'status', return_value={'state': 'listening'}):
            self.assertEqual(self.call({'model': 'tiny:1b', 'confirm_reset': True})[0], 422)
        self.assertEqual(self.state.bot.model.model, 'old:3b')

    def test_demo_and_foreign_origin_cannot_probe_or_select(self):
        self.assertEqual(self.call(origin='https://unrelated.example')[0], 403)
        self.assertEqual(self.call({'model': 'tiny:1b', 'confirm_reset': True}, token=False)[0], 403)
        self.state.mode = 'demo'
        self.assertEqual(self.call()[0], 422)
        self.assertEqual(self.call({'model': 'tiny:1b', 'confirm_reset': True})[0], 422)
        self.probe.assert_not_called()

    def test_inventory_failure_preserves_current_session(self):
        self.probe.side_effect = ValueError('Ollama is offline')
        self.assertEqual(self.call({'model': 'tiny:1b', 'confirm_reset': True})[0], 422)
        self.assertEqual(self.state.bot.model.model, 'old:3b')
        self.assertEqual(len(self.state.bot.history), 2)


if __name__ == '__main__':
    unittest.main()
