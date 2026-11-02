"""Local-first Cristal Reveal demo flow, without pretending that AI is conscious."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Cue:
    key: str
    purpose: str
    spoken: str
    operator_note: str

CUES = (
    Cue("boot", "First impression",
        "Oh! You're Cristal. Excellent. I've been told you're the sensible one around here. That makes one of us.",
        "Show SIGNAL's existing face; keep boot glitch under three seconds. Scripted opening."),
    Cue("identity", "Establish accuracy",
        "I'm SIGNAL, a prototype AI assistant for the VEIL Research Project. We're developing tools to investigate reported unusual environmental events, and to check ordinary explanations first.",
        "Do not suggest any findings have been independently validated."),
    Cue("live", "Unscripted conversation",
        "You can ask me something I haven't rehearsed. I may not always get it right, but I should say when I don't know.",
        "Invite Cristal to ask a spontaneous question; run real local LLM, never pre-write her question."),
    Cue("research", "Show practical value",
        "Imagine an unattended MTC recording. I could help log the time, questions, and observations, and flag moments for human review. A strange sound is not proof of anything on its own.",
        "Show an unmistakably labeled SAMPLE dataset, not invented live measurements."),
    Cue("closing", "Memorable finale",
        "Cristal, it's a pleasure meeting you. I'm still a prototype. But between us, I think this laboratory may have acquired its most unpredictable experiment: me.",
        "Close with a smile or small expression change if supported."),
)

def cue_by_key(key: str) -> Cue:
    return next(c for c in CUES if c.key == key)

def verify_cues() -> tuple[str, ...]:
    issues = []
    if len({c.key for c in CUES}) != len(CUES):
        issues.append("duplicate_cue")
    for cue in CUES:
        if not cue.spoken.strip() or not cue.operator_note.strip():
            issues.append("empty_cue_" + cue.key)
    return tuple(issues)
