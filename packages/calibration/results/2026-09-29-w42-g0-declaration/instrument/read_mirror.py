"""W42 G0 instrument: the mirror statistic S (charter clause 2 and Design, "The instrument"; memo C §1 and
§2c; `~/vitrea-w42/grounding/probe/mirror.py`, SHA-256 818f3919…).

The declared statistic. On a two-level checker a pixel x and its partner x' one pitch away see
colour-inverted backdrops (B' = a + b - B). For canvas-wide kernels C + C' and W + W' are then constant, and
in the mixing domain

    S = M(x) + M(x') = s0 + s1 (h(x) + h(x')),     s1 = sg gain lam (1 - w)
    D = M(x) - M(x') = d1 (C - C') + d2 (W - W')

so S carries the one-sided knee independently of the kernels' shapes, and s1 / gain is ZERO for any
two-sided linear system: that is why the charter establishes the knee by S and not by lam (a wrong mixing
space can manufacture a lam; clause 2). D, which is two-sided and linear, carries the widths.

Generalised past memo C's canvas case: a footprint-limited or clamped blur on a finite shape breaks the
partners' exact inversion, so S is regressed with the centred partner sums (C + C', W + W') as nuisance
regressors and D with the knee's residual share r = sg (h - h') - (dW - dC) / 2; each vanishes (and is
dropped) when the inversion is exact, which is memo C's reader. A two-sided linear system still reads
s1 = 0 exactly. (sn, sw) are chosen on a grid by the joint residual rmsD^2 + rmsS^2 (D alone trades width
against share on a small shape at one pitch), and s1's standard error is returned: where H = h + h' barely
varies (a sharp narrow term at a fine pitch) s1 is not identified, and the reader says so. The narrow term
may instead be LT's own depth-graded map (narrow='lt'), which is the reading on active cells with t > 0,
where no single width follows the truth; the identifiability rule is in `_finish`. Partners are taken horizontally and
vertically, both in the deep mask; the regression weights put residuals in output codes.

Returns s1/gain (= lam (1 - w) for the algebra), the implied lam and w, D's widths, both residuals and the
pair count. The pitch and the levels come from the cell's own background spec.
"""
import numpy as np
from scipy import optimize

import forward as F
import read_model as RM

SN = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0]
SW = [6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32]
# s1/gain is IDENTIFIED on a cell when every kernel within the joint residual's tolerance of the best reads it
# within this span (twice the declared +-0.03): a statistic that moves more with the kernel than the bar
# allows is not a reading on that cell.
IDENT_SPAN = 0.06
# ... and when H = h + h' spans at least this much (0..1 units): with H nearly constant s1 is not a slope.
MIN_HRANGE = 0.05
# ... and when both regressions fit at the noise floor (see _finish), and the implied w is inside (W_MIN, 1 - W_MIN).
FLOOR_RMS = 0.42
RESID_FACTOR = 1.3
W_MIN = 0.05
MIN_KEPT = 0.5
# LT kernel grid for narrow='lt' (memo E reads k 1.98-2.17)
KN = [1.0, 1.5, 2.0, 2.5, 3.0]
KW = [1.4, 1.75, 2.1, 2.45, 2.8]
# the fixed k_w's own uncertainty: the pitch-64 heavy reader's proof-1 resolution in the active pose (3.2 %)
KW_REL = 0.032


def pairs(cell, m):
    """Index arrays (A, B) of partner pixels one pitch apart, horizontally and vertically, both in m."""
    p = int(round(cell.bg_spec['cell'] * cell.scale))
    H, W = m.shape
    ys, xs = np.nonzero(m[:, :W - p] & m[:, p:])
    ys2, xs2 = np.nonzero(m[:H - p, :] & m[p:, :])
    A = (np.concatenate([ys, ys2]), np.concatenate([xs, xs2]))
    B = (np.concatenate([ys, ys2 + p]), np.concatenate([xs + p, xs2]))
    return A, B


def _canvas(cell, m, v):
    out = np.full(m.shape, np.nan)
    out[m] = v
    return out


def read_at(cell, sn, sw, kind='Rfp', space='enc', floor=True, Tkind='native', P=None, m=None, Mw=None):
    """S at one single-width Gaussian kernel (memo C's reader, generalised)."""
    C = RM.blurred(cell, sn, kind, space, floor, 'C')
    Wm = RM.blurred(cell, sw, kind, space, floor, 'W')
    r = regress_pairs(cell, C, Wm, space, Tkind, P, m, Mw)
    r.update(sn=sn, sw=sw)
    return r


def lt_maps(cell, kn, kw):
    """C and W as canvas images from the forward engine's own LT maps: the capture floor, R_fp with its
    declared margin and edge modes, the narrow width k_n 5 o(d) graded by depth, W = G(k_w 8) (encoded)."""
    key = ('lt', round(float(kn), 4), round(float(kw), 4))
    c = RM._cache(cell)
    if key not in c:
        mp = F.maps(cell, F.Family(), {'k_n': kn, 'k_w': kw})
        C = np.full(cell.d.shape, np.nan)
        W = np.full(cell.d.shape, np.nan)
        C[cell.mask], W[cell.mask] = mp['C'], mp['W']
        for k in [k for k in c if k[0] == 'lt'][:-24]:
            del c[k]
        c[key] = (C, W)
    return c[key]


def read_at_lt(cell, kn, kw, Tkind='native', P=None, m=None, Mw=None):
    """S at LT's kernel pair (k_n, k_w): the depth-graded narrow term the declared law draws."""
    C, Wm = lt_maps(cell, kn, kw)
    r = regress_pairs(cell, C, Wm, 'enc', Tkind, P, m, Mw)
    r.update(kn=kn, kw=kw, sn=np.nan, sw=kw * 8.0)
    return r


def regress_pairs(cell, C, Wm, space, Tkind, P=None, m=None, Mw=None):
    m = RM.eval_mask(cell) if m is None else m
    A, B = P if P is not None else pairs(cell, m)
    if Mw is None:
        Mo, wt, _ = RM.m_domain(cell, Tkind, m)
        Mw = (_canvas(cell, m, Mo), _canvas(cell, m, wt))
    Mo, wt = Mw
    sg = 1 if cell.scheme == 'light' else -1
    # pairs whose two pixels the MODEL places below T's trust limit (read_model.model_trusted), at this kernel
    okA = RM.model_trusted(cell, C[A], Wm[A], space, Tkind)
    okB = RM.model_trusted(cell, C[B], Wm[B], space, Tkind)
    n_cand = int(A[0].size)
    if not (okA & okB).all():
        sel = okA & okB
        if sel.sum() < 50:
            return dict(d1=np.nan, d2=np.nan, gain=np.nan, s0=np.nan, s1=np.nan, s1_gain=np.nan,
                        w=np.nan, lam=np.nan, rmsD=np.inf, rmsS=np.inf, sdS=np.nan, n=int(sel.sum()),
                        Hrange=np.nan, s1_gain_se=np.inf, n_candidates=n_cand)
        A, B = (A[0][sel], A[1][sel]), (B[0][sel], B[1][sel])
    h = lambda ix: np.maximum(0, sg * (Wm[ix] - C[ix]))
    S = Mo[A] + Mo[B]
    D = Mo[A] - Mo[B]
    ws = 1 / np.sqrt(1 / wt[A] ** 2 + 1 / wt[B] ** 2)
    hA, hB = h(A), h(B)
    Hh = hA + hB
    dC, dW = C[A] - C[B], Wm[A] - Wm[B]
    # r vanishes when the partners are exact colour inverses under the kernel (canvas blurs); a footprint
    # or a finite shape breaks that, and r carries the knee's share of D there, so gain = d1 + d2 always.
    rr = sg * (hA - hB) - 0.5 * (dW - dC)
    XD = [dC, dW] + ([rr] if np.ptp(rr) > 1e-4 else [])
    XD = np.stack(XD, 1) * 255
    cD, *_ = np.linalg.lstsq(XD * ws[:, None], D * ws, rcond=None)
    rD = (D - XD @ cD) * ws
    sums = [v - v.mean() for v in (C[A] + C[B], Wm[A] + Wm[B]) if np.ptp(v) > 1e-4]
    XS = np.stack([np.ones_like(Hh), Hh * 255] + [v * 255 for v in sums], 1)
    cS, *_ = np.linalg.lstsq(XS * ws[:, None], S * ws, rcond=None)
    rS = (S - XS @ cS) * ws
    # the standard error of s1 (output-code weighted residuals), for the identifiability flag
    Xw = XS * ws[:, None]
    try:
        cov = np.linalg.inv(Xw.T @ Xw) * np.mean(rS ** 2) * len(rS) / max(len(rS) - Xw.shape[1], 1)
        se_s1 = float(np.sqrt(cov[1, 1]))
    except np.linalg.LinAlgError:
        se_s1 = np.inf
    d1, d2 = cD[0], cD[1]
    s0, s1 = cS[0], cS[1]
    s1 = sg * s1
    gain = d1 + d2
    one_w = (s1 / 2 + d1) / gain if gain else np.nan
    lam = s1 / (gain * one_w) if gain and one_w else np.nan
    return dict(d1=float(d1), d2=float(d2), gain=float(gain), s0=float(s0), s1=float(s1),
                s1_gain=float(s1 / gain) if gain else np.nan, w=float(1 - one_w), lam=float(lam),
                rmsD=float(np.sqrt(np.mean(rD ** 2))), rmsS=float(np.sqrt(np.mean(rS ** 2))),
                sdS=float(np.std(S * ws)), n=int(A[0].size), Hrange=float(np.ptp(Hh)),
                s1_gain_se=float(se_s1 / abs(gain)) if gain else np.inf, n_candidates=n_cand)


def _finish(best, rows, score, floor_rms, forced=()):
    """The kernel spread of s1/gain and the identifiability flag. A reading is IDENTIFIED only when
    (1) every kernel the pairs do not distinguish (residual within two standard errors) reads s1/gain within
        IDENT_SPAN,
    (2) H = h + h' spans at least MIN_HRANGE,
    (3) both regressions fit at the noise floor: max(rmsD, rmsS) <= RESID_FACTOR x floor_rms, and
    (4) the implied w lies in [W_MIN, 1 - W_MIN], and
    (5) T's trust limit keeps at least MIN_KEPT of the candidate partner pairs.
    (3) and (4) were added after proof 1 found the silent false negative: on depth-graded active cells a
    single narrow width cannot follow the truth, D collapses onto W (w 0.99), S reads 0.002 against 0.44,
    and every nearby kernel agrees, so (1) and (2) alone said "identified". The collapse leaves residuals at
    about twice the floor (0.80 against 0.41); a model that does not fit its own pairs is not a reading.
    (5) was added when the dark receded rrect-ml and rrect-lg at pitch 32 read 0.12-0.20 against 0.40 with
    (1)-(4) passing: the stand-in T's clamp left 6-8 % of the pairs, chosen by their C and W, which are
    what H is made of, so the selection biased the slope."""
    # kernels the pairs do not distinguish: those whose residual is within two standard errors of the best
    # residual's own estimate (rms / sqrt(2 n) per regression, n pairs). This replaces memo C's 5 % + 0.02
    # band, which on a model that fits at the floor admitted kernels the data reject by tens of standard
    # errors; (3) below carries the robustness against a model that does not fit.
    rb = np.sqrt(score(best) / 2)
    band = 2 * rb / np.sqrt(2 * max(best['n'], 1)) + 1e-3
    ok = [r for r in rows if np.sqrt(score(r) / 2) <= rb + band and np.isfinite(r['s1_gain'])]
    ok += [r for r in forced if np.isfinite(r['s1_gain'])]      # an external width's own uncertainty
    best['s1_gain_range'] = (min(r['s1_gain'] for r in ok), max(r['s1_gain'] for r in ok))
    best['kernel_band_rms'] = float(band)
    lo, hi = best['s1_gain_range']
    fits = max(best['rmsD'], best['rmsS']) <= RESID_FACTOR * floor_rms
    w_ok = W_MIN <= best['w'] <= 1 - W_MIN
    kept = best['n'] / max(best.get('n_candidates', best['n']), 1)
    best['checks'] = dict(spread=bool(hi - lo <= IDENT_SPAN), hrange=bool(best['Hrange'] >= MIN_HRANGE),
                          fits_floor=bool(fits), w_inside=bool(w_ok), pairs_kept=bool(kept >= MIN_KEPT))
    best['pairs_kept_frac'] = float(kept)
    best['identified'] = all(best['checks'].values())
    best['floor_rms'] = floor_rms
    return best


def read(cell, kind='Rfp', space='enc', floor=True, Tkind='native', sns=SN, sws=SW, narrow='gauss',
         floor_rms=FLOOR_RMS, kns=KN, kws=KW, kw=None, kw_rel=KW_REL):
    """D picks the kernel (on a grid, refined continuously) and S is read at it.

    narrow 'gauss': one single-width Gaussian narrow term (memo C's reader; vitrea's narrow is flat in depth,
    so this stays its reading). narrow 'lt': the narrow and wide terms are the forward engine's own LT maps
    at (k_n, k_w), the narrow width graded by depth as the declared law draws it (encoded, native T).
    floor_rms is the per-pair residual expected from noise alone: the synthetic quantisation floor by
    default; on native captures the measured repeat bar sets it (G2).

    kw (narrow 'lt' only) fixes the wide scale from an independent reading (the pitch-64 heavy reader's
    sigma_w / 8 on the same endpoint). At pitch 32 on the active depth-graded shapes the pairs' own residual
    barely separates k_w, and s1/gain moves with it (about -0.8 per unit k_w on rrect-ml), so there the
    spread check refuses the free-k_w reading and the fixed-k_w reading is the one that can be identified.
    The fixed k_w is itself a reading: its uncertainty kw_rel (the heavy reader's proof-1 resolution) is
    propagated by re-reading S at k_w (1 +- kw_rel), and those readings enter the spread check whatever their
    residual, since the pairs cannot vouch for a width they did not measure."""
    m = RM.eval_mask(cell)
    P = pairs(cell, m)
    if P[0][0].size < 50:
        return None
    Mo, wt, _ = RM.m_domain(cell, Tkind, m)
    Mw = (_canvas(cell, m, Mo), _canvas(cell, m, wt))
    score = lambda r: r['rmsD'] ** 2 + r['rmsS'] ** 2
    if narrow == 'lt':
        if kw is not None:
            at = lambda a, b=None: read_at_lt(cell, a, kw, Tkind, P, m, Mw)
            rows = [at(kn) for kn in kns]
            best = min(rows, key=score)
            if not np.isfinite(score(best)):
                return None
            res = optimize.minimize_scalar(lambda v: score(at(float(np.clip(v, 0.3, 4.0)))),
                                           bounds=(max(0.3, best['kn'] - 0.5), min(4.0, best['kn'] + 0.5)),
                                           method='bounded', options=dict(xatol=0.002))
            ref = at(float(res.x))
            rows += [at(v) for v in np.linspace(ref['kn'] - 0.3, ref['kn'] + 0.3, 13)]
            if score(ref) < score(best):
                best = ref
                rows.append(ref)
            forced = []
            for f in (1 - kw_rel, 1 + kw_rel):
                at_f = lambda a: read_at_lt(cell, float(np.clip(a, 0.3, 4.0)), kw * f, Tkind, P, m, Mw)
                rf = optimize.minimize_scalar(lambda v: score(at_f(v)), bounds=(max(0.3, best['kn'] - 0.4),
                                              min(4.0, best['kn'] + 0.4)), method='bounded', options=dict(xatol=0.002))
                forced.append(at_f(float(rf.x)))
            best['narrow'] = 'lt|kw fixed'
            best['kw_rel'] = kw_rel
            return _finish(best, rows, score, floor_rms, forced)
        at = lambda a, b: read_at_lt(cell, a, b, Tkind, P, m, Mw)
        rows = [at(kn, kw_) for kw_ in kws for kn in kns]
        best = min(rows, key=score)
        if not np.isfinite(score(best)):
            return None
        z0 = [best['kn'], best['kw']]
        simplex = [z0, [z0[0] + 0.15, z0[1]], [z0[0], z0[1] + 0.1]]
        clip = lambda z: (float(np.clip(z[0], 0.3, 4.0)), float(np.clip(z[1], 0.8, 4.0)))
    else:
        # the narrow kernel is kept at most half the wide one: where a single narrow width cannot follow the
        # truth, D otherwise drifts to the degenerate branch sn ~ sw, where C ~ W and h ~ 0
        at = lambda a, b: read_at(cell, a, b, kind, space, floor, Tkind, P, m, Mw)
        rows = [at(sn, sw) for sw in sws for sn in sns if sn <= sw / 2]
        best = min(rows, key=score)
        if not np.isfinite(score(best)):
            return None
        z0 = [best['sn'], best['sw']]
        simplex = [z0, [z0[0] + 0.5, z0[1]], [z0[0], z0[1] + 1.0]]
        clip = lambda z: (min(max(z[0], 0.0), z[1] / 2), float(z[1]))
    # continuous refinement from the grid's best (the grid's steps bias s1)
    zr = optimize.minimize(lambda z: score(at(*clip(z))), z0, method='Nelder-Mead',
                           options=dict(xatol=0.005, fatol=1e-5, maxfev=60, initial_simplex=simplex)).x
    ref = at(*clip(zr))
    if score(ref) < score(best):
        best = ref
        rows.append(ref)
    if narrow == 'lt':
        rows += [at(*clip((best['kn'] + a, best['kw'] + b))) for a in (-0.1, -0.05, 0.05, 0.1) for b in (-0.1, -0.05, 0, 0.05, 0.1)]
    best['narrow'] = narrow
    return _finish(best, rows, score, floor_rms)
