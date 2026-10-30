"""Installed-voice selection and JSON speech transport, without Windows hardware."""
import io
import json
import threading
import unittest
from unittest.mock import Mock, patch
from urllib import request, error

import signal_voice
import signal_desktop


class VoiceSelectionTests(unittest.TestCase):
    def test_inventory_timeout_reports_failure_without_changing_voice(self):
        voice=signal_voice.WindowsVoice();voice.selected_voice='Existing'
        with patch.object(voice,'_require_windows'),patch.object(signal_voice.subprocess,'run',side_effect=signal_voice.subprocess.TimeoutExpired('powershell',15)):
            with self.assertRaisesRegex(RuntimeError,'inventory could not be read'):
                voice.set_voice('New')
        self.assertEqual(voice.selected_voice,'Existing');self.assertFalse(voice.enabled)

    def test_select_installed_voice_and_default_without_enabling_audio(self):
        voice = signal_voice.WindowsVoice()
        with patch.object(voice, '_require_windows'), patch.object(voice, 'list_voices', return_value=['Local David']), patch.object(signal_voice.subprocess, 'Popen') as launch:
            voice.set_voice('Local David')
            self.assertEqual(voice.selected_voice, 'Local David')
            self.assertFalse(voice.enabled)
            voice.set_voice(None)
            self.assertIsNone(voice.selected_voice)
            self.assertFalse(voice.enabled)
            launch.assert_not_called()

    def test_invalid_or_missing_voice_preserves_selection(self):
        voice = signal_voice.WindowsVoice();voice.selected_voice='Existing'
        with patch.object(voice, '_require_windows'), patch.object(voice, 'list_voices', return_value=['Existing']):
            for name in ['Not installed', '', 'x'*201, 'voice\ncommand', 2, True, {}]:
                with self.subTest(name=name), self.assertRaises(ValueError): voice.set_voice(name)
                self.assertEqual(voice.selected_voice, 'Existing')

    def test_voice_name_and_text_are_data_not_powershell_source(self):
        class Pipe(io.BytesIO):
            def close(self): self.saved=self.getvalue();super().close()
        proc=Mock();proc.stdin=Pipe();proc.poll.return_value=0
        name="A voice'); $(not-a-command)"
        voice=signal_voice.WindowsVoice()
        with patch.object(voice, '_require_windows'), patch.object(voice,'list_voices',return_value=[name]), patch.object(signal_voice.subprocess,'Popen',return_value=proc) as launch:
            voice.set_voice(name);voice.enable();voice.speak('A Unicode sample: café.')
        self.assertEqual(json.loads(proc.stdin.saved), {'text':'A Unicode sample: café.','voice':name})
        self.assertNotIn(name,repr(launch.call_args.args[0]))
        self.assertIn('ConvertFrom-Json',launch.call_args.args[0][-1])
        self.assertNotIn('shell',launch.call_args.kwargs)

    def test_voice_inventory_does_not_hold_stop_lock(self):
        voice=signal_voice.WindowsVoice();entered=threading.Event();release=threading.Event();failures=[]
        def listing():
            entered.set()
            if not release.wait(3): raise RuntimeError('Synthetic inventory timeout')
            return ['Local David']
        def select():
            try:voice.set_voice('Local David')
            except Exception as exc:failures.append(exc)
        with patch.object(voice,'_require_windows'),patch.object(voice,'list_voices',side_effect=listing):
            voice.enable();worker=threading.Thread(target=select,daemon=True);worker.start()
            try:
                self.assertTrue(entered.wait(2));voice.disable()
                self.assertFalse(voice.enabled);self.assertTrue(worker.is_alive())
            finally:release.set();worker.join(2)
        self.assertFalse(worker.is_alive());self.assertEqual(failures,[])
        self.assertEqual(voice.selected_voice,'Local David');self.assertFalse(voice.enabled)


class VoiceChoiceHTTPTests(unittest.TestCase):
    def setUp(self):
        self.server,self.state=signal_desktop.make_server(signal_desktop.DemoModel())
        self.voice=self.state.bot.voice
        self.windows=patch.object(self.voice,'_require_windows');self.windows.start()
        self.inventory=patch.object(self.voice,'list_voices',return_value=['Local David','Local Zira'])
        self.listing=self.inventory.start()
        self.processes=patch.object(signal_voice.subprocess,'Popen');self.launch=self.processes.start()
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True);self.worker.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.worker.join(2)
        self.windows.stop();self.inventory.stop();self.processes.stop()

    def call(self,data,token=True,origin=None):
        headers={'Content-Type':'application/json'}
        if token:headers['X-SIGNAL-Token']=self.state.token
        if origin:headers['Origin']=origin
        req=request.Request(self.base+'/api/voice',json.dumps(data).encode(),headers)
        try:
            with request.urlopen(req,timeout=3) as response:return response.status,json.load(response)
        except error.HTTPError as exc:return exc.code,json.load(exc)

    def test_list_and_selection_do_not_generate_or_activate_audio(self):
        self.state.bot.history=[{'role':'user','content':'existing context'}]
        code,result=self.call({'action':'list'})
        self.assertEqual(code,200);self.assertEqual(result['voices'],['Local David','Local Zira'])
        code,result=self.call({'action':'select','name':'Local Zira'})
        self.assertEqual(code,200);self.assertEqual(result['status']['voice_name'],'Local Zira')
        self.assertFalse(result['status']['voice_enabled']);self.assertFalse(result['status']['mic_enabled'])
        self.assertEqual(len(self.state.bot.history),1);self.launch.assert_not_called()

    def test_explicit_default_is_distinct_from_missing_field(self):
        self.voice.selected_voice='Local David'
        self.assertEqual(self.call({'action':'select'})[0],422)
        self.assertEqual(self.voice.selected_voice,'Local David')
        code,result=self.call({'action':'select','name':None})
        self.assertEqual(code,200);self.assertIsNone(result['status']['voice_name'])

    def test_invalid_selection_leaves_current_voice_unchanged(self):
        self.voice.selected_voice='Local David'
        self.assertEqual(self.call({'action':'select','name':'Unknown'})[0],422)
        self.assertEqual(self.voice.selected_voice,'Local David');self.launch.assert_not_called()

    def test_selection_keeps_token_origin_and_busy_guards(self):
        self.assertEqual(self.call({'action':'select','name':'Local Zira'},token=False)[0],403)
        self.assertEqual(self.call({'action':'list'},origin='https://foreign.example')[0],403)
        self.listing.assert_not_called()
        with self.state.lock:
            self.assertEqual(self.call({'action':'select','name':'Local Zira'})[0],409)
        self.assertIsNone(self.voice.selected_voice)


if __name__=='__main__':unittest.main()
