"""Bounded deterministic LOCAL stroke multistarts; no native reader or CLI.

The four endpoints share one width and optional nominal-radius coefficient.
Optimisation coordinates map onto exactly the declared feasible domain: eta
maps to gamma=(1-beta)*eta; sorting eight bounded ordinates gives the monotone
curve without a penalty or omitted parameter. Sorting creates equivalent
permutations, not additional measured degrees of freedom. Width quadrature is
piecewise constant: a zero derivative is reported as rank loss, never repaired.
"""
import numpy as np
from scipy.optimize import least_squares, minimize
from scipy.optimize._numdiff import approx_derivative
import instrument as m

ENDPOINTS=('light-active','light-inactive','dark-active','dark-inactive')

def domain(family,curvature=False):
    if family not in ('M0','M1','M2'):raise ValueError('unknown family')
    lo=[0,0,0,0,0,-1,-1];hi=[2,1,1,1,1,1,1];start=[1,.4,.4,.4,.4,0,0]
    for endpoint in range(4):
        if family=='M0':lo.extend([0,-255]);hi.extend([3,255]);start.extend([1,0])
        else:
            lo.extend([0]*8);hi.extend([255]*8);start.extend(m.NODES.tolist())
            if family=='M2' and endpoint>=2:lo.extend([0,0]);hi.extend([16,1]);start.extend([0,0])
    if curvature:lo.append(-22);hi.append(22);start.append(0)
    return np.array(lo,float),np.array(hi,float),np.array(start,float)

def unpack(q,family,endpoint):
    beta=q[1+endpoint]
    gamma=(1-beta)*q[5+endpoint//2] if endpoint in (0,2) else 0
    offset=7
    for k in range(endpoint):offset+=2 if family=='M0' else 10 if family=='M2' and k>=2 else 8
    n=2 if family=='M0' else 10 if family=='M2' and endpoint>=2 else 8
    material=np.asarray(q[offset:offset+n]).copy()
    if family!='M0':material[:8]=np.sort(material[:8])
    return float(q[0]),float(beta),float(gamma),material

def predict(q,observation,family,css_width=False,curvature=False):
    endpoint=observation['endpoint']
    w,b,g,colour=unpack(q,family,endpoint)
    return m.composite(observation['g'],observation['backdrop'],observation['shadow'],w,b,g,
                       family,colour,dark=endpoint>=2,css_width=css_width,rho=float(q[-1]) if curvature else None)

def objective_layout(observations):
    """Equal cell mass across the measured bin/channel groups, rails held hard."""
    targets=[];weights=[];groups=[];cursor=0
    for cell in observations:
        t=np.asarray(cell['target'],float);ids=np.asarray(cell['binids'])
        if t.ndim!=2 or t.shape[1]!=3 or ids.shape!=(len(t),) or not len(t) or not np.all(np.isfinite(t)):raise ValueError('finite admitted pixels and matching bins required')
        measured=(t>5)&(t<250);mass=np.zeros_like(t);cell_groups=[]
        for bi in np.unique(ids):
            at=ids==bi
            for c in range(3):
                keep=at&measured[:,c]
                if keep.any():cell_groups.append((keep,c))
        for keep,c in cell_groups:
            groups.append(cursor+np.flatnonzero(keep)*3+c)
            mass[keep,c]=1/len(observations)/len(cell_groups)/int(keep.sum())
        cursor+=t.size;targets.append(t);weights.append(mass)
    return np.concatenate(targets).ravel(),np.concatenate(weights).ravel(),groups

def fit_local(observations,family,css_width=False,curvature=False):
    """Observations are admitted calibration cells; targets are per-pixel RGB.

    Each cell carries g, backdrop, held shadow, target Nx3, and binids N. The
    caller supplies only population-admitted bins and keeps every repeat for
    the separate closure scorer. This array fitter cannot authorize archive roles.
    Minimax is max of per-bin/channel mean absolute pixel error, not pixel max
    and not absolute signed means. Censored pixels remain hard rail constraints.
    """
    if not observations:raise ValueError('no admitted calibration observations')
    if any(not 0<=o['endpoint']<4 for o in observations):raise ValueError('unknown endpoint')
    low,high,initial=domain(family,curvature);p=len(initial)
    starts=[initial,*np.random.default_rng(4100).uniform(low,high,(15,p))]
    target,mass,groups=objective_layout(observations)
    exact=(target>5)&(target<250);rail_low=target<=5;rail_high=target>=250
    def forward(q):return np.concatenate([predict(q,o,family,css_width,curvature) for o in observations]).ravel()
    def residual(q):return (forward(q)-target)[exact]*np.sqrt(mass[exact])
    def rails(q):
        pred=forward(q)
        return np.r_[5-pred[rail_low],pred[rail_high]-250]
    def bin_errors(q):
        error=abs(forward(q)-target)
        return np.array([error[ix].mean() for ix in groups])
    def maximum(q):return float(bin_errors(q).max(initial=0))
    def report(q,opt,epi=None):
        if np.any(q<low) or np.any(q>high) or not np.all(np.isfinite(q)):raise ValueError('optimizer escaped declared box')
        deficit=float(np.maximum(-rails(q),0).max(initial=0))
        jac=approx_derivative(lambda v:forward(v)[exact],q,bounds=(low,high))
        singular=np.linalg.svd(jac,compute_uv=False) if jac.size else np.array([])
        maximum_error=maximum(q);gap=None if epi is None else maximum_error-epi
        return dict(coefficients=q.tolist(),parameterFeasible=True,maximumCodes=maximum_error,
                    weightedSquaredError=float(np.sum(residual(q)**2)),railDeficitCodes=deficit,
                    rank=int(np.linalg.matrix_rank(jac)) if jac.size else 0,singularValues=singular.tolist(),
                    optimizerSuccess=bool(opt.success),message=str(opt.message),evaluations=int(opt.nfev),
                    iterations=int(getattr(opt,'nit',0)),epigraphGapCodes=gap,
                    converged=bool(opt.success and deficit==0 and (gap is None or gap<=1e-8)),
                    zeroFloorBracketCodes=[0.,maximum_error] if epi is not None and deficit==0 and maximum_error<=1e-8 else None)
    records=[]
    for i,start in enumerate(starts):
        ls=least_squares(residual,start,bounds=(low,high),max_nfev=3000,ftol=1e-10,xtol=1e-10,gtol=1e-10)
        if np.any(~exact):
            ls=minimize(lambda q:np.sum(residual(q)**2),ls.x,method='SLSQP',bounds=list(zip(low,high)),constraints=[dict(type='ineq',fun=rails)],options=dict(maxiter=3000,ftol=1e-10))
        mm=minimize(lambda v:v[-1],np.r_[start,maximum(start)+1e-8],method='SLSQP',bounds=[*zip(low,high),(0,None)],constraints=[dict(type='ineq',fun=lambda v:np.r_[v[-1]-bin_errors(v[:-1]),rails(v[:-1])])],options=dict(maxiter=3000,ftol=1e-10))
        original=report(mm.x[:-1],mm,mm.x[-1])
        # An independent raw start retains its outcome. A declared LS-seeded
        # refinement addresses the nonsmooth bin-absolute epigraph's line-search
        # failure near an exact fit; it cannot conceal the original failure.
        refine=minimize(lambda v:v[-1],np.r_[ls.x,maximum(ls.x)+1e-8],method='SLSQP',bounds=[*zip(low,high),(0,None)],constraints=[dict(type='ineq',fun=lambda v:np.r_[v[-1]-bin_errors(v[:-1]),rails(v[:-1])])],options=dict(maxiter=3000,ftol=1e-10))
        refined=report(refine.x[:-1],refine,refine.x[-1])
        valid=[v for v in (original,refined) if v['converged'] or v['zeroFloorBracketCodes'] is not None]
        chosen=min(valid,key=lambda v:v['maximumCodes']) if valid else original
        records.append(dict(startIndex=i,initial=start.tolist(),leastSquares=report(ls.x,ls),
                            minimax=chosen,rawStartMinimax=original,lsSeededMinimax=refined))
    def best(key,objective):
        good=[r for r in records if r[key]['converged'] or (key=='minimax' and r[key]['zeroFloorBracketCodes'] is not None)]
        if not good:return None
        row=min(good,key=lambda r:(r[key][objective],r['startIndex']))
        return dict(startIndex=row['startIndex'],**row[key])
    return dict(classification='LOCAL; quadrature width plateaus and gauge/rank loss retained',family=family,
                parameters=p,cssWidth=css_width,curvature=curvature,starts=records,
                leastSquares=best('leastSquares','weightedSquaredError'),minimax=best('minimax','maximumCodes'))
