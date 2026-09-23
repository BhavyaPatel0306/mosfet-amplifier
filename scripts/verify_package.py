"""Check distribution integrity, not circuit performance. Python 3 only."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import sys
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    errors = []
    records = (root / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
    seen = set()
    for record in records:
        digest, separator, name = record.partition('  ')
        relative = PurePosixPath(name)
        if (not separator or not re.fullmatch(r'[0-9a-f]{64}', digest)
                or relative.is_absolute() or '..' in relative.parts
                or '\\' in name or ':' in name or not name or name in seen):
            errors.append('Invalid or duplicate manifest entry: ' + record)
            continue
        seen.add(name)
        target = root / name
        if not target.is_file():
            errors.append('Missing file: ' + name)
        elif hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            errors.append('Checksum mismatch: ' + name)
    if not seen:
        errors.append('Manifest contains no valid files')

    hardware = root / 'hardware'
    for name in ['ELE404Project.kicad_pro', 'ELE404Project.wbk']:
        try:
            json.loads((hardware / name).read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            errors.append(f'Invalid JSON {name}: {exc}')
    try:
        schematic = (hardware / 'ELE404Project.kicad_sch').read_text(encoding='utf-8')
        libraries = re.findall(r'\(property "Sim.Library" "([^"]+)"', schematic)
        if len(libraries) != 4 or any(p != 'models/nmos_t.txt' for p in libraries):
            errors.append('Expected four portable NMOS library references')
        if not (hardware / 'models/nmos_t.txt').is_file():
            errors.append('NMOS model file is missing')
    except OSError as exc:
        errors.append('Schematic is unreadable: ' + str(exc))
    try:
        with zipfile.ZipFile(root / 'originals/MOSFET AMPLIFIER DESIGN.zip') as archive:
            bad = archive.testzip()
            if bad:
                errors.append('Original ZIP CRC failed: ' + bad)
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append('Original ZIP is unreadable: ' + str(exc))
    if errors:
        print('\n'.join('FAIL: ' + error for error in errors))
        return 1
    print(f'PASS: {len(seen)} file hashes, four model references, project/workbook JSON, and original ZIP CRC.')
    print('No simulations or electrical checks were run.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
