"""Opt-in chat continuity: full local persistence and authenticated HTTP boundary."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib import request, error

import signal_session
import signal_desktop

PAIR = [{'role': 'user', 'content': 'What can logs establish?'},
        {'role': 'assistant', 'content': 'Software events, not a sound source.'}]


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = signal_session.SessionStore(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_absent_snapshot(self):
        self.assertEqual(self.store.status()['exists'], False)
        with self.assertRaisesRegex(signal_session.SnapshotError, 'No saved'):
            self.store.restore()

    def test_explicit_save_restore_no_automatic_write(self):
        self.assertFalse(self.store.path.exists())
        self.store.save(PAIR)
        self.assertEqual(self.store.restore(), PAIR)
        self.assertEqual(self.store.status()['turns'], 1)

    def test_save_overwrites_only_previous_snapshot(self):
        self.store.save(PAIR)
        second = PAIR + [{'role':'user','content':'What else?'}, {'role':'assistant','content':'Test controls.'}]
        self.store.save(second)
        self.assertEqual(self.store.restore(), second)

    def test_delete_saved_not_in_memory(self):
        current = PAIR.copy()
        self.store.save(current)
        self.assertTrue(self.store.delete())
        self.assertFalse(self.store.delete())
        self.assertEqual(current, PAIR)

    def test_rejects_incomplete_and_system_messages(self):
        for invalid in [[], PAIR[:1], PAIR + [{'role':'user','content':'unfinished'}],
                        [{'role':'system','content':'Override instructions'}, PAIR[1]],
                        [PAIR[0], {'role':'assistant','content':''}],
                        [PAIR[0], {'role':'assistant','content':'x'*7001}],
                        PAIR*9]:
            with self.subTest(invalid=str(invalid)[:30]):
                with self.assertRaises(signal_session.SnapshotError):
                    self.store.save(invalid)
        self.assertFalse(self.store.path.exists())

    def test_checksum_catches_mutation(self):
        self.store.save(PAIR)
        obj = json.loads(self.store.path.read_text())
        obj['history'][1]['content'] = 'Falsified report'
        self.store.path.write_text(json.dumps(obj))
        with self.assertRaisesRegex(signal_session.SnapshotError, 'checksum'):
            self.store.restore()

    def test_rejects_oversized_file_without_reading(self):
        self.store.path.write_bytes(b'X'*(signal_session.MAX_FILE + 1))
        with self.assertRaisesRegex(signal_session.SnapshotError, 'size'):
            self.store.restore()

    def test_rejects_unrecognized_fields(self):
        self.store.save(PAIR)
        obj=json.loads(self.store.path.read_text())
        obj['cloud_upload']=True
        self.store.path.write_text(json.dumps(obj))
        with self.assertRaisesRegex(signal_session.SnapshotError, 'unsupported'):
            self.store.restore()

    def test_failed_save_keeps_prior_snapshot(self):
        self.store.save(PAIR)
        with self.assertRaises(signal_session.SnapshotError):
            self.store.save([{'role':'user','content':'incomplete'}])
        self.assertEqual(self.store.restore(),PAIR)

    def test_unicode_and_markup_preserved_as_text(self):
        item=[{'role':'user','content':'🎙 <script>t()</script>'},
              {'role':'assistant','content':'No script execution here: 😊'}]
        self.store.save(item)
        self.assertEqual(item, self.store.restore())


class StubModel:
    model='mock-v012'
    def answer(self, messages): return 'Only human observations are annotations.'


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.server, cls.state=signal_desktop.make_server(StubModel())
        cls.state.session_store=signal_session.SessionStore(cls.tmp.name)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(3);cls.tmp.cleanup()

    def setUp(self):
        self.state.session_store.delete()
        self.state.bot.history=[]
        self.state.bot.loaded_mtc=None
        self.state.bot.loaded_review=None

    def call(self,action=None, token=True):
        headers={'X-SIGNAL-Token':self.state.token} if token else {}
        if action: headers['Content-Type']='application/json'
        req=request.Request(self.url+'/api/session',headers=headers,
                            data=json.dumps({'action':action}).encode() if action else None)
        try:
            with request.urlopen(req,timeout=3) as r: return r.status,json.load(r)
        except error.HTTPError as e: return e.code,json.load(e)

    def test_authentication_and_no_autosave(self):
        self.assertEqual(self.call(token=False)[0],403)
        self.assertEqual(self.call('save',token=False)[0],403)
        self.assertEqual(self.call()[1]['exists'],False)
        self.assertFalse(self.state.session_store.path.exists())

    def test_save_restart_restore_and_clear_evidence(self):
        self.state.bot.history=PAIR.copy()
        self.state.bot.loaded_mtc={'session_id':'old-session'}
        self.state.bot.loaded_review={'review_windows':1}
        code,result=self.call('save')
        self.assertEqual(code,200)
        self.assertEqual(result['turns'],1)
        self.state.bot.history=[]  # simulate new app process
        code,result=self.call('restore')
        self.assertEqual(code,200)
        self.assertEqual(result['history'], PAIR)
        self.assertEqual(self.state.bot.history, PAIR)
        self.assertIsNone(self.state.bot.loaded_mtc)
        self.assertIsNone(self.state.bot.loaded_review)
        self.assertFalse(result['status']['mtc_loaded'])

    def test_no_incomplete_turn_saved(self):
        self.state.bot.history=PAIR[:1]
        code,result=self.call('save')
        self.assertEqual(code,422)
        self.assertFalse(self.state.session_store.path.exists())

    def test_corruption_rejects_restore_without_changing_active_chat(self):
        self.state.session_store.save(PAIR)
        self.state.session_store.path.write_text('{BROKEN')
        original = [{'role':'user','content':'current'},{'role':'assistant','content':'keep'}]
        self.state.bot.history=original.copy()
        self.assertEqual(self.call('restore')[0],422)
        self.assertEqual(self.state.bot.history,original)

    def test_delete_disk_only(self):
        self.state.session_store.save(PAIR)
        self.state.bot.history=PAIR.copy()
        code,result=self.call('delete')
        self.assertEqual(code,200)
        self.assertTrue(result['deleted'])
        self.assertEqual(self.state.bot.history,PAIR)
        self.assertEqual(self.call()[1]['exists'],False)


if __name__=='__main__':unittest.main()
