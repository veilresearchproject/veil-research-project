"""Deterministic synthetic-only seam screening tests; no actual VEIL evidence."""
import contextlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
import wave
from unittest import mock

import wav_seam_screen as seam


class SeamScreenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def make(self, name='room_mic_continuous.wav', values=None, *, width=2, channels=1, rate=8000):
        if values is None:
            values = [0] * 800
        samples = list(values) * channels
        limit = 1 << (8 * width - 1)
        if width == 1:
            raw = bytes(max(0, min(255, v + 128)) for v in samples)
        else:
            raw = b''.join(max(-limit, min(limit-1, v)).to_bytes(width, 'little', signed=True) for v in samples)
        p = self.root / name
        with wave.open(str(p), 'wb') as f:
            f.setnchannels(channels)
            f.setsampwidth(width)
            f.setframerate(rate)
            f.writeframes(raw)
        return p

    def pair(self, a=None, b=None, **kw):
        self.make(values=a, **kw)
        self.make('room_mic_continuous_part002.wav', values=b, **kw)

    def test_two_silent_segments_screened_but_not_verified(self):
        self.pair()
        r = seam.screen_session(self.root)
        self.assertEqual(r['status'], 'SCREENED_NOT_CONTINUITY_VERIFIED')
        self.assertFalse(r['capture_continuity_verified'])
        self.assertFalse(r['microphone_verified'])
        self.assertFalse(r['session_completion_verified'])
        self.assertEqual(len(r['joins']), 1)
        self.assertIn('PREVIOUS_TAIL_QUIET', r['joins'][0]['review_cues'])
        self.assertIn('NEXT_HEAD_QUIET', r['joins'][0]['review_cues'])

    def test_constant_nonzero_no_large_step(self):
        self.pair([1000] * 800, [1000] * 800)
        r = seam.screen_session(self.root)
        self.assertEqual(r['joins'][0]['join_sample_step_fraction_full_scale'], 0)
        self.assertEqual(r['joins'][0]['review_cues'], [])

    def test_large_step_flagged_as_review_only(self):
        self.pair([20000] * 800, [-20000] * 800)
        r = seam.screen_session(self.root)
        self.assertIn('LARGE_JOIN_SAMPLE_STEP_REVIEW_ONLY', r['joins'][0]['review_cues'])
        self.assertGreater(r['joins'][0]['join_sample_step_fraction_full_scale'], 1)

    def test_clipping_detected(self):
        self.pair([32767] * 800, [32767] * 800)
        r = seam.screen_session(self.root)
        self.assertIn('EDGE_CLIPPING_REVIEW_ONLY', r['joins'][0]['review_cues'])

    def test_no_joins_is_not_recording_success(self):
        self.make()
        r = seam.screen_session(self.root)
        self.assertEqual(r['status'], 'NO_JOINS')
        self.assertFalse(r['capture_continuity_verified'])

    def test_missing_base_holds(self):
        self.make('room_mic_continuous_part002.wav')
        r = seam.screen_session(self.root)
        self.assertEqual(r['status'], 'HOLD')
        self.assertIn('BASE_WAV_MISSING_OR_DUPLICATED', r['alerts'])

    def test_missing_part_number_holds(self):
        self.make()
        self.make('room_mic_continuous_part003.wav')
        self.assertIn('SEGMENT_SEQUENCE_GAP', seam.screen_session(self.root)['alerts'])

    def test_mismatched_sample_rate_holds(self):
        self.make(rate=8000)
        self.make('room_mic_continuous_part002.wav', rate=16000)
        self.assertIn('SEGMENT_FORMAT_MISMATCH', seam.screen_session(self.root)['alerts'])

    def test_bad_wav_holds(self):
        self.pair()
        (self.root / 'room_mic_continuous_part002.wav').write_bytes(b'broken')
        self.assertEqual(seam.screen_session(self.root)['status'], 'HOLD')

    def test_three_segments_two_joins(self):
        self.pair([1000]*800, [2000]*800)
        self.make('room_mic_continuous_part003.wav', [3000]*800)
        self.assertEqual(len(seam.screen_session(self.root)['joins']), 2)

    def test_8_bit_pcm_supported(self):
        self.pair([10]*800, [20]*800, width=1)
        self.assertEqual(seam.screen_session(self.root)['status'], 'SCREENED_NOT_CONTINUITY_VERIFIED')

    def test_24_bit_pcm_supported(self):
        self.pair([100000]*800, [200000]*800, width=3)
        self.assertEqual(seam.screen_session(self.root)['status'], 'SCREENED_NOT_CONTINUITY_VERIFIED')

    def test_32_bit_pcm_supported(self):
        self.pair([100000]*800, [200000]*800, width=4)
        self.assertEqual(seam.screen_session(self.root)['status'], 'SCREENED_NOT_CONTINUITY_VERIFIED')

    def test_stereo_supported(self):
        self.pair([1000]*800, [2000]*800, channels=2)
        self.assertEqual(seam.screen_session(self.root)['status'], 'SCREENED_NOT_CONTINUITY_VERIFIED')

    def test_short_segments_are_bounded(self):
        self.pair([1,2], [3,4])
        r = seam.screen_session(self.root)
        self.assertEqual(r['joins'][0]['window_frames_each_side'], [2,2])

    def test_sha_change_after_audit_fails_closed(self):
        self.pair()
        orig = seam._edge
        def change(path, expected_sha, seconds):
            p = self.root / 'room_mic_continuous.wav'
            if path.name == p.name:
                with p.open('r+b') as f:
                    f.seek(-2, 2)
                    f.write(b'\x11\x22')
            return orig(path, expected_sha, seconds)
        with mock.patch.object(seam, '_edge', side_effect=change):
            r = seam.screen_session(self.root)
        self.assertEqual(r['status'], 'HOLD')
        self.assertIn('SHA_CHANGED_SINCE_STRUCTURE_AUDIT', r['alerts'])

    def test_no_original_bytes_modified(self):
        self.pair([1000]*800, [2000]*800)
        paths = list(self.root.glob('*.wav'))
        originals = [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]
        seam.screen_session(self.root)
        self.assertEqual([(p.read_bytes(), p.stat().st_mtime_ns) for p in paths], originals)

    def test_report_does_not_expose_full_path_or_raw_samples(self):
        self.pair([1234]*800, [5678]*800)
        raw = json.dumps(seam.screen_session(self.root))
        self.assertNotIn(str(self.root), raw)
        self.assertNotIn('_first_samples', raw)
        self.assertNotIn('_last_samples', raw)

    def test_invalid_windows_rejected(self):
        self.pair()
        for bad in (0, -1, 5.1, float('nan'), float('inf')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                seam.screen_session(self.root, window_seconds=bad)

    def test_invalid_thresholds_rejected(self):
        self.pair()
        for kwargs in ({'quiet_dbfs': -130}, {'quiet_dbfs': float('nan')},
                       {'jump_fraction': 0}, {'jump_fraction': 3}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                seam.screen_session(self.root, **kwargs)

    def test_cli_json_and_exit_codes(self):
        self.pair()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = seam.main([str(self.root)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())['status'], 'SCREENED_NOT_CONTINUITY_VERIFIED')
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = seam.main([str(self.root / 'missing')])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out.getvalue())['status'], 'HOLD')

    def test_large_edge_window_fails_closed_before_decode(self):
        self.pair([0] * 40000, [0] * 40000, channels=8, rate=192000)
        r = seam.screen_session(self.root, window_seconds=1.0)
        self.assertEqual(r['status'], 'HOLD')
        self.assertIn('EDGE_WINDOW_EXCEEDS_MEMORY_BOUND', r['alerts'])

    def test_symlink_refused(self):
        self.pair()
        link = self.root.parent / (self.root.name + '-link')
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable')
        self.addCleanup(link.unlink)
        self.assertEqual(seam.screen_session(link)['status'], 'HOLD')


if __name__ == '__main__':
    unittest.main()
