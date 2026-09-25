"""Independent optical arithmetic and re-selection of every declared grid point."""
import gzip,json
from model import HERE,np,edge,inputs
from score import packed,grid,guard

def independent(d,p):
    # No edge.forward or score.forward: reconstruct opaque shadow and additive
    # rim directly, then encode/clamp. Packing alone shares the fixed geometry.
    k=1-p['shadowProduct']*np.clip(1+np.minimum(d['d'],0)/d['reach'],0,1)**2
    shaded=d['body']*k[:,None]
    level=shaded[:,0]*.2126+shaded[:,1]*.7152+shaded[:,2]*.0722
    width=np.array(p['widths'])[d['scale']-1]
    radial=np.clip(1-np.abs(d['d'])/width,0,1)**2
    angular=np.power(np.maximum(np.abs(d['nx']*p['axis'][0]+d['ny']*p['axis'][1])*2**.5,1e-6),p['exponent'])
    light=radial*angular*np.maximum(1+p['along']*d['along'],0)*(p['a']+p['g']*level)
    value=np.clip(shaded+light[:,None],0,1)
    return 255*np.where(value<=.0031308,value*12.92,1.055*value**(1/2.4)-.055)

def evaluate(d,p):
    a=abs(independent(d,p)-d['native']);err=np.add.reduceat(a,d['starts'],axis=0)/d['counts'][:,None]
    old=d['oldError'];delta=float(np.max(err-old));h=float(err[d['horizontal']].max());stratum=-np.inf
    for label in set(d['labels']):
        m=d['labels']==label
        stratum=max(stratum,float(err[m].max()-old[m].max()-.5),float(err[m].mean()-old[m].mean()-.5))
    return dict(minimax=float(err[~d['censored']].max()),maximumWorsening=delta,horizontalMaximum=h,maximumConstraintExcess=max(0,delta-1,h-2,stratum))

if __name__=='__main__':
    guard();records=inputs(structured=False,web=False);saved=json.loads(gzip.decompress((HERE/'search-results.json.gz').read_bytes()));fits=json.loads((HERE/'fits.json').read_text());report=[]
    for ss,fit in zip(saved,fits):
        scheme=fit['scheme'];d=packed([r for r in records if r['scheme']==scheme and r['circular']]);allrows=[];diff=0
        for i,(p,old) in enumerate(zip(grid(scheme),ss['trials'])):
            assert p==old['parameters'];new=evaluate(d,p);diff=max(diff,max(abs(new[k]-old[k]) for k in new));assert new['maximumConstraintExcess']<=1e-10 if old['feasible'] else new['maximumConstraintExcess']>1e-10
            allrows.append(dict(index=i,**new))
        valid=[r for r in allrows if r['maximumConstraintExcess']<=1e-10]
        selected=min(valid,key=lambda r:r['minimax'])['index'] if valid else None
        failed=min(allrows,key=lambda r:(r['maximumConstraintExcess'],r['minimax']))['index']
        assert selected==(fit['selected']['index'] if fit['selected'] else None)
        assert failed==fit['failureWitness']['index'];assert diff<1e-10
        report.append(dict(scheme=scheme,trials=len(allrows),maximumArithmeticDifference=diff,selected=selected,failureWitness=failed,feasible=len(valid)))
    edge.save(HERE/'independent-selection.json',dict(rows=report,guardedNativeOnly=True,independentOpticalArithmetic=True));print(json.dumps(report,indent=2))
