"""Offline, dependency-free response checks for SIGNAL; advisory, not a speech engine."""
from dataclasses import dataclass
import re

VEIL_IDENTITY = (
    "VEIL Research Project is an independent research initiative founded by "
    "Andrew Underwood to develop evidence-first methods and instruments for "
    "investigating reported anomalous environmental events."
)
INCORRECT_EXPANSIONS = (
    "viral epidemiology and infection lineage",
    "viral epidemiology",
)

@dataclass(frozen=True)
class QualityReport:
    acceptable: bool
    flags: tuple[str, ...]

def check_answer(answer: str, *, spoken_text: str | None = None, speech_complete: bool | None = None) -> QualityReport:
    """Flag known errors; does not establish semantic truth or audio quality.

    spoken_text is the transcript of actually delivered speech, not the text
    handed to TTS. speech_complete must reflect actual playback status.
    """
    flags = []
    normalized = " ".join(answer.casefold().split())
    if any(term in normalized for term in INCORRECT_EXPANSIONS):
        flags.append("incorrect_veil_identity")
    if re.search(r"\b(?:the rest is on (?:the|your) screen|read the rest on screen)\b", normalized):
        flags.append("spoken_reply_deferral")
    if speech_complete is False:
        flags.append("speech_playback_incomplete")
    if spoken_text is not None and _normalize_words(spoken_text) != _normalize_words(answer):
        flags.append("spoken_text_mismatch")
    return QualityReport(not flags, tuple(flags))

def _normalize_words(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\w+", text.casefold()))
