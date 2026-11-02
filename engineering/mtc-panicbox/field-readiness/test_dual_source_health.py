"""Synthetic fault-injection and accelerated endurance tests. NO physical hardware."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest
import wave

from dual_source_health import DualSourceHealth

START = datetime(2026, 11, 2, 15, 0, tzinfo=timezone.utc)


def stamp(t: float) -> str:
    return (START + timedelta(seconds=t)).isoformat()


def snapshot(t=0, *, session_id='SYNTHETIC-20261102', sequence=1,
             bytes_written=2048, mic_callback_count=1, recorded_seconds=0,
             microphone_connected=True, writer_ok=True, errors=None, phase='RECORDING'):
    return {
        'schema': 'veil.field-status.v0.2', 'device': 'MTC', 'phase': phase,
        'observed_at_utc': stamp(t), 'session_id': session_id,
        'simulation_only': True, 'sequence': sequence,
        'bytes_written': bytes_written, 'mic_callback_count': mic_callback_count,
        'recorded_seconds': recorded_seconds, 'microphone_connected': microphone_connected,
        'writer_ok': writer_ok, 'external_power': True, 'network_connected': False,
        'errors': [] if errors is None else errors,
    }


class DualSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.status_path = self.root / 'status.json'
        self.wav_path = self.root / 'audio.wav'
        with wave.open(str(self.wav_path), 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
            f.writeframes(b'\0\0' * 32)
        self.monitor = DualSourceHealth()

    def put(self, t, **changes):
        self.status_path.write_text(json.dumps(snapshot(t, **changes)), encoding='utf-8')

    def grow(self, frames=64):
        with self.wav_path.open('ab') as f:
            f.write(struct.pack('<h', 123) * frames)

    def check(self, t):
        return self.monitor.check(self.status_path, self.wav_path,
                                  now_monotonic=t, now_utc=stamp(t))

    def healthy_pair(self):
        self.put(0); self.check(0)
        self.grow(); self.put(5, sequence=2, bytes_written=4096, mic_callback_count=2, recorded_seconds=5)
        return self.check(5)

    def test_first_sample_never_certifies_health(self):
        self.put(0)
        r = self.check(0)
        self.assertEqual(r['status'], 'UNCONFIRMED')
        self.assertFalse(r['audio_capture_verified'])

    def test_two_progressing_observers_are_correlated_not_verified(self):
        r = self.healthy_pair()
        self.assertEqual(r['status'], 'CORRELATED_PROGRESS_NOT_AUDIO_VERIFIED')
        self.assertFalse(r['audio_capture_verified'])
        self.assertTrue(r['simulation_only'])

    def test_wav_stall_over_threshold_latches(self):
        self.healthy_pair()
        self.put(10, sequence=3, bytes_written=8192, mic_callback_count=3, recorded_seconds=10)
        self.check(10)
        self.put(31, sequence=4, bytes_written=16384, mic_callback_count=4, recorded_seconds=31)
        r = self.check(31)
        self.assertEqual(r['status'], 'ALERT_REVIEW_REQUIRED')
        self.assertIn('WAV_WAV_NO_FRAME_PROGRESS', r['latched_alerts'])
        self.assertIn('TELEMETRY_PROGRESS_WITHOUT_MATCHING_WAV_GROWTH', r['warnings'])

    def test_stalled_metadata_with_growing_wav_latches(self):
        self.healthy_pair()
        self.grow(); self.put(10, sequence=3, bytes_written=4096, mic_callback_count=3, recorded_seconds=10)
        r = self.check(10)
        self.assertEqual(r['status'], 'ALERT_REVIEW_REQUIRED')
        self.assertIn('STATUS_RECORDING_BYTES_NOT_ADVANCING', r['latched_alerts'])

    def test_microphone_disconnected_latches(self):
        self.healthy_pair()
        self.grow(); self.put(10, sequence=3, bytes_written=6000, mic_callback_count=3,
                              recorded_seconds=10, microphone_connected=False)
        self.assertIn('STATUS_MIC_DISCONNECTED', self.check(10)['latched_alerts'])

    def test_writer_error_latches(self):
        self.healthy_pair()
        self.grow(); self.put(10, sequence=3, bytes_written=6000, mic_callback_count=3,
                              recorded_seconds=10, writer_ok=False)
        self.assertIn('STATUS_WRITER_FAILURE', self.check(10)['latched_alerts'])

    def test_callback_counter_stall_latches(self):
        self.healthy_pair()
        self.grow(); self.put(10, sequence=3, bytes_written=6000, mic_callback_count=2,
                              recorded_seconds=10)
        self.assertIn('STATUS_MIC_CALLBACKS_NOT_ADVANCING', self.check(10)['latched_alerts'])

    def test_missing_snapshot_latches_even_if_wav_grows(self):
        self.healthy_pair()
        self.status_path.unlink(); self.grow()
        r = self.check(10)
        self.assertEqual(r['status'], 'ALERT_REVIEW_REQUIRED')
        self.assertIn('STATUS_SNAPSHOT_UNAVAILABLE', r['latched_alerts'])

    def test_corrupted_snapshot_latches(self):
        self.healthy_pair()
        self.status_path.write_text('{bad')
        self.assertIn('STATUS_SNAPSHOT_INVALID', self.check(10)['latched_alerts'])

    def test_missing_wav_latches_even_if_telemetry_progresses(self):
        self.healthy_pair()
        self.wav_path.unlink(); self.put(10, sequence=3, bytes_written=6000,
                                        mic_callback_count=3, recorded_seconds=10)
        self.assertIn('WAV_WAV_UNAVAILABLE', self.check(10)['latched_alerts'])

    def test_same_snapshot_replayed_over_20s_latches(self):
        self.healthy_pair()
        r = self.check(26)
        self.assertEqual(r['status'], 'ALERT_REVIEW_REQUIRED')
        self.assertTrue(any('WATCHDOG_NO_NEW_SNAPSHOT' in x for x in r['latched_alerts']))

    def test_alert_does_not_auto_clear_after_progress_resumes(self):
        self.healthy_pair()
        self.wav_path.unlink(); self.check(10)
        with wave.open(str(self.wav_path), 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
            f.writeframes(b'\0\0' * 64)
        self.grow(); self.put(15, sequence=3, bytes_written=6000,
                              mic_callback_count=3, recorded_seconds=15)
        self.assertEqual(self.check(15)['status'], 'ALERT_REVIEW_REQUIRED')

    def test_changed_wav_path_requires_review(self):
        self.healthy_pair()
        new = self.root / 'segment002.wav'
        new.write_bytes(self.wav_path.read_bytes())
        r = self.monitor.check(self.status_path, new, now_monotonic=10, now_utc=stamp(10))
        self.assertIn('WAV_PATH_CHANGED_NEW_SEGMENT_REVIEW_REQUIRED', r['latched_alerts'])

    def test_session_id_change_requires_review(self):
        self.healthy_pair()
        self.grow(); self.put(10, session_id='OTHER', sequence=3, bytes_written=6000,
                              mic_callback_count=3, recorded_seconds=10)
        self.assertIn('SESSION_ID_CHANGED_REVIEW_REQUIRED', self.check(10)['latched_alerts'])

    def test_nonrecording_phase_not_progressing(self):
        self.healthy_pair()
        self.grow(); self.put(10, phase='COMPLETE', sequence=3, bytes_written=6000,
                              mic_callback_count=3, recorded_seconds=10)
        r = self.check(10)
        self.assertNotEqual(r['status'], 'CORRELATED_PROGRESS_NOT_AUDIO_VERIFIED')
        self.assertIn('NOT_IN_RECORDING_PHASE', r['warnings'])

    def test_output_contains_no_original_path_or_audio(self):
        self.healthy_pair()
        r = json.dumps(self.check(10))
        self.assertNotIn(str(self.root), r)
        self.assertNotIn('data:', r)
        self.assertFalse(json.loads(r)['equipment_control_enabled'])
        self.assertFalse(json.loads(r)['authenticated_live_telemetry'])

    def test_accelerated_90_minute_progress_then_fault(self):
        """1081 iterations with virtual clock; not a physical 90-minute test."""
        self.put(0); self.check(0)
        for i in range(1, 1081):
            t = i * 5
            self.grow(2)
            self.put(t, sequence=i + 1, bytes_written=2048 + i * 4,
                     mic_callback_count=i + 1, recorded_seconds=t)
            result = self.check(t)
            self.assertEqual(result['status'], 'CORRELATED_PROGRESS_NOT_AUDIO_VERIFIED')
        # Simulated writer failure after 90 minutes.
        self.put(5405, sequence=1082, bytes_written=10000,
                 mic_callback_count=1082, recorded_seconds=5405, writer_ok=False)
        result = self.check(5405)
        self.assertEqual(result['status'], 'ALERT_REVIEW_REQUIRED')
        self.assertIn('STATUS_WRITER_FAILURE', result['latched_alerts'])


if __name__ == '__main__':
    unittest.main()
