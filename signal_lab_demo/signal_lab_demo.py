"""SIGNAL v0.1 synthetic sensor demonstrator. Python standard library only."""
import csv, hashlib, json, random, argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

LIMITS = {'temperature_c': (18,26), 'humidity_pct': (25,65), 'sound_db': (0,65)}
def run(folder=Path('signal_demo_output'), count=60, seed=42):
    if not 1 <= count <= 100000: raise ValueError('Invalid count')
    folder=Path(folder); folder.mkdir(parents=True, exist_ok=True)
    rng=random.Random(seed)
    start=datetime(2026,1,1,tzinfo=timezone.utc)
    rows=[]
    for i in range(count):
        rows.append(dict(sample=i, timestamp_utc=(start+timedelta(seconds=10*i)).isoformat(),
            temperature_c=round(21+rng.uniform(-.6,.6)+(8 if i==count//2 else 0),2),
            humidity_pct=round(45+rng.uniform(-2,2),2),
            sound_db=round(35+rng.uniform(-4,4)+(40 if i==count//3 else 0),2)))
    csvpath=folder/'synthetic_readings.csv'
    with csvpath.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=['sample','timestamp_utc',*LIMITS]); w.writeheader(); w.writerows(rows)
    digest=hashlib.sha256(csvpath.read_bytes()).hexdigest()
    flags=[dict(sample=r['sample'], timestamp_utc=r['timestamp_utc'], channel=k,
           measured_value=r[k], expected_range=list(lim), interpretation='Outside demonstration threshold; cause unknown')
           for r in rows for k,lim in LIMITS.items() if not lim[0] <= r[k] <= lim[1]]
    manifest=dict(schema_version='0.1',dataset_type='SYNTHETIC_SIMULATION',real_sensor_data=False,
        timestamp_notice='Synthetic timeline, not collection timestamps',seed=seed,samples=count,
        source_file=csvpath.name,source_sha256=digest,thresholds=LIMITS,flags=flags,
        human_review_required=True,provenance_notice='Threshold flags are not claims of paranormal events')
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    lines=['# SIGNAL synthetic laboratory report','','**SIMULATED DATA ONLY — no real instruments connected.**','',
           f'Samples: {count}; flagged: {len(flags)}; seed: {seed}.',f'CSV SHA-256: {digest}','','## Review queue']
    lines += [f"- Sample {f['sample']} {f['timestamp_utc']}: {f['channel']} = {f['measured_value']}" for f in flags]
    lines += ['','All flags require human review; thresholds alone do not establish a cause.']
    (folder/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    return manifest

def verify(folder):
    folder=Path(folder)
    m=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
    p=folder/m['source_file']
    return p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==m['source_sha256']

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('signal_demo_output'))
    parser.add_argument('--count',type=int,default=60)
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--verify',action='store_true')
    a=parser.parse_args()
    if a.verify:
        ok=verify(a.output); print('Integrity PASS' if ok else 'Integrity FAIL')
        raise SystemExit(0 if ok else 1)
    result=run(a.output,a.count,a.seed)
    print(f"Generated {result['samples']} SYNTHETIC readings; {len(result['flags'])} threshold flags.")
