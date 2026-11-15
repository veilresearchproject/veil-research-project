"""SIGNAL v0.4 — ten evidence-first *synthetic-only* review steps.

No physical control, model calls, audio playback, network access, or findings.
The caller must separately verify the source file before submitting records.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
from html import escape
import math
import re

UTC = timezone.utc
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
DECISIONS = frozenset(("ordinary", "unexplained", "uncertain"))


def _identifier(value, field):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ValueError(f"Invalid {field}")
    return value


def _utc(when):
    if not isinstance(when, str):
        raise ValueError("UTC timestamp must be text")
    try:
        parsed = datetime.fromisoformat(when.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("UTC timestamp required")
    return parsed.astimezone(UTC)


def _number(v, field, *, minimum=None, maximum=None):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError(f"Invalid {field}")
    if minimum is not None and v < minimum or maximum is not None and v > maximum:
        raise ValueError(f"Out-of-range {field}")
    return float(v)


# Update 17: explicit, testable hypotheses and preregistration *plan*, not certification.
def validate_protocol(plan):
    if not isinstance(plan, dict):
        raise ValueError("Protocol must be a mapping")
    required = ("protocol_id", "hypothesis", "null_hypothesis", "primary_outcome",
                "control_description", "analysis_plan", "blinding_plan", "consent_plan")
    for field in required:
        text = plan.get(field)
        if not isinstance(text, str) or not text.strip() or len(text) > 1500:
            raise ValueError(f"Missing or invalid {field}")
    _identifier(plan["protocol_id"], "protocol_id")
    if plan.get("mode") != "SYNTHETIC_SIMULATION":
        raise ValueError("Only simulated experiments supported")
    return dict(id=plan["protocol_id"], status="ILLUSTRATIVE PLAN — NOT PREREGISTERED",
                human_review_required=True, has_control=True, has_null_hypothesis=True)


# Update 18: per-source identities, UTC clock offsets and declared uncertainty.
def validate_source_registry(sources):
    if not isinstance(sources, list) or not 1 <= len(sources) <= 20:
        raise ValueError("Require 1–20 source records")
    registry = {}
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Invalid source record")
        sid = _identifier(source.get("device_id"), "device_id")
        if sid in registry:
            raise ValueError("Duplicate source device")
        modality = _identifier(source.get("modality"), "modality")
        offset = _number(source.get("clock_offset_ms"), "clock_offset_ms", minimum=-86400000, maximum=86400000)
        error = _number(source.get("clock_uncertainty_ms"), "clock_uncertainty_ms", minimum=0, maximum=86400000)
        registry[sid] = dict(device_id=sid, modality=modality, clock_offset_ms=offset,
                             clock_uncertainty_ms=error, actual_calibration_verified=False)
    return registry


# Update 19: normalize per-device timestamps (offset is device time minus UTC).
def normalize_timeline(raw_events, registry):
    if not isinstance(raw_events, list) or len(raw_events) > 300000:
        raise ValueError("Invalid or excessive event count")
    events, event_ids = [], set()
    for row in raw_events:
        if not isinstance(row, dict):
            raise ValueError("Invalid event")
        eid = _identifier(row.get("event_id"), "event_id")
        if eid in event_ids:
            raise ValueError("Duplicate event ID")
        event_ids.add(eid)
        sid = row.get("device_id")
        if sid not in registry:
            raise ValueError("Unknown device")
        channel = _identifier(row.get("channel"), "channel")
        condition = row.get("condition")
        if condition not in ("test", "control"):
            raise ValueError("Unknown condition")
        observed = _number(row.get("observed_value"), "observed_value")
        source = registry[sid]
        corrected = _utc(row.get("timestamp_utc")) - timedelta(milliseconds=source["clock_offset_ms"])
        uncertainty = timedelta(milliseconds=source["clock_uncertainty_ms"])
        events.append(dict(event_id=eid, device_id=sid, modality=source["modality"],
                           channel=channel, condition=condition, value=observed,
                           utc=corrected, earliest=corrected - uncertainty,
                           latest=corrected + uncertainty,
                           clock_uncertainty_ms=source["clock_uncertainty_ms"]))
    return sorted(events, key=lambda e: (e["utc"], e["event_id"]))


# Update 20: purely numeric screening using *declared* channel bounds.
def screen_candidates(events, thresholds):
    if not isinstance(thresholds, dict) or not thresholds:
        raise ValueError("Explicit bounds are required")
    bounds = {}
    for channel, pair in thresholds.items():
        _identifier(channel, "threshold channel")
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("Expected lower and upper threshold")
        low, high = (_number(pair[0], "low bound"), _number(pair[1], "high bound"))
        if low >= high:
            raise ValueError("Lower bound must precede upper bound")
        bounds[channel] = (low, high)
    candidates = []
    for event in events:
        if event["channel"] not in bounds:
            raise ValueError("Missing channel threshold")
        low, high = bounds[event["channel"]]
        if event["value"] < low or event["value"] > high:
            candidates.append({**event, "screening_label": "UNVERIFIED NUMERIC OUTLIER",
                               "cause": "UNKNOWN"})
    return candidates


# Update 21: group overlapping uncertainty intervals; distinct devices ≠ proof.
def group_candidate_windows(candidates, *, tolerance_ms=0):
    tol = _number(tolerance_ms, "tolerance_ms", minimum=0, maximum=600000)
    gap = timedelta(milliseconds=tol)
    result = []
    for candidate in sorted(candidates, key=lambda c: (c["earliest"], c["event_id"])):
        if not result or candidate["earliest"] > result[-1]["end"] + gap:
            result.append(dict(window_id=f"window-{len(result)+1:04d}", start=candidate["earliest"],
                               end=candidate["latest"], event_ids=[candidate["event_id"]],
                               devices={candidate["device_id"]}))
        else:
            group = result[-1]
            group["end"] = max(group["end"], candidate["latest"])
            group["event_ids"].append(candidate["event_id"])
            group["devices"].add(candidate["device_id"])
    return [dict(window_id=g["window_id"], start_utc=g["start"].isoformat(),
                 end_utc=g["end"].isoformat(), event_ids=g["event_ids"],
                 distinct_devices=len(g["devices"]),
                 cross_device_cooccurrence=len(g["devices"]) >= 2,
                 finding="TEMPORAL CANDIDATE ONLY — NOT CAUSAL EVIDENCE") for g in result]


# Update 22: explicit denominators, zero-control handling; not a significance test.
def compare_test_control(candidates, exposure_seconds):
    if not isinstance(exposure_seconds, dict) or set(exposure_seconds) != {"test", "control"}:
        raise ValueError("Test and control exposure durations required")
    rates = {}
    for label in ("test", "control"):
        seconds = _number(exposure_seconds[label], "exposure_seconds", minimum=0.001)
        count = sum(1 for c in candidates if c["condition"] == label)
        rates[label] = dict(count=count, seconds=seconds, per_hour=round(count * 3600 / seconds, 6))
    denom = rates["control"]["per_hour"]
    return dict(test=rates["test"], control=rates["control"],
                rate_ratio=None if denom == 0 else round(rates["test"]["per_hour"] / denom, 6),
                inference="DESCRIPTIVE ONLY — NOT STATISTICAL SIGNIFICANCE")


# Update 23: masked reviewer list and separate custodian key.
def prepare_blind_queue(candidates, *, secret):
    if not isinstance(secret, str) or len(secret) < 16:
        raise ValueError("Private unpredictable blinding secret required")
    blind, custodian = [], {}
    for candidate in candidates:
        eid = candidate["event_id"]
        opaque = hashlib.sha256((secret + "\0" + eid).encode("utf8")).hexdigest()[:24]
        blind.append(dict(review_id="review-" + opaque,
                          prompt="Assess separately supplied anonymous segment; source details withheld",
                          classification="UNVERIFIED SCREENING CANDIDATE"))
        custodian["review-" + opaque] = eid
    if len(custodian) != len(candidates):
        raise ValueError("Blinding-key collision or duplicate candidate")
    return dict(reviewer_packet=blind, custodian_key=custodian,
                warning="Masking identifiers alone is not validated blinding")


# Update 24: human reviews must be attributable and never silently overwritten.
def add_human_review(existing, *, review_id, reviewer_id, decision, explanation):
    _identifier(review_id, "review_id")
    _identifier(reviewer_id, "reviewer_id")
    if decision not in DECISIONS:
        raise ValueError("Unrecognized decision")
    if not isinstance(explanation, str) or not explanation.strip() or len(explanation) > 1500:
        raise ValueError("Reason is required")
    if not isinstance(existing, list):
        raise ValueError("Review records must be a list")
    if any(r["review_id"] == review_id and r["reviewer_id"] == reviewer_id for r in existing):
        raise ValueError("Duplicate review; never overwrite without a separate audit entry")
    return existing + [dict(review_id=review_id, reviewer_id=reviewer_id,
                            decision=decision, explanation=explanation.strip(),
                            authority="SELF-REPORTED HUMAN REVIEW")]


# Update 25: independent review status; disagreement remains visible.
def resolve_reviews(review_ids, entries):
    grouped = defaultdict(dict)
    for entry in entries:
        rid, who = entry["review_id"], entry["reviewer_id"]
        if who in grouped[rid]:
            raise ValueError("Duplicate reviewer identity")
        grouped[rid][who] = entry["decision"]
    output = []
    for rid in review_ids:
        votes = grouped[rid]
        if len(votes) < 2:
            status = "PENDING INDEPENDENT REVIEW"
        elif len(set(votes.values())) > 1:
            status = "REVIEWER DISAGREEMENT — UNRESOLVED"
        else:
            status = "REVIEWERS AGREE ON LABEL — NOT VALIDATED EVIDENCE"
        output.append(dict(review_id=rid, reviewer_count=len(votes), status=status,
                           self_reported_decisions=dict(votes)))
    return output


# Update 26: offline, escaped, data-minimized technical readout.
def render_lab_readout(protocol, registry, candidates, windows, comparison, decisions, *, csv_sha256):
    if not isinstance(csv_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", csv_sha256):
        raise ValueError("Expected SHA-256 hexadecimal digest")
    parts = ["<!doctype html><html lang='en'><meta charset='utf-8'>",
             "<meta name='viewport' content='width=device-width,initial-scale=1'>",
             "<title>SIGNAL v0.4 Synthetic Review</title>",
             "<style>body{font:16px system-ui;background:#111827;color:#e8edf7;max-width:950px;margin:3rem auto;padding:1rem}"
             "section{border:1px solid #64748b;border-radius:10px;margin:1rem 0;padding:1rem}"
             "h1,h2{color:#dbeafe}.warn{color:#facc15}code{overflow-wrap:anywhere}</style><main>",
             "<h1>SIGNAL v0.4 — Synthetic Research Review</h1>",
             "<p class='warn'><strong>SIMULATED ONLY. NO REAL EQUIPMENT, AI CLASSIFICATION, OR PARANORMAL FINDINGS.</strong></p>",
             f"<p>Study: {escape(protocol['id'])}; status: {escape(protocol['status'])}</p>",
             f"<p>Source devices: {len(registry)}; numeric flags: {len(candidates)}; "
             f"timing windows: {len(windows)}; human review items: {len(decisions)}</p>",
             "<section><h2>Control comparison</h2>",
             f"<p>Test: {comparison['test']['count']} flags / {comparison['test']['seconds']:g} seconds; "
             f"Control: {comparison['control']['count']} flags / {comparison['control']['seconds']:g} seconds.</p>",
             "<p>Descriptive rates only. No probability, significance, or causal conclusion.</p></section>",
             "<section><h2>Review queue</h2><ul>"]
    for decision in decisions:
        parts.append(f"<li>{escape(decision['review_id'])}: {escape(decision['status'])}</li>")
    parts += ["</ul></section>", "<section><h2>Source fingerprint</h2>",
              f"<code>{csv_sha256}</code>",
              "<p>A SHA-256 checksum detects changes but does not establish authenticity, custody, or independent sensors.</p></section>",
              "<p>No source audio, raw readings, reviewer identities, or custodian key are embedded in this report.</p>",
              "</main></html>"]
    return "".join(parts)