# SIGNAL Desktop v0.5 — Explicit local push-to-talk

**VEIL Research Project · October 30, 2026 · development prototype**

## Operation and consent

- Click **Start listening** for one deliberate attempt to recognize a short phrase using Windows `System.Speech.Recognition.SpeechRecognitionEngine`.
- A single recognition attempt listens for up to 12 seconds (with a bounded startup timeout).
- Click **Stop listening** to cancel and discard the pending result.
- Recognized words are placed in the text input, **never automatically sent** to SIGNAL or Ollama. Correct them and click **Send** yourself.
- The microphone is OFF until activated; there is no always-on mic, wake word, passive monitoring, cloud speech endpoint, saved audio, or automatic AI submission.
- SIGNAL's optional spoken replies are a separate opt-in. If speech is active when recording starts, speaking is stopped first.

## Windows support

Requires Windows, Windows PowerShell, a working **default recording microphone**, and a locally installed legacy Windows speech recognizer with dictation grammar and an appropriate language pack. This component may be missing on newer Windows installations. If absent, the feature fails closed and typing remains available. There is no cloud fallback or automatic external installation.

The recognized text is not evidence about environmental sounds or speakers, and does not analyze MTC WAV files.

## Privacy and security

Only the local server (`127.0.0.1`) can start recognition via a token-protected, same-origin request. The microphone input is handled by Windows' built-in local speech engine; Python receives **text only**. Backend text is held in RAM until fetched once by the current interface. No permanent transcript or raw audio is written by this feature.

This is not authentication, a safety system, or a Panic Box controller. User still reviews all investigations and device actions.

## Test on your PC

1. Extract the ZIP.
2. Run `START_SIGNAL_FACE_DEMO.bat` (no local AI model needed).
3. Click Start listening and say a short phrase; confirm the words appear as **editable text**.
4. Manually press Send; demo response is visibly labeled scripted.
5. Start a second phrase and click Stop listening to verify cancellation.
6. Launch `START_SIGNAL_DESKTOP.bat` with local Ollama running to try actual model-generated conversation.

Run automated checks from the extracted folder:

`py -3 -m unittest -v test_signal_core test_mtc_evidence test_signal_mtc_integration test_signal_voice test_signal_desktop test_signal_listen`

**49 automated tests passed in a non-Windows development environment**, plus a browser simulation verifying manual approval before a transcript is sent. **Real Windows microphone, language-recognizer compatibility, and live Ollama were not tested.**
