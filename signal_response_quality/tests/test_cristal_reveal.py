import unittest
from cristal_reveal import CUES, cue_by_key, verify_cues
from voice_pipeline import VoicePipeline

class RevealTests(unittest.TestCase):
    def test_cue_integrity(self):
        self.assertEqual(verify_cues(), ())
    def test_cues_fit_voice_validation(self):
        for cue in CUES:
            with self.subTest(cue=cue.key):
                self.assertTrue(VoicePipeline(cue.spoken).plan.chunks)
    def test_live_exchange_not_prewritten(self):
        self.assertIn("ask a spontaneous question", cue_by_key("live").operator_note)
    def test_demo_does_not_claim_real_data(self):
        self.assertIn("SAMPLE", cue_by_key("research").operator_note)
    def test_identity_is_project_specific(self):
        self.assertIn("VEIL Research Project", cue_by_key("identity").spoken)
    def test_keys_are_ordered(self):
        self.assertEqual([c.key for c in CUES], ["boot","identity","live","research","closing"])

if __name__ == "__main__":
    unittest.main()
