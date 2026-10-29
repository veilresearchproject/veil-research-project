#!/usr/bin/env python3
"""Read-only, value-redacting structural survey of an MTC completed session.

Zero dependencies beyond Python 3.9+. Never writes to the input directory or to disk.
This is *not* a recording validator, timeline verifier, or AI audio analyzer.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

VERSION = "0.1.0"
REQUIRED_FILES = ("session_result.json", "session_metadata.json", "events.jsonl")
MAX_SMALL_FILE = 2 * 1024 * 1024
MAX_EVENTS_FILE = 16 * 1024 * 1024
MAX_EVENT_LINE = 256 * 1024
MAX_FIELDS = 120
MAX_KEY_LEN = 120
MAX_ARRAY_SAMPLE = 12
MAX_DEPTH = 3


def typename(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    return "unknown"


def _safe_key(key):
    # Key names are necessary for mapping unknown log schemas, but limit their
    # length so untrusted content cannot dominate reports. Values are never shown.
    if len(key) <= MAX_KEY_LEN:
        return key
    return key[:MAX_KEY_LEN] + "…[truncated]"


def _path(parent, name):
    # Unambiguous JSON notation even when keys include periods or brackets.
    return parent + "[" + json.dumps(_safe_key(name), ensure_ascii=True) + "]"


def accumulate_shape(value, path, counters, dropped, depth=0):
    if path not in counters and len(counters) >= MAX_FIELDS:
        dropped[0] += 1
        return
    counters.setdefault(path, Counter())[typename(value)] += 1
    if depth >= MAX_DEPTH:
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(k, str):
                accumulate_shape(v, _path(path, k), counters, dropped, depth+1)
    elif isinstance(value, list):
        for child in value[:MAX_ARRAY_SAMPLE]:
            accumulate_shape(child, path + "[]", counters, dropped, depth+1)


def _safe_read_regular(root: Path, filename: str, byte_limit: int):
    """Accept only directly named, regular files and bound reads."""
    path = root / filename
    st = path.lstat()  # refuses symlink even if it resolves to a real file
    if not stat.S_ISREG(st.st_mode):
        raise ValueError("not a regular file (symlinks are not accepted)")
    if st.st_size > byte_limit:
        raise ValueError(f"file exceeds {byte_limit} byte safety limit")
    # O_NOFOLLOW protects the final path component against simple link swaps.
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as f:
        fs = os.fstat(f.fileno())
        if not stat.S_ISREG(fs.st_mode) or fs.st_size > byte_limit:
            raise ValueError("file changed or exceeds safety limit")
        data = f.read(byte_limit + 1)
    if len(data) > byte_limit:
        raise ValueError("file expanded past safety limit while reading")
    return data


def _profile_json(data):
    obj = json.loads(data.decode("utf-8-sig"))
    fields, dropped = {}, [0]
    accumulate_shape(obj, "$", fields, dropped)
    return {
        "top_level_type": typename(obj),
        "paths": [{"path": k, "types": dict(sorted(v.items()))} for k, v in sorted(fields.items())],
        "excess_field_paths_dropped": dropped[0],
    }


def _profile_events(data):
    fields, dropped = {}, [0]
    bad_lines, blank_lines, non_object = [], 0, 0
    valid_rows = 0
    raw_lines = data.split(b"\n")
    if raw_lines[-1] == b"":
        raw_lines.pop()
    for line_no, line in enumerate(raw_lines, 1):
        if not line.strip():
            blank_lines += 1
            continue
        if len(line) > MAX_EVENT_LINE:
            bad_lines.append({"line": line_no, "reason": "line too long"})
            continue
        try:
            obj = json.loads(line.decode("utf-8-sig"))
        except (ValueError, UnicodeError):
            bad_lines.append({"line": line_no, "reason": "invalid JSON or encoding"})
            continue
        valid_rows += 1
        if not isinstance(obj, dict):
            non_object += 1
        accumulate_shape(obj, "$", fields, dropped)
    return {
        "total_lines": len(raw_lines),
        "valid_json_rows": valid_rows,
        "blank_lines": blank_lines,
        "non_object_rows": non_object,
        "invalid_rows": bad_lines[:50],
        "invalid_row_count": len(bad_lines),
        "paths": [{"path": k, "types": dict(sorted(v.items()))} for k, v in sorted(fields.items())],
        "excess_field_paths_dropped": dropped[0],
    }


def survey(folder):
    root = Path(folder)
    report = {
        "tool": "VEIL MTC read-only session schema survey",
        "version": VERSION,
        "file_contents_exported": False,
        "evidence_files_modified": False,
        "recording_validated": False,
        "files": {},
        "errors": [],
        "warnings": [],
        "outcome": "HOLD",
    }
    try:
        if root.is_symlink() or not root.is_dir():
            raise ValueError("session folder missing, not a directory, or a symlink")
    except OSError as ex:
        raise ValueError("cannot access session folder") from ex
    for name in REQUIRED_FILES:
        cap = MAX_EVENTS_FILE if name.endswith(".jsonl") else MAX_SMALL_FILE
        try:
            raw = _safe_read_regular(root, name, cap)
            details = {"present": True, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            if name.endswith(".jsonl"):
                profile = _profile_events(raw)
                details.update(profile)
                if profile["invalid_row_count"]:
                    report["errors"].append(f"{name}: {profile['invalid_row_count']} invalid rows")
                if profile["non_object_rows"]:
                    report["warnings"].append(f"{name}: {profile['non_object_rows']} non-object JSON rows")
                if profile["blank_lines"]:
                    report["warnings"].append(f"{name}: {profile['blank_lines']} blank lines")
                if not profile["valid_json_rows"]:
                    report["errors"].append(f"{name}: no valid event rows")
            else:
                details.update(_profile_json(raw))
                if details["top_level_type"] != "object":
                    report["warnings"].append(f"{name}: top-level JSON is not an object")
            if details["excess_field_paths_dropped"]:
                report["warnings"].append(f"{name}: truncated field-path inventory")
            report["files"][name] = details
        except FileNotFoundError:
            report["files"][name] = {"present": False}
            report["errors"].append(f"{name}: missing")
        except (OSError, UnicodeError, ValueError) as ex:
            report["files"][name] = {"present": False, "error": type(ex).__name__}
            report["errors"].append(f"{name}: {str(ex)[:160]}")
    if not report["errors"]:
        report["outcome"] = "SCHEMA_PROFILED_ONLY"
    report["warnings"].append("This report contains structural metadata, NOT WAV or playback validation")
    report["warnings"].append("Do not infer a successful 90-minute test or paranormal signal")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only structural survey of MTC JSON logs; prints no source values")
    parser.add_argument("session_dir", help="Stopped, copied session directory on PERSONAL HOME PC")
    args = parser.parse_args(argv)
    try:
        result = survey(args.session_dir)
    except ValueError as exc:
        result = {"tool": "VEIL MTC read-only session schema survey", "outcome": "HOLD", "errors": [str(exc)], "files": {}, "evidence_files_modified": False}
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0 if result["outcome"] == "SCHEMA_PROFILED_ONLY" else 2


if __name__ == "__main__":
    sys.exit(main())
