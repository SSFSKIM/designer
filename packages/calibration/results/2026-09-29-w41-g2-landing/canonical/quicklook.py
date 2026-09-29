"""Owner's early warning, not a referee: the stage's light rows against the pre-W41 rows.

Per profile/scene/tier present in both, prints the chroma-structure ratio R (web/native),
the interior structure change against the retired generation (M2's statistic, 2 % bar),
and the interior level error |web - native| now and before (L1's statistic, 0.055 bar).
The adopted referees are the regenerated cuts; this only says where to look first.
"""
import json
import sys
from pathlib import Path

CAL = Path(__file__).resolve().parents[3]
stage = Path(sys.argv[1])
only = sys.argv[2] if len(sys.argv) > 2 else ''
old = {(r['key']['profileKey'], r['key']['sceneId'], r['key']['web']['renderer']): r
       for r in json.loads((CAL / 'results/generations/85ad7f7e3e0d.json').read_text())['cells']}
new = json.loads((stage / 'matrix.json').read_text())['cells']


def v(r, axis, name):
    x = r.get(axis, {}).get(name)
    return None if x is None else x['value']


rows = []
for r in new:
    k = (r['key']['profileKey'], r['key']['sceneId'], r['key']['web']['renderer'])
    if only and only not in k[1]:
        continue
    o = old.get(k)
    if o is None or r['fixtureSet'] == 'holdout':
        continue
    R = lambda x: (v(x, 'material', 'chromaStructureRatioWeb') or 0) / (
        v(x, 'material', 'chromaStructureRatioNative') or float('nan'))
    sdn, sdo = v(r, 'material', 'interiorStdDevWeb'), v(o, 'material', 'interiorStdDevWeb')
    ln = abs(v(r, 'material', 'interiorMeanWeb') - v(r, 'material', 'interiorMeanNative'))
    lo = abs(v(o, 'material', 'interiorMeanWeb') - v(o, 'material', 'interiorMeanNative'))
    rows.append((k[0].replace('apple-macos-27.0-', ''), k[1], k[2], r['fixtureSet'],
                 R(o), R(r), (sdn / sdo - 1) if sdo else float('nan'), lo, ln))
rows.sort()
print(f"{'profile':34} {'scene':44} {'tier':6} {'set':11} {'R_old':>6} {'R_new':>6} "
      f"{'dStd%':>7} {'L_old':>6} {'L_new':>6}")
for p, s, t, fs, ro, rn, ds, lo, ln in rows:
    flag = ' <' if abs(ds) > 0.02 or ln > 0.055 else ''
    print(f'{p:34} {s:44} {t:6} {fs:11} {ro:6.3f} {rn:6.3f} {100 * ds:7.2f} {lo:6.3f} {ln:6.3f}{flag}')
