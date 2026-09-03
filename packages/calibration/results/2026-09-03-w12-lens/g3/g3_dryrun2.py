"""G3 reading 9: the dry run redone at vitrea's OWN level and transmission, and the fit under it.

The G3 landing failed stop 3 (the referee's `g3-verdict.md`): the three 2x GPU texture rows fell.
The verdict names the two normalisations section 8's dry run rests on — it evaluated every candidate
at the REFERENCE's level and transmission, while the runtime renders at vitrea's own, and it left
the rim band untouched while the runtime's lens reads the body at the refracted position. This
script removes both normalisations.

  1. vitrea's own (a, t) are read from vitrea's own capture on `main` (the omega-0.8 round) by
     regressing its interior on the law `main` actually renders, and then held while only the body
     structure is swapped for the candidate's. Nothing is fitted to the reference.
  2. the band is predicted rather than skipped: a band pixel at depth u is the body sampled at the
     refracted position q - D(u)*n, with D the landed G2 law, which is how the GPU tier renders it.
     The prediction is validated against the one capture that exists for a candidate (G3's own).

`interiorStdDev` is the compare's reading of retained structure over the NATIVE silhouette bounded
to the component region (`cli/measure.ts`: "One mask for both sides, and it is the NATIVE
silhouette"); the replica here is the geometric mask u > 0, checked against the matrices' own rows.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, f'{HERE}/../g1')
import numpy as np
from scipy.ndimage import map_coordinates

from g3lib import *  # noqa: F401,F403
from w11lib import ssim_map, luma_enc, lin_to_srgb

T = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'
CAPS = {'main': f'{T}/web-captures-g2b', 'g3': f'{T}/web-captures-g3'}
MATRIX = {'main': f'{T}/matrix-g2b.json', 'g3': f'{T}/matrix-g3.json'}
PROF = {1: 'apple-macos-26.5-1x-light-standard', 2: 'apple-macos-26.5-2x-light-standard'}
CELLS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg']
BIG = ['rrect-md', 'rrect-ml', 'rrect-lg']
R = 5  # the SSIM map's 'valid' margin

# the landed law on `main` (packages/renderer-webgpu/src/material.ts)
MAIN = dict(blur_sigma=1.25, gain_max=8.0, floor=0.4, span_max=256.0)
LENS = dict(amountPerSpan=0.8, amountMax=60.0, refractionGain=0.745,
            heightPerSpan=0.25, heightMax=20.0, extentGain=1.337, profileExponent=3.69)


def native(scene, scale):
    return load_rgb(f'{ROOT}/apps/reference-apple/fixtures/{PROF[scale]}/{scene}.png')


def webcap(scene, scale, which='main'):
    return load_rgb(f'{CAPS[which]}/{PROF[scale]}/{scene}/{scene}__webgpu.png')


def k_main(span):
    return MAIN['floor'] + (1 - MAIN['floor']) * smoothstep(32, MAIN['span_max'], span)


def law_sigmas(cand, span, scale):
    """(sigma_sharp, sigma_heavy) in CSS px and the mixing weight, for one candidate at one scale."""
    dk = cand['dk'] * (scale - 1)
    k = min(max(k_main(span) + dk, 0.0), 1.0)
    ss = MAIN['blur_sigma'] / (scale if cand['sharp_device'] else 1)
    sh = MAIN['blur_sigma'] * MAIN['gain_max'] / (scale if cand['heavy_device'] else 1)
    return ss, sh, k


def geometry(comp, scale):
    W, H = CANVAS[0] * scale, CANVAS[1] * scale
    w, h, r = COMP[comp]
    d = sdf_rrect(W, H, 160 * scale, 100 * scale, w * scale, h * scale, r * scale)
    gy, gx = np.gradient(d)
    n = np.sqrt(gx * gx + gy * gy) + 1e-9
    ys, xs = np.mgrid[0:H, 0:W]
    return -d / scale, gx / n, gy / n, xs, ys


def lens_D(u, span):
    S = LENS['refractionGain'] * min(LENS['amountPerSpan'] * span, LENS['amountMax'])
    L = LENS['extentGain'] * min(LENS['heightPerSpan'] * span, LENS['heightMax'])
    return S * np.clip(1 - u / L, 0, 1) ** LENS['profileExponent']


def body_field(comp, scale, ss, sh, k, refracted):
    """The body's structure over the whole silhouette: the two-tap mix of the plate, sampled at the
    pixel itself or at the refracted position q - D(u)*n (the GPU tier's own read, W12 G2)."""
    P = plate('checkerboard', scale)
    X = structure_gpu(P, 'checkerboard', scale, ss, sh, k)
    if not refracted:
        return X
    u, nx, ny, xs, ys = geometry(comp, scale)
    D = lens_D(np.clip(u, 0, None), SPAN[comp]) * scale
    return map_coordinates(X, [ys - ny * D, xs - nx * D], order=1, mode='nearest')


out = dict(main_law=MAIN, lens=LENS, cells={}, instrument={}, fit_t_held={}, band={})

# ---------------------------------------------------------------- 0. the interiorStdDev replica
mx = {}
for tag, path in MATRIX.items():
    for c in json.load(open(path))['cells']:
        key = c['key']
        if key['web']['renderer'] != 'webgpu' or not key['sceneId'].startswith('checkerboard__'):
            continue
        kk = (tag, key['profileKey'], key['sceneId'])
        if kk not in mx or c['capturedAt'] > mx[kk]['capturedAt']:
            mx[kk] = c
print('== instrument: interiorStdDev over the u > 0 silhouette replica, against the matrices\' rows')
for scale in (1, 2):
    for comp in CELLS:
        scene = f'checkerboard__{comp}__rest'
        m = depth(comp, scale) > 0
        nat = luma_lin(native(scene, scale))
        a = luma_lin(webcap(scene, scale, 'main'))
        row = dict(native=float(nat[m].std()), main=float(a[m].std()))
        cm = mx.get(('main', PROF[scale], scene))
        if cm:
            row['matrix_native'] = cm['material']['interiorStdDevNative']['value']
            row['matrix_main'] = cm['material']['interiorStdDevWeb']['value']
        cg = mx.get(('g3', PROF[scale], scene))
        if cg and os.path.exists(f'{CAPS["g3"]}/{PROF[scale]}/{scene}/{scene}__webgpu.png'):
            b = luma_lin(webcap(scene, scale, 'g3'))
            row['g3'] = float(b[m].std())
            row['matrix_g3'] = cg['material']['interiorStdDevWeb']['value']
        out['instrument'][f'{comp}@{scale}x'] = row
        if 'matrix_main' in row:
            print(f'   {scale}x {comp:15s} native {row["native"]:.4f}/{row["matrix_native"]:.4f}  '
                  f'main {row["main"]:.4f}/{row["matrix_main"]:.4f}'
                  + (f'  g3 {row["g3"]:.4f}/{row["matrix_g3"]:.4f}' if 'g3' in row else ''))

# ---------------------------------------------------------------- 1. vitrea's own (a, t)
print('\n== vitrea\'s own level and transmission, read from its own capture on `main`')
AT = {}
for scale in (1, 2):
    for comp in CELLS:
        scene = f'checkerboard__{comp}__rest'
        box = box_mask(comp, scale)
        Yv = luma_lin(webcap(scene, scale, 'main'))
        ss, sh, k = law_sigmas(dict(dk=0.0, sharp_device=False, heavy_device=False), SPAN[comp], scale)
        X = structure_gpu(plate('checkerboard', scale), 'checkerboard', scale, ss, sh, k)
        coef, rms, r2 = lstsq_cols(Yv[box], [X[box]])
        Yn = luma_lin(native(scene, scale))
        cn, rn, r2n = lstsq_cols(Yn[box], [X[box]])
        AT[(comp, scale)] = (float(coef[0]), float(coef[1]))
        print(f'   {scale}x {comp:15s} a {coef[0]:.4f} t {coef[1]:.4f} (r² {r2:.3f}) | '
              f'the reference on the same column: a {cn[0]:.4f} t {cn[1]:.4f}  '
              f'ratio t_vitrea/t_ref {coef[1] / cn[1]:.3f}')
        out['cells'].setdefault(f'{comp}@{scale}x', {})['vitrea_at'] = dict(a=coef[0], t=coef[1], r2=r2)
        out['cells'][f'{comp}@{scale}x']['reference_at'] = dict(a=float(cn[0]), t=float(cn[1]))
        out['cells'][f'{comp}@{scale}x']['t_ratio'] = float(coef[1] / cn[1])

# ------------------------------------------------- 1b. is the nominal law a model of what is rendered?
# The retained structure a law predicts is t x std(structure). Dividing the capture's own interior
# std by the model column's std gives the transmission the runtime must be applying if the nominal
# law is what it renders. One number per span that holds at BOTH scales would validate the model;
# `main` is the control (its law is the landed one) and the G3 capture is the test.
print('\n== retained-structure check: t implied by std(capture) / std(nominal model column), on the box')
imp = {}
for scale in (1, 2):
    for comp in CELLS:
        scene = f'checkerboard__{comp}__rest'
        m = box_mask(comp, scale)
        row = {}
        for which, cand in (('main', dict(dk=0.0, sharp_device=False, heavy_device=False)),
                            ('g3', dict(dk=0.35, sharp_device=True, heavy_device=True))):
            f = f'{CAPS[which]}/{PROF[scale]}/{scene}/{scene}__webgpu.png'
            if not os.path.exists(f):
                continue
            Y = luma_lin(webcap(scene, scale, which))
            ss, sh, k = law_sigmas(cand, SPAN[comp], scale)
            X = structure_gpu(plate('checkerboard', scale), 'checkerboard', scale, ss, sh, k)
            row[which] = dict(std_capture=float(Y[m].std()), std_model=float(X[m].std()),
                              t_implied=float(Y[m].std() / X[m].std()),
                              sigma_sharp=ss, sigma_heavy=sh, k=k)
        imp[f'{comp}@{scale}x'] = row
        print(f'   {scale}x {comp:15s} main std {row["main"]["std_capture"]:.4f} / model '
              f'{row["main"]["std_model"]:.4f} = t {row["main"]["t_implied"]:.3f}'
              + (f'   |  G3 std {row["g3"]["std_capture"]:.4f} / model {row["g3"]["std_model"]:.4f} '
                 f'= t {row["g3"]["t_implied"]:.3f}' if 'g3' in row else ''))
out['retained_structure_check'] = imp

# ---------------------------------------------------------------- 2. the corrected dry run
CANDS = {'main (the landed law)': dict(dk=0.0, sharp_device=False, heavy_device=False)}
for dk in (0.0, 0.10, 0.20, 0.35):
    CANDS[f'(a) both σ device, Δk {dk:.2f}'] = dict(dk=dk, sharp_device=True, heavy_device=True)
for dk in (0.0, 0.10, 0.20):
    CANDS[f'(b) heavy σ device, Δk {dk:.2f}'] = dict(dk=dk, sharp_device=False, heavy_device=True)

print('\n== the corrected dry run: vitrea\'s own (a, t) held, only the body structure swapped')
print('   (box = the 5.41 interior box; sil = the u > 0 silhouette the compare measures)')
for scale in (2, 1):
    for comp in CELLS:
        scene = f'checkerboard__{comp}__rest'
        nat = native(scene, scale)
        cap = webcap(scene, scale, 'main')
        Yv = luma_lin(cap)
        box = box_mask(comp, scale)
        sil = depth(comp, scale) > 0
        a_v, t_v = AT[(comp, scale)]
        base_ssim = ssim_map(luma_enc(nat), luma_enc(cap))
        bx, sx = box[R:-R, R:-R], sil[R:-R, R:-R]
        rec = dict(native_std_box=float(luma_lin(nat)[box].std()),
                   native_std_sil=float(luma_lin(nat)[sil].std()),
                   main_std_box=float(Yv[box].std()), main_std_sil=float(Yv[sil].std()),
                   main_ssim_box=float(base_ssim[bx].mean()), main_ssim_sil=float(base_ssim[sx].mean()),
                   main_ssim_whole=float(base_ssim.mean()), candidates={})
        for name, cand in CANDS.items():
            ss, sh, k = law_sigmas(cand, SPAN[comp], scale)
            Xr = body_field(comp, scale, ss, sh, k, refracted=True)
            pred = a_v + t_v * Xr
            w2 = cap.copy()
            ratio = np.clip(pred[sil] / np.maximum(Yv[sil], 1e-4), 0, 10)
            w2[sil] = lin_to_srgb(srgb_to_lin(cap[sil]) * ratio[:, None])
            sm = ssim_map(luma_enc(nat), luma_enc(w2))
            rec['candidates'][name] = dict(
                sigma_sharp=ss, sigma_heavy=sh, k=k,
                std_box=float(pred[box].std()), std_sil=float(pred[sil].std()),
                ssim_box=float(sm[bx].mean()), ssim_sil=float(sm[sx].mean()),
                ssim_whole=float(sm.mean()))
        out['cells'][f'{comp}@{scale}x'].update(rec)
        if comp in BIG or scale == 2:
            print(f'   {scale}x {comp:15s} native std box {rec["native_std_box"]:.4f} sil '
                  f'{rec["native_std_sil"]:.4f} | main std box {rec["main_std_box"]:.4f} sil '
                  f'{rec["main_std_sil"]:.4f} ssim box {rec["main_ssim_box"]:.4f} whole '
                  f'{rec["main_ssim_whole"]:.4f}')
            for name, c in rec['candidates'].items():
                print(f'        {name:28s} std box {c["std_box"]:.4f} sil {c["std_sil"]:.4f} | '
                      f'ssim box {c["ssim_box"]:.4f} sil {c["ssim_sil"]:.4f} whole {c["ssim_whole"]:.4f}')

# ---------------------------------------------------------------- 3. validation against the G3 capture
print('\n== validation: the G3 candidate ((a) Δk 0.35) predicted, against the G3 capture measured')
val = {}
for comp in CELLS:
    scene = f'checkerboard__{comp}__rest'
    p = f'{CAPS["g3"]}/{PROF[2]}/{scene}/{scene}__webgpu.png'
    if not os.path.exists(p):
        continue
    nat = native(scene, 2)
    g3 = webcap(scene, 2, 'g3')
    box, sil = box_mask(comp, 2), depth(comp, 2) > 0
    sm = ssim_map(luma_enc(nat), luma_enc(g3))
    pred = out['cells'][f'{comp}@2x']['candidates']['(a) both σ device, Δk 0.35']
    val[comp] = dict(
        measured=dict(std_box=float(luma_lin(g3)[box].std()), std_sil=float(luma_lin(g3)[sil].std()),
                      ssim_box=float(sm[box[R:-R, R:-R]].mean()),
                      ssim_sil=float(sm[sil[R:-R, R:-R]].mean()), ssim_whole=float(sm.mean())),
        predicted=dict(std_box=pred['std_box'], std_sil=pred['std_sil'], ssim_box=pred['ssim_box'],
                       ssim_sil=pred['ssim_sil'], ssim_whole=pred['ssim_whole']))
    m, q = val[comp]['measured'], val[comp]['predicted']
    print(f'   {comp:15s} std sil {q["std_sil"]:.4f} vs {m["std_sil"]:.4f} | '
          f'ssim box {q["ssim_box"]:.4f} vs {m["ssim_box"]:.4f} | '
          f'whole {q["ssim_whole"]:.4f} vs {m["ssim_whole"]:.4f}')
out['validation_vs_g3_capture'] = val

# ---------------------------------------------------------------- 4. the band split of the G3 capture
print('\n== where the measured G3 capture\'s loss sits (the referee\'s split, reproduced)')
for comp in BIG:
    scene = f'checkerboard__{comp}__rest'
    nat = native(scene, 2)
    a = webcap(scene, 2, 'main')
    b = webcap(scene, 2, 'g3')
    ma = ssim_map(luma_enc(nat), luma_enc(a))
    mb = ssim_map(luma_enc(nat), luma_enc(b))
    u = depth(comp, 2)[R:-R, R:-R]
    box = box_mask(comp, 2)[R:-R, R:-R]
    regions = [('whole', np.ones_like(box)), ('box', box), ('band<24', (u >= 0) & (u < 24) & ~box),
               ('outside', u < 0)]
    rec = {}
    tot = mb.mean() - ma.mean()
    for nm, mk in regions:
        d = float(mb[mk].mean() - ma[mk].mean())
        share = float(mk.sum() * d / (mb.size * tot)) if tot != 0 else float('nan')
        rec[nm] = dict(n=int(mk.sum()), main=float(ma[mk].mean()), g3=float(mb[mk].mean()),
                       delta=d, share_of_whole_loss=share)
        print(f'   {comp:10s} {nm:9s} n {int(mk.sum()):7d} main {ma[mk].mean():.4f} '
              f'g3 {mb[mk].mean():.4f} Δ {d:+.4f} share of the whole-crop loss {share * 100:5.1f}%')
    out['band'][comp] = rec

# ---------------------------------------------------------------- 5. the probe fit with t held
print('\n== the 2x probe fit with the transmission held at vitrea\'s own (a free, t fixed)')
T_V = {comp: AT[(comp, 2)][1] for comp in CELLS}
print('   t held per span: ' + ', '.join(f'{c} {T_V[c]:.3f}' for c in CELLS))
PITCHES = PITCHES4
DKS = [round(-0.2 + 0.05 * i, 2) for i in range(17)]
fit = {}
for name, cand in (('(a) both σ device', dict(sharp_device=True, heavy_device=True)),
                   ('(b) heavy σ device', dict(sharp_device=False, heavy_device=True))):
    rows = []
    for dk in DKS:
        sse_f = n_f = sse_h = n_h = 0.0
        for comp in CELLS:
            ss, sh, k = law_sigmas(dict(cand, dk=dk), SPAN[comp], 2)
            m = box_mask(comp, 2)
            t = T_V[comp]
            s = 0.0
            n = 0
            for b in PITCHES:
                Y = capture(f'{b}__{comp}__rest', 2)[m]
                X = structure_gpu(plate(b, 2), b, 2, ss, sh, k)[m]
                r = Y - t * X
                r = r - r.mean()          # a free per (cell, scale), pooled over pitches: one mean
                s += float(r @ r)
                n += len(r)
            if comp in FIT_COMPS:
                sse_f += s
                n_f += n
            else:
                sse_h += s
                n_h += n
        rows.append((dk, float(np.sqrt(sse_f / n_f)), float(np.sqrt(sse_h / n_h))))
    best = min(rows, key=lambda r: r[1])
    fit[name] = dict(sweep=rows, best_dk=best[0], rms_fit=best[1], rms_holdout=best[2])
    print(f'   {name:20s} best Δk {best[0]:+.2f}  2x fit {best[1]:.4f}  holdout {best[2]:.4f}')
    print('      sweep: ' + '  '.join(f'{d:+.2f}:{f:.4f}' for d, f, h in rows))
out['fit_t_held'] = fit

write_part('dryrun2', out)
