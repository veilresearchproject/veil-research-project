import unittest
from desktop_acceptance_check import CHECKS, build_report

class AcceptanceTests(unittest.TestCase):
    def test_all_skipped_is_not_a_pass(self):
        report = build_report({key: 'SKIP' for key, _ in CHECKS})
        self.assertEqual(report['summary'], {'pass': 0, 'fail': 0, 'skip': len(CHECKS)})
        self.assertEqual(report['mode'], 'human_observed_not_automated')

    def test_mixed_outcomes(self):
        values = {key: 'PASS' for key, _ in CHECKS}
        values['evidence'] = 'FAIL'
        values['voice'] = 'SKIP'
        self.assertEqual(build_report(values)['summary'], {'pass': 6, 'fail': 1, 'skip': 1})

    def test_reject_missing(self):
        with self.assertRaises(ValueError):
            build_report({})

    def test_reject_invalid(self):
        with self.assertRaises(ValueError):
            build_report({key: 'OK' for key, _ in CHECKS})

    def test_no_raw_audio_or_transcript_fields(self):
        report = build_report({key: 'PASS' for key, _ in CHECKS})
        self.assertNotIn('transcript', str(report).lower())
        self.assertNotIn('audio', str(report).lower())

if __name__ == '__main__':
    unittest.main()
