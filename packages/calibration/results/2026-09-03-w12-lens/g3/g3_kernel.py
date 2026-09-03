"""G3 reading 3: the impulse kernel at the cell centre, from the pitch-4 and pitch-8 cells.

The deep interior (u >= 20 CSS px, outside the lens) of one cell over all five checkerboard pitches
at once identifies the kernel that maps backdrop to interior: pitches 4 and 8 constrain the narrow
component, 32 and 64 the wide one. The kernel is fitted as a pair of operators, core and base, with
their amplitudes non-negative and (a, t) free, so the base share is read rather than assumed:

    Y = a + t_core·(Core * P) + t_base·(Base * P),   share = t_base / (t_core + t_base)

Core candidates: a Gaussian of width σ; a box of width w CSS px; and `quarter` — the plate
downsampled to the quarter-device-scale buffer and bilinearly upsampled, which is what 5.50 2 says
the reference's sharp term actually is (a 4-device-px box, so 4 CSS px at 1x and 2 CSS px at 2x).
The comparison between the three answers "is the core flat-topped or Gaussian".
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from g3lib import *  # noqa: F401,F403
from g3lib import _nnls_two

CELLS = ['rrect-md', 'rrect-ml', 'rrect-lg']
CORE_GAUSS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
CORE_BOX = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]
BASE_GAUSS = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 16.0, 18.0, 20.0]


def box_filter(P, width_css, scale):
    """Separable box of `width_css` CSS px on a device-pixel grid, non-integer widths included."""
    w = width_css * scale
    half = w / 2
    n = int(np.ceil(half - 0.5))
    offs = np.arange(-n, n + 1)
    k = np.clip(np.minimum(offs + 0.5, half) - np.maximum(offs - 0.5, -half), 0, None)
    k = k / k.sum()
    out = np.apply_along_axis(lambda r: np.convolve(np.pad(r, n, mode='edge'), k, 'valid'), 0, P)
    return np.apply_along_axis(lambda r: np.convolve(np.pad(r, n, mode='edge'), k, 'valid'), 1, out)


_op_cache = {}


def op(kind, param, P, key, scale):
    ck = (kind, param, key, scale)
    if ck not in _op_cache:
        if kind == 'gauss':
            _op_cache[ck] = G(P, key, param, scale)
        elif kind == 'box':
            _op_cache[ck] = box_filter(P, param, scale)
        elif kind == 'quarter':
            _op_cache[ck] = quarter_buffer(P, key, scale, 0.0)[0]
        else:
            raise ValueError(kind)
    return _op_cache[ck]


def fit_pair(ys, cols_a, cols_b):
    y = np.concatenate(ys)
    A = np.concatenate(cols_a)
    B = np.concatenate(cols_b)
    coef, rms, r2 = _nnls_two(y, A, B)
    t = coef[1] + coef[2]
    return dict(a=float(coef[0]), t_core=float(coef[1]), t_base=float(coef[2]), t=float(t),
                share=float(coef[2] / t) if abs(t) > 1e-9 else float('nan'), rms=rms, r2=r2)


out = dict(cells={})
for scale in SCALES:
    for comp in CELLS:
        mask = band_mask(comp, scale, 20.0, SPAN[comp] / 2)
        ys = [capture(f'{b}__{comp}__rest', scale)[mask] for b in PITCHES5]
        Ps = [(b, plate(b, scale)) for b in PITCHES5]
        best = {}
        for core_kind, params in (('gauss', CORE_GAUSS), ('box', CORE_BOX), ('quarter', [0.0])):
            for cp in params:
                ca = [op(core_kind, cp, P, k, scale)[mask] for k, P in Ps]
                for sb in BASE_GAUSS:
                    cb = [G(P, k, sb, scale)[mask] for k, P in Ps]
                    r = fit_pair(ys, ca, cb)
                    r.update(core=core_kind, core_param=cp, base_sigma=sb,
                             base_sigma_dev=sb * scale)
                    if core_kind not in best or r['rms'] < best[core_kind]['rms']:
                        best[core_kind] = r
        # per-pitch residual of the overall winner
        win = min(best.values(), key=lambda r: r['rms'])
        per_pitch = {}
        ca = [op(win['core'], win['core_param'], P, k, scale) for k, P in Ps]
        cb = [G(P, k, win['base_sigma'], scale) for k, P in Ps]
        for (b, _), A, B, y in zip(Ps, ca, cb, ys):
            model = win['a'] + win['t_core'] * A[mask] + win['t_base'] * B[mask]
            per_pitch[b] = dict(rms=float(np.sqrt(np.mean((y - model) ** 2))),
                                std_ref=float(y.std()), std_model=float(model.std()))
        out['cells'][f'{comp}@{scale}x'] = dict(comp=comp, scale=scale, mask_px=int(mask.sum()),
                                                candidates=best, winner=win, per_pitch=per_pitch)
        print(f'== {scale}x {comp}: ' + ' | '.join(
            f'{k} {("σ" if k == "gauss" else "w")}{v["core_param"]:.2f} base σ {v["base_sigma"]:.0f} '
            f'({v["base_sigma_dev"]:.0f} dev) share {v["share"]:.3f} rms {v["rms"]:.4f}'
            for k, v in best.items()), flush=True)
        print('     per-pitch rms of the winner (' + win['core'] + '): ' +
              ' '.join(f'{b.split("-")[-1]}:{r["rms"]:.4f}' for b, r in per_pitch.items()))

write_part('kernel', out)
