"""Offline push-to-talk tests with faked Windows speech subprocess, no mic needed."""
import subprocess
import threading
import time
import unittest
from unittest.mock import patch

import signal_listen as mic


class DummyProc:
    def __init__(self, text=b'Open the evidence report', rc=0):
        self.stdout = None
        self.stderr = None
        self._text = text
        self.returncode = rc
        self.started = threading.Event()
        self.release = threading.Event()
        self.release.set()
        self.killed = False

    def communicate(self, timeout=None):
        self.started.set()
        if not self.release.wait(timeout):
            raise subprocess.TimeoutExpired('powershell.exe', timeout)
        return self._text, b''

    def poll(self):
        return self.returncode if self.release.is_set() else None

    def terminate(self):
        self.killed = True
        self.release.set()

    def wait(self, timeout=None):
        self.release.set()
        return self.returncode

    def kill(self):
        self.killed = True
        self.release.set()


def until(test, timeout=1.0):
    limit = time.monotonic() + timeout
    while time.monotonic() < limit:
        if test(): return
        time.sleep(0.005)
    raise AssertionError('Timed out waiting for worker')


class PushToTalkTests(unittest.TestCase):
    def test_never_starts_automatically(self):
        calls = []
        recognizer = mic.PushToTalk(runner=lambda: calls.append('start'), platform_check=lambda: None)
        self.assertEqual(recognizer.status()['state'], 'idle')
        self.assertEqual(calls, [])

    def test_one_utterance_retrieved_only_once_and_never_auto_sent(self):
        proc = DummyProc()
        v = mic.PushToTalk(runner=lambda: proc, platform_check=lambda: None)
        v.start()
        until(lambda: v.status()['state'] == 'ready')
        self.assertNotIn('transcript', v.status())
        one = v.status(consume=True)
        self.assertEqual(one['transcript'], 'Open the evidence report')
        self.assertEqual(v.status()['state'], 'idle')
        self.assertNotIn('transcript', v.status(consume=True))

    def test_cancel_disposes_pending_audio_and_transcript(self):
        proc = DummyProc()
        proc.release.clear()
        v = mic.PushToTalk(runner=lambda: proc, platform_check=lambda: None)
        v.start()
        proc.started.wait(1)
        with self.assertRaisesRegex(mic.ListenError, 'Already listening'):
            v.start()
        v.stop()
        self.assertTrue(proc.killed)
        self.assertEqual(v.status()['state'], 'idle')
        self.assertNotIn('transcript', v.status(consume=True))

    def test_recognizer_unavailable_fails_closed(self):
        v = mic.PushToTalk(runner=lambda: DummyProc(), platform_check=lambda: (_ for _ in ()).throw(mic.ListenError('no offline recognizer')))
        with self.assertRaisesRegex(mic.ListenError,'no offline recognizer'):
            v.start()
        self.assertEqual(v.status()['state'],'idle')

    def test_empty_or_low_confidence_result_is_not_added_to_chat(self):
        v = mic.PushToTalk(runner=lambda: DummyProc(text=b''), platform_check=lambda: None)
        v.start()
        until(lambda: v.status()['state'] == 'empty')
        res=v.status(consume=True)
        self.assertIn('No sufficiently clear', res['message'])
        self.assertNotIn('transcript',res)

    def test_failed_recognizer_no_fake_text(self):
        v=mic.PushToTalk(runner=lambda: DummyProc(rc=1),platform_check=lambda:None)
        v.start()
        until(lambda:v.status()['state']=='error')
        self.assertIn('unavailable',v.status(consume=True)['message'])
        self.assertNotIn('transcript',v.status())

    def test_long_or_control_text_rejected(self):
        for blob in [b'X'*(mic.MAX_TRANSCRIPT+1),b'bad\x00input']:
            with self.subTest(blob=blob[:5]):
                v=mic.PushToTalk(runner=lambda:DummyProc(text=blob),platform_check=lambda:None)
                v.start()
                until(lambda:v.status()['state']=='error')
                self.assertNotIn('transcript',v.status(consume=True))

    def test_script_is_constant_and_offline(self):
        self.assertIn('SpeechRecognitionEngine',mic.LISTEN_SCRIPT)
        self.assertIn('Recognize([TimeSpan]::FromSeconds(12))',mic.LISTEN_SCRIPT)
        self.assertNotIn('http:',mic.LISTEN_SCRIPT)
        self.assertNotIn('https:',mic.LISTEN_SCRIPT)
        with patch.object(mic.os,'name','posix'):
            with self.assertRaisesRegex(mic.ListenError,'Windows'):
                mic.PushToTalk().start()


if __name__=='__main__':unittest.main(verbosity=2)
