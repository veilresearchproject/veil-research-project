/* SIGNAL v37: deterministic offline PCM WAV amplitude screening, not EVP detection.
 * No recording, audio playback, network, model, equipment, or file access.
 */
(function(root){'use strict';
function fail(s){throw Error(s)}
function parse(input){
 if(!(input instanceof ArrayBuffer)||input.byteLength<44||input.byteLength>25*1024*1024)fail('WAV must be a 44-byte–25 MiB ArrayBuffer');
 const d=new DataView(input),bytes=new Uint8Array(input);const label=(p,n)=>String.fromCharCode(...bytes.slice(p,p+n));
 if(label(0,4)!=='RIFF'||label(8,4)!=='WAVE')fail('Only RIFF/WAVE is supported');
 if(d.getUint32(4,true)+8>input.byteLength)fail('Truncated RIFF file');
 let fmt=null,pcm=null,p=12;
 while(p+8<=input.byteLength){const tag=label(p,4),len=d.getUint32(p+4,true),end=p+8+len;if(end>input.byteLength)fail('Truncated WAV chunk');
  if(tag==='fmt '){if(len<16)fail('Invalid fmt chunk');fmt={format:d.getUint16(p+8,true),channels:d.getUint16(p+10,true),rate:d.getUint32(p+12,true),byteRate:d.getUint32(p+16,true),blockAlign:d.getUint16(p+20,true),bits:d.getUint16(p+22,true)};}
  if(tag==='data'&&!pcm)pcm={start:p+8,length:len};p=end+(len%2);
 }
 if(!fmt||!pcm)fail('Missing fmt/data chunk');
 if(fmt.format!==1||fmt.bits!==16||![1,2].includes(fmt.channels)||fmt.rate<8000||fmt.rate>192000||fmt.blockAlign!==fmt.channels*2||fmt.byteRate!==fmt.rate*fmt.blockAlign)fail('Only 16-bit PCM mono/stereo at 8–192 kHz supported');
 if(pcm.length%fmt.blockAlign)fail('Truncated PCM sample');
 const samples=pcm.length/fmt.blockAlign,duration=samples/fmt.rate;
 if(duration>600)fail('Maximum duration is ten minutes');
 return Object.freeze({...fmt,...pcm,samples,duration});
}
function analyze(input,{windowMs=100,ratio=3.5,floor=.04}={}){
 const m=parse(input),d=new DataView(input);
 if(!Number.isInteger(windowMs)||windowMs<20||windowMs>1000||!Number.isFinite(ratio)||ratio<2||ratio>20||!Number.isFinite(floor)||floor<.005||floor>.9)fail('Invalid analysis parameters');
 const windowSamples=Math.max(1,Math.round(m.rate*windowMs/1000));const windows=[];
 for(let start=0;start<m.samples;start+=windowSamples){const end=Math.min(m.samples,start+windowSamples);let squared=0,peak=0,points=0;
  for(let i=start;i<end;i++){for(let ch=0;ch<m.channels;ch++){const x=d.getInt16(m.start+i*m.blockAlign+2*ch,true)/32768;squared+=x*x;peak=Math.max(peak,Math.abs(x));points++;}}
  windows.push({startSec:start/m.rate,endSec:end/m.rate,rms:Math.sqrt(squared/points),peak});
 }
 const levels=windows.map(x=>x.rms).sort((a,b)=>a-b);const mid=Math.floor(levels.length/2),median=levels.length?(levels.length%2?levels[mid]:(levels[mid-1]+levels[mid])/2):0;
 const threshold=Math.max(floor,median*ratio);const candidates=[];let pending=null;
 for(let i=0;i<windows.length;i++){const w=windows[i],active=w.rms>=threshold;
  if(active){if(!pending)pending={startSec:w.startSec,endSec:w.endSec,peak:w.peak,maxRms:w.rms,windowCount:1};else {pending.endSec=w.endSec;pending.peak=Math.max(pending.peak,w.peak);pending.maxRms=Math.max(pending.maxRms,w.rms);pending.windowCount++;}}
  else if(pending){candidates.push(pending);pending=null;}
 }
 if(pending)candidates.push(pending);
 return Object.freeze({format:'PCM16',rate:m.rate,channels:m.channels,durationSec:m.duration,windowMs,medianRms:median,thresholdRms:threshold,windows:windows.length,candidates});
}
function report(x){if(!x||!Array.isArray(x.candidates))fail('Invalid audio result');return [
 'SIGNAL LOCAL WAV SCREEN — AMPLITUDE CHANGES ONLY',`Audio: ${x.channels} channel(s), ${x.rate} Hz, ${x.durationSec.toFixed(3)} s`,
 `Baseline median RMS: ${x.medianRms.toFixed(4)}; threshold: ${x.thresholdRms.toFixed(4)}`,
 `Energy-change candidates: ${x.candidates.length}`,
 ...x.candidates.slice(0,100).map((e,i)=>`${i+1}. ${e.startSec.toFixed(3)}–${e.endSec.toFixed(3)}s (peak ${e.peak.toFixed(3)}; RMS ${e.maxRms.toFixed(3)})`),
 'No speech recognized, no source inferred, no EVP/paranormal conclusion. Listen to the original and review known noises, questions, equipment and independent recordings.'
 ].join('\n')}
const api=Object.freeze({parse,analyze,report});if(typeof module!=='undefined'&&module.exports)module.exports=api;root.SIGNALAudio=api;
})(typeof window!=='undefined'?window:globalThis);
