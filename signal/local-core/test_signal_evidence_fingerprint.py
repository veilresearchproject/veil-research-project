import tempfile
import unittest
from pathlib import Path
from signal_evidence_fingerprint import fingerprint_session


class FingerprintTests(unittest.TestCase):
    def test_deterministic_and_change_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'a.wav').write_bytes(b'example audio')
            (root / 'log.json').write_text('{}')
            first = fingerprint_session(temp)
            self.assertEqual(first, fingerprint_session(temp))
            self.assertEqual(len(first['files']), 2)
            (root / 'a.wav').write_bytes(b'changed audio')
            self.assertNotEqual(first['inventory_sha256'], fingerprint_session(temp)['inventory_sha256'])

    def test_ignore_non_evidence_extensions(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / 'installer.exe').write_bytes(b'not evidence')
            self.assertEqual(fingerprint_session(temp)['files'], [])

    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'a.wav').write_bytes(b'x')
            (root / 'link.wav').symlink_to(root / 'a.wav')
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                fingerprint_session(temp)


if __name__ == '__main__':
    unittest.main()
