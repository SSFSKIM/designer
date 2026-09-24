"""Place the live black demo beside guarded native and harness pixels (§5.180)."""
import hashlib
import io
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
G1 = HERE.parent / '2026-09-24-w36-g1-black-branch'
sys.path.insert(0, str(HERE.parent / '2026-09-24-w35-g0-edge-cut'))
import edge
from w35_readers import WebReader
text = (HERE / 'laws-readings-inline.txt').read_text()
live = json.loads(text.split('### Result\n', 1)[1].split('\n###', 1)[0])
profile = 'apple-macos-27.0-1x-light-standard-glass0.5'
cell = profile + '/grey-0__circular-120__rest'
plan = next(p for p in json.loads((G1 / 'candidate-plans.json').read_text()) if p['profile'] == profile)
native_raw = edge.W.default_wave().reader(edge.G1 / 'probe').read(cell, 'png')
harness_raw = WebReader.w34(Path(plan['root']) / 'web-captures').read(cell)
proof = next(r for r in json.loads((HERE / 'sheet-readings.json').read_text()) if r['cell'] == cell)
assert hashlib.sha256(native_raw).hexdigest() == proof['nativeSha256']
assert hashlib.sha256(harness_raw).hexdigest() == proof['shippedLawSha256']
assert (HERE / 'laws-black.png').read_bytes() == (HERE / 'laws-black-repeat.png').read_bytes()
native, harness = [Image.open(io.BytesIO(raw)).convert('RGB') for raw in [native_raw, harness_raw]]
demo = Image.open(HERE / 'laws-black.png').convert('RGB')
box, stage = live['smallBox'], live['stageBox']
x, y = int(box['x'] - stage['x']), int(box['y'] - stage['y'])
# Crop the small plate with black surroundings; do not rescale either geometry.
crop = (0, y - 40, x + int(box['width']) + 60, y + int(box['height']) + 40)
small = demo.crop(crop)
placed = Image.new('RGB', (320, 200), 'black')
placed.paste(small, ((320 - small.width) // 2, (200 - small.height) // 2))
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 15)
page = Image.new('RGB', (980, 292), 'white')
draw = ImageDraw.Draw(page)
for i, (label, image) in enumerate([('Native, span44', native),
    ('Harness, shipped law (G1 price), span44', harness), ('Demo /laws/, span40', placed)]):
    draw.text((i * 330, 5), label, fill='black', font=font)
    page.paste(image, (i * 330, 30))
draw.text((0, 240), 'Light active, black backdrop, DPR1. Unresampled; different widths/radii/spans, not silhouette equality.\nThe demo uses the sealed selected material; the harness is the retained, patch-verified G1 price.',
          fill='black', font=font)
page.save(HERE / 'demo-black-pair.png')
# A named label-free interior rectangle, not a claim of a full deep-domain metric.
rectangle = [x + 18, y + 16, x + 32, y + 24]
pixels = np.asarray(demo.crop(rectangle), dtype=float)
result = dict(**live, demoCrop=list(crop), labelFreeRectangle=rectangle,
              labelFreeMedianRGB=np.median(pixels, axis=(0, 1)).tolist(),
              labelFreeMinRGB=pixels.min(axis=(0, 1)).tolist(),
              labelFreeMaxRGB=pixels.max(axis=(0, 1)).tolist(),
              harnessProvenance=proof['provenance'], nativeSha256=proof['nativeSha256'],
              harnessSha256=proof['shippedLawSha256'],
              demoSha256=hashlib.sha256((HERE / 'laws-black.png').read_bytes()).hexdigest())
with (HERE / 'demo-black-reading.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print('Demo label-free rectangle', rectangle, 'median/min/max', result['labelFreeMedianRGB'],
      result['labelFreeMinRGB'], result['labelFreeMaxRGB'], 'repeat bytes identical')
