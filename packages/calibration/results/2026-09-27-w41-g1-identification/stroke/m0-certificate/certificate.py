"""Exact necessary-bin-mean certificates for the sealed M0 law, not a fitter.

At one identical geometry/bin, uniform b and inactive shadow imply mean output
b + c*(clip(t*b+k,0,255)-b), where c is the mean quadrature coverage. Replacing
any of device/CSS/nominal-curvature coverage by arbitrary common c in [0,1]
RELAXES its law (including its max-normal gauge). Set u=c*t and v=c*k.
Monotonicity t>=0 orders intrinsic clipping low/middle/high; enumerate every
pair of break indices, including empty regions and the c=0 limit. Boundaries
can occur in either neighboring region. Bin-mean intervals are only necessary
by Jensen for absolute-before-bin mean error; no positive survival is claimed.

The LP proposes a dual support. Rational elimination and inequality arithmetic,
not its numerical status, authorize each infeasibility result. Every regime
must have a verified exact Farkas proof before rejecting a model-endpoint.
"""
from fractions import Fraction as F
from itertools import combinations
import numpy as np
from scipy.optimize import linprog


def regimes(n):
    return [[i,j] for i in range(n+1) for j in range(i,n+1)]


def constraints(rows, regime):
    """Return exact A*x<=rhs in x=(c,u,v); rows may repeat each input level."""
    bs=sorted({F(row['b']) for row in rows})
    i,j=regime
    if not 0<=i<=j<=len(bs): raise ValueError('invalid ordered clip regime')
    a=[]; rhs=[]; labels=[]
    def add(coeff, bound, label):
        a.append([F(v) for v in coeff]); rhs.append(F(bound)); labels.append(label)
    for coeff,bound,label in [([1,0,0],1,'c<=1'),([-1,0,0],0,'c>=0'),
            ([0,-1,0],0,'u>=0'),([-3,1,0],0,'u<=3c'),
            ([-255,0,1],0,'v<=255c'),([-255,0,-1],0,'v>=-255c')]:
        add(coeff,bound,label)
    for n,b in enumerate(bs):
        if n<i: add([0,b,1],0,f'b={b}:low')
        elif n<j:
            add([0,-b,-1],0,f'b={b}:mid-low')
            add([-255,b,1],0,f'b={b}:mid-high')
        else: add([255,-b,-1],0,f'b={b}:high')
    for k,row in enumerate(rows):
        b=F(row['b']); n=bs.index(b)
        coeff=[-b,0,0] if n<i else [-b,b,1] if n<j else [255-b,0,0]
        mean=F(row['mean']); bound=F(row['bound'])
        add(coeff,mean+bound-b,f'row{k}:upper')
        add([-v for v in coeff],b-mean+bound,f'row{k}:lower')
    return a,rhs,labels


def exact_weights(a):
    """Solve A_support^T*w=0, sum(w)=1 by rational elimination."""
    n=len(a); p=len(a[0])
    matrix=[[a[j][i] for j in range(n)]+[F(0)] for i in range(p)]
    matrix.append([F(1)]*n+[F(1)])
    for col in range(n):
        pivot=next((r for r in range(col,p+1) if matrix[r][col]),None)
        if pivot is None: return None
        matrix[col],matrix[pivot]=matrix[pivot],matrix[col]
        d=matrix[col][col]; matrix[col]=[v/d for v in matrix[col]]
        for r in range(p+1):
            if r!=col:
                d=matrix[r][col]
                matrix[r]=[v-d*w for v,w in zip(matrix[r],matrix[col])]
    if any(not any(row[:-1]) and row[-1] for row in matrix): return None
    return [matrix[i][-1] for i in range(n)]


def verify(cert,a,rhs):
    try:
        idx=cert['indices']; w=[F(x) for x in cert['weights']]
        if not idx or len(idx)!=len(w) or len(set(idx))!=len(idx): return False
        if any(type(i)!=int or not 0<=i<len(rhs) for i in idx): return False
        if any(v<0 for v in w) or sum(w)!=1: return False
        if any(sum(v*a[i][j] for i,v in zip(idx,w))!=0 for j in range(3)): return False
        return sum(v*rhs[i] for i,v in zip(idx,w))<0
    except (KeyError, ValueError, TypeError, ZeroDivisionError): return False


def solve(rows):
    results=[]
    for regime in regimes(len({F(row['b']) for row in rows})):
        a,rhs,labels=constraints(rows,regime)
        af=np.array(a,float); bf=np.array(rhs,float)
        fit=linprog([0,0,0,1],A_ub=np.column_stack((af,-np.ones(len(a)))),b_ub=bf,
                    bounds=[(None,None)]*3+[(0,None)],method='highs',
                    options={'maxiter':10000,'primal_feasibility_tolerance':1e-9,
                             'dual_feasibility_tolerance':1e-9})
        row=dict(regime=regime, status='UNPROVED', constraints=len(a),
                 solverSuccess=bool(fit.success), solverMessage=fit.message)
        cert=None
        if fit.success:
            row['phaseISlack']=float(fit.fun)
            support=tuple(int(k) for k in np.flatnonzero(-fit.ineqlin.marginals>0))
            # At most four supporting inequalities are needed in three unknowns.
            # Bounded exact support search follows the original support attempt.
            extras=list(dict.fromkeys([*range(6),*map(int,np.argsort(bf-af@fit.x[:3])[:12])]))
            seen=set(); attempts=0
            def attempt(indices):
                nonlocal attempts
                idx=tuple(sorted(indices))
                if not idx or len(idx)>4 or idx in seen: return None
                seen.add(idx); attempts+=1
                weights=exact_weights([a[k] for k in idx])
                if weights is None: return None
                candidate=dict(indices=list(idx),weights=list(map(str,weights)))
                if not verify(candidate,a,rhs): return None
                candidate['weightedRhs']=str(sum(w*rhs[k] for k,w in zip(idx,weights)))
                candidate['labels']=[labels[k] for k in idx]
                return candidate
            if fit.fun>0:
                cert=attempt(support)
                pool=list(dict.fromkeys([*support,*extras]))
                for size in range(1,5):
                    if cert or attempts>=2048: break
                    for indices in combinations(pool,size):
                        if attempts>=2048: break
                        cert=attempt(indices)
                        if cert: break
            row['exactAttempts']=attempts
            if cert:
                row.update(status='EXACT_INFEASIBLE',certificate=cert)
            else:
                row['floatingPointCandidate']=fit.x[:3].tolist()
                row['status']='FEASIBLE_OR_UNPROVED'
        results.append(row)
    rejected=all(row['status']=='EXACT_INFEASIBLE' for row in results)
    return dict(status='CERTIFIED_INFEASIBLE_RELAXATION' if rejected else
                'NOT_REJECTED_BY_RELAXATION',regimes=results,
                qualification='Necessary Jensen bin-mean cut only; feasible or unproved is '
                    'not survival, and not rejection. No optimizer outcome replaced.')
