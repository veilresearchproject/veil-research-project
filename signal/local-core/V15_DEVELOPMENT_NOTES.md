# SIGNAL desktop v0.15 — Local request progress and timeout guidance

## Behavior

The local status endpoint now reports whether a reply or model-connectivity test
is still running and its elapsed time, measured with a monotonic clock. It exposes
only a fixed operation label, elapsed milliseconds and a stop-request flag; it does
not expose the prompt, generated text, local paths or evidence through this field.
The existing authentication and same-origin checks remain in place.

The interface shows elapsed waiting time, explains that first model loading can
be slow, and distinguishes a requested stop from completed local cleanup. Send,
input and microphone-start stay disabled while the server reports generation in
progress, including after the browser stops receiving a partial stream. Microphone
stop remains available. Controls become usable after a fresh idle status response.
The existing status poll supplies updates; no cloud calls or model downloads occur.

This fixes a misleading sequence in which a stopped browser stream could re-enable
Send while the local model call still held the session lock. The operator can now
see why the next question needs to wait.

Timeout errors in both local model call paths now identify a timeout and suggest
trying a smaller already-installed model. Ordinary connection failures suggest
starting Ollama and checking its inventory, rather than issuing a model-download
instruction as if every failure meant a missing model.

## Verification

- 164 Python tests passed, including eight new request-progress/timeout tests.
- Real loopback HTTP tests exercised blocked ordinary replies, model checks,
  stream cancellation with pending cleanup, errors and return-to-idle state.
- Elapsed clock values and absence of prompt data in status were checked.
- JavaScript syntax and lightweight DOM interaction simulations passed, including
  elapsed status, pending-stop disabled controls and return to ready.

## Limits

Elapsed time is not an estimated completion time, token count or quality score.
This release does not speed up the model, increase PC capacity, or make cancellation
instantaneous. The existing local HTTP inactivity timeout remains unchanged; it is
not a guaranteed total request deadline. Stop requests may wait for a blocked model
read to return before backend cleanup finishes. This state is now visible.

Windows microphone, speaker, real Ollama performance and rendered layout still
need acceptance on Andrew's PC. Model output remains unverified until independently
reviewed, and partial text remains incomplete. No instrument controls or paid API
are introduced.
