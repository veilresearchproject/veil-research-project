import unittest
from reveal_stage import RevealStage
from expression_controller import Mode

class StageTests(unittest.TestCase):
    def test_listening_to_thinking(self):
        s=RevealStage();s.begin_listening();self.assertEqual(s.face.mode,Mode.LISTENING)
        s.begin_thinking();self.assertEqual(s.face.mode,Mode.THINKING)
    def test_success_returns_idle(self):
        s=RevealStage()
        self.assertTrue(s.speak('Hello, Cristal.',lambda text: True))
        self.assertEqual(s.face.mode,Mode.IDLE)
    def test_speaking_state_during_callback(self):
        s=RevealStage()
        seen=[]
        self.assertTrue(s.speak('Good evening.',lambda _:seen.append(s.face.mode) or True))
        self.assertEqual(seen,[Mode.SPEAKING])
    def test_failure_returns_error_and_closed_mouth(self):
        s=RevealStage()
        def failed(_):
            s.speech_level(0.8)
            return False
        self.assertFalse(s.speak('Hello.',failed))
        self.assertEqual(s.face.mode,Mode.ERROR)
        self.assertEqual(s.face.snapshot().mouth_open,0)
    def test_exception_returns_error(self):
        s=RevealStage()
        self.assertFalse(s.speak('Hello.', lambda _: (_ for _ in ()).throw(RuntimeError('speaker error'))))
        self.assertEqual(s.face.mode,Mode.ERROR)
    def test_blocked_answer_never_spoken(self):
        s=RevealStage();spoken=[]
        with self.assertRaises(ValueError):
            s.speak('VEIL means Viral Epidemiology and Infection Lineage.',lambda t:spoken.append(t) or True)
        self.assertEqual(spoken,[])
        self.assertEqual(s.face.mode,Mode.ERROR)
    def test_empty_answer_is_idle(self):
        s=RevealStage()
        self.assertTrue(s.speak(' ',lambda _:False))
        self.assertEqual(s.face.mode,Mode.IDLE)

if __name__=='__main__': unittest.main()
