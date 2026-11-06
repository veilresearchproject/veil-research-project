'use strict';
// SIGNAL local-first, explicitly attributed memory. No persistence or network I/O.
const SOURCES = Object.freeze(['verified_project','user_note','session']);
const MAX_ITEMS = 64;
const MAX_TEXT = 500;
function clean(value, label) {
  if (typeof value !== 'string' || !value.trim() || value.length > MAX_TEXT) throw new TypeError('Invalid '+label);
  return value.trim();
}
function makeMemory() {
  const entries = new Map();
  return Object.freeze({
    add({id,text,source,verified=false}) {
      id=clean(id,'id'); text=clean(text,'text');
      if (id.length>80 || !/^[a-zA-Z0-9_-]+$/.test(id)) throw new TypeError('Invalid id');
      if (!SOURCES.includes(source)) throw new TypeError('Invalid source');
      if (typeof verified!=='boolean') throw new TypeError('Invalid verified flag');
      if (verified && source!=='verified_project') throw new TypeError('Only project facts may be verified');
      if (!entries.has(id) && entries.size>=MAX_ITEMS) throw new RangeError('Memory capacity reached');
      const item=Object.freeze({id,text,source,verified});
      entries.set(id,item);
      return item;
    },
    get(id) {return entries.get(id)||null;},
    list() {return Array.from(entries.values());},
    remove(id) {return entries.delete(id);},
    clear() {entries.clear();},
    context() {return Array.from(entries.values()).map(e=>({text:e.text,attribution:e.verified?'VERIFIED PROJECT FACT':e.source==='user_note'?'UNVERIFIED USER NOTE':'TEMPORARY SESSION CONTEXT'}));}
  });
}
if(typeof module!=='undefined' && module.exports) module.exports={makeMemory};
