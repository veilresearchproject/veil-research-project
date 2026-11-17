/* SIGNAL image-origin research handoff. Local-only file processing. No fetch or remote upload. */
(() => {
  'use strict';
  const c = window.VEILImageOriginCore;
  const resume=window.VEILImageCaseResume;
  if (!c || !resume) return;
  const el = id => document.getElementById(id);
  const state = {original:null, variants:[], sources:[], checks:{}, review:{}, image:null, imageURL:null, selection:null};
  const canvas = el('preview');
  const outline = el('crop-outline');
  const ctx = canvas.getContext('2d');
  let dragStart = null;
  let pendingImport = null;
  function invalidateReview(){state.review={};}
  function status(message, error=false) {const n=el('feedback'); n.textContent=message;if(error)n.setAttribute('data-error','');else n.removeAttribute('data-error');}
  function fail(error) {status(error && error.message ? error.message : String(error),true);}
  async function sha256(blob) {
    if (!globalThis.crypto || !crypto.subtle) throw new Error('SHA-256 requires a secure browser context (HTTPS or localhost).');
    const bytes=await blob.arrayBuffer();
    const hash=await crypto.subtle.digest('SHA-256',bytes);
    return Array.from(new Uint8Array(hash),b=>b.toString(16).padStart(2,'0')).join('');
  }
  function download(blob, name){const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),30000);}
  async function loadImage(file) {
    if (!file) return;
    if (!['image/png','image/jpeg','image/webp'].includes(file.type) || !file.size || file.size>25*1024*1024) throw new Error('Choose a PNG/JPEG/WebP image of up to 25 MB.');
    if (state.imageURL) URL.revokeObjectURL(state.imageURL);
    state.imageURL=URL.createObjectURL(file);
    const im=new Image();
    im.src=state.imageURL;
    await im.decode();
    if (!im.naturalWidth || !im.naturalHeight || im.naturalWidth>20000 || im.naturalHeight>20000) throw new Error('Invalid image dimensions or decoding failure.');
    const next = c.validateOriginal({name:file.name,size:file.size,width:im.naturalWidth,height:im.naturalHeight,sha256:await sha256(file)});
    if (pendingImport && !resume.matchedOriginal(pendingImport.original,next)) throw Error('Original image does not match the saved case checksum/dimensions. Import remains pending; select the correct file.');
    state.image=im; state.original=pendingImport ? pendingImport.original : next; state.variants=pendingImport ? pendingImport.variants : []; state.sources=pendingImport ? pendingImport.sources : []; invalidateReview();state.selection=null;
    for(const select of document.querySelectorAll('[data-check]')){select.value=pendingImport ? pendingImport.checks[select.dataset.check] : 'not_checked';state.checks[select.dataset.check]=select.value;}
    if(pendingImport){el('case-id').value=pendingImport.caseId;el('import-status').textContent='Original verified by local checksum. Imported notes are unverified; previous reviewer cleared. Crops are metadata only: recreate crop PNGs before using them.';pendingImport=null;}
    el('reviewer').value='';el('review-note').value='';
    const scale=Math.min(1,1000/im.naturalWidth,700/im.naturalHeight);
    canvas.width=Math.max(1,Math.round(im.naturalWidth*scale));canvas.height=Math.max(1,Math.round(im.naturalHeight*scale));
    ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(im,0,0,canvas.width,canvas.height);
    el('preview-wrap').hidden=false;outline.hidden=true;el('make-crop').disabled=true;
    el('image-info').textContent=`${next.name} · ${next.width}×${next.height} px · ${next.size} bytes · SHA-256 ${next.sha256}`;
    renderCrops();renderSources();renderAssessment();status('Image validated locally. Check existing sourced claims, and search the complete image plus distinctive regions.');
  }
  function position(e) {
    const r=canvas.getBoundingClientRect();
    return {x:Math.max(0,Math.min(canvas.width,(e.clientX-r.left)*canvas.width/r.width)),y:Math.max(0,Math.min(canvas.height,(e.clientY-r.top)*canvas.height/r.height))};
  }
  canvas.addEventListener('pointerdown',e=>{if(!state.image)return;dragStart=position(e);canvas.setPointerCapture(e.pointerId);outline.hidden=false;state.selection=null;});
  canvas.addEventListener('pointermove',e=>{if(!dragStart)return;const p=position(e);const l=Math.min(p.x,dragStart.x),t=Math.min(p.y,dragStart.y),w=Math.abs(p.x-dragStart.x),h=Math.abs(p.y-dragStart.y);Object.assign(outline.style,{left:(l/canvas.width*100)+'%',top:(t/canvas.height*100)+'%',width:(w/canvas.width*100)+'%',height:(h/canvas.height*100)+'%'});});
  canvas.addEventListener('pointerup',e=>{if(!dragStart)return;const p=position(e);const l=Math.min(p.x,dragStart.x),t=Math.min(p.y,dragStart.y),r=Math.max(p.x,dragStart.x),b=Math.max(p.y,dragStart.y);dragStart=null;
    const im=state.image;const x=Math.round(l*im.naturalWidth/canvas.width),y=Math.round(t*im.naturalHeight/canvas.height);const endX=Math.min(im.naturalWidth,Math.round(r*im.naturalWidth/canvas.width)),endY=Math.min(im.naturalHeight,Math.round(b*im.naturalHeight/canvas.height));state.selection={x,y,width:endX-x,height:endY-y};el('make-crop').disabled=state.selection.width<5||state.selection.height<5;if(el('make-crop').disabled)outline.hidden=true;
  });
  canvas.addEventListener('pointercancel',()=>{dragStart=null;outline.hidden=true;state.selection=null;el('make-crop').disabled=true;});
  async function cropImage(){
    if(!state.image||!state.selection)throw Error('Select an image region first.');
    const v=state.selection, crop=document.createElement('canvas');crop.width=v.width;crop.height=v.height;
    const cc=crop.getContext('2d');cc.drawImage(state.image,v.x,v.y,v.width,v.height,0,0,v.width,v.height);
    const blob=await new Promise((resolve,reject)=>crop.toBlob(b=>b?resolve(b):reject(Error('Crop encoding failed')),'image/png'));
    const label=c.cleanText(el('crop-label').value,60),hash=await sha256(blob);
    const record=c.normalizeVariant({...v,label,sha256:hash},state.original);
    if(state.variants.some(x=>x.label.toLowerCase()===record.label.toLowerCase()))throw Error('Choose a unique crop label.');
    state.variants.push(record);invalidateReview();download(blob,`${el('case-id').value || 'VEIL'}-${label.replace(/[^a-z0-9-]/gi,'_')}.png`);
    renderCrops();renderAssessment();status('Crop downloaded locally. Upload it manually to Lens, TinEye or Bing to search that region.');
  }
  function renderCrops(){const list=el('crop-list');list.replaceChildren();for(const v of state.variants){const li=document.createElement('li');li.textContent=`${v.label}: x=${v.x}, y=${v.y}, ${v.width}×${v.height}, SHA-256 ${v.sha256}`;list.append(li);}}
  function setChecks(){const host=el('checks');for(const [key,label] of c.CHECKS){state.checks[key]='not_checked';const wrap=document.createElement('label');wrap.textContent=label;const select=document.createElement('select');select.dataset.check=key;for(const [value,title] of [['not_checked','Not checked'],['checked_no_match','Checked — no match'],['checked_matches','Checked — matches found'],['unavailable','Unavailable / blocked']]){const o=document.createElement('option');o.value=value;o.textContent=title;select.append(o);}select.addEventListener('change',()=>{state.checks[key]=select.value;invalidateReview();renderAssessment();});wrap.append(select);host.append(wrap);}}
  function addSource(form){
    const d=new FormData(form), s={id:'SRC-'+String(state.sources.length+1).padStart(3,'0'),url:d.get('url'),sourceType:d.get('sourceType'),matchType:d.get('matchType'),publishedDate:d.get('publishedDate'),dateBasis:d.get('dateBasis'),caption:d.get('caption'),note:d.get('note'),searchProvider:d.get('searchProvider'),region:d.get('region'),creatorClaim:d.get('creatorClaim'),observedAt:c.nowISO()};
    while(state.sources.some(row=>row.id===s.id)){s.id='SRC-'+String(Number(s.id.slice(4))+1).padStart(3,'0');}
    const valid=c.normalizeSource(s,state.sources);state.sources.push(valid);invalidateReview();form.reset();renderSources();renderAssessment();status('Source logged as a reported match, not established origin.');
  }
  function renderSources(){const box=el('source-list');box.replaceChildren();for(const s of state.sources){const article=document.createElement('article');const a=document.createElement('a');a.textContent=s.id+' · '+s.url;a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';const p=document.createElement('p');p.textContent=`${s.matchType}; ${s.publishedDate||'undated'} (${s.dateBasis}); ${s.caption||s.note}`;article.append(a,p);box.append(article);}}
  function readReport(){return c.buildReport({caseId:el('case-id').value,original:state.original,variants:state.variants,sources:state.sources,checks:state.checks,review:state.review});}
  function renderAssessment(){if(!state.original){el('assessment').textContent='Load an image to begin a report.';return;}try{const r=readReport(), a=r.assessment, e=a.earliestTraceableMatch, d=resume.diagnostics(r);el('assessment').textContent=`${r.sources.length} attributed source(s); ${r.variants.length} cropped variant(s). ${e?`Earliest dated matching page entered: ${e.date}, ${e.id} (${e.dateBasis}). NOT proof of creation date or origin.`:'No adequately dated visual match entered.'} ${a.captionsDiffer?'Captions conflict. ':''}${a.missingChecks.length} searches incomplete/unavailable. Status: ${r.status}.`;el('source-diagnostics').textContent=`Archive capture (not publication): ${d.earliestArchiveCapture?.date||'unknown'}; earliest dated publisher/corroborated page: ${d.earliestPublisherOrCorroboratedDate?.date||'unknown'}; repeated URLs: ${d.repeatedSourceUrls}; distinct hostnames: ${d.hostGroups.length}. Website counts do NOT establish independent sources.`;}catch(err){el('assessment').textContent=err.message;}}
  function exportReport(format){const r=readReport(),d=resume.diagnostics(r);const appendix='\n## Source-history checks\n- Earliest archive capture (not publication): '+(d.earliestArchiveCapture?.date||'unknown')+'\n- Earliest publisher/corroborated page: '+(d.earliestPublisherOrCorroboratedDate?.date||'unknown')+'\n- Repeated URLs: '+d.repeatedSourceUrls+'\n- Distinct hostnames: '+d.hostGroups.length+' (not independent witnesses)\n\n'+d.cautions.map(x=>'- '+x).join('\n')+'\n';const body=format==='md'?c.markdown(r)+appendix:JSON.stringify({...r,sourceDiagnostics:d},null,2)+'\n';download(new Blob([body],{type:format==='md'?'text/markdown':'application/json'}),`${r.caseId}-image-origin.${format}`);status('Private draft exported locally. Preserve original and source records.');}
  el('import-json').addEventListener('change',async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>resume.MAX_JSON)throw Error('Draft exceeds the 512 KB import limit.');pendingImport=resume.parseDraft(await file.text());el('import-status').textContent=`Pending ${pendingImport.caseId}: supply the matching original image. Prior reviewer approval is discarded.`;state.original=null;state.image=null;state.sources=[];state.variants=[];invalidateReview();el('preview-wrap').hidden=true;renderSources();renderCrops();renderAssessment();status('Draft parsed, but not yet restored. Choose the matching original image to continue.');}catch(err){pendingImport=null;fail(err);}});
  el('original-file').addEventListener('change',async e=>{try{await loadImage(e.target.files[0]);}catch(err){fail(err);}});
  el('make-crop').addEventListener('click',async()=>{try{await cropImage();}catch(err){fail(err);}});
  el('query').addEventListener('input',()=>{const host=el('query-links');host.replaceChildren();for(const q of c.makeQueries(el('query').value)){const a=document.createElement('a');a.href=q.url;a.textContent=q.label;a.target='_blank';a.rel='noopener noreferrer';host.append(a);}});
  el('source-form').addEventListener('submit',e=>{e.preventDefault();try{if(!state.original)throw Error('Register an original image first.');addSource(e.target);}catch(err){fail(err);}});
  el('review-record').addEventListener('click',()=>{const name=c.cleanText(el('reviewer').value,120);if(!name){status('Enter a human reviewer name to record a review.',true);return;}state.review={name,note:el('review-note').value,reviewedAt:c.nowISO()};renderAssessment();status('Review recorded as a self-declared name, NOT an authenticated approval.');});
  el('export-json').addEventListener('click',()=>{try{exportReport('json');}catch(err){fail(err);}});
  el('export-md').addEventListener('click',()=>{try{exportReport('md');}catch(err){fail(err);}});
  el('case-id').addEventListener('input',()=>{invalidateReview();renderAssessment();});
  setChecks();
})();
