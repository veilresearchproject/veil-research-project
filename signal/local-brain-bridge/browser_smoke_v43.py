"""Chromium v43 UI smoke using real deterministic analysis but MOCK SHA-256.
Localhost and external navigation are blocked by this test sandbox. Unit tests
verify real Node WebCrypto separately; browser mock exercises app lifecycle.
"""
from pathlib import Path
from io import BytesIO
import math
import wave
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parent

def make_wav():
    buf=BytesIO()
    with wave.open(buf,'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000)
        data=bytearray()
        for i in range(8000):
            pulse=1600<=i<2400 or 5000<=i<5600
            level=int(math.sin(i*.095)*15000) if pulse else 0
            data.extend(level.to_bytes(2,'little',signed=True))
        w.writeframes(bytes(data))
    return buf.getvalue()

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':900},accept_downloads=True,reduced_motion='reduce')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    html=(ROOT/'v43_lab.html').read_text()
    for module in ['voice-core.js','assignments-core.js','audio-core.js','dashboard-core.js','workflow-core.js','packet-core.js']:
        html=html.replace(f'<script src="{module}"></script>',f'<script>{(ROOT/module).read_text()}</script>')
    page.set_content(html)
    # Browser at about:blank cannot use WebCrypto. Inject deterministic MOCK digest,
    # never used to assert real SHA-256 correctness or produce genuine fingerprints.
    stub="""() => {
        Object.defineProperty(window,'crypto',{configurable:true,value:{subtle:{digest:async (_,data)=>{
          const bytes=new Uint8Array(data),out=new Uint8Array(32);let n=2166136261;
          for(let i=0;i<bytes.length;i++){n=Math.imul((n^bytes[i])>>>0,16777619)>>>0;out[i%32]^=n&255;out[(i+11)%32]^=(n>>>8)&255;}
          return out.buffer;
        }}}});
    }"""
    page.evaluate(stub)
    assert page.locator('h1').inner_text().find('v43')>=0
    assert page.evaluate('!!crypto.subtle')
    assert 'SIMULATION / REVIEW ONLY' in page.locator('.chip').inner_text()
    page.locator('#work-title').fill('MTC synthetic bench session')
    page.locator('#work-start').click()
    assert 'no WAV attached' in page.locator('#work-status').inner_text()
    file_bytes=make_wav()
    page.locator('#wav-file').set_input_files({'name':'synthetic.wav','mimeType':'audio/wav','buffer':file_bytes})
    page.locator('#work-attach').click()
    expect(page.locator('#work-status')).to_contain_text('amplitude marker')
    assert page.locator('#work-candidates li').count()>=2
    assert 'File SHA-256' in page.locator('#work-report-view').inner_text()
    page.locator('#work-marker').select_option('1')
    page.locator('#work-reviewer').fill('Synthetic investigator')
    page.locator('#work-reason').fill('Synthetic tone pulse; needs independent original playback check')
    page.locator('#work-review').click()
    assert 'human review(s)' in page.locator('#work-status').inner_text()
    page.locator('#work-marker').select_option('1')
    page.locator('#work-task').click()
    assert page.locator('#task-entries li').count()==1
    assert 'manual task' in page.locator('#work-status').inner_text()
    page.locator('#work-speak').click()
    assert 'human notes' in page.locator('#voice-text').input_value()
    with page.expect_download() as d:
        page.locator('#work-export').click()
    packet=Path(d.value.path()).read_bytes()
    assert b'signal-session-handoff' in packet
    assert b'approved_memory_v34' not in packet
    assert len(packet)<250000
    page.on('dialog',lambda dialog:dialog.accept())
    page.locator('#work-import-file').set_input_files({'name':'session.json','mimeType':'application/json','buffer':packet})
    page.locator('#work-import').click()
    expect(page.locator('#work-status')).to_contain_text('Checked local JSON loaded')
    assert page.locator('#task-entries li').count()==1
    assert page.locator('#work-candidates li').count()>=2
    # Tampering with file label must be rejected, even though format still valid.
    corrupted=packet.replace(b'synthetic.wav',b'altered__.wav')
    page.locator('#work-import-file').set_input_files({'name':'tampered.json','mimeType':'application/json','buffer':corrupted})
    page.locator('#work-import').click()
    expect(page.locator('#work-status')).to_contain_text('Import refused')
    assert 'digest mismatch' in page.locator('#work-status').inner_text().lower()
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(ROOT/'SIGNAL_v43_actual_desktop.png'),full_page=False)
    assert not errors, errors
    mobile=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
    mobile.set_content(html)
    assert mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2')
    mobile.screenshot(path=str(ROOT/'SIGNAL_v43_actual_mobile.png'),full_page=False)
    print('PASS v43 Chromium: mocked digest, 2 real synthetic WAV energy markers, manual review, assignment, summary, export/import, tamper rejection and 390px responsive layout')
    browser.close()
