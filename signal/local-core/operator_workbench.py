"""Operator-invoked SIGNAL offline workbench for prototype integration.

Allows a safe dry run of all four workstreams in one invocation.
No microphone, network, model calls, evidence modification, or hardware controls.
"""
import argparse
import json
from pathlib import Path
from four_workstreams import (
    persona_prompt, speaking_pose, review_mtc_observations,
    parse_instrument_event, instrument_summary
)

MAX_INPUT = 65536

def prepare_workbench(subject, observations, telemetry, speaking_ms=None, reduced_motion=False):
    if not isinstance(observations, list) or not isinstance(telemetry, list) or len(telemetry) > 50:
        raise ValueError('Expected bounded notes and telemetry lists')
    if speaking_ms is not None and (type(speaking_ms) is not int or speaking_ms < 0):
        raise ValueError('Speaking duration must be a nonnegative integer')
    review = review_mtc_observations(observations)
    events = [instrument_summary(parse_instrument_event(event)) for event in telemetry]
    return {
        'schema': 'veil.signal.operator_workbench.v1',
        'model_inference_performed': False,
        'hardware_control_performed': False,
        'persona_instructions': persona_prompt(subject),
        'face_state': speaking_pose(speaking_ms or 0, speaking_ms is not None, reduced_motion),
        'mtc_review_queue': review,
        'instrument_read_only_summaries': events,
        'limitations': [
            'Prototype workbench: does not change the existing desktop browser UI.',
            'Operator notes, simulated face states, and telemetry are not proof of a cause.',
            'Future instruments require authenticated transport and separate human control.',
            'No automatic Panic Box ALL CLEAR is possible.'
        ]
    }

def main(argv=None):
    p = argparse.ArgumentParser(description='SIGNAL offline four-workstream dry run')
    p.add_argument('input', type=Path, help='Explicit local JSON fixture (not MTC source evidence)')
    p.add_argument('--subject', choices=('casual','research','safety'), default='research')
    p.add_argument('--speaking-ms', type=int)
    p.add_argument('--reduced-motion', action='store_true')
    args = p.parse_args(argv)
    if not args.input.is_file() or args.input.is_symlink():
        p.error('Expected a regular, non-symlink fixture file')
    if args.input.stat().st_size > MAX_INPUT:
        p.error('Fixture too large')
    with args.input.open('rb') as handle:
        raw = handle.read(MAX_INPUT + 1)
    if len(raw) > MAX_INPUT:
        p.error('Fixture too large')
    data = json.loads(raw)
    if not isinstance(data, dict) or set(data) != {'observations','telemetry'}:
        p.error('Fixture needs exactly observations and telemetry arrays')
    report = prepare_workbench(args.subject, data['observations'], data['telemetry'],
                               args.speaking_ms, args.reduced_motion)
    print(json.dumps(report, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
