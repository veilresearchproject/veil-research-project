'use strict';
const assert=require('node:assert/strict'),BLIND=require('./blind-core.js');let n=0;
function T(name,f){f();n++;console.log('PASS '+name)}
const book={schema:'signal-casebook',version:1,title:'Some experiment',entries:[
 {number:1,sourceType:'audio',sourceLabel:'MTC Recorder',observedAt:'2026-11-05T10:00:00Z',description:'Short metallic click heard in session'},
 {number:2,sourceType:'video',sourceLabel:'Camera B',observedAt:'2026-11-05T10:00:03Z',description:'Light brightened for a moment'},
 {number:3,sourceType:'witness',sourceLabel:'Visitor',observedAt:'',description:'Reported hearing a brief sound nearby'}]};
const gen=()=>BLIND.create(book,'abcdef12');
T('creates three anonymous items',()=>{const r=gen();assert.equal(r.packet.items.length,3);assert.equal(r.key.length,3)});
T('packet omits original type/source label/timestamp',()=>{const s=JSON.stringify(gen().packet);assert.doesNotMatch(s,/MTC Recorder|Camera B|Visitor|2026-11-05T10/)});
T('descriptions still visible and limitations explicit',()=>{const r=gen();assert.match(JSON.stringify(r.packet),/Short metallic click/);assert.match(r.packet.disclosure,/may nevertheless reveal/)});
T('deterministic order for seed',()=>assert.deepEqual(gen().packet.items,gen().packet.items));
T('different seed changes packet identity',()=>assert.notEqual(gen().packet.packetId,BLIND.create(book,'12345678').packet.packetId));
T('seed validation',()=>{for(const s of ['abcd','zzzzzzzz',null,1234])assert.throws(()=>BLIND.create(book,s))});
T('numbering integrity',()=>{const b=structuredClone(book);b.entries[0].number=3;assert.throws(()=>BLIND.create(b,'abcdef12'))});
T('too many entries',()=>{const b=structuredClone(book);b.entries=Array.from({length:31},(_,i)=>({...b.entries[0],number:i+1}));assert.throws(()=>BLIND.create(b,'abcdef12'))});
T('empty case blocked',()=>assert.throws(()=>BLIND.create({...book,entries:[]},'abcdef12')));
const decide=(packet)=>packet.items.map(x=>({alias:x.alias,category:'needs-more-data',reason:'Please inspect original recording and equipment logs'}));
T('finalize all complete human decisions',()=>{const p=gen().packet;const r=BLIND.finalize(p,decide(p),'Reviewer A','2026-11-05T11:00:00Z');assert.equal(r.decisions.length,3);assert.equal(r.identityUnverified,true)});
T('missing decisions rejected',()=>{const p=gen().packet;assert.throws(()=>BLIND.finalize(p,decide(p).slice(1),'Researcher'))});
T('invalid category rejected',()=>{const p=gen().packet,d=decide(p);d[1].category='paranormal confirmed';assert.throws(()=>BLIND.finalize(p,d,'Researcher'))});
T('too-short reviewer reason rejected',()=>{const p=gen().packet,d=decide(p);d[0].reason='yes';assert.throws(()=>BLIND.finalize(p,d,'Researcher'))});
T('alias mismatch rejected',()=>{const p=gen().packet,d=decide(p);d[0].alias='OBS-999';assert.throws(()=>BLIND.finalize(p,d,'Researcher'))});
T('unattributed review rejected',()=>{const p=gen().packet;assert.throws(()=>BLIND.finalize(p,decide(p),'X'))});
T('timestamp must carry timezone',()=>{const p=gen().packet;assert.throws(()=>BLIND.finalize(p,decide(p),'Researcher','2026-11-05T11:00:00'))});
T('cannot reveal without finalization',()=>{const r=gen();assert.throws(()=>BLIND.reveal(r.packet,r.key,null))});
T('cannot reveal different packet review',()=>{const r=gen(),p=BLIND.create(book,'12345678').packet;const d=BLIND.finalize(p,decide(p),'Researcher');assert.throws(()=>BLIND.reveal(r.packet,r.key,d))});
T('reveal maps review decisions back to metadata',()=>{const r=gen(),d=BLIND.finalize(r.packet,decide(r.packet),'Researcher');const reveal=BLIND.reveal(r.packet,r.key,d);assert.equal(reveal.items.length,3);assert.match(BLIND.report(reveal),/MTC Recorder/)});
T('review report remains cautious',()=>{const r=gen(),d=BLIND.finalize(r.packet,decide(r.packet),'Researcher');assert.match(BLIND.report(BLIND.reveal(r.packet,r.key,d)),/not a paranormal finding/)});
T('does not mutate original Casebook',()=>{const before=JSON.stringify(book);gen();assert.equal(JSON.stringify(book),before)});
T('reject packet alias tampering',()=>{const r=gen();r.packet.items[0].alias='HACK';assert.throws(()=>BLIND.validatePacket(r.packet))});
T('no external calls in core',()=>{const s=require('node:fs').readFileSync(__dirname+'/blind-core.js','utf8');assert.doesNotMatch(s,/fetch\(|XMLHttpRequest|WebSocket|localStorage|navigator\.mediaDevices/) });
console.log(n+'/'+n+' SIGNAL v31 blind review core tests passed');
