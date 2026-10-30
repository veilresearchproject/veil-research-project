VEIL SIGNAL DESKTOP v0.14 — DESKTOP AUDIO TEST BUILD

Extract into a NEW folder. Keep earlier versions as fallbacks.

Read DESKTOP_TEST_STEPS.md for the short first-test sequence.

1. CHECK_SIGNAL_SETUP.bat checks installed local capabilities without audio capture.
2. Start local Ollama, then START_SIGNAL_DESKTOP.bat for real conversation.
3. Choose an installed local model if needed; test its response time.
4. Enable voice, then Test voice. Try Stop speaking and Disable voice.
5. Start listening for one phrase. Review recognized text before clicking Send.

Stop speaking, Disable voice and Stop listening now remain accessible during a
slow model call. A failed microphone stop/status check does not claim the mic is
off. Disable voice suppresses speech for a reply still being generated; Stop
speaking stops current speech only. Stop reply is a separate best-effort control.

Microphone and voice start OFF. Model selection does not download anything and
lasts for this run. Switching models starts a new chat; saved conversations,
notes and original evidence files remain unchanged. No paid API or cloud fallback.

156 automated Python tests passed here. Actual Windows microphone, speaker and
Ollama speed still need acceptance on your desktop. See V14_DEVELOPMENT_NOTES.md.
