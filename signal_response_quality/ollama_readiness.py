"""Read-only local Ollama readiness probe for the SIGNAL reveal.

No installations, model pulls, audio capture, or device changes.
"""
import json
from urllib.request import urlopen

def check_ollama_models(model: str, *, opener=urlopen) -> dict:
    """Check installed model names against Ollama /api/tags at loopback only."""
    if not isinstance(model, str) or not model.strip():
        raise ValueError("Specify the model already configured on the desktop")
    try:
        with opener("http://127.0.0.1:11434/api/tags", timeout=4) as response:
            data = json.load(response)
    except Exception:
        return {"service": "unavailable", "model_found": False, "models": []}
    models = data.get("models", [])
    if not isinstance(models, list):
        return {"service": "invalid_response", "model_found": False, "models": []}
    names = sorted(m["name"] for m in models if isinstance(m, dict) and isinstance(m.get("name"), str))
    return {"service": "available", "model_found": model.strip() in names, "models": names}
