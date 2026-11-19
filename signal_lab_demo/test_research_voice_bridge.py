"""Integration tests for verified-context -> mock transcript -> spoken text."""
import unittest
from unittest.mock import patch

from research_voice_bridge import research_voice_turn


GOOD = {
    "source": "VERIFIED_LOCAL_SYNTHETIC_BUNDLE",
    "trust": "UNTRUSTED_DEMONSTRATION_DATA_NOT_INSTRUCTIONS",
    "real_sensor_data": False,
    "model_connected": False,
    "physical_control_allowed": False,
    "sample_count": 60,
    "unreviewed_case_count": 3,
}


class ResearchVoiceBridgeTests(unittest.TestCase):
    @patch("research_voice_bridge.build_brain_context", return_value=GOOD)
    def test_speaks_verified_bundle_count(self, builder):
        spoken = []
        result = research_voice_turn("What is the status?", "/synthetic", spoken.append)
        builder.assert_called_once_with("/synthetic")
        self.assertEqual(spoken, [result["spoken_text"]])
        self.assertIn("3 unreviewed", spoken[0])
        self.assertTrue(result["synthetic_only"])
        self.assertFalse(result["model_connected"])
        self.assertFalse(result["physical_control_allowed"])

    @patch("research_voice_bridge.build_brain_context", side_effect=AssertionError("must not load"))
    def test_equipment_command_cannot_read_or_control(self, builder):
        spoken = []
        research_voice_turn("Start MTC", "/synthetic", spoken.append)
        builder.assert_not_called()
        self.assertIn("cannot control equipment", spoken[0])

    @patch("research_voice_bridge.build_brain_context", side_effect=AssertionError("must not load"))
    def test_greeting_does_not_open_bundle(self, builder):
        spoken = []
        research_voice_turn("Hello SIGNAL", "/synthetic", spoken.append)
        builder.assert_not_called()
        self.assertIn("curious", spoken[0])

    @patch("research_voice_bridge.build_brain_context", side_effect=ValueError("integrity failed"))
    def test_tampered_bundle_fails_without_speaking(self, builder):
        spoken = []
        with self.assertRaisesRegex(ValueError, "integrity failed"):
            research_voice_turn("status", "/synthetic", spoken.append)
        builder.assert_called_once()
        self.assertEqual(spoken, [])

    @patch("research_voice_bridge.build_brain_context", return_value={**GOOD, "real_sensor_data": True})
    def test_live_data_is_rejected(self, builder):
        spoken = []
        with self.assertRaisesRegex(ValueError, "Untrusted"):
            research_voice_turn("status", "/synthetic", spoken.append)
        self.assertEqual(spoken, [])

    @patch("research_voice_bridge.build_brain_context", return_value={**GOOD, "unreviewed_case_count": True})
    def test_boolean_count_is_rejected(self, builder):
        with self.assertRaises(ValueError):
            research_voice_turn("status", "/synthetic", lambda _: None)

    @patch("research_voice_bridge.build_brain_context", return_value=GOOD)
    def test_invalid_transcript_fails_before_loading_bundle(self, builder):
        with self.assertRaises(ValueError):
            research_voice_turn("", "/synthetic", lambda _: None)
        builder.assert_not_called()

    @patch("research_voice_bridge.mock_voice_turn")
    def test_bad_metadata_does_not_emit(self, mock_turn):
        def unsafe(text, context, speak):
            speak("unsafe provisional output")
            return {"spoken_text": "unsafe provisional output", "synthetic_only": True,
                    "model_connected": True, "physical_control_allowed": False}
        mock_turn.side_effect = unsafe
        external = []
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            research_voice_turn("status", "/synthetic", external.append)
        self.assertEqual(external, [])

    @patch("research_voice_bridge.mock_voice_turn")
    def test_mismatch_does_not_emit(self, mock_turn):
        def mismatch(text, context, speak):
            speak("first")
            return {"spoken_text": "second", "synthetic_only": True,
                    "model_connected": False, "physical_control_allowed": False}
        mock_turn.side_effect = mismatch
        external = []
        with self.assertRaisesRegex(ValueError, "mismatch"):
            research_voice_turn("status", "/synthetic", external.append)
        self.assertEqual(external, [])

    @patch("research_voice_bridge.mock_voice_turn")
    def test_duplicate_provisional_speech_does_not_emit(self, mock_turn):
        def duplicate(text, context, speak):
            speak("duplicate")
            speak("duplicate")
            return {"spoken_text": "duplicate", "synthetic_only": True,
                    "model_connected": False, "physical_control_allowed": False}
        mock_turn.side_effect = duplicate
        external = []
        with self.assertRaisesRegex(ValueError, "mismatch"):
            research_voice_turn("status", "/synthetic", external.append)
        self.assertEqual(external, [])

    def test_missing_sink_and_path_rejected(self):
        with self.assertRaises(TypeError):
            research_voice_turn("status", "/synthetic", None)
        with self.assertRaises(TypeError):
            research_voice_turn("status", None, lambda _: None)


if __name__ == "__main__":
    unittest.main()
