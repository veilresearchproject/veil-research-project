"""Synthetic completed-session integration tests for v0.2 (not live evidence)."""
from __future__ import annotations
import csv
import hashlib
import json
import math
import tempfile
import unittest
import wave
from datetime import datetime, timedelta, timezone
from pathlib import Path
from evidence_review_pack import build_pack, write_pack


RATE = 8000
SEGMENT_SECONDS = (60, 30)  # 90-second synthetic test: NOT an actual 90-minute run.


def create_fixture(root):
    session = root/'SYNTHETIC_MTC_SPLIT_90_SECONDS'
    session.mkdir()
    # Synthetic 1-second PCM chunks; no real microphone or speaker capture.
    def tone(amp):
        return b''.join(int(amp*math.sin(2*math.pi*173*i/RATE)).to_bytes(2,'little',signed=True)
                        for i in range(RATE))
    quiet=tone(65)
    burst=tone(11000)
    position=0
    for part,duration in enumerate(SEGMENT_SECONDS,1):
        name='room_mic_continuous.wav' if part==1 else f'room_mic_continuous_part{part:03d}.wav'
        with wave.open(str(session/name),'wb') as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(RATE)
            for second in range(position,position+duration):
                out.writeframesraw(burst if second in (10,65) else quiet)
        position += duration
    stamp=datetime(2026,10,27,21,50,tzinfo=timezone(timedelta(hours=-4)))
    events=[]
    for name,offset in [('recording_start',0),('question_start',10),('question_end',11),('recording_stop',90)]:
        events.append({'type':name,'timestamp':(stamp+timedelta(seconds=offset)).isoformat()})
    (session/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events),encoding='utf-8')
    (session/'session_result.json').write_text(json.dumps({'NOTE':'SYNTHETIC_ONLY'}),encoding='utf-8')
    (session/'session_metadata.json').write_text(json.dumps({'NOTE':'SYNTHETIC_ONLY'}),encoding='utf-8')
    return session


class SyntheticSplitTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='veil-synthetic-split-')
        self.root=Path(self.tmp.name)
        self.folder=create_fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_synthetic_total_and_two_segments(self):
        result=build_pack(self.folder)
        self.assertEqual(result['mtc']['total_wav_duration_seconds'],90.0)
        self.assertEqual(len(result['mtc']['wav_segments']),2)
        self.assertEqual(result['mtc']['events']['question_pairs'],1)
        self.assertEqual(result['mtc']['events']['alignment'],
                         'MARKER_OFFSETS_PLAUSIBLE_NOT_ACOUSTICALLY_VERIFIED')
        self.assertFalse(result['mtc']['physical_acoustic_playback_confirmed'])

    def test_loud_bursts_in_both_segments_and_question_kept(self):
        pack=build_pack(self.folder)
        candidates=pack['signal']['candidates']
        self.assertGreaterEqual(len(candidates),2)
        self.assertTrue(any(c['origin_file']=='room_mic_continuous.wav' for c in candidates))
        self.assertTrue(any(c['origin_file']=='room_mic_continuous_part002.wav' for c in candidates))
        self.assertTrue(any(c['possibly_near_question_marker'] is True for c in candidates))
        self.assertTrue(all(c['requires_human_review'] for c in candidates))

    def test_optin_clips_are_derived_and_original_hashes_constant(self):
        originals={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.folder.iterdir()}
        pack=write_pack(self.folder,self.root/'review',make_clips=True,max_clips=6)
        self.assertGreaterEqual(len(pack['derived_clips']),2)
        for entry in pack['derived_clips']:
            self.assertTrue(entry['clip_is_derived_not_original'])
            self.assertTrue((self.root/'review'/'clips'/entry['clip_file']).is_file())
        self.assertEqual(originals,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.folder.iterdir()})
        self.assertFalse((self.folder/'candidate_review.csv').exists())

    def test_candidate_csv_remains_unreviewed(self):
        pack=write_pack(self.folder,self.root/'review')
        with (self.root/'review'/'candidate_review.csv').open(newline='',encoding='utf-8') as fp:
            rows=list(csv.DictReader(fp))
        self.assertEqual(len(rows),pack['signal']['candidate_count'])
        self.assertTrue(all(r['human_classification']=='UNREVIEWED' for r in rows))

    def test_missing_middle_segment_is_not_assumed_contiguous(self):
        old=self.folder/'room_mic_continuous_part002.wav'
        old.rename(self.folder/'room_mic_continuous_part003.wav')
        pack=build_pack(self.folder)
        self.assertIn('SEGMENT_NUMBERS_MISSING_OR_DUPLICATE',
                      [r['code'] for r in pack['mtc']['issues']])
        self.assertIn('NON_ADJACENT_SEGMENT_NUMBERS_NO_COMPARISON',
                      pack['seams']['boundaries'][0]['issues'])

    def test_source_timeline_never_claims_real_continuity(self):
        pack=build_pack(self.folder)
        self.assertTrue(pack['segment_global_offsets_are_assumed'])
        self.assertFalse(pack['seams']['proves_gapless_recording'])
        self.assertIn('UNVERIFIED',pack['mtc']['segment_file_boundary_continuity'])
        self.assertFalse(pack['mtc']['paranormal_cause_established'])


if __name__=='__main__':
    unittest.main()
