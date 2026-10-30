VEIL SIGNAL Desktop v0.8 — Local readiness and evidence-notebook release

EXTRACT THE ENTIRE ZIP FIRST (do not run programs inside the ZIP).

1. Double-click CHECK_SIGNAL_SETUP.bat.
   - Checks local Ollama model listing, available Windows voices, and whether
     an offline speech recognizer can be instantiated.
   - It DOES NOT listen, speak, install models, download anything or contact a cloud AI.

2. Double-click START_SIGNAL_FACE_DEMO.bat to look at SIGNAL's approved face,
   expressions and controls WITHOUT any AI model. The banner says SCRIPTED DEMO.

3. When ready for a real AI conversation, launch Ollama locally.
   In Command Prompt check: ollama list
   If you have not downloaded llama3.2:3b, you can choose to run:
     ollama pull llama3.2:3b
   (First download requires internet and disk space. No paid API is used.)
   Then double-click START_SIGNAL_DESKTOP.bat.

4. In live desktop, select "Local readiness check" to view setup results.
   You can type a message; Windows voice is OFF until enabled.

5. To review MTC evidence: expand "Load a local MTC evidence log", enter the
   folder containing session_result.json, session_metadata.json and events.jsonl.
   Expand "Investigator observation notebook" to log known sources/needs-review
   with a time offset in SECONDS from the session start. The original WAV files
   and MTC evidence logs stay untouched. Notes are unencrypted and kept under
   %LOCALAPPDATA%\VEIL\SIGNAL\review_notes\ in a separate JSONL file.

6. To stop SIGNAL, close the browser tab then press Ctrl+C in the command window.

WARNING: This is a local engineering prototype, not a validated research
instrument. No automatic EVP identification, genuine lip-sync or continuous
listening. Test your microphone, speakers and model on your own Windows PC.

Test: py -3 -m unittest discover -v
