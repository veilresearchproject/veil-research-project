"""SIGNAL v43.1 route and optional local-model isolation with simulated Ollama."""
import json, tempfile, threading, unittest
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from signal_local_v43 import make_unified_handler
class FakeModel(BaseHTTPRequestHandler):
    questions=[]
    def log_message(self,*_):pass
    def send(self,obj):
        raw=json.dumps(obj).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if self.path=='/api/tags':self.send({'models':[{'name':'llama3.2:3b'}]})
        else:self.send_error(404)
    def do_POST(self):
        if self.path!='/api/chat':return self.send_error(404)
        data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));self.questions.append(data)
        self.send({'message':{'role':'assistant','content':'This is simulated local-model advice, not a source-file review.'}})
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.fake=ThreadingHTTPServer(('127.0.0.1',0),FakeModel)
        cls.fake.daemon_threads=True;cls.ft=threading.Thread(target=cls.fake.serve_forever,daemon=True);cls.ft.start()
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_unified_handler(cls.fake.server_port,'llama3.2:3b',Path(cls.temp.name)))
        cls.server.daemon_threads=True;cls.t=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.t.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.t.join(timeout=2)
        cls.fake.shutdown();cls.fake.server_close();cls.ft.join(timeout=2);cls.temp.cleanup()
    def url(self,path,**kw):return urlopen(Request(self.base+path,**kw),timeout=5)
    def test_root_contains_one_screen(self):
        with self.url('/') as r:
            body=r.read()
            self.assertIn(b'local Ollama conversation',body)
            self.assertIn(b'Geometric SIGNAL',body)
            self.assertIn(b'v43.1',body)
    def test_briefing_module_static_served(self):
        with self.url('/briefing-core.js') as r:
            self.assertEqual(r.status,200)
            self.assertIn('javascript',r.headers['Content-Type'])
            self.assertIn(b'SIGNALBriefing',r.read())
    def test_health_model_ready_only_local(self):
        with self.url('/api/health') as r:self.assertTrue(json.load(r)['model_ready'])
    def test_chat_only_sent_to_fake_local_model(self):
        body=json.dumps({'question':'What are the limitations?','history':[]}).encode()
        with self.url('/api/chat',method='POST',data=body,headers={'Origin':self.base,'Content-Type':'application/json'}) as r:
            j=json.load(r)
            self.assertIn('simulated local-model advice',j['reply'])
        last=FakeModel.questions[-1]
        self.assertEqual(last['messages'][-1]['content'],'What are the limitations?')
        self.assertFalse(any('audio' in k or 'workflow' in k or 'casebook' in k for k in last.keys()))
    def test_cross_site_post_still_denied(self):
        with self.assertRaises(HTTPError) as cm:
            self.url('/api/chat',method='POST',data=b'{}',headers={'Origin':'https://evil.example','Content-Type':'application/json'})
        self.assertEqual(cm.exception.code,403)
    def test_private_memory_file_not_served(self):
        with self.assertRaises(HTTPError) as cm:self.url('/memory_v34.py')
        self.assertEqual(cm.exception.code,404)
    def test_server_remains_local(self):self.assertEqual(self.server.server_address[0],'127.0.0.1')
    def test_no_static_path_traversal(self):
        with self.assertRaises(HTTPError) as cm:self.url('/../../fake-secret.txt')
        self.assertEqual(cm.exception.code,404)
if __name__=='__main__':unittest.main()
