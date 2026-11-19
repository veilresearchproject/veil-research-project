/* SIGNAL image-origin case continuity v0.2. No network/storage and no trust in imported documents. */
(function (root, factory) {
  'use strict';
  const api = factory(typeof module === 'object' && module.exports ? require('./core.js') : root.VEILImageOriginCore);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (typeof window !== 'undefined') root.VEILImageCaseResume = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (core) {
  'use strict';
  const MAX_JSON = 512 * 1024;
  function parseDraft(text) {
    if (typeof text !== 'string' || text.length === 0 || text.length > MAX_JSON) throw Error('Draft JSON must be 1–524288 characters.');
    let input;
    try {input = JSON.parse(text);} catch (_) {throw Error('Select a valid, complete JSON case export.');}
    if (!input || Array.isArray(input) || typeof input !== 'object' || input.schema !== 'VEIL-SIGNAL-IMAGE-ORIGIN-0.1') throw Error('Unsupported case format.');
    if (input.publicationApproved !== false || input.humanReview?.verifiedIdentity === true) throw Error('Imported case makes an unsupported publication or identity claim.');
    if (!Array.isArray(input.sources) || !Array.isArray(input.variants) || input.sources.length > 200 || input.variants.length > 50) throw Error('Imported case source/crop count exceeds safe bounds.');
    const fresh = core.buildReport({caseId:input.caseId,original:input.original,variants:input.variants,sources:input.sources,checks:input.checks,review:{}});
    fresh.status='DRAFT_UNVERIFIED';
    fresh.humanReview={name:'',reviewedAt:null,note:'Imported case requires a fresh human review.',verifiedIdentity:false};
    return fresh;
  }
  function matchedOriginal(saved, current) {
    const a=core.validateOriginal(saved), b=core.validateOriginal(current);
    return a.sha256 === b.sha256 && a.size === b.size && a.width === b.width && a.height === b.height;
  }
  function diagnostics(report) {
    if (!report || !Array.isArray(report.sources)) throw Error('Validated case report required.');
    const counts = new Map(), seenUrls = new Map();
    let archive = null, published = null;
    for (const s of report.sources) {
      const u = new URL(s.url), key = u.origin + u.pathname.replace(/\/$/,'') + u.search;
      const host=u.hostname.toLowerCase();
      counts.set(host,(counts.get(host)||0)+1);
      seenUrls.set(key,(seenUrls.get(key)||0)+1);
      if (!s.publishedDate || s.matchType === 'not_a_match' || s.matchType === 'context_only') continue;
      if (s.dateBasis === 'archive_capture' && (!archive || s.publishedDate < archive.date)) archive = {id:s.id,date:s.publishedDate};
      if (['publisher_timestamp','researcher_verified'].includes(s.dateBasis) && (!published || s.publishedDate < published.date)) published = {id:s.id,date:s.publishedDate};
    }
    return {
      earliestArchiveCapture:archive, earliestPublisherOrCorroboratedDate:published,
      repeatedSourceUrls:[...seenUrls].filter(([,n])=>n>1).length,
      hostGroups:[...counts].map(([host,count])=>({host,count})).sort((a,b)=>a.host.localeCompare(b.host)),
      sourceCount:report.sources.length,
      cautions:[
        'Archive capture date means that an archived copy existed by that date; it is not necessarily the original publication date.',
        'Multiple pages on one site, or copies on other sites, are not automatically independent eyewitness accounts.',
        'Reopening this draft cannot verify the original image, source pages, reviewer identity or chronology.'
      ]
    };
  }
  return {MAX_JSON,parseDraft,matchedOriginal,diagnostics};
});
