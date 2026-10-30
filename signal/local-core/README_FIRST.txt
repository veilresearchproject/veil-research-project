VEIL SIGNAL DESKTOP v0.13 — INSTALLED MODEL CHOOSER

Extract into a NEW folder; keep v0.12 as a fallback.

1. START_SIGNAL_FACE_DEMO.bat opens the scripted face demonstration (no AI).
2. For actual conversation, start local Ollama and run START_SIGNAL_DESKTOP.bat.
3. Open Choose an installed local model, then List installed models.
4. Choose a model already on this PC, click Use selected model, and confirm.
5. Run Test Ollama conversation under Local readiness check to see reply speed.

Nothing is downloaded. Model selection lasts for this run only. Switching to a
different model starts a new chat and unloads research context. Save a conversation
explicitly first if you want to keep it. Saved chats, notes and original WAVs/logs
are unchanged. Evidence must be loaded again independently.

Optional voice and microphone start OFF. This is a local Windows alpha; actual
Windows audio and Ollama speed still require testing on your desktop.

RUN_SIGNAL_TESTS.bat runs the Python tests. See V13_DEVELOPMENT_NOTES.md for
verification, limits and instructions. No paid API or automatic cloud fallback.
