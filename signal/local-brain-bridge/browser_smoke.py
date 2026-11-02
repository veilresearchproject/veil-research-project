from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    errs=[];requests=[]
    page.on('pageerror',lambda e: errs.append(str(e)))
    page.on('request',lambda r: requests.append((r.method,r.url)))
    # This test environment blocks localhost Chromium navigation. Test the exact
    # browser HTML inline; loopback server is exercised separately by unittest.
    page.set_content((root/'index.html').read_text(encoding='utf-8'),wait_until='load')
    assert page.get_by_text('No AI model active').is_visible()
    page.get_by_role('button',name='About VEIL').click()
    assert page.get_by_text('VEIL is an independent research initiative', exact=False).is_visible()
    page.locator('#question').fill('Tell me a joke')
    page.locator('#send').click()
    assert page.locator('.bubble.user').count()==2
    page.get_by_role('button',name='Check local model').click()
    assert page.get_by_text('Open through http://127.0.0.1:8765/',exact=False).is_visible()
    page.get_by_role('button',name='Clear chat').click()
    assert page.locator('.bubble').count()==1
    page.screenshot(path=str(root/'mobile_screenshot.png'),full_page=True)
    assert not errs,errs
    assert not requests,requests
    print('MOBILE SCRIPTED BROWSER SMOKE PASS; page errors=0; app requests=0; screenshot saved; backend tested separately')
    browser.close()