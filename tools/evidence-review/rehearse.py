"""Run a synthetic VEIL review on a desktop and optionally save its printable report."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from pilot import private_directory

PILOT = Path(__file__).with_name("pilot.py")
CSV = (b"timestamp,sensor_id,temperature_c\r\n"
       b"2026-11-16T08:00:00Z,synthetic-bench,21.0\r\n"
       b"2026-11-16T08:01:00Z,synthetic-bench,23.0\r\n")
PASSPHRASE = "pass:synthetic-fixture-only"


def run(*command):
    result = subprocess.run([str(part) for part in command], capture_output=True, timeout=45, check=False)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip() or "A rehearsal command failed.")
    return result.stdout


def make_certificate(directory):
    run("openssl", "req", "-x509", "-newkey", "rsa:3072", "-days", "1", "-subj",
        "/CN=VEIL Synthetic Rehearsal", "-keyout", directory / "private.key",
        "-out", directory / "public.pem", "-passout", PASSPHRASE)


def transfer(source, destination, recipient, packet):
    run("openssl", "cms", "-encrypt", "-binary", "-aes-256-gcm", "-in", source,
        "-outform", "DER", "-out", packet, recipient / "public.pem")
    run("openssl", "cms", "-decrypt", "-binary", "-inform", "DER", "-in", packet,
        "-recip", recipient / "public.pem", "-inkey", recipient / "private.key",
        "-passin", PASSPHRASE, "-out", destination)


def rehearsal(root):
    store = root / "store"

    def pilot(actor, *args, raw=False, location=store):
        result = run(sys.executable, "-B", PILOT, "--store", location, "--actor", actor, *args)
        return result if raw else json.loads(result)

    pilot("operator", "preflight")
    submitter = root / "submitter"
    reviewer = root / "reviewer"
    for directory in (submitter, reviewer):
        directory.mkdir(mode=0o700)
        make_certificate(directory)

    original = submitter / "original.csv"
    received = reviewer / "original.csv"
    original.write_bytes(CSV)
    transfer(original, received, reviewer, root / "incoming.cms")
    original_sha = hashlib.sha256(CSV).hexdigest()
    expires = (datetime.now(timezone.utc).date() + timedelta(days=7)).isoformat()
    case_id = pilot(
        "operator", "open-case", "--question", "Synthetic rehearsal: did the fixture contain a programmed step?",
        "--expires", expires, "--consent-reference", "synthetic-fixture-only",
        "--confirm-authority-and-private-review",
    )["case_id"]
    evidence = pilot(
        "operator", "intake", case_id, received, "--expected-sha256", original_sha,
        "--device", "Synthetic temperature bench", "--captured", "unknown",
        "--clock-context", "Programmed UTC timestamps", "--context", "Programmed 2 C change",
    )["evidence_id"]
    pilot("reviewer", "verify", case_id, evidence, "--compare", received)
    audit = pilot("operator", "analyze", case_id, evidence, "--interval", 60, "--threshold", 1.5)
    flags = [(flag["type"], flag["line"]) for flag in audit["measurements"]["events"]]
    if flags != [("TEMPERATURE_STEP", 3)] or audit["source_sha256"] != original_sha:
        raise ValueError("SIGNAL source trace did not match the synthetic case.")
    version = pilot(
        "reviewer", "review", case_id, "--finding", "Explained",
        "--rationale", "The synthetic fixture contains a programmed temperature step.",
        "--tests", "Compared retained original rows with the programmed step and SIGNAL audit.",
        "--limitations", "Synthetic readings only. No physical sensor or witness evidence.",
        "--reconsider-if", "A difference between the stored original and the programmed readings.",
    )["report_version"]
    report = pilot("operator", "report", case_id, version, "--format", "html", raw=True)
    exported = reviewer / "report.html"
    exported.write_bytes(report)
    expected = pilot("operator", "check-delivery", case_id, version)["html_sha256"]
    returned = submitter / "report.html"
    transfer(exported, returned, submitter, root / "outgoing.cms")
    actual = hashlib.sha256(returned.read_bytes()).hexdigest()
    if actual != expected or returned.read_bytes() != report:
        raise ValueError("Delivered synthetic report differs from the reviewed report.")
    receipt = pilot("operator", "record-delivery", case_id, version, "--report-sha256", actual,
                    "--recipient-reference", "synthetic-recipient",
                    "--delivery-reference", "synthetic-transfer", "--confirm-private-delivery")
    if receipt["html_sha256"] != actual:
        raise ValueError("Delivery receipt did not match the returned report.")
    backup = root / "restored"
    backup.mkdir(mode=0o700)
    shutil.copy2(store / "pilot.sqlite3", backup / "pilot.sqlite3")
    if not pilot("reviewer", "verify", case_id, evidence, location=backup)["verified"]:
        raise ValueError("Restored synthetic evidence did not verify.")
    if pilot("reviewer", "report", case_id, version, "--format", "html", raw=True, location=backup) != report:
        raise ValueError("Restored synthetic report differs from the reviewed report.")
    return report


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--workspace", type=Path, required=True, help="Dedicated local folder outside the repository")
    cli.add_argument("--keep-report", action="store_true", help="Keep only the synthetic HTML report")
    args = cli.parse_args()
    try:
        root = private_directory(args.workspace)
        with tempfile.TemporaryDirectory(prefix="veil-rehearsal-", dir=root) as temp:
            report = rehearsal(Path(temp))
        print("PASS: preflight, encrypted intake, SIGNAL trace, human review, encrypted return, receipt and restoration.")
        if args.keep_report:
            with tempfile.NamedTemporaryFile(
                prefix="VEIL_Synthetic_Rehearsal_", suffix=".html", dir=root, delete=False
            ) as stream:
                stream.write(report)
                target = stream.name
            print(f"Synthetic report: {target}")
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        cli.exit(1, f"Rehearsal: {exc}\n")


if __name__ == "__main__":
    main()
