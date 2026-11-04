"""Conservative read-only fusion of a snapshot gate and independent WAV/status checks.

No file writes, hardware control, or live-status claims. All inputs are untrusted
and this module cannot establish that microphone audio was actually captured.
"""
from collections.abc import Mapping
from health_gate import Decision

SCHEMA = 'veil.mtc-health-fusion.v0.1'


def fuse(gate: Decision, dual: Mapping) -> dict:
    """Require two independent progress indicators; never downgrade faults."""
    if not isinstance(gate, Decision) or not isinstance(dual, Mapping):
        return _result('UNCONFIRMED', ['INVALID_INPUT'])
    if gate.state not in ('HOLD', 'UNCONFIRMED', 'PROGRESS_ONLY'):
        return _result('UNCONFIRMED', ['UNKNOWN_GATE_STATE'])
    status = dual.get('status')
    if status not in ('ALERT_REVIEW_REQUIRED', 'UNCONFIRMED',
                      'CORRELATED_PROGRESS_NOT_AUDIO_VERIFIED'):
        return _result('UNCONFIRMED', ['UNKNOWN_DUAL_STATE'])
    if (dual.get('schema') != 'veil.mtc-dual-source-health.v0.1'
            or dual.get('simulation_only') is not True
            or dual.get('authenticated_live_telemetry') is not False
            or dual.get('equipment_control_enabled') is not False
            or dual.get('audio_capture_verified') is not False):
        return _result('UNCONFIRMED', ['INVALID_DUAL_CONTRACT'])
    reasons = list(gate.reasons)
    if gate.state == 'HOLD' or status == 'ALERT_REVIEW_REQUIRED':
        reasons.append('FAULT_REVIEW_REQUIRED')
        return _result('HOLD', reasons)
    if gate.state == 'PROGRESS_ONLY' and status == 'CORRELATED_PROGRESS_NOT_AUDIO_VERIFIED':
        return _result('PROGRESS_ONLY', reasons)
    reasons.append('INSUFFICIENT_CORROBORATION')
    return _result('UNCONFIRMED', reasons)


def _result(state: str, reasons: list[str]) -> dict:
    return {'schema': SCHEMA, 'simulation_only': True,
            'authenticated_live_telemetry': False,
            'audio_capture_verified': False, 'equipment_control_enabled': False,
            'state': state, 'reasons': list(dict.fromkeys(reasons))}
