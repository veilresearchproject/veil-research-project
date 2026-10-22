/* SIGNAL Evidence Detective v0.5.1 — shared voice / animation; fictional cases, no telemetry or external API. */
(() => {
  'use strict';
  const cases = {
    audio: {
      observation: 'A 1.2-second click appears in two room microphones exactly when the air conditioner switches on.',
      options: ['Two recordings prove an unexplained entity made it.', 'Check HVAC timing, electronics and repeatable control recordings.', 'Discard the sound because it may be ordinary.', 'Two microphones independently prove its source.'],
      correct: 1,
      explanation: 'Both microphones can verify that a sound was captured. They cannot establish its cause. Examine HVAC timing, electrical coupling and repeatable controls before interpreting it.'
    },
    temperature: {
      observation: 'One thermal sensor drops 1.8°C while neighboring sensors stay steady. A nearby air vent may have opened.',
      options: ['The entire room cooled for an unexplained reason.', 'A cold entity must have approached the sensor.', 'Inspect sensor calibration, airflow and nearby instruments.', 'Ignore any reading from one sensor.'],
      correct: 2,
      explanation: 'A sensor change is a measurement, not an explanation. Airflow, placement, calibration and independent measurements may explain the change.'
    },
    dropout: {
      observation: 'An event button activates the Panic Box, but one camera has a 12-minute recording gap. Other channels continue.',
      options: ['Document the gap and preserve the original stream and fault logs.', 'A paranormal force must have interrupted the camera.', 'Assume no event occurred during the gap.', 'Reconstruct the missing footage with generative AI.'],
      correct: 0,
      explanation: 'Preserve and report the evidence gap. Missing footage cannot establish what happened, and a synthesized replacement must never masquerade as the original.'
    },
    clock: {
      observation: 'An MTC sound and EMF peak appear simultaneous, but their recorder clocks differ by 11 seconds with unmeasured drift.',
      options: ['The devices have proven the events were simultaneous.', 'Average the shown times and ignore uncertainty.', 'Suppress the drift from the final report.', 'Measure offset and drift before attempting correlation.'],
      correct: 3,
      explanation: 'Cross-instrument timing must include clock uncertainty. Correct and document time offset and drift before claiming two observations overlap.'
    },
    sham: {
      observation: 'An audio detector flags a strong peak during a blinded sham recording without any prerecorded question. Noise is elevated.',
      options: ['Call it a response to an unheard question.', 'Examine false-positive rate and recalibrate using sham controls.', 'Delete the sham to make results appear stronger.', 'Assume the recording was manipulated.'],
      correct: 1,
      explanation: 'A flagged control trial reveals a detector limitation. Examine noise and the false-positive rate, then validate any new threshold on unseen trials.'
    }
  };
  const chooser = document.getElementById('reason-case');
  const observation = document.getElementById('reason-observation');
  const answers = document.getElementById('reason-answers');
  const result = document.getElementById('reason-result');
  if (!chooser || !observation || !answers || !result) return;
  let lastAnswer = '';
  const caseKeys = Object.keys(cases);

  function render() {
    // Stop the previous case's speech before replacing its visible explanation.
    if (typeof stopVoice === 'function') stopVoice();
    else if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    const c = cases[chooser.value] || cases.audio;
    observation.textContent = c.observation;
    answers.replaceChildren();
    result.textContent = "Choose an interpretation to see SIGNAL's reasoning.";
    result.removeAttribute('data-status');
    lastAnswer = '';
    c.options.forEach((option, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = option;
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => {
        answers.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', 'false'));
        button.setAttribute('aria-pressed', 'true');
        const isCareful = index === c.correct;
        result.dataset.status = isCareful ? 'careful' : 'caution';
        lastAnswer = (isCareful ? "Excellent thinking. " : "Oops! I nearly jumped to a conclusion. ") + c.explanation;
        result.textContent = lastAnswer;
      });
      answers.append(button);
    });
  }
  chooser.addEventListener('change', render);
  document.getElementById('reason-next').addEventListener('click', () => {
    chooser.value = caseKeys[(caseKeys.indexOf(chooser.value) + 1) % caseKeys.length];
    render();
  });
  document.getElementById('reason-hear').addEventListener('click', () => {
    if (!lastAnswer) { result.textContent = 'Choose an interpretation first, then I can explain why.'; return; }
    const voiceToggle = document.getElementById('voice');
    if (!voiceToggle || voiceToggle.getAttribute('aria-pressed') !== 'true') {
      result.textContent = lastAnswer + ' Enable spoken replies above if you want to hear this explanation.';
      return;
    }
    if (!('speechSynthesis' in window) || typeof SpeechSynthesisUtterance !== 'function') {
      result.textContent = lastAnswer + ' Spoken replies are unavailable in this browser.';
      return;
    }
    // Use the main SIGNAL voice engine: selected character voice plus speaking animation.
    if (typeof speak === 'function') { speak(lastAnswer); return; }
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(lastAnswer);
        u.rate = .97; u.pitch = 1.05; u.volume = .9;
        window.speechSynthesis.speak(u);
      } catch (e) { result.textContent += ' Speech was unavailable in this browser.'; }
    }
  });
  render();
})();