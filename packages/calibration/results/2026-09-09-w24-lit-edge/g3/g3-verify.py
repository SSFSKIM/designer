#!/usr/bin/env python3
"""W24 G3: the canonical rebuild read against G2's frozen dry run.

The wave's one holdout read was spent at G2's dry run (contract X3), so this landing is only allowed
to REPRODUCE that render — not to take a second reading of it. The proof is a digest per capture: G2
recorded one for all 229 render captures at the frozen configuration (`g2/g2-digests.txt`, with both
profile documents' file sha256 and `resolvedMaterialSha256` above them), and if a byte differs here
then either a constant or the renderer moved between the two runs and the holdout number the wave
publishes came from a configuration that no longer exists. That is a stop, not a finding, and it is
checked first.

G2's dry run passed `--alpha`, so its scratch captures include the declaration-conformance renders
too and the whole tree is comparable — checked as (ii) beside the 229 the digest file names. Every
mover is DIAGNOSED rather than named: the count of differing pixels and the largest code delta over
all four channels, plus whether any differing pixel is in the top rows inside the contour. A
one-code alpha or edge difference is the capture flake the tracker carries; a rim pixel moving is
not, and the numbers here are what tells the two apart.

The other checks:

  * **the rows.** Every matrix row equal to the dry run's to the last decimal — the same render
    measured twice, on every axis the schema carries.
  * **the bed's shape.** 229 cells and the partition `adopted-thresholds.test.ts` asserts, so a
    profile that lost a cell in the rebuild cannot be absorbed by another profile gaining one; the
    per (profile, tier, set) counts printed against the 0.12.0 bed's.
  * **the OKLab ΔE table** per profile, tier and set on the landed matrix, to be read against claims
    §5.109's dry-run figures.

    python3 g3-verify.py <before matrix> <before captures dir> <g2-digests.txt> <dry-run matrix> \
        <dry-run captures dir>

Derived from W23 G2's `g2-verify.py`, whose shape this is.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
P = 'apple-macos-26.5-'
AXES = ('shape', 'perceptual', 'material', 'coherence')
PARTITION = {P + '1x-dark-standard': 26, P + '1x-light-increased-contrast': 17,
             P + '1x-light-reduced-transparency': 16, P + '1x-light-standard': 72,
             P + '2x-dark-standard': 26, P + '2x-light-standard': 72}
CELLS = 229


def load(path):
    best = {}
    for cell in json.load(open(path))['cells']:
        key = (cell['key']['profileKey'], cell['key']['web']['renderer'], cell['key']['sceneId'])
        if key not in best or cell['capturedAt'] > best[key]['capturedAt']:
            best[key] = cell
    return best


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def diagnose(a_path, b_path):
    """The shape of a difference: how many pixels, how far, and where."""
    try:
        from PIL import Image
    except ImportError:
        return 'PIL absent — not diagnosed'
    a = Image.open(a_path).convert('RGBA')
    b = Image.open(b_path).convert('RGBA')
    if a.size != b.size:
        return f'SIZE {a.size} against {b.size}'
    pa, pb = a.load(), b.load()
    count = 0
    worst = 0
    channels = set()
    top = 0
    ys = []
    for y in range(a.size[1]):
        for x in range(a.size[0]):
            va, vb = pa[x, y], pb[x, y]
            if va == vb:
                continue
            count += 1
            for i, name in enumerate('rgba'):
                d = abs(va[i] - vb[i])
                if d:
                    channels.add(name)
                    worst = max(worst, d)
            if y < 8:
                top += 1
            if len(ys) < 6:
                ys.append((x, y))
    return (f'{count} px of {a.size[0] * a.size[1]}, max code delta {worst}, '
            f"channels {''.join(sorted(channels))}, {top} in the top 8 rows, first at "
            f"{', '.join(f'({x},{y})' for x, y in ys)}")


def metrics(cell):
    out = {}
    for axis in AXES:
        for metric, entry in (cell.get(axis) or {}).items():
            if isinstance(entry, dict) and isinstance(entry.get('value'), (int, float)):
                out[f'{axis}.{metric}'] = entry['value']
            elif isinstance(entry, (int, float)):
                out[f'{axis}.{metric}'] = entry
    return out


def tree(root):
    out = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith('.png'):
                path = os.path.join(base, name)
                out[os.path.relpath(path, root)] = path
    return out


def main():
    before_path, before_caps, digests_path, dry_path, dry_caps = sys.argv[1:6]
    canon = load(os.path.join(CAL, 'results', 'matrix.json'))
    before = load(before_path)
    dry = load(dry_path)
    captures = os.path.join(CAL, 'web-captures')

    print(f"canonical: {len(canon)} cells; the 0.12.0 bed: {len(before)}; the dry run: {len(dry)}")
    lost = sorted(k for k in dry if k not in canon)
    new = sorted(k for k in canon if k not in dry)
    print(f"rows on the dry run and not on the canonical bed: {lost if lost else 'none'}; "
          f"new rows: {new if new else 'none'}")

    # ------------------------------------------------- (i) X3 — G3's declared digests
    print("\n(i) X3 — every landed capture reproduces G3's declared digest, byte for byte:")
    declared = {}
    header = []
    for line in open(digests_path):
        parts = line.split()
        if len(parts) == 2 and len(parts[0]) == 64 and parts[1].endswith('.png'):
            declared[parts[1]] = parts[0]
        elif 'sha256' in line or 'resolvedMaterialSha256' in line:
            header.append(line.rstrip())
    for line in header:
        print('    ' + line.strip())
    live = dict(tree(captures))
    checked = matched = 0
    voided = []
    missing = []
    for name, want in sorted(declared.items()):
        if name not in live:
            missing.append(name)
            continue
        checked += 1
        got = sha(live[name])
        if got == want:
            matched += 1
        else:
            voided.append((name, want, got))
    print(f"    {checked} of {len(declared)} declared captures found and hashed; "
          f"{matched} identical, {len(voided)} MOVED, {len(missing)} MISSING")
    for name in missing:
        print(f"    MISSING  {name}")
    dry_tree = tree(dry_caps)
    for name, want, got in voided:
        print(f"    MOVED    {name}\n             declared {want}\n             landed   {got}")
        if name in dry_tree:
            print(f"             {diagnose(dry_tree[name], live[name])}")

    # ------------------------------------------- (ii) the whole tree against the dry run
    print("\n(ii) the whole capture tree against the dry run's, alpha renders included:")
    only_landed = sorted(set(live) - set(dry_tree))
    only_dry = sorted(set(dry_tree) - set(live))
    same = diff = 0
    movers = []
    for name in sorted(set(live) & set(dry_tree)):
        if sha(live[name]) == sha(dry_tree[name]):
            same += 1
        else:
            diff += 1
            movers.append(name)
    print(f"    {len(live)} landed, {len(dry_tree)} in the dry run; {same} identical, {diff} moved")
    for name in only_landed:
        print(f"    ONLY LANDED  {name}")
    for name in only_dry:
        print(f"    ONLY DRY RUN {name}")
    for name in movers:
        print(f"    MOVED        {name}\n                 {diagnose(dry_tree[name], live[name])}")

    # ---------------------------------------------------------- (iii) the rows
    print("\n(iii) every matrix row against the dry run's, to the last decimal:")
    rows = moved = 0
    worst = []
    for key in sorted(set(canon) & set(dry)):
        a, b = metrics(canon[key]), metrics(dry[key])
        for metric in sorted(set(a) | set(b)):
            rows += 1
            va, vb = a.get(metric), b.get(metric)
            if va != vb:
                moved += 1
                worst.append((abs((va or 0) - (vb or 0)), key, metric, vb, va))
    print(f"    {rows} rows compared; {moved} differ")
    for delta, key, metric, was, now in sorted(worst, reverse=True)[:40]:
        print(f"    {key} :: {metric}  dry {was} -> landed {now}  (|Δ| {delta})")

    # ---------------------------------------------------------- (iv) the shape
    print("\n(iv) the bed's shape:")
    counts = {}
    for profile, _renderer, _scene in canon:
        counts[profile] = counts.get(profile, 0) + 1
    ok = len(canon) == CELLS and counts == PARTITION
    print(f"    {len(canon)} cells (expected {CELLS}); partition "
          f"{'MATCHES' if counts == PARTITION else 'DIFFERS'}")
    for profile in sorted(PARTITION):
        print(f"      {profile}: {counts.get(profile, 0)} (expected {PARTITION[profile]})")
    print(f"    verdict: {'ok' if ok else 'FAILED'}")

    print("\n    per (profile, tier, set), landed against the 0.12.0 bed:")
    part = {}
    for key, cell in canon.items():
        part.setdefault((key[0], cell['tier'], cell['fixtureSet']), 0)
        part[(key[0], cell['tier'], cell['fixtureSet'])] += 1
    was = {}
    for key, cell in before.items():
        was.setdefault((key[0], cell['tier'], cell['fixtureSet']), 0)
        was[(key[0], cell['tier'], cell['fixtureSet'])] += 1
    for key in sorted(set(part) | set(was)):
        flag = '' if part.get(key) == was.get(key) else '   <-- MOVED'
        print(f"      {key[0]:44s} {key[1]:8s} {key[2]:12s} {part.get(key, 0):3d}"
              f" (0.12.0 bed {was.get(key, 0)}){flag}")

    # ---------------------------------------------------------- (v) the ΔE table
    print("\n(v) OKLab ΔE mean per profile, tier and set, on the landed bed "
          "(the 0.12.0 bed's beside):")
    acc = {}
    old = {}
    for key, cell in canon.items():
        entry = (cell.get('perceptual') or {}).get('oklabDeltaEMean')
        if entry is None:
            continue
        value = entry['value'] if isinstance(entry, dict) else entry
        acc.setdefault((key[0], cell['tier'], cell['fixtureSet']), []).append(value)
    for key, cell in before.items():
        entry = (cell.get('perceptual') or {}).get('oklabDeltaEMean')
        if entry is None:
            continue
        value = entry['value'] if isinstance(entry, dict) else entry
        old.setdefault((key[0], cell['tier'], cell['fixtureSet']), []).append(value)
    for key in sorted(acc):
        values = acc[key]
        prev = old.get(key)
        prev_s = f"{sum(prev) / len(prev):.5f}" if prev else '   n/a'
        print(f"      {key[0]:44s} {key[1]:8s} {key[2]:12s} n={len(values):3d} "
              f"0.12.0 {prev_s} -> landed {sum(values) / len(values):.5f}")

    print("\nVERDICT: " + ('every capture and every row reproduces the dry run'
                          if not voided and not missing and not movers and not moved and ok
                          else 'SEE THE MISMATCHES ABOVE'))


main()
