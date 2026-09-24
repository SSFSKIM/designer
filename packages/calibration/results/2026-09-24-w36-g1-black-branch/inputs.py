"""Read admitted packed tone inputs after the canonical generation check (§5.179, DL5)."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import WebReader
assert 'VERDICT  the tree and the working matrix name the same generation everywhere they meet.' in (HERE/'canonical-generation-check.txt').read_text()
r=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
out=[]
for cell in sorted(r.roles.cells):
    if not cell.startswith('apple-macos-27.0-') or '-standard-' not in cell:continue
    try:r.admit(cell)
    except (PermissionError,ValueError):continue
    try:report=json.loads(r.read(cell,'report'))
    except FileNotFoundError:continue
    for group in report['page']['groups']:
        local=group['state'].get('backdropToneAbscissae',[])
        if local:
            inputs=[(v['surfaceId'],v['encodedLuminance'],'packed silhouette') for v in local]
        elif group.get('backdropTone'):
            y=group['backdropTone']['level']
            x=12.92*y if y<=.0031308 else 1.055*y**(1/2.4)-.055
            inputs=[(group['id'],x,'source encoded')]
        else:continue
        for node,x,kind in inputs:
            if x<.004:out.append(dict(cell=cell,node=node,input=x,kind=kind,role=r.roles.roles[cell.split('/')[1]]))
result=dict(join=.003,minimum=min(v['input'] for v in out),rows=out,
    rationale='Join 0.003, below the minimum packed impulse input by at least 0.00019; no Hermite knot or slope changes.')
with (HERE/'join-inputs.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
