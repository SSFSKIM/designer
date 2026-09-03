"""G3 reading 1: the interior per scale x span x pitch, and the noise bar on the settled cells.

Single-Gaussian and unconstrained two-component fits of the 5.41 inset interior box over the
backdrop plate, in linear luminance, at both scales; the `lc16` twin beside pitch 16; the instrument
check against 5.41 1 (pitch-16 single Gaussian at 1x) and 5.38 3 (the joint two-component share);
and, for the three frequency-settled 2x `rrect-sm` cells, the distance between the two settled
states measured in the same quantities.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from g3lib import *  # noqa: F401,F403

out = dict(plate_verification=verify_plates(), box={c: box_for(c, 1) for c in COMPS}, cells={})

print('== plate generator against the committed rasters:', out['plate_verification'])

BACKDROPS = PITCHES5 + [LC16]
for scale in SCALES:
    for comp in COMPS:
        m = box_mask(comp, scale)
        for b in BACKDROPS:
            Y = capture(f'{b}__{comp}__rest', scale)
            P = plate(b, scale)
            single, curve = fit_single(Y, P, m, scale, b)
            two = fit_two(Y, P, m, scale, b)
            key = f'{b}|{comp}|{scale}x'
            out['cells'][key] = dict(
                scale=scale, comp=comp, span=SPAN[comp], backdrop=b, pitch=PITCH[b],
                mask_px=int(m.sum()),
                interior_mean=float(Y[m].mean()), interior_std=float(Y[m].std()),
                plate_mean=float(P[m].mean()), plate_std=float(P[m].std()),
                retained_contrast=(float(Y[m].std() / P[m].std()) if P[m].std() > 1e-9 else None),
                sigma_ceiling=sigma_ceiling(P, b, m, scale),
                single=dict(single, sigma_dev=single['sigma'] * scale),
                two=dict(two, sigma_sharp_dev=two['sigma_sharp'] * scale,
                         sigma_heavy_dev=two['sigma_heavy'] * scale),
                curve=curve)
            rec = out['cells'][key]
            rec['flags'] = ([] if P[m].std() >= 0.02 else ['plate-uniform-under-box'])
            if single['sigma'] == rec['sigma_ceiling']:
                rec['flags'].append('sigma-at-identifiability-ceiling')
            if rec['retained_contrast'] is not None and rec['retained_contrast'] < 0.02:
                rec['flags'].append('reference-flattened')
            print(f'{scale}x {comp:15s} {b:18s} | single σ {single["sigma"]:5.2f} css '
                  f'({single["sigma"] * scale:5.2f} dev) t {single["t"]:+.3f} a {single["a"]:.3f} '
                  f'rms {single["rms"]:.4f} r² {single["r2"]:.3f} | ceil {out["cells"][key]["sigma_ceiling"]:5.2f} | two σs {two["sigma_sharp"]:4.2f} '
                  f'σh {two["sigma_heavy"]:5.2f} share {two["share"]:.3f} t {two["t"]:+.3f} '
                  f'a {two["a"]:.3f} rms {two["rms"]:.4f}', flush=True)

# ---- instrument check A: 5.41 1's pitch-16 single-Gaussian table at 1x
ref_541 = {'rrect-sm': (1.25, 0.340, 0.444), 'capsule-button': (1.25, 0.331, 0.448),
           'rrect-md': (1.25, 0.246, 0.556), 'rrect-ml': (1.25, 0.165, 0.609),
           'rrect-lg': (1.00, 0.093, 0.659)}
check = {}
for comp, (s, t, a) in ref_541.items():
    got = out['cells'][f'checkerboard|{comp}|1x']['single']
    check[comp] = dict(claimed=dict(sigma=s, t=t, a=a),
                       measured=dict(sigma=got['sigma'], t=round(got['t'], 3), a=round(got['a'], 3)),
                       matches=bool(got['sigma'] == s and abs(got['t'] - t) < 5e-4 and abs(got['a'] - a) < 5e-4))
out['check_5_41_1'] = check
print('\n== instrument check A (5.41 1, 1x pitch 16):',
      'all reproduce' if all(v['matches'] for v in check.values()) else json.dumps(check, indent=1))

# ---- instrument check B: 5.38 3's joint two-component (σ_sharp fixed 1.0, joint over the five pitches)
checkB = {}
for scale in SCALES:
    for comp in ['rrect-md', 'rrect-ml', 'rrect-lg']:
        m = box_mask(comp, scale)
        Ys = [capture(f'{b}__{comp}__rest', scale) for b in PITCHES5]
        Ps = [(b, plate(b, scale)) for b in PITCHES5]
        joint = fit_two_joint(Ys, Ps, [m] * len(Ys), scale, sig_sharp=[1.0])
        free = fit_two_joint(Ys, Ps, [m] * len(Ys), scale)
        checkB[f'{comp}@{scale}x'] = dict(sharp_fixed_1=joint, free=free)
        print(f'   {scale}x {comp:10s} σs=1 fixed: σh {joint["sigma_heavy"]:5.2f} a {joint["a"]:.3f} '
              f't_h {joint["t_heavy"]:.3f} t_s {joint["t_sharp"]:.3f} share {joint["share"]:.3f} '
              f'rms {joint["rms"]:.4f} | free: σs {free["sigma_sharp"]:.2f} σh {free["sigma_heavy"]:5.2f} '
              f'share {free["share"]:.3f} rms {free["rms"]:.4f}', flush=True)
out['check_5_38_3'] = checkB
claimed_share = {'rrect-md': 0.56, 'rrect-ml': 0.66, 'rrect-lg': 0.76}
print('   claimed 1x shares 0.56 / 0.66 / 0.76; measured',
      [round(checkB[f'{c}@1x']['sharp_fixed_1']['share'], 3) for c in claimed_share])

# ---- the noise bar on the three frequency-settled 2x `rrect-sm` cells
prov = json.load(open(f'{ROOT}/packages/calibration/results/2026-09-03-w12-lens/probe-2x/provenance.json'))
settled = [k for k, v in prov['cells'].items() if v.get('states', 1) > 1]
noise = {}
for cell in settled:
    rec = prov['cells'][cell]
    unatt = set(rec.get('unattestedRuns', []))
    states = {}
    for run in range(1, 6):
        tag = f'probe-{run}'
        if tag in unatt:
            continue
        p = f'{SNAP2X}/snap-{tag}/apple-macos-26.5-2x-light-standard/{cell}.png'
        if not os.path.exists(p):
            continue
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        states.setdefault(h, []).append(tag)
    comp = cell.split('__')[1]
    b = cell.split('__')[0]
    m = box_mask(comp, 2)
    P = plate(b, 2)
    fits = {}
    for h, runs in states.items():
        Y = luma_lin(load_rgb(f'{SNAP2X}/snap-{runs[0]}/apple-macos-26.5-2x-light-standard/{cell}.png'))
        s, _ = fit_single(Y, P, m, 2, b)
        fits[h] = dict(runs=runs, published=(h == rec['sha256']), single=s,
                       interior_mean=float(Y[m].mean()), interior_std=float(Y[m].std()), _Y=Y)
    hs = list(fits)
    d = None
    if len(hs) == 2:
        A, B = fits[hs[0]]['_Y'], fits[hs[1]]['_Y']
        d = dict(interior_rms=float(np.sqrt(np.mean((A[m] - B[m]) ** 2))),
                 interior_mean_delta=float(A[m].mean() - B[m].mean()),
                 whole_max_abs=float(np.abs(A - B).max()),
                 dsigma=fits[hs[0]]['single']['sigma'] - fits[hs[1]]['single']['sigma'],
                 dt=fits[hs[0]]['single']['t'] - fits[hs[1]]['single']['t'],
                 da=fits[hs[0]]['single']['a'] - fits[hs[1]]['single']['a'])
    for f in fits.values():
        f.pop('_Y')
    noise[cell] = dict(share=rec['share'], attested=rec['attested'], states=fits, distance=d)
    print(f'   settled {cell}: ' + (json.dumps(d) if d else f'{len(hs)} distinct attested states'))
out['settled_noise_bar'] = noise

write_part('interior', out)
