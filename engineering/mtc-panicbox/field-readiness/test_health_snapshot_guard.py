import unittest
from health_snapshot_guard import inspect

BASE = dict(session_id='test',heartbeat_monotonic=100,wav_bytes=200,wav_frames=100,callback_count=10,writer_errors=0,dropped_callbacks=0,mic_connected=True,storage_ok=True,power_ok=True)
class GuardTests(unittest.TestCase):
    def test_valid_does_not_claim_progress(self): self.assertEqual(inspect(BASE,now_monotonic=101).state,'UNCONFIRMED')
    def test_missing_data_with_mic_fault(self): self.assertEqual(inspect({'mic_connected':False},now_monotonic=101).state,'HOLD')
    def test_missing_data_with_writer_fault(self): self.assertIn('writer_error',inspect({'writer_errors':1},now_monotonic=101).reasons)
    def test_missing_data_with_storage_fault(self): self.assertIn('storage_fault',inspect({'storage_ok':False},now_monotonic=101).reasons)
    def test_missing_data_with_power_fault(self): self.assertIn('power_fault',inspect({'power_ok':False},now_monotonic=101).reasons)
    def test_missing_data_with_drops(self): self.assertIn('dropped_callbacks',inspect({'dropped_callbacks':2},now_monotonic=101).reasons)
    def test_stale(self): self.assertIn('stale_heartbeat',inspect(BASE,now_monotonic=120).reasons)
    def test_future(self): self.assertIn('future_heartbeat',inspect(BASE,now_monotonic=90).reasons)
    def test_missing(self): self.assertEqual(inspect({},now_monotonic=101).state,'UNCONFIRMED')
    def test_bad_clock(self): self.assertEqual(inspect(BASE,now_monotonic=float('nan')).state,'HOLD')
    def test_negative_counter(self): self.assertEqual(inspect({**BASE,'wav_bytes':-1},now_monotonic=101).state,'UNCONFIRMED')
    def test_bool_counter(self): self.assertEqual(inspect({**BASE,'wav_bytes':True},now_monotonic=101).state,'UNCONFIRMED')
    def test_invalid_flag(self): self.assertEqual(inspect({**BASE,'mic_connected':None},now_monotonic=101).state,'HOLD')
    def test_nonmapping(self): self.assertEqual(inspect(None,now_monotonic=101).state,'UNCONFIRMED')
    def test_no_evidence_changes(self):
        original=BASE.copy(); inspect(BASE,now_monotonic=101); self.assertEqual(BASE,original)
if __name__=='__main__': unittest.main()
