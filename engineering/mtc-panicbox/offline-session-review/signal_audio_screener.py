"""Standard-library-only offline audio change screener. No speech/EVP recognition.

Reads 16-bit PCM WAV files without changing originals. Time offsets of sequential
segments are an *analysis assumption*, not proof that their physical capture was
continuous. Review candidates are amplitude changes, NOT anomalous voices.
"""
from __future__ import annotations
import array
import math
import statistics
import sys
import wave
from collections import deque
from pathlib import Path


def _dbfs(rms):
    return 20.0*math.log10(max(rms, 1.0 / 32768.0))


def _overlaps(a, b, question_windows, padding):
    return any(a <= qend+padding and b >= qstart-padding for qstart,qend in question_windows)


def scan(folder, wavs, *, question_windows=None, question_alignment=False,
         window_seconds=0.25, delta_db=12.0, floor_dbfs=-45.0, max_candidates=250):
    if not 0.05 <= window_seconds <= 2.0:
        raise ValueError('window_seconds out of range')
    if not 3 <= delta_db <= 50 or not -90 <= floor_dbfs <= -5:
        raise ValueError('unreasonable detection thresholds')
    source = Path(folder)
    candidates=[]
    warnings=[]
    offset=0.0
    recent=deque(maxlen=max(8, round(8/window_seconds)))
    run=None
    prompt_suppressed=0
    frames_examined=0
    question_windows = question_windows or []

    def finish_run():
        nonlocal run
        if run is not None:
            if len(candidates) < max_candidates:
                candidates.append(run)
            run = None

    for summary in wavs:
        path=source/summary['file']
        if path.is_symlink() or not path.is_file():
            warnings.append({'code':'AUDIO_FILE_UNSAFE_OR_MISSING','file':summary['file']})
            break
        if summary['format']!='NONE' or summary['sample_width_bytes']!=2 or summary['channels'] not in (1,2):
            warnings.append({'code':'UNSUPPORTED_PCM','file':summary['file']})
            break
        before=path.stat()
        try:
            with wave.open(str(path),'rb') as wav:
                rate=wav.getframerate()
                frames_per_window=max(1,round(rate*window_seconds))
                position=0
                while True:
                    data=wav.readframes(frames_per_window)
                    if not data:
                        break
                    if len(data)%2:
                        warnings.append({'code':'TRUNCATED_PCM_SAMPLE','file':summary['file']})
                        break
                    nums=array.array('h')
                    nums.frombytes(data)
                    if sys.byteorder!='little':
                        nums.byteswap()
                    if not nums:
                        break
                    mean_square=sum(v*v for v in nums)/len(nums)
                    rms=(mean_square**0.5)/32768.0
                    level=_dbfs(rms)
                    peak=max(abs(v) for v in nums)/32768.0
                    clipped=sum(1 for v in nums if abs(v)>=32760)/len(nums)
                    seconds=len(nums)/(wav.getnchannels()*rate)
                    start=offset + position/rate
                    end=start+seconds
                    position += len(nums)//wav.getnchannels()
                    frames_examined += len(nums)//wav.getnchannels()
                    baseline=statistics.median(recent) if len(recent)>=4 else None
                    is_new_sound = (baseline is not None and level>=floor_dbfs
                                    and level-baseline>=delta_db)
                    if question_alignment and _overlaps(start,end,question_windows,2.0):
                        if is_new_sound:
                            prompt_suppressed+=1
                        finish_run()
                    elif is_new_sound:
                        if run is None:
                            run={'start_seconds':round(start,3), 'end_seconds':round(end,3),
                                 'kind':'SOUND_LEVEL_CHANGE', 'max_dbfs':round(level,1),
                                 'peak_relative':round(peak,4), 'max_clipped_fraction':round(clipped,4),
                                 'origin_file':summary['file'], 'requires_human_review':True}
                        else:
                            run['end_seconds']=round(end,3)
                            run['max_dbfs']=max(run['max_dbfs'],round(level,1))
                            run['peak_relative']=max(run['peak_relative'],round(peak,4))
                            run['max_clipped_fraction']=max(run['max_clipped_fraction'],round(clipped,4))
                    else:
                        finish_run()
                    # Filter large transients out of rolling quiet-room reference.
                    if not is_new_sound and not (question_alignment and _overlaps(start,end,question_windows,2.0)):
                        recent.append(level)
            if position != wav.getnframes():
                warnings.append({'code':'WAV_READ_FRAME_COUNT_DIFFERS_FROM_HEADER',
                                 'file':summary['file'], 'declared_frames':wav.getnframes(),
                                 'read_frames':position})
            after=path.stat()
            if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
                warnings.append({'code':'WAV_CHANGED_DURING_SCREENING','file':summary['file']})
        except (OSError,EOFError,wave.Error,ValueError) as err:
            warnings.append({'code':'AUDIO_SCAN_FAILED','file':summary['file'], 'reason':type(err).__name__})
            break
        finish_run()
        recent.clear()  # never learn prior segment background as if continuous evidence
        offset+=summary['duration_seconds']
    if len(candidates)>=max_candidates:
        warnings.append({'code':'CANDIDATE_LIMIT_REACHED', 'limit':max_candidates})
    return {'schema':'veil.signal-audio-screen.v0.1', 'audio_analysis':'LEVEL_CHANGES_ONLY',
            'offline':True, 'read_only':True, 'speech_recognition_performed':False,
            'evp_classification_performed':False, 'source_audio_modified':False,
            'question_masking_used':bool(question_alignment and question_windows),
            'question_windows_from_unverified_log_markers':bool(question_alignment and question_windows),
            'question_related_windows_suppressed':prompt_suppressed,
            'candidate_count':len(candidates), 'candidates':candidates,
            'frames_examined':frames_examined, 'warnings':warnings,
            'limitations': ('Only loudness deviations from a recent baseline are flagged. '
                            'Quiet speech can be missed; ordinary noises and equipment sounds can be flagged. '
                            'No evidence of EVP or paranormal origin. Segment offsets are not proof of continuity.')}
