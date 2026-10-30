"""Reproducible archive and launcher acceptance, without starting SIGNAL."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

import build_signal_release
import signal_launcher


class ReleaseBuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'source'; self.root.mkdir()
        for name in signal_launcher.REQUIRED:
            file = self.root / name; file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(('Synthetic ' + name).encode())
        self.output = Path(self.tmp.name) / 'release.zip'

    def tearDown(self): self.tmp.cleanup()

    def test_built_archive_passes_launcher_checks_and_excludes_runtime_data(self):
        (self.root / 'memories.json').write_text('PRIVATE runtime memory')
        (self.root / 'recording.wav').write_bytes(b'PRIVATE audio')
        build_signal_release.build_release(self.root, self.output, 'a' * 40)
        with zipfile.ZipFile(self.output) as archive:
            self.assertFalse(any(n.endswith(('memories.json', 'recording.wav')) for n in archive.namelist()))
            target = Path(self.tmp.name) / 'extracted'; archive.extractall(target)
        extracted = target / ('VEIL_SIGNAL_Desktop_v' + signal_launcher.VERSION)
        self.assertGreater(signal_launcher.verify_package(extracted), len(signal_launcher.REQUIRED))

    def test_identical_inputs_produce_identical_zip_bytes(self):
        build_signal_release.build_release(self.root, self.output, 'b' * 40)
        first = self.output.read_bytes()
        build_signal_release.build_release(self.root, self.output, 'b' * 40)
        self.assertEqual(hashlib.sha256(first).hexdigest(), hashlib.sha256(self.output.read_bytes()).hexdigest())

    def test_invalid_source_or_commit_preserves_existing_release(self):
        self.output.write_bytes(b'existing release')
        with self.assertRaises(ValueError): build_signal_release.build_release(self.root, self.output, 'bad')
        (self.root / 'signal_core.py').unlink()
        with self.assertRaises(ValueError): build_signal_release.build_release(self.root, self.output)
        self.assertEqual(self.output.read_bytes(), b'existing release')


if __name__ == '__main__': unittest.main()
