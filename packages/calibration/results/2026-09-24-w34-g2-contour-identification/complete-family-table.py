#!/usr/bin/env python3.12
"""All family/comparator/domain results, with no pooled closure score (§5.176)."""
import csv
import json
from collections import defaultdict
import identification as M

sources=[('no-glass','validation-headlines.json','fits.json',0),
         ('shipped-web','w33-web-validation-headlines.json','w33-web-fits.json',0),
         ('exact-body','exact-validation-headlines.json','qualified-fits.json',400),
         ('physical-shared-alpha','alpha-validation-headlines.json','alpha-fits.json',0)]
rows=[]
for comparator,headfile,fitfile,offset in sources:
    heads=json.loads((M.HERE/headfile).read_text());fits=json.loads((M.HERE/fitfile).read_text())
    groups=defaultdict(list)
    for row in heads:
        if row['role']=='validation':groups[(row['profile'],row['pose'],row['part'],row['name'],row['space'])].append(row)
    for key,group in sorted(groups.items()):
        best=min(group,key=lambda r:(r['worstMAE'],r['shellZeroWorstMAE'],r['fit']))
        i=best['fit']+offset;spec=fits[i]['spec']
        rows.append(dict(comparator=comparator,profile=key[0],pose=key[1],part=key[2],family=key[3],space=key[4],
            objective=best['method'],fitFile=fitfile,fit=i,power=spec.get('power'),
            angleRadians=spec.get('angle',0),worstAbsoluteBin=best['worstMAE'],
            shellZeroWorstAbsoluteBin=best['shellZeroWorstMAE'],observedBarMaximum=best['maxBar'],
            effectiveTolerance=1,populatedBins=best['bins'],pixels=best['pixels'],
            underpopulatedBins=best['underpopulated'],outcome=best['outcome'],
            domain=spec.get('domain','all shapes' if spec['stage']=='W33-first' else 'circular only')))
M.save(M.HERE/'family-best-complete.json',rows)
with (M.HERE/'family-best-complete.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(len(rows),'family/space/comparator/domain/part validation rows; no holdout')
