"""VEIL offline, read-only MTC/SIGNAL review pack v0.2.

No recorder or cloud access. Keeps all candidates (including those coinciding with
question markers) for human review; optional derived clips outside evidence.
Hashes are *current inventories*, not proof that files were original/untampered.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import stat
import wave
from pathlib import Path
from session_validator import review, WAV_NAME
from signal_audio_screener import scan
from seam_survey import survey

SCHEMA = "veil.signal-review-pack.v0.2"
CHUNK = 4 * 1024 * 1024
MAX_CLIPS = 50
MAX_CLIP_SECONDS = 20.0
SOURCE_NAMES = {"events.jsonl", "session_metadata.json", "session_result.json"}


def _safe_regular(path: Path) -> bool:
    try:
        return not path.is_symlink() and stat.S_ISREG(path.stat().st_mode)
    except OSError:
        return False


def _sha256_file(path: Path):
    """Hash without modifying path. Detect common same-file mutation races.

    This is not adversarial-OS-proof; file provenance requires authenticated capture.
    """
    if not _safe_regular(path):
        return {"file": path.name, "status": "UNREADABLE_OR_UNSAFE"}
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            first = os.fstat(handle.fileno())
            if not stat.S_ISREG(first.st_mode):
                return {"file": path.name, "status": "NOT_REGULAR"}
            while True:
                data = handle.read(CHUNK)
                if not data:
                    break
                digest.update(data)
            final = os.fstat(handle.fileno())
        current = path.stat()
    except OSError as err:
        return {"file": path.name, "status": "READ_FAILURE", "reason": type(err).__name__}
    identity = (first.st_dev, first.st_ino, first.st_size, first.st_mtime_ns)
    final_identity = (final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns)
    current_identity = (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns)
    if identity != final_identity or identity != current_identity or path.is_symlink():
        return {"file": path.name, "status": "CHANGED_DURING_HASH"}
    return {"file": path.name, "bytes": first.st_size,
            "sha256": digest.hexdigest(), "status": "HASHED_CURRENT_CONTENTS"}


def inventory(folder: Path, wavs):
    # Include even CORRUPTED or UNPARSEABLE expected WAVs in hash inventory.
    # A failed WAV header is still evidence that should be fingerprinted.
    seen = {x.name for x in folder.iterdir() if WAV_NAME.fullmatch(x.name)}
    names = sorted(SOURCE_NAMES | seen | {x["file"] for x in wavs})
    rows = [_sha256_file(folder / name) for name in names]
    issues = [{"code": "FILE_HASH_NOT_AVAILABLE", "file": r["file"], "status": r["status"]}
              for r in rows if r["status"] != "HASHED_CURRENT_CONTENTS"]
    return {"hash_algorithm": "sha256", "files": rows, "issues": issues,
            "provenance": "CURRENT_CONTENTS_ONLY_NOT_AUTHENTICATED_CAPTURE",
            "coverage": "SELECTED_RECOGNIZED_FILES_ONLY_NOT_A_COMPLETE_EVIDENCE_INVENTORY"}


def _offsets(wavs):
    offsets, elapsed = {}, 0.0
    for x in wavs:
        offsets[x["file"]] = {"offset": elapsed, "duration": x["duration_seconds"],
                              "rate": x["sample_rate_hz"], "channels": x["channels"],
                              "frames": x["frames"]}
        elapsed += x["duration_seconds"]
    return offsets


def _overlaps(a, b, pairs, pad=2.0):
    return any(a <= end + pad and b >= start - pad for start, end in pairs)


def build_pack(folder: str | Path, *, delta_db=12.0, floor_dbfs=-45.0):
    folder = Path(folder)
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Session folder missing or unsafe")
    mtc = review(folder)
    # IMPORTANT: never silently hide an interesting sound merely because an
    # unverified question-start marker says the loudspeaker should be playing.
    signal = scan(folder, mtc["wav_segments"], question_alignment=False,
                  delta_db=delta_db, floor_dbfs=floor_dbfs)
    boundaries = _offsets(mtc["wav_segments"])
    plausible = mtc["events"]["alignment"].startswith("MARKER_OFFSETS_")
    windows = mtc["events"]["question_windows_seconds"]
    candidates = []
    for i, candidate in enumerate(signal["candidates"], 1):
        info = boundaries.get(candidate["origin_file"])
        if not info:
            continue
        local_start = max(0, candidate["start_seconds"] - info["offset"])
        local_end = min(info["duration"], candidate["end_seconds"] - info["offset"])
        if local_end <= local_start:
            continue
        overlap = _overlaps(candidate["start_seconds"], candidate["end_seconds"], windows) if plausible else None
        candidates.append({**candidate, "id": f"VEIL-C{i:04d}",
                           "file_start_seconds": round(local_start, 3),
                           "file_end_seconds": round(local_end, 3),
                           "possibly_near_question_marker": overlap,
                           "question_timing_corroborated_by_audio": False,
                           "human_label": "UNREVIEWED", "human_notes": ""})
    source_hashes = inventory(folder, mtc["wav_segments"])
    seams = survey(folder, mtc["wav_segments"])
    return {"schema": SCHEMA, "analysis_status": "PRELIMINARY_HUMAN_REVIEW_REQUIRED",
            "read_only_sources": True, "offline": True, "evidence_modified": False,
            "audio_classification": "AMPLITUDE_CHANGE_ONLY_NOT_SPEECH_OR_EVP",
            "mtc": mtc, "signal": {**signal, "candidates": candidates, "candidate_count": len(candidates)},
            "inventory": source_hashes, "seams": seams, "derived_clips": [],
            "segment_global_offsets_are_assumed": True,
            "blind_review_recommended": True,
            "warnings": [*signal["warnings"], *source_hashes["issues"]],
            "interpretation": ("Candidates are unclassified sound-level changes. Question markers are "
                               "unverified; overlapping events are RETAINED, not deleted. "
                               "Session-relative offsets assume contiguous segments without proof. "
                               "SHA-256 hashes only inventory bytes at review time, and do not "
                               "establish authenticity, custody, cause, or paranormal activity.")}


def _verify_dest(folder: Path, output: Path):
    source = folder.resolve(strict=True)
    if folder.is_symlink():
        raise ValueError("Refusing symbolic-link evidence directory")
    dest = output.resolve(strict=False)
    if dest == source or source in dest.parents:
        raise ValueError("Output must be outside original evidence directory")
    if dest.exists() or dest.is_symlink():
        raise FileExistsError("Output directory exists; refuse overwrite")
    if not dest.parent.is_dir() or dest.parent.is_symlink():
        raise ValueError("Output parent must already be a normal directory")
    return dest


def _extract(source: Path, wav_info, candidate, clip: Path, padding_seconds: float):
    if not _safe_regular(source):
        raise ValueError("Unsafe source WAV")
    if wav_info["channels"] not in (1, 2) or wav_info["sample_width_bytes"] != 2 or wav_info["format"] != "NONE":
        raise ValueError("Only 16-bit mono/stereo PCM clip extraction supported")
    with wave.open(str(source), "rb") as stream:
        if (stream.getframerate() != wav_info["sample_rate_hz"] or
            stream.getnframes() != wav_info["frames"] or
            stream.getnchannels() != wav_info["channels"] or
            stream.getsampwidth() != 2 or stream.getcomptype() != "NONE"):
            raise ValueError("WAV header changed since scan")
        rate = stream.getframerate()
        start = max(0.0, candidate["file_start_seconds"] - padding_seconds)
        # Cap the *entire* clip duration (including padding), preserving onset.
        end = min(wav_info["duration_seconds"],
                  max(start, candidate["file_end_seconds"] + padding_seconds),
                  start + MAX_CLIP_SECONDS)
        first = min(stream.getnframes(), int(start * rate))
        last = min(stream.getnframes(), max(first + 1, int(end * rate)))
        stream.setpos(first)
        frames = stream.readframes(last-first)
        if len(frames) != (last-first) * stream.getnchannels() * stream.getsampwidth():
            raise ValueError("Incomplete WAV read")
        with wave.open(str(clip), "wb") as out:
            out.setnchannels(stream.getnchannels())
            out.setsampwidth(stream.getsampwidth())
            out.setframerate(rate)
            out.writeframes(frames)
    return {"clip_file": str(clip.name), "candidate_id": candidate["id"],
            "source_file": source.name, "source_file_start_seconds": round(first/rate,3),
            "source_file_end_seconds": round(last/rate,3),
            "clip_duration_seconds": round((last-first)/rate, 3),
            "clip_is_derived_not_original": True, "sha256": _sha256_file(clip).get("sha256")}


def write_pack(folder: str | Path, output: str | Path, *, make_clips=False,
               max_clips=20, padding_seconds=2.0):
    folder = Path(folder)
    target = _verify_dest(folder, Path(output))
    if not 0 <= max_clips <= MAX_CLIPS or not 0 <= padding_seconds <= 5:
        raise ValueError("Invalid clip count or padding")
    pack = build_pack(folder)
    # If the event/WAV sources are damaged or changed, do not generate excerpts.
    if make_clips and (pack["inventory"]["issues"] or pack["signal"]["warnings"]):
        raise ValueError("Source inventory/scan has warnings; refusing clip extraction")
    target.mkdir()  # fails closed if someone else created the target in the meantime
    if make_clips:
        clips_dir = target / "clips"
        clips_dir.mkdir()
        wavs = {row["file"]: row for row in pack["mtc"]["wav_segments"]}
        for c in pack["signal"]["candidates"][:max_clips]:
            if c["origin_file"] not in wavs:
                continue
            clip_path = clips_dir / f'{c["id"]}.wav'
            pack["derived_clips"].append(_extract(folder / c["origin_file"],
                                                      wavs[c["origin_file"]], c,
                                                      clip_path, padding_seconds))
    post_inventory = inventory(folder, pack["mtc"]["wav_segments"])
    if post_inventory != pack["inventory"]:
        raise ValueError("Source inventory changed during derived review; output incomplete, reject and investigate")
    (target / "review.json").write_text(json.dumps(pack, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    with (target / "candidate_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["candidate_id", "source_file", "file_start_seconds", "file_end_seconds",
                         "assumed_session_start_seconds", "possibly_near_unverified_question_marker",
                         "human_classification", "reviewer_notes", "second_reviewer_notes"])
        for c in pack["signal"]["candidates"]:
            writer.writerow([c["id"], c["origin_file"], c["file_start_seconds"],
                             c["file_end_seconds"], c["start_seconds"],
                             c["possibly_near_question_marker"], "UNREVIEWED", "", ""])
    return pack


def main(argv=None):
    p = argparse.ArgumentParser(description="VEIL offline SIGNAL review pack (no live capture)")
    p.add_argument("session_dir", help="COMPLETED session folder or verified copy")
    p.add_argument("output_dir", help="new, nonexistent directory OUTSIDE original session")
    p.add_argument("--clips", action="store_true", help="opt in to derived WAV excerpts")
    p.add_argument("--max-clips", type=int, default=20)
    p.add_argument("--padding-seconds", type=float, default=2.0)
    a = p.parse_args(argv)
    result = write_pack(a.session_dir, a.output_dir, make_clips=a.clips,
                        max_clips=a.max_clips, padding_seconds=a.padding_seconds)
    print(json.dumps({"report_created": True, "candidates": result["signal"]["candidate_count"],
                      "derived_clips": len(result["derived_clips"]),
                      "interpretation": "For human review only; never proof of EVP"}))

if __name__ == "__main__":
    main()
