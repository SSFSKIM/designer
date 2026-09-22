#!/usr/bin/env python3.12
"""Test the apparent stage discrepancy off retained screenshots; no browser (§5.173)."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
paths=[HERE.parent/'2026-09-21-w32-g2-landing/laws-shadow-active-160.png']
paths+=sorted(HERE.glob('laws-shadow-*.png'))
rows=[]
for path in paths:
    rgb=np.array(Image.open(path).convert('RGB'))
    # This strip is to the right of the plate, not inside its optical output.
    strip=rgb[0:500,800:920]
    assert strip.shape==(500,120,3)
    unique_rows=np.unique(strip.reshape(500,-1),axis=0).shape[0]
    samples=[dict(x=x,y=y,rgb=rgb[y,x].tolist())
             for y in (0,16,32,48,64,96,128,256,480) for x in (810,842)]
    transitions=(np.where(np.any(strip[1:]!=strip[:-1],axis=(1,2)))[0]+1).tolist()
    rows.append(dict(verticalScanlineTransitions=transitions,path=str(path.relative_to(HERE.parent)),
                     size=[rgb.shape[1],rgb.shape[0]],
                     rightStrip=[800,0,920,500],distinctScanlines=int(unique_rows),samples=samples))
    print(path.parent.name,path.name,'right-side 120x500 strip: distinct scanlines',unique_rows)
(HERE/'eye-stop.json').write_text(json.dumps(rows,indent=2)+'\n')
