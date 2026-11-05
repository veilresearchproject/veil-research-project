"""SIGNAL v34 approved memory storage, stdlib-only.

Explicit user approval required for every addition. Does not auto-inject into AI.
No transcript ingestion, secrets, evidence originals, cloud or equipment access.
"""
import json
import os
import re
import threading
import uuid
from pathlib import Path
from datetime import datetime, timezone

KINDS = ('equipment', 'protocol', 'project', 'decision')
LOCK = threading.RLock()
MAX_RECORDS = 50


def _clean(value, limit, label):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError('Invalid ' + label)
    return value.strip()


def _path(directory):
    root = Path(directory).expanduser()
    if root.is_symlink():
        raise ValueError('Refusing symlink memory directory')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    file = root / 'approved_memory_v34.json'
    if file.is_symlink():
        raise ValueError('Refusing symlink memory file')
    return file


def _validate(data):
    if not isinstance(data, dict) or data.get('schema') != 'signal-approved-memory' or data.get('version') != 1:
        raise ValueError('Invalid memory format')
    entries = data.get('entries')
    if not isinstance(entries, list) or len(entries) > MAX_RECORDS:
        raise ValueError('Invalid memory entries')
    seen = set()
    for e in entries:
        if not isinstance(e, dict) or e.get('kind') not in KINDS or not isinstance(e.get('id'), str) or not re.fullmatch(r'[a-f0-9]{32}', e['id']) or e['id'] in seen:
            raise ValueError('Invalid memory item')
        seen.add(e['id'])
        _clean(e.get('note'), 500, 'memory note')
        _clean(e.get('source'), 160, 'memory source')
        _clean(e.get('approvedBy'), 80, 'approver')
        if not isinstance(e.get('approvedAt'), str):
            raise ValueError('Invalid approval time')
    return data


def load(directory):
    with LOCK:
        path = _path(directory)
        if not path.exists():
            return {'schema': 'signal-approved-memory', 'version': 1, 'entries': []}
        if path.stat().st_size > 80_000:
            raise ValueError('Memory file size exceeds limit')
        return _validate(json.loads(path.read_text(encoding='utf-8')))


def _save(directory, data):
    path = _path(directory)
    _validate(data)
    temp = path.with_name('.memory-' + uuid.uuid4().hex + '.tmp')
    try:
        with open(temp, 'x', encoding='utf-8') as f:
            if os.name != 'nt':
                os.chmod(temp, 0o600)
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        if path.is_symlink():
            raise ValueError('Memory file changed to symlink')
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def add(directory, payload):
    if not isinstance(payload, dict) or payload.get('approved') is not True:
        raise ValueError('Explicit approval required')
    kind = payload.get('kind')
    if kind not in KINDS:
        raise ValueError('Invalid memory category')
    note = _clean(payload.get('note'), 500, 'memory note')
    source = _clean(payload.get('source'), 160, 'memory source')
    approved_by = _clean(payload.get('approvedBy'), 80, 'approver')
    with LOCK:
        data = load(directory)
        if len(data['entries']) >= MAX_RECORDS:
            raise ValueError('Maximum 50 approved memories')
        entry = dict(id=uuid.uuid4().hex, kind=kind, note=note, source=source,
                     approvedBy=approved_by, approvedAt=datetime.now(timezone.utc).isoformat())
        data['entries'].append(entry)
        _save(directory, data)
        return entry


def remove(directory, payload):
    if not isinstance(payload, dict) or payload.get('approved') is not True or not isinstance(payload.get('id'), str):
        raise ValueError('Explicit deletion approval required')
    with LOCK:
        data = load(directory)
        entries = [e for e in data['entries'] if e['id'] != payload['id']]
        if len(entries) == len(data['entries']):
            raise ValueError('Unknown memory ID')
        data['entries'] = entries
        _save(directory, data)
        return {'removed': True, 'remaining': len(entries)}


def clear(directory, payload):
    if not isinstance(payload, dict) or payload.get('approved') is not True or payload.get('confirmation') != 'DELETE ALL APPROVED MEMORIES':
        raise ValueError('Exact deletion confirmation required')
    with LOCK:
        data = load(directory)
        count = len(data['entries'])
        data['entries'] = []
        _save(directory, data)
        return {'removed': count}
