#!/usr/bin/env python3.12
"""Supplement the black-cell eye at2x without inventing CSS probe captures (§5.172)."""
import importlib.util
import json
from pathlib import Path
import re
import sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent
G0=CAL/'results/2026-09-22-w33-g0-rim-cut'; sys.path.insert(0,str(G0))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
r=module('w33_2x_ref',G0/'referee.py')
lab=module('w33_2x_lab',HERE/'read-round.py').lab
seal=json.loads((HERE/'sealed-manifest.json').read_text())['documents']
old=Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
output=HERE/'sheets-2x'; output.mkdir(exist_ok=False)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
lsb=float(np.linalg.norm(lab(np.ones((1,1,3)))-lab(np.zeros((1,1,3))))*8*255)
rows=[]; declined=[]
def load(tree,profile,scene,tier,after):
    d=tree/profile/scene; png=d/f'{scene}__{tier}.png'
    if tier=='css' and not png.exists():return None,[]
    meta=json.loads((d/f'cell__{tier}.json').read_text())
    named=re.findall(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})',meta['capturePath'])
    assert named
    for path,sha in named:
        assert sha==seal[Path(path).name]['fileSha256' if after else 'beforeFileSha256'][:12]
    return r.rgb(png),named
for scheme in ('light','dark'):
    profile=f'apple-macos-27.0-2x-{scheme}-standard-glass0.5'
    for scene in ('hc-text-28__rrect-lg__rest','hc-text-7__rrect-lg__rest',
                  'checkerboard-8__rrect-ml__rest','checkerboard-8__rrect-lg__rest','impulse__rrect-md__rest'):
        native=r.FIXTURES/profile/(scene+'.png')
        if not native.exists():
            declined.append(dict(profile=profile,scene=scene,reason='No native fixture.'))
            continue
        n=r.rgb(native); height,width=n.shape[:2]
        rect,_,_=r.geometry(scene,2)
        mask=r.exterior_masks(width,height,rect,2)[0]
        bg=r.rgb(r.FIXTURES/'backgrounds'/f'{r.SCENE[scene]["background"]}@2x.png')
        page=Image.new('RGB',(width*4+30,(height+105)*2+45),'white'); draw=ImageDraw.Draw(page)
        draw.text((5,5),f'{profile} / {scene}',font=font,fill='black')
        for row,(label,tree,after) in enumerate((('BEFORE',old,False),('AFTER',CAL/'web-captures',True))):
            w,docs=load(tree,profile,scene,'webgpu',after)
            css,cssdocs=load(tree,profile,scene,'css',after)
            diff=np.minimum(255,np.linalg.norm(lab(n)-lab(w),axis=2)*8*255)
            delta=Image.fromarray(np.repeat(np.rint(diff).astype('uint8')[:,:,None],3,axis=2))
            cssimage=Image.fromarray(css.astype('uint8')) if css is not None else Image.new('RGB',(width,height),(242,242,242))
            y=40+row*(height+105)
            for i,(title,image) in enumerate(zip(('Native','WebGPU','CSS','WebGPU vs native: OKLab x8'),
                    (Image.fromarray(n.astype('uint8')),Image.fromarray(w.astype('uint8')),cssimage,delta))):
                x=i*(width+10); draw.text((x,y),label+' / '+title,font=font,fill='black');page.paste(image,(x,y+28))
            if css is None:
                draw.text((2*(width+10)+20,y+70),'Not captured on the declared 2x CSS probe bed.',font=font,fill='black')
                draw.text((2*(width+10)+20,y+100),'No pixels substituted; no new canonical row.',font=small,fill='black')
            black=r.black_read(n,w,bg,mask)
            footer=y+height+34
            draw.text((0,footer),f'Black-floor eligible {black["pixels"]}; GPU >0 {black["aboveZero"]}, >1 {black["aboveOne"]}',font=small,fill='black')
            draw.text((3*(width+10),footer),f'LSB 0 -> 1: x8 = {lsb:.2f}/255; actual >0 {black["aboveZero"]}, >1 {black["aboveOne"]}',font=small,fill='black')
            draw.text((0,footer+22),'Documents: '+', '.join(f'{Path(p).name}: {sha}' for p,sha in docs),font=small,fill='black')
            rows.append(dict(profile=profile,scene=scene,generation=label,black=black,documents=docs,
                             cssMeasured=css is not None,cssDocuments=cssdocs,lsbAmplification=lsb))
        name=profile.replace('apple-macos-27.0-','')+'__'+scene+'.png'
        page.save(output/name);print(name)
(HERE/'sheet-readings-2x.json').write_text(json.dumps(rows,indent=1)+'\n')
(HERE/'sheet-declined-2x.json').write_text(json.dumps(declined,indent=2)+'\n')
print('Supplemental sheets',len(rows)//2,'missing CSS panels',sum(not r['cssMeasured'] for r in rows))
