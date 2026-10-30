'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync(require('node:path').join(__dirname,'index.html'),'utf8');
const code=html.match(/<script id="logic">([\s\S]*?)<\/script>/);
assert.ok(code,'inline application script present');
const ctx={};vm.createContext(ctx);vm.runInContext(code[1],ctx);
const validate=ctx.validateReport,group=ctx.groupCandidates,stamp=ctx.timestamp;
function fixture(){return {tool:'VEIL MTC local audio review',version:'0.3',session_id:'test-001',duration_seconds:600,segments:1,warnings:[],candidates:[
 {start:31.5,end:33,score:9.5,reason:'synthetic',phase:'test'},
 {start:32,end:34,score:11,reason:'synthetic',phase:'test'},
 {start:420,end:421,score:12,reason:'synthetic',phase:'test'}]};}
function reject(change){const d=fixture();change(d);assert.throws(()=>validate(d));}
test('groups overlaps, retains source indices, and leaves source unchanged',()=>{
 const source=fixture(),before=JSON.stringify(source);
 const r=validate(source),groups=group(r.candidates);
 assert.equal(groups.length,2);assert.deepEqual(Array.from(groups[0].indices),[1,2]);
 assert.equal(groups[0].start,31.5);assert.equal(groups[0].end,34);assert.equal(groups[0].score,11);
 assert.equal(JSON.stringify(source),before);
});
test('nearby but distinct flags remain separate',()=>{const d=fixture();d.candidates[1].start=33.4;d.candidates[1].end=34;assert.equal(group(validate(d).candidates).length,3);});
test('empty candidate set is valid and shows zero windows',()=>{const d=fixture();d.candidates=[];assert.equal(group(validate(d).candidates).length,0);});
test('rejects invalid tool, version, duration, and segments',()=>{
 reject(d=>d.tool='fake');reject(d=>d.version='99');reject(d=>d.duration_seconds=0);
 reject(d=>d.duration_seconds=172801);reject(d=>d.segments=0);reject(d=>d.segments=1.5);
 reject(d=>d.session_id='bad\ncontrol');reject(d=>d.session_id='');
});
test('rejects invalid and excessive candidates',()=>{
 reject(d=>d.candidates[0].start=true);reject(d=>d.candidates[0].start=-1);
 reject(d=>d.candidates[0].end=999);reject(d=>d.candidates[0].score=Infinity);
 reject(d=>d.candidates[0].end=d.candidates[0].start);
 reject(d=>d.candidates=Array(201).fill(d.candidates[0]));
 reject(d=>d.candidates[0].reason='x'.repeat(101));
 reject(d=>d.candidates[0].phase='x\n');
});
test('rejects malformed warning entries',()=>{
 reject(d=>d.warnings=Array(26).fill('x'));reject(d=>d.warnings=[42]);
});
test('timestamps are readable and stable',()=>{
 assert.equal(stamp(31.5),'00:31.500');assert.equal(stamp(420),'07:00.000');
});
test('page has no network dependency and labels synthetic/unverified evidence',()=>{
 assert.match(html,/connect-src 'none'/);assert.match(html,/SYNTHETIC DEMO/);
 assert.match(html,/UNVERIFIED SCANNER OUTPUT/);assert.match(html,/No third-party scripts/);
 assert.doesNotMatch(html,/\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\b|<script\s+src=/);
 assert.doesNotMatch(html,/\.innerHTML\s*=/);
});
