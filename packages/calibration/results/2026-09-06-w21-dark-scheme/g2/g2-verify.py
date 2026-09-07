#!/usr/bin/env python3
"""W21 G2: the canonical rebuild read against G1's frozen dry run and against the W20 bed.

What this gate has to prove is narrower than a fidelity comparison and stricter. The wave's one
holdout read was spent at G1's dry run (contract X6), so the landing is only allowed to REPRODUCE
that render — not to take a second reading of it. The proof is a digest per dark capture: G1
recorded one for all 52 dark captures at the frozen constants (`g1-digests.txt`), and if a byte
differs here then either a constant or the renderer moved between the two runs and the holdout
number the wave published came from a configuration that no longer exists. That is a stop, not a
finding, and it is checked first.

The other four checks:

  * **the light profiles byte-identical** (contract X3's inverse). The light document is untouched,
    so every capture under the four light profiles must come back bit for bit as the W20 bed left
    it — on BOTH tiers, and including the light holdout, which this rebuild re-captures because the
    bed is rebuilt whole.
  * **the rows.** Every matrix row on the four light profiles equal to the W20 bed's to the last
    decimal (a light row that moved would mean the rebuild changed something the light profiles
    read), and every dark row equal to the dry run's — the same render measured twice.
  * **the declared-geometry read** (contract X2) — run separately by `read-canonical.sh` against the
    landed captures and diffed against `g1-clauses.txt`; this script does not duplicate it.
  * **the bed's shape.** 229 cells and the partition `adopted-thresholds.test.ts` asserts, so a
    profile that lost a cell in the rebuild cannot be absorbed by another profile gaining one.

    python3 g2-verify.py <before matrix> <before captures dir> <g1-digests.txt> <dry-run matrix>

Derived from W20 G2's `g2-verify.py`, whose shape this is: the same loader, the same "best row per
key" rule, the same per-profile ΔE table at the end.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
P = 'apple-macos-26.5-'
DARK = (P + '1x-dark-standard', P + '2x-dark-standard')
LIGHT = (P + '1x-light-standard', P + '2x-light-standard',
         P + '1x-light-increased-contrast', P + '1x-light-reduced-transparency')
AXES = ('shape', 'perceptual', 'material', 'coherence')
# The declaration-conformance rows `--alpha` takes. G1's dry run did not pass `--alpha` (it was
# measuring the material, and the canonical bed is where those rows live since W20's landing), so
# they are absent on every dry-run cell and present on every landed one. That is a difference in
# what was MEASURED, not in what was rendered — the captures behind them are byte-identical under
# (i) — so they are counted apart rather than reported as rows that moved.
ALPHA_ONLY = ('shape.declaredIoUWeb', 'shape.declaredContourMaxWeb',
              'shape.declaredContourP95Web', 'shape.drawnAreaWeb')
# `adopted-thresholds.test.ts`'s MATRIX_PARTITION and MATRIX_CELLS, copied here so that a rebuild
# that lost a cell is named by this referee before the gate runs rather than after.
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


def value(cell, axis, metric):
    if cell is None:
        return None
    entry = (cell.get(axis) or {}).get(metric)
    if entry is None:
        return None
    return entry['value'] if isinstance(entry, dict) else entry


def metrics(cell):
    """Every numeric reading on a cell, keyed `axis.metric` — the whole row, not a chosen subset."""
    out = {}
    for axis in AXES:
        for metric, entry in (cell.get(axis) or {}).items():
            if isinstance(entry, dict) and isinstance(entry.get('value'), (int, float)):
                out[f'{axis}.{metric}'] = entry['value']
            elif isinstance(entry, (int, float)):
                out[f'{axis}.{metric}'] = entry
    return out


def relative(profile, renderer, scene):
    return os.path.join(profile, scene, f'{scene}__{renderer}.png')


def main():
    before_path, before_caps, digests_path, dry_path = sys.argv[1:5]
    canon = load(os.path.join(CAL, 'results', 'matrix.json'))
    before = load(before_path)
    dry = load(dry_path) if os.path.exists(dry_path) else {}
    captures = os.path.join(CAL, 'web-captures')

    print(f"canonical: {len(canon)} cells; the W20 bed: {len(before)}; "
          f"the dry run: {len(dry) if dry else 'ABSENT'}")
    lost = sorted(k for k in before if k not in canon)
    new = sorted(k for k in canon if k not in before)
    print(f"rows on the W20 bed and not on the canonical bed: {lost if lost else 'none'}; "
          f"new rows: {new if new else 'none'}")

    # ---------------------------------------------------------------- (i) X6
    print("\n(i) X6 — every dark capture reproduces G1's digest, byte for byte:")
    declared = {}
    for line in open(digests_path):
        parts = line.split()
        if len(parts) == 2 and len(parts[0]) == 64 and parts[1].endswith('.png'):
            declared[parts[1]] = parts[0]
    checked = matched = 0
    voided = []
    for profile, renderer, scene in sorted(canon):
        if profile not in DARK:
            continue
        rel = relative(profile, renderer, scene)
        want = declared.get(rel)
        if want is None:
            voided.append((rel, 'NOT DECLARED BY G1'))
            continue
        checked += 1
        got = sha(os.path.join(captures, rel))
        if got == want:
            matched += 1
        else:
            voided.append((rel, f'{want[:12]} declared, {got[:12]} landed'))
    print(f"  dark captures declared by G1 and re-taken here: {matched} / {checked} identical")
    for rel, why in voided:
        print(f"  VOID  {rel}: {why}")
    if voided:
        print("  the holdout read is VOID — stop here and report (Decision Log 3 (d), X6)")

    # --------------------------------------------------------------- (ii) X3
    print("\n(ii) X3 — every light-profile capture byte-identical to the W20 bed, both tiers:")
    per_profile = {}
    for profile, renderer, scene in sorted(canon):
        if profile not in LIGHT:
            continue
        rel = relative(profile, renderer, scene)
        now, then = os.path.join(captures, rel), os.path.join(before_caps, rel)
        counts = per_profile.setdefault(profile, [0, 0, 0])
        if not os.path.exists(then):
            counts[2] += 1
            print(f"  MISSING on the W20 bed: {rel}")
            continue
        if sha(now) == sha(then):
            counts[0] += 1
        else:
            counts[1] += 1
            # Named, with what it is: the two captures are compared pixel by pixel so a byte
            # difference is reported as a magnitude and not as a bare inequality. A material change
            # would move a whole surface; a capture-session difference moves a handful of edge
            # pixels by one code.
            try:
                from PIL import Image
                import numpy
                a = numpy.asarray(Image.open(now).convert('RGB')).astype(int)
                b = numpy.asarray(Image.open(then).convert('RGB')).astype(int)
                delta = abs(a - b)
                changed = int((delta.max(axis=2) > 0).sum())
                print(f"  DIFFERS from the W20 bed: {rel}"
                      f" — {changed} of {a.shape[0] * a.shape[1]} pixels,"
                      f" worst channel delta {int(delta.max())}")
            except Exception:
                print(f"  DIFFERS from the W20 bed: {rel}")
    total = [sum(c[i] for c in per_profile.values()) for i in range(3)]
    for profile, (same, diff, missing) in sorted(per_profile.items()):
        print(f"  {profile.replace(P, ''):30s} byte-identical {same:3d}"
              f"{f', DIFFERS {diff}' if diff else ''}{f', missing {missing}' if missing else ''}")
    print(f"  light captures: {total[0]} / {total[0] + total[1] + total[2]} byte-identical")

    # -------------------------------------------------------------- (iii) rows
    print("\n(iii) the rows — light against the W20 bed, dark against the dry run, to the last decimal:")
    for label, profiles, reference in (('light / W20 bed', LIGHT, before), ('dark / dry run', DARK, dry)):
        if not reference:
            print(f"  {label}: the reference matrix is absent — skipped")
            continue
        rows = moved = missing = alpha_only = 0
        worst = (0.0, None)
        for key in sorted(canon):
            if key[0] not in profiles:
                continue
            other = reference.get(key)
            if other is None:
                missing += 1
                print(f"  no reference row: {key[0].replace(P, '')} / {key[1]} / {key[2]}")
                continue
            rows += 1
            mine, theirs = metrics(canon[key]), metrics(other)
            names = set(mine) | set(theirs)
            for metric in sorted(names):
                a, b = mine.get(metric), theirs.get(metric)
                if a is None or b is None:
                    if metric in ALPHA_ONLY and b is None:
                        alpha_only += 1
                        continue
                    print(f"  ROW SHAPE {key[2]} @ {key[0].replace(P, '')} / {key[1]}: "
                          f"{metric} {'absent here' if a is None else 'absent there'}")
                    moved += 1
                    continue
                if a != b:
                    moved += 1
                    delta = abs(a - b)
                    if delta > worst[0]:
                        worst = (delta, f'{metric} {key[2]} @ {key[0].replace(P, "")} / {key[1]}')
                    print(f"  MOVED {metric} {key[2]} @ {key[0].replace(P, '')} / {key[1]}: "
                          f"{b!r} → {a!r}")
        print(f"  {label}: {rows} rows compared, {moved} readings moved"
              f"{f', {alpha_only} conformance readings the reference run did not take' if alpha_only else ''}"
              f"{f', worst |Δ| {worst[0]:.6g} on {worst[1]}' if worst[1] else ''}"
              f"{f', {missing} without a reference row' if missing else ''}")

    # ---------------------------------------------------------------- (v) shape
    print("\n(v) the bed's shape — the partition adopted-thresholds.test.ts asserts:")
    counts = {}
    for profile, _renderer, _scene in canon:
        counts[profile] = counts.get(profile, 0) + 1
    ok = counts == PARTITION and len(canon) == CELLS
    for profile in sorted(set(counts) | set(PARTITION)):
        got, want = counts.get(profile, 0), PARTITION.get(profile, 0)
        print(f"  {profile.replace(P, ''):30s} {got:3d} cells "
              f"{'ok' if got == want else f'AGAINST {want} ASSERTED'}")
    print(f"  {len(canon)} cells against MATRIX_CELLS {CELLS}: {'ok' if ok else 'MISMATCH'}")

    # ------------------------------------------------------- the movement, for the record
    print("\nthe dark bed's OKLab ΔE mean per profile and tier, W20 bed → canonical "
          "(calibration | validation | holdout):")
    for profile in DARK:
        for renderer in ('webgpu', 'css'):
            out = []
            for wanted in ('calibration', 'validation', 'holdout'):
                now, then = [], []
                for key, cell in canon.items():
                    if key[0] != profile or key[1] != renderer or cell.get('fixtureSet') != wanted:
                        continue
                    a = value(cell, 'perceptual', 'oklabDeltaEMean')
                    b = value(before.get(key), 'perceptual', 'oklabDeltaEMean')
                    if a is None or b is None:
                        continue
                    now.append(a)
                    then.append(b)
                out.append(f'{sum(then) / len(then):.5f} → {sum(now) / len(now):.5f} ({len(now)})'
                           if now else '—')
            print(f"  {profile.replace(P, ''):18s} {renderer:7s} "
                  f"{out[0]:26s} {out[1]:26s} {out[2]}")

    print("\nthe dark cells per row, GPU tier, W20 bed → canonical (ΔE mean, p95, ssimMean):")
    for profile in DARK:
        for key in sorted(canon):
            if key[0] != profile or key[1] != 'webgpu':
                continue
            cell, was = canon[key], before.get(key)
            fmt = lambda x: '  —   ' if x is None else f'{x:.5f}'
            print(f"  {key[2]:46s} {profile.replace(P, ''):18s} "
                  f"{cell.get('fixtureSet', '?'):11s} "
                  f"ΔE {fmt(value(was, 'perceptual', 'oklabDeltaEMean'))} → "
                  f"{fmt(value(cell, 'perceptual', 'oklabDeltaEMean'))}   "
                  f"p95 {fmt(value(was, 'perceptual', 'oklabDeltaEP95'))} → "
                  f"{fmt(value(cell, 'perceptual', 'oklabDeltaEP95'))}   "
                  f"ssim {fmt(value(was, 'perceptual', 'ssimMean'))} → "
                  f"{fmt(value(cell, 'perceptual', 'ssimMean'))}")


if __name__ == '__main__':
    main()
