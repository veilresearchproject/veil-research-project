import io
import json
import unittest
from ollama_readiness import check_ollama_models

class FakeResponse:
    def __init__(self, data): self.body = io.BytesIO(json.dumps(data).encode())
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, n=-1): return self.body.read(n)

class ReadinessTests(unittest.TestCase):
    def test_found(self):
        def opener(url,timeout):
            self.assertEqual(url, 'http://127.0.0.1:11434/api/tags')
            return FakeResponse({'models':[{'name':'model-a:latest'}]})
        r=check_ollama_models('model-a:latest',opener=opener)
        self.assertTrue(r['model_found'])
    def test_missing(self):
        r=check_ollama_models('not-here',opener=lambda u,timeout:FakeResponse({'models':[{'name':'other'}]}))
        self.assertEqual(r['service'],'available')
        self.assertFalse(r['model_found'])
    def test_offline(self):
        def failed(*args,**kwargs): raise ConnectionError('offline')
        r=check_ollama_models('some-model',opener=failed)
        self.assertEqual(r['service'],'unavailable')
    def test_malformed(self):
        r=check_ollama_models('some-model',opener=lambda u,timeout:FakeResponse({'models':{}}))
        self.assertEqual(r['service'],'invalid_response')
    def test_empty_model(self):
        with self.assertRaises(ValueError): check_ollama_models('  ')

if __name__=='__main__':unittest.main()
