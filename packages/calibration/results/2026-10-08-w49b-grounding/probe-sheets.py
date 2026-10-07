#!/usr/bin/env python3
"""Pixel comparisons for the mechanisms, not charts or another metric.

Each row is native/current/probe, then the same at a stated display gain about the native
central-region median. Original captures remain untouched; 2x is box-downsampled for display.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parent
MAIN=Path('/Users/new/Developer/GitHub/designer')
SCRATCH=Path('/Users/new/vitrea-w49/b-grounding-scratch/renders')
cases={
    'width': [('wide9-far009',s,scene) for s in (1,2) for scene in
        ('impulse__rrect-ml__inactive','impulse__rrect-lg__inactive','checkerboard-64__rrect-lg__inactive')],
    'thin': [('thin-active',1,'impulse__capsule-button__rest'),
             ('thin-active',1,'checkerboard-32__rrect-sm__rest'),
             ('thin-receded',2,'checkerboard__capsule-button__inactive'),
             ('thin-receded',2,'checkerboard__capsule-button__inactive-tint-orange'),
             ('thin-receded',2,'impulse__capsule-button__inactive')],
}
manifest=[]
for name,group in cases.items():
    output=[]
    for label,scale,scene in group:
        profile=f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
        paths=[MAIN/'apps/reference-apple/fixtures'/profile/f'{scene}.png',
               MAIN/'packages/calibration/web-captures'/profile/scene/f'{scene}__webgpu.png',
               SCRATCH/label/f'{scale}x/web-captures'/profile/scene/f'{scene}__webgpu.png']
        ims=[]
        for path in paths:
            manifest.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            im=Image.open(path).convert('RGB')
            if scale==2:im=im.resize((320,200),Image.Resampling.BOX)
            ims.append(np.asarray(im).astype(float))
        h,w=ims[0].shape[:2];gain=8 if scene.startswith('impulse') else 4
        median=float(np.median(ims[0][h//4:3*h//4,w//4:3*w//4]))
        ims += [np.clip((im-median)*gain+128,0,255) for im in ims[:3]]
        row=Image.new('RGB',(w*6,h+28),(28,28,28))
        ImageDraw.Draw(row).text((3,3),f'{scale}x {scene} | native / W49a / {label} || same at gain {gain}, native central median {median:g}',fill='white')
        for i,im in enumerate(ims):row.paste(Image.fromarray(im.astype('uint8')),(i*w,28))
        output.append(row)
    sheet=Image.new('RGB',(max(r.width for r in output),sum(r.height for r in output)))
    y=0
    for row in output:sheet.paste(row,(0,y));y+=row.height
    sheet.save(HERE/f'probe-{name}.png')
(HERE/'probe-image-inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
