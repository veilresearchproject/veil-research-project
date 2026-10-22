'use strict';
/* SIGNAL local assignment protocol — finite-state, audited, human-reviewed.
 * No network calls, file I/O, AI inference or hardware control in this module.
 */
const ALLOWED=['audit_csv'];
function verify(b,msg){if(!b)throw Error(msg);}
function stamp(s){verify(typeof s==='string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(s)&&Number.isFinite(Date.parse(s)),'Invalid UTC timestamp');return s;}
function assign({id,kind,inputName,requestedBy,at,intervalSec=60,thresholdC=1.5}){
 verify(typeof id==='string'&&/^SIG-[a-z0-9-]{8,50}$/i.test(id),'Invalid ID');
 verify(ALLOWED.includes(kind),'Unapproved task type');
 verify(typeof inputName==='string'&&/^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\.csv$/.test(inputName)&&!inputName.includes('..'),'Unsafe CSV filename');
 verify(typeof requestedBy==='string'&&requestedBy.trim().length>=2&&requestedBy.length<=80,'Requester required');
 verify(Number.isFinite(intervalSec)&&intervalSec>=1&&intervalSec<=86400,'Invalid sampling interval');
 verify(Number.isFinite(thresholdC)&&thresholdC>0&&thresholdC<=100,'Invalid temperature threshold');
 return {schema:'signal.assignment.v0.1',id,kind,inputName,requestedBy,parameters:{intervalSec,thresholdC},
 status:'assigned',createdAt:stamp(at),result:null,events:[{at,actor:requestedBy,action:'ASSIGNED',detail:'Awaiting controlled execution'}]};
}
function move(task,status,actor,action,detail,at,result){
 const edges={assigned:['running','blocked'],running:['awaiting_review','blocked'],awaiting_review:['accepted','rejected'],accepted:[],rejected:[],blocked:[]};
 verify(edges[task.status]?.includes(status),'Invalid transition '+task.status+' → '+status);
 return {...task,status,result:result===undefined?task.result:result,
 events:[...task.events,{at:stamp(at),actor,action,detail:String(detail).slice(0,300)}]};
}
function start(task,at){return move(task,'running','SIGNAL local runner','STARTED','Allowlisted operation started',at);}
function finish(task,{csv,sha256,at,audit}){
 verify(task.status==='running'&&task.kind==='audit_csv','Task not executable');
 verify(typeof csv==='string'&&csv.length<=1000000,'CSV too large');
 verify(typeof sha256==='string'&&/^[a-f0-9]{64}$/.test(sha256),'File digest invalid');
 verify(audit&&typeof audit.analyze==='function'&&typeof audit.report==='function','Audit engine unavailable');
 const findings=audit.analyze(csv,task.parameters);
 const report=audit.report(findings,{source:'LOCAL FILE: '+task.inputName,sha256});
 const result={sourceFile:task.inputName,sourceSha256:sha256,findings,report,scientificConclusion:'none',reviewRequired:true};
 const detail=findings.validRows+' valid rows, '+findings.eventCount+' flags, '+findings.invalidRows+' invalid. Human review required.';
 return move(task,'awaiting_review','SIGNAL CSV audit engine','SUBMITTED_FOR_REVIEW',detail,at,result);
}
function block(task,{reason,at}){
 verify(['assigned','running'].includes(task.status),'Cannot block completed task');
 verify(typeof reason==='string'&&reason.trim().length>0,'Reason required');
 return move(task,'blocked','SIGNAL local runner','BLOCKED',reason,at);
}
function review(task,{approved,reviewer,reason='',at}){
 verify(task.status==='awaiting_review','Only submitted tasks may be reviewed');
 verify(typeof approved==='boolean','Explicit reviewer decision required');
 verify(typeof reviewer==='string'&&reviewer.trim().length>=2&&reviewer.length<=80,'Human reviewer required');
 return move(task,approved?'accepted':'rejected',reviewer,'HUMAN_REVIEW',
 (approved?'Accepted':'Rejected')+(reason?': '+String(reason).slice(0,200):''),at);
}
module.exports=Object.freeze({assign,start,finish,block,review});
