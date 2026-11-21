"""Offline, reviewable SIGNAL memory. Notes are claims, never verified measurements."""
import sqlite3
from datetime import datetime, timezone

MAX_TEXT = 500

def _text(value):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= MAX_TEXT:
        raise ValueError('Note must be 1-500 characters')
    if any(ord(ch) < 32 and ch not in '\n\t' for ch in value):
        raise ValueError('Control characters forbidden')
    return value.strip()

class ReviewableMemory:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL, source TEXT NOT NULL, created_utc TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('unverified','reviewed','retracted')))")
        self.db.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, note_id INTEGER NOT NULL REFERENCES notes(id), action TEXT NOT NULL, at_utc TEXT NOT NULL, reason TEXT NOT NULL)')
        self.db.commit()

    def add(self, text, source='operator'):
        text = _text(text)
        if source not in ('operator', 'synthetic_demo'):
            raise ValueError('Unknown source')
        now = datetime.now(timezone.utc).isoformat()
        with self.db:
            cur = self.db.execute('INSERT INTO notes(text,source,created_utc,status) VALUES (?,?,?,?)', (text,source,now,'unverified'))
            self.db.execute('INSERT INTO history(note_id,action,at_utc,reason) VALUES (?,?,?,?)', (cur.lastrowid,'created',now,'initial entry'))
        return cur.lastrowid

    def list_notes(self, include_retracted=False):
        sql = 'SELECT id,text,source,created_utc,status FROM notes'
        if not include_retracted:
            sql += " WHERE status != 'retracted'"
        sql += ' ORDER BY id DESC LIMIT 100'
        newest_first = [dict(zip(('id','text','source','created_utc','status'), row)) for row in self.db.execute(sql)]
        return list(reversed(newest_first))

    def review(self, note_id, reason, retract=False):
        reason = _text(reason)
        if type(note_id) is not int or note_id < 1:
            raise ValueError('Invalid note id')
        status = 'retracted' if retract else 'reviewed'
        now = datetime.now(timezone.utc).isoformat()
        with self.db:
            row = self.db.execute('SELECT status FROM notes WHERE id=?', (note_id,)).fetchone()
            if row is None or row[0] == 'retracted':
                raise ValueError('Missing or retracted note')
            self.db.execute('UPDATE notes SET status=? WHERE id=?', (status,note_id))
            self.db.execute('INSERT INTO history(note_id,action,at_utc,reason) VALUES (?,?,?,?)', (note_id,status,now,reason))

    def history(self, note_id):
        return [dict(zip(('action','at_utc','reason'),row)) for row in self.db.execute('SELECT action,at_utc,reason FROM history WHERE note_id=? ORDER BY id', (note_id,))]
