"""Operator-controlled, local-only completed-conversation snapshot for SIGNAL.

Never autosaves, restores, or syncs. Does not include evidence, memory facts,
mic transcripts, temporary model output, raw WAVs, secrets or active session IDs.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone

MAX_TURNS = 16
MAX_FILE = 130_000
MAX_USER = 4000
MAX_ASSISTANT = 7000
VERSION = 1


class SnapshotError(ValueError):
    pass


def validated_history(messages):
    if not isinstance(messages, list) or not messages or len(messages) > MAX_TURNS or len(messages) % 2:
        raise SnapshotError('Only a nonempty, completed conversation (up to eight exchanges) can be saved')
    result = []
    for i, msg in enumerate(messages):
        expected = 'user' if i % 2 == 0 else 'assistant'
        limit = MAX_USER if expected == 'user' else MAX_ASSISTANT
        if not isinstance(msg, dict) or set(msg) != {'role', 'content'}:
            raise SnapshotError('Snapshot contains unsupported fields')
        if msg['role'] != expected or not isinstance(msg['content'], str) or not 0 < len(msg['content'].strip()) <= limit:
            raise SnapshotError('Snapshot contains an invalid or incomplete conversation turn')
        result.append({'role': expected, 'content': msg['content']})
    return result


class SessionStore:
    """One explicitly managed snapshot in SIGNAL's user-private data directory."""
    def __init__(self, data_dir):
        self.path = Path(data_dir) / 'conversation_snapshot.json'

    def _load(self):
        try:
            if self.path.stat().st_size > MAX_FILE:
                raise SnapshotError('Saved conversation exceeds the safe file size')
            payload = json.loads(self.path.read_text(encoding='utf-8'))
        except FileNotFoundError as exc:
            raise SnapshotError('No saved conversation found on this computer') from exc
        except (UnicodeError, json.JSONDecodeError, IsADirectoryError, PermissionError) as exc:
            raise SnapshotError('Saved conversation is unreadable') from exc
        if not isinstance(payload, dict) or set(payload) != {'version', 'saved_utc', 'history', 'sha256'}:
            raise SnapshotError('Saved conversation has an unsupported format')
        if type(payload['version']) is not int or payload['version'] != VERSION:
            raise SnapshotError('Saved conversation format version is unsupported')
        hist = validated_history(payload['history'])
        raw = json.dumps(hist, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode('utf-8')
        if payload['sha256'] != hashlib.sha256(raw).hexdigest():
            raise SnapshotError('Saved conversation checksum mismatch; no history was restored')
        if not isinstance(payload['saved_utc'], str) or len(payload['saved_utc']) > 40:
            raise SnapshotError('Saved time is invalid')
        return payload['saved_utc'], hist

    def status(self):
        if not self.path.exists():
            return {'exists': False, 'turns': 0, 'saved_utc': None}
        timestamp, messages = self._load()
        return {'exists': True, 'turns': len(messages)//2, 'saved_utc': timestamp}

    def save(self, history):
        hist = validated_history(history)
        raw = json.dumps(hist, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode('utf-8')
        payload = {
            'version': VERSION,
            'saved_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'history': hist,
            'sha256': hashlib.sha256(raw).hexdigest(),
        }
        blob = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
        if len(blob) > MAX_FILE:
            raise SnapshotError('Conversation too large to save safely')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement: do not leave a half-written conversation on disk.
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile('wb', delete=False, dir=self.path.parent,
                                             prefix='.signal_snapshot_', suffix='.tmp') as f:
                temp_path = Path(f.name)
                f.write(blob)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
        return self.status()

    def restore(self):
        _, hist = self._load()
        return hist

    def delete(self):
        exists = self.path.exists()
        self.path.unlink(missing_ok=True)
        return exists
