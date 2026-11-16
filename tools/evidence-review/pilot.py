"""Offline, single-operator evidence review pilot. Python 3.10+."""
import argparse
from contextlib import closing, contextmanager
from datetime import date, datetime, timezone
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
AUDIT = REPO / "signal/csv-audit-core.js"
MAX_BYTES = 16 * 1024 * 1024
MAX_CSV = 1_000_000
CAPTURE_TIME = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)"
)
FINDINGS = ("Explained", "Probable explanation", "Inconclusive",
            "Unexplained after investigation")
EFFORT_STAGES = ("intake", "technical-examination", "independent-review", "correction", "delivery")
MEDIA = {
    ".jpg": (0, b"\xff\xd8\xff"), ".jpeg": (0, b"\xff\xd8\xff"),
    ".png": (0, b"\x89PNG\r\n\x1a\n"), ".wav": (8, b"WAVE"),
    ".mp4": (4, b"ftyp"), ".mov": (4, b"ftyp"),
}
SCHEMA = """
CREATE TABLE IF NOT EXISTS counters (year INTEGER PRIMARY KEY, number INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY, created TEXT NOT NULL, expires TEXT NOT NULL, details TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    sha256 TEXT NOT NULL, contents BLOB NOT NULL, details TEXT NOT NULL,
    UNIQUE (case_id, sha256)
);
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    packet TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reports (
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    version INTEGER NOT NULL, packet TEXT NOT NULL, PRIMARY KEY (case_id, version)
);
CREATE TABLE IF NOT EXISTS effort (
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    entry TEXT NOT NULL, stage TEXT NOT NULL, minutes INTEGER NOT NULL,
    PRIMARY KEY (case_id, entry)
);
CREATE TABLE IF NOT EXISTS custody (
    id INTEGER PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    utc TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL, reference TEXT NOT NULL
);
"""
AUDIT_RUNNER = """
require(process.argv[1]);
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
    try {
        const result = globalThis.SIGNALCsvAudit.analyze(input, {
            intervalSec: Number(process.argv[2]), thresholdC: Number(process.argv[3])
        });
        process.stdout.write(JSON.stringify(result));
    } catch {
        process.exitCode = 1;
    }
});
"""


def now():
    return datetime.now(timezone.utc).isoformat()


def clean(text, limit):
    if not 0 < len(text.strip()) <= limit or not text.isprintable():
        raise ValueError(f"Use printable text, 1–{limit} characters.")
    return text.strip()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_text(data):
    return json.dumps(data, ensure_ascii=True, allow_nan=False)


def private_directory(path):
    root = path.resolve()
    if root.is_relative_to(REPO) or REPO.is_relative_to(root):
        raise ValueError("Choose a dedicated evidence directory outside the repository.")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "posix":
        info = root.stat()
        if info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("The evidence directory must be owned by you and have mode 0700.")
    return root


@contextmanager
def open_store(path):
    database = private_directory(path) / "pilot.sqlite3"
    if database.is_symlink():
        raise ValueError("The evidence database must be a regular local file.")
    fd = os.open(database, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("The evidence database must be a regular, unlinked local file.")
        if os.name == "posix" and (info.st_uid != os.getuid() or info.st_mode & 0o077):
            raise ValueError("The evidence database must be owned by you and have mode 0600.")
    finally:
        os.close(fd)
    with closing(sqlite3.connect(database)) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("PRAGMA secure_delete = ON")
        db.executescript(SCHEMA)
        yield db


@contextmanager
def write(db):
    with db:
        db.execute("BEGIN IMMEDIATE")
        yield


def case(db, case_id, *, include_expired=False):
    record = db.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    if record is None:
        raise ValueError("Unknown case.")
    if not include_expired and record["expires"] <= now()[:10]:
        raise ValueError("Retention expired. Use purge-expired.")
    return record


def log(db, args, action, reference):
    db.execute("INSERT INTO custody (case_id, utc, actor, action, reference) VALUES (?, ?, ?, ?, ?)",
               (args.case, now(), args.actor, action, reference))


def open_case(db, args):
    stamp = now()
    expires = date.fromisoformat(args.expires).isoformat()
    if expires <= stamp[:10]:
        raise ValueError("Use a future UTC retention date.")
    details = {
        "review_question": clean(args.question, 800),
        "consent_reference": clean(args.consent_reference, 120),
        "intake_operator": args.actor,
        "authority_to_submit_confirmed": True,
        "private_review_consent_confirmed": True,
        "publication_permission": False,
        "training_permission": False,
        "service": "no-fee-pilot",
    }
    year = int(stamp[:4])
    db.execute("INSERT OR IGNORE INTO counters VALUES (?, 0)", (year,))
    number = db.execute("SELECT number FROM counters WHERE year = ?", (year,)).fetchone()[0] + 1
    if number > 999:
        raise ValueError("Annual case number limit reached.")
    db.execute("UPDATE counters SET number = ? WHERE year = ?", (number, year))
    args.case = f"VEIL-IR-{year}-{number:03}"
    db.execute("INSERT INTO cases VALUES (?, ?, ?, ?)", (args.case, stamp, expires, json_text(details)))
    log(db, args, "case_opened", args.case)
    return {"case_id": args.case, "expires_utc": expires, "service": details["service"]}


def read_source(path):
    ext = path.suffix.lower()
    if ext != ".csv" and ext not in MEDIA:
        raise ValueError("Supported types are CSV, JPEG, PNG, WAV, MP4 and MOV.")
    if path.is_symlink() or not path.is_file():
        raise ValueError("Select a regular source file.")
    limit = MAX_CSV if ext == ".csv" else MAX_BYTES
    with path.open("rb") as source:
        data = source.read(limit + 1)
    if not data or len(data) > limit:
        raise ValueError(f"Original must contain 1–{limit} bytes.")
    if ext == ".csv":
        decoded = data.decode("utf-8-sig")
        if any(ord(char) < 32 and char not in "\t\r\n" for char in decoded):
            raise ValueError("CSV must be UTF-8 text.")
    else:
        offset, marker = MEDIA[ext]
        if not data[offset:].startswith(marker) or (ext == ".wav" and not data.startswith(b"RIFF")):
            raise ValueError("File header does not match the selected type.")
    return ext, data


def intake(db, args):
    case(db, args.case)
    extension, data = read_source(args.file)
    captured = args.captured
    captured_utc = None
    if captured != "unknown":
        if not CAPTURE_TIME.fullmatch(captured):
            raise ValueError("Specify capture time with an offset or use 'unknown'.")
        parsed = datetime.fromisoformat(captured.replace("Z", "+00:00"))
        captured_utc = parsed.astimezone(timezone.utc).isoformat()
    sha = digest(data)
    if args.expected_sha256 is not None and args.expected_sha256.lower() != sha:
        raise ValueError("Received bytes do not match the submitter's expected SHA-256.")
    if db.execute("SELECT id FROM evidence WHERE case_id = ? AND sha256 = ?",
                  (args.case, sha)).fetchone():
        raise ValueError("These source bytes are already registered in this case.")
    count = db.execute("SELECT COUNT(*) FROM evidence WHERE case_id = ?", (args.case,)).fetchone()[0]
    if count >= 10:
        raise ValueError("Pilot limit is 10 originals per case.")
    evidence_id = f"{args.case}-EV-{count + 1:03}"
    details = {
        "original_name": clean(args.file.name, 180), "extension": extension,
        "bytes": len(data), "device": clean(args.device, 120), "captured_as_reported": captured,
        "captured_utc": captured_utc, "clock_context": clean(args.clock_context, 160),
        "acquisition_context": clean(args.context, 500),
        "submitter_checksum_matched": args.expected_sha256 is not None,
    }
    db.execute("INSERT INTO evidence VALUES (?, ?, ?, ?, ?)",
               (evidence_id, args.case, sha, data, json_text(details)))
    log(db, args, "original_received", evidence_id)
    return {"evidence_id": evidence_id, "sha256": sha, "bytes": len(data)}


def checked_evidence(db, args):
    case(db, args.case)
    record = db.execute("SELECT * FROM evidence WHERE case_id = ? AND id = ?",
                        (args.case, args.evidence)).fetchone()
    if record is None:
        raise ValueError("Unknown evidence in this case.")
    if digest(record["contents"]) != record["sha256"]:
        raise ValueError("Original checksum mismatch. Stop review and inspect the retained source.")
    return record


def verify(db, args):
    record = checked_evidence(db, args)
    if args.compare is not None:
        _, copy = read_source(args.compare)
        if digest(copy) != record["sha256"]:
            raise ValueError("Review copy does not match the stored original.")
    log(db, args, "review_copy_verified" if args.compare else "checksum_verified", args.evidence)
    return {"evidence_id": args.evidence, "sha256": record["sha256"], "verified": True}


def run_signal_audit(contents, interval, threshold):
    result = subprocess.run(
        ["node", "-e", AUDIT_RUNNER, str(AUDIT), str(interval), str(threshold)],
        input=contents, capture_output=True, timeout=15, check=False,
        env={key: os.environ[key] for key in ("PATH", "SystemRoot") if key in os.environ},
    )
    if result.returncode:
        raise ValueError("SIGNAL CSV audit failed. Check CSV format and audit parameters.")
    return json.loads(result.stdout)


def analyze(db, args):
    record = checked_evidence(db, args)
    source = json.loads(record["details"])
    if source["extension"] != ".csv":
        raise ValueError("SIGNAL analysis in this pilot supports temperature CSV only.")
    code_hash = digest(AUDIT.read_bytes())
    measurements = run_signal_audit(record["contents"], args.interval, args.threshold)
    packet = {
        "status": "provisional", "method": "deterministic CSV audit", "engine": "SIGNAL CSV Audit Bench",
        "engine_sha256": code_hash, "created_utc": now(),
        "case_id": args.case, "evidence_id": args.evidence, "source_sha256": record["sha256"],
        "source": source, "measurements": measurements,
        "uncertainty": "Threshold and cadence flags require human interpretation. Source clock, "
                       "calibration, and cause require independent verification.",
    }
    cursor = db.execute("INSERT INTO analyses (case_id, packet) VALUES (?, ?)",
                        (args.case, json_text(packet)))
    log(db, args, "signal_audit_completed", str(cursor.lastrowid))
    return {"analysis_id": cursor.lastrowid, **packet}


def review(db, args):
    record = case(db, args.case)
    details = json.loads(record["details"])
    if args.actor.casefold() == details["intake_operator"].casefold():
        raise ValueError("The pilot requires a separate human reviewer.")
    evidence = db.execute("SELECT id, sha256, details FROM evidence WHERE case_id = ? ORDER BY id",
                          (args.case,)).fetchall()
    if not evidence:
        raise ValueError("Review requires at least one original.")
    for row in evidence:
        contents = db.execute("SELECT contents FROM evidence WHERE id = ?", (row["id"],)).fetchone()[0]
        if digest(contents) != row["sha256"]:
            raise ValueError("Review requires originals with matching checksums.")
    analysis = db.execute("SELECT id, packet FROM analyses WHERE case_id = ? ORDER BY id",
                          (args.case,)).fetchall()
    version = db.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM reports WHERE case_id = ?",
                         (args.case,)).fetchone()[0]
    if version > 1 and not args.correction:
        raise ValueError("Record a correction reason before issuing another version.")
    packet = {
        "schema_version": 1, "case_id": args.case, "report_version": version,
        "supersedes": version - 1 if version > 1 else None,
        "visibility": "private", "service": "no-fee-pilot", "reviewer": args.actor,
        "reviewed_utc": now(), "review_question": details["review_question"],
        "finding": args.finding, "rationale": clean(args.rationale, 2400),
        "hypotheses_and_tests": clean(args.tests, 2400), "limitations": clean(args.limitations, 1600),
        "could_change_finding": clean(args.reconsider_if, 1200),
        "correction": clean(args.correction, 500) if args.correction else None,
        "evidence": [{"id": row["id"], "sha256": row["sha256"], **json.loads(row["details"])}
                     for row in evidence],
        "signal_analysis": [{"analysis_id": row["id"], **json.loads(row["packet"])} for row in analysis],
    }
    log(db, args, "human_review_recorded", str(version))
    packet["custody_through_review"] = status(db, args)["custody"]
    db.execute("INSERT INTO reports VALUES (?, ?, ?)", (args.case, version, json_text(packet)))
    return {"case_id": args.case, "report_version": version, "visibility": "private"}


def report_packet(db, args):
    case(db, args.case)
    row = db.execute("SELECT packet FROM reports WHERE case_id = ? AND version = ?",
                     (args.case, args.version)).fetchone()
    if row is None:
        raise ValueError("Unknown report version.")
    return json.loads(row["packet"])


def report(db, args):
    packet = report_packet(db, args)
    log(db, args, "private_report_read", str(args.version))
    return packet


def printable_report(packet):
    def section(heading, content):
        return f"<section><h2>{heading}</h2><p>{escape(content)}</p></section>"

    def appendix(heading, content):
        data = json.dumps(content, indent=2, ensure_ascii=True)
        return f"<section><h2>{heading}</h2><pre>{escape(data)}</pre></section>"

    heading = escape(f'{packet["case_id"]} · Version {packet["report_version"]}')
    sections = [
        section("Review question", packet["review_question"]),
        section("Finding", packet["finding"]),
        section("Human rationale", packet["rationale"]),
        section("Competing explanations and tests", packet["hypotheses_and_tests"]),
        section("Limitations", packet["limitations"]),
        section("What could change the finding", packet["could_change_finding"]),
        section("Revision history", packet["correction"] or "Initial issue."),
        appendix("Evidence inventory", packet["evidence"]),
        appendix("Provisional SIGNAL analysis", packet["signal_analysis"]),
        appendix("Recorded custody events", packet["custody_through_review"]),
    ]
    reviewer = escape(packet["reviewer"])
    reviewed = escape(packet["reviewed_utc"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>{heading}</title><style>
body {{ max-width: 54rem; margin: 2rem auto; padding: 0 1rem; font: 16px/1.5 system-ui, sans-serif; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; font-size: 0.8em; }}
h2 {{ break-after: avoid; }}
</style></head><body><header><p>VEIL Research Project · Private · No-fee pilot</p>
<h1>{heading}</h1><p>Human reviewer {reviewer} · {reviewed}</p></header>
<main>{"".join(sections)}</main></body></html>"""


def delivery_digest(db, args):
    packet = report_packet(db, args)
    latest = db.execute("SELECT MAX(version) FROM reports WHERE case_id = ?", (args.case,)).fetchone()[0]
    if args.version != latest:
        raise ValueError("Use the latest reviewed report for delivery.")
    evidence = db.execute("SELECT id, sha256 FROM evidence WHERE case_id = ? ORDER BY id",
                          (args.case,)).fetchall()
    reviewed = [(item["id"], item["sha256"]) for item in packet["evidence"]]
    if [tuple(row) for row in evidence] != reviewed:
        raise ValueError("Evidence has changed since review. Issue a new reviewed version.")
    analysis = db.execute("SELECT id FROM analyses WHERE case_id = ? ORDER BY id", (args.case,))
    if [row["id"] for row in analysis] != [item["analysis_id"] for item in packet["signal_analysis"]]:
        raise ValueError("Analysis has changed since review. Issue a new reviewed version.")
    for evidence_id, sha in reviewed:
        contents = db.execute("SELECT contents FROM evidence WHERE id = ?", (evidence_id,)).fetchone()[0]
        if digest(contents) != sha:
            raise ValueError("Original checksum mismatch. Stop delivery and inspect the retained source.")
    return digest(printable_report(packet).encode("utf-8"))


def check_delivery(db, args):
    return {"case_id": args.case, "report_version": args.version, "html_sha256": delivery_digest(db, args)}


def record_delivery(db, args):
    expected = delivery_digest(db, args)
    if args.report_sha256.lower() != expected:
        raise ValueError("Delivered HTML checksum does not match the reviewed version.")
    receipt = {
        "report_version": args.version,
        "html_sha256": expected,
        "recipient_reference": clean(args.recipient_reference, 120),
        "delivery_reference": clean(args.delivery_reference, 120),
    }
    reference = json_text(receipt)
    exists = db.execute(
        "SELECT 1 FROM custody WHERE case_id = ? AND action = ? AND reference = ?",
        (args.case, "private_delivery_recorded", reference),
    ).fetchone()
    if not exists:
        log(db, args, "private_delivery_recorded", reference)
    return {"case_id": args.case, **receipt, "already_recorded": exists is not None}


def preflight(path):
    root = private_directory(path)
    openssl = subprocess.run(["openssl", "version"], capture_output=True, text=True, timeout=10, check=True)
    if not openssl.stdout.startswith("OpenSSL 3."):
        raise ValueError("The documented encrypted handoff uses OpenSSL 3.")
    synthetic = (b"timestamp,temperature_c\n"
                 b"2026-11-16T08:00:00Z,21.0\n2026-11-16T08:01:00Z,23.0\n")
    with tempfile.TemporaryDirectory(prefix="preflight-", dir=root) as temp:
        with open_store(Path(temp)) as db, write(db):
            db.execute("INSERT INTO counters VALUES (?, ?)", (2026, 1))
        with open_store(Path(temp)) as db:
            if db.execute("PRAGMA quick_check").fetchone()[0] != "ok" or db.execute(
                    "SELECT number FROM counters WHERE year = ?", (2026,)).fetchone()[0] != 1:
                raise ValueError("Temporary evidence database failed the write/read check.")
        if run_signal_audit(synthetic, 60, 1.5)["steps"] != 1:
            raise ValueError("SIGNAL did not detect the synthetic temperature step.")
    return {
        "temporary_store": "write/read passed",
        "posix_permissions": "checked" if os.name == "posix" else "manual Windows ACL check required",
        "signal_csv": "synthetic temperature step detected",
        "openssl": openssl.stdout.strip(),
        "manual_checks_remaining": [
            "Volume encryption and access under the intended local account",
            "Encrypted handoff and backup restoration on this workstation",
            "Consent, reviewer independence and private delivery",
        ],
    }


def record_effort(db, args):
    case(db, args.case)
    entry = clean(args.entry, 80)
    if not 1 <= args.minutes <= 1440:
        raise ValueError("Record between 1 and 1440 active minutes per entry.")
    previous = db.execute("SELECT stage, minutes FROM effort WHERE case_id = ? AND entry = ?",
                          (args.case, entry)).fetchone()
    if previous is not None and tuple(previous) != (args.stage, args.minutes):
        raise ValueError("This effort entry already exists with different values.")
    db.execute("INSERT OR IGNORE INTO effort VALUES (?, ?, ?, ?)",
               (args.case, entry, args.stage, args.minutes))
    return {"entry": entry, "stage": args.stage, "minutes": args.minutes,
            "already_recorded": previous is not None}


def effort_summary(db, args):
    record = case(db, args.case)
    stages = {stage: 0 for stage in EFFORT_STAGES}
    for row in db.execute("SELECT stage, SUM(minutes) AS total FROM effort WHERE case_id = ? GROUP BY stage",
                          (args.case,)):
        stages[row["stage"]] = row["total"]
    inventory = db.execute("SELECT details FROM evidence WHERE case_id = ?", (args.case,))
    formats = {}
    total_bytes = 0
    for row in inventory:
        source = json.loads(row["details"])
        extension = source["extension"]
        formats[extension] = formats.get(extension, 0) + 1
        total_bytes += source["bytes"]
    first_delivery = db.execute(
        "SELECT MIN(utc) FROM custody WHERE case_id = ? AND action = 'private_delivery_recorded'",
        (args.case,),
    ).fetchone()[0]
    turnaround = None
    if first_delivery:
        elapsed = datetime.fromisoformat(first_delivery) - datetime.fromisoformat(record["created"])
        turnaround = round(elapsed.total_seconds() / 60, 2)
    return {
        "case_id": args.case, "active_minutes_by_stage": stages,
        "total_active_minutes": sum(stages.values()), "file_count_by_extension": formats,
        "total_source_bytes": total_bytes, "first_delivery_turnaround_minutes": turnaround,
        "visibility": "private",
    }


def status(db, args):
    record = case(db, args.case)
    return {
        "case_id": args.case, "expires_utc": record["expires"],
        "custody": [dict(row) for row in db.execute(
            "SELECT utc, actor, action, reference FROM custody WHERE case_id = ? ORDER BY id",
            (args.case,))],
    }


def withdraw(db, args):
    case(db, args.case, include_expired=True)
    db.execute("DELETE FROM cases WHERE id = ?", (args.case,))
    return {"case_id": args.case, "removed_from_active_store": True}


def purge_expired(db, args):
    cursor = db.execute("DELETE FROM cases WHERE expires <= ?", (now()[:10],))
    return {"expired_cases_removed_from_active_store": cursor.rowcount}


def parser():
    cli = argparse.ArgumentParser(description=__doc__, fromfile_prefix_chars="@")
    cli.add_argument("--store", required=True, type=Path)
    cli.add_argument("--actor", required=True, help="Local operator or reviewer identifier")
    commands = cli.add_subparsers(dest="command", required=True)

    commands.add_parser("preflight")
    new = commands.add_parser("open-case")
    for option in ("question", "consent-reference", "expires"):
        new.add_argument("--" + option, required=True)
    new.add_argument("--confirm-authority-and-private-review", action="store_true", required=True)

    add = commands.add_parser("intake")
    add.add_argument("case")
    add.add_argument("file", type=Path)
    add.add_argument("--expected-sha256")
    for option in ("device", "captured", "clock-context", "context"):
        add.add_argument("--" + option, required=True)

    for name in ("verify", "analyze"):
        command = commands.add_parser(name)
        command.add_argument("case")
        command.add_argument("evidence")
        if name == "verify":
            command.add_argument("--compare", type=Path)
        else:
            command.add_argument("--interval", required=True, type=float)
            command.add_argument("--threshold", required=True, type=float)

    finalize = commands.add_parser("review")
    finalize.add_argument("case")
    finalize.add_argument("--finding", required=True, choices=FINDINGS)
    for option in ("rationale", "tests", "limitations", "reconsider-if"):
        finalize.add_argument("--" + option, required=True)
    finalize.add_argument("--correction")

    read = commands.add_parser("report")
    read.add_argument("case")
    read.add_argument("version", type=int)
    read.add_argument("--format", choices=("json", "html"), default="json")
    for name in ("check-delivery", "record-delivery"):
        delivery = commands.add_parser(name)
        delivery.add_argument("case")
        delivery.add_argument("version", type=int)
        if name == "record-delivery":
            for option in ("report-sha256", "recipient-reference", "delivery-reference"):
                delivery.add_argument("--" + option, required=True)
            delivery.add_argument("--confirm-private-delivery", action="store_true", required=True)
    effort = commands.add_parser("record-effort")
    effort.add_argument("case")
    effort.add_argument("--entry", required=True)
    effort.add_argument("--stage", required=True, choices=EFFORT_STAGES)
    effort.add_argument("--minutes", required=True, type=int)
    commands.add_parser("effort-summary").add_argument("case")
    commands.add_parser("status").add_argument("case")
    withdrawal = commands.add_parser("withdraw")
    withdrawal.add_argument("case")
    withdrawal.add_argument("--confirm", action="store_true", required=True)
    commands.add_parser("purge-expired").add_argument("--confirm", action="store_true", required=True)
    return cli


OPERATIONS = {"open-case": open_case, "intake": intake, "verify": verify, "analyze": analyze,
              "review": review, "report": report, "check-delivery": check_delivery,
              "record-delivery": record_delivery, "status": status,
              "record-effort": record_effort, "effort-summary": effort_summary,
              "withdraw": withdraw, "purge-expired": purge_expired}


def main():
    cli = parser()
    args = cli.parse_args()
    try:
        args.actor = clean(args.actor, 80)
        if args.command == "preflight":
            result = preflight(args.store)
        else:
            with open_store(args.store) as db, write(db):
                result = OPERATIONS[args.command](db, args)
        if args.command == "report" and args.format == "html":
            sys.stdout.buffer.write(printable_report(result).encode("utf-8"))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=True))
    except (ValueError, OSError, sqlite3.Error, subprocess.SubprocessError) as exc:
        cli.exit(1, f"Pilot: {exc}\n")


if __name__ == "__main__":
    main()
