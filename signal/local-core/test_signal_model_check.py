"""Explicit local Ollama smoke test must not alter transcript, notes, mic or voice."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib import request, error

import signal_desktop

class Fake:
    model='test-local-model'
    calls=0
    def answer(self, messages):
        self.calls+=1
        assert len(messages)==2 and messages[1]['role']=='user'
        return 'The JSON log cannot prove what was audible in the room.'

class ModelEndpointTests(unittest.TestCase):
    def setUp(self):
        self.model=Fake()
        self.server,self.state=signal_desktop.make_server(self.model)
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.worker.start()
        self.base='http://127.0.0.1:'+str(self.server.server_port)
        self.temp=tempfile.TemporaryDirectory()
        self.state.review_dir=Path(self.temp.name)/'notes'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.worker.join(2);self.temp.cleanup()
    def call(self,token=True):
        headers={'Content-Type':'application/json'}
        if token:headers['X-SIGNAL-Token']=self.state.token
        r=request.Request(self.base+'/api/model-check',headers=headers,data=b'{}')
        try:
            with request.urlopen(r,timeout=3) as response:return response.status,json.load(response)
        except error.HTTPError as exc:return exc.code,json.load(exc)
    def test_opt_in_fixed_prompt_and_no_history(self):
        self.assertEqual(self.call(False)[0],403)
        self.assertEqual(self.model.calls,0)
        code,obj=self.call()
        self.assertEqual(code,200)
        self.assertEqual(obj['status'],'responded')
        self.assertIn('cannot prove',obj['reply_preview'])
        self.assertEqual(self.model.calls,1)
        self.assertEqual(self.state.bot.history,[])
        self.assertFalse(self.state.bot.voice.enabled)
        self.assertEqual(self.state.listener.status()['state'],'idle')
        self.assertFalse(self.state.review_dir.exists())
    def test_demo_cannot_masquerade_as_local_model(self):
        self.state.mode='demo'
        self.assertEqual(self.call()[0],422)
        self.assertEqual(self.model.calls,0)

if __name__=='__main__':unittest.main()
