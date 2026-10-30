# SIGNAL desktop v0.13 — Installed local model chooser

When the default `llama3.2:3b` model is missing or slow, the operator can now
choose another eligible model already installed in Ollama without editing Python.

## Use

1. Extract this release into a new folder, preserving v0.12.
2. Start Ollama, then run `START_SIGNAL_DESKTOP.bat`.
3. Open **Choose an installed local model** and click **List installed models**.
4. Choose a model, click **Use selected model**, and confirm the new chat.
5. Under **Local readiness check**, click **Test Ollama conversation** to measure
   an actual reply time for the selected model. Generated text still needs review.

The list and selection contact only the fixed local Ollama inventory endpoint.
They do not generate text, download/install/delete models, activate the microphone,
enable voice, contact a paid API, or write configuration files. Selection lasts
for this run; restarting uses the existing default. To keep the current chat,
use the existing explicit save control before switching.

Changing models clears active chat, loaded MTC logs, and imported scanner context
so the new model cannot inherit an undisclosed research session. Saved snapshots,
investigator notes and original evidence files are unchanged. Selecting the
current model is a no-op. The user may explicitly restore saved chat afterward;
research records must be reloaded independently.

## Boundaries and failures

Names are selected from a freshly revalidated local inventory, bounded to 256 KB
and 100 eligible names. Entries identified by remote metadata or a name containing
`cloud` are excluded. This conservative filter is not an audit of arbitrary Ollama
aliases, proxy configuration, or model provenance; use trusted local model installs.
No automatic model downloads or fallback are provided.

Busy generation, active listening, demo mode, malformed requests, unknown models,
missing explicit confirmation, failed inventory, absent tokens and foreign origins
all reject the operation. Failed validation preserves the active chat and evidence
context. Installed does not mean fast, accurate, or hardware-validated.

The readiness parser also now handles a malformed JSON root (`null` or a list)
without crashing.

## Verification

- 147 Python tests passed: existing 137 plus 10 new inventory/HTTP acceptance tests.
- Real loopback HTTP tests exercise selection, authentication, busy/listening
  rejection, unavailable inventories and preservation of original file bytes.
- `node --check signal_face.js` passed.
- `node test_signal_model_ui.cjs` passed a lightweight DOM interaction simulation
  covering opt-in inventory, cancel, selection/reset, unchanged-model behavior and
  unavailable inventory. This is not a rendered browser or hardware test.

Windows speech, microphone operation, actual Ollama performance, and visual layout
still require acceptance on Andrew's Windows PC. No claim of paranormal detection,
autonomous instrument control, or finished hands-free operation is made.
