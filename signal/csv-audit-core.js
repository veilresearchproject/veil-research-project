/* SIGNAL CSV Audit Bench v0.8 — deterministic, local browser calculations.
 * Not a language model; not live instrument data; not a scientifically validated detector.
 * Inputs: timestamp (strict ISO-8601 WITH timezone), temperature_c, optional sensor_id.
 * Security: plain text only, maximum 1,000,000 characters and 15,000 CSV data rows.
 */
(function(root) {
  'use strict';
  const MAX_CHARS = 1000000, MAX_ROWS = 15000;
  function csvRows(csv) {
    if (typeof csv !== 'string' || csv.length > MAX_CHARS) throw Error('CSV must be text smaller than 1,000,000 characters.');
    let rows=[], row=[], field='', quoted=false, closed=false;
    function addField() {
      if (row.length >= 24) throw Error('Too many columns (maximum 24).');
      row.push(field); field=''; closed=false;
    }
    function addRow() {
      addField();
      if (!(row.length===1 && row[0].trim()==='')) rows.push(row);
      if (rows.length > MAX_ROWS+1) throw Error('CSV exceeds the 15,000-data-row limit.');
      row=[];
    }
    csv=csv.replace(/^\uFEFF/, '');
    for(let i=0;i<csv.length;i++){
      const c=csv[i];
      if(c==='"'){
        if(quoted && csv[i+1]==='"'){field+='"';i++;}
        else if(quoted){quoted=false;closed=true;}
        else if(field===''){quoted=true;}
        else throw Error('Unescaped quote in CSV field near character '+(i+1)+'.');
      } else if(!quoted && (c===','||c==='\n'||c==='\r')){
        if(c===',') addField();
        else {addRow(); if(c==='\r' && csv[i+1]==='\n') i++;}
      } else {
        if(closed) throw Error('Unexpected text after closing quote near character '+(i+1)+'.');
        field+=c;
        if(field.length>1500)throw Error('CSV field too long (maximum 1,500 characters).');
      }
    }
    if(quoted) throw Error('CSV has an unclosed quoted field.');
    if(field!=='' || closed || row.length) addRow();
    return rows;
  }
  function strictTime(raw){
    const m=String(raw).trim().match(/^(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)(?:\.(\d{1,3}))?(Z|[+-]\d\d:\d\d)$/i);
    if(!m) return NaN;
    const yr=+m[1],mo=+m[2],day=+m[3],h=+m[4],min=+m[5],sec=+m[6];
    if(yr<1970||mo<1||mo>12||day<1||h>23||min>59||sec>59) return NaN;
    const dt=new Date(Date.UTC(yr,mo-1,day));
    if(dt.getUTCFullYear()!==yr||dt.getUTCMonth()!==mo-1||dt.getUTCDate()!==day)return NaN;
    if(m[8]!=='Z' && m[8]!=='z'){
      const t=m[8].slice(1).split(':').map(Number);
      if(t[0]>23||t[1]>59)return NaN;
    }
    const n=Date.parse(String(raw).trim());
    return Number.isFinite(n)?n:NaN;
  }
  function optionsCheck(options){
    const interval=Number(options?.intervalSec ?? 60);
    const threshold=Number(options?.thresholdC ?? 1.5);
    if(!Number.isFinite(interval)||interval<1||interval>86400)throw Error('Expected sample interval must be 1–86,400 seconds.');
    if(!Number.isFinite(threshold)||threshold<=0||threshold>100)throw Error('Temperature-change threshold must be greater than 0 and at most 100°C.');
    return {intervalSec:interval,thresholdC:threshold};
  }
  function analyze(csv, opts={}){
    const o=optionsCheck(opts), rows=csvRows(csv);
    if(!rows.length)throw Error('CSV is empty.');
    const header=rows.shift().map(x=>x.trim().toLowerCase());
    if(new Set(header).size!==header.length)throw Error('Duplicate column names.');
    const ti=header.indexOf('timestamp'),vi=header.indexOf('temperature_c'),si=header.indexOf('sensor_id');
    if(ti<0||vi<0)throw Error('CSV requires columns timestamp and temperature_c; sensor_id is optional.');
    const streams=new Map(), events=[],badExamples=[];
    let invalid=0, valid=0, dropped=0, outOfOrder=0, gaps=0, steps=0, min=Infinity,max=-Infinity;
    function flag(item){if(events.length<150)events.push(item);else dropped++;}
    rows.forEach((row,i)=>{
      const line=i+2;
      const rawTime=(row[ti]||'').trim(), rawValue=(row[vi]||'').trim();
      const sensor=si>=0?(row[si]||'').trim():'sensor-1';
      const ms=strictTime(rawTime);
      const numeric=/^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i.test(rawValue)?Number(rawValue):NaN;
      if(row.length!==header.length||!sensor||sensor.length>80||!Number.isFinite(ms)||!Number.isFinite(numeric)||numeric < -273.15){
        invalid++;
        if(badExamples.length<8)badExamples.push(line);
        return;
      }
      valid++;min=Math.min(min,numeric);max=Math.max(max,numeric);
      const key=sensor;
      if(!streams.has(key)) streams.set(key,{sensor:key,count:0,last:null,min:Infinity,max:-Infinity,stepCount:0,gapCount:0,orderCount:0});
      const stream=streams.get(key);stream.count++;stream.min=Math.min(stream.min,numeric);stream.max=Math.max(stream.max,numeric);
      if(stream.last){
        const elapsed=(ms-stream.last.ms)/1000;
        if(elapsed<=0){outOfOrder++;stream.orderCount++;flag({type:'TIME_ORDER',line,sensor,detail:elapsed===0?'Duplicate timestamp':'Timestamp earlier than previous row',timestamp:rawTime});}
        else {
          if(elapsed>o.intervalSec*1.5){
            gaps++;stream.gapCount++;
            flag({type:'CADENCE_GAP',line,sensor,detail:'Interval '+Number(elapsed.toFixed(3))+' s exceeds 1.5× expected '+o.intervalSec+' s',timestamp:rawTime});
          }
          const delta=numeric-stream.last.temp;
          if(Math.abs(delta)>=o.thresholdC){
            steps++;stream.stepCount++;
            flag({type:'TEMPERATURE_STEP',line,sensor,detail:'Δ '+Number(delta.toFixed(3))+'°C from prior valid sample',timestamp:rawTime});
          }
        }
      }
      // Never conceal reordered timestamps by sorting: original CSV order is retained.
      stream.last={ms,temp:numeric};
    });
    return {
      version:'0.8', rows:rows.length, validRows:valid, invalidRows:invalid,
      invalidExampleLines:badExamples, sensorCount:streams.size, intervalSec:o.intervalSec,
      thresholdC:o.thresholdC, minC:valid?min:null, maxC:valid?max:null,
      gaps, steps, outOfOrder, eventCount:gaps+steps+outOfOrder,
      events, omittedEventCount:dropped,
      sensors:Array.from(streams.values()).map(s=>({id:s.sensor,rows:s.count,minC:s.min,maxC:s.max,steps:s.stepCount,gaps:s.gapCount,timeOrderIssues:s.orderCount})),
      caution:'Algorithmic checks flag measurements and acquisition quality, not causes. No calibration, provenance, or independent corroboration is established by this tool.'
    };
  }
  function report(result, options={}){
    const src=options.source || 'visitor-supplied CSV (not verified)';
    const lines=[
      'SIGNAL — CSV EVIDENCE-QUALITY CHECK v'+result.version,
      'LOCAL DETERMINISTIC ANALYSIS — NOT AI INTERPRETATION',
      'NO REAL-TIME SENSOR CONNECTION; SOURCE AND CAUSES ARE UNVERIFIED',
      'Source: '+src,
      'File SHA-256: '+(options.sha256||'not computed'),
      'Note: A hash identifies file bytes, not evidence authenticity or custody.',
      'Expected interval: '+result.intervalSec+' seconds; step threshold: '+result.thresholdC+'°C',
      'Rows: '+result.rows+'; valid: '+result.validRows+'; invalid: '+result.invalidRows+'; sensors: '+result.sensorCount,
      'Temperature range: '+(result.minC===null?'n/a':result.minC+' to '+result.maxC+'°C'),
      'Cadence gaps: '+result.gaps+'; timestamp order issues: '+result.outOfOrder+'; temperature steps: '+result.steps,
      'Flagged events: '+result.eventCount+'; displayed: '+result.events.length+'; omitted due to display cap: '+result.omittedEventCount,
      'Invalid source line examples: '+(result.invalidExampleLines.join(', ')||'none'),
      '',
      'Per-sensor summary:'
    ];
    result.sensors.forEach(s=>lines.push(s.id+' | samples='+s.rows+' | min='+s.minC+'°C | max='+s.maxC+'°C | gaps='+s.gaps+' | order='+s.timeOrderIssues+' | changes='+s.steps));
    lines.push('','Flagged observations (not explanations):');
    result.events.forEach(e=>lines.push('Source line '+e.line+' | '+e.sensor+' | '+e.type+' | '+e.timestamp+' | '+e.detail));
    lines.push('','LIMITATIONS: '+result.caution,'Thresholds are user-defined; false positives and misses are possible.','Keep original source files and verify timing, calibration, environment, and chain of custody independently.');
    return lines.join('\n');
  }
  const sampleCsv=[
    'timestamp,sensor_id,temperature_c',
    '2026-10-22T08:00:00Z,Room-A,21.0',
    '2026-10-22T08:00:00Z,Room-B,20.9',
    '2026-10-22T08:01:00Z,Room-A,21.1',
    '2026-10-22T08:01:00Z,Room-B,20.9',
    '2026-10-22T08:02:00Z,Room-A,19.2',
    '2026-10-22T08:02:00Z,Room-B,21.0',
    '2026-10-22T08:06:00Z,Room-A,19.1',
    '2026-10-22T08:03:00Z,Room-B,20.9'
  ].join('\n');
  root.SIGNALCsvAudit=Object.freeze({parse:csvRows,analyze,report,sampleCsv});
})(typeof window==='object'?window:globalThis);
