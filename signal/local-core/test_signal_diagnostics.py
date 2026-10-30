"""No network or real audio required to exercise local readiness checks."""
import json
import unittest
from unittest.mock import patch, Mock
from urllib.error import URLError
import signal_diagnostics as sd

class Response:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, n): return self.data[:n]

class DiagnosticsTests(unittest.TestCase):
    def test_installed_model_and_strict_loopback_url(self):
        seen=[]
        def opener(req, timeout):
            seen.append((req.full_url, timeout))
            return Response(b'{"models":[{"name":"llama3.2:3b"},{"name":"other:latest"}]}')
        result=sd.check_ollama('llama3.2:3b', opener)
        self.assertEqual(result['status'],'ready')
        self.assertEqual(seen,[(sd.OLLAMA_TAGS,2.0)])
        self.assertEqual(result['installed_model_count'],2)

    def test_server_running_model_missing(self):
        r=sd.check_ollama('llama3.2:3b', lambda *a,**k: Response(b'{"models":[{"name":"small:latest"}]}'))
        self.assertEqual(r['status'],'model_missing')

    def test_ollama_missing_is_graceful(self):
        r=sd.check_ollama('llama3.2:3b',lambda *a,**k: (_ for _ in ()).throw(URLError('offline')))
        self.assertEqual(r['status'],'unavailable')
        self.assertNotIn('offline',str(r))

    def test_invalid_response_is_not_ready(self):
        for response in [b'not json', b'null', b'[]', b'{"models":"broken"}',b'{"models":[]}']:
            r=sd.check_ollama('llama3.2:3b',lambda *a,**k: Response(response))
            self.assertNotEqual(r['status'],'ready')

    def test_windows_audio_check_does_not_activate_microphone(self):
        fake=Mock()
        fake.returncode=0
        fake.stdout=b'RECOGNIZER_AVAILABLE\r\n'
        voice=Mock()
        voice.list_voices.return_value=['Local voice']
        with patch.object(sd.os,'name','nt'),patch.object(sd.shutil,'which',return_value='powershell.exe'), \
             patch.object(sd.subprocess,'run',return_value=fake) as process:
            result=sd.check_windows_audio(voice)
        self.assertEqual(result['voice']['status'],'ready')
        self.assertEqual(result['microphone']['status'],'available')
        args=process.call_args.args[0]
        self.assertEqual(args[0], 'powershell.exe')
        self.assertNotIn('SetInputToDefaultAudioDevice',' '.join(args))
        self.assertNotIn('Recognize(',' '.join(args))

    def test_unsupported_platform_no_voice_probe(self):
        voice=Mock()
        with patch.object(sd.os,'name','posix'),patch.object(sd.shutil,'which',return_value=None):
            result=sd.check_windows_audio(voice)
        self.assertEqual(result['microphone']['status'],'unavailable')
        voice.list_voices.assert_not_called()

    def test_combined_checks_clearly_disclose_limits(self):
        result=sd.run_checks('test',Mock(),lambda v:{'voice':{'status':'missing'},'microphone':{'status':'missing'}},lambda v:{'status':'model_missing'})
        self.assertIn('microphone',result['notes'])
        self.assertNotIn('https',json.dumps(result))

if __name__=='__main__': unittest.main()
