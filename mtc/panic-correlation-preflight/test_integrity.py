"""Synthetic fixtures only; no live hardware, no human-subject evidence."""
from __future__ import annotations
import hashlib
import pathlib
import tempfile
import unittest

from correlation import InvalidEvent
from local_integrity import verify_and_correlate


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.payload = b"SYNTHETIC MTC example bytes only"
        self.sha = hashlib.sha256(self.payload).hexdigest()
        (self.root / "mtc.bin").write_bytes(self.payload)
        self.rows = [dict(event_id="MTC01", session_id="SESSION01", source_kind="MTC",
                          device_id="MIC01", source_file_sha256=self.sha,
                          recorded_at="2026-11-17T21:00:00Z", clock_offset_ms=0,
                          clock_uncertainty_ms=100, event_window_ms=100,
                          flag_type="SYNTHETIC_SOUND")]

    def run_case(self, originals=None, workspace=None):
        return verify_and_correlate(self.rows, workspace or self.root, originals or {self.sha: "mtc.bin"})

    def test_01_real_bytes_checked(self):
        out = self.run_case()
        self.assertEqual(out['file_integrity'][0]['sha256'], self.sha)
    def test_02_marked_metadata_unverified(self):
        self.assertIn('METADATA_UNVERIFIED', self.run_case()['status'])
    def test_03_does_not_approve_publication(self):
        self.assertFalse(self.run_case()['publication_approved'])
    def test_04_hash_mismatch_blocks(self):
        (self.root / 'mtc.bin').write_bytes(b"changed")
        with self.assertRaisesRegex(InvalidEvent, 'checksum mismatch'): self.run_case()
    def test_05_missing_file_blocks(self):
        with self.assertRaises(InvalidEvent): self.run_case({self.sha: 'absent.bin'})
    def test_06_relative_escape_blocks(self):
        with self.assertRaisesRegex(InvalidEvent, 'unsafe'): self.run_case({self.sha: '../private.bin'})
    def test_07_absolute_path_blocks(self):
        with self.assertRaisesRegex(InvalidEvent, 'unsafe'): self.run_case({self.sha: '/etc/passwd'})
    def test_08_symlink_source_blocks(self):
        (self.root / 'link.bin').symlink_to(self.root / 'mtc.bin')
        with self.assertRaisesRegex(InvalidEvent, 'symlink'): self.run_case({self.sha: 'link.bin'})
    def test_09_missing_mapping_blocks(self):
        with self.assertRaisesRegex(InvalidEvent, 'every source checksum'): verify_and_correlate(self.rows, self.root, {})
    def test_10_empty_file_blocks(self):
        (self.root / 'mtc.bin').write_bytes(b'')
        with self.assertRaises(InvalidEvent): self.run_case()
    def test_11_workspaces_must_exist(self):
        with self.assertRaises(InvalidEvent): self.run_case(workspace=self.root / 'missing')
    def test_12_same_file_not_two_different_hashes(self):
        other='f'*64
        self.rows.append({**self.rows[0], 'event_id':'BOX01','source_kind':'PANIC_BOX','device_id':'CAM01','source_file_sha256':other})
        with self.assertRaises(InvalidEvent): self.run_case({self.sha:'mtc.bin',other:'mtc.bin'})
    def test_13_multiple_distinct_files_supported(self):
        payload=b'SYNTHETIC PANIC BOX data'; sha=hashlib.sha256(payload).hexdigest()
        (self.root/'box.bin').write_bytes(payload)
        self.rows.append({**self.rows[0], 'event_id':'BOX01','source_kind':'PANIC_BOX','device_id':'CAM01','source_file_sha256':sha})
        out=self.run_case({self.sha:'mtc.bin',sha:'box.bin'})
        self.assertEqual(len(out['file_integrity']),2)
        self.assertEqual(len(out['pairs']),1)
    def test_14_unmeasured_clocks_still_do_not_correlate(self):
        self.rows[0]['clock_offset_ms']=None;self.rows[0]['clock_uncertainty_ms']=None
        payload=b'ANOTHER SYNTHETIC';sha=hashlib.sha256(payload).hexdigest();(self.root/'box.bin').write_bytes(payload)
        self.rows.append({**self.rows[0], 'event_id':'BOX01','source_kind':'PANIC_BOX','device_id':'CAM01','source_file_sha256':sha})
        out=self.run_case({self.sha:'mtc.bin',sha:'box.bin'})
        self.assertEqual(out['pairs'][0]['classification'],'CLOCK_DATA_MISSING')
    def test_15_invalid_timestamp_fails_before_read(self):
        self.rows[0]['recorded_at']='2026-11-17T21:00:00'
        with self.assertRaises(InvalidEvent): self.run_case()

if __name__=='__main__': unittest.main()
