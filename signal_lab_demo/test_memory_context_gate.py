import unittest
from memory_context_gate import build_memory_context


class Memory:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    def list_notes(self, include_retracted=False):
        assert include_retracted is False
        self.calls += 1
        return self.rows


def note(i, status='reviewed'):
    return {'id': i, 'text': f'Operator note {i}', 'source': 'operator', 'status': status}


class ContextGateTests(unittest.TestCase):
    def test_no_consent_no_read(self):
        m = Memory([note(1)])
        self.assertFalse(build_memory_context(m, authenticated=True)['allowed'])
        self.assertEqual(m.calls, 0)

    def test_no_auth_no_read(self):
        m = Memory([note(1)])
        self.assertFalse(build_memory_context(m, consent=True)['allowed'])
        self.assertEqual(m.calls, 0)

    def test_metadata_only_default(self):
        result = build_memory_context(Memory([note(1)]), consent=True, authenticated=True)
        self.assertTrue(result['allowed'])
        self.assertNotIn('text', result['notes'][0])

    def test_explicit_text_opt_in(self):
        result = build_memory_context(Memory([note(1)]), consent=True, authenticated=True, include_text=True)
        self.assertEqual(result['notes'][0]['text'], 'Operator note 1')

    def test_unreviewed_and_retracted_excluded(self):
        result = build_memory_context(Memory([note(1, 'unverified'), note(2, 'retracted'), note(3)]), consent=True, authenticated=True, include_text=True)
        self.assertEqual([n['id'] for n in result['notes']], [3])

    def test_latest_five_only(self):
        result = build_memory_context(Memory([note(i) for i in range(1,13)]), consent=True, authenticated=True)
        self.assertEqual([n['id'] for n in result['notes']], [8, 9, 10, 11, 12])

    def test_bad_flags_fail_closed(self):
        for flags in ({'consent': 1}, {'authenticated': 'yes'}, {'include_text': 1}):
            with self.assertRaises(ValueError): build_memory_context(Memory([]), **flags)

    def test_bad_limit(self):
        for limit in (0, 6, True):
            with self.assertRaises(ValueError): build_memory_context(Memory([]), consent=True, authenticated=True, limit=limit)

    def test_malformed_reviewed_record(self):
        with self.assertRaises(ValueError): build_memory_context(Memory([{'id': 1, 'source': 'unknown', 'status': 'reviewed'}]), consent=True, authenticated=True)

    def test_read_only(self):
        m = Memory([note(1)])
        build_memory_context(m, consent=True, authenticated=True)
        self.assertEqual(m.rows[0]['text'], 'Operator note 1')
        self.assertEqual(m.calls, 1)


if __name__ == '__main__':
    unittest.main()
