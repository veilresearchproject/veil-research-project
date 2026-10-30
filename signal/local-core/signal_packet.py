"""Offline, read-only MTC *review packet* export for SIGNAL.

Records software log assertions, separately imported scanner findings, and manual
notes without presenting them as independently verified acoustic observations.
Does not open WAV files, access the microphone, or modify evidence or notes.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import html
import json
import re
from typing import Any

import signal_annotations

SCHEMA = 'veil.signal.review_packet.v0.1'
MAX_PACKET = 1_800_000  # bytes; no giant notes/report export


class PacketError(ValueError):
    pass


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def build_packet(session, scanner, review_dir, *, created=None):
    """Construct a bounded human-auditable export, not an attestation of authenticity."""
    if not isinstance(session, dict) or not isinstance(session.get('session_id'), str):
        raise PacketError('Load verified MTC logs before exporting a review packet')
    sid = session['session_id']
    if scanner is not None and (not isinstance(scanner, dict) or scanner.get('session_id') != sid):
        raise PacketError('Scanner findings belong to a different MTC session')
    # Never silently truncate export (the UI intentionally lists only the latest 100).
    notes = signal_annotations.list_notes(review_dir, session, limit=None)
    timestamp = created or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise PacketError('Export timestamp must be timezone-aware')
    packet = {
        'schema': SCHEMA,
        'generated_utc': timestamp.astimezone(timezone.utc).isoformat(timespec='seconds'),
        'status': 'OPERATOR REVIEW RECORD — NOT AN AUTOMATED SCIENTIFIC CONCLUSION',
        'session_id': sid,
        'session_log_summary': dict(session),
        'scanner_review': scanner if scanner is not None else None,
        'investigator_notes': notes,
        'note_count': len(notes),
        'evidence_boundaries': [
            'The MTC log adapter checked software-declared JSON log structure and embedded JSON hashes.',
            'No raw WAV recordings were opened, hashed or acoustically assessed by this export.',
            'Scanner flags are acoustic outliers; they are not verified speech, EVP, or a cause.',
            'Overlapping flags are grouped only to reduce repeated review, not to identify a common cause.',
            'Investigator annotations are manually entered assertions, not independently verified facts.',
            'Unexplained means no cause has been established; it does not mean paranormal.',
            'This review packet is not signed, tamper-proof or an independent chain of custody.'
        ],
    }
    # A content fingerprint identifies this *exported summary*, not the source WAV data.
    fingerprint = hashlib.sha256(_canonical(packet)).hexdigest()
    packet['packet_content_sha256'] = fingerprint
    packet['hash_scope'] = ('SHA-256 of canonical exported packet fields excluding packet_content_sha256 '
                            'and hash_scope; not a WAV hash or authenticity signature')
    if len(_canonical(packet)) > MAX_PACKET:
        raise PacketError('Review packet exceeds the safe export size limit')
    return packet


def json_bytes(packet):
    return (json.dumps(packet, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode('utf-8')


def verify_packet_fingerprint(packet):
    if not isinstance(packet, dict):
        return False
    hashvalue = packet.get('packet_content_sha256')
    content = {k: v for k, v in packet.items() if k not in ('packet_content_sha256', 'hash_scope')}
    try:
        return isinstance(hashvalue, str) and hashlib.sha256(_canonical(content)).hexdigest() == hashvalue
    except (TypeError, ValueError, OverflowError):
        return False


def html_bytes(packet):
    """Printable standalone HTML; all user/scanner content is escaped as text."""
    esc = lambda x: html.escape(str(x), quote=True)
    s = packet['session_log_summary']
    scanner = packet['scanner_review']
    notes = packet['investigator_notes']
    events = []
    if scanner:
        for g in scanner.get('groups', []):
            # scanner groups have already been bounded and validated on import
            events.append('<tr><td>' + esc(g.get('review_id', '')) + '</td><td>' +
                          esc(g.get('start', '')) + '–' + esc(g.get('end', '')) +
                          '</td><td>' + esc(g.get('count', '')) + '</td><td>' +
                          esc(g.get('score', '')) + '</td></tr>')
    note_rows = []
    for n in notes:
        note_rows.append('<tr><td>' + esc(n.get('seconds_from_start', '')) +
                         '</td><td>' + esc(n.get('classification', '')) +
                         '</td><td>' + esc(n.get('note', '')) +
                         '</td><td>' + esc(n.get('created_utc', '')) + '</td></tr>')
    boundaries = ''.join('<li>' + esc(x) + '</li>' for x in packet['evidence_boundaries'])
    report_hash = scanner.get('report_sha256', 'not supplied') if scanner else 'No scanner report loaded'
    doc = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>VEIL SIGNAL · MTC Investigator Review Packet</title>
<style>body{font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;max-width:980px;margin:40px auto;padding:0 24px;color:#1c2934}h1{color:#133950}h2{border-bottom:2px solid #c9d8df;padding-bottom:5px;margin-top:30px}small,.muted{color:#526876}.stamp{font-weight:700;border:2px solid #b9cbd2;padding:10px;background:#f1f5f7}table{width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed}th,td{border:1px solid #cdd8de;padding:8px;text-align:left;vertical-align:top;word-break:break-word}th{background:#eaf1f4}li{margin:5px 0}code{overflow-wrap:anywhere}footer{margin-top:35px;border-top:1px solid #cbd7df;padding-top:12px} @media print{body{margin:0;max-width:none;padding:0}h2{break-after:avoid}tr{break-inside:avoid}table{font-size:11px}}</style>
</head><body><header><small>VEIL RESEARCH PROJECT · SIGNAL LOCAL RESEARCH ASSISTANT</small><h1>MTC investigator review packet</h1><p class="stamp">OPERATOR REVIEW RECORD — NOT AN AUTOMATED SCIENTIFIC CONCLUSION</p></header>
<p><strong>Session:</strong> __SID__<br><strong>Exported (UTC):</strong> __WHEN__<br><strong>Logged duration:</strong> __DURATION__ seconds<br><strong>Logged outcome:</strong> __OUTCOME__</p>
<h2>1. Source and scope</h2><p>MTC JSON log consistency checks: __INTEGRITY__. Log event entries: __EVENTS__. Declared recording segments: __SEGMENTS__.</p><p><strong>Audio scanner report SHA-256:</strong> <code>__SCANNER_HASH__</code></p>
<h2>2. Scanner review windows (unclassified acoustic changes)</h2><p>Scanner flags: __RAW__; overlapping review windows: __GROUPED__. These rows do not identify voices or causes.</p>
<table><thead><tr><th>Review ID</th><th>Seconds after start</th><th>Flags grouped</th><th>Scanner score</th></tr></thead><tbody>__EVENT_ROWS__</tbody></table>
<h2>3. Investigator notes (manually entered)</h2><p>Notes: __NOTES_COUNT__. Interpretations are attributed to the local operator, not authenticated or independently confirmed.</p>
<table><thead><tr><th>Time (s)</th><th>Classification</th><th>Operator observation</th><th>Created UTC</th></tr></thead><tbody>__NOTE_ROWS__</tbody></table>
<h2>4. Evidence limitations</h2><ul>__BOUNDARIES__</ul>
<footer><p><strong>Packet content fingerprint (SHA-256):</strong> <code>__FINGERPRINT__</code></p><p class="muted">Fingerprint applies to canonical exported JSON fields, not the original WAV recordings or independent evidence authentication. Re-export after new notes to obtain a new fingerprint. Keep original files separately.</p></footer></body></html>'''
    replacements = {
        '__SID__': esc(packet['session_id']), '__WHEN__': esc(packet['generated_utc']),
        '__DURATION__': esc(s.get('recorded_seconds', 'unknown')), '__OUTCOME__': esc(s.get('outcome', 'unknown')),
        '__INTEGRITY__': esc('matched embedded JSON hashes' if all(s.get('file_integrity', {}).values()) and s.get('file_integrity') else 'unavailable'),
        '__EVENTS__': esc(s.get('events', 'unknown')), '__SEGMENTS__': esc(s.get('segments_declared', 'unknown')),
        '__SCANNER_HASH__': esc(report_hash),
        '__RAW__': esc(scanner['raw_candidates'] if scanner else 'No scanner report'),
        '__GROUPED__': esc(scanner['review_windows'] if scanner else 'No scanner report'),
        '__EVENT_ROWS__': ''.join(events) or '<tr><td colspan="4">No scanner report loaded.</td></tr>',
        '__NOTES_COUNT__': esc(len(notes)),
        '__NOTE_ROWS__': ''.join(note_rows) or '<tr><td colspan="4">No investigator notes recorded.</td></tr>',
        '__BOUNDARIES__': boundaries,
        '__FINGERPRINT__': esc(packet['packet_content_sha256'])
    }
    # Single-pass substitution: user text that resembles a placeholder stays literal.
    doc = re.sub(r'__(?:SID|WHEN|DURATION|OUTCOME|INTEGRITY|EVENTS|SEGMENTS|SCANNER_HASH|RAW|GROUPED|EVENT_ROWS|NOTES_COUNT|NOTE_ROWS|BOUNDARIES|FINGERPRINT)__',
                 lambda match: replacements[match.group(0)], doc)
    return doc.encode('utf-8')
