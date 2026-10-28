"""Read-only synthetic/field WAV seam *heuristics*, not continuity verification.

Compares brief PCM slices on either side of file boundaries. It cannot detect
omitted samples, paused microphones, offset clocks, or validated time sync.
"""
from __future__ import annotations
import array
import math
import sys
import wave
from pathlib import Path


def _rms_db(raw: bytes) -> float:
    samples = array.array('h')
    samples.frombytes(raw)
    if sys.byteorder != 'little':
        samples.byteswap()
    if not samples:
        return -100.0
    rms = (sum(x*x for x in samples)/len(samples))**0.5 / 32768.0
    return round(20 * math.log10(max(rms, 1e-5)), 2)


def _edge(path: Path, *, last: bool, seconds: float):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Unsafe WAV path')
    with wave.open(str(path), 'rb') as w:
        if w.getsampwidth() != 2 or w.getnchannels() not in (1,2) or w.getcomptype() != 'NONE':
            raise ValueError('Unsupported PCM')
        n = max(1,min(w.getnframes(),int(w.getframerate()*seconds)))
        if last:
            w.setpos(w.getnframes()-n)
        raw = w.readframes(n)
        if len(raw) != n*w.getnchannels()*2:
            raise ValueError('Truncated edge read')
        return {"dbfs": _rms_db(raw), "frames": n,
                "sample_rate_hz": w.getframerate(), "channels": w.getnchannels()}


def survey(folder: str | Path, wavs, *, edge_seconds=0.25, jump_db=18.0):
    if not 0.05 <= edge_seconds <= 1.0 or not 6 <= jump_db <= 50:
        raise ValueError('Invalid seam thresholds')
    source = Path(folder)
    rows=[]
    for left,right in zip(wavs, wavs[1:]):
        entry={"left_file": left['file'], "right_file": right['file'],
               "physical_continuity": "UNVERIFIED", "issues": []}
        if right['segment_number'] != left['segment_number'] + 1:
            entry['issues'].append('NON_ADJACENT_SEGMENT_NUMBERS_NO_COMPARISON')
            rows.append(entry)
            continue
        if (left['sample_rate_hz'], left['channels'], left['sample_width_bytes'], left['format']) != (right['sample_rate_hz'], right['channels'], right['sample_width_bytes'], right['format']):
            entry['issues'].append('INCOMPATIBLE_BOUNDARY_FORMAT')
            rows.append(entry)
            continue
        try:
            a=_edge(source/left['file'], last=True, seconds=edge_seconds)
            b=_edge(source/right['file'], last=False, seconds=edge_seconds)
            entry['left_edge_dbfs']=a['dbfs']
            entry['right_edge_dbfs']=b['dbfs']
            entry['difference_db']=round(b['dbfs']-a['dbfs'],2)
            if abs(entry['difference_db']) >= jump_db:
                entry['issues'].append('LARGE_EDGE_LEVEL_DIFFERENCE_REVIEW')
            if a['dbfs'] < -58 or b['dbfs'] < -58:
                entry['issues'].append('NEAR_SILENT_BOUNDARY_EDGE_REVIEW')
        except (OSError,ValueError,wave.Error,EOFError) as err:
            entry['issues'].append('BOUNDARY_UNREADABLE_'+type(err).__name__.upper())
        rows.append(entry)
    return {"analysis": "WAV_EDGE_LOUDNESS_HEURISTIC_ONLY", "boundaries_examined": len(rows),
            "boundaries": rows, "proves_gapless_recording": False,
            "limitations": "Even matching edge levels cannot prove time continuity, no lost frames, microphone activity, or acoustic events. Level changes may be ordinary room sounds. Check seam timing against independently synchronized audio/video and listen around the seam."}
