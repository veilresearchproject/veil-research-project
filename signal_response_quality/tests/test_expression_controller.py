import unittest
from expression_controller import ExpressionController, Mode

class Tests(unittest.TestCase):
    def test_initial_idle(self):
        c=ExpressionController(); self.assertEqual(c.snapshot().mode, Mode.IDLE)
    def test_speech_level_opens_mouth(self):
        c=ExpressionController(); c.set_mode(Mode.SPEAKING); c.update_speech_level(1); self.assertEqual(c.snapshot().mouth_open, .85)
    def test_not_talking_doesnt_move_mouth(self):
        c=ExpressionController(); c.set_mode(Mode.LISTENING); c.update_speech_level(1); self.assertEqual(c.snapshot().mouth_open, 0)
    def test_transition_closes_mouth(self):
        c=ExpressionController(); c.set_mode(Mode.SPEAKING); c.update_speech_level(.8); c.set_mode(Mode.THINKING); self.assertEqual(c.snapshot().mouth_open,0)
    def test_bad_level_rejected(self):
        c=ExpressionController(); c.set_mode(Mode.SPEAKING)
        for val in (-1,2,float('nan')):
            with self.assertRaises(ValueError):c.update_speech_level(val)
    def test_bad_mode_rejected(self):
        with self.assertRaises(ValueError):ExpressionController().set_mode('speaking')
    def test_error_expression(self):
        c=ExpressionController(); c.set_mode(Mode.ERROR); self.assertFalse(c.snapshot().blink_allowed)
if __name__=='__main__':unittest.main()
