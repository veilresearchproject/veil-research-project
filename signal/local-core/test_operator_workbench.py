import unittest
from operator_workbench import prepare_workbench

def telemetry():
    return {'instrument_type':'mtc','device_id':'MTC_1',
            'timestamp_utc':'2026-10-31T15:00:00Z',
            'measurements':{'status':'ready'}}

class WorkbenchTests(unittest.TestCase):
    def test_all_four_paths(self):
        r = prepare_workbench('research',
                [{'timestamp_s':10.25,'description':'one click'}], [telemetry()],
                speaking_ms=140)
        self.assertIn('paranormal causes', r['persona_instructions'])
        self.assertEqual(r['face_state'], 'mouth-wide')
        self.assertEqual(r['mtc_review_queue'][0]['status'], 'needs_human_review')
        self.assertEqual(r['instrument_read_only_summaries'][0]['operator_action'], 'none')
        self.assertFalse(r['hardware_control_performed'])
        self.assertFalse(r['model_inference_performed'])

    def test_off_not_animated(self):
        self.assertEqual(prepare_workbench('casual', [], [])['face_state'], 'neutral')

    def test_reduced_motion(self):
        self.assertEqual(prepare_workbench('casual', [], [], 140, True)['face_state'], 'neutral')

    def test_reject_hardware_command(self):
        item = telemetry()
        item['all_clear'] = True
        with self.assertRaises(ValueError):
            prepare_workbench('safety', [], [item])

    def test_reject_negative_speaking_duration(self):
        with self.assertRaises(ValueError):
            prepare_workbench('casual', [], [], -1)

    def test_reject_boolean_speaking_duration(self):
        with self.assertRaises(ValueError):
            prepare_workbench('casual', [], [], True)

    def test_reject_too_many_packets(self):
        with self.assertRaises(ValueError):
            prepare_workbench('research', [], [telemetry()] * 51)

if __name__ == '__main__':
    unittest.main()
