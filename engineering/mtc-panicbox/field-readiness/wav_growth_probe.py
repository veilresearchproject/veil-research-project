"""VEIL independent WAV-growth probe v0.1 (read-only, local, synthetic-tested).

This is NOT a recorder, audio validator, phone monitor or health certificate.
Physical file growth and approximate complete-frame counts do not prove sound,
source identity, microphone connection, or WAV integrity. No file modifications.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import struct
import time

HEADER_LIMIT = 64 * 1024


class WaveProbeError(ValueError):
    """Machine-readable fail-closed error; does not expose file paths."""


def read_wav_snapshot(path: str | Path) -> dict:
    """Inspect a bounded WAV header and filesystem length, without reading audio.

    Supports classic RIFF/WAVE uncompressed integer PCM, with fmt before data.
    Assumes live PCM payload extends from the data chunk to EOF; appended RIFF
    metadata, RF64, WAVE64, compressed and float WAVs are unsupported. For these,
    return UNCONFIRMED/ALERT rather than infer reliable audio-frame progress.
    """
    path = os.fspath(path)
    if os.path.islink(path):
        raise WaveProbeError('WAV_SYMLINK_NOT_ALLOWED')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise WaveProbeError('WAV_UNAVAILABLE') from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise WaveProbeError('WAV_NOT_REGULAR_FILE')
        if st.st_size < 44:
            raise WaveProbeError('WAV_HEADER_INCOMPLETE')
        header = os.read(fd, min(st.st_size, HEADER_LIMIT))
    except OSError as exc:
        raise WaveProbeError('WAV_READ_ERROR') from exc
    finally:
        os.close(fd)

    if len(header) < 12 or header[:4] != b'RIFF' or header[8:12] != b'WAVE':
        raise WaveProbeError('WAV_UNSUPPORTED_CONTAINER')
    offset = 12
    fmt = None
    data_offset = None
    declared_data_bytes = None
    while offset + 8 <= len(header):
        chunk_type = header[offset:offset + 4]
        chunk_size = struct.unpack_from('<I', header, offset + 4)[0]
        body = offset + 8
        if chunk_type == b'fmt ':
            if chunk_size < 16 or body + 16 > len(header):
                raise WaveProbeError('WAV_FMT_INCOMPLETE')
            audio_format, channels, sample_rate, byte_rate, block_align, bits = struct.unpack_from(
                '<HHIIHH', header, body)
            if (audio_format != 1 or channels not in range(1, 9) or
                    not 8000 <= sample_rate <= 192000 or bits not in (8, 16, 24, 32) or
                    block_align != channels * (bits // 8) or
                    byte_rate != sample_rate * block_align):
                raise WaveProbeError('WAV_UNSUPPORTED_FORMAT')
            fmt = (channels, sample_rate, bits, block_align)
        if chunk_type == b'data':
            if fmt is None:
                raise WaveProbeError('WAV_FMT_MISSING_BEFORE_DATA')
            data_offset = body
            declared_data_bytes = chunk_size
            break
        # Refuse to jump beyond our bounded header scan.
        next_offset = body + chunk_size + (chunk_size % 2)
        if next_offset > HEADER_LIMIT:
            raise WaveProbeError('WAV_HEADER_TOO_LARGE')
        if next_offset <= offset:
            raise WaveProbeError('WAV_INVALID_CHUNK')
        offset = next_offset
    if data_offset is None:
        raise WaveProbeError('WAV_DATA_CHUNK_NOT_FOUND')
    if data_offset > st.st_size:
        raise WaveProbeError('WAV_DATA_OFFSET_INVALID')
    channels, sample_rate, bits, block_align = fmt
    payload = st.st_size - data_offset
    return {
        'identity': (st.st_dev, st.st_ino),
        'file_bytes': st.st_size,
        'data_offset': data_offset,
        'payload_bytes_estimate': payload,
        'complete_frames_estimate': payload // block_align,
        'partial_frame_bytes': payload % block_align,
        'declared_data_bytes': declared_data_bytes,
        'header_size_differs': declared_data_bytes != payload,
        'format': (channels, sample_rate, bits, block_align),
    }


class WaveGrowthProbe:
    """Separate RAM-only observer. No recorder/phone/equipment access."""

    def __init__(self, *, stalled_after_seconds: float = 20.0):
        if not 0 < stalled_after_seconds <= 3600:
            raise ValueError('invalid stalled_after_seconds')
        self.stalled_after_seconds = float(stalled_after_seconds)
        self.previous = None
        self.last_progress_at = None
        self.last_tick = None
        self.latched_fault = None

    @staticmethod
    def result(status: str, alerts: list[str], snapshot=None) -> dict:
        return {
            'schema': 'veil.wav-growth-probe.v0.1',
            'status': status,
            'alerts': alerts,
            'simulation_only': False,
            'physical_capture_validated': False,
            'equipment_control_enabled': False,
            'observed_file_bytes': snapshot['file_bytes'] if snapshot else None,
            'estimated_complete_frames': snapshot['complete_frames_estimate'] if snapshot else None,
            'header_size_differs': snapshot['header_size_differs'] if snapshot else None,
            'interpretation': 'Read-only file-growth observation; never proof of acoustic capture, provenance, or valid audio.',
        }

    def check(self, path: str | Path, *, now_monotonic: float | None = None) -> dict:
        tick = time.monotonic() if now_monotonic is None else float(now_monotonic)
        if self.last_tick is not None and tick < self.last_tick:
            self.previous = None
            self.last_progress_at = None
            self.latched_fault = 'WAV_PROBE_CLOCK_REGRESSION'
        self.last_tick = tick
        if self.latched_fault:
            return self.result('ALERT', [self.latched_fault])
        try:
            current = read_wav_snapshot(path)
        except WaveProbeError as exc:
            self.previous = None
            self.last_progress_at = None
            return self.result('ALERT', [str(exc)])
        if self.previous is None:
            self.previous = current
            self.last_progress_at = tick
            if current['partial_frame_bytes']:
                return self.result('UNCONFIRMED', ['WAV_PARTIAL_FRAME', 'SECOND_WAV_SAMPLE_REQUIRED'], current)
            return self.result('UNCONFIRMED', ['SECOND_WAV_SAMPLE_REQUIRED'], current)
        prev = self.previous
        if current['identity'] != prev['identity']:
            self.latched_fault = 'WAV_FILE_REPLACED_REBASE_REQUIRED'
        elif current['format'] != prev['format'] or current['data_offset'] != prev['data_offset']:
            self.latched_fault = 'WAV_FORMAT_CHANGED_REBASE_REQUIRED'
        elif current['file_bytes'] < prev['file_bytes']:
            self.latched_fault = 'WAV_TRUNCATED_REBASE_REQUIRED'
        if self.latched_fault:
            return self.result('ALERT', [self.latched_fault], current)
        if current['partial_frame_bytes']:
            # Could be a transient writer state; persistent incompleteness is an alert.
            if tick - self.last_progress_at > self.stalled_after_seconds:
                return self.result('ALERT', ['WAV_PARTIAL_FRAME', 'WAV_NO_FRAME_PROGRESS'], current)
            return self.result('UNCONFIRMED', ['WAV_PARTIAL_FRAME'], current)
        if current['complete_frames_estimate'] > prev['complete_frames_estimate']:
            self.previous = current
            self.last_progress_at = tick
            notes = ['WAV_HEADER_SIZE_NOT_FINALIZED'] if current['header_size_differs'] else []
            return self.result('GROWTH_OBSERVED_NOT_AUDIO_VERIFIED', notes, current)
        if tick - self.last_progress_at > self.stalled_after_seconds:
            return self.result('ALERT', ['WAV_NO_FRAME_PROGRESS'], current)
        return self.result('UNCONFIRMED', ['WAITING_FOR_WAV_FRAME_PROGRESS'], current)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='VEIL read-only local PCM WAV growth observer; not an audio validator')
    p.add_argument('wav_path', help='Explicit active PCM WAV file path; never modifies it')
    p.add_argument('--poll-seconds', type=float, default=5.0)
    p.add_argument('--stalled-after-seconds', type=float, default=20.0)
    p.add_argument('--once', action='store_true', help='One observation cannot establish growth')
    args = p.parse_args(argv)
    if not 0 < args.poll_seconds <= 3600:
        p.error('poll-seconds must be >0 and <=3600')
    try:
        probe = WaveGrowthProbe(stalled_after_seconds=args.stalled_after_seconds)
    except ValueError as exc:
        p.error(str(exc))
    try:
        while True:
            print(json.dumps(probe.check(args.wav_path)), flush=True)
            if args.once:
                return 0
            time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
