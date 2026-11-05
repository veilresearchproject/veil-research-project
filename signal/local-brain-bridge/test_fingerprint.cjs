'use strict';
const assert=require('node:assert/strict');const f=require('./fingerprint-core');
let n=0;async function test(name,fn){await fn();n++;console.log('PASS '+name)}
(async()=>{
await test('empty file known SHA256 vector',async()=>assert.equal(await f.bytes(new ArrayBuffer(0)),'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'));
await test('abc known SHA256 vector',async()=>assert.equal(await f.bytes(new TextEncoder().encode('abc').buffer),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'));
await test('accepts 64 hex reference',async()=>assert.equal(f.reference(' A'.padEnd(65,'A')), 'a'.repeat(64)));
await test('rejects malformed reference',async()=>assert.throws(()=>f.reference('sha256: abc')));
await test('reference match not case sensitive',async()=>assert.equal(f.compare('A'.repeat(64),'a'.repeat(64)),true));
await test('reference mismatch detectable',async()=>assert.equal(f.compare('f'.repeat(64),'0'.repeat(64)),false));
await test('rejects non-buffer',async()=>await assert.rejects(()=>f.bytes('abc')));
await test('rejects large buffer',async()=>await assert.rejects(()=>f.bytes(new ArrayBuffer(f.MAX_FILE_SIZE+1))));
await test('oversize file is rejected before read',async()=>{let read=false;await assert.rejects(()=>f.fingerprint({name:'bad.mov',size:f.MAX_FILE_SIZE+1,arrayBuffer:async()=>{read=true}}));assert.equal(read,false)});
await test('rejects changed file length',async()=>await assert.rejects(()=>f.fingerprint({name:'clip.wav',size:3,arrayBuffer:async()=>new ArrayBuffer(2)})));
await test('rejects control characters in names',async()=>await assert.rejects(()=>f.fingerprint({name:'evil\0clip.wav',size:0,arrayBuffer:async()=>new ArrayBuffer(0)})));
await test('hashes actual file-like bytes',async()=>{const b=new TextEncoder().encode('abc').buffer;const r=await f.fingerprint({name:'test.wav',size:3,arrayBuffer:async()=>b});assert.equal(r.sha256,'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');assert.equal(r.sizeBytes,3)});
await test('narrative note never claims file authenticity',async()=>{const note=f.note({fileName:'a.wav',sizeBytes:0,sha256:'0'.repeat(64)});assert.match(note,/not origin or authenticity/)});
await test('note rejects fabricated digest',async()=>assert.throws(()=>f.note({fileName:'bad',sizeBytes:4,sha256:'fake'})));
await test('no network or upload APIs in core',async()=>{const text=require('node:fs').readFileSync(__filename.replace('test_fingerprint.cjs','fingerprint-core.js'),'utf8');assert.doesNotMatch(text,/(?:fetch\(|XMLHttpRequest|WebSocket|https?:\/\/)/) });
console.log(`${n}/${n} SIGNAL fingerprint checks passed`)
})().catch(e=>{console.error(e);process.exitCode=1});
