#!/usr/bin/env python3
"""W22 G2: the well-conditioned predicate re-derived from the LANDED matrix, and the four cells'
silhouette bodies read on both beds.

`adopted-thresholds.test.ts` asserts that `PREDICATE_EXCLUDES` equals the machine's own output, so
the list is a derivation and not a decision. This prints that derivation directly off the committed
artifact — the same four arms the test reads (`silhouetteAreaNative` / `Web` against 0.95 of
`componentRegionArea`, `silhouetteBodiesNative` / `Web` against `componentRegionBodies`) — beside the
list the file carries, and then reads the four cells W22 removes on the W21 bed and on this one so
the reason is attributable rather than asserted.

    python3 g2-predicate.py <before matrix>
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
RATIO = 0.95
ARMS = ('silhouetteAreaNative', 'silhouetteAreaWeb', 'silhouetteBodiesNative',
        'silhouetteBodiesWeb', 'componentRegionArea', 'componentRegionBodies')


def load(path):
    best = {}
    for cell in json.load(open(path))['cells']:
        key = (cell['key']['profileKey'], cell['tier'], cell['key']['sceneId'])
        if key not in best or cell['capturedAt'] > best[key]['capturedAt']:
            best[key] = cell
    return best


def at(cell, metric):
    entry = (cell.get('shape') or {}).get(metric)
    if entry is None:
        return None
    return entry['value'] if isinstance(entry, dict) else entry


def name(profile, cell):
    return f"{cell['tier']} / {cell['fixtureSet']} / {cell['key']['sceneId']} / {profile}"


def excluded(cells):
    out = []
    for (profile, _tier, _scene), cell in cells.items():
        if cell.get('shape') is None:
            continue
        area = at(cell, 'componentRegionArea')
        bodies = at(cell, 'componentRegionBodies')
        if area is None or bodies is None:
            continue
        ok = (at(cell, 'silhouetteAreaNative') >= RATIO * area
              and at(cell, 'silhouetteAreaWeb') >= RATIO * area
              and at(cell, 'silhouetteBodiesNative') <= bodies
              and at(cell, 'silhouetteBodiesWeb') <= bodies)
        if not ok:
            out.append(name(profile, cell))
    return sorted(out)


def in_file():
    source = open(os.path.join(CAL, 'test', 'adopted-thresholds.test.ts')).read()
    block = source.split('const PREDICATE_EXCLUDES = [', 1)[1].split('] as const;', 1)[0]
    return re.findall(r'"([^"]+)"', block)


def main():
    before = load(sys.argv[1])
    landed = load(os.path.join(CAL, 'results', 'matrix.json'))

    machine = excluded(landed)
    listed = in_file()
    print(f"the machine's derivation off the landed matrix: {len(machine)} lines")
    for line in machine:
        print(f"    {line}")
    print(f"\nPREDICATE_EXCLUDES as the file carries it: {len(listed)} lines")
    print(f"equal: {machine == sorted(listed)}")
    for line in sorted(set(machine) - set(listed)):
        print(f"    ONLY THE MACHINE  {line}")
    for line in sorted(set(listed) - set(machine)):
        print(f"    ONLY THE FILE     {line}")

    print("\nwhat the W21 bed excluded that this one does not:")
    was = excluded(before)
    for line in sorted(set(was) - set(machine)):
        print(f"    LEAVES  {line}")
    for line in sorted(set(machine) - set(was)):
        print(f"    JOINS   {line}")

    print("\nthe four cells W22 removes, read on both beds "
          "(area native/web against 0.95 × region, bodies native/web against region bodies):")
    four = [('apple-macos-26.5-2x-light-standard', 'texture', scene) for scene in (
        'checkerboard__rrect-md__rest', 'checkerboard__rrect-ml__rest',
        'checkerboard__glass-over-glass__rest', 'checkerboard__rrect-lg__rest')]
    for key in four:
        for label, bed in (('W21 bed', before), ('landed ', landed)):
            cell = bed.get(key)
            if cell is None:
                print(f"    {key[2]:40s} {label}  ABSENT")
                continue
            area = at(cell, 'componentRegionArea')
            print(f"    {key[2]:40s} {label}  region {area:8.0f}/{at(cell, 'componentRegionBodies'):.0f}"
                  f"  areaNative {at(cell, 'silhouetteAreaNative'):8.0f}"
                  f"  areaWeb {at(cell, 'silhouetteAreaWeb'):8.0f}"
                  f"  bodiesNative {at(cell, 'silhouetteBodiesNative'):.0f}"
                  f"  bodiesWeb {at(cell, 'silhouetteBodiesWeb'):.0f}"
                  f"  IoU {at(cell, 'silhouetteIoU'):.5f}"
                  f"  contourMean {at(cell, 'contourDistanceMean'):.4f}"
                  f"  P95 {at(cell, 'contourDistanceP95'):.0f}")


main()
