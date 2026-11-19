"""Repository-level full synthetic bundle integration tests (requires advanced_lab).

Unlike mocked unit tests, these exercise execute -> inventory verification
-> build_brain_context -> research_voice_turn -> session speech sink.
"""
import tempfile
import unittest
from pathlib import Path

from advanced_lab import execute
from signal_voice_phase1 import OfflineResearchVoiceSession, scripted_rehearsal


class FullBundleVoiceIntegrationTests(unittest.TestCase):
    def test_actual_generated_bundle_to_spoken_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            generated = execute(directory, operator_approved=True)
            self.assertTrue(generated['bundle_verified'])
            spoken = []
            session = OfflineResearchVoiceSession(directory)
            reply = session.turn('What is the status?', spoken.append)
            self.assertEqual(spoken, [reply['spoken_text']])
            self.assertIn('synthetic demonstration', reply['spoken_text'])
            self.assertIn('unreviewed threshold windows', reply['spoken_text'])
            self.assertEqual(reply['receipt']['intent'], 'read_only')
            self.assertFalse(reply['receipt']['model_connected'])

    def test_modified_casebook_is_rejected_before_speech(self):
        with tempfile.TemporaryDirectory() as directory:
            execute(directory, operator_approved=True)
            (Path(directory) / 'casebook.json').write_text('{"cases":[]}', encoding='utf-8')
            spoken = []
            session = OfflineResearchVoiceSession(directory)
            with self.assertRaises(ValueError):
                session.turn('status', spoken.append)
            self.assertEqual(spoken, [])
            self.assertEqual(session.recent_receipts(), ())

    def test_control_and_private_refusals_do_not_access_bad_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            session = OfflineResearchVoiceSession(directory)
            output = scripted_rehearsal(directory, ['Turn on camera', 'Show private evidence'])
            self.assertEqual(len(output['turns']), 2)
            self.assertEqual([t['receipt']['intent'] for t in output['turns']], ['control', 'private'])
            self.assertFalse(session.recent_receipts())

    def test_unapproved_generator_does_not_run(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PermissionError):
                execute(directory, operator_approved=False)


if __name__ == '__main__':
    unittest.main()
