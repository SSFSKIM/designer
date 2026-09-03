"""W13 G0, step 5: the impulse cells — the dot's response through the glass, and the gap.

The `impulse` backdrop is a 5 × 3 grid of 4 × 4 CSS px white dots on black, 64 CSS px apart.
Exactly one dot falls under `capsule-button` (at 159.5, 103.5 — SDF depth 18.5 CSS px on a
span of 44, so u/(span/2) = 0.84, deep where the ramp has faded the sharp share); three fall
under `rrect-md`, of which the middle one sits at depth 44.5 on a span of 96.

For each dot, at both scales and both schemes, on the reference fixture and on vitrea's own
canonical capture:

  * the radial profile of linear luminance about the dot,
  * the peak contrast against the local surround, and vitrea's ratio to the reference's —
    the user's "the dot disappears" as a number,
  * a two-component read on a disc about the dot (core width and weight, base width and
    weight), which says whether the gap is a width or a weight.

Nothing here is captured; the fixtures, the web captures and the backdrop rasters are all
committed.
"""
import numpy as np

import w13lib as L

g3 = L.g3lib
DOTS = {'capsule-button': [(159.5, 103.5)],
        'rrect-md': [(95.5, 103.5), (159.5, 103.5), (223.5, 103.5)]}
SIG_S = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]
SIG_H = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 14.0]


def radial(Y, scale, cx, cy, r_max=26.0, step=1.0, mask=None):
    H, W = Y.shape
    ys, xs = np.mgrid[0:H, 0:W]
    rr = np.hypot((xs + 0.5) / scale - cx, (ys + 0.5) / scale - cy)
    prof = []
    for r0 in np.arange(0, r_max, step):
        m = (rr >= r0) & (rr < r0 + step)
        if mask is not None:
            m &= mask
        prof.append(float(Y[m].mean()) if m.any() else float('nan'))
    return np.arange(0, r_max, step) + step / 2, np.array(prof)


out = {}
print('the impulse cells — peak contrast in linear luminance, and vitrea`s ratio to the reference\n')
print(f'   {"cell":<38} {"depth":>6} {"native":>9} {"vitrea":>9} {"ratio":>7}')
for scale in (1, 2):
    for scheme in ('light', 'dark'):
        profile = f'apple-macos-26.5-{scale}x-{scheme}-standard'
        P = L.background('impulse', scale)
        for comp, dots in DOTS.items():
            scene = f'impulse__{comp}__rest'
            try:
                N = L.w11lib.luma_lin(L.w11lib.load_rgb(f'{L.FIX}/{profile}/{scene}.png'))
                V = L.w11lib.luma_lin(L.w11lib.load_rgb(
                    f'{L.WEB}/{profile}/{scene}/{scene}__webgpu.png'))
            except FileNotFoundError:
                continue
            depth = L.depth_map(comp, scale)
            inside = depth > 2.0
            for (cx, cy) in dots:
                d0 = float(depth[int(cy * scale), int(cx * scale)])
                H, W = N.shape
                ys, xs = np.mgrid[0:H, 0:W]
                rr = np.hypot((xs + 0.5) / scale - cx, (ys + 0.5) / scale - cy)
                near = (rr <= 6.0) & inside
                far = (rr >= 26.0) & (rr <= 34.0) & inside
                if not far.any():
                    far = (rr >= 20.0) & (rr <= 30.0) & inside
                rec = {'depth': d0}
                for tag, Y in (('native', N), ('vitrea', V)):
                    surround = float(np.median(Y[far]))
                    peak = float(Y[near].max())
                    r, prof = radial(Y, scale, cx, cy, mask=inside)
                    disc = (rr <= 24.0) & inside
                    fit = g3.fit_two_joint([Y], [('impulse', P)], [disc], scale,
                                           sig_sharp=SIG_S, sig_heavy=SIG_H, min_gap=1.0)
                    rec[tag] = dict(surround=surround, peak=peak, contrast=peak - surround,
                                    radial_r=list(r), radial=list(prof),
                                    core_sigma=fit['sigma_sharp'], base_sigma=fit['sigma_heavy'],
                                    core_weight=fit['t_sharp'], base_weight=fit['t_heavy'],
                                    t=fit['t'], share=fit['share'], rms=fit['rms'])
                rec['ratio'] = (rec['vitrea']['contrast'] / rec['native']['contrast']
                                if abs(rec['native']['contrast']) > 1e-9 else float('nan'))
                key = f'{comp}@{scale}x-{scheme}-dot({cx:.1f},{cy:.1f})'
                out[key] = rec
                print(f'   {key:<38} {d0:>6.1f} {rec["native"]["contrast"]:>9.4f} '
                      f'{rec["vitrea"]["contrast"]:>9.4f} {rec["ratio"]:>7.2f}')

print('\nthe two-component read on the disc about each dot (σ in CSS px, weights are transmissions)')
print(f'   {"cell":<38} {"core σ":>13} {"base σ":>13} {"core w":>13} {"base w":>13}')
for key, rec in out.items():
    n, v = rec['native'], rec['vitrea']
    print(f'   {key:<38} {n["core_sigma"]:>6.2f}/{v["core_sigma"]:<6.2f} '
          f'{n["base_sigma"]:>6.2f}/{v["base_sigma"]:<6.2f} '
          f'{n["core_weight"]:>6.3f}/{v["core_weight"]:<6.3f} '
          f'{n["base_weight"]:>6.3f}/{v["base_weight"]:<6.3f}')

# ---- what the interior carries at all, backdrop by backdrop
# The dot reading above turns on one fact that needs its own table: on `impulse` vitrea's
# capsule interior is EXACTLY uniform. This asks whether that is the impulse scene or the
# thin material generally, by reading the interior's own mean and standard deviation on every
# backdrop the canonical bed carries for the same two components.
print('\nthe interior (depth > 4 CSS px), backdrop by backdrop — mean / std in linear luminance')
print(f'   {"backdrop":<14} {"plate mean":>10} {"plate std":>9}   '
      f'{"capsule N":>18} {"capsule V":>18} {"rrect-md N":>18} {"rrect-md V":>18}')
levels = {}
for scale in (1, 2):
    for bd in ('impulse', 'dark-solid', 'checkerboard', 'hc-text', 'photo', 'light-solid'):
        try:
            P = L.background(bd, scale)
        except FileNotFoundError:
            continue
        rec = dict(plate_mean=float(P.mean()), plate_std=float(P.std()))
        cells = []
        for comp in ('capsule-button', 'rrect-md'):
            scene = f'{bd}__{comp}__rest'
            try:
                N = L.w11lib.luma_lin(L.w11lib.load_rgb(
                    f'{L.FIX}/apple-macos-26.5-{scale}x-light-standard/{scene}.png'))
                V = L.w11lib.luma_lin(L.w11lib.load_rgb(
                    f'{L.WEB}/apple-macos-26.5-{scale}x-light-standard/{scene}/{scene}__webgpu.png'))
            except FileNotFoundError:
                cells += ['—', '—']
                continue
            m = L.depth_map(comp, scale) > 4
            rec[comp] = dict(native_mean=float(N[m].mean()), native_std=float(N[m].std()),
                             web_mean=float(V[m].mean()), web_std=float(V[m].std()))
            cells += [f'{N[m].mean():.4f} / {N[m].std():.5f}',
                      f'{V[m].mean():.4f} / {V[m].std():.5f}']
        levels[f'{bd}@{scale}x'] = rec
        print(f'   {bd}@{scale}x{"":<5} {P.mean():>10.4f} {P.std():>9.4f}   '
              + ' '.join(f'{c:>18}' for c in cells))
out['_interior_levels'] = levels

L.write_part('g0-impulse', out)

# ---- the figure: the radial profiles
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

keys = ([k for k in out if 'capsule-button' in k]
        + [k for k in out if 'rrect-md' in k and '159.5' in k])
fig, axes = plt.subplots(2, 4, figsize=(15, 6.5), sharex=True)
for ax, key in zip(axes.ravel(), keys):
    rec = out[key]
    for tag, colour in (('native', '#111111'), ('vitrea', '#BE123C')):
        ax.plot(rec[tag]['radial_r'], rec[tag]['radial'], color=colour, lw=1.5, label=tag)
    ax.set_title(key.replace('__rest', ''), fontsize=7.5)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
for ax in axes[1]:
    ax.set_xlabel('radius from the dot, CSS px')
for ax in axes[:, 0]:
    ax.set_ylabel('linear luminance')
fig.suptitle('W13 G0 — the dot through the glass: radial profiles, reference against vitrea',
             fontsize=12)
fig.tight_layout()
fig.savefig(f'{L.OUT}/g0-impulse.png', dpi=140)
print(f'[wrote] {L.OUT}/g0-impulse.png')
