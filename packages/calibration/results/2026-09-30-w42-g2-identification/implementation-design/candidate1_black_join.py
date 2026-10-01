"""W42 G2: the executable form of `candidate1-black-join-addendum.md`, the parent's pre-read amendment
of candidate 1's landed tone inside W36's open interval below the black join.

The hashed rehearsal is never edited. This wraps its `landed_T` (`gate/rehearsal/body.py:504`), and
replaces the per-pixel landed tone inside the open interval of the black branch's own abscissa.
- The abscissa, per endpoint, is the solve's `x = enc(level)` (`body.py:369`, `513–515`): the
  source abscissa's linear luminance of dec(A), or the silhouette abscissa's encoded luma of A.
- The interval is 0 < x < X_END, where X_END = 0.003 is the branch's end: its blend weight
  strength · (1 − smoothstep(0, 0.003, x)) reaches 0 there and the response is the old solve
  (`body.py:373`, `wgsl/optics.ts:1462–1464`, `material.ts:4619–4625`).
- There, per channel, y(A) = (1 − x/X_END) · y(0) + (x/X_END) · y(A_end). Here y is `landed_T`,
  y(0) is its value at black, and A_end is A's own ray through black taken to the end, in the
  abscissa's own space:
  - silhouette (encoded): A_end = A · X_END / L_enc(A);
  - source (linear light): dec(A_end) = dec(A) · dec(X_END) / L_lin(dec A).
  Either way A_end's abscissa is exactly X_END. For a grey it is the grey at the end.
- Nothing else moves: black itself, every input at or above the end, the group-level solve and
  every document's digest.

    python3.12 -B candidate1_black_join.py     # writes candidate1_black_join.txt and fixtures/landed-bridged.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import u2_fixtures as U  # noqa: E402  (puts the rehearsal on the path)

BODY = U.BODY
X_END = 0.003


def silhouette(e):
    return e['abscissa'] != 'source(default)'


def abscissa(e, A):
    """The black branch's own abscissa for arguments A (..., 3), encoded: body.py's x = enc(level)."""
    level = BODY.dec(A @ BODY.W709) if silhouette(e) else BODY.dec(A) @ BODY.W709
    return BODY.enc(level)


def ray_end(e, A):
    """A's own ray through black taken to the branch's end, in the abscissa's own space."""
    if silhouette(e):
        L = A @ BODY.W709
        return A * (X_END / np.where(L > 0, L, 1.0))[..., None]
    c = BODY.dec(A)
    ell = c @ BODY.W709
    return BODY.enc(c * (BODY.dec(X_END) / np.where(ell > 0, ell, 1.0))[..., None])


def bridge(tone, e, A):
    """Apply the amendment to a tone y(A) that evaluates arrays of arguments (..., 3)."""
    A = np.asarray(A, dtype=np.float64)
    y = tone(A)
    if not e['black'][0] > 0:
        return y
    x = abscissa(e, A)
    inside = (x > 0) & (x < X_END)
    if not inside.any():
        return y
    y0 = tone(np.zeros_like(A))
    y1 = tone(np.where(inside[..., None], ray_end(e, A), A))
    f = (x / X_END)[..., None]
    return np.where(inside[..., None], (1 - f) * y0 + f * y1, y)


def landed_T(ep, scale, component, A):
    """The amended candidate 1: the hashed `landed_T` with the interval bridged."""
    return bridge(lambda X: BODY.landed_T(ep, scale, component, X), BODY.RES[ep], A)


def landed_at(e, sizeK, A):
    """`landed_T`'s arithmetic for one sizeK over a list of arguments (u2_fixtures' landed form)."""
    c = BODY.dec(A)
    lin = c @ BODY.W709
    level = BODY.dec(A @ BODY.W709) if silhouette(e) else lin
    return BODY.compose(e, c, BODY.solve(e, sizeK, level, lin), c)


def probe(ep, scale, component, colours, amended):
    """`landed_T` itself (or its amendment) at the given arguments, placed on surface 0's owned pixels."""
    fl = BODY.field(component, scale)
    ys, xs = np.nonzero(fl.owner == 0)
    canvas = np.zeros(fl.owner.shape + (3,))
    canvas[ys[:len(colours)], xs[:len(colours)]] = colours
    out = (landed_T if amended else BODY.landed_T)(ep, scale, component, canvas)
    return out[ys[:len(colours)], xs[:len(colours)]]


def codes(linear):
    return 255 * BODY.enc(linear)


def report():
    lines = [__doc__.split('\n\n')[0], '',
             f'X_END = {X_END} (encoded input; {255 * X_END:.3f} codes)', '']
    comps = (('capsule-button', 'capsule, sizeK 0.0923'), ('rrect-sm', 'rrect-sm, sizeK 0'),
             ('rrect-md', 'rrect-md/ml/lg, sizeK 1'))
    lines.append('The bridge\'s endpoint values, grey output codes (every channel equal): y(0) at black '
                 'and y(end) at the grey on the end')
    lines.append(f"{'endpoint':14s} {'scale':5s} {'component':26s} {'y(0)':>8s} {'y(end)':>8s}")
    ends = np.array([[0.0] * 3, [X_END] * 3])
    for ep in BODY.RES:
        for scale in (1, 2):
            for comp, label in comps:
                y = codes(probe(ep, scale, comp, ends, amended=False))
                lines.append(f'{ep:14s} {scale}x    {label:26s} {y[0, 0]:8.3f} {y[1, 0]:8.3f}')
    lines.append('')
    lines.append('Before / after over [0, 2] codes of grey input, output codes; 1x, and 2x asserted equal '
                 '(sizeK is per component and the same at both scales)')
    grid = np.round(np.arange(0, 2.0001, 0.1), 4)
    greys = np.repeat((grid / 255)[:, None], 3, axis=1)
    for ep in BODY.RES:
        for comp, label in comps[::2]:
            before = codes(probe(ep, 1, comp, greys, amended=False))[:, 0]
            after = codes(probe(ep, 1, comp, greys, amended=True))[:, 0]
            # Read at 2x as well: the landed solve depends on the scale only through sizeK.
            assert np.allclose(before, codes(probe(ep, 2, comp, greys, amended=False))[:, 0], atol=1e-9)
            assert np.allclose(after, codes(probe(ep, 2, comp, greys, amended=True))[:, 0], atol=1e-9)
            lines.append(f'{ep} {label}')
            lines.append('  code   ' + ' '.join(f'{g:6.1f}' for g in grid))
            lines.append('  before ' + ' '.join(f'{v:6.1f}' for v in before))
            lines.append('  after  ' + ' '.join(f'{v:6.1f}' for v in after))
    return '\n'.join(lines) + '\n'


def fixture():
    """The amended landed tone at landed.json's sizeKs, on greys across the interval and chromatic
    arguments inside it, for renderer-webgpu's CPU reference."""
    rng = np.random.default_rng(20261002)
    greys = [0.0, 0.0001, 0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.0029, 0.00299, 0.003, 0.0031, 0.004,
             0.01, 0.1, 0.5, 1.0]
    colours = [[g, g, g] for g in greys]
    for _ in range(24):   # near-black chromatic arguments, most of them inside the interval
        colours.append(list(rng.uniform(0, 0.012, 3)))
    A = np.array(colours)
    out = {}
    for ep, e in BODY.RES.items():
        cases = []
        for sizeK in (0.0, 0.0923, 0.35, 1.0):
            y = bridge(lambda X: landed_at(e, sizeK, X), e, A)
            cases.append(dict(sizeK=sizeK, A=A.tolist(), linear=y.tolist(),
                              inside=((abscissa(e, A) > 0) & (abscissa(e, A) < X_END)).tolist()))
        out[ep] = dict(cases=cases)
    # The wrapper and the per-colour form agree with the hashed landed_T itself.
    for ep in BODY.RES:
        for comp in ('capsule-button', 'rrect-md'):
            direct = probe(ep, 1, comp, A, amended=True)
            sizeK = BODY.RES[ep]['perScale']['1x']['components'][
                'capsule' if comp == 'capsule-button' else 'rrect-md']['sizeK']
            viaform = bridge(lambda X: landed_at(BODY.RES[ep], sizeK, X), BODY.RES[ep], A)
            assert np.allclose(direct, viaform, atol=1e-12), (ep, comp)
    return out


def main():
    text = report()
    with open(os.path.join(HERE, 'candidate1_black_join.txt'), 'w') as fh:
        fh.write(text)
    with open(os.path.join(HERE, 'fixtures', 'landed-bridged.json'), 'w') as fh:
        json.dump(fixture(), fh, separators=(',', ':'))
        fh.write('\n')
    print(text)


if __name__ == '__main__':
    main()
