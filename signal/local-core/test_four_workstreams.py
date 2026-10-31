import unittest
from four_workstreams import (
    PERSONA_RULES, persona_prompt, speaking_pose,
    review_mtc_observations, parse_instrument_event, instrument_summary
)

def event():
    return dict(instrument_type='panic_box', device_id='box_01',
                timestamp_utc='2026-10-31T14:00:00Z',
                measurements={'status': 'active', 'motion_detected': True})

class FourWorkstreamTests(unittest.TestCase):
    def test_persona_evidence_rule(self):
        self.assertIn('ALL CLEAR', PERSONA_RULES)
        self.assertIn('do not infer paranormal causes', persona_prompt('research'))
    def test_safety_no_jokes(self):
        self.assertIn('Do not joke', persona_prompt('safety'))
    def test_unknown_context_rejected(self):
        with self.assertRaises(ValueError):
            persona_prompt('unknown')
    def test_pose_moves_when_speaking(self):
        self.assertNotEqual(speaking_pose(0, True), speaking_pose(140, True))
    def test_pose_stops_and_respects_accessibility(self):
        self.assertEqual(speaking_pose(140, False), 'neutral')
        self.assertEqual(speaking_pose(140, True, True), 'neutral')
    def test_pose_invalid_time(self):
        with self.assertRaises(ValueError):
            speaking_pose(-1, True)
    def test_mtc_sorted_and_unverified(self):
        entries = review_mtc_observations([
            {'timestamp_s': 7, 'description': 'tap'},
            {'timestamp_s': 2, 'description': 'door'}])
        self.assertEqual([x['timestamp_s'] for x in entries], [2, 7])
        self.assertTrue(all(x['source'] == 'unverified_operator_note' for x in entries))
    def test_mtc_untrusted_input(self):
        with self.assertRaises(ValueError):
            review_mtc_observations([{'timestamp_s': -2, 'description': 'noise'}])
    def test_telemetry_read_only(self):
        packet = parse_instrument_event(event())
        summary = instrument_summary(packet)
        self.assertEqual(summary['operator_action'], 'none')
        self.assertEqual(packet.measurements['status'], 'active')
    def test_reject_commands(self):
        data = event()
        data['all_clear'] = True
        with self.assertRaises(ValueError):
            parse_instrument_event(data)
    def test_reject_bad_measurements(self):
        data = event()
        data['measurements']['temperature_c'] = float('nan')
        with self.assertRaises(ValueError):
            parse_instrument_event(data)
    def test_reject_unknown_sensor(self):
        data = event()
        data['measurements']['send_alert'] = True
        with self.assertRaises(ValueError):
            parse_instrument_event(data)
    def test_reject_oversized_input(self):
        with self.assertRaises(ValueError):
            parse_instrument_event(' ' * 9000)

if __name__ == '__main__':
    unittest.main()
