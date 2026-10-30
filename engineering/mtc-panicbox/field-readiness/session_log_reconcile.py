"""VEIL MTC v0.1: read-only completed-session log/WAV timing reconciliation.

Offline Python 3.10+ standard library. Does not establish recording continuity,
question audibility, microphone health, provenance, or paranormal phenomena.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import stat

from session_segment_audit import audit_session

MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_LINE_BYTES = 64 * 1024
MAX_EVENTS = 100000
EVENT_NAMES = ('event', 'type')
TIME_NAMES = ('elapsed_seconds', 't_seconds', 'time_seconds')
START = {'recording_start', 'recording_started'}
STOP = {'recording_stop', 'recording_stopped'}
QSTART = {'question_start'}
QEND = {'question_end'}
ERROR_EVENTS = {'recording_error', 'writer_error', 'microphone_error', 'storage_error',
                'callback_drop', 'audio_overflow', 'device_disconnected', 'fatal_error'}


class SourceProblem(ValueError):
    pass


def _read_original(path: Path) -> tuple[bytes, dict]:
    """Bounded, no-follow, single-open read; check file identity before/after."""
    if path.is_symlink():
        raise SourceProblem('SOURCE_SYMLINK_REJECTED')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise SourceProblem('SOURCE_MISSING_OR_UNREADABLE') from exc
    try:
        with os.fdopen(fd, 'rb') as f:
            fd = -1
            a = os.fstat(f.fileno())
            if not stat.S_ISREG(a.st_mode):
                raise SourceProblem('SOURCE_NOT_REGULAR_FILE')
            if a.st_size > MAX_FILE_BYTES:
                raise SourceProblem('SOURCE_EXCEEDS_SIZE_LIMIT')
            data = f.read(MAX_FILE_BYTES + 1)
            b = os.fstat(f.fileno())
        if len(data) > MAX_FILE_BYTES or len(data) != a.st_size:
            raise SourceProblem('SOURCE_CHANGED_DURING_READ')
        if (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns) != (b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns):
            raise SourceProblem('SOURCE_CHANGED_DURING_READ')
        try:
            c = path.stat(follow_symlinks=False)
        except OSError as exc:
            raise SourceProblem('SOURCE_CHANGED_DURING_READ') from exc
        if (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns) != (c.st_dev, c.st_ino, c.st_size, c.st_mtime_ns):
            raise SourceProblem('SOURCE_CHANGED_DURING_READ')
        return data, {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    except OSError as exc:
        raise SourceProblem('SOURCE_READ_ERROR') from exc
    finally:
        if fd >= 0:
            os.close(fd)


def _parse_json(data: bytes) -> dict:
    try:
        value = json.loads(data.decode('utf-8-sig'))
    except (UnicodeError, ValueError) as exc:
        raise SourceProblem('INVALID_JSON_OBJECT') from exc
    if not isinstance(value, dict):
        raise SourceProblem('INVALID_JSON_OBJECT')
    return value


def _event_name(record: dict) -> str | None:
    for key in EVENT_NAMES:
        val = record.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().lower()
    return None


def _event_time(record: dict) -> float | None:
    for key in TIME_NAMES:
        if key in record:
            value = record[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return None
            t = float(value)
            return t if math.isfinite(t) and t >= 0 else None
    return None


def _parse_events(data: bytes) -> tuple[list[tuple[str, float | None]], Counter]:
    records = []
    counts = Counter()
    if not data.strip():
        raise SourceProblem('EMPTY_EVENT_LOG')
    for line in data.splitlines():
        if not line.strip():
            continue
        if len(line) > MAX_LINE_BYTES:
            raise SourceProblem('EVENT_LINE_TOO_LARGE')
        if len(records) >= MAX_EVENTS:
            raise SourceProblem('EVENT_COUNT_LIMIT')
        try:
            record = json.loads(line.decode('utf-8-sig'))
        except (UnicodeError, ValueError) as exc:
            raise SourceProblem('INVALID_EVENT_JSONL') from exc
        if not isinstance(record, dict):
            raise SourceProblem('INVALID_EVENT_JSONL')
        name = _event_name(record)
        if name is None:
            raise SourceProblem('EVENT_TYPE_UNRECOGNIZED_SCHEMA')
        records.append((name, _event_time(record)))
        counts[name] += 1
    if not records:
        raise SourceProblem('EMPTY_EVENT_LOG')
    return records, counts


def reconcile_session(folder: str | Path, *, expected_minutes: float | None = None,
                      tolerance_seconds: float = 120.0) -> dict:
    """Inspect completed session only. No output written to source directory."""
    root = Path(folder)
    report = {
        'schema': 'veil.mtc-log-reconcile.v0.1', 'status': 'UNCONFIRMED',
        'alerts': [], 'holds': [], 'sources': {}, 'events': {},
        'wav': {}, 'originals_modified_by_tool': False,
        'capture_continuity_verified': False, 'question_audibility_verified': False,
        'physical_session_validated': False, 'provenance_established': False,
        'interpretation': 'Log/WAV structural plausibility only. Independently verify audio, clocks, hardware and event meaning.'
    }
    if root.is_symlink() or not root.is_dir():
        report['alerts'].append('SESSION_FOLDER_UNAVAILABLE_OR_SYMLINK')
        report['status'] = 'ALERT'
        return report
    wav = audit_session(root, expected_minutes=expected_minutes, tolerance_seconds=tolerance_seconds)
    report['wav'] = {'status': wav['status'], 'total_audio_seconds': wav['total_audio_seconds'],
                     'segment_count': len(wav['segments']), 'alerts': wav['alerts'],
                     'segments': [{'name': x['name'], 'sha256': x.get('sha256'),
                                   'duration_seconds': x.get('duration_seconds')}
                                  for x in wav['segments']]}
    if wav['status'] != 'STRUCTURE_CONSISTENT_NOT_CONTINUITY_VERIFIED':
        report['alerts'].append('WAV_STRUCTURAL_AUDIT_NOT_CLEAN')
    parsed = {}
    for name in ('events.jsonl', 'session_result.json', 'session_metadata.json'):
        try:
            data, info = _read_original(root / name)
            report['sources'][name] = info
            parsed[name] = _parse_events(data) if name == 'events.jsonl' else _parse_json(data)
        except SourceProblem as exc:
            report['alerts'].append(name.upper().replace('.', '_') + '_' + str(exc))
    if 'session_result.json' in parsed:
        result = parsed['session_result.json']
        report['result_keys'] = sorted(str(k) for k in result.keys())[:40]
        for k in ('error', 'fatal_error', 'exception'):
            if result.get(k):
                report['alerts'].append('RESULT_REPORTED_ERROR')
        for k in ('status', 'result', 'outcome'):
            val = result.get(k)
            if isinstance(val, str) and val.strip().lower() in {'failed', 'failure', 'error', 'aborted', 'crashed'}:
                report['alerts'].append('RESULT_REPORTED_FAILURE')
        # No known, verified result schema: never infer a normal stop from generic success text.
        report['holds'].append('RESULT_SCHEMA_NOT_AUTHENTICATED_FOR_NORMAL_STOP')
    if 'session_metadata.json' in parsed:
        report['metadata_keys'] = sorted(str(k) for k in parsed['session_metadata.json'].keys())[:40]
    if 'events.jsonl' in parsed:
        records, counts = parsed['events.jsonl']
        report['events'] = {'count': len(records), 'types': dict(sorted(counts.items())),
                            'question_pairs': 0, 'recording_marker_span_seconds': None}
        if any(name in ERROR_EVENTS or name.endswith('_error') for name, _ in records):
            report['alerts'].append('LOG_REPORTED_RECORDING_OR_DEVICE_ERROR')
        times = [t for _, t in records]
        if any(t is None for t in times):
            report['holds'].append('EVENT_TIME_SCHEMA_INCOMPLETE_OR_UNRECOGNIZED')
        elif any(b < a for a, b in zip(times, times[1:])):
            report['alerts'].append('EVENT_TIMES_OUT_OF_ORDER')
        else:
            active_question = None
            recording_start = None
            recording_stop = None
            for name, t in records:
                if name in START:
                    if recording_start is not None:
                        report['alerts'].append('DUPLICATE_RECORDING_START')
                    recording_start = t
                elif name in STOP:
                    if recording_stop is not None:
                        report['alerts'].append('DUPLICATE_RECORDING_STOP')
                    recording_stop = t
                elif name in QSTART:
                    if active_question is not None:
                        report['alerts'].append('OVERLAPPING_QUESTION_MARKERS')
                    active_question = t
                elif name in QEND:
                    if active_question is None or t < active_question:
                        report['alerts'].append('QUESTION_END_WITHOUT_START')
                    else:
                        report['events']['question_pairs'] += 1
                    active_question = None
            if active_question is not None:
                report['alerts'].append('QUESTION_START_WITHOUT_END')
            if recording_start is None or recording_stop is None:
                report['holds'].append('RECORDING_START_STOP_MARKERS_MISSING')
            elif recording_stop < recording_start:
                report['alerts'].append('RECORDING_STOP_BEFORE_START')
            else:
                span = round(recording_stop - recording_start, 3)
                report['events']['recording_marker_span_seconds'] = span
                if abs(span - wav['total_audio_seconds']) > tolerance_seconds:
                    report['alerts'].append('LOG_WAV_DURATION_MISMATCH')
            if counts['question_start'] == 0 and counts['question_end'] == 0:
                report['holds'].append('NO_RECOGNIZED_QUESTION_MARKERS')
    report['alerts'] = sorted(set(report['alerts']))
    report['holds'] = sorted(set(report['holds']))
    report['status'] = ('ALERT' if report['alerts'] else
                        'UNCONFIRMED' if report['holds'] else
                        'TIMELINE_PLAUSIBLE_NOT_VALIDATED')
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='Read-only completed MTC log/WAV plausibility audit (not validation)')
    p.add_argument('session_directory', help='Personal home PC, finished session folder')
    p.add_argument('--expected-minutes', type=float, default=None, help='Planned duration, not an observed fact')
    p.add_argument('--tolerance-seconds', type=float, default=120.0)
    a = p.parse_args(argv)
    try:
        report = reconcile_session(a.session_directory, expected_minutes=a.expected_minutes,
                                   tolerance_seconds=a.tolerance_seconds)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if report['status'] != 'TIMELINE_PLAUSIBLE_NOT_VALIDATED' else 0


if __name__ == '__main__':
    raise SystemExit(main())
