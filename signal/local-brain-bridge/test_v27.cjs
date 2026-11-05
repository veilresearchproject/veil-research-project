'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');const path=require('node:path');
const page=fs.readFileSync(path.join(__dirname,'v27.html'),'utf8');const server=fs.readFileSync(path.join(__dirname,'v27_server.py'),'utf8');
const cases=[
 ['HTML script parses',()=>new vm.Script(page.match(/<script>([\s\S]*?)<\/script>/)[1])],
 ['strict local-only CSP',()=>assert.match(page,/connect-src 'self'/)],
 ['casebook script same-origin only',()=>assert.match(page,/script src="casebook-core\.js"/)],
 ['no CDN or telemetry',()=>{assert.doesNotMatch(page,/(?:https?:\/\/[^'"\s]+|localStorage|sessionStorage|indexedDB|document\.cookie)/)}],
 ['explicit local-model opt-in',()=>assert.match(page,/mode!=='local'/)],
 ['explicit case note consent required',()=>assert.match(page,/case-share'\)\.checked/)],
 ['XSS safe DOM rendering',()=>{assert.match(page,/detail\.textContent/);assert.match(page,/case-entries'\);list\.replaceChildren/)}],
 ['source descriptions imported locally',()=>assert.match(page,/await file\.text\(\)/)],
 ['export stays client-side',()=>{assert.match(page,/new Blob/);assert.match(page,/URL\.createObjectURL/)}],
 ['no device control introduced',()=>assert.doesNotMatch(page,/(?:getUserMedia|navigator\.serial|navigator\.usb|websocket)/i)],
 ['UI has schema checklist',()=>['case-original','case-timestamp','case-alternative','case-corroboration'].forEach(id=>assert.match(page,new RegExp('id="'+id+'"')))],
 ['model input bound to bridge limit',()=>assert.match(page,/prompt\.length>800/)],
 ['separate v27 port and loopback',()=>{assert.match(server,/127\.0\.0\.1/);assert.match(server,/8767/)}],
 ['serves only required script',()=>assert.match(server,/self\.path == '\/casebook-core\.js'/)],
 ['core module contains no network use',()=>{const core=fs.readFileSync(path.join(__dirname,'casebook-core.js'),'utf8');assert.doesNotMatch(core,/(?:fetch\(|XMLHttpRequest|WebSocket|https?:\/\/)/)}]
];
for(const [name,fn] of cases){fn();console.log('PASS '+name)}
console.log(`${cases.length}/${cases.length} SIGNAL v27 static contract checks passed`);
