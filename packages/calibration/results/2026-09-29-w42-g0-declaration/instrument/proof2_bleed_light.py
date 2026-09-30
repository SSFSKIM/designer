"""W42 G0 proof 2, the dump-literal bleed's LIGHT pairs, bounded without a fit (the review of b151aff4, I-3).

In light the literal bleed is a darken blend toward Q = 0.9 + 0.1 sat(Bl) at w = 0.5 t r(d): it can only pull a
channel down where the composite exceeds Q, i.e. above about 0.9 encoded, and inside the deep mask the band leaves
w at most 0.27 (rrect-lg). On this bed that moves no pixel by more than a few hundredths of a code, so each pair is
bounded at the truth's own parameters: the other family evaluated at the SAME k, lam (and k_b) reaches every region
statistic of the truth's exact render within s_bound. A least-squares-and-minimax fit can only do as well or better
at its own optimum, so s <= s_bound, and s_bound < 0.5 is UNRESOLVED by construction. Whole bed: families B, B',
C, D and E, both scales, at the narrow-support mask. Writes proof2_bleed_light.json / .txt.
"""
import json

import numpy as np

import bed
import families as FA
import forward as F
import proof_common as PC

EP = 'light-rest'
LETTERS = ('B', "B'", 'C', 'D', 'E')


def bound(truth_name, fit_name, cells):
    tfam, ffam = FA.FAMILIES[truth_name][0], FA.FAMILIES[fit_name][0]
    p = PC.truth(truth_name if truth_name != 'LT' else fit_name, EP)
    p.setdefault('k_b', p['k'])
    q = F.expand(tfam, p)
    exact = [F.render(c, tfam, q) for c in cells]
    st = PC.stats_list(cells, exact)
    preds = [F.render(c, ffam, F.expand(ffam, p)) for c in cells]
    s, where = PC.survival_misfit(cells, preds, st)
    px = max(float(np.abs(a - b).max()) for a, b in zip(exact, preds))
    return dict(truth=truth_name, fit=fit_name, ep=EP, whole=True, n_cells=len(cells), s_bound=s, where=where,
                max_pixel=px, params={k: v for k, v in p.items() if k in ('k', 'lam', 'k_b')},
                verdict=PC.verdict(s) + ' (bound at the truth\'s own parameters; no fit)', bed=bed.BED_COMMIT[:8],
                kernel='n', engine=F.ENGINE)


if __name__ == '__main__':
    cells = bed.cells(EP, 2, letters=LETTERS, kernel='n') + bed.cells(EP, 1, letters=LETTERS, kernel='n')
    rows = []
    for n in [n for n in FA.FAMILIES if 'bleed-lit' in n]:
        for t, f in ((n, 'LT'), ('LT', n)):
            r = bound(t, f, cells)
            rows.append(r)
            print(f"{t} -> {f}: s <= {r['s_bound']:.3f} (max pixel {r['max_pixel']:.3f}) {r['verdict']}", flush=True)
    json.dump(rows, open('proof2_bleed_light.json', 'w'), indent=1, default=float)
    L = ['W42 G0 proof 2: the dump-literal bleed against LT in LIGHT active, bounded at the truth\'s own parameters',
         f'(whole bed, B-E, both scales, narrow mask, pin {bed.BED_COMMIT[:8]}): s_bound >= the fitted s.']
    for r in rows:
        L.append(f"  {r['truth']:>22s} -> {r['fit']:<22s} s <= {r['s_bound']:.3f}  max pixel {r['max_pixel']:.3f} code  "
                 f"{r['verdict']}  ({r['n_cells']} cells)")
    open('proof2_bleed_light.txt', 'w').write('\n'.join(L) + '\n')
