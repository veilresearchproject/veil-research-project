import hashlib
import unittest
from datetime import timedelta
from evidence_v04 import (
    validate_protocol, validate_source_registry, normalize_timeline, screen_candidates,
    group_candidate_windows, compare_test_control, prepare_blind_queue,
    add_human_review, resolve_reviews, render_lab_readout,
)

PLAN = dict(protocol_id='SYNTHETIC_001', mode='SYNTHETIC_SIMULATION',
    hypothesis='Flags may differ between windows', null_hypothesis='No difference',
    primary_outcome='Flag count', control_description='Matched synthetic controls',
    analysis_plan='Compare counts per unit time', blinding_plan='Mask conditions',
    consent_plan='No participants')
SOURCES = [dict(device_id='AUDIO_SIM', modality='audio', clock_offset_ms=150,
                clock_uncertainty_ms=25),
           dict(device_id='THERMAL_SIM', modality='thermal', clock_offset_ms=0,
                clock_uncertainty_ms=35)]


def event(event_id='e1', device='AUDIO_SIM', when='2026-01-01T00:00:01Z', value=90,
          channel='sound_db', condition='test'):
    return dict(event_id=event_id, device_id=device, timestamp_utc=when,
                channel=channel, observed_value=value, condition=condition)


class ResearchV04Tests(unittest.TestCase):
    def setUp(self):
        self.registry = validate_source_registry(SOURCES)
        self.events = normalize_timeline([event(), event('e2', 'THERMAL_SIM',
                                      '2026-01-01T00:00:01Z', 30, 'temperature_c', 'control')],
                                         self.registry)
        self.candidates = screen_candidates(self.events,
                {'sound_db':(0,65),'temperature_c':(18,26)})

    def test_17_protocol_explicit_controls(self):
        self.assertTrue(validate_protocol(PLAN)['has_null_hypothesis'])
        self.assertIn('NOT PREREGISTERED', validate_protocol(PLAN)['status'])
        with self.assertRaises(ValueError): validate_protocol({**PLAN,'null_hypothesis':''})
        with self.assertRaises(ValueError): validate_protocol({**PLAN,'mode':'REAL'})

    def test_18_registry_rejects_duplicates_or_invalid_uncertainty(self):
        self.assertEqual(len(self.registry),2)
        with self.assertRaises(ValueError): validate_source_registry([SOURCES[0], SOURCES[0]])
        with self.assertRaises(ValueError): validate_source_registry([{**SOURCES[0], 'clock_uncertainty_ms':-1}])

    def test_19_utc_offset_correction_and_duplicate_ids(self):
        first = next(e for e in self.events if e['event_id']=='e1')
        self.assertEqual(first['utc'].isoformat(), '2026-01-01T00:00:00.850000+00:00')
        self.assertEqual((first['latest']-first['earliest']),timedelta(milliseconds=50))
        with self.assertRaises(ValueError): normalize_timeline([event(),event()],self.registry)
        with self.assertRaises(ValueError): normalize_timeline([event(when='2026-01-01T00:00:01')],self.registry)

    def test_20_candidates_not_paranormal_verdicts(self):
        self.assertEqual(len(self.candidates),2)
        self.assertTrue(all(x['cause']=='UNKNOWN' for x in self.candidates))
        with self.assertRaises(ValueError): screen_candidates(self.events, {'sound_db':(65,0)})

    def test_21_windows_cross_device_not_causal(self):
        groups = group_candidate_windows(self.candidates, tolerance_ms=200)
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]['distinct_devices'],2)
        self.assertTrue(groups[0]['cross_device_cooccurrence'])
        self.assertIn('NOT CAUSAL',groups[0]['finding'])
        with self.assertRaises(ValueError):group_candidate_windows(self.candidates,tolerance_ms=-1)

    def test_22_rates_handle_zero_control(self):
        rates = compare_test_control(self.candidates,{'test':120,'control':240})
        self.assertEqual(rates['test']['count'],1)
        self.assertEqual(rates['control']['count'],1)
        self.assertEqual(rates['rate_ratio'],2)
        no_control = compare_test_control(self.candidates[:1],{'test':120,'control':240})
        self.assertIsNone(no_control['rate_ratio']) if no_control['control']['count']==0 else None
        with self.assertRaises(ValueError):compare_test_control(self.candidates,{'test':0,'control':10})

    def test_23_blind_packet_omits_conditions_and_timestamps(self):
        packet = prepare_blind_queue(self.candidates,secret='test-secret-that-is-not-production')
        self.assertEqual(len(packet['reviewer_packet']),2)
        reviewer_text = str(packet['reviewer_packet'])
        self.assertNotIn('test',reviewer_text.lower())
        self.assertNotIn('2026-',reviewer_text)
        self.assertNotIn('AUDIO_SIM',reviewer_text)
        self.assertEqual(len(packet['custodian_key']),2)
        with self.assertRaises(ValueError):prepare_blind_queue(self.candidates,secret='short')

    def test_24_human_reviewer_duplicate_rejected(self):
        a=add_human_review([], review_id='review-a',reviewer_id='person-one',
                           decision='uncertain',explanation='Insufficient context')
        self.assertEqual(len(a),1)
        with self.assertRaises(ValueError):add_human_review(a, review_id='review-a',
            reviewer_id='person-one',decision='ordinary',explanation='changed')
        with self.assertRaises(ValueError):add_human_review([],review_id='r',reviewer_id='p',
            decision='proven_ghost',explanation='invalid')

    def test_25_disagreement_preserved(self):
        records=[]
        for name,decision in [('alpha','ordinary'),('beta','uncertain')]:
            records=add_human_review(records, review_id='review-case',reviewer_id=name,
                                     decision=decision,explanation='Documented separately')
        status=resolve_reviews(['review-case'],records)[0]
        self.assertIn('DISAGREEMENT',status['status'])
        self.assertEqual(status['reviewer_count'],2)
        self.assertIn('PENDING',resolve_reviews(['review-case'],[])[0]['status'])

    def test_26_escaped_offline_html_and_digest(self):
        p=validate_protocol({**PLAN,'protocol_id':'safe_id'})
        pkt=prepare_blind_queue(self.candidates,secret='test-secret-that-is-not-production')
        decisions=resolve_reviews([x['review_id'] for x in pkt['reviewer_packet']],[])
        html=render_lab_readout(p,self.registry,self.candidates,[],
            compare_test_control(self.candidates,{'test':120,'control':240}),decisions,
            csv_sha256=hashlib.sha256(b'synthetic').hexdigest())
        self.assertIn('SIMULATED ONLY',html)
        self.assertNotIn('<script',html)
        self.assertNotIn('AUDIO_SIM',html)
        with self.assertRaises(ValueError):render_lab_readout(p,self.registry,self.candidates,[],
            compare_test_control(self.candidates,{'test':120,'control':240}),decisions,
            csv_sha256='not-a-hash')

    def test_26_report_escapes_untrusted_ids(self):
        data=dict(id='<script>alert(1)</script>',status='ILLUSTRATIVE')
        html=render_lab_readout(data,self.registry,[],[],
            compare_test_control([],{'test':120,'control':240}),[], csv_sha256='f'*64)
        self.assertIn('&lt;script&gt;',html)
        self.assertNotIn('<script>',html)


if __name__ == '__main__':
    unittest.main(verbosity=2)