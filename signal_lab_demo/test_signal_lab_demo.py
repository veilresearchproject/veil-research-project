import tempfile, unittest
from pathlib import Path
from signal_lab_demo import run,verify

class DemoTests(unittest.TestCase):
    def test_reproducible_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            m=run(p,60,42)
            self.assertEqual(m['dataset_type'],'SYNTHETIC_SIMULATION')
            self.assertEqual(len(m['flags']),2)
            original=(p/'synthetic_readings.csv').read_bytes()
            self.assertTrue(verify(p))
            run(p,60,42)
            self.assertEqual((p/'synthetic_readings.csv').read_bytes(),original)
            with (p/'synthetic_readings.csv').open('ab') as f: f.write(b'tamper')
            self.assertFalse(verify(p))
    def test_invalid_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):run(Path(tmp),0)
if __name__=='__main__':unittest.main()
