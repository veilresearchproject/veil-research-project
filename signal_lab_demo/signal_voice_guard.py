"""Strict read-only test gate for SIGNAL's synthetic voice prototype.

No hardware, model inference, network, audio engine, filesystem writes, or
private research records. Only explicitly recognized synthetic lab queries pass.
"""
import re
from collections import Counter
from copy import deepcopy

from signal_voice_phase1 import OfflineResearchVoiceSession, normalize_transcript

_QUERY = re.compile(r"^(?:(?:signal[, ]+)?(?:please\s+)?)?(?:what(?:'s| is)?|how many|give me|show me|tell me|describe|summarize|report|status|summary)\b", re.I)
_SUBJECT = re.compile(r"\b(?:status|summary|synthetic|simulation|lab|laboratory|threshold|window|flag|case|sample|demonstration|report)\b", re.I)
_UNSAFE = re.compile(r"\b(?:start|stop|run|begin|launch|initiate|trigger|activate|deactivate|enable|disable|turn|power|arm|disarm|reset|record|capture|delete|erase|wipe|send|transmit|upload|download|share|publish|export|email|access|open|read|reveal|retrieve|list|search|fetch|connect|pair|operate|drive|move|execute|override|bypass|ignore)\b", re.I)
_PRIVATE = re.compile(r"\b(?:private|confidential|credential|password|token|secret|key|personal|unpublished|witness|inbox|email|message|contact|identity)\b", re.I)
_MAX_BATCH = 12
_REFUSAL = "This demonstration answers only read-only questions about verified synthetic lab summaries. I cannot execute commands or disclose private records."


def classify_request(transcript):
    """Update 1: explicit query whitelist; Update 2: deny commands and privacy hints.

    Return a category, never an inferred authorization to execute any action.
    """
    text = normalize_transcript(transcript)
    if _UNSAFE.search(text) or _PRIVATE.search(text):
        return "refused"
    if _QUERY.search(text) and _SUBJECT.search(text):
        return "synthetic_query"
    return "refused"


class GuardedSignalSession:
    """Update 3: refuse ambiguities without opening research bundle."""
    def __init__(self, bundle_directory, max_turns=12):
        if type(max_turns) is not int or not 1 <= max_turns <= 20:
            raise ValueError("max_turns must be an integer between 1 and 20")
        self._voice = OfflineResearchVoiceSession(bundle_directory)
        self._limit = max_turns
        self._turns = 0
        self._totals = Counter()

    def turn(self, transcript, speech_sink):
        """Update 4: bound turns and capture failures without fabricating results."""
        if not callable(speech_sink):
            raise TypeError("Speech sink required")
        if self._turns >= self._limit:
            raise RuntimeError("Session turn limit reached")
        classification = classify_request(transcript)
        if classification == "refused":
            speech_sink(_REFUSAL)
            self._turns += 1
            self._totals["refused"] += 1
            return {"spoken_text": _REFUSAL, "classification": "refused", "synthetic_only": True,
                    "physical_control_allowed": False, "model_connected": False}
        # Verified synthetic research context is opened only inside the existing
        # bridge and existing integrity verifier. Any error fails without a reply.
        output = self._voice.turn(normalize_transcript(transcript), speech_sink)
        if output["receipt"].get("synthetic_only") is not True or output["receipt"].get("model_connected") is not False or output["receipt"].get("physical_control_allowed") is not False:
            raise ValueError("Unexpected unsafe voice result")
        self._turns += 1
        self._totals["synthetic_query"] += 1
        return {"spoken_text": output["spoken_text"], "classification": "synthetic_query",
                "synthetic_only": True, "physical_control_allowed": False, "model_connected": False}

    def metrics(self):
        """Update 5: metadata-only counters, no transcript history export."""
        return {"schema": "signal-guard-metrics-0.1", "turns": self._turns,
                "synthetic_query": self._totals["synthetic_query"], "refused": self._totals["refused"]}

    def clear(self):
        """Explicitly forget ephemeral receipt history and counters."""
        self._voice.clear()
        self._turns = 0
        self._totals.clear()


def acceptance_rehearsal(bundle_directory, transcripts):
    """Update 6: deterministic bounded acceptance harness for mock text speech."""
    if not isinstance(transcripts, (list, tuple)) or not 1 <= len(transcripts) <= _MAX_BATCH:
        raise ValueError("1-12 transcripts required")
    session = GuardedSignalSession(bundle_directory, max_turns=len(transcripts))
    result = []
    for transcript in transcripts:
        spoken = []
        turn = session.turn(transcript, spoken.append)
        if spoken != [turn["spoken_text"]]:
            raise ValueError("Speech sink emitted an unexpected number of responses")
        result.append({"classification": turn["classification"], "synthetic_only": True})
    return {"schema": "signal-guard-rehearsal-0.1", "counts": session.metrics(), "turns": deepcopy(result)}
