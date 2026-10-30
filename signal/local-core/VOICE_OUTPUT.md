# SIGNAL local Windows voice output — v0.18

SIGNAL uses optional Windows System.Speech text-to-speech with locally available
voices. It starts off. There are no paid speech services, downloads or voice cloning.

## Desktop test

1. Extract the complete ZIP and open START_HERE.bat.
2. Choose the scripted face demo to try audio without Ollama, or the live assistant
   when local Ollama is running. Demo dialogue remains scripted.
3. Open Choose an installed Windows voice, then List installed voices. Choose a
   name or System default and click Use selected voice. This does not enable speech
   or play a sample. The choice lasts until SIGNAL is restarted.
4. Click Enable voice, then Test voice. Check volume and Windows output device.
   Naturalness depends on the voices on your PC.
5. Stop speaking stops the current utterance. Disable voice also prevents a pending
   reply from speaking later. Stop reply is a separate best-effort model control.
   The speed selector adjusts the installed voice rate.

Changing the voice stops its current utterance. Invalid/unavailable selections
leave the old choice unchanged. If inventory fails, typing remains available.
Voice and microphone are separate opt-in controls.

The legacy console still supports /voice list, /voice on, /voice off, /voice stop,
/voice test and /voice rate N. Voice-name selection is in the desktop interface.
START_VOICE_TEST.bat remains a separate local test.

## Data and validation

Speech text and the chosen name travel as JSON through a local UTF-8 stdin pipe
into a fixed PowerShell script. They are not evaluated as code. Spoken text is
bounded to roughly 650 characters; the full model response stays on screen.

The voice can read inaccurate model output. Spoken claims about MTC logs do not
establish what was audible or what caused a sound. This is not custom SIGNAL
speech, voice cloning or phoneme lip synchronization.

185 Python tests and simulated interface checks passed. Real Windows voice
selection, speaker output and model performance still need desktop acceptance.
Run RUN_SIGNAL_TESTS.bat for Python tests. See V18_DEVELOPMENT_NOTES.md for limits.
