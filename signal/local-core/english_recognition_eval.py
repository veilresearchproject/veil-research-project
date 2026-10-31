"""Opt-in, offline English speech-to-text evaluation for VEIL SIGNAL.

Consumes only operator-provided reference/transcript text pairs. Never records,
transcribes, calls a model, profiles a speaker, or writes results to disk.
Standard library only; synthetic data is supplied separately for demonstrations.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import statistics

SCHEMA = "veil.signal.english_recognition_eval.v1"
MAX_INPUT_BYTES = 65536
MAX_SAMPLES = 100
MAX_TEXT_CHARS = 500
MAX_TERMS = 30
MAX_TOKENS = 120
MAX_LATENCY_MS = 600000
_WORDS = re.compile(r"[^\W_]+(?:'[^\W_]+)*", re.UNICODE)


def tokenize(text):
    """Case-fold and ignore punctuation for reproducible English-first scoring."""
    return _WORDS.findall(text.casefold())


def _check_text(value, name, allow_empty=False):
    if not isinstance(value, str) or len(value) > MAX_TEXT_CHARS:
        raise ValueError(f"{name} must be text of at most {MAX_TEXT_CHARS} characters")
    if any(ord(ch) < 32 and ch not in "\t\n\r" for ch in value):
        raise ValueError(f"{name} contains a control character")
    words = tokenize(value)
    if len(words) > MAX_TOKENS or (not words and not allow_empty):
        raise ValueError(f"{name} must contain 1 to {MAX_TOKENS} words" if not allow_empty
                         else f"{name} contains too many words")
    return words


def edit_counts(reference, hypothesis):
    """Return (substitutions, deletions, insertions), deterministic tie breaking."""
    n, m = len(reference), len(hypothesis)
    # Each cell: (total cost, substitutions, deletions, insertions).
    prev = [(j, 0, 0, j) for j in range(m + 1)]
    for i in range(1, n + 1):
        cur = [(i, 0, i, 0)]
        for j in range(1, m + 1):
            if reference[i - 1] == hypothesis[j - 1]:
                cur.append(prev[j - 1])
                continue
            s = prev[j - 1]
            d = prev[j]
            ins = cur[j - 1]
            choices = [
                (s[0] + 1, s[1] + 1, s[2], s[3], 0),
                (d[0] + 1, d[1], d[2] + 1, d[3], 1),
                (ins[0] + 1, ins[1], ins[2], ins[3] + 1, 2),
            ]
            chosen = min(choices, key=lambda item: (item[0], item[4]))
            cur.append(chosen[:4])
        prev = cur
    return prev[-1][1:]


def _ngram_counts(words, pattern):
    size = len(pattern)
    return sum(tuple(words[i:i + size]) == pattern
               for i in range(len(words) - size + 1))


def _latency(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("latency_ms must be a number")
    if not math.isfinite(value) or not 0 <= value <= MAX_LATENCY_MS:
        raise ValueError("latency_ms is outside the allowed range")
    return value


def evaluate(payload):
    """Compute aggregate scores; do not echo or persist transcript text."""
    if not isinstance(payload, dict) or set(payload) != {"schema", "samples", "terms"}:
        raise ValueError("Expected schema, samples and terms")
    if payload["schema"] != SCHEMA:
        raise ValueError("Unsupported schema")
    samples, terms = payload["samples"], payload["terms"]
    if not isinstance(samples, list) or not 1 <= len(samples) <= MAX_SAMPLES:
        raise ValueError("Expected 1 to 100 samples")
    if not isinstance(terms, list) or len(terms) > MAX_TERMS:
        raise ValueError("Expected at most 30 terms")
    term_tokens = []
    for t in terms:
        w = _check_text(t, "term")
        if len(w) > 5:
            raise ValueError("Term must contain at most five words")
        if tuple(w) in term_tokens:
            raise ValueError("Duplicate normalized term")
        term_tokens.append(tuple(w))

    reference_words = 0
    sub = deletion = insertion = exact = 0
    latencies = []
    totals = [0] * len(terms)
    found = [0] * len(terms)
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict) or not (
            {"reference", "transcript"} <= set(sample) <=
            {"reference", "transcript", "latency_ms"}
        ):
            raise ValueError(f"Invalid sample #{index + 1}")
        ref = _check_text(sample["reference"], "reference")
        hyp = _check_text(sample["transcript"], "transcript", allow_empty=True)
        reference_words += len(ref)
        s, d, i = edit_counts(ref, hyp)
        sub += s
        deletion += d
        insertion += i
        exact += int(ref == hyp)
        if "latency_ms" in sample:
            latencies.append(_latency(sample["latency_ms"]))
        for t, pattern in enumerate(term_tokens):
            count = _ngram_counts(ref, pattern)
            totals[t] += count
            found[t] += min(count, _ngram_counts(hyp, pattern))

    errors = sub + deletion + insertion
    latencies.sort()
    return {
        "schema": "veil.signal.english_recognition_report.v1",
        "status": "operator_supplied_transcripts_unverified",
        "sample_count": len(samples),
        "reference_word_count": reference_words,
        "substitutions": sub,
        "deletions": deletion,
        "insertions": insertion,
        "word_error_rate": round(errors / reference_words, 4),
        "sentence_accuracy": round(exact / len(samples), 4),
        "technical_terms": [
            {"term": terms[k], "reference_occurrences": totals[k],
             "recognized_occurrences": found[k],
             "recall": round(found[k] / totals[k], 4) if totals[k] else None}
            for k in range(len(terms))
        ],
        "latency_ms": {
            "samples": len(latencies),
            "median": round(statistics.median(latencies), 2) if latencies else None,
            "p95_nearest_rank": latencies[math.ceil(.95 * len(latencies)) - 1]
            if latencies else None,
        },
        "limitations": [
            "Text-only evaluation; no microphone, speech recognition, or local model was run.",
            "Human reference and transcript pairs are not independently verified.",
            "Punctuation/case are ignored; exact technical-term matches are not time-aligned.",
            "Do not compare microphone accuracy without matched phrases, rooms and recognition settings.",
            "No speaker identity, ability, or education is inferred.",
        ],
    }


def _unique_pairs(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError("Duplicate JSON key")
        data[key] = value
    return data


def _no_constants(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


def load_fixture(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Fixture must be a regular file, not a symlink")
    with path.open("rb") as stream:
        data = stream.read(MAX_INPUT_BYTES + 1)
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError("Fixture exceeds 64 KiB")
    return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs,
                      parse_constant=_no_constants)


def main(argv=None):
    parser = argparse.ArgumentParser(description="SIGNAL offline English transcription evaluation")
    parser.add_argument("fixture", type=Path, help="Manually prepared JSON (no audio)")
    args = parser.parse_args(argv)
    try:
        report = evaluate(load_fixture(args.fixture))
    except (ValueError, UnicodeError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
