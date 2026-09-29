"""W42 G0 instrument: the resolution table (the stream's hand-back), assembled mechanically from the proofs'
outputs: the family fitters (proof1_families.json, proof2_separation.json) and the statistic readers
(resolution_rows_a.json, resolution_rows_b.json, written by summarize_a.py and report_readers_b.py).

Writes resolution.json (every row, and every pair not distinguished with the bed family that would separate
it) and resolution.txt (the same, readable). The per-pair notes are this stream's reading of WHY a pair is
not separated and WHAT would separate it; they are the only hand-written part.
"""
import json

import numpy as np

EPS = ('light-rest', 'light-inactive', 'dark-rest', 'dark-inactive')

# Why each pair the separation proof does not distinguish stays unresolved, and the bed cell or family that
# would separate it. Keyed (truth, fit, pose): 'rest' = active, 'inactive' = receded, '*' = both.
SEPARATORS = {
    ('W-canvas', 'LT', 'rest'): (
        "U3's active question (does active W read the canvas or R_fp) has no answering cell: R_fp's active "
        'margin (16 pt, 0.35 s above 64) plus the deep mask puts any content a canvas-wide W would see and a '
        'clamped R_fp would not at >= 50 pt from every readable pixel, where a sigma_w of ~16.5 pt weighs it '
        'below 1e-3; the D steps 8 and 16 pt outside the edge were the answering rows and are '
        'refraction-confounded (19.2 pt outer reach). Non-identifiable on this bed; no cell within the canvas '
        'and outside the refraction reach separates it. Recorded, not a bed question with an answer.'),
    ('edge-swap', 'LT', 'rest'): (
        "R_fp's active edge mode (clamp vs normalised) is invisible for the same reason: the active margin keeps "
        "R_fp's edge >= 45 pt from the deep mask. Memo E's 0.23-code dark-active choice is below the bar. "
        'Non-identifiable on this bed; it does not matter to a render at these margins either.'),
    ('R1', 'LT', 'inactive'): (
        "R1 (T on C and W before the fill) and LT's order differ only through T's CURVATURE over the levels a "
        'cell spans: an affine T commutes with the fill composite. The stand-in T is nearly straight in light '
        'receded over 144-255 (slopes 0.50, 0.40, 0.37), so B\'s P5 144/240 and P3 96/160 cannot separate them '
        "there. Family A's greys 160-255 decide it: if native T is curved there, P5 and P3 separate R1; if it is "
        'straight, the order is non-identifiable by construction and needs no cell. Dark receded (a compressive '
        'T) separates them (s 2.5).'),
    ('LT', 'R1', 'inactive'): 'The mirror of R1 -> LT: see there.',
    ('R1', 'LT', 'rest'): (
        'As receded: light active T is nearly straight over the levels (the stand-in); family A decides. Under '
        'ruling 3 the whole-bed re-read has 15 active cells (rrect-ml and -lg: the P1 checkers, the impulses and '
        "the 48/208 steps) and reads 0.14; B's P5/P3 on rrect-lg would be the answering rows."),
    ('W-canvas', 'W-shape', 'inactive'): (
        'Not a separation failure: W-shape with a large margin contains the canvas support at every readable '
        'pixel; the reverse (W-shape -> W-canvas) is distinguished (6.8-6.9).'),
    ('LT', 'R1', 'rest'): 'The mirror of R1 -> LT (active): see there.',
    ('K2', 'LT', 'inactive'): (
        "K2's second fill width (sk 12 against 8k = 16.3 pt) moves region statistics by 1.2-1.4 codes on the "
        "p64 knee sides: the bed separates K2 at a larger width difference. What would separate it at this "
        "one: C's S 32 patch surround at 16-48 pt (U1's rows) read at their own bar, or a P2/P4 pitch-32 cell "
        'between the p16 and p64 rows.'),
    ('LT-2k', 'LT', 'inactive'): (
        'k_n against k_w when receded (1.75 against 2.10) moves statistics by 1.4 codes: the receded narrow width '
        "is 0.4 + 0.4t of the radius, so k_n's lever is small on t = 0 shapes. C's S 8 against S 32 on rrect-md "
        'carries it; a receded S 8 on rrect-lg (t = 1, opacity 0.8) doubles the lever.'),
    ('LT', 'W-shape', 'rest'): (
        'Not a separation failure: in the active pose W-shape with a margin mu of the order of R_fp\'s reproduces '
        "LT's box support at every readable pixel (the deep mask is far from both supports' edges), so W-shape "
        'contains LT there. The reverse, W-shape (mu 4) -> LT, is distinguished (1.96 light, 2.98 dark).'),
    ('LT', 'W-canvas', 'rest'): 'The mirror of W-canvas -> LT (active): see there.',
    ('LT', 'edge-swap', 'rest'): 'The mirror of edge-swap -> LT (active): see there.',
    ('W-shape', 'K2', 'inactive'): (
        "The rounded-shape support differs from R_fp's box only near the corners and the capsule's ends, and K2's "
        'second fill width (or W-tails\' tail) absorbs most of that to within 0.8-0.9 code. What separates them: '
        'receded structure within ~16 pt of an rrect corner or a capsule end (a step or a P1 patch placed there; '
        "fork B's step reader cannot call box against shape on D's centred steps either). A bed question."),
    ('W-shape', 'W-tails', 'inactive'): 'As W-shape -> K2 (receded): structure near a corner or a capsule end.',
    ('free-sn', 'LT', 'inactive'): (
        "The free receded span law's truth sits within 0.64 pt of LT's k 5 (0.4 + 0.4t) at every ordinate, so "
        'this pair measures that the bed does NOT separate a departure that small (max 0.64 pt, at s = 160; '
        'whole bed at pin 5d719b60: 1.17); the estimated resolution row gives the departure it would separate.'),
}


def load(p):
    try:
        return json.load(open(p))
    except FileNotFoundError:
        return None


def family_rows(p1):
    rows = []
    if not p1:
        return rows
    for r in p1.get('A', []):
        if 'skipped' in r:
            continue
        band = 'outside (d_in = 20 + 2 sigma_n,ref)' if r['ep'].endswith('rest') else 'receded (no band)'
        for pn, v in r['recovered'].items():
            rows.append(dict(reader=f"family fitter: {r['family']}", quantity=pn, endpoints=[r['ep']], band=band, gated=True,
                             synthetic=dict(resolution=f"{v['err']:+.4f} (read {v['read']:.4f}, truth {v['truth']:.4f})",
                                            tolerance=f"+-{v['tol']}", verdict='PASS' if v['ok'] else 'FAIL'),
                             vitrea=None,
                             notes=f"pooled rms {r['pooled']:.3f}, {r['n_cells']} cells" +
                                   (f"; excluded {r['excluded']}" if r.get('excluded') else '')))
    for r in p1.get('Aw', []):
        if 'skipped' in r:
            rows.append(dict(reader=f"family fitter: {r['family']} (ruling 3)", quantity='all', endpoints=[r['ep']],
                             band='outside (d_in 53.6 pt, W support)', gated=True,
                             synthetic=dict(resolution='no answering cell', tolerance='-', verdict='NON-IDENTIFIABLE'),
                             vitrea=None, notes=r['skipped']))
            continue
        for pn, v in r['recovered'].items():
            rows.append(dict(reader=f"family fitter: {r['family']} (ruling 3)", quantity=pn, endpoints=[r['ep']],
                             band='outside (d_in 53.6 pt, W support)', gated=True,
                             synthetic=dict(resolution=f"{v['err']:+.4f} (read {v['read']:.4f}, truth {v['truth']:.4f})",
                                            tolerance=f"+-{v['tol']}",
                                            verdict='PASS' if v['ok'] else ('NON-IDENTIFIABLE' if abs(v['err']) > 5 else 'FAIL')),
                             vitrea=None, notes=f"pooled rms {r['pooled']:.3f}, {r['n_cells']} cells (rrect-ml and -lg only)"))
    for r in p1.get('C', []):
        band = 'outside' if r['ep'].endswith('rest') else 'receded (no band)'
        rows.append(dict(reader='family fitter: LT (survival resolution)', quantity='k', endpoints=[r['ep']],
                         band=band, synthetic=dict(resolution=f"+{r['k_up']:.4f} / -{r['k_down']:.4f}",
                                                   tolerance='the move that shifts some region statistic by 1 code',
                                                   verdict='REPORTED'), vitrea=None, notes='lam refitted by LS'))
        rows.append(dict(reader='family fitter: LT (survival resolution)', quantity='lam', endpoints=[r['ep']],
                         band=band, synthetic=dict(resolution=f"+{r['lam_up']:.4f} / -{r['lam_down']:.4f}",
                                                   tolerance='the move that shifts some region statistic by 1 code',
                                                   verdict='REPORTED'), vitrea=None, notes='k held'))
    return rows


# Resolution of each nested rival's extra parameter, ESTIMATED from its separation pair: s grows about linearly
# with the departure from LT once it is well above the quantisation, so the departure that reaches the
# DISTINGUISHED line (1.5 codes) is about departure x 1.5 / s. An estimate, not a measurement: it assumes the
# linearity and one departure shape per rival.
DEPARTURES = {'LT-2k': ('|k_n - k_w|', 0.35), 'K2': ('|sk - 8 k| (pt)', None), 'free-sn': ('max ordinate departure (pt)', None),
              'W-tails': ('weight a of a 40-pt tail', 0.25), 'W-shape': ('box -> shape + 4 pt', None)}


def estimate_rows(table):
    import families as FA
    rows = []
    for r in table:
        if r['fit'] != 'LT' or r['truth'] not in DEPARTURES or r['s'] <= 0.5:
            continue
        what, dep = DEPARTURES[r['truth']]
        if r['truth'] == 'K2':
            dep = abs(12.0 - 8 * FA.TRUTH_K[r['ep']])
        if r['truth'] == 'free-sn':
            pose = r['ep'].split('-')[1]
            ords = FA.TRUTH_EXTRA['free-sn'][pose]
            import forward as F
            import geometry as G
            law = {sp: (FA.TRUTH_K[r['ep']] * 5 * (0.4 + 0.4 * G.size_t(sp)) if pose == 'inactive'
                        else FA.TRUTH_K[r['ep']] * 5 * 0.8 * G.size_t(sp)) for sp in ords}
            dep = max(abs(ords[sp] - law[sp]) for sp in ords)
        if dep is None:
            continue
        rows.append(dict(reader=f'family fitter: {r["truth"]} against LT (estimated resolution)', quantity=what,
                         endpoints=[r['ep']], band='outside' if r['ep'].endswith('rest') else 'receded (no band)',
                         synthetic=dict(resolution=f'~{dep * 1.5 / r["s"]:.3g} (from s {r["s"]:.2f} at {dep:.3g})',
                                        tolerance='the departure that reaches s = 1.5 codes', verdict='ESTIMATE'),
                         vitrea=None, notes='linear in the departure; see DEPARTURES in resolution.py'))
    return rows


def separation(p2):
    if not p2:
        return [], []
    best = {}
    for r in p2['pairs']:
        key = (r['truth'], r['fit'], r['ep'])
        if key not in best or r.get('whole'):
            best[key] = r
    table, open_pairs = [], []
    for (t, f, ep), r in sorted(best.items()):
        import proof_common as PC
        b = PC.bounds_for(f)
        bound = sorted({k for k, v in list(r['ls_x'].items()) + list(r['mm_x'].items())
                        if min(abs(v - b[k.split('@')[0]][0]), abs(v - b[k.split('@')[0]][1])) < 1e-3 *
                        max(1, abs(v))})
        table.append(dict(truth=t, fit=f, ep=ep, s=r['s'], s_ls=r['s_ls'], verdict=r['verdict'], where=r['where'],
                          whole=r.get('whole', False), n_cells=r['n_cells'], at_bound=bound,
                          bed=r.get('bed', '5ba68aeb')))
        if r['verdict'] != 'DISTINGUISHED':
            pose = ep.split('-')[1]
            note = SEPARATORS.get((t, f, pose)) or SEPARATORS.get((t, f, '*')) or 'NO NOTE: to be read'
            open_pairs.append(dict(truth=t, fit=f, ep=ep, s=r['s'], verdict=r['verdict'], where=r['where'],
                                   separator=note))
    return table, open_pairs


def main():
    rows = family_rows(load('proof1_families.json'))
    for f in ('resolution_rows_a.json', 'resolution_rows_b.json'):
        rows += load(f) or []
    table, open_pairs = separation(load('proof2_separation.json'))
    nulls = load('proof2_nulls.json') or []
    rows += estimate_rows(table)
    p1 = load('proof1_families.json') or {}
    json.dump(dict(rows=rows, separation=table, unresolved=open_pairs, nulls=nulls, nesting=p1.get('B'),
                   nesting_regions=p1.get('E'), engine=p1.get('D')),
              open('resolution.json', 'w'), indent=1, default=float)
    L = ['W42 G0 instrument: resolution of every reader (clause 2), the separation table and the open pairs', '']
    L.append('READERS (synthetic = proof 1 through the memo C T stand-in; vitrea = proof 3 on the canonical web tree)')
    for r in rows:
        e = r.get('endpoints', 'all four')
        eps = e if isinstance(e, str) else ','.join(e)
        s, v = r.get('synthetic'), r.get('vitrea')
        g = r.get('gated')
        L.append(f"- {r['reader']} | {r['quantity']} | {eps} | band: {r['band']}"
                 + ('' if g is None else f" | {'GATED' if g else 'descriptive'}"))
        if s:
            L.append(f"    synthetic {s['resolution']} (tol {s['tolerance']}) {s['verdict']}")
        if v:
            L.append(f"    vitrea    {v['resolution']} (tol {v['tolerance']}) {v['verdict']}")
        vs = r.get('vitrea_superseded')
        for x in ([vs] if isinstance(vs, dict) else (vs or [])):
            q = f"{x['quantity']}: " if x.get('quantity') else ''
            L.append(f"    vitrea, superseded sigma_RMS bar: {q}{x.get('resolution')} (tol {x.get('tolerance')}) {x.get('verdict')}")
        if r.get('notes'):
            L.append(f"    notes: {r['notes'][:600]}")
    if p1.get('B'):
        L += ['', 'k NESTING (four endpoints together): truth, level, params, pooled (per endpoint), k read']
        for r in p1['B']:
            pe = ' '.join(f"{e}:{v:.3f}" for e, v in r['pooled_by_ep'].items())
            ks = ', '.join(f'{k} {v:.4f}' for k, v in r['x'].items())
            L.append(f"  {r['truth']:7s} {r['level']:12s} {r['n_params']:2d} pooled {r['pooled']:.3f} [{pe}] {ks}")
    L += ['', 'SEPARATION (s = the fitted family\'s best max region-statistic miss against the truth, codes)']
    for r in table:
        L.append(f"  {r['truth']:>12s} -> {r['fit']:<13s} {r['ep']:15s} s {r['s']:6.2f}  {r['verdict']:13s}"
                 f"{' (whole bed)' if r['whole'] else ''}  {r['where']}"
                 + (f"  [fit at its bound: {', '.join(r['at_bound'])}; s is an upper bound]" if r['at_bound'] else ''))
    if nulls:
        L += ['', "REJECTED NULLS fitted to an LT truth (memo E's bars: mixture >= 2.60, units and R2 >= 4.65)"]
        for r in sorted(nulls, key=lambda r: (r['fit'], r['ep'])):
            import proof_common as PC
            b = PC.bounds_for(r['fit'])
            at_bound = any(min(abs(v - b[k.split('@')[0]][0]), abs(v - b[k.split('@')[0]][1])) < 1e-3
                           for k, v in r['x'].items())
            verdict = 'VOID: the fit sat on the k bound (4.0); widened for the resume' if at_bound else r['verdict']
            L.append(f"  {r['fit']:14s} {r['ep']:15s} pooled {r['pooled']:6.2f} max cell {r['max_cell']:6.2f}  {verdict}")
    L += ['', 'PAIRS NOT DISTINGUISHED, AND WHAT WOULD SEPARATE THEM']
    for r in open_pairs:
        L.append(f"- {r['truth']} -> {r['fit']} ({r['ep']}): s {r['s']:.2f} {r['verdict']}")
        L.append(f"    {r['separator']}")
    open('resolution.txt', 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
