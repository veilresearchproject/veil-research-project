# SIGNAL local Ollama readiness test — November 3, 2026

Status: Python logic tested with six mock-based unit tests; **not yet validated on Andrew's Windows PC**. Does not modify SIGNAL installation or recordings.

Use this only when Ollama is already running locally and the model `llama3.2:3b` is installed.

From the directory containing the scripts:

```powershell
py -3 signal_ollama_smoke.py --list-only
py -3 signal_ollama_smoke.py --timeout 120
py -3 -m unittest -v test_signal_ollama_smoke.py
```

The script connects exclusively to `http://127.0.0.1:11434` through Ollama's local HTTP API, checks the model, and sends three **synthetic** prompts only when not in `--list-only` mode. Outputs success and time measurements to the terminal; it does not write a log. No research evidence is processed. No internet connection or package installation is required.

An unsuccessful connection may mean that Ollama has not been started or that another port is configured; do not change GPU settings or the working SIGNAL bridge merely to satisfy this optional check.

**Boundaries:** This only tests basic model responsiveness; it does not evaluate factual accuracy, sound capture, voice output, face animation, endpoint privacy of other components, unattended reliability or end-to-end SIGNAL operation. Do not label it as complete acceptance of SIGNAL.
