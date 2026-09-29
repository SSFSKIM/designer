"""W42 G0 rehearsal: coefficient sensitivity on the cells where a referee fails.

A referee fails "by construction" (charter clause 3) when it fails whatever the structure's
coefficients. The structure's two free parameters are kappa and lambda (charter, "The law":
the count is 2 per endpoint); this sweep re-renders (swaps) and re-measures only the failing
cells over a grid of both, with the variant's T, and reports each referee's per-cell quantity:
L1's error and growth against its W33 baseline, M2's move and Decision Log 5a verdict, M1's R.
Rows are measured by `compare --skip-capture`, exactly as `measure.py` does; nothing is
published and nothing is written inside the repository.

    python3.12 -B sweep.py --variant c2 --cells P/S,P/S --kappa 1.6,2.07,2.5 --lam 0.5,0.7,0.9,1 \\
        --out /scratch/sweep-c2-dr
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import body as B  # noqa: E402
import swap as S  # noqa: E402

L1_DECL = json.loads((S.CAL / 'results/2026-09-24-w36-g0-level-cut/l1-declaration.json').read_text())


def l1_baseline():
    out = {}
    sys.path.insert(0, str(HERE.parent / 'referees'))
    import referee_source as rs
    for scheme, g in L1_DECL['baselineGeneration'].items():
        for c in rs.generation(g['active'], g['receded'])[0]:
            if c['key']['web']['renderer'] == 'webgpu':
                out[(c['key']['profileKey'], c['key']['sceneId'])] = c
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--variant', required=True)
    ap.add_argument('--cells', required=True)
    ap.add_argument('--kappa', default='')
    ap.add_argument('--lam', default='')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    cells = [tuple(c.split('/')) for c in args.cells.split(',')]
    rows = {(r['key']['profileKey'], r['key']['sceneId']): r for r in S.population()}
    base = l1_baseline()
    kappas = [None] + [float(k) for k in args.kappa.split(',') if k]
    lams = [float(x) for x in args.lam.split(',') if x] or [B.LAMBDA]
    results = []
    for kappa, lam in itertools.product(kappas, lams):
        tag = f"k{'mE' if kappa is None else kappa}-l{lam}"
        S.OVERRIDE.clear()
        S.OVERRIDE.update(kappa=kappa, lam=lam)
        tree = args.out / tag / 'tree'
        for p, s in cells:
            scheme = 'light' if '-light-' in p else 'dark'
            S.swap_cell(args.variant, rows[(p, s)], tree, S.documents(args.variant, scheme))
        for p in sorted({p for p, _ in cells}):
            scheme = 'light' if '-light-' in p else 'dark'
            docs = HERE / 'documents' / args.variant
            m = args.out / tag / f'{p}.json'
            scenes = ','.join(s for q, s in cells if q == p)
            env = dict(os.environ, VITREA_WEB_CAPTURES=str(tree))
            cmd = ['pnpm', '-s', 'run', 'compare', '--', '--skip-capture', '--profile', p,
                   '--renderer', 'webgpu', '--set', 'calibration,validation,probe', '--scene', scenes,
                   '--material-profile', str((docs / f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json').relative_to(S.CAL)),
                   '--receded-profile', str((docs / f'apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded.json').relative_to(S.CAL)),
                   '--out-matrix', str(m)]
            subprocess.run(cmd, cwd=S.CAL, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for r in S.store.load_current_rows(matrix_path=str(m)):
                key = (p, r['key']['sceneId'])
                mat, ref = r['material'], rows[key]['material']
                val = lambda x, f: x[f]['value'] if f in x else None
                n, w = val(mat, 'interiorMeanNative'), val(mat, 'interiorMeanWeb')
                b = base.get(key)
                be = None if b is None else abs(val(b['material'], 'interiorMeanWeb') - val(b['material'], 'interiorMeanNative'))
                sd_r, sd_w, sd_n = val(ref, 'interiorStdDevWeb'), val(mat, 'interiorStdDevWeb'), val(mat, 'interiorStdDevNative')
                d = (sd_w - sd_r) / sd_r
                toward, beyond = (sd_w - sd_r) * (sd_n - sd_r) > 0, (sd_w - sd_n) * (sd_n - sd_r) > 0
                m2 = 'within' if abs(d) <= 0.02 else ('named' if toward and (not beyond or abs(sd_w - sd_n) / sd_n <= 0.02) else 'FAIL')
                R = None
                if 'chromaStructureRatioWeb' in mat:
                    R = val(mat, 'chromaStructureRatioWeb') / val(mat, 'chromaStructureRatioNative')
                results.append(dict(tag=tag, kappa=kappa if kappa is not None else 'memoE', lam=lam,
                                    cell=f'{p}/{r["key"]["sceneId"]}', l1Error=abs(w - n),
                                    l1Growth=None if be is None else abs(w - n) - be,
                                    m2Delta=d, m2Verdict=m2, M1R=R))
        shutil.rmtree(tree)
    (args.out / 'sweep.json').write_text(json.dumps(results, indent=1) + '\n')
    for r in results:
        g = '' if r['l1Growth'] is None else f"{r['l1Growth']:+.4f}"
        R = '' if r['M1R'] is None else f"{r['M1R']:.3f}"
        print(f"{r['tag']:14s} {r['cell'][17:]:62s} L1 {r['l1Error']:.4f} g {g:8s} "
              f"M2 {r['m2Delta'] * 100:+7.2f}% {r['m2Verdict']:6s}  R {R}")

if __name__ == '__main__':
    main()
