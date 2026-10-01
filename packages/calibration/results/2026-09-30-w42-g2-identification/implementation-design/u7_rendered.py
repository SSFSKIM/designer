"""W42 G2 step 3, U7: the rendered agreement of the law ON against `forward.py` with a known T, and
uniform invariance on rendered cells.

`prepare` writes the cells a browser spec renders into a scratch directory
(`renderer-webgpu/e2e/gpu/w42-body-law.spec.ts`, run with W42_U7_DIR set). Each cell carries the
instrument's own backdrop at the cell's scale, the surface, the law's leaves, a known T, and the
expected output codes at deep-interior pixels.

**The expectation** is `forward.py`'s output, `compose` → T(255 · M), on the cell's deep mask
(`Cell.mask`). It uses forward's own maps (exact or decimated Gaussians, its own narrow levels) and
LT's family with the cell's k and λ. The known T is a monotone piecewise-linear table, identical
on every span row, given to the runtime as candidate 2's table at strength 1 and to `forward.py`
as `tone.TableT`. The backdrops are grey, so forward's per-channel T and candidate 2's luma curve
are one curve. The appearance terms that would add to the body — the rim and the inner shadow —
are zeroed in the render's patch, and the group draws with refraction off. The active pose is read
only past the 20-pt band, where the law's weight is 1.

**And the exact per-pixel Gaussian beside it.** `forward.py` realises the depth-graded narrow term
with its own levels, interpolated linearly (`narrow_map`). At a sharp impulse that interpolation is
itself off the exact Gaussian by up to about 0.18 code (measured on this bed). So each sample also
carries the composite over the EXACT Gaussians at the pixel's own σn and at σw (`narrow_error.exact_at`,
the U2 mirror's oracle), through the same knee, fill and T. The spec holds the render to that at
0.15 code, and records its distance from `forward.py` beside it.

**Uniform invariance.** Over a uniform backdrop, A is the backdrop's encoded colour, so with an
identity T (the table's levels as its codes, unit chroma gains) the rendered body IS the backdrop,
chromatic ones included, at every interior pixel the law's weight is 1.

`summarise` reads the spec's `result.json` and writes `u7_rendered.json` beside this file.

    python3.12 -B u7_rendered.py prepare /tmp/w42-u7
    (cd packages/renderer-webgpu && W42_U7_DIR=/tmp/w42-u7 npx playwright test --grep @w42-u7)
    python3.12 -B u7_rendered.py summarise /tmp/w42-u7
"""
import base64
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import u2_fixtures as U  # noqa: E402  (puts the instrument and the rehearsal on the path)
import u2_mirror as M  # noqa: E402
import narrow_error as N  # noqa: E402
import native_t as NT  # noqa: E402

F, G = U.F, U.G
import tone as TONE  # noqa: E402

LEVELS = list(NT.GRID_LEVELS)
ROW = [round(20 + 0.85 * x + 20 * np.sin(np.pi * x / 255), 6) for x in LEVELS]
IDENTITY = [float(x) for x in LEVELS]
BACKDROPS = ('checkerboard', 'checkerboard-8', 'impulse', 'hc-text')
COMPONENTS = ('capsule-button', 'rrect-md', 'rrect-lg')
UNIFORM = ('light-solid', 'dark-solid', 'mid-dark-solid', 'mid-chroma-solid')
SAMPLES = 400
APPEARANCE_OFF = {'optics': {'regular': {'rimAlpha': 0, 'rimLevelGain': 0, 'shadowAlpha': 0}}}


def law_patch(scheme, pose, row, chroma_scale=1.0):
    receded = pose == 'receded'
    k = (M.K_REC if receded else M.K)[scheme]
    lam = (M.LAM_REC if receded else M.LAM)[scheme]
    return dict(APPEARANCE_OFF, bodyLawStrength=1, bodyLawK=[k, k], bodyLawLambda=lam,
                bodyLawNormal=F.WN, bodyLawHinge=1 if scheme == 'light' else -1,
                bodyLawPose=1 if receded else 0, bodyLawKnee=0, bodyLawEdgeSwap=0,
                bodyLawWidthUnit=1, bodyLawEncodedAveraging=1, bodyToneTableStrength=1,
                bodyToneTableLevels=LEVELS, bodyToneTableSpans=list(NT.GRID_SPANS),
                bodyToneTableCodes=[row] * 5, bodyToneChromaGains=[1, 1, 1],
                bodyToneChromaScale=chroma_scale), k, lam


def surface(comp):
    cx, cy, w, h, r = G.shape_frame(comp)
    return dict(nodeId='s', family='fixed-rounded-rect',
                shape=dict(center=[cx, cy], size=[w, h], radii=[r] * 4, smoothing=0, thickness=8))


def raster(bg, scale):
    B8 = G.render_background(bg, scale)
    H, W = B8.shape[:2]
    rgba = np.concatenate([B8.astype(np.uint8), np.full((H, W, 1), 255, np.uint8)], -1)
    return W, H, base64.b64encode(rgba.tobytes()).decode(), B8


def prepare(out):
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261004)
    cells = []
    for bg in BACKDROPS + UNIFORM:
        uniform = bg in UNIFORM
        for comp in COMPONENTS:
            for pose in ('active', 'receded'):
                for scale in (1, 2):
                    for scheme in ('light', 'dark'):
                        if uniform and (comp != 'rrect-md' or scheme != 'light'):
                            continue
                        row = IDENTITY if uniform else ROW
                        patch, k, lam = law_patch(scheme, pose, row)
                        W, H, rgba, B8 = raster(bg, scale)
                        cell = F.Cell(f'{bg}/{comp}', bg, comp, scale, scheme,
                                      'rest' if pose == 'active' else 'inactive', rgb=True,
                                      T=TONE.TableT(LEVELS, row))
                        ys, xs = np.nonzero(cell.mask)
                        if uniform:
                            expected = B8[ys, xs].astype(float)
                        else:
                            fam = F.Family()
                            p = F.expand(fam, {'k': k, 'lam': lam})
                            expected = F.compose(cell, fam, F.maps(cell, fam, p), lam)
                        pick = rng.choice(len(ys), min(SAMPLES, len(ys)), replace=False)
                        exact = np.asarray(expected)[pick]
                        if not uniform:
                            win = cell.crop('box')
                            S = cell.S(win)
                            fam = F.Family()
                            p = F.expand(fam, {'k': k, 'lam': lam})
                            mode = 'clamp' if pose == 'active' else 'norm'
                            py, px = ys[pick], xs[pick]
                            sig = F.sigma_n_pt(cell, fam, p, cell.d[py, px]) * cell.unit_dev(fam.units)
                            sw = k * F.RW * cell.unit_dev(fam.units)
                            Cx = np.array([[N.exact_at(S[..., ch], a - win[0], b - win[2], sg, mode)
                                            for ch in range(3)] for a, b, sg in zip(py, px, sig)])
                            Wx = np.array([[N.exact_at(S[..., ch], a - win[0], b - win[2], sw, mode)
                                            for ch in range(3)] for a, b in zip(py, px)])
                            h = 1 if scheme == 'light' else -1
                            Nx = Cx + h * lam * np.maximum(0, h * (Wx - Cx))
                            exact = TONE.TableT(LEVELS, row)(255 * ((1 - F.WN) * Nx + F.WN * Wx))
                        cells.append(dict(
                            id=f'{bg}__{comp}__{pose}__{scale}x__{scheme}', uniform=uniform,
                            scene=dict(name=f'w42-{bg}-{comp}-{pose}-{scale}-{scheme}', widthCss=320,
                                       heightCss=200, devicePixelRatio=scale,
                                       backdrop=dict(kind='pixels', width=W, height=H, rgba=rgba),
                                       groups=[dict(groupId='g', surfaces=[surface(comp)],
                                                    refraction='none', analysisExact=True,
                                                    backdropSourceId='bg')]),
                            patch=patch, x=xs[pick].tolist(), y=ys[pick].tolist(),
                            expected=np.asarray(expected)[pick].tolist(), exact=np.asarray(exact).tolist()))
    with open(os.path.join(out, 'cells.json'), 'w') as fh:
        json.dump(dict(source='implementation-design/u7_rendered.py', table=dict(levels=LEVELS, row=ROW),
                       cells=cells), fh)
    print(f'{len(cells)} cells written to {out}/cells.json')


def summarise(out):
    result = json.load(open(os.path.join(out, 'result.json')))
    rows = result['cells']
    law = [r for r in rows if not r['uniform']]
    uni = [r for r in rows if r['uniform']]
    worst = max(law, key=lambda r: r['maxCodes'])
    doc = dict(
        adapter=result['adapter'], cells=len(rows), gpuErrors=result['gpuErrors'],
        format=result['format'], formatRoundingCodes=result['formatRoundingCodes'],
        agreement=dict(cells=len(law), samplesPerCell=SAMPLES, boundCodes=0.15,
                       againstExactGaussian=dict(maxCodes=max(r['maxCodes'] for r in law),
                                                 worstP99Codes=max(r['p99Codes'] for r in law),
                                                 worst=worst['id']),
                       againstForward=dict(maxCodes=max(r['forwardMaxCodes'] for r in law),
                                           worst=max(law, key=lambda r: r['forwardMaxCodes'])['id'],
                                           cellsAbove015=[r['id'] for r in law
                                                          if r['forwardMaxCodes'] > 0.15]),
                       perCell={r['id']: dict(exact=r['maxCodes'], forward=r['forwardMaxCodes'])
                                for r in law}),
        uniformInvariance=dict(cells=len(uni), maxCodes=max(r['maxCodes'] for r in uni),
                               perCell={r['id']: r['maxCodes'] for r in uni}),
        table=dict(levels=LEVELS, row=ROW), identityTable=IDENTITY,
    )
    path = os.path.join(HERE, 'u7_rendered.json')
    with open(path, 'w') as fh:
        json.dump(doc, fh, indent=1)
        fh.write('\n')
    print(json.dumps({k: v for k, v in doc.items() if k not in ('agreement', 'uniformInvariance')}, indent=1))
    print('agreement', {k: v for k, v in doc['agreement'].items() if k != 'perCell'})
    print('uniform', {k: v for k, v in doc['uniformInvariance'].items() if k != 'perCell'})


if __name__ == '__main__':
    {'prepare': prepare, 'summarise': summarise}[sys.argv[1]](sys.argv[2])
