"""W41 fixed-strip spatial families; pure arrays, no archive admission.

The group/local blend and positional term are exactly the sealed declaration.
The optimizer is bounded deterministic multistart, a local result only. This
module cannot choose another strip, change a role, or nominate a spatial leaf.
"""
import numpy as np
from scipy.optimize import least_squares,minimize
from scipy.optimize._numdiff import approx_derivative


def predict(family,q,x,mean,y,tone,active):
    if family not in ('S0','S1','S2'):raise ValueError('undeclared family')
    size=0 if family=='S0' else 2 if family=='S2' and active else 1
    q=np.asarray(q,float)
    if q.shape!=(size,) or not np.all(np.isfinite(q)):raise ValueError('coefficient shape')
    if size and not 0<=q[0]<=1:raise ValueError('blend bound')
    if size==2 and not -255<=q[1]<=255:raise ValueError('position bound')
    x=np.asarray(x,float);mean=np.asarray(mean,float);y=np.asarray(y,float)
    if x.shape!=mean.shape or x.shape!=(len(y),3):raise ValueError('row shape')
    m=1. if not size else q[0]
    out=np.asarray(tone(m*x+(1-m)*mean),float)
    if size==2:out=out+q[1]*y[:,None]
    return np.clip(out,0,255)


def fit(family,x,mean,y,target,mass,tone,active):
    target=np.asarray(target,float);mass=np.asarray(mass,float)
    if not np.all((target>5)&(target<250)):raise ValueError('spatial strip must be uncensored')
    if mass.shape!=(len(target),) or np.any(mass<=0):raise ValueError('positive row mass required')
    if not np.isclose(mass.sum(),1):raise ValueError('equal-cell mass must total one')
    n=2 if family=='S2' and active else 1
    if family=='S0':
        p=predict(family,[],x,mean,y,tone,active)
        record=dict(coefficients=[],maximumCodes=float(abs(p-target).max()),weightedSquaredError=float(np.sum((p-target)**2*mass[:,None]/3)),rank=0,singularValues=[],converged=True)
        return dict(classification='fixed null',starts=[],leastSquares=record,minimax=record)
    low=np.array([0.,-255.][:n]);high=np.array([1.,255.][:n]);initial=np.array([1.,0.][:n])
    starts=[initial,*np.random.default_rng(4100).uniform(low,high,(15,n))]
    sqrt=np.sqrt(mass[:,None]/3)
    def forward(q):return predict(family,q,x,mean,y,tone,active)
    def residual(q):return (forward(q)-target).ravel()
    def weighted(q):return ((forward(q)-target)*sqrt).ravel()
    def epi(v):
        r=residual(v[:-1]);return np.r_[v[-1]-r,v[-1]+r]
    def record(result,epigraph=False):
        q=result.x[:-1] if epigraph else result.x
        error=abs(residual(q));maximum=float(error.max())
        jac=approx_derivative(lambda v:forward(v).ravel(),q,bounds=(low,high))
        singular=np.linalg.svd(jac,compute_uv=False)
        gap=None if not epigraph else maximum-float(result.x[-1])
        return dict(coefficients=q.tolist(),maximumCodes=maximum,weightedSquaredError=float(np.sum(weighted(q)**2)),rank=int(np.linalg.matrix_rank(jac)),singularValues=singular.tolist(),optimizerSuccess=bool(result.success),message=str(result.message),evaluations=int(result.nfev),iterations=int(getattr(result,'nit',0)),epigraphGapCodes=gap,converged=bool(result.success and (gap is None or gap<=1e-8)))
    records=[]
    for index,initial in enumerate(starts):
        least=least_squares(weighted,initial,bounds=(low,high),max_nfev=3000,ftol=1e-10,xtol=1e-10,gtol=1e-10)
        mm=minimize(lambda v:v[-1],np.r_[initial,abs(residual(initial)).max()+1e-8],method='SLSQP',bounds=list(zip(low,high))+[(0,None)],constraints=[dict(type='ineq',fun=epi)],options=dict(maxiter=3000,ftol=1e-10))
        records.append(dict(startIndex=index,initial=initial.tolist(),leastSquares=record(least),minimax=record(mm,True)))
    def choose(key,objective):
        rows=[r for r in records if r[key]['converged']]
        if not rows:return None
        selected=min(rows,key=lambda r:(r[key][objective],r['startIndex']))
        return dict(**selected[key],startIndex=selected['startIndex'])
    return dict(classification='LOCAL; not a certified family negative',starts=records,leastSquares=choose('leastSquares','weightedSquaredError'),minimax=choose('minimax','maximumCodes'))
