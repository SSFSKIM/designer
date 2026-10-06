#!/usr/bin/env python3.12
"""W47 G0 (g): the ladders' reader (charter clause 5; `protocol.json`; X60, X63, X69, X70). Reads only;
writes `results.json`, `results.txt` and `selections.json` beside it. W46 G0's reader
(`results/2026-10-05-w46-g0-declaration/ladders/read.py`), ported by copy and re-bound; W46's committed
copy is untouched.

What W47 changes from W46's reader:
- **X70 at read.** Per rung and scale, the rows measured must be exactly the cells `compare` planned for
  the rung's requested cells (`x70_read`), and the planned set exactly the requested one; anything else
  refuses the rung (a partial rung decides nothing). W46's `admit` (each row this rung's candidate at
  its hash, the pinned Chromium, WebGPU, a T1 cell with its structure reading, no withheld cell) runs
  after it, the withheld cells through W47's X69 loader.
- **Clause 5's four bars in B**, `B = max(1 code, 2 bar)` per cell (W44 G0's bar file), each a pure
  function over the rung's per-cell readings (`bar_i` … `bar_iv`), tested on synthetic readings:
  (i) the five thick rest cells within 1 B of the reference while the thin rest cells keep at least half
  of point A's gain (read from point A's committed cut, pinned in the protocol) with L1 passing; (ii) at
  2x the thick fine and text cells fall toward Apple while `checkerboard-64__rrect-lg__rest` does not fall
  below the reference, every 1x capture byte-identical to the control's; (iii) both fine inactive cells
  fall at least 3 B toward Apple while the guards fall no more than 1 B below the reference; (iv) both
  fine cells within 2 B of Apple where `photo__rrect-md__inactive` reads at least point A's ratio.
- **The phases.** A rung that is not rendered (WAITING for an operator, or depending on a selection not
  yet recorded) is listed `notRead` and never refused; each ladder states whether it is complete. The
  selections the protocol declares (`iii-width-1x`, `iii-width-2x`, `iii-best`) are recorded in
  `selections.json` once the rungs they read are all read, and only then can ladder.py build the rungs
  that depend on them.
- **The decisions part 2 may take** (`operators`): operator 1 separates when a ladder (i) rung meets its
  bar at both scales; the 2x width when a ladder (ii) rung meets its bar; operator 2 when a tap rung of
  ladder (iii) meets its bar at both scales, the body width first when a blurSigma rung does; a
  separation at one scale only is named for the parent, never decided here.

W46 G0's text follows, unchanged; where it says W46 it is W47.

W46 G0 (e): the ladders' reader (charter clause 4; `protocol.json`). Reads only; writes `results.json`
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
- **X60 by evidence**: `stage/x60.py evidence` over the ladder candidates.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402
import ladder as LADDER  # noqa: E402

B, T1, RULE = W.load_cuts()
BARS = T1.load_bars()
SCRATCH = LADDER.SCRATCH
CONF: dict = {}
TIE_B = 0.1


def level():
    """W47's level check (`level/level.py`), imported only where a read needs it (the control's
    identity, L1 on ladder (i)), so the bars and X70 read without it."""
    sys.path.insert(0, str(EVIDENCE / "level"))
    import level as LEVEL  # noqa: PLC0415
    return LEVEL


def census_gate():
    """W47's census gate (`census-gate.py`): the browser pin every row's engine is read against."""
    if "w47_census_gate" not in sys.modules:
        W.load_module("w47_census_gate", EVIDENCE / "census-gate.py")
    return sys.modules["w47_census_gate"]


def sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def matrix_path(label: str, scale: int) -> Path:
    return CONF["scratch"] / label / f"{scale}x" / "matrix.json"


def rendered(label: str) -> bool:
    return all(matrix_path(label, s).exists() for s in (1, 2))


def rows_of(label: str) -> dict:
    out = {}
    for scale in (1, 2):
        path = matrix_path(label, scale)
        if not path.exists():
            raise W.Refusal(f"{label}: no {scale}x render")
        for r in json.loads(path.read_bytes())["cells"]:
            key = (r["key"]["profileKey"], r["key"]["sceneId"])
            if key in out:
                raise W.Refusal(f"{label}: two rows for {key}")
            out[key] = r
    return out


def x70_read(label: str, rows: dict, requested: list[str], sets: str, scenes: dict | None = None) -> None:
    """X70 at read: per scale, requested == planned (re-checked) and measured == planned."""
    for scale in (1, 2):
        profile = W.PROFILE[scale]
        want = {(profile, s) for s in requested}
        plan = LADDER.planned(requested, scale, sets, scenes)
        if plan != want:
            raise W.Refusal(f"{label} {scale}x: X70 REFUSES: compare plans {sorted(s for _, s in plan)[:4]}… for the "
                            f"requested cells; not planned {sorted(s for _, s in want - plan)[:6]}")
        measured = {k for k in rows if k[0] == profile}
        if measured != plan:
            missing, extra = sorted(s for _, s in plan - measured), sorted(s for _, s in measured - plan)
            raise W.Refusal(f"{label} {scale}x: X70 REFUSES the rung: the rows measured are not the cells planned: "
                            f"{len(missing)} missing {missing[:4]}, {len(extra)} extra {extra[:4]}; a partial rung "
                            "decides nothing")


def admit(label: str, rows: dict, requested, sets: str | None = None) -> B.Candidate:
    """X70 (`x70_read`), then W46's admission: the rung's rows, refused unless they are EXACTLY its
    declared cells at both dark scales, each with its structure reading where it is a T1 cell, this
    rung's candidate at its hash, the pinned engine, WebGPU, no withheld cell (X69)."""
    x70_read(label, rows, requested, sets or LADDER.protocol()["sets"])
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
            raise W.Refusal(f"{label} {profile} {sid}: a withheld cell rendered (clause 4's stop)")
    bad = census_gate().pinned_engine(list(rows.values()))
    if bad:
        raise W.Refusal(f"{label}: rows not on the pinned Chromium: {bad[:3]}")
    return candidate


def reading(profile: str, sid: str, row: dict, control: dict) -> dict:
    """One cell's T1 against the control (the snapshots, identical to d0219cd684bf), in bars and in B."""
    n = B.value(row, "material", "interiorStdDevNative")
    k = B.value(row, "material", "interiorStdDevWeb")
    c = B.value(control, "material", "interiorStdDevWeb")
    entry = BARS.get((profile, sid))
    mean = B.value(row, "material", "interiorMeanNative")
    base = dict(scale=B.scale_of(profile), pose=T1.pose(sid), span=B.SCENES.span(sid),
                stratum=T1.stratum(sid) if B.SCENES.by_id[sid]["background"] in T1.T1_BACKDROPS else None)
    if None in (n, k, c) or (entry is None and mean is None):
        return dict(base, native=n, web=k, control=c, ratio=None, controlRatio=None, delta=None, bar=None,
                    B=None, moved=False, g=None)
    if entry:
        bar, code = entry["bar"], entry["code"]
    else:
        code = T1.code_step(mean)
        bar = 0.5 * code
    return dict(base, native=n, web=k, control=c, ratio=k / n if n else None, controlRatio=c / n if n else None,
                delta=k - c, bar=bar, B=max(code, 2 * bar), moved=abs(k - c) > bar, g=abs(k - n) - abs(c - n))


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


# ---------------------------------------------------------------------------------------------------
# Clause 5's bars, as pure functions over a rung's readings: `cells` maps (scale, scene) -> reading.
# ---------------------------------------------------------------------------------------------------
def _at(cells: dict, scale: int, sid: str) -> dict | None:
    r = cells.get((scale, sid))
    return r if r is not None and r.get("g") is not None else None


def point_a(protocol: dict) -> dict:
    """Point A's committed gate cut (pinned in the protocol): (scale, scene) -> its dark WebGPU T1 cell."""
    ref = protocol["pointA"]["cut"]
    path = W.ROOT / ref["path"]
    if W.file_sha(path) != ref["sha256"]:
        raise W.Refusal(f"{ref['path']} is not the pinned point A cut")
    cut = json.loads(gzip.decompress(path.read_bytes()))
    return {(c["scale"], c["scene"]): c for c in cut["T1"]["cells"]
            if c["tier"] == "webgpu" and c["profile"] in W.DARK_025}


def thin_cells(rest: list[str], pa: dict) -> list[str]:
    """Ladder (i)'s thin rest cells: its rest cells with a T1 reading in point A's cut at span class thin."""
    return sorted({sid for (scale, sid), c in pa.items() if sid in set(rest) and c["spanClass"] == "thin"})


def bar_i(cells: dict, thick: list[str], thin: list[str], pa: dict, l1_passes: bool | None) -> dict:
    out = dict(perScale={})
    for scale in (1, 2):
        th = {sid: _at(cells, scale, sid) for sid in thick}
        thick_ok = all(r is not None and abs(r["web"] - r["control"]) <= r["B"] for r in th.values())
        gain, gain_a = 0.0, 0.0
        for sid in thin:
            r, a = _at(cells, scale, sid), pa.get((scale, sid))
            if r is None or a is None:
                continue
            gain += abs(r["control"] - r["native"]) - abs(r["web"] - r["native"])
            gain_a += abs(a["reference"] - a["native"]) - abs(a["candidate"] - a["native"])
        keeps = gain_a > 0 and gain >= 0.5 * gain_a
        out["perScale"][scale] = dict(
            thickWithin1B=thick_ok,
            thickInB={sid: (None if r is None else (r["web"] - r["control"]) / r["B"]) for sid, r in th.items()},
            thinGain=gain, pointAThinGain=gain_a, thinKeepsHalf=keeps, meets=thick_ok and keeps and bool(l1_passes))
    out["L1passes"] = l1_passes
    out["meetsAt"] = [s for s, v in out["perScale"].items() if v["meets"]]
    out["meets"] = len(out["meetsAt"]) == 2
    return out


def bar_ii(cells: dict, one_x_not_identical: list[str]) -> dict:
    fall = {sid: _at(cells, 2, sid) for sid in ("checkerboard-8__rrect-lg__rest", "hc-text__rrect-lg__rest")}
    hold = _at(cells, 2, "checkerboard-64__rrect-lg__rest")
    falls = {sid: (r is not None and RULE.growth_change(r["native"], r["control"], r["web"], r["bar"]) == "toward"
                   and r["web"] < r["control"]) for sid, r in fall.items()}
    holds = hold is not None and hold["web"] >= hold["control"] - hold["bar"]
    return dict(falls=falls, holds=holds, oneXNotIdentical=one_x_not_identical,
                gInB={sid: (None if r is None else r["g"] / r["B"]) for sid, r in fall.items()},
                holdDeltaInBars=None if hold is None else hold["delta"] / hold["bar"],
                meets=all(falls.values()) and holds and not one_x_not_identical)


FINE = ("checkerboard-8__rrect-md__inactive", "checkerboard-8__rrect-lg__inactive")
GUARD = ("checkerboard-64__rrect-md__inactive", "photo__rrect-md__inactive")


def bar_iii(cells: dict) -> dict:
    out = dict(perScale={})
    for scale in (1, 2):
        fine = {sid: _at(cells, scale, sid) for sid in FINE}
        guard = {sid: _at(cells, scale, sid) for sid in GUARD}
        fall = {sid: (None if r is None else -r["g"] / r["B"]) for sid, r in fine.items()}
        fine_ok = all(v is not None and v >= 3 for v in fall.values())
        guard_ok = all(r is not None and r["web"] >= r["control"] - r["B"] for r in guard.values())
        out["perScale"][scale] = dict(fineFallInB=fall, guardsHold=guard_ok,
                                      guardDeltaInB={sid: (None if r is None else (r["web"] - r["control"]) / r["B"])
                                                     for sid, r in guard.items()},
                                      meanFallInB=(statistics.mean(fall.values())
                                                   if all(v is not None for v in fall.values()) else None),
                                      meets=fine_ok and guard_ok)
    out["meetsAt"] = [s for s, v in out["perScale"].items() if v["meets"]]
    out["meets"] = len(out["meetsAt"]) == 2
    return out


def bar_iv(cells: dict, pa: dict) -> dict:
    out = dict(perScale={})
    for scale in (1, 2):
        fine = {sid: _at(cells, scale, sid) for sid in FINE}
        within = {sid: (None if r is None else abs(r["web"] - r["native"]) / r["B"]) for sid, r in fine.items()}
        photo = _at(cells, scale, "photo__rrect-md__inactive")
        floor = pa[(scale, "photo__rrect-md__inactive")]["ratio"]
        photo_ok = photo is not None and photo["ratio"] >= floor
        fine_ok = all(v is not None and v <= 2 for v in within.values())
        out["perScale"][scale] = dict(fineErrorInB=within, photoRatio=None if photo is None else photo["ratio"],
                                      pointAPhotoRatio=floor, photoHolds=photo_ok, meets=fine_ok and photo_ok)
    out["meetsAt"] = [s for s, v in out["perScale"].items() if v["meets"]]
    out["meets"] = len(out["meetsAt"]) == 2
    return out


def select_width(readings: dict, scale: int) -> dict:
    """`iii-width-<scale>x`: among the width rungs (value -> bar_iii reading), those whose guards hold at
    `scale`, the largest mean fall of the fine cells; ties within TIE_B to the smaller width."""
    ok = {w: r["perScale"][scale]["meanFallInB"] for w, r in readings.items()
          if r["perScale"][scale]["guardsHold"] and r["perScale"][scale]["meanFallInB"] is not None}
    if not ok:
        return dict(value=None, why=f"no width rung holds the guards at {scale}x")
    top = max(ok.values())
    value = min(w for w, v in ok.items() if v >= top - TIE_B)
    return dict(value=value, meanFallInB=ok[value], candidates=ok)


def select_best(tap: dict, body: dict) -> dict:
    """`iii-best`: among the tap rungs (label -> (receded overrides, bar_iii reading)) whose guards hold at
    both scales, the largest pooled mean fall; ties within TIE_B to the smaller share, then the smaller
    widths. None: the best body-width rung (`body`, the same shape) instead, said so."""
    def pooled(r):
        v = [r["perScale"][s]["meanFallInB"] for s in (1, 2)]
        return None if None in v else statistics.mean(v)

    def pick(pool):
        ok = {lab: (o, pooled(r)) for lab, (o, r) in pool.items()
              if all(r["perScale"][s]["guardsHold"] for s in (1, 2)) and pooled(r) is not None}
        if not ok:
            return None
        top = max(v for _, v in ok.values())
        tied = [(lab, o) for lab, (o, v) in ok.items() if v >= top - TIE_B]
        tied.sort(key=lambda x: (x[1].get("sizeFineTapShare", 0), x[1].get("sizeFineTapSigma", 0),
                                 x[1].get("sizeFineTapSigma2x", 0), x[1].get("optics.regular.blurSigma", 0)))
        lab, o = tied[0]
        return dict(label=lab, overrides={"receded.dark": o}, pooledMeanFallInB=ok[lab][1])

    got = pick(tap)
    if got:
        return dict(got, form="operator 2")
    got = pick(body)
    if got:
        return dict(got, form="the receded body width (no operator-2 rung admissible)")
    return dict(label=None, overrides=None, why="no ladder (iii) rung holds the guards at both scales")


def summarise(protocol: dict, rungs: list, per: dict, inapplicable: dict) -> tuple[dict, dict, dict]:
    """(ladders, selections, operators) from the rungs read (`per`, label -> entry with its `bar`) and the
    rungs a completed reading made inapplicable (label -> why). A ladder is COMPLETE when every rung is read
    or inapplicable: when ladder (iii)'s width reading found no admissible width at a scale, the share rungs
    that would sit at that width cannot be built, and the ladder is resolved without them, so `iii-best`
    (operator 2's best rung, else the body width's, else none) and the declared decisions proceed —
    body-width-first, or the tap named unfitted (reviewer-medium, W47 G0). A rung merely not yet read keeps
    its ladder incomplete."""
    ladders = {}
    for lad in protocol["ladders"]:
        labels = [x["label"] for x in lad["rungs"]]
        read_ = [lab for lab in labels if lab in per]
        ladders[lad["id"]] = dict(
            complete=all(lab in per or lab in inapplicable for lab in labels), read=read_,
            inapplicable=[lab for lab in labels if lab in inapplicable],
            notRead=[lab for lab in labels if lab not in per and lab not in inapplicable],
            meets=[lab for lab in read_ if per[lab]["bar"]["meets"]],
            meetsAtOneScaleOnly=[lab for lab in read_ if per[lab]["bar"].get("meetsAt") and not per[lab]["bar"]["meets"]],
            passingL1=[lab for lab in read_ if per[lab].get("level", {}).get("L1passes")] if lad["id"] == "i" else None)

    chosen = {}
    width = {r["label"]: r for r in rungs if r.get("ladder") == "iii" and r["label"].startswith("iii-s")}
    if width and all(lab in per for lab in width):
        by_w = {r["overrides"]["receded.dark"]["sizeFineTapSigma"]: per[lab]["bar"] for lab, r in width.items()}
        chosen["iii-width-1x"] = select_width(by_w, 1)
        chosen["iii-width-2x"] = select_width(by_w, 2)
    iii_all = [r for r in rungs if r.get("ladder") == "iii"]
    if iii_all and all(r["label"] in per or r["label"] in inapplicable for r in iii_all):
        tap = {r["label"]: (r["overrides"]["receded.dark"], per[r["label"]]["bar"]) for r in iii_all
               if "sizeFineTapShare" in r["overrides"].get("receded.dark", {}) and r["label"] in per}
        body = {r["label"]: (r["overrides"]["receded.dark"], per[r["label"]]["bar"]) for r in iii_all
                if "optics.regular.blurSigma" in r["overrides"].get("receded.dark", {}) and r["label"] in per}
        chosen["iii-best"] = select_best(tap, body)

    body_meets = [lab for lab in ladders.get("iii", {}).get("meets", []) if lab.startswith("iii-b")]
    tap_meets = [lab for lab in ladders.get("iii", {}).get("meets", []) if not lab.startswith("iii-b")]
    operators = {
        "operator 1": dict(separates=bool(ladders["i"]["meets"]), complete=ladders["i"]["complete"],
                           rungs=ladders["i"]["meets"], oneScaleOnly=ladders["i"]["meetsAtOneScaleOnly"]),
        "2x width": dict(meets=bool(ladders["ii"]["meets"]), complete=ladders["ii"]["complete"],
                         rungs=ladders["ii"]["meets"]),
        "operator 2": dict(separates=bool(tap_meets), bodyWidthMeets=bool(body_meets),
                           complete=ladders["iii"]["complete"], rungs=tap_meets, bodyRungs=body_meets,
                           oneScaleOnly=ladders["iii"]["meetsAtOneScaleOnly"],
                           inapplicable=ladders["iii"]["inapplicable"]),
        "joint": dict(meets=bool(ladders["iv"]["meets"]), complete=ladders["iv"]["complete"]),
    }
    return ladders, chosen, operators


# ---------------------------------------------------------------------------------------------------
def main(scratch: Path | None = None, candidates: Path | None = None, rungs: list | None = None,
         out: Path | None = None, protocol: dict | None = None, x60: bool = True) -> int:
    """The read; its arguments exist for `test_read.py` (a synthetic scratch, candidates and rungs)."""
    CONF.update(scratch=scratch or SCRATCH, candidates=candidates or LADDER.CANDIDATES)
    out = out or HERE
    protocol = protocol or LADDER.protocol()
    rungs = rungs if rungs is not None else LADDER.rungs(protocol, resolve=True)
    sets = protocol["sets"]
    LEVEL = level()
    control_rows = rows_of("control")
    control = admit("control", control_rows, rungs[0]["cells"], sets)
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
    result = dict(schema="w47-ladder-results-1", protocolSha256=W.file_sha(LADDER.PROTOCOL_PATH),
                  control=dict(verdict=instrument["verdict"], cells=instrument["cells"],
                               identical=instrument["pixelAndMeasurementIdentical"],
                               failures=instrument["failures"][:20]),
                  rungs={}, notRead={}, ladders={})
    if instrument["verdict"] != "IDENTICAL":
        result["stop"] = "the control is not identical to d0219cd684bf: an instrument failure; nothing is read"
        (out / "results.json").write_text(json.dumps(result, indent=1) + "\n")
        print(result["stop"])
        return 1
    pa = point_a(protocol)
    lad_i = next(l for l in protocol["ladders"] if l["id"] == "i")
    rest_i = json.loads(W.LADDER_CELLS.read_text())["ladders"]["i"]["rest"]
    thick, thin = lad_i["reads"]["thick"], thin_cells(rest_i, pa)

    per, inapplicable = {}, {}
    for r in rungs[1:]:
        if r.get("inapplicable") and not LADDER.waiting(r):
            inapplicable[r["label"]] = r["inapplicable"]
            continue
        why = LADDER.waiting(r) or r.get("unresolved")
        if why or not rendered(r["label"]):
            result["notRead"][r["label"]] = why or "not rendered"
            continue
        rows = rows_of(r["label"])
        candidate = admit(r["label"], rows, r["cells"], sets)
        cells = {(B.scale_of(p), s): reading(p, s, row, control_rows[(p, s)]) for (p, s), row in rows.items()}
        entry = dict(ladder=r["ladder"], overrides=r["overrides"], actsAt=r["actsAt"],
                     cells={f"{s}x/{sid}": v for (s, sid), v in cells.items()})
        if r["ladder"] == "i":
            lv = LEVEL.check(list(rows.values()), candidate, reference_bed)
            l1 = lv["L1"]["growthClausePasses"] and lv["L1"]["absoluteClausePasses"]
            entry["level"] = dict(L1passes=l1, maxError=lv["L1"]["maxError"], maxGrowth=lv["L1"]["maxGrowth"],
                                  excesses=lv["excesses"], unexplained=lv["unexplained"])
            entry["bar"] = bar_i(cells, thick, thin, pa, l1)
        elif r["ladder"] == "ii":
            entry["bar"] = bar_ii(cells, captures_identical(r["label"], 1, rows.keys()))
        elif r["ladder"] == "iii":
            entry["bar"] = bar_iii(cells)
        else:
            entry["bar"] = bar_iv(cells, pa)
        per[r["label"]] = entry
    result["rungs"] = per
    result["inapplicable"] = inapplicable
    result["ladders"], chosen, result["operators"] = summarise(protocol, rungs, per, inapplicable)
    if chosen:
        (out / "selections.json").write_text(json.dumps(dict(
            schema="w47-ladder-selections-1", protocolSha256=result["protocolSha256"], selections=chosen), indent=1) + "\n")
    result["selections"] = chosen
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
    lines = [f"W47 G0 (g): the ladders read (protocol sha256 {r['protocolSha256'][:12]})",
             f"control: {r['control']['verdict']} ({r['control']['identical']} of {r['control']['cells']} rows pixel- and "
             "measurement-identical to d0219cd684bf)", ""]
    for lab, e in r["rungs"].items():
        b = e["bar"]
        lines.append(f"  ({e['ladder']}) {lab:<22} {'MEETS' if b['meets'] else 'meets at ' + str(b.get('meetsAt')) if b.get('meetsAt') else 'no'}"
                     + (f"; L1 {'passes' if e['level']['L1passes'] else 'FAILS'}" if "level" in e else ""))
    for lab, why in r["notRead"].items():
        lines.append(f"  not read {lab}: {why}")
    for lab, why in r.get("inapplicable", {}).items():
        lines.append(f"  inapplicable {lab}: {why}")
    lines.append("")
    for lad, v in r["ladders"].items():
        lines.append(f"ladder ({lad}): {'complete' if v['complete'] else 'INCOMPLETE'}; meets {v['meets']}"
                     + (f"; inapplicable {v['inapplicable']}" if v.get("inapplicable") else ""))
    for name, v in r["operators"].items():
        lines.append(f"{name}: {json.dumps(v)}")
    for name, v in r.get("selections", {}).items():
        lines.append(f"selection {name}: {json.dumps({k: x for k, x in v.items() if k != 'candidates'})}")
    lines.append(f"X60 by evidence: exit {r['x60']['exitCode']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
