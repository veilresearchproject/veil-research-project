import unittest
from playback_tracker import PlaybackTracker

class PlaybackTrackerTests(unittest.TestCase):
    def test_success(self):
        t = PlaybackTracker(2)
        self.assertEqual(t.next_index, 0)
        t.confirm_completed(0)
        self.assertFalse(t.done)
        t.confirm_completed(1)
        self.assertTrue(t.done)
        self.assertIsNone(t.next_index)

    def test_failed_can_resume_at_same_chunk(self):
        t = PlaybackTracker(3)
        t.confirm_completed(0)
        t.mark_failed(1)
        self.assertFalse(t.done)
        self.assertIsNone(t.next_index)
        with self.assertRaises(RuntimeError):
            t.confirm_completed(1)
        self.assertEqual(t.resume_failed_chunk(), 1)
        t.confirm_completed(1)
        t.confirm_completed(2)
        self.assertTrue(t.done)

    def test_duplicate_rejected(self):
        t = PlaybackTracker(2)
        t.confirm_completed(0)
        with self.assertRaises(ValueError):
            t.confirm_completed(0)

    def test_out_of_order_rejected(self):
        t = PlaybackTracker(2)
        with self.assertRaises(ValueError):
            t.confirm_completed(1)

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            PlaybackTracker(0)

    def test_double_resume_rejected(self):
        t = PlaybackTracker(1)
        t.mark_failed(0)
        t.resume_failed_chunk()
        with self.assertRaises(RuntimeError):
            t.resume_failed_chunk()

    def test_completed_cannot_fail(self):
        t = PlaybackTracker(1)
        t.confirm_completed(0)
        with self.assertRaises(ValueError):
            t.mark_failed(0)

if __name__ == "__main__":
    unittest.main()
