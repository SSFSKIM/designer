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

def verdict(r):
    if r['bar'] is None:
        return 'n/a (no memo E bar)'
    return 'PASS' if r['pooled'] >= r['bar'] else 'NOT REFUSED: non-identifiable by the declared pooled bar'


def _void(r):
    return any(abs(v - 4.0) < 1e-3 for v in r['x'].values()) and r['fit'] == 'null-dev'


if __name__ == '__main__':
    # The active mask is the caller's (W42_KERNEL, default 'n': the revised ruling 3's primary). Until the review of
    # b151aff4 this script forced 'w', so a re-run reproduced the fallback's mask, and the recorded active rows
    # mixed the two masks. A row counts only at the current pin, kernel and engine.
    import os
    import forward as F
    import proof_common as PC
    here = lambda r: (r.get('bed'), r.get('kernel'), r.get('engine')) == (
        bed.BED_COMMIT[:8], PC.KERNEL if r['ep'].endswith('rest') else 'receded (no band)', F.ENGINE)
    try:
        rows = [r for r in json.load(open('proof2_nulls.json')) if not _void(r)]
    except FileNotFoundError:
        rows = []
    done = {(r['fit'], r['ep']) for r in rows if here(r)}
    jobs = [(n, ep) for n in P.NULLS for ep in P.EPS if (n, ep) not in done]
    with Pool(int(os.environ.get('W42_POOL', '2'))) as pool:
        for r in pool.imap_unordered(P.run_null, jobs):
            r['bed'] = bed.BED_COMMIT[:8]
            r['engine'] = F.ENGINE
            r['bar'] = BARS[r['fit']]
            r['verdict'] = verdict(r)
            rows.append(r)
            print(r['fit'], r['ep'], round(r['pooled'], 2), r['verdict'], flush=True)
            json.dump(rows, open('proof2_nulls.json', 'w'), indent=1, default=float)
    rows.sort(key=lambda r: (r['fit'], r['ep']))
    cur = [r for r in rows if here(r)]
    L = ['W42 G0 proof 2, rejected nulls fitted to an LT truth: pooled rms (codes) against memo E\'s separation bars',
         f'(tolerances.json). Current rows: pin {bed.BED_COMMIT[:8]}, engine {F.ENGINE}, active mask kernel '
         f'{PC.KERNEL}. A null whose pooled rms misses its declared bar is NOT refused by this bed\'s synthetic proof',
         '(clause 2\'s stop: non-identifiable by the declared bar); its worst cell is a descriptive reading. The unit',
         'nulls are refereed in the sitting by the 1x pass (worst cells, not the pooled rms of a mostly-2x bed).']
    for r in cur:
        L.append(f"  {r['fit']:14s} {r['ep']:15s} pooled {r['pooled']:6.2f} max cell {r['max_cell']:6.2f} bar "
                 f"{r['bar']} {r['verdict']} x {r['x']} ({r['n_cells']} cells) kernel {r.get('kernel')}")
    old = [r for r in rows if not here(r)]
    if old:
        L += ['', 'superseded rows (earlier pins, the mixed active masks of b151aff4, the engine before its review):']
        for r in old:
            L.append(f"  {r['fit']:14s} {r['ep']:15s} pooled {r['pooled']:6.2f} max cell {r['max_cell']:6.2f} "
                     f"pin {r.get('bed')} kernel {r.get('kernel', 'n (pre-ruling)')} engine {r.get('engine', '-')}")
    open('proof2_nulls.txt', 'w').write('\n'.join(L) + '\n')
