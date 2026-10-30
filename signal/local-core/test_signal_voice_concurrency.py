"""Speech process races tested without Windows or a real speaker."""
import io
import threading
import unittest
from unittest.mock import patch
import signal_voice


class Process:
    def __init__(self):
        self.stdin = io.BytesIO()
        self.terminated = 0
    def poll(self): return 0 if self.terminated else None
    def terminate(self): self.terminated += 1
    def wait(self, timeout=None): return 0


class VoiceConcurrencyTests(unittest.TestCase):
    def test_disable_during_process_creation_leaves_no_speech_process(self):
        voice = signal_voice.WindowsVoice()
        proc = Process()
        spawning, finish_spawn, disabling = threading.Event(), threading.Event(), threading.Event()
        errors = []
        def create(*args, **kwargs):
            spawning.set()
            if not finish_spawn.wait(3): raise RuntimeError('Test spawn blocked')
            return proc
        def speak():
            try: voice.speak('A test phrase')
            except Exception as exc: errors.append(exc)
        def disable(): disabling.set(); voice.disable()
        with patch.object(voice, '_require_windows'), patch.object(signal_voice.subprocess, 'Popen', side_effect=create):
            voice.enable()
            speaker = threading.Thread(target=speak, daemon=True)
            stopper = threading.Thread(target=disable, daemon=True)
            try:
                speaker.start(); self.assertTrue(spawning.wait(2))
                stopper.start(); self.assertTrue(disabling.wait(2))
            finally:
                finish_spawn.set()
                speaker.join(2); stopper.join(2)
            self.assertFalse(speaker.is_alive()); self.assertFalse(stopper.is_alive())
            self.assertEqual(errors, [])
            self.assertFalse(voice.enabled)
            self.assertIsNone(voice._process)
            self.assertEqual(proc.terminated, 1)
            self.assertFalse(voice.speak('Must stay silent'))

    def test_simultaneous_stops_terminate_only_once(self):
        voice = signal_voice.WindowsVoice()
        proc = Process(); voice._process = proc
        gate = threading.Barrier(3)
        def stop(): gate.wait(); voice.stop()
        workers = [threading.Thread(target=stop, daemon=True) for _ in range(2)]
        for worker in workers: worker.start()
        gate.wait(timeout=2)
        for worker in workers: worker.join(2); self.assertFalse(worker.is_alive())
        self.assertEqual(proc.terminated, 1)
        self.assertIsNone(voice._process)


if __name__ == '__main__': unittest.main()
