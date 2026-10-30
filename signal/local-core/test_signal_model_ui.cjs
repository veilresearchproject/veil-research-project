// DOM interaction simulation; not a Windows hardware or visual browser test.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
class Element {
  constructor() { this.children=[];this.handlers={};this.dataset={};this.value='';this.textContent='';this.disabled=false;this.classList={toggle(){}}; }
  addEventListener(event, fn) {this.handlers[event]=fn;}
  append(...items) {this.children.push(...items);}
  appendChild(item) {this.append(item);}
  replaceChildren(...items) {this.children=[...items];}
  setAttribute() {}
  focus() {}
}
const html = fs.readFileSync(path.join(__dirname,'signal_face.html'),'utf8');
const elements = new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
const get = id=>{assert(elements.has(id), 'Missing HTML element '+id);return elements.get(id);};
get('model-select').disabled=true;get('model-select-apply').disabled=true;
const calls=[];
let permit=true, fail=false, changed=true;
const status={mode:'local-ollama',stream_supported:true,voice_enabled:false,speaking:false,mtc_loaded:false};
const sandbox={console,Image:class{},TextDecoder,AbortController,
  document:{getElementById:get,querySelector:()=>({content:'test-token'}),querySelectorAll:()=>[],createElement:()=>new Element()},
  window:{matchMedia:()=>({matches:true}),setInterval(){},setTimeout(){},clearTimeout(){},confirm:()=>permit},
  fetch:async(route,opts)=>{
    calls.push({route,opts});
    assert.equal(opts.headers['X-SIGNAL-Token'],'test-token');
    if(route==='/api/status') return {ok:true,json:async()=>status};
    assert.equal(route,'/api/models');
    if(fail)return {ok:false,status:422,json:async()=>({error:'Ollama offline'})};
    if(opts.method==='POST')return {ok:true,json:async()=>({changed,selected:'tiny:1b',status,message:'Model selected for this run.'})};
    return {ok:true,json:async()=>({selected:'old:3b',models:['old:3b','tiny:1b']})};
  }};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'signal_face.js'),'utf8'),sandbox);
(async()=>{
  await new Promise(setImmediate);
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
  console.log('PASS: model chooser opt-in, cancellation, reset, same-model preservation and unavailable inventory');
})().catch(e=>{console.error(e);process.exitCode=1;});
