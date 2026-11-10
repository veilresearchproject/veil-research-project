// Run with: node signal/pocket-voice-demo/tests/spoken-status.test.cjs
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(script,'inline demo script present');
const sandbox={document:{getElementById(){return {addEventListener(){}}},querySelectorAll(){return []},addEventListener(){}},window:{addEventListener(){}}};
vm.createContext(sandbox);
vm.runInContext(script[1],sandbox);
const cases=[[{"kind":"simulation","message":"SIMULATED MTC: status unknown."},"SIGNAL demonstration. SIMULATED MTC: status unknown."],[{"kind":"blocked","message":"Control requests are disabled."},"SIGNAL demonstration. Control requests are disabled."],[{"kind":"rejected","message":"Enter a request first."},"SIGNAL demonstration. Enter a request first."],[{"kind":"unrecognized","message":"No simulated status match."},"SIGNAL demonstration. No simulated status match."],[{"kind":"live","message":"Device online."},null],[null,null]];
for(const [input,expected] of cases){assert.equal(sandbox.statusSpeechText(input),expected);}
assert.match(html,/id="status-speak"[^>]*disabled/);
assert.match(html,/status-request'\)\.addEventListener\('input'/);
assert.match(html,/connect-src 'none'/);
console.log('9 SIGNAL spoken-status checks passed');
