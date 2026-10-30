# SIGNAL v0.6 — subtle portrait motion (engineering prototype)

This extends the **existing** SIGNAL v0.5 local desktop assistant. We deliberately retain the six approved expressions and the investigator-consent microphone workflow.

## What changed

- Four locally generated, very small mouth-aperture poses derived from the approved neutral portrait (`face_assets/speech_0.webp` through `speech_3.webp`). Original expression files are not overwritten.
- When the Windows speech process reports active speech, the browser cycles those poses at approximately 180 ms intervals. It returns to the selected expression after speech completes or is stopped.
- A **Preview face movement** button demonstrates the same movement **silently** for up to 4.5 seconds. It does not invoke the microphone, send a prompt to the AI, or generate audio.
- Slight idle breathing is simulated by a restrained image transform, respecting operating-system **Reduce Motion** preference. If reduced motion is set, the preview refuses animation.
- Earlier features remain: optional Windows voice output, user-approved push-to-talk input, read-only MTC JSON log review, local Ollama conversation, and a clearly identified scripted demo mode.

## Accuracy and limitations

This is **speaking-activity animation**, not accurate phoneme/viseme lip synchronization, facial tracking, or real-time expressive video. The approved portrait is a still image; talking poses are a limited 2D effect. Photo motion is deliberately subtle to avoid an artificial or theatrical appearance.

No raw microphone audio is captured by this animation feature. The signal used is merely whether the **local Windows speech synthesizer** is running. Audio still requires your Windows installation and an enabled Windows speech voice. The true Ollama conversation and microphone recognizer still need testing on your Windows computer.

## Try on Windows

1. Extract the ZIP; don't overwrite the v0.5 folder yet.
2. Double-click **START_SIGNAL_FACE_DEMO.bat**; it does **not** need Ollama.
3. Click **Preview face movement** beneath SIGNAL's face. He should move his mouth slightly for a few seconds. Click again to stop early. This is silent, and the microphone remains OFF.
4. For actual local AI conversation and speech, first start a locally installed Ollama model, then double-click **START_SIGNAL_DESKTOP.bat** and select **Enable voice**. Facial movement begins while speech is active.
5. If motion is disabled by the OS accessibility setting, the preview explains why and remains still.
6. For faults, keep the black command window open and share the visible error. There is **no cloud fallback**.

## Regression

Run `py -3 -m unittest discover -v` from the extracted directory. The tests use only Python's standard library and do not need installed speech hardware. The optional `browser_speech_smoke.py` developer test requires Playwright and Chromium; it is not a runtime dependency.

**Not validated on the user's Windows PC** as of the v0.6 package. No changes are deployed to the production VEIL website or MTC recorder.
