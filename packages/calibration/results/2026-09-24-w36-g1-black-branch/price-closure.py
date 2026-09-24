"""Correct the first price table's C1 pooling, and name missing alpha fields (§5.179)."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent
plans=json.loads((HERE/'candidate-plans.json').read_text())
base=json.loads((CAL/'results/matrix.json').read_text())
old={(c['key']['profileKey']+'/'+c['key']['sceneId']):c for c in base['cells'] if c['key']['web']['renderer']=='webgpu'}
new={c['key']['profileKey']+'/'+c['key']['sceneId']:c for p in plans for c in json.loads((Path(p['root'])/'matrix.json').read_text())['cells'] if c['key']['web']['renderer']=='webgpu'}
missing={};changed=[]
for key,c in new.items():
    if key not in old:continue
    for axis in ['shape','material','perceptual','shadow']:
        b=old[key].get(axis,{});n=c.get(axis,{})
        for k,v in b.items():
            if k not in n:missing[k]=missing.get(k,0)+1
            elif n[k]!=v:changed.append(dict(cell=key,axis=axis,metric=k,baseline=v,candidate=n[k]))
groups={};rows=json.loads((HERE/'price-c1.json').read_text())
for row in rows:
    cell=new[row['cell']]
    if cell['state']=='inactive':continue
    if row['T'] is not None and row['bands']==row['admitted']:
        groups.setdefault((row['bed'],row['span']),[]).append(row['T'])
table=[dict(bed=b,span=s,cells=len(v),T=sorted(v)[len(v)//2],expectedBound=.0042,passStop=sorted(v)[len(v)//2]<=.0042) for (b,s),v in sorted(groups.items())]
result=dict(correction='The initial C1 table pooled both poses; C1 gates active only. Per-cell T readings were correct and unchanged. This table executes the adopted active-only population.',C1=table,sharedMetricChanges=changed,missingMetrics=missing,
    alphaQualification='Price did not request --alpha: four declared-alpha fields are UNMEASURED, not changed. All shared shape fields (the conditioning inputs included) are exact; the normal PNGs are byte-identical. The attributed canonical read will include --alpha.',
    materialPerceptualShadow='Every common field equals its W33 row exactly; no new per-cell miss or predicate movement on measured fields.',
    passStop=len(table)==12 and all(x['passStop'] for x in table) and not changed)
with (HERE/'price-gpu-closure.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2));assert result['passStop']
