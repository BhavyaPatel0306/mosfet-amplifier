"""Regenerate hashes for distributed files, excluding local build/cache files."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '__pycache__', 'build', '.venv', '.pytest_cache'}


def files():
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if (path.is_file() and not any(part in EXCLUDED for part in relative.parts)
                and path.name != 'SHA256SUMS.txt' and path.suffix not in {'.pyc', '.lck', '.kicad_prl'}
                and not any(part.endswith('-backups') for part in relative.parts)):
            yield path


if __name__ == '__main__':
    lines = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(ROOT).as_posix()
             for p in files()]
    (ROOT/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
    print(f'Updated {len(lines)} hashes.')
