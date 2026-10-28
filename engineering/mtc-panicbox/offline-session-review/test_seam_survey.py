"""Synthetic-only seam heuristics. Equal edge levels never prove continuity."""
import tempfile
import unittest
from pathlib import Path
from test_offline_review import make_wav
from session_validator import wav_summary
from seam_survey import survey

class SeamTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.folder=Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def _survey(self):
        wavs,_ = wav_summary(self.folder)
        return survey(self.folder,wavs)
    def test_one_file_no_seam(self):
        make_wav(self.folder/'room_mic_continuous.wav',seconds=1)
        self.assertEqual(self._survey()['boundaries_examined'],0)
    def test_both_silent_does_not_prove_continuity(self):
        make_wav(self.folder/'room_mic_continuous.wav',seconds=1)
        make_wav(self.folder/'room_mic_continuous_part002.wav',seconds=1)
        out=self._survey()
        self.assertFalse(out['proves_gapless_recording'])
        self.assertIn('NEAR_SILENT_BOUNDARY_EDGE_REVIEW',out['boundaries'][0]['issues'])
    def test_large_change_flagged(self):
        make_wav(self.folder/'room_mic_continuous.wav',seconds=1,bursts=[(0,.99,24000)])
        make_wav(self.folder/'room_mic_continuous_part002.wav',seconds=1)
        self.assertIn('LARGE_EDGE_LEVEL_DIFFERENCE_REVIEW',self._survey()['boundaries'][0]['issues'])
    def test_no_spurious_jump_for_matching_noise(self):
        make_wav(self.folder/'room_mic_continuous.wav',seconds=1,bursts=[(0,1,12000)])
        make_wav(self.folder/'room_mic_continuous_part002.wav',seconds=1,bursts=[(0,1,12000)])
        self.assertNotIn('LARGE_EDGE_LEVEL_DIFFERENCE_REVIEW',self._survey()['boundaries'][0]['issues'])
    def test_corrupt_second_file_fails_closed(self):
        make_wav(self.folder/'room_mic_continuous.wav',seconds=1)
        (self.folder/'room_mic_continuous_part002.wav').write_bytes(b'bad')
        wavs,_ = wav_summary(self.folder)
        self.assertEqual(len(wavs),1)
        self.assertEqual(survey(self.folder,wavs)['boundaries_examined'],0)
    def test_missing_middle_segment_not_compared_as_adjacent(self):
        make_wav(self.folder/'room_mic_continuous.wav',seconds=1)
        make_wav(self.folder/'room_mic_continuous_part003.wav',seconds=1)
        r=self._survey()
        self.assertIn('NON_ADJACENT_SEGMENT_NUMBERS_NO_COMPARISON',r['boundaries'][0]['issues'])
        self.assertNotIn('difference_db',r['boundaries'][0])
    def test_parameter_validation(self):
        with self.assertRaises(ValueError):survey(self.folder, [], edge_seconds=10)

if __name__=='__main__': unittest.main()
