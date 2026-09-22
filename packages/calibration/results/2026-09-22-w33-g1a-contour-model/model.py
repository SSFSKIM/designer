#!/usr/bin/env python3.12
"""W33 G1a identification, not a fit/seal (§5.171).

Extend G0's population, SDF and referee. No holdout image is opened by default.
Each pixel enters one angle bin (nearest of 16 normals), not an arc resample.
All fits are diagnostic in-sample lower bounds on model complexity. One byte is
an encoding-resolution comparator, NOT a measured native repeatability bar.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
G0 = HERE.parent / '2026-09-22-w33-g0-rim-cut'
sys.path.insert(0, str(G0))
import referee as g0
from rules import fitting_role, residual
ROOT = g0.ROOT


def dump(path, value):
    path.write_text('{\n'+',\n'.join(json.dumps(k)+': '+(
        '[\n'+',\n'.join(json.dumps(r,separators=(',', ':'),allow_nan=False) for r in v)+'\n]'
        if isinstance(v,list) else json.dumps(v,separators=(',', ':'),allow_nan=False))
        for k,v in value.items())+'\n}\n')


def normals(width, height, rect, radius):
    y, x = np.mgrid[:height, :width]
    dx = x + .5 - (rect[0] + rect[2])/2
    dy = y + .5 - (rect[1] + rect[3])/2
    qx = np.abs(dx) - (rect[2]-rect[0])/2 + radius
    qy = np.abs(dy) - (rect[3]-rect[1])/2 + radius
    vx, vy = np.maximum(qx, 0), np.maximum(qy, 0)
    norm = np.maximum(np.hypot(vx, vy), 1e-12)
    nx, ny = vx/norm*np.sign(dx), vy/norm*np.sign(dy)
    inside = (vx == 0) & (vy == 0)
    nx = np.where(inside, np.where(qx > qy, np.sign(dx), 0), nx)
    ny = np.where(inside, np.where(qx > qy, 0, np.sign(dy)), ny)
    return nx, ny


def klass(background):
    if background in g0.BLACK: return 'black-bearing'
    if background in ('photo', 'light-solid', 'dark-solid'): return background
    return 'mid-solids' if 'solid' in background else 'other-raster'


def angular_fit(nx, ny, delta):
    """Fit bin means with pixel weights, then report every bin's signed error.

    A law closes only if every populated bin's RGB-mean signed residual is <=1
    byte. This is a stringent model diagnostic, not a newly adopted gate.
    """
    bins = np.floor((np.arctan2(ny, nx) % (2*np.pi))/(2*np.pi/16)+.5).astype(int) % 16
    rows = []
    for b in range(16):
        m = bins == b
        if m.any(): rows.append((b, m, float(delta[m].mean())))
    y = np.array([r[2] for r in rows])
    weights = np.sqrt([int(r[1].sum()) for r in rows])
    families = [('constant', np.ones((len(nx), 1)))]
    for k in (.5, 1, 2, 4, 8):
        q = np.abs(nx)**k
        families += [(f'even-{k:g}', q[:, None]),
                     (f'isotropic-even-{k:g}', np.column_stack((np.ones(len(nx)), q)))]
    families += [('one-sided-diagonal', np.maximum(-(nx+ny)/np.sqrt(2), 0)[:, None]),
                 ('shipped-diagonal-unit-exponent', np.abs(nx+ny)[:, None]),
                 ('signed-normal', np.column_stack((np.ones(len(nx)), nx, ny)))]
    fits = []
    for name, basis in families:
        X = np.array([basis[m].mean(axis=0) for _, m, _ in rows])
        coef = np.linalg.lstsq(X*weights[:, None], y*weights, rcond=None)[0]
        err = y-X@coef
        fits.append(dict(law=name, coefficients=coef.tolist(),
            parameters=len(coef), weightedMAE=float(np.average(np.abs(err), weights=weights**2)),
            maxBinResidual=float(np.max(np.abs(err))), closesOneByte=bool(np.max(np.abs(err)) <= 1),
            bins=[dict(bin=b, angleDegrees=b*22.5, pixels=int(m.sum()), signed=float(v),
                predicted=float(v-e), residual=float(e), signedRGB=delta[m].mean(axis=0).tolist(),
                maeRGB=np.abs(delta[m]).mean(axis=0).tolist()) for (b,m,v), e in zip(rows,err)]))
    closing = [f for f in fits if f['closesOneByte']]
    best = min(closing, key=lambda f:(f['parameters'],f['weightedMAE'])) if closing else min(fits,key=lambda f:f['weightedMAE'])
    return dict(selected=best['law'], closesOneByte=bool(closing), fits=fits)


def decode(x):
    return np.where(x <= .04045, x/12.92, ((x+.055)/1.055)**2.4)


def encode(x):
    return np.where(x <= .0031308, 12.92*x, 1.055*np.maximum(x,0)**(1/2.4)-.055)


def colour_fit(n, w, nx, space, family, exponent=2):
    """Colour follows geometry: delta = affine0(W) + |nx|^k affine1(W).

    Each channel gets independent coefficients only in the tinted family.
    Coefficients are shared over ALL backdrops, spans and geometry in a bed/pose.
    No scene id or backdrop class can become a runtime switch.
    """
    x, y = w/255, n/255
    if space == 'linear': x, y = decode(x), decode(y)
    q = np.abs(nx)**exponent
    coefs = []
    if family == 'tinted-affine':
        for c in range(3):
            X = np.column_stack((x[:,c], q*x[:,c], np.ones(len(x)), q))
            coefs.append(np.linalg.lstsq(X, y[:,c]-x[:,c], rcond=None)[0])
    else:
        X = np.column_stack((x.ravel(), np.repeat(q,3)*x.ravel(),
                             np.ones(x.size), np.repeat(q,3)))
        if family == 'multiply': X = X[:,:2]
        if family == 'add': X = X[:,2:]
        coef = np.linalg.lstsq(X, (y-x).ravel(), rcond=None)[0]
        if family == 'multiply': coef = np.r_[coef,0,0]
        if family == 'add': coef = np.r_[0,0,coef]
        coefs = [coef]*3
    coef = np.array(coefs)
    pred = colour_predict(w, nx, space, coef, exponent)
    return dict(space=space, family=family, exponent=exponent,
                coefficients=coef.tolist(), **residual(n,pred))


def colour_predict(w, nx, space, coef, exponent):
    x = w/255
    if space == 'linear': x=decode(x)
    q = np.abs(nx)[:,None]**exponent
    y = np.clip(x + (coef[:,0]+q*coef[:,1])*x + coef[:,2]+q*coef[:,3],0,1)
    return 255*(encode(y) if space == 'linear' else y)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=HERE)
    ap.add_argument('--include-holdout',action='store_true',help='Post-seal only; not run in G1a')
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    old=json.loads((G0/'referee.json').read_text())
    matrix=json.loads((ROOT/'packages/calibration/results/matrix.json').read_text())['cells']
    lookup={(c['key']['profileKey'],c['key']['sceneId']):c for c in matrix if c['tier']=='texture'}
    # G0's inventory is the population authority; flag semantics match its rule.
    pairs=[(r['profile'],r['scene']) for r in old['stroke'] if '27.0' in r['profile']]
    if args.include_holdout:
        pairs += [(p,s) for p in g0.PROFILES for s in g0.SCENE if g0.ROLES[s]=='holdout'
                  and s.endswith(('__rest','__inactive'))
                  and g0.SCENES['components'][g0.SCENE[s]['component']]['kind'] in ('rrect','capsule')
                  and (p,s) in lookup]
    records=[]; radial=[]; angular=defaultdict(list); backgrounds={}
    for p,s in pairs:
        assert fitting_role(g0.ROLES[s],args.include_holdout)
        scene=g0.SCENE[s]; comp=g0.SCENES['components'][scene['component']]
        base=g0.CAPTURES/p/s
        meta=json.loads((base/'cell__webgpu.json').read_text())
        assert meta['capturePath']==lookup[(p,s)]['key']['web']['capturePath']
        for name,digest in re.findall(r'(packages/calibration/profiles/\S+\.json) sha256:([0-9a-f]{12})',meta['capturePath']):
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()[:12]==digest
        n=g0.rgb(g0.FIXTURES/p/(s+'.png')); w=g0.rgb(base/(s+'__webgpu.png'))
        h,width=n.shape[:2]; scale=width/320
        bk=(scene['background'],scale)
        if bk not in backgrounds:
            backgrounds[bk]=g0.rgb(g0.FIXTURES/'backgrounds'/f'{bk[0]}@{scale:g}x.png')
        b=backgrounds[bk]
        rect,radius,span=g0.geometry(s,scale); d,sides=g0.sdf_masks(width,h,rect,radius)
        nx,ny=normals(width,h,rect,radius)
        kind=comp['kind']; ring=(d>=0)&(d<1)
        identity=dict(profile=p,scene=s,role=g0.ROLES[s],pose=scene['state'],span=span,
                      backdropClass=klass(scene['background']),kind=kind,scale=scale)
        # The safe core is beyond the documented continuous-corner reach. It
        # separates the axial plateau from a shoulder labelled straight by G0.
        yy,xx=np.mgrid[:h,:width]
        safe=(((sides['top']|sides['bottom']) &
               (np.abs(xx+.5-(rect[0]+rect[2])/2)<(rect[2]-rect[0])/2-1.528665*radius)) |
              ((sides['left']|sides['right']) &
               (np.abs(yy+.5-(rect[1]+rect[3])/2)<(rect[3]-rect[1])/2-1.528665*radius)))
        straight=sides['top']|sides['bottom']|sides['left']|sides['right']
        for part, mask in [('straight',straight),('safe-straight',safe),('arcs',~straight)]:
            for start in range(-2,4):
                m=mask&(d>=start)&(d<start+1)
                if m.any():
                    radial.append(dict(**identity,part=part,startDevicePx=start,
                        distanceMean=float(d[m].mean()),pixels=int(m.sum()),
                        nativeRGB=n[m].mean(axis=0).tolist(), webRGB=w[m].mean(axis=0).tolist(),
                        backgroundRGB=b[m].mean(axis=0).tolist(), **{k:v for k,v in residual(n[m],w[m]).items() if k!='pixels'}))
        for part, mask in [('straight',straight),('arcs',~straight),('all',np.ones_like(ring))]:
            m=ring&mask
            if m.any(): angular[(p,scene['state'],identity['backdropClass'],span,kind,part)].append((nx[m],ny[m],n[m]-w[m]))
        records.append(dict(**identity,n=n[ring],w=w[ring],b=b[ring],nx=nx[ring],ny=ny[ring],
                            indices=np.flatnonzero(ring).tolist(),sides={k:v[ring] for k,v in sides.items()}))
    angular_rows=[]
    for key,values in sorted(angular.items()):
        x,y,delta=[np.concatenate([v[i] for v in values]) for i in range(3)]
        angular_rows.append(dict(profile=key[0],pose=key[1],backdropClass=key[2],span=key[3],kind=key[4],part=key[5],
                                 cells=len(values),**angular_fit(x,y,delta)))
    for row in angular_rows:
        for fit in row['fits']:
            if fit['law'] not in (row['selected'], 'shipped-diagonal-unit-exponent'):
                del fit['bins']
    dump(args.out/'angular.json',dict(includeHoldout=args.include_holdout,bins=16,rows=angular_rows))
    dump(args.out/'radial.json',dict(includeHoldout=args.include_holdout,rows=radial))
    models=[]; predictions=[]; strata=defaultdict(list)
    # The proposed candidate is one even angular affine family, not whichever
    # family wins each backdrop. The exponent is selected on angular bin residuals BEFORE
    # the colour fit, over .5,1,2,4,8; it is not selected to win a colour score.
    for p,pose in sorted({(r['profile'],r['pose']) for r in records}):
        rs=[r for r in records if r['profile']==p and r['pose']==pose]
        n,w,nx=[np.concatenate([r[k] for r in rs]) for k in ('n','w','nx')]
        angle_rows=[r for r in angular_rows if r['profile']==p and r['pose']==pose and r['part']=='all']
        exponent=min((.5,1,2,4,8), key=lambda k:sum(
            next(f['weightedMAE'] for f in r['fits'] if f['law']==f'isotropic-even-{k:g}')
            for r in angle_rows))
        fits=[colour_fit(n,w,nx,space,family,exponent) for space in ('encoded','linear')
              for family in ('multiply','add','affine','tinted-affine')]
        chosen=next(f for f in fits if f['space']=='encoded' and f['family']=='tinted-affine')
        models.append(dict(profile=p,pose=pose,cells=len(rs),fits=fits,candidate=chosen))
        coef=np.array(chosen['coefficients'])
        for r in rs:
            pred=colour_predict(r['w'],r['nx'],'encoded',coef,exponent)
            # Algebra prices use encoded RGBA8 targets, not sub-byte predictions.
            target=np.floor(pred+.5)
            predictions.append(dict(profile=p,scene=r['scene'],indices=r['indices'],rgb=target.astype(int).tolist()))
            for side,mask in r['sides'].items():
                if not mask.any(): continue
                key=(p,pose,r['backdropClass'],side)
                strata[key].append((r['n'][mask],r['w'][mask],target[mask],r['b'][mask],r['nx'][mask]))
    colour_rows=[]
    bounds=json.loads((G0/'tables.json').read_text())['bounds']
    for key,rs in sorted(strata.items()):
        n,w,pred,b,nx=[np.concatenate([r[i] for r in rs]) for i in range(5)]
        oldclass=key[2] if key[2] in ('photo','light-solid','black-bearing') else 'dark-or-other-solid'
        bound=next(r['bound'] for r in bounds if (r['profile'],r['pose'],r['backdropClass'],r['side'])==(key[0],key[1],oldclass,key[3]))
        # Class-local fits are optimistic diagnostics, never candidate switches.
        local=[colour_fit(n,w,nx,space,fam) for space in ('encoded','linear')
               for fam in ('multiply','add','affine','tinted-affine')]
        black=np.all(b==0,axis=1); white=np.all(b==255,axis=1)
        colour_rows.append(dict(profile=key[0],pose=key[1],backdropClass=key[2],side=key[3],cells=len(rs),
            candidate=residual(n,pred),baseline=residual(n,w),g0Ceiling=bound,
            exceedsParentCeiling=residual(n,pred)['mae']>bound,localFits=local,
            nativeMinusBlack=n[black].mean(axis=0).tolist() if black.any() else None,
            nativeMinusWhite=(n[white]-255).mean(axis=0).tolist() if white.any() else None))
    dump(args.out/'colour.json',dict(includeHoldout=args.include_holdout,models=models,strata=colour_rows))
    dump(args.out/'targets.json',dict(includeHoldout=args.include_holdout,rows=predictions))
    dump(args.out/'population.json',dict(includeHoldout=args.include_holdout,
        matrixSha256=hashlib.sha256((ROOT/'packages/calibration/results/matrix.json').read_bytes()).hexdigest(),
        g0Sha256=hashlib.sha256((G0/'referee.json').read_bytes()).hexdigest(),
        rows=[{k:v for k,v in r.items() if k not in ('n','w','b','nx','ny','indices','sides')} for r in records],
        frozenControls=[r for r in old['notchSummary'] if '26.5' in r['profile']]))
    print(json.dumps(dict(cells=len(records),angularStrata=len(angular_rows),
        angularClosed=sum(r['closesOneByte'] for r in angular_rows),radialRows=len(radial),
        colourStrata=len(colour_rows),candidateCeilingMisses=sum(r['exceedsParentCeiling'] for r in colour_rows))))


if __name__=='__main__': main()
