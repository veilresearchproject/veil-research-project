"""Live request progress checks against blocked local test models, without hardware."""
import json
import tempfile
import threading
import unittest
from urllib import request, error
from unittest.mock import patch

import signal_core
import signal_desktop
import test_signal_audio_controls as audio_helpers


class RequestProgressTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.model = audio_helpers.SlowModel()
        self.server, self.state = signal_desktop.make_server(self.model)
        self.state.bot.memories = signal_core.Memories(self.tmp.name)
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.job = None

    def tearDown(self):
        self.model.release.set()
        if self.job: self.job.join(3)
        self.server.shutdown(); self.server.server_close(); self.worker.join(2)
        self.tmp.cleanup()

    def call(self, route, data=None, token=True):
        headers = {'Content-Type': 'application/json'}
        if token: headers['X-SIGNAL-Token'] = self.state.token
        req = request.Request(self.base + route, headers=headers,
                              data=json.dumps(data).encode() if data is not None else None)
        try:
            with request.urlopen(req, timeout=4) as response:
                body = response.read().decode()
                return response.status, json.loads(body) if 'ndjson' not in response.headers.get('Content-Type','') else body
        except error.HTTPError as exc: return exc.code, json.load(exc)

    def run_blocked(self, route, payload):
        self.result = []
        self.job = threading.Thread(target=lambda: self.result.append(self.call(route, payload)), daemon=True)
        self.job.start()
        self.assertTrue(self.model.entered.wait(2))

    def finish_and_status(self):
        self.model.release.set(); self.job.join(3)
        self.assertFalse(self.job.is_alive())
        # Wait for the request's finally block, not for an arbitrary sleep.
        self.assertTrue(self.state.lock.acquire(timeout=2))
        self.state.lock.release()
        return self.call('/api/status')[1]

    def test_nonstream_reply_exposes_busy_without_prompt_or_evidence(self):
        self.run_blocked('/api/chat', {'message': 'PRIVATE TEST QUESTION'})
        code, status = self.call('/api/status')
        self.assertEqual(code, 200)
        self.assertTrue(status['generating'])
        progress = status['request_progress']
        self.assertEqual(progress['kind'], 'reply')
        self.assertGreaterEqual(progress['elapsed_ms'], 0)
        self.assertFalse(progress['stop_requested'])
        self.assertNotIn('PRIVATE TEST QUESTION', json.dumps(status))
        self.assertEqual(self.call('/api/status', token=False)[0], 403)
        final = self.finish_and_status()
        self.assertFalse(final['generating']); self.assertIsNone(final['request_progress'])

    def test_model_check_reports_its_own_operation_kind(self):
        self.run_blocked('/api/model-check', {})
        progress = self.call('/api/status')[1]['request_progress']
        self.assertEqual(progress['kind'], 'model-check')
        self.assertFalse(self.finish_and_status()['generating'])
        self.assertEqual(self.state.bot.history, [])

    def test_stream_stop_stays_busy_until_reader_has_finished(self):
        def stream(messages):
            yield 'Partial'
            self.model.entered.set()
            if not self.model.release.wait(4): raise RuntimeError('Test was not released')
            yield 'never committed'
        self.model.stream_answer = stream
        self.run_blocked('/api/chat/stream', {'message': 'A test'})
        self.assertTrue(self.call('/api/chat/stop', {})[1]['stop_requested'])
        active = self.call('/api/status')[1]
        self.assertTrue(active['generating'])
        self.assertTrue(active['request_progress']['stop_requested'])
        final = self.finish_and_status()
        self.assertFalse(final['generating']); self.assertIsNone(final['request_progress'])
        self.assertEqual(self.state.bot.history, [])
        self.assertIn('stopped by operator', self.result[0][1])

    def test_error_clears_progress_and_preserves_history(self):
        def fail(messages): raise RuntimeError('Synthetic local failure')
        self.model.answer = fail
        self.assertEqual(self.call('/api/chat', {'message': 'fail'})[0], 422)
        with self.state.lock:
            status = self.state.status()
        self.assertFalse(status['generating']); self.assertIsNone(status['request_progress'])
        self.assertEqual(self.state.bot.history, [])

    def test_elapsed_is_monotonic_and_never_negative(self):
        with patch.object(signal_desktop.time, 'monotonic', side_effect=[10, 12.345, 9]):
            self.state.begin_model_operation('reply')
            self.assertEqual(self.state.operation_status()['elapsed_ms'], 2345)
            self.assertEqual(self.state.operation_status()['elapsed_ms'], 0)
        self.state.end_model_operation()
        self.assertIsNone(self.state.operation_status())

    def test_commands_and_invalid_requests_do_not_leave_busy_state(self):
        for payload in [{'message': '/status'}, {'message': ''}, {'message': 'x' * 4001}]:
            self.call('/api/chat', payload)
            with self.state.lock:
                self.assertIsNone(self.state.operation_status())
        self.assertEqual(self.model.calls, 0)


class ModelTimeoutTests(unittest.TestCase):
    def test_nonstream_timeout_has_specific_guidance_without_download_instruction(self):
        for exc in [TimeoutError(), error.URLError(TimeoutError())]:
            with self.subTest(exc=type(exc)), patch.object(signal_core.request, 'urlopen', side_effect=exc):
                with self.assertRaisesRegex(RuntimeError, 'timed out') as failure:
                    signal_core.LocalModel().answer([])
                self.assertIn('smaller installed model', str(failure.exception))
                self.assertNotIn('ollama pull', str(failure.exception))

    def test_stream_timeout_remains_an_incomplete_turn(self):
        with patch.object(signal_core.request, 'urlopen', side_effect=TimeoutError()):
            with self.assertRaisesRegex(RuntimeError, 'stream timed out'):
                list(signal_core.LocalModel().stream_answer([]))


if __name__ == '__main__': unittest.main()
