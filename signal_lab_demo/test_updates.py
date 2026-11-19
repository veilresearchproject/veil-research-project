import tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from profile import Profile
from ingest import load
from correlate import windows
from provenance import verify_inventory
from review import record,read
from run_lab import run_v02
class UpdatesTest(unittest.TestCase):
    def test_01_profile(self):
        with self.assertRaises(ValueError):Profile('invalid',{'temperature_c':(1,2)})
    def test_02_import(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.csv';p.write_text('wrong,header\n1,2\n')
            with self.assertRaises(ValueError):load(p)
    def test_03_correlation(self):
        flags=[{'sample':1,'channel':'temperature_c'},{'sample':2,'channel':'sound_db'},{'sample':8,'channel':'sound_db'}]
        groups=windows(flags)
        self.assertEqual(len(groups),2)
        self.assertEqual(groups[0]['channels'],['sound_db','temperature_c'])
    def test_04_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);run_v02(p)
            self.assertTrue(verify_inventory(p))
            (p/'dashboard.html').write_text('tampered')
            self.assertFalse(verify_inventory(p))
    def test_05_review(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'reviews.jsonl'
            record(p,event_id='W-001',reviewer='Operator',decision='inconclusive',note='Test',when=datetime(2026,1,1,tzinfo=timezone.utc))
            self.assertEqual(read(p)[0]['decision'],'inconclusive')
            with self.assertRaises(ValueError):record(p,event_id='W-001',reviewer='Operator',decision='paranormal',note='')
    def test_06_dashboard(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);result=run_v02(p)
            self.assertEqual(result,{'samples':60,'flags':2,'windows':2,'inventory_entries':5})
            self.assertIn('SIMULATED DATA ONLY',(p/'dashboard.html').read_text())
            self.assertTrue(verify_inventory(p))
if __name__=='__main__':unittest.main()
