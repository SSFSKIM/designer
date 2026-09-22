#!/usr/bin/env python3.12
"""Native | WebGPU | CSS | absolute OKLab difference x8, before/after (§5.172).

The difference is the established grayscale magnitude ramp, not a categorical
palette. Each panel carries its one-byte-at-black amplification and actual
black-floor counts, so the nonlinear display cannot impersonate a large byte
error. Raw pixels are never resized. Both document hashes are checked per cell.
"""
import importlib.util
import json
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent
ROOT=CAL.parent.parent
BEFORE=Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
AFTER=CAL/'web-captures'
FIXTURES=ROOT/'apps/reference-apple/fixtures'
G0=CAL/'results/2026-09-22-w33-g0-rim-cut'
sys.path.insert(0,str(G0))

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

reader=module('w33_round_reader',HERE/'read-round.py')
referee=module('w33_sheet_referee',G0/'referee.py')
sealed=json.loads((HERE/'sealed-manifest.json').read_text())['documents']
output=HERE/'sheets'; output.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
lsb=float(np.linalg.norm(reader.lab(np.ones((1,1,3)))-reader.lab(np.zeros((1,1,3))))*8*255)
records=[]
declined=[]


def load(tree,profile,scene,tier,after):
    directory=tree/profile/scene
    meta=json.loads((directory/f'cell__{tier}.json').read_text())
    named=re.findall(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})',meta['capturePath'])
    assert named
    for path,digest in named:
        expected=sealed[Path(path).name]['fileSha256' if after else 'beforeFileSha256'][:12]
        assert digest==expected,(profile,scene,tier,path,digest,expected)
    return referee.rgb(directory/f'{scene}__{tier}.png'),named


cells=[]
for scheme in ('light','dark'):
    p=f'apple-macos-27.0-1x-{scheme}-standard-glass0.5'
    cells += [(p,s) for s in ('hc-text-28__rrect-lg__rest','hc-text-7__rrect-lg__rest',
        'checkerboard-8__rrect-ml__rest','checkerboard-8__rrect-lg__rest','impulse__rrect-md__rest')]
    for scale in (1,2):
        p=f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'
        cells += [(p,f'photo__{component}__rest') for component in ('rrect-lg','capsule-button')]

for profile,scene in cells:
    if not (FIXTURES/profile/(scene+'.png')).exists():
        declined.append(dict(profile=profile,scene=scene,reason='No native fixture; not substituted or inferred.'))
        continue
    n=referee.rgb(FIXTURES/profile/(scene+'.png'))
    height,width=n.shape[:2]; scale=width/320
    rect,_,_=referee.geometry(scene,scale)
    mask=referee.exterior_masks(width,height,rect,scale)[0]
    background=referee.SCENE[scene]['background']
    bg=referee.rgb(FIXTURES/'backgrounds'/f'{background}@{scale:g}x.png')
    page=Image.new('RGB',(4*width+30,2*(height+90)+45),'white')
    draw=ImageDraw.Draw(page)
    draw.text((5,5),f'{profile} / {scene}',font=font,fill='black')
    for row,(label,tree,is_after) in enumerate((('BEFORE',BEFORE,False),('AFTER',AFTER,True))):
        w,docs=load(tree,profile,scene,'webgpu',is_after)
        css,cssdocs=load(tree,profile,scene,'css',is_after)
        diff=np.minimum(255,np.linalg.norm(reader.lab(n)-reader.lab(w),axis=2)*8*255)
        delta=Image.fromarray(np.repeat(np.rint(diff).astype('uint8')[:,:,None],3,axis=2))
        y=35+row*(height+90)
        for i,(title,image) in enumerate(zip(('Native','WebGPU','CSS','WebGPU vs native: OKLab x8'),
                 (Image.fromarray(n.astype('uint8')),Image.fromarray(w.astype('uint8')),
                  Image.fromarray(css.astype('uint8')),delta))):
            x=i*(width+10)
            draw.text((x,y),label+' / '+title,font=font,fill='black')
            page.paste(image,(x,y+25))
        black=referee.black_read(n,w,bg,mask)
        cssblack=referee.black_read(n,css,bg,mask)
        max_byte=int(np.max(np.abs(n-w)[mask]))
        footer=y+height+30
        draw.text((0,footer),f'Black-floor pixels {black["pixels"]}; GPU >0 {black["aboveZero"]}, >1 {black["aboveOne"]}; '+
                  f'CSS >0 {cssblack["aboveZero"]}, >1 {cssblack["aboveOne"]}',font=small,fill='black')
        draw.text((3*(width+10),footer),f'LSB 0 -> 1: x8 = {lsb:.2f}/255',font=small,fill='black')
        draw.text((3*(width+10),footer+16),f'Actual black >0 {black["aboveZero"]}; >1 {black["aboveOne"]}',font=small,fill='black')
        draw.text((0,footer+18),'Documents: '+', '.join(f'{Path(path).name}: {sha}' for path,sha in docs),
                  font=small,fill='black')
        records.append(dict(profile=profile,scene=scene,generation=label,documents=docs,cssDocuments=cssdocs,
                            lsbBlackOneByteAmplification=lsb,black=black,cssBlack=cssblack,
                            maximumExteriorByteDifference=max_byte))
    filename=profile.replace('apple-macos-27.0-','')+'__'+scene+'.png'
    if (output/filename).exists():
        assert np.array_equal(np.asarray(Image.open(output/filename)),np.asarray(page))
    else:
        page.save(output/filename)
    print(filename)
(HERE/'sheet-readings.json').write_text(json.dumps(records,indent=1)+'\n')
(HERE/'sheet-declined.json').write_text(json.dumps(declined,indent=2)+'\n')
print('sheets',len(cells)-len(declined),'rows',len(records),'one-byte at black x8',lsb)
