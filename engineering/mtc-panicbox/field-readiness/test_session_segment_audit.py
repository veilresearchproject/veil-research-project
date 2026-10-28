"""Deterministic synthetic WAV fixtures. No physical MTC or audio evidence."""
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import wave

from session_segment_audit import audit_session, inspect_segment, AuditError


class SegmentAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def wav(self, name='room_mic_continuous.wav', *, rate=8000, channels=1,
            sample_width=2, frames=8000):
        path = self.root / name
        with wave.open(str(path), 'wb') as out:
            out.setnchannels(channels)
            out.setsampwidth(sample_width)
            out.setframerate(rate)
            out.writeframes(b'\x00' * (frames * channels * sample_width))
        return path

    def test_single_file_structure_and_hash(self):
        path = self.wav()
        r = audit_session(self.root)
        self.assertEqual(r['status'], 'STRUCTURE_CONSISTENT_NOT_CONTINUITY_VERIFIED')
        self.assertEqual(r['total_audio_seconds'], 1.0)
        self.assertEqual(r['segments'][0]['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertFalse(r['capture_continuity_verified'])
        self.assertFalse(r['acoustic_capture_verified'])

    def test_two_segments_order_and_duration(self):
        self.wav(frames=16000)
        self.wav('room_mic_continuous_part002.wav', frames=24000)
        r = audit_session(self.root)
        self.assertEqual([x['name'] for x in r['segments']],
                         ['room_mic_continuous.wav', 'room_mic_continuous_part002.wav'])
        self.assertEqual(r['total_audio_seconds'], 5.0)
        self.assertEqual(r['total_frames'], 40000)

    def test_noncontiguous_numbering_alert(self):
        self.wav()
        self.wav('room_mic_continuous_part003.wav')
        self.assertIn('SEGMENT_SEQUENCE_GAP', audit_session(self.root)['alerts'])

    def test_missing_base_alert(self):
        self.wav('room_mic_continuous_part002.wav')
        self.assertIn('BASE_WAV_MISSING_OR_DUPLICATED', audit_session(self.root)['alerts'])

    def test_no_segments_unconfirmed(self):
        r = audit_session(self.root)
        self.assertEqual(r['status'], 'UNCONFIRMED')

    def test_different_sample_rate_alert(self):
        self.wav(rate=8000)
        self.wav('room_mic_continuous_part002.wav', rate=16000)
        self.assertIn('SEGMENT_FORMAT_MISMATCH', audit_session(self.root)['alerts'])

    def test_expected_duration_outside_tolerance(self):
        self.wav()
        self.assertIn('DURATION_OUTSIDE_USER_TOLERANCE',
                      audit_session(self.root, expected_minutes=90, tolerance_seconds=5)['alerts'])

    def test_expected_duration_within_tolerance(self):
        self.wav()
        r = audit_session(self.root, expected_minutes=1/60, tolerance_seconds=0)
        self.assertEqual(r['status'], 'STRUCTURE_CONSISTENT_NOT_CONTINUITY_VERIFIED')

    def test_truncated_file_alert(self):
        path = self.wav()
        path.write_bytes(path.read_bytes()[:-20])
        self.assertIn('WAV_RIFF_LENGTH_MISMATCH', audit_session(self.root)['alerts'])

    def test_extra_data_alert(self):
        path = self.wav()
        with path.open('ab') as f:
            f.write(b'extra')
        self.assertIn('WAV_RIFF_LENGTH_MISMATCH', audit_session(self.root)['alerts'])

    def test_partial_pcm_frame_alert(self):
        path = self.wav()
        data = bytearray(path.read_bytes())
        data.extend(b'\x00\x00')  # one data byte plus one RIFF pad byte
        struct.pack_into('<I', data, 4, len(data)-8)
        struct.pack_into('<I', data, 40, len(data)-45)
        path.write_bytes(data)
        self.assertIn('WAV_INCOMPLETE_PCM_FRAME', audit_session(self.root)['alerts'])

    def test_zero_length_data_alert(self):
        self.wav(frames=0)
        self.assertIn('WAV_EMPTY_DATA', audit_session(self.root)['alerts'])

    def test_symlink_file_alert(self):
        original = self.wav('source.wav')
        link = self.root / 'room_mic_continuous.wav'
        try:
            link.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest('symlink creation unavailable')
        self.assertIn('WAV_SYMLINK_NOT_ALLOWED', audit_session(self.root)['alerts'])

    def test_symlink_folder_alert(self):
        link = self.root.parent / (self.root.name + '-link')
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlink creation unavailable')
        self.addCleanup(link.unlink)
        self.assertIn('SESSION_DIRECTORY_UNAVAILABLE_OR_SYMLINK', audit_session(link)['alerts'])

    def test_unsupported_float_wav(self):
        path = self.wav()
        raw = bytearray(path.read_bytes())
        struct.pack_into('<H', raw, 20, 3)
        path.write_bytes(raw)
        self.assertIn('WAV_UNSUPPORTED_PCM_FORMAT', audit_session(self.root)['alerts'])

    def test_unrelated_files_ignored(self):
        self.wav()
        (self.root / 'events.jsonl').write_text('{"fake":true}\n')
        (self.root / 'session_result.json').write_text('{"fake":true}')
        self.assertEqual(len(audit_session(self.root)['segments']), 1)

    def test_original_evidence_not_modified(self):
        path = self.wav()
        before = path.read_bytes()
        stat_before = path.stat()
        audit_session(self.root)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(path.stat().st_mtime_ns, stat_before.st_mtime_ns)

    def test_report_omits_private_full_paths(self):
        self.wav()
        self.assertNotIn(str(self.root), str(audit_session(self.root)))

    def test_reject_invalid_expected_duration(self):
        self.wav()
        with self.assertRaises(ValueError):
            audit_session(self.root, expected_minutes=-1)

    def test_invalid_part_001(self):
        self.wav()
        self.wav('room_mic_continuous_part001.wav')
        self.assertIn('INVALID_PART_NUMBER', audit_session(self.root)['alerts'])

    def test_invalid_file_header(self):
        p = self.root / 'room_mic_continuous.wav'
        p.write_bytes(b'BAD!' * 20)
        self.assertIn('WAV_UNSUPPORTED_CONTAINER', audit_session(self.root)['alerts'])


if __name__ == '__main__':
    unittest.main()
