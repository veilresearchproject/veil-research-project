import unittest
from hardware_triage import evaluate

class TriageTests(unittest.TestCase):
    def test_qualified(self):
        r = evaluate({'ram_gb':32, 'free_storage_gb':200, 'logical_cores':12})
        self.assertTrue(all(v['status']=='candidate_for_testing' for v in r.values()))
    def test_mini_only(self):
        r = evaluate({'ram_gb':8, 'free_storage_gb':80, 'logical_cores':4})
        self.assertEqual(r['mini_mtc']['status'],'candidate_for_testing')
        self.assertEqual(r['signal_desktop_cpu']['status'],'insufficient')
    def test_unknown(self):
        self.assertEqual(evaluate({})['mini_mtc']['status'],'needs_more_info')
    def test_bad_input(self):
        with self.assertRaises(ValueError):
            evaluate({'ram_gb':-1})

if __name__=='__main__': unittest.main()
