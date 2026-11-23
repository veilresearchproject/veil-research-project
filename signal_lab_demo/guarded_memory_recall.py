"""Guarded Phase-1 recall entry point; no network, speech or instrument control.

The legacy memory_recall.recall_memory remains available for compatibility, but
must not be exposed directly to a phone or model: it lacks a consent gate.
The authenticated flag is caller-reported, NOT proof of authentication.
"""
from memory_recall import _RECALL, _CONTROL, MAX_QUERY
from memory_context_gate import build_memory_context


def guarded_recall(question, memory, *, consent=False, authenticated=False,
                   include_text=False, limit=5):
    """Return bounded reviewed notes only after explicit opt-in.

    No provider reads occur for unrelated questions, controls, or denied access.
    Text is for on-screen operator review, never automatic speech output.
    """
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= MAX_QUERY:
        raise ValueError("Question must contain 1-240 characters")
    if any(ord(ch) < 32 and ch not in "\t\n" for ch in question):
        raise ValueError("Invalid control character")
    # Validate flags even on unrelated questions, avoiding inconsistent policy.
    if any(type(flag) is not bool for flag in (consent, authenticated, include_text)):
        raise ValueError("Flags must be booleans")
    if type(limit) is not int or not 1 <= limit <= 5:
        raise ValueError("Invalid limit")
    result = {"handled": False, "allowed": False, "notes": [],
              "spoken_text": "", "read_only": True}
    if _CONTROL.search(question):
        result.update(handled=True, spoken_text="I cannot change memories or control equipment through recall.")
        return result
    if not _RECALL.search(question):
        return result
    result["handled"] = True
    context = build_memory_context(memory, consent=consent,
                                   authenticated=authenticated,
                                   include_text=include_text, limit=limit)
    if not context["allowed"]:
        result["spoken_text"] = "Memory recall needs operator consent and an authenticated session."
        return result
    result["allowed"] = True
    result["notes"] = context["notes"]
    result["spoken_text"] = (
        f"I found {len(context['notes'])} reviewed notes. They are attributed "
        "statements, not verified scientific findings. Please review them on screen."
    )
    return result
