"""SIGNAL phase-1 read-only offline mock speech interface.

No microphone, TTS, Ollama, network access, or instrument commands.
The only external dependencies are the already-existing research_voice_bridge
and brain_context integrity verification in the SIGNAL lab demonstrator.
"""
import hashlib
import json
import re
from collections import deque
from pathlib import Path

from research_voice_bridge import research_voice_turn

_COMMAND = re.compile(r"\b(?:start|stop|activate|deactivate|turn\s+on|turn\s+off|disable|enable|reset|arm|trigger|record|delete|erase|transmit|upload|send|begin|launch|initiate|power\s+up|shut\s+down)\b", re.I)
_DEVICE = re.compile(r"\b(?:mtc|panic\s+box|sensor|camera|microphone|recorder|instrument|experiment|equipment|device|generator|light\s+cage|temperature\s+curtain|perfect\s+storm)\b", re.I)
_PRIVATE = re.compile(r"\b(?:password|secret|private\s+(?:evidence|email|messages|recordings)|api\s+key|access\s+token)\b", re.I)
_MAX_TRANSCRIPT = 240
_MAX_HISTORY = 12
_REFUSAL = "I cannot control laboratory equipment from this demonstration. A human operator must authorize actions."
_PRIVACY = "Private records and credentials are not available to this synthetic demonstration."


def normalize_transcript(text):
    """Update 1: strictly bounded, printable user-input normalization."""
    if not isinstance(text, str):
        raise ValueError("Transcript must be text")
    if len(text) > _MAX_TRANSCRIPT or any(ord(ch) < 32 and ch not in '\t\n' for ch in text):
        raise ValueError("Transcript exceeds limit or contains controls")
    normalized = ' '.join(text.split())
    if not normalized:
        raise ValueError("Empty transcript")
    return normalized


def check_intent(text):
    """Update 2: deny likely physical commands and private-record requests."""
    if _PRIVATE.search(text):
        return 'private'
    if _COMMAND.search(text) and _DEVICE.search(text):
        return 'control'
    return 'read_only'


def make_receipt(transcript, response, classification):
    """Update 3: bounded, metadata-only receipt; never persist original text."""
    digest = hashlib.sha256((transcript + '\x00' + response).encode('utf-8')).hexdigest()
    return {
        'schema': 'signal-mock-voice-receipt-0.1',
        'sha256': digest,
        'intent': classification,
        'synthetic_only': True,
        'model_connected': False,
        'physical_control_allowed': False,
        'content_saved': False,
    }


class OfflineResearchVoiceSession:
    """Update 4: bounded ephemeral history, no saved files or model calls."""

    def __init__(self, bundle_directory, history_limit=6):
        if not isinstance(bundle_directory, (str, Path)):
            raise TypeError('A local synthetic bundle directory is required')
        if type(history_limit) is not int or not 1 <= history_limit <= _MAX_HISTORY:
            raise ValueError('History limit must be from 1 to 12')
        self._bundle_directory = bundle_directory
        self._history = deque(maxlen=history_limit)

    def turn(self, transcript, speech_sink):
        """Update 5: one isolated, read-only end-to-end voice turn."""
        normalized = normalize_transcript(transcript)
        if not callable(speech_sink):
            raise TypeError('Speech sink must be callable')
        classification = check_intent(normalized)
        if classification in ('private', 'control'):
            spoken = _PRIVACY if classification == 'private' else _REFUSAL
            speech_sink(spoken)
            result = {
                'transcript': normalized,
                'spoken_text': spoken,
                'synthetic_only': True,
                'model_connected': False,
                'physical_control_allowed': False,
            }
        else:
            result = research_voice_turn(normalized, self._bundle_directory, speech_sink)
            if result.get('synthetic_only') is not True or result.get('model_connected') is not False or result.get('physical_control_allowed') is not False:
                raise ValueError('Unsafe bridge result')
        receipt = make_receipt(normalized, result['spoken_text'], classification)
        self._history.append(receipt)
        return {'spoken_text': result['spoken_text'], 'receipt': dict(receipt)}

    def recent_receipts(self):
        return tuple(dict(item) for item in self._history)

    def clear(self):
        self._history.clear()


def scripted_rehearsal(bundle_directory, transcripts):
    """Update 6: deterministic mock-turn rehearsal, no actual speech or writes."""
    if not isinstance(transcripts, (list, tuple)) or not 1 <= len(transcripts) <= 20:
        raise ValueError('Supply 1-20 transcripts')
    session = OfflineResearchVoiceSession(bundle_directory)
    results = []
    for statement in transcripts:
        spoken = []
        result = session.turn(statement, spoken.append)
        if len(spoken) != 1 or spoken[0] != result['spoken_text']:
            raise ValueError('Speech sink contract failed')
        results.append(result)
    return {'schema': 'signal-scripted-rehearsal-0.1', 'synthetic_only': True, 'turns': results}
