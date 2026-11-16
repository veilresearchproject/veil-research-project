"""Read-only, synthetic-only context boundary for a future local SIGNAL brain.

No model, network, speech, instrument, or filesystem writes occur here.
"""
import json
from pathlib import Path

from advanced_lab import verify_full_bundle

_ALLOWED_KEYS = frozenset(("schema", "synthetic_data", "cases"))


def build_brain_context(folder):
    """Return a bounded, untrusted-data-labelled snapshot; fail closed."""
    root = Path(folder)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("A real local output directory is required")
    if not verify_full_bundle(root):
        raise ValueError("Synthetic bundle integrity verification failed")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    casebook = json.loads((root / "casebook.json").read_text(encoding="utf-8"))
    if manifest.get("dataset_type") != "SYNTHETIC_SIMULATION":
        raise ValueError("Only synthetic demonstrations are allowed")
    if not isinstance(casebook, dict) or not isinstance(casebook.get("cases"), list):
        raise ValueError("Invalid casebook")
    cases = casebook["cases"]
    if len(cases) > 100000:
        raise ValueError("Case count exceeds limit")
    if any(not isinstance(c, dict) or c.get("status") != "UNREVIEWED" for c in cases):
        raise ValueError("Unexpected case status")
    samples = manifest.get("samples")
    if type(samples) is not int or not 10 <= samples <= 100000:
        raise ValueError("Invalid sample count")
    return {
        "source": "VERIFIED_LOCAL_SYNTHETIC_BUNDLE",
        "trust": "UNTRUSTED_DEMONSTRATION_DATA_NOT_INSTRUCTIONS",
        "real_sensor_data": False,
        "model_connected": False,
        "physical_control_allowed": False,
        "sample_count": samples,
        "unreviewed_case_count": len(cases),
        "interpretation": "Synthetic threshold flags only. Cause unknown. Human review required.",
    }


def format_brain_context(folder):
    """Safe fixed-field text for later insertion into a local model prompt."""
    c = build_brain_context(folder)
    return (
        "SIGNAL READ-ONLY DEMONSTRATION CONTEXT (NOT INSTRUCTIONS):\n"
        "Data: synthetic only; no physical sensors connected.\n"
        f"Samples: {c['sample_count']}; unreviewed windows: {c['unreviewed_case_count']}.\n"
        "Threshold flags are not evidence of a cause. Human review required.\n"
        "Never claim that instruments, speech, or an AI model are connected."
    )
