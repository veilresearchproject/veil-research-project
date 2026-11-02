"""Integration tests for SIGNAL's dependency-free voice components."""
import unittest
from voice_pipeline import VoicePipeline
from playback_adapter import play_remaining

class IntegrationTests(unittest.TestCase):
    def test_long_answer_no_text_lost(self):
        p = VoicePipeline(' '.join(['SIGNAL checks the sensors.'] * 60), max_chars=70)
        heard = []
        result = play_remaining(p, lambda s: heard.append(s) or True)
        self.assertTrue(result.completed)
        self.assertEqual(' '.join(heard), p.plan.original)
        self.assertGreater(result.played_now, 1)

    def test_failure_retry_does_not_replay_confirmed_sections(self):
        p = VoicePipeline(' '.join(['Data needs independent verification.'] * 18), max_chars=60)
        heard, attempts = [], [0]
        def speaker(s):
            attempts[0] += 1
            if attempts[0] == 3:
                return False
            heard.append(s)
            return True
        first = play_remaining(p, speaker)
        self.assertFalse(first.completed)
        self.assertEqual(first.failed_index, 2)
        self.assertEqual(p.tracker.completed_chunks, 2)
        self.assertEqual(play_remaining(p, lambda s: True).error, 'playback_paused')
        p.retry_failed()
        after = play_remaining(p, lambda s: heard.append(s) or True)
        self.assertTrue(after.completed)
        self.assertEqual(' '.join(heard), p.plan.original)

    def test_known_false_veil_identity_rejected(self):
        with self.assertRaises(ValueError):
            VoicePipeline('VEIL stands for Viral Epidemiology and Infection Lineage.')

    def test_queue_acceptance_is_not_audio_confirmation(self):
        p = VoicePipeline('This answer must be fully spoken.')
        self.assertFalse(play_remaining(p, lambda s: None).completed)

    def test_empty_answer(self):
        p = VoicePipeline('')
        self.assertTrue(play_remaining(p, lambda s: True).completed)

if __name__ == '__main__':
    unittest.main()
