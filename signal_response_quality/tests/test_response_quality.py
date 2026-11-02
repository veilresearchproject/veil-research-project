import unittest
from response_quality import VEIL_IDENTITY, check_answer

class ResponseQualityTests(unittest.TestCase):
    def test_correct_identity(self):
        self.assertTrue(check_answer(VEIL_IDENTITY).acceptable)
    def test_false_identity(self):
        self.assertIn("incorrect_veil_identity", check_answer("VEIL means Viral Epidemiology and Infection Lineage.").flags)
    def test_screen_deferral(self):
        self.assertIn("spoken_reply_deferral", check_answer("The rest is on the screen.").flags)
    def test_incomplete_playback(self):
        self.assertIn("speech_playback_incomplete", check_answer("Hello", speech_complete=False).flags)
    def test_speech_mismatch(self):
        self.assertIn("spoken_text_mismatch", check_answer("Hello world", spoken_text="Hello").flags)
    def test_matching_spoken_text(self):
        self.assertTrue(check_answer("Hello, world!", spoken_text="Hello world", speech_complete=True).acceptable)
    def test_no_false_promise_for_unchecked_audio(self):
        self.assertTrue(check_answer("Long response", speech_complete=None).acceptable)

if __name__ == "__main__":
    unittest.main()
