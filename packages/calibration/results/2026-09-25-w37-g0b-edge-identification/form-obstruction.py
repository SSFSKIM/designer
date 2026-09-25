"""A same-input symmetry witness, not another fitted family (§5.182)."""
import itertools,json,sys
import numpy as np
import identify,law
from common import HERE,edge

def main():
    records=identify.inputs();witnesses=[]
    for scale,shell in [(1,-6),(2,-12),(2,-11)]:
        cell=f'apple-macos-27.0-{scale}x-light-standard-glass0.5/grey-255__circular-200__rest'
        r=next(r for r in records if r['cell']==cell);pair=[];indices=[]
        for angle in [4,12]:
            b=next(b for b in r['bins'] if b['part']=='straight' and b['shell']==shell and b['bin']==angle)
            ids=b['indices'];indices.append(ids[0])
            assert np.ptp(r['d'][ids])<1e-12 and np.ptp(r['ny'][ids])<1e-12
            assert np.all(r['native'][ids]<254.5)
            pair.append(dict(side='bottom' if angle==4 else 'top',bin=angle,shell=shell,pixels=len(ids),
                distanceCss=float(r['d'][ids[0]]),normalY=float(r['ny'][ids[0]]),
                nativeRGB=r['native'][ids].mean(0).tolist(),
                nativeMinimum=r['native'][ids].min(0).tolist(),nativeMaximum=r['native'][ids].max(0).tolist(),
                toleranceRGB=identify.BARS[(cell,'straight',shell,angle)]))
        assert pair[0]['distanceCss']==pair[1]['distanceCss']
        assert pair[0]['normalY']==-pair[1]['normalY']
        tiny={**r,**{k:r[k][indices] for k in ['d','nx','ny','arc']}}
        checks=[]
        for family in ['F1','F2','F3']:
            maximum=0
            for w,p in itertools.product([.8,1.,1.2,1.4,1.6,1.8,2.,2.2,2.4],[1,2,3,4,6]):
                x=law.features(r['body']/255,law.radial(tiny,dict(width=w,exponent=p),family),family)
                maximum=max(maximum,float(abs(x[0]-x[1]).max()))
            assert maximum<1e-14
            checks.append(dict(family=family,shapes=45,maximumFeatureDifference=maximum))
        floor=abs(np.array(pair[0]['nativeRGB'])-pair[1]['nativeRGB'])/2
        assert np.all(floor==1.5)
        witnesses.append(dict(cell=cell,role=r['role'],nativeDeep=r['body'].tolist(),pair=pair,
            minimaxLowerBoundCodes=floor.tolist(),checks=checks))
    result=dict(scope='all declared shapes and coefficients; grey calibration straight bins, both scales',
        proof='Reflection changes ny sign but not t, |ny|, conditioning or the symmetric pixel integral. '
              'All basis features coincide. A common prediction cannot lie within one of both250 and253. '
              'Triangle inequality gives max error >=1.5 even after clipping. This is a form obstruction, '
              'not proof against direction-sensitive or otherwise undeclared families.',witnesses=witnesses)
    if '--verify' in sys.argv:assert result==json.loads((HERE/'form-obstruction.json').read_text())
    else:edge.save(HERE/'form-obstruction.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
