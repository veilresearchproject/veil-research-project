// DOM interaction simulation; not a Windows hardware or visual browser test.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
class Element {
  constructor() { this.children=[];this.handlers={};this.dataset={};this.value='';this.textContent='';this.disabled=false;this.classList={toggle(){}}; }
  addEventListener(event, fn) {this.handlers[event]=fn;}
  append(...items) {for(const item of items){item.parentElement=this;this.children.push(item);}}
  appendChild(item) {this.append(item);}
  replaceChildren(...items) {this.children=[...items];}
  setAttribute() {}
  focus() {}
  querySelector(selector) {return this.children.find(c=>c.className===selector.slice(1)) || null;}
}
const html = fs.readFileSync(path.join(__dirname,'signal_face.html'),'utf8');
const elements = new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
const get = id=>{assert(elements.has(id), 'Missing HTML element '+id);return elements.get(id);};
get('model-select').disabled=true;get('model-select-apply').disabled=true;
get('voice-select').disabled=true;get('voice-select-apply').disabled=true;
const calls=[];
let permit=true, fail=false, changed=true, micFailure=false;
let chatMode='failure', pendingChatResolve=null;
let voiceListFailure=false, voiceRejectSelection=false;
let noteContextFailure=false;
const intervals=[];
const status={mode:'local-ollama',version:'0.20',stream_supported:true,voice_enabled:false,speaking:false,mtc_loaded:false};
const sandbox={console,Image:class{},TextDecoder,AbortController,
  document:{getElementById:get,querySelector:()=>({content:'test-token'}),querySelectorAll:()=>[],createElement:()=>new Element()},
  window:{matchMedia:()=>({matches:true}),setInterval(fn){intervals.push(fn);},setTimeout(){},clearTimeout(){},confirm:()=>permit},
  fetch:async(route,opts)=>{
    calls.push({route,opts});
    assert.equal(opts.headers['X-SIGNAL-Token'],'test-token');
    if(route==='/api/status') return {ok:true,json:async()=>status};
    if(route==='/api/note-context') {
      if(noteContextFailure)return {ok:false,status:422,json:async()=>({error:'Notebook validation failed'})};
      status.notes_context_loaded=JSON.parse(opts.body).action==='include';
      status.notes_context_count=status.notes_context_loaded?2:0;status.notes_context_omitted=0;
      return {ok:true,json:async()=>({message:'Manual note context updated by operator.',status})};
    }
    if(route==='/api/chat') {
      if(chatMode==='network')throw Error('Connection interrupted');
      if(chatMode==='pending')return new Promise(resolve=>{pendingChatResolve=resolve;});
      if(chatMode==='failure')return {ok:false,status:422,json:async()=>({error:'Local model unavailable'})};
      return {ok:true,json:async()=>({reply:'A complete test answer.',mode:'local-ollama',status})};
    }
    if(route==='/api/chat/stream') {
      const chunks=[Buffer.from('{"event":"delta","text":"Partial reply"}\n'),
                    Buffer.from('{"event":"error","error":"Synthetic stream failure"}\n')];
      return {ok:true,body:{getReader:()=>({read:async()=>chunks.length?{value:chunks.shift(),done:false}:{done:true},cancel:async()=>{}})}};
    }
    if(route==='/api/listen/status') {
      if(micFailure)throw Error('Test connection interrupted');
      return {ok:true,json:async()=>({state:'listening'})};
    }
    if(route==='/api/listen') {
      const action=JSON.parse(opts.body).action;
      if(micFailure)throw Error('Test connection interrupted');
      return {ok:true,json:async()=>({state:action==='start'?'listening':'idle'})};
    }
    if(route==='/api/voice') {
      const data=JSON.parse(opts.body);
      if(data.action==='list') {
        if(voiceListFailure)throw Error('Windows voice inventory unavailable');
        return {ok:true,json:async()=>({voices:['Local David','Local Zira'],status})};
      }
      if(data.action==='select') {
        if(voiceRejectSelection)return {ok:false,status:422,json:async()=>({error:'Voice no longer installed'})};
        status.voice_name=data.name;
        return {ok:true,json:async()=>({reply:'Selected for this run. Test explicitly when ready.',status})};
      }
      return {ok:true,json:async()=>({reply:'Voice is off. Enable it explicitly to play a test.',status})};
    }
    if(route==='/api/session')return {ok:true,json:async()=>({history:[{role:'user',content:'Saved test question'},{role:'assistant',content:'Saved test answer'}],status,message:'Saved chat restored.'})};
    assert.equal(route,'/api/models');
    if(fail)return {ok:false,status:422,json:async()=>({error:'Ollama offline'})};
    if(opts.method==='POST')return {ok:true,json:async()=>({changed,selected:'tiny:1b',status,message:'Model selected for this run.'})};
    return {ok:true,json:async()=>({selected:'old:3b',models:['old:3b','tiny:1b']})};
  }};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'signal_face.js'),'utf8'),sandbox);
(async()=>{
  await new Promise(setImmediate);
  assert.equal(get('app-version').textContent,'alpha 0.20','Displayed release version follows local server status');
  assert.doesNotMatch(html,/Good morning/,'Greeting must work regardless of local clock');
  assert(!calls.some(c=>c.route==='/api/models'),'Inventory must be opt-in');
  await get('models-refresh').handlers.click();
  assert.equal(get('model-select').children.length,2);
  assert.equal(get('model-select').disabled,false);
  get('model-select').value='tiny:1b';
  permit=false;
  const before=calls.length;
  await get('model-select-apply').handlers.click();
  assert.equal(calls.length,before,'Cancel must not send a selection request');
  permit=true;
  get('messages').append(new Element());get('scanner-list').append(new Element());get('review-list').append(new Element());
  await get('model-select-apply').handlers.click();
  const sent=calls.at(-1);
  assert.deepEqual(JSON.parse(sent.opts.body),{model:'tiny:1b',confirm_reset:true});
  assert.equal(get('messages').children.length,1);
  assert.equal(get('scanner-list').children.length,0);
  assert.equal(get('review-list').children.length,0);
  assert.match(get('model-check-results').textContent,/not been tested/);
  changed=false;
  await get('model-select-apply').handlers.click();
  assert.equal(get('messages').children.length,1,'Unchanged model preserves displayed chat');
  fail=true;
  await get('models-refresh').handlers.click();
  assert.equal(get('model-select').disabled,true);
  assert.equal(get('model-select-apply').disabled,true);
  assert.match(get('model-selection-state').textContent,/offline/);
  await get('mic-button').handlers.click();
  assert.equal(get('mic-button').textContent,'■ Stop listening');
  micFailure=true;
  await get('mic-button').handlers.click();
  assert.equal(get('mic-button').textContent,'■ Stop listening','Failed stop must retain active mic controls');
  assert.match(get('mic-note').textContent,/Could not confirm/);
  await intervals.find(fn=>fn.name==='pollListen')();
  assert.equal(get('mic-button').textContent,'■ Stop listening');
  assert.match(get('mic-note').textContent,/may still be listening/);
  micFailure=false;
  await get('mic-button').handlers.click();
  assert.equal(get('mic-button').textContent,'🎙 Start listening');
  assert.match(get('mic-note').textContent,/Microphone OFF/);
  await get('voice-test').handlers.click();
  assert.equal(calls.at(-1).route,'/api/voice');
  assert.equal(JSON.parse(calls.at(-1).opts.body).action,'test');
  assert(!calls.some(c=>c.route==='/api/chat'),'Microphone simulation must not auto-submit chat');
  status.generating=true;
  status.request_progress={kind:'reply',elapsed_ms:12600,stop_requested:false};
  await intervals.find(fn=>fn.name==='refresh')();
  assert.equal(get('send').disabled,true);
  assert.equal(get('question').disabled,true);
  assert.match(get('reply-status').textContent,/12 seconds/);
  status.request_progress.stop_requested=true;
  await intervals.find(fn=>fn.name==='refresh')();
  assert.match(get('reply-status').textContent,/cleanup is still running/);
  assert.equal(get('send').disabled,true);
  status.generating=false;status.request_progress=null;
  await intervals.find(fn=>fn.name==='refresh')();
  assert.equal(get('send').disabled,false);
  assert.equal(get('question').disabled,false);
  assert.match(get('reply-status').textContent,/No local model request/);
  status.stream_supported=false;
  await intervals.find(fn=>fn.name==='refresh')();
  const submit=()=>get('chat-form').handlers.submit({preventDefault(){}});
  const chatCalls=()=>calls.filter(c=>c.route==='/api/chat'||c.route==='/api/chat/stream').length;
  get('question').value='Keep this question after failure';
  const initialCalls=chatCalls();
  await submit();
  assert.equal(chatCalls(),initialCalls+1,'Failure must not automatically retry');
  assert.equal(get('question').value,'Keep this question after failure');
  assert.equal(get('draft-recovery').hidden,false);
  get('question').value='A newer unsent question';permit=false;
  await get('draft-restore').handlers.click();
  assert.equal(get('question').value,'A newer unsent question','Cancel preserves the newer unsent text');
  permit=true;
  await get('draft-restore').handlers.click();
  assert.equal(get('question').value,'Keep this question after failure');
  assert.equal(chatCalls(),initialCalls+1,'Restoring must never send');
  chatMode='success';
  await submit();
  assert.equal(get('question').value,'');
  const beforeNotesChat=chatCalls();
  await get('note-context-include').handlers.click();
  assert.equal(status.notes_context_loaded,true);
  assert.match(get('note-context-state').textContent,/2 manual notes included as unverified/);
  assert.equal(chatCalls(),beforeNotesChat,'Including notes must not query the model');
  await get('note-context-clear').handlers.click();
  assert.equal(status.notes_context_loaded,false);
  assert.match(get('note-context-state').textContent,/not included/);
  await get('note-context-include').handlers.click();
  noteContextFailure=true;
  await get('note-context-include').handlers.click();
  assert.equal(status.notes_context_loaded,true);
  assert.match(get('note-context-state').textContent,/unchanged/);
  const voiceTestsBefore=calls.filter(c=>c.route==='/api/voice'&&JSON.parse(c.opts.body).action==='test').length;
  assert(!calls.some(c=>c.route==='/api/voice'&&JSON.parse(c.opts.body).action==='list'),'Voice inventory must be opt-in');
  await get('voices-refresh').handlers.click();
  assert.equal(get('voice-select').children.length,3);
  assert.equal(get('voice-select').disabled,false);
  get('voice-select').value='Local Zira';
  await get('voice-select-apply').handlers.click();
  assert.equal(status.voice_name,'Local Zira');
  assert.equal(status.voice_enabled,false);
  assert.match(get('voice-selection-state').textContent,/Local Zira/);
  assert.equal(calls.filter(c=>c.route==='/api/voice'&&JSON.parse(c.opts.body).action==='test').length,voiceTestsBefore,'Selecting must not play a sample');
  get('voice-select').value='';
  await get('voice-select-apply').handlers.click();
  assert.equal(status.voice_name,null);
  assert.match(get('voice-selection-state').textContent,/system default/);
  get('voice-select').value='Local Zira';await get('voice-select-apply').handlers.click();
  voiceRejectSelection=true;
  get('voice-select').value='Local David';await get('voice-select-apply').handlers.click();
  assert.equal(status.voice_name,'Local Zira');
  assert.match(get('voice-selection-state').textContent,/unchanged/);
  voiceListFailure=true;
  await get('voices-refresh').handlers.click();
  assert.equal(get('voice-select').disabled,true);
  assert.equal(get('voice-select-apply').disabled,true);
  assert.equal(status.voice_name,'Local Zira');
  assert.match(get('voice-selection-state').textContent,/unavailable/);
  assert.equal(get('draft-recovery').hidden,true,'Successful manual retry clears the matching recovery copy');
  chatMode='network';get('question').value='A question interrupted by disconnection';
  await submit();
  assert.equal(get('question').value,'A question interrupted by disconnection');
  await get('draft-dismiss').handlers.click();
  assert.equal(get('draft-recovery').hidden,true);
  assert.equal(get('question').value,'A question interrupted by disconnection','Dismiss leaves the editor untouched');
  chatMode='pending';get('question').value='Only send this once';
  const pending=submit();
  const during=chatCalls();
  await submit();
  assert.equal(chatCalls(),during,'A second click while pending must not submit twice');
  get('question').value='New text selected while the old request was pending';
  pendingChatResolve({ok:true,json:async()=>({reply:'A completed response.',mode:'local-ollama',status})});
  await pending;
  assert.equal(get('question').value,'New text selected while the old request was pending','Success must not erase newer editor text');
  status.stream_supported=true;
  await intervals.find(fn=>fn.name==='refresh')();
  get('question').value='Keep this interrupted stream question';
  const beforeStream=chatCalls();await submit();
  assert.equal(chatCalls(),beforeStream+1);
  assert.equal(get('question').value,'Keep this interrupted stream question');
  assert.equal(get('draft-recovery').hidden,false);
  const lastPartial=get('messages').children.filter(el=>el.className==='message signal').at(-1);
  assert.match(lastPartial.querySelector('.message-foot').textContent,/INCOMPLETE/);
  status.generating=true;status.request_progress={kind:'reply',elapsed_ms:10,stop_requested:true};
  await intervals.find(fn=>fn.name==='refresh')();
  get('question').value='Do not replace this while busy';
  await get('draft-restore').handlers.click();
  assert.equal(get('question').value,'Do not replace this while busy');
  status.generating=false;status.request_progress=null;
  await intervals.find(fn=>fn.name==='refresh')();
  fail=false;changed=true;
  await get('models-refresh').handlers.click();
  get('model-select').value='tiny:1b';
  await get('model-select-apply').handlers.click();
  assert.equal(get('draft-recovery').hidden,true,'A confirmed model reset clears recovery context');
  assert.equal(get('question').value,'');
  get('question').value='Another interrupted question';
  await submit();
  assert.equal(get('draft-recovery').hidden,false);
  permit=false;
  await get('session-restore').handlers.click();
  assert.equal(get('draft-recovery').hidden,false,'Cancelled restore preserves the draft');
  permit=true;
  await get('session-restore').handlers.click();
  assert.equal(get('draft-recovery').hidden,true,'Confirmed chat restore clears the old recovery context');
  assert.equal(get('question').value,'');
  console.log('PASS: model chooser opt-in, cancellation, reset, same-model preservation and unavailable inventory');
  console.log('PASS: failed microphone stop/status remain visibly uncertain, retry succeeds, voice test is explicit');
  console.log('PASS: elapsed waiting status, post-cancel busy controls and return to ready');
  console.log('PASS: failed/network/partial-stream question recovery, manual restore, double-click guard, newer-text preservation and confirmed model reset');
  console.log('PASS: opt-in installed voice list, explicit selection/default, no auto sample and selection/inventory failure preservation');
  console.log('PASS: explicit manual-note context include/clear, attribution labels, no model call and validation failure preservation');
})().catch(e=>{console.error(e);process.exitCode=1;});
