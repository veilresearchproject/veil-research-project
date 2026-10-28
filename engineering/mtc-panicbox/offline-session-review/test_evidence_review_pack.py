"""Synthetic-only validation of opt-in derived outputs and source integrity."""
import copy
import hashlib
import json
import tempfile
import unittest
import wave
from pathlib import Path
from evidence_review_pack import build_pack, write_pack, _sha256_file, _verify_dest
from test_offline_review import make_session, make_wav


class ReviewPackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.session = self.root / 'MTC_test'
        self.session.mkdir()
        make_session(self.session, events=False)

    def tearDown(self):
        self.temp.cleanup()

    def test_hashes_are_repeatable(self):
        hashes = build_pack(self.session)['inventory']['files']
        self.assertEqual({r['file'] for r in hashes},
                         {'room_mic_continuous.wav','session_metadata.json','session_result.json','events.jsonl'})
        self.assertIn('UNREADABLE_OR_UNSAFE', {x['status'] for x in hashes})
        wav_row = next(r for r in hashes if r['file'].endswith('.wav'))
        self.assertEqual(wav_row['sha256'], hashlib.sha256((self.session / wav_row['file']).read_bytes()).hexdigest())

    def test_known_question_is_not_silently_discarded(self):
        make_session(self.session)
        result = build_pack(self.session)
        self.assertGreater(result['signal']['candidate_count'], 0)
        self.assertTrue(any(c['possibly_near_question_marker'] is True
                            for c in result['signal']['candidates']))
        self.assertTrue(all(c['human_label'] == 'UNREVIEWED' for c in result['signal']['candidates']))
        self.assertFalse(result['mtc']['physical_acoustic_playback_confirmed'])

    def test_question_without_known_alignment_is_uncertain(self):
        result = build_pack(self.session)
        self.assertTrue(all(c['possibly_near_question_marker'] is None for c in result['signal']['candidates']))

    def test_wav_segments_are_assumed_not_proven(self):
        make_wav(self.session / 'room_mic_continuous_part002.wav', seconds=1)
        result = build_pack(self.session)
        self.assertTrue(result['segment_global_offsets_are_assumed'])
        self.assertIn('UNVERIFIED', result['mtc']['segment_file_boundary_continuity'])

    def test_readonly_report_does_not_touch_origins(self):
        originals = {p.name: p.read_bytes() for p in self.session.iterdir()}
        result = write_pack(self.session, self.root / 'new-report')
        self.assertTrue((self.root / 'new-report' / 'review.json').exists())
        self.assertEqual(result['derived_clips'], [])
        self.assertEqual(originals, {p.name: p.read_bytes() for p in self.session.iterdir()})

    def test_optin_clips_are_external_and_pcm_valid(self):
        make_session(self.session)
        originals = {p.name: p.read_bytes() for p in self.session.iterdir()}
        result = write_pack(self.session, self.root / 'derived', make_clips=True)
        clips = result['derived_clips']
        self.assertGreater(len(clips), 0)
        clip = self.root / 'derived' / 'clips' / clips[0]['clip_file']
        self.assertEqual(clips[0]['sha256'], hashlib.sha256(clip.read_bytes()).hexdigest())
        with wave.open(str(clip), 'rb') as w:
            self.assertEqual(w.getsampwidth(), 2)
            self.assertGreater(w.getnframes(), 0)
        self.assertEqual(originals, {p.name: p.read_bytes() for p in self.session.iterdir()})

    def test_report_not_inside_evidence_folder(self):
        with self.assertRaises(ValueError):
            write_pack(self.session, self.session / 'review')

    def test_refuse_existing_report_folder(self):
        target = self.root / 'there'
        target.mkdir()
        with self.assertRaises(FileExistsError):
            write_pack(self.session, target)

    def test_refuse_nonexistent_parent(self):
        with self.assertRaises(ValueError):
            write_pack(self.session, self.root / 'not-created' / 'report')

    def test_symlink_hash_fails_closed(self):
        src = self.session / 'events.jsonl'
        src.unlink(missing_ok=True)
        try:
            src.symlink_to(self.session / 'session_result.json')
        except (OSError, NotImplementedError):
            self.skipTest('symlinks not supported in this test environment')
        result = _sha256_file(src)
        self.assertEqual(result['status'], 'UNREADABLE_OR_UNSAFE')

    def test_clip_export_refuses_missing_logs(self):
        with self.assertRaises(ValueError):
            write_pack(self.session, self.root / 'derived', make_clips=True)
        self.assertFalse((self.root / 'derived').exists())

    def test_invalid_padding_rejected(self):
        with self.assertRaises(ValueError):
            write_pack(self.session, self.root / 'derived', padding_seconds=6)
        self.assertFalse((self.root / 'derived').exists())

    def test_corrupt_wav_is_still_fingerprinted_as_evidence(self):
        (self.session/'room_mic_continuous_part002.wav').write_bytes(b'corrupt WAV header')
        found=build_pack(self.session)['inventory']['files']
        self.assertIn('room_mic_continuous_part002.wav', {x['file'] for x in found})
    def test_no_candidate_for_silent_file(self):
        make_wav(self.session / 'room_mic_continuous.wav', seconds=2)
        pack = build_pack(self.session)
        self.assertEqual(pack['signal']['candidate_count'], 0)

    def test_clip_20second_cap(self):
        # When an excursion lasts far longer, clip bounds must stay limited.
        make_wav(self.session / 'room_mic_continuous.wav', seconds=32,
                 bursts=[(10, 31, 14000)])
        make_session(self.session)
        # Regenerate the WAV after the metadata was generated.
        make_wav(self.session / 'room_mic_continuous.wav', seconds=32,
                 bursts=[(10, 31, 14000)])
        pack = write_pack(self.session, self.root / 'report', make_clips=True)
        self.assertTrue(all(c['clip_duration_seconds'] <= 20 for c in pack['derived_clips']))

    def test_original_report_has_no_paranormal_determination(self):
        pack = build_pack(self.session)
        self.assertFalse(pack['mtc']['paranormal_cause_established'])
        self.assertEqual(pack['audio_classification'], 'AMPLITUDE_CHANGE_ONLY_NOT_SPEECH_OR_EVP')


class AnnotationCSVTests(unittest.TestCase):
    def test_candidate_spreadsheet_is_generated_outside_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            folder=root/'synthetic';folder.mkdir()
            make_session(folder)
            report=root/'derived'
            pack=write_pack(folder, report)
            csv_path=report/'candidate_review.csv'
            self.assertTrue(csv_path.exists())
            text=csv_path.read_text(encoding='utf-8')
            self.assertIn('human_classification', text)
            self.assertIn('UNREVIEWED', text)
            self.assertFalse((folder/'candidate_review.csv').exists())
            self.assertEqual(text.count('VEIL-C'), pack['signal']['candidate_count'])

if __name__ == '__main__':
    unittest.main()
