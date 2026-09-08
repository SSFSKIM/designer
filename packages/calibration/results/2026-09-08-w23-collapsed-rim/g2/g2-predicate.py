#!/usr/bin/env python3
"""W23 G2: the gate's three derived lists re-derived from the LANDED matrix.

`adopted-thresholds.test.ts` asserts that each of them equals the machine's own output, so they are
derivations and not decisions. This prints all three directly off the committed artifact, beside the
lists the file carries, and reads the cells that move on both beds so the reason for each is
attributable rather than asserted.

  1. **`PREDICATE_EXCLUDES`** — the four arms the test reads (`silhouetteAreaNative` / `Web` against
     0.95 of `componentRegionArea`, `silhouetteBodiesNative` / `Web` against
     `componentRegionBodies`).
  2. **the no-shape scenes** — the cells carrying no `shape` axis at all, per profile AND per tier,
     which is what the count assertion at `adopted-thresholds.test.ts:1332` compares
     `NO_SHAPE_AXIS_SCENES` against on each tier separately.
  3. **the no-interior scenes** — the dom cells with no `coherence.interiorLevelRatioGpuOverCss`,
     which the coherence rows require to be named in the same list.

    python3 g2-predicate.py <before matrix>
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
RATIO = 0.95


def load(path):
    best = {}
    for cell in json.load(open(path))['cells']:
        key = (cell['key']['profileKey'], cell['tier'], cell['key']['sceneId'])
        if key not in best or cell['capturedAt'] > best[key]['capturedAt']:
            best[key] = cell
    return best


def at(cell, metric, axis='shape'):
    entry = (cell.get(axis) or {}).get(metric)
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


def arms(cell):
    """Which of the four arms fires, with its numbers."""
    area = at(cell, 'componentRegionArea')
    bodies = at(cell, 'componentRegionBodies')
    fired = []
    if at(cell, 'silhouetteAreaNative') < RATIO * area:
        fired.append(f"areaNative {at(cell, 'silhouetteAreaNative'):.0f} < {RATIO * area:.0f}")
    if at(cell, 'silhouetteAreaWeb') < RATIO * area:
        fired.append(f"areaWeb {at(cell, 'silhouetteAreaWeb'):.0f} < {RATIO * area:.0f}")
    if at(cell, 'silhouetteBodiesNative') > bodies:
        fired.append(f"bodiesNative {at(cell, 'silhouetteBodiesNative'):.0f} > {bodies:.0f}")
    if at(cell, 'silhouetteBodiesWeb') > bodies:
        fired.append(f"bodiesWeb {at(cell, 'silhouetteBodiesWeb'):.0f} > {bodies:.0f}")
    return fired


def in_file(constant):
    source = open(os.path.join(CAL, 'test', 'adopted-thresholds.test.ts')).read()
    block = source.split(f'const {constant} = [', 1)[1].split('] as const;', 1)[0]
    return re.findall(r'"([^"]+)"', block)


def no_shape(cells):
    out = {}
    for (profile, tier, scene), cell in cells.items():
        if cell.get('shape') is None:
            out.setdefault((profile, tier), []).append(scene)
    return {k: sorted(v) for k, v in out.items()}


def no_interior(cells):
    out = {}
    for (profile, tier, scene), cell in cells.items():
        if tier != 'dom':
            continue
        if (cell.get('coherence') or {}).get('interiorLevelRatioGpuOverCss') is None:
            out.setdefault(profile, []).append(scene)
    return {k: sorted(v) for k, v in out.items()}


def main():
    before = load(sys.argv[1])
    landed = load(os.path.join(CAL, 'results', 'matrix.json'))

    # ------------------------------------------------------ 1. PREDICATE_EXCLUDES
    machine = excluded(landed)
    listed = in_file('PREDICATE_EXCLUDES')
    print(f"1. the machine's derivation off the landed matrix: {len(machine)} lines")
    for line in machine:
        print(f"    {line}")
    print(f"\nPREDICATE_EXCLUDES as the file carries it: {len(listed)} lines")
    print(f"equal: {machine == sorted(listed)}")
    for line in sorted(set(machine) - set(listed)):
        print(f"    ONLY THE MACHINE  {line}")
    for line in sorted(set(listed) - set(machine)):
        print(f"    ONLY THE FILE     {line}")

    was = excluded(before)
    print("\nwhat the 0.11.0 bed excluded that this one does not, and what joins:")
    index = {}
    for (profile, tier, scene), cell in landed.items():
        index[name(profile, cell)] = (profile, tier, scene)
    was_index = {}
    for (profile, tier, scene), cell in before.items():
        was_index[name(profile, cell)] = (profile, tier, scene)
    def show(c):
        if c is None:
            return "ABSENT"
        if c.get('shape') is None:
            return "NO SHAPE AXIS — the extractor found nothing to measure"
        return (f"region {at(c, 'componentRegionArea'):.0f}/{at(c, 'componentRegionBodies'):.0f}"
                f"  areaNative {at(c, 'silhouetteAreaNative'):.0f}"
                f"  areaWeb {at(c, 'silhouetteAreaWeb'):.0f}"
                f"  bodiesNative {at(c, 'silhouetteBodiesNative'):.0f}"
                f"  bodiesWeb {at(c, 'silhouetteBodiesWeb'):.0f}"
                f"  IoU {at(c, 'silhouetteIoU'):.5f}   arms: {'; '.join(arms(c)) or 'none'}")

    for verb, lines in (('LEAVES', sorted(set(was) - set(machine))),
                        ('JOINS ', sorted(set(machine) - set(was)))):
        for line in lines:
            print(f"    {verb}  {line}")
            print(f"            0.11.0  {show(before.get(was_index.get(line)))}")
            print(f"            landed  {show(landed.get(index.get(line)))}")

    # ------------------------------------------------------ 2. the no-shape scenes
    print("\n2. the cells carrying no `shape` axis, per profile and TIER "
          "(0.11.0 bed -> landed):")
    now, then = no_shape(landed), no_shape(before)
    for key in sorted(set(now) | set(then)):
        flag = '' if now.get(key, []) == then.get(key, []) else '   <-- MOVED'
        print(f"    {key[0]:44s} {key[1]:8s} {then.get(key, [])} -> {now.get(key, [])}{flag}")

    # ------------------------------------------------------ 3. the no-interior scenes
    print("\n3. the dom cells with no `coherence.interiorLevelRatioGpuOverCss` "
          "(0.11.0 bed -> landed):")
    now_i, then_i = no_interior(landed), no_interior(before)
    for key in sorted(set(now_i) | set(then_i)):
        flag = '' if now_i.get(key, []) == then_i.get(key, []) else '   <-- MOVED'
        print(f"    {key:44s} {then_i.get(key, [])} -> {now_i.get(key, [])}{flag}")

    # ------------------------------------------------------ 4. the collapsed capsule and rrect
    print("\n4. the two scenes the rim moved, read on both beds:")
    for scene in ('dark-solid__capsule-button__rest', 'dark-solid__rrect-md__rest'):
        for (profile, tier, sid), cell in sorted(landed.items()):
            if sid != scene:
                continue
            old = before.get((profile, tier, sid))
            def show(c):
                if c is None or c.get('shape') is None:
                    return 'no shape axis'
                return (f"areaNative {at(c, 'silhouetteAreaNative'):.0f}"
                        f"  areaWeb {at(c, 'silhouetteAreaWeb'):.0f}"
                        f"  region {at(c, 'componentRegionArea'):.0f}"
                        f"  bodiesWeb {at(c, 'silhouetteBodiesWeb'):.0f}"
                        f"/{at(c, 'componentRegionBodies'):.0f}"
                        f"  IoU {at(c, 'silhouetteIoU'):.5f}")
            print(f"    {scene:42s} {tier:8s} {profile}")
            print(f"        0.11.0  {show(old)}")
            print(f"        landed  {show(cell)}")


main()
