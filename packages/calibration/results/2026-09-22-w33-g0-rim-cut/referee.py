#!/usr/bin/env python3.12
"""W33 G0: archival native census and non-holdout RGB referees (§5.170).

The historical census opens NATIVE fixtures only, including holdout. All web
reads pass fitting_role first. No output is written outside --out; captures
are read-only. The black-floor integer convention uses offset >= 2 CSS px
from the declared box (centres 1.5 CSS px out at 1x); analytic distance >= 2
is tabled separately. Corners use the exact rounded-rect SDF at pixel centres:
the band [k-1,k) is a one-device-pixel normal-distance shell, not a box corner.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
import re
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXTURES = ROOT / 'apps/reference-apple/fixtures'
CAPTURES = Path(os.environ.get('VITREA_WEB_CAPTURES', ROOT / 'packages/calibration/web-captures'))
SCENES = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())
SCENE = {s['id']: s for s in SCENES['scenes']}
ROLES = {s: role for role, ids in SCENES['split'].items() if not role.startswith('$') for s in ids}
BLACK = ('checkerboard', 'checkerboard-4', 'checkerboard-8', 'checkerboard-32',
         'checkerboard-64', 'impulse', 'hc-text', 'hc-text-7', 'hc-text-28')
PROFILES = [p['key'] for p in SCENES['profiles'] if '27.0' in p['key']
            and '-increased-contrast-glass' not in p['key']]
CONTROLS = ['apple-macos-26.5-1x-light-standard', 'apple-macos-26.5-1x-dark-standard']


from rules import fitting_role, residual


def rgb(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.float64)


def geometry(scene, scale):
    c = SCENES['components'][SCENE[scene]['component']]
    # The census's legacy bounding box names the overlay for a stack. The
    # stroke referee declines composite geometry explicitly, rather than
    # pretending its exposed contours are one rounded rectangle.
    if c['kind'] == 'stack':
        c = c['over']
    if c['kind'] == 'group':
        size = (sum(x['size'][0] for x in c['items']) + c['spacing'] * (len(c['items'])-1),
                max(x['size'][1] for x in c['items']))
    else:
        size = c['size']
    off = c.get('offset', [0, 0])
    x0 = (SCENES['canvas']['width'] - size[0]) / 2 + off[0]
    y0 = (SCENES['canvas']['height'] - size[1]) / 2 + off[1]
    rect = tuple(v * scale for v in (x0, y0, x0 + size[0], y0 + size[1]))
    radius = c.get('radius', size[1]/2) * scale
    return rect, radius, min(size)


def exterior_masks(width, height, rect, scale):
    y, x = np.mgrid[:height, :width]
    x0, y0, x1, y1 = rect
    # Integer distance agrees with the predecessor: first outside pixel is 1.
    integer = np.maximum.reduce((x0-x, x-(x1-1), y0-y, y-(y1-1))) >= 2*scale
    qx = np.maximum(np.maximum(x0-(x+.5), (x+.5)-x1), 0)
    qy = np.maximum(np.maximum(y0-(y+.5), (y+.5)-y1), 0)
    analytic = np.hypot(qx, qy) >= 2*scale
    return integer, analytic


def sdf_masks(width, height, rect, radius):
    y, x = np.mgrid[:height, :width]
    x0, y0, x1, y1 = rect
    dx = x+.5-(x0+x1)/2
    dy = y+.5-(y0+y1)/2
    qx = np.abs(dx)-(x1-x0)/2+radius
    qy = np.abs(dy)-(y1-y0)/2+radius
    d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx,qy),0)-radius
    # A point on a corner arc projects onto its centre along the radial normal.
    # Reading SDF shells assigns each raster pixel once; angular resampling
    # would duplicate pixels close to the axes and overweight them.
    corner = (qx > 0) & (qy > 0)
    masks = {}
    for name, signx, signy in [('tl',-1,-1),('tr',1,-1),('bl',-1,1),('br',1,1)]:
        masks['corner-'+name] = corner & (dx*signx>0) & (dy*signy>0)
    masks.update(top=(~corner)&(np.abs(dx) <= (x1-x0)/2-radius)&(dy<0),
                 bottom=(~corner)&(np.abs(dx) <= (x1-x0)/2-radius)&(dy>0),
                 left=(~corner)&(np.abs(dy) <= (y1-y0)/2-radius)&(dx<0),
                 right=(~corner)&(np.abs(dy) <= (y1-y0)/2-radius)&(dx>0))
    return d, masks


def black_read(native, web, background, mask):
    backdrop = mask & np.all(background == 0, axis=2)
    eligible = backdrop & np.all(native == 0, axis=2)
    w = web.max(axis=2)
    return dict(backdropBlack=int(backdrop.sum()), nativeNonzero=int((backdrop & np.any(native>0,axis=2)).sum()),
                pixels=int(eligible.sum()), aboveZero=int((eligible & (w>0)).sum()),
                aboveOne=int((eligible & (w>1)).sum()),
                fraction=float((eligible & (w>0)).sum()/eligible.sum()) if eligible.any() else None)


def summarize_black(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r['profile'],r['pose'],r['span'])].append(r)
    out=[]
    for (p,pose,span), rs in sorted(groups.items()):
        totals={k:sum(r['integer'][k] for r in rs) for k in ('pixels','aboveZero','aboveOne','backdropBlack','nativeNonzero')}
        out.append(dict(profile=p,pose=pose,span=span,cells=len(rs),**totals,
                        fraction=totals['aboveZero']/totals['pixels'] if totals['pixels'] else None))
    return out


def family_models(n, w):
    """Diagnostic fits only, never material fits: scalar neutral families in both spaces.

    A two-parameter neutral affine includes neutral source-over (1-a)*w+a*c.
    A signed constant addition is deliberately not silently clipped before the
    residual: physical candidate output is clipped in each space, then encoded.
    """
    decode=lambda x:np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
    encode=lambda x:np.where(x<=.0031308,12.92*x,1.055*np.maximum(x,0)**(1/2.4)-.055)
    results={}
    for space in ('encoded','linear'):
        x=w/255; y=n/255
        if space=='linear': x,y=decode(x),decode(y)
        for family in ('multiply','add','affine','tinted-affine'):
            if family=='multiply':
                slope=float((x*y).sum()/(x*x).sum()); bias=np.zeros(3)
            elif family=='add': slope=1.; bias=np.repeat((y-x).mean(),3)
            elif family=='affine':
                slope,b=np.linalg.lstsq(np.column_stack((x.ravel(),np.ones(x.size))),y.ravel(),rcond=None)[0]
                bias=np.repeat(b,3)
            else:
                xc=x-x.mean(axis=0); yc=y-y.mean(axis=0)
                slope=float((xc*yc).sum()/(xc*xc).sum()); bias=y.mean(axis=0)-slope*x.mean(axis=0)
            pred=np.clip(slope*x+bias,0,1)
            if space=='linear': pred=encode(pred)
            results[space+'-'+family]=dict(slope=float(slope),bias=bias.tolist(),**residual(n,pred*255))
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE)
    parser.add_argument('--include-holdout',action='store_true',help='Post-seal G1 use ONLY')
    args=parser.parse_args()
    matrix=json.loads((ROOT/'packages/calibration/results/matrix.json').read_text())['cells']
    if not CAPTURES.is_dir():
        raise SystemExit('Capture tree absent: set VITREA_WEB_CAPTURES; an empty referee is not a pass')
    for cell in matrix:
        p=cell['key']['profileKey']; sid=cell['key']['sceneId']
        if p not in PROFILES or cell['tier']!='texture' or not fitting_role(ROLES[sid],args.include_holdout):
            continue
        directory=CAPTURES/p/sid
        if not (directory/(sid+'__webgpu.png')).is_file():
            raise SystemExit(f'Missing fitting capture: {p}/{sid}')
        capture=json.loads((directory/'cell__webgpu.json').read_text())
        if capture['capturePath']!=cell['key']['web']['capturePath']:
            raise SystemExit(f'Capture/matrix generation mismatch: {p}/{sid}')
        for name,digest in re.findall(r'(packages/calibration/profiles/\S+\.json) sha256:([0-9a-f]{12})',capture['capturePath']):
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()[:12]!=digest:
                raise SystemExit(f'Unshipped document: {name}')
    # Archival census deduplicates tier. It reads no WEB pixel, and its holdout
    # rows can never enter any fitting result below.
    pairs=sorted({(c['key']['profileKey'],c['key']['sceneId']) for c in matrix if c['key']['profileKey'] in PROFILES})
    census=[]
    census_variants=dict(farExclusive=0,farInclusive=0,farInwardOne=0,expandedOne=0)
    for p,s in pairs:
        if SCENE[s]['state'] not in ('rest','inactive'): continue
        n=rgb(FIXTURES/p/(s+'.png')); h,w=n.shape[:2]; scale=w/320
        rect,_,span=geometry(s,scale); y,x=np.mgrid[:h,:w]; x0,y0,x1,y1=rect
        ext=(x<x0)|(x>=x1)|(y<y0)|(y>=y1)
        native_black=np.all(n==0,axis=2)
        count=int((ext & native_black).sum())
        variants=dict(farExclusive=ext,
            farInclusive=(x<x0)|(x>x1)|(y<y0)|(y>y1),
            farInwardOne=(x<x0)|(x>=x1-1)|(y<y0)|(y>=y1-1),
            expandedOne=(x<x0-1)|(x>=x1+1)|(y<y0-1)|(y>=y1+1))
        for name,mask in variants.items(): census_variants[name]+=int((mask&native_black).sum())
        census.append(dict(profile=p,scene=s,role=ROLES[s],span=span,pixels=count))
    # Reproduce the memo's all-role NATIVE lift census without opening held-out
    # web images. Composite geometry is outside that historical census.
    native_lift=[]
    for p in PROFILES+CONTROLS:
        for scene in SCENES['scenes']:
            sid=scene['id']; comp=SCENES['components'][scene['component']]
            if scene['state'] not in ('rest','inactive') or comp['kind'] not in ('rrect','capsule'):
                continue
            if scene['background'] not in BLACK: continue
            npth=FIXTURES/p/(sid+'.png')
            if not npth.exists() or not (CAPTURES/p/sid/(sid+'__webgpu.png')).exists(): continue
            n=rgb(npth); h,w=n.shape[:2]; scale=w/320
            b=rgb(FIXTURES/'backgrounds'/f'{scene['background']}@{scale:g}x.png')
            rect,_,_=geometry(sid,scale); mask=exterior_masks(w,h,rect,scale)[0]&np.all(b==0,axis=2)
            if mask.any():
                native_lift.append(dict(profile=p,scene=sid,role=ROLES[sid],pixels=int(mask.sum()),
                    nonzero=int((mask&np.any(n>0,axis=2)).sum())))
    bg_cache={}
    black=[]; strokes=[]; populations=[]; declined=[]; models=defaultdict(lambda:[[],[]])
    for p in PROFILES+CONTROLS:
        available=[]
        for s, scene in SCENE.items():
            npth=FIXTURES/p/(s+'.png'); wp=CAPTURES/p/s/(s+'__webgpu.png')
            if not npth.exists() or not wp.exists(): continue
            if scene['state'] not in ('rest','inactive'): continue
            available.append(s)
        for pose in ('rest','inactive'):
            # Detector population is untinted literal rest/inactive, not all
            # scenes whose resolved state happens to be rest.
            ids=[s for s in available if s.endswith('__'+pose) and SCENES['components'][SCENE[s]['component']]['kind'] in ('rrect','capsule')]
            populations.append(dict(profile=p,pose=pose,available=len(ids),
                fitting=sum(fitting_role(ROLES[s],False) for s in ids),
                holdout=[s for s in ids if ROLES[s]=='holdout']))
        for s in available:
            if not fitting_role(ROLES[s],args.include_holdout): continue
            scene=SCENE[s]; comp=SCENES['components'][scene['component']]
            n=rgb(FIXTURES/p/(s+'.png')); w=rgb(CAPTURES/p/s/(s+'__webgpu.png'))
            assert n.shape==w.shape
            h,width=n.shape[:2]; scale=width/320
            key=(scene['background'],scale)
            if key not in bg_cache: bg_cache[key]=rgb(FIXTURES/'backgrounds'/f'{key[0]}@{scale:g}x.png')
            b=bg_cache[key]; rect,radius,span=geometry(s,scale)
            identity=dict(profile=p,scene=s,role=ROLES[s],span=span,pose=scene['state'],background=scene['background'])
            if scene['background'] in BLACK:
                masks=exterior_masks(width,h,rect,scale)
                readings=[black_read(n,w,b,m) for m in masks]
                if readings[0]['backdropBlack']:
                    black.append(dict(**identity,integer=readings[0],analytic=readings[1]))
            if comp['kind'] not in ('rrect','capsule'):
                declined.append(dict(profile=p,scene=s,reason='Composite geometry; not an exact single rounded-rect SDF'))
                continue
            if not s.endswith(('__rest','__inactive')): continue
            d,sides=sdf_masks(width,h,rect,radius)
            klass=('black-bearing' if scene['background'] in BLACK else
                   'photo' if scene['background']=='photo' else
                   'light-solid' if scene['background']=='light-solid' else 'dark-or-other-solid')
            rings=[]
            for offset in range(1,7):
                mask=(d>=offset-1)&(d<offset)
                pieces={side:residual(n[mask&m],w[mask&m]) for side,m in sides.items() if (mask&m).any()}
                # The predecessor's straight-only statistic remains beside the
                # widened SDF-shell reading, never substituted for its corners.
                straight=np.zeros((h,width),dtype=bool)
                for side,m in sides.items():
                    if not side.startswith('corner-'): straight |= m
                rings.append(dict(offset=offset,all=residual(n[mask],w[mask]),
                    straight=residual(n[mask&straight],w[mask&straight]),strata=pieces))
            # The model-free detector is the difference of ring luma means,
            # which is a DETECTOR, never the referee's absolute RGB statistic.
            lum=np.array([.2126,.7152,.0722])
            means=lambda a:[float((a[(d>=k)&(d<k+1)]@lum).mean()) for k in (-1,0,1)]
            nm,wm=means(n),means(w)
            notch=lambda v:v[1]-min(v[0],v[2])
            ring=(d>=0)&(d<1)
            row=dict(**identity,backdropClass=klass,offsets=rings,nativeNotch=notch(nm),webNotch=notch(wm),
                     nativeRing=nm,webRing=wm,backdropRingRGB=b[ring].mean(axis=0).tolist())
            strokes.append(row)
            if p in PROFILES:
                for label in (p+' / '+scene['state']+' / '+klass, p+' / '+scene['state']+' / all'):
                    models[label][0].append(n[ring]); models[label][1].append(w[ring])
                for side,m in sides.items():
                    mask=ring&m
                    if not mask.any(): continue
                    label=p+' / '+scene['state']+' / '+klass+' / '+side
                    models[label][0].append(n[mask]); models[label][1].append(w[mask])
    summaries=[]
    for p in PROFILES+CONTROLS:
        for pose in ('rest','inactive'):
            rs=[r for r in strokes if r['profile']==p and r['pose']==pose]
            if rs:
                summaries.append(dict(profile=p,pose=pose,cells=len(rs),nativeMedian=float(np.median([r['nativeNotch'] for r in rs])),
                    webMedian=float(np.median([r['webNotch'] for r in rs])),nativeBelowMinus5=sum(r['nativeNotch'] < -5 for r in rs),
                    webBelowMinus5=sum(r['webNotch'] < -5 for r in rs)))
    model_results={k:family_models(np.concatenate(v[0]),np.concatenate(v[1])) for k,v in models.items()}
    artifact=dict(schema=1,includeHoldout=args.include_holdout,captureTree=str(CAPTURES),
        matrixSha256=hashlib.sha256((ROOT/'packages/calibration/results/matrix.json').read_bytes()).hexdigest(),
        censusConventions=census_variants,nativeLiftInventory=native_lift,census=census,censusSummary=dict(cells=len(census),withBlack=sum(r['pixels']>0 for r in census),
            pixels=sum(r['pixels'] for r in census),holdoutWithBlack=sum(r['pixels']>0 and r['role']=='holdout' for r in census)),
        blackBackdrops=list(BLACK),black=black,blackSummary=summarize_black(black),
        populations=populations,stroke=strokes,notchSummary=summaries,models=model_results,declined=declined,
        targets=dict(blackFraction=0,aboveOne=0))
    args.out.mkdir(parents=True,exist_ok=True)
    # One row per line keeps per-cell evidence inspectable without millions of
    # indentation-only lines. Values are never rounded in the evidence.
    (args.out/'referee.json').write_text('{\n'+',\n'.join(
        json.dumps(k)+': '+ ('[\n'+',\n'.join(json.dumps(r) for r in v)+'\n]'
                            if isinstance(v,list) else json.dumps(v))
        for k,v in artifact.items())+'\n}\n')
    print('NATIVE-ONLY archival census',artifact['censusSummary'])
    print('Full-exterior census conventions',census_variants)
    print('Holdout web pixels included in referees:',args.include_holdout)
    for p in populations: print('population',p)
    for s in summaries: print('notch',s)
    for r in black:
        if r['integer']['aboveOne']: print('above-one baseline',r['profile'],r['scene'],r['integer'],r['analytic'])
    for p in CONTROLS+PROFILES:
        rs=[r for r in black if r['profile']==p]
        print('black',p,'cells',len(rs),'Apple nonzero cells',sum(r['integer']['nativeNonzero']>0 for r in rs),
              'pixels',sum(r['integer']['backdropBlack'] for r in rs))

if __name__=='__main__': main()
