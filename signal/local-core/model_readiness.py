"""Read-only, loopback-only Ollama readiness diagnostic for VEIL SIGNAL.

Checks server and exact installed model tag. Never invokes model inference,
starts audio, downloads files, or sends requests to external hosts.
"""
import argparse
import json
from urllib import request, error

TAGS_URL = 'http://127.0.0.1:11434/api/tags'
MAX_RESPONSE_BYTES = 1024 * 1024

def check_model(model, opener=request.urlopen):
    if not isinstance(model, str) or not model or len(model) > 160 or any(ch.isspace() for ch in model):
        raise ValueError('Expected one exact, nonempty Ollama model tag (no whitespace).')
    req = request.Request(TAGS_URL, headers={'Accept': 'application/json'}, method='GET')
    try:
        with opener(req, timeout=3) as resp:
            raw = resp.read(MAX_RESPONSE_BYTES + 1)
    except (error.URLError, TimeoutError, OSError) as exc:
        return {'status': 'server_unavailable', 'installed': False, 'detail': type(exc).__name__}
    if len(raw) > MAX_RESPONSE_BYTES:
        return {'status': 'invalid_response', 'installed': False, 'detail': 'response_too_large'}
    try:
        doc = json.loads(raw)
        if not isinstance(doc, dict) or not isinstance(doc.get('models'), list):
            raise ValueError('models not list')
        tags = [entry.get('name') for entry in doc['models'] if isinstance(entry, dict) and isinstance(entry.get('name'), str)]
    except (UnicodeError, ValueError, TypeError):
        return {'status': 'invalid_response', 'installed': False, 'detail': 'invalid_model_inventory'}
    found = model in tags
    return {'status': 'installed' if found else 'model_missing', 'installed': found,
            'detail': 'Model tag found; inference NOT tested' if found else 'Exact model tag not installed'}

def main(argv=None):
    p = argparse.ArgumentParser(description='No-inference, loopback-only Ollama model readiness check')
    p.add_argument('--model', default='llama3.2:3b')
    args = p.parse_args(argv)
    report = check_model(args.model)
    print(json.dumps({'model': args.model, **report, 'live_inference_tested': False}, indent=2))
    return 0 if report['installed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
