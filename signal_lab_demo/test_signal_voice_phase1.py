"""Offline tests for six SIGNAL mock voice enhancements."""
import unittest
from unittest.mock import patch
from signal_voice_phase1 import (OfflineResearchVoiceSession, check_intent,
                                make_receipt, normalize_transcript, scripted_rehearsal)

SAFE = {'transcript': 'status', 'spoken_text': 'Synthetic: 3 unreviewed windows; human review required.', 'synthetic_only': True, 'model_connected': False, 'physical_control_allowed': False}

class SessionTests(unittest.TestCase):
    def test_01_normalize(self):
        self.assertEqual(normalize_transcript('  lab\nstatus  '), 'lab status')
        for bad in (None, '', '  ', 'x'*241, '\x00bad'):
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError): normalize_transcript(bad)
    def test_02_controls(self):
        for text in ('Turn on camera', 'Begin experiment', 'Activate MTC', 'Power up panic box', 'Launch perfect storm'):
            self.assertEqual(check_intent(text), 'control')
        self.assertEqual(check_intent('What is the lab status?'), 'read_only')
        self.assertEqual(check_intent('Show me private evidence'), 'private')
    def test_03_receipt_privacy(self):
        r = make_receipt('private evidence', 'Denied', 'private')
        self.assertEqual(len(r['sha256']), 64)
        self.assertNotIn('private evidence', str(r))
        self.assertFalse(r['content_saved'])
    @patch('signal_voice_phase1.research_voice_turn')
    def test_04_read_only_uses_verified_bridge(self, bridge):
        def run(text, folder, speak):
            speak(SAFE['spoken_text']); return dict(SAFE)
        bridge.side_effect = run
        session = OfflineResearchVoiceSession('/test',history_limit=2)
        spoken=[]; r=session.turn('status', spoken.append)
        self.assertEqual(spoken, [SAFE['spoken_text']]);self.assertEqual(r['receipt']['intent'],'read_only')
        self.assertEqual(len(session.recent_receipts()),1)
    @patch('signal_voice_phase1.research_voice_turn', side_effect=AssertionError('not called'))
    def test_05_commands_bypass_research(self, bridge):
        s=OfflineResearchVoiceSession('/missing'); spoken=[]
        r=s.turn('Turn on camera', spoken.append)
        self.assertIn('cannot control',r['spoken_text']); bridge.assert_not_called()
    @patch('signal_voice_phase1.research_voice_turn', side_effect=AssertionError('not called'))
    def test_06_privacy_bypasses_research(self, bridge):
        s=OfflineResearchVoiceSession('/missing'); spoken=[]
        self.assertIn('Private records',s.turn('Send private email',spoken.append)['spoken_text'])
        bridge.assert_not_called()
    @patch('signal_voice_phase1.research_voice_turn')
    def test_07_bounded_history_and_clear(self, bridge):
        def run(t,b,speak): speak(SAFE['spoken_text']);return dict(SAFE)
        bridge.side_effect=run
        s=OfflineResearchVoiceSession('/test',2)
        for _ in range(4): s.turn('status',lambda _:None)
        self.assertEqual(len(s.recent_receipts()),2);s.clear();self.assertFalse(s.recent_receipts())
    def test_08_invalid_history(self):
        for v in (0,13,True,1.5):
            with self.assertRaises(ValueError): OfflineResearchVoiceSession('/test',v)
    @patch('signal_voice_phase1.research_voice_turn', side_effect=ValueError('bundle damaged'))
    def test_09_failed_verification_does_not_log(self,bridge):
        s=OfflineResearchVoiceSession('/test');spoken=[]
        with self.assertRaises(ValueError): s.turn('status',spoken.append)
        self.assertEqual(spoken,[]);self.assertEqual(s.recent_receipts(),())
    @patch('signal_voice_phase1.research_voice_turn')
    def test_10_rehearsal(self, bridge):
        def run(t,b,speak): speak(SAFE['spoken_text']);return dict(SAFE)
        bridge.side_effect=run
        r=scripted_rehearsal('/test',['status','Turn on camera','Show me private evidence'])
        self.assertEqual(len(r['turns']),3);self.assertTrue(r['synthetic_only']);bridge.assert_called_once()
    def test_11_rehearsal_bounds(self):
        for transcripts in ([], ['status']*21, 'status'):
            with self.assertRaises(ValueError): scripted_rehearsal('/test',transcripts)
    @patch('signal_voice_phase1.research_voice_turn',return_value={**SAFE,'model_connected':True})
    def test_12_unsafe_bridge_rejected(self, bridge):
        with self.assertRaises(ValueError): OfflineResearchVoiceSession('/test').turn('status',lambda _:None)

if __name__=='__main__':unittest.main()
