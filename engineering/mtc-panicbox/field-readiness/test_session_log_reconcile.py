"""Synthetic tests only; no user evidence, Windows hardware, or real recorder."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import wave

from session_log_reconcile import reconcile_session, _parse_events, _read_original, SourceProblem


def setup(root, *, duration=8, events=None, result=None, metadata=None):
    with wave.open(str(root / 'room_mic_continuous.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(struct.pack('<h', 0) * (8000 * duration))
    if events is None:
        events = [{'event': 'recording_start', 't_seconds': 0},
                  {'event': 'question_start', 't_seconds': 2},
                  {'event': 'question_end', 't_seconds': 3},
                  {'event': 'recording_stop', 't_seconds': duration}]
    (root / 'events.jsonl').write_text('\n'.join(json.dumps(x) for x in events)+'\n', encoding='utf-8')
    (root / 'session_result.json').write_text(json.dumps(result if result is not None else {'result':'ok'}))
    (root / 'session_metadata.json').write_text(json.dumps(metadata if metadata is not None else {'sample_rate':8000}))


class TestSessionLogReconcile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        setup(self.root)

    def run_audit(self, **kw):
        return reconcile_session(self.root, tolerance_seconds=1, **kw)

    def test_healthy_synthetic_is_unconfirmed_without_verified_result_schema(self):
        x=self.run_audit(); self.assertEqual(x['status'],'UNCONFIRMED')
        self.assertEqual(x['events']['question_pairs'],1)
        self.assertFalse(x['physical_session_validated'])

    def test_sources_hashed_and_unchanged(self):
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir()}
        x=self.run_audit()
        after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir()}
        self.assertEqual(before,after)
        self.assertEqual(x['sources']['events.jsonl']['sha256'],before['events.jsonl'])

    def test_missing_session_alert(self):
        self.assertEqual(reconcile_session(self.root/'none')['status'],'ALERT')

    def test_missing_events_alert(self):
        (self.root/'events.jsonl').unlink()
        self.assertIn('EVENTS_JSONL_SOURCE_MISSING_OR_UNREADABLE',self.run_audit()['alerts'])

    def test_missing_result_alert(self):
        (self.root/'session_result.json').unlink()
        self.assertEqual(self.run_audit()['status'],'ALERT')

    def test_missing_metadata_alert(self):
        (self.root/'session_metadata.json').unlink()
        self.assertEqual(self.run_audit()['status'],'ALERT')

    def test_malformed_jsonl_alert(self):
        (self.root/'events.jsonl').write_text('{broken\n')
        self.assertIn('EVENTS_JSONL_INVALID_EVENT_JSONL',self.run_audit()['alerts'])

    def test_jsonl_array_rejected(self):
        (self.root/'events.jsonl').write_text('[]\n')
        self.assertEqual(self.run_audit()['status'],'ALERT')

    def test_invalid_result_object(self):
        (self.root/'session_result.json').write_text('[]')
        self.assertEqual(self.run_audit()['status'],'ALERT')

    def test_unrecognized_event_schema_alert(self):
        (self.root/'events.jsonl').write_text('{"message":"no type"}\n')
        self.assertEqual(self.run_audit()['status'],'ALERT')

    def test_unrecognized_time_schema_holds(self):
        setup(self.root, events=[{'event':'recording_start','timestamp':'2026-10-30T00:00:00Z'}])
        x=self.run_audit()
        self.assertIn('EVENT_TIME_SCHEMA_INCOMPLETE_OR_UNRECOGNIZED',x['holds'])

    def test_non_monotonic_alert(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':4}, {'event':'recording_stop','t_seconds':1}])
        self.assertIn('EVENT_TIMES_OUT_OF_ORDER',self.run_audit()['alerts'])

    def test_negative_time_holds(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':-1}])
        self.assertEqual(self.run_audit()['status'],'UNCONFIRMED')

    def test_boolean_time_holds(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':True}])
        self.assertEqual(self.run_audit()['status'],'UNCONFIRMED')

    def test_missing_question_end_alert(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':0},
                                 {'event':'question_start','t_seconds':1},
                                 {'event':'recording_stop','t_seconds':8}])
        self.assertIn('QUESTION_START_WITHOUT_END',self.run_audit()['alerts'])

    def test_extra_question_end_alert(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':0},
                                 {'event':'question_end','t_seconds':1},
                                 {'event':'recording_stop','t_seconds':8}])
        self.assertIn('QUESTION_END_WITHOUT_START',self.run_audit()['alerts'])

    def test_overlapping_question_alert(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':0},
                                 {'event':'question_start','t_seconds':1},
                                 {'event':'question_start','t_seconds':2},
                                 {'event':'question_end','t_seconds':3},
                                 {'event':'recording_stop','t_seconds':8}])
        self.assertIn('OVERLAPPING_QUESTION_MARKERS',self.run_audit()['alerts'])

    def test_missing_stop_holds(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':0}])
        self.assertIn('RECORDING_START_STOP_MARKERS_MISSING',self.run_audit()['holds'])

    def test_duplicate_stop_alert(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':0},
                                 {'event':'recording_stop','t_seconds':7},
                                 {'event':'recording_stop','t_seconds':8}])
        self.assertIn('DUPLICATE_RECORDING_STOP',self.run_audit()['alerts'])

    def test_duration_mismatch_alert(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':0},
                                 {'event':'recording_stop','t_seconds':120}])
        self.assertIn('LOG_WAV_DURATION_MISMATCH',self.run_audit()['alerts'])

    def test_error_event_alert(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':0},
                                 {'event':'writer_error','t_seconds':2},
                                 {'event':'recording_stop','t_seconds':8}])
        self.assertIn('LOG_REPORTED_RECORDING_OR_DEVICE_ERROR',self.run_audit()['alerts'])

    def test_result_failure_alert(self):
        setup(self.root, result={'status':'failed'})
        self.assertIn('RESULT_REPORTED_FAILURE',self.run_audit()['alerts'])

    def test_missing_wav_alert(self):
        (self.root/'room_mic_continuous.wav').unlink()
        self.assertIn('WAV_STRUCTURAL_AUDIT_NOT_CLEAN',self.run_audit()['alerts'])

    def test_expected_duration_alert(self):
        self.assertIn('WAV_STRUCTURAL_AUDIT_NOT_CLEAN',self.run_audit(expected_minutes=1)['alerts'])

    def test_symlink_events_rejected(self):
        p=self.root/'events.jsonl'; data=p.read_bytes(); p.unlink()
        target=self.root/'other.txt'; target.write_bytes(data)
        p.symlink_to(target)
        self.assertIn('EVENTS_JSONL_SOURCE_SYMLINK_REJECTED',self.run_audit()['alerts'])

    def test_event_oversized_line_rejected(self):
        (self.root/'events.jsonl').write_text(json.dumps({'event':'x','data':'x'*70000})+'\n')
        self.assertEqual(self.run_audit()['status'],'ALERT')

    def test_no_raw_event_text_in_report(self):
        setup(self.root, events=[{'event':'recording_start','t_seconds':0,'secret':'sensitive_text'},
                                 {'event':'recording_stop','t_seconds':8}])
        self.assertNotIn('sensitive_text',json.dumps(self.run_audit()))

    def test_file_size_limit(self):
        p=self.root/'events.jsonl'; p.write_bytes(b'x'*(16*1024*1024+1))
        self.assertIn('EVENTS_JSONL_SOURCE_EXCEEDS_SIZE_LIMIT',self.run_audit()['alerts'])

    def test_parse_multiple_time_fields(self):
        ev,ct=_parse_events(b'{"type":"recording_start","elapsed_seconds":0}\n')
        self.assertEqual(ev,[('recording_start',0.0)])

    def test_no_source_path_leak(self):
        self.assertNotIn(str(self.root),json.dumps(self.run_audit()))


if __name__=='__main__': unittest.main()