#!/usr/bin/env python3
"""W21 G2: what claims §5.15's margin rule would give the dark pair's four tables now.

A PROPOSAL, not an adoption. W21 Decision Log 3 (d) keeps the dark bounds a user decision, and
`adopted-thresholds.test.ts` is left holding every current bound exactly as it was. This script
exists so that the decision is made against numbers rather than against an impression that the dark
scheme improved — and the numbers cut both ways. On the texture tier the rule would tighten seven of
eight rows; on the dom tier it would have to LOOSEN four, because the CSS tier's structured-backdrop
residual (W21 Decision Log 3 (a)) took the nested pane's rows backwards. A loosening is not
something this rule may be used to authorise: the founding rule is that nothing is widened and the
claim narrows in writing. Those rows are named in `g2-gate.txt` and belong to the parent.

The rule, as the doc comment above `TEXTURE_TIER_DARK` states it: for a `≤` row the smallest
half-step reaching 1.4× the worst measurement (a 1% step for the unitless rows), for a `≥` row 0.02
below the worst, floored to the hundredth; and the worst is taken over the CALIBRATION and HOLDOUT
columns both, not the holdout alone, because a table a calibration cell violates is not enforceable.
Shape rows are read only over the cells the conditioning predicate admits, exactly as the gate reads
them; perceptual rows cover every cell of the profile and tier.

The script prints each table against two beds — the W20 bed and the landed one — so that the rule
can be seen reproducing the adopted bounds where the bed did not move, which is the check that it is
the same rule the gate was set by.

    python3 g2-dark-bounds.py <W20 bed matrix>
"""
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
P = 'apple-macos-26.5-'
COLUMNS = ('calibration', 'holdout')
AREA_RATIO = 0.95

# The four tables as `adopted-thresholds.test.ts` holds them today.
TABLES = {
    (P + '1x-dark-standard', 'texture', 'TEXTURE_TIER_DARK'): [
        ('shape', 'silhouetteIoU', '≥', 0.93), ('shape', 'contourDistanceMean', '≤', 0.5),
        ('shape', 'contourDistanceP95', '≤', 1.5), ('perceptual', 'ssimMean', '≥', 0.87),
        ('perceptual', 'oklabDeltaEMean', '≤', 0.09), ('perceptual', 'oklabDeltaEP95', '≤', 0.17),
        ('perceptual', 'edgeWeightedMean', '≤', 0.04), ('perceptual', 'ssimOutside', '≥', 0.83)],
    (P + '1x-dark-standard', 'dom', 'DOM_TIER_DARK'): [
        ('shape', 'silhouetteIoU', '≥', 0.93), ('shape', 'contourDistanceMean', '≤', 0.5),
        ('shape', 'contourDistanceP95', '≤', 1.5), ('perceptual', 'ssimMean', '≥', 0.83),
        ('perceptual', 'oklabDeltaEMean', '≤', 0.09), ('perceptual', 'oklabDeltaEP95', '≤', 0.18),
        ('perceptual', 'edgeWeightedMean', '≤', 0.05), ('perceptual', 'ssimOutside', '≥', 0.78)],
    (P + '2x-dark-standard', 'texture', 'TEXTURE_TIER_2X_DARK'): [
        ('shape', 'silhouetteIoU', '≥', 0.93), ('shape', 'contourDistanceMean', '≤', 1.0),
        ('shape', 'contourDistanceP95', '≤', 1.5), ('perceptual', 'ssimMean', '≥', 0.88),
        ('perceptual', 'oklabDeltaEMean', '≤', 0.09), ('perceptual', 'oklabDeltaEP95', '≤', 0.17),
        ('perceptual', 'edgeWeightedMean', '≤', 0.04), ('perceptual', 'ssimOutside', '≥', 0.86)],
    (P + '2x-dark-standard', 'dom', 'DOM_TIER_2X_DARK'): [
        ('shape', 'silhouetteIoU', '≥', 0.93), ('shape', 'contourDistanceMean', '≤', 0.5),
        ('shape', 'contourDistanceP95', '≤', 3.0), ('perceptual', 'ssimMean', '≥', 0.85),
        ('perceptual', 'oklabDeltaEMean', '≤', 0.09), ('perceptual', 'oklabDeltaEP95', '≤', 0.19),
        ('perceptual', 'edgeWeightedMean', '≤', 0.05), ('perceptual', 'ssimOutside', '≥', 0.82)],
}
# A half-pixel step for the contour rows, which are device-pixel quantities; a 1% step for the
# unitless ones (§5.15, and the doc comment the dark tables carry).
STEP = {'contourDistanceMean': 0.5, 'contourDistanceP95': 0.5}


def load(path):
    best = {}
    for cell in json.load(open(path))['cells']:
        key = (cell['key']['profileKey'], cell['key']['web']['renderer'], cell['key']['sceneId'])
        if key not in best or cell['capturedAt'] > best[key]['capturedAt']:
            best[key] = cell
    return best


def value(cell, axis, metric):
    entry = (cell.get(axis) or {}).get(metric)
    if entry is None:
        return None
    return entry['value'] if isinstance(entry, dict) else entry


def conditions(cell):
    if cell.get('shape') is None:
        return False
    at = lambda m: value(cell, 'shape', m)
    return (at('silhouetteAreaNative') >= AREA_RATIO * at('componentRegionArea')
            and at('silhouetteAreaWeb') >= AREA_RATIO * at('componentRegionArea')
            and at('silhouetteBodiesNative') <= at('componentRegionBodies')
            and at('silhouetteBodiesWeb') <= at('componentRegionBodies'))


def proposed(comparison, metric, worst):
    if comparison == '≤':
        step = STEP.get(metric, 0.01)
        return math.ceil((1.4 * worst) / step - 1e-9) * step
    return math.floor((worst - 0.02) * 100 + 1e-9) / 100


def table(matrix, profile, tier, rows):
    renderer = 'webgpu' if tier == 'texture' else 'css'
    cells = [c for k, c in matrix.items()
             if k[0] == profile and k[1] == renderer and c.get('fixtureSet') in COLUMNS]
    out = []
    for axis, metric, comparison, adopted in rows:
        applicable = [c for c in cells if conditions(c)] if axis == 'shape' else cells
        readings = [(value(c, axis, metric), c['key']['sceneId'], c.get('fixtureSet'))
                    for c in applicable if value(c, axis, metric) is not None]
        if not readings:
            out.append((axis, metric, comparison, adopted, None, None, None, 0))
            continue
        worst = min(readings) if comparison == '≥' else max(readings)
        out.append((axis, metric, comparison, adopted, worst[0], worst[1], worst[2],
                    len(readings)))
    return out


def main():
    beds = [('the W20 bed', load(sys.argv[1])),
            ('the landed bed', load(os.path.join(CAL, 'results', 'matrix.json')))]
    print("W21 G2 — the dark pair's four gate tables under claims §5.15's margin rule.")
    print("A PROPOSAL. Nothing here is adopted: W21 Decision Log 3 (d) leaves the dark bounds to the")
    print("user, and the gate is left holding every bound in the `adopted` column exactly as it was.")
    print("Three of those bounds the landed bed MISSES — see `g2-gate.txt`; a proposal is not where")
    print("a missed bound is settled. The rule: `≤` the smallest half-step (1% for the unitless rows)")
    print("reaching 1.4x the worst; `≥` 0.02 below the worst, floored to the hundredth; the worst")
    print("over the calibration and holdout columns both.\n")
    for (profile, tier, name), rows in TABLES.items():
        print(f"=== {name} — {profile}, {tier} tier ===")
        print(f"  {'row':22s} {'cmp':3s} {'adopted':>8s}  "
              f"{'W20 worst':>10s} {'W20 rule':>9s}  {'landed worst':>13s} {'landed rule':>12s}  "
              f"{'move':>6s}  driving cell (landed)")
        computed = {}
        for label, bed in beds:
            for row in table(bed, profile, tier, rows):
                computed[(label, row[1])] = row
        for axis, metric, comparison, adopted in [(a, m, c, t) for a, m, c, t in rows]:
            old = computed[('the W20 bed', metric)]
            new = computed[('the landed bed', metric)]
            if old[4] is None or new[4] is None:
                print(f"  {metric:22s} {comparison:3s} {adopted:8.2f}  "
                      f"{'no reading':>10s}")
                continue
            old_rule = proposed(comparison, metric, old[4])
            new_rule = proposed(comparison, metric, new[4])
            # The adopted column was derived by this rule on the bed of 2026-09-01 (claims §5.28),
            # not on the W20 bed. Where the two disagree the BED moved between those dates — eleven
            # of the 32 rows — and saying so beside the row keeps the rule's identity checkable.
            reproduces = '' if abs(old_rule - adopted) < 1e-9 else '  (the bed moved since the 2026-09-01 adoption)'
            tighter = 'tighter' if ((comparison == '≤' and new_rule < adopted) or
                                    (comparison == '≥' and new_rule > adopted)) else (
                'same' if abs(new_rule - adopted) < 1e-9 else 'LOOSER')
            print(f"  {metric:22s} {comparison:3s} {adopted:8.2f}  "
                  f"{old[4]:10.4f} {old_rule:9.2f}  {new[4]:13.4f} {new_rule:12.2f}  "
                  f"{tighter:>7s}  {new[5]} ({new[6]}, n={new[7]}){reproduces}")
        print()


if __name__ == '__main__':
    main()
