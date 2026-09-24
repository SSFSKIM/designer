"""Guarded native / previous / shipped-law triptychs (§5.180 clause 8).

Canonical panels use the current and superseded capture trees. W34 black is not
in the canonical matrix: its third panel is G1's retained pre-seal price at the
now-shipped law, labelled as such. Its base plus tune and explicit receded patch
must equal the shipped documents; no scratch digest is relabelled a sealed one.
"""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CAL = HERE.parent.parent
ROOT = CAL.parent.parent
MAIN = Path('/Users/new/Developer/GitHub/designer/packages/calibration')
G1 = HERE.parent / '2026-09-24-w36-g1-black-branch'
sys.path.insert(0, str(HERE.parent / '2026-09-24-w35-g0-edge-cut'))
import edge
from w35_readers import WebReader, CanonicalNativeReader
spec = importlib.util.spec_from_file_location('colour', HERE.parent / '2026-09-22-w33-g1b-rim-fit/read-round.py')
colour = importlib.util.module_from_spec(spec)
spec.loader.exec_module(colour)
plans = {p['profile']: p for p in json.loads((G1 / 'candidate-plans.json').read_text())}
sealed = json.loads((G1 / 'sealed-manifest.json').read_text())['documents']
wave = edge.W.default_wave()
native34 = wave.reader(edge.G1 / 'probe')
nativeC = CanonicalNativeReader()
old34 = WebReader.w34()
current = WebReader.canonical(MAIN / 'web-captures')
matrix = {c['key']['profileKey'] + '/' + c['key']['sceneId']: c for c in
          json.loads((CAL / 'results/matrix.json').read_text())['cells'] if c['key']['web']['renderer'] == 'webgpu'}
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 16)
small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 12)
lsb = float(np.linalg.norm(colour.lab(np.ones((1, 1, 3))) - colour.lab(np.zeros((1, 1, 3)))) * 8 * 255)
output = HERE / 'sheets'
output.mkdir(exist_ok=True)
records = []
for scheme in ['light', 'dark']:
    previous_sha = '6e509c7f76cc' if scheme == 'light' else 'eab099cc6698'
    oldC = WebReader.canonical(MAIN / 'web-captures-superseded' / previous_sha)
    superseded = {c['key']['profileKey'] + '/' + c['key']['sceneId']: c for c in
                  json.loads((CAL / f'results/superseded/{previous_sha}.json').read_text())['cells']
                  if c['key']['web']['renderer'] == 'webgpu'}
    active_name = f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json'
    receded_name = active_name.replace('.json', '-receded.json')
    active = json.loads((CAL / 'profiles' / active_name).read_text())
    receded = json.loads((CAL / 'profiles' / receded_name).read_text())
    base = json.loads(subprocess.check_output(['git', '-C', str(ROOT), 'show',
        '2f49d390^:packages/calibration/profiles/' + active_name]))
    for scale in [1, 2]:
        profile = f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'
        for pose in ['rest', 'inactive']:
            for background in ['grey-0', 'impulse', 'photo']:
                is34 = background == 'grey-0'
                sid = background + ('__circular-120__' if is34 else '__capsule-button__') + pose
                cell = profile + '/' + sid
                native_raw = native34.read(cell, 'png') if is34 else nativeC.read(cell)
                previous_raw = (old34 if is34 else oldC).read(cell)
                if is34:
                    reader = WebReader.w34(Path(plans[profile]['root']) / 'web-captures')
                    shipped_raw = reader.read(cell)
                    report = json.loads(reader.read(cell, 'report'))
                    meta = json.loads(reader.read(cell, 'metadata'))
                    assert meta['deterministic'] and meta['repeatNoise'] == 0
                    assert meta['gpuAdapter'] == 'apple/metal-3' and not report['fallback']
                    for field in ['materialProfile', 'recededProfile']:
                        document = report[field]
                        assert hashlib.sha256(Path(document['path']).read_bytes()).hexdigest()[:12] == document['sha256']
                    assert {**base['patch'], **report['materialProfile']['patch']} == active['patch']
                    assert report['recededProfile']['patch'] == receded['patch']
                    assert report['page']['material']['resolvedMaterialSha256'] == sealed[active_name]['beforeDigest']
                    provenance = 'G1 pre-seal price; base+tune equals shipped patch; not a canonical capture'
                    label = 'Shipped law (G1 pre-seal price)'
                else:
                    shipped_raw = current.read(cell)
                    meta = json.loads(current.read(cell, 'metadata'))
                    old_meta = json.loads(oldC.read(cell, 'metadata'))
                    assert meta['capturePath'] == matrix[cell]['key']['web']['capturePath']
                    assert old_meta['capturePath'] == superseded[cell]['key']['web']['capturePath']
                    docs = re.findall(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})', meta['capturePath'])
                    assert len(docs) == 2
                    for path, digest in docs:
                        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:12] == digest
                    provenance = 'Canonical shipped and W33 superseded captures, matrix paths and both hashes checked'
                    label = 'Shipped canonical WebGPU'
                images = [Image.open(io.BytesIO(raw)).convert('RGB') for raw in [native_raw, previous_raw, shipped_raw]]
                native, previous, shipped = [np.asarray(im, float) for im in images]
                height, width = native.shape[:2]
                gap = 10
                page = Image.new('RGB', (3 * width + 2 * gap, 2 * height + 156), 'white')
                draw = ImageDraw.Draw(page)
                draw.text((0, 3), cell, font=font, fill='black')
                for i, (caption, image) in enumerate(zip(['Native', 'Previous W33 WebGPU', label], images)):
                    draw.text((i * (width + gap), 28), caption, font=font, fill='black')
                    page.paste(image, (i * (width + gap), 50))
                panels = []
                for i, (caption, image) in enumerate([('Previous - native', previous), ('Shipped law - native', shipped)]):
                    delta = np.minimum(255, np.linalg.norm(colour.lab(native) - colour.lab(image), axis=2) * 8 * 255)
                    panel = Image.fromarray(np.repeat(np.rint(delta).astype('uint8')[:, :, None], 3, axis=2))
                    y = height + 72
                    draw.text((i * (width + gap), y), caption + ' | abs OKLab x8', font=font, fill='black')
                    page.paste(panel, (i * (width + gap), y + 22))
                    draw.text((i * (width + gap), y + height + 25),
                              f'LSB 0 -> 1: {lsb:.2f}/255; white >= 0.125', font=small, fill='black')
                    panels.append(dict(label=caption, lsbBlackOneByteAmplification=lsb,
                                       maxChannelCodes=float(np.max(abs(image - native)))))
                draw.text((2 * (width + gap), height + 80),
                          'Unresampled pixels.\nBlack is the closure.\nGrey, chroma and the edge\nremain named gaps.\n\n' +
                          ('W34: retained G1 price,\nnot a new sealed capture.' if is34 else 'Both document hashes\nmatch the live matrix.'),
                          font=font, fill='black')
                name = profile.removeprefix('apple-macos-27.0-') + '__' + sid + '.png'
                if (output / name).exists():
                    raise RuntimeError('sheet already recorded')
                page.save(output / name)
                records.append(dict(cell=cell, origin='w34' if is34 else 'canonical',
                    file='sheets/' + name, provenance=provenance, panels=panels,
                    nativeSha256=hashlib.sha256(native_raw).hexdigest(),
                    previousSha256=hashlib.sha256(previous_raw).hexdigest(),
                    shippedLawSha256=hashlib.sha256(shipped_raw).hexdigest(),
                    currentCapturePath=meta['capturePath'],
                    shippedDocuments={name: sealed[name]['fileSha256'] for name in [active_name, receded_name]}))
with (HERE / 'sheet-readings.json').open('x') as f:
    json.dump(records, f, indent=2)
    f.write('\n')
print('Sheets', len(records), 'LSB', lsb, 'all role guards and provenance checks passed')
