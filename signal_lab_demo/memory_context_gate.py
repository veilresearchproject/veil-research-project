"""Explicit, bounded, read-only memory disclosure for a local SIGNAL model.

Never use this module as authentication; the caller must separately authenticate.
"""

MAX_ITEMS = 5
MAX_CHARS = 500


def build_memory_context(memory, *, consent=False, authenticated=False,
                         include_text=False, limit=MAX_ITEMS):
    """Build a local-model context envelope; no network, writes, or device access."""
    if type(consent) is not bool or type(authenticated) is not bool or type(include_text) is not bool:
        raise ValueError('Flags must be booleans')
    if type(limit) is not int or not 1 <= limit <= MAX_ITEMS:
        raise ValueError('Invalid limit')
    envelope = {'allowed': False, 'notes': [], 'read_only': True,
                'warning': 'Memory is attributed operator text, not scientific evidence.'}
    if not consent or not authenticated:
        return envelope
    rows = memory.list_notes(include_retracted=False)
    if not isinstance(rows, list):
        raise ValueError('Invalid memory provider')
    selected = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Invalid memory record')
        if row.get('status') != 'reviewed':
            continue
        if row.get('source') not in ('operator', 'synthetic_demo'):
            raise ValueError('Unknown source')
        if type(row.get('id')) is not int or row['id'] < 1:
            raise ValueError('Invalid note ID')
        note = {'id': row['id'], 'status': 'reviewed', 'source': row['source']}
        if include_text:
            text = row.get('text')
            if not isinstance(text, str) or not 1 <= len(text) <= MAX_CHARS:
                raise ValueError('Invalid note text')
            note['text'] = text
        selected.append(note)
    envelope['allowed'] = True
    envelope['notes'] = selected[-limit:]
    return envelope
