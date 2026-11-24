"""SIGNAL v0.3: synthetic-only offline lab workflow, no network or real hardware."""
import argparse, hashlib, json, re
from pathlib import Path
from ingest import load
from profile import DEFAULT
from correlate import flag, windows
from provenance import fingerprint, write_inventory, verify_inventory
from run_lab import run_v02

SCHEMA='signal-lab-0.3'
def parse_command(text):
    if not isinstance(text,str) or len(text)>200:raise ValueError('Invalid command')
    normalized=' '.join(text.strip().lower().split())
    phrases={'status':['status','lab status','signal status','what is the lab status'],
             'plan':['plan','show protocol','describe experiment'],
             'run':['run simulation','start simulated experiment'],
             'report':['report','show report','summarize simulation'],
             'review':['review','review flags','show review queue'],
             'verify':['verify','verify evidence','check evidence integrity']}
    for action,values in phrases.items():
        if normalized in values:return dict(action=action,authorized=action!='run',scope='SIMULATION_ONLY')
    raise ValueError('Unrecognized command')
def protocol(count=60,seed=42,warmup=5,cooldown=5):
    if any(not isinstance(v,int) or isinstance(v,bool) for v in (count,seed,warmup,cooldown)):raise ValueError('Integer values required')
    if not 10<=count<=100000 or not 0<=warmup<=3600 or not 0<=cooldown<=3600:raise ValueError('Out of range')
    return dict(schema=SCHEMA,mode='SYNTHETIC_ONLY',samples=count,seed=seed,
        sample_interval_seconds=DEFAULT.interval_seconds,warmup_seconds=warmup,
        cooldown_seconds=cooldown,estimated_virtual_duration_seconds=warmup+cooldown+count*DEFAULT.interval_seconds,
        human_authorization_required=True,physical_outputs_enabled=False,
        interpretation_policy='Flag measurements, never infer a cause')
def preflight(p):
    problems=[]
    if p.get('mode')!='SYNTHETIC_ONLY':problems.append('Synthetic mode required')
    if p.get('physical_outputs_enabled') is not False:problems.append('Physical outputs disabled')
    if p.get('human_authorization_required') is not True:problems.append('Authorization gate required')
    try:
        if not 10<=p['samples']<=100000:problems.append('Invalid count')
    except (KeyError,TypeError,ValueError):problems.append('Invalid count')
    if p.get('sample_interval_seconds')!=DEFAULT.interval_seconds:problems.append('Invalid interval')
    return dict(passed=not problems,problems=problems,physical_device_connected=False)
def virtual_schedule(p):
    warm=p['warmup_seconds'];end=warm+p['samples']*p['sample_interval_seconds']
    return [dict(phase='warmup',start_second=0,end_second=warm),
        dict(phase='synthetic_sampling',start_second=warm,end_second=end),
        dict(phase='cooldown',start_second=end,end_second=end+p['cooldown_seconds'])]
def sensor_health(rows):
    if not rows:raise ValueError('Empty rows')
    return dict(sample_count=len(rows),sensor_channels={c:dict(
      min=min(r[c] for r in rows),max=max(r[c] for r in rows),
      distinct_values=len(set(r[c] for r in rows)),
      stuck_sensor_warning=len(set(r[c] for r in rows))==1 and len(rows)>=3)
      for c in ('temperature_c','humidity_pct','sound_db')},health_is_not_calibration=True)
def make_casebook(groups,digest):
    return dict(schema='signal-casebook-0.1',synthetic_data=True,cases=[
        dict(case_id=g['id'],source='synthetic_readings.csv',source_sha256=digest,
             first_sample=g['first_sample'],last_sample=g['last_sample'],channels=g['channels'],
             flags=g['flags'],status='UNREVIEWED',uncertainty='Threshold flags only; cause unknown')
        for g in groups])
def summarize(rows,groups,health):
    return (f'SIGNAL simulated laboratory briefing: {len(rows)} synthetic samples were checked across '
      f'{len(health["sensor_channels"])} channels. {len(groups)} event window(s) require human review. '
      'No real sensors were connected. No causal conclusions were drawn.')
def safe_artifact_name(name):
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',name) or '..' in name or name.startswith('.'):
        raise ValueError('Invalid artifact name')
    return name
def verify_full_bundle(folder):
    folder=Path(folder)
    if not verify_inventory(folder):return False
    m=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
    if m.get('dataset_type')!='SYNTHETIC_SIMULATION' or m.get('source_sha256')!=fingerprint(folder/'synthetic_readings.csv'):return False
    book=json.loads((folder/'casebook.json').read_text(encoding='utf8'))
    return book.get('synthetic_data') is True and all(x['source_sha256']==m['source_sha256'] for x in book['cases'])
def execute(folder,*,count=60,seed=42,operator_approved=False):
    p=protocol(count,seed);gate=preflight(p)
    if not gate['passed']:raise RuntimeError('Preflight failed')
    if operator_approved is not True:raise PermissionError('Explicit simulation approval required')
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    run_v02(folder,count=count,seed=seed)
    rows=load(folder/'synthetic_readings.csv');groups=windows(flag(rows,DEFAULT))
    outputs={'protocol.json':p,'preflight.json':gate,'schedule.json':virtual_schedule(p),
        'sensor_health.json':sensor_health(rows),
        'casebook.json':make_casebook(groups,fingerprint(folder/'synthetic_readings.csv'))}
    for name,payload in outputs.items():
        safe_artifact_name(name);(folder/name).write_text(json.dumps(payload,indent=2)+'\n',encoding='utf8')
    (folder/'briefing.txt').write_text(summarize(rows,groups,outputs['sensor_health.json'])+'\n',encoding='utf8')
    write_inventory(folder,['synthetic_readings.csv','manifest.json','report.md','event_windows.json','dashboard.html',*outputs,'briefing.txt'])
    if not verify_full_bundle(folder):raise RuntimeError('Integrity failed')
    return dict(schema=SCHEMA,samples=count,cases=len(groups),bundle_verified=True,simulated_only=True,
      briefing=(folder/'briefing.txt').read_text(encoding='utf8').strip())
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=Path('signal_advanced_output'))
    p.add_argument('--count',type=int,default=60)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--approve-simulation',action='store_true')
    p.add_argument('--verify-only',action='store_true')
    a=p.parse_args()
    if a.verify_only:
        ok=verify_full_bundle(a.output);print('Bundle PASS' if ok else 'Bundle FAIL');raise SystemExit(0 if ok else 1)
    print(json.dumps(execute(a.output,count=a.count,seed=a.seed,operator_approved=a.approve_simulation),indent=2))
