import io
import json
import unittest
from unittest.mock import Mock, patch

import signal_core
import signal_voice


class VoiceTests(unittest.TestCase):
    def test_off_by_default_never_launches(self):
        v = signal_voice.WindowsVoice()
        with patch.object(signal_voice.subprocess, 'Popen') as launch:
            self.assertFalse(v.speak('No automatic speaking'))
            launch.assert_not_called()

    def test_no_cloud_fallback_on_unsupported_host(self):
        v = signal_voice.WindowsVoice()
        with patch.object(signal_voice.WindowsVoice, '_require_windows', side_effect=RuntimeError('Windows required')):
            with self.assertRaisesRegex(RuntimeError, 'Windows required'):
                v.enable()
        self.assertFalse(v.enabled)

    def test_speech_uses_stdin_not_shell_interpolation(self):
        class CapturedPipe(io.BytesIO):
            def close(self):
                self.saved = self.getvalue()
                super().close()
        class Proc:
            def __init__(self):
                self.stdin = CapturedPipe()
            def poll(self): return 0
        proc = Proc()
        with patch.object(signal_voice.WindowsVoice, '_require_windows'), \
             patch.object(signal_voice.subprocess, 'Popen', return_value=proc) as launch:
            v = signal_voice.WindowsVoice()
            v.enable()
            dangerous = "hello; $(Invoke-WebRequest https://example.org)"
            self.assertTrue(v.speak(dangerous))
            args, kwargs = launch.call_args
            self.assertEqual(args[0][0], 'powershell.exe')
            self.assertNotIn(dangerous, repr(args[0]))
            self.assertEqual(kwargs['stdout'], signal_voice.subprocess.DEVNULL)
            self.assertEqual(json.loads(proc.stdin.saved), {'text': dangerous, 'voice': None})

    def test_stop_terminates_active_speech(self):
        proc = Mock()
        proc.poll.return_value = None
        v = signal_voice.WindowsVoice()
        v._process = proc
        v.stop()
        proc.terminate.assert_called_once()
        proc.wait.assert_called_once()
        self.assertIsNone(v._process)

    def test_text_is_bounded_and_markup_removed(self):
        out = signal_voice.speech_text('Hello **researcher**\n\n' + ('x' * 2000))
        self.assertTrue(out.startswith('Hello researcher '))
        self.assertLess(len(out), 700)
        self.assertIn('rest is on the screen', out)
        self.assertEqual(signal_voice.speech_text(''), '')

    def test_rate_validation(self):
        v = signal_voice.WindowsVoice()
        v.set_rate(-3)
        self.assertEqual(v.rate, -3)
        for bad in ('1', 6, -6, True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    v.set_rate(bad)

    def test_list_voices_fixed_command_and_no_cloud(self):
        done = Mock(returncode=0, stdout=b'Microsoft David\r\nMicrosoft Zira\r\n')
        with patch.object(signal_voice.WindowsVoice, '_require_windows'), \
             patch.object(signal_voice.subprocess, 'run', return_value=done) as run:
            self.assertEqual(signal_voice.WindowsVoice().list_voices(), ['Microsoft David','Microsoft Zira'])
            self.assertNotIn('https:', repr(run.call_args))


class DummyModel:
    model = 'test-model'
    def answer(self, messages): return 'A good research instrument never guesses.'


class DummyVoice:
    def __init__(self): self.enabled = False; self.events = []; self.rate = 0
    def enable(self): self.enabled = True
    def disable(self): self.enabled = False; self.events.append('off')
    def stop(self): self.events.append('stop')
    def speak(self, value):
        if self.enabled: self.events.append(value)
    def status(self): return 'voice on' if self.enabled else 'voice off'
    def list_voices(self): return ['Mock voice']
    def set_rate(self, rate): self.rate = rate


class VoiceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.voice = DummyVoice()
        self.bot = signal_core.Assistant(DummyModel(), Mock(), voice=self.voice)
        self.bot.memories.get.return_value = {}

    def test_voice_off_then_on_then_stop_then_off(self):
        self.bot.ask('hi')
        self.assertEqual(self.voice.events, [])
        self.assertIn('enabled', self.bot.action('/voice on'))
        self.bot.ask('Please reply')
        self.assertIn('A good research instrument', self.voice.events[-1])
        self.assertEqual(self.bot.action('/voice stop'), 'Speech stopped.')
        self.assertEqual(self.voice.events[-1], 'stop')
        self.bot.action('/voice off')
        self.assertFalse(self.voice.enabled)
        self.assertIn('voice off', self.bot.action('/voice'))

    def test_test_phrase_requires_opt_in(self):
        self.assertIn('Voice is off', self.bot.action('/voice test'))
        self.bot.action('/voice on')
        self.assertIn('Playing short', self.bot.action('/voice test'))
        self.assertIn('door still closes', self.voice.events[-1])
        self.assertIn('Mock voice', self.bot.action('/voice list'))
        self.assertIn('rate set', self.bot.action('/voice rate 2'))
        self.assertEqual(self.voice.rate, 2)

    def test_clear_stops_speaking_and_drops_loaded_log(self):
        self.bot.action('/voice on')
        self.bot.loaded_mtc = {'test': 'dummy'}
        self.bot.action('/clear')
        self.assertIsNone(self.bot.loaded_mtc)
        self.assertEqual(self.voice.events[-1], 'stop')


if __name__ == '__main__':
    unittest.main(verbosity=2)
