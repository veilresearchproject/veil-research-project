"""Regression checks for opt-in MTC log injection into SIGNAL local chat."""
import tempfile
import unittest
from pathlib import Path

import signal_core as core
import test_mtc_evidence


class FakeModel:
    model = 'mock-local-model'
    def __init__(self): self.calls = []
    def answer(self, messages):
        self.calls.append(messages)
        return 'Mock local reply (no internet or Ollama call)'


class TestSignalMtcIntegration(unittest.TestCase):
    def setUp(self):
        self.fixture = test_mtc_evidence.TestMtcEvidence()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.model = FakeModel()
        self.bot = core.Assistant(self.model, core.Memories(Path(self.tmp.name)))

    def test_log_read_then_available_to_local_model(self):
        self.assertIn('not loaded', self.bot.action('/status'))
        summary = self.bot.action('/mtc "' + str(self.fixture.folder) + '"')
        self.assertIn('15.0 seconds', summary)
        self.assertIn('loaded', self.bot.action('/status'))
        self.bot.ask('Did the session complete?')
        system_message = self.model.calls[-1][0]['content']
        self.assertIn('question starts/finished', system_message.lower())
        self.assertIn('not audio', system_message)
        self.assertNotIn(str(self.fixture.folder), system_message)

    def test_clear_removes_log_evidence_but_not_memory(self):
        self.bot.action('/remember role = investigator')
        self.bot.action('/mtc ' + str(self.fixture.folder))
        self.bot.action('/clear')
        self.bot.ask('What evidence do you have?')
        self.assertNotIn('READ-ONLY MTC SOFTWARE LOGS', self.model.calls[-1][0]['content'])
        self.assertIn('investigator', self.model.calls[-1][0]['content'])

    def test_bad_logs_are_not_silently_accepted(self):
        self.bot.action('/mtc ' + str(self.fixture.folder))
        (self.fixture.folder / 'events.jsonl').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            self.bot.action('/mtc ' + str(self.fixture.folder))
        self.assertIsNotNone(self.bot.loaded_mtc)
        self.assertIn('cleared', self.bot.action('/mtc-clear'))
        self.assertIsNone(self.bot.loaded_mtc)


if __name__ == '__main__':
    unittest.main(verbosity=2)
