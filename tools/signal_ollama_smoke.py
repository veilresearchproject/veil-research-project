#!/usr/bin/env python3
"""VEIL SIGNAL: optional offline synthetic Ollama readiness test.

Only contacts 127.0.0.1. Sends no personal/research recordings.
Python standard library only. Designed to fail safely if Ollama isn't available.
"""
import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HOST = 'http://127.0.0.1:11434'
TEST_PROMPTS = [
    'In one sentence, explain why an unexplained sound is not proof of a spirit.',
    'Give one ordinary explanation for an unexpected clicking sound in a house.',
    'What should a researcher do before changing an original audio recording?',
]

def request_json(path, data=None, timeout=30):
    payload = None if data is None else json.dumps(data).encode('utf-8')
    req = Request(HOST + path, data=payload, headers={'Content-Type': 'application/json'})
    with urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError('Unexpected HTTP status: ' + str(response.status))
        return json.loads(response.read().decode('utf-8'))

def inspect_response(payload):
    if not isinstance(payload, dict):
        return 'Invalid JSON response'
    answer = payload.get('response')
    if not isinstance(answer, str) or not answer.strip():
        return 'Missing or empty response'
    if payload.get('done') is not True:
        return 'Response did not report completion'
    return None

def run(model, timeout, evaluate=True):
    tags = request_json('/api/tags', timeout=timeout)
    names = [m.get('name') for m in tags.get('models', []) if isinstance(m, dict)]
    if model not in names:
        return {'ok': False, 'reason': 'Requested model not installed', 'installed_models': names}
    if not evaluate:
        return {'ok': True, 'installed_model': model, 'test_results': []}
    results = []
    for index, prompt in enumerate(TEST_PROMPTS, 1):
        start = time.monotonic()
        payload = request_json('/api/generate', {
            'model': model, 'prompt': prompt, 'stream': False,
            'options': {'temperature': 0}, 'keep_alive': '1m'
        }, timeout=timeout)
        elapsed = round(time.monotonic() - start, 2)
        error = inspect_response(payload)
        results.append({'case': index, 'completed': error is None,
                        'seconds': elapsed,
                        'response_characters': len(payload.get('response', '')) if isinstance(payload.get('response'), str) else 0,
                        'error': error})
    return {'ok': all(r['completed'] for r in results), 'installed_model': model,
            'test_results': results,
            'note': 'Readiness check only; does not assess reasoning accuracy or voice/face quality.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='llama3.2:3b')
    parser.add_argument('--timeout', type=int, default=120, help='Per-request timeout in seconds')
    parser.add_argument('--list-only', action='store_true',
                        help='Check installed model, send no test questions')
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 600:
        parser.error('Timeout must be between 1 and 600 seconds')
    try:
        output = run(args.model, args.timeout, evaluate=not args.list_only)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
        output = {'ok': False, 'reason': 'Local Ollama request failed', 'details': str(exc)}
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if output.get('ok') else 1)

if __name__ == '__main__':
    main()
