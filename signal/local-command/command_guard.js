/* SIGNAL local command guard v0.1. No device I/O. Offline pure functions. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object' && module.exports)module.exports=api;
  else root.SignalCommandGuard=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const MAX_LENGTH=240;
  const SAFE=Object.freeze({
    status:Object.freeze({intent:'read_status',reply:'I can describe system status when a trusted local status source is connected. No instruments were queried.'}),
    help:Object.freeze({intent:'help',reply:'I can explain VEIL, describe my capabilities, or request a read-only status. I cannot activate equipment.'}),
    veil:Object.freeze({intent:'about_veil',reply:'VEIL investigates reported anomalies using documented measurements, controls, and human review. A flag is not proof of anything paranormal.'})
  });
  function classify(input){
    if(typeof input!=='string'||input.length>MAX_LENGTH)return Object.freeze({intent:'invalid',allowed:false,reply:'Command must be text of 240 characters or fewer.'});
    const normalized=input.normalize('NFKC').toLowerCase().trim().replace(/\s+/g,' ');
    if(!normalized)return Object.freeze({intent:'empty',allowed:false,reply:'Please enter a question or command.'});
    // Deny any requested action first, even if the phrase also includes a safe keyword.
    if(/\b(start|stop|reset|arm|disarm|trigger|activate|deactivate|switch|turn on|turn off|unlock|erase|delete|write|send|upload|record|capture|power|shutdown|reboot|override|disable)\b/.test(normalized))
      return Object.freeze({intent:'control_blocked',allowed:false,reply:'Instrument controls are disabled in this prototype. No action was taken.'});
    if(/\b(status|health|ready|online|connected)\b/.test(normalized))return Object.freeze({allowed:true,...SAFE.status});
    if(/\b(help|capabilities|what can you do)\b/.test(normalized))return Object.freeze({allowed:true,...SAFE.help});
    if(/\b(veil|research|evidence)\b/.test(normalized))return Object.freeze({allowed:true,...SAFE.veil});
    return Object.freeze({intent:'unrecognized',allowed:false,reply:'I do not recognize that request. No action was taken. Try status, VEIL, or help.'});
  }
  return Object.freeze({classify,MAX_LENGTH});
});