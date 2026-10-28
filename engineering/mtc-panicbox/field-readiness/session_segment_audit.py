"""VEIL MTC v0.1: offline, read-only *completed* segmented PCM WAV structure audit.

For post-session inspection only. No audio decoding, provenance certification,
recording control, cloud upload, event interpretation or continuity proof.
Python 3.10+ standard library. Prints a report to stdout; never writes to source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct

HEADER_LIMIT = 64 * 1024
CHUNK_SIZE = 1024 * 1024
BASE = 'room_mic_continuous.wav'
PART = re.compile(r'^room_mic_continuous_part(\d{3})\.wav$', re.IGNORECASE)


class AuditError(ValueError):
    """Stable machine-readable error without private paths."""


def _parse_header(header: bytes, total_size: int) -> dict:
    if len(header) < 44:
        raise AuditError('WAV_HEADER_INCOMPLETE')
    if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
        raise AuditError('WAV_UNSUPPORTED_CONTAINER')
    if struct.unpack_from('<I', header, 4)[0] != total_size - 8:
        raise AuditError('WAV_RIFF_LENGTH_MISMATCH')
    offset, fmt, data_size, data_offset = 12, None, None, None
    while offset + 8 <= len(header):
        kind = header[offset:offset + 4]
        n = struct.unpack_from('<I', header, offset + 4)[0]
        body = offset + 8
        if kind == b'fmt ':
            if fmt is not None or n < 16 or body + 16 > len(header):
                raise AuditError('WAV_FMT_INVALID')
            audio_format, channels, rate, byte_rate, align, bits = struct.unpack_from('<HHIIHH', header, body)
            if (audio_format != 1 or not 1 <= channels <= 8 or not 8000 <= rate <= 192000
                    or bits not in (8, 16, 24, 32) or align != channels * (bits // 8)
                    or byte_rate != rate * align):
                raise AuditError('WAV_UNSUPPORTED_PCM_FORMAT')
            fmt = {'channels': channels, 'sample_rate': rate, 'bits_per_sample': bits,
                   'block_align': align}
        elif kind == b'data':
            if fmt is None:
                raise AuditError('WAV_FMT_MISSING_BEFORE_DATA')
            if n == 0:
                raise AuditError('WAV_EMPTY_DATA')
            data_offset, data_size = body, n
            if data_offset + n + (n & 1) != total_size:
                raise AuditError('WAV_DATA_LENGTH_OR_TRAILING_CHUNKS_MISMATCH')
            break
        next_offset = body + n + (n & 1)
        if next_offset > HEADER_LIMIT:
            raise AuditError('WAV_HEADER_TOO_LARGE')
        if next_offset <= offset:
            raise AuditError('WAV_INVALID_CHUNK')
        offset = next_offset
    if data_size is None:
        raise AuditError('WAV_DATA_CHUNK_MISSING_OR_HEADER_TOO_LARGE')
    if data_size % fmt['block_align']:
        raise AuditError('WAV_INCOMPLETE_PCM_FRAME')
    frames = data_size // fmt['block_align']
    return {**fmt, 'frames': frames, 'audio_bytes': data_size,
            'duration_seconds': frames / fmt['sample_rate']}


def inspect_segment(path: Path) -> dict:
    """Hash full original file, check strict finalized RIFF/PCM structure, no writes."""
    if path.is_symlink():
        raise AuditError('WAV_SYMLINK_NOT_ALLOWED')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise AuditError('WAV_UNAVAILABLE') from exc
    try:
        with os.fdopen(fd, 'rb') as f:
            fd = -1
            before = os.fstat(f.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise AuditError('WAV_NOT_REGULAR_FILE')
            if before.st_size < 44:
                raise AuditError('WAV_HEADER_INCOMPLETE')
            header = f.read(min(HEADER_LIMIT, before.st_size))
            info = _parse_header(header, before.st_size)
            f.seek(0)
            digest = hashlib.sha256()
            total = 0
            while True:
                block = f.read(CHUNK_SIZE)
                if not block:
                    break
                total += len(block)
                digest.update(block)
            after = os.fstat(f.fileno())
        if (total != before.st_size or before.st_size != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns
                or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)):
            raise AuditError('WAV_CHANGED_DURING_AUDIT')
        try:
            path_after = path.stat(follow_symlinks=False)
        except OSError as exc:
            raise AuditError('WAV_CHANGED_DURING_AUDIT') from exc
        if (path_after.st_dev, path_after.st_ino, path_after.st_size, path_after.st_mtime_ns) != (
                before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns):
            raise AuditError('WAV_CHANGED_DURING_AUDIT')
        return {**info, 'file_bytes': total, 'sha256': digest.hexdigest()}
    except OSError as exc:
        raise AuditError('WAV_READ_ERROR') from exc
    finally:
        if fd >= 0:
            os.close(fd)


def audit_session(directory: str | Path, *, expected_minutes: float | None = None,
                  tolerance_seconds: float = 120.0) -> dict:
    """Audit one completed session folder, including numbered split WAV files.

    Never claims that adjacent WAV files are sample-contiguous or acoustically
    valid. Does not inspect events.jsonl or session_result.json.
    """
    if expected_minutes is not None and not 0 < expected_minutes <= 10000:
        raise ValueError('expected_minutes must be >0 and <=10000')
    if not 0 <= tolerance_seconds <= 3600:
        raise ValueError('tolerance_seconds must be between 0 and 3600')
    directory = Path(directory)
    report = {
        'schema': 'veil.mtc-segment-audit.v0.1',
        'status': 'UNCONFIRMED', 'alerts': [], 'segments': [],
        'total_frames': 0, 'total_audio_seconds': 0.0,
        'expected_seconds': None if expected_minutes is None else expected_minutes * 60,
        'capture_continuity_verified': False, 'acoustic_capture_verified': False,
        'session_completion_verified': False, 'event_timeline_verified': False,
        'source_write_attempted': False,
        'interpretation': 'Completed WAV structure and SHA-256 audit only; segment joins, acoustic content, event timing, and unattended operation require independent verification.'
    }
    if directory.is_symlink() or not directory.is_dir():
        report['alerts'].append('SESSION_DIRECTORY_UNAVAILABLE_OR_SYMLINK')
        report['status'] = 'ALERT'
        return report
    try:
        entries = list(directory.iterdir())
    except OSError:
        report['alerts'].append('SESSION_DIRECTORY_UNREADABLE')
        report['status'] = 'ALERT'
        return report
    base = []
    parts = {}
    for entry in entries:
        if entry.name.lower() == BASE:
            base.append(entry)
        else:
            match = PART.fullmatch(entry.name)
            if match:
                parts.setdefault(int(match.group(1)), []).append(entry)
    if not base and not parts:
        report['alerts'].append('NO_MATCHING_WAV_SEGMENTS')
        return report
    if len(base) != 1:
        report['alerts'].append('BASE_WAV_MISSING_OR_DUPLICATED')
    if any(i < 2 for i in parts):
        report['alerts'].append('INVALID_PART_NUMBER')
    if any(len(paths) != 1 for paths in parts.values()):
        report['alerts'].append('DUPLICATE_PART_NUMBER')
    if parts:
        expected_parts = set(range(2, max(parts) + 1))
        if set(parts) != expected_parts:
            report['alerts'].append('SEGMENT_SEQUENCE_GAP')
    ordered = base + [p for i in sorted(parts) for p in parts[i]]
    fmt = None
    for path in ordered:
        segment = {'name': path.name}
        try:
            info = inspect_segment(path)
            segment.update(info)
            signature = (info['channels'], info['sample_rate'], info['bits_per_sample'], info['block_align'])
            if fmt is None:
                fmt = signature
            elif signature != fmt:
                report['alerts'].append('SEGMENT_FORMAT_MISMATCH')
            report['total_frames'] += info['frames']
            report['total_audio_seconds'] += info['duration_seconds']
        except AuditError as exc:
            segment['error'] = str(exc)
            report['alerts'].append(str(exc))
        report['segments'].append(segment)
    report['total_audio_seconds'] = round(report['total_audio_seconds'], 3)
    if expected_minutes is not None:
        report['duration_difference_seconds'] = round(report['total_audio_seconds'] - expected_minutes * 60, 3)
        if abs(report['duration_difference_seconds']) > tolerance_seconds:
            report['alerts'].append('DURATION_OUTSIDE_USER_TOLERANCE')
    report['alerts'] = list(dict.fromkeys(report['alerts']))
    report['status'] = 'ALERT' if report['alerts'] else 'STRUCTURE_CONSISTENT_NOT_CONTINUITY_VERIFIED'
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Read-only post-session MTC segmented WAV audit (NOT a continuity proof)')
    parser.add_argument('session_directory', help='Personal home PC: completed session directory')
    parser.add_argument('--expected-minutes', type=float, default=None,
                        help='Optional operator-supplied planned length; not an observed fact')
    parser.add_argument('--tolerance-seconds', type=float, default=120)
    args = parser.parse_args(argv)
    try:
        result = audit_session(args.session_directory, expected_minutes=args.expected_minutes,
                               tolerance_seconds=args.tolerance_seconds)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'STRUCTURE_CONSISTENT_NOT_CONTINUITY_VERIFIED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
