"""Offline, opt-in human acceptance checklist for SIGNAL desktop.

No model calls, microphone access, network, or automatic collection.
Only operator-entered PASS/FAIL/SKIP outcomes are stored, not transcripts.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CHECKS = (
    ('startup', 'START_HERE opens and shows the correct desktop version'),
    ('local_reply', 'A real installed Ollama model completes a text reply'),
    ('persona', 'Friendly reply sounds like SIGNAL without invented abilities'),
    ('evidence', 'MTC question distinguishes observations from evidence and causes'),
    ('interrupt', 'Stop reply leaves incomplete text labeled and retains question'),
    ('voice', 'Explicit voice test plays; Stop and Disable work'),
    ('microphone', 'Explicit microphone test only inserts editable words'),
    ('privacy', 'Voice and microphone start disabled; no automatic network upload'),
)
VALID = {'PASS', 'FAIL', 'SKIP'}

def build_report(outcomes, version='v0.20'):
    if set(outcomes) != {key for key, _ in CHECKS}:
        raise ValueError('All checklist IDs must be present once')
    if any(value not in VALID for value in outcomes.values()):
        raise ValueError('Outcomes must be PASS, FAIL or SKIP')
    return {
        'schema': 'veil.signal.desktop_acceptance.v1',
        'signal_version': version,
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'mode': 'human_observed_not_automated',
        'checks': [{'id': key, 'description': label, 'result': outcomes[key]}
                   for key, label in CHECKS],
        'summary': {status.lower(): sum(v == status for v in outcomes.values())
                    for status in ('PASS', 'FAIL', 'SKIP')},
        'limitations': 'Operator answers are not independent hardware or scientific verification.'
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline SIGNAL desktop human acceptance checklist')
    parser.add_argument('--output', type=Path, required=True, help='Write results to new JSON file')
    parser.add_argument('--version', default='v0.20')
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error('Output already exists; choose a new filename (never overwrite evidence).')
    outcomes = {}
    for key, label in CHECKS:
        print(f'\n{label}')
        while True:
            response = input('PASS / FAIL / SKIP: ').strip().upper()
            if response in VALID:
                outcomes[key] = response
                break
            print('Please enter PASS, FAIL, or SKIP.')
    report = build_report(outcomes, args.version)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    print(f"Saved local checklist to {args.output}. No transcript or microphone audio was collected.")

if __name__ == '__main__':
    main()
