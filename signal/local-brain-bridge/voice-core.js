/* SIGNAL v35: deterministic speech lifecycle controller. No microphone access. */
(function(root){'use strict';
const STATES=Object.freeze(['idle','speaking','listening','processing','paused','error']);
function create(){return {state:'idle',generation:0,partial:'',lastTranscript:'',notice:'Ready. Microphone not connected.'}}
function transition(s,event,details=''){
 if(!s||!STATES.includes(s.state)||!Number.isInteger(s.generation))throw Error('Invalid voice session');
 if(typeof event!=='string'||typeof details!=='string'||details.length>1000)throw Error('Invalid voice event');
 const a={...s,generation:s.generation+1};
 switch(event){
  case 'speak':if(!['idle','paused','processing'].includes(s.state))throw Error('Cannot start speech from current state');a.state='speaking';a.notice='Device speech requested; playback may require internet';break;
  case 'barge-in':if(s.state!=='speaking')throw Error('Can only interrupt active speaking');a.state='listening';a.notice='Speech cancelled; listening is simulated until microphone recognition is connected';break;
  case 'press-to-talk':if(!['idle','paused'].includes(s.state))throw Error('Busy; stop current action first');a.state='listening';a.notice='Push-to-talk activated (simulation only; no mic accessed)';break;
  case 'heard-text':if(s.state!=='listening')throw Error('Not accepting speech transcript');if(!details.trim())throw Error('Empty transcript');a.state='processing';a.lastTranscript=details.trim();a.partial='';a.notice='Transcript provided by operator, not recognized from audio';break;
  case 'speech-end':if(s.state!=='speaking')throw Error('Not speaking');a.state='idle';a.notice='Speech completed';break;
  case 'pause':if(!['listening','speaking','processing'].includes(s.state))throw Error('Nothing active to pause');a.state='paused';a.notice='Stopped; any pending speech must be cancelled by UI';break;
  case 'ready':a.state='idle';a.partial='';a.notice='Ready';break;
  case 'fail':a.state='error';a.notice='Voice error: '+(details.trim()||'unknown').slice(0,80);break;
  default:throw Error('Event not allowlisted');
 }
 return a;
}
const api=Object.freeze({STATES,create,transition});
if(typeof module!=='undefined'&&module.exports)module.exports=api;root.SIGNALVoice=api;
})(typeof window!=='undefined'?window:globalThis);
