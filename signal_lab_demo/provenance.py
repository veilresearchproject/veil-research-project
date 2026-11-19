"""Update 4: SHA-256 inventory of output artifacts."""
import hashlib,json
from pathlib import Path
def fingerprint(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inventory(folder,names):
    root=Path(folder);out=[]
    for name in names:
        p=root/name
        if p.name!=name or not p.is_file() or p.is_symlink(): raise ValueError('Output artifact must be a regular file')
        out.append(dict(name=name,bytes=p.stat().st_size,sha256=fingerprint(p)))
    return dict(schema='signal-artifact-inventory-v1',entries=out,source_type='SIMULATION',claim='Fingerprint checks changes, not authenticity')
def write_inventory(folder,names):
    m=inventory(folder,names)
    (Path(folder)/'artifact_inventory.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
    return m
def verify_inventory(folder):
    root=Path(folder);m=json.loads((root/'artifact_inventory.json').read_text(encoding='utf8'))
    return all(Path(e['name']).name==e['name'] and (root/e['name']).is_file() and (root/e['name']).stat().st_size==e['bytes'] and fingerprint(root/e['name'])==e['sha256'] for e in m['entries'])
