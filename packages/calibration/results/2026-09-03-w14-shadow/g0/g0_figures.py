"""The figures: c(d) and a(d) by side, the vibrant test, and the blur's sigma curve.

Every panel carries vitrea's own capture beside the reference's, which is X4 in picture form: the
lift panel's vitrea line is the flat zero a black multiply must give, and the transmission panel's
vitrea line is W8's own falloff.

All four are read from the committed rasters directly, so the figures do not depend on the shape of
any `parts/*.json`.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import w14lib as L

BLACK, WHITE = 0.02, 0.98
MAXD = 48
COMPS = ['rrect-md', 'rrect-ml', 'rrect-lg']
SIDE_STYLE = {'below': ('C3', '-'), 'above': ('C0', '-'), 'left': ('C2', '--'),
              'right': ('C4', ':')}


def profiles(path, comp, scale, BG, d, side):
    """Per side, per 1 CSS px ring: the black-square mean (the lift) and the white-square mean."""
    Y = L.luma_of(L.image_srgb(path))
    out = {}
    for name in ('below', 'above', 'left', 'right'):
        lift, trans, ds = [], [], []
        for k in range(MAXD):
            m = (d >= max(k, 1.5 / scale)) & (d < k + 1) & (side == L.SIDES.index(name))
            mb, mw = m & (BG < BLACK), m & (BG > WHITE)
            if mb.sum() < 8 or mw.sum() < 8:
                continue
            ds.append(k + 0.5)
            lift.append(float(Y[mb].mean()))
            trans.append(float(Y[mw].mean() - Y[mb].mean()))
        out[name] = (np.array(ds), np.array(lift), np.array(trans))
    return out


def panel_set(scale):
    prof = L.profile_key(scale)
    BG = L.luma_of(L.image_srgb(L.backdrop_path('checkerboard', scale)))
    data = {}
    for comp in COMPS:
        scene = f'checkerboard__{comp}__rest'
        d, side = L.geometry(comp, scale)
        data[comp] = {
            'native': profiles(L.native_path(prof, scene), comp, scale, BG, d, side),
            'webgpu': profiles(L.web_path(prof, scene), comp, scale, BG, d, side),
        }
    return data


for name, index, ylabel, title in (
        ('lift', 1, 'lift, encoded luma',
         'c(d): the reference lifts the black squares, vitrea does not'),
        ('transmission', 2, 'transmission a(d), encoded',
         'a(d): the black term on the white squares, the lift removed')):
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    for row, scale in enumerate((1, 2)):
        data = panel_set(scale)
        for col, comp in enumerate(COMPS):
            ax = axes[row][col]
            for src, width, alpha in (('native', 2.0, 1.0), ('webgpu', 1.2, 0.75)):
                for sname, (colour, style) in SIDE_STYLE.items():
                    ds, lift, trans = data[comp][src][sname]
                    y = (lift, trans)[index - 1]
                    kw = dict(color=colour, lw=width, alpha=alpha,
                              label=f'{sname} — {src}' if row == 0 and col == 0 else None)
                    if src == 'webgpu':
                        kw['dashes'] = (2, 2)
                    ax.plot(ds, y, style, **kw)
            ax.set_title(f'{comp}  span {L.span_of(comp):.0f}  {scale}x', fontsize=9)
            ax.grid(alpha=0.25)
            if col == 0:
                ax.set_ylabel(ylabel, fontsize=8)
            if row == 1:
                ax.set_xlabel('distance outside the declared contour, CSS px', fontsize=8)
    axes[0][0].legend(fontsize=6, ncol=2)
    fig.suptitle(title + '   (solid: Apple, dashed: vitrea GPU; checkerboard, pitch 16)',
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(f'{L.OUT}/fig-{name}-by-side.png', dpi=140)
    plt.close(fig)
    print('wrote', f'{L.OUT}/fig-{name}-by-side.png')

# ---- the vibrant test: the lift against the blurred backdrop, across backdrops
with open(f'{L.PARTS}/vibrant.json') as fh:
    vib = json.load(fh)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
for ax, scale in zip(axes, (1, 2)):
    for comp, colour in zip(('rrect-md', 'rrect-ml', 'rrect-lg', 'capsule-button'),
                            ('C0', 'C1', 'C3', 'C7')):
        key = f'{scale}x/{comp}'
        if key not in vib:
            continue
        g = vib[key]['native']['groups']
        x = [r['B']['40.0'] * 255 for r in g]  # keys are strings once the JSON round-trips
        y = [r['lift'] * 255 for r in g]
        ax.plot(x, y, 'o', color=colour, label=f'{comp} (span {L.span_of(comp):.0f})')
        b = vib[key]['native']['best']
        if b['sigma'] == 40.0:
            xs = np.linspace(0, 255, 2)
            ax.plot(xs, b['slope'] * xs + b['intercept'] * 255, '-', color=colour, lw=1, alpha=0.6)
    ax.set_xlabel('blur-40 of the backdrop at the black pixels, encoded luma x255')
    ax.set_ylabel('lift, encoded luma x255')
    ax.set_title(f'{scale}x — the lift on near-black pixels, 0-6 CSS px below')
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
fig.suptitle('the lift is the backdrop\'s own light: zero over `impulse`, full over the '
             'checkerboard', fontsize=10)
fig.tight_layout()
fig.savefig(f'{L.OUT}/fig-vibrant.png', dpi=140)
plt.close(fig)
print('wrote', f'{L.OUT}/fig-vibrant.png')

# ---- the blur's sigma curve
with open(f'{L.PARTS}/blur-black-square.json') as fh:
    blur = json.load(fh)
fig, ax = plt.subplots(figsize=(6.5, 4.2))
for key, rec in sorted(blur.items()):
    if not key.endswith('/0-6'):
        continue
    c = rec['curve']
    ax.plot([r['sigma'] for r in c], [r['rms'] * 255 for r in c], 'o-', lw=1.2, ms=3, label=key)
ax.axvline(40, color='k', ls=':', lw=1)
ax.text(40.6, ax.get_ylim()[1] * 0.98, "the layer tree's BlurRadius 40", fontsize=7, va='top')
ax.set_xlabel('sigma of the blurred copy, CSS px')
ax.set_ylabel('residual of the pooled black-square fit, encoded luma x255')
ax.set_title("the lift's blur from the pitch axis, ring 0-6 below")
ax.grid(alpha=0.25)
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(f'{L.OUT}/fig-blur-sigma.png', dpi=140)
plt.close(fig)
print('wrote', f'{L.OUT}/fig-blur-sigma.png')
