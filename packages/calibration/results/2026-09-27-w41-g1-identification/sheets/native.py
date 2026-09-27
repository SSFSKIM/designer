"""Single-repeat PNG bridge. The only native payload open is Reader.read(cal/val)."""
import argparse
import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
from PIL import Image

HERE = Path(__file__).resolve().parent
W39 = HERE.parents[1] / '2026-09-26-w39-g0-colour-edge-bed'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def select_repeat(runs, ordinal):
    normal = sorted((r for r in runs if r['admitted'] and r['protocol'] == 'normal'),
                    key=lambda r: r['run'])
    if len(normal) != 7 or len({r['run'] for r in normal}) != 7:
        raise ValueError('seven distinct admitted normal repeats required')
    if ordinal not in range(7): raise ValueError('repeat ordinal must be 0..6')
    return normal[ordinal]


def read_native(root, generation, cell, ordinal):
    wave = module('sheet_wave', W39 / 'wave.py').default_wave()
    # Admission precedes Reader construction; it does not accept a caller's role label.
    if cell not in wave.cells or wave.roles[cell.split('/', 1)[1]] not in ('calibration', 'validation'):
        raise PermissionError('native sheets admit calibration/validation only')
    reader = wave.reader(root, roles=('calibration', 'validation'))
    if reader.generation != generation: raise ValueError('native inventory generation mismatch')
    entry = reader.entries[(cell, 'crop')]
    if not entry.get('admitted'): raise PermissionError('unadmitted archive cell')
    archive = module('sheet_archive', W39 / 'w39_archive.py')
    raw = reader.read(cell, 'crop')
    runs, states = archive.unbundle(raw)
    selected = select_repeat(runs, ordinal)
    payload = archive.unpack(states[selected['state']])
    stream = io.BytesIO()
    Image.fromarray(payload['rgb']).save(stream, format='PNG')
    png = stream.getvalue()
    return dict(png=base64.b64encode(png).decode(), provenance=dict(
        cell=cell, generation=reader.generation, cropSha256=hashlib.sha256(raw).hexdigest(),
        selectionRule='ordinal in lexically sorted admitted normal run names', ordinal=ordinal,
        selected=selected, allRuns=runs, pngSha256=hashlib.sha256(png).hexdigest(),
        payloadMetadata={k: v for k, v in payload.items() if k not in archive.PIXELS}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--archive-root', required=True)
    p.add_argument('--generation', required=True)
    p.add_argument('--cell', required=True)
    p.add_argument('--repeat', type=int, required=True)
    a = p.parse_args()
    print(json.dumps(read_native(a.archive_root, a.generation, a.cell, a.repeat)))
