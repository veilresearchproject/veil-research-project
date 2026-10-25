"""Run: python -m unittest -v test_mtc_sequence_review.py"""
import hashlib
import unittest

from mtc_sequence_review import review_synthetic_mtc


HEADER = 'timestamp,recorder_id,marker\n'

def fixture(*records):
    lines = [f'2026-10-22T08:{i:02d}:00Z,{recorder},{marker}'
             for i, (recorder, marker) in enumerate(records)]
    return (HEADER + '\n'.join(lines) + '\n').encode('ascii')


def codes(raw):
    return [item['code'] for item in review_synthetic_mtc(raw)['findings']]


class MTCSequenceTests(unittest.TestCase):
    def test_valid_independent_recorders(self):
        raw = fixture(('A', 'RECORDING_START'), ('B', 'RECORDING_START'),
                      ('A', 'QUESTION_START'), ('A', 'QUESTION_END'),
                      ('B', 'RECORDING_END'), ('A', 'RECORDING_END'))
        result = review_synthetic_mtc(raw)
        self.assertTrue(result['valid_marker_sequence'])
        self.assertEqual(result['questions_completed'], 1)
        self.assertEqual(result['recorders']['B']['questions_completed'], 0)
        self.assertFalse(result['audio_examined'])
        self.assertFalse(result['live_instrument_connection'])

    def test_question_outside_recording(self):
        self.assertIn('QUESTION_OUTSIDE_RECORDING', codes(fixture(('A', 'QUESTION_START'))))

    def test_question_end_without_start(self):
        self.assertIn('QUESTION_END_WITHOUT_START', codes(fixture(('A', 'RECORDING_START'),
                                                                ('A', 'QUESTION_END'), ('A', 'RECORDING_END'))))

    def test_recording_end_without_start(self):
        self.assertEqual(codes(fixture(('A', 'RECORDING_END'))), ['RECORDING_END_WITHOUT_START'])

    def test_duplicate_recording_start(self):
        self.assertIn('DUPLICATE_RECORDING_START', codes(fixture(('A', 'RECORDING_START'),
                          ('A', 'RECORDING_START'), ('A', 'RECORDING_END'))))

    def test_duplicate_question_start(self):
        self.assertIn('DUPLICATE_QUESTION_START', codes(fixture(('A', 'RECORDING_START'),
                         ('A', 'QUESTION_START'), ('A', 'QUESTION_START'),
                         ('A', 'QUESTION_END'), ('A', 'RECORDING_END'))))

    def test_recording_end_with_open_question(self):
        self.assertIn('RECORDING_END_WITH_QUESTION_OPEN', codes(fixture(
            ('A', 'RECORDING_START'), ('A', 'QUESTION_START'), ('A', 'RECORDING_END'))))

    def test_eof_unclosed_states(self):
        self.assertEqual(codes(fixture(('A', 'RECORDING_START'), ('A', 'QUESTION_START'))),
                         ['UNCLOSED_QUESTION', 'UNCLOSED_RECORDING'])

    def test_eof_recording_only(self):
        self.assertEqual(codes(fixture(('A', 'RECORDING_START'))), ['UNCLOSED_RECORDING'])

    def test_independent_recorder_state(self):
        raw = fixture(('A', 'RECORDING_START'), ('B', 'QUESTION_START'),
                      ('A', 'RECORDING_END'))
        result = review_synthetic_mtc(raw)
        self.assertEqual(result['finding_count'], 1)
        self.assertEqual(result['findings'][0]['recorder_id'], 'B')

    def test_non_increasing_per_recorder_timestamp(self):
        raw = (HEADER + '2026-10-22T08:01:00Z,A,RECORDING_START\n'
               '2026-10-22T08:00:00Z,A,RECORDING_END\n').encode()
        self.assertIn('NON_INCREASING_TIMESTAMP', codes(raw))

    def test_different_recorder_same_timestamp_valid(self):
        raw = (HEADER + '2026-10-22T08:00:00Z,A,RECORDING_START\n'
               '2026-10-22T08:00:00Z,B,RECORDING_START\n'
               '2026-10-22T08:01:00Z,B,RECORDING_END\n'
               '2026-10-22T08:01:00Z,A,RECORDING_END\n').encode()
        self.assertEqual(codes(raw), [])

    def test_equal_timestamp_on_same_recorder_flagged(self):
        raw = (HEADER + '2026-10-22T08:00:00Z,A,RECORDING_START\n'
               '2026-10-22T08:00:00Z,A,RECORDING_END\n').encode()
        self.assertIn('NON_INCREASING_TIMESTAMP', codes(raw))

    def test_integrity_and_unmodified_bytes(self):
        raw = fixture(('A', 'RECORDING_START'), ('A', 'RECORDING_END'))
        digest = hashlib.sha256(raw).hexdigest()
        result = review_synthetic_mtc(raw, expected_sha256=digest)
        self.assertEqual(result['sha256'], digest)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
        with self.assertRaises(ValueError):
            review_synthetic_mtc(raw, expected_sha256='0' * 64)

    def test_unknown_marker_rejected(self):
        with self.assertRaises(ValueError):
            review_synthetic_mtc(fixture(('A', 'COMMAND_PANIC_BOX_ON')))

    def test_invalid_csv_rejected(self):
        with self.assertRaises(ValueError):
            review_synthetic_mtc(b'timestamp,marker\n2026-10-22T08:00:00Z,RECORDING_START\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
