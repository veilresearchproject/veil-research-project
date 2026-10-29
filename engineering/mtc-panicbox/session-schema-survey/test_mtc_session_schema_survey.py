import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from mtc_session_schema_survey import survey, main, MAX_EVENTS_FILE, MAX_SMALL_FILE


class SessionSchemaSurveyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / "session"
        self.folder.mkdir()
        self.write_defaults()

    def write_defaults(self):
        (self.folder / "session_result.json").write_text(json.dumps({"status": "success", "secret": "PRIVATE-DATA-MARKER"}))
        (self.folder / "session_metadata.json").write_text(json.dumps({"settings": {"recorder": "HyperX", "question": "SECRET-QUESTION"}}))
        (self.folder / "events.jsonl").write_text('\n'.join([json.dumps({"event": "playback", "question": "HIDDEN-QUESTION", "time": 1}), json.dumps({"event": "end", "time": 2})]) + '\n')

    def test_schema_profiles_only_keys_types(self):
        result = survey(self.folder)
        self.assertEqual(result["outcome"], "SCHEMA_PROFILED_ONLY")
        self.assertEqual(result["files"]["events.jsonl"]["valid_json_rows"], 2)
        self.assertEqual(result["files"]["events.jsonl"]["invalid_row_count"], 0)
        self.assertEqual(result["files"]["session_metadata.json"]["top_level_type"], "object")
        encoded = json.dumps(result)
        for forbidden in ("PRIVATE-DATA-MARKER", "SECRET-QUESTION", "HIDDEN-QUESTION", "HyperX", "success", "playback"):
            self.assertNotIn(json.dumps(forbidden), encoded)
        self.assertIn('settings', encoded)

    def test_result_json_missing(self):
        (self.folder / "session_result.json").unlink()
        result = survey(self.folder)
        self.assertEqual(result["outcome"], "HOLD")
        self.assertTrue(any("missing" in s for s in result["errors"]))

    def test_broken_metadata_json(self):
        (self.folder / "session_metadata.json").write_text('{ "bad" :')
        result = survey(self.folder)
        self.assertEqual(result["outcome"], "HOLD")

    def test_invalid_jsonl_line_without_content_leak(self):
        (self.folder / "events.jsonl").write_text('{"event":"yes"}\n{PRIVATESECRET\n')
        result = survey(self.folder)
        self.assertEqual(result["files"]["events.jsonl"]["invalid_row_count"], 1)
        self.assertNotIn('PRIVATESECRET', json.dumps(result))

    def test_blank_lines_warning(self):
        (self.folder / "events.jsonl").write_text('\n{"kind": 1}\n\n')
        r = survey(self.folder)
        self.assertEqual(r["outcome"], "SCHEMA_PROFILED_ONLY")
        self.assertEqual(r["files"]["events.jsonl"]["blank_lines"], 2)

    def test_events_single_line_without_final_newline(self):
        (self.folder / "events.jsonl").write_text('{"foo":true}')
        self.assertEqual(survey(self.folder)["files"]["events.jsonl"]["total_lines"], 1)

    def test_event_non_objects_warn(self):
        (self.folder / "events.jsonl").write_text('[]\n5\n"hello"\n')
        r = survey(self.folder)
        self.assertEqual(r["files"]["events.jsonl"]["non_object_rows"], 3)
        self.assertEqual(r["outcome"], "SCHEMA_PROFILED_ONLY")

    def test_invalid_encoding(self):
        (self.folder / "session_result.json").write_bytes(b'\xff')
        self.assertEqual(survey(self.folder)["outcome"], "HOLD")

    def test_bom_utf8(self):
        (self.folder / "session_result.json").write_bytes(b'\xef\xbb\xbf{"ok":true}')
        self.assertEqual(survey(self.folder)["outcome"], "SCHEMA_PROFILED_ONLY")

    def test_large_metadata_rejected(self):
        with (self.folder / "session_result.json").open('wb') as f:
            f.write(b' ' * (MAX_SMALL_FILE + 1))
        self.assertEqual(survey(self.folder)["outcome"], "HOLD")

    def test_large_events_rejected(self):
        with (self.folder / "events.jsonl").open('wb') as f:
            f.truncate(MAX_EVENTS_FILE + 1)
        self.assertEqual(survey(self.folder)["outcome"], "HOLD")

    def test_large_line_rejected(self):
        (self.folder / "events.jsonl").write_text('{"x":"' + 'A' * (256*1024) + '"}\n')
        r = survey(self.folder)
        self.assertEqual(r["outcome"], "HOLD")
        self.assertEqual(r["files"]["events.jsonl"]["invalid_row_count"], 1)

    def test_symlink_file_rejected(self):
        external = Path(self.temp.name) / "external.json"
        external.write_text('{"private":"outside"}')
        (self.folder / "session_result.json").unlink()
        try:
            (self.folder / "session_result.json").symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unsupported')
        self.assertEqual(survey(self.folder)["outcome"], "HOLD")

    def test_symlink_root_rejected(self):
        link = Path(self.temp.name) / "link"
        try:
            link.symlink_to(self.folder, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unsupported')
        with self.assertRaises(ValueError):
            survey(link)

    def test_no_files_changed(self):
        before = {f.name: f.read_bytes() for f in self.folder.iterdir()}
        survey(self.folder)
        after = {f.name: f.read_bytes() for f in self.folder.iterdir()}
        self.assertEqual(before, after)

    def test_key_path_escaped(self):
        (self.folder / "session_result.json").write_text(json.dumps({'a.b[0]': 1}))
        s = json.dumps(survey(self.folder))
        self.assertIn('a.b[0]', s)
        self.assertNotIn('"a.b[0]": 1', s)

    def test_array_shapes(self):
        (self.folder / "session_metadata.json").write_text(json.dumps({'items': [{'x':1},{'x':'two'}]}))
        p = survey(self.folder)["files"]["session_metadata.json"]["paths"]
        self.assertTrue(any('items' in x['path'] and '[]' in x['path'] for x in p))

    def test_boolean_distinct_number(self):
        (self.folder / "events.jsonl").write_text('{"v":true}\n{"v":3}\n')
        p = survey(self.folder)["files"]["events.jsonl"]["paths"]
        v = next(x for x in p if x['path'] == '$["v"]')
        self.assertEqual(v['types'], {'boolean': 1, 'number': 1})

    def test_cli_exit_success_without_local_writes(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            code=main([str(self.folder)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["outcome"], "SCHEMA_PROFILED_ONLY")

    def test_cli_exit_missing(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            code=main([str(self.folder / 'nope')])
        self.assertEqual(code, 2)
        self.assertIn('HOLD', out.getvalue())


if __name__ == '__main__':
    unittest.main()
