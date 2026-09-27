"""A necessary nonnegative-coverage-ratio cut, never a stroke fit or survival test.

On a uniform neutral b with inactive shadow, mean(O_bin)-b is c_bin*d_b,
where d_b=S(b)-b is arbitrary in this RELAXATION. Coverage is geometry-only,
so identical supplied geometry and bin pixels make each c_bin fixed across b.
Every declared rival has c_bin>=0; no angular law or width is fitted here.

For two bins A,B, a departure interval excluding zero in B implies c_B>0.
Then r=c_A/c_B>=0 is common to all levels. The exact possible ratio interval
is the range of x_A/x_B over the two necessary Jensen intervals, intersected
with [0,infinity). Denominator intervals containing zero are omitted, not
silently divided; omission can only relax the problem. Disjoint ratio
intervals prove impossibility. Nonempty intervals do NOT establish survival.
"""
from fractions import Fraction as F


def interval(values):
    low,high=map(F,values)
    if low>high: raise ValueError('empty input departure interval')
    return low,high


def sign(values):
    low,high=interval(values)
    return 'positive' if low>0 else 'negative' if high<0 else 'includes-zero'


def ratio_interval(numerator,denominator):
    a=interval(numerator); b=interval(denominator)
    result=dict(numerator=list(map(str,a)),denominator=list(map(str,b)),
                signs=[sign(a),sign(b)])
    if b[0]<=0<=b[1]:
        return dict(result,status='OMITTED_DENOMINATOR_INCLUDES_ZERO',interval=None,
                    denominatorCoveragePositive=False)
    corners=[x/y for x in a for y in b]
    low=max(F(0),min(corners)); high=max(corners)
    if high<0:
        return dict(result,status='EMPTY_SIGN_CONSTRAINT',interval=None,
                    denominatorCoveragePositive=True)
    return dict(result,status='NECESSARY_INTERVAL',interval=[str(low),str(high)],
                denominatorCoveragePositive=True)


def intersect_ratios(entries):
    rows=[]; low=F(0); high=None; low_owner=None; high_owner=None; impossible_sign=[]
    for i,entry in enumerate(entries):
        row=dict(entry,**ratio_interval(entry['numerator'],entry['denominator']))
        rows.append(row)
        if row['status']=='EMPTY_SIGN_CONSTRAINT':
            impossible_sign.append(i)
        elif row['status']=='NECESSARY_INTERVAL':
            a,b=map(F,row['interval'])
            if a>low:low=a;low_owner=i
            if high is None or b<high:high=b;high_owner=i
    empty=bool(impossible_sign or (high is not None and low>high))
    return dict(status='EXACT_EMPTY_INTERSECTION' if empty else 'NOT_DETERMINING',
                lower=str(low),upper=str(high) if high is not None else None,
                lowerOwner=low_owner,upperOwner=high_owner,signContradictions=impossible_sign,
                strictGap=str(low-high) if high is not None and low>high else None,
                entries=rows,
                qualification='Only necessary Jensen mean intervals; nonempty or omitted '
                    'constraints are not survival or a model-endpoint rejection.')
