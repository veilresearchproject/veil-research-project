"""Live loopback HTTP regression tests. No internet, Ollama, speaker or microphone."""
import json
from pathlib import Path
import re
import threading
import unittest
from urllib import request, error

import signal_desktop


class FakeModel:
    model='mocked-local-model'
    def answer(self, messages):
        self.last_messages=messages
        return 'Evidence first. The source has not been identified.'


class DesktopServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=FakeModel()
        cls.server,cls.state=signal_desktop.make_server(cls.model)
        cls.thread=threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url='http://127.0.0.1:'+str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def fetch(self, route, content=None, token=True, origin=None, host=None):
        headers={}
        if token: headers['X-SIGNAL-Token']=self.state.token
        if origin: headers['Origin']=origin
        if host: headers['Host']=host
        if content is not None: headers['Content-Type']='application/json'
        req=request.Request(self.url+route,data=(json.dumps(content).encode('utf8') if content is not None else None),headers=headers)
        try:
            with request.urlopen(req,timeout=4) as resp:
                return resp.status,resp.headers,resp.read()
        except error.HTTPError as e:
            return e.code,e.headers,e.read()

    def test_landing_page_contains_local_token_and_no_external_assets(self):
        status,headers,body=self.fetch('/',token=False)
        self.assertEqual(status,200)
        self.assertIn(self.state.token.encode(),body)
        self.assertIn(b'VEIL RESEARCH PROJECT',body)
        self.assertNotIn(b'https://',body)
        self.assertIn('connect-src \'self\'',headers['Content-Security-Policy'])
        self.assertEqual(headers['Cache-Control'],'no-store')

    def test_all_character_expressions_are_served_locally(self):
        for name in signal_desktop.FACES:
            with self.subTest(name=name):
                status,headers,body=self.fetch('/face_assets/'+name+'.webp',token=False)
                self.assertEqual(status,200)
                self.assertEqual(headers['Content-Type'],'image/webp')
                self.assertGreater(len(body),1000)

    def test_unauthorized_request_rejected(self):
        status,_,_=self.fetch('/api/status',token=False)
        self.assertEqual(status,403)
        status,_,_=self.fetch('/api/chat',{'message':'hello'},token=False)
        self.assertEqual(status,403)

    def test_cross_origin_and_host_rejected(self):
        status,_,_=self.fetch('/api/chat',{'message':'hi'},origin='https://not-veil.example')
        self.assertEqual(status,403)
        status,_,_=self.fetch('/api/status',host='not-veil.example')
        self.assertEqual(status,403)

    def test_real_mock_model_output_and_no_mutation(self):
        status,_,body=self.fetch('/api/chat',{'message':'Is this sound a ghost?'})
        self.assertEqual(status,200)
        result=json.loads(body)
        self.assertIn('Evidence first.',result['reply'])
        self.assertEqual(self.model.last_messages[-1]['content'],'Is this sound a ghost?')
        self.assertFalse(result['status']['voice_enabled'])
        self.assertFalse(result['status']['mic_enabled'])

    def test_voice_requires_windows_and_remains_off(self):
        status,_,body=self.fetch('/api/voice',{'action':'on'})
        if signal_desktop.os.name != 'nt':
            self.assertEqual(status,422)
            self.assertIn('Windows',json.loads(body)['error'])
        status,_,body=self.fetch('/api/status')
        self.assertEqual(status,200)
        self.assertFalse(json.loads(body)['voice_enabled'])

    def test_unapproved_route_not_exposed(self):
        status,_,_=self.fetch('/signal_core.py',token=False)
        self.assertEqual(status,404)
        status,_,_=self.fetch('/api/execute',{'cmd':'rm -rf'},token=True)
        self.assertEqual(status,404)
        status,_,_=self.fetch('/../../etc/passwd',token=False)
        self.assertEqual(status,404)

    def test_bad_data_is_rejected(self):
        status,_,_=self.fetch('/api/chat',{'message':'a'*4001})
        self.assertEqual(status,422)
        status,_,_=self.fetch('/api/voice',{'action':'rate','rate':'fast'})
        self.assertEqual(status,422)

    def test_explicit_demo_is_labeled(self):
        model=signal_desktop.DemoModel()
        self.assertIn('scripted',model.answer([{'content':'hello'}]).lower())
        self.assertEqual(signal_desktop.SessionState(model).mode,'demo')


if __name__=='__main__':
    unittest.main(verbosity=2)
