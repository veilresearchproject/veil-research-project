'use strict';
const assert=require('node:assert/strict');
const {classify,MAX_LENGTH}=require('./command_guard.js');
const cases=[
 ['status','read_status',true],['Is SIGNAL online?','read_status',true],
 ['What is VEIL research?','about_veil',true],['help','help',true],
 ['START the MTC','control_blocked',false],['reset panic box status','control_blocked',false],
 ['stop and tell me status','control_blocked',false],['turn on the generator','control_blocked',false],
 ['delete all records','control_blocked',false],['send status','control_blocked',false],
 ['  ','empty',false],['nonsense','unrecognized',false],
 ['x'.repeat(MAX_LENGTH+1),'invalid',false],[null,'invalid',false],
 ['ＳＴＡＲＴ the device','control_blocked',false],['What can you do?','help',true]
];
for(const [input,intent,allowed] of cases){const r=classify(input);assert.equal(r.intent,intent);assert.equal(r.allowed,allowed);assert.equal(typeof r.reply,'string');assert.ok(Object.isFrozen(r));}
console.log('PASS '+cases.length+' offline command guard cases');