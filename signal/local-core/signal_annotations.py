"""Operator-written MTC review notes stored separately from original research records.

Simple local JSONL notebook; append-only in normal operation, NOT tamper-proof.
No WAV or MTC source files are ever opened or changed by this module.
"""
import json
import math
import os
from pathlib import Path
import re
from datetime import datetime, timezone

LABELS = ('known_source', 'needs_review', 'unexplained', 'instrument_issue')
ID = re.compile(r'^[A-Za-z0-9_.-]{1,80}$')
MAX_NOTE_BYTES = 1024 * 1024


class ReviewError(ValueError):
    pass


def _folder(root):
    p = Path(root).expanduser()
    if p.exists() and (p.is_symlink() or not p.is_dir()):
        raise ReviewError('Unsafe review-notebook folder')
    p.mkdir(parents=True, exist_ok=True)
    if p.is_symlink():
        raise ReviewError('Unsafe review-notebook folder')
    return p


def _target(root, session_id):
    if not isinstance(session_id, str) or not ID.fullmatch(session_id) or '..' in session_id:
        raise ReviewError('Invalid MTC session identifier')
    folder = _folder(root)
    p = folder / (session_id + '.jsonl')
    if p.is_symlink() or (p.exists() and not p.is_file()):
        raise ReviewError('Unsafe notebook file')
    return p


def _valid_timestamp(value, duration):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ReviewError('Time must be a finite number of seconds')
    if value < 0 or value > duration:
        raise ReviewError('Time outside loaded session duration')
    return round(float(value), 3)


def append_note(root, session, timestamp, label, note):
    if not isinstance(session, dict) or not ID.fullmatch(str(session.get('session_id', ''))):
        raise ReviewError('Load a verified MTC session first')
    duration = session.get('recorded_seconds')
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        raise ReviewError('Invalid loaded MTC session duration')
    t = _valid_timestamp(timestamp, duration)
    if label not in LABELS:
        raise ReviewError('Choose one of the allowed investigator labels')
    if not isinstance(note, str) or not 1 <= len(note.strip()) <= 400:
        raise ReviewError('Observation must contain 1–400 characters')
    if any(ord(c) < 32 and c not in '\t\n' for c in note):
        raise ReviewError('Observation contains invalid characters')
    note = note.strip()
    p = _target(root, session['session_id'])
    if p.exists() and p.stat().st_size >= MAX_NOTE_BYTES:
        raise ReviewError('Notebook is full; archive a copy before adding more notes')
    entry = {'schema': 'veil.signal.review.v0.1',
             'session_id': session['session_id'], 'seconds_from_start': t,
             'classification': label, 'note': note,
             'author': 'local_operator_unverified',
             'created_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
             'provenance': 'Manual interpretation of local session; not automatic detection'}
    data = json.dumps(entry, ensure_ascii=False, separators=(',', ':')) + '\n'
    if len(data.encode('utf-8')) > 3000:
        raise ReviewError('Review entry is oversized')
    # Exclusive file create guards against accidentally following a symlink at first write.
    # No claims of protection from another malicious local process.
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    if hasattr(os, 'O_NOFOLLOW'): flags |= os.O_NOFOLLOW
    fd = os.open(p, flags, 0o600)
    try:
        if os.fstat(fd).st_size + len(data.encode('utf-8')) > MAX_NOTE_BYTES:
            raise ReviewError('Notebook size limit reached')
        with os.fdopen(fd, 'ab', closefd=False) as out:
            out.write(data.encode('utf-8'))
            out.flush()
            os.fsync(out.fileno())
    finally:
        os.close(fd)
    return entry


def list_notes(root, session, *, limit=100):
    if not isinstance(session, dict):
        raise ReviewError('Load an MTC session first')
    p = _target(root, session.get('session_id'))
    if not p.exists():
        return []
    if p.stat().st_size > MAX_NOTE_BYTES:
        raise ReviewError('Notebook exceeds safe read limit')
    notes = []
    for line in p.read_text(encoding='utf-8').splitlines():
        try:
            item = json.loads(line)
        except ValueError as exc:
            raise ReviewError('Damaged notebook: retain file and investigate') from exc
        if not isinstance(item, dict) or item.get('session_id') != session['session_id']:
            raise ReviewError('Notebook has an inconsistent entry')
        notes.append(item)
    if limit is None:
        return notes
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ReviewError('Invalid notebook display limit')
    return notes[-limit:]
