'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const V=require('./voice-core.js'),A=require('./assignments-core.js'),W=require('./audio-core.js'),D=require('./dashboard-core.js');
let count=0;function test(n,fn){fn();count++;console.log('PASS',n)}
function wav(samples,{rate=8000,channels=1}={}){const bytes=new ArrayBuffer(44+samples.length*2*channels),view=new DataView(bytes);for(const [at,str] of [[0,'RIFF'],[8,'WAVE'],[12,'fmt '],[36,'data']])for(let j=0;j<4;j++)view.setUint8(at+j,str.charCodeAt(j));view.setUint32(4,bytes.byteLength-8,true);view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,channels,true);view.setUint32(24,rate,true);view.setUint32(28,rate*channels*2,true);view.setUint16(32,channels*2,true);view.setUint16(34,16,true);view.setUint32(40,samples.length*channels*2,true);for(let i=0;i<samples.length;i++)for(let c=0;c<channels;c++)view.setInt16(44+i*channels*2+c*2,samples[i],true);return bytes}
// Voice
let v=V.create();test('v35 defaults idle and no microphone',()=>{assert.equal(v.state,'idle');assert.match(v.notice,/not connected/)});
test('v35 speech request',()=>{v=V.transition(v,'speak');assert.equal(v.state,'speaking')});
test('v35 barge in',()=>{v=V.transition(v,'barge-in');assert.equal(v.state,'listening')});
test('v35 transcribed text is explicitly typed',()=>{v=V.transition(v,'heard-text',' Operator typed this ');assert.equal(v.lastTranscript,'Operator typed this')});
test('v35 reset to idle',()=>{v=V.transition(v,'ready');assert.equal(v.state,'idle')});
test('v35 PTT simulated',()=>{v=V.transition(v,'press-to-talk');assert.equal(v.state,'listening')});
test('v35 invalid interrupt',()=>assert.throws(()=>V.transition(V.create(),'barge-in')));
test('v35 reject blank transcript',()=>assert.throws(()=>V.transition(v,'heard-text','  ')));
test('v35 reject arbitrary event',()=>assert.throws(()=>V.transition(v,'delete-files')));
test('v35 no microphone APIs',()=>assert.doesNotMatch(fs.readFileSync(path.join(__dirname,'voice-core.js'),'utf8'),/getUserMedia|SpeechRecognition|fetch\(/));
// Assignments
let task=A.create('review-mtc-notes','Review sample metadata','VEIL tester');test('v36 new task assigned',()=>assert.equal(task.state,'assigned'));
test('v36 no fabricated task type',()=>assert.throws(()=>A.create('control-panic-box','Open it','Operator')));
test('v36 only start moves to in progress',()=>{task=A.advance(task,'start');assert.equal(task.state,'in-progress')});
test('v36 cannot accept before review',()=>assert.throws(()=>A.advance(task,'accept',{reviewer:'Researcher',reason:'OK'})));
test('v36 submit manual findings',()=>{task=A.advance(task,'submit',{result:'Operator reviewed synthetic notes'});assert.equal(task.state,'awaiting-review')});
test('v36 cannot accept without named reviewer',()=>assert.throws(()=>A.advance(task,'accept',{reviewer:'',reason:'OK'})));
test('v36 human acceptance',()=>{task=A.advance(task,'accept',{reviewer:'VEIL researcher',reason:'Reviewed'});assert.equal(task.state,'accepted')});
test('v36 no second acceptance',()=>assert.throws(()=>A.advance(task,'accept',{reviewer:'Researcher',reason:'Again'})));
test('v36 rejection path',()=>{let t=A.create('triage-csv','Review synthetic values','Operator');t=A.advance(t,'start');t=A.advance(t,'submit',{result:'Human entered findings'});t=A.advance(t,'reject',{reviewer:'Reviewer',reason:'Insufficient controls'});assert.equal(t.state,'rejected')});
test('v36 report discloses manual nature',()=>assert.match(A.report([task]),/No autonomous execution/));
test('v36 rejects control chars',()=>assert.throws(()=>A.create('review-mtc-notes','Bad\ncontent','Operator')));
// WAV
const quiet=Array(4000).fill(0),pulse=Array.from({length:4000},(_,i)=>i>=1600&&i<2400?Math.round(Math.sin(i*.07)*15000):0);const data=wav(pulse);
test('v37 parses PCM16 mono',()=>{let x=W.parse(data);assert.equal(x.rate,8000);assert.equal(x.samples,4000);assert.equal(x.duration,.5)});
test('v37 silent WAV no events',()=>assert.equal(W.analyze(wav(quiet)).candidates.length,0));
test('v37 detects synthetic pulse',()=>{const result=W.analyze(data);assert.equal(result.candidates.length,1);assert.ok(result.candidates[0].startSec>=.19&&result.candidates[0].startSec<=.21)});
test('v37 stereo format supported',()=>assert.equal(W.analyze(wav(pulse,{channels:2})).channels,2));
test('v37 source bytes unchanged',()=>{const before=new Uint8Array(data).slice();W.analyze(data);assert.deepEqual(new Uint8Array(data),before)});
test('v37 report explicitly not EVP detection',()=>assert.match(W.report(W.analyze(data)),/no EVP\/paranormal conclusion/i));
test('v37 reject unknown container',()=>{let a=data.slice(0);new DataView(a).setUint8(0,0);assert.throws(()=>W.parse(a))});
test('v37 reject unsupported format',()=>{let a=data.slice(0);new DataView(a).setUint16(20,3,true);assert.throws(()=>W.parse(a))});
test('v37 reject truncated RIFF',()=>assert.throws(()=>W.parse(data.slice(0,30))));
test('v37 reject oversized',()=>assert.throws(()=>W.parse(new ArrayBuffer(25*1024*1024+1))));
test('v37 reject unsafe ratio',()=>assert.throws(()=>W.analyze(data,{ratio:1})));
test('v37 rejects non WAV buffer',()=>assert.throws(()=>W.parse('fake.wav')));
// Dashboard
const seed=D.validate(D.synthetic);
test('v38 fixtures explicitly synthetic',()=>assert.ok(seed.every(x=>x.simulated===true)));
test('v38 snapshots start with three',()=>assert.equal(D.snapshot(seed).total,3));
test('v38 simulated update',()=>{let a=D.simulate(seed,'SIM-MTC-01','attention');assert.equal(D.snapshot(a).attention,2)});
test('v38 fixture unaffected by update',()=>assert.equal(seed[0].status,'recording'));
test('v38 stale instrument flagged only as mock',()=>{const x=D.snapshot([{...seed[0],ageSeconds:121}]);assert.equal(x.attention,1);assert.equal(x.stations[0].stale,true)});
test('v38 rejects unlabeled live device',()=>assert.throws(()=>D.validate([{...seed[0],simulated:false}])));
test('v38 rejects rogue status',()=>assert.throws(()=>D.simulate(seed,'SIM-MTC-01','reset')));
test('v38 rejects unknown station',()=>assert.throws(()=>D.simulate(seed,'CAMERA-LIVE','ready')));
test('v38 report always says simulated',()=>assert.match(D.report(D.snapshot(seed)),/NOT LIVE/));
test('v38 no network or hardware APIs in model',()=>assert.doesNotMatch(fs.readFileSync(path.join(__dirname,'dashboard-core.js'),'utf8'),/(?:fetch\(|XMLHttpRequest|WebSocket|serial\.requestPort|bluetooth\.requestDevice)/));
console.log(`${count}/${count} SIGNAL v35-v38 deterministic checks passed`);
