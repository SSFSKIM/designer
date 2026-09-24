"""Re-derive L1 at the read, against its named superseded W33 generation (§5.179)."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent
G0=HERE.parent/'2026-09-24-w36-g0-level-cut'
d=json.loads((G0/'l1-declaration.json').read_text());snapshot=json.loads((G0/'l1-baseline.json').read_text());sealed=json.loads((HERE/'sealed-manifest.json').read_text())['documents']
baseline={}
for scheme,generation in d['baselineGeneration'].items():
    for c in json.loads((CAL/generation['supersededFile']).read_text())['cells']:
        if c['key']['web']['renderer']=='webgpu' and f"sha256:{generation['active']}" in c['key']['web']['capturePath']:
            baseline[c['key']['profileKey']+'/'+c['key']['sceneId']]=c
current={c['key']['profileKey']+'/'+c['key']['sceneId']:c for c in json.loads((CAL/'results/matrix.json').read_text())['cells'] if c['key']['web']['renderer']=='webgpu'}
def value(c,k):return c.get('material',{}).get(k,{}).get('value')
rows=[]
for b in snapshot:
    old=baseline[b['cell']];c=current[b['cell']]
    for name,doc in sealed.items():
        scheme='dark' if '-dark-' in name else 'light'
        if '-'+scheme+'-' in c['key']['profileKey']:
            assert 'sha256:'+doc['fileSha256'][:12] in c['key']['web']['capturePath']
    n,w=value(c,'interiorMeanNative'),value(c,'interiorMeanWeb');bn,bw=value(old,'interiorMeanNative'),value(old,'interiorMeanWeb')
    error=None if n is None or w is None else abs(w-n);before=None if bn is None or bw is None else abs(bw-bn)
    assert before==b['absoluteError'] and n==bn
    growth=None if error is None or before is None else error-before
    rows.append(dict(cell=b['cell'],capturePath=c['key']['web']['capturePath'],native=n,web=w,baselineError=before,error=error,growth=growth,status='UNMEASURED' if error is None else 'MEASURED',existingMiss=before is not None and before>d['absoluteBound']))
misses=[r for r in rows if r['error'] is not None and r['error']>d['absoluteBound']];growthMisses=[r for r in rows if r['growth'] is not None and r['growth']>d['growthBound']]
missing=[r['cell'] for r in rows if r['error'] is None]
result=dict(claims='c9a §5.179',matrixSha256=hashlib.sha256((CAL/'results/matrix.json').read_bytes()).hexdigest(),absoluteBound=d['absoluteBound'],growthBound=d['growthBound'],baselineGeneration=d['baselineGeneration'],population=len(rows),measured=sum(r['error'] is not None for r in rows),missing=missing,absoluteMisses=misses,growthFailures=growthMisses,cells=rows)
with (HERE/'l1-cut.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('L1',result['population'],result['measured'],'missing',len(missing),'absolute misses',len(misses),'growth failures',len(growthMisses),'max growth',max(r['growth'] for r in rows if r['growth'] is not None))
assert len(rows)==140 and result['measured']==136 and sorted(missing)==sorted(d['missing'])
assert sorted(r['cell'] for r in misses)==sorted(r['cell'] for r in d['absoluteMisses']) and not growthMisses
