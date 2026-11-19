"""Update 2: read-only strict CSV importer for synthetic data."""
import csv,math
from datetime import datetime
from pathlib import Path
from profile import CHANNELS
REQUIRED=('sample','timestamp_utc',*CHANNELS)
def load(path,max_rows=100000):
    if not 1<=max_rows<=1000000: raise ValueError('Invalid row cap')
    with Path(path).open(newline='',encoding='utf8') as stream:
        reader=csv.DictReader(stream)
        if tuple(reader.fieldnames or ())!=REQUIRED: raise ValueError('Unexpected columns')
        rows=[];previous=None
        for idx,row in enumerate(reader):
            if idx>=max_rows: raise ValueError('Too many rows')
            if None in row or any(v is None or not v.strip() for v in row.values()): raise ValueError('Malformed reading')
            if int(row['sample'])!=idx: raise ValueError('Noncontiguous sample index')
            when=datetime.fromisoformat(row['timestamp_utc'])
            if when.tzinfo is None or when.utcoffset().total_seconds()!=0: raise ValueError('UTC timestamps required')
            if previous and when<=previous: raise ValueError('Time order invalid')
            previous=when
            values={channel:float(row[channel]) for channel in CHANNELS}
            if not all(math.isfinite(v) for v in values.values()): raise ValueError('Nonfinite value')
            rows.append(dict(sample=idx,timestamp_utc=when.isoformat(),**values))
    if not rows: raise ValueError('Empty input')
    return rows
