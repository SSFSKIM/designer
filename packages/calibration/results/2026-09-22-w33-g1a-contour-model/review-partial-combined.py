# Independent W33 G1a reviewer artifact, offline, 2026-09-22 (§5.171).
# Preserved scratch script, not a standalone replay: paths/dependencies remain as reviewed.
from pathlib import Path
import json,numpy as np
p=Path('/tmp/w33-g1a-independent-review/partial.py');text=p.read_text();text=text[:text.index('results=[]')];exec(text)
prior=json.loads((out/'partial.json').read_text());results={r['name']:r for r in prior};delta=np.zeros_like(N)
settings={}
for group,ids in schemeGroups.items():
 if group[0]=='accessibility':continue
 ix=np.array(ids);name='active-even-2' if group==('dark','rest') else 'isotropic';strength=results[name]['settings'][str(group)]['strength'];q=abs(NX[ix])**2 if name=='active-even-2' else np.ones(len(ix));coefs=[]
 for c in range(3):
  X=np.column_stack((q*W[ix,c],q));coef=np.linalg.lstsq(X,D[ix,c],rcond=None)[0];delta[ix,c]=strength*(X@coef);coefs.append(coef.tolist())
 settings[str(group)]={'name':name,'strength':strength,'coefficients':coefs}
T=np.floor(np.clip(W+delta,0,255)+.5);P=cap(T)
# The accessibility endpoint is an explicit gate-zero bypass, never reconstructed.
for group,ids in schemeGroups.items():
 if group[0]=='accessibility':P[np.array(ids)]=W[np.array(ids)]
mae,errs=score(P);print('combined simple capped',mae,'ceilings failed',sum(errs>bars+1e-10),settings)
targets=json.loads((ev/'targets.json').read_text());bykey={(r['profile'],r['scene']):r for r in targets['rows']}
for r in rs:bykey[r['profile'],r['scene']]['rgb']=T[r['index']].astype(int).tolist()
(out/'partial-targets.json').write_text(json.dumps(targets))
source=(out/'prices.ts').read_text().replace('resolve(here, "targets.json")',json.dumps(str(out/'partial-targets.json'))).replace(str(out/'prices.json'),str(out/'partial-prices.json'))
(out/'partial-prices.ts').write_text(source)
