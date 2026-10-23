"""Unit tests simulate local Ollama; they do not verify a real model or Windows."""
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import URLError

import preflight


class Response:
    def __init__(self, content):
        self.content = json.dumps(content).encode('utf-8')
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, n=-1):
        return self.content if n == -1 else self.content[:n]


class PreflightTests(unittest.TestCase):
    def opener(self, content):
        def open_local(url, timeout):
            self.assertEqual(url, preflight.TAGS_URL)
            self.assertEqual(timeout, 4)
            return Response(content)
        return open_local

    def test_installed_exact_tag_is_ready_but_not_inference_tested(self):
        report = preflight.check(opener=self.opener({'models': [{'name': 'llama3.2:3b'}]}),
                                 python_version=(3, 11), system='Windows')
        self.assertTrue(report['ready_for_live_benchmark'])
        self.assertTrue(report['running_on_windows'])
        self.assertFalse(report['actual_model_inference_tested'])
        self.assertFalse(report['windows_hardware_validated'])

    def test_other_installed_model_is_not_requested_tag(self):
        report = preflight.check(opener=self.opener({'models': [{'name': 'qwen3:1.7b'}]}),
                                 system='Windows')
        self.assertTrue(report['ollama_local_running'])
        self.assertFalse(report['model_installed'])
        self.assertFalse(report['ready_for_live_benchmark'])

    def test_secondary_model_field_accepted(self):
        report = preflight.check(opener=self.opener({'models': [{'model': 'llama3.2:3b'}]}))
        self.assertTrue(report['model_installed'])

    def test_unreachable_local_server_is_friendly_failure(self):
        def offline(url, timeout):
            self.assertEqual(url, preflight.TAGS_URL)
            raise URLError('not running')
        report = preflight.check(opener=offline)
        self.assertFalse(report['ready_for_live_benchmark'])
        self.assertIsNotNone(report['error'])
        self.assertNotIn('not running', report['error'])

    def test_invalid_endpoint_response_fails_closed(self):
        for invalid in ({}, {'models': {}}, [], {'models': None}):
            with self.subTest(data=invalid):
                report = preflight.check(opener=self.opener(invalid))
                self.assertFalse(report['ollama_local_running'])
                self.assertFalse(report['ready_for_live_benchmark'])

    def test_old_python_never_reports_ready(self):
        report = preflight.check(opener=self.opener({'models': [{'name': 'llama3.2:3b'}]}),
                                 python_version=(3, 9))
        self.assertFalse(report['python_supported'])
        self.assertFalse(report['ready_for_live_benchmark'])

    def test_no_remote_url_and_no_cloud_fallback(self):
        self.assertEqual(preflight.TAGS_URL, 'http://127.0.0.1:11434/api/tags')
        report = preflight.check(opener=self.opener({'models': []}))
        self.assertTrue(report['no_cloud_contact'])
        self.assertFalse(report['model_installed'])

    def test_cli_does_not_claim_inference_or_download(self):
        with patch.object(preflight, 'check', return_value={
            'python_supported': True, 'running_on_windows': True,
            'ollama_local_running': True, 'model_installed': True,
            'ready_for_live_benchmark': True, 'error': None,
        }):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(preflight.main(['--model', 'llama3.2:3b']), 0)
            self.assertIn('Actual inference tested: NO', output.getvalue())
            self.assertNotIn('ollama pull', output.getvalue())

    def test_blank_model_name_rejected(self):
        with self.assertRaises(ValueError):
            preflight.check(model=' ')


if __name__ == '__main__':
    unittest.main(verbosity=2)
