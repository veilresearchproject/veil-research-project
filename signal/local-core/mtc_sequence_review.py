"""Deterministic, read-only review of SYNTHETIC MTC event markers.

No file access, audio capture, live hardware, network calls, model inference, or
instrument control. The caller supplies CSV bytes; this cannot verify whether
any sound was actually recorded or whether a paranormal event occurred.
"""
import csv
from datetime import datetime, timezone
import io

import synthetic_evidence


def review_synthetic_mtc(raw, *, expected_sha256=None):
    """Check per-recorder RECORDING and QUESTION marker order in synthetic CSV.

    Returns structured warnings, not corrected data or scientific conclusions.
    Strict input/schema/hash checks are delegated to inspect_synthetic.
    """
    intake = synthetic_evidence.inspect_synthetic(
        raw, 'mtc_markers', expected_sha256=expected_sha256)
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''))
    states = {}
    findings = []
    completed_questions = 0

    def flag(code, recorder, row):
        findings.append({'code': code, 'recorder_id': recorder, 'row': row})

    for row_no, event in enumerate(reader, 1):
        recorder = event['recorder_id']
        marker = event['marker']
        when = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        when = when.astimezone(timezone.utc)
        state = states.setdefault(recorder, {
            'recording': False, 'question': False, 'last_timestamp': None,
            'last_row': None, 'questions_completed': 0,
        })
        if state['last_timestamp'] is not None and when <= state['last_timestamp']:
            flag('NON_INCREASING_TIMESTAMP', recorder, row_no)
        state['last_timestamp'] = when
        state['last_row'] = row_no

        if marker == 'RECORDING_START':
            if state['recording']:
                flag('DUPLICATE_RECORDING_START', recorder, row_no)
            else:
                state['recording'] = True
        elif marker == 'RECORDING_END':
            if not state['recording']:
                flag('RECORDING_END_WITHOUT_START', recorder, row_no)
            else:
                if state['question']:
                    flag('RECORDING_END_WITH_QUESTION_OPEN', recorder, row_no)
                    state['question'] = False
                state['recording'] = False
        elif marker == 'QUESTION_START':
            if not state['recording']:
                flag('QUESTION_OUTSIDE_RECORDING', recorder, row_no)
            elif state['question']:
                flag('DUPLICATE_QUESTION_START', recorder, row_no)
            else:
                state['question'] = True
        elif marker == 'QUESTION_END':
            if not state['question']:
                flag('QUESTION_END_WITHOUT_START', recorder, row_no)
            else:
                state['question'] = False
                state['questions_completed'] += 1
                completed_questions += 1

    for recorder, state in sorted(states.items()):
        if state['question']:
            flag('UNCLOSED_QUESTION', recorder, state['last_row'])
        if state['recording']:
            flag('UNCLOSED_RECORDING', recorder, state['last_row'])

    return {
        'schema': 'signal.synthetic-mtc-sequence.0.1',
        'source_type': 'SYNTHETIC_ONLY',
        'sha256': intake['sha256'],
        'rows': intake['rows'],
        'recorders': {recorder: {'questions_completed': state['questions_completed']}
                      for recorder, state in sorted(states.items())},
        'questions_completed': completed_questions,
        'findings': findings,
        'finding_count': len(findings),
        'valid_marker_sequence': not findings,
        'live_instrument_connection': False,
        'audio_examined': False,
        'model_inference': False,
        'scientific_cause_determined': False,
        'limitation': ('Synthetic marker sequencing only. Does not establish acoustic '
                       'capture, device synchronization, evidence provenance, or cause.'),
    }
