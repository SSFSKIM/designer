#!/usr/bin/env python3.12
"""Correct the composite exterior beside G0's immutable referee (§5.173, DL4).

This is an archival pixel reading, not a capture or another holdout read. The
box is the union's bounding box, not a union-of-SDF contour sampler. Neither
composite type enters X1. G0's overlay-only counts remain recorded beside it.
"""
import hashlib
import json
from pathlib import Path
import re
import referee as r
import numpy as np

HERE = Path(__file__).resolve().parent
matrix = json.loads((r.ROOT/'packages/calibration/results/matrix.json').read_text())['cells']


def part_box(part, scale):
    width, height = part['size']
    dx, dy = part.get('offset', [0, 0])
    return np.array([(320-width)/2+dx, (200-height)/2+dy,
                     (320+width)/2+dx, (200+height)/2+dy]) * scale


def union_geometry(component, scale):
    if component['kind'] == 'stack':
        boxes = {name: part_box(component[name], scale) for name in ('base', 'over')}
    else:
        items = component['items']
        total = sum(p['size'][0] for p in items) + component['spacing']*(len(items)-1)
        x = (320-total)/2
        boxes = {}
        for i, item in enumerate(items):
            w, h = item['size']
            boxes[str(i)] = np.array([x, (200-h)/2, x+w, (200+h)/2])*scale
            x += w + component['spacing']
    return (min(b[0] for b in boxes.values()), min(b[1] for b in boxes.values()),
            max(b[2] for b in boxes.values()), max(b[3] for b in boxes.values())), boxes


rows = []
for cell in matrix:
    profile, sid = cell['key']['profileKey'], cell['key']['sceneId']
    scene = r.SCENE[sid]
    component = r.SCENES['components'][scene['component']]
    if not (profile.startswith('apple-macos-27.0-') and '-standard-' in profile
            and cell['tier'] == 'texture' and scene['background'] in r.BLACK
            and scene['state'] in ('rest', 'inactive') and component['kind'] in ('stack', 'group')):
        continue
    directory = r.CAPTURES/profile/sid
    meta = json.loads((directory/'cell__webgpu.json').read_text())
    assert meta['capturePath'] == cell['key']['web']['capturePath']
    documents = re.findall(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})', meta['capturePath'])
    assert len(documents) == 2
    for path, sha in documents:
        assert hashlib.sha256((r.ROOT/path).read_bytes()).hexdigest()[:12] == sha
    n = r.rgb(r.FIXTURES/profile/(sid+'.png'))
    w = r.rgb(directory/(sid+'__webgpu.png'))
    height, width = n.shape[:2]
    scale = width/320
    b = r.rgb(r.FIXTURES/'backgrounds'/f'{scene["background"]}@{scale:g}x.png')
    old_rect = r.geometry(sid, scale)[0]
    rect, parts = union_geometry(component, scale)
    old_masks = r.exterior_masks(width, height, old_rect, scale)
    masks = r.exterior_masks(width, height, rect, scale)
    old = {name:r.black_read(n,w,b,m) for name,m in zip(('integer','analytic'),old_masks)}
    new = {name:r.black_read(n,w,b,m) for name,m in zip(('integer','analytic'),masks)}
    hits = old_masks[0] & np.all(n==0,axis=2) & np.all(b==0,axis=2) & np.any(w>0,axis=2)
    pixels=[]
    for y,x in zip(*np.where(hits)):
        inside = {name:bool(box[0]<=x+.5<box[2] and box[1]<=y+.5<box[3])
                  for name,box in parts.items()}
        pixels.append(dict(deviceXY=[int(x),int(y)], rgb=w[y,x].tolist(), inside=inside))
    rows.append(dict(profile=profile, scene=sid, role=r.ROLES[sid],
                     legacy=old, union=new, unionBoxCss=[float(v/scale) for v in rect], pixels=pixels))
assert rows
misses=[row for row in rows if row['pixels']]
assert len(misses)==4 and sum(len(row['pixels']) for row in misses)==5
assert all(pixel['inside']['base'] and not pixel['inside']['over']
           for row in misses for pixel in row['pixels'])
assert all(row['union'][mask]['aboveZero']==row['union'][mask]['aboveOne']==0
           for row in rows for mask in ('integer','analytic'))
(HERE/'referee-union.json').write_text(json.dumps(dict(atDocuments='shipped',
    archivalIncludesHoldout=True, adopted=False, cells=rows),indent=2)+'\n')
print('Composite cells',len(rows),'legacy missed cells',len(misses),'legacy missed pixels',
      sum(len(row['pixels']) for row in misses),'union >0 and >1: 0 on every cell and both masks')
for row in misses: print(json.dumps(row))
