#!/usr/bin/env python3
"""W25 G4: the canonical rebuild read against G3b's frozen dry run.

The wave's one holdout read was spent at G3b's dry run (contract X3), so this landing is only
allowed to REPRODUCE that render — not to take a second reading of it. The proof is a digest per
capture: G3b recorded one for all 229 render captures at the frozen configuration
(`g3/g3b-digests.txt`, with both profile documents' file sha256 and `resolvedMaterialSha256` above
them), and if a byte differs here then either a constant or the renderer moved between the two runs
and the holdout number the wave publishes came from a configuration that no longer exists.

This wave's landing has a second bed to referee, and it is not in the digest file. The PROBE set
was captured on the web only in the fitting ladder's scratch, whose last rung `rPAIR` is the landing
pair — so the probe half of the referee is the whole capture tree of that rung and its matrix,
compared cell for cell. The rung's documents are the ladder's patched copies (`sha256:479f9ad2` and
`e13f8cf2`) rather than the re-recorded ones on disk, so the KEYS differ by construction and only
the pixels and the readings can be compared: a byte-identical capture is the proof that the two
documents resolved to the same material.

Every mover is DIAGNOSED rather than named: the count of differing pixels and the largest code delta
over all four channels, plus whether any differing pixel is in the top rows inside the contour. A
one-code alpha or edge difference is the capture flake the tracker carries; a rim pixel moving is
not, and the numbers here are what tells the two apart.

    g4-verify.py <before matrix> <before captures> <g3b-digests.txt> <dry-run matrix> \
        <dry-run captures> <probe matrix> <probe captures>

W24 G3's `g3-verify.py`, with the probe half added.
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


def load(path, probe=None):
    """The newest cell per (profile, renderer, scene), optionally only the probe rows or only not."""
    best = {}
    for cell in json.load(open(path))['cells']:
        if probe is True and cell['fixtureSet'] != 'probe':
            continue
        if probe is False and cell['fixtureSet'] == 'probe':
            continue
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
            for i, name_ in enumerate('rgba'):
                d = abs(va[i] - vb[i])
                if d:
                    channels.add(name_)
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


def tree(root, scenes=None):
    out = {}
    for base, _dirs, files in os.walk(root):
        for name_ in files:
            if not name_.endswith('.png'):
                continue
            path = os.path.join(base, name_)
            relative = os.path.relpath(path, root)
            if scenes is not None and relative.split(os.sep)[1] not in scenes:
                continue
            out[relative] = path
    return out


def compare_rows(landed, reference, label):
    print(f"\n{label}")
    rows = moved = 0
    worst = []
    only_landed = sorted(set(landed) - set(reference))
    only_ref = sorted(set(reference) - set(landed))
    for key in sorted(set(landed) & set(reference)):
        a, b = metrics(landed[key]), metrics(reference[key])
        for metric in sorted(set(a) | set(b)):
            rows += 1
            va, vb = a.get(metric), b.get(metric)
            if va != vb:
                moved += 1
                worst.append((abs((va or 0) - (vb or 0)), key, metric, vb, va))
    print(f"    {len(landed)} landed cells, {len(reference)} reference cells, "
          f"{len(set(landed) & set(reference))} in common; {rows} rows compared; {moved} differ")
    for key in only_landed:
        print(f"    ONLY LANDED    {key}")
    for key in only_ref:
        print(f"    ONLY REFERENCE {key}")
    for delta, key, metric, was, now in sorted(worst, reverse=True)[:40]:
        print(f"    {key} :: {metric}  reference {was} -> landed {now}  (|Δ| {delta})")
    return moved, only_landed, only_ref


def compare_tree(live, reference, label):
    print(f"\n{label}")
    only_landed = sorted(set(live) - set(reference))
    only_ref = sorted(set(reference) - set(live))
    same = diff = 0
    movers = []
    for name_ in sorted(set(live) & set(reference)):
        if sha(live[name_]) == sha(reference[name_]):
            same += 1
        else:
            diff += 1
            movers.append(name_)
    print(f"    {len(live)} landed, {len(reference)} in the reference; {same} identical, "
          f"{diff} moved")
    for name_ in only_landed:
        print(f"    ONLY LANDED    {name_}")
    for name_ in only_ref:
        print(f"    ONLY REFERENCE {name_}")
    for name_ in movers:
        print(f"    MOVED          {name_}\n                   "
              f"{diagnose(reference[name_], live[name_])}")
    return movers


def main():
    (before_path, before_caps, digests_path, dry_path, dry_caps,
     probe_path, probe_caps) = sys.argv[1:8]
    canon = load(os.path.join(CAL, 'results', 'matrix.json'), probe=False)
    canon_probe = load(os.path.join(CAL, 'results', 'matrix.json'), probe=True)
    before = load(before_path)
    dry = load(dry_path)
    probe = load(probe_path)
    captures = os.path.join(CAL, 'web-captures')

    print(f"canonical: {len(canon)} gated cells and {len(canon_probe)} probe cells; "
          f"the 0.13.0 bed: {len(before)}; the dry run: {len(dry)}; the probe rung: {len(probe)}")

    # ------------------------------------------------- (i) X3 — G3b's declared digests
    print("\n(i) X3 — every landed capture reproduces G3b's declared digest, byte for byte:")
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
    for name_, want in sorted(declared.items()):
        if name_ not in live:
            missing.append(name_)
            continue
        checked += 1
        got = sha(live[name_])
        if got == want:
            matched += 1
        else:
            voided.append((name_, want, got))
    print(f"    {checked} of {len(declared)} declared captures found and hashed; "
          f"{matched} identical, {len(voided)} MOVED, {len(missing)} MISSING")
    for name_ in missing:
        print(f"    MISSING  {name_}")
    dry_tree = tree(dry_caps)
    for name_, want, got in voided:
        print(f"    MOVED    {name_}\n             declared {want}\n             landed   {got}")
        if name_ in dry_tree:
            print(f"             {diagnose(dry_tree[name_], live[name_])}")

    # ------------------------------------------- (ii) the gated tree against the dry run
    gated_scenes = {scene for _p, _r, scene in canon}
    probe_scenes = {scene for _p, _r, scene in canon_probe}
    live_gated = tree(captures, gated_scenes)
    live_probe = tree(captures, probe_scenes)
    movers = compare_tree(
        live_gated, dry_tree,
        "(ii) the gated capture tree against the dry run's, alpha renders included:")

    # ------------------------------------------- (iii) the probe tree against the rung's
    probe_movers = compare_tree(
        live_probe, tree(probe_caps),
        "(iii) the probe capture tree against the landing rung's (`rPAIR`), alpha included — "
        "the rung captured the GPU tier only, so its CSS renders have no reference here:")

    # ---------------------------------------------------------- (iv) the rows
    moved, lost, new = compare_rows(
        canon, dry, "(iv) every gated matrix row against the dry run's, to the last decimal:")
    probe_moved, probe_lost, probe_new = compare_rows(
        canon_probe, probe,
        "(v) every probe matrix row against the rung's, to the last decimal:")

    # ---------------------------------------------------------- (vi) the shape
    print("\n(vi) the gated bed's shape:")
    counts = {}
    for profile, _renderer, _scene in canon:
        counts[profile] = counts.get(profile, 0) + 1
    ok = len(canon) == CELLS and counts == PARTITION
    print(f"    {len(canon)} cells (expected {CELLS}); partition "
          f"{'MATCHES' if counts == PARTITION else 'DIFFERS'}")
    for profile in sorted(PARTITION):
        print(f"      {profile}: {counts.get(profile, 0)} (expected {PARTITION[profile]})")
    print(f"    verdict: {'ok' if ok else 'FAILED'}")

    print("\n    per (profile, tier, set), landed against the 0.13.0 bed:")
    part = {}
    for key, cell in list(canon.items()) + list(canon_probe.items()):
        part.setdefault((key[0], cell['tier'], cell['fixtureSet']), 0)
        part[(key[0], cell['tier'], cell['fixtureSet'])] += 1
    was = {}
    for key, cell in before.items():
        was.setdefault((key[0], cell['tier'], cell['fixtureSet']), 0)
        was[(key[0], cell['tier'], cell['fixtureSet'])] += 1
    for key in sorted(set(part) | set(was)):
        flag = '' if part.get(key) == was.get(key) else '   <-- MOVED'
        if key[2] == 'probe':
            flag = '   <-- new this wave, gated by nothing'
        print(f"      {key[0]:44s} {key[1]:8s} {key[2]:12s} {part.get(key, 0):3d}"
              f" (0.13.0 bed {was.get(key, 0)}){flag}")

    # ---------------------------------------------------------- (vii) the ΔE table
    print("\n(vii) OKLab ΔE mean per profile, tier and set, on the landed bed "
          "(the 0.13.0 bed's beside):")
    acc = {}
    old = {}
    for key, cell in list(canon.items()) + list(canon_probe.items()):
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
              f"0.13.0 {prev_s} -> landed {sum(values) / len(values):.5f}")

    clean = (not voided and not missing and not movers and not moved and ok
             and not lost and not new)
    probe_clean = not probe_movers and not probe_moved and not probe_lost
    print("\nVERDICT: " + ('every gated capture and every gated row reproduces the dry run'
                          if clean else 'SEE THE GATED MISMATCHES ABOVE')
          + '; the probe half ' + ('reproduces the rung' if probe_clean else 'SEE ABOVE'))


main()
