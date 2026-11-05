"""Deterministic unit tests for SIGNAL v32 readiness; uses no public network."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
import signal_doctor as D

class FakeHTTP:
    status=200
    def __enter__(self):return self
    def __exit__(self,*_):return False
    def read(self,n):return json.dumps({'models':[{'name':'llama3.2:3b'}]}).encode()

class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def required(self):
        for n in D.REQUIRED:
            (self.root/n).write_text('print("test preview")\n'+'x'*100)
        (self.root/'v31_server.py').write_text('print("syntax okay")\n'+'#'*100)
    def test_empty_folder_warns_and_fails_files(self):
        r=D.audit(self.root)
        self.assertFalse(r['launch_ready'])
        self.assertGreater(r['totals']['FAIL'],0)
        self.assertEqual(next(x for x in r['results'] if x['check']=='base-bridge')['status'],'WARN')
    def test_fully_populated_launch_ready(self):
        self.required();(self.root/'server.py').write_text('print("old bridge")\n')
        r=D.audit(self.root)
        self.assertEqual(r['totals']['FAIL'],0)
        self.assertTrue(r['launch_ready'])
    def test_existing_preview_without_bridge_not_ready(self):
        self.required();r=D.audit(self.root)
        self.assertFalse(r['launch_ready'])
        self.assertEqual(r['totals']['FAIL'],0)
    def test_python_syntax_failure(self):
        self.required();(self.root/'v31_server.py').write_text('if this is invalid python\n'+'#'*100)
        self.assertEqual(D.compile_preview(self.root)['status'],'FAIL')
    def test_symlink_file_rejected(self):
        self.required();(self.root/'clock-core.js').unlink()
        (self.root/'clock-core.js').symlink_to(self.root/'casebook-core.js')
        d={x['check']:x['status'] for x in D.inspect_files(self.root)}
        self.assertEqual(d['file:clock-core.js'],'FAIL')
    def test_malformed_model_name_never_queries(self):
        with mock.patch.object(D,'urlopen') as send:
            r=D.check_ollama('https://somewhere.example')
        self.assertEqual(r['status'],'FAIL');send.assert_not_called()
    def test_local_model_ready(self):
        with mock.patch.object(D,'urlopen',return_value=FakeHTTP()) as call:
            r=D.check_ollama('llama3.2:3b')
        self.assertEqual(r['status'],'PASS')
        self.assertIn('127.0.0.1',call.call_args.args[0].full_url)
    def test_model_absent_no_download(self):
        with mock.patch.object(D,'urlopen',return_value=FakeHTTP()):
            r=D.check_ollama('other:7b')
        self.assertEqual(r['status'],'WARN')
    def test_unreachable_model_warn_only(self):
        with mock.patch.object(D,'urlopen',side_effect=OSError('not running')):
            self.assertEqual(D.check_ollama('llama3.2:3b')['status'],'WARN')
    def test_no_connections_by_default(self):
        self.required()
        with mock.patch.object(D,'urlopen') as request,mock.patch.object(D.socket,'create_connection') as socket:
            D.audit(self.root)
        request.assert_not_called();socket.assert_not_called()
    def test_optional_tests_not_run_by_default(self):
        self.required()
        with mock.patch.object(D.subprocess,'run') as run:D.audit(self.root)
        run.assert_not_called()
    def test_node_test_success(self):
        (self.root/'test_blind.cjs').write_text('sample')
        with mock.patch.object(D.shutil,'which',return_value='/usr/bin/node'),mock.patch.object(D.subprocess,'run',return_value=mock.Mock(returncode=0,stdout='23/23 passed')):
            report=D.run_test_scripts(self.root)
        self.assertEqual(next(x for x in report if x['check']=='test:test_blind.cjs')['status'],'PASS')
    def test_node_test_failure(self):
        (self.root/'test_blind.cjs').write_text('sample')
        with mock.patch.object(D.shutil,'which',return_value='/usr/bin/node'),mock.patch.object(D.subprocess,'run',return_value=mock.Mock(returncode=1,stdout='')):
            report=D.run_test_scripts(self.root)
        self.assertEqual(next(x for x in report if x['check']=='test:test_blind.cjs')['status'],'FAIL')
    def test_report_json_has_no_paths(self):
        self.required();obj=D.audit(self.root)
        encoded=json.dumps(obj)
        self.assertEqual(obj['schema'],'signal-readiness-v32')
        self.assertNotIn(str(self.root),encoded)
    def test_all_reports_contain_known_status(self):
        for x in D.audit(self.root)['results']:
            self.assertIn(x['status'],('PASS','WARN','FAIL','SKIP'))
    def test_cli_json_stays_machine_readable(self):
        buf=io.StringIO()
        with redirect_stdout(buf):D.main(['--json'])
        self.assertEqual(json.loads(buf.getvalue())['version'],1)

if __name__=='__main__':unittest.main(verbosity=2)
