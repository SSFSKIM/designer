#!/usr/bin/env python3.12
"""W43 G0 (c → e): fold memo F's reading into the w-test's prediction (clause 2's bar; Design "The w-test").

    python3.12 -B fold.py <reading/tables.json> [--out fold.json]

Clause 2: every declared input that moves with x is written down as a pointer, and the w-test's
prediction is stated in their terms before the hash; an input that moves and that the declaration
cannot state keeps it open. This sorts every input memo F found moving into the role it plays in
LT's algebra (W42 Design, LT; charter Design "The w-test"):

    N = C + λ·max(0, W − C),  M = (1 − w)·N + w·W,  y = T(M)        (light; dark the mirror)

- **C**, the narrow term: the narrow blur's radius, opacities and SDF distances, and the backdrop
  layer's capture scale and margin (they set what C and W average over);
- **W**, the wide term: the blur fill's radius (and the capture scale, shared with C);
- **λ**, the hinge: the fill's Lighten (light) or Darken (dark) opacity;
- **w**, the Normal weight: the fill's Normal opacity, which the w-test varies;
- **T**, everything pointwise after M: the face colour matrix, its fill, MaxLuma, the clamp;
- **outside the deep body**: refraction, the bleed, the shadows and the highlight, which act at the
  edge or outside the deep mask and are not in the free side's support (named, never silently dropped).

The prediction w(0.25) / w(0.5) = 0.5 is declared per endpoint and span stratum on the free side
WHERE NO C- OR W-INPUT MOVES between 0.25 and 0.5, and where the Normal weight reads exactly x at both.
λ and T moving is expected and leaves the free side's prediction intact (λ does not enter it; T is
inverted natively at each position). Anything unclassified is reported as `unclassified`, which keeps
the declaration open until a human classifies it.
"""
import argparse
import json
from pathlib import Path

G = 'glassBackground.input'
ROLES = (
    ('w', (G + 'BlurFillNormalOpacity',)),
    ('lambda', (G + 'BlurFillLightenOpacity', G + 'BlurFillDarkenOpacity')),
    ('C', (G + 'BlurRadius', G + 'BlurOpacity', G + 'BlurDistance', 'bd.scale', 'bd.marginWidth', 'elements',
           'out.effect.minimum', 'out.effect.maximum', 'out.smoothness', 'out.effect.gaussianRadius')),
    ('W', (G + 'BlurFillBlurRadius',)),
    ('T', (G + 'FaceColorMatrix', G + 'FaceOpacity', G + 'Clamp', G + 'MaxHeadroom', G + 'SDRHoldingTone')),
    ('outside', (G + 'InnerRefraction', G + 'OuterRefraction', G + 'Refraction', G + 'Bleed', G + 'Shadow',
                 G + 'RingShadow', G + 'KeyFillHighlight', G + 'SDRGradient', G + 'SDRShadow', G + 'Aberration',
                 'hl.', 'parent.')),
)
SUPPORT_SPANS = {'44', '64', '80', '96'}       # capsule, rrect-64, rrect-80, rrect-md (Design, "The support")


def role_of(field):
    for role, prefixes in ROLES:
        if any(field == p or field.startswith(p) for p in prefixes):
            return role
    return 'unclassified'


def fold(tables):
    out = dict(endpoints={}, unclassified=set())
    for ep, e in tables['endpoints'].items():
        by_role = {}
        for field, by_x in e['moving'].items():
            role = role_of(field)
            if role == 'unclassified':
                out['unclassified'].add(field)
            spans = sorted({s for v in by_x.values() for s in v})
            by_role.setdefault(role, []).append(dict(field=field, xs=sorted(by_x, key=float), spans=spans))
        ramps = e.get('ramps', {})
        moved_at_025 = {f for f, by_x in e['moving'].items() if '0.25' in by_x}
        cw_025 = sorted(f for f in moved_at_025 if role_of(f) in ('C', 'W'))
        cw_025_support = sorted(f for f in cw_025 if set(e['moving'][f]['0.25']) & SUPPORT_SPANS)
        normal = ramps.get(G + 'BlurFillNormalOpacity', {}).get('values', {})
        normal_is_x = all(abs(v - float(x)) < 1e-6 for pts in normal.values() for x, v in pts.items()
                          if v is not None)
        holds = not cw_025_support and normal_is_x
        out['endpoints'][ep] = dict(
            moving=by_role, cOrWMovingAt025=cw_025, cOrWMovingAt025OnSupport=cw_025_support,
            normalEqualsX=normal_is_x,
            prediction=('w(0.25) / w(0.5) = 0.5 on the free side at every support span' if holds else
                        'NOT STATED: a C- or W-input moves at 0.25 on the support, or Normal is not x; the '
                        'declaration stays open until the prediction is restated in its terms (clause 2)'),
            predictionStated=holds)
    out['unclassified'] = sorted(out['unclassified'])
    out['open'] = bool(out['unclassified']) or not all(v['predictionStated'] for v in out['endpoints'].values())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tables', type=Path)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    tables = json.loads(args.tables.read_text())
    tables = tables.get('reading', tables)
    result = fold(tables)
    text = json.dumps(result, indent=1) + '\n'
    if args.out:
        args.out.write_text(text)
    for ep, v in result['endpoints'].items():
        roles = {r: [m['field'].replace(G, '') for m in ms] for r, ms in v['moving'].items()}
        print(f"{ep}: {v['prediction']}\n    moving by role: {roles}")
    print('unclassified:', result['unclassified'] or 'none', '| declaration open:', result['open'])


if __name__ == '__main__':
    main()
