/* SIGNAL v38: entirely simulated multi-site monitoring. No devices, network or actions. */
(function(root){'use strict';
const statuses=Object.freeze(['ready','recording','attention','offline']);const kinds=Object.freeze(['MTC','Panic Box','Camera']);
const synthetic=Object.freeze([
 {id:'SIM-MTC-01',kind:'MTC',location:'Bench rehearsal',status:'recording',ageSeconds:0,simulated:true},
 {id:'SIM-PANIC-01',kind:'Panic Box',location:'Demo room',status:'ready',ageSeconds:0,simulated:true},
 {id:'SIM-CAMERA-01',kind:'Camera',location:'Demo corridor',status:'attention',ageSeconds:0,simulated:true}
]);
function validate(rows){if(!Array.isArray(rows)||rows.length>24)throw Error('Invalid station list');return rows.map(x=>{
 if(!x||x.simulated!==true||!kinds.includes(x.kind)||!statuses.includes(x.status)||typeof x.id!=='string'||!/^SIM-[A-Z0-9-]{1,35}$/.test(x.id)||typeof x.location!=='string'||x.location.length>80||!Number.isFinite(x.ageSeconds)||x.ageSeconds<0)throw Error('Simulated stations only');return {...x};
 })}
function snapshot(rows){const stations=validate(rows);return Object.freeze({simulated:true,total:stations.length,attention:stations.filter(x=>x.status==='attention'||x.status==='offline'||x.ageSeconds>=120).length,stations:stations.map(x=>({...x,stale:x.ageSeconds>=120}))})}
function simulate(rows,id,status){if(!statuses.includes(status))throw Error('Invalid simulated status');const stations=validate(rows);if(!stations.some(x=>x.id===id))throw Error('Unknown simulated station');return stations.map(x=>x.id===id?{...x,status,ageSeconds:0}:x)}
function report(s){if(!s||s.simulated!==true||!Array.isArray(s.stations))throw Error('Invalid simulated snapshot');return ['SIMULATED VEIL COMMAND CENTER — NOT LIVE',...s.stations.map(x=>x.id+' | '+x.kind+' | '+x.status.toUpperCase()+(x.stale?' | STALE MOCK':'')+' | '+x.location),'NO device connections, real alerts, hardware commands, live telemetry, or recorded events.'].join('\n')}
const api=Object.freeze({statuses,kinds,synthetic,validate,snapshot,simulate,report});if(typeof module!=='undefined'&&module.exports)module.exports=api;root.SIGNALDashboard=api;
})(typeof window!=='undefined'?window:globalThis);
