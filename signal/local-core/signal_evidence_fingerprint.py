"""Read-only SHA-256 inventory for an MTC session; not proof of authenticity or EVP."""
import argparse
import hashlib
import json
from pathlib import Path

MAX_FILES = 2000
CHUNK = 1024 * 1024
EXTENSIONS = {'.wav', '.json', '.csv', '.txt', '.mp4', '.mkv'}


def fingerprint_session(folder: str) -> dict:
    root = Path(folder).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Session path must be a directory')
    records = []
    paths = sorted(root.rglob('*'), key=lambda p: p.relative_to(root).as_posix().lower())
    for path in paths:
        if path.is_symlink():
            raise ValueError(f'Symlink rejected: {path.relative_to(root)}')
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if len(records) >= MAX_FILES:
            raise ValueError('File count exceeds safety limit')
        before = path.stat()
        sha = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(CHUNK), b''):
                sha.update(block)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError(f'File changed during hashing: {path.relative_to(root)}')
        records.append({'path': path.relative_to(root).as_posix(), 'bytes': after.st_size,
                        'sha256': sha.hexdigest()})
    canonical = json.dumps(records, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')
    return {'schema': 'veil.signal.evidence-fingerprint.v1', 'algorithm': 'SHA-256',
            'scope': 'selected file extensions only; no symlinks', 'files': records,
            'inventory_sha256': hashlib.sha256(canonical).hexdigest(),
            'warning': 'Not an authenticity certification or paranormal finding.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('session_folder', help='Existing local MTC session folder')
    args = parser.parse_args()
    print(json.dumps(fingerprint_session(args.session_folder), indent=2))


if __name__ == '__main__':
    main()
