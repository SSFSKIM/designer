"""Copy eight calibration-only bridge bundles; no fit, validation or holdout read."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROOF = Path('/Users/new/vitrea-w41/pre-w41-proof')
RESULTS = PROOF/'packages/calibration/results'
sys.path.insert(0, str(RESULTS/'2026-09-26-w39-g2-identification'))
import native


def main():
    root = Path((HERE.parents[1]/'archive-root.txt').read_text().strip())
    assert Path.home()/'.cache/vitrea-archives' in root.resolve().parents
    wave, reader = native.guarded(root, ('calibration',))
    assert reader.generation == '58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61'
    out = HERE/'inputs'
    out.mkdir(exist_ok=False)
    rows = []
    for scheme in ('light', 'dark'):
        for scale in (1, 2):
            for colour in ('red', 'green'):
                cell = f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5/{colour}-colour__inactive'
                assert wave.roles[cell.split('/', 1)[1]] == 'calibration'
                data = reader.read(cell, 'crop')
                digest = hashlib.sha256(data).hexdigest()
                assert digest == reader.entries[cell, 'crop']['sha256']
                name = f'{scheme}-{scale}x-{colour}.crop'
                (out/name).write_bytes(data)
                rows.append(dict(cell=cell, role='calibration', scheme=scheme, scale=scale,
                                 colour=colour, file=name, sha256=digest, bytes=len(data)))
    (out/'manifest.json').write_text(json.dumps(dict(archiveRoot=str(root),
        inventorySha256=reader.generation, roles=['calibration'], cells=rows), indent=2)+'\n')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
