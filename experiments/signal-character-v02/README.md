# SIGNAL character rehearsal v0.2 — November 3, 2026

Experimental prototype, not deployed. Uses a separate loopback-only Python HTTP server at `127.0.0.1:8766` to display the character page and proxy typed questions to locally installed Ollama at `127.0.0.1:11434` with model `llama3.2:3b`. It does not modify the existing SIGNAL bridge on port 8765. Scripted answers remain an offline fallback. Voice uses browser speech synthesis and mouth animation is approximate.

Nine mock-based server integration tests passed locally, including healthy/unavailable model, question handling, cross-site request denial, invalid inputs, and file-path denial. Real Ollama interaction and end-to-end Windows desktop operation remain untested.

A self-contained ZIP package with the HTML page, Python server, and instructions was delivered in the conversation. No cloud dependency or additional Python packages needed. Keep the experimental server bound to 127.0.0.1. Preserve the existing working installation, and do not put actual research evidence into this demo.
