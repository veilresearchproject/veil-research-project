import unittest
from expression_controller import ExpressionController, Mode
from audio_expression import AudioExpressionDriver

class AudioExpressionTests(unittest.TestCase):
    def setUp(self):
        self.face = ExpressionController()
        self.driver = AudioExpressionDriver(self.face)
    def test_silence_mouth_closed(self):
        self.face.set_mode(Mode.SPEAKING)
        self.assertEqual(self.driver.feed_pcm([0.0] * 16), 0.0)
    def test_real_samples_move_mouth(self):
        self.face.set_mode(Mode.SPEAKING)
        self.assertGreater(self.driver.feed_pcm([0.5, -0.5] * 8), 0)
    def test_no_movement_while_listening(self):
        self.face.set_mode(Mode.LISTENING)
        self.assertEqual(self.driver.feed_pcm([0.5] * 8), 0)
    def test_release_smoothly(self):
        self.face.set_mode(Mode.SPEAKING)
        loud = self.driver.feed_pcm([1.0] * 8)
        quiet = self.driver.feed_pcm([0] * 8)
        self.assertLess(quiet, loud)
        self.assertGreater(quiet, 0)
    def test_stop_closes_mouth(self):
        self.face.set_mode(Mode.SPEAKING)
        self.driver.feed_pcm([0.5] * 8)
        self.driver.stop()
        self.assertEqual(self.face.snapshot().mouth_open, 0)
    def test_reject_invalid_pcm(self):
        self.face.set_mode(Mode.SPEAKING)
        for frame in ([], [float('nan')], [2], ['x']):
            with self.assertRaises(ValueError): self.driver.feed_pcm(frame)
    def test_invalid_settings(self):
        with self.assertRaises(ValueError): AudioExpressionDriver(self.face, attack=-1)
    def test_noise_floor(self):
        self.face.set_mode(Mode.SPEAKING)
        self.assertEqual(self.driver.feed_pcm([0.01] * 8), 0)

if __name__ == '__main__': unittest.main()
