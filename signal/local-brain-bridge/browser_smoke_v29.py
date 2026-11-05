"""Chromium v29 smoke. Localhost navigation is blocked in this test sandbox,
so same exact client-side modules are inlined into page.set_content. No Ollama.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parent
html=(ROOT/'v29.html').read_text()
for filename in ('casebook-core.js','fingerprint-core.js','correlation-core.js'):
    tag=f'<script src="{filename}"></script>'
    assert tag in html
    html=html.replace(tag,'<script>'+(ROOT/filename).read_text()+'</script>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce',accept_downloads=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html)
    assert 'v29' in page.locator('h1').inner_text()
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2')
    page.locator('#auto').uncheck()
    page.locator('#case-title').fill('MTC and camera cross-check')
    page.locator('#case-new').click()
    page.locator('#case-source').select_option('audio')
    page.locator('#case-source-label').fill('MTC Recorder A')
    page.locator('#case-observed').fill('2026-11-05T05:00:00-05:00')
    page.locator('#case-description').fill('An audio click was reported after the question.')
    page.locator('#case-timestamp').check()
    page.locator('#case-add').click()
    page.locator('#case-source').select_option('video')
    page.locator('#case-source-label').fill('Camera B')
    page.locator('#case-observed').fill('2026-11-05T10:00:04Z')
    page.locator('#case-description').fill('A light change was reported on a camera feed.')
    page.locator('#case-timestamp').uncheck()
    page.locator('#case-add').click()
    assert page.locator('#case-entries li').count()==2
    page.locator('#cor-run').click()
    assert '1 candidate time alignment' in page.locator('#cor-status').inner_text()
    assert 'Δ4.000s' in page.locator('#cor-report').inner_text()
    assert 'Independence is NOT verified' in page.locator('#cor-report').inner_text()
    assert 'No source recording or sensor stream was read' in page.locator('#cor-report').inner_text()
    with page.expect_download() as event:
        page.locator('#cor-export').click()
    data=Path(event.value.path()).read_text(encoding='utf-8')
    assert event.value.suggested_filename=='signal-timestamp-candidates.txt'
    assert 'Candidate timestamp alignments: 1' in data
    page.locator('#cor-window').fill('2')
    page.locator('#cor-run').click()
    assert '0 candidate time alignment' in page.locator('#cor-status').inner_text()
    page.locator('#cor-window').fill('5')
    page.locator('#cor-run').click()
    page.locator('#case-observed').fill('')
    page.locator('#case-source-label').fill('Unlabeled testimony')
    page.locator('#case-description').fill('A separate witness reported an odd sound.')
    page.locator('#case-add').click()
    page.locator('#cor-export').click()
    assert 'Casebook changed since this report' in page.locator('#cor-status').inner_text()
    page.locator('#cor-run').click()
    assert 'Missing explicit timestamps: 1' in page.locator('#cor-report').inner_text()
    page.locator('#cor-clear').click()
    assert 'No candidate alignments calculated' in page.locator('#cor-report').inner_text()
    assert not errors, errors
    print('PASS Chromium v29: responsive 390×844, human timestamps, candidate proximity, no-cause notice, local report export, tolerance, stale-report rejection, missing timestamp and clear.')
    print('Actual instrument/Windows/Ollama and browser-to-localhost integration remain untested.')
    page.screenshot(path='/mnt/data/signal_v29_preview.png',full_page=True)
    browser.close()
