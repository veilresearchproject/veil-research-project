import unittest
from preflight_fusion import evaluate_fused

BASE=dict(session_id='s',heartbeat_monotonic=100,wav_bytes=200,wav_frames=100,callback_count=10,writer_errors=0,dropped_callbacks=0,mic_connected=True,storage_ok=True,power_ok=True)
PREV={**BASE,'heartbeat_monotonic':95,'wav_bytes':100,'wav_frames':50,'callback_count':5}
DUAL=dict(schema='veil.mtc-dual-source-health.v0.1',simulation_only=True,authenticated_live_telemetry=False,equipment_control_enabled=False,audio_capture_verified=False,status='CORRELATED_PROGRESS_NOT_AUDIO_VERIFIED')
class Tests(unittest.TestCase):
 def run_eval(self,snapshot,dual=DUAL,previous=PREV,now=101): return evaluate_fused(snapshot,dual,now_monotonic=now,previous=previous)
 def test_normal_progress(self): self.assertEqual(self.run_eval(BASE)['state'],'PROGRESS_ONLY')
 def test_first_snapshot_no_progress(self): self.assertEqual(self.run_eval(BASE,previous=None)['state'],'UNCONFIRMED')
 def test_mic_fault_partial(self): self.assertEqual(self.run_eval({'mic_connected':False})['state'],'HOLD')
 def test_writer_fault_partial(self): self.assertEqual(self.run_eval({'writer_errors':1})['state'],'HOLD')
 def test_storage_fault_partial(self): self.assertEqual(self.run_eval({'storage_ok':False})['state'],'HOLD')
 def test_power_fault_partial(self): self.assertEqual(self.run_eval({'power_ok':False})['state'],'HOLD')
 def test_drops_partial(self): self.assertEqual(self.run_eval({'dropped_callbacks':2})['state'],'HOLD')
 def test_stale(self): self.assertEqual(self.run_eval(BASE,now=200)['state'],'HOLD')
 def test_missing(self): self.assertEqual(self.run_eval({})['state'],'UNCONFIRMED')
 def test_invalid_counter(self): self.assertEqual(self.run_eval({**BASE,'wav_bytes':True})['state'],'UNCONFIRMED')
 def test_regression(self): self.assertEqual(self.run_eval({**BASE,'wav_frames':20})['state'],'HOLD')
 def test_stall(self): self.assertEqual(self.run_eval({**BASE,'wav_bytes':100})['state'],'HOLD')
 def test_dual_fault(self): self.assertEqual(self.run_eval(BASE,{**DUAL,'status':'ALERT_REVIEW_REQUIRED'})['state'],'HOLD')
 def test_invalid_dual(self): self.assertEqual(self.run_eval(BASE,{**DUAL,'simulation_only':False})['state'],'UNCONFIRMED')
 def test_no_mutation(self):
  before=BASE.copy(); self.run_eval(BASE); self.assertEqual(BASE,before)
 def test_no_audio_claim(self): self.assertFalse(self.run_eval(BASE)['audio_capture_verified'])
 def test_future_heartbeat(self): self.assertEqual(self.run_eval(BASE,now=90)['state'],'HOLD')
if __name__=='__main__': unittest.main()
