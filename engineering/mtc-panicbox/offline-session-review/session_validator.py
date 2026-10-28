"""Offline read-only checks for a completed VEIL MTC session folder.

No device access, changes to recorder, or claims of EVP/recording continuity.
Only a small explicit event marker vocabulary can be interpreted. Unknown
v0.1.4 event schemas need mapping after inspection of real logs.
"""
from __future__ import annotations
import json
import re
import stat
import wave
from datetime import datetime, timezone
from pathlib import Path

MAX_LOG_BYTES = 16 * 1024 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_EVENTS = 150_000
WAV_NAME = re.compile(r'^room_mic_continuous(?:_part(\d+))?\.wav$', re.I)
START = {'recording_start', 'recording_started', 'recording_begin'}
STOP = {'recording_stop', 'recording_stopped', 'recording_end', 'recording_finished'}
QSTART = {'question_start', 'question_started', 'question_playback_started'}
QEND = {'question_end', 'question_finished', 'question_playback_finished', 'question_playback_ended'}


def _file(path: Path, limit: int | None = None) -> bool:
    """Refuse symbolic links/nonregular files and oversized metadata."""
    if path.is_symlink() or not path.is_file():
        return False
    info = path.stat()
    return stat.S_ISREG(info.st_mode) and (limit is None or info.st_size <= limit)


def _load_json(path: Path, limit: int):
    if not _file(path, limit):
        raise ValueError('missing, unsafe, or oversized JSON file')
    with path.open('r', encoding='utf-8-sig') as fp:
        return json.load(fp)


def _utc(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _wav_order(path: Path):
    name = path.name
    match = WAV_NAME.fullmatch(name)
    if not match:
        return None
    return 1 if match.group(1) is None else int(match.group(1))


def wav_summary(folder: Path):
    wavs = []
    issues = []
    try:
        paths = sorted((p for p in folder.iterdir() if _wav_order(p) is not None), key=_wav_order)
    except OSError as err:
        return [], [{'code': 'SESSION_DIR_UNREADABLE', 'detail': type(err).__name__}]
    if not paths:
        issues.append({'code': 'NO_EXPECTED_WAV_FILES'})
        return wavs, issues
    orders = [_wav_order(p) for p in paths]
    if orders != list(range(1, len(orders)+1)):
        issues.append({'code': 'SEGMENT_NUMBERS_MISSING_OR_DUPLICATE', 'observed': orders})
    first_format = None
    for path in paths:
        if not _file(path):
            issues.append({'code': 'WAV_UNSAFE_OR_MISSING', 'file': path.name})
            continue
        try:
            before = path.stat()
            with wave.open(str(path), 'rb') as stream:
                codec = stream.getcomptype()
                channels, width, rate, frames = (stream.getnchannels(), stream.getsampwidth(),
                                                   stream.getframerate(), stream.getnframes())
                if codec != 'NONE' or channels not in (1,2) or width != 2 or rate <= 0:
                    issues.append({'code': 'WAV_UNSUPPORTED_FOR_SCREENING', 'file': path.name})
                fmt = (channels, width, rate, codec)
                if first_format is not None and fmt != first_format:
                    issues.append({'code': 'SEGMENT_FORMAT_MISMATCH', 'file': path.name})
                first_format = fmt if first_format is None else first_format
                wavs.append({'file': path.name, 'bytes': before.st_size, 'channels': channels,
                             'sample_width_bytes': width, 'sample_rate_hz': rate,
                             'frames': frames, 'duration_seconds': round(frames/rate, 4),
                             'format': codec, 'segment_number': _wav_order(path)})
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                issues.append({'code': 'WAV_CHANGED_DURING_REVIEW', 'file': path.name})
        except (OSError, EOFError, wave.Error, ValueError) as err:
            issues.append({'code': 'WAV_CANNOT_OPEN', 'file': path.name, 'reason': type(err).__name__})
    return wavs, issues


def events_summary(folder: Path, *, total_wav_seconds: float):
    path = folder/'events.jsonl'
    result = {'present': path.exists(), 'events_seen': 0, 'recognized_markers': 0,
              'unknown_types': {}, 'question_pairs': 0, 'question_windows_seconds': [],
              'alignment': 'NOT_VERIFIED', 'recording_marker_duration_seconds': None}
    issues = []
    if not _file(path, MAX_LOG_BYTES):
        issues.append({'code': 'EVENT_LOG_MISSING_UNSAFE_OR_TOO_LARGE'})
        return result, issues
    last_time = None
    recording_start = None
    recording_stop = None
    active_question = None
    marker_types = START | STOP | QSTART | QEND
    try:
        with path.open('r', encoding='utf-8-sig') as fp:
            for lineno, line in enumerate(fp, 1):
                if lineno > MAX_EVENTS:
                    issues.append({'code': 'EVENT_LIMIT_REACHED'})
                    break
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    issues.append({'code': 'MALFORMED_EVENT_JSON', 'line': lineno})
                    continue
                result['events_seen'] += 1
                if not isinstance(event, dict):
                    issues.append({'code': 'EVENT_NOT_OBJECT', 'line': lineno})
                    continue
                raw_type = next((event[k] for k in ('type','event_type','event','name')
                                if isinstance(event.get(k), str)), None)
                if raw_type is None:
                    result['unknown_types']['<missing>'] = result['unknown_types'].get('<missing>', 0)+1
                    continue
                event_type = raw_type.lower().replace('-', '_').replace(' ', '_')
                if event_type not in marker_types:
                    key = event_type[:80]
                    if len(result['unknown_types']) < 30 or key in result['unknown_types']:
                        result['unknown_types'][key] = result['unknown_types'].get(key, 0)+1
                    continue
                result['recognized_markers'] += 1
                stamp = _utc(next((event[k] for k in ('timestamp_utc','timestamp','ts','time')
                                   if k in event), None))
                if stamp is None:
                    issues.append({'code': 'MARKER_TIMESTAMP_MISSING_OR_UNTRUSTED', 'line': lineno})
                    continue
                if last_time is not None and stamp <= last_time:
                    issues.append({'code': 'NON_INCREASING_MARKER_TIME', 'line': lineno})
                last_time = stamp
                if event_type in START:
                    if recording_start is not None:
                        issues.append({'code': 'DUPLICATE_RECORDING_START', 'line': lineno})
                    else:
                        recording_start = stamp
                elif event_type in STOP:
                    if recording_start is None or recording_stop is not None:
                        issues.append({'code': 'UNMATCHED_RECORDING_STOP', 'line': lineno})
                    else:
                        recording_stop = stamp
                elif event_type in QSTART:
                    if active_question is not None or recording_start is None or recording_stop is not None:
                        issues.append({'code': 'INVALID_QUESTION_START', 'line': lineno})
                    else:
                        active_question = stamp
                elif event_type in QEND:
                    if active_question is None:
                        issues.append({'code': 'UNMATCHED_QUESTION_END', 'line': lineno})
                    elif stamp <= active_question:
                        issues.append({'code': 'QUESTION_TIME_INVALID', 'line': lineno})
                        active_question = None
                    else:
                        result['question_pairs'] += 1
                        if recording_start is not None:
                            begin = (active_question-recording_start).total_seconds()
                            end = (stamp-recording_start).total_seconds()
                            result['question_windows_seconds'].append([round(begin,3),round(end,3)])
                        active_question = None
    except (OSError, UnicodeError) as err:
        issues.append({'code': 'EVENT_LOG_READ_FAILED', 'reason': type(err).__name__})
    if active_question is not None:
        issues.append({'code': 'UNCLOSED_QUESTION'})
    if result['recognized_markers'] == 0:
        issues.append({'code': 'EVENT_SCHEMA_UNRECOGNIZED'})
    if recording_start is None or recording_stop is None or recording_stop <= recording_start:
        issues.append({'code': 'RECORDING_START_STOP_NOT_VERIFIED'})
    else:
        duration = (recording_stop-recording_start).total_seconds()
        result['recording_marker_duration_seconds'] = round(duration, 3)
        if abs(duration-total_wav_seconds) > max(2.0, total_wav_seconds*0.01):
            issues.append({'code': 'MARKER_WAV_DURATION_DIFFERENCE', 'seconds': round(duration-total_wav_seconds,3)})
        elif not issues:
            # Time offsets are still not proof of acoustic question playback.
            result['alignment'] = 'MARKER_OFFSETS_PLAUSIBLE_NOT_ACOUSTICALLY_VERIFIED'
    return result, issues


def review(folder: str | Path):
    folder = Path(folder)
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError('Session directory missing or unsafe')
    wavs, issues = wav_summary(folder)
    total = round(sum(x['duration_seconds'] for x in wavs), 4)
    events, event_issues = events_summary(folder, total_wav_seconds=total)
    issues.extend(event_issues)
    metadata = {}
    for filename in ('session_result.json','session_metadata.json'):
        path = folder/filename
        try:
            value = _load_json(path, MAX_JSON_BYTES)
            metadata[filename] = {'present': True, 'valid_json_object': isinstance(value,dict),
                                  'top_level_keys': sorted(map(str,value))[:60] if isinstance(value,dict) else []}
            if not isinstance(value,dict):
                issues.append({'code': 'SESSION_JSON_NOT_OBJECT', 'file': filename})
        except (ValueError, OSError, UnicodeError, json.JSONDecodeError):
            metadata[filename] = {'present': False, 'valid_json_object': False}
            issues.append({'code': 'SESSION_JSON_MISSING_OR_INVALID', 'file': filename})
    return {'schema': 'veil.offline-mtc-session-review.v0.1',
            'read_only': True, 'files_examined_from_disk': True,
            'session_label': folder.name, 'wav_segments': wavs, 'total_wav_duration_seconds': total,
            'segment_file_boundary_continuity': 'UNVERIFIED_WITHOUT_INDEPENDENT_TIME_ANCHORS',
            'events': events, 'metadata': metadata, 'issues': issues,
            'structure_status': 'REVIEW_REQUIRED' if issues else 'NO_STRUCTURAL_ISSUES_OBSERVED',
            'physical_acoustic_playback_confirmed': False,
            'paranormal_cause_established': False,
            'limitations': ('WAV frame counts and log markers cannot prove continuous sound capture, '
                            'segment seams, playback audibility, clock synchronization, or anomalous cause. '
                            'Actual MTC v0.1.4 event/JSON schema has not yet been verified.')}
