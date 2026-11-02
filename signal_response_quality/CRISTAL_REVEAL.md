# SIGNAL: The Cristal Reveal — operator run-of-show (prototype)

## Goal
A 3–5 minute personal demo featuring the existing SIGNAL character face, a short scripted introduction, an **actual** unscripted Cristal conversation, and an evidence-first mock research example. This script is not yet integrated with the desktop UI.

## Run of show
1. **0:00–0:03** Brief boot flicker (maximum 3 seconds). Do not deliberately flash rapidly or use strobing.
2. **0:03–0:40** Play the **boot** and **identity** cues through the voice pipeline.
3. **0:40–2:30** **live** cue, then invite Cristal to ask an unrehearsed question. **This phase must use real local model answers**, not a scripted reply. If voice recognition fails, switch to typed input and be transparent.
4. **2:30–4:00** **research** cue; show an expressly labeled **SAMPLE / SIMULATED** MTC observation log with timestamps, recording provenance, control checks and alternative explanations. Never imply fictional values are measurements.
5. **4:00–5:00** **closing** cue; optional tiny expression animation if supported.

## Acceptance criteria for a real reveal
- Full voice audio plays and remains synchronized to the displayed text; no "rest is on screen" deferrals.
- One genuinely spontaneous exchange works, including a follow-up question.
- Recognizes VEIL accurately; does not invent expansions for the name.
- Distinguishes sample observations from real evidence.
- Demonstrates graceful fallback to typed input on microphone errors.
- No claim of being conscious, alive, or having real feelings.
- Does not silently replace a known functional desktop installation.

## Desktop rehearsal
First run unit tests offline. Inspect current desktop UI, Ollama model, ASR, TTS and camera/face integrations before applying changes. Test speaker/microphone together. No live playback has been verified by this branch.

## Suggested local sample table (NOT experimental data)
| Timestamp | Event | Source | Interpretation |
| --- | --- | --- | --- |
| 00:00 | Session begins | Simulated MTC log | Demonstration only |
| 02:15 | Recorded question | Simulated audio event | Check speaker bleed |
| 02:28 | Unexpected click | Simulated mic event | Check room noise and device |
