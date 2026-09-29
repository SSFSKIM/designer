"""Owner's pre-publication preview of L1 and M2 on the stage (not the regenerated cuts).

L1: W36 G2's adopted population (l1-cut.json's 140 cells) with each light row replaced by
the stage's row for the same profile/scene, |interiorMeanWeb - native| against 0.055 and
growth against the cell's recorded W33 baseline error against 0.005.
M2: the 26 cells of W36 G1's chroma cut; for the light ones, interiorStdDevWeb in the
stage against the retired pre-W41 generation (this gate's re-baseline), bar 2 %.
M1: chromaStructureRatioWeb / Native on the same cells, per-cell [0.6, 1.4], medians
[0.8, 1.2] per scheme and pose.
"""
import json
import statistics
import sys
from pathlib import Path

CAL = Path(__file__).resolve().parents[3]
stage = {(r['key']['profileKey'] + '/' + r['key']['sceneId'], r['key']['web']['renderer']): r
         for r in json.loads((Path(sys.argv[1]) / 'matrix.json').read_text())['cells']}
retired = {(r['key']['profileKey'] + '/' + r['key']['sceneId'], r['key']['web']['renderer']): r
           for r in json.loads((CAL / 'results/generations/85ad7f7e3e0d.json').read_text())['cells']}
v = lambda r, n: (r.get('material', {}).get(n) or {}).get('value')

l1 = json.loads((CAL / 'results/2026-09-24-w36-g2-landing/l1-cut.json').read_text())
out = {'L1': [], 'M2': [], 'M1': []}
missing = []
for c in l1['cells']:
    if '-light-' not in c['cell']:
        continue
    r = stage.get((c['cell'], 'webgpu'))
    if r is None:
        missing.append(c['cell'])
        continue
    n, w = v(r, 'interiorMeanNative'), v(r, 'interiorMeanWeb')
    if n is None or w is None:
        continue
    e = abs(w - n)
    growth = e - c['baselineError'] if c['baselineError'] is not None else None
    out['L1'].append(dict(cell=c['cell'], errorBefore=c['error'], error=e, baselineW33=c['baselineError'],
                          growth=growth, absFail=e > 0.055, growthFail=growth is not None and growth > 0.005))
cut = json.loads((CAL / 'results/2026-09-24-w36-g1-black-branch/chroma-cut.json').read_text())
for c in cut['cells']:
    if '-light-' not in c['profile']:
        continue
    k = (c['profile'] + '/' + c['scene'], 'webgpu')
    r, o = stage.get(k), retired.get(k)
    if r is None or o is None:
        missing.append(k[0])
        continue
    d = v(r, 'interiorStdDevWeb') / v(o, 'interiorStdDevWeb') - 1
    R = v(r, 'chromaStructureRatioWeb') / v(r, 'chromaStructureRatioNative')
    Ro = v(o, 'chromaStructureRatioWeb') / v(o, 'chromaStructureRatioNative')
    out['M2'].append(dict(cell=k[0], structureDelta=d, fail=abs(d) > 0.02,
                          nativeStd=v(r, 'interiorStdDevNative'), webStdBefore=v(o, 'interiorStdDevWeb'),
                          webStd=v(r, 'interiorStdDevWeb')))
    out['M1'].append(dict(cell=k[0], R=R, Rbefore=Ro, fail=not 0.6 <= R <= 1.4))
for pose in ('inactive', 'rest'):
    Rs = [m['R'] for m in out['M1'] if ('__inactive' in m['cell']) == (pose == 'inactive')]
    if Rs:
        out['M1median_light_' + pose] = statistics.median(Rs)
out['missing'] = missing
out['L1summary'] = dict(rows=len(out['L1']), absFail=sum(x['absFail'] for x in out['L1']),
                        growthFail=sum(x['growthFail'] for x in out['L1']))
out['M2summary'] = dict(rows=len(out['M2']), fail=sum(x['fail'] for x in out['M2']))
print(json.dumps(out, indent=1))
