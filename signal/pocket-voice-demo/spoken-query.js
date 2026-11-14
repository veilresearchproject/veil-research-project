'use strict';
// Render a deterministic memory answer for optional local speech. Never upgrades attribution.
function prepareSpokenAnswer(answer) {
  if (typeof answer !== 'string') throw new TypeError('Answer must be text');
  const clean = answer.trim();
  if (!clean || clean.length > 12000) throw new RangeError('Invalid answer length');
  return 'SIGNAL offline demonstration. ' + clean;
}
if (typeof module !== 'undefined' && module.exports) module.exports = {prepareSpokenAnswer};
if (typeof globalThis !== 'undefined') globalThis.SignalSpokenQuery = Object.freeze({prepareSpokenAnswer});
