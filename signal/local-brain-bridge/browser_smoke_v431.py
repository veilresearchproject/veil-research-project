"""SIGNAL v43.1 standalone Chromium UI smoke. No real Ollama, microphone or instruments.
Local HTTP navigation blocked here; modules are inlined and WebCrypto is mocked only
for the file attach UI. Real SHA-256 correctness is independently tested by Node.
"""
from pathlib import Path
from io import BytesIO
from playwright.sync_api import sync_playwright,expect
import math,wave
ROOT=Path(__file__).resolve().parent
HTML=(ROOT/'v43_lab.html').read_text(encoding='utf-8')
for filename in ('voice-core.js','assignments-core.js','audio-core.js','dashboard-core.js','workflow-core.js','packet-core.js','briefing-core.js'):
    t=f'<script src="{filename}"></script>'
    assert t in HTML,filename
    HTML=HTML.replace(t,'<script>'+(ROOT/filename).read_text(encoding='utf-8')+'</script>')

def sample():
    b=BytesIO()
    with wave.open(b,'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000)
        signal=bytearray()
        for i in range(8000):
            high=(1600<=i<2400 or 5000<=i<5600)
            amp=int(math.sin(i*.095)*15000) if high else 0
            signal.extend(amp.to_bytes(2,'little',signed=True))
        w.writeframes(bytes(signal))
    return b.getvalue()

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':900},reduced_motion='reduce')
    errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    page.set_content(HTML)
    assert 'v43.1' in page.locator('h1').inner_text()
    assert 'No briefing requested' in page.locator('#assistant-caption').inner_text()
    page.locator('[data-brief="overview"]').click()
    assert 'No active case' in page.locator('#assistant-caption').inner_text()
    assert not requests,requests
    # A request for voice is rejected without deliberate device-voice consent.
    page.locator('#assistant-voice').click()
    assert 'consent checkbox' in page.locator('#assistant-voice-status').inner_text()
    page.locator('#assistant-question').fill('activate the panic box')
    page.locator('#assistant-form button[type="submit"]').click()
    assert 'cannot operate' in page.locator('#assistant-caption').inner_text()
    assert 'SIMULATION' in page.locator('.chip').inner_text()
    page.locator('#work-title').fill('Synthetic MTC experiment')
    page.locator('#work-start').click()
    assert 'session changed' in page.locator('#assistant-caption').inner_text().lower()
    page.locator('[data-brief="next"]').click()
    assert 'Attach a supported WAV' in page.locator('#assistant-caption').inner_text()
    # In about:blank this is a deterministic *fake* digest; not evidence integrity verification.
    page.evaluate("""() => {Object.defineProperty(window,'crypto',{configurable:true,value:{subtle:{digest:async()=>new Uint8Array(32).fill(77).buffer}}});}""")
    page.locator('#wav-file').set_input_files({'name':'synthetic.wav','mimeType':'audio/wav','buffer':sample()})
    page.locator('#work-attach').click()
    expect(page.locator('#work-status')).to_contain_text('amplitude marker')
    assert page.locator('#work-candidates li').count()==2
    page.locator('#assistant-question').fill('next marker')
    page.locator('#assistant-form button[type="submit"]').click()
    assert 'Next unreviewed candidate: marker 1' in page.locator('#assistant-caption').inner_text()
    assert page.locator('#work-marker').input_value()=='1'
    assert 'synthetic.wav' not in page.locator('#assistant-caption').inner_text()
    page.locator('#work-reviewer').fill('Synthetic investigator')
    page.locator('#work-reason').fill('Human note: do not identify cause until listening')
    page.locator('#work-review').click()
    assert 'session changed' in page.locator('#assistant-caption').inner_text().lower()
    page.locator('[data-brief="next"]').click()
    assert 'marker 2' in page.locator('#assistant-caption').inner_text()
    # Simulate browser TTS and preserve stale callback cancellation.
    page.evaluate("""() => {
        window.__assistantSpoken=[];
        window.SpeechSynthesisUtterance=class {constructor(text){this.text=text}};
        Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{
            cancel:()=>{},speak:u=>{window.__assistantSpoken.push(u);u.onstart?.()}
        }});
    }""")
    page.locator('#assistant-tts-consent').check()
    page.locator('#assistant-voice').click()
    assert page.locator('#assistant-entity').get_attribute('data-state')=='speaking'
    page.evaluate('window.__assistantSpoken[0].onboundary?.({charIndex:5})')
    page.locator('#assistant-stop').click()
    assert page.locator('#assistant-entity').get_attribute('data-state')=='idle'
    page.evaluate('window.__assistantSpoken[0].onend?.()')
    assert page.locator('#assistant-entity').get_attribute('data-state')=='idle'
    page.locator('[data-brief="stations"]').click()
    assert 'SYNTHETIC' in page.locator('#assistant-caption').inner_text()
    page.locator('[data-brief="assignments"]').click()
    assert '0 self-reported manual assignments' in page.locator('#assistant-caption').inner_text()
    page.locator('#assistant-reduce').check()
    assert 'none' in page.locator('.assistant-entity .orbit').evaluate('(e)=>e.style.animation')
    # Optional Ollama flow is explicitly enabled, with mocked same-origin backend.
    page.locator('#assistant-ai-details summary').click()
    assert page.locator('#assistant-ai-send').is_disabled()
    page.evaluate("""() => {
      window.assistantLocalOrigin=()=>true;
      window.__calls=[];
      window.fetch=async (url, options={})=>{
        window.__calls.push({url,body:options.body||null});
        return {ok:true,json:async()=>url==='/api/health'
          ?{model_ready:true,detail:'Fake Ollama'}
          :{reply:'Simulated local AI response; originals still need human review.'}}
      };
    }""")
    page.locator('#assistant-ai-enable').click()
    expect(page.locator('#assistant-ai-send')).to_be_enabled()
    page.locator('#assistant-ai-question').fill('What can a researcher verify?')
    page.locator('#assistant-ai-send').click()
    expect(page.locator('#assistant-caption')).to_contain_text('LOCAL AI — UNVERIFIED RESPONSE')
    calls=page.evaluate('window.__calls')
    assert len(calls)==2,calls
    assert calls[0]['url']=='/api/health'
    assert calls[1]['url']=='/api/chat'
    payload=__import__('json').loads(calls[1]['body'])
    assert payload=={'question':'What can a researcher verify?','history':[]}
    assert 'Synthetic MTC experiment' not in calls[1]['body']
    assert 'Human note: do not identify cause' not in calls[1]['body']
    # Case changes clear local AI context, preventing conversations bleeding across cases.
    page.on('dialog',lambda dialog:dialog.accept())
    page.locator('#work-title').fill('Another synthetic test case')
    page.locator('#work-start').click()
    assert 'Local AI context cleared' in page.locator('#assistant-ai-status').inner_text()
    assert page.evaluate('assistantAI.history.length')==0
    page.locator('#assistant-ai-enable').click()  # disable
    assert page.locator('#assistant-ai-send').is_disabled()
    # The older v43 tools remain present (regression check).
    for id_ in ['work-export','work-import','sim-event','memory-add','wav-analyze']:
        assert page.locator('#'+id_).count()==1
    assert not errors,errors
    assert not requests,requests
    page.screenshot(path=str(ROOT/'SIGNAL_v43_1_integrated_desktop.png'),full_page=False)
    mobile=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
    mobile.set_content(HTML)
    assert mobile.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2')
    mobile.locator('[data-brief="overview"]').click()
    assert 'No active case' in mobile.locator('#assistant-caption').inner_text()
    mobile.screenshot(path=str(ROOT/'SIGNAL_v43_1_integrated_mobile.png'),full_page=False)
    browser.close()
    print('PASS v43.1 Chromium: anonymous summaries, next marker, stale state, read-only refusal, consent TTS and stale callback, reduced motion, desktop/mobile, no outbound requests')
