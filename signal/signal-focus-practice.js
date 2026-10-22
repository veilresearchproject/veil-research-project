/* SIGNAL v0.7 — guided focus + note-taking practice. Entirely ephemeral and visitor-controlled.
   Never a live sensor feed, scientific record, autonomous assistant, or external service. */
(() => {
  'use strict';
  const focusDisplay = document.getElementById('signal-focus-current');
  const notesDisplay = document.getElementById('signal-notes-count');
  const exportButton = document.getElementById('signal-export-session');
  const clearButton = document.getElementById('signal-clear-session');
  const exampleButton = document.getElementById('signal-focus-example');
  const status = document.getElementById('signal-question-status');
  if (!focusDisplay || !notesDisplay || !exportButton || !clearButton || !exampleButton || !status) return;

  let task = '';
  let notes = [];
  let events = [];
  let started = new Date();
  const stamp = () => new Date().toISOString();
  function log(type, detail) {
    events.push({ at: stamp(), type, detail: String(detail).slice(0, 500) });
    if (events.length > 150) events.shift();
  }
  function refresh() {
    focusDisplay.textContent = task || 'No practice task set';
    notesDisplay.textContent = notes.length + ' practice note' + (notes.length === 1 ? '' : 's') + ' this visit';
  }
  function respond(question) {
    const q = String(question || '').trim();
    let match = q.match(/^(?:focus on|set (?:my )?focus(?: to| on)?|my task is|start(?: a)? task(?: to)?|work on)\s*:?\s*(.+)$/i);
    if (match) {
      task = match[1].trim().slice(0, 120);
      log('PRACTICE FOCUS', task);
      refresh();
      return "SAY NO TO SQUIRLS! Today's practice task is: " + task + ". One step at a time. Ask 'what is my focus?' to get back on track, or say 'task complete' when you're done.";
    }
    if (/^(?:what(?:'s| is) my (?:focus|task)|what am i working on|say no to squirls)[\s?.!]*$/i.test(q)) {
      return task
        ? 'SAY NO TO SQUIRLS! Our practice focus is: ' + task + '. Shall we finish this before chasing another idea?'
        : "SAY NO TO SQUIRLS! Tell me one next action: 'focus on' followed by your task.";
    }
    if (/^(?:done|task complete|mark task done|finished (?:my|the) task)[\s?.!]*$/i.test(q)) {
      if (!task) return "No practice task is active. Try 'focus on checking the microphone'.";
      const finished = task;
      task = '';
      log('PRACTICE TASK MARKED COMPLETE', finished);
      refresh();
      return 'Marked complete in this practice session: ' + finished + '. Well done! That is a visitor-reported status, not verification of real work.';
    }
    match = q.match(/^(?:note|log note|research note|record note|take a note)\s*[:\-]\s*(.+)$/i);
    if (match) {
      const text = match[1].trim().slice(0, 180);
      notes.push({ at: stamp(), text });
      if (notes.length > 25) notes.shift();
      log('PRACTICE NOTE', text);
      refresh();
      return 'Practice note added: ' + text + '. This is not validated scientific data. Download the temporary practice log if you want to keep it.';
    }
    if (/^(?:show notes|what notes|recall notes|read notes)[\s?.!]*$/i.test(q)) {
      return notes.length
        ? 'Latest practice notes: ' + notes.slice(-3).map((n, i) => (i + 1) + ') ' + n.text).join('  ') + '. These exist only during this visit.'
        : "There are no notes yet. Try 'note: Test the room microphone'.";
    }
    return null;
  }
  function recordQuestion(question, response) {
    log('VISITOR', question);
    log('SIGNAL — GUIDED REPLY', response);
  }
  function prepareText() {
    const lines = [
      'SIGNAL — GUIDED LAB ASSISTANT PRACTICE',
      'FICTIONAL DEMONSTRATION — NOT AN ACTUAL INSTRUMENT RECORD',
      'Started (UTC): ' + started.toISOString(),
      'Exported (UTC): ' + stamp(),
      'Current focus: ' + (task || '(none)'),
      'Practice notes: ' + notes.length
    ];
    notes.forEach((n, i) => lines.push((i + 1) + '. [' + n.at + '] ' + n.text));
    lines.push('', 'Practice session transcript and actions:');
    events.forEach(e => lines.push('[' + e.at + '] ' + e.type + ': ' + e.detail));
    lines.push('', 'Source: Browser-only guided rehearsal. No real measurements, background monitoring, or AI inferences.');
    return lines.join('\n');
  }
  function clear() {
    if (typeof window.confirm === 'function' &&
        !window.confirm("Clear SIGNAL's temporary practice focus, notes, and visible conversation?")) return;
    task = ''; notes = []; events = []; started = new Date();
    refresh();
    if (window.signalConversationBridge?.clear) window.signalConversationBridge.clear();
    status.textContent = 'Temporary practice session cleared. No information was uploaded.';
  }
  exportButton.addEventListener('click', () => {
    if (typeof Blob !== 'function' || !window.URL || !window.URL.createObjectURL) {
      status.textContent = 'Local file download is unavailable in this browser.';
      return;
    }
    let url = null;
    try {
      url = window.URL.createObjectURL(new Blob([prepareText()], {type: 'text/plain;charset=utf-8'}));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'SIGNAL_practice_session.txt';
      link.style.display = 'none';
      document.body.append(link);
      link.click();
      link.remove();
      status.textContent = 'Practice log downloaded locally; it has not been sent to VEIL.';
    } catch (_error) {
      status.textContent = 'Local download failed; no data was sent.';
    } finally {
      if (url) setTimeout(() => window.URL.revokeObjectURL(url), 1000);
    }
  });
  clearButton.addEventListener('click', clear);
  exampleButton.addEventListener('click', () => {
    const question = document.getElementById('signal-question');
    const form = document.getElementById('signal-question-form');
    if (!question || !form) return;
    question.value = 'Focus on checking the MTC microphone before recording';
    if (typeof form.requestSubmit === 'function') form.requestSubmit();
    else question.focus();
  });
  refresh();
  window.signalPractice = Object.freeze({ respond, recordQuestion, prepareText });
})();