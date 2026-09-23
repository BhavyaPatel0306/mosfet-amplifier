"""Build a verified, deterministic project ZIP using the checksum manifest."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'build')
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT/'scripts/verify_package.py')], check=True)
    version = (ROOT/'VERSION').read_text().strip()
    names = [line.split('  ', 1)[1] for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines()]
    names.append('SHA256SUMS.txt')
    args.output.mkdir(parents=True, exist_ok=True)
    archive_path = args.output/f'mosfet-amplifier-v{version}.zip'
    with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(names):
            entry = zipfile.ZipInfo(f'mosfet-amplifier/{name}', date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, (ROOT/name).read_bytes())
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        for name in names:
            assert archive.read('mosfet-amplifier/'+name) == (ROOT/name).read_bytes()
    checksum = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    archive_path.with_suffix('.zip.sha256').write_text(f'{checksum}  {archive_path.name}\n')
    print(f'Built and verified {archive_path} ({len(names)} files). SHA-256: {checksum}')


if __name__ == '__main__':
    main()
