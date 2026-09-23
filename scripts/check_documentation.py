"""Check local Markdown links and parse published simulation metadata."""
import json
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []
for doc in ROOT.rglob('*.md'):
    if any(part in {'.git', 'build', '__pycache__'} for part in doc.relative_to(ROOT).parts):
        continue
    for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
        if '://' in link or link.startswith(('mailto:', '#')):
            continue
        if not (doc.parent/link.split('#')[0]).exists():
            errors.append(f'{doc.relative_to(ROOT)}: missing {link}')
data = json.loads((ROOT/'simulations/results/summary.json').read_text())
for name, digest in data['source_hashes'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, f'Simulation source changed: {name}'
for name in ['baseline', 'candidate']:
    result = data['results'][name]
    assert hashlib.sha256((ROOT/f'simulations/netlists/{name}.cir').read_bytes()).hexdigest() == result['netlist_sha256']
    assert result['dc_power_w'] > 0
    assert 0 <= result['load_reduction_percent'] < 100
    assert result['transient']['output_vpp'] > 0
    for analysis in ['ac-loaded', 'ac-unloaded', 'transient']:
        assert (ROOT/f'simulations/results/{name}-{analysis}.csv').is_file()
if errors:
    raise SystemExit('\n'.join(errors))
print('PASS: local documentation links and published simulation metadata structure.')
print('This is not a rerun of the circuit simulations.')
