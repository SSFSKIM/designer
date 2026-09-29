"""W42 G0 instrument: the pitch-64 heavy reader (charter Design, "The instrument"; memo C §2a;
`~/vitrea-w42/grounding/probe/heavy.py`, SHA-256 1f8d8ae7…, and `heavy2.py`).

The declared statistic. On a two-level checker's CORES, the pixels at least d_core pt from every checker
edge, the narrow term has saturated at the square's own level, so the hinge is decided by the side alone:
on the knee side (light: the darker level; dark: the brighter) h = sg (W - C) is always positive, and on the
far side it is always zero. The algebra then reduces, per side, to an affine function of W alone:

    M = alpha_side + beta_side W,   far: beta = w,   knee: beta = lam + w (1 - lam)

so W's width and SUPPORT are read without the narrow term's width, the hinge's form or a lam prior, by
scanning sigma_w for each support family and keeping the best residual:
'Rfp' (LT's declared footprint and edge mode), 'canvas', 'shape' (normalised over the rounded shape),
'box' (normalised over its bounding box) and 'group' (the shape's mean, the group-level null memo C rejected
by 5-10x). The best sigma_w is refined continuously within its grid bracket; its interval is the grid range
where rms <= 1.05 best + 0.02 (memo C's 5 % interval), and lam, w follow from the two betas.

d_core defaults to memo C's 14 pt; at pitch 64 that leaves each square a 36-pt core. The narrow term is only
approximately saturated there when it is wide (the receded rrect-lg reads sigma_n about 8 pt), which is part
of what proof 1 measures.
"""
import numpy as np
from scipy import ndimage, optimize

import geometry as G
import read_model as RM

SWH = [4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 26, 28, 32, 40, 48]
FAMILIES = ('Rfp', 'canvas', 'shape', 'box', 'group')


def edge_distance(cell):
    """Distance (pt) to the nearest checker edge, and the boolean 'bright' map of the backdrop."""
    B = cell.B if cell.B.ndim == 2 else G.luma(cell.B * 255) / 255
    bright = B > 0.5 * (B.min() + B.max())
    e = np.zeros_like(bright)
    e[:, 1:] |= bright[:, 1:] != bright[:, :-1]
    e[:, :-1] |= bright[:, 1:] != bright[:, :-1]
    e[1:, :] |= bright[1:, :] != bright[:-1, :]
    e[:-1, :] |= bright[1:, :] != bright[:-1, :]
    return ndimage.distance_transform_edt(~e) / cell.scale, bright


def prep(cell, d_core, Tkind):
    m = RM.eval_mask(cell)
    dist, bright = edge_distance(cell)
    m = m & (dist >= d_core)
    Mo, wt, _ = RM.m_domain(cell, Tkind, m)
    knee = (~bright if cell.scheme == 'light' else bright)[m]
    return m, knee, Mo, wt


def fit_w(W, knee, Mo, wt):
    far = ~knee
    X = np.stack([knee, far, W * knee * 255, W * far * 255], 1).astype(float)
    cf, *_ = np.linalg.lstsq(X * wt[:, None], Mo * wt, rcond=None)
    r = (Mo - X @ cf) * wt
    return dict(a_knee=cf[0], a_far=cf[1], b_knee=cf[2], b_far=cf[3], rms=float(np.sqrt(np.mean(r ** 2))),
                n_knee=int(knee.sum()), n_far=int(far.sum()))


def algebra(r):
    """lam, w from the two betas: far beta = w; knee beta = lam + w (1 - lam)."""
    bk, bf = r['b_knee'], r['b_far']
    return dict(w=float(bf), lam=float((bk - bf) / (1 - bf)) if bf != 1 else np.nan)


def scan(cell, fam, d_core=14.0, space='enc', floor=True, Tkind='native', sws=SWH, refine=True):
    m, knee, Mo, wt = prep(cell, d_core, Tkind)
    if m.sum() < 30 or knee.all() or not knee.any():
        return None
    Wat = lambda sw: RM.blurred(cell, sw, fam, space, floor, 'W')[m]
    Cc = RM.source(cell, space, floor)[m]      # the saturated narrow term: the core's own (floored) level
    lim = getattr(cell.T, 'trust_below', None)
    if Tkind == 'native' and lim is not None and space == 'enc':
        # model-based trust (read_model.model_trusted), per width: keep a core pixel when 255 max(C, W) is
        # below T's limit; selecting on the observed code would censor on the dependent variable
        def fit_at(sw):
            W = Wat(sw)
            keep = RM.model_trusted(cell, Cc, W, space, Tkind)
            if keep.sum() < 30 or knee[keep].all() or not knee[keep].any():
                return dict(rms=np.inf, b_knee=np.nan, b_far=np.nan, a_knee=np.nan, a_far=np.nan,
                            n_knee=0, n_far=0)
            return fit_w(W[keep], knee[keep], Mo[keep], wt[keep])
    else:
        fit_at = lambda sw: fit_w(Wat(sw), knee, Mo, wt)
    if fam == 'group':
        r = fit_at(0.0)
        r.update(sw=0.0, iv=(0.0, 0.0), **algebra(r))
        return r
    rows = []
    for sw in sws:
        r = fit_at(sw)
        r['sw'] = sw
        rows.append(r)
    best = min(rows, key=lambda r: r['rms'])
    if not np.isfinite(best['rms']):
        return None
    ok = [r['sw'] for r in rows if r['rms'] <= best['rms'] * 1.05 + 0.02]
    iv = (min(ok), max(ok))
    if refine:
        i = sws.index(best['sw'])
        lo, hi = sws[max(0, i - 1)], sws[min(len(sws) - 1, i + 1)]
        res = optimize.minimize_scalar(lambda v: fit_at(v)['rms'], bounds=(lo, hi),
                                       method='bounded', options=dict(xatol=0.01))
        rr = fit_at(res.x)
        if rr['rms'] <= best['rms']:
            rr['sw'] = float(res.x)
            best = rr
    best['iv'] = iv
    best.update(algebra(best))
    return best


def read(cell, d_core=14.0, space='enc', floor=True, Tkind='native', families=FAMILIES):
    """Every support family's best sigma_w, rms, interval and algebra; 'best' names the family ranked first."""
    out = {}
    for fam in families:
        r = scan(cell, fam, d_core, space, floor, Tkind)
        if r is not None:
            out[fam] = r
    if out:
        out['best'] = min((f for f in out), key=lambda f: out[f]['rms'])
    return out
