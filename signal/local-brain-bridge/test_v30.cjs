'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'v30.html'),'utf8');let tests=0;function test(n,fn){fn();tests++;console.log('PASS '+n)}
test('v30 page with geometric face',()=>{assert.match(html,/SIGNAL v30/);assert.match(html,/class="entity"/)});
test('clock core script before inline script',()=>assert.match(html,/<script src="clock-core\.js"><\/script><script>/));
test('clock calibration fields present',()=>['clock-label','clock-method','clock-offset','clock-uncertainty','clock-note'].forEach(x=>assert.match(html,new RegExp('id="'+x+'"'))));
test('clock workflow controls present',()=>['clock-save','clock-run','clock-export','clock-clear','clock-profiles','clock-report'].forEach(x=>assert.match(html,new RegExp('id="'+x+'"'))));
test('read-only local-first CSP',()=>{assert.match(html,/connect-src 'self'/);assert.doesNotMatch(html,/(?:http:\/\/(?!127\.0\.0\.1)|https:\/\/)(?:[^\s"']+)/)});
test('retains previous modules',()=>['casebook-core.js','fingerprint-core.js','correlation-core.js'].forEach(n=>assert.match(html,new RegExp(n.replace('.','\\.')))));
test('uses inert text output',()=>assert.match(html,/clock-report'\)\.textContent=clockText/));
test('no auto-save',()=>assert.doesNotMatch(html,/(?:localStorage|sessionStorage|indexedDB)/));
test('rejects blank offset instead of zero',()=>assert.match(html,/blank is not zero/));
test('stale export prevention',()=>assert.match(html,/clockLastInput!==clockFingerprint\(\)/));
test('inline JavaScript parses',()=>{const m=html.match(/<script>([\s\S]*)<\/script>/);assert(m);new vm.Script(m[1])});
test('backend localhost only',()=>{const py=fs.readFileSync(path.join(__dirname,'v30_server.py'),'utf8');assert.match(py,/127\.0\.0\.1/);assert.match(py,/8770/)});
console.log(tests+'/'+tests+' SIGNAL v30 contract tests passed');
