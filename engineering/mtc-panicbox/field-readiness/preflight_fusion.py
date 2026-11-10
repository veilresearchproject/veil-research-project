"""Conservative adapter: preflight faults override legacy gate and dual monitor.
Pure Python, no I/O. All snapshots are synthetic contracts, not live telemetry.
"""
from collections.abc import Mapping
from health_snapshot_guard import inspect
from health_gate import evaluate, Decision
from health_gate_fusion import fuse, _result


def evaluate_fused(snapshot, dual, *, now_monotonic, previous=None, max_age=15):
    preflight = inspect(snapshot, now_monotonic=now_monotonic, max_age=max_age)
    # Preserve faults even if the legacy gate rejects an incomplete snapshot.
    if preflight.state == 'HOLD':
        return _result('HOLD', list(preflight.reasons) + ['PREFLIGHT_FAULT'])
    if preflight.state != 'UNCONFIRMED' or preflight.reasons != ('preflight_only_no_progress_history',):
        return _result('UNCONFIRMED', list(preflight.reasons))
    gate = evaluate(snapshot, now_monotonic=now_monotonic, previous=previous, max_age=max_age)
    return fuse(gate, dual)
