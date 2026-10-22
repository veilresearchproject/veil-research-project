/* SIGNAL Audit Bench v0.8 reproducible regression checks.
 * Run from repository root: node signal/tests-csv-audit.js
 * Requires Node.js; no packages, credentials, network, or instrument hardware.
 */
'use strict';
if (typeof require !== 'function') throw Error('Run with Node.js: node signal/tests-csv-audit.js');
require('./csv-audit-core.js');
const audit=globalThis.SIGNALCsvAudit;
const cases=[];
function check(name,fn) {
  try{fn();cases.push({name,status:'PASS'});}
  catch(err){cases.push({name,status:'FAIL',error:String(err?.message||err)});}
}
function equal(a,b){if(a!==b)throw Error('Expected '+JSON.stringify(b)+' but got '+JSON.stringify(a));}
function shouldFail(fn){
  let failed=false;
  try{fn();}catch(_err){failed=true;}
  if(!failed)throw Error('Expected rejection');
}
check('Sample counts and per-sensor isolation',()=>{
  const r=audit.analyze(audit.sampleCsv);
  equal(r.validRows,8);equal(r.sensorCount,2);equal(r.steps,1);equal(r.gaps,1);equal(r.outOfOrder,0);
});
check('Local timezone with explicit offset',()=>{
  const r=audit.analyze('timestamp,temperature_c\n2026-10-22T08:00:00-04:00,20\n2026-10-22T08:01:00-04:00,21.6');
  equal(r.validRows,2);equal(r.steps,1);
});
check('Duplicate timestamps flagged',()=>{
  equal(audit.analyze('timestamp,temperature_c\n2026-10-22T00:00:00Z,20\n2026-10-22T00:00:00Z,21').outOfOrder,1);
});
check('Out-of-order source timestamps flagged',()=>{
  equal(audit.analyze('timestamp,temperature_c\n2026-10-22T00:01:00Z,20\n2026-10-22T00:00:00Z,21').outOfOrder,1);
});
check('No fake time inference without timezone',()=>{
  equal(audit.analyze('timestamp,temperature_c\n2026-10-22T01:00:00,20').invalidRows,1);
});
check('Impossible calendar date marked invalid',()=>{
  equal(audit.analyze('timestamp,temperature_c\n2026-02-30T00:00:00Z,20').invalidRows,1);
});
check('Physically impossible temperature marked invalid',()=>{
  equal(audit.analyze('timestamp,temperature_c\n2026-10-22T00:00:00Z,-275').invalidRows,1);
});
check('Quoted sensor name with comma',()=>{
  equal(audit.analyze('timestamp,sensor_id,temperature_c\n2026-10-22T00:00:00Z,"Room, West",20').sensors[0].id,'Room, West');
});
check('Excel BOM header accepted',()=>{
  equal(audit.analyze('\uFEFFtimestamp,temperature_c\r\n2026-10-22T00:00:00Z,20\r\n2026-10-22T00:01:00Z,20.2').validRows,2);
});
check('Malformed quoted fields rejected',()=>shouldFail(()=>audit.analyze('timestamp,temperature_c\n"2026-10-22T01:00:00Z,20')));
check('Reject oversized input',()=>shouldFail(()=>audit.analyze('a'.repeat(1000001))));
check('Reject invalid threshold',()=>shouldFail(()=>audit.analyze(audit.sampleCsv,{thresholdC:0})));
check('Report explicitly limits interpretations',()=>{
  const txt=audit.report(audit.analyze(audit.sampleCsv),{source:'SYNTHETIC TEST'});
  if(!txt.includes('NOT AI INTERPRETATION')||!txt.includes('not evidence authenticity'))throw Error('Expected limitations absent');
});
check('12k rows without false alarms',()=>{
  const csv=['timestamp,sensor_id,temperature_c'];
  for(let i=0;i<12000;i++){
    const h=String(Math.floor(i/3600)).padStart(2,'0'),m=String(Math.floor(i/60)%60).padStart(2,'0'),sec=String(i%60).padStart(2,'0');
    csv.push('2026-10-22T'+h+':'+m+':'+sec+'Z,Sensor-A,'+(20+(i%5)/10));
  }
  const r=audit.analyze(csv.join('\n'),{intervalSec:1});
  equal(r.validRows,12000);equal(r.eventCount,0);
});
console.log('SIGNAL v0.8 CSV Audit Regression Tests');
for(const c of cases)console.log(c.status+' — '+c.name+(c.error?' ('+c.error+')':''));
const failed=cases.filter(c=>c.status==='FAIL');
console.log('RESULT: '+(cases.length-failed.length)+'/'+cases.length+' passed');
if(failed.length)process.exitCode=1;
