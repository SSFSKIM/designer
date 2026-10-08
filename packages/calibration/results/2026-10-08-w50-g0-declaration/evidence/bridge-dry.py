"""Exercise committed opening bridges through region statistics, without any native launch."""
import importlib.util
import io
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
DECL = HERE.parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location('w50_bridge_dry', DECL / 'bed/sitting/w50.py')
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)
W.dry_imports()
driver = W.configure(DECL / 'bed/sitting-g1.json')
plan = json.loads((DECL / 'bed/sitting-g1.json').read_text())
doc = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())
scenes = {s['id']: s for s in doc['scenes']}
checks = []
for p in plan['passes']:
    if not p['name'].startswith('open-'):
        continue
    for cell, reference in driver.bridge_references(p).items():
        scene = scenes[cell.split('/', 1)[1]]
        # A single exterior pixel changes, so neither byte nor pixel identity can skip the
        # actual region reader. It cannot shift a populated region's median by a whole code.
        with Image.open(io.BytesIO(reference)) as original:
            image = original.convert('RGBA')
        r, g, b, a = image.getpixel((0, 0))
        image.putpixel((0, 0), (r + 1 if r < 255 else r - 1, g, b, a))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        verdict = driver.bridge_verdict(buffer.getvalue(), reference,
            doc['backgrounds'][scene['background']], doc['components'][scene['component']],
            p['scale'], 'dark', p['pose'], cell=cell)
        if not verdict['agrees'] or verdict.get('statistics', 0) <= 0:
            raise ValueError(f'Opening bridge has no usable region reading: {cell}: {verdict}')
        checks.append({'cell': cell, 'statistics': verdict['statistics'],
                       'worstDelta': verdict['worstDelta'], 'referenceSha256': verdict['referenceSha256']})
print(json.dumps({'status': 'PASS', 'openingReferenceCells': len(checks), 'checks': checks}, indent=2))
