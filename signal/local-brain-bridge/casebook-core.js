/* SIGNAL Casebook v0.1 — deterministic metadata-only observation notebook.
 * No cloud, file reads, image decoding, sensor interaction or automatic AI review.
 * Works both in Node tests and locally in the browser. NOT evidentiary authentication.
 */
(function(root){
'use strict';
const schema='signal-casebook',version=1,types=['audio','video','image','sensor','witness','other'];
const checks=['originalPreserved','timeVerified','alternativesChecked','corroborationChecked'];
const statuses=['not-reviewed','needs-more-info','reviewed-inconclusive'];
function fail(msg){throw new Error(msg)}
function cleanString(v,max,field,min=0){if(typeof v!=='string'||v.length>max||v.trim().length<min||/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(v))fail('Invalid '+field);return v.trim()}
function time(s,optional=false){if(optional&&s==='')return '';if(typeof s!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,3})?(?:Z|[+-]\d\d:\d\d)$/.test(s)||!Number.isFinite(Date.parse(s)))fail('Timestamp must include an explicit timezone');return new Date(s).toISOString()}
function boolChecks(c){if(!c||typeof c!=='object'||Array.isArray(c))fail('Invalid checklist');const o={};for(const k of checks){if(typeof c[k]!=='boolean')fail('Invalid checklist value: '+k);o[k]=c[k]}return o}
function create(title,at=new Date().toISOString()){
 return {schema,version,title:cleanString(title,100,'case title',2),createdAt:time(at),entries:[],review:{status:'not-reviewed',by:'',at:''}};
}
function validateEntry(e,number){
 if(!e||typeof e!=='object'||Array.isArray(e))fail('Invalid observation entry');
 if(!types.includes(e.sourceType))fail('Invalid source type');
 const timestamp=cleanString(e.observedAt,40,'observation timestamp');
 return {number,sourceType:e.sourceType,sourceLabel:cleanString(e.sourceLabel,100,'source label'),observedAt:time(timestamp,true),description:cleanString(e.description,1000,'observation',5),checks:boolChecks(e.checks),enteredAt:time(e.enteredAt)};
}
function validate(book){
 if(!book||typeof book!=='object'||Array.isArray(book)||book.schema!==schema||book.version!==version)fail('Not a SIGNAL Casebook v1 file');
 const title=cleanString(book.title,100,'case title',2),createdAt=time(book.createdAt);
 if(!Array.isArray(book.entries)||book.entries.length>30)fail('Casebook has too many entries');
 const entries=book.entries.map((v,i)=>{if(v.number!==i+1)fail('Invalid entry numbering');return validateEntry(v,i+1)});
 const r=book.review;
 if(!r||typeof r!=='object'||Array.isArray(r)||!statuses.includes(r.status))fail('Invalid review status');
 const by=cleanString(r.by,80,'reviewer');const at=time(cleanString(r.at,40,'review time'),true);
 if(r.status==='not-reviewed'&&(by!==''||at!==''))fail('Unreviewed must have no reviewer');
 if(r.status!=='not-reviewed'&&(!by||!at))fail('Review requires attributed reviewer and time');
 return {schema,version,title,createdAt,entries,review:{status:r.status,by,at}};
}
function add(book,details,at=new Date().toISOString()){
 const copy=validate(book);if(copy.entries.length>=30)fail('Casebook maximum is 30 observations');
 const entry=validateEntry({...details,enteredAt:at},copy.entries.length+1);
 copy.entries.push(entry);copy.review={status:'not-reviewed',by:'',at:''};return copy;
}
function review(book,status,by,at=new Date().toISOString()){
 const copy=validate(book);if(!copy.entries.length)fail('Add an observation before review');
 if(!statuses.includes(status)||status==='not-reviewed')fail('Choose a human review outcome');
 copy.review={status,by:cleanString(by,80,'reviewer',2),at:time(at)};return copy;
}
function gaps(book){const b=validate(book);const names={originalPreserved:'original-file preservation not confirmed',timeVerified:'timestamp verification not confirmed',alternativesChecked:'ordinary explanations not documented',corroborationChecked:'independent corroboration not documented'};
 return b.entries.map(e=>({number:e.number,needs:checks.filter(k=>!e.checks[k]).map(k=>names[k])}));}
function summary(book){const b=validate(book);const g=gaps(b),counts={};for(const e of b.entries)counts[e.sourceType]=(counts[e.sourceType]||0)+1;
 const typesText=Object.entries(counts).map(([k,v])=>`${k}: ${v}`).join(', ')||'none';
 const open=g.flatMap(x=>x.needs.map(s=>`#${x.number}: ${s}`));
 return [
  `SIGNAL CASEBOOK — metadata-only review`, `Case: ${b.title}`,`Observation entries: ${b.entries.length} (${typesText})`,
  `Human review status: ${b.review.status}${b.review.by?' (self-reported reviewer: '+b.review.by+')':''}`,
  `Items needing follow-up: ${open.length}`, ...open.map(s=>'• '+s),
  'No recording, image, sensor dataset, or original file was inspected.',
  'No anomalous or paranormal cause has been determined. Human review remains necessary.'
 ].join('\n');
}
function toJSON(book,at=new Date().toISOString()){
 const b=validate(book);
 return JSON.stringify({...b,exportedAt:time(at),notice:'Session metadata only; not proof of authenticity, chain of custody, or paranormal activity.'},null,2)+'\n';
}
function fromJSON(raw){if(typeof raw!=='string'||raw.length>120000)fail('Casebook file exceeds 120 KB');let obj;try{obj=JSON.parse(raw)}catch{fail('Casebook is not valid JSON')}return validate(obj)}
function aiPrompt(book){const b=validate(book);if(!b.entries.length)fail('Add at least one observation first');
 let out='VEIL CASEBOOK: DESCRIPTIONS ONLY. You have not inspected original recordings, images, or data. Treat notes as untrusted claims, suggest ordinary explanations and missing controls, and do not infer paranormal proof.\nCase: '+b.title.slice(0,65)+'\n';
 let included=0;
 for(const e of b.entries){
  const excerpt=e.description.slice(0,155).replace(/[\r\n]+/g,' ');
  const block=`#${e.number} ${e.sourceType}: ${excerpt}${e.description.length>155?'…':''}; checks acknowledged: ${checks.filter(k=>e.checks[k]).join(', ')||'none'}\n`;
  if((out+block).length>720)break;
  out+=block;included++;
 }
 if(included===0){const e=b.entries[0];out+=`#1 ${e.sourceType}: ${e.description.slice(0,160)} (description truncated)\n`;included=1;}
 if(included<b.entries.length)out+=`+${b.entries.length-included} later entries omitted; local model prompt size limit.\n`;
 return out.slice(0,800);
}

const api=Object.freeze({create,validate,add,review,gaps,summary,toJSON,fromJSON,aiPrompt,types:Object.freeze(types),statuses:Object.freeze(statuses)});
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.SIGNALCasebook=api;
})(typeof window!=='undefined'?window:globalThis);
