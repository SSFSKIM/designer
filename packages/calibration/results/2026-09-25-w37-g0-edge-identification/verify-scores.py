"""Replay encoded bins and refit each selected shape on guarded native pixels only."""
import gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
# The native Mac recording remains bit-exact; Linux BLAS roundoff is bounded
# without relaxing bins, population or categorical verdicts.
from replay_equality import same_evidence
import numpy as np
import identify,law
HERE=law.HERE;edge=law.edge
records=identify.inputs();stored=json.loads(gzip.decompress((HERE/'residuals.json.gz').read_bytes()))
transfers=json.loads(gzip.decompress((HERE/'transfer.json.gz').read_bytes()))
all_rows=[];all_transfer=[];checks=[]
for fit in json.loads((HERE/'fits.json').read_text()):
    rr,tt=identify.score(records,fit);all_rows+=rr;all_transfer+=tt
    xs=[];ys=[];cells=[]
    for r in records:
        if not (r['active'] and r['circular'] and r['role']=='calibration' and r['scheme']==fit['scheme']):continue
        cells.append(r['cell'])
        b=r['body']/255;native=r['native']/255
        valid=(b[None,:]<254.5/255)&(native<254.5/255)
        if fit['space']=='linear':b=edge.decode(b);native=edge.decode(native)
        x=law.features(b,r['d'],r['ny'],fit['shape'],fit['space']);y=native-b
        for bn in r['bins']:
            if not bn['admissible']:continue
            ids=bn['indices']
            for channel in range(3):
                keep=ids[valid[ids,channel]]
                if not len(keep):continue
                weight=1/np.sqrt(len(keep));xs.append(x[keep,channel]*weight);ys.append(y[keep,channel]*weight)
    coefficients,_,rank,_=np.linalg.lstsq(np.concatenate(xs),np.concatenate(ys),rcond=None)
    error=float(np.max(abs(coefficients-fit['coefficients'])));assert error<1e-10
    assert cells==fit['fitCells'];assert rank==5
    checks.append(dict(space=fit['space'],scheme=fit['scheme'],nativeOnlyCoefficientDifference=error,rank=int(rank)))
assert same_evidence(all_rows,stored),'recorded forward bins changed'
assert same_evidence(all_transfer,transfers),'recorded transfer changed'
print(json.dumps(dict(residualBins=len(stored),transferCells=len(transfers),exactReproduction=sys.platform=='darwin',reproductionVerified=True,checks=checks),indent=2))
