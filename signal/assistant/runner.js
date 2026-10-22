'use strict';
/* SIGNAL local assignment runner. Node.js, offline; allowed operation: CSV audit only.
 * Usage: node signal/assistant/runner.js demo|assign|run|review|status
 * All private records stay in workspace (gitignored). Single-operator prototype.
 */
const fs=require('node:fs'), path=require('node:path'), crypto=require('node:crypto');
const tasks=require('./assignment-core.js');
require('../csv-audit-core.js');
const audit=globalThis.SIGNALCsvAudit;
const base=path.join(__dirname,'workspace'),inbox=path.join(base,'inbox'),records=path.join(base,'records'),reports=path.join(base,'reports');
function setup(){
 for(const p of [base,inbox,records,reports]){
  if(fs.existsSync(p)&&fs.lstatSync(p).isSymbolicLink())throw Error('Refusing symlink directory: '+p);
  fs.mkdirSync(p,{recursive:true});
 }
}
const now=()=>new Date().toISOString();
function taskId(id){if(typeof id!=='string'||!/^SIG-[A-Za-z0-9-]{8,50}$/.test(id))throw Error('Bad assignment ID');return id;}
function recordPath(id){return path.join(records,taskId(id)+'.json');}
function load(id){return JSON.parse(fs.readFileSync(recordPath(id),'utf8'));}
function save(t){
 const target=recordPath(t.id),tmp=target+'.tmp-'+process.pid;
 fs.writeFileSync(tmp,JSON.stringify(t,null,2)+'\n',{flag:'wx',mode:0o600});
 fs.renameSync(tmp,target);
}
function inputPath(filename){
 if(typeof filename!=='string'||!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\.csv$/.test(filename)||filename.includes('..'))throw Error('CSV must be a safe filename, not a path');
 const baseReal=fs.realpathSync(inbox),full=fs.realpathSync(path.join(inbox,filename));
 if(path.dirname(full)!==baseReal)throw Error('CSV escaped the authorized inbox');
 const stat=fs.statSync(full);
 if(!stat.isFile()||stat.size>1000000)throw Error('CSV must be a regular file at most 1 MB');
 return full;
}
function assign(name,seconds=60,degrees=1.5){
 const id='SIG-'+now().replace(/[-:.TZ]/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
 const t=tasks.assign({id,kind:'audit_csv',inputName:name,requestedBy:'Local operator',at:now(),intervalSec:Number(seconds),thresholdC:Number(degrees)});
 save(t);console.log('ASSIGNED '+id+' to audit '+name+'; run: node runner.js run '+id);return id;
}
function execute(id){
 let t=load(id);
 t=tasks.start(t,now());save(t);
 try{
  const bytes=fs.readFileSync(inputPath(t.inputName));
  const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
  const sha256=crypto.createHash('sha256').update(bytes).digest('hex');
  t=tasks.finish(t,{csv:text,sha256,at:now(),audit});save(t);
  fs.writeFileSync(path.join(reports,id+'.txt'),t.result.report+'\n',{flag:'wx',mode:0o600});
  console.log('AWAITING HUMAN REVIEW '+id+'; '+t.result.findings.eventCount+' flags, '+t.result.findings.invalidRows+' invalid rows.');
  console.log('Report: '+path.join(reports,id+'.txt'));
 }catch(error){
  t=tasks.block(t,{reason:String(error.message||error),at:now()});save(t);
  console.error('BLOCKED '+id+': '+error.message);process.exitCode=1;
 }
}
function review(id,decision,reviewer){
 if(!['accept','reject'].includes(decision))throw Error('Use accept or reject');
 const t=tasks.review(load(id),{approved:decision==='accept',reviewer,at:now()});
 save(t);console.log('HUMAN '+t.status.toUpperCase()+' '+id+' by '+reviewer+' (self-reported reviewer identity)');
}
function status(){
 const files=fs.readdirSync(records).filter(f=>/^SIG-[a-z0-9-]{8,50}\.json$/i.test(f)).sort();
 if(!files.length)console.log('No assignments');
 for(const file of files){const t=load(file.slice(0,-5));console.log(t.id+' | '+t.kind+' | '+t.status+' | '+t.inputName);}
}
function demo(){
 const file=path.join(inbox,'synthetic-demo.csv');
 if(!fs.existsSync(file))fs.writeFileSync(file,audit.sampleCsv+'\n','utf8');
 console.log('SYNTHETIC DEMO: not real sensor evidence.');
 const id=assign('synthetic-demo.csv');execute(id);
}
function help(){
 console.log('SIGNAL offline assignment runner (Node.js, no paid services, no instruments)');
 console.log('demo | assign file.csv [intervalSec] [thresholdC] | run ID | review ID accept|reject "Human Name" | status');
 console.log('Place CSV files in signal/assistant/workspace/inbox; all task records stay local.');
}
function main(argv){setup();const [cmd,...rest]=argv;
 if(cmd==='demo')demo();
 else if(cmd==='assign')assign(rest[0],rest[1]??60,rest[2]??1.5);
 else if(cmd==='run')execute(taskId(rest[0]));
 else if(cmd==='review')review(taskId(rest[0]),rest[1],rest.slice(2).join(' '));
 else if(cmd==='status')status();
 else help();
}
try{main(process.argv.slice(2));}
catch(e){console.error('SIGNAL STOPPED: '+String(e.message||e));process.exitCode=1;}
