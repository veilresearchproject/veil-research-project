import io, json, unittest
from unittest.mock import patch
from ollama_bridge import OllamaBridge
class FakeResponse:
    def __init__(self, data): self.raw=io.BytesIO(json.dumps(data).encode())
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def read(self,n=-1): return self.raw.read(n)
class Tests(unittest.TestCase):
    def test_localonly(self):
        for url in ['https://example.com/api/chat','http://192.168.0.3:11434/api/chat','http://127.0.0.1:11434/other','http://localhost:11434/api/chat?x=1']:
            with self.assertRaises(ValueError): OllamaBridge('model',url)
    def test_good(self):
        b=OllamaBridge('test')
        with patch('ollama_bridge.urlopen',return_value=FakeResponse({'message':{'content':'  Hello Cristal! '}})) as mock:
            result=b([{'role':'user','content':'Hi'}])
            self.assertEqual(result,'Hello Cristal!')
            payload=json.loads(mock.call_args.args[0].data)
            self.assertFalse(payload['stream'])
            self.assertEqual(payload['messages'][0]['content'],'Hi')
    def test_empty(self):
        with patch('ollama_bridge.urlopen',return_value=FakeResponse({'message':{'content':' '}})):
            with self.assertRaises(RuntimeError): OllamaBridge('test')([])
    def test_invalid_model(self):
        with self.assertRaises(ValueError): OllamaBridge('  ')
    def test_timeout(self):
        with self.assertRaises(ValueError): OllamaBridge('test',timeout=0)
if __name__=='__main__': unittest.main()
