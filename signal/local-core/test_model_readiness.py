import io
import unittest
from urllib.error import URLError
from model_readiness import TAGS_URL, check_model

class FakeResponse:
    def __init__(self, body):
        self.body = io.BytesIO(body)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def read(self, amount):
        return self.body.read(amount)

def opener(data):
    def run(req, timeout):
        assert req.full_url == TAGS_URL and timeout == 3 and req.get_method() == 'GET'
        return FakeResponse(data)
    return run

class ReadinessTests(unittest.TestCase):
    def test_installed_exact(self):
        r = check_model('llama3.2:3b', opener(b'{"models":[{"name":"llama3.2:3b"}]}'))
        self.assertEqual(r['status'], 'installed')
        self.assertIn('NOT tested', r['detail'])
    def test_nonmatching_tag(self):
        self.assertEqual(check_model('llama3.2:3b', opener(b'{"models":[{"name":"llama3.2:latest"}]}'))['status'], 'model_missing')
    def test_no_server(self):
        self.assertEqual(check_model('x', lambda *a, **kw: (_ for _ in ()).throw(URLError('offline')))['status'], 'server_unavailable')
    def test_bad_json(self):
        self.assertEqual(check_model('x', opener(b'{'))['status'], 'invalid_response')
    def test_wrong_shape(self):
        self.assertEqual(check_model('x', opener(b'{"models":{}}'))['status'], 'invalid_response')
    def test_oversize(self):
        self.assertEqual(check_model('x', opener(b'x' * (1024*1024+1)))['detail'], 'response_too_large')
    def test_bad_model(self):
        with self.assertRaises(ValueError):
            check_model('bad model')
    def test_no_false_inference(self):
        self.assertNotIn('inference_tested', check_model('x', opener(b'{"models":[]}')))

if __name__ == '__main__':
    unittest.main()
