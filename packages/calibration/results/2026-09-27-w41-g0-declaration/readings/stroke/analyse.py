from pathlib import Path
import json,numpy as np,collections
scratch=Path('/Users/new/vitrea-w41/grounding/stroke')
D=json.loads((scratch/'reading.json').read_text()); rows=D['rows']; cells={c['cell']:c for c in D['cells']}
def filt(rr,**kw):return [r for r in rr if all(r.get(k)==v for k,v in kw.items())]
def center(r):return cells[r['cell']]['component']=={'kind':'capsule-circular','size':[120,44],'position':[160,140]}
base=[r for r in rows if center(r)]
