/* SIGNAL v0.6: scripted visitor conversation & optional microphone preview.
   This is NOT generative AI, live lab hardware, or a remote data service. */
(() => {
  'use strict';
  const form = document.getElementById('signal-question-form');
  const field = document.getElementById('signal-question');
  const micButton = document.getElementById('signal-microphone');
  const status = document.getElementById('signal-question-status');
  if (!form || !field || !micButton || !status) return;

  const topics = [
    { key: 'focus', match: /\b(squirl|squirls|squirrel|squirrels|distract|focus|off.track|priority|priorities|remind)\b/i,
      reply: "Say No to Squirls! Ah, yes, my favorite anti-distraction protocol. One task, one next step. What were we trying to accomplish? For now I can help you practice staying on topic here; a future authorized lab assistant could track tasks and remind a researcher where they left off.",
      more: "Our future focus helper would keep a visible task list and give gentle reminders, not silently override anyone's decisions. Researchers stay in control." },
    { key: 'safety', match: /\b(panic.box|all.clear|emergency|alarm|button|trigger)\b/i,
      reply: "The Panic Box is planned as a field recorder with continuous baseline capture. In the proposed system, an event trigger switches to FULL mode, and only an offsite human operator can issue ALL CLEAR. I'm demonstrating the idea, not monitoring real devices.",
      more: "The important engineering checks are timestamps, independent recording, battery backup, an audit trail, and verified operator authorization for ALL CLEAR." },
    { key: 'mtc', match: /\b(mtc|evp|voice.record|audio.record|unattended|playback)\b/i,
      reply: "The MTC is VEIL's proposed unattended audio-question system. It plays prerecorded questions aloud while a room microphone records the actual sound, including quiet periods. A second independent recording helps check what was captured.",
      more: "Before interpreting a sound, we'd inspect the original WAV file, room noise, playback timing, nearby devices, and blind control recordings. A voice-like sound does not prove its source." },
    { key: 'anomaly', match: /\b(anomal|ghost|paranormal|temperature|sensor|proof|evidence|skeptic|scientific|experiment)\b/i,
      reply: "An unusual observation is a question, not a conclusion! I'd help a researcher preserve the original reading, check equipment and environmental conditions, and compare controls. The human team decides what the evidence supports.",
      more: "A real assistant should report clock uncertainty, calibration, missing readings and alternate explanations before claiming that two events are related." },
    { key: 'voice', match: /\b(voice|hear|sound|speak|talk|microphone|mic|accent)\b/i,
      reply: "Testing, testing—one, two, three! I'm still finding my voice. Enable spoken replies above and try the Voice Discovery Studio. My voice currently comes from your browser, so the available choices vary by device.",
      more: "The goal is a consistent, recognizable voice and natural back-and-forth. This webpage uses guided replies, not a live language model, and microphone transcription may use your browser's speech service." },
    { key: 'memory', match: /\b(memory|remember|forget|know.me|my.name|conversation|private|privacy|store|data)\b/i,
      reply: "For this guided preview, I only keep the last topic while this page stays open. I don't retain your questions on a server or build a personal profile. Future lab memory should be opt-in, reviewable, and controlled by the researcher.",
      more: "Future memory would distinguish a research note from a casual conversation. It would also log who said what and require permission before sensitive actions." },
    { key: 'role', match: /\b(lab.assistant|companion|future|plan|can.you.do|what.do.you.do|abilities|capabilit|help.with|ai)\b/i,
      reply: "My future job at VEIL is to be an attentive lab companion: check acquisition status, timestamp notes, organize experiments, flag possible equipment faults, and help people review evidence. I won't replace scientific judgment or claim discoveries I cannot verify.",
      more: "Picture this: hands-free notes, synchronized audio/video/sensor timelines, warnings about missing data, and a draft report that a human reviews before publication. Those integrations are planned, not operating on this webpage." },
    { key: 'hello', match: /\b(hello|hi|hey|good.morning|good.evening|who.are.you|name)\b/i,
      reply: "Oh! Hello there. I'm SIGNAL—VEIL's rather eccentric digital host. Still tuning the transmission, but my rule is simple: curiosity opens the door; evidence gets the final word. What would you like to explore?",
      more: "I was imagined as a guide who learns through documented, human-approved development. I am a fictional host today, and a prototype direction for a future practical assistant." }
  ];
  let lastTopic = null;
  let recognition = null;
  let listening = false;

  function chooseResponse(question) {
    const q = question.trim();
    if (/^(more|tell me more|how so|explain|go on|continue|why)[\s?.!]*$/i.test(q) && lastTopic) {
      return lastTopic.more;
    }
    if (/\b(what did we discuss|what was i asking|where were we|last topic)\b/i.test(q)) {
      return lastTopic
        ? "We were talking about " + lastTopic.key.replace('role', 'my future lab role') + ". Want to explore that further? This short-term topic memory disappears when you leave this page."
        : "We haven't explored a topic together yet. Try asking what I could do in the lab.";
    }
    const match = topics.find(t => t.match.test(q));
    if (match) { lastTopic = match; return match.reply; }
    return "A fascinating question! Unfortunately this version of me uses guided, authored replies, so I can't answer that one reliably yet. Ask about my future lab role, the MTC, Panic Box, evidence controls, voice, memory, or Say No to Squirls. Real conversation is a development goal, not a feature I'm pretending to have today.";
  }

  function submitQuestion(value) {
    const question = String(value || '').trim().slice(0, 220);
    if (!question) { status.textContent = 'Type or dictate a question first.'; field.focus(); return; }
    const bridge = window.signalConversationBridge;
    if (!bridge || typeof bridge.post !== 'function') {
      status.textContent = "SIGNAL's conversation display is not ready. Refresh the page to try again.";
      return;
    }
    bridge.post(question, chooseResponse(question));
    field.value = '';
    status.textContent = 'Guided reply shown above. Spoken replies are optional.';
  }

  form.addEventListener('submit', e => {
    e.preventDefault();
    submitQuestion(field.value);
  });
  document.querySelectorAll('[data-signal-prompt]').forEach(button => {
    button.addEventListener('click', () => submitQuestion(button.getAttribute('data-signal-prompt')));
  });

  // Browsers may perform recognition remotely. Only start on an explicit click.
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    micButton.disabled = true;
    micButton.title = 'Microphone transcription is not supported by this browser. Typed questions still work.';
    micButton.textContent = 'Microphone unavailable';
    return;
  }
  micButton.addEventListener('click', () => {
    if (listening) { if (recognition) recognition.stop(); return; }
    try {
      recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.onstart = () => {
        listening = true;
        micButton.textContent = '■ Stop listening';
        status.textContent = "Microphone on. Your browser may use an online speech service. No transcript is sent to VEIL by this page.";
      };
      recognition.onresult = e => {
        const value = e.results && e.results[0] && e.results[0][0] && e.results[0][0].transcript;
        if (value) submitQuestion(value);
      };
      recognition.onerror = e => {
        status.textContent = 'Speech input unavailable (' + String(e.error || 'browser error') + '). You can still type your question.';
      };
      recognition.onend = () => {
        listening = false;
        micButton.textContent = '🎙 Ask by voice';
      };
      recognition.start();
    } catch (_error) {
      listening = false;
      micButton.textContent = '🎙 Ask by voice';
      status.textContent = 'Microphone could not start. Try typing your question instead.';
    }
  });
  window.addEventListener('pagehide', () => {
    if (recognition && listening) recognition.abort();
  });
})();