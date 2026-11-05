"""SIGNAL v33 Chromium smoke using actual UI modules; no localhost browser navigation.
The hosted Chromium environment blocks local HTTP navigation. This test injects
the local scripts and tests the UI only; it does not test Ollama or desktop voices.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
html=(HERE/'v33.html').read_text(encoding='utf-8')
for module in ('casebook-core.js','fingerprint-core.js','correlation-core.js','clock-core.js','blind-core.js'):
    tag=f'<script src="{module}"></script>'
    if tag not in html:raise AssertionError('UI requires '+module)
    html=html.replace(tag,'<script>'+(HERE/module).read_text(encoding='utf-8')+'</script>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce',accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda ex:errors.append(str(ex)))
    page.set_content(html)
    assert 'SIGNAL v33' in page.locator('h1').inner_text()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2')
    page.locator('#auto').uncheck()
    page.locator('button[data-prompt="Tell me a joke"]').click()
    assert page.locator('#chat .bubble').count()>=3
    page.locator('#case-title').fill('Synthetic browser rehearsal')
    page.locator('#case-new').click()
    for label,description,timestamp in [
        ('MTC Mic','Synthetic sound reported by operator','2026-11-05T10:00:00Z'),
        ('Camera B','Synthetic frame change described by operator','2026-11-05T10:00:03Z')]:
        page.locator('#case-source-label').fill(label)
        page.locator('#case-description').fill(description)
        page.locator('#case-observed').fill(timestamp)
        page.locator('#case-add').click()
    assert page.locator('#case-entries li').count()==2
    page.locator('#cor-run').click()
    assert '1 candidate time alignment' in page.locator('#cor-status').inner_text()
    page.locator('#blind-start').click()
    assert page.locator('#blind-items li').count()==2
    assert 'MTC Mic' not in page.locator('#blind-items').inner_text()
    page.locator('#blind-reset').click()
    assert page.locator('#blind-items li').count()==0
    assert not errors,errors
    print('PASS Chromium 390x844: SIGNAL v33 scripted chat, responsive layout, Casebook, timeline, blind review/reset')
    browser.close()
