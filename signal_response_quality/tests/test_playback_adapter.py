import unittest
from playback_adapter import play_remaining

class FakePipeline:
    def __init__(self, chunks):
        self.chunks, self.index, self.failed = chunks, 0, False
    @property
    def done(self):
        return self.index == len(self.chunks) and not self.failed
    def next_chunk(self):
        return None if self.failed or self.done else (self.index, self.chunks[self.index])
    def confirm_played(self, index):
        if self.failed or index != self.index:
            raise ValueError("out of order")
        self.index += 1
    def fail_chunk(self, index):
        if index != self.index:
            raise ValueError("wrong index")
        self.failed = True
    def retry_failed(self):
        if not self.failed:
            raise RuntimeError("not failed")
        self.failed = False
        return self.index

class AdapterTests(unittest.TestCase):
    def test_success(self):
        p, heard = FakePipeline(["one", "two"]), []
        result = play_remaining(p, lambda s: heard.append(s) or True)
        self.assertTrue(result.completed)
        self.assertEqual(heard, ["one", "two"])
        self.assertEqual(result.played_now, 2)
    def test_false_stops(self):
        p, heard = FakePipeline(["one", "two", "three"]), []
        result = play_remaining(p, lambda s: heard.append(s) or (s != "two"))
        self.assertFalse(result.completed)
        self.assertEqual(result.failed_index, 1)
        self.assertEqual(heard, ["one", "two"])
    def test_exception_redacted(self):
        p = FakePipeline(["one"])
        def broken(_):
            raise RuntimeError("private transcript must not leak")
        result = play_remaining(p, broken)
        self.assertEqual(result.error, "RuntimeError")
        self.assertNotIn("private", str(result))
    def test_explicit_retry(self):
        p = FakePipeline(["first", "second"])
        play_remaining(p, lambda _: False)
        self.assertFalse(play_remaining(p, lambda _: True).completed)
        p.retry_failed()
        self.assertTrue(play_remaining(p, lambda _: True).completed)
    def test_none_not_confirmation(self):
        p = FakePipeline(["first"])
        self.assertEqual(play_remaining(p, lambda _: None).error, "playback_not_confirmed")
    def test_empty(self):
        self.assertTrue(play_remaining(FakePipeline([]), lambda _: True).completed)
    def test_already_finished(self):
        p = FakePipeline(["one"])
        play_remaining(p, lambda _: True)
        self.assertEqual(play_remaining(p, lambda _: self.fail("should not replay")).played_now, 0)

if __name__ == "__main__":
    unittest.main()
