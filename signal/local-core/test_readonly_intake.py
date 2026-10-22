"""Run: python -m unittest -v test_readonly_intake.py"""
import hashlib
from pathlib import Path
import unittest
import synthetic_evidence as s

FIX = Path(__file__).parent / 'fixtures'
THERMAL = (FIX / 'synthetic_thermal.csv').read_bytes()
MTC = (FIX / 'synthetic_mtc_markers.csv').read_bytes()

class IntakeTests(unittest.TestCase):
    def test_thermal_expected_flags(self):
        a = s.inspect_synthetic(THERMAL, 'thermal')
        self.assertEqual(a['rows'], 8)
        self.assertEqual(a['temperature_step_flags'], 1)
        self.assertEqual(a['cadence_gaps'], 1)
        self.assertEqual(a['timestamp_order_issues'], 0)
        self.assertFalse(a['live_instrument_connection'])

    def test_mtc_metadata(self):
        a = s.inspect_synthetic(MTC, 'mtc_markers')
        self.assertEqual(a['rows'], 6)
        self.assertEqual(a['marker_counts']['RECORDING_START'], 2)
        self.assertFalse(a['model_inference'])

    def test_hash_verification(self):
        digest = hashlib.sha256(THERMAL).hexdigest()
        self.assertEqual(s.inspect_synthetic(THERMAL, 'thermal', expected_sha256=digest)['sha256'], digest)
        with self.assertRaises(ValueError):
            s.inspect_synthetic(THERMAL, 'thermal', expected_sha256='0' * 64)

    def test_unknown_schema(self):
        with self.assertRaises(ValueError):
            s.inspect_synthetic(THERMAL, 'unsupported')

    def test_timestamp_order(self):
        changed = THERMAL.replace(b'08:01:00Z,Room-A', b'08:00:00Z,Room-A')
        self.assertEqual(s.inspect_synthetic(changed, 'thermal')['timestamp_order_issues'], 1)

    def test_unchanged_inputs(self):
        before = hashlib.sha256(THERMAL).hexdigest()
        s.inspect_synthetic(THERMAL, 'thermal')
        self.assertEqual(before, hashlib.sha256(THERMAL).hexdigest())

if __name__ == '__main__':
    unittest.main(verbosity=2)
