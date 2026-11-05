"""Headless Chromium UI smoke. The testing sandbox blocks localhost navigation.
Inline the existing local Casebook module for page.set_content, and mock only the
local bridge fetch. This is NOT an actual browser-to-Python/Ollama roundtrip.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

DIR=Path(__file__).resolve().parent
html=(DIR/'v27.html').read_text(encoding='utf-8')
core=(DIR/'casebook-core.js').read_text(encoding='utf-8')
assert '<script src="casebook-core.js"></script>' in html
html=html.replace('<script src="casebook-core.js"></script>', '<script>'+core+'</script>')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html)
    assert page.locator('h1').inner_text().startswith('SIGNAL v27')
    assert page.locator('#entity polygon').count()>=2
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2'), 'horizontal mobile overflow'
    assert page.locator('#case-state').inner_text().startswith('No active case')
    page.locator('#auto').uncheck()
    page.locator('button[data-prompt="Tell me a joke"]').click()
    assert 'depth sensor' in page.locator('#chat').inner_text()
    page.locator('#case-title').fill('Unattended MTC rehearsal')
    page.locator('#case-new').click()
    page.locator('#case-source').select_option('audio')
    page.locator('#case-source-label').fill('Recorder A')
    page.locator('#case-observed').fill('2026-11-05T05:15:00-05:00')
    page.locator('#case-description').fill('<img src=x onerror="alert(1)"> A click was reported after question three.')
    page.locator('#case-original').check()
    page.locator('#case-add').click()
    assert page.locator('#case-entries li').count()==1
    assert '<img src=x onerror=' in page.locator('#case-entries').inner_text()
    assert page.locator('#case-entries img').count()==0, 'XSS-like description rendered as HTML'
    assert 'Items needing follow-up: 3' in page.locator('#case-summary').inner_text()
    assert 'No recording, image, sensor dataset' in page.locator('#case-summary').inner_text()
    page.locator('#case-ask-ai').click()
    assert 'Enable your local Ollama' in page.locator('#case-notice').inner_text()
    page.locator('#case-reviewer').fill('Researcher')
    page.locator('#case-decision').select_option('reviewed-inconclusive')
    page.locator('#case-review').click()
    assert 'reviewed-inconclusive' in page.locator('#case-state').inner_text()
    with page.expect_download() as download_info:
        page.locator('#case-export').click()
    download=download_info.value
    assert download.suggested_filename=='signal-casebook-v1.json'
    data=Path(download.path()).read_text(encoding='utf-8')
    assert 'A click was reported' in data
    page.on('dialog',lambda dialog:dialog.accept())
    page.locator('#case-discard').click()
    assert page.locator('#case-entries li').count()==0
    page.locator('#case-file').set_input_files({'name':'case.json','mimeType':'application/json','buffer':data.encode('utf-8')})
    page.wait_for_function('document.querySelectorAll("#case-entries li").length===1')
    assert '1 observation' in page.locator('#case-state').inner_text()
    assert not page.locator('#case-share').is_checked()
    # Stub browser-local bridge. No actual network request leaves this sandbox.
    page.evaluate("""() => {
      window.__mockChats=[];
      window.localOrigin=()=>true;
      window.fetch=async (url,options={})=>{
        if(url==='/api/health')return {ok:true,json:async()=>({model_ready:true,detail:'Mock model ready'})};
        if(url==='/api/chat'){window.__mockChats.push(JSON.parse(options.body));return {ok:true,json:async()=>({reply:'Mock model: check fans and timestamps. No original file reviewed.'})};}
        throw Error('Unexpected API');
      };
    }""")
    page.locator('#enable').click()
    page.wait_for_function('document.querySelector("#mode").textContent.includes("LOCAL OLLAMA")')
    page.locator('#case-ask-ai').click()
    assert 'Check explicit case-sharing consent' in page.locator('#case-notice').inner_text()
    assert page.evaluate('window.__mockChats.length')==0
    page.locator('#case-share').check()
    page.locator('#case-ask-ai').click()
    page.wait_for_function('document.querySelector("#chat").textContent.includes("Mock model:")')
    data=page.evaluate('window.__mockChats')
    assert len(data)==1
    assert 'not inspected original recordings' in data[0]['question']
    assert 'A click was reported' in data[0]['question']
    assert len(data[0]['question'])<=800
    assert not errors, errors
    print('PASS Chromium 390×844: case intake, sanitized output, gap assessment, review, JSON roundtrip, double opt-in, bounded mocked local AI')
    print('Actual Ollama and Windows device speech are NOT tested here.')
    browser.close()
