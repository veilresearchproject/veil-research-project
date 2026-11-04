'use strict';
// Run with: node signal/pocket-voice-demo/test-voice.cjs
// No packages or network required.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script,'Inline SIGNAL script exists');
function harness({available=true,throwOnSpeak=false}={}){
  const handlers={};const elements=new Map();const utterances=[];
  function el(id){if(!elements.has(id))elements.set(id,{textContent:'',handlers:{},addEventListener(name,fn){this.handlers[name]=fn},click(){this.handlers.click?.()}});return elements.get(id)}
  const buttons=['intro','veil','evidence','humor'].map(key=>({dataset:{line:key},addEventListener(name,fn){this.click=fn}}));
  const document={hidden:false,getElementById:el,querySelectorAll:()=>buttons,addEventListener(name,fn){handlers['document:'+name]=fn}};
  const synth={cancelCount:0,cancel(){this.cancelCount++},speak(u){if(throwOnSpeak)throw Error('speech engine failed');utterances.push(u)},getVoices(){return [{name:'device voice'}]}};
  const window={addEventListener(name,fn){handlers['window:'+name]=fn}};
  if(available)window.speechSynthesis=synth;
  class SpeechSynthesisUtterance{constructor(text){this.text=text}}
  const context=vm.createContext({document,window,...(available?{SpeechSynthesisUtterance}:{})});
  vm.runInContext(script,context,{filename:'signal-voice-inline.js'});
  return {elements:el,buttons,handlers,utterances,synth,document,context};
}
const tests=[];
function test(name,fn){fn();tests.push(name)}
test('all four scripted buttons update text',()=>{const h=harness();for(const b of h.buttons){b.click();assert.ok(h.elements('speech').textContent.length>20)}});
test('speech requests use selected line',()=>{const h=harness();h.buttons[3].click();h.elements('speak').click();assert.match(h.utterances[0].text,/spreadsheets/)});
test('stop invalidates late onstart and onerror',()=>{const h=harness();h.elements('speak').click();const u=h.utterances[0];h.elements('stop').click();u.onstart();u.onerror();assert.equal(h.elements('voice-state').textContent,'Voice idle.')});
test('switching lines ignores stale speech completion',()=>{const h=harness();h.elements('speak').click();const u=h.utterances[0];h.buttons[1].click();u.onend();assert.equal(h.elements('voice-state').textContent,'Voice idle.');assert.match(h.elements('speech').textContent,/VEIL is/)});
test('old utterance cannot change newer speech status',()=>{const h=harness();h.elements('speak').click();const first=h.utterances[0];h.elements('speak').click();const second=h.utterances[1];second.onstart();first.onerror();assert.equal(h.elements('voice-state').textContent,'Speaking scripted line.')});
test('unavailable speech API fails visibly',()=>{const h=harness({available:false});h.elements('speak').click();assert.match(h.elements('voice-state').textContent,/unavailable/)});
test('speech engine exception fails visibly',()=>{const h=harness({throwOnSpeak:true});h.elements('speak').click();assert.match(h.elements('voice-state').textContent,/request failed/)});
test('voice support check does not claim offline voice',()=>{const h=harness();h.elements('check-voice').click();assert.match(h.elements('voice-state').textContent,/Offline voice availability is not verified/)});
test('page hide and background cancel speech',()=>{const h=harness();h.elements('speak').click();h.handlers['window:pagehide']();assert.equal(h.elements('voice-state').textContent,'Voice idle.');h.elements('speak').click();h.document.hidden=true;h.handlers['document:visibilitychange']();assert.equal(h.elements('voice-state').textContent,'Voice idle.')});
test('no app network access in CSP',()=>{assert.match(html,/connect-src 'none'/);assert.doesNotMatch(script,/\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon/)});
console.log(tests.length+' SIGNAL Pocket Voice tests passed');for(const name of tests)console.log('PASS',name);
