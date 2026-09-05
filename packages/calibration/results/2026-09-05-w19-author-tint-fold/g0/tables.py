"""W19 G0 — the findings' tables, printed from the parts rather than typed.

Every number in `g0-findings.md` comes out of here, so a reader can regenerate the tables from
the committed JSON and a typo cannot enter the document by hand.

Usage, from `packages/calibration`:
    python results/2026-09-05-w19-author-tint-fold/g0/tables.py <partsDir>
"""

import json
import sys
from pathlib import Path

parts = Path(sys.argv[1])


def grid(rows, seed, key, backdrops, strengths, fmt="{:+8.4f}"):
    out = ["  s \\ b   " + "  ".join(f"{b:>8}" for b in backdrops)]
    for s in strengths:
        vals = []
        for b in backdrops:
            r = next(x for x in rows if x["seed"] == seed and x["strength"] == s and x["backdrop"] == b)
            vals.append(r["luminance"][key])
        out.append(f"  {s:<5}   " + "  ".join(fmt.format(v) for v in vals))
    return "\n".join(out)


def closed_form_section():
    d = json.loads((parts / "closed-form.json").read_text())
    rows, backdrops, strengths = d["rows"], d["backdrops"], d["strengths"]
    print("### closed-form.json")
    print("surface", d["surface"], "floorAlpha", d["floorAlpha"])
    for seed in d["seeds"]:
        print(f"\n-- seed {seed}: today - intended, linear luminance")
        print(grid(rows, seed, "errorToday", backdrops, strengths))
        print(f"-- seed {seed}: the closed form, same projection")
        print(grid(rows, seed, "closedFormEncodedLuma", backdrops, strengths))
        print(f"-- seed {seed}: the renderer's law minus the intended expression")
        print(grid(rows, seed, "rendererAgainstIntended", backdrops, strengths))
        print(f"-- seed {seed}: the fold (eight-bit declaration) minus intended")
        print(grid(rows, seed, "errorFoldQuantised", backdrops, strengths))

    print("\n-- the interior root.ts resolves at each backdrop level")
    seen = set()
    for r in rows:
        if r["backdrop"] in seen:
            continue
        seen.add(r["backdrop"])
        print(
            f"   b={r['backdrop']:<5} alpha={r['interior']['tintAlpha']:.4f}",
            "tint=[" + ", ".join(f"{v:.4f}" for v in r["interior"]["tint"]) + "]",
            f"X={r['interior']['addedLight']:.5f}",
            f"level={r['compositeLevelForForm']:.4f} form={r['form']}/{r['formCandidate']}",
        )

    print("\n-- where the table saturates (the closed form's own limit)")
    saturated = [
        (r["seed"], r["strength"], r["backdrop"], c["channel"], c["encodedResidual"])
        for r in rows
        for c in r["perChannel"]
        if abs(c["encodedResidual"]) > 1e-6
    ]
    print(f"   {len(saturated)} of {len(rows) * 3} channel cells; worst residual "
          f"{max((abs(x[4]) for x in saturated), default=0):.5f} encoded")
    for x in saturated:
        print(f"   {x[0]:<7} s={x[1]:<5} b={x[2]:<5} channel {x[3]}  residual {x[4]:+.5f}")

    print("\n-- the fold's identity and the floor")
    print("  ", d["foldIdentity"])
    print("   form flips:", d["formFlips"])
    print("\n-- at s = 1, the two declarations")
    for x in d["fullStrengthDeclarations"]:
        print("  ", x)


def x4_section():
    path = parts / "x4-recovery.json"
    if not path.exists():
        return
    print("\n### x4-recovery.json")
    for entry in json.loads(path.read_text()):
        print(f"-- {entry['sceneId']} {entry['tier']} @{entry['dpr']}x  sha {entry['capture']['sha256']}")
        for r in entry["readings"]:
            print(
                f"   {r['mask']:<28} {r['pixels']:>7} px  as captured {r['asCaptured']:.6f}"
                f"  recovery {r['readerRecovery']:+.6f}"
                f"  vs nominal {r['readerErrorAgainstNominal']:+.6f}"
                f"  vs disk {r['readerMinusAchieved']:+.2e}"
            )
        print("   production path:", entry["productionPath"])


def ladder_section():
    for name in ("ladder-1x.json", "ladder-2x.json", "ladder-fold-reduced-transparency.json", "ladder-fold-increased-contrast.json"):
        path = parts / name
        if not path.exists():
            continue
        print(f"\n### {name}")
        rows = json.loads(path.read_text())
        print(f"   {'scene':<52} {'GPU':>8} {'CSS':>8} {'CSS-GPU':>9}  form")
        for r in rows:
            if "skipped" in r:
                print(f"   {r['scene']:<52} skipped: {r['skipped']}")
                continue
            w = r["whole"]["declared"]
            print(
                f"   {r['scene']:<52} {w['gpu']:8.4f} {w['css']:8.4f} {w['delta']:+9.4f}"
                f"  {r.get('cssTint')}"
            )


def native_section():
    path = parts / "native-ladder.json"
    if not path.exists():
        return
    print("\n### native-ladder.json — Apple's curve against an encoded mix of Apple's own endpoints")
    print(f"   {'scene':<52}{'s':>6}{'native':>9}{'encMix':>9}{'encRes':>9}{'linMix':>9}{'linRes':>9}")
    for r in json.loads(path.read_text()):
        if "skipped" in r:
            print("  ", r.get("scene", r.get("background")), r["skipped"])
            continue
        print(
            f"   {r['scene']:<52}{r['strength']:>6}{r['nativeMeasured']:>9.4f}{r['encodedMix']:>9.4f}"
            f"{r['encodedMixResidual']:>+9.4f}{r['linearMix']:>9.4f}{r['linearMixResidual']:>+9.4f}"
        )


closed_form_section()
x4_section()
ladder_section()
native_section()
