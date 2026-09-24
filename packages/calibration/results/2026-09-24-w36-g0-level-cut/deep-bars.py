"""The declared median's own repeat bar, not an edge-bin bar (§5.178 clause 1)."""
import itertools
import numpy as np
from cut import edge,save
rows=[]
for r in edge.cells():
    if not r['cell'].split('/')[1].startswith('grey-'):continue
    scale=r['payload']['scale'];mask=r['geo'][0]<=-6*scale
    states={x['state'] for x in r['runs'] if x['admitted'] and x['protocol']=='normal'}
    medians=[np.median(r['states'][s]['rgb'][mask],axis=0) for s in states]
    pairs=[abs(a-b) for a,b in itertools.combinations(medians,2)]
    bar=np.max(pairs,axis=0) if pairs else np.zeros(3)
    rows.append(dict(cell=r['cell'],role=r['role'],pixels=int(mask.sum()),states=len(states),
        observations=sum(x['admitted'] and x['protocol']=='normal' for x in r['runs']),
        normalDeepMedianBar=bar.tolist(),tolerance=np.maximum(1,bar).tolist()))
save('deep-median-bars.json',rows)
print('Grey cells',len(rows),'max deep median bar',max(max(r['normalDeepMedianBar']) for r in rows))
