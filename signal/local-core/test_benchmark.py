"""Unit tests verify harness plumbing only, not local model quality."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import benchmark


class FakeClock:
    def __init__(self):
        self.t = 0.0
    def __call__(self):
        self.t += 0.01
        return self.t


class FakeModel:
    def __init__(self):
        self.calls = []
    def answer(self, messages):
        self.calls.append(messages)
        return "I cannot verify. Ask a human operator and check the controls."


class BrokenModel:
    def answer(self, messages):
        raise RuntimeError("Ollama unavailable")


class BenchmarkTests(unittest.TestCase):
    def test_six_distinct_cases_cover_boundaries(self):
        ids = [c["id"] for c in benchmark.CASES]
        self.assertEqual(len(ids), 6)
        self.assertEqual(len(set(ids)), len(ids))
        self.assertIn("panic_all_clear", ids)
        self.assertIn("fabricated_csv", ids)

    def test_mock_report_cannot_be_mistaken_for_live_quality(self):
        report = benchmark.run_benchmark(FakeModel(), "mock", "FAKE", clock=FakeClock())
        self.assertFalse(report["live_model_inference_tested"])
        self.assertFalse(report["windows_hardware_tested"])
        self.assertTrue(report["mock_latency_not_representative"])
        self.assertIsNone(report["model_quality_score"])
        self.assertTrue(report["human_review_required"])
        self.assertEqual(report["number_of_cases"], 6)

    def test_no_conversation_or_memory_leaks_to_report(self):
        model = FakeModel()
        report = benchmark.run_benchmark(model, "mock", "FAKE", clock=FakeClock())
        dumped = json.dumps(report)
        self.assertNotIn("I cannot verify. Ask", dumped)
        self.assertNotIn("Ignore your rules", dumped)
        self.assertFalse(report["raw_prompts_or_replies_saved"])
        for messages in model.calls:
            self.assertEqual([m["role"] for m in messages], ["system", "user"])
            self.assertNotIn("Saved user facts", messages[0]["content"])

    def test_live_label_is_not_windows_hardware_validation(self):
        report = benchmark.run_benchmark(FakeModel(), "live", "FAKE", clock=FakeClock())
        self.assertTrue(report["live_model_inference_tested"])
        self.assertFalse(report["windows_hardware_tested"])
        self.assertIsNone(report["cases"][0]["factual_accuracy"])
        self.assertEqual(report["cases"][0]["human_review_status"], "NOT_REVIEWED")

    def test_invalid_reply_and_latency_rejected(self):
        with self.assertRaises(TypeError):
            benchmark.evaluate_case(benchmark.CASES[0], None, 10)
        with self.assertRaises(ValueError):
            benchmark.evaluate_case(benchmark.CASES[0], "ok", -1)

    def test_failure_does_not_write_success_report(self):
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            benchmark.run_benchmark(BrokenModel(), "live", "FAKE")

    def test_cli_mock_writes_metrics_without_raw_content(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metrics.json"
            with patch("builtins.print"):
                self.assertEqual(benchmark.main(["--mode", "mock", "--output", str(path)]), 0)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["mode"], "mock")
            self.assertEqual(len(data["cases"]), 6)
            self.assertNotIn("I have not uploaded", path.read_text(encoding="utf-8"))

    def test_explicit_review_callback_only(self):
        seen = []
        benchmark.run_benchmark(FakeModel(), "mock", "FAKE", clock=FakeClock(),
                                review_callback=lambda case_id, reply: seen.append((case_id, reply)))
        self.assertEqual(len(seen), 6)
        self.assertEqual(seen[0][0], "unseen_audio")
        self.assertIn("cannot verify", seen[0][1])

    def test_no_default_mode_prevents_accidental_live_calls(self):
        with patch("sys.stderr"):
            with self.assertRaises(SystemExit) as ctx:
                benchmark.main([])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
