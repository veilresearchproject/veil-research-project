"""Synthetic standalone runner checks; v0.3 verifier is mocked for isolated tests."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from run_v04 import run, FIELDNAMES


class SyntheticRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source = root / 'v03'
        self.source.mkdir()
        self.destination = root / 'v04'
        with (self.source / 'synthetic_readings.csv').open('w', newline='', encoding='utf8') as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()
            for i in range(12):
                w.writerow(dict(sample=i, timestamp_utc=f'2026-01-01T00:{i:02d}:00+00:00',
                                temperature_c=30 if i == 7 else 21, humidity_pct=45,
                                sound_db=75 if i == 3 else 35))
        digest = hashlib.sha256((self.source/'synthetic_readings.csv').read_bytes()).hexdigest()
        (self.source/'manifest.json').write_text(json.dumps(dict(dataset_type='SYNTHETIC_SIMULATION',
            real_sensor_data=False, source_sha256=digest, samples=12)), encoding='utf8')
        self.fake_advanced = types.ModuleType('advanced_lab')
        self.fake_advanced.verify_full_bundle = lambda directory: True

    def call_run(self):
        with patch.dict(sys.modules, {'advanced_lab':self.fake_advanced}):
            return run(self.source, self.destination)

    def test_runner_end_to_end_synthetic(self):
        result = self.call_run()
        self.assertTrue(result['simulated_only'])
        self.assertEqual(result['flagged'],2)
        self.assertEqual(len(list(self.destination.iterdir())),5)
        text=(self.destination/'v04_readout.html').read_text(encoding='utf8')
        self.assertIn('SIMULATED ONLY',text)
        self.assertIn('No source audio',text)
        blind=(self.destination/'reviewer_packet_SYNTHETIC.json').read_text(encoding='utf8')
        self.assertNotIn('2026-',blind)
        self.assertNotIn('SIMULATOR_01',blind)

    def test_refuses_non_simulated_data(self):
        manifest=json.loads((self.source/'manifest.json').read_text())
        manifest['dataset_type']='REAL'
        (self.source/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'synthetic'):
            self.call_run()

    def test_detects_original_file_modification(self):
        with (self.source/'synthetic_readings.csv').open('a') as f:
            f.write('tampered\n')
        with self.assertRaisesRegex(ValueError,'differs'):
            self.call_run()

    def test_refuses_overwrite(self):
        self.call_run()
        with self.assertRaises(FileExistsError):
            self.call_run()

    def test_requires_v03_verification(self):
        self.fake_advanced.verify_full_bundle = lambda directory: False
        with self.assertRaisesRegex(ValueError,'integrity'):
            self.call_run()


if __name__ == '__main__': unittest.main(verbosity=2)