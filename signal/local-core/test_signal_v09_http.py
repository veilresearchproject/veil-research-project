"""Only local simulated HTTP interactions. No Ollama or microphone capture."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib import request,error
import signal_desktop
from test_signal_review_import import SESSION


class Model:
    model='mock-local-model'
    def __init__(self): self.received=[]
    def answer(self,msg):
        self.received.append(msg)
        return 'Scanner flags are not evidence of a voice.'


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=Model()
        cls.server,cls.state=signal_desktop.make_server(cls.model)
        cls.state.bot.loaded_mtc={**SESSION,'software_version':'0.1.4-overnight','outcome':'COMPLETE',
            'fault_count':0,'question_starts_logged':121,'question_ends_completed_logged':121,
            'response_windows_completed_logged':121,'cycles_started_logged':12,'cycles_completed_logged':11,
            'question_files_listed':11,'limitations':'Log-only checks, no WAV reviewed.'}
        cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.worker.start()
        cls.host='http://127.0.0.1:'+str(cls.server.server_port)
        cls.temp=tempfile.TemporaryDirectory()
        cls.file=Path(cls.temp.name)/'review_summary.json'
        cls.report={'tool':'VEIL MTC local audio review','version':'0.3',
            'session_id':SESSION['session_id'],'duration_seconds':5400.021,'segments':2,
            'candidates':[{'start':32,'end':34,'score':10,'reason':'sharp peak','phase':'settling'},
                          {'start':33,'end':35,'score':12,'reason':'level rise','phase':'settling'}]}
        cls.file.write_text(json.dumps(cls.report))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.worker.join(2);cls.temp.cleanup()

    def call(self,route,data=None,token=True):
        h={'X-SIGNAL-Token':self.state.token} if token else {}
        if data is not None:h['Content-Type']='application/json'
        req=request.Request(self.host+route,headers=h,data=json.dumps(data).encode() if data is not None else None)
        try:
            with request.urlopen(req,timeout=4) as resp:return resp.status,json.load(resp)
        except error.HTTPError as exc:return exc.code,json.load(exc)

    def test_auth_and_load_and_conversation(self):
        self.assertEqual(self.call('/api/review',token=False)[0],403)
        self.assertEqual(self.call('/api/review',{'action':'load','path':str(self.file)},token=False)[0],403)
        status,data=self.call('/api/review',{'action':'load','path':str(self.file)})
        self.assertEqual(status,200)
        self.assertEqual(data['review']['review_windows'],1)
        status,data=self.call('/api/review')
        self.assertEqual(status,200)
        self.assertEqual(data['review']['raw_candidates'],2)
        status,reply=self.call('/api/chat',{'message':'What can these acoustic flags establish?'})
        self.assertEqual(status,200)
        system=self.model.received[-1][0]['content']
        self.assertIn('2 scanner flags, grouped into 1',system)
        self.assertNotIn(str(self.file),system)

    def test_bad_import_retains_old_report(self):
        self.call('/api/review',{'action':'load','path':str(self.file)})
        status,_=self.call('/api/review',{'action':'load','path':str(self.file)+'does-not-exist'})
        self.assertEqual(status,422)
        status,data=self.call('/api/review')
        self.assertEqual(status,200)
        self.assertEqual(data['review']['review_windows'],1)

    def test_clear_and_no_mic(self):
        self.call('/api/review',{'action':'load','path':str(self.file)})
        status,data=self.call('/api/review',{'action':'clear'})
        self.assertEqual(status,200)
        self.assertIsNone(data['review'])
        self.assertIsNone(self.state.bot.loaded_review)
        self.assertEqual(self.state.listener.status()['state'],'idle')

    def test_latest_uses_validated_local_report(self):
        from unittest.mock import patch
        with patch.object(signal_desktop.signal_review_import,'latest_report',return_value={'review_windows':1,'session_id':SESSION['session_id']}) as fake:
            status,data=self.call('/api/review',{'action':'latest'})
        self.assertEqual(status,200)
        self.assertEqual(data['review']['review_windows'],1)
        fake.assert_called_once()
        self.assertEqual(fake.call_args.args[0]['session_id'],SESSION['session_id'])

    def test_unloaded_session_cannot_import(self):
        old=self.state.bot.loaded_mtc
        self.state.bot.loaded_mtc=None
        try:
            code,_=self.call('/api/review',{'action':'load','path':str(self.file)})
            self.assertEqual(code,422)
        finally:self.state.bot.loaded_mtc=old


if __name__ == '__main__':unittest.main(verbosity=2)
