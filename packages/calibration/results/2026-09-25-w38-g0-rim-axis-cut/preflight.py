"""Declare pre-W38 artifacts and reproduce the reviewer's known forward point."""
import gzip,hashlib,json,re
from pathlib import Path

from model import HERE,ROOT,CAL,G0,edge,inputs,material,np

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    rows=inputs(structured=False)
    r=next(r for r in rows if r['cell']=='apple-macos-27.0-2x-light-standard-glass0.5/grey-128__circular-120__rest')
    pred=edge.forward(edge.decode(r['body']/255),r['d'],1,a=.2157179550,g=0,width=2.3245354651,shadow_depth=.35,shadow_alpha=.05,shadow_reach=r['reach'],lit=np.maximum(abs(r['ny'])*np.sqrt(2),1e-6)**.85)['encoded']
    points=[]
    for sh in [-2,-1]:
        b=next(b for b in r['bins'] if b['part']=='straight' and b['bin']==12 and b['shell']==sh);ix=b['indices']
        points.append(dict(shell=sh,predictedExcess=(pred[ix]-r['body']).mean(0).tolist(),nativeExcess=(r['native'][ix]-r['body']).mean(0).tolist()))
    summary=dict(cells=84,bins=9637,oldReplayMaximumDifference=0,memoGridExact=True,memoLimitsExact=True,reviewerPoint=dict(exponent=.85,width2x=2.3245354651,a=.2157179550,g=0,along=0,shadowProduct=.0175,rows=points),idealScale=2**(-.85/2),literalScale=.7071**.85,rotationGain=2**(.85/2),literalRotationGain=(1/.7071)**.85,oldLiteralTop=(np.sqrt(2)*.7071)**.85)
    for name in ['scores.json','limits.json','reproduction.json']:
        actual=json.loads((HERE/'memo-reproduction'/name).read_text());original=json.loads((Path('/Users/new/vitrea-w38/grounding')/name).read_text());assert actual==original
    edge.save(HERE/'reproduction-summary.json',summary)
    matrix=json.loads((CAL/'results/matrix.json').read_text());decl=json.loads((ROOT/'apps/reference-apple/scenes.json').read_text());roles={s:role for role,ss in decl['split'].items() for s in ss}
    admitted=[r for r in matrix['cells'] if '27.0' in r['key']['profileKey'] and 'standard' in r['key']['profileKey'] and roles.get(r['key']['sceneId']) in ['calibration','validation','probe']]
    edge.save(HERE/'stop-baseline.json.gz',dict(matrixSha256=sha(CAL/'results/matrix.json'),rows=admitted,meaning='Current recorded values. Prospective nonidentity actual-render values are not identifiable without rendering; numerical forward deltas are not these metrics. No-change closure preserves every row.'))
    docpaths=sorted((CAL/'profiles').glob('*27.0*standard*json'));documents={str(p.relative_to(ROOT)):dict(fileSha256=sha(p),resolvedMaterialSha256=json.loads(p.read_text()).get('resolvedMaterialSha256')) for p in docpaths}
    pinned=['packages/platform-web/e2e/shared/window-activation.spec.ts','packages/renderer-webgpu/e2e/fixtures/harness.ts','packages/calibration/test/tier-coherence.test.ts','packages/calibration/test/adopted-thresholds.test.ts','packages/calibration/results/2026-09-25-w37-g0b-edge-identification/e1-baseline-repaired.json','apps/reference-apple/scenes.json']
    goldens={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'packages/renderer-webgpu/e2e/goldens').glob('*.png'))};assert len(goldens)==13
    window=(ROOT/pinned[0]).read_text();baselines=dict(parent='008b0e4ae6b4dcdb037d375130e499d9adb458f5',matrixSha256=sha(CAL/'results/matrix.json'),documents=documents,goldens=goldens,sourceHashes={p:sha(ROOT/p) for p in pinned},windowActivationHashes=sorted(set(re.findall(r'[0-9a-f]{64}',window))),nonHoldoutStopRows=len(admitted),holdout='No payload read. Only population metadata and complete matrix file digest.')
    edge.save(HERE/'pre-w38-baselines.json',baselines)
    print(json.dumps(summary,indent=2));print('baseline rows',len(admitted))
