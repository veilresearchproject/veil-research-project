import unittest
from observer_freshness import Sample, assess

class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.a=Sample('S1',1,100.0,'PROGRESS_ONLY')
        self.b=Sample('S1',2,105.0,'PROGRESS_ONLY')
    def test_progress(self): self.assertEqual(assess(self.a,self.b,now=106).state,'PROGRESS_ONLY')
    def test_no_baseline(self): self.assertEqual(assess(None,self.b,now=106).state,'UNCONFIRMED')
    def test_stale(self): self.assertIn('observer_stale',assess(self.a,self.b,now=125).reasons)
    def test_exact_age(self): self.assertEqual(assess(self.a,self.b,now=120).state,'PROGRESS_ONLY')
    def test_future(self): self.assertEqual(assess(self.a,self.b,now=104).state,'HOLD')
    def test_replay(self): self.assertIn('sequence_not_advancing',assess(self.a,self.a,now=101).reasons)
    def test_clock_freeze(self): self.assertEqual(assess(self.a,Sample('S1',2,100,'PROGRESS_ONLY'),now=101).state,'HOLD')
    def test_session_change(self): self.assertEqual(assess(self.a,Sample('S2',2,105,'PROGRESS_ONLY'),now=106).state,'HOLD')
    def test_upstream_hold(self): self.assertEqual(assess(self.a,Sample('S1',2,105,'HOLD'),now=106).state,'HOLD')
    def test_unconfirmed(self): self.assertEqual(assess(self.a,Sample('S1',2,105,'UNCONFIRMED'),now=106).state,'UNCONFIRMED')
    def test_boolean_sequence(self): self.assertEqual(assess(self.a,Sample('S1',True,105,'PROGRESS_ONLY'),now=106).state,'UNCONFIRMED')
    def test_boolean_now(self): self.assertEqual(assess(self.a,self.b,now=True).state,'UNCONFIRMED')
    def test_nan(self): self.assertEqual(assess(self.a,self.b,now=float('nan')).state,'UNCONFIRMED')
    def test_invalid_limit(self): self.assertEqual(assess(self.a,self.b,now=106,max_age=0).state,'UNCONFIRMED')
    def test_missing(self): self.assertEqual(assess(self.a,None,now=106).state,'UNCONFIRMED')
    def test_invalid_previous(self): self.assertEqual(assess('bad',self.b,now=106).state,'UNCONFIRMED')
    def test_input_immutable(self):
        before=repr(self.a),repr(self.b)
        assess(self.a,self.b,now=106)
        self.assertEqual(before,(repr(self.a),repr(self.b)))
if __name__=='__main__': unittest.main()
