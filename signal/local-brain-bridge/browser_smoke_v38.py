"""Real Chromium DOM smoke with isolated local JS modules and mocked memory API.
No localhost network, microphone, hardware or real Ollama calls.
"""
from pathlib import Path
import struct
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
html=(ROOT/'v38_lab.html').read_text(encoding='utf-8')
for f in ['voice-core.js','assignments-core.js','audio-core.js','dashboard-core.js']:
 tag=f'<script src="{f}"></script>'
 assert tag in html
 html=html.replace(tag,'<script>'+(ROOT/f).read_text(encoding='utf-8')+'</script>')
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce')
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(html)
 assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2')
 assert 'SIMULATED' in page.locator('#sim-report').inner_text()
 assert page.locator('.station').count()==3
 page.locator('#sim-event').click()
 assert '2 attention' in page.locator('#sim-status').inner_text()
 page.locator('#sim-reset').click()
 assert '1 attention' in page.locator('#sim-status').inner_text()
 page.locator('#task-description').fill('Manually review synthetic session notes')
 page.locator('#task-create').click()
 assert page.locator('#task-entries li').count()==1
 page.locator('button:text("Mark manually started")').click()
 assert 'IN-PROGRESS' in page.locator('#task-entries').inner_text()
 page.locator('#voice-ptt').click()
 assert 'LISTENING' in page.locator('#voice-state').inner_text()
 page.locator('#voice-transcript').fill('Stop there, SIGNAL')
 page.locator('#voice-transmit').click()
 assert 'PROCESSING' in page.locator('#voice-state').inner_text()
 page.locator('#voice-stop').click()
 assert 'IDLE' in page.locator('#voice-state').inner_text()
 # Mock only the local persistence endpoints. No network request is made.
 page.evaluate('''() => {window.__memory=[];window.fetch=async(url,opts={})=>{
   let data={};if(opts.body)data=JSON.parse(opts.body);
   if(url==='/api/memory')return {ok:true,json:async()=>({entries:window.__memory})};
   if(url==='/api/memory/add'){
      if(!data.approved)return {ok:false,json:async()=>({error:'Approval needed'})};
      const e={...data,id:'a'.repeat(32)};window.__memory.push(e);
      return {ok:true,json:async()=>({result:e})};
   }
   throw Error('Unexpected network call: '+url);
 };}''')
 page.locator('#memory-note').fill('<img src=x onerror=alert(1)> synthetic note')
 page.locator('#memory-source').fill('Synthetic methods log')
 page.locator('#memory-by').fill('VEIL operator')
 page.locator('#memory-add').click()
 assert 'Please approve' in page.locator('#memory-status').inner_text()
 page.locator('#memory-approved').check()
 page.locator('#memory-add').click()
 page.wait_for_function('document.querySelectorAll("#memory-entries li").length===1')
 assert page.locator('#memory-entries img').count()==0
 # Generate real 16-bit PCM bytes, 8000Hz, 0.5 s with 0.1 s transient.
 values=[int(15000 if 1600<=i<2400 and i%2==0 else -15000 if 1600<=i<2400 else 0) for i in range(4000)]
 pcm=struct.pack('<%dh'%len(values),*values)
 riff=b'RIFF'+struct.pack('<I',36+len(pcm))+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,1,8000,16000,2,16)+b'data'+struct.pack('<I',len(pcm))+pcm
 page.locator('#wav-file').set_input_files({'name':'synthetic.wav','mimeType':'audio/wav','buffer':riff})
 page.locator('#wav-analyze').click()
 page.wait_for_function('document.querySelector("#wav-status").textContent.includes("Analysis complete")')
 assert '1 volume-energy' in page.locator('#wav-status').inner_text()
 assert 'no EVP/paranormal conclusion' in page.locator('#wav-report').inner_text()
 page.screenshot(path=str(ROOT/'SIGNAL_v38_lab_screenshot.png'),full_page=True)
 assert not errors,errors
 browser.close()
print('PASS v38 actual Chromium mobile DOM: simulated stations, assignments, voice, approval memory, safe text, real in-browser synthetic PCM analysis')
