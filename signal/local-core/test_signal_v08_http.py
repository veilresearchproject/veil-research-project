"""HTTP endpoints for readiness and private review notes, using only local fake services."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib import request, error

import signal_desktop

class LocalFake:
    model='test-local-model'
    def answer(self,messages):return 'Review the log and do not infer causes.'

class EndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server,cls.state=signal_desktop.make_server(LocalFake())
        cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.worker.start()
        cls.origin='http://127.0.0.1:'+str(cls.server.server_port)
        cls.temp=tempfile.TemporaryDirectory()
        cls.state.review_dir=Path(cls.temp.name)/'notes'
        cls.state.bot.loaded_mtc={'session_id':'20261027_215040_70c105','recorded_seconds':5400.021}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.worker.join(2);cls.temp.cleanup()

    def call(self,url,body=None,token=True):
        h={'X-SIGNAL-Token':self.state.token} if token else {}
        if body is not None:h['Content-Type']='application/json'
        req=request.Request(self.origin+url, data=json.dumps(body).encode() if body is not None else None,headers=h)
        try:
            with request.urlopen(req,timeout=3) as r:return r.status,json.load(r)
        except error.HTTPError as e:return e.code,json.load(e)

    def test_diagnostics_is_opt_in_authorized_and_no_capture(self):
        code,_=self.call('/api/diagnostics',token=False)
        self.assertEqual(code,403)
        with patch.object(signal_desktop.signal_diagnostics,'run_checks',return_value={'ollama':{'status':'ready'},'voice':{},'microphone':{}}) as inspect:
            code,obj=self.call('/api/diagnostics')
        self.assertEqual(code,200)
        inspect.assert_called_once()
        self.assertEqual(obj['ollama']['status'],'ready')
        self.assertEqual(self.state.listener.status()['state'],'idle')

    def test_append_read_private_note(self):
        code,body=self.call('/api/notes',{'time_s':31.251,'classification':'known_source','note':'Door closing when investigator left room'})
        self.assertEqual(code,200)
        self.assertEqual(body['entry']['classification'],'known_source')
        code,notes=self.call('/api/notes')
        self.assertEqual(code,200)
        self.assertTrue(any('Door closing' in x['note'] for x in notes['notes']))
        self.assertEqual(list(self.state.review_dir.glob('*.wav')),[])

    def test_bad_or_unauthorized_notes(self):
        code,_=self.call('/api/notes',{'time_s':30,'classification':'known_source','note':'x'},token=False)
        self.assertEqual(code,403)
        code,_=self.call('/api/notes',{'time_s':999999,'classification':'known_source','note':'x'})
        self.assertEqual(code,422)
        code,_=self.call('/api/notes',{'time_s':30,'classification':'confirmed_paranormal','note':'x'})
        self.assertEqual(code,422)

if __name__=='__main__':unittest.main()
