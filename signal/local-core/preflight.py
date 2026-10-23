"""Read-only, local-only Ollama readiness check for SIGNAL (Python standard library).

Checks the loopback Ollama tags endpoint. Never downloads a model, sends a prompt,
records model output, or contacts an external service. Readiness is not inference validation.
"""
import argparse
import json
import platform
import sys
from urllib import error, request

TAGS_URL = 'http://127.0.0.1:11434/api/tags'
DEFAULT_MODEL = 'llama3.2:3b'


def check(model=DEFAULT_MODEL, opener=None, python_version=None, system=None):
    """Return a truthful non-sensitive readiness report without writing to disk."""
    if not isinstance(model, str) or not model.strip():
        raise ValueError('A local Ollama model tag is required')
    opener = opener or request.urlopen
    version = python_version or sys.version_info
    host_os = system or platform.system()
    report = {
        'model_requested': model,
        'python_supported': tuple(version[:2]) >= (3, 10),
        'running_on_windows': host_os == 'Windows',
        'ollama_local_running': False,
        'model_installed': False,
        'ready_for_live_benchmark': False,
        'actual_model_inference_tested': False,
        'windows_hardware_validated': False,
        'no_cloud_contact': True,
        'error': None,
    }
    try:
        # Hard-coded 127.0.0.1 prevents off-computer requests and cloud fallback.
        with opener(TAGS_URL, timeout=4) as response:
            data = json.load(response)
        if not isinstance(data, dict) or not isinstance(data.get('models'), list):
            raise ValueError('Ollama returned an unexpected model list')
        names = {name for entry in data['models'] if isinstance(entry, dict)
                 for name in (entry.get('name'), entry.get('model')) if isinstance(name, str)}
        report['ollama_local_running'] = True
        report['model_installed'] = model in names
    except (error.URLError, TimeoutError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        report['error'] = 'Local Ollama is unreachable or returned an invalid response (' + type(exc).__name__ + ').'
    report['ready_for_live_benchmark'] = (report['python_supported'] and
                                          report['ollama_local_running'] and report['model_installed'])
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description='SIGNAL: local-only preflight; no AI prompts sent')
    parser.add_argument('--model', default=DEFAULT_MODEL, help='Exact installed local Ollama tag')
    args = parser.parse_args(argv)
    report = check(args.model)
    print('SIGNAL Local Preflight (checks only; no inference performed)')
    print('Python 3.10+:', 'YES' if report['python_supported'] else 'NO')
    print('Windows host:', 'YES' if report['running_on_windows'] else 'NO')
    print('Ollama loopback running:', 'YES' if report['ollama_local_running'] else 'NO')
    print('Model installed (' + args.model + '):', 'YES' if report['model_installed'] else 'NO')
    print('Ready to TRY a live benchmark:', 'YES' if report['ready_for_live_benchmark'] else 'NO')
    print('Actual inference tested: NO; hardware performance validated: NO')
    if report['error']:
        print(report['error'])
        print('Start local Ollama, then run this check again.')
    elif not report['model_installed']:
        print('To install this model locally, run: ollama pull ' + args.model)
    if report['ready_for_live_benchmark']:
        print('Next (manual): py -3 benchmark.py --mode live --model ' + args.model + ' --show-responses')
    return 0 if report['ready_for_live_benchmark'] else 2


if __name__ == '__main__':
    sys.exit(main())
