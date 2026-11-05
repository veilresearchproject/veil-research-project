"""Chromium UI smoke; localhost navigation blocked by sandbox, so same exact
local browser modules are inlined in page.set_content. No actual model call.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
DIR=Path(__file__).resolve().parent
html=(DIR/'v28.html').read_text(encoding='utf-8')
for name in ['casebook-core.js','fingerprint-core.js']:
    marker=f'<script src="{name}"></script>'
    assert marker in html
    html=html.replace(marker,'<script>'+(DIR/name).read_text(encoding='utf-8')+'</script>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html)
    assert 'v28' in page.locator('h1').inner_text()
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2')
    # About:blank in this sandbox is not a secure context, so WebCrypto is unavailable.
    # Stub the well-known SHA-256(abc) vector to exercise UI only; actual algorithm
    # is separately verified by Node WebCrypto tests.
    page.evaluate("""() => {const hex='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad';
      const b=new Uint8Array(hex.match(/../g).map(x=>parseInt(x,16)));
      Object.defineProperty(window.crypto,'subtle',{configurable:true,value:{digest:async()=>b.buffer}});
    }""")
    page.locator('#auto').uncheck()
    page.locator('#case-title').fill('MTC audio comparison')
    page.locator('#case-new').click()
    page.locator('#hash-file').set_input_files({'name':'known.txt','mimeType':'text/plain','buffer':b'abc'})
    page.locator('#hash-calc').click()
    expect(page.locator('#hash-output')).to_contain_text("ba7816bf8f01cfea")
    digest='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    assert digest in page.locator('#hash-output').inner_text()
    assert 'No file bytes were uploaded' in page.locator('#hash-status').inner_text()
    page.locator('#hash-reference').fill(digest.upper())
    page.locator('#hash-compare').click()
    assert 'MATCH' in page.locator('#hash-status').inner_text()
    assert 'does not prove origin' in page.locator('#hash-status').inner_text()
    page.locator('#hash-reference').fill('0'*64)
    page.locator('#hash-compare').click()
    assert 'MISMATCH' in page.locator('#hash-status').inner_text()
    page.locator('#hash-copy').click()
    assert digest in page.locator('#case-description').input_value()
    assert 'not origin or authenticity' in page.locator('#case-description').input_value()
    page.locator('#case-add').click()
    assert page.locator('#case-entries li').count()==1
    assert 'original-file preservation not confirmed' in page.locator('#case-summary').inner_text()
    # Read-only hashing must not transmit automatically or add a case note without user click.
    page.locator('#hash-clear').click()
    assert page.locator('#hash-file').input_value()==''
    assert digest not in page.locator('#hash-output').inner_text()
    assert not errors, errors
    print('PASS Chromium 390×844 v28: mocked WebCrypto digest, match/mismatch, explicit note insertion, clear and no JS errors')
    print('Sandbox limitation: browser routes to localhost are blocked; UI modules tested with page.set_content.')
    page.screenshot(path="/mnt/data/signal_v28_preview.png",full_page=True)
    browser.close()
