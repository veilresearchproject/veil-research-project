import unittest
from guarded_memory_recall import guarded_recall


class Memory:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0
    def list_notes(self, include_retracted=False):
        assert include_retracted is False
        self.calls += 1
        return self.rows


def note(i, status="reviewed"):
    return {"id": i, "text": f"Operator note {i}", "source": "operator", "status": status}


class GuardedRecallTests(unittest.TestCase):
    def test_no_consent_no_read(self):
        m = Memory([note(1)])
        self.assertFalse(guarded_recall("remember", m, authenticated=True)["allowed"])
        self.assertEqual(m.calls, 0)
    def test_no_auth_no_read(self):
        m = Memory([note(1)])
        self.assertFalse(guarded_recall("memory", m, consent=True)["allowed"])
        self.assertEqual(m.calls, 0)
    def test_unrelated_no_read(self):
        m = Memory([note(1)])
        self.assertFalse(guarded_recall("hello", m, consent=True, authenticated=True)["handled"])
        self.assertEqual(m.calls, 0)
    def test_control_refused_without_read(self):
        m = Memory([note(1)])
        self.assertEqual(guarded_recall("delete memory", m, consent=True, authenticated=True)["notes"], [])
        self.assertEqual(m.calls, 0)
    def test_reviewed_only(self):
        m = Memory([note(1, "unverified"), note(2)])
        r = guarded_recall("what do you remember", m, consent=True, authenticated=True)
        self.assertEqual([n["id"] for n in r["notes"]], [2])
    def test_default_metadata_only(self):
        r = guarded_recall("notes", Memory([note(1)]), consent=True, authenticated=True)
        self.assertNotIn("text", r["notes"][0])
    def test_opt_in_text_never_spoken(self):
        r = guarded_recall("notes", Memory([note(1)]), consent=True, authenticated=True, include_text=True)
        self.assertEqual(r["notes"][0]["text"], "Operator note 1")
        self.assertNotIn("Operator note 1", r["spoken_text"])
    def test_bounded(self):
        r = guarded_recall("recall", Memory([note(i) for i in range(1, 12)]),
                           consent=True, authenticated=True, limit=3)
        self.assertEqual([n["id"] for n in r["notes"]], [9, 10, 11])
    def test_invalid_flags_and_limit(self):
        for opts in ({"consent": 1}, {"authenticated": "yes"}, {"include_text": 1}, {"limit": 6}, {"limit": True}):
            with self.assertRaises(ValueError):
                guarded_recall("remember", Memory([]), **opts)
    def test_malformed_record_fails_closed(self):
        with self.assertRaises(ValueError):
            guarded_recall("remember", Memory([{"id": 1, "status": "reviewed", "source": "unknown"}]),
                           consent=True, authenticated=True)
    def test_invalid_question(self):
        for q in ("", "\x00memory", "x" * 241):
            with self.assertRaises(ValueError):
                guarded_recall(q, Memory([]))
    def test_no_device_or_network_access(self):
        m = Memory([note(1)])
        r = guarded_recall("activate equipment and recall", m, consent=True, authenticated=True)
        self.assertEqual(r["notes"], [])
        self.assertEqual(m.calls, 0)


if __name__ == "__main__":
    unittest.main()
