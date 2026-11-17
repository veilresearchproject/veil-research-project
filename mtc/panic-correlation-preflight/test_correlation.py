import copy
import json
import unittest
from correlation import parse_event, compare, generate_report, output_json, InvalidEvent

H='a'*64

def event(**kw):
    d={"event_id":"MTC01", "session_id":"SESSION20261117", "source_kind":"MTC", "device_id":"MIC01", "source_file_sha256":H,"recorded_at":"2026-11-17T21:00:00Z", "clock_offset_ms":0,"clock_uncertainty_ms":100, "event_window_ms":100, "flag_type":"WAVE_ENERGY"}
    d.update(kw)
    return d

def box(**kw):
    d=event(event_id='BOX01',source_kind='PANIC_BOX',device_id='CAM01',flag_type='MOTION_FLAG')
    d.update(kw)
    return d

class Tests(unittest.TestCase):
    def test_01_parse(self):self.assertEqual(parse_event(event()).event_id,'MTC01')
    def test_02_utc_time(self):self.assertTrue(parse_event(event()).recorded_at.isoformat().endswith('+00:00'))
    def test_03_offset_converted(self):self.assertEqual(parse_event(event(recorded_at='2026-11-17T16:00:00-05:00')).recorded_at,parse_event(event()).recorded_at)
    def test_04_naive_reject(self):
        with self.assertRaises(InvalidEvent):parse_event(event(recorded_at='2026-11-17T21:00:00'))
    def test_05_fake_sha_reject(self):
        with self.assertRaises(InvalidEvent):parse_event(event(source_file_sha256='bad'))
    def test_06_boolean_offset_reject(self):
        with self.assertRaises(InvalidEvent):parse_event(event(clock_offset_ms=True))
    def test_07_negative_uncertainty_reject(self):
        with self.assertRaises(InvalidEvent):parse_event(event(clock_uncertainty_ms=-1))
    def test_08_missing_offset_pair_reject(self):
        with self.assertRaises(InvalidEvent):parse_event(event(clock_offset_ms=None))
    def test_09_no_clock_pair_valid(self):self.assertIsNone(parse_event(event(clock_offset_ms=None,clock_uncertainty_ms=None)).interval_ms())
    def test_10_overlapping_review_only(self):self.assertEqual(compare(parse_event(event()),parse_event(box()))['classification'],'POSSIBLE_TEMPORAL_OVERLAP_REVIEW_ONLY')
    def test_11_uncertainty_boundary_overlap(self):self.assertEqual(compare(parse_event(event()),parse_event(box(recorded_at='2026-11-17T21:00:00.400Z')))['classification'],'POSSIBLE_TEMPORAL_OVERLAP_REVIEW_ONLY')
    def test_12_separated(self):self.assertEqual(compare(parse_event(event()),parse_event(box(recorded_at='2026-11-17T21:00:01Z')))['classification'],'NO_TEMPORAL_OVERLAP')
    def test_13_missing_clock_fail_closed(self):self.assertEqual(compare(parse_event(event()),parse_event(box(clock_offset_ms=None,clock_uncertainty_ms=None)))['classification'],'CLOCK_DATA_MISSING')
    def test_14_different_sessions(self):self.assertEqual(compare(parse_event(event()),parse_event(box(session_id='OTHERSESSION')))['classification'],'DIFFERENT_SESSION')
    def test_15_same_device_not_independent(self):self.assertEqual(compare(parse_event(event()),parse_event(box(device_id='MIC01')))['classification'],'SAME_DEVICE')
    def test_16_same_event_rejected(self):
        with self.assertRaises(InvalidEvent):compare(parse_event(event()),parse_event(event()))
    def test_17_duplicate_ids_rejected(self):
        with self.assertRaises(InvalidEvent):generate_report([event(),event()])
    def test_18_unknown_source_rejected(self):
        with self.assertRaises(InvalidEvent):parse_event(event(source_kind='ALIEN'))
    def test_19_report_no_publication(self):
        rep=generate_report([event(),box()]);self.assertTrue(rep['human_review_required']);self.assertFalse(rep['publication_approved']);self.assertEqual(len(rep['pairs']),1)
    def test_20_single_source_no_cross_pair(self):self.assertFalse(generate_report([event()])['pairs'])
    def test_21_report_preserves_shas(self):self.assertEqual(generate_report([event()])['events'][0]['source_file_sha256'],H)
    def test_22_json_deterministic(self):self.assertEqual(output_json([event(),box()]),output_json([event(),box()]))
    def test_23_event_limit(self):
        with self.assertRaises(InvalidEvent):generate_report([event()]*201)
    def test_24_clock_offset_compensates(self):self.assertEqual(compare(parse_event(event()),parse_event(box(recorded_at='2026-11-17T20:59:59Z',clock_offset_ms=1000)))['classification'],'POSSIBLE_TEMPORAL_OVERLAP_REVIEW_ONLY')

if __name__=='__main__':unittest.main()
