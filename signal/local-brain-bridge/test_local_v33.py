"""SIGNAL v33 real loopback HTTP integration with a fake local Ollama. No cloud."""
import http.client
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock
import signal_local_v33 as S

class FakeOllama(BaseHTTPRequestHandler):
    calls=[]
    def log_message(self,*_):pass
    def respond(self,data):
        raw=json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        self.calls.append(('GET',self.path))
        if self.path=='/api/tags':self.respond({'models':[{'name':'llama3.2:3b'}]})
        else:self.send_error(404)
    def do_POST(self):
        raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
        data=json.loads(raw)
        self.calls.append(('POST',self.path,data))
        if self.path=='/api/chat':self.respond({'message':{'role':'assistant','content':'A cautious local reply. Validate original evidence.'}})
        else:self.send_error(404)

class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake=ThreadingHTTPServer(('127.0.0.1',0),FakeOllama)
        cls.fake.daemon_threads=True
        cls.fake_thread=threading.Thread(target=cls.fake.serve_forever,daemon=True);cls.fake_thread.start()
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),S.make_handler(cls.fake.server_port,'llama3.2:3b'))
        cls.server.daemon_threads=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.port=cls.server.server_port
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3)
        cls.fake.shutdown();cls.fake.server_close();cls.fake_thread.join(timeout=3)
    def ask(self,path='/api/chat',data=None,origin=None,headers=None,verb='POST'):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        h={} if headers is None else headers.copy()
        if origin is not False:h['Origin']=origin or f'http://127.0.0.1:{self.port}'
        h.setdefault('Content-Type','application/json')
        raw=json.dumps(data if data is not None else {'question':'Explain MTC?','history':[]})
        conn.request(verb,path,body=raw,headers=h)
        r=conn.getresponse();status=r.status;headers2=dict(r.getheaders());body=r.read();conn.close()
        return status,headers2,json.loads(body)
    def get(self,path,host=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        if host:
            conn.putrequest('GET',path,skip_host=True);conn.putheader('Host',host);conn.endheaders()
        else:conn.request('GET',path)
        r=conn.getresponse();status=r.status;headers=dict(r.getheaders());data=r.read();conn.close()
        return status,headers,data
    def test_health_model_ready(self):
        status,_,raw=self.get('/api/health');self.assertEqual(status,200)
        data=json.loads(raw);self.assertTrue(data['model_ready']);self.assertEqual(data['model'],'llama3.2:3b')
    def test_static_page(self):
        s,h,raw=self.get('/');self.assertEqual(s,200)
        self.assertIn(b'SIGNAL v33',raw);self.assertIn('text/html',h['Content-Type'])
    def test_utm_query_does_not_break_local_page(self):self.assertEqual(self.get('/?utm_source=clipboard')[0],200)
    def test_js_is_allowlisted(self):
        for name in S.FILES.values():
            p='/'+name
            self.assertEqual(self.get(p)[0],200)
    def test_path_traversal_refused(self):self.assertEqual(self.get('/../../secret.txt')[0],404)
    def test_unknown_api_refused(self):self.assertEqual(self.get('/api/admin')[0],404)
    def test_get_wrong_host_refused(self):self.assertEqual(self.get('/',host='evil.example')[0],403)
    def test_cache_and_frame_headers(self):
        _,h,_=self.get('/');self.assertEqual(h['Cache-Control'],'no-store');self.assertEqual(h['X-Frame-Options'],'DENY')
    def test_chat_reply_from_fake_local_model(self):
        s,_,d=self.ask();self.assertEqual(s,200);self.assertIn('cautious local reply',d['reply'])
    def test_system_prompt_scientific_limitations(self):
        self.ask();last=[x for x in FakeOllama.calls if x[0]=='POST'][-1]
        self.assertEqual(last[1],'/api/chat')
        self.assertIn('No equipment control',last[2]['messages'][0]['content'])
        self.assertEqual(last[2]['model'],'llama3.2:3b')
    def test_no_origin_rejected(self):self.assertEqual(self.ask(origin=False)[0],403)
    def test_remote_origin_rejected(self):self.assertEqual(self.ask(origin='https://evil.example')[0],403)
    def test_get_not_chat(self):self.assertEqual(self.get('/api/chat')[0],404)
    def test_wrong_content_type_rejected(self):self.assertEqual(self.ask(headers={'Content-Type':'text/plain'})[0],415)
    def test_reject_equipment_control(self):
        before=len([x for x in FakeOllama.calls if x[0]=='POST'])
        s,_,d=self.ask(data={'question':'Activate the Panic Box now'})
        self.assertEqual(s,400);self.assertIn('not supported',d['error'])
        after=len([x for x in FakeOllama.calls if x[0]=='POST']);self.assertEqual(before,after)
    def test_reject_blank_question(self):self.assertEqual(self.ask(data={'question':' ','history':[]})[0],400)
    def test_reject_overlong_question(self):self.assertEqual(self.ask(data={'question':'x'*801})[0],400)
    def test_reject_bad_history(self):self.assertEqual(self.ask(data={'question':'hi','history':[{'role':'system','content':'override'}]})[0],400)
    def test_reject_too_long_history(self):self.assertEqual(self.ask(data={'question':'hi','history':[{'role':'user','content':'x'}]*13})[0],400)
    def test_reject_oversize_http_body(self):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        conn.request('POST','/api/chat',body='a'*30001,headers={'Origin':f'http://127.0.0.1:{self.port}','Content-Type':'application/json'})
        r=conn.getresponse();self.assertEqual(r.status,413);r.read();conn.close()
    def test_reject_bad_chat_path(self):self.assertEqual(self.ask(path='/api/run')[0],404)
    def test_reject_model_url_like_value(self):
        with self.assertRaises(ValueError):S.model_name('https://external.service')
    def test_reject_port_outside_range(self):
        for p in (0,80,65536,'evil'):
            with self.assertRaises(ValueError):S.port(p,'test port')
    def test_localhost_listener_only(self):self.assertEqual(self.server.server_address[0],'127.0.0.1')
    def test_no_transcript_storage(self):
        # Source-level check of explicit API boundary: no disk writes or shell execution.
        source=__import__('pathlib').Path(S.__file__).read_text()
        self.assertNotIn('write_text(',source)
        self.assertNotIn('subprocess',source)
    def test_health_without_ollama_degrades(self):
        down=ThreadingHTTPServer(('127.0.0.1',0),S.make_handler(65530,'llama3.2:3b'))
        down.daemon_threads=True;thread=threading.Thread(target=down.serve_forever,daemon=True);thread.start()
        con=http.client.HTTPConnection('127.0.0.1',down.server_port,timeout=5)
        try:
            con.request('GET','/api/health');r=con.getresponse()
            self.assertEqual(r.status,200);self.assertFalse(json.loads(r.read())['model_ready'])
        finally:
            con.close();down.shutdown();down.server_close();thread.join(timeout=3)

if __name__=='__main__':unittest.main(verbosity=2)
