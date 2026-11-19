'use strict';
function classifyMemoryQuestion(input) {
  if (typeof input !== 'string' || input.length > 240) return {kind:'invalid'};
  const q=input.trim().toLowerCase().replace(/\s+/g,' ');
  if (!q) return {kind:'invalid'};
  if (/\b(delete|erase|clear|remove|forget|export|send|upload|share|verify|certify)\b/.test(q)) return {kind:'blocked'};
  if (/\b(remember|memory|notes?|recall)\b/.test(q) && /\b(what|which|show|tell|list|recall|remember|notes?|memory)\b/.test(q)) return {kind:'recall'};
  return {kind:'unknown'};
}
function answerMemoryQuestion(input, entries) {
  const kind=classifyMemoryQuestion(input).kind;
  if(kind==='invalid')return 'Please enter a short memory question.';
  if(kind==='blocked')return 'This question box is read-only. Use the separate memory controls to change notes.';
  if(kind!=='recall')return 'I can answer questions like: What did I ask you to remember?';
  if(!Array.isArray(entries))return 'Memory unavailable; no claims can be verified.';
  const notes=entries.filter(e=>e && e.source==='session' && e.verified===false && typeof e.text==='string');
  if(!notes.length)return 'I have no temporary unverified notes in this session.';
  return 'Temporary, unverified notes from this session (not established facts):\n'+notes.slice(0,64).map((e,i)=>(i+1)+'. '+e.text.slice(0,500)).join('\n');
}
if(typeof module!=='undefined'&&module.exports)module.exports={classifyMemoryQuestion,answerMemoryQuestion};
if(typeof globalThis!=='undefined')globalThis.SignalMemoryQuery=Object.freeze({classifyMemoryQuestion,answerMemoryQuestion});
