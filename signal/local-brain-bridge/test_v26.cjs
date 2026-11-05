'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'v26.html'),'utf8');
const match=html.match(/<script>([\s\S]*?)<\/script>/);assert(match,'inline script exists');new vm.Script(match[1],{filename:'v26.html:inline-script'});
const checks=[
 ['faceless geometric SVG',()=>assert.match(html,/<polygon class="facet"/)],
 ['all expression states',()=>['idle','listening','thinking','speaking','humor','uncertain','error'].forEach(x=>assert.match(html,new RegExp(x)))],
 ['captions and reduced motion',()=>{assert.match(html,/id="captions"/);assert.match(html,/prefers-reduced-motion/);assert.match(html,/id="reduce"/)}],
 ['no remote connections allowed by CSP',()=>assert.match(html,/connect-src 'self'/)],
 ['scripted mode default and opt-in',()=>{assert.match(html,/let mode='scripted'/);assert.match(html,/id="enable"/)}],
 ['same-origin Ollama request',()=>{assert.match(html,/fetch\('\/api\/chat'/);assert.match(html,/fetch\('\/api\/health'/)}],
 ['session only bounded history',()=>{assert.match(html,/history\.slice\(-12\)/);assert.doesNotMatch(html,/(?:localStorage|sessionStorage|indexedDB|document\.cookie)/)}],
 ['voice lifecycle guards',()=>{assert.match(html,/voiceEpoch/);assert.match(html,/u\.onboundary/);assert.match(html,/u\.onend/);assert.match(html,/stopVoice\(\)/)}],
 ['no camera or microphone capture',()=>assert.doesNotMatch(html,/(?:getUserMedia|SpeechRecognition|mediaDevices)/)],
 ['read-only control denial',()=>assert.match(html,/function disallowedControl/)],
 ['generated code parses',()=>assert.ok(true)],
 ['preview binds loopback on alternate port',()=>{const s=fs.readFileSync(path.join(__dirname,'v26_server.py'),'utf8');assert.match(s,/127\.0\.0\.1/);assert.match(s,/8766/);assert.match(s,/from server import Handler/)}]
];
for (const [name,test] of checks){test();console.log('PASS '+name)}console.log(`${checks.length}/${checks.length} SIGNAL v26 static/contract checks passed`);
