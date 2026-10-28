"""Command-line, no-install, offline MTC / SIGNAL completed-session reviewer."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from session_validator import review
from signal_audio_screener import scan


def main(argv=None):
    parser=argparse.ArgumentParser(description='Read-only offline MTC session + SIGNAL level-change review')
    parser.add_argument('session_dir', help='completed MTC session folder (do not use a live recording)')
    parser.add_argument('--output', help='optional JSON report path OUTSIDE the session evidence folder')
    parser.add_argument('--skip-audio',action='store_true',help='metadata and WAV header checks only')
    opts=parser.parse_args(argv)
    folder=Path(opts.session_dir).resolve(strict=True)
    if opts.output:
        out=Path(opts.output).resolve()
        if out == folder or folder in out.parents:
            parser.error('report destination must be OUTSIDE session evidence folder')
        if out.exists():
            parser.error('report destination already exists; refusal to overwrite')
    report=review(folder)
    if not opts.skip_audio:
        data=report['events']
        report['signal_audio_screener']=scan(folder,report['wav_segments'],
                  question_windows=data['question_windows_seconds'],
                  question_alignment=data['alignment'].startswith('MARKER_OFFSETS_'))
        if report['signal_audio_screener']['warnings']:
            report['structure_status']='REVIEW_REQUIRED'
    payload=json.dumps(report,indent=2,sort_keys=True)
    if opts.output:
        out.write_text(payload+'\n',encoding='utf-8')
        print(f'Read-only review saved to {out.name}; sources were not altered.')
    else:
        print(payload)

if __name__=='__main__':
    main()
