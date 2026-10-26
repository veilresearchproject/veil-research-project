"""Independent, read-only *synthetic* VEIL field-status watchdog.

Consumes snapshots exported by another process. Never controls equipment, edits
recordings, serves telemetry, or claims that a WAV has been acoustically verified.
Python 3.10+ standard library only. No network or external dependencies.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import time

from status_contract import BadTelemetry, assess, validate

MAX_SNAPSHOT_BYTES = 16 * 1024
MAX_SILENCE_SECONDS = 20.0


def read_snapshot(path: str | Path) -> tuple[dict, str]:
    """Read bounded JSON without following symlinks where supported.

    File replacement should be atomic in a future producer. No provenance or
    authentication is established by these local filesystem checks.
    """
    path = os.fspath(path)
    if os.path.islink(path):
        raise ValueError('SYMLINK_NOT_ALLOWED')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0)
    flags |= getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise ValueError('SNAPSHOT_UNAVAILABLE') from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('SNAPSHOT_NOT_REGULAR_FILE')
        if info.st_size > MAX_SNAPSHOT_BYTES:
            raise ValueError('SNAPSHOT_TOO_LARGE')
        with os.fdopen(fd, 'rb') as f:
            fd = -1
            raw = f.read(MAX_SNAPSHOT_BYTES + 1)
        if len(raw) > MAX_SNAPSHOT_BYTES:
            raise ValueError('SNAPSHOT_TOO_LARGE')
    except OSError as exc:
        raise ValueError('SNAPSHOT_READ_ERROR') from exc
    finally:
        if fd >= 0:
            os.close(fd)
    try:
        data = json.loads(raw.decode('utf-8'))
        validate(data)
    except (UnicodeDecodeError, json.JSONDecodeError, BadTelemetry, ValueError) as exc:
        raise ValueError('SNAPSHOT_INVALID') from exc
    return data, hashlib.sha256(raw).hexdigest()


class IndependentWatchdog:
    """State lives in watchdog RAM, separate from the recorder process.

    Each new content digest must have a fresh sequence, timestamp and progress
    according to the existing v0.2 contract. Replaying an identical snapshot
    cannot extend liveness. Local monotonic time detects missing updates even
    when device timestamps or wall clocks are unreliable.
    """
    def __init__(self, *, silence_seconds: float = MAX_SILENCE_SECONDS):
        if not 0 < silence_seconds <= 3600:
            raise ValueError('invalid silence_seconds')
        self.silence_seconds = float(silence_seconds)
        self.previous = None
        self.last_digest = None
        self.last_change_monotonic = None
        self.last_monotonic = None

    @staticmethod
    def _result(status, alerts, *, assessment=None):
        return {
            'schema': 'veil.external-watchdog.v0.1',
            'simulation_only': True,
            'equipment_control_enabled': False,
            'status': status,
            'alerts': alerts,
            'assessment': assessment,
            'interpretation': 'Independent read-only simulated snapshot check; not a physical recording or phone-link test.',
        }

    def check(self, path: str | Path, *, now_monotonic: float | None = None,
              now_utc: str | None = None) -> dict:
        tick = time.monotonic() if now_monotonic is None else float(now_monotonic)
        if self.last_monotonic is not None and tick < self.last_monotonic:
            self.previous = self.last_digest = self.last_change_monotonic = None
            self.last_monotonic = tick
            return self._result('ALERT', ['WATCHDOG_CLOCK_REGRESSION'])
        self.last_monotonic = tick
        try:
            current, digest = read_snapshot(path)
        except ValueError as exc:
            self.previous = self.last_digest = self.last_change_monotonic = None
            return self._result('ALERT', [str(exc)])

        if digest == self.last_digest:
            gap = tick - self.last_change_monotonic
            if gap > self.silence_seconds:
                return self._result('ALERT', ['WATCHDOG_NO_NEW_SNAPSHOT'])
            # Still run timestamp freshness checks, even if bytes unchanged.
            check = assess(current, self.previous, now_utc=now_utc)
            critical = [a for a in check['alerts'] if a in (
                'HEARTBEAT_STALE', 'DEVICE_CLOCK_AHEAD_OR_UNTRUSTED',
                'WRITER_FAILURE', 'MIC_DISCONNECTED', 'REPORTED_ERRORS',
                'DEVICE_REPORTED_ERROR', 'EXTERNAL_POWER_LOSS_BATTERY_UNVERIFIED',
                'REMOTE_LINK_UNAVAILABLE_FULL_REMAINS_ACTIVE')]
            return self._result('ALERT' if critical else 'UNCONFIRMED',
                                critical or ['WAITING_FOR_NEW_SNAPSHOT'], assessment=check)

        # A changed file is not necessarily a new healthy sample.
        result = assess(current, self.previous, now_utc=now_utc)
        if self.previous is None and result['status'] == 'STATE_REPORTED':
            result = {**result, 'status': 'UNCONFIRMED',
                      'alerts': result['alerts'] + ['SECOND_SAMPLE_REQUIRED']}
        self.previous = current
        self.last_digest = digest
        self.last_change_monotonic = tick
        return self._result(result['status'], result['alerts'], assessment=result)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Offline, read-only simulated field watchdog')
    parser.add_argument('snapshot', help='Path to JSON snapshot produced elsewhere')
    parser.add_argument('--poll-seconds', type=float, default=5.0)
    parser.add_argument('--silence-seconds', type=float, default=20.0)
    parser.add_argument('--once', action='store_true', help='Read once (cannot establish progress)')
    args = parser.parse_args(argv)
    if args.poll_seconds <= 0 or args.poll_seconds > 3600:
        parser.error('--poll-seconds must be >0 and <=3600')
    wd = IndependentWatchdog(silence_seconds=args.silence_seconds)
    try:
        while True:
            print(json.dumps(wd.check(args.snapshot)), flush=True)
            if args.once:
                break
            time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
