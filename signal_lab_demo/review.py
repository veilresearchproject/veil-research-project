"""Update 5: append-only human decision log (JSON Lines)."""
import json
from pathlib import Path
from datetime import datetime,timezone
DECISIONS=('unreviewed','needs_followup','explained','inconclusive')
def record(path,*,event_id,reviewer,decision,note,when=None):
    if not event_id.startswith('W-') or not event_id[2:].isdigit():raise ValueError('Invalid event ID')
    if not reviewer.strip() or len(reviewer)>120:raise ValueError('Reviewer required')
    if decision not in DECISIONS or len(note)>2000:raise ValueError('Invalid review')
    instant=when or datetime.now(timezone.utc)
    if instant.tzinfo is None:raise ValueError('Timezone required')
    r=dict(event_id=event_id,reviewer=reviewer,decision=decision,note=note,reviewed_at_utc=instant.astimezone(timezone.utc).isoformat())
    with Path(path).open('a',encoding='utf8') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    return r
def read(path):
    p=Path(path)
    return [json.loads(line) for line in p.read_text(encoding='utf8').splitlines() if line.strip()] if p.exists() else []
