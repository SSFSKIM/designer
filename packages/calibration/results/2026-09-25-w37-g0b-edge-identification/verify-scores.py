"""Independent chosen-shape basis/LS reconstruction and recorded table replay.

The recording Mac remains exact; other BLAS implementations have bounded
last-bit drift without changing the selected coefficients or verdicts.
"""
import gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
# The native Mac recording remains bit-exact; Linux BLAS roundoff is bounded
# without relaxing bins, population or categorical verdicts.
from replay_equality import same_evidence
import numpy as np
import identify
from common import HERE,edge

def independent_basis(r,shape,family):
    n=len(r['d']);rad=np.zeros((n,7));w=shape['width'];p=shape['exponent']
    for iy in range(8):
        for ix in range(8):
            dx=((ix+.5)/8-.5)/r['scale'];dy=((iy+.5)/8-.5)/r['scale']
            d=r['d']+dx*r['nx']+dy*r['ny'];ny=r['ny'].copy()
            ids=np.flatnonzero(r['arc']);radius=r['span']/2
            qx=(r['d'][ids]+radius)*r['nx'][ids]+dx
            qy=(r['d'][ids]+radius)*r['ny'][ids]+dy
            length=np.sqrt(qx*qx+qy*qy);d[ids]=length-radius;ny[ids]=qy/length
            t=-d;a=abs(ny)**p
            line=np.where((t>=0)&(t<w),(1-t/w)**(2 if family=='F2' else 1),0)
            h0=np.where((t>=0)&(t<=2),1-t/2,0)
            h2=np.where((t>=0)&(t<=2),t/2,np.where((t>2)&(t<=6),(6-t)/4,0))
            h6=np.where((t>=2)&(t<=6),(t-2)/4,np.where((t>6)&(t<=12),(12-t)/6,0))
            rad+=np.stack([line*a,h0,h2,h6,h0*a,h2*a,h6*a],axis=1)/64
    b=r['body']/255;y=float(np.dot(b,[.2126,.7152,.0722]));columns=[]
    for j in range(7):
        terms=[np.ones(3),np.full(3,y)]
        if family=='F3':terms.append(np.full(3,y*y))
        terms.extend([b-y,(b-y)*y])
        if family=='F3':terms.append((b-y)*y*y)
        columns.extend([rad[:,j,None]*term for term in terms])
    return np.stack(columns,axis=-1)

def main():
    records=identify.inputs();stored=json.loads(gzip.decompress((HERE/'residuals.json.gz').read_bytes()))
    transfers=json.loads(gzip.decompress((HERE/'transfer.json.gz').read_bytes()));rr=[];tt=[];checks=[];quadrature=[]
    for fit in json.loads((HERE/'fits.json').read_text()):
        xs=[];ys=[]
        for r in identify.fit_population(records,fit['scheme']):
            x=independent_basis(r,fit['shape'],fit['family']);target=(r['native']-r['body'])/255
            for b in r['bins']:
                if not b['admissible']:continue
                for ch in range(3):
                    ids=b['indices'];ids=ids[(r['body'][ch]<254.5)&(r['native'][ids,ch]<254.5)]
                    if len(ids):xs.append(x[ids,ch]/np.sqrt(len(ids)));ys.append(target[ids,ch]/np.sqrt(len(ids)))
        c,_,rank,s=np.linalg.lstsq(np.concatenate(xs),np.concatenate(ys),rcond=None)
        difference=float(abs(c-fit['coefficients']).max());assert difference<1e-8,(fit['family'],difference)
        assert rank==fit['rank']==fit['columns']
        checks.append(dict(family=fit['family'],scheme=fit['scheme'],rank=int(rank),coefficientMaxDifference=difference))
        r8,t8=identify.score(records,fit);rr+=r8;tt+=t8
        r16,_=identify.score(records,fit,order=16)
        differences=[dict(cell=a['cell'],part=a['part'],shell=a['shell'],bin=a['bin'],
            predictedMeanDeltaRGB=(np.array(b['predictedExcess'])-a['predictedExcess']).tolist(),
            residualDeltaRGB=(np.array(b['residualRGB'])-a['residualRGB']).tolist()) for a,b in zip(r8,r16)]
        worst=max(differences,key=lambda a:max(abs(v) for v in a['predictedMeanDeltaRGB']))
        quadrature.append(dict(family=fit['family'],scheme=fit['scheme'],
            maximumMeanDifference=max(abs(v) for v in worst['predictedMeanDeltaRGB']),worst=worst,
            closureAt16=identify.summary(r16)))
    assert same_evidence(rr,stored);assert same_evidence(tt,transfers)
    result=dict(residualBins=len(rr),transferCells=len(tt),exactReproduction=sys.platform=='darwin',reproductionVerified=True,checks=checks,
        quadratureCheck='8 to16 with fixed coefficients, no refit or reselection',quadrature=quadrature)
    if '--verify' not in sys.argv:edge.save(HERE/'verification.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='quadrature'},indent=2))

if __name__=='__main__':main()
