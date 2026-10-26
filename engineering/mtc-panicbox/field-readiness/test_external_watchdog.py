import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from datetime import timedelta
from test_status_contract import T0, snapshot
from external_watchdog import IndependentWatchdog, MAX_SNAPSHOT_BYTES, read_snapshot


def at(seconds):
    return (T0 + timedelta(seconds=seconds)).isoformat()


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'status.json'
        self.wd = IndependentWatchdog(silence_seconds=20)

    def put(self, data):
        self.path.write_text(json.dumps(data), encoding='utf-8')

    def check(self, seconds):
        return self.wd.check(self.path, now_monotonic=seconds, now_utc=at(seconds))

    def test_no_file_alert(self):
        self.assertEqual(self.check(0)['alerts'], ['SNAPSHOT_UNAVAILABLE'])

    def test_first_snapshot_not_healthy(self):
        self.put(snapshot())
        self.assertEqual(self.check(0)['status'], 'UNCONFIRMED')

    def test_progress_after_two_distinct_snapshots(self):
        self.put(snapshot()); self.check(0)
        self.put(snapshot(sequence=2, bytes_written=2048, mic_callback_count=10,
                          observed_at_utc=at(5), recorded_seconds=7))
        self.assertEqual(self.check(5)['status'], 'PROGRESS_OBSERVED')

    def test_replay_does_not_extend_liveness(self):
        self.put(snapshot()); self.check(0)
        self.assertEqual(self.check(10)['status'], 'UNCONFIRMED')
        self.assertEqual(self.check(21)['alerts'], ['WATCHDOG_NO_NEW_SNAPSHOT'])

    def test_rewrite_same_bytes_does_not_extend_liveness(self):
        self.put(snapshot()); self.check(0)
        self.put(snapshot())
        self.check(19)
        self.assertIn('WATCHDOG_NO_NEW_SNAPSHOT', self.check(21)['alerts'])

    def test_sequence_regression_alert(self):
        self.put(snapshot()); self.check(0)
        self.put(snapshot(sequence=0, bytes_written=2000, mic_callback_count=10,
                          observed_at_utc=at(5)))
        self.assertIn('SEQUENCE_NOT_ADVANCING', self.check(5)['alerts'])

    def test_stalled_bytes_alert(self):
        self.put(snapshot()); self.check(0)
        self.put(snapshot(sequence=2, bytes_written=1024, mic_callback_count=10,
                          observed_at_utc=at(5)))
        self.assertIn('RECORDING_BYTES_NOT_ADVANCING', self.check(5)['alerts'])

    def test_missing_mic_alert(self):
        self.put(snapshot(microphone_connected=False))
        self.assertIn('MIC_DISCONNECTED', self.check(0)['alerts'])

    def test_invalid_json_fails_closed_and_requires_new_pair(self):
        self.put(snapshot()); self.check(0)
        self.path.write_text('{broken', encoding='utf-8')
        self.assertEqual(self.check(2)['alerts'], ['SNAPSHOT_INVALID'])
        self.put(snapshot(sequence=2, bytes_written=2048, mic_callback_count=10,
                          observed_at_utc=at(5)))
        self.assertEqual(self.check(5)['status'], 'UNCONFIRMED')

    def test_oversize_rejected(self):
        self.path.write_bytes(b' ' * (MAX_SNAPSHOT_BYTES+1))
        self.assertEqual(self.check(0)['alerts'], ['SNAPSHOT_TOO_LARGE'])

    def test_symlink_rejected(self):
        real = Path(self.tmp.name) / 'real.json'
        real.write_text(json.dumps(snapshot()))
        try:
            self.path.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable')
        self.assertEqual(self.check(0)['alerts'], ['SYMLINK_NOT_ALLOWED'])

    def test_panic_full_link_loss_preserves_full(self):
        self.put(snapshot(device='PANIC_BOX', phase='FULL', network_connected=False))
        r=self.check(0)
        self.assertEqual(r['assessment']['phase'], 'FULL')
        self.assertIn('REMOTE_LINK_UNAVAILABLE_FULL_REMAINS_ACTIVE', r['alerts'])
        self.assertFalse(r['equipment_control_enabled'])

    def test_panic_first_sample_not_health_claim(self):
        self.put(snapshot(device='PANIC_BOX', phase='BASELINE'))
        self.assertEqual(self.check(0)['status'], 'UNCONFIRMED')

    def test_monotonic_clock_regression(self):
        self.put(snapshot()); self.check(5)
        self.assertEqual(self.check(4)['alerts'], ['WATCHDOG_CLOCK_REGRESSION'])

    def test_device_timestamp_stale_even_with_new_file(self):
        self.put(snapshot()); self.check(0)
        self.put(snapshot(sequence=2, bytes_written=2048, mic_callback_count=10))
        self.assertIn('HEARTBEAT_STALE', self.check(30)['alerts'])

    def test_no_physical_claim_or_control(self):
        self.put(snapshot()); r=self.check(0)
        self.assertTrue(r['simulation_only'])
        self.assertFalse(r['equipment_control_enabled'])
        self.assertIn('not a physical',r['interpretation'])


if __name__ == '__main__':
    unittest.main()
