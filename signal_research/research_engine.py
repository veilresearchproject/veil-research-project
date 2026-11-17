"""Offline bounded research-result ledger. No web requests or automated Lens access."""
import hashlib, ipaddress, json
from urllib.parse import urlsplit, urlunsplit

def normalize_url(url):
    if not isinstance(url,str) or len(url)>2048 or any(ord(c)<33 for c in url): raise ValueError("Invalid URL")
    p=urlsplit(url)
    if p.scheme!="https" or not p.hostname or p.username or p.password or p.fragment: raise ValueError("Public HTTPS required")
    host=p.hostname.rstrip(".").lower()
    if host=="localhost" or host.endswith((".localhost",".local",".internal")): raise ValueError("Private host")
    try: ip=ipaddress.ip_address(host)
    except ValueError:
        if "." not in host or any(not x for x in host.split(".")): raise ValueError("Invalid host")
    else:
        if not ip.is_global: raise ValueError("Private IP")
    if p.port not in (None,443): raise ValueError("Unexpected port")
    return urlunsplit(("https",p.netloc.lower(),p.path or "/",p.query,""))

def prepare_results(records):
    from datetime import datetime
    if not isinstance(records,list) or len(records)>20: raise ValueError("Maximum 20 results")
    out=[];seen=set()
    for r in records:
        if not isinstance(r,dict) or set(r)!={"url","title","excerpt","observed_utc"}: raise ValueError("Invalid fields")
        url=normalize_url(r["url"]);title=r["title"];excerpt=r["excerpt"];stamp=r["observed_utc"]
        if not isinstance(title,str) or not 1<=len(title)<=180: raise ValueError("Invalid title")
        if not isinstance(excerpt,str) or len(excerpt)>600: raise ValueError("Invalid excerpt")
        if not isinstance(stamp,str) or not stamp.endswith("Z"): raise ValueError("UTC required")
        try: datetime.fromisoformat(stamp.replace("Z","+00:00"))
        except ValueError as e: raise ValueError("Invalid date") from e
        if url in seen: continue
        seen.add(url)
        digest=hashlib.sha256((url+"\n"+title+"\n"+excerpt).encode()).hexdigest()
        out.append(dict(citation_id=f"R{len(out)+1:03}",url=url,title=title,excerpt=excerpt,observed_utc=stamp,record_sha256=digest,status="UNVERIFIED_HUMAN_SUPPLIED",original_image_verified=False))
    return out

def save_ledger(db,records):
    items=prepare_results(records)
    db.execute("CREATE TABLE IF NOT EXISTS research_sources (citation_id TEXT PRIMARY KEY,payload TEXT NOT NULL)")
    with db:
        for item in items: db.execute("INSERT OR REPLACE INTO research_sources VALUES (?,?)",(item["citation_id"],json.dumps(item,sort_keys=True)))
    return len(items)

def citation_brief(items):
    if len(items)>20: raise ValueError("Too many sources")
    return "\n".join(f"[{x['citation_id']}] {x['title']} — {x['url']} (unverified, observed {x['observed_utc']})" for x in items)
