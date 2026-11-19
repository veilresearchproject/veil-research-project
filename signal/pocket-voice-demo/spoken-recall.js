'use strict';
// Explicitly user-initiated speech. Every note is attributed as unverified.
function spokenRecall(entries) {
  if (!Array.isArray(entries)) throw new TypeError('Invalid memory list');
  if (entries.length === 0) return 'SIGNAL demonstration. No temporary notes to recall.';
  const safe=entries.slice(0,64).map(entry=>{
    if (!entry || entry.source!=='session' || entry.verified!==false || typeof entry.text!=='string' || !entry.text.trim() || entry.text.length>500)
      throw new TypeError('Only unverified temporary session notes may be spoken');
    return entry.text.trim();
  });
  return 'SIGNAL demonstration. These are unverified temporary notes, not established facts. '+safe.map((note,i)=>'Note '+(i+1)+': '+note).join('. ');
}
if(typeof module!=='undefined' && module.exports) module.exports={spokenRecall};
if(typeof globalThis!=='undefined') globalThis.SignalSpokenRecall=Object.freeze({spokenRecall});
