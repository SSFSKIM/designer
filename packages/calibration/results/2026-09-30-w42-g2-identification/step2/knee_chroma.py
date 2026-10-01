"""W42 G2 step 2, part 3: family E, the knee form (declaration `kneeForms`) and candidate 2's chroma scale
(`candidate2Chroma`, Decision Log 5c as the parent reads it, A3), reading-plan.md item 6.

On grey backdrops the three knee forms coincide exactly, so family E answers the knee. With the family's k and lam
held at its grey fit (the minimax point of fits/<tag>/<family>__<endpoint>__n.json), each form is read through
candidate 2's declared chroma form

    y_c = clip(T_c(L(arg)) + s g(L(arg)) (arg_c - L(arg)), 0, 255)          (codes; L = Rec.709 on encoded)

with arg = M_rgb (per-channel), the whole-colour on-luma composite (knee-luma), or M_L + (W - L(W)) (on luma, chroma
from W); T_c the per-channel native T; g W41 G1's E3 fit (least squares, the rehearsal's G_FIT) for the endpoint.
s is fitted on E's calibration cells (least squares at equal cell weight, then minimax on their region statistics)
and checked on E's validation cells at clause 6's bar.

    python3.12 -B knee_chroma.py [FAMILY] [TAG]     -> knee/<family>__<endpoint>.json
"""
import gzip
import hashlib
import json
import sys

import numpy as np
from scipy import optimize

import common as C

F = C.F
FORMS = ('channel', 'luma', 'lumaW')
FORM_NAME = {'channel': 'per-channel (arg = M_rgb)', 'luma': 'on-luma, whole colour',
             'lumaW': 'on-luma, chroma from W (A = M_L + (W - L(W)))'}
E3 = C.P.RESULTS / '2026-09-27-w41-g1-identification' / 'body' / 'attempt-1'
W41_NAME = {'light-rest': 'light-active', 'light-inactive': 'light-inactive', 'dark-rest': 'dark-active',
            'dark-inactive': 'dark-inactive'}
S_BOUNDS = (0.0, 3.0)


def g_coeffs(ep):
    return json.loads((E3 / f'{W41_NAME[ep]}-E3-fit.json').read_text())['local']['leastSquares']['coefficients']


def g_of(q, L):
    g0, g1, g2 = q
    L = np.asarray(L, float)
    lo = g0 + np.clip((L - 63) / 30, 0, 1) * (g1 - g0)
    hi = g1 + np.clip((L - 93) / 25, 0, 1) * (g2 - g1)
    return np.where(L > 93, hi, lo)


def argument(c, fam, p, form):
    mp = F.maps(c, fam, F.expand(fam, p))
    Cm, W = mp['C'], mp['W']
    sg = 1.0 if c.scheme == 'light' else -1.0
    lam = p['lam']
    if form == 'channel':
        N = Cm + sg * lam * np.maximum(0, sg * (W - Cm))
        return 0.5 * N + 0.5 * W
    if form == 'luma':
        gap = sg * ((W - Cm) @ C.W709)
        N = Cm + lam * (gap > 0)[:, None] * (W - Cm)
        return 0.5 * N + 0.5 * W
    CL, WL = Cm @ C.W709, W @ C.W709
    NL = CL + sg * lam * np.maximum(0, sg * (WL - CL))
    ML = 0.5 * NL + 0.5 * WL
    return ML[:, None] + (W - WL[:, None])


def output(c, arg, s, q):
    a = 255 * arg
    L = a @ C.W709
    base = np.stack([Tc(L) for Tc in c.Tc], -1)
    return np.clip(base + s * g_of(q, L)[:, None] * (a - L[:, None]), 0, 255)


def run(family='LT', tag='main'):
    import fit_family
    FF = fit_family
    fam = fit_family.family_of(family)
    out = {}
    for ep in C.EPS:
        fit = json.loads((C.HERE / 'fits' / tag / f'{family}__{ep}__n.json').read_text())
        pt = fit['minimax']
        p = {k.split('@')[0]: v for k, v in pt['params'].items()}
        p['lam'] = pt['lam'][ep]
        p = F.expand(fam, p)
        q = g_coeffs(ep)
        cal = C.cells(ep, 2, ('calibration',), letters=('E',), rgb=True)
        val = C.cells(ep, 2, ('validation',), letters=('E',), rgb=True)
        tables = {}
        res = dict(family=family, endpoint=ep, lawParams=dict(p), gCoefficients=q,
                   gSource=f'{W41_NAME[ep]}-E3-fit.json local.leastSquares.coefficients (the rehearsal G_FIT)', forms={})
        for form in FORMS:
            args_cal = [argument(c, fam, p, form) for c in cal]
            args_val = [argument(c, fam, p, form) for c in val]
            ys = [c.y[c.mask].astype(float) for c in cal]

            def ls(s):
                return float(np.mean([np.mean((output(c, a, s, q) - y) ** 2) for c, a, y in zip(cal, args_cal, ys)]))
            r = optimize.minimize_scalar(ls, bounds=S_BOUNDS, method='bounded', options=dict(xatol=1e-5))
            s_ls = float(r.x)

            def mm(s):
                return max(max(C.minimax_objective_terms(c, output(c, a, s, q)) or [0])
                           for c, a in zip(cal, args_cal))
            lo, hi = max(S_BOUNDS[0], s_ls - 0.5), min(S_BOUNDS[1], s_ls + 0.5)
            grid = np.linspace(lo, hi, 101)
            vals = [mm(s) for s in grid]
            s0 = float(grid[int(np.argmin(vals))])
            r2 = optimize.minimize_scalar(mm, bounds=(max(lo, s0 - 0.01), min(hi, s0 + 0.01)), method='bounded',
                                          options=dict(xatol=1e-5))
            s_mm = float(r2.x) if r2.fun <= min(vals) else s0
            row = {}
            for key, s in (('ls', s_ls), ('minimax', s_mm)):
                pc = [output(c, a, s, q) for c, a in zip(cal, args_cal)]
                pv = [output(c, a, s, q) for c, a in zip(val, args_val)]
                sc, sv = C.summarize(cal, pc), C.summarize(val, pv)
                tables.setdefault(form, {})[key] = dict(calibration=FF.stat_table(cal, pc),
                                                        validation=FF.stat_table(val, pv))
                row[key] = dict(s=s, calibration={k: v for k, v in sc.items() if k != 'failed'},
                                validation={k: v for k, v in sv.items() if k != 'failed'},
                                failed=(sc['failed'] + sv['failed'])[:30], failures=sc['failures'] + sv['failures'],
                                survives=sc['failures'] + sv['failures'] == 0,
                                lumaOnlyWorst=_luma_worst(cal + val, pc + pv))
            row['lsObjective'] = float(np.sqrt(r.fun))
            row['minimaxObjective'] = float(min(vals + [r2.fun]))
            res['forms'][form] = row
            print(f"{ep:15s} {form:8s} s ls {s_ls:.4f} mm {s_mm:.4f}  fail {row['ls']['failures']} / "
                  f"{row['minimax']['failures']}  worst cal {row['minimax']['calibration']['worstMeasured']:.2f} "
                  f"val {row['minimax']['validation']['worstMeasured']:.2f}  ls rms {row['lsObjective']:.3f}",
                  flush=True)
        raw = json.dumps(tables, sort_keys=True, default=float).encode()
        scratch = C.SCRATCH / 'knee' / f'{family}__{ep}.json.gz'
        scratch.parent.mkdir(parents=True, exist_ok=True)
        scratch.write_bytes(gzip.compress(raw, mtime=0))
        res['statisticsTable'] = dict(path=str(scratch), sha256=hashlib.sha256(raw).hexdigest())
        out[ep] = res
        C.save(C.HERE / 'knee' / f'{family}__{ep}.json', res)
    return out


def _luma_worst(cells, preds):
    """Descriptive: the worst |luma(pred) - luma(native)| over the region statistics (luma of the per-channel
    medians), which separates a structure miss from a chroma miss."""
    worst = 0.0
    for c, pr in zip(cells, preds):
        sp, sn = C.stats(c, pr), C.native_stats(c)
        names = {k.rsplit('|', 1)[0] for k in sn}
        for n in names:
            a = sum(w * sp[f'{n}|{ch}'] for w, ch in zip(C.W709, 'RGB'))
            b = sum(w * sn[f'{n}|{ch}'] for w, ch in zip(C.W709, 'RGB'))
            worst = max(worst, abs(a - b))
    return worst


if __name__ == '__main__':
    run(*(sys.argv[1:] or ['LT']))
