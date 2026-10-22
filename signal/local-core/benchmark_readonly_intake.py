"""Offline, deterministic benchmark of synthetic thermal/MTC metadata intake.

Run: python benchmark_readonly_intake.py --cases 240 --json
No model inference, sensors, instrument commands, network or external packages.
Timing measures this Python parser on the current machine, NOT Ollama.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import random
import statistics
import sys
import time
import tracemalloc
import synthetic_evidence as intake

CATEGORIES = ('normal', 'temperature_step', 'cadence_gap', 'timestamp_order',
              'mtc_markers', 'hash_mismatch', 'unknown_marker', 'unsupported_schema')


def thermal_case(category, baseline):
    start = datetime(2026, 10, 22, 8, 0, tzinfo=timezone.utc)
    rows = ['timestamp,sensor_id,temperature_c']
    for i in range(32):
        for stream in ('Sensor-A', 'Sensor-B'):
            when = start + timedelta(minutes=i)
            if category == 'cadence_gap' and stream == 'Sensor-B' and i >= 18:
                when += timedelta(minutes=3)
            if category == 'timestamp_order' and stream == 'Sensor-A' and i == 31:
                when -= timedelta(minutes=1)
            value = baseline + (0.5 if stream == 'Sensor-B' else 0)
            if category == 'temperature_step' and stream == 'Sensor-A' and i >= 12:
                value += 2.0
            rows.append(f'{when:%Y-%m-%dT%H:%M:%SZ},{stream},{value:.3f}')
    return ('\n'.join(rows) + '\n').encode('ascii')


def mtc_case():
    return ('timestamp,recorder_id,marker\n'
            '2026-10-22T08:00:00Z,Recorder-A,RECORDING_START\n'
            '2026-10-22T08:01:00Z,Recorder-A,QUESTION_START\n'
            '2026-10-22T08:01:04Z,Recorder-A,QUESTION_END\n'
            '2026-10-22T08:03:00Z,Recorder-A,RECORDING_END\n').encode('ascii')


def evaluate(category, baseline):
    if category in ('mtc_markers', 'unknown_marker'):
        raw = mtc_case()
        if category == 'unknown_marker':
            raw = raw.replace(b'QUESTION_START', b'UNRECOGNIZED_MARKER')
    else:
        raw = thermal_case(category, baseline)
    if category in ('hash_mismatch', 'unknown_marker', 'unsupported_schema'):
        try:
            intake.inspect_synthetic(
                raw, 'unsupported' if category == 'unsupported_schema' else
                ('mtc_markers' if category == 'unknown_marker' else 'thermal'),
                expected_sha256='0' * 64 if category == 'hash_mismatch' else None)
        except ValueError as exc:
            return {'expected_rejection': category, 'exception': type(exc).__name__}
        raise AssertionError('Invalid mock input accepted: ' + category)
    result = intake.inspect_synthetic(
        raw, 'mtc_markers' if category == 'mtc_markers' else 'thermal',
        expected_sha256=hashlib.sha256(raw).hexdigest())
    if result['sha256'] != hashlib.sha256(raw).hexdigest():
        raise AssertionError('Incorrect source hash')
    if result['live_instrument_connection'] or result['model_inference'] or result['scientific_cause_determined']:
        raise AssertionError('False claim of hardware, model or causal interpretation')
    if result['source_type'] != 'SYNTHETIC_ONLY':
        raise AssertionError('Synthetic provenance label missing')
    if category == 'mtc_markers':
        if result['rows'] != 4 or result['marker_counts']['QUESTION_START'] != 1:
            raise AssertionError('MTC metadata mismatch')
    else:
        expected = {'normal': (0, 0, 0), 'temperature_step': (1, 0, 0),
                    'cadence_gap': (0, 1, 0), 'timestamp_order': (0, 0, 1)}[category]
        observed = (result['temperature_step_flags'], result['cadence_gaps'],
                    result['timestamp_order_issues'])
        if result['rows'] != 64 or observed != expected:
            raise AssertionError(f'{category}: expected {expected}, got {observed}')
    return result


def run(cases=240, seed=20261022):
    if not 1 <= cases <= 2000:
        raise ValueError('cases must be between 1 and 2000')
    rng = random.Random(seed)
    times = []
    failures = []
    passed = 0
    digest = hashlib.sha256()
    tracemalloc.start()
    started = time.perf_counter()
    for index in range(cases):
        category = CATEGORIES[index % len(CATEGORIES)]
        baseline = round(rng.uniform(17.0, 25.0), 3)
        one = time.perf_counter()
        try:
            output = evaluate(category, baseline)
            digest.update(json.dumps(output, sort_keys=True, separators=(',', ':')).encode())
            passed += 1
        except Exception as exc:
            failures.append({'case': index, 'category': category, 'error': str(exc)[:200]})
        times.append((time.perf_counter() - one) * 1000)
    elapsed = (time.perf_counter() - started) * 1000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    sorted_times = sorted(times)
    return {'harness': 'SIGNAL deterministic synthetic evidence evaluation v0.1',
            'cases': cases, 'seed': seed, 'passed': passed, 'failed': len(failures),
            'categories': list(CATEGORIES), 'failures': failures[:10],
            'output_sha256': digest.hexdigest(),
            'elapsed_ms': round(elapsed, 2),
            'median_case_ms': round(statistics.median(times), 4),
            'p95_case_ms': round(sorted_times[min(len(times)-1, int(0.95*len(times)))], 4),
            'peak_traced_kib': round(peak/1024, 1),
            'python': sys.version.split()[0],
            'hardware_tested': False, 'ollama_tested': False,
            'note': 'Parser timing on synthetic data only; not model inference or physical sensors.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=int, default=240)
    parser.add_argument('--seed', type=int, default=20261022)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        outcome = run(args.cases, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(outcome, indent=2, sort_keys=True))
    else:
        print(f"SIGNAL synthetic evaluation: {outcome['passed']}/{outcome['cases']} passed; "
              f"failed={outcome['failed']}; elapsed={outcome['elapsed_ms']} ms; "
              f"p95={outcome['p95_case_ms']} ms; peak={outcome['peak_traced_kib']} KiB")
        print('Output fingerprint:', outcome['output_sha256'])
        print(outcome['note'])
        for failure in outcome['failures']:
            print('FAIL:', failure)
    return 0 if not outcome['failed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
