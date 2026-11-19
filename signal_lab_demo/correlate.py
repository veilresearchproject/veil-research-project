"""Update 3: group nearby threshold flags without claiming causation."""
from profile import CHANNELS
def flag(rows,profile):
    return [dict(sample=r['sample'],timestamp_utc=r['timestamp_utc'],channel=c,value=r[c],range=list(profile.thresholds[c])) for r in rows for c in CHANNELS if not profile.thresholds[c][0]<=r[c]<=profile.thresholds[c][1]]
def windows(flags,distance_samples=2):
    if not 0<=distance_samples<=1000: raise ValueError('Invalid window')
    ordered=sorted(flags,key=lambda f:(f['sample'],f['channel']))
    groups=[]
    for f in ordered:
        if not groups or f['sample']-groups[-1][-1]['sample']>distance_samples:groups.append([])
        groups[-1].append(f)
    return [dict(id=f'W-{i:03d}',first_sample=g[0]['sample'],last_sample=g[-1]['sample'],channels=sorted({f['channel'] for f in g}),flags=g,interpretation='Temporal proximity only; no common cause established') for i,g in enumerate(groups,1)]
