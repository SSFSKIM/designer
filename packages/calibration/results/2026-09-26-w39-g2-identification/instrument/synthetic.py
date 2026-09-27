"""Noiseless recovery and wrong-family checks before the first native fit."""
import json
from pathlib import Path
import numpy as np
import body
import fitting
import edge_law

HERE=Path(__file__).resolve().parent
materials=json.loads((HERE/'resolved-materials.json').read_text())
# Synthetic inputs, deliberately not native observations or selected residuals.
rng=np.random.default_rng(3902)
x=np.r_[rng.uniform(40,150,(90,3)),np.repeat((body.KNOTS*255)[:,None],3,axis=1)]/255
neutral=np.array([.35,.4,.46,.52,.57,.62,.67])
results=[]
for family,q0,true,fn in [
 ('H1',neutral*.9,neutral,lambda q:body.h1(x,q)),
 ('H3',[1,0,0,1,0,0],[1.6,-.8,.2,1.3,-.5,.1],lambda q:body.h3(x,neutral,q)),
 ('H3prime',[1,0,0,1],[1.6,.3,-.4,1.2],lambda q:body.h3prime(x,neutral,q)),
]:
    y=fn(np.asarray(true));fit=fitting.fit(fn,y,q0)
    results.append(dict(family=family,**fit))
    assert fit['leastSquares']['rss']<1e-8,(family,fit)
    assert fit['minimax']['rss']<1e-8,(family,fit)
    if family!='H1':
        wrong=abs(body.h1(x,neutral)-y)*255
        results[-1]['wrongH1MaximumCodes']=float(wrong.max())
        assert wrong.max()>1
for endpoint,m in materials.items():
    if endpoint=='default':continue
    exact=body.h2(x,m)
    results.append(dict(family='H2',endpoint=endpoint,parameters=0,rss=0,
        syntheticOutputRangeCodes=[float(exact.min()*255),float(exact.max()*255)]))
    true=np.r_[.55,np.array(m['backdropToneResponseThin'])*.97+.006]
    initial=np.r_[m['bodyChromaRetention'],m['backdropToneResponseThin']]
    fn=lambda q:body.h2(x,m,q=q)
    fit=fitting.fit(fn,fn(true),initial,[(0,1)]*5,monotone_start=1)
    results.append(dict(family='H2prime',endpoint=endpoint,**fit))
    assert fit['leastSquares']['rss']<1e-8,(endpoint,fit)
    assert fit['minimax']['rss']<1e-8,(endpoint,fit)
# Colour-changing independent samples exercise every response coefficient.
b=rng.uniform(.2,.7,(200,3));back=rng.uniform(.1,.6,(200,3))
d=-rng.uniform(.05,11.8,200);ny=rng.uniform(-1,1,200)
rad=edge_law.radial(d,ny,rng.choice([1,2],200),1.4,2)
features=edge_law.features(b,rad);true=np.sin(np.arange(44)+1)*.01
# Exact linear solve is appropriate before clipping here: all outputs stay interior.
y=edge_law.forward(b,rad,true);q,_,rank,singular=np.linalg.lstsq(features.reshape(-1,44),(y-b).ravel(),rcond=None)
rss=float(np.sum((edge_law.forward(b,rad,q)-y)**2))
results.append(dict(family='edge',rank=int(rank),columns=44,singularValues=singular.tolist(),rss=rss,maximumCoefficient=float(abs(q).max())))
assert rank==44 and rss<1e-20 and abs(q).max()<=4096
extra=lambda q:edge_law.h4(b,back,rad,q)
fit=fitting.fit(extra,extra([.08,-.04]),[0,0],bounds=[(-4096,4096)]*2)
results.append(dict(family='H4',**fit))
assert fit['leastSquares']['rss']<1e-8
# H4's body-chroma term duplicates the edge signed line's c coefficient exactly.
h4body=extra([0,1]).ravel();edgec=features[:,:,6].ravel()
assert np.array_equal(h4body,edgec)
results.append(dict(finding='H4 body-chroma coefficient duplicates signed-line c',
                    maximumDifference=float(abs(h4body-edgec).max())))
print(json.dumps(dict(nativeReads=0,results=results),indent=2,allow_nan=False))
