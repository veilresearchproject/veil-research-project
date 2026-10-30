"""Concurrent loopback acceptance tests: stop controls never wait for generation."""
import json
import tempfile
import threading
import unittest
from unittest.mock import Mock
from urllib import request, error

import signal_core
import signal_desktop


class SlowModel:
    model = 'test:local'
    def __init__(self):
        self.entered = threading.Event()
        self.release = threading.Event()
        self.calls = 0
    def answer(self, messages):
        self.calls += 1
        self.entered.set()
        if not self.release.wait(5): raise RuntimeError('Test model was not released')
        return 'A controlled test response.'


class Voice:
    def __init__(self):
        self.enabled = True
        self._process = None
        self.stopped = 0
        self.spoken = []
    def stop(self): self.stopped += 1
    def disable(self): self.enabled = False; self.stop()
    def speak(self, text):
        if self.enabled: self.spoken.append(text)


class AudioControlHTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.model = SlowModel()
        self.server, self.state = signal_desktop.make_server(self.model)
        self.state.bot.memories = signal_core.Memories(self.tmp.name)
        self.state.bot.voice = Voice()
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.chat_worker = None

    def tearDown(self):
        self.model.release.set()
        if self.chat_worker: self.chat_worker.join(3)
        self.server.shutdown(); self.server.server_close(); self.worker.join(2)
        self.tmp.cleanup()

    def call(self, route, data, token=True, origin=None):
        headers = {'Content-Type': 'application/json'}
        if token: headers['X-SIGNAL-Token'] = self.state.token
        if origin: headers['Origin'] = origin
        req = request.Request(self.base + route, json.dumps(data).encode(), headers)
        try:
            with request.urlopen(req, timeout=3) as response:
                return response.status, json.load(response)
        except error.HTTPError as exc: return exc.code, json.load(exc)

    def start_chat(self):
        self.chat_result = []
        self.chat_worker = threading.Thread(target=lambda: self.chat_result.append(
            self.call('/api/chat', {'message': 'Please answer slowly'})), daemon=True)
        self.chat_worker.start()
        self.assertTrue(self.model.entered.wait(2))

    def test_speech_stop_returns_while_model_still_blocked(self):
        self.start_chat()
        code, result = self.call('/api/voice', {'action': 'stop'})
        self.assertEqual(code, 200)
        self.assertEqual(self.state.bot.voice.stopped, 1)
        self.assertTrue(self.chat_worker.is_alive())
        self.assertTrue(self.state.bot.voice.enabled)  # Stops current audio only.

    def test_disable_during_generation_suppresses_its_later_speech(self):
        self.start_chat()
        self.assertEqual(self.call('/api/voice', {'action': 'off'})[0], 200)
        self.assertFalse(self.state.bot.voice.enabled)
        self.model.release.set(); self.chat_worker.join(2)
        self.assertFalse(self.chat_worker.is_alive())
        self.assertEqual(self.chat_result[0][0], 200)
        self.assertEqual(self.state.bot.voice.spoken, [])
        self.assertEqual(len(self.state.bot.history), 2)

    def test_microphone_stop_works_while_model_lock_is_held(self):
        with self.state.lock:
            code, result = self.call('/api/listen', {'action': 'stop'})
        self.assertEqual((code, result['state']), (200, 'idle'))

    def test_stop_still_requires_authentication_and_same_origin(self):
        for route, action in [('/api/voice', 'stop'), ('/api/voice', 'off'), ('/api/listen', 'stop')]:
            with self.subTest(route=route, action=action):
                self.assertEqual(self.call(route, {'action': action}, token=False)[0], 403)
                self.assertEqual(self.call(route, {'action': action}, origin='https://foreign.example')[0], 403)
        self.assertEqual(self.state.bot.voice.stopped, 0)

    def test_start_and_test_actions_do_not_bypass_busy_lock(self):
        with self.state.lock:
            for route, action in [('/api/voice', 'on'), ('/api/voice', 'test'), ('/api/listen', 'start')]:
                self.assertEqual(self.call(route, {'action': action})[0], 409)

    def test_listening_blocks_chat_stream_and_test_speech(self):
        self.state.listener = Mock()
        self.state.listener.status.return_value = {'state': 'listening'}
        for route, payload in [('/api/chat', {'message': 'hello'}),
                               ('/api/chat/stream', {'message': 'hello'}),
                               ('/api/voice', {'action': 'test'})]:
            self.assertEqual(self.call(route, payload)[0], 422)
        self.assertEqual(self.model.calls, 0)
        self.assertEqual(self.state.bot.voice.spoken, [])

    def test_microphone_start_stops_speech_first(self):
        listener = Mock()
        def start():
            self.assertEqual(self.state.bot.voice.stopped, 1)
            return {'state': 'listening'}
        listener.start.side_effect = start
        self.state.listener = listener
        self.assertEqual(self.call('/api/listen', {'action': 'start'})[0], 200)
        listener.start.assert_called_once()


if __name__ == '__main__': unittest.main()
