#!/usr/bin/env python3.12
"""Physical constant-alpha source-over subset, shared RGB alpha (§5.176).

The unrestricted affine responses do not by themselves identify alpha and target.
This constrained follow-up tests a genuine stroke: 0<=alpha<=1, one target RGB in
[0,1], band [0,1) device px, and G0's constrained body baseline. Premultiplied
stroke targets t_c=alpha*T_c obey 0<=t_c<=alpha. Both objectives fit calibration.
"""
import json
import numpy as np
from scipy.optimize import linprog, minimize, LinearConstraint, Bounds
import identification as M
import forward as F


def solve(X,y,method):
    A=np.c_[-np.ones(3),np.eye(3)]
    if method=='least-squares':
        H=X.T@X/len(y);q=X.T@y/len(y)
        out=minimize(lambda b:float(b@H@b-2*q@b),np.array([.5,.25,.25,.25]),
                     jac=lambda b:2*(H@b-q),bounds=Bounds(0,1),
                     constraints=[LinearConstraint(A,-np.inf,0)],method='SLSQP',
                     options={'ftol':1e-12,'maxiter':1000})
        if not out.success:raise RuntimeError(out.message)
        return out.x
    ids=set(np.linspace(0,len(y)-1,min(256,len(y)),dtype=int))
    for _ in range(100):
        take=np.array(sorted(ids));z=np.ones(len(take))
        out=linprog([0,0,0,0,1],A_ub=np.vstack([np.c_[X[take],-z],np.c_[-X[take],-z],np.c_[A,np.zeros(3)]]),
                    b_ub=np.r_[y[take],-y[take],np.zeros(3)],bounds=[(0,1)]*4+[(0,None)],method='highs')
        if not out.success:raise RuntimeError(out.message)
        err=abs(X@out.x[:4]-y)
        if err.max()<=out.x[4]+1e-7:return out.x[:4]
        ids.update(np.argsort(err)[-32:].tolist())
    raise RuntimeError('constrained minimax did not converge')


def main():
    records,_=M.extract(M.W.default_wave())
    records=[r for r in records if r['cov'] is not None and r['backgroundKind'] in ['solid','linear-gradient']]
    for r in records:
        r['exactBaselines']={s:F.baseline(r,s,r['alignment']['translationDevicePx'],cov=r['cov'])[0]
                             for s in ['encoded','linear']}
    fits=[]
    for profile,pose in sorted({(r['profile'],r['pose']) for r in records}):
        rs=[r for r in records if (r['profile'],r['pose'])==(profile,pose) and r['role']=='calibration']
        for space in ['encoded','linear']:
            xs=[];ys=[]
            for r in rs:
                D=r['D']/255;N=r['n']/255
                if space=='linear':D,N=M.decode(D),M.decode(N)
                g=r['cov']['band'];X=np.zeros((len(g),3,4));X[:,:,0]=-g[:,None]*D
                for c in range(3):X[:,c,c+1]=g
                xs.append(X.reshape(-1,4));ys.append((N-r['exactBaselines'][space]).ravel())
            for method in ['least-squares','minimax']:
                b=solve(np.concatenate(xs),np.concatenate(ys),method)
                fit=dict(profile=profile,pose=pose,method=method,
                    spec=dict(name='body-forward-affine',space=space,stage='new-axes',power=2.,exactBody=True,
                              domain='circular solid and affine gradient',physicalSharedAlpha=True),
                    coefficients=[[-float(b[0]),float(b[c+1])] for c in range(3)],
                    alpha=float(b[0]),targetRGB=(b[1:]/b[0]).tolist() if b[0]>1e-12 else None,
                    calibrationCells=len(rs))
                fits.append(fit);print('physical alpha',len(fits),profile,pose,space,method,flush=True)
    M.save(M.HERE/'alpha-fits.json',fits)
    M.evaluate(records,fits,'alpha-validation')


if __name__=='__main__':main()
