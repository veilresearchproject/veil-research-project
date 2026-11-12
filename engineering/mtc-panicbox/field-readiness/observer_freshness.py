"""Fail-closed freshness check for externally collected MTC health observations.

No I/O, network, equipment control or evidence writes. `now` must be supplied by
an independent supervisor's monotonic clock in the same clock domain as sample.
"""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Sample:
    session_id: str
    sequence: int
    collected_at: float
    state: str

@dataclass(frozen=True)
class Result:
    state: str
    reasons: tuple[str, ...]

def _number(x):
    return type(x) in (int, float) and math.isfinite(x) and x >= 0

def _valid(s):
    return (isinstance(s, Sample) and isinstance(s.session_id, str)
            and bool(s.session_id.strip()) and type(s.sequence) is int
            and s.sequence >= 0 and _number(s.collected_at)
            and s.state in ('HOLD', 'UNCONFIRMED', 'PROGRESS_ONLY'))

def assess(previous, current, *, now, max_age=15.0):
    if not _number(now) or not _number(max_age) or max_age <= 0:
        return Result('UNCONFIRMED', ('invalid_supervisor_clock_or_limit',))
    if not _valid(current):
        return Result('UNCONFIRMED', ('invalid_observation',))
    faults = []
    if current.collected_at > now:
        faults.append('observation_from_future')
    elif now - current.collected_at > max_age:
        faults.append('observer_stale')
    if previous is not None:
        if not _valid(previous):
            return Result('UNCONFIRMED', ('invalid_previous_observation',))
        if previous.session_id != current.session_id:
            faults.append('session_changed')
        if current.sequence <= previous.sequence:
            faults.append('sequence_not_advancing')
        if current.collected_at <= previous.collected_at:
            faults.append('observer_clock_not_advancing')
    if current.state == 'HOLD':
        faults.append('upstream_hold')
    if faults:
        return Result('HOLD', tuple(faults))
    if previous is None:
        return Result('UNCONFIRMED', ('no_previous_observation',))
    if current.state != 'PROGRESS_ONLY':
        return Result('UNCONFIRMED', ('upstream_unconfirmed',))
    return Result('PROGRESS_ONLY', ('fresh_independent_progress_only',))
