/* SIGNAL Audit Bench v0.8 — local CSV analysis. No uploads or network calls. */
(() => {
 'use strict';
 const core=window.SIGNALCsvAudit;
 const byId=id=>document.getElementById(id);
 const file=byId('signal-audit-file'),interval=byId('signal-audit-interval'),
   threshold=byId('signal-audit-threshold'),example=byId('signal-audit-example'),
   run=byId('signal-audit-run'),download=byId('signal-audit-download'),
   clear=byId('signal-audit-clear'),result=byId('signal-audit-result'),
   status=byId('signal-audit-status'),preview=byId('signal-audit-preview');
 if(!core||![file,interval,threshold,example,run,download,clear,result,status,preview].every(Boolean)) return;
 let selected=null, report=null, busy=false;
 const say=t=>{status.textContent=t};
 function reset(){
   selected=null; report=null; download.disabled=true; preview.value='';
   result.textContent='No analysis run yet.'; file.value='';
 }
 example.addEventListener('click',()=>{
   reset();selected={text:core.sampleCsv,source:'SYNTHETIC EXAMPLE — NOT PHYSICAL DATA'};
   preview.value=selected.text;say('Synthetic example loaded. Analyze CSV will run actual calculations.');
 });
 file.addEventListener('change',()=>{
   selected=null;report=null;download.disabled=true;preview.value='';
   result.textContent='No analysis run yet.';
   say(file.files?.length?'Local file selected. Click Analyze CSV. No upload occurs.':'Choose a CSV or load the synthetic example.');
 });
 run.addEventListener('click',async()=>{
   if(busy)return;busy=true;run.disabled=true;report=null;download.disabled=true;
   try{
     let text,bytes,src;
     if(file.files?.length){
       const f=file.files[0];
       if(f.size>1000000)throw Error('File exceeds 1 MB.');
       if(typeof f.arrayBuffer!=='function')throw Error('Local file reader unavailable.');
       const raw=await f.arrayBuffer();bytes=new Uint8Array(raw);
       if(bytes.length>1000000)throw Error('File exceeds 1 MB.');
       text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
       src='LOCAL CSV FILE: '+String(f.name||'unnamed.csv').replace(/[\r\n]/g,' ').slice(0,100);
     }else if(selected){
       text=selected.text;src=selected.source;
       bytes=new TextEncoder().encode(text);
     }else throw Error('Select a local CSV or load the synthetic example first.');
     const data=core.analyze(text,{intervalSec:interval.value,thresholdC:threshold.value});
     let hash='unavailable';
     try{
       if(window.crypto?.subtle?.digest){
         const h=await window.crypto.subtle.digest('SHA-256',bytes);
         hash=Array.from(new Uint8Array(h),b=>b.toString(16).padStart(2,'0')).join('');
       }
     }catch(_err){hash='unavailable';}
     report=core.report(data,{source:src,sha256:hash});
     const lines=[
       src,'',
       'Valid rows: '+data.validRows+'/'+data.rows+' | Invalid: '+data.invalidRows,
       'Sensors: '+data.sensorCount,
       'Temperature range: '+(data.minC===null?'n/a':data.minC+' to '+data.maxC+'°C'),
       'Cadence gaps: '+data.gaps,
       'Timestamp-order issues: '+data.outOfOrder,
       'Temperature steps ≥ '+data.thresholdC+'°C: '+data.steps,
       'SHA-256: '+hash,'',
       'FLAGS (SOURCE ROW):'
     ];
     if(!data.events.length)lines.push('None at selected thresholds; this does not verify data quality.');
     data.events.slice(0,15).forEach(e=>lines.push('Row '+e.line+' — '+e.sensor+' — '+e.type+' — '+e.detail));
     if(data.eventCount>15)lines.push('Additional flags in report, if within capped event limit.');
     if(data.invalidRows)lines.push('Invalid rows include: '+data.invalidExampleLines.join(', '));
     lines.push('','Interpretation: flagged measurements require human review and independent controls; no cause is determined.');
     result.textContent=lines.join('\n');
     preview.value=text.slice(0,3000);
     download.disabled=false;
     say('Analysis completed locally. No file was uploaded. Download a text report if useful.');
   }catch(e){
     result.textContent='No completed analysis.';
     say('Cannot analyze: '+String(e.message||e));
   }finally{busy=false;run.disabled=false;}
 });
 download.addEventListener('click',()=>{
   if(!report)return;
   let url=null;
   try{
     url=window.URL.createObjectURL(new Blob([report],{type:'text/plain;charset=utf-8'}));
     const link=document.createElement('a');link.href=url;link.download='SIGNAL_CSV_Audit_Report.txt';
     document.body.append(link);link.click();link.remove();
     say('Local text report download initiated. Original CSV remains your responsibility.');
   }catch(_e){say('Download unavailable in this browser.');}
   finally{if(url)setTimeout(()=>window.URL.revokeObjectURL(url),1000);}
 });
 clear.addEventListener('click',()=>{reset();say('Selected data and report cleared from the page.');});
 reset();
})();