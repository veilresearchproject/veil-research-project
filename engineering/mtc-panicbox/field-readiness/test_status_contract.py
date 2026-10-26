import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from status_contract import validate, assess, BadTelemetry

T0 = datetime(2026,10,26,12,0,tzinfo=timezone.utc)
def snapshot(phase='RECORDING', **kwargs):
    base={
        'schema':'veil.field-status.v0.2', 'simulation_only':True, 'device':'MTC', 'phase':phase,
        'observed_at_utc': T0.isoformat(), 'session_id':'DEMO-001','sequence':1,
        'bytes_written':1024,'mic_callback_count':5,'recorded_seconds':2,
        'microphone_connected':True,'writer_ok':True,'external_power':True,'network_connected':True,'errors':[]
    }
    base.update(kwargs)
    return base

class StatusContractTests(unittest.TestCase):
    def good_pair(self):
        a=snapshot()
        b=snapshot(observed_at_utc=(T0+timedelta(seconds=5)).isoformat(),sequence=2,
                   bytes_written=2048,mic_callback_count=10,recorded_seconds=7)
        return a,b
    def test_healthy_progress_requires_two_samples(self):
        a,b=self.good_pair()
        self.assertEqual(assess(b,a,now_utc=(T0+timedelta(seconds=6)).isoformat())['status'],'PROGRESS_OBSERVED')
    def test_single_sample_not_confirmed(self):
        _,b=self.good_pair()
        self.assertIn('SECOND_SAMPLE_REQUIRED',assess(b,now_utc=b['observed_at_utc'])['alerts'])
    def test_heartbeat_stale(self):
        a,b=self.good_pair()
        result=assess(b,a,now_utc=(T0+timedelta(seconds=40)).isoformat())
        self.assertEqual(result['status'],'ALERT')
        self.assertIn('HEARTBEAT_STALE',result['alerts'])
    def test_mic_unplugged(self):
        a,b=self.good_pair();b['microphone_connected']=False
        self.assertIn('MIC_DISCONNECTED',assess(b,a,now_utc=b['observed_at_utc'])['alerts'])
    def test_writer_failure(self):
        a,b=self.good_pair();b['writer_ok']=False
        self.assertIn('WRITER_FAILURE',assess(b,a,now_utc=b['observed_at_utc'])['alerts'])
    def test_wav_not_growing(self):
        a,b=self.good_pair();b['bytes_written']=a['bytes_written']
        self.assertIn('RECORDING_BYTES_NOT_ADVANCING',assess(b,a,now_utc=b['observed_at_utc'])['alerts'])
    def test_mic_callbacks_not_growing(self):
        a,b=self.good_pair();b['mic_callback_count']=a['mic_callback_count']
        self.assertIn('MIC_CALLBACKS_NOT_ADVANCING',assess(b,a,now_utc=b['observed_at_utc'])['alerts'])
    def test_clock_anomaly(self):
        a,b=self.good_pair()
        self.assertIn('DEVICE_CLOCK_AHEAD_OR_UNTRUSTED',assess(b,a,now_utc=(T0-timedelta(seconds=2)).isoformat())['alerts'])
    def test_regressed_sequence(self):
        a,b=self.good_pair();b['sequence']=a['sequence']
        self.assertIn('SEQUENCE_NOT_ADVANCING',assess(b,a,now_utc=b['observed_at_utc'])['alerts'])
    def test_session_switch_invalidates_previous(self):
        a,b=self.good_pair();b['session_id']='OTHER'
        self.assertIn('SECOND_SAMPLE_REQUIRED',assess(b,a,now_utc=b['observed_at_utc'])['alerts'])
    def test_power_loss_unverified(self):
        a,b=self.good_pair();b['external_power']=False
        self.assertIn('EXTERNAL_POWER_LOSS_BATTERY_UNVERIFIED',assess(b,a,now_utc=b['observed_at_utc'])['alerts'])
    def test_panic_full_offline_cannot_be_reassuring(self):
        x=snapshot(device='PANIC_BOX',phase='FULL',network_connected=False)
        r=assess(x, now_utc=x['observed_at_utc'])
        self.assertEqual(r['phase'],'FULL')
        self.assertIn('REMOTE_LINK_UNAVAILABLE_FULL_REMAINS_ACTIVE',r['alerts'])
        self.assertFalse(r['equipment_control_enabled'])
    def test_panic_baseline_allowed(self):
        x=snapshot(device='PANIC_BOX',phase='BASELINE')
        self.assertEqual(assess(x,now_utc=x['observed_at_utc'])['status'],'STATE_REPORTED')
    def test_reject_unsimulated_fake_live(self):
        x=snapshot(simulation_only=False)
        with self.assertRaises(BadTelemetry):validate(x)
    def test_reject_wrong_schema(self):
        x=snapshot(schema='fake')
        with self.assertRaises(BadTelemetry):validate(x)
    def test_reject_bad_types(self):
        for name,val in [('sequence',True),('bytes_written',-1),('errors','hello'),('writer_ok','yes'),('recorded_seconds',1.3)]:
            with self.subTest(name=name),self.assertRaises(BadTelemetry):validate(snapshot(**{name:val}))
    def test_mtc_cannot_claim_full(self):
        with self.assertRaises(BadTelemetry):validate(snapshot(phase='FULL'))

if __name__=='__main__':unittest.main()
