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

    def test_invalid_marker_rejected(self):
        changed = MTC.replace(b'QUESTION_START', b'UNKNOWN_MARKER')
        with self.assertRaises(ValueError):
            s.inspect_synthetic(changed, 'mtc_markers')

    def test_empty_and_size_limit(self):
        for raw in (b'', b'a' * (s.MAX_BYTES + 1)):
            with self.assertRaises(ValueError):
                s.inspect_synthetic(raw, 'thermal')

    def test_bad_calendar_and_missing_timezone(self):
        for stamp in (b'2026-02-30T08:00:00Z', b'2026-10-22T08:00:00'):
            changed = THERMAL.replace(b'2026-10-22T08:00:00Z', stamp)
            with self.assertRaises(ValueError):
                s.inspect_synthetic(changed, 'thermal')

    def test_nonfinite_temperature(self):
        changed = THERMAL.replace(b'Room-A,21.0', b'Room-A,NaN')
        with self.assertRaises(ValueError):
            s.inspect_synthetic(changed, 'thermal')

    def test_fixed_csv_header(self):
        changed = THERMAL.replace(b'temperature_c', b'temperature_c,extra', 1)
        with self.assertRaises(ValueError):
            s.inspect_synthetic(changed, 'thermal')

    def test_bad_encoding(self):
        with self.assertRaises(ValueError):
            s.inspect_synthetic(bytes([255]), 'thermal')

if __name__ == '__main__':
    unittest.main(verbosity=2)
