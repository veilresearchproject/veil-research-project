import unittest
from live_conversation import LiveConversation

class LiveTests(unittest.TestCase):
    def test_unexpected_question_passed_to_generator(self):
        seen = []
        c = LiveConversation(lambda msgs: seen.append(msgs) or 'An unexpected but real response.')
        self.assertEqual(c.ask('Why does glass reflect light?'), 'An unexpected but real response.')
        self.assertEqual(seen[0][-1]['content'], 'Why does glass reflect light?')
    def test_followup_remembers(self):
        prompts = []
        c = LiveConversation(lambda m: prompts.append(m) or 'Answer')
        c.ask('What is MTC?'); c.ask('What did I just ask?')
        self.assertEqual(prompts[1][-3]['content'], 'What is MTC?')
    def test_invalid_question(self):
        with self.assertRaises(ValueError): LiveConversation(lambda m: 'x').ask('  ')
    def test_model_failure_does_not_pollute_history(self):
        c = LiveConversation(lambda m: '')
        with self.assertRaises(RuntimeError): c.ask('Hello')
        self.assertEqual(c.history, [])
    def test_wrong_veil_meaning_blocked(self):
        c = LiveConversation(lambda m: 'VEIL means Viral Epidemiology and Infection Lineage')
        with self.assertRaises(RuntimeError): c.ask('What is VEIL?')
        self.assertEqual(c.history, [])
    def test_reset(self):
        c = LiveConversation(lambda m: 'Hi')
        c.ask('Hello'); c.reset(); self.assertEqual(c.history, [])
    def test_context_bounded(self):
        saved = []
        c = LiveConversation(lambda m: saved.append(m) or 'Okay', max_turns=2)
        for i in range(5): c.ask(str(i))
        self.assertEqual([x['content'] for x in saved[-1] if x['role'] == 'user'], ['2', '3', '4'])

if __name__ == '__main__':
    unittest.main()
