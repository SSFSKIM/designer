"""W42 G0 instrument: the resolution rows of the five statistic readers of proofs 1 and 3 (read_model,
read_mirror, read_heavy, read_esf, read_impulse), assembled mechanically from proof1_readers_a.<ep>.all.json
and proof3_readers_a.<ep>.json into resolution_rows_a.json and resolution_rows_a.txt.

A resolution is the worst absolute error over the cells where the reader IDENTIFIES the quantity (its own
interval criterion); cells where it does not are counted as non-identifiable and named, never averaged in.
Band: 'outside' / 'across' / 'inside' the active refraction band (20 pt plus the reader's support, declared
as twice the widest sigma the statistic depends on), 'receded (no band)' for the receded pose.
"""
import glob
import json

import numpy as np

TOL = json.load(open('tolerances.json'))
EPS = ('light-rest', 'light-inactive', 'dark-rest', 'dark-inactive')


def section_of(r):
    if r.get('mirror_only'):
        return 'proof3-mirror'
    if 'section' in r:
        return r['section']
    if 'band' in r and 'd_in' in r:
        return 'band'
    return {'linear-control': 'linear', 'esf-linear-control': 'esf', 'impulse-linear-control': 'impulse',
            'exclusion': 'exclusion'}.get(r.get('reader'), r.get('reader', 'proof3'))


def load(prefix):
    """Every run file of a proof; a section re-run in a later file ('<ep>.<sections>.json') replaces that
    section of the endpoint's 'all' run (a re-run after a fix; the replaced rows are not read)."""
    files = sorted(f for f in glob.glob(f'{prefix}.*.json') if not f.endswith('.replica.json'))
    by = {}
    for f in files:
        parts = f[len(prefix) + 1:-5].split('.')
        which = parts[1] if len(parts) > 1 else 'all'
        for r in json.load(open(f)):
            key = (r.get('ep'), section_of(r))
            by.setdefault(key, {}).setdefault(which, []).append(r)
    rows = []
    for key, runs in by.items():
        specific = [w for w in runs if w != 'all']
        rows += runs[specific[-1]] if specific else runs['all']
    return rows


def fmt(v, unit, pct=False):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return 'n/a'
    return f'{100 * v:.1f} %' if pct else f'+-{v:.3f}{unit}'


def group(rows, active):
    return [r for r in rows if r.get('ep', '').endswith('rest') == active]


def verdict(ok, n_ident):
    if n_ident == 0:
        return 'NON-IDENTIFIABLE'
    return 'PASS' if ok else 'FAIL'


def synthetic_rows(P1):
    out = []
    tol = TOL['proof1_statistic_readers']
    # ---- model reader on flat cells
    M = [r for r in P1 if r['reader'] == 'model' and r.get('flat') and r.get('err')]
    for active, band in ((False, 'receded (no band)'), (True, 'across')):
        G = group(M, active)
        for q, key, unit in (('sn', 'sigma_n_pt', ' pt'), ('sw', 'sigma_w_pt', ' pt'), ('lam', 'lam', ''), ('w', 'w', '')):
            # lam and w are gated where the wide width is identified too: where W is flat across the pitch
            # (sigma_w >> pitch) the knee's reference is the mean and lam and w trade with it
            idn = [r for r in G if (r['identified'].get(q, True) if q in ('sn', 'sw') else r['identified'].get('sw', True))]
            nid = [r['ep'] + ' ' + r['cell'] for r in G if r not in idn]
            if not G:
                continue
            res = max(abs(r['err'][q]) for r in idn) if idn else None
            ok = res is not None and res <= tol['model reader (memo C)'][key]
            misses = [f"{r['ep']} {r['cell']} {r['err'][q]:+.3f}" for r in idn if abs(r['err'][q]) > tol['model reader (memo C)'][key]]
            out.append(dict(reader='model reader (memo C)', quantity=q, endpoints='active' if active else 'receded',
                            band=band, synthetic=dict(resolution=fmt(res, unit), tolerance=f"+-{tol['model reader (memo C)'][key]}{unit}",
                                                      verdict=verdict(ok, len(idn))),
                            vitrea=None, notes=f"{len(idn)} identified cells" + (f"; non-identifiable on {len(nid)}: {', '.join(nid)}" if nid else '')
                            + (f"; misses: {'; '.join(misses)}" if misses else '')
                            + ('; active flat cells are t = 0 (capsule, rrect-64): o = 0, sn = the floor; W support 2 sigma_w reaches the band' if active else '')))
    Ma = [r for r in P1 if r['reader'] == 'model' and not r.get('flat') and r.get('read')]
    if Ma:
        out.append(dict(reader='model reader (memo C)', quantity='sn on depth-graded active cells (effective)',
                        endpoints='active', band='across', synthetic=dict(resolution='n/a (an effective width)', tolerance='not gated', verdict='N/A'),
                        vitrea=None, notes='; '.join(f"{r['ep']} {r['cell']} sn {r['read']['sn']:.2f} lam {r['read']['lam']:.2f}" for r in Ma)))
    # ---- mirror: three readings per cell (single width; LT narrow with k_w free; LT narrow with k_w fixed
    # from the heavy reader and its uncertainty propagated)
    S = [r for r in P1 if r['reader'] == 'mirror' and r.get('reads')]
    labels = {'gauss': 'single-width narrow', 'lt': 'LT depth-graded narrow, k_w free',
              'lt|kw': 'LT depth-graded narrow, k_w fixed from the heavy reader (+-3.2 % propagated)'}
    for tag in ('gauss', 'lt', 'lt|kw'):
        for active, band in ((False, 'receded (no band)'), (True, 'across')):
            G = [(r, r['reads'].get(tag)) for r in group(S, active)]
            G = [(r, x) for r, x in G if x is not None]
            if not G:
                continue
            idn = [(r, x) for r, x in G if x['identified']]
            nid = [f"{r['ep']} {r['cell']} ({','.join(k for k, v in x['checks'].items() if not v)})" for r, x in G if not x['identified']]
            none = [f"{r['ep']} {r['cell']}" for r in group(S, active) if r['reads'].get(tag) is None]
            res = max(abs(x['err']) for r, x in idn) if idn else None
            misses = [f"{r['ep']} {r['cell']} {x['err']:+.4f}" for r, x in idn if abs(x['err']) > 0.03]
            silent = [f"{r['ep']} {r['cell']} read {x['s1_gain']:+.3f}" for r, x in G if not x['identified'] and abs(x['err']) > 0.1]
            out.append(dict(reader='mirror statistic S', quantity=f's1/gain = lam (1 - w); {labels[tag]}',
                            endpoints='active' if active else 'receded', band=band,
                            synthetic=dict(resolution=fmt(res, ''), tolerance='+-0.03',
                                           verdict=verdict(res is not None and res <= 0.03, len(idn))),
                            vitrea=None,
                            notes=f"{len(idn)} identified (every identified reading within +-0.03: {not misses})"
                                  + (f"; misses among identified: {'; '.join(misses)}" if misses else '')
                                  + f"; refused on {len(nid)}: {', '.join(nid)}"
                                  + (f"; no model-trusted partner pairs (dark stand-in T clamp / size): {', '.join(none)}" if none else '')
                                  + f"; refused readings off by > 0.1 (the flag caught them): {len(silent)}"))
    L = [r for r in P1 if r['reader'] == 'linear-control']
    s_lin = [abs(r['mirror_lin']['s1_gain']) for r in L if r.get('mirror_lin') and r['pitch'] >= 8 and r['mirror_lin']['identified']]
    s_lin_all = [abs(r['mirror_lin']['s1_gain']) for r in L if r.get('mirror_lin') and r['pitch'] >= 8]
    out.append(dict(reader='mirror statistic S', quantity='two-sided linear control |s1/gain| (p >= 8)', endpoints='all',
                    band='n/a (synthetic control)', synthetic=dict(resolution=fmt(max(s_lin_all) if s_lin_all else None, ''), tolerance='<= 0.024',
                                                                    verdict='PASS' if s_lin_all and max(s_lin_all) <= 0.024 else 'FAIL'),
                    vitrea=None, notes=f'{len(s_lin_all)} control reads, linear space; max over identified {max(s_lin) if s_lin else float("nan"):.4f}'))
    s_enc = [r['mirror_enc']['s1_gain'] for r in L if r.get('mirror_enc') and r['pitch'] >= 8]
    lam_enc = [r['model_enc']['lam'] for r in L]
    lam_lin = [r['model_lin']['lam'] for r in L]
    out.append(dict(reader='known-space control', quantity='lam and s1/gain manufactured by the ENCODED reading of a linear two-sided body',
                    endpoints='all', band='n/a (synthetic control)',
                    synthetic=dict(resolution=f"lam {min(lam_enc):+.2f}..{max(lam_enc):+.2f} (linear reading {min(lam_lin):+.3f}..{max(lam_lin):+.3f}); "
                                              f"S {min(s_enc):+.3f}..{max(s_enc):+.3f}", tolerance='reported, not gated', verdict='N/A'),
                    vitrea=None, notes='lam alone manufactures a knee in the wrong space (to the 1.6 bound); S in the wrong space reads up to '
                                       f'{max(np.abs(s_enc)):.2f}, so S establishes the knee only with the space right (every linear fit\'s loss)'))
    # ---- heavy
    H = [r for r in P1 if r['reader'] == 'heavy' and r.get('read') and np.isfinite(r['read'][r['best']]['rms'])]
    H_none = [f"{r['ep']} {r['cell']}" for r in P1 if r['reader'] == 'heavy' and r.get('read') is not None
              and r not in H and r.get('truth_support') == 'Rfp']
    for active, band in ((False, 'receded (no band)'), (True, 'across')):
        G = group(H, active)
        if not G:
            continue
        errs = [abs(r['sw_err_rel']) for r in G if r['sw_err_rel'] is not None]
        rank_bad = [f"{r['ep']} {r['cell']} truth {r['truth_support']} best {r['best']} gap {r['rank_gap']:.3f}" for r in G if r['rank_gap'] > 0.05]
        grp = all(r['group_rejected'] for r in G)
        out.append(dict(reader='pitch-64 heavy reader', quantity='sigma_w (true support family)', endpoints='active' if active else 'receded',
                        band=band, synthetic=dict(resolution=fmt(max(errs), '', pct=True), tolerance='5 %', verdict='PASS' if max(errs) <= 0.05 else 'FAIL'),
                        vitrea=None, notes=f"{len(G)} reads (truths Rfp, canvas, shape mu 0); "
                        + '; '.join(f"{r['ep']} {r['cell']} truth {r['truth_support']} {100 * r['sw_err_rel']:+.1f} %" for r in G
                                    if r['sw_err_rel'] is not None and abs(r['sw_err_rel']) > 0.05)
                        + (f"; no model-trusted cores (dark T clamp at spans >= 96): {', '.join(sorted(set(H_none)))}" if H_none else '')))
        out.append(dict(reader='pitch-64 heavy reader', quantity='support call and group rejection', endpoints='active' if active else 'receded',
                        band=band, synthetic=dict(resolution=f"{len(rank_bad)} mis-ranks beyond 0.05 code; group rejected everywhere: {grp}",
                                                  tolerance='true support first where supports differ by > 0.05 code; group rejected',
                                                  verdict='PASS' if not rank_bad and grp else 'FAIL'),
                        vitrea=None, notes='; '.join(rank_bad) or 'Rfp = canvas in the active pose (large margin, clamp): not separable, and not required'))
    # ---- ESF
    E = [r for r in P1 if r['reader'] == 'esf' and r.get('read')]
    for active, band in ((False, 'receded (no band)'), (True, 'outside')):
        G = group(E, active)
        idn = [r for r in G if r['read']['identified']]
        nid = [f"{r['ep']} {r['cell']} ({100 * r['err_rel']:+.0f} %)" for r in G if not r['read']['identified']]
        res = max(abs(r['err_rel']) for r in idn) if idn else None
        misses = [f"{r['ep']} {r['cell']} {100 * r['err_rel']:+.1f} %" for r in idn if abs(r['err_rel']) > 0.03]
        out.append(dict(reader='ESF reader (memo B)', quantity='effective narrow sigma', endpoints='active' if active else 'receded',
                        band=band, synthetic=dict(resolution=fmt(res, '', pct=True), tolerance='3 %', verdict=verdict(res is not None and res <= 0.03, len(idn))),
                        vitrea=None, notes=f"{len(idn)} identified; non-identifiable (bound only) on {len(nid)}: {', '.join(nid)}"
                        + (f"; misses: {'; '.join(misses)}" if misses else '')))
    # ---- impulse
    I = [r for r in P1 if r['reader'] == 'impulse' and r.get('single') and r.get('polarity') == 'narrow']
    for active, band in ((False, 'receded (no band)'), (True, 'outside')):
        G = group(I, active)
        if not G:
            continue
        res = max(abs(r['err_rel']) for r in G)
        misses = [f"{r['ep']} {r['cell']} {100 * r['err_rel']:+.1f} %" for r in G if abs(r['err_rel']) > 0.03]
        out.append(dict(reader='impulse reader (memo B)', quantity='single sigma (linear-side polarity)', endpoints='active' if active else 'receded',
                        band=band, synthetic=dict(resolution=fmt(res, '', pct=True), tolerance='3 %', verdict='PASS' if res <= 0.03 else 'FAIL'),
                        vitrea=None, notes=f"{len(G)} cells" + (f"; misses: {'; '.join(misses)}" if misses else '')))
    Ic = [r for r in P1 if r['reader'] == 'impulse-linear-control']
    if Ic:
        es = max(abs(r['err_s1']) for r in Ic)
        ek = max(abs(r['err_k']) for r in Ic)
        out.append(dict(reader='impulse reader (memo B)', quantity='two-Gaussian s1 and share k (linear control, share defined)',
                        endpoints='all', band='n/a (synthetic control)',
                        synthetic=dict(resolution=f's1 {100 * es:.1f} %, k +-{ek:.3f}', tolerance='sigma 3 %, share +-0.03',
                                       verdict='PASS' if es <= 0.03 and ek <= 0.03 else 'FAIL'), vitrea=None, notes=f'{len(Ic)} control cells'))
    # ---- band pass
    B = [r for r in P1 if r.get('band') in ('outside', 'excluded') and r['reader'] in ('W-readers', 'esf', 'impulse') and 'd_in' in r]
    if B:
        notes = []
        for r in B:
            if r['band'] == 'excluded':
                notes.append(f"{r['ep']} {r['cell']} EXCLUDED ({r['reason']})")
            elif r['reader'] == 'W-readers':
                m, t = r['model'], r['truth']
                notes.append(f"{r['ep']} {r['cell']} d_in {r['d_in']:.1f}: model sw {m['sw']:.2f}/{t['sw']:.2f} lam {m['lam']:.3f} w {m['w']:.3f}"
                             + (f"; S {r['mirror']['s1_gain']:+.3f}/{t['s1_gain']:.3f}" if r.get('mirror') else '') if m else f"{r['ep']} {r['cell']}: model none")
            else:
                notes.append(f"{r['ep']} {r['cell']} d_in {r['d_in']:.1f}: {r['reader']} {100 * r['err_rel']:+.1f} %")
        out.append(dict(reader='all five (active refraction band)', quantity='readings moved beyond 20 pt + support',
                        endpoints='active', band='outside', synthetic=dict(resolution='see notes', tolerance='as each reader', verdict='see notes'),
                        vitrea=None, notes='; '.join(notes)))
    return out


def share(r):
    """The deep share k the code draws on the cell: the replica's mean over the read pixels where it was
    rendered (1x), else the code-map's centre value."""
    return r['k_mean_replica'] if r.get('k_mean_replica') is not None else r['truth']['k_centre']


NARROW_MIN = 0.25    # a narrow width is a reading only where the narrow share 1 - k is at least this
DEEP_MIN = 0.25      # a deep width only where k is at least this (and, on checkers, the pitch >= 32)


def vitrea_rows(P3):
    """Proof 3's rows. Each width is gated only on the cells where the code's own share makes it visible;
    the rest are counted as non-identifiable on that cell, with the share named."""
    out = []
    cap = [r for r in P3 if r['src'] == 'capture']
    rep = [r for r in P3 if r['src'] == 'replica']
    ck = [r for r in cap if 'model_lin' in r]
    lab = lambda r: f"{r['ep']} {r['scale']}x {r['cell'].split('__')[0]}/{r['cell'].split('__')[1]}"
    if ck:
        lam = max(abs(r['model_lin']['lam']) for r in ck)
        bad = [f"{lab(r)} {r['model_lin']['lam']:+.3f}" for r in ck if abs(r['model_lin']['lam']) > 0.12]
        out.append(dict(reader='model reader (memo C)', quantity='lam (linear reading; truth 0)', endpoints='all',
                        band='n/a (vitrea: lens core)', synthetic=None,
                        vitrea=dict(resolution=fmt(lam, ''), tolerance='|lam| <= 0.12', verdict='PASS' if not bad else 'FAIL'),
                        notes=f'{len(ck)} checker cells, pitches 4-64, both scales, all four endpoints'
                              + (f'; over the bar: {"; ".join(bad)}' if bad else '')))
        g = [r for r in ck if 1 - share(r) >= NARROW_MIN and r['pitch'] >= 8]
        ng = [f"{lab(r)} (k {share(r):.2f})" for r in ck if r not in g]
        if g:
            e = [abs(r['model_lin']['sn'] / r['truth']['sn'] - 1) for r in g]
            bad = [f"{lab(r)} {r['model_lin']['sn']:.2f}/{r['truth']['sn']:.2f}" for r, x in zip(g, e) if x > 0.20]
            out.append(dict(reader='model reader (memo C)', quantity='sn vs the body kernel sigma_RMS (1.58 dev)', endpoints='all',
                            band='n/a (vitrea: lens core)', synthetic=None,
                            vitrea=dict(resolution=fmt(max(e), '', pct=True), tolerance='20 %', verdict='PASS' if not bad else 'FAIL'),
                            notes=f'{len(g)} cells with narrow share >= {NARROW_MIN} and pitch >= 8' + (f'; over the bar: {"; ".join(bad)}' if bad else '')
                                  + f'; not identifiable (share or pitch 4): {len(ng)}'))
        g = [r for r in ck if share(r) >= DEEP_MIN and r['pitch'] >= 32]
        if g:
            e = [abs(r['model_lin']['sw'] / r['truth']['sw'] - 1) for r in g]
            bad = [f"{lab(r)} {r['model_lin']['sw']:.1f}/{r['truth']['sw']:.1f}" for r, x in zip(g, e) if x > 0.25]
            out.append(dict(reader='model reader (memo C)', quantity='sw vs the deep kernel sigma_RMS (pitch >= 32)', endpoints='all',
                            band='n/a (vitrea: lens core)', synthetic=None,
                            vitrea=dict(resolution=fmt(max(e), '', pct=True), tolerance='25 %', verdict='PASS' if not bad else 'FAIL'),
                            notes=f'{len(g)} cells with deep share >= {DEEP_MIN}' + (f'; over the bar: {"; ".join(bad)}' if bad else '')))
        lam_e = [r['model_enc_known_space']['lam'] for r in ck]
        out.append(dict(reader='known-space control', quantity='lam from the ENCODED reading of vitrea (a linear two-sided body)', endpoints='all',
                        band='n/a (vitrea: lens core)', synthetic=None,
                        vitrea=dict(resolution=f'lam {min(lam_e):+.2f}..{max(lam_e):+.2f}', tolerance='reported (memo C read 1.4-1.5)', verdict='N/A'),
                        notes='the linear reading of the same cells reads |lam| <= ' + f'{lam:.3f}' + '; the knee is established by S and every linear fit\'s loss, never by lam alone'))
        sv = [r for r in ck if r.get('mirror') and r['pitch'] >= 8]
        if sv:
            smax = max(abs(r['mirror']['s1_gain']) for r in sv)
            bad = [f"{lab(r)} {r['mirror']['s1_gain']:+.4f}" + ('' if 'checks' not in r['mirror'] else
                   f" (flag: {'identified' if r['mirror']['identified'] else 'refused: ' + ','.join(k for k, v in r['mirror']['checks'].items() if not v)})")
                   for r in sv if abs(r['mirror']['s1_gain']) > 0.024]
            idn = [r for r in sv if r['mirror'].get('identified')]
            smax_i = max(abs(r['mirror']['s1_gain']) for r in idn) if idn else None
            out.append(dict(reader='mirror statistic S', quantity='|s1/gain| on vitrea (two-sided; truth 0), pitch >= 8, single-width path',
                            endpoints='all', band='n/a (vitrea: lens core)', synthetic=None,
                            vitrea=dict(resolution=f'all cells {fmt(smax, "")}; identified cells {fmt(smax_i, "")}',
                                        tolerance='<= 0.024',
                                        verdict=('PASS' if not bad else ('FAIL on all cells; PASS on identified cells'
                                                                         if smax_i is not None and smax_i <= 0.024 else 'FAIL'))),
                            notes=f'{len(sv)} cells, {len(idn)} identified by the flag' + (f'; over the bar: {"; ".join(bad)}' if bad else '')
                                  + '; the flag refuses many vitrea cells by w_inside because vitrea\'s deep share is ~1 there (the '
                                    'check is a collapse detector for Apple\'s w = 0.5, conservative on vitrea)'))
        hv = [r for r in ck if r.get('heavy') and 'canvas' in r['heavy']]
        if hv:
            grp = [lab(r) for r in hv if not ('group' not in r['heavy'] or r['heavy']['group']['rms'] > r['heavy'][r['heavy']['best']]['rms'] + 0.3)]
            false_fp = [lab(r) for r in hv if min(r['heavy'][f]['rms'] for f in ('shape', 'box') if f in r['heavy']) < r['heavy']['canvas']['rms'] - 0.04]
            g = [r for r in hv if share(r) >= DEEP_MIN]
            e = [abs(r['heavy']['canvas']['sw'] / r['truth']['sw'] - 1) for r in g]
            bad = [f"{lab(r)} {r['heavy']['canvas']['sw']:.1f}/{r['truth']['sw']:.1f}" for r, x in zip(g, e) if x > 0.25]
            out.append(dict(reader='pitch-64 heavy reader', quantity='group rejected; no false footprint call; canvas sigma_w', endpoints='all',
                            band='n/a (vitrea: lens core)', synthetic=None,
                            vitrea=dict(resolution=f'group not rejected on {len(grp)}; false footprint calls {len(false_fp)}; sigma_w {fmt(max(e) if e else None, "", pct=True)}',
                                        tolerance='group rejected; within 0.04 code; sigma_w 25 %',
                                        verdict='PASS' if not grp and not false_fp and not bad else 'FAIL'),
                            notes='; '.join([f'group not rejected: {", ".join(grp)}'] * bool(grp) + [f'false footprint: {", ".join(false_fp)}'] * bool(false_fp)
                                            + [f'sigma_w over the bar: {"; ".join(bad)}'] * bool(bad))))
        es = []
        for r in ck:
            if r['pitch'] > 16 or 1 - share(r) < NARROW_MIN:
                continue
            for side in ('esf_bright', 'esf_dark'):
                x = r.get(side)
                if x and x['identified']:
                    es.append((r, x, side))
        if es:
            e = [abs(x['sigma'] / r['truth']['sn'] - 1) for r, x, _ in es]
            bad = [f"{lab(r)} {side[4:]} {x['sigma']:.2f}/{r['truth']['sn']:.2f}" for (r, x, side), v in zip(es, e) if v > 0.10]
            out.append(dict(reader='ESF reader (memo B)', quantity='narrow sigma vs 1.58 dev (pitch <= 16, narrow share >= 0.25)', endpoints='all',
                            band='n/a (vitrea: lens core)', synthetic=None,
                            vitrea=dict(resolution=fmt(max(e), '', pct=True), tolerance='10 %', verdict='PASS' if not bad else 'FAIL'),
                            notes=f'{len(es)} identified half-profiles (vitrea is two-sided: both sides read)' + (f'; over the bar: {"; ".join(bad)}' if bad else '')))
    im = [r for r in cap if 'impulse_single' in r]
    if im:
        g = [r for r in im if 1 - share(r) >= NARROW_MIN]
        ng = [f"{lab(r)} (k {share(r):.2f})" for r in im if r not in g]
        if g:
            e0 = [abs(r['impulse_single']['sigma'] / r['truth']['sn'] - 1) for r in g]
            e1 = [abs(r['impulse_mix']['s1'] / r['truth']['sn'] - 1) for r in g]
            bad = [f"{lab(r)} single {r['impulse_single']['sigma']:.2f} s1 {r['impulse_mix']['s1']:.2f} / {r['truth']['sn']:.2f}"
                   for r, a, b in zip(g, e0, e1) if min(a, b) > 0.10]
            out.append(dict(reader='impulse reader (memo B)', quantity='narrow sigma (the better of single and two-Gaussian s1)', endpoints='all',
                            band='n/a (vitrea: lens core)', synthetic=None,
                            vitrea=dict(resolution=f'single {fmt(max(e0), "", pct=True)}, s1 {fmt(max(e1), "", pct=True)}; best-of per cell {fmt(max(min(a, b) for a, b in zip(e0, e1)), "", pct=True)}',
                                        tolerance='10 %', verdict='PASS' if not bad else 'FAIL'),
                            notes=f'{len(g)} cells with narrow share >= {NARROW_MIN}' + (f'; over the bar: {"; ".join(bad)}' if bad else '')
                                  + (f'; not identifiable (deep share): {", ".join(ng)}' if ng else '')))
            gk = [r for r in g if r.get('k_mean_replica') is not None]
            if gk:
                ek = [abs(r['impulse_mix']['k'] - r['k_mean_replica']) for r in gk]
                out.append(dict(reader='impulse reader (memo B)', quantity='deep share k (two-Gaussian) vs the replica', endpoints='all',
                                band='n/a (vitrea: lens core)', synthetic=None,
                                vitrea=dict(resolution=fmt(max(ek), ''), tolerance='+-0.1 (memo B, 2x)', verdict='PASS' if max(ek) <= 0.1 else 'FAIL'),
                                notes='; '.join(f"{lab(r)} k {r['impulse_mix']['k']:.2f}/{r['k_mean_replica']:.2f} s2 {r['impulse_mix']['s2']:.1f}/{r['truth']['sw']:.1f}" for r in gk)))
    if rep:
        notes = []
        for r in rep:
            c = next((x for x in cap if x['ep'] == r['ep'] and x['cell'] == r['cell'] and x['scale'] == r['scale']), None)
            if c is None:
                continue
            if 'model_lin' in r:
                notes.append(f"{lab(r)}: sn cap/rep/truth {c['model_lin']['sn']:.2f}/{r['model_lin']['sn']:.2f}/{r['truth']['sn']:.2f}; "
                             f"ESF {c['esf_bright'] and round(c['esf_bright']['sigma'], 2)}/{r['esf_bright'] and round(r['esf_bright']['sigma'], 2)}; "
                             f"w {c['model_lin']['w']:.2f}/{r['model_lin']['w']:.2f} k {share(r):.2f}")
            elif 'impulse_single' in r:
                notes.append(f"{lab(r)}: impulse single cap/rep/truth {c['impulse_single']['sigma']:.2f}/{r['impulse_single']['sigma']:.2f}/{r['truth']['sn']:.2f}")
        out.append(dict(reader='model mismatch against real pixels (memo B float64 replica, 1x)', quantity='the same readers on the code-exact render',
                        endpoints='all', band='n/a', synthetic=None, vitrea=dict(resolution='see notes', tolerance='reported', verdict='N/A'),
                        notes='; '.join(notes)))
    return out


# ---------------------------------------------------------------- ruling 1: proof 3 against the replica

BARS = TOL['proof3_vitrea']


def _nar_ok(r):
    return 1 - r['k_mean'] >= 0.25


def _deep_ok(r):
    return r['k_mean'] >= 0.25 and (r.get('pitch') or 0) >= 32


def _score(pairs, bar):
    """pairs: [(label, id_cap, id_rep, diff)]. Returns (resolution over scored, n scored, misses, one-only,
    both-refused) with diff None where a reading is missing."""
    scored = [(l, d) for l, a, b, d in pairs if a and b and d is not None]
    one = [l for l, a, b, d in pairs if a != b]
    none = [l for l, a, b, d in pairs if not a and not b]
    over = [f'{l} {d:.4f}' for l, d in scored if d > bar]
    res = max((d for _, d in scored), default=None)
    return res, len(scored), over, one, none


def _row(reader, quantity, gated, res, unit, bar_txt, bar, n, over, one, none, extra=''):
    ok = n > 0 and not over and not one
    verdict = 'NON-IDENTIFIABLE' if n == 0 and not one else ('PASS' if ok else 'FAIL')
    notes = (f'{n} cells scored' + (f'; over the bar: {"; ".join(over)}' if over else '')
             + (f'; identifiable on one image only (a miss): {"; ".join(one)}' if one else '')
             + (f'; not identifiable on either image (reported, not scored): {len(none)}' if none else '') + extra)
    return dict(reader=reader, quantity=quantity, endpoints='all', band='n/a (vitrea: lens core x replica core)',
                synthetic=None, gated=gated,
                vitrea=dict(resolution=('n/a' if res is None else (f'{100 * res:.1f} %' if unit == '%' else f'+-{res:.3f}{unit}')),
                            tolerance=bar_txt, verdict=verdict,
                            measure='|reading(capture) - reading(replica)|, same cell, same call (ruling 1)'),
                notes=notes)


def replica_rows(R):
    """R: rows of proof3_readers_a.<ep>.replica.json. Each reader is scored on the capture-replica difference
    at its proof-1 bar; only S is gated (ruling 2)."""
    out = []
    lab = lambda r: f"{r['ep']} {r['scale']}x {r['cell'].split('__')[0]}/{r['cell'].split('__')[1]}"
    ck = [r for r in R if r['kind'] == 'checkerboard']
    im = [r for r in R if r['kind'] == 'impulse']
    # model reader (descriptive)
    for q, unit, bar, need in (('sn', ' pt', 0.05, _nar_ok), ('sw', ' pt', 0.05, _deep_ok), ('lam', '', 0.03, _deep_ok),
                               ('w', '', 0.03, _deep_ok)):
        pairs = []
        for r in ck:
            a, b = r['cap'].get('model'), r['rep'].get('model')
            ident = bool(need(r) and (q == 'sn' and r['pitch'] >= 8 or q != 'sn'))
            d = None if (a is None or b is None) else abs(a[q] - b[q])
            pairs.append((lab(r), ident and a is not None, ident and b is not None, d))
        res, n, over, one, none = _score(pairs, bar)
        out.append(_row('model reader (memo C)', f'{q} (capture vs replica)', False, res, unit, f'{bar}{unit}', bar, n,
                        over, one, none, '; identifiable by the code\'s own share on the cell (narrow share >= 0.25 for sn; '
                        'deep share >= 0.25 and pitch >= 32 for sw, lam, w), the same on both images'))
    # S (gated): flag per image
    pairs = []
    flags_differ = []
    for r in ck:
        a, b = r['cap'].get('mirror'), r['rep'].get('mirror')
        if r['pitch'] < 8 or a is None or b is None:
            continue
        d = abs(a['s1_gain'] - b['s1_gain'])
        pairs.append((lab(r), a['identified'], b['identified'], d))
        if a['identified'] != b['identified']:
            flags_differ.append(f"{lab(r)} capture {'identified' if a['identified'] else 'refused (' + ','.join(k for k, v in a['checks'].items() if not v) + ')'}"
                                f" / replica {'identified' if b['identified'] else 'refused (' + ','.join(k for k, v in b['checks'].items() if not v) + ')'}")
    res, n, over, one, none = _score(pairs, 0.024)
    out.append(_row('mirror statistic S', '|S(capture) - S(replica)| and the same flag call (single-width path)', True,
                    res, '', '0.024 and the same identifiability call', 0.024, n, over, flags_differ, none))
    # heavy (descriptive)
    pairs, calls = [], []
    for r in ck:
        a, b = r['cap'].get('heavy'), r['rep'].get('heavy')
        if not a or not b:
            continue
        fa, fb = a['best'], b['best']
        d = abs(a[fa]['sw'] / b[fb]['sw'] - 1)
        pairs.append((lab(r), True, True, d))
        same = fa == fb or abs(a[fb]['rms'] - a[fa]['rms']) <= 0.01 or abs(b[fa]['rms'] - b[fb]['rms']) <= 0.01
        grp = lambda x, f: x['group']['rms'] > x[f]['rms'] + 0.3 if 'group' in x else True
        if not same or grp(a, fa) != grp(b, fb):
            calls.append(f"{lab(r)} capture {fa} (group rejected {grp(a, fa)}) / replica {fb} (group rejected {grp(b, fb)})")
    res, n, over, one, none = _score(pairs, 0.05)
    out.append(_row('pitch-64 heavy reader', 'best-family sigma_w, support and group calls (capture vs replica)', False,
                    res, '%', '5 %; identical calls', 0.05, n, over + [f'call differs: {c}' for c in calls], [], none))
    # ESF (descriptive)
    pairs = []
    for r in ck:
        for side in ('esf_bright', 'esf_dark'):
            a, b = r['cap'].get(side), r['rep'].get(side)
            if a is None and b is None:
                continue
            ia, ib = bool(a and a['identified']), bool(b and b['identified'])
            d = abs(a['sigma'] / b['sigma'] - 1) if (a and b) else None
            pairs.append((f'{lab(r)} {side[4:]}', ia, ib, d))
    res, n, over, one, none = _score(pairs, 0.03)
    out.append(_row('ESF reader (memo B)', 'sigma (capture vs replica)', False, res, '%', '3 %', 0.03, n, over, one, none,
                    '; identifiable by the reader\'s own interval flag on each image'))
    # impulse (descriptive)
    pairs, pk = [], []
    for r in im:
        a, b = r['cap'].get('impulse'), r['rep'].get('impulse')
        if not a or not b:
            continue
        ok = _nar_ok(r)
        pairs.append((lab(r), ok, ok, abs(a['single']['sigma'] / b['single']['sigma'] - 1)))
        pk.append((lab(r), ok, ok, abs(a['mix']['k'] - b['mix']['k'])))
    res, n, over, one, none = _score(pairs, 0.03)
    out.append(_row('impulse reader (memo B)', 'single sigma (capture vs replica)', False, res, '%', '3 %', 0.03, n, over,
                    one, none, '; identifiable where the narrow share 1 - k >= 0.25'))
    res, n, over, one, none = _score(pk, 0.03)
    out.append(_row('impulse reader (memo B)', 'two-Gaussian share k (capture vs replica)', False, res, '', '0.03', 0.03, n,
                    over, one, none))
    le = [r['cap']['model_enc']['lam'] for r in ck if r['cap'].get('model_enc')]
    lr = [r['rep']['model_enc']['lam'] for r in ck if r['rep'].get('model_enc')]
    out.append(dict(reader='known-space control', quantity='lam from the ENCODED reading (capture; replica)', endpoints='all',
                    band='n/a', synthetic=None, gated=False,
                    vitrea=dict(resolution=f'capture {min(le):+.2f}..{max(le):+.2f}; replica {min(lr):+.2f}..{max(lr):+.2f}',
                                tolerance='reported, not gated', verdict='N/A'),
                    notes='the wrong-space reading manufactures lam on both images alike: it is the model, not the pixels'))
    return out


def as_old(R):
    """The replica run's capture reads in the old proof-3 row format, for the superseded sigma_RMS verdicts."""
    out = []
    for r in R:
        a = r['cap']
        o = dict(ep=r['ep'], cell=r['cell'], scale=r['scale'], pitch=r.get('pitch'), src='capture', truth=r['truth'],
                 k_mean_replica=r['k_mean'])
        if r['kind'] == 'checkerboard':
            if a.get('model') is None:
                continue
            o.update(model_lin=a['model'], model_enc_known_space=a['model_enc'] or {'lam': float('nan')},
                     mirror=a.get('mirror'), heavy=a.get('heavy'), esf_bright=a.get('esf_bright'), esf_dark=a.get('esf_dark'))
        else:
            if not a.get('impulse'):
                continue
            o.update(impulse_single=a['impulse']['single'], impulse_mix=a['impulse']['mix'])
        out.append(o)
    return out


def band_rows(P1):
    """Ruling 3: the active result of a reader of W (model sw/lam/w, S, heavy) is the band pass, every region at
    least 20 pt + 2 sigma_w inside the edge; S there is gated."""
    B = [r for r in P1 if r.get('reader') == 'W-readers' and r.get('band') == 'outside']
    X = [f"{r['ep']} {r['cell']}" for r in P1 if r.get('reader') == 'W-readers' and r.get('band') == 'excluded']
    out = []
    sm = [(r, r['mirror']) for r in B if r.get('mirror')]
    idn = [(r, m) for r, m in sm if m['identified']]
    ref = [f"{r['ep']} {r['cell']} read {m['s1_gain']:+.3f} ({','.join(k for k, v in m.get('checks', {}).items() if not v)})" for r, m in sm if not m['identified']]
    none = [f"{r['ep']} {r['cell']}" for r in B if not r.get('mirror')]
    res = max((abs(m['s1_gain'] - r['truth']['s1_gain']) for r, m in idn), default=None)
    out.append(dict(reader='mirror statistic S', quantity='s1/gain, active, beyond 20 pt + 2 sigma_w (LT narrow, k_w fixed from the heavy reader)',
                    endpoints='active', band='outside', gated=True,
                    synthetic=dict(resolution=fmt(res, ''), tolerance='+-0.03', verdict=verdict(res is not None and res <= 0.03, len(idn))),
                    vitrea=None, notes=f"{len(idn)} identified: " + '; '.join(f"{r['ep']} {r['cell']} {m['s1_gain']:+.3f}/{r['truth']['s1_gain']:.3f}" for r, m in idn)
                    + f"; refused: {'; '.join(ref)}" + (f"; no model-trusted pairs: {', '.join(none)}" if none else '')
                    + f"; excluded (no pixel beyond the band + support): {', '.join(X)}"))
    for q, unit, bar in (('sw', ' pt', 0.05), ('lam', '', 0.03), ('w', '', 0.03)):
        e = [(r, abs(r['model'][q] - r['truth'][q])) for r in B if r.get('model')]
        res = max((d for _, d in e), default=None)
        out.append(dict(reader='model reader (memo C)', quantity=f'{q}, active, beyond 20 pt + 2 sigma_w', endpoints='active',
                        band='outside', gated=False,
                        synthetic=dict(resolution=fmt(res, unit), tolerance=f'+-{bar}{unit}', verdict='PASS' if res is not None and res <= bar else ('NON-IDENTIFIABLE' if res is None else 'FAIL')),
                        vitrea=None, notes='; '.join(f"{r['ep']} {r['cell']} {r['model'][q]:.3f}/{r['truth'][q]:.3f}" for r, _ in e)
                        + '; depth-graded cells: the single-width model is misspecified there (descriptive)'))
    hv = [r for r in B if r.get('heavy') and r['heavy'].get('Rfp') and np.isfinite(r['heavy']['Rfp']['rms'])]
    res = max((abs(r['heavy']['Rfp']['sw'] / r['truth']['sw'] - 1) for r in hv), default=None)
    out.append(dict(reader='pitch-64 heavy reader', quantity='sigma_w, active, beyond 20 pt + 2 sigma_w', endpoints='active',
                    band='outside', gated=False,
                    synthetic=dict(resolution=fmt(res, '', pct=True), tolerance='5 %', verdict='PASS' if res is not None and res <= 0.05 else ('NON-IDENTIFIABLE' if res is None else 'FAIL')),
                    vitrea=None, notes='; '.join(f"{r['ep']} {r['cell']} Rfp {r['heavy']['Rfp']['sw']:.2f}/{r['truth']['sw']:.2f}" for r in hv)
                    or 'no readable pitch-64 core beyond the band'))
    return out


def gate_and_attach(rows, superseded):
    """Every row gets 'gated' (ruling 2: only S); default-mask active rows of W readers are marked superseded
    by the band pass (ruling 3); proof 3's old sigma_RMS verdicts are attached beside the replica ones."""
    for r in rows:
        r.setdefault('gated', r['reader'] == 'mirror statistic S')
        if r['reader'] in ('model reader (memo C)', 'mirror statistic S', 'pitch-64 heavy reader') and r.get('band') == 'across':
            r['gated'] = False
            r['band'] = 'across (descriptive; the reported active result is the band pass, 20 pt + 2 sigma_w)'
    for r in rows:
        if r.get('vitrea') and 'measure' in r['vitrea']:
            old = [x for x in superseded if x['reader'] == r['reader']]
            r['vitrea_superseded'] = [dict(quantity=x['quantity'], **{k: x['vitrea'][k] for k in ('resolution', 'tolerance', 'verdict')})
                                      for x in old]
    return rows


if __name__ == '__main__':
    P1 = load('proof1_readers_a')
    P3 = load('proof3_readers_a')
    mo = {(r['ep'], r['cell'], r['scale'], r['src']): r for r in P3 if r.get('mirror_only')}
    P3 = [r for r in P3 if not r.get('mirror_only')]
    for r in P3:
        key = (r['ep'], r['cell'], r['scale'], r['src'])
        if key in mo and 'model_lin' in r:
            r['mirror'] = mo[key]['mirror']
    RR = []
    for f in sorted(glob.glob('proof3_readers_a.*.replica.json')):
        RR += json.load(open(f))['rows']
    superseded = vitrea_rows(as_old(RR)) if RR else vitrea_rows(P3)
    rows = synthetic_rows(P1) + band_rows(P1) + (replica_rows(RR) if RR else [])
    rows = gate_and_attach(rows, superseded)
    json.dump(rows, open('resolution_rows_a.json', 'w'), indent=1, default=float)
    with open('resolution_rows_a.txt', 'w') as fh:
        for r in rows:
            s = r['synthetic'] or {}
            v = r['vitrea'] or {}
            fh.write(f"{r['reader']} | {r['quantity']} | {r['endpoints']} | band {r['band']} | gated {r['gated']}\n"
                     f"   synthetic: {s.get('resolution', '-')} (tol {s.get('tolerance', '-')}) {s.get('verdict', '-')}\n"
                     f"   vitrea:    {v.get('resolution', '-')} (tol {v.get('tolerance', '-')}) {v.get('verdict', '-')}\n"
                     + ''.join(f"   superseded sigma_RMS bar: {x['quantity']}: {x['resolution']} (tol {x['tolerance']}) {x['verdict']}\n"
                               for x in r.get('vitrea_superseded', []))
                     + f"   notes: {r['notes']}\n")
    print(open('resolution_rows_a.txt').read())
