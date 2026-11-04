import unittest
from health_gate import evaluate

BASE = dict(session_id='test',heartbeat_monotonic=100.,wav_bytes=1000,wav_frames=100,callback_count=10,writer_errors=0,dropped_callbacks=0,mic_connected=True,storage_ok=True,power_ok=True)
NEXT = dict(BASE,heartbeat_monotonic=105.,wav_bytes=2000,wav_frames=200,callback_count=20)
class GateTests(unittest.TestCase):
    def check(self, change, reason):
        s=dict(NEXT,**change)
        self.assertIn(reason,evaluate(s,now_monotonic=106,previous=BASE).reasons)
    def test_progress(self): self.assertEqual(evaluate(NEXT,now_monotonic=106,previous=BASE).state,'PROGRESS_ONLY')
    def test_no_baseline(self): self.assertEqual(evaluate(NEXT,now_monotonic=106).state,'UNCONFIRMED')
    def test_missing(self): self.assertEqual(evaluate({},now_monotonic=106).state,'UNCONFIRMED')
    def test_stale(self): self.check({'heartbeat_monotonic':80},'stale_heartbeat')
    def test_future(self): self.assertEqual(evaluate(dict(NEXT,heartbeat_monotonic=107),now_monotonic=106).state,'UNCONFIRMED')
    def test_mic(self): self.check({'mic_connected':False},'microphone_fault')
    def test_storage(self): self.check({'storage_ok':False},'storage_fault')
    def test_power(self): self.check({'power_ok':False},'power_fault')
    def test_writer(self): self.check({'writer_errors':1},'writer_error')
    def test_dropped(self): self.check({'dropped_callbacks':1},'dropped_callbacks')
    def test_bytes_stall(self): self.check({'wav_bytes':1000},'no_progress_wav_bytes')
    def test_frames_stall(self): self.check({'wav_frames':100},'no_progress_wav_frames')
    def test_callback_stall(self): self.check({'callback_count':10},'no_progress_callback_count')
    def test_regression(self): self.check({'wav_bytes':900},'counter_regression_wav_bytes')
    def test_session(self): self.check({'session_id':'other'},'session_mismatch')
    def test_bool_counter(self): self.assertEqual(evaluate(dict(NEXT,wav_bytes=True),now_monotonic=106).state,'UNCONFIRMED')
    def test_invalid_flag(self): self.check({'mic_connected':'yes'},'microphone_fault')
    def test_no_mutation(self):
        old=dict(NEXT); evaluate(NEXT,now_monotonic=106,previous=BASE); self.assertEqual(NEXT,old)
if __name__=='__main__': unittest.main()
