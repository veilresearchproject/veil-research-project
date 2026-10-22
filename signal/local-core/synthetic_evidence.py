"""SIGNAL synthetic evidence intake contract v0.1 (stdlib only).

Pure, read-only byte parser. It cannot open files, access instruments, use a
network, or invoke an AI model. Only deterministic synthetic fixtures are
accepted in v0.1. All observations remain unverified metadata.
"""
import csv
from datetime import datetime
import hashlib
import io
import math
import re

MAX_BYTES = 128_000
MAX_ROWS = 1_000
ISO = re.compile(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|[+-]\d\d:\d\d)$')
IDENT = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$')
SCHEMAS = {
    'thermal': ('timestamp', 'sensor_id', 'temperature_c'),
    'mtc_markers': ('timestamp', 'recorder_id', 'marker'),
}
MARKERS = frozenset({'RECORDING_START', 'RECORDING_END', 'QUESTION_START', 'QUESTION_END'})


def _timestamp(value):
    if not ISO.fullmatch(value):
        raise ValueError('Timestamp must be ISO 8601 with an explicit timezone')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('Invalid calendar timestamp') from exc
    if parsed.utcoffset() is None:
        raise ValueError('Timezone required')
    return parsed.timestamp()


def inspect_synthetic(raw, kind, *, expected_sha256=None, interval_sec=60, threshold_c=1.5):
    """Inspect caller-provided bytes only; return facts, not explanations.

    Caller is responsible for source authorization and provenance. This
    function has no file, URL, device, or model access. It cannot certify data.
    """
    if kind not in SCHEMAS:
        raise ValueError('Unsupported evidence schema')
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ValueError('Expected 1 to 128,000 bytes of synthetic CSV')
    if not isinstance(interval_sec, (int, float)) or not math.isfinite(interval_sec) or not 1 <= interval_sec <= 86400:
        raise ValueError('Invalid sample interval')
    if not isinstance(threshold_c, (int, float)) or not math.isfinite(threshold_c) or not 0 < threshold_c <= 100:
        raise ValueError('Invalid temperature threshold')
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and (not isinstance(expected_sha256, str) or
                                        not re.fullmatch('[0-9a-f]{64}', expected_sha256) or
                                        digest != expected_sha256):
        raise ValueError('Source SHA-256 mismatch')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('Source is not valid UTF-8') from exc
    if '\x00' in text:
        raise ValueError('NUL bytes are not valid CSV metadata')
    try:
        rows = csv.reader(io.StringIO(text, newline=''), strict=True)
        header = next(rows, None)
        if header != list(SCHEMAS[kind]):
            raise ValueError('Unexpected header; schema is fixed and ordered')
        count = 0
        streams = {}
        last = {}
        marker_counts = {}
        issues = 0
        gaps = 0
        steps = 0
        min_c = None
        max_c = None
        for row in rows:
            count += 1
            if count > MAX_ROWS:
                raise ValueError('Synthetic fixture exceeds 1,000 data rows')
            if len(row) != 3 or any(len(cell) > 80 for cell in row):
                raise ValueError('Malformed or oversized metadata field')
            when = _timestamp(row[0])
            stream = row[1]
            if not IDENT.fullmatch(stream):
                raise ValueError('Invalid stream identifier')
            streams[stream] = streams.get(stream, 0) + 1
            if kind == 'thermal':
                try:
                    value = float(row[2])
                except ValueError as exc:
                    raise ValueError('Invalid temperature') from exc
                if not math.isfinite(value) or value < -273.15 or value > 1000:
                    raise ValueError('Temperature outside allowed numeric range')
                min_c = value if min_c is None else min(min_c, value)
                max_c = value if max_c is None else max(max_c, value)
                if stream in last:
                    previous_time, previous_value = last[stream]
                    elapsed = when - previous_time
                    if elapsed <= 0:
                        issues += 1
                    else:
                        if elapsed > 1.5 * interval_sec:
                            gaps += 1
                        if abs(value - previous_value) >= threshold_c:
                            steps += 1
                last[stream] = (when, value)
            else:
                marker = row[2]
                if marker not in MARKERS:
                    raise ValueError('Unknown MTC marker; no freeform instructions accepted')
                marker_counts[marker] = marker_counts.get(marker, 0) + 1
                if stream in last and when <= last[stream]:
                    issues += 1
                last[stream] = when
    except csv.Error as exc:
        raise ValueError('Malformed CSV metadata') from exc
    if not count:
        raise ValueError('No data rows')
    return {
        'schema': 'signal.synthetic-evidence.0.1',
        'source_type': 'SYNTHETIC_ONLY',
        'kind': kind,
        'sha256': digest,
        'rows': count,
        'streams': dict(sorted(streams.items())),
        'timestamp_order_issues': issues,
        'cadence_gaps': gaps if kind == 'thermal' else None,
        'temperature_step_flags': steps if kind == 'thermal' else None,
        'min_c': min_c,
        'max_c': max_c,
        'marker_counts': dict(sorted(marker_counts.items())) if kind == 'mtc_markers' else None,
        'live_instrument_connection': False,
        'model_inference': False,
        'scientific_cause_determined': False,
        'limitation': 'Deterministic metadata check only. Synthetic data; no acquisition, calibration, provenance, or cause verified.',
    }
