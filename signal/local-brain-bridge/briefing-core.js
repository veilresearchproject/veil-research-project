/* SIGNAL v43.1 — read-only, deterministic research briefing engine.
 * Only validated aggregate counts and file-relative candidate timing are exposed.
 * No raw notes, names, file content, saved memory, device control or AI calls.
 */
(function(root){'use strict';
const WF=root.SIGNALWorkflow||(typeof module!=='undefined'&&module.exports?require('./workflow-core.js'):null);
const DA=root.SIGNALDashboard||(typeof module!=='undefined'&&module.exports?require('./dashboard-core.js'):null);
const TA=root.SIGNALAssignments||(typeof module!=='undefined'&&module.exports?require('./assignments-core.js'):null);
if(!WF||!DA||!TA)throw Error('Briefing needs workflow, dashboard and assignment modules');
const INTENTS=Object.freeze(['overview','next','assignments','stations','limitations','help']);
function fail(message){throw new Error(message)}
function snapshot(workflow,tasks,stations){
 const book=workflow==null?null:WF.validate(workflow);
 if(!Array.isArray(tasks)||tasks.length>20)fail('Invalid task session');
 for(const t of tasks){if(!t||!TA.KINDS.includes(t.kind)||!TA.STATES.includes(t.state)||typeof t.description!=='string'||typeof t.operator!=='string')fail('Invalid assignment in session')}
 const board=DA.snapshot(stations);
 const candidates=book&&book.audio?book.audio.candidates:[];
 const unreviewed=candidates.filter(x=>x.status==='unreviewed');
 const next=unreviewed.length?{id:unreviewed[0].id,startSec:unreviewed[0].startSec,endSec:unreviewed[0].endSec}:null;
 const statusCounts={};for(const status of TA.STATES)statusCounts[status]=tasks.filter(t=>t.state===status).length;
 return Object.freeze({hasCase:!!book,hasAudio:!!(book&&book.audio),markerCount:candidates.length,
  reviewedCount:candidates.length-unreviewed.length,unreviewedCount:unreviewed.length,omitted:book&&book.audio?book.audio.omitted:0,
  next:next?Object.freeze(next):null,taskCount:tasks.length,taskStates:Object.freeze(statusCounts),
  simulatedTotal:board.total,simulatedAttention:board.attention});
}
function classify(input){
 if(typeof input!=='string'||input.length>120)return 'unsupported';
 const q=input.trim().toLowerCase().replace(/[?.!]+$/g,'').replace(/\s+/g,' ');
 if(/\b(arm|disarm|activate|deactivate|disable|reset|unlock|open|erase|delete|trigger|shut down|turn on|turn off|all clear|publish|send|execute|start recording|stop recording)\b/.test(q))return 'refused';
 const lookups={
  overview:['brief case','brief me','case status','status','summary','what is the case status'],
  next:['next marker','next review','what should i review next','find next unreviewed marker'],
  assignments:['assignments','task status','what assignments are pending','tasks'],
  stations:['stations','simulated stations','station status','command center status'],
  limitations:['limits','limitations','what can you verify','what do you actually know'],
  help:['help','commands','what can i ask']
 };
 for(const [intent,examples] of Object.entries(lookups))if(examples.includes(q))return intent;
 return 'unsupported';
}
function answer(intent,summary){
 if(!summary||typeof summary.hasCase!=='boolean'||!Number.isInteger(summary.markerCount)||!Number.isInteger(summary.taskCount)||!Number.isInteger(summary.simulatedTotal))fail('Invalid briefing snapshot');
 let message='',next=null;
 switch(intent){
 case 'overview':
  message=summary.hasCase?
   (summary.hasAudio?`There is an active case with ${summary.markerCount} amplitude-energy marker${summary.markerCount===1?'':'s'}. ${summary.reviewedCount} have human review notes and ${summary.unreviewedCount} remain unreviewed. ${summary.omitted} additional markers were omitted by the preview limit.`:'There is an active case but no WAV analysis is attached.'):
   'No active case is open. You can start one in the evidence workspace.';
  message+=` There are ${summary.taskCount} manual assignment${summary.taskCount===1?'':'s'}. No original recording was listened to by SIGNAL.`;
  break;
 case 'next':
  if(!summary.hasCase)message='Start a case before selecting a review marker.';
  else if(!summary.hasAudio)message='Attach a supported WAV to the case first. Only local amplitude screening is available.';
  else if(!summary.next)message='There are no unreviewed amplitude markers in the current preview queue. This does not mean the recording was fully reviewed.';
  else {next=summary.next.id;message=`Next unreviewed candidate: marker ${summary.next.id}, from ${summary.next.startSec.toFixed(3)} to ${summary.next.endSec.toFixed(3)} seconds relative to the WAV. A human must listen to the original and consider ordinary explanations.`}
  break;
 case 'assignments':
  message=`There are ${summary.taskCount} self-reported manual assignments: ${summary.taskStates.assigned} assigned, ${summary.taskStates['in-progress']} in progress, ${summary.taskStates['awaiting-review']} awaiting human review, ${summary.taskStates.accepted} accepted, and ${summary.taskStates.rejected} rejected. Assignment states are not proof that work was performed.`;
  break;
 case 'stations':
  message=`All ${summary.simulatedTotal} station entries are SYNTHETIC. ${summary.simulatedAttention} have simulated attention, offline, or stale indicators. No real MTC, Panic Box, camera, alarm or sensor connection is present.`;
  break;
 case 'limitations':
  message='I can report validated session counts, manually entered reviews, and locally computed amplitude candidates. I cannot hear or identify voices, verify causes, authenticate evidence, control equipment, or prove a paranormal event. Source files and human judgment remain essential.';
  break;
 case 'help':
  message='Try: brief me, next marker, assignments, simulated stations, or limitations. These are read-only requests; typing does not control instruments or submit research findings.';
  break;
 case 'refused':
  message='I cannot operate, reset, erase, publish, or clear any real or simulated equipment or evidence from a typed command. Use the explicit human-operated interface for authorized actions.';
  break;
 default:message='I cannot interpret that as a supported read-only briefing. Try: brief me, next marker, assignments, simulated stations, or limitations.';
 }
 return Object.freeze({text:message,focusMarker:next,intent:INTENTS.includes(intent)?intent:'unsupported'});
}
const api=Object.freeze({INTENTS,classify,snapshot,answer});
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.SIGNALBriefing=api;
})(typeof window!=='undefined'?window:globalThis);
