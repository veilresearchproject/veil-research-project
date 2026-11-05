/* SIGNAL v39–v42: bounded, metadata-only unified audio/case/review workflow.
 * In-memory only. Does not read audio itself, contact hardware or AI, or claim EVP.
 */
(function(root){'use strict';
const SCHEMA='signal-review-workflow',VERSION=1;
const OUTCOMES=Object.freeze(['unreviewed','listen','ordinary-possible','inconclusive']);
function fail(message){throw Error(message)}
function clean(s,max,min=0){if(typeof s!=='string'||s.length>max||s.trim().length<min||/[\u0000-\u001f\u007f]/.test(s))fail('Invalid field length or control character');return s.trim()}
function finite(n,min,max){if(typeof n!=='number'||!Number.isFinite(n)||n<min||n>max)fail('Invalid numeric field');return n}
function utc(s){if(typeof s!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,3})?Z$/.test(s)||!Number.isFinite(Date.parse(s)))fail('Invalid UTC date');return new Date(s).toISOString()}
function create(title,now=new Date().toISOString()){return {schema:SCHEMA,version:VERSION,title:clean(title,100,2),createdAt:utc(now),audio:null,reviewedAt:'',notes:[]}}
function hex(s){if(typeof s!=='string'||!(/^[0-9a-f]{64}$/.test(s)))fail('Invalid SHA-256');return s}
function validate(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw)||raw.schema!==SCHEMA||raw.version!==VERSION)fail('Unrecognized SIGNAL case schema');
 const title=clean(raw.title,100,2),createdAt=utc(raw.createdAt);
 if(!Array.isArray(raw.notes)||raw.notes.length>30)fail('Invalid note count');
 const notes=raw.notes.map(n=>({text:clean(n.text,800,5),by:clean(n.by,80,2),at:utc(n.at)}));
 if(raw.audio===null)return {schema:SCHEMA,version:VERSION,title,createdAt,audio:null,reviewedAt:'',notes};
 const a=raw.audio;
 if(!a||typeof a!=='object'||Array.isArray(a)||!Array.isArray(a.candidates)||a.candidates.length>80)fail('Invalid audio metadata');
 const obj={filename:clean(a.filename,160,1),sizeBytes:finite(a.sizeBytes,44,25*1024*1024),sha256:hex(a.sha256),rate:finite(a.rate,8000,192000),channels:finite(a.channels,1,2),durationSec:finite(a.durationSec,0,600),windowMs:finite(a.windowMs,20,1000),thresholdRms:finite(a.thresholdRms,0,1),omitted:finite(a.omitted,0,30000),candidates:[]};
 const ids=new Set();
 for(const c of a.candidates){
  if(!c||typeof c!=='object'||Array.isArray(c)||!Number.isInteger(c.id)||c.id<1||ids.has(c.id)||!OUTCOMES.includes(c.status))fail('Invalid candidate');ids.add(c.id);
  const startSec=finite(c.startSec,0,obj.durationSec+0.001),endSec=finite(c.endSec,startSec,obj.durationSec+0.001);
  const reviewer=clean(c.reviewer,80),reason=clean(c.reason,600),at=c.reviewedAt===''?'':utc(c.reviewedAt);
  if(c.status==='unreviewed'&&(reviewer||reason||at))fail('Unreviewed candidate cannot have a decision');
  if(c.status!=='unreviewed'&&(!reviewer||reviewer.length<2||reason.length<5||!at))fail('Review needs human attribution');
  obj.candidates.push({id:c.id,startSec,endSec,maxRms:finite(c.maxRms,0,1),peak:finite(c.peak,0,1),status:c.status,reviewer,reason,reviewedAt:at});
 }
 return {schema:SCHEMA,version:VERSION,title,createdAt,audio:obj,reviewedAt:'',notes};
}
function attach(raw,meta,analysis){
 const book=validate(raw);
 if(book.audio)fail('Existing audio already attached: start a new case to avoid silently replacing evidence');
 if(!meta||!analysis||!Array.isArray(analysis.candidates))fail('Missing analysis results');
 if(analysis.candidates.length>30000)fail('Too many intervals');
 const top=analysis.candidates.slice(0,80);
 book.audio={filename:clean(meta.filename,160,1),sizeBytes:meta.sizeBytes,sha256:hex(meta.sha256),rate:analysis.rate,channels:analysis.channels,durationSec:analysis.durationSec,windowMs:analysis.windowMs,thresholdRms:analysis.thresholdRms,omitted:Math.max(0,analysis.candidates.length-top.length),candidates:top.map((c,i)=>({id:i+1,startSec:c.startSec,endSec:c.endSec,maxRms:c.maxRms,peak:c.peak,status:'unreviewed',reviewer:'',reason:'',reviewedAt:''}))};
 return validate(book);
}
function review(raw,id,status,reviewer,reason,now=new Date().toISOString()){
 const book=validate(raw);if(!book.audio)fail('No audio attached');
 if(!Number.isInteger(id)||!OUTCOMES.includes(status)||status==='unreviewed')fail('Choose a review status');
 const c=book.audio.candidates.find(x=>x.id===id);if(!c)fail('Unknown candidate');
 if(c.status!=='unreviewed')fail('Do not silently overwrite an existing decision');
 c.status=status;c.reviewer=clean(reviewer,80,2);c.reason=clean(reason,600,5);c.reviewedAt=utc(now);
 return validate(book);
}
function note(raw,text,by,now=new Date().toISOString()){
 const b=validate(raw);if(b.notes.length>=30)fail('Maximum 30 notes');
 b.notes.push({text:clean(text,800,5),by:clean(by,80,2),at:utc(now)});return validate(b);
}
function taskDraft(raw,id){
 const b=validate(raw);if(!b.audio)fail('No audio attached');const c=b.audio.candidates.find(x=>x.id===id);
 if(!c||c.status==='unreviewed')fail('Review candidate before proposing a task');
 return `Manually listen to original ${b.audio.filename} at ${c.startSec.toFixed(3)}–${c.endSec.toFixed(3)} seconds; check question playback, ordinary noises and independent sources. Source SHA-256: ${b.audio.sha256.slice(0,16)}…; reviewer noted: ${c.reason.slice(0,110)}. Analysis only flagged amplitude; no speech identified.`.slice(0,400);
}
function report(raw){
 const b=validate(raw),a=b.audio;
 if(!a)return 'SIGNAL CASE WORKSPACE — NO AUDIO ATTACHED\n'+b.title+'\nNo files inspected, findings or research conclusions.';
 const reviewed=a.candidates.filter(x=>x.status!=='unreviewed').length;
 return [
  'SIGNAL LOCAL CASE REVIEW — DESCRIPTION & ENERGY LEVELS ONLY',
  'Case: '+b.title,'File label: '+a.filename,'File SHA-256: '+a.sha256,
  'Size bytes: '+a.sizeBytes,'Audio: '+a.channels+' channels, '+a.rate+' Hz; duration '+a.durationSec.toFixed(3)+' s',
  'Analysis window: '+a.windowMs+' ms; RMS threshold: '+a.thresholdRms.toFixed(5),
  'Amplitude markers retained: '+a.candidates.length+'; omitted: '+a.omitted+'; human-reviewed: '+reviewed,
  ...a.candidates.map(c=>`#${c.id} ${c.startSec.toFixed(3)}–${c.endSec.toFixed(3)}s; ${c.status}; ${c.status==='unreviewed'?'HUMAN REVIEW PENDING':c.reviewer+' (self-reported): '+c.reason}`),
  ...b.notes.map(n=>'Human note: '+n.text+' ('+n.by+', self-reported)'),
  'Times are FILE-RELATIVE, not synchronized to camera or MTC device clocks.',
  'No transcription, speech recognition, EVP identification, independent corroboration, forensic authenticity, paranormal conclusion, or instrument operation occurred.',
  'Operator must listen to the original and establish acquisition provenance and equipment timing independently.'
 ].join('\n');
}
const api=Object.freeze({SCHEMA,VERSION,OUTCOMES,create,validate,attach,review,note,taskDraft,report});
if(typeof module!=='undefined'&&module.exports)module.exports=api;root.SIGNALWorkflow=api;
})(typeof window!=='undefined'?window:globalThis);
