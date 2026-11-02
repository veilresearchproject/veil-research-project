import unittest
from voice_pipeline import VoicePipeline

class PipelineTests(unittest.TestCase):
    def test_complete_in_order(self):
        p = VoicePipeline('one two three four five six seven eight nine ten', 20)
        self.assertFalse(p.done)
        seen = []
        while p.next_chunk() is not None:
            i, text = p.next_chunk()
            seen.append(text)
            p.confirm_played(i)
        self.assertTrue(p.done)
        self.assertEqual(' '.join(seen), p.plan.original)

    def test_bad_veil_claim_blocked(self):
        with self.assertRaises(ValueError):
            VoicePipeline('VEIL means Viral Epidemiology and Infection Lineage.')

    def test_screen_deferral_blocked(self):
        with self.assertRaises(ValueError):
            VoicePipeline('The rest is on the screen.')

    def test_failure_and_retry(self):
        p = VoicePipeline('one two three four five six seven eight', 20)
        i, first = p.next_chunk()
        p.fail_chunk(i)
        self.assertIsNone(p.next_chunk())
        self.assertFalse(p.done)
        self.assertEqual(p.retry_failed(), i)
        self.assertEqual(p.next_chunk(), (i, first))
        p.confirm_played(i)
        while p.next_chunk() is not None:
            j, _ = p.next_chunk()
            p.confirm_played(j)
        self.assertTrue(p.done)

    def test_empty_answer(self):
        p = VoicePipeline('   ')
        self.assertTrue(p.done)
        self.assertIsNone(p.next_chunk())
        with self.assertRaises(ValueError):
            p.confirm_played(0)

    def test_cannot_confirm_out_of_order(self):
        p = VoicePipeline('one two three four five six', 20)
        with self.assertRaises(ValueError):
            p.confirm_played(1)

if __name__ == '__main__':
    unittest.main()
