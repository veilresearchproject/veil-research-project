'use strict';
// Local-only display of attributed notes. This is not AI recall or verification.
function summarizeSessionNotes(entries) {
  if (!Array.isArray(entries)) throw new TypeError('Entries must be an array');
  if (entries.length > 64) throw new RangeError('Too many entries');
  if (entries.length===0) return 'No temporary notes to recall.';
  const lines=['SIGNAL note recall (not AI-generated). These are unverified user-entered notes, not evidence:'];
  for (const entry of entries) {
    if (!entry || entry.source!=='session' || entry.verified!==false || typeof entry.text!=='string' || !entry.text.trim() || entry.text.length>500) throw new TypeError('Invalid session note');
    lines.push('UNVERIFIED TEMPORARY NOTE: '+entry.text);
  }
  return lines.join('\n');
}
if(typeof module!=='undefined' && module.exports) module.exports={summarizeSessionNotes};
if(typeof globalThis!=='undefined') globalThis.SignalRecall=Object.freeze({summarizeSessionNotes});
