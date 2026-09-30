"""W42 G2 step 3, U2: the band blend's order (the design review's R4).

The rehearsal eases the law in across the active 20 pt band by adding the two bodies' difference to the
shipped capture in ENCODED OUTPUT codes, after the author tint's transfer (`swap.py:322-337`):

    rehearsal  y = t(ship) + w (t(cand) - t(ship)),      w = coverage x smoothstep(0, 20 pt, depth)

where t is the tint composite fitted on the tinted cell against its untinted twin (`swap.tint_model`) and
the identity on an untinted cell. The runtime could reproduce that by running the tint twice, once per
body, or take a cheaper order that blends the untinted bodies first and tints once:

    encoded    y = t(ship + w (cand - ship))                  (the bodies blended in encoded codes)
    linear     y = t(enc(mix(dec ship, dec cand, w)))         (the design's first proposal, §2.7)

The parent admits a cheaper order only if it sits within 0.1 code of the rehearsal on the canonical band
cells, tinted ones included. On an untinted cell `encoded` IS the rehearsal (t is the identity, so both are
ship + w (cand - ship)); the tinted cells are what decide it. This reads every active tinted cell of the
canonical calibration/validation population in all four macOS 27 profiles, for candidate 1 (per-channel
knee, its own chroma, r3-1pnb) and candidate 2 (per-channel, g, r3-2pgb), at the rehearsal's own bodies.
Reads the shipped canonical captures (the gitignored tree the rehearsal read) for the tint fits only.

    taskpolicy -b nice -n 19 env OPENBLAS_NUM_THREADS=1 python3.12 -B u2_band_blend.py
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G0 = os.path.abspath(os.path.join(HERE, '..', '..', '2026-09-29-w42-g0-declaration'))
sys.path.insert(0, os.path.join(G0, 'gate', 'rehearsal'))
import body as B  # noqa: E402
import swap as SW  # noqa: E402

VARIANTS = ('r3-1pnb', 'r3-2pgb')


def main():
    rows = [r for r in SW.population() if '__rest' in r['key']['sceneId']]
    tinted = [r for r in rows if '-tint-' in r['key']['sceneId']]
    untinted = [r for r in rows if '-tint-' not in r['key']['sceneId']][:4]
    out, t0 = [], time.time()
    for row in tinted + untinted:
        profile, scene = row['key']['profileKey'], row['key']['sceneId']
        scale = 2 if '-2x-' in profile else 1
        scheme = 'light' if '-light-' in profile else 'dark'
        bg, comp, _ = scene.split('__')
        ep = B.endpoint_of(scheme, B.pose_of(scene))
        fl = B.field(comp, scale)
        fx, fy = fl.displacement(ep)
        bt, _ = B.shipped_argument(ep, scale, bg, comp, lensed=True)
        ship = B.enc(B.shipped_body(ep, scale, bg, comp, lensed=True)) * 255
        transfer, fit = SW.tint_model(profile, scene, fl)
        t = (lambda x: x) if transfer is None else transfer
        w = SW.swap_weight(ep, fl, 'r3-2pgb')[..., None]
        band = (fl.d < 0) & (-fl.d < SW.BLEND_PT) & (w[..., 0] > 0)
        span = min(s[3] for s in fl.surfaces)
        for variant in VARIANTS:
            cand = B.enc(SW.candidate_body(variant, ep, scale, bg, comp, span, fl, fx, fy, bt)) * 255
            rehearsal = t(ship) + w * (t(cand) - t(ship))
            encoded = t(ship + w * (cand - ship))
            linear = t(255 * B.enc(B.dec(ship / 255) + w * (B.dec(cand / 255) - B.dec(ship / 255))))
            d_enc = np.abs(encoded - rehearsal)[band]
            d_lin = np.abs(linear - rehearsal)[band]
            out.append(dict(profile=profile, scene=scene, variant=variant, tinted=transfer is not None,
                            tintFitRms=None if fit is None else fit['rms'], bandPixels=int(band.sum()),
                            encoded_max=float(d_enc.max()), encoded_p99=float(np.percentile(d_enc, 99)),
                            linear_max=float(d_lin.max()), linear_p99=float(np.percentile(d_lin, 99))))
        print(f'{len(out) // 2}/{len(tinted) + len(untinted)} {profile} {scene} {time.time() - t0:.0f}s',
              file=sys.stderr, flush=True)
    json.dump(out, open(os.path.join(HERE, 'u2_band_blend.json'), 'w'), indent=0)
    lines = ['order against the rehearsal, codes, over the band (0 < depth < 20 pt) of every active cell read:']
    for tinted_flag in (True, False):
        g = [r for r in out if r['tinted'] == tinted_flag]
        if not g:
            continue
        lines.append(f"  {'tinted' if tinted_flag else 'untinted'} ({len(g)} cell-candidates): encoded-before-tint "
                     f"max {max(r['encoded_max'] for r in g):.4f} (p99 {max(r['encoded_p99'] for r in g):.4f}); "
                     f"linear-before-tint max {max(r['linear_max'] for r in g):.3f} "
                     f"(p99 {max(r['linear_p99'] for r in g):.3f})")
    worst = sorted(out, key=lambda r: -r['encoded_max'])[:5]
    lines.append('  the five worst cells for the encoded order:')
    for r in worst:
        lines.append(f"    {r['profile']} {r['scene']} {r['variant']}: {r['encoded_max']:.4f} "
                     f"(tint fit rms {r['tintFitRms']})")
    text = '\n'.join(lines)
    open(os.path.join(HERE, 'u2_band_blend.txt'), 'w').write(
        __doc__.split('\n\n')[0] + '\n\n' + text + f'\n\nrun time {time.time() - t0:.0f} s\n')
    print(text)


if __name__ == '__main__':
    main()
