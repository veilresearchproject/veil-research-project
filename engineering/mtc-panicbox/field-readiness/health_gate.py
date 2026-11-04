"""Fail-closed read-only gate for MTC status snapshots; standard library only."""
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class Decision:
    state: str
    reasons: tuple[str, ...]


def evaluate(snapshot: Mapping, *, now_monotonic: float, previous: Mapping | None = None, max_age: float = 15.0) -> Decision:
    """Never return VERIFIED_AUDIO; progress is not proof of microphone capture.

    Timestamps are local monotonic seconds; never compare across computers.
    Missing/untrusted inputs fail closed. Previous must be from the same session.
    """
    if not isinstance(snapshot, Mapping) or not isinstance(now_monotonic, (int, float)):
        return Decision('UNCONFIRMED', ('invalid_input',))
    import math
    if not math.isfinite(now_monotonic) or not math.isfinite(max_age) or max_age <= 0:
        return Decision('UNCONFIRMED', ('invalid_clock',))
    required = ('session_id','heartbeat_monotonic','wav_bytes','wav_frames','callback_count','writer_errors','dropped_callbacks','mic_connected','storage_ok','power_ok')
    if any(k not in snapshot for k in required):
        return Decision('UNCONFIRMED', ('missing_fields',))
    if not isinstance(snapshot['session_id'], str) or not snapshot['session_id'].strip():
        return Decision('UNCONFIRMED', ('invalid_session',))
    nums = ('wav_bytes','wav_frames','callback_count','writer_errors','dropped_callbacks')
    if any(type(snapshot[k]) is not int or snapshot[k] < 0 for k in nums):
        return Decision('UNCONFIRMED', ('invalid_counters',))
    hb = snapshot['heartbeat_monotonic']
    if type(hb) not in (int,float) or not math.isfinite(hb) or hb > now_monotonic:
        return Decision('UNCONFIRMED', ('invalid_heartbeat',))
    faults = []
    if now_monotonic - hb > max_age: faults.append('stale_heartbeat')
    for flag,reason in [('mic_connected','microphone_fault'),('storage_ok','storage_fault'),('power_ok','power_fault')]:
        if snapshot[flag] is not True: faults.append(reason)
    if snapshot['writer_errors']: faults.append('writer_error')
    if snapshot['dropped_callbacks']: faults.append('dropped_callbacks')
    if previous is not None:
        if not isinstance(previous, Mapping) or previous.get('session_id') != snapshot['session_id']:
            faults.append('session_mismatch')
        elif any(k not in previous or type(previous[k]) is not int or previous[k] < 0 for k in nums):
            faults.append('invalid_previous')
        else:
            for k in nums:
                if snapshot[k] < previous[k]: faults.append('counter_regression_' + k)
            for k in ('wav_bytes','wav_frames','callback_count'):
                if snapshot[k] == previous[k]: faults.append('no_progress_' + k)
    else:
        return Decision('UNCONFIRMED', ('no_previous_snapshot',) + tuple(faults))
    return Decision('HOLD' if faults else 'PROGRESS_ONLY', tuple(faults))
