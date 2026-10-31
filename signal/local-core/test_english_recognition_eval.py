"""Synthetic-only tests for SIGNAL offline English speech recognition scoring."""
import json
import tempfile
from pathlib import Path
import unittest
from english_recognition_eval import (
    SCHEMA, edit_counts, evaluate, load_fixture, tokenize, main,
)


def sample(reference="SIGNAL check MTC", transcript="signal check mtc", **extras):
    return dict(reference=reference, transcript=transcript, **extras)


def fixture(samples=None, terms=None):
    return dict(schema=SCHEMA, samples=samples or [sample()], terms=terms or [])


class EnglishRecognitionTests(unittest.TestCase):
    def test_tokenization_case_and_punctuation(self):
        self.assertEqual(tokenize("SIGNAL, what's the MTC?"), ["signal", "what's", "the", "mtc"])

    def test_exact_case_ignored(self):
        r = evaluate(fixture())
        self.assertEqual(r["word_error_rate"], 0)
        self.assertEqual(r["sentence_accuracy"], 1)

    def test_substitution(self):
        r = evaluate(fixture([sample("check the box", "check the door")]))
        self.assertEqual((r["substitutions"], r["deletions"], r["insertions"]), (1, 0, 0))
        self.assertEqual(r["word_error_rate"], .3333)

    def test_deletion(self):
        self.assertEqual(edit_counts(["a", "b"], ["a"]), (0, 1, 0))

    def test_insertion(self):
        self.assertEqual(edit_counts(["a"], ["a", "b"]), (0, 0, 1))

    def test_empty_transcript_is_deletion(self):
        r = evaluate(fixture([sample("MTC ready", "")]))
        self.assertEqual(r["deletions"], 2)
        self.assertEqual(r["word_error_rate"], 1)

    def test_wer_may_exceed_one(self):
        r = evaluate(fixture([sample("ready", "ready extra words")]))
        self.assertEqual(r["word_error_rate"], 2)

    def test_terms_and_absent_term(self):
        r = evaluate(fixture([sample("VEIL MTC MTC", "veil mtc")],
                             ["VEIL", "MTC", "panic box"]))
        self.assertEqual([x["recall"] for x in r["technical_terms"]], [1, .5, None])

    def test_phrase_term(self):
        r = evaluate(fixture([sample("panic box ready", "panic box ready")], ["panic box"]))
        self.assertEqual(r["technical_terms"][0]["recall"], 1)

    def test_latency_median_and_p95(self):
        r = evaluate(fixture([sample("one", "one", latency_ms=50),
                              sample("two", "two", latency_ms=100),
                              sample("three", "three")]))
        self.assertEqual(r["latency_ms"]["median"], 75)
        self.assertEqual(r["latency_ms"]["p95_nearest_rank"], 100)
        self.assertEqual(r["latency_ms"]["samples"], 2)

    def test_boolean_latency_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(fixture([sample(latency_ms=True)]))

    def test_nan_latency_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(fixture([sample(latency_ms=float("nan"))]))

    def test_duplicate_terms_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(fixture(terms=["SIGNAL", "signal"]))

    def test_invalid_schema_and_unknown_fields(self):
        bad = fixture()
        bad["schema"] = "wrong"
        with self.assertRaises(ValueError):
            evaluate(bad)
        bad = fixture()
        bad["samples"][0]["device_id"] = "do-not-profile"
        with self.assertRaises(ValueError):
            evaluate(bad)

    def test_reference_must_have_words(self):
        with self.assertRaises(ValueError):
            evaluate(fixture([sample("!!!", "hello")]))

    def test_input_bounds(self):
        with self.assertRaises(ValueError):
            evaluate(fixture([sample("word " * 121, "word")]))
        with self.assertRaises(ValueError):
            evaluate(fixture([sample()] * 101))

    def test_no_transcript_echo(self):
        r = evaluate(fixture([sample("PRIVATE TEXT 123", "OTHER PRIVATE TEXT")]))
        output = json.dumps(r)
        self.assertNotIn("PRIVATE", output)
        self.assertNotIn("OTHER", output)

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fixture.json"
            path.write_text('{"schema":"a","schema":"b"}')
            with self.assertRaises(ValueError):
                load_fixture(path)

    def test_oversize_file_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "large.json"
            path.write_bytes(b" " * 65537)
            with self.assertRaises(ValueError):
                load_fixture(path)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "real.json"
            path.write_text("{}")
            link = Path(td) / "link.json"
            try:
                link.symlink_to(path)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(ValueError):
                load_fixture(link)

    def test_synthetic_fixture_end_to_end(self):
        path = Path(__file__).with_name("english_recognition_demo.json")
        r = evaluate(load_fixture(path))
        self.assertEqual(r["sample_count"], 4)
        self.assertGreater(r["word_error_rate"], 0)
        self.assertEqual(r["status"], "operator_supplied_transcripts_unverified")


if __name__ == "__main__":
    unittest.main()
