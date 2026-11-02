import unittest
from voice_queue import plan_speech

class QueueTests(unittest.TestCase):
    def test_long_answer_not_lost(self):
        text = ' '.join(['SIGNAL explains the evidence carefully.'] * 25)
        plan = plan_speech(text, 90)
        self.assertGreater(len(plan.chunks), 1)
        self.assertEqual(' '.join(plan.chunks), text)
    def test_completion_requires_all_chunks(self):
        plan = plan_speech('one two three four five six', 20)
        self.assertFalse(plan.verified_complete(0))
        self.assertFalse(plan.verified_complete(len(plan.chunks)-1))
        self.assertTrue(plan.verified_complete(len(plan.chunks)))
    def test_empty(self):
        self.assertEqual(plan_speech('  ').chunks, ())
    def test_unbreakable_word(self):
        with self.assertRaises(ValueError):
            plan_speech('a'*100, 30)
    def test_whitespace_normalized(self):
        plan = plan_speech('Hi\n  there.  How are you?', 20)
        self.assertEqual(' '.join(plan.chunks), 'Hi there. How are you?')
    def test_max_chars(self):
        plan = plan_speech('one two three four five six seven eight', 20)
        self.assertTrue(all(len(chunk) <= 20 for chunk in plan.chunks))

if __name__ == '__main__':
    unittest.main()
