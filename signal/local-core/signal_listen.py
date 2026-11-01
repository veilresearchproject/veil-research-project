"""SIGNAL opt-in Windows offline push-to-talk (speech to text only).

No cloud, no continuous background recognition, no audio recording, no auto-send.
Recognize one utterance through installed Windows System.Speech.Recognition.
"""
import os
import shutil
import subprocess
import threading

RECOGNITION_SECONDS = 12
PROCESS_TIMEOUT = 20
MAX_TRANSCRIPT = 700

# Constant source, passed as an argument to PowerShell, not interpolated user data.
LISTEN_SCRIPT = r'''
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Speech
$engine = New-Object System.Speech.Recognition.SpeechRecognitionEngine
try {
  $engine.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
  $engine.SetInputToDefaultAudioDevice()
  $result = $engine.Recognize([TimeSpan]::FromSeconds(12))
  if ($null -ne $result -and $result.Confidence -ge 0.45) {
    [Console]::Write($result.Text)
  }
} finally {
  $engine.Dispose()
}
'''


class ListenError(RuntimeError):
    pass


class PushToTalk:
    """One shot recognition; session-local results held briefly in RAM."""
    def __init__(self, runner=None, platform_check=None):
        self._runner = runner or self._new_process
        self._platform_check = platform_check or self._check_windows
        self._mutex = threading.RLock()
        self._process = None
        self._worker = None
        self._generation = 0
        self._state = 'idle'
        self._transcript = ''
        self._error = ''

    @staticmethod
    def _check_windows():
        if os.name != 'nt' or not shutil.which('powershell.exe'):
            raise ListenError('Offline microphone input needs Windows PowerShell and a locally installed Windows speech recognizer. Text chat still works.')

    @staticmethod
    def _new_process():
        return subprocess.Popen(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', LISTEN_SCRIPT],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )

    def start(self):
        with self._mutex:
            if self._state == 'listening':
                raise ListenError('Already listening. Stop the current attempt first.')
            self._platform_check()
            self._transcript = ''
            self._error = ''
            # A fresh attempt is only created on the explicit Start click.
            try:
                proc = self._runner()
            except (OSError, subprocess.SubprocessError) as exc:
                self._state = 'error'
                raise ListenError('Unable to start Windows offline speech recognition. Check microphone and language settings.') from exc
            self._generation += 1
            version = self._generation
            self._process = proc
            self._state = 'listening'
            self._worker = threading.Thread(target=self._finish, args=(proc, version), daemon=True)
            self._worker.start()
            return self.status()

    def _finish(self, proc, version):
        try:
            raw, _err = proc.communicate(timeout=PROCESS_TIMEOUT)
            code = proc.returncode
            recognized = raw.decode('utf-8-sig', errors='replace').strip()
            if code != 0:
                outcome = ('error', '', 'Offline Windows speech recognition was unavailable. Check installed speech language and microphone permissions.')
            elif not recognized:
                outcome = ('empty', '', 'No sufficiently clear phrase was recognized. You can try again or type instead.')
            elif len(recognized) > MAX_TRANSCRIPT or any(ord(ch) < 32 and ch not in '\t\n' for ch in recognized):
                outcome = ('error', '', 'Speech result was not valid.')
            else:
                outcome = ('ready', recognized, '')
        except subprocess.TimeoutExpired:
            self._terminate(proc)
            outcome = ('error', '', 'Offline speech recognition timed out. Try again or type.')
        except (OSError, ValueError):
            outcome = ('error', '', 'Offline speech recognition failed. You can still type.')
        finally:
            try:
                if proc.stdout: proc.stdout.close()
                if proc.stderr: proc.stderr.close()
            except OSError:
                pass
        with self._mutex:
            if version == self._generation and self._state == 'listening':
                self._process = None
                self._state, self._transcript, self._error = outcome

    @staticmethod
    def _terminate(proc):
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)

    def stop(self):
        with self._mutex:
            proc = self._process
            self._generation += 1
            self._process = None
            self._state = 'idle'
            self._transcript = ''
            self._error = ''
        if proc is not None:
            self._terminate(proc)
        return self.status()

    def status(self, consume=False):
        with self._mutex:
            result = {'state': self._state, 'message': self._error}
            if consume and self._state == 'ready':
                result['transcript'] = self._transcript
                self._transcript = ''
                self._state = 'idle'
            elif consume and self._state in ('empty', 'error'):
                self._state = 'idle'
                self._error = ''
            return result
