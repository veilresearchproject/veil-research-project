"""SIGNAL v26 headless Chromium smoke test (scripted UI + mocked local APIs).
Requires playwright and Chromium. Does not contact Ollama or external services.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
    failures=[]
    page.on('pageerror',lambda e:failures.append(str(e)))
    page.set_content((ROOT/'v26.html').read_text(encoding='utf-8'))
    assert page.locator('#entity polygon').count()>=2
    page.locator('#auto').uncheck()
    page.locator('#reduce').check()
    assert page.locator('html').evaluate('(e)=>e.classList.contains("reduced")')
    page.locator('button[data-prompt="Tell me a joke"]').click()
    assert 'depth sensor' in page.locator('#chat').inner_text()
    assert 'MAGENTA' in page.locator('#state').inner_text()
    page.evaluate("""() => {
       window.__spoken=[];
       window.SpeechSynthesisUtterance=class{constructor(text){this.text=text;}};
       Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{
          getVoices:()=>[{name:'Microsoft Ryan Natural',lang:'en-US',localService:false}],
          speak:u=>{window.__spoken.push(u);u.onstart?.()},cancel:()=>{}
       }});
    }""")
    page.locator('#speak').click()
    assert 'HUMOR' in page.locator('#state').inner_text()
    page.evaluate('window.__spoken[0].onboundary({charIndex:3,charLength:8})')
    assert page.locator('#entity').evaluate('(e)=>e.classList.contains("word")')
    page.locator('#stop').click()
    assert 'IDLE' in page.locator('#state').inner_text()
    page.evaluate('window.__spoken[0].onend()')
    assert 'IDLE' in page.locator('#state').inner_text()
    page.locator('#question').fill('Activate the panic box now')
    page.locator('#ask').click()
    assert 'cannot activate' in page.locator('#chat').inner_text()
    page.locator('#clear').click()
    assert 'Session cleared' in page.locator('#notice').inner_text()
    # Browser harness mocks responses and localOrigin; not a real network test.
    page.evaluate("""() => {
       window.localOrigin=()=>true;
       window.fetch=async (path)=>({ok:true,json:async()=>path==='/api/health'
           ?{model_ready:true,detail:'Fake local model ready'}
           :{reply:'Simulated model answer. Verify original recordings.'}});
    }""")
    page.locator('#enable').click()
    page.wait_for_function('document.querySelector("#mode").textContent.includes("LOCAL OLLAMA")')
    page.locator('#question').fill('What controls should we check?')
    page.locator('#ask').click()
    page.wait_for_function('document.querySelector("#chat").textContent.includes("Simulated model answer")')
    page.locator('#enable').click()
    assert 'SCRIPTED' in page.locator('#mode').inner_text()
    assert not failures,failures
    print('PASS SIGNAL v26 Chromium mobile, speech callback lifecycle, read-only UI, mocked opt-in model')
    browser.close()
