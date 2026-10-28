"""Synthetic benchmark invariants — never proof of EVP or field performance."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import wave
from signal_synthetic_benchmark import PROFILES, DURATION, generate_wav, measure


class SignalBenchmarkTests(unittest.TestCase):
    def test_profiles_cover_negative_positive_and_known_limitations(self):
        self.assertIn('NEGATIVE', PROFILES.values())
        self.assertIn('CLEAR_SOUND', PROFILES.values())
        self.assertIn('NOT_TESTABLE_BY_LEVEL_RISE', PROFILES.values())

    def test_generated_pcm_format_and_duration(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'test.wav'
            generate_wav(path,'hard_tone',16000,2,2)
            with wave.open(str(path),'rb') as f:
                self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes()),
                                 (2,2,16000,round(DURATION*16000)))

    def test_no_audio_data_modified_by_measure(self):
        report=measure(seeds=1)
        self.assertTrue(report['synthetic_only'])
        self.assertFalse(report['source_evidence_processed'])
        self.assertEqual(report['cases'],len(PROFILES)*2)

    def test_reproducible_metrics(self):
        first=measure(seeds=1)
        second=measure(seeds=1)
        self.assertEqual(first,second)

    def test_nonrepresentative_limitations_preserved(self):
        rep=measure(seeds=1)
        self.assertIn('not sensitivity to EVP',rep['limitations'])
        self.assertFalse(rep['model_inference_performed'])

    def test_case_counts_and_row_provenance(self):
        rep=measure(seeds=1)
        self.assertEqual(rep['negative_cases'],6)
        self.assertEqual(rep['clear_sound_cases'],6)
        self.assertEqual(rep['exploratory_cases'],6)
        self.assertTrue(all(len(r['synthetic_sha256'])==64 for r in rep['rows']))

    def test_invalid_seed_counts_rejected(self):
        for value in (0,11,True,'2',1.5):
            with self.subTest(value=value),self.assertRaises(ValueError):
                measure(seeds=value)

    def test_all_positive_profiles_present(self):
        rep=measure(seeds=1)
        self.assertEqual({r['profile'] for r in rep['rows']},set(PROFILES))

    def test_silent_negative_not_falsely_reported(self):
        rep=measure(seeds=1)
        silent=[r for r in rep['rows'] if r['profile']=='silence']
        self.assertTrue(all(r['candidate_count']==0 for r in silent))

    def test_strong_tone_detected(self):
        rep=measure(seeds=1)
        tone=[r for r in rep['rows'] if r['profile']=='hard_tone']
        self.assertTrue(all(r['hit'] for r in tone))

    def test_fixed_thresholds_are_explicit(self):
        rep=measure(seeds=1)
        self.assertEqual(rep['fixed_thresholds']['delta_db'],12.0)


if __name__=='__main__':
    unittest.main()
