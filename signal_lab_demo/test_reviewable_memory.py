import os
import tempfile
import unittest
from reviewable_memory import ReviewableMemory

class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, 'memory.sqlite')
        self.mem = ReviewableMemory(self.path)
    def tearDown(self):
        self.mem.db.close()
        self.tmp.cleanup()
    def test_persistence(self):
        i = self.mem.add('Check microphone')
        self.mem.db.close()
        self.mem = ReviewableMemory(self.path)
        self.assertEqual(self.mem.list_notes()[0]['id'], i)
    def test_default_unverified(self):
        self.mem.add('A ghost spoke')
        self.assertEqual(self.mem.list_notes()[0]['status'], 'unverified')
    def test_review_history(self):
        i = self.mem.add('Operator observation')
        self.mem.review(i, 'Human reviewed source')
        self.assertEqual([h['action'] for h in self.mem.history(i)], ['created','reviewed'])
    def test_retraction_retains_history(self):
        i = self.mem.add('Wrong note')
        self.mem.review(i, 'Incorrect', retract=True)
        self.assertEqual(self.mem.list_notes(), [])
        self.assertEqual(self.mem.list_notes(True)[0]['status'], 'retracted')
    def test_reject_oversize(self):
        with self.assertRaises(ValueError): self.mem.add('a'*501)
    def test_reject_unknown_source(self):
        with self.assertRaises(ValueError): self.mem.add('x', 'web')
    def test_reject_control(self):
        with self.assertRaises(ValueError): self.mem.add('bad'+chr(0)+'text')
    def test_no_review_missing(self):
        with self.assertRaises(ValueError): self.mem.review(100, 'No such note')
    def test_no_reinstate_retracted(self):
        i=self.mem.add('x')
        self.mem.review(i,'wrong',retract=True)
        with self.assertRaises(ValueError): self.mem.review(i,'restore')

    def test_newest_100_are_visible_in_chronological_order(self):
        for i in range(115):
            self.mem.add(f'Note {i}')
        rows = self.mem.list_notes()
        self.assertEqual(len(rows), 100)
        self.assertEqual(rows[0]['text'], 'Note 15')
        self.assertEqual(rows[-1]['text'], 'Note 114')
    def test_retracted_notes_do_not_consume_active_window(self):
        ids = [self.mem.add(f'Note {i}') for i in range(105)]
        for note_id in ids[-8:]:
            self.mem.review(note_id, 'Withdrawn', retract=True)
        rows = self.mem.list_notes()
        self.assertEqual(len(rows), 97)
        self.assertEqual(rows[-1]['text'], 'Note 96')
        self.assertTrue(all(row['status'] != 'retracted' for row in rows))
    def test_recall_uses_newest_saved_notes(self):
        from memory_recall import recall_memory
        for i in range(108):
            self.mem.add(f'Note {i}')
        result = recall_memory('What notes do you remember?', self.mem, limit=3)
        self.assertEqual([row['text'] for row in result['notes']], ['Note 105', 'Note 106', 'Note 107'])
        self.assertNotIn('Note 107', result['spoken_text'])

if __name__ == '__main__': unittest.main()
