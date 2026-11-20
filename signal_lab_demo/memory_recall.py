"""Bounded, read-only memory recall for SIGNAL Phase 1; no model or device access."""
import re

MAX_QUERY = 240
_RECALL = re.compile(r"\b(remember|memory|memories|notes|recall)\b", re.I)
_CONTROL = re.compile(r"\b(delete|erase|retract|change|edit|approve|verify|send|upload|transmit|start|stop|activate|reset)\b", re.I)


def recall_memory(question, memory, limit=5):
    """Return explicitly attributed note text; never perform writes or infer truth."""
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= MAX_QUERY:
        raise ValueError("Question must contain 1-240 characters")
    if any(ord(c) < 32 and c not in "\t\n" for c in question):
        raise ValueError("Invalid control character")
    if type(limit) is not int or not 1 <= limit <= 10:
        raise ValueError("Limit must be an integer between 1 and 10")
    if _CONTROL.search(question):
        return {"handled": True, "spoken_text": "I cannot change memories or control equipment through recall. Human review is required.", "notes": [], "read_only": True}
    if not _RECALL.search(question):
        return {"handled": False, "spoken_text": "", "notes": [], "read_only": True}
    rows = memory.list_notes(include_retracted=False)
    if not isinstance(rows, list):
        raise ValueError("Invalid memory provider")
    selected = []
    for row in rows[-limit:]:
        if not isinstance(row, dict) or row.get("status") not in ("unverified", "reviewed") or row.get("source") not in ("operator", "synthetic_demo"):
            raise ValueError("Invalid memory record")
        if type(row.get("id")) is not int or not isinstance(row.get("text"), str) or not 1 <= len(row["text"]) <= 500:
            raise ValueError("Invalid memory record")
        selected.append({"id": row["id"], "text": row["text"], "source": row["source"], "status": row["status"]})
    if not selected:
        spoken = "I have no active notes to recall."
    else:
        spoken = f"I found {len(selected)} saved notes. These are attributed statements, not verified scientific findings. Review the notes on screen before relying on them."
    return {"handled": True, "spoken_text": spoken, "notes": selected, "read_only": True}
