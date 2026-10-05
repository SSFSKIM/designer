#!/usr/bin/env python3.12
"""W46 G0 (e): the ladders' reader (charter clause 4; `protocol.json`). Reads only; writes `results.json`
and `results.txt` beside it. W45's `ladders/read.py` is the pattern; the readings are W46's protocol's.

Every rung's rows are admitted first: EXACTLY its declared cells at both dark scales (one row each, a T1
cell with its structure reading; a partial rung decides nothing), each naming its candidate at its hash
(candidate mode), the pinned Chromium, WebGPU, and no withheld cell. Then:

- **The instrument.** `level.py identity` on the control's rows: pixel identity and measurement
  identity to `d0219cd684bf` on every ladder cell, at both scales. Anything else stops the read.
- **T1 per cell per rung** off the rows (`interiorStdDev{Web,Native}`), with the cell's bar and code
  from W44 G0's bar file (0.5 code per dark cell); `delta` is the rung's web SD less the control's,
  `moved` is |delta| > bar, `g` the error growth against the control (|k − n| − |c − n|).
- **The scale anchoring.** A lever acting at one scale must leave the other byte-identical to the
  control (PNG and alpha); `tintAlpha` acts at both.
- **Ladder (i)**, per arm: the photo cells' T1 along the rungs (monotone: no step lowers a photo
  cell's web SD beyond its bar; the photo median ratio per rung), and `level.py check` at every rung —
  L1's absolute and growth clauses on the arm's L1 cells, every excess and its attribution. The
  PASSING rungs are those whose L1 clauses both pass.
- **Ladder (ii)**, per lever at the scale it acts at: the thin rest cells' median delta in bars and
  their lowest, the mid cells', and the two F inactive bar cells'; a rung MEETS the bar when the thin
  median delta exceeds one bar, no thin cell falls beyond its bar and neither bar cell rises beyond
  its bar. FLAT: no cell of the lever moves beyond its bar on any rung.
- **Ladder (iii)**, per lever at the scale it acts at: both fine inactive cells' growth (a rung MEETS
  the bar when both fall toward Apple beyond their bar and the photo inactive cell does not fall
  beyond its bar), the coarse inactive cell beside them. FLAT as (ii).
- **X60 by evidence**: `stage/x60.py evidence` over the ladder candidates.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
sys.path.insert(0, str(EVIDENCE / "level"))
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402
import ladder as LADDER  # noqa: E402
import level as LEVEL  # noqa: E402

B, T1 = LEVEL.B, LEVEL.T1
BARS = T1.load_bars()
SCRATCH = LADDER.SCRATCH
CONF: dict = {}


def sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def rows_of(label: str) -> dict:
    out = {}
    for scale in (1, 2):
        path = CONF["scratch"] / label / f"{scale}x" / "matrix.json"
        if not path.exists():
            raise W.Refusal(f"{label}: no {scale}x render")
        for r in json.loads(path.read_bytes())["cells"]:
            key = (r["key"]["profileKey"], r["key"]["sceneId"])
            if key in out:
                raise W.Refusal(f"{label}: two rows for {key}")
            out[key] = r
    return out


def admit(label: str, rows: dict, scenes) -> B.Candidate:
    """The rung's rows, refused unless they are EXACTLY its declared cells at both dark scales (the driver
    writes with --write-partial, so a failed capture would otherwise vanish from a bar's `all(...)`: the
    review of G0's tools, P1), each with its structure reading where it is a T1 cell."""
    want = {(p, s) for p in W.DARK_025 for s in scenes}
    if set(rows) != want:
        missing, extra = sorted(want - set(rows)), sorted(set(rows) - want)
        raise W.Refusal(f"{label}: the rows are not its declared cells: {len(missing)} missing {missing[:4]}, "
                        f"{len(extra)} extra {extra[:4]}; a partial rung decides nothing")
    for (profile, sid), r in rows.items():
        if B.SCENES.by_id[sid]["background"] in T1.T1_BACKDROPS and None in (
                B.value(r, "material", "interiorStdDevWeb"), B.value(r, "material", "interiorStdDevNative")):
            raise W.Refusal(f"{label} {profile} {sid}: a T1 cell with no structure reading")
    candidate = B.Candidate.read(str((CONF["candidates"] / label / "candidate.json").relative_to(W.ROOT)))
    held = B.referee_plan.referee_cells(B.referee_plan.load_manifest())
    for (profile, sid), r in rows.items():
        why = B._admit_candidate(r, candidate)
        if why or profile not in W.DARK_025 or r["key"]["web"]["renderer"] != "webgpu":
            raise W.Refusal(f"{label} {profile} {sid}: not admitted ({why or 'profile or tier'})")
        if (profile, sid) in held or B.SCENES.role[sid] == "holdout":
            raise W.Refusal(f"{label} {profile} {sid}: a withheld cell rendered (clause 3's stop)")
    bad = LEVEL.CENSUS.pinned_engine(list(rows.values()))
    if bad:
        raise W.Refusal(f"{label}: rows not on the pinned Chromium: {bad[:3]}")
    return candidate


def t1(profile: str, sid: str, row: dict, control: dict) -> dict:
    n = B.value(row, "material", "interiorStdDevNative")
    k = B.value(row, "material", "interiorStdDevWeb")
    c = B.value(control, "material", "interiorStdDevWeb")
    entry = BARS.get((profile, sid))
    mean = B.value(row, "material", "interiorMeanNative")
    if None in (n, k, c) or (entry is None and mean is None):
        # A cell with no structure reading (the dark-solid inactive means W36 left UNMEASURED): read by
        # the level check only.
        return dict(native=n, web=k, control=c, ratio=None, controlRatio=None, delta=None, bar=None, moved=False, g=None)
    bar = entry["bar"] if entry else 0.5 * T1.code_step(mean)
    return dict(native=n, web=k, control=c, ratio=k / n if n else None, controlRatio=c / n if n else None,
                delta=k - c, bar=bar, moved=abs(k - c) > bar, g=abs(k - n) - abs(c - n))


def captures_identical(label: str, scale: int, cells) -> list[str]:
    """The cells whose `scale` captures are not byte-identical to the control's."""
    out = []
    for profile, sid in cells:
        if B.scale_of(profile) != scale:
            continue
        for suffix in ("", "__alpha"):
            name = f"{sid}__webgpu{suffix}.png"
            a = sha(CONF["scratch"] / label / f"{scale}x" / "web-captures" / profile / sid / name)
            b = sha(CONF["scratch"] / "control" / f"{scale}x" / "web-captures" / profile / sid / name)
            if a is None or a != b:
                out.append(f"{profile} {sid} {suffix or 'png'}")
    return out


def span(sid: str) -> float:
    return B.SCENES.span(sid)


def main(scratch: Path | None = None, candidates: Path | None = None, rungs: list | None = None,
         out: Path | None = None, protocol: dict | None = None, x60: bool = True) -> int:
    """The read; its arguments exist for `test_read.py` (a synthetic scratch, candidates and rungs)."""
    CONF.update(scratch=scratch or SCRATCH, candidates=candidates or LADDER.CANDIDATES)
    out = out or HERE
    protocol = protocol or LADDER.protocol()
    rungs = rungs if rungs is not None else LADDER.rungs()
    control_rows = rows_of("control")
    control = admit("control", control_rows, rungs[0]["cells"])
    reference_bed = B.load_published(W.REFERENCE["dark"])
    reference = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r for r in reference_bed.rows}
    merged = CONF["scratch"] / "control" / "merged-captures"
    for scale in (1, 2):
        tree = CONF["scratch"] / "control" / f"{scale}x" / "web-captures"
        for prof in tree.iterdir():
            for cell in prof.iterdir():
                (merged / prof.name / cell.name).mkdir(parents=True, exist_ok=True)
                for f in cell.iterdir():
                    link = merged / prof.name / cell.name / f.name
                    if not link.exists():
                        link.hardlink_to(f)
    instrument = LEVEL.identity(list(control_rows.values()), merged, control, reference)
    result = dict(schema="w46-ladder-results-1", protocolSha256=W.file_sha(LADDER.PROTOCOL_PATH),
                  control=dict(verdict=instrument["verdict"], cells=instrument["cells"],
                               identical=instrument["pixelAndMeasurementIdentical"],
                               failures=instrument["failures"][:20]),
                  rungs={}, ladders={})
    if instrument["verdict"] != "IDENTICAL":
        result["stop"] = "the control is not identical to d0219cd684bf: an instrument failure; nothing is read"
        (out / "results.json").write_text(json.dumps(result, indent=1) + "\n")
        print(result["stop"])
        return 1

    per = {}
    for r in rungs[1:]:
        rows = rows_of(r["label"])
        candidate = admit(r["label"], rows, r["cells"])
        cells = {}
        for key, row in rows.items():
            cells[f"{key[0]}/{key[1]}"] = dict(scale=B.scale_of(key[0]), pose=LEVEL.T1.pose(key[1]),
                                               span=span(key[1]), stratum=T1.stratum(key[1])
                                               if B.SCENES.by_id[key[1]]["background"] in T1.T1_BACKDROPS else None,
                                               **t1(*key, row, control_rows[key]))
        acts = r["actsAt"]
        other = [] if acts == "both" else captures_identical(r["label"], 2 if acts == "1x" else 1, rows.keys())
        entry = dict(ladder=r["ladder"], lever=r["lever"], slot=r["slot"], leaf=r["leaf"], value=r["value"],
                     actsAt=acts, otherScaleNotIdentical=other, cells=cells)
        if r["ladder"] == "i":
            entry["level"] = LEVEL.check(list(rows.values()), candidate, reference_bed)
        per[r["label"]] = entry
    result["rungs"] = per

    def at_scale(entry, cell):
        return entry["actsAt"] == "both" or f"{cell['scale']}x" == entry["actsAt"]

    for lad in protocol["ladders"]:
        by_lever = {}
        for lev in lad.get("arms", []) + lad.get("levers", []):
            labels = [f"{lev['id']}-{LADDER.fmt(v)}" for v in lev["values"]]
            readings = []
            for label in labels:
                e = per[label]
                cs = {k: v for k, v in e["cells"].items() if at_scale(e, v)}
                moved = sorted(k for k, v in cs.items() if v["moved"])
                reading = dict(label=label, value=e["value"], moved=len(moved), cells=len(cs),
                               otherScaleNotIdentical=len(e["otherScaleNotIdentical"]))
                if lad["id"] == "i":
                    photo = {k: v for k, v in cs.items() if "/photo__" in k}
                    lv = e["level"]
                    reading.update(
                        photoMedianRatio=statistics.median(v["ratio"] for v in photo.values()),
                        photoControlMedianRatio=statistics.median(v["controlRatio"] for v in photo.values()),
                        photo={k: dict(ratio=v["ratio"], controlRatio=v["controlRatio"], deltaInBars=v["delta"] / v["bar"])
                               for k, v in photo.items()},
                        checkerT1={k: dict(ratio=v["ratio"], controlRatio=v["controlRatio"]) for k, v in cs.items()
                                   if "/checkerboard__" in k},
                        L1=dict(growthPasses=lv["L1"]["growthClausePasses"], absolutePasses=lv["L1"]["absoluteClausePasses"],
                                maxError=lv["L1"]["maxError"], maxGrowth=lv["L1"]["maxGrowth"],
                                growthMisses=[dict(cell=c["cell"], growth=c["growth"]) for c in lv["L1"]["growthMisses"]],
                                absoluteMisses=[dict(cell=c["cell"], error=c["error"]) for c in lv["L1"]["absoluteMisses"]]),
                        excesses=lv["excesses"], unexplained=lv["unexplained"],
                        passes=lv["L1"]["growthClausePasses"] and lv["L1"]["absoluteClausePasses"])
                elif lad["id"] == "ii":
                    tex = {k: v for k, v in cs.items() if v["stratum"] in ("F", "C") and v["delta"] is not None}
                    thin = {k: v for k, v in tex.items() if v["pose"] == "rest" and v["span"] <= 44}
                    mid = {k: v for k, v in tex.items() if v["pose"] == "rest" and v["span"] == 96}
                    bar_cells = {k: v for k, v in tex.items() if v["pose"] == "inactive"}
                    thin_med = statistics.median(v["delta"] / v["bar"] for v in thin.values()) if thin else None
                    reading.update(
                        thinMedianDeltaInBars=thin_med,
                        thinLowestDeltaInBars=min((v["delta"] / v["bar"] for v in thin.values()), default=None),
                        thinMedianRatio=statistics.median(v["ratio"] for v in thin.values()) if thin else None,
                        thinControlMedianRatio=statistics.median(v["controlRatio"] for v in thin.values()) if thin else None,
                        midMedianDeltaInBars=statistics.median(v["delta"] / v["bar"] for v in mid.values()) if mid else None,
                        barCellsDeltaInBars={k: v["delta"] / v["bar"] for k, v in bar_cells.items()},
                        perCell={k: dict(ratio=v["ratio"], controlRatio=v["controlRatio"], deltaInBars=v["delta"] / v["bar"])
                                 for k, v in tex.items()})
                    reading["meetsBar"] = bool(thin) and thin_med > 1 and reading["thinLowestDeltaInBars"] >= -1 \
                        and all(d <= 1 for d in reading["barCellsDeltaInBars"].values())
                else:
                    fine = {k: v for k, v in cs.items() if "/checkerboard-8__" in k}
                    photo = {k: v for k, v in cs.items() if "/photo__" in k}
                    coarse = {k: v for k, v in cs.items() if "/checkerboard__" in k}
                    reading.update(
                        fineGrowthInBars={k: v["g"] / v["bar"] for k, v in fine.items()},
                        fineRatio={k: dict(ratio=v["ratio"], controlRatio=v["controlRatio"]) for k, v in fine.items()},
                        photoDeltaInBars={k: v["delta"] / v["bar"] for k, v in photo.items()},
                        photoRatio={k: v["ratio"] for k, v in photo.items()},
                        coarse={k: dict(ratio=v["ratio"], controlRatio=v["controlRatio"], deltaInBars=v["delta"] / v["bar"])
                                for k, v in coarse.items()})
                    reading["meetsBar"] = bool(fine) and all(g < -1 for g in reading["fineGrowthInBars"].values()) \
                        and all(d >= -1 for d in reading["photoDeltaInBars"].values())
                readings.append(reading)
            flat = all(x["moved"] == 0 for x in readings)
            nonflat = [lev["shipped"]] + [x["value"] for x in readings if x["moved"] > 0]
            entry = dict(lever=lev["id"], slot=lev["slot"], leaf=lev["leaf"], shipped=lev["shipped"], actsAt=lev["actsAt"],
                         readings=readings, flat=flat, nonFlatRange=[min(nonflat), max(nonflat)],
                         scaleAnchored=all(x["otherScaleNotIdentical"] == 0 for x in readings))
            if lad["id"] == "i":
                ratios = [x["photoMedianRatio"] for x in readings]
                entry["passingRungs"] = [lev["shipped"]] + [x["value"] for x in readings if x["passes"]]
                entry["photoMonotone"] = all(
                    (x["photo"][k]["deltaInBars"] - (readings[i - 1]["photo"][k]["deltaInBars"] if i else 0)) >= -1
                    for i, x in enumerate(readings) for k in x["photo"])
                entry["photoMedianRatios"] = [readings[0]["photoControlMedianRatio"]] + ratios
                entry["raisesPhoto"] = any(x["passes"] and x["photoMedianRatio"] > x["photoControlMedianRatio"] for x in readings)
            else:
                entry["meetsBar"] = [x["value"] for x in readings if x["meetsBar"]]
            by_lever[lev["id"]] = entry
        result["ladders"][lad["id"]] = by_lever
    lev_i, lev_ii, lev_iii = result["ladders"]["i"], result["ladders"]["ii"], result["ladders"]["iii"]
    result["targets"] = {
        "P": dict(lever=[k for k, v in lev_i.items() if v["raisesPhoto"]],
                  note="an arm raises the photo ratio at a passing rung"),
        "C rest": dict(lever=[k for k, v in lev_ii.items() if v["meetsBar"]],
                       note="a lever raises the thin cells without raising the F inactive cells"),
        "F inactive": dict(lever=[k for k, v in lev_iii.items() if v["meetsBar"]],
                           note="a lever lowers both fine inactive cells toward Apple without lowering the photo inactive cell"),
    }
    if x60:
        got = subprocess.run([sys.executable, "-B", str(EVIDENCE / "stage" / "x60.py"), "evidence",
                              "--out", str(out / "x60-evidence.json")], cwd=EVIDENCE / "stage", capture_output=True,
                             text=True)
        result["x60"] = dict(exitCode=got.returncode, tail=(got.stdout + got.stderr)[-600:])
    else:
        result["x60"] = dict(exitCode=None, tail="not run")
    (out / "results.json").write_text(json.dumps(result, indent=1) + "\n")
    (out / "results.txt").write_text(report(result))
    print(report(result))
    return 0


def report(r: dict) -> str:
    lines = [f"W46 G0 (e): the ladders read (protocol sha256 {r['protocolSha256'][:12]})",
             f"control: {r['control']['verdict']} ({r['control']['identical']} of {r['control']['cells']} rows pixel- and "
             "measurement-identical to d0219cd684bf)", ""]
    for lad_id, levers in r["ladders"].items():
        lines.append(f"ladder ({lad_id})")
        for lev_id, e in levers.items():
            lines.append(f"  {lev_id} {e['slot']} {e['leaf']} (shipped {e['shipped']}, acts at {e['actsAt']}): "
                         f"{'FLAT' if e['flat'] else 'non-flat ' + str(e['nonFlatRange'])}; scale-anchored {e['scaleAnchored']}"
                         + (f"; passing rungs {e['passingRungs']}; photo monotone {e['photoMonotone']}; raises photo "
                            f"{e['raisesPhoto']}" if lad_id == "i" else f"; meets the bar at {e['meetsBar']}"))
            for x in e["readings"]:
                if lad_id == "i":
                    lines.append(f"    {x['value']:<5} photo median ×{x['photoMedianRatio']:.3f} (control ×{x['photoControlMedianRatio']:.3f}); "
                                 f"L1 max error {x['L1']['maxError']:.4f}, max growth {x['L1']['maxGrowth']:+.4f}, "
                                 f"{'passes' if x['passes'] else 'FAILS'}; {len(x['excesses'])} excess(es), "
                                 f"{len(x['unexplained'])} unexplained")
                    for m in x["L1"]["growthMisses"]:
                        lines.append(f"      L1 growth {m['cell']} {m['growth']:+.4f}")
                    for ex in x["excesses"][:12]:
                        lines.append(f"      excess {ex['cell']}: {', '.join(ex['excess'])} -> {ex['attribution']} "
                                     f"(predicted {ex['predictedDelta']:+.4f})")
                elif lad_id == "ii":
                    lines.append(f"    {x['value']:<5} thin median Δ {x['thinMedianDeltaInBars']:+.2f} bars (lowest "
                                 f"{x['thinLowestDeltaInBars']:+.2f}), thin median ×{x['thinMedianRatio']:.3f} (control "
                                 f"×{x['thinControlMedianRatio']:.3f}); mid {x['midMedianDeltaInBars']:+.2f}; F inactive "
                                 + ", ".join(f"{k.split('/')[1].split('__')[1]} {v:+.2f}" for k, v in x["barCellsDeltaInBars"].items())
                                 + f"; {'MEETS' if x['meetsBar'] else 'no'}; moved {x['moved']}/{x['cells']}")
                else:
                    lines.append(f"    {x['value']:<5} fine g " + ", ".join(f"{k.split('/')[1].split('__')[1]} {v:+.2f}"
                                                                         for k, v in x["fineGrowthInBars"].items())
                                 + " bars; photo Δ " + ", ".join(f"{v:+.2f}" for v in x["photoDeltaInBars"].values())
                                 + f" bars (×{list(x['photoRatio'].values())[0]:.3f}); {'MEETS' if x['meetsBar'] else 'no'}; "
                                 f"moved {x['moved']}/{x['cells']}")
        lines.append("")
    for t, v in r["targets"].items():
        lines.append(f"target {t}: {'levers ' + ', '.join(v['lever']) if v['lever'] else 'NO LEVER (X63: named, not fitted)'}")
    lines.append(f"X60 by evidence: exit {r['x60']['exitCode']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
