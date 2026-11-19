"""Read-only local original-file verification before MTC/Panic metadata correlation.

No device access, no network; verifies bytes at investigator-supplied workspace paths.
All source inputs remain untrusted and must be reviewed by a person.
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import re
import stat
from typing import Any

from correlation import InvalidEvent, generate_report

_MAX_FILE_BYTES = 128 * 1024 * 1024
_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
_SHA = re.compile(r"^[a-f0-9]{64}$")


def _checksum(path: pathlib.Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    # os.O_NOFOLLOW is available on common Unix platforms; also reject symlinks pre-open.
    if path.is_symlink() or not path.is_file():
        raise InvalidEvent("source must be an existing regular file, not a symlink")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags)
    except (OSError, ValueError) as exc:
        raise InvalidEvent("source file could not be opened") from exc
    try:
        with os.fdopen(fd, "rb") as handle:
            meta = os.fstat(handle.fileno())
            if not stat.S_ISREG(meta.st_mode) or not 1 <= meta.st_size <= _MAX_FILE_BYTES:
                raise InvalidEvent("source must be a nonempty regular file no larger than 128 MiB")
            while True:
                data = handle.read(1024 * 1024)
                if not data:
                    break
                size += len(data)
                if size > _MAX_FILE_BYTES:
                    raise InvalidEvent("source exceeded 128 MiB")
                digest.update(data)
    except OSError as exc:
        raise InvalidEvent("source file read failed") from exc
    return digest.hexdigest(), size


def verify_and_correlate(rows: list[dict[str, Any]], workspace: str | pathlib.Path,
                         originals: dict[str, str]) -> dict[str, Any]:
    """Map each declared SHA-256 hash to a safe basename in workspace and verify bytes.

    The returned report only upgrades **file bytes verified**, not origin, time, identity,
    timestamp accuracy, device independence, authenticity, or chain of custody.
    """
    report = generate_report(rows)  # input validation and bounded event count first
    if not isinstance(originals, dict) or len(originals) > 200:
        raise InvalidEvent("originals must be a bounded hash-to-basename mapping")
    root = pathlib.Path(workspace)
    if root.is_symlink() or not root.is_dir():
        raise InvalidEvent("workspace must be an existing local directory")
    root = root.resolve(strict=True)
    required = {e["source_file_sha256"] for e in report["events"]}
    if set(originals) != required:
        raise InvalidEvent("every source checksum must have one explicitly named local original")
    used_names: set[str] = set()
    verified: list[dict[str, Any]] = []
    for expected in sorted(required):
        filename = originals[expected]
        if not isinstance(filename, str) or not _SHA.fullmatch(expected) or not _NAME.fullmatch(filename) or filename in {".", ".."}:
            raise InvalidEvent("invalid hash or unsafe source filename")
        if filename in used_names:
            raise InvalidEvent("same file is assigned to multiple declared hashes")
        used_names.add(filename)
        target = root / filename
        digest, size = _checksum(target)
        if digest != expected:
            raise InvalidEvent("original file checksum mismatch; do not correlate")
        verified.append({"sha256": expected, "filename": filename, "verified_size_bytes": size,
                         "file_bytes_verified": True})
    report["file_integrity"] = verified
    report["status"] = "FILE_BYTES_VERIFIED_METADATA_UNVERIFIED_REVIEW_ONLY"
    report["limitations"].append("Local file-byte checks passed, but file creation date, capture conditions, custody and device clock calibration are not authenticated.")
    return report
