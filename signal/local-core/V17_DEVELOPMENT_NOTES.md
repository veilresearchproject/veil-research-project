# SIGNAL desktop v0.17 — Interrupted-question recovery

Previously, submitting a question immediately emptied the editor. If the local
request failed or was interrupted, the operator had to retype it or copy it from
the transcript. The editor now keeps submitted text until a response completes.
Successful completion clears it only if it still matches that submission; newer
text selected while a reply was pending is preserved.

After failure or interruption, a recovery panel keeps the last question (bounded
to 4,000 characters) in this browser tab. **Restore last interrupted question**
copies it into the editor for inspection; it never calls the model. Replacing a
different unsent question requires confirmation. **Dismiss recovery copy** removes
the extra copy while leaving the current editor text alone. A successful manual
retry of that question clears its recovery copy.

The existing pending-request guard blocks a second Send while a request is active.
There are no automatic retries. This is not an exactly-once protocol: if a response
completed on the server before a connection broke, a manual resend could create
another turn. Review the conversation before retrying an ambiguous interruption.

Recovery is in JavaScript memory only: no localStorage, disk write, conversation
snapshot, microphone recording or cloud synchronization. It disappears when the
tab reloads/closes. Confirmed model changes and saved-chat restores clear the old
draft/recovery context as well as replacing the conversation; their confirmation
text now states this. Cancelled or failed changes preserve it.

## Verification

- All 176 existing Python tests passed; no backend behavior changed for recovery.
- JavaScript syntax passed.
- The DOM interaction simulation now covers failed requests, connection errors,
  partial-stream failure, explicit restore without sending, cancel confirmation,
  dismiss-with-editor-preservation, manual retry success, double-click rejection,
  newer-text preservation, busy restore rejection, and model/chat context resets.
- The new ZIP passed extraction/manifest checks and the launcher guide smoke test.

These are simulated local request flows, not a rendered browser or Windows
hardware test. Actual Windows startup/audio and live Ollama performance still
require acceptance on Andrew's desktop. This release does not make any new claim
about model accuracy, hands-free operation, or instrument control.
