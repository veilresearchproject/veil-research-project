"""Regression: faults on the first snapshot must not be hidden by missing history."""
import unittest
from health_gate import evaluate

BASE = dict(session_id='test-001', heartbeat_monotonic=100.,
            wav_bytes=1000, wav_frames=500, callback_count=10,
            writer_errors=0, dropped_callbacks=0,
            mic_connected=True, storage_ok=True, power_ok=True)

class FirstSnapshotTests(unittest.TestCase):
    def check_fault(self, change, reason):
        decision = evaluate(dict(BASE, **change), now_monotonic=101)
        self.assertEqual(decision.state, 'HOLD')
        self.assertIn(reason, decision.reasons)

    def test_clean_first_unconfirmed(self):
        self.assertEqual(evaluate(BASE, now_monotonic=101).state, 'UNCONFIRMED')
    def test_microphone(self): self.check_fault({'mic_connected': False}, 'microphone_fault')
    def test_storage(self): self.check_fault({'storage_ok': False}, 'storage_fault')
    def test_power(self): self.check_fault({'power_ok': False}, 'power_fault')
    def test_writer(self): self.check_fault({'writer_errors': 1}, 'writer_error')
    def test_dropped(self): self.check_fault({'dropped_callbacks': 1}, 'dropped_callbacks')
    def test_stale(self):
        self.assertEqual(evaluate(BASE, now_monotonic=120).state, 'HOLD')
    def test_multiple(self):
        decision = evaluate(dict(BASE, mic_connected=False, writer_errors=2), now_monotonic=101)
        self.assertEqual(set(decision.reasons), {'microphone_fault', 'writer_error'})
    def test_no_false_progress(self):
        self.assertNotEqual(evaluate(BASE, now_monotonic=101).state, 'PROGRESS_ONLY')
    def test_bool_clock_rejected(self):
        self.assertEqual(evaluate(BASE, now_monotonic=True).state, 'UNCONFIRMED')
    def test_bool_max_age_rejected(self):
        self.assertEqual(evaluate(BASE, now_monotonic=101, max_age=True).state, 'UNCONFIRMED')

if __name__ == '__main__':
    unittest.main()
