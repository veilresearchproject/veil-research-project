"""SIGNAL v31 synthetic Chromium UI smoke; requires Playwright and /usr/bin/chromium.
Inlines local modules because the isolated browser sandbox blocks localhost navigation.
No Ollama, external URLs or original evidence files.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
html=(ROOT/'v31.html').read_text(encoding='utf-8')
for name in ('casebook-core.js','fingerprint-core.js','correlation-core.js','clock-core.js','blind-core.js'):
    tag=f'<script src="{name}"></script>'
    assert tag in html
    html=html.replace(tag,'<script>'+(ROOT/name).read_text(encoding='utf-8')+'</script>')
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
    page.locator('#auto').uncheck()
    page.locator('#case-title').fill('Synthetic source-identity rehearsal')
    page.locator('#case-new').click()
    for label,description in [('MTC Recorder','Synthetic click reported in audio'),
                              ('Camera 2','Synthetic brightening reported in video')]:
        page.locator('#case-source-label').fill(label)
        page.locator('#case-observed').fill('2026-11-05T10:00:00Z')
        page.locator('#case-description').fill(description)
        page.locator('#case-add').click()
    page.locator('#blind-start').click()
    assert page.locator('#blind-items li').count()==2
    assert page.locator('#casebook').evaluate("e=>getComputedStyle(e).display==='none'")
    assert 'MTC Recorder' not in page.locator('#blind-items').inner_text()
    page.locator('#blind-reveal').click()
    assert 'full current review is required' in page.locator('#blind-status').inner_text()
    with page.expect_download() as e:
        page.locator('#blind-packet').click()
    packet=Path(e.value.path()).read_text()
    assert 'MTC Recorder' not in packet and 'Camera 2' not in packet
    page.locator('#blind-reviewer').fill('Anonymous reviewer')
    for s in page.locator('#blind-items select').all():s.select_option('needs-more-data')
    for t in page.locator('#blind-items textarea').all():t.fill('Check the original media and mundane explanations')
    page.locator('#blind-lock').click()
    assert page.locator('#blind-items select').first.is_disabled()
    with page.expect_download() as e2:
        page.locator('#blind-review-export').click()
    review=Path(e2.value.path()).read_text()
    assert 'needs-more-data' in review and 'MTC Recorder' not in review
    page.locator('#blind-reveal').click()
    assert 'MTC Recorder' in page.locator('#blind-output').inner_text()
    assert 'not a paranormal finding' in page.locator('#blind-output').inner_text()
    page.locator('#blind-reset').click()
    assert page.locator('#blind-items li').count()==0
    assert not errors,errors
    print('PASS v31 Chromium synthetic source-hidden review, gated reveal, local exports and reset')
    browser.close()
