"""Independent exact replay of the deciding neutral128 subset from four bundles.

No import or call to width_cut/bounded_cut solvers is used. Reconstruct every
pixel and sample with the unchanged law, then enumerate widths and intersect
all seven-repeat/median Jensen constraints independently. All deciding native
samples are uncensored; white's rail arithmetic is unnecessary to this proof.
"""
from fractions import Fraction as F
import hashlib
import importlib
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'m1-certificate/sources'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    forbidden=[Path.home()/'vitrea-w39',Path.home()/'.cache/vitrea-archives']
    def guard(event,args):
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=Path(args[0].decode() if isinstance(args[0],bytes) else args[0]).resolve()
            if any(p==root or root in p.parents for root in forbidden):raise PermissionError('saved only')
    sys.addaudithook(guard)
    manifest=json.loads((HERE.parent/'m1-certificate/sources.json').read_text())
    for r in manifest['files']:assert sha((SOURCE/r['path']).read_bytes())==r['sha256']
    results=SOURCE/'packages/calibration/results'
    sys.path.insert(0,str(results/'2026-09-27-w41-g0-declaration/instrument'))
    m=importlib.import_module('instrument');shadow=importlib.import_module('shadow');mats=shadow.materials()
    sys.path.insert(0,str(m.G0));archive=importlib.import_module('w39_archive')
    bundles=json.loads((HERE/'inputs/manifest.json').read_text())['records']
    records=[r for r in bundles if r['b']==128];assert len(records)==4
    observations={};common_component=None
    for record in records:
        raw=(HERE/'inputs'/record['file']).read_bytes();assert sha(raw)==record['sha256']
        runs,states=archive.unbundle(raw)
        runs=[r for r in runs if r['protocol']=='normal' and r['admitted']]
        assert len(runs)==7 and len({r['run'] for r in runs})==7
        payloads=[archive.unpack(states[r['state']]) for r in runs]
        p=payloads[0];scale=record['scale'];endpoint=record['endpoint']
        if common_component is None:common_component=p['component']
        for v in payloads:
            assert v['component']==common_component and v['pose']=='inactive'
            assert v['scale']==scale and v['scheme']+'-inactive'==endpoint
            assert v['profile']+'/'+v['sceneId']==record['cell']
            assert v['rgb'].shape==p['rgb'].shape and np.all(v['noGlass']==128)
        shape=m.readers.shapes_of(p['component'])[0]
        geo=m.readers.geometry(p['rgb'].shape[:2],[shape],scale)
        bins,labels=m.readers.edge_bins(geo,inner_css=0,outer_css=4)
        observations.setdefault(endpoint,{})
        for shell in ((0,) if scale==1 else (0,1)):
            bi=next(i for i,b in enumerate(bins) if b['part']=='straight' and b['side']=='top' and b['shell']==shell)
            yy,xx=np.nonzero(labels==bi);assert len(xx)>=4
            g=m.samples(shape,np.c_[xx,yy],scale,16)
            assert np.all(g['nx']==0) and np.all(g['ny']==-1) and not g['arc'].any()
            assert np.all(g['d']>0) and np.array_equal(g['d'],np.broadcast_to(g['d'][0],g['d'].shape))
            b=m.bilinear(p['noGlass'],g['q']);assert np.all(b==128)
            assert np.all(shadow.at(g['q'],shape,scale,mats[endpoint],float(m.body.decode(128/255)))==0)
            pixels=np.array([v['rgb'][yy,xx] for v in payloads])
            assert np.all((pixels>5)&(pixels<250))
            means=[[F(int(v[:,ch].sum()),len(xx)) for ch in range(3)] for v in pixels]
            bars=[F(1,2)+(max(v[ch] for v in means)-min(v[ch] for v in means))/2 for ch in range(3)]
            targets=[np.median(pixels,axis=0),*pixels]
            observations[endpoint][f'{scale}x-s{shell}']=dict(
                thresholds=[F(float(d))/scale for d in g['d'][0]],
                constraints=[(F(int(v[:,ch].sum()),len(xx))-128,max(F(1),bars[ch]),state,ch)
                             for state,v in enumerate(targets) for ch in (0,)],
                g=g,pixels=len(xx),bars=list(map(str,bars)),
                minimumRGB=pixels.min((0,1)).tolist(),maximumRGB=pixels.max((0,1)).tolist())
    saved=json.loads((HERE/'bounded/certificate.json').read_text())
    reports={}
    for endpoint,obs in observations.items():
        points=sorted({F(0),F(2),*(t for v in obs.values() for t in v['thresholds'] if 0<=t<=2)})
        partition=[]
        for i,w in enumerate(points):
            partition.append(('point',w,w,w))
            if i+1<len(points):partition.append(('open',w,points[i+1],(w+points[i+1])/2))
        assert len(partition)==99 and len(points)==50
        proofs=[]
        for index,(kind,left,right,w) in enumerate(partition):
            expected=saved['outcomes'][endpoint]['states'][index]
            assert (kind,str(left),str(right),str(w))==tuple(expected[k] for k in ('kind','lower','upper','representative'))
            lower,upper=F(-128),F(127);lower_source=upper_source='sealed-z-range';zero=[]
            fractions={}
            for name,v in obs.items():
                f=F(sum(0<t<w for t in v['thresholds']),len(v['thresholds']));fractions[name]=str(f)
                assert str(f)==expected['fractions'][name]
                dense=m.coverage(v['g'],float(w),0,0,css_width=True)
                assert np.all(dense.mean(1)==float(f))
                for centre,bound,state,ch in v['constraints']:
                    lo,hi=centre-bound,centre+bound;label=f'{name}/state{state}/channel{ch}'
                    if f==0:
                        if not lo<=0<=hi:zero.append(dict(row=label,lower=str(lo),upper=str(hi)))
                    else:
                        if lo/f>lower:lower,lower_source=lo/f,label
                        if hi/f<upper:upper,upper_source=hi/f,label
            assert zero or lower>upper,(endpoint,index)
            assert not expected['groups']['input128-channel0']['feasible']
            proofs.append(dict(index=index,kind=kind,lowerWidth=str(left),upperWidth=str(right),
                fractions=fractions,proof=(dict(kind='zero-coverage',witness=zero[0]) if zero else
                dict(kind='disjoint-z',lower=str(lower),upper=str(upper),gap=str(lower-upper),
                     lowerSource=lower_source,upperSource=upper_source))))
        reports[endpoint]=dict(states=99,allStatesExactlyRejected=True,decidingInput=128,
            native={key:{k:v[k] for k in ('pixels','bars','minimumRGB','maximumRGB')} for key,v in obs.items()},
            proofs=proofs)
    print(json.dumps(dict(savedReplay=True,independentIntervalImplementation=True,
        archiveReads=0,cropBundlesVerified=4,allDecidingPixelsUncensored=True,
        certificateSha256=sha((HERE/'bounded/certificate.json').read_bytes()),endpoints=reports),indent=2))


if __name__=='__main__':main()
