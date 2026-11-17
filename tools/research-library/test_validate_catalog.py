"""Regression tests for public catalog validation, using temporary fixtures."""
import json
from pathlib import Path
import tempfile
import unittest

from validate_catalog import validate_catalog


class CatalogTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.catalog = self.root / "cases.json"
        (self.root / "sample.pdf").write_bytes(b"%PDF-1.7\nFixture header")
        self.entry = {
            "id": "VEIL-IR-2026-001", "title": "Synthetic report", "summary": "Test fixture",
            "event_date": "2026-11-13", "publication_date": "2026-11-15",
            "status": "published", "classification": "Inconclusive", "report_url": "sample.pdf",
            "topics": ["temperature"], "review_version": "1",
        }

    def write_cases(self, *cases):
        self.catalog.write_text(json.dumps({
            "schema_version": "1.0", "last_updated": "2026-11-16", "cases": cases,
        }), encoding="utf-8")

    def test_empty_and_valid(self):
        self.write_cases()
        self.assertEqual(validate_catalog(self.catalog), 0)
        self.write_cases(self.entry)
        self.assertEqual(validate_catalog(self.catalog), 1)

    def test_invalid_entries(self):
        scenarios = [
            ({"status": "draft"}, "published status"),
            ({"private_contact": "synthetic"}, "unexpected fields"),
            ({"publication_date": "2026-02-30"}, "Invalid publication_date"),
            ({"publication_date": "2026-11-17"}, "out of order"),
            ({"report_url": "//example.test/x.pdf"}, "relative PDF"),
            ({"report_url": "../sample.pdf"}, "relative PDF"),
            ({"report_url": "missing.pdf"}, "must be a local file"),
            ({"topics": "temperature"}, "list of nonempty strings"),
        ]
        for changes, message in scenarios:
            with self.subTest(changes=changes):
                self.write_cases(self.entry | changes)
                with self.assertRaisesRegex(ValueError, message):
                    validate_catalog(self.catalog)

    def test_duplicate_ids_links_and_keys(self):
        self.write_cases(self.entry, self.entry)
        with self.assertRaisesRegex(ValueError, "duplicate case ID"):
            validate_catalog(self.catalog)
        self.write_cases(self.entry, self.entry | {"id": "VEIL-IR-2026-002"})
        with self.assertRaisesRegex(ValueError, "already belongs"):
            validate_catalog(self.catalog)
        self.catalog.write_text('{"cases": [], "cases": []}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            validate_catalog(self.catalog)

    def test_non_pdf_rejected(self):
        (self.root / "sample.pdf").write_bytes(b"html")
        self.write_cases(self.entry)
        with self.assertRaisesRegex(ValueError, "PDF header"):
            validate_catalog(self.catalog)


if __name__ == "__main__":
    unittest.main()
