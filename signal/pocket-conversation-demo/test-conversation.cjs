'use strict';
// Run with node test-conversation.cjs. No packages, network, microphone, or cloud.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script,'inline conversation script exists');
function harness({voice=true,failSpeak=false}={}){
  const elements=new Map(),callbacks={},utterances=[];
  function element(id){if(!elements.has(id)){
    const e={id,value:'',textContent:'',children:[],scrollTop:0,scrollHeight:100,className:'',handlers:{},
      addEventListener(type,fn){this.handlers[type]=fn},
      appendChild(child){this.children.push(child)},
      replaceChildren(){this.children=[]},focus(){this.focused=true}};
    elements.set(id,e);
  }return elements.get(id)}
  const suggestions=['Who are you?','What is VEIL?','How does the MTC work?','What counts as evidence?','Tell me a joke'].map(prompt=>({dataset:{prompt},handlers:{},addEventListener(type,fn){this.handlers[type]=fn},click(){this.handlers.click()}}));
  const document={hidden:false,getElementById:element,createElement:()=>({textContent:'',appendChild(child){(this.children??=[]).push(child)}}),querySelectorAll:()=>suggestions,addEventListener(name,fn){callbacks['document:'+name]=fn}};
  const synth={cancelCount:0,cancel(){this.cancelCount++},speak(u){if(failSpeak)throw Error('unavailable');utterances.push(u)}};
  const window={addEventListener(name,fn){callbacks['window:'+name]=fn}};
  if(voice)window.speechSynthesis=synth;
  class SpeechSynthesisUtterance{constructor(text){this.text=text}}
  const context=vm.createContext({window,document,...(voice?{SpeechSynthesisUtterance}:{} )});
  vm.runInContext(script,context,{filename:'signal-pocket-conversation.js'});
  const run=code=>vm.runInContext(code,context);
  return {elements:element,suggestions,callbacks,utterances,synth,document,run};
}
let passed=0;
function test(name,fn){fn();passed++;console.log('PASS',name)}
test('five demo prompt buttons produce replies',()=>{const h=harness();for(const b of h.suggestions){const before=h.elements('chat').children.length;b.click();assert.equal(h.elements('chat').children.length,before+2)}});
test('VEIL identity is accurate and research center is future',()=>{const h=harness();let s=h.run('replyTo("What is VEIL?")').reply;assert.match(s,/independent research/);s=h.run('replyTo("Tell me more about VEIL")').reply;assert.match(s,/no(t)? (yet )?have a physical research center|don.t yet have a physical research center/) });
test('MTC content includes prerecorded questions and independent review',()=>{const h=harness();const s=h.run('replyTo("How does MTC work?")').reply;assert.match(s,/prerecorded questions/);assert.match(s,/Independent/)});
test('evidence is not framed as paranormal proof',()=>{const h=harness();assert.match(h.run('replyTo("Does this prove a ghost?")').reply,/not automatic proof|not a conclusion/)});
test('explicit question preserves topic context',()=>{const h=harness();h.run('replyTo("What is the Panic Box?")');const r=h.run('replyTo("How does it work?")');assert.equal(r.topic,'followup');assert.match(r.reply,/authorized human operator/)});
test('MTC followups give MTC details rather than switching topics',()=>{const h=harness();h.run('replyTo("What is MTC?")');const r=h.run('replyTo("Tell me more")');assert.match(r.reply,/MTC/);assert.match(r.reply,/played questions/)});
test('VEIL followups correctly explain future facility',()=>{const h=harness();h.run('replyTo("What is VEIL?")');const r=h.run('replyTo("And what next?")');assert.match(r.reply,/future goal/)});
test('privacy and sentience claims are honest',()=>{const h=harness();assert.match(h.run('replyTo("Do you save private messages?")').reply,/doesn't record audio|No hidden microphone/);assert.match(h.run('replyTo("Are you sentient?")').reply,/No|not a conscious/)});
test('unknown question openly declines to invent facts',()=>{const h=harness();const r=h.run('replyTo("What is the moon made of?")');assert.equal(r.topic,'unknown');assert.match(r.reply,/don't have a verified|won't invent/)});
test('user input is text-only and cannot inject markup',()=>{const h=harness();h.run('answer("<script>alert(1)</script>")');const list=h.elements('chat').children;const u=list[list.length-2];assert.equal(u.children[1].textContent,'<script>alert(1)</script>')});
test('maximum typed length is capped',()=>{const h=harness();h.run(`answer('a'.repeat(800))`);const list=h.elements('chat').children;assert.equal(list[list.length-2].children[1].textContent.length,300)});
test('clear removes prior messages and resets short-term state',()=>{const h=harness();h.run('answer("Tell me a joke")');h.run('clearConversation()');assert.equal(h.elements('chat').children.length,1);assert.equal(h.run('lastReply'),'');assert.equal(h.run('lastTopic'),'greeting')});
test('voice is opt-in and starts only on speak button',()=>{const h=harness();h.run('answer("What is VEIL?")');assert.equal(h.utterances.length,0);h.elements('speak').handlers.click();assert.equal(h.utterances.length,1)});
test('late voice callbacks cannot overwrite new status',()=>{const h=harness();h.run('answer("Tell me a joke")');h.elements('speak').handlers.click();const u=h.utterances[0];h.elements('stop').handlers.click();u.onstart();u.onerror();assert.equal(h.elements('voice-state').textContent,'Voice idle.')});
test('backgrounding stops speech',()=>{const h=harness();h.run('answer("What is VEIL?")');h.elements('speak').handlers.click();h.document.hidden=true;h.callbacks['document:visibilitychange']();assert.equal(h.elements('voice-state').textContent,'Voice idle.')});
test('unavailable speech gracefully falls back to text',()=>{const h=harness({voice:false});h.run('answer("Hello")');h.elements('speak').handlers.click();assert.match(h.elements('voice-state').textContent,/unavailable/)});
test('speech engine errors do not break conversation',()=>{const h=harness({failSpeak:true});h.run('answer("Hi")');h.elements('speak').handlers.click();assert.match(h.elements('voice-state').textContent,/request failed/);assert.equal(h.run('replyTo("What is MTC?")').topic,'mtc')});
test('strict no-network CSP, no persistent storage or outbound APIs',()=>{assert.match(html,/connect-src 'none'/);assert.doesNotMatch(script,/\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon|localStorage|sessionStorage|indexedDB/)});
console.log(`${passed} SIGNAL Pocket Conversation tests passed`);