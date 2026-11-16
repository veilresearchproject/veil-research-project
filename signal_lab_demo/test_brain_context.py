"""Offline regression tests for the read-only synthetic context boundary."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from brain_context import build_brain_context, format_brain_context
from advanced_lab import execute


class BrainContextTests(unittest.TestCase):
    def test_valid_synthetic_bundle(self):
        with tempfile.TemporaryDirectory() as d:
            execute(d, operator_approved=True)
            result = build_brain_context(d)
            self.assertEqual(result["sample_count"], 60)
            self.assertFalse(result["physical_control_allowed"])
            self.assertIn("synthetic only", format_brain_context(d))
            self.assertNotIn("source_sha256", format_brain_context(d))

    def test_no_unapproved_generation(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(PermissionError):
                execute(d, operator_approved=False)

    def test_missing_bundle_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                build_brain_context(d)

    def test_tampered_bundle_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            execute(d, operator_approved=True)
            (Path(d) / "casebook.json").write_text('{"cases":[]}')
            with self.assertRaises(ValueError):
                build_brain_context(d)

    def test_verifier_failure_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("brain_context.verify_full_bundle", return_value=False):
                with self.assertRaises(ValueError):
                    build_brain_context(d)


if __name__ == "__main__":
    unittest.main()
