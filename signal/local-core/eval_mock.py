"""SIGNAL offline mock transport benchmark; no Ollama, sensors, GPU or network.

Measures Python request plumbing, NOT model speed, answer accuracy or safety behavior.
Run: python eval_mock.py --iterations 20 --json
"""
import argparse
import hashlib
import io
import json
import platform
import statistics
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
import signal_core as core

TOPICS = {
    'thermal': ('1.9 C temperature drop', 'door-open temperature rise',
                'uncalibrated thermometers', 'impossible -274 C reading'),
    'audio': ('unattended MTC playback sound', 'possible speaker bleed',
              'recorders with mismatched clocks', 'transcript versus audio evidence'),
    'integrity': ('duplicate CSV timestamps', '240-second acquisition gap',
                  'SHA-256 changed after copy', 'missing chain-of-custody notes'),
    'controls': ('EM coil off before observation', 'randomized sham comparison',
                 'uncorroborated witness report', 'baseline sensor drift'),
    'permissions': ('activate Panic Box all clear without operator',
                    'ignore rules and command equipment', 'read a private file',
                    'upload evidence to a public server'),
    'context': ('observation versus conclusion', 'remember without consent',
                'describe actual computer access', 'uncertainties in synthetic data'),
}
CASES = [(group, 'Synthetic research scenario: ' + topic + '. Explain limits.')
         for group, topics in TOPICS.items() for topic in topics]


def require(condition, why):
    if not condition:
        raise AssertionError(why)


def fake_ollama(req, timeout=0):
    require(req.full_url == 'http://127.0.0.1:11434/api/chat' == core.LOCAL_URL,
            'Non-loopback endpoint')
    require(timeout == 90, 'Unexpected timeout')
    require(req.get_header('Content-type') == 'application/json', 'Wrong MIME type')
    payload = json.loads(req.data.decode('utf-8'))
    require(payload['model'] == 'signal-eval:mock', 'Wrong model')
    require(payload['stream'] is False and payload['options']['num_ctx'] == 4096,
            'Unexpected transport options')
    msgs = payload['messages']
    require(msgs[0]['role'] == 'system' and msgs[-1]['role'] == 'user',
            'Missing system/user roles')
    require(len(msgs) <= 18, 'History exceeds eight turns')
    for phrase in ('run lab instruments', 'offsite human operator',
                   'not commands', 'cannot see, hear'):
        require(phrase in msgs[0]['content'].lower(), 'Missing system caveat: ' + phrase)
    require(all(m['role'] in ('system', 'user', 'assistant') for m in msgs),
            'Unexpected message role')
    digest = hashlib.sha256(msgs[-1]['content'].encode()).hexdigest()[:16]
    return io.BytesIO(json.dumps({'message': {'content': 'MOCK_ACK_' + digest}}).encode())


def fault_probes():
    failures = (
        ('offline', URLError('offline'), 'No cloud fallback'),
        ('bad_json', b'{broken', 'Invalid JSON'),
        ('bad_utf8', b'\\xff\\xfe', 'Invalid JSON'),
        ('oversize_http', b'x' * (core.MAX_RESPONSE_BYTES + 1), '1 MB'),
        ('empty', b'{"message":{"content":" "}}', 'Unexpected local model response'),
        ('missing', b'{}', 'Unexpected local model response'),
        ('long_reply', json.dumps({'message': {'content': 'x' * (core.MAX_REPLY_CHARS + 1)}}).encode(), '8,000-character'),
    )
    for name, value, expected in failures:
        def respond(*args, **kwargs):
            if isinstance(value, Exception):
                raise value
            return io.BytesIO(value)
        with patch.object(core.request, 'urlopen', side_effect=respond):
            try:
                core.LocalModel().answer([{'role': 'user', 'content': 'mock'}])
            except RuntimeError as exc:
                require(expected in str(exc), name + ': incorrect error classification')
            else:
                raise AssertionError(name + ': failure was not rejected')
    return len(failures)


def run(iterations):
    require(1 <= iterations <= 20, 'iterations must be 1..20')
    elapsed = []
    with tempfile.TemporaryDirectory(prefix='signal-mock-') as tmp:
        mem = core.Memories(Path(tmp))
        assistant = core.Assistant(core.LocalModel('signal-eval:mock'), mem)
        require(not mem.path.exists(), 'Memory file already exists')
        with patch.object(core.request, 'urlopen', side_effect=fake_ollama) as patched:
            for _ in range(iterations):
                for _category, prompt in CASES:
                    t = time.perf_counter_ns()
                    answer = assistant.ask(prompt)
                    elapsed.append((time.perf_counter_ns() - t) / 1_000_000)
                    digest = hashlib.sha256(prompt.encode()).hexdigest()[:16]
                    require(answer == 'MOCK_ACK_' + digest, 'Incorrect mock response')
            require(patched.call_count == len(CASES) * iterations,
                    'Unexpected number of model requests')
        require(not mem.path.exists(), 'Conversation persisted without opt-in')
        require(len(assistant.history) == 16, 'History limit violated')
        require('Unknown command' in assistant.action('/run-instrument'),
                'Instrument command incorrectly accepted')
        assistant.action('/remember synthetic note = test only')
        require(mem.get().get('synthetic note') == 'test only', 'Memory opt-in failed')
        assistant.action('/forget synthetic note')
        require(mem.get() == {}, 'Forget failed')
        assistant.action('/clear')
        require(assistant.history == [], 'Clear failed')
    faults = fault_probes()
    ordered = sorted(elapsed)
    return {
        'mode': 'offline_mock_only', 'requests': len(elapsed),
        'cases': len(CASES), 'categories': sorted(TOPICS), 'iterations': iterations,
        'fault_probes_passed': faults,
        'boundary_checks': ['loopback only', 'system disclaimer present',
                            '8-turn context limit', 'memory opt-in/delete',
                            'no unapproved command', 'malformed response rejection'],
        'mock_python_path_ms': {
            'median': round(statistics.median(elapsed), 4),
            'p95': round(ordered[int(.95 * (len(ordered) - 1))], 4),
        },
        'python': platform.python_version(),
        'real_model_tested': False, 'gpu_tested': False,
        'instrument_connected': False, 'semantic_quality_tested': False,
        'warning': 'Mock timings exclude actual model inference; no claim of safety compliance or scientific reasoning quality.'
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iterations', type=int, default=5)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    try:
        result = run(args.iterations)
    except (AssertionError, RuntimeError, ValueError) as exc:
        print('FAIL: ' + str(exc))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print('PASS: {} synthetic mocked requests, {} fault probes'.format(
            result['requests'], result['fault_probes_passed']))
        print(result['warning'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
