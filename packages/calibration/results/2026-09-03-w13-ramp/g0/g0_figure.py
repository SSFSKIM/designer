"""W13 G0: the ramp figure — s(u) against u/(span/2), one panel per scale, one line per span.

Left column: the reference, from `parts/g0-ramp.json`. Right column: the same instrument on
vitrea's own captures (`parts/g0-validation.json`), which is what contract X4 asks to travel
beside every reference reading — vitrea's share is one number per span and the instrument
must, and does, read it flat.
"""
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import w13lib as L  # noqa: E402

ramp = json.load(open(f'{L.OUT}/parts/g0-ramp.json'))
val = json.load(open(f'{L.OUT}/parts/g0-validation.json'))
COMPS = ['rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg']
COLOURS = dict(zip(COMPS, ['#B45309', '#0E7490', '#1D4ED8', '#7C3AED', '#BE123C']))

fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.0), sharex=True)
for row, scale in enumerate((1, 2)):
    ax = axes[row][0]
    for comp in COMPS:
        rec = ramp['primary'][f'{comp}@{scale}x']
        span = L.SPAN[comp]
        rows = [r for r in rec['rows'] if r['u0'] >= 4 - 1e-9 and r['u1'] <= span / 2 - 4 + 1e-9]
        u = np.array([r['u_mid'] for r in rows]) / (span / 2)
        s = np.array([1 - r['k'] for r in rows])
        ax.plot(u, s, 'o-', ms=3.5, lw=1.4, color=COLOURS[comp], label=f'{comp} ({span})')
    x = np.linspace(0, 1, 50)
    ax.plot(x, 0.5 * (1 - x), 'k--', lw=1.2, label='H1: 0.5·(1 − u/(span/2))')
    h = ramp['h2'][f'shared@{scale}x']
    ax.plot(x, h['s0'] * np.maximum(0, 1 - x / h['rho']) + h['floor'], 'k:', lw=1.4,
            label=f'H2 shared: s0 {h["s0"]:.2f}, ρ {h["rho"]:.2f}, floor {h["floor"]:.2f}')
    ax.axhline(0, color='#999', lw=0.6)
    ax.set_ylim(-0.35, 0.75)
    ax.set_ylabel(f'sharp share s at {scale}x')
    ax.set_title(f'the reference, {scale}x — probe pitches 16 / 32 / 64', fontsize=10)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(alpha=0.25)

    ax = axes[row][1]
    for comp in ('capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg'):
        key = f'{comp}@{scale}x|checkerboard+photo'
        rec = val['vitrea'].get(key) or val['vitrea'].get(f'{comp}@{scale}x|checkerboard')
        if rec is None:
            continue
        span = L.SPAN[comp]
        rows = [r for r in rec['rows']
                if r['u_mid'] - 2 >= 4 - 1e-9 and r['u_mid'] + 2 <= span / 2 - 4 + 1e-9]
        u = np.array([r['u_mid'] for r in rows]) / (span / 2)
        s = np.array([1 - r['k'] for r in rows])
        ax.plot(u, s, 'o-', ms=3.5, lw=1.4, color=COLOURS[comp], label=f'{comp} ({span})')
        ax.axhline(1 - L.vitrea_k(span), color=COLOURS[comp], lw=0.8, ls='--', alpha=0.7)
    ax.set_ylim(-0.35, 0.75)
    ax.set_title(f'vitrea `main`, {scale}x — the known uniform share (dashed)', fontsize=10)
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(alpha=0.25)
for ax in axes[1]:
    ax.set_xlabel('depth u / (span/2)')
fig.suptitle('W13 G0 — the sharp share by depth, through the landed lens', fontsize=12)
fig.tight_layout()
fig.savefig(f'{L.OUT}/g0-ramp.png', dpi=140)
print(f'[wrote] {L.OUT}/g0-ramp.png')

# ---- the same in absolute depth, which is what the reach question turns on
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2), sharey=True)
for ax, scale in zip(axes, (1, 2)):
    for comp in COMPS:
        rec = ramp['primary'][f'{comp}@{scale}x']
        span = L.SPAN[comp]
        rows = [r for r in rec['rows'] if r['u0'] >= 4 - 1e-9 and r['u1'] <= span / 2 - 4 + 1e-9]
        ax.plot([r['u_mid'] for r in rows], [1 - r['k'] for r in rows], 'o-', ms=3.5, lw=1.4,
                color=COLOURS[comp], label=f'{comp} ({span})')
    ax.axhline(0, color='#999', lw=0.6)
    ax.set_xlabel('depth u, CSS px')
    ax.set_title(f'{scale}x', fontsize=10)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
axes[0].set_ylabel('sharp share s')
fig.suptitle('W13 G0 — the same readings against absolute depth', fontsize=12)
fig.tight_layout()
fig.savefig(f'{L.OUT}/g0-ramp-absolute.png', dpi=140)
print(f'[wrote] {L.OUT}/g0-ramp-absolute.png')
