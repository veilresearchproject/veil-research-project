# First desktop test — SIGNAL v0.15

Keep the prior working folder. Extract this ZIP into a new folder first.

1. **Check setup:** double-click `CHECK_SIGNAL_SETUP.bat`. This checks local
   capabilities; it does not speak, listen or download a model. Note any missing
   component. An installed component is not yet a successful hardware test.
2. **Start conversation:** start local Ollama, then double-click
   `START_SIGNAL_DESKTOP.bat`. The interface must say LOCAL OLLAMA MODEL.
   SCRIPTED VISUAL DEMO is a different mode and cannot test real AI replies.
3. **Check the model:** under Local readiness check, click Test Ollama conversation.
   If the default is missing or slow, use Choose an installed local model, then
   repeat the conversation test. Note the reported response time. Nothing is
   downloaded by the chooser; the choice lasts only until restart.
   While it runs, confirm the elapsed-waiting status appears. It reports time
   spent waiting, not an estimated finish time.
4. **Check speaker and stop:** click Enable voice, then Test voice. Confirm you
   hear it. Click Stop speaking while it plays. If it finishes before the click,
   repeat the test. Stop speaking leaves voice enabled; Disable voice turns it off.
5. **Check microphone:** click Start listening, say a short phrase, and verify the
   recognized words appear for review. Nothing should send until you click Send.
   Try another attempt and click Stop listening before speaking. Confirm capture
   stops. A status error means the microphone state is uncertain, not confirmed off.
6. **Check a real exchange:** send the reviewed phrase and confirm an answer arrives.
   With voice enabled, confirm speech follows the completed answer. While another
   reply is pending, Disable voice and confirm no new speech starts for that reply.
   If you use Stop reply, partial text must remain marked incomplete. If local
   cleanup continues, Send should stay disabled until SIGNAL reports idle.
7. **Check continuity if wanted:** save a completed short conversation, close the
   application, reopen, and explicitly restore it. It must not restore automatically.
   Saved chat is context only; MTC logs and scanner reports must be loaded separately.

Record **pass / fail / not tested** for each step and the exact onscreen error when
something fails. A failure does not require reinstalling or deleting evidence.
Keep the console window open long enough to capture its error information.

Close the local server command window when finished. Leave original MTC recordings
in their existing folders. This test is conversation/audio acceptance, not a test
of paranormal detection or instrument control.
