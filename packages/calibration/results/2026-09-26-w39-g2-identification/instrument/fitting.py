"""Calibration-only LS and minimax; caller supplies only its admitted fit arrays.

The normalized weights assign equal total mass to each cell and to each channel
within it. Edge callers reduce equally over bins before supplying constraints.
No ridge, prior, or rank repair is used. Nonconvergence is explicit, never a pass.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.optimize._numdiff import approx_derivative


def fit(forward,target,initial,bounds=None,monotone_start=None):
    target=np.asarray(target,float);initial=np.asarray(initial,float)
    bounds=bounds or [(None,None)]*len(initial)
    weights=np.ones_like(target)/target.size
    def residual(q):return np.asarray(forward(q))-target
    constraints=[]
    if monotone_start is not None:
        constraints=[dict(type='ineq',fun=lambda q:np.diff(q[monotone_start:]))]
    ls=minimize(lambda q:float(np.sum(weights*residual(q)**2)),initial,
        method='SLSQP',bounds=bounds,constraints=constraints,options=dict(ftol=1e-14,maxiter=3000))
    start=np.r_[ls.x,np.max(abs(residual(ls.x)))+1e-8]
    mmconstraints=[dict(type='ineq',fun=lambda p:np.r_[p[-1]-residual(p[:-1]).ravel(),p[-1]+residual(p[:-1]).ravel()])]
    if monotone_start is not None:
        mmconstraints.append(dict(type='ineq',fun=lambda p:np.diff(p[monotone_start:-1])))
    mm=minimize(lambda p:p[-1],start,method='SLSQP',bounds=[*bounds,(0,None)],
        constraints=mmconstraints,options=dict(ftol=1e-12,maxiter=3000))
    def report(result,q):
        r=residual(q);j=approx_derivative(lambda p:np.asarray(forward(p)).ravel(),q).reshape(target.size,len(q))
        s=np.linalg.svd(j,compute_uv=False)
        return dict(coefficients=q.tolist(),rss=float(np.sum(r*r)),meanSquared=float(np.sum(weights*r*r)),
            maximum=float(np.max(abs(r))),rank=int(np.linalg.matrix_rank(j)),
            columns=len(q),singularValues=s.tolist(),converged=bool(result.success),
            message=str(result.message),iterations=int(result.nit))
    return dict(leastSquares=report(ls,ls.x),minimax=report(mm,mm.x[:-1]))
