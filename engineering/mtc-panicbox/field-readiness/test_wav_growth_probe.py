"""Synthetic RIFF/WAV file fixtures. No real microphone, recorder or Windows tests."""
import io
import os
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest
import wave

from wav_growth_probe import WaveGrowthProbe, WaveProbeError, read_wav_snapshot


class WaveGrowthProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'synthetic.wav'
        self.make_pcm(frames=8)
        self.probe = WaveGrowthProbe(stalled_after_seconds=20)

    def make_pcm(self, frames=8, channels=1, width=2):
        with wave.open(str(self.path), 'wb') as w:
            w.setnchannels(channels)
            w.setsampwidth(width)
            w.setframerate(16000)
            w.writeframes(b'\x00' * (frames * channels * width))

    def grow(self, frames=8):
        # Simulates a writer appending PCM payload without finalizing RIFF sizes.
        with self.path.open('ab') as f:
            f.write(b'\x00\x01' * frames)

    def check(self, tick):
        return self.probe.check(self.path, now_monotonic=tick)

    def test_first_sample_not_success(self):
        r = self.check(0)
        self.assertEqual(r['status'], 'UNCONFIRMED')
        self.assertFalse(r['physical_capture_validated'])

    def test_unchanged_file_is_not_healthy(self):
        self.check(0)
        self.assertEqual(self.check(5)['status'], 'UNCONFIRMED')
        self.assertEqual(self.check(21)['alerts'], ['WAV_NO_FRAME_PROGRESS'])

    def test_growing_payload_observed_not_acoustics(self):
        self.check(0)
        self.grow()
        r = self.check(5)
        self.assertEqual(r['status'], 'GROWTH_OBSERVED_NOT_AUDIO_VERIFIED')
        self.assertIn('WAV_HEADER_SIZE_NOT_FINALIZED', r['alerts'])
        self.assertEqual(r['estimated_complete_frames'], 16)
        self.assertFalse(r['physical_capture_validated'])

    def test_touch_only_cannot_fake_growth(self):
        self.check(0)
        os.utime(self.path, None)
        self.assertEqual(self.check(21)['alerts'], ['WAV_NO_FRAME_PROGRESS'])

    def test_partial_frame_not_counted(self):
        self.check(0)
        with self.path.open('ab') as f:
            f.write(b'\x00')
        r = self.check(5)
        self.assertEqual(r['status'], 'UNCONFIRMED')
        self.assertIn('WAV_PARTIAL_FRAME', r['alerts'])

    def test_persistent_partial_frame_escalates(self):
        self.check(0)
        with self.path.open('ab') as f:
            f.write(b'\x00')
        self.assertEqual(self.check(5)['status'], 'UNCONFIRMED')
        r = self.check(21)
        self.assertEqual(r['status'], 'ALERT')
        self.assertIn('WAV_NO_FRAME_PROGRESS', r['alerts'])

    def test_partial_frame_then_complete_frame(self):
        self.check(0)
        with self.path.open('ab') as f:
            f.write(b'\x00')
        self.check(5)
        with self.path.open('ab') as f:
            f.write(b'\x01')
        self.assertEqual(self.check(6)['status'], 'GROWTH_OBSERVED_NOT_AUDIO_VERIFIED')

    def test_missing_file_alert(self):
        self.path.unlink()
        self.assertEqual(self.check(0)['alerts'], ['WAV_UNAVAILABLE'])

    def test_missing_then_reappear_requires_pair(self):
        self.check(0)
        self.path.unlink()
        self.check(1)
        self.make_pcm(8)
        self.assertEqual(self.check(2)['status'], 'UNCONFIRMED')

    def test_truncate_is_latched(self):
        self.check(0)
        self.path.write_bytes(self.path.read_bytes()[:44])
        self.assertIn('WAV_TRUNCATED_REBASE_REQUIRED', self.check(1)['alerts'])
        self.make_pcm(32)
        self.assertEqual(self.check(2)['status'], 'ALERT')

    def test_replacement_latched(self):
        self.check(0)
        replacement = self.path.with_suffix('.new')
        replacement.write_bytes(self.path.read_bytes())
        os.replace(replacement, self.path)
        self.assertIn('WAV_FILE_REPLACED_REBASE_REQUIRED', self.check(1)['alerts'])

    def test_clock_regression_latched(self):
        self.check(5)
        self.assertEqual(self.check(4)['alerts'], ['WAV_PROBE_CLOCK_REGRESSION'])

    def test_corrupt_header(self):
        self.path.write_bytes(b'junk' * 20)
        with self.assertRaisesRegex(WaveProbeError, 'WAV_UNSUPPORTED_CONTAINER'):
            read_wav_snapshot(self.path)

    def test_short_header(self):
        self.path.write_bytes(b'RIFF')
        self.assertIn('WAV_HEADER_INCOMPLETE', self.check(0)['alerts'])

    def test_symlink_rejected(self):
        original = self.path.with_suffix('.real')
        self.path.rename(original)
        try:
            self.path.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable')
        self.assertIn('WAV_SYMLINK_NOT_ALLOWED', self.check(0)['alerts'])

    def test_unsupported_float_format_rejected(self):
        data = bytearray(self.path.read_bytes())
        data[20:22] = struct.pack('<H', 3)
        self.path.write_bytes(data)
        self.assertIn('WAV_UNSUPPORTED_FORMAT', self.check(0)['alerts'])

    def test_stereo_frame_alignment(self):
        self.make_pcm(frames=8, channels=2)
        s = read_wav_snapshot(self.path)
        self.assertEqual(s['complete_frames_estimate'], 8)
        self.assertEqual(s['format'], (2, 16000, 16, 4))

    def test_65min_virtual_clock_not_physical_endurance(self):
        # Fast-forwarded synthetic timeline. No 65-minute physical recording.
        self.check(0)
        for tick in range(5, 3901, 5):
            self.grow()
            self.assertEqual(self.check(tick)['status'], 'GROWTH_OBSERVED_NOT_AUDIO_VERIFIED')
        self.assertEqual(self.check(3925)['alerts'], ['WAV_NO_FRAME_PROGRESS'])

    def test_no_network_or_mutation_on_inspection(self):
        before = self.path.read_bytes()
        self.check(0)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse(self.check(1)['equipment_control_enabled'])

    def test_restart_resets_only_ram_observation(self):
        self.check(0)
        self.grow()
        self.check(5)
        second = WaveGrowthProbe()
        self.assertEqual(second.check(self.path, now_monotonic=6)['status'], 'UNCONFIRMED')

    def test_format_change_latched(self):
        self.check(0)
        data = bytearray(self.path.read_bytes())
        data[24:28] = struct.pack('<I', 8000)
        data[28:32] = struct.pack('<I', 16000)
        self.path.write_bytes(data)
        self.assertIn('WAV_FORMAT_CHANGED_REBASE_REQUIRED', self.check(1)['alerts'])


if __name__ == '__main__':
    unittest.main()
