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
  let lastExpression = 'neutral', lastActivityTime = Date.now();
  const pose = (name, speakingNow = false) => {
    if (!(name in descriptions)) name = 'neutral';
    if (currentExpression !== name) {
      currentExpression = name;
      face.src = '/face_assets/' + name + '.webp';
    }
    portrait.dataset.state = speakingNow ? 'speaking' : (answering ? 'thinking' : name);
    $('expression-label').textContent = speakingNow ? 'SPEAKING' : descriptions[name][0];
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
    $('voice-status').textContent = speaking ? 'Speaking locally using Windows speech.' :
       (voiceOn ? 'Voice enabled. Replies will be spoken on this computer.' : 'Voice starts OFF. Audio uses Windows speech on this PC.');
    if (state.mtc_loaded) $('mtc-state').textContent = 'Loaded session: '+(state.session_id || 'MTC');
    else $('mtc-state').textContent = 'No session loaded';
    if (listening) { pose('excited'); portrait.dataset.state='listening'; }
    else pose(lastExpression,speaking);
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
    else pose(lastExpression, speaking);
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
  // Poll the local Windows speech process, allowing the visual state to return to idle
  // after the utterance finishes. This is expressive animation, not phoneme lip sync.
  window.setInterval(refresh,750);
  refresh();
})();
