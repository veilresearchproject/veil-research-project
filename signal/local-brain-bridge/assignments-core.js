/* SIGNAL v36: human-reviewed assignment board. Does not execute tasks or access devices. */
(function(root){'use strict';
const KINDS=Object.freeze(['review-mtc-notes','triage-csv','compare-time-logs','prepare-method-review']);
const STATES=Object.freeze(['assigned','in-progress','awaiting-review','accepted','rejected']);
function fail(s){throw Error(s)}
function text(s,max,min=1){if(typeof s!=='string'||s.trim().length<min||s.length>max||/[\u0000-\u001f\u007f]/.test(s))fail('Invalid text');return s.trim()}
function create(kind,description,operator){if(!KINDS.includes(kind))fail('Task type not allowed');return Object.freeze({id:'SIG-TASK-'+Math.random().toString(36).slice(2,12),kind,description:text(description,400),operator:text(operator,80),state:'assigned',result:'',reviewer:'',decision:'',updatedAt:new Date().toISOString()})}
function advance(task,action,details={}){
 if(!task||!STATES.includes(task.state)||!KINDS.includes(task.kind))fail('Invalid assignment');
 const next={...task,updatedAt:new Date().toISOString()};
 if(action==='start'&&task.state==='assigned')next.state='in-progress';
 else if(action==='submit'&&task.state==='in-progress'){next.state='awaiting-review';next.result=text(details.result,1200)}
 else if(action==='accept'&&task.state==='awaiting-review'){next.state='accepted';next.reviewer=text(details.reviewer,80);next.decision=text(details.reason,400)}
 else if(action==='reject'&&task.state==='awaiting-review'){next.state='rejected';next.reviewer=text(details.reviewer,80);next.decision=text(details.reason,400)}
 else fail('Unauthorized assignment transition');
 return Object.freeze(next);
}
function report(tasks){if(!Array.isArray(tasks)||tasks.length>60)fail('Task list too long');return ['SIGNAL ASSIGNMENT BOARD — MANUAL WORKFLOW ONLY', ...tasks.map(t=>{
 if(!t||!STATES.includes(t.state))fail('Invalid task');return t.id+' | '+t.kind+' | '+t.state+' | '+t.description.slice(0,80)
}),'A status change is not proof that research was performed. No autonomous execution or equipment control.'].join('\n')}
const api=Object.freeze({KINDS,STATES,create,advance,report});if(typeof module!=='undefined'&&module.exports)module.exports=api;root.SIGNALAssignments=api;
})(typeof window!=='undefined'?window:globalThis);
