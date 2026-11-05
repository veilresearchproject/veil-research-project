'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'v29.html'),'utf8'),svr=fs.readFileSync(path.join(__dirname,'v29_server.py'),'utf8');
const cases=[
 ['JS parses',()=>new vm.Script(html.match(/<script>([\s\S]*?)<\/script>/)[1])],
 ['v29 branding',()=>assert.match(html,/SIGNAL <span class="small">v29/)],
 ['connect only to localhost',()=>assert.match(html,/connect-src 'self'/)],
 ['correlation core on same origin',()=>assert.match(html,/src="correlation-core\.js"/)],
 ['casebook and fingerprint preserved',()=>{assert.match(html,/src="casebook-core\.js"/);assert.match(html,/src="fingerprint-core\.js"/)}],
 ['user chooses window',()=>assert.match(html,/id="cor-window" min="0" max="300" step="1" value="5"/)],
 ['explicit analysis button',()=>assert.match(html,/cor-run'\)\.addEventListener\('click'/)],
 ['uses validated casebook from session',()=>assert.match(html,/COR\.analyze\(caseBook,/)],
 ['result rendered as safe text',()=>assert.match(html,/cor-report'\)\.textContent=correlationReport/)],
 ['report requires explicit download click',()=>assert.match(html,/cor-export'\)\.addEventListener\('click'/)],
 ['stale result export refused',()=>assert.match(html,/JSON\.stringify\(caseBook\)!==correlationCaseSnapshot/)],
 ['no network/device access introduced',()=>assert.doesNotMatch(html,/(?:XMLHttpRequest|navigator\.serial|navigator\.usb|new WebSocket)/)],
 ['preview uses separate loopback port',()=>{assert.match(svr,/127\.0\.0\.1/);assert.match(svr,/8769/)}],
 ['server exposes limited correlation module',()=>assert.match(svr,/'correlation-core\.js'/)],
 ['no cookie or auto note persistence',()=>assert.doesNotMatch(html,/(?:localStorage|sessionStorage|indexedDB|document\.cookie)/)]
];
for(const [name,fn] of cases){fn();console.log('PASS '+name)}console.log(`${cases.length}/${cases.length} SIGNAL v29 contract checks passed`);
