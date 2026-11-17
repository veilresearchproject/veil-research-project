/* VEIL / SIGNAL Image-Origin Workbench v0.1 — pure, offline research-record logic.
 * This module does not search the internet, fetch URLs, upload images, or authenticate reviewers.
 */
(function (root, factory) {
  'use strict';
  const core = factory();
  if (typeof module === 'object' && module.exports) module.exports = core;
  if (typeof window !== 'undefined') root.VEILImageOriginCore = core;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const CHECKS = Object.freeze([
    ['lens_whole', 'Google Lens — complete image'],
    ['lens_crop', 'Google Lens — selected region/crop'],
    ['tineye', 'TinEye — visual matches'],
    ['bing', 'Bing Visual Search — visual matches'],
    ['text', 'Caption, object and contextual text search'],
    ['archives', 'Archive and publication-date verification']
  ]);
  const PROVIDERS = Object.freeze({
    lens: 'https://lens.google.com/',
    tineye: 'https://tineye.com/',
    bing: 'https://www.bing.com/visualsearch'
  });
  const statuses = new Set(['not_checked', 'checked_no_match', 'checked_matches', 'unavailable']);
  const types = new Set(['webpage', 'news', 'social', 'archive', 'photographer', 'other']);
  const dates = new Set(['unknown', 'publisher_timestamp', 'archive_capture', 'researcher_verified']);
  const matches = new Set(['exact', 'partial', 'altered', 'context_only', 'not_a_match']);
  const nowISO = () => new Date().toISOString();
  function cleanText(v, limit = 700) {
    if (typeof v !== 'string') return '';
    return v.replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, limit);
  }
  function validURL(input) {
    const value = cleanText(input, 2048);
    let u;
    try { u = new URL(value); } catch (_) { throw new Error('Enter a complete HTTPS source URL.'); }
    if (u.protocol !== 'https:' || u.username || u.password || !u.hostname || u.hostname.length > 253) {
      throw new Error('Source URL must be public HTTPS without credentials.');
    }
    const host = u.hostname.toLowerCase();
    const blocked = /(^localhost$|\.local$|\.localhost$|\.internal$|\.test$|\.invalid$|\.example$)/.test(host)
      || /^(127\.|10\.|192\.168\.|169\.254\.|0\.|::1$)/.test(host)
      || /^172\.(1[6-9]|2\d|3[01])\./.test(host)
      || /^(\d{1,3}\.){3}\d{1,3}$/.test(host)
      || host.includes(':');
    if (blocked) throw new Error('Local, IP-address and private-network links are not accepted.');
    return u.toString();
  }
  function validDate(input) {
    if (input === '' || input === null || input === undefined) return null;
    if (typeof input !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(input)) throw new Error('Use YYYY-MM-DD for a documented date.');
    const d = new Date(input + 'T00:00:00Z');
    if (Number.isNaN(d.getTime()) || d.toISOString().slice(0, 10) !== input) throw new Error('Invalid calendar date.');
    return input;
  }
  function validateHash(hash) {
    if (!/^[a-f0-9]{64}$/.test(hash || '')) throw new Error('Original SHA-256 checksum is required.');
    return hash;
  }
  function validateOriginal(o) {
    if (!o || typeof o !== 'object') throw new Error('Load and hash an original file first.');
    const name = cleanText(o.name, 150);
    if (!name || !Number.isSafeInteger(o.size) || o.size <= 0 || o.size > 25 * 1024 * 1024) throw new Error('Invalid image name or file size (max 25 MB).');
    if (!Number.isSafeInteger(o.width) || !Number.isSafeInteger(o.height) || o.width < 1 || o.height < 1 || o.width > 20000 || o.height > 20000) throw new Error('Invalid image dimensions.');
    return {name, size:o.size, width:o.width, height:o.height, sha256:validateHash(o.sha256)};
  }
  function normalizeSource(s, existing = []) {
    if (!s || typeof s !== 'object') throw new Error('Source record is missing.');
    const id = cleanText(s.id, 60);
    if (!/^SRC-[A-Z0-9-]{2,50}$/.test(id)) throw new Error('Source ID must begin SRC- and use uppercase letters/numbers.');
    if (existing.some(x => x.id === id)) throw new Error('Duplicate source ID.');
    if (!types.has(s.sourceType)) throw new Error('Choose the source category.');
    if (!dates.has(s.dateBasis)) throw new Error('Choose how the date was established.');
    if (!matches.has(s.matchType)) throw new Error('Choose the visual match type.');
    const publishedDate = validDate(s.publishedDate);
    if (!publishedDate && s.dateBasis !== 'unknown') throw new Error('A verified date basis needs a documented publication date.');
    if (publishedDate && s.dateBasis === 'unknown') throw new Error('Choose a documented date basis, or leave date blank.');
    const observedAt = cleanText(s.observedAt, 40);
    if (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3})?Z$/.test(observedAt) || !Number.isFinite(Date.parse(observedAt))) throw new Error('Invalid UTC research log timestamp.');
    const caption = cleanText(s.caption, 500);
    const note = cleanText(s.note, 1200);
    if (!caption && !note) throw new Error('Include the caption or what this source shows.');
    return {
      id, url:validURL(s.url), sourceType:s.sourceType, matchType:s.matchType,
      publishedDate, dateBasis:s.dateBasis, observedAt, caption, note,
      searchProvider:cleanText(s.searchProvider, 80), region:cleanText(s.region, 80),
      creatorClaim:cleanText(s.creatorClaim, 160)
    };
  }
  function normalizeVariant(v, original) {
    const label = cleanText(v.label, 60);
    if (!label) throw new Error('Give the selected crop a label.');
    const rect = [v.x, v.y, v.width, v.height];
    if (!rect.every(Number.isSafeInteger) || rect[0] < 0 || rect[1] < 0 || rect[2] < 5 || rect[3] < 5 || rect[0] + rect[2] > original.width || rect[1] + rect[3] > original.height) throw new Error('Crop must lie within the original image and be at least 5 px.');
    return {label, x:v.x, y:v.y, width:v.width, height:v.height, sha256:validateHash(v.sha256)};
  }
  function makeQueries(caption) {
    const words = cleanText(caption, 200);
    if (!words) return [];
    const query = words.replace(/["'`]/g, '').trim();
    return [
      {label:'Google text/context', url:'https://www.google.com/search?q='+encodeURIComponent('"'+query+'"')},
      {label:'Bing text/context', url:'https://www.bing.com/search?q='+encodeURIComponent('"'+query+'"')},
      {label:'Google image-context search', url:'https://www.google.com/search?tbm=isch&q='+encodeURIComponent(query)}
    ];
  }
  function assess(sources, checks) {
    const sorted = sources.filter(x => x.publishedDate && x.matchType !== 'not_a_match' && x.matchType !== 'context_only')
      .slice().sort((a,b) => a.publishedDate.localeCompare(b.publishedDate) || a.id.localeCompare(b.id));
    const qualified = sorted.filter(s => s.dateBasis === 'archive_capture' || s.dateBasis === 'publisher_timestamp' || s.dateBasis === 'researcher_verified');
    const earliest = qualified[0] || null;
    const captions = [...new Set(sources.map(x => cleanText(x.caption).toLowerCase()).filter(Boolean))];
    const missingChecks = CHECKS.filter(([k]) => checks[k] !== 'checked_no_match' && checks[k] !== 'checked_matches');
    const exact = sources.filter(x => x.matchType === 'exact').length;
    const partial = sources.filter(x => x.matchType === 'partial' || x.matchType === 'altered').length;
    return {
      earliestTraceableMatch:earliest ? {id:earliest.id, date:earliest.publishedDate, url:earliest.url, dateBasis:earliest.dateBasis} : null,
      earliestUndatedOrWeaklyDated:sorted.length > 0 && qualified.length === 0,
      captionsDiffer:captions.length > 1,
      distinctCaptionCount:captions.length,
      exactMatchCount:exact, partialOrAlteredMatchCount:partial,
      missingChecks:missingChecks.map(([k,label]) => label),
      limitations:[
        'Earliest located posting is not proof of the image creator, capture date, or original context.',
        'Dates, visual matches, captions and identities are human-entered claims requiring corroboration.',
        'A checksum establishes file identity only; it cannot establish authenticity or custody.'
      ]
    };
  }
  function buildReport(data) {
    if (!data || typeof data !== 'object') throw new Error('Investigation data is required.');
    const caseId = cleanText(data.caseId, 50);
    if (!/^VEIL-IMG-[0-9]{4}-[0-9]{3,6}$/.test(caseId)) throw new Error('Case ID must look like VEIL-IMG-2026-001.');
    const original = validateOriginal(data.original);
    const variants = (data.variants || []).map(v => normalizeVariant(v, original));
    if (new Set(variants.map(x=>x.label.toLowerCase())).size !== variants.length) throw new Error('Crop labels must be unique.');
    const sources = [];
    for (const s of (data.sources || [])) sources.push(normalizeSource(s, sources));
    const checks = {};
    for (const [k] of CHECKS) {
      const status = data.checks && data.checks[k] || 'not_checked';
      if (!statuses.has(status)) throw new Error('Unknown verification checklist value.');
      checks[k] = status;
    }
    const review = data.review || {};
    const reviewer = cleanText(review.name, 120);
    const reviewedAt = cleanText(review.reviewedAt, 40);
    if (reviewedAt && !Number.isFinite(Date.parse(reviewedAt))) throw new Error('Invalid reviewer timestamp.');
    const canMarkReviewed = !!reviewer && !!reviewedAt;
    const result = {
      schema:'VEIL-SIGNAL-IMAGE-ORIGIN-0.1',
      caseId, status:canMarkReviewed ? 'HUMAN_REVIEW_RECORDED' : 'DRAFT_UNVERIFIED',
      original, variants, checks, sources,
      assessment:assess(sources, checks),
      humanReview:{name:canMarkReviewed ? reviewer : '', reviewedAt:canMarkReviewed ? reviewedAt : null,
        note:cleanText(review.note, 900), verifiedIdentity:false},
      externalSearch:'All image uploads and searches must be performed by the investigator outside this workbench.',
      publicationApproved:false
    };
    return result;
  }
  function markdown(report) {
    const safe = s => String(s === null || s === undefined ? '' : s).replace(/[\r\n|]/g, ' ').replace(/[`]/g, "'");
    const lines = [
      '# VEIL / SIGNAL Image-Origin Investigation — '+safe(report.caseId), '',
      '**Status:** '+report.status+' (not publication authorization)',
      '**Original file:** '+safe(report.original.name)+'; SHA-256 `'+report.original.sha256+'`; '+report.original.width+'×'+report.original.height+' px',
      '', '## Search handoffs / checklist'
    ];
    for (const [key,label] of CHECKS) lines.push('- '+label+': **'+safe(report.checks[key])+'**');
    lines.push('', '## Cropped variants');
    if (!report.variants.length) lines.push('No cropped regions logged.');
    for (const v of report.variants) lines.push('- '+safe(v.label)+': x='+v.x+', y='+v.y+', '+v.width+'×'+v.height+' px, SHA-256 `'+v.sha256+'`');
    lines.push('', '## Attributed web findings', '| Source | URL | Published date | Date evidence | Match | Caption / note |', '|---|---|---|---|---|---|');
    for (const s of report.sources) lines.push('| '+safe(s.id)+' | '+safe(s.url)+' | '+safe(s.publishedDate || 'unknown')+' | '+safe(s.dateBasis)+' | '+safe(s.matchType)+' | '+safe(s.caption || s.note)+' |');
    const e = report.assessment.earliestTraceableMatch;
    lines.push('', '## Assessment', e ? 'Earliest *traceable match entered*: '+safe(e.id)+' on '+e.date+' ('+safe(e.dateBasis)+'). **Not established as the origin.**' : 'No adequately dated visual match has been entered. Image origin remains unestablished.');
    lines.push('Different captions detected: '+(report.assessment.captionsDiffer?'yes':'not from entered records')+'.');
    lines.push('Incomplete/unavailable verification checks: '+(report.assessment.missingChecks.join('; ') || 'none recorded')+'.');
    for (const caution of report.assessment.limitations) lines.push('- '+caution);
    lines.push('', '## Human review', 'Recorded reviewer: '+safe(report.humanReview.name || 'none')+'; date: '+safe(report.humanReview.reviewedAt || 'not reviewed'),
      'Authentication: **not implemented**. Publication approval: **no**.', '',
      'Prepared for private review. Do not publish image or identifiable sources without permission.');
    return lines.join('\n')+'\n';
  }
  return {CHECKS, PROVIDERS, nowISO, cleanText, validURL, validDate, validateOriginal, normalizeSource, normalizeVariant, makeQueries, assess, buildReport, markdown};
});
