'use strict';
(() => {
  const token = document.querySelector('meta[name="signal-session"]').content;
  const $ = (id) => document.getElementById(id);
  const face = $('face'), portrait = $('portrait'), activity = $('activity');
  const messages = $('messages'), question = $('question'), send = $('send');
  const descriptions = {
    neutral: ['ATTENTIVE', 'Calm • Approachable'],
    focused: ['THINKING', 'Thoughtful • Analytical'],
    amused: ['AMUSED', 'Wry • Friendly'],
    excited: ['CURIOUS', 'Engaged • Curious'],
    concentrating: ['FOCUSED', 'Careful • Evidence-first'],
    reassuring: ['REASSURING', 'Warm • Supportive']
  };
  let currentExpression = 'neutral', answering = false, voiceOn = false, speaking = false;
  let listening = false, listenRequestPending = false;
  const motionAllowed = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Gentle illustration only: preserve photographic mouth pixels and never fake phoneme alignment.
  // Small, irregular rests are less distracting than a six-frame mechanical loop.
  const speechFrames = [0,1,0,2,1,0,1,3,1,0,2,0,1];
  const speechDelays = [225,270,190,310,235,340,180,280,215,260,360];
  const motionAssets = [0,1,2,3].map(n => '/face_assets/speech_' + n + '.webp');
  let speechFrameIndex=0, previewMotion=false, motionEnabled=true;
  let speechTickTimer=null, previewTimeout=null;
  // Preload into the browser cache to prevent expression flashes during movement.
  motionAssets.forEach(src => { const img = new Image(); img.src = src; });
  let currentImage='';
  let lastExpression = 'neutral', lastActivityTime = Date.now();
  const pose = (name, speakingNow = false) => {
    if (!(name in descriptions)) name = 'neutral';
    currentExpression = name;
    // Keep non-neutral expressions completely stable during speech.
    // v0.6 switched the whole face to neutral on every reply, a noticeable jump.
    const moving = speakingNow && motionAllowed && motionEnabled && name === 'neutral';
    const imageName = moving ? 'speech_' + speechFrames[speechFrameIndex % speechFrames.length] : name;
    if (currentImage !== imageName) {
      face.src = '/face_assets/' + imageName + '.webp';
      currentImage = imageName;
    }
    portrait.dataset.state = speakingNow ? 'speaking' : (answering ? 'thinking' : name);
    $('expression-label').textContent = speakingNow ? (previewMotion ? 'MOTION PREVIEW' : 'SPEAKING') : descriptions[name][0];
    $('expression-description').textContent = descriptions[name][1];
  };
  const setActivity = (text) => { activity.textContent = text; lastActivityTime = Date.now(); };
  const addMessage = (speaker, content, detail = '') => {
    const el = document.createElement('div');
    el.className = 'message ' + speaker;
    const who = document.createElement('span'); who.className = 'sender';
    who.textContent = speaker === 'user' ? 'YOU' : (speaker === 'error' ? 'SYSTEM' : 'SIGNAL');
    const p = document.createElement('p'); p.textContent = content;
    el.append(who, p);
    if (detail) { const foot = document.createElement('span'); foot.className = 'message-foot'; foot.textContent = detail; el.append(foot); }
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  };
  const request = async (route, data = null) => {
    const opts = {headers:{'X-SIGNAL-Token':token},cache:'no-store'};
    if (data !== null) { opts.method='POST'; opts.headers['Content-Type']='application/json'; opts.body=JSON.stringify(data); }
    const response = await fetch(route, opts);
    let result;
    try { result=await response.json(); } catch { throw Error('The local SIGNAL server returned an unexpected response.'); }
    if (!response.ok) throw Error(result.error || 'Local service error '+response.status);
    return result;
  };
  const chooseExpression = (answer) => {
    // A restrained, transparent heuristic—not machine emotion or speech recognition.
    const lower = answer.toLowerCase();
    if (/unsafe|fault|integrity|uncertain|unverified|risk|cannot establish|error/.test(lower)) return 'concentrating';
    if (/door again|hair.*feature|unreasonably ordinary/.test(lower)) return 'amused';
    if (/you can|let's try|we can test|good to see/.test(lower)) return 'reassuring';
    if (/fascinating|curious|experiment/.test(lower)) return 'excited';
    return 'neutral';
  };
  const syncStatus = (state) => {
    const demo = state.mode === 'demo';
    $('mode').classList.toggle('demo',demo);
    $('mode').textContent = demo ? 'SCRIPTED VISUAL DEMO' : 'LOCAL OLLAMA MODEL';
    $('connection').textContent = demo ? 'No AI model in demo mode' : 'Local model • Windows computer';
    voiceOn = Boolean(state.voice_enabled);
    $('voice-toggle').textContent = voiceOn ? 'Disable voice' : 'Enable voice';
    $('voice-toggle').setAttribute('aria-pressed',String(voiceOn));
    speaking = Boolean(state.speaking);
    $('voice-status').textContent = previewMotion ? 'Silent character movement preview. No microphone or speech is active.' : (speaking ? 'Speaking locally using Windows speech.' :
       (voiceOn ? 'Voice enabled. Replies will be spoken on this computer.' : 'Voice starts OFF. Face motion responds to speech activity, not phonemes.'));
    if (state.mtc_loaded) $('mtc-state').textContent = 'Loaded session: '+(state.session_id || 'MTC');
    else $('mtc-state').textContent = 'No session loaded';
    if (listening) { pose('excited'); portrait.dataset.state='listening'; }
    else pose(previewMotion ? 'neutral' : lastExpression, speaking || previewMotion);
    ensureMotion();
  };
  const refresh = async () => {
    try { const state = await request('/api/status'); syncStatus(state); }
    catch (err) { $('connection').textContent='Local service disconnected'; $('voice-status').textContent=err.message; }
  };
  async function submitMessage(text, origin='chat') {
    if (answering || listening || !text.trim()) return;
    answering=true; send.disabled=true; question.disabled=true;
    addMessage('user',text);
    question.value=''; lastExpression='focused'; pose('focused'); setActivity('Analyzing locally…');
    try {
      const reply = await request('/api/chat',{message:text});
      addMessage('signal',reply.reply,reply.mode==='demo'?'Scripted UI demonstration • no generated AI response':'Local Ollama response • verify research claims');
      lastExpression=chooseExpression(reply.reply);
      answering=false;
      syncStatus(reply.status);
      setActivity(origin==='mtc' ? 'MTC log review returned' : 'Response complete');
      if (origin === 'mtc') {refreshNotes();refreshScanner();}
    } catch (err) {
      answering=false; lastExpression='concentrating'; pose(lastExpression);
      addMessage('error',err.message,'Local server error • no cloud fallback');
      setActivity('Unable to respond');
    } finally {
      send.disabled=listening; question.disabled=listening; question.focus();
    }
  }
  const micButton = $('mic-button'), micNote = $('mic-note');
  const micState = (active, note, state='idle') => {
    listening = active;
    micButton.textContent = active ? '■ Stop listening' : '🎙 Start listening';
    micButton.setAttribute('aria-pressed', String(active));
    micNote.textContent = note;
    micNote.dataset.state = state;
    send.disabled = answering || active;
    question.disabled = answering || active;
    if (active) { pose('excited'); portrait.dataset.state='listening'; }
    else pose(previewMotion ? 'neutral' : lastExpression, speaking || previewMotion);
  };
  async function listenOnce() {
    if (listenRequestPending || answering) return;
    listenRequestPending=true;
    try {
      if (listening) {
        await request('/api/listen', {action:'stop'});
        micState(false,'Microphone OFF. No sound was saved.');
      } else {
        // Avoid locally synthesized SIGNAL speech being picked up as investigator input.
        if (speaking) await request('/api/voice',{action:'stop'});
        await request('/api/listen', {action:'start'});
        micState(true,'Listening locally for one phrase (up to 12 seconds). Click Stop to cancel.', 'listening');
      }
    } catch (err) {
      micState(false,'Microphone unavailable: '+err.message);
    } finally { listenRequestPending=false; }
  }
  micButton.addEventListener('click',listenOnce);
  async function pollListen() {
    if (!listening || listenRequestPending) return;
    try {
      const result=await request('/api/listen/status');
      if (result.state==='listening') return;
      if (result.state==='ready' && typeof result.transcript==='string' && result.transcript.trim()) {
        // Never auto-submit; operator must inspect/approve recognition text.
        question.value=result.transcript.slice(0,700);
        micState(false,'Microphone OFF. Review the recognized text, then click Send.');
        question.focus();
      } else if (result.state==='empty' || result.state==='error') {
        micState(false,'Microphone OFF. '+(result.message || 'No phrase recognized. Try again or type.'));
      } else micState(false,'Microphone OFF.');
    } catch(err) { micState(false,'Mic status unavailable: '+err.message); }
  }
  window.setInterval(pollListen,500);
  $('chat-form').addEventListener('submit',(e)=>{e.preventDefault();submitMessage(question.value)});
  question.addEventListener('keydown',(e)=>{if(e.key==='Enter' && !e.shiftKey){e.preventDefault();submitMessage(question.value)}});
  document.querySelectorAll('.suggestion').forEach(b=>b.addEventListener('click',()=>{question.value=b.dataset.prompt;question.focus()}));
  async function voiceCommand(action, extra = {}) {
    try {
      const response=await request('/api/voice',{action,...extra});
      syncStatus(response.status); setActivity(response.reply);
    } catch(err) { addMessage('error',err.message);setActivity('Voice operation unavailable'); }
  }
  // Only animate while Windows speech is truly active, or during explicit preview.
  // No always-on animation timer: it stops scheduling frames while idle.
  const speechTick = () => {
    speechTickTimer = null;
    if (!motionAllowed || !motionEnabled || !(speaking || previewMotion)) return;
    speechFrameIndex = (speechFrameIndex + 1) % speechFrames.length;
    pose(previewMotion ? 'neutral' : lastExpression, true);
    speechTickTimer = window.setTimeout(speechTick, speechDelays[speechFrameIndex % speechDelays.length]);
  };
  const ensureMotion = () => {
    if (!motionAllowed || !motionEnabled || !(speaking || previewMotion)) {
      if (speechTickTimer !== null) window.clearTimeout(speechTickTimer);
      speechTickTimer = null;
      speechFrameIndex = 0;
      pose(lastExpression,speaking && !previewMotion);
    } else if (speechTickTimer === null) {
      speechTickTimer = window.setTimeout(speechTick, speechDelays[0]);
    }
  };
  $('motion-preview').addEventListener('click',() => {
    if (!motionAllowed || !motionEnabled) {
      setActivity('Face motion disabled. Enable it first, or review Windows reduced-motion settings.');
      return;
    }
    if (previewTimeout) window.clearTimeout(previewTimeout);
    previewMotion = !previewMotion;
    speechFrameIndex=0;
    $('motion-preview').setAttribute('aria-pressed',String(previewMotion));
    $('motion-preview').textContent=previewMotion ? 'Stop preview' : 'Preview face movement';
    if (previewMotion) {
      setActivity('Silent facial movement preview (no audio)');
      previewTimeout=window.setTimeout(() => {
        previewMotion=false;previewTimeout=null;
        $('motion-preview').setAttribute('aria-pressed','false');
        $('motion-preview').textContent='Preview face movement';
        pose(lastExpression,speaking);
        ensureMotion();
        setActivity('Ready for research');
      }, 4500);
    }
    pose(previewMotion ? 'neutral' : lastExpression,speaking || previewMotion);
    ensureMotion();
  });
  $('motion-toggle').addEventListener('click', () => {
    motionEnabled = !motionEnabled;
    if (!motionEnabled) {
      previewMotion = false;
      if (previewTimeout !== null) window.clearTimeout(previewTimeout);
      previewTimeout = null;
      $('motion-preview').textContent = 'Preview face movement';
      $('motion-preview').setAttribute('aria-pressed','false');
    }
    $('motion-toggle').textContent = motionEnabled ? 'Motion: subtle' : 'Motion: still';
    $('motion-toggle').setAttribute('aria-pressed',String(motionEnabled));
    ensureMotion();
    setActivity(motionEnabled ? 'Subtle motion enabled' : 'Portrait movement paused');
  });
  $('voice-toggle').addEventListener('click',()=>voiceCommand(voiceOn?'off':'on'));
  $('voice-stop').addEventListener('click',()=>voiceCommand('stop'));
  $('rate').addEventListener('change',(e)=>voiceCommand('rate',{rate:Number(e.target.value)}));
  $('mtc-form').addEventListener('submit',(e)=>{
    e.preventDefault();
    const path = $('mtc-path').value.trim();
    if (!path) { $('mtc-state').textContent='Enter the local session folder path.';return; }
    $('mtc-state').textContent='Verifying local log files…';
    submitMessage('/mtc "'+path.replace(/"/g,'')+'"','mtc');
  });
  // v0.8: diagnostics run only when operator clicks Check; no background network probes.
  const diagOutput = $('diagnostics-results');
  const diagButton = $('check-setup');
  diagButton.addEventListener('click', async () => {
    diagButton.disabled = true;
    diagOutput.textContent = 'Checking local Ollama and installed Windows capabilities…';
    try {
      const result = await request('/api/diagnostics');
      if (result.mode === 'scripted-demo') {
        diagOutput.textContent = result.message;
      } else {
        diagOutput.replaceChildren();
        for (const [label,key] of [['Ollama','ollama'],['Windows voice','voice'],['Offline dictation','microphone']]) {
          const entry = result[key] || {status:'unknown',message:'No result'};
          const div = document.createElement('div');
          div.dataset.result = entry.status;
          div.textContent = label + ': ' + entry.status.toUpperCase() + ' — ' + entry.message;
          diagOutput.append(div);
        }
        const p = document.createElement('p');
        p.textContent = result.notes + ' ' + result.next_steps;
        diagOutput.append(p);
      }
    } catch (err) { diagOutput.textContent = 'Readiness check failed: ' + err.message; }
    finally { diagButton.disabled = false; }
  });
  // v0.10: one-click opt-in local model smoke test; does not enter chat history.
  $('model-check').addEventListener('click', async () => {
    const button = $('model-check'), output = $('model-check-results');
    button.disabled=true;
    output.textContent='Testing local Ollama with a fixed evidence-limits question…';
    try {
      const check = await request('/api/model-check', {});
      output.textContent = 'Local model ' + check.model + ' responded in ' +
        (check.elapsed_ms / 1000).toFixed(1) + ' seconds.\n' +
        'Response (not independently verified): ' + check.reply_preview + '\n' + check.limitations;
      setActivity('Local Ollama conversation check completed');
    } catch(err) {output.textContent='Local Ollama check failed: '+err.message;}
    finally{button.disabled=false;}
  });
  // v0.9: opt-in, read-only acoustic scanner summary, not WAV/EVP analysis.
  const scannerState = $('scanner-state'), scannerList = $('scanner-list');
  function clearScannerDisplay(message) {
    scannerList.replaceChildren();
    scannerState.textContent = message;
  }
  function renderScannerReview(review) {
    scannerList.replaceChildren();
    if (!review) {clearScannerDisplay('No scanner report loaded. MTC evidence logs and original audio remain unchanged.');return;}
    scannerState.textContent = review.raw_candidates + ' raw scanner flags grouped into ' +
      review.review_windows + ' overlapping review windows. These are acoustic changes, not identified voices or causes.';
    const groups = Array.isArray(review.groups) ? review.groups.slice(0,100) : [];
    for (const group of groups) {
      const card = document.createElement('div'); card.className = 'scanner-item';
      const label = document.createElement('span');
      label.textContent = group.review_id + ' · ' + formatClock(group.start) + ' – ' + formatClock(group.end);
      const details = document.createElement('small');
      details.textContent = group.count + ' scanner flag(s) · acoustic score ' + group.score;
      const select = document.createElement('button'); select.type = 'button'; select.textContent = 'Note this time';
      select.addEventListener('click', () => {
        $('review-notebook').open = true;
        $('review-time').value = String(group.start);
        $('review-label').value = 'needs_review';
        $('review-text').focus();
        reviewState.textContent = 'Selected ' + group.review_id + '. Listen in the separate MTC waveform viewer, then enter your observation here.';
      });
      card.append(label, details, select); scannerList.append(card);
    }
    if (review.warnings?.length) {
      const w = document.createElement('p'); w.textContent = 'Scanner warnings: ' + review.warnings.join(' | '); scannerList.prepend(w);
    }
  }
  async function refreshScanner() {
    try { const data = await request('/api/review'); renderScannerReview(data.review); }
    catch(err) {clearScannerDisplay('Scanner summary unavailable: ' + err.message);}
  }
  $('scanner-form').addEventListener('submit',async(e)=>{
    e.preventDefault();
    const path = $('scanner-path').value.trim();
    if (!path) {scannerState.textContent = 'Enter the complete review_summary.json file path.';return;}
    scannerState.textContent = 'Loading scanner report locally and checking its session and duration…';
    try {
      const data=await request('/api/review',{action:'load',path});
      renderScannerReview(data.review);
      setActivity('Scanner intervals loaded for review');
    } catch(err) { scannerState.textContent = 'Could not load scanner report: ' + err.message; }
  });
  $('scanner-latest').addEventListener('click',async()=>{
    scannerState.textContent = 'Checking existing local VEIL_Reviews reports for this session…';
    try {const data=await request('/api/review',{action:'latest'});renderScannerReview(data.review);
      setActivity('Matching MTC scanner report loaded');}
    catch(err) {scannerState.textContent = 'Cannot find matching scanner report: ' + err.message;}
  });
  $('scanner-clear').addEventListener('click',async()=>{
    try {await request('/api/review',{action:'clear'});renderScannerReview(null);}
    catch(err) {scannerState.textContent = err.message;}
  });
  $('scanner-refresh').addEventListener('click',refreshScanner);
  $('scanner-review').addEventListener('toggle',()=>{if($('scanner-review').open)refreshScanner();});
  const reviewState = $('review-state'), reviewList = $('review-list');
  function formatClock(seconds) {
    const n = Number(seconds);
    const h = Math.floor(n / 3600), m = Math.floor(n % 3600 / 60), s = (n % 60).toFixed(3).padStart(6,'0');
    return String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0') + ':' + s;
  }
  async function refreshNotes() {
    try {
      const data = await request('/api/notes');
      reviewList.replaceChildren();
      if (!data.notes.length) { reviewState.textContent = 'No observations saved for this loaded session.'; return; }
      for (const item of data.notes.slice().reverse()) {
        const box = document.createElement('div'); box.className = 'review-entry';
        const head = document.createElement('b');
        head.textContent = formatClock(item.seconds_from_start) + ' · ' + item.classification.replaceAll('_', ' ');
        const note = document.createElement('span'); note.textContent = ' — ' + item.note;
        box.append(head, note); reviewList.append(box);
      }
      reviewState.textContent = data.notes.length + ' most recent manual observations shown (up to 100).';
    } catch (err) { reviewState.textContent = err.message; }
  }
  $('note-form').addEventListener('submit',async(e) => {
    e.preventDefault();
    const raw = $('review-time').value;
    if (!raw) {reviewState.textContent='Enter a time in seconds.';return;}
    const time_s = Number(raw);
    const note = $('review-text').value.trim();
    if (!note) {reviewState.textContent='Write the observation before saving.';return;}
    reviewState.textContent = 'Saving investigator note locally…';
    try {
      await request('/api/notes',{time_s,classification:$('review-label').value,note});
      $('review-text').value = '';
      await refreshNotes();
      setActivity('Investigator note saved');
    } catch(err) {reviewState.textContent = 'Unable to save note: ' + err.message;}
  });
  $('review-notebook').addEventListener('toggle', () => {if ($('review-notebook').open) refreshNotes();});
  // v0.10: explicit read-only packet export. Auth stays in custom loopback header.
  async function exportPacket(kind) {
    const state = $('packet-state');
    const button = $(kind === 'json' ? 'export-json' : 'export-html');
    button.disabled = true;
    state.textContent = 'Preparing local research record (original evidence is unchanged)…';
    try {
      const response = await fetch('/api/export?format=' + kind,
        {headers:{'X-SIGNAL-Token':token}, cache:'no-store'});
      if (!response.ok) {
        let problem = 'Export returned error ' + response.status;
        try {const info=await response.json(); problem=info.error || problem;} catch {};
        throw Error(problem);
      }
      const disposition = response.headers.get('Content-Disposition') || '';
      const match = disposition.match(/filename="(SIGNAL_MTC_[A-Za-z0-9_.-]+\.(?:json|html))"/);
      if (!match) throw Error('Unexpected local export filename');
      const blob = await response.blob();
      if (blob.size > 1800000) throw Error('Review packet exceeds export size limit');
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.href = url; link.download = match[1];
      document.body.appendChild(link); link.click(); link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 2000);
      state.textContent = 'Saved ' + match[1] + ' to your browser downloads. The original evidence was not modified.';
      setActivity('Review packet exported');
    } catch (err) {state.textContent = 'Packet export unavailable: ' + err.message;}
    finally {button.disabled = false;}
  }
  $('export-json').addEventListener('click',()=>exportPacket('json'));
  $('export-html').addEventListener('click',()=>exportPacket('html'));
  // Poll the local Windows speech process, allowing the visual state to return to idle
  // after the utterance finishes. This is expressive animation, not phoneme lip sync.
  window.setInterval(refresh,750);
  refresh();
})();
