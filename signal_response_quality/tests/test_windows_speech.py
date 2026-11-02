import unittest
from unittest.mock import Mock, patch
from windows_speech import speak_windows_blocking

class WindowsSpeechTests(unittest.TestCase):
    def test_synchronous_call(self):
        speaker = Mock()
        self.assertTrue(speak_windows_blocking('Hello SIGNAL', speaker_factory=lambda: speaker))
        speaker.Speak.assert_called_once_with('Hello SIGNAL', 0)
    def test_empty_rejected(self):
        factory = Mock()
        self.assertFalse(speak_windows_blocking('  ', speaker_factory=factory))
        factory.assert_not_called()
    def test_error_propagates(self):
        speaker = Mock()
        speaker.Speak.side_effect = RuntimeError('engine not ready')
        with self.assertRaises(RuntimeError):
            speak_windows_blocking('Hello', speaker_factory=lambda: speaker)
    def test_factory_error_propagates(self):
        def broken():
            raise OSError('SAPI unavailable')
        with self.assertRaises(OSError):
            speak_windows_blocking('Hello', speaker_factory=broken)
    def test_non_windows_without_factory(self):
        with patch('windows_speech.sys.platform', 'linux'):
            with self.assertRaises(RuntimeError):
                speak_windows_blocking('hello')

if __name__ == '__main__':
    unittest.main()
