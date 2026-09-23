#!/usr/bin/env python3.12
"""A coefficient-free lower bound from a shell the outside stroke cannot reach."""
from collections import defaultdict
import gzip
import json
import identification as M

fits=json.loads((M.HERE/'qualified-fits.json').read_text())[400:]
rows=json.loads(gzip.decompress((M.HERE/'exact-validation-residuals.json.gz').read_bytes()))
groups=defaultdict(list)
for r in rows:
    if r['role']=='validation' and r['shell']==-2 and r['admissible']:
        f=fits[r['fit']]
        groups[(f['profile'],f['pose'],r['part'],f['spec']['space'])].append(r)
output=[]
for key,rs in sorted(groups.items()):
    by_cell=defaultdict(list)
    for r in rs:by_cell[(r['cell'],r['bin'])].append(r)
    for values in by_cell.values():
        assert len({tuple(r['maeRGB']) for r in values})==1
    worst=max(rs,key=lambda r:max(r['maeRGB']))
    output.append(dict(profile=key[0],pose=key[1],part=key[2],space=key[3],
        coefficientIndependentFloor=max(worst['maeRGB']),
        witness={k:worst[k] for k in ['cell','bin','pixels','maeRGB','barRGB','tauRGB']},
        proof='For d in [-2,-1), every subpixel remains inside the nominated body: the unit pixel half-diagonal is sqrt(.5)<1. The outside band [0,1) has zero coverage. Every alpha/target/angular coefficient multiplies zero. All four fitted alternatives per space agree exactly on each such bin. This is a floor for the nominated body/path decomposition, not exclusion of Apple stroke colour in isolation.'))
M.save(M.HERE/'coefficient-independent-floors.json',output)
