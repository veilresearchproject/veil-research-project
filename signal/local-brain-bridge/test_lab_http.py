"""Local HTTP tests. No external network, real equipment or real Ollama."""
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from signal_local_v38 import make_lab_handler

class LabHttp(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory()
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_lab_handler(11434,'llama3.2:3b',Path(cls.temp.name)))
  cls.port=cls.server.server_port;cls.base=f'http://127.0.0.1:{cls.port}'
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.server.server_close();cls.thread.join(3);cls.temp.cleanup()
 def get(self,path,host=None):
  req=Request(self.base+path,headers={'Host':host} if host else {})
  try:
   with urlopen(req,timeout=3) as r:return r.status,r.read(),r.headers
  except HTTPError as e:return e.code,e.read(),e.headers
 def post(self,path,payload,origin=None,kind='application/json'):
  origin=origin or self.base
  data=json.dumps(payload).encode()
  req=Request(self.base+path,data=data,headers={'Content-Type':kind,'Origin':origin},method='POST')
  try:
   with urlopen(req,timeout=3) as r:return r.status,json.loads(r.read())
  except HTTPError as e:return e.code,json.loads(e.read())
 def test_root_serves_lab(self):
  status,body,h=self.get('/');self.assertEqual(status,200);self.assertIn(b'SIGNAL',body);self.assertIn(b'v38',body);self.assertIn(b'no-store',str(h).encode())
 def test_previous_companion_still_served(self):
  status,body,_=self.get('/v33.html');self.assertEqual(status,200);self.assertIn(b'SIGNAL',body)
 def test_modules_are_local(self):
  for module in ['voice-core.js','assignments-core.js','audio-core.js','dashboard-core.js']:
   status,body,_=self.get('/'+module);self.assertEqual(status,200);self.assertGreater(len(body),300)
 def test_unknown_routes_denied(self):self.assertEqual(self.get('/../../etc/passwd')[0],404)
 def test_get_memory_empty(self):
  code,body,_=self.get('/api/memory');self.assertEqual(code,200);self.assertEqual(json.loads(body)['entries'],[])
 def test_post_without_approval_denied(self):
  code,_=self.post('/api/memory/add',{'kind':'project','note':'Test','source':'Log','approvedBy':'Operator'})
  self.assertEqual(code,400)
 def test_cross_origin_denied(self):
  code,_=self.post('/api/memory/add',{'approved':True},origin='https://example.org');self.assertEqual(code,403)
 def test_memory_add_and_remove(self):
  note={'approved':True,'kind':'protocol','note':'Synthetic protocol test only','source':'Manual test','approvedBy':'VEIL operator'}
  code,data=self.post('/api/memory/add',note);self.assertEqual(code,200);id=data['result']['id']
  self.assertEqual(len(json.loads(self.get('/api/memory')[1])['entries']),1)
  code,data=self.post('/api/memory/remove',{'approved':True,'id':id});self.assertEqual(code,200)
  self.assertEqual(len(json.loads(self.get('/api/memory')[1])['entries']),0)
 def test_memory_request_size_cap(self):
  code,data=self.post('/api/memory/add',{'approved':True,'kind':'project','note':'x'*5000,'source':'Log','approvedBy':'Operator'})
  self.assertEqual(code,413)
 def test_model_health_does_not_require_model(self):
  code,body,_=self.get('/api/health');self.assertEqual(code,200);self.assertIn(b'model_ready',body)
 def test_chat_requires_origin(self):
  code,_=self.post('/api/chat',{'question':'Hello'},origin='https://evil.example');self.assertEqual(code,403)
 def test_equipment_controls_still_denied(self):
  code,_=self.post('/api/chat',{'question':'activate the panic box now'});self.assertEqual(code,400)

if __name__=='__main__':unittest.main(verbosity=2)
