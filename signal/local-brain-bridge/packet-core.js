/* SIGNAL v43: deliberate local JSON session export/import with SHA-256 check.
 * A digest detects changed bytes but is NOT authentication, signature, chain of custody or proof.
 */
(function(root){'use strict';
const WF=root.SIGNALWorkflow || (typeof module!=='undefined'&&module.exports?require('./workflow-core.js'):null);
const DASH=root.SIGNALDashboard || (typeof module!=='undefined'&&module.exports?require('./dashboard-core.js'):null);
const TASKS=root.SIGNALAssignments || (typeof module!=='undefined'&&module.exports?require('./assignments-core.js'):null);
function fail(s){throw Error(s)}
function checkTasks(raw){if(!Array.isArray(raw)||raw.length>20)fail('Invalid task count');const ids=new Set();return raw.map(t=>{
 if(!t||typeof t!=='object'||typeof t.id!=='string'||!/^SIG-TASK-[a-z0-9]{1,12}$/.test(t.id)||ids.has(t.id)||!TASKS.KINDS.includes(t.kind)||!TASKS.STATES.includes(t.state))fail('Invalid assignment');ids.add(t.id);
 const clean=(v,max)=>{if(typeof v!=='string'||v.length>max||/[\u0000-\u001f\u007f]/.test(v))fail('Invalid task text');return v};
 const o={id:t.id,kind:t.kind,description:clean(t.description,400),operator:clean(t.operator,80),state:t.state,result:clean(t.result,1200),reviewer:clean(t.reviewer,80),decision:clean(t.decision,400),updatedAt:clean(t.updatedAt,50)};
 if(!o.description||!o.operator||!Number.isFinite(Date.parse(o.updatedAt)))fail('Incomplete assignment');
 if(o.state==='awaiting-review'&&!o.result)fail('Missing submitted result');
 if(['accepted','rejected'].includes(o.state)&&(!o.result||!o.reviewer||!o.decision))fail('Missing review decision');
 return o;
})}
function snapshot(workflow,tasks,stations){return {workflow:WF.validate(workflow),tasks:checkTasks(tasks),stations:DASH.validate(stations)}}
const subtle=()=>{const crypto=root.crypto||(typeof require!=='undefined'?require('node:crypto').webcrypto:null);if(!crypto||!crypto.subtle)fail('Local SHA-256 WebCrypto unavailable');return crypto.subtle};
async function sha256(utf8){const encoder=new TextEncoder();const bytes=encoder.encode(utf8);const buf=await subtle().digest('SHA-256',bytes);return [...new Uint8Array(buf)].map(v=>v.toString(16).padStart(2,'0')).join('')}
async function exportJSON(workflow,tasks,stations,now=new Date().toISOString()){
 const payload=snapshot(workflow,tasks,stations);if(!Number.isFinite(Date.parse(now)))fail('Invalid export time');
 const digest=await sha256(JSON.stringify(payload));
 return JSON.stringify({schema:'signal-session-handoff',version:1,exportedAt:now,warning:'Operator-selected notes only. Not a forensic chain-of-custody or signed report; self-reported human identities. Simulated station data is not live.',integrity:{algorithm:'SHA-256',hex:digest},payload},null,2)+'\n';
}
async function importJSON(raw){
 if(typeof raw!=='string'||raw.length>250000)fail('Handoff exceeds 250 KB');let obj;
 try{obj=JSON.parse(raw)}catch(_){fail('Invalid JSON')}
 if(!obj||obj.schema!=='signal-session-handoff'||obj.version!==1||!obj.integrity||obj.integrity.algorithm!=='SHA-256'||typeof obj.integrity.hex!=='string'||!/^[0-9a-f]{64}$/.test(obj.integrity.hex)||!obj.payload)fail('Unsupported or invalid handoff');
 const actual=await sha256(JSON.stringify(obj.payload));if(actual!==obj.integrity.hex)fail('Handoff digest mismatch: contents may have changed');
 return snapshot(obj.payload.workflow,obj.payload.tasks,obj.payload.stations);
}
const api=Object.freeze({snapshot,sha256,exportJSON,importJSON});if(typeof module!=='undefined'&&module.exports)module.exports=api;root.SIGNALPacket=api;
})(typeof window!=='undefined'?window:globalThis);
