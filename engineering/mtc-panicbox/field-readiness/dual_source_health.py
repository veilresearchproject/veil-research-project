"""Read-only, *synthetic-only* fusion of MTC status and active PCM WAV growth.

An exported recorder heartbeat alone cannot establish that audio frames reached disk.
This module checks two independently observed signals and fails closed on faults.
No network, recording, evidence edits, alerts transport, or equipment control.

The field-status contract currently *requires* simulation_only=True. This code is
NOT a live field monitor or an authenticated mobile telemetry system.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from external_watchdog import IndependentWatchdog
from wav_growth_probe import WaveGrowthProbe

SCHEMA = 'veil.mtc-dual-source-health.v0.1'


class DualSourceHealth:
    """Combine independent metadata/WAV observers without certifying capture.

    A serious fault is latched for operator review for the life of this instance.
    Recreating the instance clears RAM-only state, NOT an equipment safety latch.
    The caller must manage session boundaries and explicit human review.
    """

    def __init__(self, *, silence_seconds: float = 20.0,
                 stalled_after_seconds: float = 20.0):
        self.watchdog = IndependentWatchdog(silence_seconds=silence_seconds)
        self.wav_probe = WaveGrowthProbe(stalled_after_seconds=stalled_after_seconds)
        self.latched_alerts: list[str] = []
        self.expected_session_id: str | None = None
        self.expected_wav_path: str | None = None

    def check(self, status_path: str | Path, wav_path: str | Path,
              *, now_monotonic: float | None = None,
              now_utc: str | None = None) -> dict:
        # Explicit file-path change is a segment boundary; never silently
        # interpret a new WAV as continuous recording or reset a fault.
        wav_id = str(Path(wav_path).absolute())
        if self.expected_wav_path is None:
            self.expected_wav_path = wav_id
        elif wav_id != self.expected_wav_path:
            self._latch('WAV_PATH_CHANGED_NEW_SEGMENT_REVIEW_REQUIRED')

        metadata = self.watchdog.check(status_path, now_monotonic=now_monotonic,
                                       now_utc=now_utc)
        wav = self.wav_probe.check(wav_path, now_monotonic=now_monotonic)
        assessment = metadata.get('assessment') or {}
        session_id = assessment.get('session_id')
        phase = assessment.get('phase')
        if session_id:
            if self.expected_session_id is None:
                self.expected_session_id = session_id
            elif session_id != self.expected_session_id:
                self._latch('SESSION_ID_CHANGED_REVIEW_REQUIRED')
        if metadata['status'] == 'ALERT':
            self._latch('STATUS_' + ','.join(metadata['alerts']))
        if wav['status'] == 'ALERT':
            self._latch('WAV_' + ','.join(wav['alerts']))
        if phase and phase != 'RECORDING':
            # A completed/idle session may have a valid WAV, but is not
            # actively recording and cannot be called live-progressing.
            note = 'NOT_IN_RECORDING_PHASE'
        else:
            note = None

        if self.latched_alerts:
            state = 'ALERT_REVIEW_REQUIRED'
        elif (metadata['status'] == 'PROGRESS_OBSERVED'
              and wav['status'] == 'GROWTH_OBSERVED_NOT_AUDIO_VERIFIED'
              and phase == 'RECORDING'):
            state = 'CORRELATED_PROGRESS_NOT_AUDIO_VERIFIED'
        else:
            state = 'UNCONFIRMED'
        warnings = []
        if note:
            warnings.append(note)
        if (metadata['status'] == 'PROGRESS_OBSERVED'
                and wav['status'] != 'GROWTH_OBSERVED_NOT_AUDIO_VERIFIED'):
            warnings.append('TELEMETRY_PROGRESS_WITHOUT_MATCHING_WAV_GROWTH')
        if (wav['status'] == 'GROWTH_OBSERVED_NOT_AUDIO_VERIFIED'
                and metadata['status'] != 'PROGRESS_OBSERVED'):
            warnings.append('WAV_GROWTH_WITHOUT_MATCHING_TELEMETRY_PROGRESS')
        return {
            'schema': SCHEMA,
            'simulation_only': True,
            'authenticated_live_telemetry': False,
            'equipment_control_enabled': False,
            'audio_capture_verified': False,
            'status': state,
            'latched_alerts': self.latched_alerts.copy(),
            'warnings': warnings,
            'metadata_status': metadata['status'],
            'metadata_alerts': metadata['alerts'],
            'wav_status': wav['status'],
            'wav_alerts': wav['alerts'],
            'observed_file_bytes': wav['observed_file_bytes'],
            'estimated_complete_frames': wav['estimated_complete_frames'],
            'interpretation': 'Synthetic-only cross-check of status and WAV growth; no microphone, audio-content, provenance, or field validation.',
        }

    def _latch(self, reason: str) -> None:
        if reason not in self.latched_alerts:
            self.latched_alerts.append(reason)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Offline synthetic-only read-only MTC dual-source check')
    parser.add_argument('status_json', help='Local simulated status snapshot')
    parser.add_argument('active_wav', help='Local active PCM WAV; never modified')
    parser.add_argument('--once', action='store_true', help='One check never establishes progress')
    parser.add_argument('--poll-seconds', type=float, default=5)
    args = parser.parse_args(argv)
    if not 0 < args.poll_seconds <= 3600:
        parser.error('--poll-seconds must be >0 and <=3600')
    import time
    monitor = DualSourceHealth()
    try:
        while True:
            result = monitor.check(args.status_json, args.active_wav)
            print(json.dumps(result), flush=True)
            if args.once:
                return 0 if result['status'] == 'UNCONFIRMED' else 2
            time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
