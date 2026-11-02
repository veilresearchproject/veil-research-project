import unittest
from unittest.mock import patch
from windows_voice_demo import run, SAMPLE
from voice_pipeline import VoicePipeline
from playback_adapter import play_remaining

class DemoTests(unittest.TestCase):
    def test_dry_run_complete(self):
        result,pipe,delivered=run(SAMPLE,max_chars=32)
        self.assertTrue(result.completed)
        self.assertEqual(' '.join(delivered),pipe.plan.original)
        self.assertGreater(len(delivered),1)
    def test_no_real_speaker_in_default_mode(self):
        with patch('windows_voice_demo.speak_windows_blocking',side_effect=AssertionError('unexpected live audio')):
            self.assertTrue(run()[0].completed)
    def test_live_opt_in_mock(self):
        spoken=[]
        with patch('windows_voice_demo.speak_windows_blocking',side_effect=lambda s: spoken.append(s) or True):
            result,pipe,_=run(live_windows=True,max_chars=32)
        self.assertTrue(result.completed)
        self.assertEqual(' '.join(spoken),pipe.plan.original)
    def test_simulated_engine_failure_stops(self):
        p=VoicePipeline(SAMPLE,max_chars=32)
        called=[]
        def fail_second(s):
            called.append(s)
            if len(called)==2:raise RuntimeError('device not ready')
            return True
        result=play_remaining(p,fail_second)
        self.assertFalse(result.completed)
        self.assertEqual(result.failed_index,1)
        self.assertEqual(p.tracker.completed_chunks,1)
        self.assertEqual(result.error,'RuntimeError')
    def test_resume_failed_chunk(self):
        p=VoicePipeline(SAMPLE,max_chars=32)
        times=[0]
        def fail_second_once(s):
            times[0]+=1
            return times[0]!=2
        first=play_remaining(p,fail_second_once)
        self.assertFalse(first.completed)
        self.assertEqual(p.retry_failed(),1)
        second=play_remaining(p,lambda _:True)
        self.assertTrue(second.completed)
        self.assertEqual(first.played_now+second.played_now,len(p.plan.chunks))
    def test_false_veil_identity_rejected(self):
        with self.assertRaises(ValueError):run('VEIL means Viral Epidemiology and Infection Lineage.')

if __name__=='__main__':unittest.main()
