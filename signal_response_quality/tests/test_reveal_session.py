import unittest
from reveal_session import RevealSession
from expression_controller import Mode

class RevealSessionTests(unittest.TestCase):
    def test_end_to_end(self):
        spoken=[]
        s=RevealSession(lambda m:'What an excellent question, Cristal!', lambda txt:spoken.append(txt) or True)
        result=s.ask('Why the messy hair?')
        self.assertTrue(result.spoken)
        self.assertEqual(' '.join(spoken),result.answer)
        self.assertEqual(s.stage.face.mode,Mode.IDLE)
    def test_followup_context(self):
        messages=[]
        def model(m):messages.append(m);return 'Of course.'
        s=RevealSession(model,lambda _:True)
        s.ask('Question one');s.ask('And what about that?')
        self.assertEqual(messages[1][-3]['content'],'Question one')
    def test_model_failure(self):
        s=RevealSession(lambda m:'',lambda _:True)
        r=s.ask('Hi')
        self.assertFalse(r.spoken)
        self.assertEqual(s.stage.face.mode,Mode.ERROR)
    def test_audio_failure(self):
        s=RevealSession(lambda m:'Hello.',lambda _:False)
        r=s.ask('Hi')
        self.assertEqual(r.answer,'Hello.')
        self.assertEqual(r.status,'playback_failed')
        self.assertEqual(s.stage.face.mode,Mode.ERROR)
    def test_bad_identity_never_spoken(self):
        heard=[]
        s=RevealSession(lambda m:'VEIL means Viral Epidemiology and Infection Lineage.',lambda t:heard.append(t) or True)
        self.assertFalse(s.ask('What is VEIL?').spoken)
        self.assertFalse(heard)
    def test_exception_in_speaker(self):
        def speaker(t):raise OSError('offline device')
        s=RevealSession(lambda m:'Hello.',speaker)
        self.assertEqual(s.ask('Hi').status,'playback_failed')
    def test_blank_question(self):
        s=RevealSession(lambda m:'Hello.',lambda _:True)
        self.assertEqual(s.ask(' ').status,'ValueError')
if __name__=='__main__':unittest.main()
