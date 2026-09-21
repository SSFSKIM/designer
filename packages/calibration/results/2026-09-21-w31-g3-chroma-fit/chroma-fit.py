#!/usr/bin/env python3
"""W31 G3 — the chroma fit's measuring loop, in `fit.py`'s idiom (claims §5.164 §4).

    python3 chroma-fit.py doc    <out.json> <base.json> <overrides.json>
    python3 chroma-fit.py render <label> <profile> <document> <receded> [--set S] [--scene a,b]
    python3 chroma-fit.py read   <label|matrix.json ...>   [--csv out.csv]
    python3 chroma-fit.py stops  <before-label> <after-label>

`results/2026-09-19-w29-g3-refit/fit.py` one statistic along, COPIED rather than
imported on that directory's own convention — nothing under `results/` is edited
after commit, and a fit loop that hard-codes the bed it fitted is the only kind
whose numbers a later reader can reproduce. What is kept verbatim: the machine
refusal, the scratch-only output, and above all `cells()`, the single place every
reader gets its rows from, which DROPS EVERY HOLDOUT ROW before returning.

**THE FIT NEVER READS A HOLDOUT ROW.** All four rows this wave claims are holdout
rows (claims §5.161 §4) and the fit is judged on the declared bed —
`calibration` + `validation`, the untinted `photo` cells of the four macOS 27
standard profiles, WebGPU tier, the two poses bounded separately (§5.161 §7 (b)).
`--with-holdout` exists in `fit.py` for the canonical read; it is NOT here,
because this file has no verb that may ever see one.

Two things this adds to `fit.py`.

**A receded document per render.** The inactive pose draws a CANDIDATE receded
document composed over the active one, which is the material a root hands the
renderer when the window loses focus. `fit.py render` never passed
`--receded-profile`, so its inactive rows were the shipped recede whatever the
candidate held — fine for a fit on the active endpoint and wrong for this one,
where the receded documents carry their own value (Decision Log 2 (a)).

**The statistic.** `R = chromaStructureRatioWeb / chromaStructureRatioNative`,
web against native on the same cell and never against 1, with the INVARIANT TWIN
`chromaSpread / oklabLStdDev` read beside it at every step (§5.161 §11, N3) and
the two stops read on every cell:

  * the LEVEL stop — `|interiorMeanWeb − interiorMeanNative| ≤ 0.055`, and that
    quantity growing by no more than 0.005 from its pre-fit value, whose
    baseline is the corrected one: medians 0.0060 light and 0.0210 dark on both
    tiers, worst cell 0.04933 (§5.161 §7 (c) as its closure corrects it);
  * the STRUCTURE stop — `interiorStdDevWeb` within 2 % of its pre-fit value on
    every cell of the bed, without which `R` is not a sufficient statistic
    because it is scale-free in the deviations.

Ratio (ii) (`rawChromaRatio*`) is tabled beside both, so a fit that moves only
the confounded one is visible rather than reported as a result.
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent
SCENES = ROOT / "apps/reference-apple/scenes.json"
SCRATCH = Path(os.environ.get("VITREA_G3_SCRATCH", "/tmp/w31-g3-fit"))

HOLDOUT = "holdout"

#: The declared bed's scenes — the untinted `photo` cells in both poses. The
#: holdout components (`rrect-lg`, `glass-over-glass`) are absent BY NAME as
#: well as by `--set`, so a mistyped set cannot reach them.
BED_SCENES = ",".join(
    f"photo__{component}__{pose}"
    for component in ("capsule-button", "rrect-md", "rrect-ml", "rrect-sm", "toolbar-group")
    for pose in ("rest", "inactive")
)

#: The probe anchor, granted for the chromaticity DIRECTION only (Decision Log
#: 2 (d)). It is level-broken on both schemes — 2.415x dark, 0.75x light — and
#: `R` scales as (level)^(-2/3) exactly, so it must not carry the tolerance.
ANCHOR_SCENES = ",".join(
    f"mid-chroma-solid__{component}__{pose}"
    for component in ("capsule-button", "rrect-md", "rrect-lg")
    for pose in ("rest", "inactive")
)

PROFILES = {
    "apple-macos-27.0-1x-light-standard-glass0.5": ("light", 1),
    "apple-macos-27.0-2x-light-standard-glass0.5": ("light", 2),
    "apple-macos-27.0-1x-dark-standard-glass0.5": ("dark", 1),
    "apple-macos-27.0-2x-dark-standard-glass0.5": ("dark", 2),
}


def machine_ready() -> None:
    """`fit.py`'s refusal, verbatim (X6)."""
    out = subprocess.run(
        ["pgrep", "-f", "compare.ts|sweep.ts|capture-web|VitreaReference"], capture_output=True
    )
    if out.returncode == 0:
        raise SystemExit("chroma-fit: another calibration capture is running (X6)")
    reads = {}
    for name, domain, key in (
        ("reduceTransparency", "com.apple.universalaccess", "reduceTransparency"),
        ("increaseContrast", "com.apple.universalaccess", "increaseContrast"),
        ("NSGlassTintAmount", "-g", "NSGlassTintAmount"),
    ):
        got = subprocess.run(["defaults", "read", domain, key], capture_output=True, text=True)
        reads[name] = got.stdout.strip() if got.returncode == 0 else "absent"
    print(f"machine: {reads}", file=sys.stderr)
    if reads["reduceTransparency"] != "0" or reads["increaseContrast"] != "0":
        raise SystemExit(f"chroma-fit: accessibility toggles must read 0, got {reads}")
    if reads["NSGlassTintAmount"] != "0.5":
        raise SystemExit(f"chroma-fit: the bed is at slider 0.5, machine reads {reads}")


def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, value in over.items():
        out[key] = deep_merge(out[key], value) if isinstance(value, dict) and isinstance(out.get(key), dict) else value
    return out


def make_doc(out: Path, base: Path, overrides: dict) -> Path:
    """A candidate document: a committed profile's sections with a patch merged over.

    The `profileKey` is carried through unchanged, which is load-bearing: the
    web page refuses a document whose OS token names a material the runtime does
    not ship, and a candidate is a difference from the shipped material rather
    than a new one.
    """
    source = json.loads(base.read_text())
    doc = {
        "$comment": [
            "W31 G3 SCRATCH — a fit candidate, not evidence. The sealed documents are",
            "packages/calibration/profiles/apple-macos-27.0-*.json.",
        ],
        "profileKey": source.get("profileKey"),
        "colorSpace": source.get("colorSpace", "srgb"),
        "patch": deep_merge(source.get("patch", {}), overrides.get("patch", {})),
    }
    for key in ("resolvedOverActiveDocument", "cssTierMapping"):
        if key in source:
            doc[key] = source[key]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n")
    return out


def holdout_scenes() -> frozenset[str]:
    """The declared holdout ids, read from `scenes.json` and named nowhere here."""
    return frozenset(json.loads(SCENES.read_text())["split"][HOLDOUT])


def flag_list(argv: list[str], name: str) -> list[str]:
    out: list[str] = []
    for index, token in enumerate(argv):
        if token == f"--{name}" and index + 1 < len(argv):
            out += [part.strip() for part in argv[index + 1].split(",") if part.strip()]
    return out


def capture_refusal(argv: list[str]) -> str | None:
    """Why this `render` must not run, or None — `fit.py`'s check with no exception.

    `compare` prints a line per measured cell into the label's log, so a
    selection naming the holdout puts a holdout number one `cat` away from the
    person choosing constants whether or not any table prints it.
    """
    if HOLDOUT in flag_list(argv, "set"):
        return "chroma-fit: --set names the holdout and this is a fit loop (X4)."
    named = sorted(set(flag_list(argv, "scene")) & holdout_scenes())
    if named:
        return f"chroma-fit: --scene names {len(named)} declared holdout scene(s): {', '.join(named)}"
    return None


def render(label: str, profile: str, document: Path, receded: Path, argv: list[str]) -> Path:
    refusal = capture_refusal(argv)
    if refusal is not None:
        raise SystemExit(refusal)
    machine_ready()
    run = SCRATCH / label
    run.mkdir(parents=True, exist_ok=True)
    matrix = run / f"{profile}.webgpu.json"
    if matrix.exists():
        matrix.unlink()
    command = [
        "npx", "tsx", "cli/compare.ts",
        "--profile", profile,
        "--material-profile", str(document),
        "--receded-profile", str(receded),
        "--renderer", "webgpu",
        "--alpha",
        "--out-matrix", str(matrix),
        "--write-partial",
        *argv,
    ]
    env = {**os.environ, "VITREA_WEB_CAPTURES": str(run / "web-captures")}
    log = (run / f"{profile}.webgpu.log").open("w")
    subprocess.run(command, cwd=PACKAGE, env=env, stdout=log, stderr=subprocess.STDOUT)
    if not matrix.exists():
        raise SystemExit(f"chroma-fit: {matrix} was not written; see {run}")
    return matrix


def cells(matrix: Path) -> list[dict]:
    """Every cell of one scratch matrix — MINUS the holdout rows.

    THE FIT NEVER READS A HOLDOUT ROW. The drop is here, in the one function
    every reader is built on, rather than in each invocation's flags where one
    mistyped list would undo it. The count and the scenes are printed rather
    than swallowed, so a round that captured more than it meant to says so.
    """
    everything = json.loads(matrix.read_text())["cells"]
    dropped = [cell for cell in everything if cell.get("fixtureSet") == HOLDOUT]
    if dropped:
        print(f"# {len(dropped)} holdout row(s) in {matrix.name} and NOT read (X4):")
        for profile, scene in sorted({(c["key"]["profileKey"], c["key"]["sceneId"]) for c in dropped}):
            print(f"#   {profile} {scene}")
    return [cell for cell in everything if cell.get("fixtureSet") != HOLDOUT]


def readings(matrix: Path) -> list[dict]:
    rows = []
    for cell in cells(matrix):
        material = cell.get("material") or {}
        at = lambda k: material[k]["value"] if isinstance(material.get(k), dict) else None
        key = cell["key"]
        scene = key["sceneId"]
        profile = key["profileKey"]
        scheme, scale = PROFILES.get(profile, (None, None))
        backdrop, component, pose = (scene.split("__") + ["", ""])[:3]
        rn, rw = at("chromaStructureRatioNative"), at("chromaStructureRatioWeb")
        tn, tw = at("interiorOklabLSdDevNative"), at("interiorOklabLSdDevWeb")
        cn, cw = at("interiorChromaMeanNative"), at("interiorChromaMeanWeb")
        rows.append(
            {
                "profile": profile,
                "scheme": scheme,
                "scale": scale,
                "renderer": key["web"]["renderer"],
                "scene": scene,
                "backdrop": backdrop,
                "component": component,
                "pose": "inactive" if pose.startswith("inactive") else "active",
                "tinted": "-tint-" in scene,
                "set": cell.get("fixtureSet"),
                "R": (rw / rn) if rn else None,
                # The invariant twin: the same numerator over sd(L_oklab), which
                # is exactly invariant under a luma-only change where the
                # declared form scales by c^(-2/3) (§5.161 §1, §11 N3).
                "twin": ((cw / tw) / (cn / tn)) if (tn and tw and cn and cw) else None,
                "ratio2Native": at("rawChromaRatioNative"),
                "ratio2Web": at("rawChromaRatioWeb"),
                "levelNative": at("interiorMeanNative"),
                "levelWeb": at("interiorMeanWeb"),
                "structureNative": at("interiorStdDevNative"),
                "structureWeb": at("interiorStdDevWeb"),
                "rimPeakWeb": at("rimPeakLuminanceWeb"),
                "rimPeakNative": at("rimPeakLuminanceNative"),
                "tintDeltaLWeb": at("tintDeltaLWeb"),
                "tintChromaDeltaWeb": at("tintChromaDeltaWeb"),
                "ssim": ((cell.get("perceptual") or {}).get("ssimMean") or {}).get("value"),
                "deP95": ((cell.get("perceptual") or {}).get("oklabDeltaEP95") or {}).get("value"),
                "departure": ((cell.get("shadow") or {}).get("meanDepartureWeb") or {}).get("value"),
                "departureNative": ((cell.get("shadow") or {}).get("meanDepartureNative") or {}).get("value"),
            }
        )
    return rows


def collect(sources: list[str]) -> list[dict]:
    rows: list[dict] = []
    for source in sources:
        path = Path(source)
        matrices = sorted((SCRATCH / source).glob("*.json")) if not path.exists() else [path]
        if not matrices and path.is_dir():
            matrices = sorted(path.glob("*.json"))
        for matrix in matrices:
            rows += readings(matrix)
    return rows


def bed(rows: list[dict]) -> list[dict]:
    """§5.161 §7 (b)'s bed: untinted `photo`, four standard profiles, WebGPU."""
    return [
        r
        for r in rows
        if r["backdrop"] == "photo"
        and not r["tinted"]
        and r["renderer"] == "webgpu"
        and r["scheme"] is not None
        and r["set"] in ("calibration", "validation")
        and r["R"] is not None
    ]


def summarise(rows: list[dict], label: str) -> dict:
    out: dict = {}
    print(f"\n== {label} — R = chromaStructureRatioWeb / chromaStructureRatioNative ==")
    print(f"{'scheme':<7}{'pose':<10}{'n':>4}{'median R':>11}{'min R':>9}{'max R':>9}"
          f"{'median twin':>13}{'median r2 W':>13}{'median r2 N':>13}")
    for scheme in ("light", "dark"):
        for pose in ("active", "inactive"):
            group = [r for r in rows if r["scheme"] == scheme and r["pose"] == pose]
            if not group:
                continue
            vals = [r["R"] for r in group]
            twins = [r["twin"] for r in group if r["twin"] is not None]
            out[f"{scheme}|{pose}"] = {
                "n": len(group),
                "median": statistics.median(vals),
                "min": min(vals),
                "max": max(vals),
                "twin": statistics.median(twins) if twins else None,
            }
            print(f"{scheme:<7}{pose:<10}{len(group):>4}{statistics.median(vals):>11.4f}"
                  f"{min(vals):>9.4f}{max(vals):>9.4f}"
                  f"{(statistics.median(twins) if twins else float('nan')):>13.4f}"
                  f"{statistics.median([r['ratio2Web'] for r in group if r['ratio2Web'] is not None]):>13.4f}"
                  f"{statistics.median([r['ratio2Native'] for r in group if r['ratio2Native'] is not None]):>13.4f}")
    return out


def per_cell(rows: list[dict], label: str) -> None:
    print(f"\n-- {label}, cell by cell --")
    print(f"{'profile':<50}{'scene':<38}{'set':<12}{'R':>8}{'twin':>8}{'r2W':>8}"
          f"{'lvlN':>8}{'lvlW':>8}{'|d|':>8}{'sdW':>9}")
    for r in sorted(rows, key=lambda r: (r["profile"], r["scene"])):
        delta = abs((r["levelWeb"] or 0) - (r["levelNative"] or 0))
        print(f"{r['profile']:<50}{r['scene']:<38}{(r['set'] or ''):<12}"
              f"{r['R']:>8.4f}{(r['twin'] or float('nan')):>8.4f}"
              f"{(r['ratio2Web'] or float('nan')):>8.4f}"
              f"{(r['levelNative'] or 0):>8.4f}{(r['levelWeb'] or 0):>8.4f}{delta:>8.4f}"
              f"{(r['structureWeb'] or 0):>9.5f}")


def stops(before: list[dict], after: list[dict]) -> int:
    """The two hard stops, cell by cell, before against after (§5.161 §7 (b), (c))."""
    index = {(r["profile"], r["scene"], r["renderer"]): r for r in before}
    failures = 0
    print(f"\n== the stops, per cell ==")
    print(f"{'profile':<50}{'scene':<38}{'|d|before':>11}{'|d|after':>10}{'growth':>9}"
          f"{'sd before':>11}{'sd after':>10}{'sd %':>8}")
    worst_level = 0.0
    worst_growth = -1.0
    worst_structure = 0.0
    for r in sorted(after, key=lambda r: (r["profile"], r["scene"])):
        key = (r["profile"], r["scene"], r["renderer"])
        b = index.get(key)
        if b is None:
            continue
        db = abs((b["levelWeb"] or 0) - (b["levelNative"] or 0))
        da = abs((r["levelWeb"] or 0) - (r["levelNative"] or 0))
        sb, sa = b["structureWeb"] or 0, r["structureWeb"] or 0
        pct = (sa - sb) / sb * 100 if sb else 0.0
        worst_level = max(worst_level, da)
        worst_growth = max(worst_growth, da - db)
        worst_structure = max(worst_structure, abs(pct))
        flag = ""
        if da > 0.055:
            flag, failures = " LEVEL>0.055", failures + 1
        if da - db > 0.005:
            flag, failures = flag + " GROWTH>0.005", failures + 1
        if abs(pct) > 2.0:
            flag, failures = flag + " STRUCTURE>2%", failures + 1
        print(f"{r['profile']:<50}{r['scene']:<38}{db:>11.5f}{da:>10.5f}{da - db:>9.5f}"
              f"{sb:>11.5f}{sa:>10.5f}{pct:>8.3f}{flag}")
    print(f"\nworst |Δlevel| {worst_level:.5f} (stop 0.055); worst growth {worst_growth:+.5f} "
          f"(stop 0.005); worst |Δstructure| {worst_structure:.3f} % (stop 2 %)")
    print(f"stop failures: {failures}")
    return failures


def main() -> int:
    argv = sys.argv[1:]
    verb = argv[0] if argv else ""
    if verb == "doc":
        out, base, overrides = (Path(a) for a in argv[1:4])
        print(make_doc(out, base, json.loads(overrides.read_text())))
    elif verb == "render":
        label, profile, document, receded = argv[1:5]
        print(render(label, profile, Path(document), Path(receded), argv[5:]))
    elif verb == "read":
        csv_out = None
        if "--csv" in argv:
            csv_out = Path(argv[argv.index("--csv") + 1])
            argv = argv[: argv.index("--csv")] + argv[argv.index("--csv") + 2 :]
        rows = collect(argv[1:])
        inbed = bed(rows)
        summarise(inbed, "the declared bed")
        per_cell(inbed, "the declared bed")
        if csv_out is not None:
            with csv_out.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            print(f"\nwrote {csv_out} ({len(rows)} rows, every set but holdout)")
    elif verb == "stops":
        before = bed(collect([argv[1]]))
        after = bed(collect([argv[2]]))
        summarise(before, f"{argv[1]} (before)")
        summarise(after, f"{argv[2]} (after)")
        return 1 if stops(before, after) else 0
    else:
        raise SystemExit(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
