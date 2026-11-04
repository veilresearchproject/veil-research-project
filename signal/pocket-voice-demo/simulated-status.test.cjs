// Pure offline simulated-status contract tests. Run: node signal/pocket-voice-demo/simulated-status.test.cjs
'use strict';
const assert=require('node:assert/strict');
function simulatedStatus(input) {
  if (typeof input !== 'string' || input.length > 240) return {kind:'rejected',message:'Enter a short text request.'};
  const q=input.trim().toLowerCase().replace(/\s+/g,' ');
  if (!q) return {kind:'rejected',message:'Enter a request first.'};
  // Deny potential control actions before matching status keywords.
  if (/\b(start|stop|reset|arm|disarm|activate|deactivate|delete|erase|power|unlock|open|close|trigger|override|disable|enable|turn|launch|run|reboot|shutdown)\b/.test(q))
    return {kind:'blocked',message:'Control requests are disabled in this demonstration. No instrument was contacted.'};
  if (/\b(mtc|recorder|audio)\b/.test(q) && /\b(status|state|health|online|ready)\b/.test(q))
    return {kind:'simulation',message:'SIMULATED MTC: status unknown. No live device connection or measurement exists.'};
  if (/\b(panic box|panicbox)\b/.test(q) && /\b(status|state|health|online|ready)\b/.test(q))
    return {kind:'simulation',message:'SIMULATED Panic Box: status unknown. No live device connection or measurement exists.'};
  return {kind:'unrecognized',message:'No simulated status match. Try “MTC status” or “Panic Box status”. No device was contacted.'};
}
const cases=[["MTC status","simulation","SIMULATED MTC"],["What is the panic box status?","simulation","SIMULATED Panic Box"],["audio health","simulation","SIMULATED MTC"],["recorder ready","simulation","SIMULATED MTC"],["reset MTC status","blocked","No instrument"],["stop panic box status","blocked","No instrument"],["please activate mtc","blocked","No instrument"],["delete audio status","blocked","No instrument"],["turn on panic box status","blocked","No instrument"],["MTC status; override","blocked","No instrument"],["hello","unrecognized","No device"],["","rejected","Enter a request"],["                                                                                                                                                                                                                                                 ","rejected","Enter a short"],["panic box health","simulation","SIMULATED Panic Box"]];
for(const [input,kind,fragment] of cases){const r=simulatedStatus(input);assert.equal(r.kind,kind,input);assert.ok(r.message.includes(fragment),input);}
assert.equal(simulatedStatus(null).kind,'rejected');
assert.equal(simulatedStatus('MTC STATUS').kind,'simulation');
console.log('PASS: '+(cases.length+2)+' simulated status contract tests');
