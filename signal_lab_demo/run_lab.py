"""Run six additive, standard-library SIGNAL lab updates on synthetic data."""
import argparse,json
from pathlib import Path
from signal_lab_demo import run
from profile import DEFAULT
from ingest import load
from correlate import flag,windows
from provenance import write_inventory,verify_inventory
from dashboard import render
def run_v02(folder,*,count=60,seed=42):
    folder=Path(folder)
    run(folder,count,seed)
    rows=load(folder/'synthetic_readings.csv')
    flagged=flag(rows,DEFAULT)
    groups=windows(flagged)
    (folder/'event_windows.json').write_text(json.dumps(groups,indent=2)+'\n',encoding='utf8')
    render(folder,profile=DEFAULT,windows=groups,sample_count=len(rows))
    manifest=write_inventory(folder,['synthetic_readings.csv','manifest.json','report.md','event_windows.json','dashboard.html'])
    if not verify_inventory(folder):raise RuntimeError('Artifact fingerprint validation failed')
    return dict(samples=len(rows),flags=len(flagged),windows=len(groups),inventory_entries=len(manifest['entries']))
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=Path('signal_lab_output'))
    p.add_argument('--count',type=int,default=60)
    p.add_argument('--seed',type=int,default=42)
    args=p.parse_args()
    print(json.dumps(run_v02(args.output,count=args.count,seed=args.seed),indent=2))
