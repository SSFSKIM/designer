#!/usr/bin/env python3.12
"""Native | harness WebGPU | /laws/, raw pixels, both spans and poses (§5.173).

A juxtaposition, not a pixel equality claim: the stage has its own width and
coloured checker, and the 96px harness comparison is on photo. No resampling.
The entire raw stage screenshot is retained beside each cropped sheet.
"""
import hashlib
import json
from pathlib import Path
import re
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
TREE=Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
FIX=ROOT/'apps/reference-apple/fixtures'
PROFILE='apple-macos-27.0-2x-light-standard-glass0.5'
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
rows=[]
for pose in ('active','receded'):
    state='rest' if pose=='active' else 'inactive'
    for span,component,bg in [(96,'rrect-md','photo'),(160,'rrect-lg','checkerboard')]:
        scene=f'{bg}__{component}__{state}'
        directory=TREE/PROFILE/scene
        meta=json.loads((directory/'cell__webgpu.json').read_text())
        docs=re.findall(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})',meta['capturePath'])
        assert len(docs)==2
        for path,sha in docs:assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12]==sha
        panels=[Image.open(FIX/PROFILE/(scene+'.png')).convert('RGB'),
                Image.open(directory/(scene+'__webgpu.png')).convert('RGB'),
                Image.open(HERE/f'laws-shadow-{pose}-{span}.png').convert('RGB').crop((0,0,800,500))]
        sheet=Image.new('RGB',(2100,600),'white');draw=ImageDraw.Draw(sheet)
        draw.text((8,8),f'{span} CSS px, {pose}; {PROFILE} / {scene}; all panels raw DPR2 pixels',font=font,fill='black')
        x=0
        for title,image in zip(('Native harness','WebGPU harness','/laws/ shadow stage, its own ground'),panels):
            draw.text((x+4,38),title,font=font,fill='black');sheet.paste(image,(x,64));x+=image.width+10
        draw.text((5,570),'Shipped documents: '+', '.join(sha for _,sha in docs)+'; no equality claimed between different grounds/widths.',font=font,fill='black')
        name=f'demo-beside-harness-{pose}-{span}.png';sheet.save(HERE/name)
        rows.append(dict(file=name,profile=PROFILE,scene=scene,documents=docs,stageCrop=[0,0,800,500]))
        print(name)
(HERE/'demo-sheets.json').write_text(json.dumps(rows,indent=2)+'\n')
