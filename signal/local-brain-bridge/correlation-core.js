/* SIGNAL Cross-Source Correlation v0.1 — deterministic candidate time alignments.
 * Human entered metadata only; never claims independent corroboration or cause.
 * Safe for Node tests and browser; does no file/network/device access.
 */
(function(root){
'use strict';
const CB=root.SIGNALCasebook || (typeof module!=='undefined'&&module.exports?require('./casebook-core.js'):null);
if(!CB)throw Error('SIGNAL Casebook module must be loaded first');
function fail(m){throw new Error(m)}
function tolerance(value){
 if(typeof value!=='number'&&typeof value!=='string')fail('Window must be integer seconds');
 if(value===''||value===null||!Number.isInteger(Number(value))||Number(value)<0||Number(value)>300)fail('Time window must be 0–300 whole seconds');
 return Number(value);
}
function neutralLabel(e){return String(e.sourceLabel||'').trim().replace(/[\r\n\t]+/g,' ').slice(0,100)}
function analyze(raw,seconds=5){
 const book=CB.validate(raw),windowSec=tolerance(seconds),items=book.entries;
 const missingTime=items.filter(x=>!x.observedAt).length;
 const missingLabels=items.filter(x=>!neutralLabel(x)).length;
 const uncheckedTimes=items.filter(x=>x.observedAt&&!x.checks.timeVerified).length;
 const candidates=[];
 for(let i=0;i<items.length;i++){
  const a=items[i],labelA=neutralLabel(a);
  if(!a.observedAt||!labelA)continue;
  for(let j=i+1;j<items.length;j++){
   const b=items[j],labelB=neutralLabel(b);
   if(!b.observedAt||!labelB||labelA.toLocaleLowerCase('en')===labelB.toLocaleLowerCase('en'))continue;
   const deltaMs=Math.abs(Date.parse(a.observedAt)-Date.parse(b.observedAt));
   if(!Number.isFinite(deltaMs)||deltaMs>windowSec*1000)continue;
   candidates.push({entryA:a.number,entryB:b.number,sourceA:labelA,sourceB:labelB,observedA:a.observedAt,observedB:b.observedAt,deltaSeconds:deltaMs/1000,reportedTimeChecks:!!a.checks.timeVerified&&!!b.checks.timeVerified});
  }
 }
 candidates.sort((a,b)=>a.deltaSeconds-b.deltaSeconds||a.entryA-b.entryA||a.entryB-b.entryB);
 return {caseTitle:book.title,windowSeconds:windowSec,totalEntries:items.length,candidateCount:candidates.length,missingTime,missingLabels,uncheckedTimes,candidates};
}
function report(result){
 if(!result||!Array.isArray(result.candidates)||!Number.isInteger(result.windowSeconds)||!Number.isInteger(result.totalEntries))fail('Invalid correlation result');
 const lines=[
  'SIGNAL CROSS-SOURCE TIMESTAMP CANDIDATES — DESCRIPTIONS ONLY',
  `Case: ${result.caseTitle}`,
  `Window: ±${result.windowSeconds} seconds`,
  `Human-entered observations: ${result.totalEntries}`,
  `Candidate timestamp alignments: ${result.candidateCount}`,
  `Missing explicit timestamps: ${result.missingTime}`,
  `Missing distinct source labels: ${result.missingLabels}`,
  `Timestamp verification not confirmed: ${result.uncheckedTimes}`,
  'Candidates are only time proximity between distinct self-reported source labels. Independence is NOT verified.',
 ];
 for(const x of result.candidates){lines.push(`#${x.entryA} (${x.sourceA}) and #${x.entryB} (${x.sourceB}): Δ${x.deltaSeconds.toFixed(3)}s; timestamp checks ${x.reportedTimeChecks?'both self-reported':'not fully confirmed'}`)}
 lines.push('No source recording or sensor stream was read. No matching observation content, causal link, equipment independence, or paranormal cause has been established.');
 lines.push('Researcher must inspect original files, time synchronization, source placement, signal lag and mundane explanations independently.');
 return lines.join('\n');
}
const api=Object.freeze({tolerance,analyze,report});
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.SIGNALCorrelation=api;
})(typeof window!=='undefined'?window:globalThis);
