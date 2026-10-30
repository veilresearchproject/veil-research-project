"""One operator-selected desktop entry point. No installs or automatic audio checks."""
import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parent
VERSION = '0.16'
REQUIRED = (
    'signal_launcher.py', 'signal_desktop.py', 'signal_core.py', 'signal_face.html',
    'signal_face.js', 'signal_face.css', 'signal_check_setup.py', 'signal_voice.py',
    'signal_listen.py', 'signal_diagnostics.py', 'signal_models.py', 'signal_session.py',
    'signal_annotations.py', 'signal_packet.py', 'signal_review_import.py', 'mtc_evidence.py',
    'test_signal_core.py', 'test_signal_desktop.py', 'test_signal_launcher.py',
    'DESKTOP_TEST_STEPS.md',
) + tuple('face_assets/' + name + '.webp' for name in
          ('neutral', 'focused', 'amused', 'excited', 'concentrating', 'reassuring',
           'speech_0', 'speech_1', 'speech_2', 'speech_3'))
ACTIONS = {
    '1': ('demo', 'Scripted face demo (no AI model)'),
    '2': ('live', 'Live assistant (requires local Ollama)'),
    '3': ('setup', 'Check local setup (no speaking or microphone capture)'),
    '4': ('tests', 'Run automated Python tests (no real model or audio)'),
    '5': ('guide', 'Read the desktop test steps'),
}


class LaunchError(ValueError):
    pass


def verify_package(root, version=None):
    """Detect incomplete extraction and accidental damage, not publisher authenticity."""
    version = sys.version_info if version is None else version
    if tuple(version[:2]) < (3, 10):
        raise LaunchError('Python 3.10 or newer is required. No software was installed or changed.')
    root = Path(root).resolve()
    manifest = root / 'SHA256_MANIFEST.txt'
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size > 131072:
        raise LaunchError('Package manifest is missing or too large. Extract the complete Windows ZIP into a new folder.')
    try:
        rows = manifest.read_text(encoding='utf-8').splitlines()
        if not rows or len(rows) > 500:
            raise LaunchError('Package manifest is not usable. Extract the complete ZIP again.')
        seen = set()
        for row in rows:
            fields = row.split('  ', 1)
            if len(fields) != 2 or not re.fullmatch(r'[a-f0-9]{64}', fields[0]):
                raise LaunchError('Package manifest contains an invalid entry.')
            digest, name = fields
            relative = PurePosixPath(name)
            if (not name or relative.is_absolute() or relative.as_posix() != name or '\\' in name or ':' in name
                or any(part in ('..', '.') for part in name.split('/')) or name in seen):
                raise LaunchError('Package manifest contains an unsafe or duplicate path.')
            seen.add(name)
            file = root.joinpath(*relative.parts)
            if file.is_symlink() or not file.resolve().is_relative_to(root):
                raise LaunchError('Package entry does not resolve to a regular local package file.')
            if not file.is_file() or file.stat().st_size > 16 * 1024 * 1024:
                raise LaunchError('Package file is missing or too large: ' + name)
            if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
                raise LaunchError('Package file has changed or is damaged: ' + name + '. Extract a fresh copy into a new folder.')
        if not set(REQUIRED).issubset(seen):
            raise LaunchError('Manifest does not cover all required startup files. Use a complete Windows release ZIP.')
        return len(seen)
    except (OSError, UnicodeError) as exc:
        raise LaunchError('Could not read the extracted package. Try a fresh folder with read access.') from exc


def command_for(action, root=ROOT, executable=None):
    executable = sys.executable if executable is None else executable
    root = Path(root).resolve()
    scripts = {'demo': ('signal_desktop.py', '--demo'),
               'live': ('signal_desktop.py',), 'setup': ('signal_check_setup.py',)}
    if action in scripts:
        script, *args = scripts[action]
        return [executable, str(root / script), *args]
    if action == 'tests':
        return [executable, '-m', 'unittest', 'discover', '-s', str(root), '-p', 'test_*.py', '-q']
    raise LaunchError('Choose one of the listed actions.')


def main(argv=None, input_fn=input, output=print, exec_fn=None, root=ROOT):
    parser = argparse.ArgumentParser(description='SIGNAL checked desktop launcher')
    parser.add_argument('--action', choices=('demo', 'live', 'setup', 'tests', 'guide'))
    args = parser.parse_args(argv)
    try:
        count = verify_package(root)
        output('SIGNAL v' + VERSION + ' — ' + str(count) + ' packaged files checked.')
        output('This check detects package damage; it does not test Windows audio or model performance.')
        action = args.action
        if action is None:
            for key, (_, label) in ACTIONS.items(): output(key + '. ' + label)
            output('Q. Quit without starting SIGNAL')
            choice = input_fn('Choose an option: ').strip().lower()
            if choice == 'q': return 0
            if choice not in ACTIONS: raise LaunchError('No action started. Choose a listed number next time.')
            action = ACTIONS[choice][0]
        if action == 'guide':
            output((Path(root) / 'DESKTOP_TEST_STEPS.md').read_text(encoding='utf-8'))
            return 0
        command = command_for(action, root)
        output('Starting ' + action + '. No model download or automatic microphone activation.')
        # Replaces the launcher so console Ctrl+C belongs to the selected program.
        # Fixed argv, current interpreter, absolute script path, no shell execution.
        (exec_fn or os.execv)(command[0], command)
        return 0  # Used only by injected test exec functions; real exec does not return.
    except (LaunchError, OSError, EOFError) as exc:
        output('SIGNAL could not start: ' + str(exc))
        output('Keep existing MTC evidence and saved chats. See README_FIRST.txt.')
        return 2
    except KeyboardInterrupt:
        output('No launch selected.')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
