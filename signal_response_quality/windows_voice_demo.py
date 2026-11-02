"""Opt-in demonstration of SIGNAL's offline speech pipeline.

Dry run uses a fake blocking speaker; real Windows SAPI playback requires
--live-windows and an existing pywin32 installation. No network or recordings.
"""
import argparse
from voice_pipeline import VoicePipeline
from playback_adapter import play_remaining
from windows_speech import speak_windows_blocking

SAMPLE = 'Hello. I am SIGNAL, a prototype assistant for the VEIL Research Project. I am ready to help document evidence carefully.'

def run(text: str = SAMPLE, *, live_windows: bool = False, max_chars: int = 80):
    pipeline = VoicePipeline(text, max_chars=max_chars)
    delivered = []
    def dry_speaker(chunk):
        delivered.append(chunk)
        return True  # simulation only; not proof of audible output
    speaker = speak_windows_blocking if live_windows else dry_speaker
    result = play_remaining(pipeline, speaker)
    return result, pipeline, tuple(delivered)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-windows', action='store_true', help='Opt in to actual SAPI speech output')
    parser.add_argument('--text', default=SAMPLE)
    args = parser.parse_args()
    result, pipeline, delivered = run(args.text, live_windows=args.live_windows)
    print('Mode:', 'Windows SAPI' if args.live_windows else 'dry run (no audio)')
    print('Chunks:', len(pipeline.plan.chunks), 'Completed:', result.completed, 'Played this run:', result.played_now)
    if not args.live_windows:
        print('Simulated delivery matches:', ' '.join(delivered) == pipeline.plan.original)
    if not result.completed: raise SystemExit(1)

if __name__ == '__main__': main()
