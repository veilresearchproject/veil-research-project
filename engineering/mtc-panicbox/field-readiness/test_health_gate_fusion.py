import unittest
from health_gate import Decision
from health_gate_fusion import fuse

BASE = {'schema': 'veil.mtc-dual-source-health.v0.1',
        'simulation_only': True, 'authenticated_live_telemetry': False,
        'equipment_control_enabled': False, 'audio_capture_verified': False,
        'status': 'CORRELATED_PROGRESS_NOT_AUDIO_VERIFIED'}

class FusionTests(unittest.TestCase):
    def test_both_progress(self):
        r = fuse(Decision('PROGRESS_ONLY', ()), BASE)
        self.assertEqual(r['state'], 'PROGRESS_ONLY')
        self.assertFalse(r['audio_capture_verified'])
    def test_gate_fault_wins(self):
        self.assertEqual(fuse(Decision('HOLD', ('microphone_fault',)), BASE)['state'], 'HOLD')
    def test_dual_fault_wins(self):
        self.assertEqual(fuse(Decision('PROGRESS_ONLY', ()), dict(BASE, status='ALERT_REVIEW_REQUIRED'))['state'], 'HOLD')
    def test_missing_previous(self):
        self.assertEqual(fuse(Decision('UNCONFIRMED', ('no_previous_snapshot',)), BASE)['state'], 'UNCONFIRMED')
    def test_missing_wav_progress(self):
        self.assertEqual(fuse(Decision('PROGRESS_ONLY', ()), dict(BASE, status='UNCONFIRMED'))['state'], 'UNCONFIRMED')
    def test_contract_false_live(self):
        self.assertEqual(fuse(Decision('PROGRESS_ONLY', ()), dict(BASE, simulation_only=False))['state'], 'UNCONFIRMED')
    def test_contract_false_verified_audio(self):
        self.assertEqual(fuse(Decision('PROGRESS_ONLY', ()), dict(BASE, audio_capture_verified=True))['state'], 'UNCONFIRMED')
    def test_unknown_state(self):
        self.assertEqual(fuse(Decision('PROGRESS_ONLY', ()), dict(BASE, status='HEALTHY'))['state'], 'UNCONFIRMED')
    def test_unknown_gate(self):
        self.assertEqual(fuse(Decision('VERIFIED', ()), BASE)['state'], 'UNCONFIRMED')
    def test_bad_inputs(self):
        self.assertEqual(fuse(None, None)['state'], 'UNCONFIRMED')
    def test_no_hardware_control(self):
        self.assertFalse(fuse(Decision('PROGRESS_ONLY', ()), BASE)['equipment_control_enabled'])

if __name__ == '__main__': unittest.main()
