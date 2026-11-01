"""Read-only MTC v0.1.4 session-log adapter for SIGNAL (Python standard library).

Log assertions are not measurements of acoustic content; WAV audio is never opened.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
import re
from pathlib import Path

FILES = ('session_result.json', 'session_metadata.json', 'events.jsonl')
MAX_BYTES = {'session_result.json': 2_000_000,
             'session_metadata.json': 2_000_000,
             'events.jsonl': 20_000_000}


class EvidenceError(ValueError):
    """Invalid or inconsistent MTC log package."""


def _read(folder, name):
    path = folder / name
    if path.is_symlink() or not path.is_file():
        raise EvidenceError('Missing or linked MTC log: ' + name)
    if path.stat().st_size > MAX_BYTES[name]:
        raise EvidenceError('MTC log exceeds size limit: ' + name)
    return path.read_bytes()


def _object(raw, name):
    try:
        value = json.loads(raw.decode('utf-8'))
    except (UnicodeError, ValueError) as exc:
        raise EvidenceError('Unreadable JSON: ' + name) from exc
    if not isinstance(value, dict):
        raise EvidenceError('Expected JSON object: ' + name)
    return value


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise EvidenceError('Invalid numeric field: ' + label)
    return value


def _label(value, field, limit=80):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,' + str(limit) + r'}', value):
        raise EvidenceError('Invalid MTC label: ' + field)
    return value


def read_session(folder):
    """Return bounded, deterministic facts from *logs only*, without modifying files."""
    folder = Path(folder).expanduser()
    if folder.is_symlink() or not folder.is_dir():
        raise EvidenceError('Choose a local MTC session folder')
    raw = {name: _read(folder, name) for name in FILES}
    result = _object(raw[FILES[0]], FILES[0])
    meta = _object(raw[FILES[1]], FILES[1])

    integrity = {}
    for name, field in [('session_metadata.json', 'metadata_sha256'),
                        ('events.jsonl', 'events_sha256')]:
        expected = result.get(field)
        actual = hashlib.sha256(raw[name]).hexdigest()
        integrity[name] = expected == actual
        if not integrity[name]:
            raise EvidenceError('SHA-256 mismatch for ' + name)

    events = []
    previous = -1.0
    for lineno, line in enumerate(raw['events.jsonl'].splitlines(), 1):
        if not line.strip():
            continue
        entry = _object(line, 'events.jsonl line ' + str(lineno))
        seconds = _number(entry.get('seconds_from_start'), 'event time')
        if seconds + 0.00001 < previous:
            raise EvidenceError('Event timestamps run backward at line ' + str(lineno))
        previous = seconds
        if not isinstance(entry.get('event'), str):
            raise EvidenceError('Missing event name at line ' + str(lineno))
        events.append(entry)
    if not events:
        raise EvidenceError('Empty events.jsonl')

    rate = _number(meta.get('sample_rate'), 'sample_rate')
    if rate == 0:
        raise EvidenceError('Invalid zero sample rate')
    segments = result.get('recording_segments')
    if not isinstance(segments, list) or not segments or len(segments) > 200:
        raise EvidenceError('Missing or invalid recording segment list')
    frame_cursor = 0
    for part in segments:
        if not isinstance(part, dict) or part.get('start_frame') != frame_cursor:
            raise EvidenceError('Recording segment frame offsets are not contiguous')
        frames = _number(part.get('frames'), 'segment frames')
        if not isinstance(frames, int) or frames < 1:
            raise EvidenceError('Invalid segment frame count')
        frame_cursor += frames
    if frame_cursor != result.get('total_recording_frames'):
        raise EvidenceError('Total frame count does not match segments')
    primary = result.get('primary_recording_info')
    if not isinstance(primary, dict) or primary.get('frames') != frame_cursor or primary.get('segments') != len(segments):
        raise EvidenceError('Primary recording declaration does not match segments')
    duration = frame_cursor / rate
    if abs(_number(primary.get('duration_seconds'), 'duration_seconds') - duration) > 0.1:
        raise EvidenceError('Declared duration does not match frame count')
    if not isinstance(result.get('faults'), list):
        raise EvidenceError('Invalid faults field')

    counts = Counter(e['event'] for e in events)
    completed = Counter(e['event'] for e in events if e.get('completed') is True)
    questions = len(meta.get('questions', [])) if isinstance(meta.get('questions'), list) else None
    final = [e for e in events if e['event'] == 'session_finished']
    if len(final) != 1 or final[0].get('outcome') != result.get('outcome'):
        raise EvidenceError('Session result disagrees with finish event')
    return {
        'source': 'MTC session JSON logs only (audio WAV not inspected)',
        'session_id': _label(meta.get('session_id'), 'session_id'),
        'software_version': _label(meta.get('version'), 'version'),
        'outcome': _label(result.get('outcome'), 'outcome', 40),
        'fault_count': len(result['faults']),
        'recorded_seconds': round(duration, 3),
        'segments_declared': len(segments),
        'segment_frame_offsets_contiguous_in_logs': True,
        'file_integrity': integrity,
        'events': len(events),
        'question_files_listed': questions,
        'question_starts_logged': counts['question_start'],
        'question_ends_completed_logged': completed['question_end'],
        'response_windows_completed_logged': completed['response_window_end'],
        'cycles_started_logged': counts['question_cycle_start'],
        'cycles_completed_logged': counts['question_cycle_end'],
        'limitations': ('This checks reported software events and SHA-256 of JSON logs, '
                        'not WAV bytes, playback audibility, acoustic continuity, EVP, '
                        'human presence, or any cause of a sound.'),
    }


def format_summary(data):
    return ('SIGNAL MTC READ-ONLY LOG REVIEW\n'
            'Session: {session_id} | software: {software_version}\n'
            'Outcome reported: {outcome} | logged faults: {fault_count}\n'
            'Declared recording: {recorded_seconds} seconds across {segments_declared} segments; '
            'frame offsets contiguous in logs (not independently verified WAV audio).\n'
            'Question starts/finished: {question_starts_logged}/{question_ends_completed_logged}; '
            'completed response windows: {response_windows_completed_logged}.\n'
            'Cycles started/completed: {cycles_started_logged}/{cycles_completed_logged}; '
            'question WAVs listed: {question_files_listed}.\n'
            'Metadata and event-log SHA-256 match result: yes.\n'
            'LIMITATION: {limitations}').format(**data)


def main(argv=None):
    parser = argparse.ArgumentParser(description='SIGNAL read-only MTC session-log review')
    parser.add_argument('folder', type=Path, help='MTC session folder containing three JSON logs')
    parser.add_argument('--json', action='store_true', help='print machine-readable facts')
    args = parser.parse_args(argv)
    try:
        facts = read_session(args.folder)
    except (EvidenceError, OSError) as exc:
        parser.exit(2, 'SIGNAL MTC BLOCKED: ' + str(exc) + '\n')
    print(json.dumps(facts, indent=2) if args.json else format_summary(facts))


if __name__ == '__main__':
    main()
