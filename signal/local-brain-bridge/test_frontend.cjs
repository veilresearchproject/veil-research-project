'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');const code=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];assert.ok(code);
function harness({server=false,ready=true,fail=false,failChat=false}={}){
 const elems=new Map(),handlers={},requests=[],buttons=[];
 function el(id){if(!elems.has(id)){const classes=new Set();elems.set(id,{id,textContent:'',value:'',children:[],className:'',disabled:false,scrollTop:0,scrollHeight:100,
 classList:{add(v){classes.add(v)},remove(v){classes.delete(v)},toggle(v,on){if(on)classes.add(v);else classes.delete(v)},contains(v){return classes.has(v)}},
 addEventListener(type,cb){this.handlers??={};this.handlers[type]=cb},append(...kids){this.children.push(...kids)},appendChild(kid){this.children.push(kid)},replaceChildren(){this.children=[]},focus(){this.focused=true}})}return elems.get(id)}
 const prompts=['Who are you?','What is VEIL?','How does MTC work?','What is good evidence?','Tell me a joke'].map(prompt=>({dataset:{prompt},addEventListener(type,fn){this.click=fn}}));
 const document={getElementById:el,querySelectorAll:()=>prompts,createElement:()=>({textContent:'',append(...kids){(this.children??=[]).push(...kids)}}),addEventListener(type,fn){handlers[type]=fn},hidden:false};
 let cancel=0,spoke=0;const speechSynthesis={cancel(){cancel++},speak(){spoke++}};
 const location=server?{protocol:'http:',hostname:'127.0.0.1'}:{protocol:'file:',hostname:''};
 const fetch=async (url,opts={})=>{requests.push({url,opts});if(fail)throw Error('unavailable');if(url==='/api/health')return {ok:true,json:async()=>({model_ready:ready,detail:ready?'ready':'missing'})};if(failChat)throw Error('model disconnected');return {ok:true,json:async()=>({reply:'Original recordings should be checked first.'})}};
 class AbortController{constructor(){this.signal={aborted:false}}abort(){this.signal.aborted=true}}
 class SpeechSynthesisUtterance{constructor(v){this.text=v}}
 const window={speechSynthesis,addEventListener(type,fn){handlers['window:'+type]=fn}};
 const sandbox=vm.createContext({window,document,location,fetch,AbortController,SpeechSynthesisUtterance});vm.runInContext(code,sandbox);
 return {elems:el,handlers,requests,prompts,run:s=>vm.runInContext(s,sandbox),speech:()=>({spoke,cancel})};
}
const tests=[];async function test(label,fn){await fn();tests.push(label);console.log('PASS',label)};
(async()=>{
 await test('scripted mode works without requests',async()=>{const h=harness();await h.run('answer("What is VEIL?")');assert.equal(h.requests.length,0);assert.match(h.elems('chat').children.at(-1).children[1].textContent,/VEIL/)});
 await test('unknown question does not invent scientific facts',async()=>{const h=harness();await h.run('answer("Where is Neptune?")');assert.match(h.elems('chat').children.at(-1).children[1].textContent,/no reliable answer|rehearsed vocabulary/)});
 await test('scripted mode displays evidence uncertainty',async()=>{const h=harness();await h.run('answer("Does evidence prove ghosts?")');assert.match(h.elems('chat').children.at(-1).children[1].textContent,/Unexplained|uncertainty/)});
 await test('scripted chat uses textContent not markup',async()=>{const h=harness();await h.run('answer("<img src=x onerror=alert(1)>")');assert.equal(h.elems('chat').children.at(-2).children[1].textContent,'<img src=x onerror=alert(1)>')});
 await test('check model on file cannot make requests',async()=>{const h=harness();await h.run('checkModel()');assert.equal(h.requests.length,0)});
 await test('enable local AI only if ready',async()=>{const h=harness({server:true,ready:false});await h.run('toggleLocal()');assert.equal(h.run('mode'),'scripted');assert.equal(h.requests.length,1)});
 await test('local AI explicitly activates and sends chat history',async()=>{const h=harness({server:true});await h.run('toggleLocal()');assert.equal(h.run('mode'),'local');await h.run('answer("What is VEIL?")');let r=h.requests.at(-1);assert.equal(r.url,'/api/chat');assert.equal(JSON.parse(r.opts.body).question,'What is VEIL?');assert.match(h.elems('chat').children.at(-1).children[1].textContent,/Original recordings/)});
 await test('second local request contains bounded context',async()=>{const h=harness({server:true});await h.run('toggleLocal()');await h.run('answer("Who are you?")');await h.run('answer("And why?")');const history=JSON.parse(h.requests.at(-1).opts.body).history;assert.equal(history.length,2);assert.equal(history[0].role,'user');assert.equal(history[1].role,'assistant')});
 await test('disable local AI resets conversational context',async()=>{const h=harness({server:true});await h.run('toggleLocal()');await h.run('answer("Hello")');await h.run('toggleLocal()');assert.equal(h.run('mode'),'scripted');assert.equal(h.run('history.length'),0)});
 await test('bridge failure never claims successful generated answer',async()=>{const h=harness({server:true,failChat:true});await h.run('toggleLocal()');assert.equal(h.run('mode'),'local');h.requests.length=0;await h.run('answer("What now?")');assert.equal(h.requests.at(-1).url,'/api/chat');assert.match(h.elems('chat').children.at(-1).children[1].textContent,/Local model could not answer/);assert.equal(h.run('history.length'),0)});
 await test('clear resets visible messages and history',async()=>{const h=harness();await h.run('answer("Hello")');h.run('clearChat()');assert.equal(h.elems('chat').children.length,1);assert.equal(h.run('lastReply'),'')});
 await test('voice is opt-in only',async()=>{const h=harness();await h.run('answer("What is VEIL?")');assert.equal(h.speech().spoke,0);h.run('speak()');assert.equal(h.speech().spoke,1)});
 await test('strict CSP contains only local origin connections',async()=>{assert.match(html,/connect-src 'self'/);assert.doesNotMatch(code, /fetch\(\s*['"]https?:\/\//);assert.doesNotMatch(code,/localStorage|sessionStorage|indexedDB|WebSocket|sendBeacon|XMLHttpRequest/)});
 await test('prompts produce responses',async()=>{const h=harness();for(let p of h.prompts)await p.click();assert.equal(h.elems('chat').children.length,11)});
 await test('startup does not try model or request microphone',async()=>{const h=harness({server:true});assert.equal(h.requests.length,0);assert.doesNotMatch(code,/getUserMedia|mediaDevices/)});
 console.log(`${tests.length}/${tests.length} SIGNAL frontend tests passed`);
})().catch(e=>{console.error(e);process.exitCode=1});