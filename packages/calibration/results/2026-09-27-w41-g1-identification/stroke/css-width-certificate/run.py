"""Rebuild the CSS-width necessary screen from saved pixels and unchanged law.

Only inactive uniform-neutral top straights are used:1x shell0,2x shell0/1.
All admitted pixels, all256 samples and all seven repeats are retained. The
16 vertical midpoint distances are a proven exact reduction, not a bin fit.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import width_cut as cut

HERE=Path(__file__).resolve().parent
M1=HERE.parent/'m1-certificate'
SOURCE=M1/'sources'
RESULTS=SOURCE/'packages/calibration/results'
DECLARATION_SHA='850747c1f03781a6efe9b433bd4ce3bd6cf72b63c9befd8d5d98de9eadf7f759'
LEVELS=(40,56,72,88,104,128,150,255)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def guard():
    forbidden=[Path.home()/'vitrea-w39',Path.home()/'.cache/vitrea-archives']
    def audit(event,args):
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=Path(args[0].decode() if isinstance(args[0],bytes) else args[0]).resolve()
            if any(p==root or root in p.parents for root in forbidden):
                raise PermissionError('CSS-width proof permits saved bundles only')
    sys.addaudithook(audit)


def load():
    manifest=json.loads((M1/'sources.json').read_text())
    assert manifest['revision']=='d35b4cbf43f1fcdda55063b3b8e0fa178d720a78'
    for r in manifest['files']:
        assert sha((SOURCE/r['path']).read_bytes())==r['sha256'],r['path']
    g0=RESULTS/'2026-09-27-w41-g0-declaration'
    assert sha((g0/'bounds-declaration.txt').read_bytes())==DECLARATION_SHA
    sys.path.insert(0,str(g0/'instrument'))
    import instrument as m
    import shadow
    mats=shadow.materials() # Unchanged loader still checks runtime/document provenance.
    sys.path.insert(0,str(m.G0))
    import w39_archive as archive
    return m,shadow,mats,archive


def mean(values):
    values=np.asarray(values).ravel()
    assert len(values)>0 and np.all(values==values.astype(np.int64))
    return F(sum(map(int,values)),len(values))


def allowances(pixels,b,geometry):
    """Jensen on the SAME uncensored subset as score_bin; rails remain hard."""
    assert pixels.shape[0]==7 and pixels.shape[1]>=4 and pixels.shape[2]==3
    run_means=[[mean(v[:,ch]) for ch in range(3)] for v in pixels]
    bars=[F(1,2)+(max(v[ch] for v in run_means)-min(v[ch] for v in run_means))/2 for ch in range(3)]
    rows=[]
    for state,target in enumerate([np.median(pixels,axis=0),*pixels]):
        for ch in range(3):
            v=target[:,ch];low=v<=5;high=v>=250;exact=~(low|high)
            common=dict(geometry=geometry,state=state,channel=ch,b=b,
                        totalPixels=len(v),uncensoredPixels=int(exact.sum()),
                        lowRailPixels=int(low.sum()),highRailPixels=int(high.sum()),
                        bar=str(bars[ch]),bound=str(max(F(1),bars[ch])))
            if np.any(exact):
                centre=mean(v[exact])-b;bound=max(F(1),bars[ch])
                rows.append(dict(**common,kind='Jensen-uncensored-mean',
                                 lower=str(centre-bound),upper=str(centre+bound)))
            if np.any(low):
                rows.append(dict(**common,kind='hard-low-rail',lower=None,upper=str(5-b)))
            if np.any(high):
                rows.append(dict(**common,kind='hard-high-rail',lower=str(250-b),upper=None))
    return rows,bars


def derive():
    guard();m,shadow,mats,archive=load()
    manifest=json.loads((HERE/'inputs/manifest.json').read_text())
    assert manifest['roles']==['calibration'] and manifest['newArchiveReads']==0
    expected={(endpoint,scale,b) for endpoint in ('light-inactive','dark-inactive')
              for scale in (1,2) for b in LEVELS}
    assert {(r['endpoint'],r['scale'],r['b']) for r in manifest['records']}==expected
    assert len(manifest['records'])==32
    arrays={};observations=[];thresholds={};geometry_fields={};shared_component=None
    groups={endpoint:{} for endpoint in ('light-inactive','dark-inactive')}
    for record in manifest['records']:
        raw=(HERE/'inputs'/record['file']).read_bytes()
        assert sha(raw)==record['sha256']==record['archiveEntry']['sha256']
        assert record['role']=='calibration' and record['archiveEntry']['admitted']
        runs,states=archive.unbundle(raw)
        runs=[r for r in runs if r['protocol']=='normal' and r['admitted']]
        assert len(runs)==7 and len({r['run'] for r in runs})==7
        payloads=[archive.unpack(states[r['state']]) for r in runs]
        p=payloads[0];scale=record['scale'];b=record['b'];endpoint=record['endpoint']
        assert p['profile']+'/'+p['sceneId']==record['cell']
        if shared_component is None:shared_component=p['component']
        assert p['component']==shared_component,'cross-scale supplied shape/path/position changed'
        shapes=m.readers.shapes_of(p['component'])
        assert len(shapes)==1 and not shapes[0].opaque
        shape=shapes[0]
        assert shape.circular and shape.size==(120.,44.)
        for v in payloads:
            assert v['pose']=='inactive' and v['scheme']+'-inactive'==endpoint and v['scale']==scale
            assert v['component']==shared_component and v['rgb'].shape==p['rgb'].shape
            assert v['profile']+'/'+v['sceneId']==record['cell']
            assert np.all(v['noGlass']==b),'actual uniform full RGB reference differs'
        mat=mats[endpoint]
        for key in ('thinOcclusionDark','thinOcclusionMid','thinOcclusionBright',
                    'thickOcclusionAt96','thickOcclusionAt128','thickOcclusionAt160',
                    'sizeGain','liftAmplitude'):
            assert mat['outerShadow'][key]==0
        geo=m.readers.geometry(p['rgb'].shape[:2],shapes,scale)
        bins,labels=m.readers.edge_bins(geo,0,inner_css=0,outer_css=4)
        for shell in ((0,) if scale==1 else (0,1)):
            bi=next(i for i,row in enumerate(bins) if row['part']=='straight'
                    and row['side']=='top' and row['shell']==shell)
            binrow=bins[bi]; yy,xx=np.nonzero(labels==bi);xy=np.c_[xx,yy]
            assert len(xy)==binrow['pixels']>=4 and binrow['admissible']
            g=m.samples(shape,xy,scale,16)
            assert np.all(g['nx']==0) and np.all(g['ny']==-1) and not np.any(g['arc'])
            assert np.all(g['d']>0) and np.array_equal(g['d'],np.broadcast_to(g['d'][0],g['d'].shape))
            # No inferred raster phase: the actual supplied path's distances
            # must equal these exact vertical midpoint rows for every pixel.
            expected_d=np.repeat(np.array([shell+(2*i+1)/32 for i in range(16)]),16)[::-1]
            # q's y increases while outward top distance decreases.
            assert np.array_equal(g['d'][0],expected_d)
            ref=m.bilinear(p['noGlass'],g['q']);assert np.all(ref==b)
            luminance=float(m.body.decode(np.array([b,b,b])/255)@m.body.W)
            alpha=shadow.at(g['q'],shape,scale,mat,luminance);assert np.all(alpha==0)
            key=f'{scale}x-s{shell}'
            # The repeated x samples have equal distances; retain the full field
            # but reduce its exact threshold counting to16 equipopulated values.
            counts=Counter(F(float(d))/scale for d in g['d'][0])
            assert len(counts)==16 and set(counts.values())=={16}
            ts=sorted(counts)
            if key not in thresholds:
                thresholds[key]=list(map(str,ts));geometry_fields[key]=(xy.copy(),g)
            else:
                assert thresholds[key]==list(map(str,ts))
                saved_xy,saved_g=geometry_fields[key]
                assert np.array_equal(saved_xy,xy)
                for name in ('q','d','nx','ny','arc'):
                    assert np.array_equal(saved_g[name],g[name])
            native=np.array([v['rgb'][yy,xx] for v in payloads])
            refs=np.array([v['noGlass'][yy,xx] for v in payloads])
            rows,bars=allowances(native,b,key)
            check=m.score_bin(np.full((len(xy),3),b,float),native)
            assert check['barRGB']==list(map(float,bars))
            prefix=f'{endpoint}_{b}_{key}'
            arrays[prefix+'_nativeRGBSevenRuns']=native
            arrays[prefix+'_referenceRGBSevenRuns']=refs
            arrays[prefix+'_xy']=xy
            # Geometry is saved once per true common field, not silently inferred.
            for name in ('q','d','nx','ny','arc'):
                arrays[f'{key}_{name}']=g[name]
            arrays[f'{key}_shadowAlpha']=alpha
            for row in rows:
                group=f"input{b}-channel{row['channel']}"
                groups[endpoint].setdefault(group,[]).append(dict(**row,cell=record['cell']))
            observations.append(dict(cell=record['cell'],endpoint=endpoint,scale=scale,b=b,
                bin=binrow,geometry=key,component=p['component'],frameShape=list(p['rgb'].shape),
                runIds=[r['run'] for r in runs],stateMembership=[r['state'] for r in runs],
                barRGB=list(map(str,bars)),nativeRunMeanRGB=native.mean(1).tolist(),
                allReferencesExactlyUniformRGB=[b,b,b],constraints=rows))
    # Full law uses w*scale. Check every actual boundary and midpoint against its
    # unchanged coverage, per pixel, with gamma0 and top beta0 so A=1.
    partition=cut.states(thresholds)
    for state in partition:
        w=F(state['representative'])
        for key,(_,g) in geometry_fields.items():
            coverage=m.coverage(g,float(w),0.,0.,css_width=True)
            expected_fraction=cut.fraction(thresholds[key],w)
            assert np.all(coverage.mean(1)==float(expected_fraction))
            assert np.array_equal(coverage,((g['d']>0)&(g['d']<float(w)*g['scale'])).astype(float))
    meta=dict(schema='w41-css-width-observations-1',declarationSha256=DECLARATION_SHA,
        sourceManifest=str(M1/'sources.json'),sourceManifestSha256=sha((M1/'sources.json').read_bytes()),
        inputManifestSha256=sha((HERE/'inputs/manifest.json').read_bytes()),
        originalSourceRevision='d35b4cbf43f1fcdda55063b3b8e0fa178d720a78',
        archiveReads=0,savedCells=32,observations=observations,thresholds=thresholds,groups=groups,
        exactSourceChecks=dict(actualTopNormals='nx=0,ny=-1,arc=false at every subpixel',
            gamma=0,shadow=0,uniformFullRGB=True,sameSuppliedComponentAllScales=True,
            allPixelsSameDistanceArray=True,distinctDistancesPerPixel=16,
            multiplicityEachDistance=16,law='coverage:w=width*g[scale] if css_width else width;0<d<w',
            completeWidthStatesVerifiedThroughUnchangedCoverage=len(partition)),
        proof='At each input/channel/endpoint, z=A(top)*(S(b)-b) is common across scale and shell. '
            'The actual top normal is constant, references are identical full RGB, and shadow=reference. '
            'All pixels in each bin have the same256 distances,16 distinct values each repeated16. '
            'Thus every pixel prediction is exactly b+f(w)*z, not a bin-mean approximation. '
            'The mean native constraints are necessary by Jensen on the same uncensored subset '
            'as score_bin; every censor rail is an additional hard one-sided inequality. '
            'Independent z for every channel/input further relaxes all material coupling. '
            'All distinct d/scale thresholds in[0,2], endpoints, singleton boundaries and adjacent '
            'open intervals partition every real CSS width. Predicates cannot change inside an '
            'open interval; strict d<w excludes equality at each singleton. No widths are omitted.',
        scope='CSS-width rival only; inactive endpoints separately; modelsM0,M1,M2; '
            'device-width and nominal-curvature untouched; no candidate survival inferred.')
    return meta,arrays


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    meta,arrays=derive()
    result={endpoint:cut.solve(meta['thresholds'],groups) for endpoint,groups in meta['groups'].items()}
    out=HERE/'unbounded'
    if args.check:
        assert meta==json.loads((out/'observations.json').read_text())
        assert result==json.loads((out/'certificate.json').read_text())
        with np.load(out/'pixels-and-geometry.npz',allow_pickle=False) as saved:
            assert set(saved.files)==set(arrays)
            for key,value in arrays.items():assert np.array_equal(saved[key],value),key
        print('Saved replay PASS: raw tree and fetched archive denied; no new native reads.')
    else:
        out.mkdir(exist_ok=False)
        write(out/'observations.json',meta);write(out/'certificate.json',result)
        np.savez_compressed(out/'pixels-and-geometry.npz',**arrays)
    print(json.dumps({k:dict(status=v['status'],states=v['stateCount'],points=v['pointCount'],
        intervals=v['openIntervalCount'],feasibleStateIndices=v['feasibleStateIndices'])
        for k,v in result.items()},indent=2))


if __name__=='__main__':main()
