# SIGNAL v28 — Local Evidence Fingerprint, isolated preview (November 5, 2026)

**Status:** Review-only, local-first development; no merge or website deployment. Separate from working v25, v26, and v27. v28 extends the v27 geometric interface and keeps all Casebook functionality intact. No purchase or cloud subscription is needed.

## New v28 milestone

1. **Human-initiated local file selection** — The operator chooses one file; without that action SIGNAL reads no file. It does not access folders or scan for evidence.
2. **Local SHA-256 fingerprint** — Reads the selected file into browser memory and calculates its SHA-256 using standard Web Crypto. No content is uploaded, stored automatically, or sent to AI. Available on trusted local `http://127.0.0.1:8768/`; secure context and support required.
3. **25 MiB safety bound** — Rejects large selections *before* reading bytes. This preview does not support typical large video files; a future chunked, locally audited hashing option would be needed.
4. **Comparison to an operator-provided digest** — Reports MATCH or MISMATCH, not "tampered" or "real". Hash identity does not establish that a file was original, when it was made, who made it, or whether observations are anomalous.
5. **Deliberate Casebook note insertion** — Copies hash, file label and size only into the *unsaved* observation description when the operator presses a button. Another explicit "Add observation" click is required. The UI never automatically shares file bytes, metadata or hashes with Ollama.

## Windows setup

Keep your existing Ollama/`server.py`/v25 environment as-is. Place these *new* files beside the existing `signal/local-brain-bridge/server.py`: `v28.html`, `fingerprint-core.js`, `casebook-core.js`, `v28_server.py`, `START_SIGNAL_V28_FINGERPRINT.bat`. Double-click the batch file; navigate directly to `http://127.0.0.1:8768/` on your desktop. The launcher only starts a localhost Python server, not Ollama or the existing v25 instance, and defaults to your already-installed `llama3.2:3b` if SIGNAL_MODEL is unset.

The ZIP is an **add-on**, not a complete replacement: it does not include the original `server.py`, desktop v25, Windows voice engines or Ollama model. Scripted mode works without the model. Do not overwrite working code. Stop the extra local server with Ctrl+C.

## Verified checks

- `node test_casebook.cjs`: **25/25** previously passed unchanged.
- `node test_fingerprint.cjs`: **15/15** passed including SHA-256 standard empty/`abc` vectors with Node's WebCrypto, file size rejection before file read, mismatch and no-network source check.
- `node test_v28.cjs`: **15/15** static and contract checks passed.
- `python -m py_compile v28_server.py`: passed.
- `python browser_smoke_v28.py`: Chromium 390×844 UI smoke passed for explicit file selection, displayed digest, MATCH/MISMATCH, deliberate Casebook insertion and clear. Browser sandbox blocks HTTP loopback navigation and has no WebCrypto in `about:blank`, so the UI smoke **mocks the cryptographic digest** while the real SHA-256 algorithm is verified separately in Node. **A real browser-to-Python, Windows device, and real Ollama test have not been performed.**

## Evidence and security limitations

- SHA-256 is a byte fingerprint of whichever file the operator selected. It is not a certification of evidence origin, date, truth or an anomalous cause.
- This is a local, untrusted single-operator preview, not a forensic evidence-handling or tamper-evident chain-of-custody system. The browser engine, local disk and human operator are outside this application's verification boundary.
- The file name, size and hash may be copied into a note only by operator action. Browser-selected file contents are never sent to Ollama, even when AI critique is enabled. Casebook note descriptions (which may include a hash) can be sent to the local model **only after separate explicit permission and button click**.
- Do not use it with private subject material, classified records, or sensitive research data before suitable access-control, retention and threat review.
- Full-size recordings, stream-based hashing, instrument adapters, authentication, offline speech verification, and actual Windows CPU/GPU benchmarking remain future work.