'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'memory.js'),'utf8');
function browserMemory(){const sandbox={};vm.runInNewContext(source,sandbox,{timeout:1000});return sandbox.SignalMemory.makeMemory;}
test('browser global export is available',()=>assert.equal(typeof browserMemory(),'function'));
test('temporary notes never become verified',()=>{const m=browserMemory()();m.add({id:'note_1',text:'Check again',source:'session'});assert.match(m.context()[0].attribution,/TEMPORARY/);assert.throws(()=>m.add({id:'note_2',text:'unverified',source:'session',verified:true}))});
test('remove and clear work without persistence',()=>{const m=browserMemory()();m.add({id:'note_1',text:'One',source:'session'});m.remove('note_1');assert.equal(m.list().length,0);m.add({id:'note_2',text:'Two',source:'session'});m.clear();assert.equal(m.list().length,0)});
test('memory instances remain separate',()=>{const make=browserMemory();const a=make(),b=make();a.add({id:'note_1',text:'Only A',source:'session'});assert.equal(b.list().length,0)});
test('page has wired local controls and no network client',()=>{const page=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');for(const id of ['memory-add','memory-clear','memory-list','memory-note'])assert.ok(page.includes('id="'+id+'"'));assert.match(page,/src="memory.js"/);assert.doesNotMatch(page,/\\bfetch\\s*\\(|XMLHttpRequest|sendBeacon|WebSocket/);});
