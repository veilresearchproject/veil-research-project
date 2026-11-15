"""Offline review of v0.3's explicitly synthetic output; no hardware or model calls."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import secrets

from evidence_v04 import (validate_protocol, validate_source_registry, normalize_timeline,
    screen_candidates, group_candidate_windows, compare_test_control,
    prepare_blind_queue, resolve_reviews, render_lab_readout)

CHANNELS = ('temperature_c', 'humidity_pct', 'sound_db')
BOUNDS = {'temperature_c': (18, 26), 'humidity_pct': (25, 65), 'sound_db': (0, 65)}
FIELDNAMES = ('sample', 'timestamp_utc', *CHANNELS)


def run(input_dir, output_dir):
    source = Path(input_dir)
    target = Path(output_dir)
    if target.exists() and any(target.iterdir()):
        raise FileExistsError('Output folder is not empty; choose a new folder to avoid overwriting artifacts')
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf8'))
    if manifest.get('dataset_type') != 'SYNTHETIC_SIMULATION' or manifest.get('real_sensor_data') is not False:
        raise ValueError('Refusing input not explicitly marked as synthetic simulation')
    raw = (source / 'synthetic_readings.csv').read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != manifest.get('source_sha256'):
        raise ValueError('Source file differs from source manifest')
    if len(raw) > 20_000_000:
        raise ValueError('Synthetic source exceeds 20 MB cap')

    # V0.3 must have verified every original output before v0.4 will review it.
    from advanced_lab import verify_full_bundle
    if not verify_full_bundle(source):
        raise ValueError('Prior simulation bundle failed integrity check')

    with (source / 'synthetic_readings.csv').open(newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != FIELDNAMES:
            raise ValueError('Unexpected CSV header')
        rows = []
        for row in reader:
            if len(rows) >= 100000 or None in row or any(v is None for v in row.values()):
                raise ValueError('Invalid CSV row or excessive count')
            if int(row['sample']) != len(rows):
                raise ValueError('Noncontiguous sample index')
            values = {key: float(row[key]) for key in CHANNELS}
            if not all(math.isfinite(value) for value in values.values()):
                raise ValueError('Nonfinite sensor value')
            rows.append((row['timestamp_utc'], values))
    if len(rows) < 10 or manifest.get('samples') != len(rows):
        raise ValueError('Invalid simulation sample count')

    plan = validate_protocol(dict(protocol_id='SIMULATED_MTC_CONTROL_v04', mode='SYNTHETIC_SIMULATION',
        hypothesis='Test-window rates might differ from control-window rates',
        null_hypothesis='Test and control window rates do not differ',
        primary_outcome='Numerical threshold flags per hour',
        control_description='First half of synthetic samples used as an illustrative control window',
        analysis_plan='Predeclare numerical bounds; compare per-hour counts, no significance claims',
        blinding_plan='Hide condition and source identity in separate synthetic reviewer packet',
        consent_plan='No humans, live recordings or physical locations included'))
    devices = validate_source_registry([dict(device_id='SIMULATOR_01', modality='multichannel_csv',
        clock_offset_ms=0, clock_uncertainty_ms=0)])
    half = len(rows) // 2
    raw_events = [dict(event_id=f's{index:06d}-{channel}', device_id='SIMULATOR_01',
                       channel=channel, timestamp_utc=when, observed_value=values[channel],
                       condition='control' if index < half else 'test')
                  for index, (when, values) in enumerate(rows) for channel in CHANNELS]
    events = normalize_timeline(raw_events, devices)
    candidates = screen_candidates(events, BOUNDS)
    groups = group_candidate_windows(candidates)
    comparisons = compare_test_control(candidates, dict(control=half * 10,
                                                       test=(len(rows) - half) * 10))
    blind = prepare_blind_queue(candidates, secret=secrets.token_hex(32))
    decisions = resolve_reviews([item['review_id'] for item in blind['reviewer_packet']], [])
    html = render_lab_readout(plan, devices, candidates, groups, comparisons, decisions,
                              csv_sha256=digest)
    # Everything written below is newly derived synthetic data; original source is untouched.
    target.mkdir(parents=True, exist_ok=True)
    def save_json(filename, payload):
        (target / filename).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf8')
    save_json('v04_summary.json', dict(mode='SYNTHETIC_ONLY', protocol=plan,
        devices=list(devices.values()), flagged=len(candidates), timing_windows=groups,
        comparison=comparisons, source_sha256=digest,
        warning='Not independent verification or evidence of unexplained phenomena'))
    save_json('reviewer_packet_SYNTHETIC.json', blind['reviewer_packet'])
    save_json('custodian_key_PRIVATE_SYNTHETIC.json', blind['custodian_key'])
    save_json('review_status.json', decisions)
    (target / 'v04_readout.html').write_text(html, encoding='utf8')
    return dict(output=str(target), source_sha256=digest, flagged=len(candidates),
                timing_windows=len(groups), review_items=len(decisions), simulated_only=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Read-only v0.4 synthetic lab review')
    p.add_argument('--input', type=Path, required=True, help='Existing v0.3 synthetic output folder')
    p.add_argument('--output', type=Path, default=Path('signal_v04_output'))
    p.add_argument('--approve-simulation', action='store_true')
    args = p.parse_args()
    if not args.approve_simulation:
        p.error('Explicit --approve-simulation is required; no real sources supported')
    print(json.dumps(run(args.input, args.output), indent=2))