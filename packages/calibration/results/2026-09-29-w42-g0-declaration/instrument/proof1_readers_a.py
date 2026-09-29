"""W42 G0 instrument, proof 1 for five statistic readers (charter clause 2, first bar): on synthetic renders of
the declared families through the known T, quantised +-0.5, on the bed's declared geometries, each reader
recovers the known parameters to the tolerance `tolerances.json` declared before this ran.

Readers: memo C's model reader (read_model), the mirror statistic S (read_mirror), the pitch-64 heavy reader
(read_heavy), memo B's ESF and impulse readers (read_esf, read_impulse). Truths: LT at memo E's k per endpoint
and memo C's knee (families.TRUTH_K / TRUTH_LAM); for the heavy reader's support call also W on the canvas and
W on the rounded shape (mu = 0, the reader's own 'shape' family); and the two-sided LINEAR control
(control_linear) for S's zero, for the model reader's linear reading and for the known-space control.

Usage: python3.12 proof1_readers_a.py [endpoint ...]  -> proof1_readers_a.json and .txt (appends per endpoint
when run per endpoint; `--merge` rebuilds the .txt from the per-endpoint json files).
"""
import json
import sys
import time

import numpy as np

import bed
import control_linear as CL
import families as FA
import forward as F
import read_esf as RE
import read_heavy as RH
import read_impulse as RI
import read_mirror as RMi
import read_model as RM

TOL = json.load(open('tolerances.json'))
LT = F.Family()


def lt_truth(c, k):
    """Per-cell LT truth for the flat-width readers: sn = k 5 o (flat when receded or t = 0), sw = 8 k."""
    o = 0.4 + 0.4 * c.t if not c.active else 0.8 * c.t
    return k * 5 * o, 8 * k


def eff_narrow(c, k, depths_pt):
    """The effective narrow width the ESF and impulse readers see: k 5 o(d) and the capture's floor in
    quadrature, rms over the sample depths (CSS px)."""
    o = F.opacity_law(-np.asarray(depths_pt, float), c.span, c.active)
    return float(np.sqrt(np.mean((k * 5 * o * c.scale) ** 2 + (0.4 * c.f) ** 2)) / c.scale)


def pick(ep, scale, ids):
    """Declared cells of a pass by bed id, in the order given; ids a pass does not carry are skipped."""
    got = {c.bed_id: c for c in bed.cells(ep, scale, ids=ids)}
    return [got[i] for i in ids if i in got]


def patch_linear_side(c):
    """True when the patch's own level is on the side the knee leaves linear (light: brighter than its
    surround; dark: darker), where the impulse reader reads the narrow term."""
    fg = float(np.mean(c.bg_spec['foreground']))
    bgl = float(np.mean(c.bg_spec['background']))
    return (fg > bgl) == (c.scheme == 'light')


def window_truth(c, k, margin, R_pt=30.0):
    """The effective narrow width the impulse reader sees: LT's width is set at each OUTPUT pixel's depth, so
    the truth is the rms of k 5 o(d) (with the floor) over the window pixels that carry the patch's signal,
    those within half the patch plus twice the centre width of a square's centre."""
    sq, _, _ = RI.squares(c)
    m = RI.window(c, sq, margin, R_pt)
    s = c.scale
    H, W = c.d.shape
    yy, xx = np.mgrid[0:H, 0:W]
    near = np.zeros_like(m)
    for (y0, y1, x0, x1) in sq:
        cy, cx = (y0 + y1) / 2, (x0 + x1) / 2
        sig = eff_narrow(c, k, [-c.d[int(cy), int(cx)]])
        near |= np.hypot(yy + 0.5 - cy, xx + 0.5 - cx) < ((y1 - y0) / 2 / s + 2 * sig) * s
    sel = m & near
    return eff_narrow(c, k, -c.d[sel]) if sel.any() else float('nan')


def synth(c, fam, p, seed):
    F.synth(c, fam, p, seed=seed)
    c._rm = {}


def model_rows(ep, log):
    k, lam = FA.TRUTH_K[ep], FA.TRUTH_LAM[ep]
    pose = ep.split('-')[1]
    ids2 = ['b-p2-c16-rrect-md', 'b-p4-c64-rrect-md', 'b-p5-c64-rrect-md', 'bp-p1-c32-capsule-button',
            'bp-p1-c64-capsule-button', 'bp-p1-c32-rrect-64', 'bp-p1-c32-rrect-80', 'bp-p1-c64-rrect-ml',
            'bp-p1-c32-rrect-lg', 'bp-p1-c8-capsule-button']
    cells = pick(ep, 2, ids2) + pick(ep, 1, ['bp-p1-c8-capsule-button', 'bp-p1-c32-rrect-lg'])
    rows = []
    for i, c in enumerate(cells):
        synth(c, LT, {'k': k, 'lam': lam}, 100 + i)
        flat = (not c.active) or c.t == 0
        sn_t, sw_t = lt_truth(c, k)
        t0 = time.time()
        r = RM.read(c, kind='Rfp', space='enc', floor=True, Tkind='native', intervals=flat)
        if r is None:
            rows.append(dict(reader='model', ep=ep, cell=c.id, read=None, reason='fewer than MIN_PX trusted pixels'))
            log(f'model {ep:14s} {c.id:30s} not readable: T trust leaves fewer than {RM.MIN_PX} px')
            continue
        row = dict(reader='model', ep=ep, cell=c.id, truth=dict(sn=sn_t if flat else None, sw=sw_t, lam=lam, w=0.5),
                   read={n: r[n] for n in ('sn', 'sw', 'lam', 'w', 'rms')}, grid=r['grid'], flat=flat,
                   sn_iv=r.get('sn_iv'), sw_iv=r.get('sw_iv'))
        if flat:
            tol = TOL['proof1_statistic_readers']['model reader (memo C)']
            err = dict(sn=r['sn'] - sn_t, sw=r['sw'] - sw_t, lam=r['lam'] - lam, w=r['w'] - 0.5)
            # a width whose +0.10-code interval is ten times wider than its tolerance is not a reading on
            # that cell (declared non-identifiable there), as opposed to a biased reading (a miss)
            key = {'sn': 'sigma_n_pt', 'sw': 'sigma_w_pt'}
            ident = {n: bool(iv is not None and np.isfinite(iv[0]) and (iv[1] - iv[0]) <= 20 * tol[key[n]])
                     for n, iv in (('sn', r.get('sn_iv')), ('sw', r.get('sw_iv')))}
            row.update(err=err, identified=ident,
                       pass_=dict(sn=abs(err['sn']) <= tol['sigma_n_pt'], sw=abs(err['sw']) <= tol['sigma_w_pt'],
                                  lam=abs(err['lam']) <= tol['lam'], w=abs(err['w']) <= tol['w'],
                                  floor=r['rms'] <= TOL['synthetic_render']['fit_reaches_floor_if_pooled_rms_at_most']))
        rows.append(row)
        log(f"model {ep:14s} {c.id:30s} truth sn {row['truth']['sn'] if flat else float('nan'):6.3f} sw {sw_t:6.3f} "
            f"lam {lam:.2f} | read sn {r['sn']:6.3f} sw {r['sw']:6.3f} lam {r['lam']:.3f} w {r['w']:.3f} "
            f"rms {r['rms']:.3f}" + (f" | sn_iv {tuple(round(v, 2) for v in r['sn_iv'])} sw_iv "
                                      f"{tuple(round(v, 2) for v in r['sw_iv'])} pass {row['pass_']}" if flat
                                      else ' | depth-graded: effective sn, not gated') + f" {time.time() - t0:.0f}s")
    return rows


def linear_rows(ep, log):
    """The two-sided linear control: the model reader in linear light (recovers sn, sw, lam = 0, w = k), the
    mirror statistic's zero, and the known-space control (the same renders read in ENCODED space)."""
    rows = []
    ids = ['b-p2-c16-rrect-md', 'b-p4-c64-rrect-md', 'bp-p1-c32-capsule-button', 'bp-p1-c64-rrect-ml',
           'bp-p1-c32-rrect-80', 'bp-p1-c32-rrect-lg']
    cells = pick(ep, 2, ids) + pick(ep, 1, ['bp-p1-c8-capsule-button'])
    for i, c in enumerate(cells):
        for (sn, sw, k) in ((0.79, 10.0, 0.6), (0.79, 10.0, 0.99)):
            CL.render(c, sn, sw, k, seed=200 + i)
            lin = RM.read(c, kind='canvas', space='lin', floor=False, Tkind='srgb')
            enc = RM.read(c, kind='canvas', space='enc', floor=False, Tkind='enc-affine')
            mir = RMi.read(c, kind='canvas', space='lin', floor=False, Tkind='srgb')
            mir_enc = RMi.read(c, kind='canvas', space='enc', floor=False, Tkind='enc-affine')
            row = dict(reader='linear-control', ep=ep, cell=c.id, truth=dict(sn=sn, sw=sw, lam=0.0, w=k),
                       model_lin={n: lin[n] for n in ('sn', 'sw', 'lam', 'w', 'rms')},
                       model_enc={n: enc[n] for n in ('sn', 'sw', 'lam', 'w', 'rms')},
                       mirror_lin=None if mir is None else {n: mir[n] for n in ('s1_gain', 's1_gain_range', 'identified', 'lam', 'w')},
                       mirror_enc=None if mir_enc is None else {n: mir_enc[n] for n in ('s1_gain', 's1_gain_range', 'identified', 'lam', 'w')},
                       pitch=c.bg_spec['cell'])
            rows.append(row)
            log(f"lin-ctl {ep:14s} {c.id:30s} k {k:.2f} | lin: sn {lin['sn']:.3f} sw {lin['sw']:.2f} lam {lin['lam']:+.3f} "
                f"w {lin['w']:.3f} rms {lin['rms']:.2f} | enc(manufactured): lam {enc['lam']:+.3f} w {enc['w']:.3f} "
                f"rms {enc['rms']:.2f} | S lin {row['mirror_lin'] and round(row['mirror_lin']['s1_gain'], 4)} "
                f"S enc {row['mirror_enc'] and round(row['mirror_enc']['s1_gain'], 4)}")
    return rows


_KW = {}


def kw_from_heavy(ep, log=print):
    """The wide scale S's fixed-k_w reading takes: the pitch-64 heavy reader's Rfp sigma_w / 8 on the
    endpoint's pitch-64 cell (rrect-md, else rrect-ml), read on its own synthetic render. None where no
    pitch-64 core is readable (the dark stand-in T's clamp at spans >= 96)."""
    if ep not in _KW:
        k, lam = FA.TRUTH_K[ep], FA.TRUTH_LAM[ep]
        _KW[ep] = None
        for cid in ('b-p4-c64-rrect-md', 'bp-p1-c64-rrect-ml'):
            cs = pick(ep, 2, [cid])
            if not cs:
                continue
            c = cs[0]
            synth(c, LT, {'k': k, 'lam': lam}, 290)
            hv = RH.read(c, families=('Rfp',))
            if hv and 'Rfp' in hv and np.isfinite(hv['Rfp']['rms']):
                _KW[ep] = hv['Rfp']['sw'] / 8.0
                log(f"mirror {ep:14s} k_w for the fixed-k_w reading: {_KW[ep]:.4f} (heavy Rfp sigma_w "
                    f"{hv['Rfp']['sw']:.2f} on {cid}; truth {k:.4f})")
                break
        if _KW[ep] is None:
            log(f'mirror {ep:14s} no pitch-64 heavy reading: the fixed-k_w reading is not available')
    return _KW[ep]


def mirror_one(c, ep, lam, log, kw):
    """S three ways on one cell: the single-width reader, LT's depth-graded narrow with k_w free, and with
    k_w fixed from the heavy reader."""
    truth = lam * 0.5
    reads = {}
    for tag, kw_ in (('gauss', None), ('lt', None), ('lt|kw', kw)):
        if tag == 'lt|kw' and kw_ is None:
            continue
        r = RMi.read(c, narrow='gauss' if tag == 'gauss' else 'lt', kw=kw_)
        if r is None:
            reads[tag] = None
            continue
        reads[tag] = {q: r[q] for q in ('s1_gain', 's1_gain_range', 'identified', 'checks', 'lam', 'w', 'rmsD',
                                        'rmsS', 'n', 'Hrange')}
        reads[tag].update({q: r.get(q) for q in ('sn', 'sw', 'kn', 'kw')})
    row = dict(reader='mirror', ep=ep, cell=c.id, pitch=c.bg_spec['cell'], truth=truth, reads=reads,
               depth_graded=bool(c.active and c.t > 0))
    for tag, r in reads.items():
        if r is None:
            log(f'mirror {ep:14s} {c.id:30s} {tag:6s} no deep partner pairs / no model-trusted pairs')
            continue
        err = r['s1_gain'] - truth
        r['err'] = err
        r['pass'] = bool(abs(err) <= 0.03) if r['identified'] else None
        failed = [k for k, v in r['checks'].items() if not v]
        log(f"mirror {ep:14s} {c.id:30s} {tag:6s} truth {truth:.3f} read {r['s1_gain']:+.4f} range "
            f"({r['s1_gain_range'][0]:+.3f},{r['s1_gain_range'][1]:+.3f}) identified {r['identified']}"
            f"{' (fails: ' + ', '.join(failed) + ')' if failed else ''} err {err:+.4f}")
    return row


def mirror_rows(ep, log):
    k, lam = FA.TRUTH_K[ep], FA.TRUTH_LAM[ep]
    ids = ['b-p2-c16-rrect-md', 'b-p2-c64-rrect-md', 'b-p4-c64-rrect-md', 'b-p5-c64-rrect-md',
           'bp-p1-c32-capsule-button', 'bp-p1-c64-capsule-button', 'bp-p1-c32-rrect-ml', 'bp-p1-c64-rrect-ml',
           'bp-p1-c32-rrect-80', 'bp-p1-c32-rrect-lg', 'bp-p1-c8-capsule-button']
    cells = pick(ep, 2, ids) + pick(ep, 1, ['bp-p1-c32-rrect-lg'])
    kw = kw_from_heavy(ep, log)
    rows = []
    for i, c in enumerate(cells):
        synth(c, LT, {'k': k, 'lam': lam}, 300 + i)
        rows.append(mirror_one(c, ep, lam, log, kw))
    return rows


def heavy_rows(ep, log):
    k, lam = FA.TRUTH_K[ep], FA.TRUTH_LAM[ep]
    ids = ['b-p2-c64-rrect-md', 'b-p4-c64-rrect-md', 'bp-p1-c64-capsule-button', 'bp-p1-c64-rrect-ml']
    cells = pick(ep, 2, ids)
    truths = (('Rfp', LT, {}), ('canvas', F.Family(support='canvas', edge='clamp'), {}),
              ('shape', F.Family(support='shape'), {'mu': 0.0}))
    rows = []
    for i, c in enumerate(cells):
        for tname, fam, ex in truths:
            synth(c, fam, {'k': k, 'lam': lam, **ex}, 400 + i)
            r = RH.read(c)
            if not r:
                rows.append(dict(reader='heavy', ep=ep, cell=c.id, truth_support=tname, read=None))
                log(f'heavy {ep:14s} {c.id:30s} truth {tname:6s} no readable cores (trust or size)')
                continue
            sw_t = 8 * k
            best = r['best']
            tr = r.get(tname)
            gap = tr['rms'] - r[best]['rms'] if tr else np.nan
            rows.append(dict(reader='heavy', ep=ep, cell=c.id, truth_support=tname, truth_sw=sw_t,
                             read={f: {q: r[f][q] for q in ('sw', 'iv', 'rms', 'lam', 'w')} for f in RH.FAMILIES if f in r},
                             best=best, sw_err_rel=(tr['sw'] / sw_t - 1) if tr else None,
                             rank_gap=gap, group_rejected=bool('group' not in r or r['group']['rms'] > r[best]['rms'] + 0.5),
                             pass_sw=bool(tr and abs(tr['sw'] / sw_t - 1) <= 0.05),
                             pass_rank=bool(gap <= 0.05) if tr else None))
            log(f"heavy {ep:14s} {c.id:30s} truth {tname:6s} sw {sw_t:.2f} | best {best:6s} | " +
                ' '.join(f"{f}:{r[f]['sw']:.2f} {r[f]['rms']:.3f}" for f in RH.FAMILIES if f in r) +
                (f" | true-family sw err {100 * rows[-1]['sw_err_rel']:+.1f}% rank gap {gap:.3f}"
                 if rows[-1]['sw_err_rel'] is not None else ' | the true family has no model-trusted cores'))
    return rows


def esf_rows(ep, log):
    k, lam = FA.TRUTH_K[ep], FA.TRUTH_LAM[ep]
    ids = ['b-p2-c16-rrect-md', 'b-p3-c16-rrect-md', 'bp-p1-c8-capsule-button', 'bp-p1-c32-capsule-button',
           'bp-p1-c32-rrect-64', 'bp-p1-c32-rrect-80', 'bp-p1-c32-rrect-ml', 'bp-p1-c32-rrect-lg', 'bp-p1-c8-rrect-ml']
    cells = pick(ep, 2, ids) + pick(ep, 1, ['bp-p1-c8-capsule-button', 'bp-p1-c4-capsule-button',
                                            'bp-p1-c4-rrect-md', 'bp-p1-c32-rrect-lg'])
    rows = []
    for i, c in enumerate(cells):
        synth(c, LT, {'k': k, 'lam': lam}, 500 + i)
        r = RE.read(c, Tkind='native', margin_pt=c.d_in)
        if r is None:
            rows.append(dict(reader='esf', ep=ep, cell=c.id, read=None))
            log(f'esf {ep:14s} {c.id:30s} no deep edges')
            continue
        tr = eff_narrow(c, k, r['edge_depth_pt'])
        err = r['sigma'] / tr - 1
        rows.append(dict(reader='esf', ep=ep, cell=c.id, pitch=c.bg_spec['cell'], truth_eff=tr,
                         read={q: r[q] for q in ('sigma', 'iv', 'identified', 'rms', 'n_edges')}, err_rel=err,
                         pass_=bool(abs(err) <= 0.03)))
        log(f"esf {ep:14s} {c.id:30s} truth_eff {tr:.3f} read {r['sigma']:.3f} iv ({r['iv'][0]:.2f},{r['iv'][1]:.2f}) "
            f"identified {r['identified']} err {100 * err:+.1f}% edges {r['n_edges']}")
    # the linear control: vitrea-like sharp 1.58 dev at both scales
    for c in pick(ep, 2, ['b-p2-c16-rrect-md', 'bp-p1-c32-rrect-80']) + pick(ep, 1, ['bp-p1-c8-capsule-button']):
        CL.render(c, 1.58 / c.scale, 10.0, 0.6, seed=550)
        r = RE.read(c, Tkind='srgb', space='lin', side=1, margin_pt=c.d_in)
        if r is None:
            continue
        tr = 1.58 / c.scale
        rows.append(dict(reader='esf-linear-control', ep=ep, cell=c.id, truth=tr,
                         read={q: r[q] for q in ('sigma', 'iv', 'identified', 'rms', 'n_edges')},
                         err_rel=r['sigma'] / tr - 1))
        log(f"esf lin-ctl {ep:14s} {c.id:30s} truth {tr:.3f} read {r['sigma']:.3f} err {100 * (r['sigma'] / tr - 1):+.1f}%")
    return rows


def impulse_rows(ep, log):
    """The narrow width is read on the polarity whose patch the knee leaves linear (light: a bright patch on
    dark; dark: a dark patch on bright); the other polarity's patch is flattened toward W and reads W's
    width instead (memo B §8), which is reported beside it and not gated."""
    k, lam = FA.TRUTH_K[ep], FA.TRUTH_LAM[ep]
    ids = ['c-s8-hi-rrect-md', 'c-s8-lo-rrect-md', 'c-s32-hi-rrect-md', 'c-s32-lo-rrect-md', 'c-s16-hi-capsule-button',
           'c-s16-lo-capsule-button', 'c-s8-hi-d24-rrect-md', 'c-s8-hi-d40-rrect-lg', 'c-s8-hi-d80-rrect-lg',
           'c-impulse-rrect-ml']
    cells = pick(ep, 2, ids) + pick(ep, 1, ['c-impulse-rrect-lg'])
    rows = []
    for i, c in enumerate(cells):
        synth(c, LT, {'k': k, 'lam': lam}, 600 + i)
        margin = c.d_in
        r = RI.read(c, margin_pt=margin, R_pt=30.0, Tkind='native')
        if r is None:
            rows.append(dict(reader='impulse', ep=ep, cell=c.id, read=None))
            log(f'impulse {ep:14s} {c.id:30s} no window')
            continue
        tr = window_truth(c, k, margin)
        g, m = r['single'], r['mix']
        err = g['sigma'] / tr - 1
        reads_c = patch_linear_side(c) and c.bg_spec['size'] <= 8
        rows.append(dict(reader='impulse', ep=ep, cell=c.id, truth_eff=tr, single=g, mix=m, err_rel=err,
                         polarity='narrow' if reads_c else ('patch > 8 pt (not an impulse)' if patch_linear_side(c)
                                                            else 'knee side (reads W)'),
                         pass_=bool(abs(err) <= 0.03) if reads_c else None))
        log(f"impulse {ep:14s} {c.id:30s} {'' if reads_c else '[' + rows[-1]['polarity'] + '] '}truth_eff {tr:.3f} single "
            f"{g['sigma']:.3f} ({100 * err:+.1f}%) rms {g['rms']:.2f} | mix s1 {m['s1']:.2f} s2 {m['s2']:.2f} "
            f"k {m['k']:.2f} rms {m['rms']:.2f}")
    # the linear control: narrow 1.58 dev, wide 10 pt (2x) / 7 pt (1x), share 0.6: width and share defined
    for c in pick(ep, 2, ['c-impulse-rrect-ml']) + pick(ep, 1, ['c-impulse-rrect-lg']):
        sw = 10.0 if c.scale == 2 else 7.0
        CL.render(c, 1.58 / c.scale, sw, 0.6, seed=650)
        r = RI.read(c, margin_pt=c.d_in, R_pt=30.0, Tkind='srgb')
        if r is None:
            continue
        g, m = r['single'], r['mix']
        rows.append(dict(reader='impulse-linear-control', ep=ep, cell=c.id, truth=dict(s1=1.58 / c.scale, s2=sw, k=0.6),
                         single=g, mix=m, err_s1=m['s1'] / (1.58 / c.scale) - 1, err_k=m['k'] - 0.6))
        log(f"impulse lin-ctl {ep:14s} {c.id:30s} truth s1 {1.58 / c.scale:.3f} s2 {sw} k 0.6 | single {g['sigma']:.3f} | "
            f"mix s1 {m['s1']:.3f} s2 {m['s2']:.2f} k {m['k']:.3f} rms {m['rms']:.2f}")
    return rows

# ---------------------------------------------------------------- the active refraction band (parent's ruling)
# Apple refracts, in the ACTIVE pose only, inside an inner band reaching BAND_IN pt inward from the edge and an
# outer reach of BAND_OUT pt beyond it; LT models neither. An active reading is band-clear when every pixel it
# reads sits at least BAND_IN pt plus its kernel support inward; the support is declared as twice the widest
# Gaussian sigma the statistic depends on (the W readers: 2 sigma_w; the narrow readers: 2 sigma_n), and since
# BAND_IN exceeds BAND_OUT that same depth keeps the outer reach out of the support too.
BAND_IN, BAND_OUT = 20.0, 19.2


def band_status(active, min_depth, max_depth, support):
    if not active:
        return 'n/a (receded: no refraction)'
    if min_depth >= BAND_IN + support:
        return 'outside'
    if max_depth < BAND_IN:
        return 'inside'
    return 'across'


def band_rows(ep, log):
    """Active only: the readers re-run with every region moved beyond the band plus its support, on each cell
    that keeps a readable region there; the cells that keep none are listed as excluded with the reason."""
    if not ep.endswith('rest'):
        return []
    k, lam = FA.TRUTH_K[ep], FA.TRUTH_LAM[ep]
    light = ep.startswith('light')
    rows = []
    sw_t = 8 * k

    def fresh(cid, scale, d_in):
        c = bed.cells(ep, scale, ids=[cid], with_excluded=True)[0]
        c.mask = c.d <= -d_in
        c.d_in = d_in
        c._rm = {}
        return c

    def excluded(reader, cid, d_in, why):
        rows.append(dict(reader=reader, ep=ep, cell=cid, band='excluded', d_in=d_in, reason=why))
        log(f'band  {reader:8s} {ep:14s} {cid:30s} EXCLUDED: {why}')
    # W readers: model reader, mirror, heavy; support 2 sigma_w
    d_w = BAND_IN + 2 * sw_t
    for cid in ('bp-p1-c64-capsule-button', 'bp-p1-c32-rrect-64', 'bp-p1-c32-rrect-80', 'b-p4-c64-rrect-md',
                'bp-p1-c64-rrect-ml', 'bp-p1-c32-rrect-ml', 'bp-p1-c32-rrect-lg'):
        if not bed.cells(ep, 2, ids=[cid], with_excluded=True):
            excluded('W-readers', cid, d_w, 'not carried by this pass (or its deep mask is empty)')
            continue
        c = fresh(cid, 2, d_w)
        if c.mask.sum() < RM.MIN_PX:
            excluded('W-readers', cid, d_w, f'no pixel at depth >= {d_w:.1f} pt (band 20 + 2 sigma_w); all W '
                     'information lies inside the refraction band')
            continue
        synth(c, LT, {'k': k, 'lam': lam}, 700)
        m = RM.read(c, kind='Rfp', space='enc', floor=True, Tkind='native')
        kw_h = kw_from_heavy(ep, log)
        mi = RMi.read(c, narrow='lt', kw=kw_h) if kw_h is not None else RMi.read(c, narrow='lt')
        hv = RH.read(c, d_core=14.0) if c.bg_spec['cell'] >= 64 else None
        o_c = 0.8 * c.t
        row = dict(reader='W-readers', ep=ep, cell=cid, band='outside', d_in=d_w,
                   model=None if m is None else {q: m[q] for q in ('sn', 'sw', 'lam', 'w', 'rms')},
                   mirror=None if mi is None else {q: mi[q] for q in ('s1_gain', 's1_gain_range', 'identified', 'checks', 'narrow')},
                   heavy=None if not hv else {'best': hv['best'], **{f: {q: hv[f][q] for q in ('sw', 'rms')} for f in RH.FAMILIES if f in hv}},
                   truth=dict(sw=sw_t, lam=lam, w=0.5, s1_gain=0.5 * lam, sn_centre=k * 5 * o_c))
        rows.append(row)
        log(f"band  W-readers {ep:14s} {cid:30s} d_in {d_w:.1f} px {int(c.mask.sum())} | model "
            + ('none' if m is None else f"sn {m['sn']:.2f} sw {m['sw']:.2f}/{sw_t:.2f} lam {m['lam']:.3f} w {m['w']:.3f} rms {m['rms']:.2f}")
            + ' | S ' + ('none' if mi is None else f"{mi['s1_gain']:+.3f}/{0.5 * lam:.3f} id {mi['identified']}")
            + ' | heavy ' + ('none' if not hv else f"{hv['best']} " + ' '.join(f"{f}:{hv[f]['sw']:.1f} {hv[f]['rms']:.3f}" for f in ('Rfp', 'shape', 'group') if f in hv)))
    # narrow readers: ESF and impulse; support 2 sigma_n(centre)
    for cid, reader in (('bp-p1-c8-capsule-button', 'esf'), ('b-p2-c16-rrect-md', 'esf'), ('bp-p1-c32-rrect-80', 'esf'),
                        ('bp-p1-c32-rrect-ml', 'esf'), ('bp-p1-c32-rrect-lg', 'esf'),
                        (f"c-s8-{'hi' if light else 'lo'}-rrect-md", 'impulse'),
                        (f"c-s16-{'hi' if light else 'lo'}-capsule-button", 'impulse'), ('c-s8-hi-d80-rrect-lg', 'impulse')):
        found = bed.cells(ep, 2, ids=[cid], with_excluded=True)
        if not found:
            excluded(reader, cid, float('nan'), 'not carried by this pass (or its deep mask is empty)')
            continue
        c0 = found[0]
        sn_c = np.sqrt((k * 5 * 0.8 * c0.t * c0.scale) ** 2 + (0.4 * c0.f) ** 2) / c0.scale
        d_n = BAND_IN + 2 * sn_c
        c = fresh(cid, 2, d_n)
        if c.mask.sum() < RM.MIN_PX:
            excluded(reader, cid, d_n, f'no pixel at depth >= {d_n:.1f} pt (band 20 + 2 sigma_n); the narrow '
                     'term is read only inside the refraction band')
            continue
        synth(c, LT, {'k': k, 'lam': lam}, 710)
        if reader == 'esf':
            r = RE.read(c, Tkind='native', margin_pt=d_n)
            if r is None:
                excluded(reader, cid, d_n, 'no checker edge whose samples all clear the band')
                continue
            tr = eff_narrow(c, k, r['edge_depth_pt'])
            rows.append(dict(reader='esf', ep=ep, cell=cid, band='outside', d_in=d_n, truth_eff=tr,
                             read={q: r[q] for q in ('sigma', 'iv', 'identified', 'n_edges')}, err_rel=r['sigma'] / tr - 1))
            log(f"band  esf      {ep:14s} {cid:30s} d_in {d_n:.1f} truth_eff {tr:.3f} read {r['sigma']:.3f} "
                f"err {100 * (r['sigma'] / tr - 1):+.1f}% edges {r['n_edges']} identified {r['identified']}")
        else:
            r = RI.read(c, margin_pt=d_n, R_pt=30.0, Tkind='native', mix=False)
            if r is None:
                excluded(reader, cid, d_n, 'no impulse window clears the band')
                continue
            tr = window_truth(c, k, d_n)
            g = r['single']
            rows.append(dict(reader='impulse', ep=ep, cell=cid, band='outside', d_in=d_n, truth_eff=tr, single=g,
                             err_rel=g['sigma'] / tr - 1))
            log(f"band  impulse  {ep:14s} {cid:30s} d_in {d_n:.1f} truth_eff {tr:.3f} single {g['sigma']:.3f} "
                f"err {100 * (g['sigma'] / tr - 1):+.1f}%")
    return rows


def main(eps, which):
    for ep in eps:
        out = []
        fn = f'proof1_readers_a.{ep}.{which}.txt'
        fh = open(fn, 'w')

        def log(s):
            print(s, flush=True)
            fh.write(s + '\n')
            fh.flush()
        t0 = time.time()
        for name, f in (('model', model_rows), ('linear', linear_rows), ('mirror', mirror_rows),
                        ('heavy', heavy_rows), ('esf', esf_rows), ('impulse', impulse_rows), ('band', band_rows)):
            if which != 'all' and name not in which.split(','):
                continue
            for r in f(ep, log):
                r['section'] = name
                out.append(r)
        for sc in (2, 1):
            for cid, why in bed.refraction_exclusions(ep, sc).items():
                out.append(dict(reader='exclusion', ep=ep, cell=f'{sc}x|{cid}', reason=why))
                log(f'excluded {ep:14s} {sc}x|{cid}: {why}')
        log(f'# {ep} {which} done in {time.time() - t0:.0f} s')
        json.dump(out, open(f'proof1_readers_a.{ep}.{which}.json', 'w'), indent=1, default=float)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    which = next((a[8:] for a in sys.argv[1:] if a.startswith('--which=')), 'all')
    main(args or list(F.ENDPOINTS), which)
