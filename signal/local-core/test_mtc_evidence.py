"""No external dependencies; no model/hardware required."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import mtc_evidence as mtc


class TestMtcEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.events = [
            {'seconds_from_start': 0, 'event': 'session_setup'},
            {'seconds_from_start': 1, 'event': 'question_cycle_start'},
            {'seconds_from_start': 2, 'event': 'question_start'},
            {'seconds_from_start': 3, 'event': 'question_end', 'completed': True},
            {'seconds_from_start': 4, 'event': 'response_window_end', 'completed': True},
            {'seconds_from_start': 5, 'event': 'question_cycle_end'},
            {'seconds_from_start': 6, 'event': 'session_finished', 'outcome': 'COMPLETE'},
        ]
        self.metadata = {'sample_rate': 100, 'version': 'test', 'session_id': 'test-001',
                         'questions': [{'filename': '01_question.wav'}]}
        self.write_fixture()

    def write_fixture(self):
        meta = json.dumps(self.metadata).encode()
        events = ('\n'.join(json.dumps(e) for e in self.events) + '\n').encode()
        result = {
            'outcome': 'COMPLETE', 'faults': [],
            'recording_segments': [
                {'start_frame': 0, 'frames': 1000},
                {'start_frame': 1000, 'frames': 500},
            ],
            'total_recording_frames': 1500,
            'primary_recording_info': {'frames': 1500, 'segments': 2, 'duration_seconds': 15},
            'metadata_sha256': hashlib.sha256(meta).hexdigest(),
            'events_sha256': hashlib.sha256(events).hexdigest(),
        }
        (self.folder / 'session_metadata.json').write_bytes(meta)
        (self.folder / 'events.jsonl').write_bytes(events)
        (self.folder / 'session_result.json').write_text(json.dumps(result), encoding='utf-8')

    def test_valid_log_package_is_read_only(self):
        before = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        data = mtc.read_session(self.folder)
        self.assertEqual(data['recorded_seconds'], 15)
        self.assertEqual(data['question_starts_logged'], 1)
        self.assertEqual(data['response_windows_completed_logged'], 1)
        self.assertTrue(all(data['file_integrity'].values()))
        self.assertIn('not WAV bytes', mtc.format_summary(data))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.folder.iterdir()})

    def test_tampered_log_is_blocked(self):
        with (self.folder / 'events.jsonl').open('ab') as f:
            f.write(b' ')
        with self.assertRaisesRegex(mtc.EvidenceError, 'SHA-256 mismatch'):
            mtc.read_session(self.folder)

    def test_backward_timestamps_are_blocked(self):
        self.events[3]['seconds_from_start'] = 1.5
        self.write_fixture()
        with self.assertRaisesRegex(mtc.EvidenceError, 'backward'):
            mtc.read_session(self.folder)

    def test_segment_gap_is_blocked(self):
        result = json.loads((self.folder / 'session_result.json').read_text())
        result['recording_segments'][1]['start_frame'] = 1001
        (self.folder / 'session_result.json').write_text(json.dumps(result))
        with self.assertRaisesRegex(mtc.EvidenceError, 'not contiguous'):
            mtc.read_session(self.folder)

    def test_falsified_finish_is_blocked(self):
        self.events[-1]['outcome'] = 'INTERRUPTED'
        self.write_fixture()
        with self.assertRaisesRegex(mtc.EvidenceError, 'disagrees'):
            mtc.read_session(self.folder)

    def test_missing_file_is_blocked(self):
        (self.folder / 'session_metadata.json').unlink()
        with self.assertRaisesRegex(mtc.EvidenceError, 'Missing'):
            mtc.read_session(self.folder)

    def test_large_file_is_blocked(self):
        (self.folder / 'events.jsonl').write_bytes(b'x' * (mtc.MAX_BYTES['events.jsonl'] + 1))
        with self.assertRaisesRegex(mtc.EvidenceError, 'size limit'):
            mtc.read_session(self.folder)

    def test_symlink_is_blocked_when_supported(self):
        original = self.folder / 'session_metadata.json'
        original.rename(self.folder / 'saved_metadata.json')
        try:
            original.symlink_to(self.folder / 'saved_metadata.json')
        except (OSError, NotImplementedError):
            self.skipTest('Symlink not available on this host')
        with self.assertRaisesRegex(mtc.EvidenceError, 'linked'):
            mtc.read_session(self.folder)


if __name__ == '__main__':
    unittest.main(verbosity=2)
