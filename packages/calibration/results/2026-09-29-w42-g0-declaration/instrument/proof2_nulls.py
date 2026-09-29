"""W42 G0 proof 2, the rejected nulls (memo E's control on the new bed's geometry): LT rendered at its truth on
the structured families B, B', C and D of both scales, each rejected null fitted to it by least squares; its
pooled rms against memo E's bars (tolerances.json: the mixture reading >= 2.60, texel or device-px units and
R2 >= 4.65). A first run on 2x cells alone is kept beside it (proof2_nulls-2xonly.json): it showed the unit
nulls cannot be refused at one scale. Run apart from proof2_separation.py's
pairs so the two can proceed at once; writes proof2_nulls.json / .txt."""
import json
from multiprocessing import Pool

import bed
import proof2_separation as P

BARS = {'null-mix': 2.60, 'null-texel': 4.65, 'null-dev': 4.65, 'null-R2': 4.65, 'null-boxfloor': None}

def _void(r):
    return any(abs(v - 4.0) < 1e-3 for v in r['x'].values()) and r['fit'] == 'null-dev'


if __name__ == '__main__':
    import os
    import proof_common as PC
    PC.KERNEL = 'w'     # ruling 3: an LT fit reads W, so its active mask adds 2 sigma_w
    try:
        rows = [r for r in json.load(open('proof2_nulls.json')) if not _void(r)]
    except FileNotFoundError:
        rows = []
    done = {(r['fit'], r['ep']) for r in rows}
    jobs = [(n, ep) for n in P.NULLS for ep in P.EPS if (n, ep) not in done]
    with Pool(int(os.environ.get('W42_POOL', '2'))) as pool:
        for r in pool.imap_unordered(P.run_null, jobs):
            r['bed'] = bed.BED_COMMIT[:8]
            r['bar'] = BARS[r['fit']]
            r['verdict'] = 'n/a (no memo E bar)' if r['bar'] is None else ('PASS' if r['pooled'] >= r['bar'] else 'FAIL')
            rows.append(r)
            print(r['fit'], r['ep'], round(r['pooled'], 2), r['verdict'], flush=True)
            json.dump(rows, open('proof2_nulls.json', 'w'), indent=1, default=float)
    rows.sort(key=lambda r: (r['fit'], r['ep']))
    L = ['W42 G0 proof 2, rejected nulls fitted to an LT truth: pooled rms (codes) against memo E\'s separation bars',
         'kernel: the active mask\'s support (rows without it ran at the narrow support, before ruling 3)']
    for r in rows:
        L.append(f"  {r['fit']:14s} {r['ep']:15s} pooled {r['pooled']:6.2f} max cell {r['max_cell']:6.2f} bar "
                 f"{r['bar']} {r['verdict']} x {r['x']} ({r['n_cells']} cells) kernel {r.get('kernel', 'n (pre-ruling)')}")
    open('proof2_nulls.txt', 'w').write('\n'.join(L) + '\n')
