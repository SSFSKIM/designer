"""Add only the sealed algebraic range -b<=A*(S(b)-b)<=255-b.

The unbounded screen and its small-width quadrature alias remain unchanged.
M0/M1 clip output to0..255. M2 encodes its held-luma gamut-compressed output
in that same range (on neutral inputs its contextual correction is identity).
The sealed angular law gives0<=A<=1 including beta1/A0. Consequently each
product lies in[-b,255-b], with no empirical bound or new parameter introduced.
"""
from fractions import Fraction as F
import width_cut as cut


def solve(thresholds,groups):
    rows={}
    bounds={}
    for key,values in groups.items():
        bs={F(r['b']) for r in values}
        if len(bs)!=1:raise ValueError('one relaxed z cannot mix input levels')
        b=bs.pop()
        bounds[key]=dict(geometry='sealed-z-bound',lower=str(-b),upper=str(255-b),
                         kind='sealed-angular-and-material-range',b=str(b))
        rows[key]=[*values,bounds[key]]
    states=[]
    for state in cut.states(thresholds):
        fractions={key:str(cut.fraction(ts,state['representative'])) for key,ts in thresholds.items()}
        fractions['sealed-z-bound']='1'
        intersections={key:cut.intersect(values,fractions) for key,values in rows.items()}
        states.append(dict(**state,fractions=fractions,groups=intersections,
                           feasible=all(v['feasible'] for v in intersections.values())))
    levels=sorted({F(v['b']) for v in bounds.values()})
    single={str(b):all(any(not state['groups'][key]['feasible'] for key in groups
                           if F(bounds[key]['b'])==b) for state in states) for b in levels}
    rejected=all(not s['feasible'] for s in states)
    return dict(status='CERTIFIED_INFEASIBLE_RELAXATION' if rejected else 'NOT_REJECTED_BY_RELAXATION',
                stateCount=len(states),pointCount=sum(s['kind']=='point' for s in states),
                openIntervalCount=sum(s['kind']=='open' for s in states),
                feasibleStateIndices=[i for i,s in enumerate(states) if s['feasible']],
                independentlyRejectingInputLevels=[b for b,rejects in single.items() if rejects],
                bounds=bounds,states=states)
