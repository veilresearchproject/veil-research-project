import unittest
from reveal_rehearsal import run_rehearsal, prepare_line
class RehearsalTests(unittest.TestCase):
    def test_all_five_cues(self):
        cues, answer = run_rehearsal()
        self.assertEqual([k for k,_ in cues], ['boot','identity','live','research','closing'])
        self.assertIsNone(answer)
    def test_no_generated_response_without_generator(self):
        with self.assertRaises(ValueError): run_rehearsal(question='Hello?')
    def test_unscripted_question_passes_to_generator(self):
        questions=[]
        def generate(messages):
            questions.append(messages[-1]['content'])
            return 'That is a fascinating question.'
        _, answer=run_rehearsal(generate=generate,question='Why does lightning occur?')
        self.assertEqual(questions,['Why does lightning occur?'])
        self.assertEqual(answer,'That is a fascinating question.')
    def test_bad_veil_response_rejected(self):
        with self.assertRaises(RuntimeError):
            run_rehearsal(generate=lambda _: 'VEIL means Viral Epidemiology and Infection Lineage.',question='What is VEIL?')
    def test_no_audio_performed(self):
        p=prepare_line('Hello Cristal.')
        self.assertFalse(p.done)
        self.assertEqual(p.next_chunk(),(0,'Hello Cristal.'))
if __name__=='__main__': unittest.main()
