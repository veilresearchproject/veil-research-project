"""Check authenticated opt-in export; no WAV or Ollama needed."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib import request, error

import signal_desktop
import signal_annotations


class FakeModel:
    model = 'local-test-no-ollama'
    def answer(self, messages):return 'No automatic interpretations.'


class ExportHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.state = signal_desktop.make_server(FakeModel())
        cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.worker.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.temp=tempfile.TemporaryDirectory()
        cls.state.review_dir=Path(cls.temp.name)/'notes'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.worker.join(3);cls.temp.cleanup()
    def get(self, url, auth=True):
        headers={'X-SIGNAL-Token':self.state.token} if auth else {}
        req=request.Request(self.base+url,headers=headers)
        try:
            with request.urlopen(req,timeout=3) as r:return r.status,r.read(),dict(r.headers)
        except error.HTTPError as exc:return exc.code,exc.read(),dict(exc.headers)
    def setUp(self):
        self.state.bot.loaded_mtc = None
        self.state.bot.loaded_review = None
    def test_auth_and_no_loaded_session(self):
        code,_,_=self.get('/api/export?format=json',auth=False)
        self.assertEqual(code,403)
        code,data,_=self.get('/api/export?format=json')
        self.assertEqual(code,422)
        self.assertIn('Load verified MTC',data.decode())
    def test_export_json_html_preserves_notes_and_doesnt_use_model(self):
        self.state.bot.loaded_mtc={'session_id':'MTC_HTTP_TEST','recorded_seconds':120.0,
            'outcome':'complete','events':8,'segments_declared':1,
            'file_integrity':{'session_metadata.json':True,'events.jsonl':True}}
        signal_annotations.append_note(self.state.review_dir,self.state.bot.loaded_mtc,
                                       32.2,'known_source','Door closing at departure')
        before = (self.state.review_dir/'MTC_HTTP_TEST.jsonl').read_bytes()
        code,data,headers=self.get('/api/export?format=json')
        self.assertEqual(code,200)
        self.assertEqual(json.loads(data)['note_count'],1)
        self.assertEqual(json.loads(data)['investigator_notes'][0]['note'],'Door closing at departure')
        self.assertIn('attachment;',headers['Content-Disposition'])
        code,page,_=self.get('/api/export?format=html')
        self.assertEqual(code,200)
        self.assertIn(b'Door closing at departure',page)
        self.assertIn(b'not the original WAV recordings',page)
        self.assertEqual(before,(self.state.review_dir/'MTC_HTTP_TEST.jsonl').read_bytes())
    def test_unknown_format_is_blocked(self):
        self.assertEqual(self.get('/api/export?format=csv')[0],422)
        self.assertEqual(self.get('/api/export?format=html&format=json')[0],422)

if __name__=='__main__':unittest.main()
