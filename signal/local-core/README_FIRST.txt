VEIL SIGNAL DESKTOP v0.15 — LOCAL WAITING STATUS

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

164 automated Python tests passed here. Actual Windows microphone, speaker and
Ollama speed still need acceptance on your desktop. See V15_DEVELOPMENT_NOTES.md.

NEW IN v0.15: Elapsed waiting time is shown for local replies and model tests.
After Stop reply, Send stays disabled while backend cleanup is still running.
Timeout messages suggest a smaller installed model without downloading anything.
