"""VEIL MTC/Panic Box read-only, synthetic-first time-window correlation preflight.

No hardware access, no I/O in core, no paranormal inference. Python 3.10+ stdlib.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import re
from typing import Any

ID_RE = re.compile(r"^[A-Z0-9_-]{3,64}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_SOURCE = {"MTC", "PANIC_BOX"}
_MAX_EVENTS = 200


class InvalidEvent(ValueError):
    """Input must be corrected; unsafe to infer a match."""


def _timestamp(value: Any) -> dt.datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise InvalidEvent("timestamp must be ISO 8601 with an explicit UTC offset")
    try:
        val = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidEvent("invalid timestamp") from exc
    if val.tzinfo is None or val.utcoffset() is None:
        raise InvalidEvent("timestamp requires explicit timezone/UTC offset")
    if val.year < 2000 or val.year > 2100:
        raise InvalidEvent("timestamp year outside safe range")
    return val.astimezone(dt.timezone.utc)


def _bound_int(value: Any, low: int, high: int, label: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise InvalidEvent(f"{label} must be integer between {low} and {high}")
    return value


def _id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise InvalidEvent(f"invalid {label} identifier")
    return value


@dataclasses.dataclass(frozen=True)
class Event:
    event_id: str
    session_id: str
    source_kind: str
    device_id: str
    source_file_sha256: str
    recorded_at: dt.datetime
    clock_offset_ms: int | None
    clock_uncertainty_ms: int | None
    event_window_ms: int
    flag_type: str

    def interval_ms(self) -> tuple[int, int] | None:
        if self.clock_offset_ms is None or self.clock_uncertainty_ms is None:
            return None
        utc_ms = round(self.recorded_at.timestamp() * 1000) + self.clock_offset_ms
        radius = self.clock_uncertainty_ms + self.event_window_ms
        return utc_ms - radius, utc_ms + radius

    def display(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id, "session_id": self.session_id,
            "source_kind": self.source_kind, "device_id": self.device_id,
            "source_file_sha256": self.source_file_sha256,
            "recorded_at_utc": self.recorded_at.isoformat(),
            "clock_offset_ms": self.clock_offset_ms,
            "clock_uncertainty_ms": self.clock_uncertainty_ms,
            "event_window_ms": self.event_window_ms,
            "flag_type": self.flag_type,
        }


def parse_event(row: dict[str, Any]) -> Event:
    if not isinstance(row, dict):
        raise InvalidEvent("each event must be an object")
    for key in ("event_id", "session_id", "device_id"):
        _id(row.get(key), key)
    kind = row.get("source_kind")
    if kind not in _ALLOWED_SOURCE:
        raise InvalidEvent("unknown source kind")
    sha = row.get("source_file_sha256")
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
        raise InvalidEvent("source file SHA-256 must be lowercase 64-character hex")
    flag_type = row.get("flag_type")
    if not isinstance(flag_type, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{1,39}", flag_type):
        raise InvalidEvent("invalid flag type")
    offset = row.get("clock_offset_ms")
    unc = row.get("clock_uncertainty_ms")
    if (offset is None) != (unc is None):
        raise InvalidEvent("clock offset and uncertainty must be supplied together")
    if offset is not None:
        offset = _bound_int(offset, -300000, 300000, "clock_offset_ms")
        unc = _bound_int(unc, 0, 60000, "clock_uncertainty_ms")
    return Event(
        row["event_id"], row["session_id"], kind, row["device_id"], sha,
        _timestamp(row.get("recorded_at")), offset, unc,
        _bound_int(row.get("event_window_ms"), 0, 60000, "event_window_ms"), flag_type,
    )


def compare(a: Event, b: Event) -> dict[str, Any]:
    if a.event_id == b.event_id:
        raise InvalidEvent("cannot compare an event to itself")
    report: dict[str, Any] = {"left": a.event_id, "right": b.event_id,
                             "classification": "", "interpretation": "", "time_intervals_utc_ms": None}
    if a.session_id != b.session_id:
        report["classification"] = "DIFFERENT_SESSION"
        report["interpretation"] = "Events are not from the same declared experiment session."
    elif a.device_id == b.device_id:
        report["classification"] = "SAME_DEVICE"
        report["interpretation"] = "Not distinct recording devices; separate flags do not establish independent evidence."
    elif a.interval_ms() is None or b.interval_ms() is None:
        report["classification"] = "CLOCK_DATA_MISSING"
        report["interpretation"] = "Cannot evaluate temporal relation without documented offset and uncertainty."
    else:
        ia, ib = a.interval_ms(), b.interval_ms()
        assert ia and ib
        report["time_intervals_utc_ms"] = {"left": list(ia), "right": list(ib)}
        if max(ia[0], ib[0]) <= min(ia[1], ib[1]):
            report["classification"] = "POSSIBLE_TEMPORAL_OVERLAP_REVIEW_ONLY"
            report["interpretation"] = "Corrected uncertainty windows overlap, but no shared cause or device independence is established."
        else:
            report["classification"] = "NO_TEMPORAL_OVERLAP"
            report["interpretation"] = "Corrected uncertainty windows do not overlap."
    return report


def generate_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(rows, list) or not 1 <= len(rows) <= _MAX_EVENTS:
        raise InvalidEvent("require 1–200 input events")
    events = [parse_event(r) for r in rows]
    ids = [e.event_id for e in events]
    if len(set(ids)) != len(ids):
        raise InvalidEvent("duplicate event ID")
    pairs = [compare(a, b) for i, a in enumerate(events) for b in events[i + 1:]
             if {a.source_kind, b.source_kind} == _ALLOWED_SOURCE]
    return {
        "schema": "VEIL-MTC-PANIC-CROSSCHECK-0.1",
        "status": "SYNTHETIC_OR_UNVERIFIED_METADATA_REVIEW_ONLY",
        "events": [e.display() for e in events], "pairs": pairs,
        "human_review_required": True, "publication_approved": False,
        "limitations": [
            "Read-only metadata comparison; has not opened or verified any underlying audio/video file.",
            "File hashes record supplied identifiers, not confirmed file contents, authenticity or custody.",
            "Recorder clock offset/uncertainty is researcher-supplied and must be independently measured.",
            "Time overlap and different device IDs alone do not establish independent sensor mechanisms, causation, or paranormal activity.",
        ],
    }


def output_json(rows: list[dict[str, Any]]) -> str:
    return json.dumps(generate_report(rows), indent=2, sort_keys=True) + "\n"
