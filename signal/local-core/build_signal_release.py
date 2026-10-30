"""Build a checked Windows ZIP from this source folder. Does not run hardware tests."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

import signal_launcher


def build_release(root, output, source_commit=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    if source_commit is not None and not re.fullmatch(r'[a-f0-9]{40}', source_commit):
        raise ValueError('Source commit must be a complete 40-character Git SHA')
    files = {}
    for file in sorted(root.rglob('*')):
        relative = file.relative_to(root)
        if any(part.startswith('.') or part == '__pycache__' for part in relative.parts):
            continue
        if not file.is_file(): continue
        name = relative.as_posix()
        allowed = ((len(relative.parts) == 1 and
                   (file.suffix in ('.py', '.bat', '.cjs', '.md', '.txt', '.html', '.css', '.js') or re.fullmatch(r'V\d+_QA\.json', name)))
                   or (len(relative.parts) == 2 and relative.parts[0] == 'face_assets' and file.suffix == '.webp'))
        if not allowed or name in ('SHA256_MANIFEST.txt', 'SOURCE_COMMIT.txt'): continue
        if file.is_symlink() or not file.resolve().is_relative_to(root):
            raise ValueError('Release inputs must be regular files within the source folder')
        data = file.read_bytes()
        if len(data) > 16 * 1024 * 1024: raise ValueError('Release input exceeds the launcher size limit')
        files[name] = data
    if not set(signal_launcher.REQUIRED).issubset(files):
        raise ValueError('Source folder is missing required SIGNAL release files')
    files['SOURCE_COMMIT.txt'] = ('SIGNAL v' + signal_launcher.VERSION + '\nSource commit: ' +
                                  (source_commit or 'not recorded') + '\n').encode()
    files['BUILD_INFO.json'] = (json.dumps({'version': signal_launcher.VERSION,
        'source_commit': source_commit, 'note': 'Packaging verifies bytes; it does not run tests or prove hardware readiness.'}, indent=2) + '\n').encode()
    manifest = '\n'.join(hashlib.sha256(data).hexdigest() + '  ' + name for name, data in sorted(files.items())) + '\n'
    files['SHA256_MANIFEST.txt'] = manifest.encode()
    prefix = 'VEIL_SIGNAL_Desktop_v' + signal_launcher.VERSION + '/'
    output.parent.mkdir(parents=True, exist_ok=True)
    # A temporary sibling avoids leaving a half-written release at the final path.
    temporary = output.with_name(output.name + '.building')
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(files.items()):
                entry = zipfile.ZipInfo(prefix + name, (2026, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data)
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None: raise ValueError('Archive integrity check failed')
            for name, data in files.items():
                if archive.read(prefix + name) != data: raise ValueError('Archive content verification failed')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return {'path': str(output), 'files': len(files), 'bytes': output.stat().st_size}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Package SIGNAL source without installs or downloads')
    parser.add_argument('--output', required=True)
    parser.add_argument('--source-commit')
    args = parser.parse_args()
    print(json.dumps(build_release(Path(__file__).resolve().parent, args.output, args.source_commit)))
