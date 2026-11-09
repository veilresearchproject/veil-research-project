"""Read-only preflight for MTC snapshots; no recorder or evidence access."""
from collections.abc import Mapping
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Result:
    state: str
    reasons: tuple[str, ...]


def inspect(snapshot, *, now_monotonic, max_age=15):
    """Faults win over missing data; never infer verified audio."""
    if not isinstance(snapshot, Mapping):
        return Result('UNCONFIRMED', ('invalid_snapshot',))
    reasons = []
    for key, reason in (('mic_connected', 'microphone_fault'),
                        ('storage_ok', 'storage_fault'), ('power_ok', 'power_fault')):
        if key in snapshot and snapshot[key] is not True:
            reasons.append(reason)
    for key, reason in (('writer_errors', 'writer_error'),
                        ('dropped_callbacks', 'dropped_callbacks')):
        value = snapshot.get(key)
        if type(value) is int and value > 0:
            reasons.append(reason)
    if type(now_monotonic) not in (int, float) or not math.isfinite(now_monotonic) or type(max_age) not in (int,float) or not math.isfinite(max_age) or max_age <= 0:
        reasons.append('invalid_clock')
    else:
        hb = snapshot.get('heartbeat_monotonic')
        if type(hb) in (int,float) and math.isfinite(hb):
            if hb > now_monotonic: reasons.append('future_heartbeat')
            elif now_monotonic - hb > max_age: reasons.append('stale_heartbeat')
    if reasons:
        return Result('HOLD', tuple(reasons))
    required = ('session_id','heartbeat_monotonic','wav_bytes','wav_frames','callback_count',
                'writer_errors','dropped_callbacks','mic_connected','storage_ok','power_ok')
    if any(k not in snapshot for k in required):
        return Result('UNCONFIRMED', ('missing_fields',))
    if not isinstance(snapshot['session_id'], str) or not snapshot['session_id'].strip():
        return Result('UNCONFIRMED', ('invalid_session',))
    for key in ('wav_bytes','wav_frames','callback_count','writer_errors','dropped_callbacks'):
        if type(snapshot[key]) is not int or snapshot[key] < 0:
            return Result('UNCONFIRMED', ('invalid_counter_' + key,))
    if any(snapshot[k] is not True for k in ('mic_connected','storage_ok','power_ok')):
        return Result('UNCONFIRMED', ('invalid_flags',))
    hb = snapshot['heartbeat_monotonic']
    if type(hb) not in (int,float) or not math.isfinite(hb):
        return Result('UNCONFIRMED', ('invalid_heartbeat',))
    return Result('UNCONFIRMED', ('preflight_only_no_progress_history',))
