"""SIGNAL four-workstream offline prototype helpers.

Pure functions only: no recording access, no model calls, no hardware commands.
Designed for explicit operator-controlled integration into the local desktop.
"""
from dataclasses import dataclass
from math import isfinite
import json
import re

PERSONA_RULES = (
    "You are SIGNAL, VEIL's curious, warm, slightly eccentric research assistant. "
    "Answer the question before making a quick joke. Use humor only for casual subjects, "
    "never for safety, distress, or research evidence. Never pretend to see, hear, "
    "remember unsupplied events, have consciousness, or control instruments. "
    "Distinguish recorded observations, operator descriptions, and hypotheses. "
    "State what could falsify an interpretation; consider mundane causes. "
    "Only an authorized human may issue a Panic Box ALL CLEAR."
)

def persona_prompt(subject='casual'):
    if subject not in ('casual', 'research', 'safety'):
        raise ValueError('Unknown subject')
    suffix = {
        'casual': 'Light theatrical wit is welcome; keep it short.',
        'research': 'Use neutral, evidence-first wording; do not infer paranormal causes.',
        'safety': 'Be calm, direct, and serious. Do not joke or issue any ALL CLEAR.',
    }[subject]
    return PERSONA_RULES + ' ' + suffix

def speaking_pose(elapsed_ms, speaking, reduced_motion=False):
    """Deterministic speaking face state; does not claim lip/phoneme alignment."""
    if not speaking or reduced_motion:
        return 'neutral'
    if not isinstance(elapsed_ms, (int, float)) or not isfinite(elapsed_ms) or elapsed_ms < 0:
        raise ValueError('Invalid elapsed time')
    return ('mouth-small', 'mouth-wide', 'mouth-small', 'neutral')[int(elapsed_ms // 140) % 4]

def review_mtc_observations(observations, limit=100):
    """Treat operator entries as unverified claims; produce a bounded review queue."""
    if not isinstance(observations, list) or len(observations) > limit:
        raise ValueError('Invalid observation count')
    result = []
    for item in observations:
        if not isinstance(item, dict):
            raise ValueError('Expected observation object')
        t, detail = item.get('timestamp_s'), item.get('description')
        if isinstance(t, bool) or not isinstance(t, (int, float)) or not isfinite(t) or t < 0:
            raise ValueError('Invalid timestamp')
        if not isinstance(detail, str) or not 0 < len(detail.strip()) <= 500:
            raise ValueError('Invalid operator description')
        result.append({
            'timestamp_s': round(t, 3), 'operator_description': detail.strip(),
            'status': 'needs_human_review', 'source': 'unverified_operator_note',
            'review_questions': [
                'Is the event audible or visible in the original synchronized recording?',
                'Can equipment, people, environment or timing explain it?',
                'Is there independent instrument or camera corroboration?'
            ]
        })
    return sorted(result, key=lambda x: x['timestamp_s'])

INSTRUMENT_TYPES = frozenset({'panic_box', 'mtc', 'temperature_curtain', 'light_cage', 'spatial_sensor'})
SENSOR_KEYS = frozenset({'temperature_c', 'sound_level_db', 'emf_ut', 'motion_detected', 'status'})

@dataclass(frozen=True)
class InstrumentEvent:
    instrument_type: str
    device_id: str
    timestamp_utc: str
    measurements: dict

def parse_instrument_event(payload):
    """Validate future read-only instrument telemetry; return data, not commands."""
    if isinstance(payload, (bytes, str)):
        if len(payload) > 8192:
            raise ValueError('Oversized input')
        payload = json.loads(payload)
    if not isinstance(payload, dict) or set(payload) != {'instrument_type', 'device_id', 'timestamp_utc', 'measurements'}:
        raise ValueError('Invalid event shape')
    typ, device, stamp, values = [payload[k] for k in ('instrument_type','device_id','timestamp_utc','measurements')]
    if typ not in INSTRUMENT_TYPES:
        raise ValueError('Unknown instrument')
    if not isinstance(device, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', device):
        raise ValueError('Invalid device ID')
    if not isinstance(stamp, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', stamp):
        raise ValueError('Expected UTC timestamp')
    if not isinstance(values, dict) or not values or not set(values) <= SENSOR_KEYS:
        raise ValueError('Unexpected sensor keys')
    for key, value in values.items():
        if key == 'motion_detected' and type(value) is not bool:
            raise ValueError('Expected boolean motion')
        elif key == 'status' and (not isinstance(value, str) or value not in ('ready', 'active', 'offline', 'fault')):
            raise ValueError('Invalid status')
        elif key not in ('motion_detected', 'status') and (
            isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)):
            raise ValueError('Invalid numeric measurement')
    return InstrumentEvent(typ, device, stamp, dict(values))

def instrument_summary(event):
    if not isinstance(event, InstrumentEvent):
        raise TypeError('Validated event required')
    return {'device': event.device_id, 'kind': event.instrument_type,
            'received': 'unverified_telemetry', 'operator_action': 'none',
            'limitations': 'No sensor authentication, calibration or independent corroboration.'}
