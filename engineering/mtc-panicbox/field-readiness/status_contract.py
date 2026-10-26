"""VEIL research status contract v0.2 — offline, pure synthetic evaluation.

No capture, networking, equipment control, authentication or notification transport.
This deliberately refuses to infer recording success from a timer or heartbeat alone.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json

SCHEMA = 'veil.field-status.v0.2'
MAX_AGE_S = 20.0

class BadTelemetry(ValueError):
    pass


def _utc(stamp):
    if not isinstance(stamp, str):
        raise BadTelemetry('timestamp must be a string')
    try:
        parsed = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    except ValueError as exc:
        raise BadTelemetry('invalid ISO timestamp') from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise BadTelemetry('timestamp must contain timezone')
    return parsed.astimezone(timezone.utc)


def _str(v, name, options):
    if not isinstance(v, str) or v not in options:
        raise BadTelemetry(f'invalid {name}')
    return v


def _int(v, name):
    if type(v) is not int or v < 0:
        raise BadTelemetry(f'{name} must be a nonnegative integer')
    return v


def validate(snapshot):
    if not isinstance(snapshot, dict):
        raise BadTelemetry('expected JSON object')
    if snapshot.get('schema') != SCHEMA:
        raise BadTelemetry('wrong schema')
    dev = _str(snapshot.get('device'), 'device', {'MTC', 'PANIC_BOX'})
    phase = _str(snapshot.get('phase'), 'phase', {'IDLE', 'RECORDING', 'COMPLETE', 'ERROR', 'BASELINE', 'FULL'})
    if dev == 'MTC' and phase not in {'IDLE','RECORDING','COMPLETE','ERROR'}:
        raise BadTelemetry('MTC cannot use Panic Box phase')
    if dev == 'PANIC_BOX' and phase not in {'BASELINE','FULL','ERROR'}:
        raise BadTelemetry('Panic Box cannot use MTC phase')
    _utc(snapshot.get('observed_at_utc'))
    sid = snapshot.get('session_id')
    if not isinstance(sid, str) or not sid or len(sid) > 90:
        raise BadTelemetry('invalid session_id')
    if type(snapshot.get('simulation_only')) is not bool or not snapshot['simulation_only']:
        raise BadTelemetry('prototype only permits explicitly simulated snapshots')
    _int(snapshot.get('sequence'), 'sequence')
    for name in ('bytes_written', 'mic_callback_count', 'recorded_seconds'):
        _int(snapshot.get(name), name)
    for name in ('microphone_connected', 'writer_ok', 'external_power', 'network_connected'):
        if type(snapshot.get(name)) is not bool:
            raise BadTelemetry(f'{name} must be boolean')
    errors = snapshot.get('errors')
    if not isinstance(errors, list) or len(errors) > 20 or any(not isinstance(e,str) or len(e)>250 for e in errors):
        raise BadTelemetry('errors must be short string list')
    return snapshot


def assess(current, previous=None, *, now_utc=None):
    """Status evaluation is fail-closed. Healthy needs two successive, progressing samples.

    Observation timestamps are NOT proof of clock sync or provenance. This is for
    synthetic/testing use until an authenticated, independent status transport exists.
    """
    cur = validate(current)
    prev = validate(previous) if previous is not None else None
    now = _utc(now_utc) if now_utc is not None else datetime.now(timezone.utc)
    age = (now-_utc(cur['observed_at_utc'])).total_seconds()
    reasons = []
    if age < -5:
        reasons.append('DEVICE_CLOCK_AHEAD_OR_UNTRUSTED')
    if age > MAX_AGE_S:
        reasons.append('HEARTBEAT_STALE')
    if cur['errors']:
        reasons.append('REPORTED_ERRORS')
    if not cur['writer_ok']:
        reasons.append('WRITER_FAILURE')
    if cur['device']=='MTC' and cur['phase']=='RECORDING':
        if not cur['microphone_connected']:
            reasons.append('MIC_DISCONNECTED')
        if prev is None:
            reasons.append('SECOND_SAMPLE_REQUIRED')
        elif prev['session_id'] != cur['session_id'] or prev['device'] != cur['device']:
            reasons.append('SECOND_SAMPLE_REQUIRED')
        elif cur['sequence'] <= prev['sequence']:
            reasons.append('SEQUENCE_NOT_ADVANCING')
        elif cur['bytes_written'] <= prev['bytes_written']:
            reasons.append('RECORDING_BYTES_NOT_ADVANCING')
        elif cur['mic_callback_count'] <= prev['mic_callback_count']:
            reasons.append('MIC_CALLBACKS_NOT_ADVANCING')
        elif (_utc(cur['observed_at_utc'])-_utc(prev['observed_at_utc'])).total_seconds() <= 0:
            reasons.append('TIMESTAMP_NOT_ADVANCING')
    if cur['device'] == 'PANIC_BOX' and cur['phase']=='FULL' and not cur['network_connected']:
        reasons.append('REMOTE_LINK_UNAVAILABLE_FULL_REMAINS_ACTIVE')
    if not cur['external_power']:
        reasons.append('EXTERNAL_POWER_LOSS_BATTERY_UNVERIFIED')
    if cur['phase']=='ERROR' and 'DEVICE_REPORTED_ERROR' not in reasons:
        reasons.append('DEVICE_REPORTED_ERROR')
    if reasons:
        state = 'ALERT' if any(x in reasons for x in ('REPORTED_ERRORS','WRITER_FAILURE','MIC_DISCONNECTED','HEARTBEAT_STALE','RECORDING_BYTES_NOT_ADVANCING','MIC_CALLBACKS_NOT_ADVANCING','SEQUENCE_NOT_ADVANCING','DEVICE_REPORTED_ERROR')) else 'UNCONFIRMED'
    else:
        state = 'PROGRESS_OBSERVED' if cur['phase']=='RECORDING' else 'STATE_REPORTED'
    return {
        'schema': 'veil.field-assessment.v0.2', 'simulation_only': True,
        'equipment_control_enabled': False,
        'status': state,
        'phase': cur['phase'],
        'session_id': cur['session_id'],
        'age_seconds': round(age,2), 'alerts': reasons,
        'interpretation': 'Simulated metadata checks only; does not prove physical recording, microphone acoustics, network reliability, or safety.',
    }
