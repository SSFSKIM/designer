"""G3 reading 10: the response-curve read at both scales — does the transmission itself carry a
scale term the body law cannot supply? (claims 5.34's method, on the two probe beds.)

Section 9.6 item 4 left one question open. vitrea's transmission divided by the reference's is
0.81-0.92 at 2x and 0.93-1.16 at 1x on the same constants, and a body law cannot supply that: it
redistributes structure between two widths at a fixed transmission. But "the reference transmits
more at 2x" and "the reference's kernel is narrower at 2x" produce the same retained structure, and
section 9 could not tell them apart. Two readings separate them:

  the LEVEL law      mean = a + s x backdrop_mean, from the three solids: s is the transmission of
                     the backdrop's *level*, measured with no kernel in it at all (a solid has no
                     structure for a kernel to act on);
  the STRUCTURE t    std(interior) / std(K * plate) over the same box, with K the two-component
                     kernel fitted to that same cell here — the width divided out, so what is left
                     is the amplitude the material passes. This is the quantity section 9 used.

If the level slope is scale-invariant and the structure t is not, the reference passes more of the
backdrop's *variation* at the second scale at a fixed level, which neither a body law nor a plain
alpha can carry. If both are scale-invariant, the whole 2x-vs-1x difference in retained structure is
the kernel's and no transmission term is needed.

Run noise: the same quantities recomputed on each attested run of the two probes (7 runs at 1x, 5 at
2x, the unattested captures of claims 5.53 1 excluded per cell), so every ratio below carries the
spread of the bed it came from.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np

from g3lib import *  # noqa: F401,F403

SOLIDS = ['dark-solid', 'mid-dark-solid', 'light-solid']
STRUCTURED = ['checkerboard', LC16, 'checkerboard-32']
T = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'
VIT = f'{T}/web-captures-g2b'
PROF = {1: 'apple-macos-26.5-1x-light-standard', 2: 'apple-macos-26.5-2x-light-standard'}
SNAP = {1: ('/Users/new/.claude/jobs/5c70e47f/tmp/w9snap-probe-%d', range(1, 8)),
        2: (f'{T}/snap-probe-%d', range(1, 6))}
PROV = {1: f'{ROOT}/packages/calibration/results/2026-09-02-w9-probe/provenance.json',
        2: f'{ROOT}/packages/calibration/results/2026-09-03-w12-lens/probe-2x/provenance.json'}
SS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0]
SH = [2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 14.0]


def vit_path(scene, scale):
    return f'{VIT}/{PROF[scale]}/{scene}/{scene}__webgpu.png'


def read(scene, scale, side, run=None):
    """The probe cell ('ref'), one probe run ('run'), or vitrea's canonical capture ('vitrea')."""
    if side == 'vitrea':
        p = vit_path(scene, scale)
        return luma_lin(load_rgb(p)) if os.path.exists(p) else None
    if side == 'run':
        p = (SNAP[scale][0] % run) + f'/{PROF[scale]}/{scene}.png'
        return luma_lin(load_rgb(p)) if os.path.exists(p) else None
    p = probe_path(scene, scale)
    return luma_lin(load_rgb(p)) if os.path.exists(p) else None


def level_law(get, comp, scale):
    """mean = a + s x backdrop_mean over the three solids; s is the level transmission."""
    xs, ys, pts = [], [], {}
    m = box_mask(comp, scale)
    for b in SOLIDS:
        Y = get(f'{b}__{comp}__rest', scale)
        if Y is None:
            continue
        P = plate(b, scale)
        xs.append(float(P[m].mean()))
        ys.append(float(Y[m].mean()))
        pts[b] = dict(backdrop=xs[-1], interior=ys[-1])
    if len(xs) < 2:
        return None
    A = np.stack([np.ones(len(xs)), np.asarray(xs)], 1)
    coef, *_ = np.linalg.lstsq(A, np.asarray(ys), rcond=None)
    res = np.asarray(ys) - A @ coef
    out = dict(a=float(coef[0]), slope=float(coef[1]), n=len(xs), points=pts,
               rms=float(np.sqrt(np.mean(res ** 2))))
    # where do the structured backdrops of the same mean sit against that line?
    for b in STRUCTURED:
        Y = get(f'{b}__{comp}__rest', scale)
        if Y is None:
            continue
        P = plate(b, scale)
        pred = coef[0] + coef[1] * float(P[m].mean())
        out.setdefault('structured_residual', {})[b] = dict(
            backdrop=float(P[m].mean()), interior=float(Y[m].mean()),
            residual=float(Y[m].mean() - pred))
    return out


def structure_t(get, comp, scale, backdrop):
    """std(interior) / std(K * plate) with K the two-component kernel fitted to this same cell."""
    Y = get(f'{backdrop}__{comp}__rest', scale)
    if Y is None:
        return None
    m = box_mask(comp, scale)
    P = plate(backdrop, scale)
    f = fit_two(Y, P, m, scale, backdrop, sig_sharp=SS, sig_heavy=SH, min_gap=0.5)
    if f['share'] != f['share']:
        return None
    K = structure_gpu(P, backdrop, scale, f['sigma_sharp'], f['sigma_heavy'], f['share'])
    ks = float(K[m].std())
    if ks < 1e-4:
        return None
    return dict(t=float(Y[m].std() / ks), sigma_sharp=f['sigma_sharp'], sigma_heavy=f['sigma_heavy'],
                share=f['share'], fit_t=f['t'], fit_rms=f['rms'],
                interior_std=float(Y[m].std()), kernel_std=ks,
                sigma_ceiling=f.get('sigma_ceiling'),
                at_ceiling=bool(f['sigma_heavy'] == f.get('sigma_ceiling')))


out = dict(solids=SOLIDS, structured=STRUCTURED, cells={}, run_noise={}, ratios={})

print('== the level law, mean = a + s x backdrop_mean, from the three solids')
for side in ('ref', 'vitrea'):
    for scale in SCALES:
        for comp in COMPS:
            law = level_law(lambda s, sc, side=side: read(s, sc, side), comp, scale)
            if law is None:
                continue
            out['cells'].setdefault(f'{comp}@{scale}x', {}).setdefault(side, {})['level'] = law
            sr = law.get('structured_residual', {})
            print(f'   {side:6s} {scale}x {comp:15s} s {law["slope"]:.4f} a {law["a"]:.4f} '
                  f'(n {law["n"]}, rms {law["rms"]:.4f})' +
                  ('  | structured residual ' + ' '.join(f'{k.split("-")[-1]}:{v["residual"]:+.4f}'
                                                         for k, v in sr.items()) if sr else ''))

# The per-cell kernel fit is unidentifiable wherever that pitch is annihilated (claims 5.41 1), and
# then std(K * plate) collapses and the ratio explodes. The transmission is therefore read PRIMARILY
# from the joint fit over the whole pitch axis — one kernel per (comp, scale), its total amplitude
# t = t_sharp + t_heavy, both components mean-preserving, so t is the transmission with the width
# divided out. That is the quantity the probe's pitch axis exists to identify (5.38 3).
print('\n== the structure transmission, joint over the five pitches: t = t_sharp + t_heavy')
JOINT = {}
for scale in SCALES:
    for comp in COMPS:
        m = box_mask(comp, scale)
        Ys = [read(f'{b}__{comp}__rest', scale, 'ref') for b in PITCHES5]
        if any(y is None for y in Ys):
            continue
        Ps = [(b, plate(b, scale)) for b in PITCHES5]
        free = fit_two_joint(Ys, Ps, [m] * len(Ys), scale, sig_sharp=SS, sig_heavy=SH, min_gap=0.5)
        pinned = fit_two_joint(Ys, Ps, [m] * len(Ys), scale, sig_sharp=[1.0], sig_heavy=SH)
        JOINT[(comp, scale)] = dict(free=free, sharp_pinned=pinned)
        out['cells'].setdefault(f'{comp}@{scale}x', {}).setdefault('ref', {})['joint'] = JOINT[(comp, scale)]
        print(f'   ref    {scale}x {comp:15s} free: t {free["t"]:.3f} (σ {free["sigma_sharp"]:.2f}/'
              f'{free["sigma_heavy"]:.1f} k {free["share"]:.2f}, rms {free["rms"]:.4f}) | '
              f'σs pinned 1.0: t {pinned["t"]:.3f} (σh {pinned["sigma_heavy"]:.1f} '
              f'k {pinned["share"]:.2f}, rms {pinned["rms"]:.4f})')
print('   the joint ratio 2x/1x per span: ' + ', '.join(
    f'{c} free {JOINT[(c, 2)]["free"]["t"] / JOINT[(c, 1)]["free"]["t"]:.3f} / pinned '
    f'{JOINT[(c, 2)]["sharp_pinned"]["t"] / JOINT[(c, 1)]["sharp_pinned"]["t"]:.3f}'
    for c in COMPS if (c, 1) in JOINT and (c, 2) in JOINT))

# vitrea has only pitch 16 on the canonical bed, so its transmission is read the way section 9 read
# it: the capture's interior spread divided by the spread of the law vitrea actually renders.
print('\n== vitrea\'s transmission through its own nominal law (section 9\'s reading)')
for scale in SCALES:
    for comp in COMPS:
        Y = read(f'checkerboard__{comp}__rest', scale, 'vitrea')
        if Y is None:
            continue
        m = box_mask(comp, scale)
        k = 0.4 + 0.6 * smoothstep(32, 256.0, SPAN[comp])
        X = structure_gpu(plate('checkerboard', scale), 'checkerboard', scale, 1.25, 10.0, k)
        t = float(Y[m].std() / X[m].std())
        out['cells'].setdefault(f'{comp}@{scale}x', {}).setdefault('vitrea', {})['t_nominal'] = t
        print(f'   vitrea {scale}x {comp:15s} t {t:.3f}')

print('\n== the structure transmission t = std(interior) / std(K * plate), K fitted per cell')
for side in ('ref', 'vitrea'):
    for scale in SCALES:
        for comp in COMPS:
            row = {}
            for b in STRUCTURED:
                r = structure_t(lambda s, sc, side=side: read(s, sc, side), comp, scale, b)
                if r:
                    row[b] = r
            if not row:
                continue
            out['cells'].setdefault(f'{comp}@{scale}x', {}).setdefault(side, {})['structure'] = row
            print(f'   {side:6s} {scale}x {comp:15s} ' + ' | '.join(
                f'{("p16" if b == "checkerboard" else "lc16" if b == LC16 else "p32")} '
                f't {r["t"]:.3f} (σ {r["sigma_sharp"]:.2f}/{r["sigma_heavy"]:.1f} k {r["share"]:.2f}'
                + (', at ceiling' if r['at_ceiling'] else '') + ')' for b, r in row.items()))

print('\n== run noise: the same quantities on every attested run of each probe')
for scale in SCALES:
    prov = json.load(open(PROV[scale]))
    pat, runs = SNAP[scale]
    for comp in COMPS:
        vals = {'slope': [], 'p16': [], 'lc16': [], 'p32': []}
        for run in runs:
            tag = f'probe-{run}'
            def get(scene, sc, run=run, prov=prov, tag=tag):
                cell = prov['cells'].get(scene, {})
                if tag in cell.get('unattestedRuns', []):
                    return None
                return read(scene, sc, 'run', run)
            law = level_law(get, comp, scale)
            if law and law['n'] == 3:
                vals['slope'].append(law['slope'])
            for b, key in ((('checkerboard'), 'p16'), (LC16, 'lc16'), ('checkerboard-32', 'p32')):
                r = structure_t(get, comp, scale, b)
                if r:
                    vals[key].append(r['t'])
        rec = {k: dict(n=len(v), mean=float(np.mean(v)), sd=float(np.std(v, ddof=1)) if len(v) > 1 else 0.0,
                       spread=float(max(v) - min(v)) if v else 0.0) for k, v in vals.items() if v}
        out['run_noise'][f'{comp}@{scale}x'] = rec
        print(f'   {scale}x {comp:15s} ' + ' | '.join(
            f'{k} n{v["n"]} sd {v["sd"]:.4f} spread {v["spread"]:.4f}' for k, v in rec.items()))

print('\n== the ratio 2x / 1x per span, with the run noise beside it')
settled = json.load(open(f'{OUT}/parts/interior.json')).get('settled_noise_bar', {})
for side in ('ref', 'vitrea'):
    for comp in COMPS:
        a = out['cells'].get(f'{comp}@1x', {}).get(side, {})
        b = out['cells'].get(f'{comp}@2x', {}).get(side, {})
        if not a or not b:
            continue
        rec = {}
        if 'level' in a and 'level' in b:
            rec['slope'] = dict(x1=a['level']['slope'], x2=b['level']['slope'],
                                ratio=b['level']['slope'] / a['level']['slope'])
        for key, bd in (('p16', 'checkerboard'), ('lc16', LC16), ('p32', 'checkerboard-32')):
            if bd in a.get('structure', {}) and bd in b.get('structure', {}):
                t1, t2 = a['structure'][bd]['t'], b['structure'][bd]['t']
                rec[key] = dict(x1=t1, x2=t2, ratio=t2 / t1,
                                at_ceiling=a['structure'][bd]['at_ceiling'] or b['structure'][bd]['at_ceiling'])
        out['ratios'].setdefault(side, {})[comp] = rec
        n1 = out['run_noise'].get(f'{comp}@1x', {})
        n2 = out['run_noise'].get(f'{comp}@2x', {})
        line = f'   {side:6s} {comp:15s} '
        for k, v in rec.items():
            sd = max(n1.get(k, {}).get('sd', 0.0), n2.get(k, {}).get('sd', 0.0))
            mark = '*' if v.get('at_ceiling') else ' '
            line += f'{k} {v["x1"]:.3f}→{v["x2"]:.3f} ×{v["ratio"]:.3f}{mark} (±{sd:.3f}) | '
        print(line)
        for cell, s in settled.items():
            if cell.endswith(f'{comp}__rest') and s.get('distance'):
                print(f'          settled cell {cell}: the two states are '
                      f'{s["distance"]["interior_rms"]:.3f} apart in interior RMS')

write_part('transmission', out)
