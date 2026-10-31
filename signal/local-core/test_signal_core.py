import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
import signal_core as s


class Dummy:
    model = 'mock-model'
    def __init__(self):
        self.calls = []
    def answer(self, messages):
        self.calls.append(messages)
        return 'Test reply from simulated local model'


class TestSignal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem = s.Memories(Path(self.tmp.name))
        self.model = Dummy()
        self.bot = s.Assistant(self.model, self.mem)

    def tearDown(self):
        self.tmp.cleanup()

    def test_persona_instructions_remain_candid_and_evidence_first(self):
        context = self.bot._messages('Hi')[0]['content']
        self.assertIn('slightly eccentric scientist', context)
        self.assertIn('founder is Andrew', context)
        self.assertIn('Distinguish any theatrical character remarks', context)
        self.assertIn('cannot see, hear', context)
        self.assertIn('offsite human operator', context)
        self.assertIn('Never joke about safety', context)
        self.assertIn('not a finished autonomous system', context)
        self.assertIn('local time', context)
        self.assertFalse(self.mem.path.exists())

    def test_real_chat_bridge_has_model_call_not_scripted_reply(self):
        self.assertIn('simulated local model', self.bot.ask('What is an EVP?'))
        self.assertEqual(self.model.calls[0][-1]['content'], 'What is an EVP?')
        self.assertFalse(self.mem.path.exists())

    def test_recent_history_and_bound(self):
        for i in range(12):
            self.bot.ask('question ' + str(i))
        self.assertEqual(len(self.bot.history), 16)
        self.assertEqual(len(self.model.calls[-1]), 18)

    def test_explicit_memory_can_be_recalled_and_deleted(self):
        self.assertEqual(self.bot.action('/remember nickname = Drew'), 'Saved on this computer only.')
        self.assertEqual(self.mem.get()['nickname'], 'Drew')
        self.bot.ask('Recall my nickname')
        self.assertIn('Drew', self.model.calls[-1][0]['content'])
        self.assertEqual(self.bot.action('/forget nickname'), 'Removed')
        self.assertEqual(self.mem.get(), {})

    def test_invalid_memory_does_not_write(self):
        for key in ('../secret', '', 'x' * 41):
            with self.assertRaises(ValueError):
                self.mem.remember(key, 'x')
        with self.assertRaises(ValueError):
            self.mem.remember('name', 'x' * 501)
        self.assertFalse(self.mem.path.exists())

    def test_clear_retains_explicit_memories(self):
        self.mem.remember('role', 'researcher')
        self.bot.ask('Hello')
        self.bot.action('/clear')
        self.assertEqual(self.bot.history, [])
        self.assertEqual(self.mem.get()['role'], 'researcher')

    def test_no_remote_fallback(self):
        with patch.object(s.request, 'urlopen', side_effect=URLError('offline')) as urlopen:
            with self.assertRaisesRegex(RuntimeError, 'No cloud fallback'):
                s.LocalModel().answer([{'role':'user', 'content':'Hi'}])
        self.assertEqual(urlopen.call_args.args[0].full_url, s.LOCAL_URL)
        self.assertEqual(s.LOCAL_URL, 'http://127.0.0.1:11434/api/chat')

    def test_local_api_request_and_reply(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"message":{"content":"Hello from Ollama"}}'
        with patch.object(s.request, 'urlopen', return_value=Response()) as call:
            self.assertEqual(s.LocalModel().answer([]), 'Hello from Ollama')
        body = json.loads(call.call_args.args[0].data)
        self.assertFalse(body['stream'])
        self.assertEqual(body['model'], s.MODEL)

    def test_invalid_reply_and_long_prompt(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{}'
        with patch.object(s.request, 'urlopen', return_value=Response()):
            with self.assertRaisesRegex(RuntimeError, 'Unexpected'):
                s.LocalModel().answer([])
        with self.assertRaises(ValueError):
            self.bot.ask('a' * 4001)

    def test_lab_safety_and_command_allowlist(self):
        self.assertIn('offsite human operator', s.SYSTEM)
        self.assertIn('cannot see, hear', s.SYSTEM)
        self.assertIn('Unknown command', self.bot.action('/run-physical-device'))
        self.assertIn('no instruments', self.bot.action('/status'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
