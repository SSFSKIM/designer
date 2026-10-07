#!/usr/bin/env python3.12
"""Grounding attribution from committed cuts; contact sheets read captured pixels, never render.

Run with the capture-machine checkout as the sole argument. The current pair is verified against
capture report fields before images are used; source files are hashed in the emitted manifest.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
ROOT = CAL.parents[1]
MAIN = Path(sys.argv[1])
CURRENT = 'b2d074d2df24-940384c06f73'
cut_path = CAL / 'results/2026-10-07-w49a-g1-landing/cuts/cut-025-dark-w49a-landing.json'
cut = json.loads(cut_path.read_text())
cells = {(c['scale'], c['scene']): c for c in cut['T1']['cells']
         if c['scheme'] == 'dark' and c['tier'] == 'webgpu'}
old = json.loads((CAL / 'results/2026-10-07-w49-grounding/attribution.json').read_text())
old_rows = {(c['scale'], c['scene']): c for c in old['landed']}
owner = (CAL / 'test/adopted-thresholds.test.ts').read_text()
authorised = owner.split('const T1_DARK_AUTHORISED_REGRESSIONS:')[1].split('\n];')[0]
keys = [(int(s), scene) for s, scene in re.findall(r'apple-macos-27.0-([12])x-dark-standard-glass0.25", (?:scene: )?"([^"]+)"', authorised)]
# The final three object literals have their profile and scene on the same line but include `scene:`.
assert len(keys) == 15, keys
rows = []
for scale, scene in keys:
    c = cells[scale, scene]
    ref = 'b2d074d2df24' if scene == 'impulse__rrect-ml__inactive' else 'd0219cd684bf'
    if ref == 'b2d074d2df24':
        # Canonical read-8 values, not the rounded authorisation numbers.
        prior_path = CAL / 'results/generations/b2d074d2df24.json'
        prior = json.loads(prior_path.read_text())
        row = next(r for r in prior['cells'] if r['key']['profileKey'] == c['profile']
                   and r['key']['sceneId'] == scene and r['key']['web']['renderer'] == 'webgpu')
        reference = row['material']['interiorStdDevWeb']['value']
    else:
        reference = c['reference']
    mechanism = ('D: shared scatter/transmission top, plus scatter scale gain' if scene.endswith('__rrect-lg__rest')
                 else 'L: opened transmission on low-contrast mid-span; far laws have zero authority' if 'lc16' in scene
                 else 'N-active: thin edge ramp admits more of the transmitted impulse' if scene == 'impulse__capsule-button__rest'
                 else 'N-receded: thin ramp suppression, not far alpha' if 'capsule-button' in scene
                 else 'P-width: pitch-selective thick body; coarse transmission deficit' if 'checkerboard-32' in scene
                 else 'P-width: transmitted impulse energy; opposite sign from coarse thick deficit')
    rows.append(dict(scale=scale, scene=scene, partition=c['partition'], native=c['native'],
        current=c['candidate'], referenceGeneration=ref, reference=reference, B=c['B'],
        growthInB=(abs(c['candidate']-c['native'])-abs(reference-c['native']))/c['B'], mechanism=mechanism))

manifest=[]
def load(path):
    manifest.append(dict(path=str(path.relative_to(MAIN)), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float32)

def sheet(group, number):
    output=[]
    for scale, scene in group:
        c=cells[scale,scene]; profile=c['profile']
        native=MAIN/'apps/reference-apple/fixtures'/profile/f'{scene}.png'
        now=MAIN/'packages/calibration/web-captures'/profile/scene/f'{scene}__webgpu.png'
        # Generation metadata is read from the report; filenames alone are not evidence.
        report=now.parent/'report__webgpu.json'
        text=report.read_text()
        assert 'b2d074d2df24' in text and ('940384c06f73' in text if '__inactive' in scene else True), report
        oldgen='b2d074d2df24' if scene=='impulse__rrect-ml__inactive' else 'd0219cd684bf'
        prior=MAIN/'packages/calibration/web-captures-superseded'/oldgen/profile/scene/f'{scene}__webgpu.png'
        ims=[load(p) for p in (native,prior,now)]
        if scale==2:
            ims=[np.asarray(Image.fromarray(im.astype('uint8')).resize((320,200),Image.Resampling.BOX)).astype(float) for im in ims]
        median=float(np.median(ims[0]))
        ims += [np.clip((im-median)*4+128,0,255) for im in ims[:3]]
        h,w=ims[0].shape[:2]
        row=Image.new('RGB',(w*6,h+30),(28,28,28))
        for i,im in enumerate(ims): row.paste(Image.fromarray(im.astype('uint8')),(i*w,30))
        ImageDraw.Draw(row).text((4,3),f'{scale}x {scene}: Apple | {oldgen} | W49a current || same, gain 4 about native median',fill='white')
        output.append(row)
    image=Image.new('RGB',(max(x.width for x in output),sum(x.height for x in output)))
    y=0
    for row in output: image.paste(row,(0,y)); y+=row.height
    image.save(HERE/f'sheet-{number}.png')

named=sorted(k for k,c in cells.items() if c['stratum']=='P'
             or c['stratum']=='F' and c['pose']=='inactive' and c['scale']==2)
for k in named:
    cells[k]['groundingMechanism'] = ('Pressed highlight hotspot (highlight.ts radial press glow), opposite sign from ordinary photo; its separate contribution is not isolated here'
        if 'pressed' in k[1] else 'Fine-band leakage including rim/edge contribution; not a scalar-alpha repair'
        if cells[k]['stratum']=='F' else 'Insufficient transmitted spatial/chromatic contrast; group-level tone and blur composite, not opacity at the current endpoint')
allkeys=keys+named
for start in range(0,len(allkeys),5): sheet(allkeys[start:start+5],1+start//5)
(HERE/'attribution.json').write_text(json.dumps(dict(base=CURRENT,sourceCutSha256=hashlib.sha256(cut_path.read_bytes()).hexdigest(),
    authorised=rows,namedMissCells=[cells[k] for k in named],imageInputs=manifest),indent=2)+'\n')
for r in rows: print(f"{r['scale']}x {r['scene']:55} n={r['native']:.6f} ref={r['reference']:.6f} current={r['current']:.6f} {r['growthInB']:+.4f} B {r['mechanism']}")
