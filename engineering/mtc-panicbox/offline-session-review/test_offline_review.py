"""Deterministic synthetic tests; not real MTC evidence or acoustic validation."""
from __future__ import annotations
import json
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from session_validator import review
from signal_audio_screener import scan
from run_review import main


def make_wav(path, *, seconds=2, rate=4000, noise=0, bursts=(), channels=1):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        for i in range(int(rate*seconds)):
            t=i/rate
            amp=next((volume for start,end,volume in bursts if start<=t<end),noise)
            v=int(amp*math.sin(2*math.pi*173*t))
            w.writeframesraw(struct.pack('<h',v)*channels)


def make_session(folder, *, events=True, second=False):
    make_wav(folder/'room_mic_continuous.wav',seconds=2,bursts=[(1,1.5,12000)])
    if second:
        make_wav(folder/'room_mic_continuous_part002.wav',seconds=1)
    (folder/'session_result.json').write_text('{"result":"simulated"}', encoding='utf8')
    (folder/'session_metadata.json').write_text('{"source":"synthetic"}', encoding='utf8')
    if events:
        events=[{'type':'recording_start','timestamp':'2026-10-27T21:50:00-04:00'},
                {'type':'question_start','timestamp':'2026-10-27T21:50:01-04:00'},
                {'type':'question_end','timestamp':'2026-10-27T21:50:01.500-04:00'},
                {'type':'recording_stop','timestamp':'2026-10-27T21:50:02-04:00'}]
        (folder/'events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in events),encoding='utf8')


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.folder=Path(self.temp.name)/'session'
        self.folder.mkdir()
    def tearDown(self):
        self.temp.cleanup()

    def test_wav_duration(self):
        make_session(self.folder)
        self.assertEqual(review(self.folder)['total_wav_duration_seconds'],2.0)
    def test_unknown_schema_fails_closed(self):
        make_session(self.folder, events=False)
        (self.folder/'events.jsonl').write_text('{"event":"mystery"}\n',encoding='utf8')
        r=review(self.folder)
        self.assertEqual(r['events']['alignment'],'NOT_VERIFIED')
        self.assertIn('EVENT_SCHEMA_UNRECOGNIZED',[x['code'] for x in r['issues']])
    def test_question_pair(self):
        make_session(self.folder)
        r=review(self.folder)
        self.assertEqual(r['events']['question_pairs'],1)
        self.assertEqual(r['events']['question_windows_seconds'],[[1.0,1.5]])
    def test_missing_event_log(self):
        make_session(self.folder,events=False)
        self.assertIn('EVENT_LOG_MISSING_UNSAFE_OR_TOO_LARGE',[x['code'] for x in review(self.folder)['issues']])
    def test_malformed_event(self):
        make_session(self.folder)
        with (self.folder/'events.jsonl').open('a') as f:f.write('broken\n')
        self.assertIn('MALFORMED_EVENT_JSON',[x['code'] for x in review(self.folder)['issues']])
    def test_duplicate_marker(self):
        make_session(self.folder)
        events=self.folder/'events.jsonl'
        text=events.read_text()
        events.write_text(text.splitlines(True)[0]+text,encoding='utf8')
        self.assertIn('DUPLICATE_RECORDING_START',[x['code'] for x in review(self.folder)['issues']])
    def test_missing_segment_part(self):
        make_session(self.folder)
        make_wav(self.folder/'room_mic_continuous_part003.wav',seconds=1)
        self.assertIn('SEGMENT_NUMBERS_MISSING_OR_DUPLICATE',[x['code'] for x in review(self.folder)['issues']])
    def test_split_files_never_prove_continuity(self):
        make_session(self.folder,second=True)
        self.assertEqual(review(self.folder)['segment_file_boundary_continuity'],'UNVERIFIED_WITHOUT_INDEPENDENT_TIME_ANCHORS')
    def test_corrupt_wav(self):
        (self.folder/'room_mic_continuous.wav').write_bytes(b'junk')
        r=review(self.folder)
        self.assertIn('WAV_CANNOT_OPEN',[x['code'] for x in r['issues']])
    def test_no_wav(self):
        self.assertIn('NO_EXPECTED_WAV_FILES',[x['code'] for x in review(self.folder)['issues']])
    def test_missing_json(self):
        make_session(self.folder)
        (self.folder/'session_metadata.json').unlink()
        self.assertIn('SESSION_JSON_MISSING_OR_INVALID',[x['code'] for x in review(self.folder)['issues']])
    def test_detect_burst(self):
        make_session(self.folder,events=False)
        r=review(self.folder)
        sig=scan(self.folder,r['wav_segments'],floor_dbfs=-50)
        self.assertGreater(sig['candidate_count'],0)
        self.assertFalse(sig['evp_classification_performed'])
    def test_mask_question(self):
        make_session(self.folder)
        r=review(self.folder)
        sig=scan(self.folder,r['wav_segments'],question_windows=r['events']['question_windows_seconds'],question_alignment=True)
        self.assertEqual(sig['candidate_count'],0)
        self.assertTrue(sig['question_masking_used'])
    def test_no_mask_without_time_mapping(self):
        make_session(self.folder)
        r=review(self.folder)
        sig=scan(self.folder,r['wav_segments'],question_windows=[[1,1.5]],question_alignment=False)
        self.assertGreater(sig['candidate_count'],0)
    def test_silence_never_candidate(self):
        make_wav(self.folder/'room_mic_continuous.wav',seconds=2)
        sig=scan(self.folder,review(self.folder)['wav_segments'])
        self.assertEqual(sig['candidate_count'],0)
    def test_late_timestamps_flagged(self):
        make_session(self.folder)
        path=self.folder/'events.jsonl'
        data=[json.loads(x) for x in path.read_text().splitlines()]
        data[2]['timestamp']='2026-10-27T21:49:50-04:00'
        path.write_text(''.join(json.dumps(x)+'\n' for x in data),encoding='utf8')
        self.assertIn('NON_INCREASING_MARKER_TIME',[x['code'] for x in review(self.folder)['issues']])
    def test_event_log_oversize(self):
        make_session(self.folder)
        with (self.folder/'events.jsonl').open('ab') as f:f.truncate(16*1024*1024+1)
        self.assertIn('EVENT_LOG_MISSING_UNSAFE_OR_TOO_LARGE',[x['code'] for x in review(self.folder)['issues']])
    def test_refuses_write_inside_evidence_folder(self):
        make_session(self.folder)
        with self.assertRaises(SystemExit):
            main([str(self.folder),'--output',str(self.folder/'report.json')])
    def test_refuses_overwrite(self):
        make_session(self.folder)
        output=Path(self.temp.name)/'report.json'
        output.write_text('do not overwrite')
        with self.assertRaises(SystemExit):
            main([str(self.folder),'--output',str(output)])
        self.assertEqual(output.read_text(),'do not overwrite')
    def test_original_bytes_unchanged(self):
        make_session(self.folder)
        paths=list(self.folder.iterdir())
        original={p.name:p.read_bytes() for p in paths}
        r=review(self.folder)
        scan(self.folder,r['wav_segments'])
        self.assertEqual(original,{p.name:p.read_bytes() for p in paths})
    def test_multichannel(self):
        make_wav(self.folder/'room_mic_continuous.wav',seconds=2,channels=2,bursts=[(1,1.5,14000)])
        sig=scan(self.folder,review(self.folder)['wav_segments'])
        self.assertGreater(sig['candidate_count'],0)
    def test_invalid_threshold_rejected(self):
        with self.assertRaises(ValueError):scan(self.folder,[],delta_db=-2)

if __name__=='__main__':unittest.main()
