"""SIGNAL v43 local HTTP and isolation tests; no real Ollama or hardware."""
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from signal_local_v43 import make_unified_handler


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage=tempfile.TemporaryDirectory()
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_unified_handler(65530,'llama3.2:3b',Path(cls.storage.name)))
        cls.server.daemon_threads=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.origin='http://127.0.0.1:%d'%cls.server.server_port
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=2);cls.storage.cleanup()
    def fetch(self,path='/',method='GET',data=None,headers=None):
        return urlopen(Request(self.origin+path,data=data,method=method,headers=headers or {}),timeout=5)
    def test_root_v43(self):
        with self.fetch() as r:self.assertIn(b'SIGNAL',r.read());self.assertEqual(r.status,200)
    def test_static_workflow_core(self):
        with self.fetch('/workflow-core.js') as r:self.assertIn(b'SIGNALWorkflow',r.read())
    def test_static_packet_core(self):
        with self.fetch('/packet-core.js') as r:self.assertIn(b'SIGNALPacket',r.read())
    def test_inherited_audio_core(self):
        with self.fetch('/audio-core.js') as r:self.assertIn(b'SIGNALAudio',r.read())
    def test_inherited_v33_geometric(self):
        with self.fetch('/v33.html') as r:self.assertIn(b'SIGNAL',r.read())
    def test_no_paths_outside_allowlist(self):
        with self.assertRaises(HTTPError) as ctx:self.fetch('/signal_local_v43.py')
        self.assertEqual(ctx.exception.code,404)
    def test_no_remote_host(self):
        req=Request(self.origin+'/workflow-core.js',headers={'Host':'evil.example'})
        with self.assertRaises(HTTPError) as ctx:urlopen(req,timeout=5)
        self.assertEqual(ctx.exception.code,403)
    def test_no_unapproved_memory(self):
        body=json.dumps({'kind':'project','note':'Unapproved notes','source':'test','approvedBy':'T','approved':False}).encode()
        with self.assertRaises(HTTPError) as ctx:self.fetch('/api/memory/add','POST',body,{'Origin':self.origin,'Content-Type':'application/json'})
        self.assertEqual(ctx.exception.code,400)
    def test_no_cross_origin_memory_write(self):
        body=b'{}'
        with self.assertRaises(HTTPError) as ctx:self.fetch('/api/memory/add','POST',body,{'Origin':'https://evil.invalid','Content-Type':'application/json'})
        self.assertEqual(ctx.exception.code,403)
    def test_memory_endpoint_empty(self):
        with self.fetch('/api/memory') as r:self.assertEqual(json.load(r)['entries'],[])
    def test_old_ai_not_started(self):
        with self.fetch('/api/health') as r:self.assertFalse(json.load(r)['model_ready'])
    def test_no_nonexistent_control(self):
        with self.assertRaises(HTTPError) as ctx:self.fetch('/api/panic-box/clear','POST',b'{}',{'Origin':self.origin,'Content-Type':'application/json'})
        self.assertEqual(ctx.exception.code,404)

if __name__=='__main__':unittest.main()
