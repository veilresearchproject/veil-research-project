"""VEIL MTC v0.1: offline read-only *screening* of joins between completed PCM WAVs.

Not a continuity test, EVP detector, sound-source attribution, or live monitor.
Requires session_segment_audit.py from the Oct 28 draft branch.
Python 3.10+ standard library; never writes to evidence or stores audio.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import struct
import wave

from session_segment_audit import audit_session

CHUNK = 1024 * 1024
MAX_EDGE_SAMPLES = 250_000


class SeamError(ValueError):
    pass


def _samples(data: bytes, width: int) -> list[float]:
    if width == 1:
        return [(v - 128) / 128.0 for v in data]
    if width == 2:
        return [v / 32768.0 for v in struct.unpack('<' + 'h' * (len(data) // 2), data)]
    if width in (3, 4):
        limit = float(1 << (width * 8 - 1))
        return [int.from_bytes(data[i:i + width], 'little', signed=True) / limit
                for i in range(0, len(data), width)]
    raise SeamError('UNSUPPORTED_SAMPLE_WIDTH')


def _rms_db(samples: list[float]) -> float | None:
    if not samples:
        return None
    mean_square = sum(v * v for v in samples) / len(samples)
    return round(20 * math.log10(math.sqrt(mean_square)), 2) if mean_square else -120.0


def _edge(path: Path, expected_sha: str, seconds: float) -> dict:
    """Read exact original bytes and edge windows on one read-only descriptor."""
    if path.is_symlink():
        raise SeamError('SYMLINK_NOT_ALLOWED')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise SeamError('FILE_UNAVAILABLE') from exc
    try:
        with os.fdopen(fd, 'rb') as f:
            fd = -1
            before = os.fstat(f.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise SeamError('NOT_REGULAR_FILE')
            sha = hashlib.sha256()
            while True:
                block = f.read(CHUNK)
                if not block:
                    break
                sha.update(block)
            if sha.hexdigest() != expected_sha:
                raise SeamError('SHA_CHANGED_SINCE_STRUCTURE_AUDIT')
            f.seek(0)
            try:
                with wave.open(f, 'rb') as wav:
                    if wav.getcomptype() != 'NONE':
                        raise SeamError('UNSUPPORTED_COMPRESSED_AUDIO')
                    channels, width, rate, total = (wav.getnchannels(), wav.getsampwidth(),
                                                    wav.getframerate(), wav.getnframes())
                    n = min(total, max(1, int(round(rate * seconds))))
                    if n * channels > MAX_EDGE_SAMPLES:
                        raise SeamError('EDGE_WINDOW_EXCEEDS_MEMORY_BOUND')
                    first = wav.readframes(n)
                    wav.setpos(total - n)
                    last = wav.readframes(n)
            except SeamError:
                raise
            except (wave.Error, EOFError, ValueError, OSError) as exc:
                raise SeamError('WAV_DECODE_ERROR') from exc
            if len(first) != n * channels * width or len(last) != n * channels * width:
                raise SeamError('EDGE_READ_INCOMPLETE')
            after = os.fstat(f.fileno())
        try:
            final = path.stat(follow_symlinks=False)
        except OSError as exc:
            raise SeamError('FILE_CHANGED_DURING_SCREEN') from exc
        def identity(s):
            return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
        if identity(before) != identity(after) or identity(before) != identity(final):
            raise SeamError('FILE_CHANGED_DURING_SCREEN')
        a, b = _samples(first, width), _samples(last, width)
        return {'channels': channels, 'width': width, 'rate': rate, 'frames': total,
                'window_frames': n, 'first_rms_dbfs': _rms_db(a),
                'last_rms_dbfs': _rms_db(b),
                'first_clipped_fraction': round(sum(abs(v) >= 0.999 for v in a) / len(a), 5),
                'last_clipped_fraction': round(sum(abs(v) >= 0.999 for v in b) / len(b), 5),
                '_first_samples': a[:channels], '_last_samples': b[-channels:]}
    except OSError as exc:
        raise SeamError('FILE_READ_ERROR') from exc
    finally:
        if fd >= 0:
            os.close(fd)


def screen_session(directory: str | Path, *, window_seconds: float = 0.25,
                   quiet_dbfs: float = -55.0, jump_fraction: float = 0.5) -> dict:
    """Screen each join for conspicuous edge silence, clipping and sample steps.

    A small step is NOT evidence of contiguous recording; a large step is NOT
    evidence of a dropped frame. Only a cue for human listening/independent logs.
    """
    if not (math.isfinite(window_seconds) and 0.01 <= window_seconds <= 1):
        raise ValueError('window_seconds must be 0.01..1')
    if not (math.isfinite(quiet_dbfs) and -120 <= quiet_dbfs <= -5):
        raise ValueError('quiet_dbfs must be -120..-5')
    if not (math.isfinite(jump_fraction) and 0 < jump_fraction <= 2):
        raise ValueError('jump_fraction must be >0..2')
    result = {'schema': 'veil.mtc-wav-seam-screen.v0.1', 'status': 'UNCONFIRMED',
              'alerts': [], 'joins': [], 'screening_only': True,
              'capture_continuity_verified': False, 'microphone_verified': False,
              'session_completion_verified': False, 'source_write_attempted': False,
              'interpretation': 'Edge sample statistics are review cues, NOT evidence of continuous recording, missing frames, microphone validity, or anomalous sound.'}
    audit = audit_session(directory)
    if audit['status'] != 'STRUCTURE_CONSISTENT_NOT_CONTINUITY_VERIFIED':
        result['status'] = 'HOLD'
        result['alerts'] = ['STRUCTURAL_AUDIT_NOT_CLEAN'] + audit['alerts']
        return result
    if len(audit['segments']) < 2:
        result['status'] = 'NO_JOINS'
        return result
    edges = []
    for seg in audit['segments']:
        try:
            edges.append(_edge(Path(directory) / seg['name'], seg['sha256'], window_seconds))
        except SeamError as exc:
            result['status'] = 'HOLD'
            result['alerts'] = [str(exc)]
            result['joins'] = []
            return result
    for i in range(len(edges) - 1):
        prev, nxt = edges[i:i+2]
        if (prev['channels'], prev['width'], prev['rate']) != (nxt['channels'], nxt['width'], nxt['rate']):
            result['status'] = 'HOLD'
            result['alerts'] = ['SEGMENT_FORMAT_CHANGED']
            result['joins'] = []
            return result
        step = max(abs(x - y) for x, y in zip(prev['_last_samples'], nxt['_first_samples']))
        cues = []
        if prev['last_rms_dbfs'] <= quiet_dbfs:
            cues.append('PREVIOUS_TAIL_QUIET')
        if nxt['first_rms_dbfs'] <= quiet_dbfs:
            cues.append('NEXT_HEAD_QUIET')
        if step >= jump_fraction:
            cues.append('LARGE_JOIN_SAMPLE_STEP_REVIEW_ONLY')
        if prev['last_clipped_fraction'] >= 0.01 or nxt['first_clipped_fraction'] >= 0.01:
            cues.append('EDGE_CLIPPING_REVIEW_ONLY')
        result['joins'].append({'from': audit['segments'][i]['name'],
                                'to': audit['segments'][i + 1]['name'],
                                'previous_tail_rms_dbfs': prev['last_rms_dbfs'],
                                'next_head_rms_dbfs': nxt['first_rms_dbfs'],
                                'previous_tail_clipped_fraction': prev['last_clipped_fraction'],
                                'next_head_clipped_fraction': nxt['first_clipped_fraction'],
                                'join_sample_step_fraction_full_scale': round(step, 5),
                                'window_seconds_requested': window_seconds,
                                'window_frames_each_side': [prev['window_frames'], nxt['window_frames']],
                                'review_cues': cues})
    result['status'] = 'SCREENED_NOT_CONTINUITY_VERIFIED'
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='MTC read-only WAV seam screening; never continuity proof')
    p.add_argument('session_directory', help='Completed copied evidence folder, PERSONAL home PC only')
    p.add_argument('--window-seconds', type=float, default=0.25)
    p.add_argument('--quiet-dbfs', type=float, default=-55)
    p.add_argument('--jump-fraction', type=float, default=0.5)
    a = p.parse_args(argv)
    try:
        result = screen_session(a.session_directory, window_seconds=a.window_seconds,
                                quiet_dbfs=a.quiet_dbfs, jump_fraction=a.jump_fraction)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result['status'] in ('SCREENED_NOT_CONTINUITY_VERIFIED', 'NO_JOINS') else 2


if __name__ == '__main__':
    raise SystemExit(main())
