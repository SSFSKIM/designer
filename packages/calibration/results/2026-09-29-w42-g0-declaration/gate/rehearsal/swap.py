"""W42 G0 rehearsal (charter clause 3): memo A's body swap, on the canonical shipped captures.

    web'(x) = round(web(x) + cov(x) (t(B_cand(x)) - t(B_ship(x)) - q(x)))     encoded codes

`web` is the shipped WebGPU capture of the canonical tree (what the matrix rows name), B_ship
the shipped body `body.py` replicates at the refracted position, B_cand the candidate body at
the same refracted position, `cov` the contour's pixel coverage (in the ACTIVE pose, only beyond
the 20 pt refraction band; see ACTIVE_BAND_PT), `t` the author tint's
composite fitted on a tinted cell (the identity elsewhere), and q the capture's rounding where
it is within one code of the replica (see `swap_cell`). Everything the capture carries beyond the
body — rim, highlight, inner shadow, outer shadow, the tint's own layer — is kept, because only
the difference between two bodies is added. Memo A's swap (grounding `argument/core.py`
`synth`) inverted E3 on E3's own stage capture; this one needs no inversion, so it runs in all
four endpoints from the tree the matrix names.

Variants (the rehearsal's candidate documents name them):
  identity  B_cand = B_ship: the capture unchanged (pixel for pixel), re-measured; the base every other variant
            is read beside (clause 10's "the base's own scratch union at the same membership").
  c1        candidate 1, the LANDED T: LT's argument toned by the shipped solve's uniform
            response per pixel in light active, dark active and dark receded; by E3's F
            (extended above 150, stand-in ordinates) and g(L(W)) v(W) in light receded.
  c1s       candidate 1 with the light receded tone left at the shipped solve (Decision Log 3's
            partial adoption); the other three endpoints are c1's.
  c1m       DIAGNOSTIC, not a candidate: c1 with the chroma of the per-channel composite M
            instead of W's (body.lt_argument chroma='M'), to show what Stop P and M1 read of the
            chroma kernel the charter leaves open (U6, family E).
  c2        candidate 2, NATIVE T: c1's chroma with its luma replaced by memo C's native
            uniform table at M's luma, span-corrected.
  e3ctl     the CONTROL: the sealed W41 E3 shader on the shipped argument (light only). W41 G2's
            stage captured exactly this body for real, so web' against that capture measures
            the swap's own error, band by band.

    python3.12 -B swap.py --variant c1 --out /scratch/tree [--profiles P,...] [--scenes S,...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import body as B  # noqa: E402

CAL = HERE.parents[3]
ROOT = HERE.parents[5]
CANONICAL = Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
sys.path.insert(0, str(CAL / 'results/2026-09-26-w40-g0-generations'))
import matrix_store as store  # noqa: E402

PROFILES = [f'apple-macos-27.0-{s}x-{c}-standard-glass0.5' for c in ('light', 'dark') for s in (1, 2)]
SPLIT = {}
for role, scenes in B.SPEC['split'].items():
    if isinstance(scenes, list):
        for s in scenes:
            SPLIT[s] = role
VARIANTS = ('identity', 'c1', 'c1s', 'c1m', 'c2', 'e3ctl')
DOC_DIR = HERE / 'documents'


def population(profiles=PROFILES):
    """Every current WebGPU row of the four standard profiles outside the holdout, from the
    current union (the canonical tree holds exactly these captures)."""
    rows = store.load_current_rows(matrix_path=str(CAL / 'results/matrix.json'))
    out = []
    for r in rows:
        p = r['key']['profileKey']
        if p in profiles and r['key']['web']['renderer'] == 'webgpu' and r['fixtureSet'] != 'holdout':
            assert SPLIT.get(r['key']['sceneId']) == r['fixtureSet'], r['key']['sceneId']
            out.append(r)
    return sorted(out, key=lambda r: (r['key']['profileKey'], r['key']['sceneId']))


def rgb(path):
    with Image.open(path) as im:
        return np.asarray(im.convert('RGB'), dtype=np.float64)


def untinted(scene):
    bg, comp, pose = scene.split('__')
    return f'{bg}__{comp}__{pose.split("-tint-")[0]}' if '-tint-' in pose else None


def tint_model(profile, scene, fl):
    """The author tint as the optics pass composites it after the body, fitted on this cell:

        y_c = (1 - s) x_c + s 255 enc(p_c + q_c Y(x))          (encoded codes)

    `optics.ts` mixes the ENCODED body with the encoded layer `seed * shade(u)` at the tint's
    strength s, and `shade` is linear in the body's linear luma u (clamped). x is the untinted
    twin's shipped capture, y this cell's, over the body at depth >= 2 CSS px. Returns the
    transfer as a function of a body in codes, and its fit residual (rms codes); None when the
    scene is untinted. On a solid backdrop the luma slope is unidentified (one luma), which a
    small ridge holds at zero; a body delta there moves by (1 - s) alone."""
    twin = untinted(scene)
    if twin is None:
        return None, None
    from scipy.optimize import least_squares
    x = rgb(CANONICAL / profile / twin / f'{twin}__webgpu.png')
    y = rgb(CANONICAL / profile / scene / f'{scene}__webgpu.png')
    m = -fl.d >= 2
    X, Yt = x[m], y[m]
    if len(X) > 20000:
        idx = np.random.default_rng(0).choice(len(X), 20000, replace=False)
        X, Yt = X[idx], Yt[idx]
    u = B.dec(X / 255) @ B.W709

    def model(p, xx, uu):
        s, pc, qc = p[0], p[1:4], p[4:7]
        return (1 - s) * xx + s * 255 * B.enc(np.clip(pc + qc * uu[:, None], 0, 1))

    def resid(p):
        return np.concatenate([(model(p, X, u) - Yt).ravel(), 0.05 * 255 * p[4:7]])

    fit = least_squares(resid, np.array([0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0]),
                        bounds=([0, 0, 0, 0, -2, -2, -2], [1, 1, 1, 1, 2, 2, 2]))
    rms = float(np.sqrt(np.mean((model(fit.x, X, u) - Yt) ** 2)))

    def transfer(body255):
        shape = body255.shape
        flat = body255.reshape(-1, 3)
        return model(fit.x, flat, B.dec(flat / 255) @ B.W709).reshape(shape)
    return transfer, dict(params=fit.x.tolist(), rms=rms)


#: Coefficient overrides for the sensitivity sweep (sweep.py): kappa and lambda at other values
#: than memo E's readings, to tell a referee that fails whatever the coefficients (by
#: construction) from one that fails at these readings.
OVERRIDE: dict = {}


def candidate_body(variant, ep, scale, bg, comp, span, fl, fx, fy, bt_lensed):
    """The candidate's LINEAR body at the refracted position, or None for identity."""
    if variant == 'identity':
        return None
    if variant == 'e3ctl':
        return B.dec(B.e3_shader(B.enc(bt_lensed) * 255) / 255)
    A, ML, W = B.lt_argument(ep, scale, bg, comp, chroma='M' if variant == 'c1m' else 'W',
                             kappa=None if OVERRIDE.get('kappa') is None else OVERRIDE['kappa'],
                             lam=OVERRIDE.get('lam', B.LAMBDA))
    A = B.sample_image(A, fx, fy, scale)
    ML = B.sample_image(ML, fx, fy, scale)
    W = B.sample_image(W, fx, fy, scale)
    if ep == 'light-receded' and variant in ('c1', 'c2'):
        c1 = B.dec(B.e3_extended(ML, W) / 255)
    elif ep == 'light-receded' and variant == 'c1m':
        LW = W @ B.W709
        c1 = B.dec(np.clip(B.e3_F(ML)[..., None] + B.e3_gain(LW)[..., None] * (A - ML[..., None]),
                           0, 255) / 255)
    else:
        c1 = B.landed_T(ep, scale, comp, A / 255)
    if variant in ('c1', 'c1s', 'c1m'):
        return c1
    # c2: candidate 1's chroma, its luma replaced by the native curve at M's luma (codes).
    enc1 = B.enc(c1) * 255
    L1 = enc1 @ B.W709
    Tn = np.zeros_like(L1)
    for i, s in enumerate(fl.surfaces):
        m = fl.owner == i
        Tn[m] = B.native_T(ep, min(s[3], s[4]), ML[m])
    return B.dec(np.clip(enc1 + (Tn - L1)[..., None], 0, 255) / 255)


def documents(variant, scheme):
    """The rehearsal's candidate documents: the shipped bytes plus one comment naming the
    variant, so the resolved material (and resolvedMaterialSha256) is the shipped one and only
    the file hash moves. Written once, deterministically; returned as (kind, path, sha12)."""
    out = []
    for kind, suffix in (('materialProfile', ''), ('recededProfile', '-receded')):
        name = f'apple-macos-27.0-1x-{scheme}-standard-glass0.5{suffix}.json'
        src = CAL / 'profiles' / name
        dst = DOC_DIR / variant / name
        doc = json.loads(src.read_text())
        doc['$comment-w42-g0-rehearsal'] = (
            f"W42 G0 rehearsal (charter clause 3), variant '{variant}'. NOT a material: these are "
            f"the shipped bytes of {name} (sha256 {hashlib.sha256(src.read_bytes()).hexdigest()}) "
            "with this one key added, so the resolved material and its digest are unchanged. The "
            "captures that name this file were not rendered with it; they are the canonical "
            "shipped captures with the body swapped offline by "
            "results/2026-09-29-w42-g0-declaration/gate/rehearsal/swap.py (see its docstring for "
            "what the variant draws).")
        data = (json.dumps(doc, indent=2, ensure_ascii=False) + '\n').encode()
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_bytes() != data:
            dst.write_bytes(data)
        out.append((kind, str(dst.relative_to(ROOT)), hashlib.sha256(data).hexdigest()[:12]))
    return out


def rename_documents(capture_path, docs):
    import re
    out = capture_path
    for kind, path, sha in docs:
        out, n = re.subn(rf'{kind}=\S+ sha256:[0-9a-f]{{12}}', f'{kind}={path} sha256:{sha}', out)
        assert n == 1, (kind, capture_path)
    return out


#: Apple refracts in a band 20 pt inward from the edge in the ACTIVE pose, vitrea draws its own
#: lens there, and LT does not model refraction (the parent's instruction to the gate stream,
#: 2026-09-29). So an active cell is swapped only beyond the band and the band stays exactly as
#: vitrea drew it; the receded pose, where Apple does not refract, is swapped over the whole body.
ACTIVE_BAND_PT = 20.0


def swap_weight(ep, fl):
    """Where the candidate body replaces the shipped one: the contour's coverage, and in the
    active pose only beyond the refraction band, with a one-device-pixel antialiased boundary."""
    if ep.endswith('receded'):
        return fl.cov
    return np.clip((-fl.d - ACTIVE_BAND_PT) * fl.scale + 0.5, 0.0, 1.0)


def swap_cell(variant, row, out_root, docs):
    profile, scene = row['key']['profileKey'], row['key']['sceneId']
    scale = 2 if '-2x-' in profile else 1
    scheme = 'light' if '-light-' in profile else 'dark'
    bg, comp, _ = scene.split('__')
    ep = B.endpoint_of(scheme, B.pose_of(scene))
    src = CANONICAL / profile / scene
    web = rgb(src / f'{scene}__webgpu.png')
    fl = B.field(comp, scale)
    fx, fy = fl.displacement(ep)
    info = dict(profile=profile, scene=scene, endpoint=ep, variant=variant)
    if variant == 'identity' or (variant == 'e3ctl' and ep != 'light-receded'):
        out = web
        info['moved'] = 0
    else:
        bt, _ = B.shipped_argument(ep, scale, bg, comp, lensed=True)
        ship = B.enc(B.shipped_body(ep, scale, bg, comp, lensed=True)) * 255
        span = min(s[3] for s in fl.surfaces)
        cand = B.enc(candidate_body(variant, ep, scale, bg, comp, span, fl, fx, fy, bt)) * 255
        transfer, tint = tint_model(profile, scene, fl)
        ship_t = ship if transfer is None else transfer(ship)
        cand_t = cand if transfer is None else transfer(cand)
        # The capture is the shipped body ROUNDED plus whatever else the pass drew. Where it is
        # within one code of the replica, the difference is the rounding (and the replica's own
        # error, rms 0.3 in the body): it is dropped, so the candidate is rounded once, as the
        # renderer would round it, and a uniform body cannot inherit a systematic half code.
        # Larger residuals are the rim, the highlight and the edge, and they are carried.
        r = web - ship_t
        q = np.where(np.abs(r) <= 1.0, r, 0.0)
        weight = swap_weight(ep, fl)
        cov = weight[..., None]
        out = np.clip(np.round(web + cov * (cand_t - ship_t - q)), 0, 255)
        inside = fl.d < 0
        info.update(moved=int(np.any(out != web, axis=2).sum()), tint=tint,
                    bodyDeltaCodes=float(np.abs(cand - ship)[inside].mean()),
                    swappedFraction=float(weight[inside].mean()))
    dst = out_root / profile / scene
    dst.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out.astype(np.uint8), 'RGB').save(dst / f'{scene}__webgpu.png')
    for name in os.listdir(src):
        if name.endswith('__webgpu.png') and not name.endswith('__alpha.png'):
            continue
        if 'webgpu' not in name:
            continue
        if name == 'cell__webgpu.json':
            cell = json.loads((src / name).read_text())
            cell['capturePath'] = rename_documents(cell['capturePath'], docs)
            (dst / name).write_text(json.dumps(cell, indent=2) + '\n')
        else:
            shutil.copyfile(src / name, dst / name)
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--variant', choices=VARIANTS, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--profiles', default=','.join(PROFILES))
    ap.add_argument('--scenes', default=None)
    args = ap.parse_args()
    out = args.out.resolve()
    if ROOT in out.parents:
        raise SystemExit('swap: write the tree outside the repository')
    rows = population(args.profiles.split(','))
    if args.scenes:
        keep = set(args.scenes.split(','))
        rows = [r for r in rows if r['key']['sceneId'] in keep]
    docs = {s: documents(args.variant, s) for s in ('light', 'dark')}
    log = []
    t0 = time.time()
    for i, row in enumerate(rows):
        scheme = 'light' if '-light-' in row['key']['profileKey'] else 'dark'
        log.append(swap_cell(args.variant, row, out, docs[scheme]))
        if i % 20 == 0:
            print(f'{i}/{len(rows)} {time.time() - t0:.0f}s', file=sys.stderr)
    (out / f'swap-{args.variant}.json').write_text(json.dumps(dict(
        variant=args.variant, documents={s: [dict(kind=k, path=p, sha12=h) for k, p, h in d]
                                         for s, d in docs.items()},
        cells=log), indent=1) + '\n')
    print(f'{len(rows)} cells -> {out}')


if __name__ == '__main__':
    main()
