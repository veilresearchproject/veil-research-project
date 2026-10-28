"""Deterministic, fully offline MTC/SIGNAL *synthetic* audio screener evaluation.

No capture or production recorder integration. Generated sine and PCM waves are
NOT speech samples, EVP examples or a scientifically representative dataset.
No remote access, network, changes to source files or field evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
import tempfile
import wave
from pathlib import Path
from signal_audio_screener import scan

SCHEMA = 'veil.signal-synthetic-benchmark.v0.1'
PROFILES = {
    'silence': 'NEGATIVE',
    'quiet_hum': 'NEGATIVE',
    'steady_hum': 'NEGATIVE',
    'hard_tone': 'CLEAR_SOUND',
    'short_impact': 'CLEAR_SOUND',
    'two_impacts': 'CLEAR_SOUND',
    'faint_tone': 'EXPLORATORY',
    'slow_ramp': 'EXPLORATORY',
    'mic_dropout': 'NOT_TESTABLE_BY_LEVEL_RISE',
}
DURATION = 5.0
ONSET = 2.0


def _clip(value):
    return max(-32768, min(32767, int(round(value))))


def generate_wav(path: Path, profile: str, rate: int, channels: int, seed: int):
    """Five-second PCM test audio with known synthetic perturbations.

    Intentionally uses very simple tones; it is not a speech recognizer benchmark.
    16-bit little-endian mono/stereo. Generates samples in memory only for one
    short disposable test WAV at a time.
    """
    if profile not in PROFILES or rate not in (8000, 16000) or channels not in (1, 2):
        raise ValueError('unsupported synthetic test profile/rate/channels')
    rng = random.Random(seed)
    raw = bytearray()
    total = round(DURATION * rate)
    for i in range(total):
        t = i / rate
        # Deterministic baseline, representative ONLY of synthetic audio.
        baseline = 0.0
        if profile in ('quiet_hum', 'steady_hum', 'hard_tone', 'short_impact',
                       'two_impacts', 'faint_tone', 'slow_ramp', 'mic_dropout'):
            baseline = 60.0*math.sin(2*math.pi*120*t) + rng.randrange(-24, 25)
        if profile == 'steady_hum':
            baseline = 800.0 * math.sin(2*math.pi*100*t) + rng.randrange(-30, 31)
        if profile == 'mic_dropout' and 2.0 <= t < 3.5:
            baseline = 0.0
        if profile in ('hard_tone','faint_tone','slow_ramp'):
            amp = 0.0
            if profile == 'hard_tone' and ONSET <= t < 2.75: amp = 9000
            if profile == 'faint_tone' and ONSET <= t < 2.75: amp = 100
            if profile == 'slow_ramp' and ONSET <= t < 3.0: amp = 8000*(t-ONSET)
            baseline += amp*math.sin(2*math.pi*360*t)
        if profile in ('short_impact','two_impacts'):
            strikes = (2.0,) if profile == 'short_impact' else (2.0,2.75)
            for strike in strikes:
                if strike <= t < strike+0.06:
                    baseline += 16000*math.exp(-50*(t-strike))*math.sin(2*math.pi*420*t)
        # Deliberately put synthetic sound on only one channel for stereo cases.
        for channel in range(channels):
            v = baseline
            if channels == 2 and channel == 1 and profile in ('hard_tone','short_impact','two_impacts'):
                v = 0.0
            raw += _clip(v).to_bytes(2, 'little', signed=True)
    with wave.open(str(path),'wb') as out:
        out.setnchannels(channels)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(raw)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _intersects(candidate, onset=ONSET, tail=3.0):
    return candidate['end_seconds'] >= onset and candidate['start_seconds'] <= tail


def measure(*, seeds=2):
    """Compute event hit rates for obvious TEST TONES; no threshold tuning."""
    if type(seeds) is not int or not 1 <= seeds <= 10:
        raise ValueError('seeds must be integer 1..10')
    rows = []
    with tempfile.TemporaryDirectory(prefix='veil-signal-benchmark-') as td:
        folder = Path(td)
        for profile, category in PROFILES.items():
            for rate, channels in ((8000,1),(16000,2)):
                for seed in range(seeds):
                    path = folder/'room_mic_continuous.wav'
                    before_hash = generate_wav(path, profile, rate, channels, seed)
                    wavs=[{'file':path.name,'channels':channels,'sample_width_bytes':2,
                           'sample_rate_hz':rate, 'frames':round(DURATION*rate),
                           'duration_seconds':DURATION,'format':'NONE','segment_number':1}]
                    result = scan(folder, wavs, question_alignment=False)
                    after_hash=hashlib.sha256(path.read_bytes()).hexdigest()
                    if before_hash != after_hash:
                        raise AssertionError('Input synthetic WAV was changed by scan')
                    if result['warnings']:
                        raise AssertionError(f'Unexpected screener warning: {result["warnings"]}')
                    hits=sum(1 for c in result['candidates'] if _intersects(c))
                    rows.append({'profile':profile, 'category':category,
                                 'sample_rate_hz':rate,'channels':channels,'seed':seed,
                                 'candidate_count':result['candidate_count'],
                                 'hit':hits>0, 'frames_examined':result['frames_examined'],
                                 'synthetic_sha256':before_hash})
                    path.unlink()
    strong=[r for r in rows if r['category']=='CLEAR_SOUND']
    negatives=[r for r in rows if r['category']=='NEGATIVE']
    uncertain=[r for r in rows if r['category'] in ('EXPLORATORY','NOT_TESTABLE_BY_LEVEL_RISE')]
    false_alerts=sum(r['candidate_count'] for r in negatives)
    # This is only a synthetic benchmark: there are no true EVP labels.
    return {'schema':SCHEMA, 'synthetic_only':True, 'source_evidence_processed':False,
            'model_inference_performed':False, 'cases':len(rows), 'test_clip_seconds':DURATION,
            'fixed_thresholds':{'delta_db':12.0,'floor_dbfs':-45.0,'window_seconds':0.25},
            'clear_sound_cases':len(strong),
            'clear_sound_hit_count':sum(r['hit'] for r in strong),
            'clear_sound_hit_rate':round(sum(r['hit'] for r in strong)/len(strong),3),
            'negative_cases':len(negatives),
            'negative_candidate_count':false_alerts,
            'negative_candidate_rate_per_minute':round(false_alerts / (len(negatives)*DURATION/60),3),
            'exploratory_cases':len(uncertain),
            'exploratory_hits':sum(r['hit'] for r in uncertain),
            'per_profile':[{'profile':p,'category':cat,'cases':sum(r['profile']==p for r in rows),
                            'hits':sum(r['hit'] for r in rows if r['profile']==p),
                            'candidates':sum(r['candidate_count'] for r in rows if r['profile']==p)}
                           for p,cat in PROFILES.items()],
            'rows':rows,
            'limitations': ('Artificial short tones and simple deterministic background only. '
                            'Clear-sound hit rate is not sensitivity to EVP, speech, whispers, '
                            'real microphone failure, or paranormal events. Negative case '
                            'alerts are not a field false-positive rate. Real acoustic '
                            'recordings and blinded human labeling are required.')}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', type=int, default=2)
    parser.add_argument('--output', type=Path, help='New, nonexisting result file outside raw evidence')
    args=parser.parse_args(argv)
    report=measure(seeds=args.seeds)
    if args.output:
        if args.output.exists():
            parser.error('Output already exists; cannot overwrite')
        if not args.output.parent.is_dir():
            parser.error('Output parent must already exist')
        args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('cases','clear_sound_cases','clear_sound_hit_count',
          'negative_cases','negative_candidate_count','exploratory_cases','exploratory_hits')}))

if __name__ == '__main__':
    main()
