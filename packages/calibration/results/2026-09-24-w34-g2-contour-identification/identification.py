#!/usr/bin/env python3.12
"""W34 G2 analysis through G0's role reader (§5.176, clauses 5–6).

Coefficients are fit on calibration only. Every residual takes channelwise
absolute values before bin reduction. Signed profiles remain diagnostics.
Minimax means pixelwise L-infinity in the declared composition space, not a
signed-bin minimax. The encoded-byte referee is identical for both spaces.
"""
import argparse
import base64
from collections import defaultdict
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image
from scipy.optimize import linprog
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
G0 = HERE.parent / '2026-09-23-w34-g0-contour-bed'
G1 = HERE.parent / '2026-09-23-w34-g1-contour-sitting'
sys.path.insert(0, str(G0))
import instrument as I
spec = importlib.util.spec_from_file_location('w34wave', G0 / 'wave.py')
W = importlib.util.module_from_spec(spec); spec.loader.exec_module(W)
POWERS = [.5, 1., 2., 4., 8.]


def save(path, value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    if str(path).endswith('.gz'):
        raw = gzip.compress(raw, mtime=0)
    path = Path(path)
    if path.exists():
        raise ValueError('Refuse to replace recorded output: ' + str(path))
    path.write_bytes(raw)


def decode(x):
    return np.where(x <= .04045, x/12.92, ((x+.055)/1.055)**2.4)


def encode(x):
    return np.where(x <= .0031308, 12.92*x, 1.055*np.maximum(x, 0)**(1/2.4)-.055)


def fit(X, y, method):
    if method == 'least-squares':
        return np.linalg.lstsq(X, y, rcond=None)[0]
    # Constraint generation solves the full pixelwise LP, checking every
    # omitted constraint before termination. It is not a sampled minimax.
    scale = np.maximum(np.max(np.abs(X), axis=0), 1e-12)
    A = X / scale
    selected = set(np.linspace(0, len(y)-1, min(len(y), 256), dtype=int))
    for _ in range(100):
        ids = np.array(sorted(selected))
        inequalities = np.vstack((np.c_[A[ids], -np.ones(len(ids))],
                                  np.c_[-A[ids], -np.ones(len(ids))]))
        result = linprog(np.r_[np.zeros(X.shape[1]), 1.], A_ub=inequalities,
                         b_ub=np.r_[y[ids], -y[ids]],
                         bounds=[(None, None)]*X.shape[1]+[(0, None)], method='highs')
        if not result.success:
            raise RuntimeError(result.message)
        error = np.abs(A@result.x[:-1]-y)
        if error.max() <= result.x[-1]+1e-7:
            return result.x[:-1]/scale
        selected.update(np.argsort(error)[-32:].tolist())
    raise RuntimeError('Minimax did not satisfy every pixel constraint')


def body_coordinates(x,y,scale):
    """Evaluate G0's integer-index affine fit at geometric subpixel positions.

    Index x names the observation centred at geometric x+.5. Equivalently,
    converting its coefficients subtracts betaX/(2*w)+betaY/(2*h) from beta0.
    The frozen coefficients are not mutated; both quadrature paths and the
    compact body moments use this same coordinate conversion.
    """
    return (x-.5)/(320*scale)-.5,(y-.5)/(200*scale)-.5


def coverage(pixels, component, scale, translation, samples=64):
    """Integrate disjoint body and outside one-device-pixel band at subpixels.

    Continuous shapes use G0's flattened supplied segments; a nearest-midpoint
    tree supplies a conservative candidate set. Midpoint radius includes the
    longest half-segment, then exact point-to-segment distance selects the path.
    """
    offsets = (np.arange(samples)+.5)/samples
    oy, ox = np.meshgrid(offsets, offsets, indexing='ij')
    ox, oy = ox.ravel(), oy.ravel()
    origin = np.array(component['suppliedPaths'][0]['frameOrigin'])*scale+translation
    size = np.array(component['size'])*scale
    rect = [*origin, *(origin+size)]
    circular = component['kind'] == 'capsule-circular'
    if not circular:
        segs = I.segments(component['suppliedPaths'][0]['elements'])
        # Split straight segments too: midpoint candidate queries must not miss
        # a long side whose midpoint is far from the nearest endpoint.
        segments = []
        for a, b, _ in segs:
            a, b = a*scale+origin, b*scale+origin
            n = max(1, int(np.ceil(np.linalg.norm(b-a)/.25)))
            points = np.linspace(a, b, n+1)
            segments.extend(zip(points[:-1], points[1:]))
        starts = np.array([a for a,b in segments]); ends = np.array([b for a,b in segments])
        vectors = ends-starts; lengths = np.sum(vectors*vectors, axis=1)
        tree = cKDTree((starts+ends)/2)
    output = {'body':[], 'band':[], 'bodyX':[], 'bodyY':[]}
    for k in POWERS:
        output['q'+str(k)] = []
    for chunk in np.array_split(pixels, max(1, int(np.ceil(len(pixels)/64)))):
        x = chunk[:,0,None]+ox; y = chunk[:,1,None]+oy
        if circular:
            d, nx, ny, _ = I.stadium(x, y, rect, min(size)/2)
        else:
            points = np.c_[x.ravel(), y.ravel()]
            # Segments are at most .25px; nearest 16 includes adjacent samples
            # across both smooth joins and the capsule's tangent joins.
            _, index = tree.query(points, k=16)
            a = starts[index]; v = vectors[index]
            t = np.clip(np.sum((points[:,None,:]-a)*v, axis=2)/lengths[index], 0, 1)
            delta = points[:,None,:]-(a+t[:,:,None]*v)
            dist = np.sum(delta*delta, axis=2)
            nearest = np.argmin(dist, axis=1); ids=np.arange(len(points))
            vn = v[ids,nearest]; normal=np.c_[vn[:,1],-vn[:,0]]/np.linalg.norm(vn,axis=1)[:,None]
            sign = np.sign(np.sum(delta[ids,nearest]*normal,axis=1))
            d=(np.sqrt(dist[ids,nearest])*sign).reshape(x.shape)
            nx=normal[:,0].reshape(x.shape); ny=normal[:,1].reshape(x.shape)
        body = d<0; band=(d>=0)&(d<1)
        output['body'].extend(body.mean(axis=1)); output['band'].extend(band.mean(axis=1))
        bx,by=body_coordinates(x,y,scale)
        output['bodyX'].extend((body*bx).mean(axis=1))
        output['bodyY'].extend((body*by).mean(axis=1))
        for k in POWERS:
            output['q'+str(k)].extend((band*np.abs(nx)**k).mean(axis=1))
    return {k:np.array(v) for k,v in output.items()}


def bin_residual(native, predicted, uncertainty, bar):
    errors = np.abs(native-predicted)
    mae = errors.mean(axis=0)
    interval = np.maximum(errors-uncertainty, 0).mean(axis=0)
    admissible = len(native)>=4
    return dict(pixels=len(native), admissible=admissible,
                signedRGB=(native-predicted).mean(axis=0).tolist(), maeRGB=mae.tolist(),
                intervalMAERGB=interval.tolist(), nuisanceWidthRGB=(2*uncertainty).mean(axis=0).tolist(),
                barRGB=np.asarray(bar).tolist(), tauRGB=np.maximum(1,bar).tolist(),
                status=('unmeasured: population below four' if not admissible else
                        'point compatible' if np.all(mae<=np.maximum(1,bar)) else 'point fails'))


def extract(wave, roles=('calibration','validation'), authorization=None):
    repeat = wave.reader(G1/'repeat', roles, authorization)
    probe = wave.reader(G1/'probe', roles, authorization)
    bars = {r['cell']:r for r in json.loads((G1/'bar.json').read_text())}
    held_bars = wave.reader(G1, roles, authorization) if 'holdout' in roles else None
    records=[]; controls={}; geo_cache={}
    for cell, kind in sorted(repeat.entries):
        if kind!='crop' or cell.split('/',1)[1] not in repeat.allowed:
            continue
        crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
        run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
        payload=I.unpack(base64.b64decode(crop['states'][run['state']]))
        # Materialized native bytes, with the repeat archive's fixed masks and
        # captured dependencies. No plurality-selected bar is recomputed here.
        payload['rgb']=np.asarray(Image.open(io.BytesIO(probe.read(cell,'png'))).convert('RGB'))
        component=payload['component']; scale=payload['scale']; align=payload['alignment']
        n=payload['rgb'].astype(float); back=payload['background'].astype(float)
        h,w=n.shape[:2]
        key=json.dumps([component,scale,align],sort_keys=True)
        if key not in geo_cache:
            d,nx,ny,arc=I.geometry(w,h,component,scale,align['translationDevicePx'])
            mask=(d>=-2)&(d<4); yy,xx=np.where(mask)
            masks=[(k,m[mask]) for k,m in I.strata(d,nx,ny,arc)]
            # Only circular controls have a physical forward fit. Continuous
            # supplied-path bins are still read, with no circular substitution.
            cov=coverage(np.c_[xx,yy],component,scale,align['translationDevicePx']) if component['kind']=='capsule-circular' else None
            geo_cache[key]=(d,nx,ny,arc,mask,xx,yy,masks,cov)
        d,nx,ny,arc,mask,xx,yy,masks,cov=geo_cache[key]
        body=I.body_baseline(n,d,payload['backgroundKind'])
        B=np.tile(body['betaRGB'],(len(xx),1))
        if 'coefficients' in body:
            B=np.clip(np.c_[np.ones(len(xx)),xx/w-.5,yy/h-.5]@np.array(body['coefficients']),0,255)
        profile,sid=cell.split('/',1); scene=wave.scenes[sid]
        bar=(json.loads(held_bars.read(cell,'normal-bar')) if held_bars else bars[cell])
        bmap={(r['part'],r['shell'],r['bin']):r for r in bar['bins']}
        for k,m in masks:
            assert bmap[k]['pixels']==int(m.sum()), (cell,k,'bar mask mismatch')
        gy,gx=np.gradient(back.mean(axis=2))
        notch=[]
        for part,pm in [('arc',arc),('straight',~arc)]:
            means=[]
            for shell in [-1,0,1]:
                v=n[pm&(d>=shell)&(d<shell+1)]
                means.append(float((v@np.array([.2126,.7152,.0722])).mean()) if len(v) else None)
            notch.append(dict(part=part,shellLuma=means,
                              notch=None if None in means else means[1]-min(means[0],means[2])))
        control_key=json.dumps([profile,scene['state'],scene['component']],sort_keys=True)
        if control_key not in controls:
            white=np.full_like(payload['opaque'],255); black=np.zeros_like(white)
            controls[control_key]=dict(cell=cell,glassAlignment=align,body=body,
                opaque=[I.fit_alignment(payload[name],bg,component,scale,True,space)
                        for name,bg in [('opaque',white),('opaqueInverse',black)]
                        for space in ['encoded','linear']],
                cubicErrorCSSPx=.006*min(component['size'])/2/22 if cov is not None else None)
        records.append(dict(cell=cell,role=wave.roles[sid],profile=profile,pose=scene['state'],
            kind=component['kind'],backgroundKind=payload['backgroundKind'],component=component,
            scale=scale,alignment=align,n=n[mask],D=back[mask],B=B,body=body,d=d[mask],
            nx=nx[mask],ny=ny[mask],gx=gx[mask],gy=gy[mask],masks=masks,bar=bmap,
            cov=cov,xy=np.c_[xx,yy],notch=notch))
        print('extracted',len(records),cell,flush=True)
    return records,controls


def angular_basis(r, family, power=2., angle=0., reference=False):
    x,y=r['nx'],r['ny']; one=np.ones(len(x));q=np.abs(x)**power
    if family=='constant': cols=[one]
    elif family=='even': cols=[q]
    elif family=='isotropic-even': cols=[one,q]
    elif family=='one-sided-diagonal':cols=[np.maximum(-(x+y)/np.sqrt(2),0)]
    elif family=='shipped-diagonal':cols=[np.abs(x+y)]
    elif family=='signed-normal':cols=[one,x,y]
    elif family=='two-term-even':cols=[np.abs(x)**power,np.abs(y)**power]
    elif family=='rotated-axis':cols=[one,np.abs(x*np.cos(angle)+y*np.sin(angle))**power]
    elif family=='isotropic-two-axis':
        if reference:
            v=x*np.cos(angle)+y*np.sin(angle);u=-x*np.sin(angle)+y*np.cos(angle)
            cols=[one,np.abs(v)**power,np.abs(u)**power]
        else:cols=[one,q,np.abs(y)**power]  # Original G2 axis-fixed variant.
    elif family in ['gradient','colour-gradient']:
        gx,gy=r['gx']/255,r['gy']/255;dot=x*gx+y*gy
        cols=[one,q,gx,gy,dot,np.abs(dot)]
        if family=='colour-gradient':
            colour=r['D'].mean(axis=1)/255
            cols=([one,q,colour,q*colour,gx,gy,dot,np.abs(dot)] if reference else
                  [*cols,colour,q*colour])
    else:raise ValueError(family)
    return np.column_stack(cols)


def family_specs():
    old=[]
    for family in ['constant','even','isotropic-even','one-sided-diagonal','shipped-diagonal',
                   'signed-normal','two-term-even','rotated-axis','isotropic-two-axis',
                   'gradient','colour-gradient']:
        old.append(dict(name=family,stage='W33-first',space='encoded'))
    new=[]
    for space in ['encoded','linear']:
        for family in ['coverage-add','coverage-multiply','coverage-screen','coverage-affine',
                       'coverage-even-affine','body-forward-affine','body-forward-even-affine']:
            new.append(dict(name=family,stage='new-axes',space=space))
    return old+new


def design(r, spec, channel):
    name=spec['name'];space=spec['space']
    reference=spec.get('w33Reference',False)
    power=spec.get('power',4. if reference and name in ['gradient','colour-gradient'] else 2.)
    D=r['D']/255;B=r['B']/255
    if space=='linear':D,B=decode(D),decode(B)
    if spec['stage']=='W33-first':
        X=angular_basis(r,name,power,spec.get('angle',0.),reference)
        support=((r['d']>=0)&(r['d']<1)).astype(float)
        return X*support[:,None],D[:,channel]
    cov=r['cov'];g=cov['band'];a=cov['body'];q=cov['q'+str(power)]
    base=D[:,channel]
    if spec.get('exactBody'):
        base=r['exactBaselines'][space][:,channel]
    elif name.startswith('body-forward'):
        base=base+a*(B[:,channel]-base)
        if space=='encoded' and 'coefficients' in r['body']:
            c=np.array(r['body']['coefficients'])[:,channel]/255
            base=D[:,channel]*(1-a)+a*c[0]+cov['bodyX']*c[1]+cov['bodyY']*c[2]
    z=D[:,channel]
    if name=='coverage-add':cols=[g]
    elif name=='coverage-multiply':cols=[g*z]
    elif name=='coverage-screen':cols=[g*(1-z)]
    elif 'even' in name:cols=[g*z,g,q*z,q]
    else:cols=[g*z,g]
    return np.column_stack(cols),base


def predict(r,spec,coefficients):
    channels=[]
    for c in range(3):
        X,base=design(r,spec,c)
        value=np.clip(base+X@np.array(coefficients[c]),0,1)
        if spec['space']=='linear':value=encode(value)
        channels.append(np.floor(value*255+.5))
    return np.column_stack(channels)


def fit_spec(records,spec,method):
    coefficients=[];objective=0.
    for c in range(3):
        xs=[];ys=[]
        for r in records:
            X,base=design(r,spec,c)
            domain=(r['d']>=0)&(r['d']<1) if spec['stage']=='W33-first' else np.ones(len(base),bool)
            target=r['n'][:,c]/255
            if spec['space']=='linear':target=decode(target)
            xs.append(X[domain]);ys.append((target-base)[domain])
        X=np.concatenate(xs);y=np.concatenate(ys)
        coef=fit(X,y,method);error=np.abs(X@coef-y)
        objective=max(objective,float(error.max())) if method=='minimax' else objective+float(np.mean(error**2))
        coefficients.append(coef.tolist())
    return coefficients,objective


def parameter_grid(template):
    name=template['name']
    if template.get('w33Reference'):
        if name in ['gradient','colour-gradient']:return [4.],[0.]
        if name in ['rotated-axis','isotropic-two-axis']:
            return [*POWERS,16.],np.arange(0,np.pi,np.pi/72)
    powers=POWERS if name in ['even','isotropic-even','two-term-even','rotated-axis',
        'isotropic-two-axis','coverage-even-affine','body-forward-even-affine'] else [2.]
    return powers,np.arange(0,np.pi,np.pi/72) if name=='rotated-axis' else [0.]


def fit_all(records):
    results=[]
    groups=sorted({(r['profile'],r['pose']) for r in records})
    # The full W33 family pass completes before any new-axis family is fitted.
    for template in family_specs():
        for profile,pose in groups:
            fitting=[r for r in records if (r['profile'],r['pose'])==(profile,pose) and r['role']=='calibration'
                     and (template['stage']=='W33-first' or r['cov'] is not None)]
            for method in ['least-squares','minimax']:
                name=template['name']
                # The explicit reference flag selects W33's original grid;
                # unflagged frozen fits retain their separately labelled G2 variant.
                powers,angles=parameter_grid(template)
                best=None;grid=[]
                for power in powers:
                    for angle in angles:
                        spec={**template,'power':power,'angle':float(angle)}
                        coef,objective=fit_spec(fitting,spec,method)
                        grid.append(dict(power=power,angle=float(angle),objective=objective))
                        if best is None or objective<best[0]:best=(objective,spec,coef)
                row=dict(profile=profile,pose=pose,method=method,spec=best[1],coefficients=best[2],
                         calibrationObjective=best[0],calibrationCells=len(fitting),grid=grid)
                results.append(row)
                print('fitted',len(results),name,profile,pose,method,flush=True)
    return results


def evaluate(records,fits,prefix):
    # Full per-bin tables are compressed without rounding; the index is small.
    tables=[];headlines=[]
    for index,fitrow in enumerate(fits):
        spec=fitrow['spec'];per=defaultdict(list)
        for r in records:
            if (r['profile'],r['pose'])!=(fitrow['profile'],fitrow['pose']):continue
            if spec['stage']!='W33-first' and r['cov'] is None:continue
            pred=predict(r,spec,fitrow['coefficients'])
            # Nominal effective-response fits have no physical nuisance claim.
            # Forward body's declared interval is propagated, not put in tau.
            uncertainty=np.full_like(pred,.5)
            if spec['name'].startswith('body-forward'):
                uncertainty+=r['cov']['body'][:,None]*np.array(r['body']['uncertaintyRGB'])
            for key,mask in r['masks']:
                bar=r['bar'][key]['barRGB']
                row=dict(fit=index,cell=r['cell'],role=r['role'],part=key[0],shell=key[1],bin=key[2],
                         **bin_residual(r['n'][mask],pred[mask],uncertainty[mask],bar))
                tables.append(row);per[(r['role'],key[0])].append(row)
        for (role,part),rows in per.items():
            admitted=[r for r in rows if r['admissible']]
            headlines.append(dict(fit=index,profile=fitrow['profile'],pose=fitrow['pose'],role=role,part=part,
                name=spec['name'],space=spec['space'],method=fitrow['method'],
                bins=len(admitted),pixels=sum(r['pixels'] for r in admitted),
                underpopulated=len(rows)-len(admitted),
                worstMAE=max(max(r['maeRGB']) for r in admitted),
                shellZeroWorstMAE=max(max(r['maeRGB']) for r in admitted if r['shell']==0),
                maxBar=max(max(r['barRGB']) for r in admitted),effectiveTolerance=1,
                failedBins=sum(r['status']=='point fails' for r in admitted),
                pointClosure=all(r['status']=='point compatible' for r in admitted),
                outcome='not closed' if any(r['status']=='point fails' for r in admitted) else 'insufficient resolution'))
    save(HERE/(prefix+'-residuals.json.gz'),tables)
    save(HERE/(prefix+'-headlines.json'),headlines)
    return headlines


def instrument_tables(records,controls,prefix):
    rows=[];notches=[];bodies=[]
    for r in records:
        for key,mask in r['masks']:
            rows.append(dict(cell=r['cell'],role=r['role'],part=key[0],shell=key[1],bin=key[2],
                **bin_residual(r['n'][mask],r['D'][mask],np.zeros_like(r['n'][mask]),r['bar'][key]['barRGB'])))
        notches.extend(dict(cell=r['cell'],profile=r['profile'],pose=r['pose'],role=r['role'],**n) for n in r['notch'])
        bodies.append(dict(cell=r['cell'],role=r['role'],backgroundKind=r['backgroundKind'],body=r['body'],alignment=r['alignment']))
    save(HERE/(prefix+'-zero.json.gz'),rows)
    save(HERE/(prefix+'-notches.json'),notches)
    save(HERE/(prefix+'-controls.json'),controls)
    save(HERE/(prefix+'-bodies.json'),bodies)


def main():
    wave=W.default_wave();records,controls=extract(wave)
    instrument_tables(records,controls,'native')
    fits=fit_all(records)
    save(HERE/'fits.json',fits)
    evaluate(records,fits,'validation')


if __name__=='__main__':main()
