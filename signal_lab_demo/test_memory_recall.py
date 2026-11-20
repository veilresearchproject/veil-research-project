import unittest
from memory_recall import recall_memory

class Memory:
    def __init__(self, rows): self.rows = rows; self.calls = 0
    def list_notes(self, include_retracted=False):
        self.calls += 1
        assert include_retracted is False
        return self.rows

def note(i, status='unverified'):
    return {'id':i,'text':'Check MTC microphone','source':'operator','status':status}

class RecallTests(unittest.TestCase):
    def test_recall(self):
        m=Memory([note(1),note(2,'reviewed')])
        result=recall_memory('What do you remember?',m)
        self.assertEqual(len(result['notes']),2)
        self.assertIn('not verified scientific findings',result['spoken_text'])
    def test_no_memory(self):
        self.assertIn('no active notes',recall_memory('my notes',Memory([]))['spoken_text'])
    def test_not_recall(self):
        m=Memory([note(1)])
        self.assertFalse(recall_memory('hello',m)['handled'])
        self.assertEqual(m.calls,0)
    def test_no_mutation(self):
        m=Memory([note(1)])
        self.assertEqual(recall_memory('delete memory',m)['notes'],[])
        self.assertEqual(m.calls,0)
    def test_limit(self):
        self.assertEqual([n['id'] for n in recall_memory('notes',Memory([note(i) for i in range(8)]),3)['notes']],[5,6,7])
    def test_bad_limit(self):
        for limit in (0,11,True,1.2):
            with self.assertRaises(ValueError): recall_memory('notes',Memory([]),limit)
    def test_bad_query(self):
        for q in ('','a'*241,'notes\x00',None):
            with self.assertRaises(ValueError): recall_memory(q,Memory([]))
    def test_bad_record(self):
        with self.assertRaises(ValueError): recall_memory('notes',Memory([note(1,'retracted')]))
    def test_bad_provider(self):
        class Bad:
            def list_notes(self,include_retracted=False): return 'oops'
        with self.assertRaises(ValueError): recall_memory('notes',Bad())
    def test_no_automatic_speech_of_note_text(self):
        r=recall_memory('notes',Memory([{'id':1,'text':'sensitive note','source':'operator','status':'unverified'}]))
        self.assertNotIn('sensitive note',r['spoken_text'])

if __name__ == '__main__': unittest.main()
