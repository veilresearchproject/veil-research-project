"""Integration regression tests for SIGNAL Phase 1 guarded memory boundaries.
Offline only; no model, authentication provider, speech device or instrument invoked.
"""
import unittest
from guarded_memory_recall import guarded_recall


class FakeMemory:
    def __init__(self, notes):
        self.notes = notes
        self.reads = 0

    def list_notes(self, include_retracted=False):
        assert include_retracted is False
        self.reads += 1
        return self.notes


class Phase1IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.memory = FakeMemory([
            {'id': 1, 'status': 'unverified', 'source': 'operator', 'text': 'An orb is confirmed.'},
            {'id': 2, 'status': 'reviewed', 'source': 'operator', 'text': 'Camera clock differs by 2 seconds.'},
            {'id': 3, 'status': 'reviewed', 'source': 'synthetic_demo', 'text': 'SIMULATED event at 00:02.'},
        ])

    def test_voice_style_reply_never_contains_note_text(self):
        r = guarded_recall('What do you remember?', self.memory, consent=True,
                           authenticated=True, include_text=True)
        self.assertTrue(r['allowed'])
        self.assertEqual([n['id'] for n in r['notes']], [2, 3])
        for item in self.memory.notes:
            self.assertNotIn(item['text'], r['spoken_text'])
        self.assertIn('not verified scientific findings', r['spoken_text'])

    def test_no_access_does_not_query_storage(self):
        for flags in ({}, {'consent': True}, {'authenticated': True}):
            r = guarded_recall('recall', self.memory, **flags)
            self.assertFalse(r['allowed'])
        self.assertEqual(self.memory.reads, 0)

    def test_equipment_command_does_not_query_storage(self):
        r = guarded_recall('activate panic box and recall memory',
                           self.memory, consent=True, authenticated=True)
        self.assertFalse(r['allowed'])
        self.assertEqual(r['notes'], [])
        self.assertEqual(self.memory.reads, 0)

    def test_on_screen_text_requires_separate_opt_in(self):
        r = guarded_recall('notes', self.memory, consent=True, authenticated=True)
        self.assertTrue(r['allowed'])
        self.assertTrue(all('text' not in n for n in r['notes']))

    def test_unrelated_conversation_no_memory_access(self):
        r = guarded_recall('Hello SIGNAL, how are your circuits?',
                           self.memory, consent=True, authenticated=True)
        self.assertFalse(r['handled'])
        self.assertEqual(self.memory.reads, 0)


if __name__ == '__main__':
    unittest.main()
