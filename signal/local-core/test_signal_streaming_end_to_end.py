"""Real loopback HTTP integration: SIGNAL desktop -> Ollama-compatible mock endpoint.

No cloud, no real model, no microphone or speaker. This test deliberately exercises
Python's real streaming HTTP client rather than only a patched urlopen object.
"""
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import request
from unittest.mock import patch

import signal_core as core
import signal_desktop as desktop


class MockOllama(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_POST(self):
        length=int(self.headers['Content-Length'])
        data=json.loads(self.rfile.read(length))
        self.server.calls.append(data)
        self.send_response(200)
        self.send_header('Content-Type','application/x-ndjson')
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        if data['stream']:
            for text,done in [('JSON logs ',False),('cannot verify audio.',True)]:
                frame={'message':{'role':'assistant','content':text},'done':done}
                self.wfile.write(json.dumps(frame).encode()+b'\n')
                self.wfile.flush()
        else:
            frame={'message':{'role':'assistant','content':'Logs cannot prove what was audible.'}}
            self.wfile.write(json.dumps(frame).encode())
            self.wfile.flush()


class FullLoopbackStreamingTest(unittest.TestCase):
    def setUp(self):
        self.mock=ThreadingHTTPServer(('127.0.0.1',0),MockOllama)
        self.mock.calls=[]
        self.fake_worker=threading.Thread(target=self.mock.serve_forever,daemon=True)
        self.fake_worker.start()
        self.url=f'http://127.0.0.1:{self.mock.server_port}/api/chat'
        self.patch=patch.object(core,'LOCAL_URL',self.url)
        self.patch.start()
        self.server,self.state=desktop.make_server(core.LocalModel('fake:tiny'))
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.worker.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
        self.tmp=tempfile.TemporaryDirectory()
        self.state.bot.memories=core.Memories(self.tmp.name)
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.worker.join(2)
        self.mock.shutdown();self.mock.server_close();self.fake_worker.join(2)
        self.patch.stop();self.tmp.cleanup()

    def send(self,endpoint,payload):
        headers={'Content-Type':'application/json','X-SIGNAL-Token':self.state.token}
        req=request.Request(self.base+endpoint,headers=headers,data=json.dumps(payload).encode())
        with request.urlopen(req,timeout=6) as resp:
            return resp.status,resp.read().decode()

    def test_real_network_round_trip_streams_tokens_then_commits(self):
        status,body=self.send('/api/chat/stream',{'message':'What can logs prove?'})
        self.assertEqual(status,200)
        frames=[json.loads(x) for x in body.strip().split('\n')]
        self.assertEqual([x['event'] for x in frames],['delta','delta','complete'])
        self.assertEqual(''.join(x.get('text','') for x in frames),'JSON logs cannot verify audio.')
        self.assertEqual(self.state.bot.history[-1]['content'],'JSON logs cannot verify audio.')
        self.assertEqual(len(self.mock.calls),1)
        self.assertTrue(self.mock.calls[0]['stream'])
        self.assertEqual(self.mock.calls[0]['model'],'fake:tiny')
        self.assertFalse(self.state.bot.voice.enabled)

    def test_nonstream_model_check_uses_distinct_request_and_no_history(self):
        status,body=self.send('/api/model-check',{})
        result=json.loads(body)
        self.assertEqual(status,200)
        self.assertEqual(result['status'],'responded')
        self.assertEqual(len(self.state.bot.history),0)
        self.assertEqual(len(self.mock.calls),1)
        self.assertFalse(self.mock.calls[0]['stream'])

if __name__ == '__main__': unittest.main()
