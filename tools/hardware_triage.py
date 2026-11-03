#!/usr/bin/env python3
"""Offline first-pass VEIL computer suitability checker. Python 3.9+, stdlib only.

This is not a performance benchmark and does not establish field reliability.
"""
import argparse
import json
from pathlib import Path

# Conservative planning floors, NOT vendor-certified requirements.
TIERS = {
    'mini_mtc': {'ram_gb': 8, 'free_storage_gb': 64, 'logical_cores': 4},
    'signal_desktop_cpu': {'ram_gb': 16, 'free_storage_gb': 100, 'logical_cores': 8},
}

def evaluate(spec):
    results = {}
    for name, floors in TIERS.items():
        missing, below = [], []
        for field, floor in floors.items():
            value = spec.get(field)
            if value is None:
                missing.append(field)
            elif isinstance(value, bool) or not isinstance(value, (int,float)) or value < 0:
                raise ValueError(f'{field} must be a nonnegative number')
            elif value < floor:
                below.append({'field':field,'found':value,'planning_floor':floor})
        results[name] = {
            'status': 'insufficient' if below else (
                'needs_more_info' if missing else 'candidate_for_testing'),
            'below_floor': below, 'missing': missing
        }
    return results

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('spec_json', type=Path,
                    help='JSON with ram_gb, free_storage_gb, logical_cores')
    ap.add_argument('--json', action='store_true',
                    help='machine-readable output')
    args = ap.parse_args()
    try:
        data = json.loads(args.spec_json.read_text(encoding='utf-8'))
        if not isinstance(data,dict):
            raise ValueError('JSON root must be an object')
        results = evaluate(data)
    except (OSError, ValueError) as exc:
        ap.error(str(exc))
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for tier, outcome in results.items():
            print(f'{tier}: {outcome["status"]}')
            for item in outcome['below_floor']:
                print(f'  {item["field"]}: {item["found"]} < planning floor {item["planning_floor"]}')
            if outcome['missing']:
                print('  Need: ' + ', '.join(outcome['missing']))
        print('Planning filters only: test microphones, recording duration, '
              'thermals, storage, and local AI performance before use.')

if __name__ == '__main__':
    main()
