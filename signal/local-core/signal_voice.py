"""Optional offline Windows speech for SIGNAL. No AI model, mic, cloud or dependencies.

Fixed PowerShell commands use Windows System.Speech (SAPI) and take speech text
through standard input, never through interpolated shell commands or arguments.
"""
import os
import re
import shutil
import subprocess

_MAX_SPOKEN = 650
# The voice runs on Windows with locally-installed voices; no network calls.
_SPEAK_SCRIPT = r'''
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Speech
$text = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($text)) { exit 2 }
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $voice.Rate = __RATE__
    $voice.Speak($text)
} finally { $voice.Dispose() }
'''
_LIST_SCRIPT = r'''
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Speech
$v = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { foreach ($i in $v.GetInstalledVoices()) { if ($i.Enabled) { Write-Output $i.VoiceInfo.Name } } }
finally { $v.Dispose() }
'''


def speech_text(value):
    """Bound the spoken portion; avoid raw formatting or long uninterruptible speeches."""
    if not isinstance(value, str):
        raise ValueError('Speech requires text')
    text = re.sub(r'[\x00-\x1f\x7f]+', ' ', value).strip()
    # Remove some markdown formatting but retain punctuation and factual text.
    text = re.sub(r'[`*_#]', '', text)
    text = re.sub(r'\[(.*?)\]\(https?://[^\s)]+\)', r'\1', text)
    if len(text) <= _MAX_SPOKEN:
        return text
    cut = max(text.rfind('. ', 0, _MAX_SPOKEN),
              text.rfind('? ', 0, _MAX_SPOKEN),
              text.rfind('! ', 0, _MAX_SPOKEN))
    cut = cut + 1 if cut >= 180 else _MAX_SPOKEN
    return text[:cut].rstrip() + ' ... The rest is on the screen.'


class WindowsVoice:
    """Single-operator, text-to-speech output only, off by default."""

    def __init__(self):
        self.enabled = False
        self.rate = 0
        self._process = None

    @staticmethod
    def _require_windows():
        if os.name != 'nt' or shutil.which('powershell.exe') is None:
            raise RuntimeError('Local speech requires Windows PowerShell and a Windows speech voice; no cloud fallback.')

    def enable(self):
        self._require_windows()
        self.enabled = True

    def disable(self):
        self.enabled = False
        self.stop()

    def stop(self):
        p = self._process
        self._process = None
        if p is not None and p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(timeout=2)

    def speak(self, text):
        if not self.enabled:
            return False
        self._require_windows()
        safe_text = speech_text(text)
        if not safe_text:
            return False
        self.stop()  # A new response replaces a currently speaking one.
        script = _SPEAK_SCRIPT.replace('__RATE__', str(self.rate))
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        p = subprocess.Popen(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
        self._process = p
        try:
            p.stdin.write(safe_text.encode('utf-8'))
            p.stdin.close()
        except (OSError, BrokenPipeError) as exc:
            self.stop()
            raise RuntimeError('Windows voice could not receive text') from exc
        return True

    def list_voices(self):
        self._require_windows()
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', _LIST_SCRIPT],
            capture_output=True, check=False, timeout=15, creationflags=flags,
        )
        if result.returncode:
            raise RuntimeError('Unable to list installed Windows speech voices')
        output = result.stdout.decode('utf-8-sig', errors='replace')
        return [line.strip() for line in output.splitlines() if line.strip()][:40]

    def set_rate(self, rate):
        if isinstance(rate, bool) or not isinstance(rate, int) or not -5 <= rate <= 5:
            raise ValueError('Voice rate must be a whole number from -5 to 5')
        self.rate = rate

    def status(self):
        return ('voice on' if self.enabled else 'voice off') + ', rate ' + str(self.rate)
