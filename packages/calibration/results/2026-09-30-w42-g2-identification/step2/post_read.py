"""W42 G2 step 2 — POST-READ DESCRIPTION, asked for by the parent after the negative (2026-10-01). Neither reading is
a fit for adoption, neither was declared before the read, and neither changes any verdict of verdicts.txt.

1. F4, the shipped baseline (declaration `rejectedNulls`: "F4, vitrea's shipped form T(group) + b (K * B - group), is
   the baseline the referees read against"), on the same calibration and validation region statistics:
   - F4 / native T: the shipped body's structure re-anchored at native T. Per pixel, in linear light,
         y = dec(T_c(g)) + shipped(x) - shipped_uniform(g)
     where shipped(x) is the shipped WebGPU body (gate/rehearsal/body.py, memo B's float64 replica: the linear-light
     two-sided mix of the device-px body tap and the heavy tap or scatter level, the depth ramp, the group-level tone
     solve, body chroma retention), g the shipped tone abscissa of the group (active: the source; receded: the
     silhouette), and shipped_uniform(g) the shipped body over a uniform backdrop with that abscissa. A constant
     backdrop therefore reads T(g) exactly, as every declared family does. Every constant is SHIPPED: resolved.json
     (the rehearsal's resolution of the macOS 27 documents); the bed's spans the canonical bed lacks (64, 80, and
     the offset shapes' own spans) take resolve.ts's own component law from the same document constants. Nothing is
     fitted. The lens is not applied (every deep mask lies beyond the refraction band).
   - F4 as shipped: the same body with its own landed tone (no native T), i.e. what ships.
   - LT at its least-squares point (fits/main), family E through candidate 2's chroma form with the per-channel knee
     and its scale refitted by least squares at that point.
   Per endpoint: pooled rms (calibration, validation), worst, failures; and per stratum (bed family and pitch or
   patch size) and per span.
2. The anatomy of LT's failures at its least-squares point: (a) memo E §2e's 1x aliasing cells (1x rrect-md, -ml,
   -lg at pitch 4-8, "which no Gaussian closes"); (b) the remaining rrect-ml and rrect-lg cells, both scales (memo C's
   U7 span growth); (c) everything else. Worst and count per class; the signed residual of the matched cells by span
   (described, no span law fitted).

    python3.12 -B post_read.py     -> post-read/f4-baseline.json, post-read/anatomy.json, post-read/post-read.md
"""
import functools
import gzip
import hashlib
import importlib.util
import json
import math
import time
from collections import defaultdict

import numpy as np
from scipy import optimize

import common as C
import knee_chroma as KC

F = C.F
OUT = C.HERE / 'post-read'
REH = C.DECL / 'gate' / 'rehearsal'
EP_B = {'light-rest': 'light-active', 'light-inactive': 'light-receded', 'dark-rest': 'dark-active',
        'dark-inactive': 'dark-receded'}


def _body():
    spec = importlib.util.spec_from_file_location('w42_rehearsal_body', REH / 'body.py')
    B = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(B)

    @functools.lru_cache(maxsize=None)
    def backdrop(bg, scale):
        return C.G.render_background(C.G.BACKGROUNDS[bg], scale).astype(np.float64) / 255.0

    def surfaces(component):
        cx, cy, w, h, r = C.G.shape_frame(component)
        return [(component, cx, cy, w, h, r)]
    B.backdrop = backdrop
    B.surfaces = surfaces
    B.chain.cache_clear()
    return B


def component_law(e, sc, w, h):
    """resolve.ts lines 128-143, from the same document constants (no new number)."""
    clamp01 = lambda x: min(max(x, 0.0), 1.0)
    span = min(w, h)
    lo, hi = e['sizeSpanMin'], e['sizeSpanMax']
    thickT = clamp01((span - lo) / max(hi - lo, 1e-6))
    sizeThick = thickT * thickT * (3 - 2 * thickT)
    sizeK = clamp01(sizeThick * e['fold'])
    deepT = clamp01((span - lo) / max(sc['spanTop'] - lo, 1e-6))
    kDeep = clamp01(sc['floor'] + (1 - sc['floor']) * deepT * deepT * (3 - 2 * deepT) + sc['thickLift'] * sizeThick)
    farT = clamp01((span - hi) / max(sc['spanTop'] - hi, 1e-6))
    farS = farT * farT * (3 - 2 * farT)
    rampStart = sc['startThin'] + (sc['startThick'] - sc['startThin']) * sizeThick + (sc['startFar'] - sc['startThick']) * farS
    gainEff = sc['gainNear'] + (sc['gainFar'] - sc['gainNear']) * farS
    lod = min(max(sc['bodyChainLod'] + math.log2(max(gainEff, 1e-4)), 0), sc['plan']['maxLod'])
    return dict(span=span, sizeThick=sizeThick, sizeK=sizeK, kDeep=kDeep, sDeep=1 - kDeep, farS=farS,
                rampStart=rampStart, gainEff=gainEff, scatterLod=lod,
                sizedAlpha=e['tintAlpha'] + e['sizeOcclusionGain'] * sizeK * (1 - e['tintAlpha']))


def check_law(B):
    """The port reproduces every component resolved.json carries."""
    worst = 0.0
    sizes = {'capsule': (120, 44), 'rrect-sm': (64, 32), 'rrect-md': (160, 96), 'rrect-ml': (224, 128),
             'rrect-lg': (280, 160)}
    for ep, e in B.RES.items():
        for s, sc in e['perScale'].items():
            for name, (w, h) in sizes.items():
                ref, got = sc['components'][name], component_law(e, sc, w, h)
                worst = max(worst, max(abs(ref[k] - got[k]) for k in ref))
    return worst


def register(B, comps):
    for e in B.RES.values():
        for sc in e['perScale'].values():
            for name in comps:
                cx, cy, w, h, r = C.G.shape_frame(name)
                sc['components'].setdefault(name, component_law(e, sc, w, h))


def f4_cell(B, c):
    """(F4 / native T, F4 as shipped), codes on c.mask, (n, 3)."""
    ep = EP_B[c.ep]
    e = B.RES[ep]
    sc = e['perScale'][f'{c.scale}x']
    bg = c.bg_spec['name'] if 'name' in c.bg_spec else None
    bt, _ = B.shipped_argument(ep, c.scale, c._bgname, c.comp_name, lensed=False)
    fl = B.field(c.comp_name, c.scale)
    img = B.backdrop(c._bgname, c.scale)
    surf = fl.surfaces[0]
    comp = sc['components'][surf[0]]
    st = B.silhouette_stat(img, c.scale, surf) if e['abscissa'] != 'source(default)' else B.source_stat(img)
    s = B.solve(e, comp['sizeK'], st['level'], st['linLum'])
    m = c.mask
    n = int(m.sum())
    full = lambda d: {k: np.full(n, float(v)) for k, v in d.items()}
    col = B.compose(e, bt[m], full(s), np.full(3, st['linLum']))
    lvl = st['level']
    s_ref = B.solve(e, comp['sizeK'], lvl, lvl)
    col_ref = B.compose(e, np.full((1, 3), lvl), {k: np.full(1, float(v)) for k, v in s_ref.items()},
                        np.full(3, lvl))[0]
    g = 255.0 * float(B.enc(lvl))
    Tg = np.array([float(Tc(np.array([g]))[0]) for Tc in c.Tc])
    native = 255.0 * B.enc(B.dec(Tg / 255.0)[None, :] + col - col_ref[None, :])
    shipped = 255.0 * B.enc(col)
    return native, shipped, dict(g=g, level=lvl, linLum=st['linLum'])


def lt_e_preds(ep, cells_e, p):
    """LT at its least-squares point on family E, per-channel knee, the scale refitted by least squares there."""
    fam = F.Family()
    q = KC.g_coeffs(ep)
    args = [KC.argument(c, fam, p, 'channel') for c in cells_e]
    cal = [i for i, c in enumerate(cells_e) if c.role == 'calibration']
    ys = [cells_e[i].y[cells_e[i].mask].astype(float) for i in cal]
    f = lambda s: float(np.mean([np.mean((KC.output(cells_e[i], args[i], s, q) - y) ** 2) for i, y in zip(cal, ys)]))
    s = float(optimize.minimize_scalar(f, bounds=KC.S_BOUNDS, method='bounded', options=dict(xatol=1e-5)).x)
    return [KC.output(c, a, s, q) for c, a in zip(cells_e, args)], s


def stratum(c):
    g = c.geometry
    if c.letter == 'A':
        return 'uniform (A)'
    if c.letter in ('B', "B'"):
        return f'checker pitch {g["pitch"]} ({c.letter})'
    if c.letter == 'C':
        return 'impulse grid (C)' if g.get('patchesInCanvas') == 'grid' else f'patch {g["patchSize"]} pt (C)'
    if c.letter == 'D':
        return 'step (D)'
    if c.letter == 'E':
        return 'colour (E)'
    return c.letter


def rows_of(c, pred):
    return C.score_cell(c, pred)


def summarize_group(items):
    """items: [(cell, rows, rms)] -> pooled rms, worst measured, failures, statistics."""
    if not items:
        return None
    rms = [r for _, _, r in items]
    worst, fails, n = 0.0, 0, 0
    for _, rows, _ in items:
        for k, nv, pv, err, bound, st, failed in rows:
            n += 1
            fails += int(failed)
            if st == 'measured':
                worst = max(worst, abs(err))
    return dict(cells=len(items), pooled=float(np.sqrt(np.mean(np.square(rms)))), worst=worst, failures=fails,
                statistics=n)


def main():
    t0 = time.time()
    OUT.mkdir(exist_ok=True)
    B = _body()
    law = check_law(B)
    assert law < 1e-9, f'component law port differs from resolved.json by {law}'
    comps = set()
    res = dict(schema='w42-g2-step2-post-read-f4-1', status='POST-READ DESCRIPTION: not declared before the read, '
               'not a fit for adoption, changes no verdict', componentLawPortCheck=law, endpoints={})
    anatomy = dict(schema='w42-g2-step2-post-read-anatomy-1', status=res['status'], endpoints={})
    for ep in C.EPS:
        cells = []
        for sc in (2, 1):
            for roles in (('calibration',), ('validation',)):
                cells += C.cells(ep, sc, roles, letters=('A', 'B', "B'", 'C', 'D', 'E'), kernel='n')
        for c in cells:
            cid = c.bed_id
            c._bgname = next(s['background'] for s in C.IB.SCENES if s['id'] == C.sid(cid, ep))
            comps.add(c.comp_name)
        register(B, comps)
        fit = json.loads((C.HERE / 'fits' / 'main' / f'LT__{ep}__n.json').read_text())
        p = {k.split('@')[0]: v for k, v in fit['ls']['params'].items()}
        p['lam'] = fit['ls']['lam'][ep]
        p = F.expand(F.Family(), p)
        cells_e = [c for c in cells if c.letter == 'E']
        lt_e, s_e = lt_e_preds(ep, cells_e, p)
        lt_e = dict(zip([c.id for c in cells_e], lt_e))
        groups = {k: defaultdict(list) for k in ('F4 / native T', 'F4 as shipped', 'LT (least squares)')}
        per_cell = {}
        lt_rows_all = {}
        for c in cells:
            nat, shp, info = f4_cell(B, c)
            y = c.y[c.mask].astype(float)
            lt = lt_e[c.id] if c.letter == 'E' else C.render_rgb(c, F.Family(), p)
            preds = {'F4 / native T': nat, 'F4 as shipped': shp, 'LT (least squares)': lt}
            per_cell[c.id] = {}
            for name, pr in preds.items():
                rows = rows_of(c, pr)
                rms = float(np.sqrt(np.mean((pr - y) ** 2)))
                item = (c, rows, rms)
                for key in ('all', f'role:{c.role}', f'stratum:{stratum(c)}', f'span:{int(c.span)}',
                            f'scale:{c.scale}x'):
                    groups[name][key].append(item)
                fails = sum(int(r[6]) for r in rows)
                worst = max([abs(r[3]) for r in rows if r[5] == 'measured'], default=0.0)
                per_cell[c.id][name] = dict(rms=rms, failures=fails, worst=worst, statistics=len(rows))
                if name == 'LT (least squares)':
                    lt_rows_all[c.id] = (c, rows)
            per_cell[c.id]['group'] = info
        E = {name: {k: summarize_group(v) for k, v in g.items()} for name, g in groups.items()}
        res['endpoints'][ep] = dict(models=E, perCell=per_cell, ltParams=dict(k=p['k'], lam=p['lam']),
                                    ltChromaScaleLS=s_e)
        anatomy['endpoints'][ep] = classify(lt_rows_all)
        print(ep, f'{time.time() - t0:.0f}s', {n: (round(E[n]['all']['pooled'], 3), round(E[n]['all']['worst'], 2),
                                                 E[n]['all']['failures']) for n in E}, flush=True)
    C.save(OUT / 'f4-baseline.json', res)
    C.save(OUT / 'anatomy.json', anatomy)
    write_md(res, anatomy)


CLASS_A = {('rrect-md', 4), ('rrect-md', 8), ('rrect-ml', 4), ('rrect-ml', 8), ('rrect-lg', 4), ('rrect-lg', 8)}


def klass(c):
    base = c.comp_name.split('-o')[0] if c.comp_name.startswith('rrect') else c.comp_name
    pitch = c.geometry.get('pitch')
    if c.scale == 1 and (base, pitch) in CLASS_A:
        return 'a'
    if base in ('rrect-ml', 'rrect-lg'):
        return 'b'
    return 'c'


def classify(lt_rows):
    out = {}
    for cls in 'abc':
        sel = [(c, rows) for c, rows in lt_rows.values() if klass(c) == cls]
        fails = sum(int(r[6]) for _, rows in sel for r in rows)
        stats = sum(len(rows) for _, rows in sel)
        worst, at = 0.0, None
        for c, rows in sel:
            for r in rows:
                if r[5] == 'measured' and abs(r[3]) > worst:
                    worst, at = abs(r[3]), f'{c.id}:{r[0]}'
        out[cls] = dict(cells=sorted(c.id for c, _ in sel), failures=fails, statistics=stats, worst=worst, worstAt=at,
                        failingCells=sum(1 for _, rows in sel if any(r[6] for r in rows)))
    # the span trend: matched cells, signed residual (prediction - native) of their pooled statistics, mean of
    # channels, by span
    trend = defaultdict(dict)
    for c, rows in lt_rows.values():
        if c.scale != 2:
            continue
        bid = c.bed_id
        key = None
        if bid.startswith('bp-p1-c32-'):
            key = 'P1 0/255 pitch 32'
        elif bid.startswith('bp-p1-c64-'):
            key = 'P1 0/255 pitch 64'
        elif bid.startswith('bp-p1-c8-'):
            key = 'P1 0/255 pitch 8'
        elif bid.startswith('b-p5-c16-'):
            key = 'P5 144/240 pitch 16'
        elif bid.startswith('b-p5-c64-'):
            key = 'P5 144/240 pitch 64'
        elif bid.startswith('b-p3-c16-'):
            key = 'P3 96/160 pitch 16'
        elif bid in ('d-d0-lohi-capsule-button', 'd-d0-lohi-rrect-md', 'd-d0-lohi-rrect-lg', 'd-d0-lohi-rrect-sm'):
            key = 'step 48|208 at the centre'
        elif bid.startswith('c-impulse-'):
            key = 'impulse 255 on 0, spacing 64'
        if key is None:
            continue
        pooled = defaultdict(list)
        for k, nv, pv, err, bound, st, failed in rows:
            name = k.rsplit('|', 1)[0]
            if name in ('knee-cores', 'far-cores', 'plateau-lo', 'plateau-hi') and st == 'measured':
                pooled[name].append(err)
        if key.startswith('impulse'):
            ring = defaultdict(list)
            for k, nv, pv, err, bound, st, failed in rows:
                name = k.rsplit('|', 1)[0]
                if st == 'measured' and ':' in name:
                    ring[name.split(':')[1]].append(err)
            pooled = {r: v for r, v in ring.items()}
        worst = max([abs(r[3]) for r in rows if r[5] == 'measured'], default=0.0)
        trend[key][int(c.span)] = dict(signed={n: round(float(np.mean(v)), 2) for n, v in sorted(pooled.items())},
                                       worst=round(worst, 2), cell=c.id)
    return dict(classes=out, spanTrend={k: dict(sorted(v.items())) for k, v in trend.items()})


def write_md(res, anatomy):
    L = ['# W42 G2 step 2 — POST-READ DESCRIPTION: F4 against LT, and the anatomy of LT\'s misses', '',
         '**Asked for by the parent after the negative; not declared before the read; not a fit for adoption; changes '
         'no verdict of `verdicts.txt`.** Generated by `post_read.py`. Codes; pooled = rms of per-cell rms over the '
         'cells (all channels, deep mask); worst = largest measured region-statistic miss; failures = statistics '
         'beyond max(1, bar) or a rail deficit.', '',
         'F4 / native T: the shipped body\'s structure re-anchored at native T (y = T(g) + shipped(x) − shipped over '
         'a uniform backdrop at the group\'s abscissa g; every constant shipped, nothing fitted). F4 as shipped: the '
         'same body with its own landed tone. LT: the least-squares point of `fits/main` (family E: the per-channel '
         'knee, its chroma scale refitted by least squares at that point).', '']
    names = ('F4 / native T', 'F4 as shipped', 'LT (least squares)')
    for ep, E in res['endpoints'].items():
        M = E['models']
        L += [f'## {ep} ({C.EP_NAME[ep]}); LT k {E["ltParams"]["k"]:.3f}, λ {E["ltParams"]["lam"]:.3f}, E chroma scale '
              f'{E["ltChromaScaleLS"]:.3f}', '',
              '| model | pooled cal | pooled val | worst | failures / statistics |', '| --- | --- | --- | --- | --- |']
        for n in names:
            a, cal, val = M[n]['all'], M[n].get('role:calibration'), M[n].get('role:validation')
            L.append(f"| {n} | {cal['pooled']:.2f} | {val['pooled']:.2f} | {a['worst']:.2f} | {a['failures']} / "
                     f"{a['statistics']} |")
        for axis in ('stratum', 'span'):
            keys = sorted({k for k in M[names[0]] if k.startswith(axis + ':')},
                          key=lambda k: (int(k.split(':')[1]) if axis == 'span' else k))
            L += ['', f'| {axis} | cells | ' + ' | '.join(f'{n}: pooled / worst / fails' for n in names) + ' |',
                  '| --- | --- | ' + ' | '.join('---' for _ in names) + ' |']
            for k in keys:
                cells_n = M[names[0]][k]['cells']
                L.append(f"| {k.split(':', 1)[1]} | {cells_n} | " + ' | '.join(
                    f"{M[n][k]['pooled']:.2f} / {M[n][k]['worst']:.1f} / {M[n][k]['failures']}" for n in names) + ' |')
        L.append('')
        an = anatomy['endpoints'][ep]
        L += ['LT\'s failures (least squares) by class: (a) memo E §2e\'s 1x aliasing cells; (b) the other rrect-ml / '
              'rrect-lg cells; (c) the rest.', '', '| class | cells | failing cells | failures / statistics | worst | at |',
              '| --- | --- | --- | --- | --- | --- |']
        for cls, d in an['classes'].items():
            L.append(f"| ({cls}) | {len(d['cells'])} | {d['failingCells']} | {d['failures']} / {d['statistics']} | "
                     f"{d['worst']:.2f} | {d['worstAt']} |")
        L += ['', 'Span trend (2x matched cells; LT\'s signed residual, prediction − native, of the pooled statistics, '
              'mean over channels; worst |miss| of the cell):', '']
        for key, by in an['spanTrend'].items():
            L.append(f"- {key}: " + '; '.join(
                f"s {s}: " + ', '.join(f'{n} {v:+.2f}' for n, v in d['signed'].items()) + f" (worst {d['worst']})"
                for s, d in by.items()))
        L.append('')
    (OUT / 'post-read.md').write_text('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
