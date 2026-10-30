# SIGNAL desktop v0.14 — Responsive audio controls

## Problem and behavior

Previously, every voice and microphone operation waited for the same lock as a
model reply. A slow model could reject Stop speaking, Disable voice, and Stop
listening as busy. Those three deactivation actions now operate independently
of generation after the same authentication and request validation.

WindowsVoice now serializes process creation, stopping, disabling and rate changes
with its own reentrant lock. Disabling voice during a reply suppresses the reply's
later speech; it does not cancel the text reply. Stop speaking stops current audio
only; voice remains enabled for subsequent replies. Stop reply is a separate
existing best-effort generation cancellation control.

Start listening stops SIGNAL's speech server-side before opening recognition.
Chat generation and the voice test reject requests while a microphone attempt is
active, including requests from another tab. Start/enable/test operations still
use the generation lock; no automatic audio activation is introduced.

The interface adds **Test voice**, which plays the existing short phrase only
after voice has been enabled. If a microphone stop or status check fails, the UI
keeps the microphone's status uncertain and leaves Stop listening available. It
does not falsely declare the microphone off or auto-submit recognized words.

## Verification

- 156 Python tests passed, including seven new concurrent HTTP tests and two new
  speech-process race tests. These use loopback servers and simulated processes.
- Actual concurrent HTTP requests confirm a stop response arrives while a test
  model is still blocked, and disabling voice suppresses that reply's later audio.
- JavaScript syntax check passed.
- Lightweight DOM simulation passed model selection, failed microphone stop and
  status handling, stop retry, and explicit voice-test interactions.

No actual Windows microphone, speaker, recognizer, Ollama model, or rendered
browser layout was tested in this environment. Stop cannot be guaranteed when
the OS, local server, browser, or audio process itself is unresponsive. Local
process termination still has its existing bounded waits. This is a desktop
prototype, not a hardware emergency-stop or Panic Box ALL CLEAR system.

No paid APIs, model downloads, background microphone or cloud fallback were added.
See DESKTOP_TEST_STEPS.md for the first real-PC acceptance sequence.
