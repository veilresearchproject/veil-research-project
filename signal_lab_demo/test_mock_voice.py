import unittest
from mock_voice import mock_voice_turn

CONTEXT = dict(source='VERIFIED_LOCAL_SYNTHETIC_BUNDLE', real_sensor_data=False, physical_control_allowed=False, unreviewed_case_count=3)

class MockVoiceTests(unittest.TestCase):
    def test_read_only_summary(self):
        spoken=[]
        result=mock_voice_turn('What is the status?',lambda: CONTEXT,spoken.append)
        self.assertEqual(spoken,[result['spoken_text']]);self.assertIn('3 unreviewed',spoken[0]);self.assertFalse(result['model_connected'])
    def test_control_refusal_does_not_load_context(self):
        spoken=[]
        def forbidden():raise AssertionError('context must not be loaded')
        mock_voice_turn('Start MTC',forbidden,spoken.append)
        self.assertIn('cannot control equipment',spoken[0])
    def test_nonquestion_personality_without_context(self):
        spoken=[]
        mock_voice_turn('Hello SIGNAL',lambda: (_ for _ in ()).throw(AssertionError()),spoken.append)
        self.assertIn('curious',spoken[0])
    def test_rejects_untrusted_context(self):
        for context in ({**CONTEXT,'real_sensor_data':True},{**CONTEXT,'source':'LIVE'},{**CONTEXT,'unreviewed_case_count':True}):
            with self.subTest(context=context),self.assertRaises(ValueError):mock_voice_turn('summary',lambda:context,lambda _:None)
    def test_rejects_invalid_transcript(self):
        for value in ('', 'a'*241, None, chr(0)+'hi'):
            with self.subTest(value=value),self.assertRaises(ValueError):mock_voice_turn(value,lambda:CONTEXT,lambda _:None)
    def test_requires_callbacks(self):
        with self.assertRaises(TypeError):mock_voice_turn('status',None,lambda _:None)
    def test_summarize_routes_to_verified_context(self):
        spoken=[]
        result=mock_voice_turn('Signal, please summarize the lab',lambda:CONTEXT,spoken.append)
        self.assertEqual(spoken,[result['spoken_text']])
        self.assertIn('3 unreviewed threshold windows',spoken[0])
        self.assertNotIn('My circuits are curious',spoken[0])
    def test_summarize_rejects_untrusted_context(self):
        spoken=[]
        with self.assertRaises(ValueError):
            mock_voice_turn('Summarize the lab',lambda:{**CONTEXT,'real_sensor_data':True},spoken.append)
        self.assertEqual(spoken,[])
    def test_no_network_or_microphone(self):
        import inspect,mock_voice
        source=inspect.getsource(mock_voice)
        for forbidden in ('import requests','import socket','import pyaudio','subprocess','urlopen('):self.assertNotIn(forbidden,source)

if __name__=='__main__':unittest.main()
