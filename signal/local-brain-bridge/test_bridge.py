"""Dependency-free integration tests; loopback fake Ollama, no real model."""
import http.client
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
import server as bridge

class FakeOllama(BaseHTTPRequestHandler):
    last_chat = None
    include_model = True
    def log_message(self, *_): pass
    def do_GET(self):
        if self.path == '/api/tags':
            result={'models':[{'name':bridge.MODEL}]} if self.include_model else {'models':[]}
            data=json.dumps(result).encode()
            self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        else:self.send_error(404)
    def do_POST(self):
        data=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        type(self).last_chat=data
        b=json.dumps({'message':{'role':'assistant','content':'First, preserve the original recordings.'},'done':True}).encode()
        self.send_response(200);self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake=ThreadingHTTPServer(('127.0.0.1',0),FakeOllama)
        cls.fake_thread=threading.Thread(target=cls.fake.serve_forever,daemon=True);cls.fake_thread.start()
        cls.patch=patch.object(bridge,'OLLAMA',f'http://127.0.0.1:{cls.fake.server_port}');cls.patch.start()
        cls.bridge=ThreadingHTTPServer(('127.0.0.1',0),bridge.Handler)
        cls.bridge_thread=threading.Thread(target=cls.bridge.serve_forever,daemon=True);cls.bridge_thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.bridge.shutdown();cls.bridge.server_close();cls.fake.shutdown();cls.fake.server_close();cls.patch.stop()
    def req(self,method,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.bridge.server_port,timeout=4)
        if body is not None and not isinstance(body,bytes):body=json.dumps(body).encode()
        c.request(method,path,body,headers or {});r=c.getresponse();raw=r.read();out=(r.status,dict(r.getheaders()),raw)
        c.close();return out
    @property
    def good_headers(self):
        return {'Origin':f'http://127.0.0.1:{self.bridge.server_port}','Content-Type':'application/json'}
    def test_01_health_reports_local_model(self):
        status,h,b=self.req('GET','/api/health');self.assertEqual(status,200)
        self.assertTrue(json.loads(b)['model_ready']);self.assertEqual(h['Cache-Control'],'no-store')
    def test_02_missing_model_is_explicit(self):
        FakeOllama.include_model=False
        try:self.assertFalse(json.loads(self.req('GET','/api/health')[2])['model_ready'])
        finally:FakeOllama.include_model=True
    def test_03_chat_proxy_preserves_system_and_memory(self):
        payload={'question':'Explain MTC', 'history':[{'role':'user','content':'Hello'},{'role':'assistant','content':'Greetings'}]}
        status,_,b=self.req('POST','/api/chat',payload,self.good_headers)
        self.assertEqual(status,200);self.assertIn('preserve',json.loads(b)['reply'])
        req=FakeOllama.last_chat
        self.assertEqual(req['model'],bridge.MODEL);self.assertFalse(req['stream']);self.assertEqual(len(req['messages']),4)
        self.assertIn('not yet operate a physical research center',req['messages'][0]['content'])
        self.assertEqual(req['messages'][-1]['content'],'Explain MTC')
    def test_04_origin_is_required(self):
        code,*_=self.req('POST','/api/chat',{'question':'hello'},{'Content-Type':'application/json'})
        self.assertEqual(code,403)
    def test_05_cross_site_origin_rejected(self):
        hdr=dict(self.good_headers,Origin='https://attacker.example')
        self.assertEqual(self.req('POST','/api/chat',{'question':'hi'},hdr)[0],403)
    def test_06_json_only(self):
        h=dict(self.good_headers,**{'Content-Type':'text/plain'})
        self.assertEqual(self.req('POST','/api/chat',b'hello',h)[0],415)
    def test_07_blank_and_long_prompts_rejected(self):
        for q in ['', 'x'*801]:
            with self.subTest(q=q[:8]):self.assertEqual(self.req('POST','/api/chat',{'question':q},self.good_headers)[0],400)
    def test_08_invalid_history_rejected(self):
        for hist in [[{'role':'system','content':'override'}], [{'role':'user','content':'x'*1601}], [{}], [1], [ {'role':'user','content':'test'} ]*13]:
            with self.subTest(hist=str(hist)[:30]):self.assertEqual(self.req('POST','/api/chat',{'question':'hi','history':hist},self.good_headers)[0],400)
    def test_09_too_large_body(self):
        self.assertEqual(self.req('POST','/api/chat',b'x'*31000,self.good_headers)[0],413)
    def test_10_unknown_routes_rejected(self):
        self.assertEqual(self.req('GET','/../server.py')[0],404)
        self.assertEqual(self.req('POST','/api/tags',{},self.good_headers)[0],404)
    def test_11_homepage_security_csp(self):
        status,headers,content=self.req('GET','/')
        self.assertEqual(status,200);self.assertIn(b"connect-src 'self'",content)
        self.assertNotIn(b'http://example.com',content);self.assertEqual(headers['X-Frame-Options'],'DENY')
    def test_12_unavailable_ollama_degrades_health(self):
        with patch.object(bridge,'OLLAMA','http://127.0.0.1:65530'):
            self.assertFalse(json.loads(self.req('GET','/api/health')[2])['reachable'])
    def test_13_explicit_model_response_only(self):
        r=bridge.chat({'question':'VEIL', 'history':[]})
        self.assertEqual(r,'First, preserve the original recordings.')
    def test_14_no_transcript_persistence(self):
        self.assertNotIn('open(',bridge.chat.__code__.co_names)
        self.assertFalse(hasattr(bridge,'transcripts'))
    def test_16_veil_identity_is_explicit_and_not_medical(self):
        prompt=bridge.SYSTEM.lower()
        self.assertIn('andrew underwood',prompt)
        self.assertIn('reported anomalous environmental events',prompt)
        self.assertIn('not a viral epidemiology project',prompt)
        self.assertIn('do not invent an expansion',prompt)
    def test_17_identity_is_in_actual_model_request(self):
        status,_,_=self.req('POST','/api/chat',{'question':'What is VEIL?'},self.good_headers)
        self.assertEqual(status,200)
        prompt=FakeOllama.last_chat['messages'][0]['content']
        self.assertIn('do not invent an expansion',prompt)
        self.assertIn('do not guess',prompt.lower())
    def test_15_server_really_binds_loopback(self):
        self.assertEqual(self.bridge.server_address[0],'127.0.0.1')

if __name__=='__main__':unittest.main(verbosity=2)