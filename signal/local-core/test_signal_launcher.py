"""Checked launch dispatch with synthetic packages; never opens apps or devices."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

import signal_launcher as launcher


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='signal launcher test ')
        self.root = Path(self.temp.name)
        for name in launcher.REQUIRED:
            file = self.root / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('Synthetic package file: ' + name)
        self.manifest = self.root / 'SHA256_MANIFEST.txt'
        self.write_manifest()

    def tearDown(self): self.temp.cleanup()

    def write_manifest(self):
        self.manifest.write_text('\n'.join(hashlib.sha256((self.root / n).read_bytes()).hexdigest() + '  ' + n
                                           for n in launcher.REQUIRED) + '\n')

    def test_complete_package_and_minimum_python(self):
        self.assertEqual(launcher.verify_package(self.root), len(launcher.REQUIRED))
        with self.assertRaisesRegex(launcher.LaunchError, '3.10'):
            launcher.verify_package(self.root, version=(3, 9))

    def test_missing_and_changed_files_fail_before_execution(self):
        file = self.root / 'signal_core.py'
        file.write_text('Damaged')
        execute = Mock()
        self.assertEqual(launcher.main(['--action', 'live'], output=Mock(), exec_fn=execute, root=self.root), 2)
        execute.assert_not_called()
        file.unlink()
        with self.assertRaisesRegex(launcher.LaunchError, 'missing'):
            launcher.verify_package(self.root)

    def test_missing_manifest_gives_extraction_guidance(self):
        self.manifest.unlink()
        with self.assertRaisesRegex(launcher.LaunchError, 'Extract the complete'):
            launcher.verify_package(self.root)

    def test_unsafe_duplicate_and_uncovered_paths_are_rejected(self):
        valid = self.manifest.read_text()
        for name in ['../outside', '/absolute', 'C:/outside', 'face_assets\\neutral.webp', 'face_assets//neutral.webp']:
            with self.subTest(name=name):
                self.manifest.write_text(valid + '0' * 64 + '  ' + name + '\n')
                with self.assertRaises(launcher.LaunchError): launcher.verify_package(self.root)
        self.manifest.write_text(valid + valid.splitlines()[0] + '\n')
        with self.assertRaisesRegex(launcher.LaunchError, 'duplicate'): launcher.verify_package(self.root)
        self.manifest.write_text(valid.splitlines()[0] + '\n')
        with self.assertRaisesRegex(launcher.LaunchError, 'required'): launcher.verify_package(self.root)

    def test_quit_and_invalid_choice_never_launch(self):
        execute = Mock()
        self.assertEqual(launcher.main([], input_fn=lambda _: 'q', output=Mock(), exec_fn=execute, root=self.root), 0)
        self.assertEqual(launcher.main([], input_fn=lambda _: '2 & something', output=Mock(), exec_fn=execute, root=self.root), 2)
        execute.assert_not_called()

    def test_selected_demo_uses_fixed_argv_with_space_in_path(self):
        execute = Mock()
        self.assertEqual(launcher.main([], input_fn=lambda _: '1', output=Mock(), exec_fn=execute, root=self.root), 0)
        executable, command = execute.call_args.args
        self.assertEqual(command, [executable, str(self.root / 'signal_desktop.py'), '--demo'])
        self.assertNotIn('shell', execute.call_args.kwargs)

    def test_live_setup_and_test_dispatch_are_explicit(self):
        expected = {'live': 'signal_desktop.py', 'setup': 'signal_check_setup.py'}
        for action, file in expected.items():
            execute = Mock()
            self.assertEqual(launcher.main(['--action', action], output=Mock(), exec_fn=execute, root=self.root), 0)
            self.assertEqual(execute.call_args.args[1][1:], [str(self.root / file)])
        execute = Mock()
        launcher.main(['--action', 'tests'], output=Mock(), exec_fn=execute, root=self.root)
        self.assertEqual(execute.call_args.args[1][1:], ['-m', 'unittest', 'discover', '-s', str(self.root), '-p', 'test_*.py', '-q'])

    def test_guide_is_local_text_only(self):
        execute, output = Mock(), Mock()
        self.assertEqual(launcher.main(['--action', 'guide'], output=output, exec_fn=execute, root=self.root), 0)
        execute.assert_not_called()
        output.assert_any_call('Synthetic package file: DESKTOP_TEST_STEPS.md')

    def test_launch_os_error_reports_failure_without_installing(self):
        execute = Mock(side_effect=OSError('Synthetic process failure'))
        output = Mock()
        self.assertEqual(launcher.main(['--action', 'live'], output=output, exec_fn=execute, root=self.root), 2)
        self.assertTrue(any('Synthetic process failure' in str(c) for c in output.call_args_list))


if __name__ == '__main__': unittest.main()
