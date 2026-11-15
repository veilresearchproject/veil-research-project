"""Update 6: static HTML overview, no scripts or external requests."""
from html import escape
from pathlib import Path
def render(folder,*,profile,windows,sample_count):
    cards=[]
    for w in windows:
        rows=''.join('<tr><td>'+str(f['sample'])+'</td><td>'+escape(f['channel'])+'</td><td>'+escape(str(f['value']))+'</td></tr>' for f in w['flags'])
        cards.append('<section><h2>'+escape(w['id'])+'</h2><p>Samples '+str(w['first_sample'])+'-'+str(w['last_sample'])+' / Channels: '+escape(', '.join(w['channels']))+'</p><table><thead><tr><th>Sample</th><th>Channel</th><th>Value</th></tr></thead><tbody>'+rows+'</tbody></table><p>Temporal proximity does not establish a common cause.</p></section>')
    html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SIGNAL Synthetic Lab</title><style>body{font:16px system-ui;max-width:960px;margin:3rem auto;padding:0 1rem;background:#101827;color:#eef5ff}section{border:1px solid #52647a;border-radius:12px;padding:1rem;margin:1rem 0}table{border-collapse:collapse;width:100%}td,th{padding:.5rem;text-align:left;border-bottom:1px solid #52647a}.warning{color:#ffd285}</style><main><h1>SIGNAL Laboratory Demonstrator</h1><p class="warning"><strong>SIMULATED DATA ONLY.</strong> No instruments, voice or AI model connected.</p><p>Profile: '+escape(profile.name)+' / Samples: '+str(sample_count)+' / Review windows: '+str(len(windows))+'</p>'+''.join(cards)+'<p>Human review required. Original simulated CSV and artifact inventory are in the same folder.</p></main></html>'
    p=Path(folder)/'dashboard.html';p.write_text(html,encoding='utf8');return p
