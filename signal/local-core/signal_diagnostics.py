"""Explicit, read-only first-run checks for SIGNAL's local Windows stack.

Never downloads a model, starts a microphone, or reaches the internet.
Only the literal loopback Ollama /api/tags endpoint is queried.
"""
import json
import os
import shutil
import subprocess
from urllib import request, error

OLLAMA_TAGS = 'http://127.0.0.1:11434/api/tags'
MAX_TAG_BYTES = 256_000
RECOGNIZER_PROBE = r'''$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$engine = New-Object System.Speech.Recognition.SpeechRecognitionEngine
try { Write-Output 'RECOGNIZER_AVAILABLE' } finally { $engine.Dispose() }
'''


def check_ollama(model, opener=None):
    """Return an operator-friendly result; a healthy server is not proof of usable inference."""
    opener = opener or request.urlopen
    try:
        req = request.Request(OLLAMA_TAGS, method='GET')
        with opener(req, timeout=2.0) as resp:
            data = resp.read(MAX_TAG_BYTES + 1)
            if len(data) > MAX_TAG_BYTES:
                raise ValueError('Model list too large')
        payload = json.loads(data.decode('utf-8'))
        entries = payload.get('models', [])
        if not isinstance(entries, list):
            raise ValueError('Invalid model listing')
        names = [m.get('name') for m in entries if isinstance(m, dict) and isinstance(m.get('name'), str)]
        exact = model in names
        return {'status': 'ready' if exact else 'model_missing',
                'message': ('Ollama responds and the configured model is installed.' if exact else
                            'Ollama is running, but the configured local model is not listed.'),
                'configured_model': model,
                'installed_model_count': len(names)}
    except (error.URLError, OSError, ValueError, UnicodeError, TypeError, KeyError) as exc:
        return {'status': 'unavailable',
                'message': 'Ollama did not return a usable local model list. Start Ollama and try again.',
                'configured_model': model, 'installed_model_count': None}


def check_windows_audio(voice):
    if os.name != 'nt' or not shutil.which('powershell.exe'):
        return {'voice': {'status': 'unavailable', 'message': 'Built-in voice requires Windows PowerShell.'},
                'microphone': {'status': 'unavailable', 'message': 'Offline dictation requires Windows speech recognition.'}}
    try:
        voices = voice.list_voices()
        speech = {'status': 'ready' if voices else 'missing',
                  'message': 'Installed Windows speech voices available.' if voices else 'No enabled Windows speech voices found.',
                  'voice_count': len(voices)}
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        speech = {'status': 'unavailable', 'message': 'Windows speech voices could not be listed.'}
    # Only checks whether a recognizer can be created. No microphone permissions requested,
    # no audio captured, no device bound, and no recognition started.
    try:
        p = subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',RECOGNIZER_PROBE],
                           capture_output=True, timeout=6, check=False,
                           creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        ok = p.returncode == 0 and b'RECOGNIZER_AVAILABLE' in p.stdout
        mic = {'status': 'available' if ok else 'missing',
               'message': ('Offline recognizer detected. Microphone operation is not yet tested.' if ok else
                           'No usable legacy Windows offline recognizer detected. Typing remains available.')}
    except (OSError, subprocess.TimeoutExpired):
        mic = {'status': 'unavailable', 'message': 'Offline recognizer check did not complete.'}
    return {'voice': speech, 'microphone': mic}


def run_checks(model, voice, check_audio=check_windows_audio, check_models=check_ollama):
    # Values exposed to the interface are fixed diagnostic labels, not process output or local paths.
    return {'mode': 'local-only', 'ollama': check_models(model), **check_audio(voice),
            'next_steps': ('If Ollama is missing, start it. If the configured model is missing, '
                           'use ollama pull llama3.2:3b only when you choose to download it. '
                           'To test, type a short question; no cloud fallback exists.'),
            'notes': ('Checks do not send a chat request, access the microphone, verify actual speaker output, '
                      'or prove that a local model can answer successfully.')}
