"""End-to-end offline pilot regression tests using generated evidence."""
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("pilot.py").resolve()
CSV = ("timestamp,sensor_id,temperature_c\r\n"
       "2026-11-16T09:00:00-05:00,bench-a,20.0\r\n"
       "\r\n"
       "2026-11-16T09:01:00-05:00,bench-a,22.0\r\n"
       "2026-11-16T09:04:00-05:00,bench-a,22.1\r\n")


class PilotTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.store = self.root / "private"
        self.source = self.root / "controlled.csv"
        self.source.write_bytes(CSV.encode())

    def run_pilot(self, *args, actor="operator", expected=None, raw=False):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--store", str(self.store), "--actor", actor, *map(str, args)],
            capture_output=True, encoding="utf-8", check=False,
        )
        if expected:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected, result.stderr)
            return
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout if raw else json.loads(result.stdout)

    def new_case(self):
        return self.run_pilot(
            "open-case", "--question", "What did the controlled bench test record?",
            "--expires", (date.today() + timedelta(days=7)).isoformat(),
            "--consent-reference", "synthetic-test-fixture", "--confirm-authority-and-private-review",
        )["case_id"]

    def intake(self, case_id, *extra, source=None, expected=None, captured="2026-11-16T09:00:00-05:00"):
        return self.run_pilot(
            "intake", case_id, source or self.source, "--device", "synthetic bench",
            "--captured", captured, "--clock-context", "Simulated clock; no independent reference",
            "--context", "Programmed 2°C step; one intentionally omitted cadence interval",
            *extra, expected=expected,
        )

    def review(self, case_id, *extra, actor="human-reviewer", expected=None):
        return self.run_pilot(
            "review", case_id, "--finding", "Explained",
            "--rationale", "Fixture contains a programmed change. <script>literal text</script>",
            "--tests", "Compared raw rows with programmed temperatures and timestamps.",
            "--limitations", "Synthetic data with no physical sensor or calibration.",
            "--reconsider-if", "A mismatch between stored rows and fixture construction.",
            *extra, actor=actor, expected=expected,
        )

    def test_end_to_end_review_and_correction(self):
        case_id = self.new_case()
        source = self.intake(case_id, "--expected-sha256", hashlib.sha256(self.source.read_bytes()).hexdigest())
        evidence = source["evidence_id"]
        self.assertEqual(source["sha256"], self.run_pilot(
            "verify", case_id, evidence, "--compare", self.source
        )["sha256"])
        audit = self.run_pilot("analyze", case_id, evidence, "--interval", 60, "--threshold", 1.5)
        self.assertEqual(audit["source_sha256"], source["sha256"])
        self.assertEqual(audit["source"]["captured_utc"], "2026-11-16T14:00:00+00:00")
        self.assertEqual(audit["status"], "provisional")
        self.assertTrue(audit["source"]["submitter_checksum_matched"])
        self.assertRegex(audit["engine_sha256"], "^[a-f0-9]{64}$")
        self.assertEqual([(flag["type"], flag["line"], flag["timestamp"], flag["sensor"])
                          for flag in audit["measurements"]["events"]], [
            ("TEMPERATURE_STEP", 4, "2026-11-16T09:01:00-05:00", "bench-a"),
            ("CADENCE_GAP", 5, "2026-11-16T09:04:00-05:00", "bench-a"),
        ])
        self.review(case_id, actor="OPERATOR", expected="separate human reviewer")
        self.assertEqual(self.review(case_id)["report_version"], 1)
        self.review(case_id, expected="correction reason")
        self.assertEqual(self.review(case_id, "--correction", "Clarified fixture construction.")["report_version"], 2)
        first = self.run_pilot("report", case_id, 1)
        second = self.run_pilot("report", case_id, 2)
        self.assertEqual(first["finding"], "Explained")
        self.assertEqual(first["visibility"], "private")
        self.assertEqual(first["signal_analysis"], [audit])
        self.assertEqual(second["supersedes"], 1)
        self.assertIsNone(first["correction"])
        self.assertEqual(second["correction"], "Clarified fixture construction.")
        printable = self.run_pilot("report", case_id, 2, "--format", "html", raw=True)
        self.assertNotIn("<script>", printable)
        self.assertIn("&lt;script&gt;literal text&lt;/script&gt;", printable)
        self.assertIn("Provisional SIGNAL analysis", printable)
        actions = [row["action"] for row in self.run_pilot("status", case_id)["custody"]]
        self.assertEqual(actions[:4], ["case_opened", "original_received", "review_copy_verified", "signal_audit_completed"])
        with sqlite3.connect(self.store / "pilot.sqlite3") as db:
            self.assertEqual(db.execute("SELECT contents FROM evidence WHERE id = ?", (evidence,)).fetchone()[0],
                             self.source.read_bytes())
        restored = self.root / "restored"
        restored.mkdir(mode=0o700)
        shutil.copy2(self.store / "pilot.sqlite3", restored / "pilot.sqlite3")
        self.store = restored
        self.assertTrue(self.run_pilot("verify", case_id, evidence)["verified"])
        self.assertEqual(self.run_pilot("report", case_id, 2), second)

    def test_invalid_duplicate_copy_and_checksum(self):
        case_id = self.new_case()
        self.intake(case_id, captured="2026-11-16T09:00:00", expected="capture time with an offset")
        wrong = self.root / "wrong.png"
        wrong.write_bytes(b"other format")
        self.intake(case_id, source=wrong, expected="File header")
        huge = self.root / "oversize.csv"
        huge.write_bytes(b"x" * 1_000_001)
        self.intake(case_id, source=huge, expected="1–1000000 bytes")
        self.intake(case_id, "--expected-sha256", "0" * 64, expected="submitter's expected SHA-256")
        evidence = self.intake(case_id)["evidence_id"]
        self.intake(case_id, expected="already registered")
        different = self.root / "copy.csv"
        different.write_text(CSV + "extra row", encoding="utf-8")
        self.run_pilot("verify", case_id, evidence, "--compare", different, expected="does not match")
        other_case = self.new_case()
        self.run_pilot("verify", other_case, evidence, expected="Unknown evidence")
        with sqlite3.connect(self.store / "pilot.sqlite3") as db:
            db.execute("UPDATE evidence SET contents = ? WHERE id = ?", (b"changed", evidence))
        self.run_pilot("verify", case_id, evidence, expected="checksum mismatch")
        self.run_pilot("analyze", case_id, evidence, "--interval", 60, "--threshold", 1.5,
                       expected="checksum mismatch")
        self.review(case_id, expected="matching checksums")

    def test_expiry_and_withdrawal(self):
        case_id = self.new_case()
        evidence = self.intake(case_id)["evidence_id"]
        self.review(case_id)
        with sqlite3.connect(self.store / "pilot.sqlite3") as db:
            db.execute("UPDATE cases SET expires = '2000-01-01' WHERE id = ?", (case_id,))
        self.run_pilot("report", case_id, 1, expected="Retention expired")
        self.run_pilot("verify", case_id, evidence, expected="Retention expired")
        self.assertEqual(self.run_pilot("purge-expired", "--confirm")["expired_cases_removed_from_active_store"], 1)
        self.run_pilot("status", case_id, expected="Unknown case")
        with sqlite3.connect(self.store / "pilot.sqlite3") as db:
            for table in ("cases", "evidence", "analyses", "reports", "custody"):
                self.assertEqual(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)
        second = self.new_case()
        self.assertNotEqual(second, case_id)
        self.run_pilot("withdraw", second, expected="--confirm")
        self.assertTrue(self.run_pilot("withdraw", second, "--confirm")["removed_from_active_store"])

    @unittest.skipUnless(os.name == "posix", "POSIX permission test")
    def test_rejects_shared_store(self):
        self.store.mkdir(mode=0o755)
        self.store.chmod(0o755)
        self.run_pilot("status", "example", expected="mode 0700")

    def test_rejects_repository_storage(self):
        self.store = SCRIPT.parents[2] / "private"
        self.run_pilot("status", "example", expected="outside the repository")


if __name__ == "__main__":
    unittest.main()
