#!/usr/bin/env python3.12
"""W47 G0, Decision Log 8: the ladders re-read under the re-stated bars, on the SAME renders (no render).
Reads only; writes `reread.json` and `reread.txt` beside it.

    python3.12 -B reread.py            (from this directory, after `pnpm -r build`)

The bars are part 1's as amended once under Decision Log 8 (`declaration.json` items `ladders` and
`level`, key `decisionLog8`; `amendments.json`). This reader takes its thresholds from there and refuses
unless the declaration on disk is the last hash of `declaration.sha256` and its one amendment is Decision
Log 8's. `protocol.json`'s bars and `results.json`'s readings stand; this reads beside them.

What it reads, and with what:
- **The rows and the whole band** exactly as `read.py` reads them: every rung's rows re-admitted
  (`read.admit`: X70's three sets, the candidate at its hash, the pinned engine, WebGPU, no withheld
  cell) and each cell's T1 reading (`read.reading`) re-derived and required EQUAL to `results.json`'s,
  so the re-read stands on the same numbers the hashed bars were read on.
- **T1-fine and T1-low** off the rung's and the control's captures in the ladder scratch and the native
  fixture, through W44 G1's pinned `cuts/readings.py` (the diagnostic's and W46 G2's reader). Two
  cross-checks hold the instrument: the control's fine band on the diagnostic's four cells equals
  `diagnostic/reading.json`'s reference values, and the control's bands on a T cell equal W46 G2's dark
  T-band fixture for `d0219cd684bf` (the control is pixel-identical to it).
- **Operator 1** (ladder (i)): the landing rule's own reader, `cuts/rule.py` `reads`, on the five thick
  rest cells: the change band (T1, or T1-fine for the T cell) partitions by `growth_change` against the
  control; the away band (T1, or T1-low) prices growth in B. Per scale: none away beyond the ceiling,
  at most the declared count away beyond B, every cell over Apple at the reference reading `toward`,
  the thin clause (`read.bar_i`'s, unchanged) and L1 (`results.json`'s level reading, unchanged).
  The level check's unexplained excesses are listed beside L1 and gate nothing.
- **Operator 2** (ladder (iii)): each fine cell's fine-band E and R (the diagnostic's), R at least the
  declared minimum; the guards' whole-band clause unchanged; the whole-band fall and the fine-band error
  ratio reported beside.
- **The joint** (ladder (iv)): operator 1's partition clauses on the four fine cells (stratum F: the
  rule reads them on T1) and operator 2's fine-band halving on the same cells, with the photo inactive
  ratio at least point A's. Each component is reported on its own.
- **The outcome**: an operator separates when one rung meets at BOTH scales (the parent's ruling,
  unchanged); a body-width rung meeting at both is body-width-first; a rung meeting at one scale only is
  named for the parent. Ladder (ii) is not re-stated and is not re-read.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402
import ladder as LADDER  # noqa: E402
import read as READ  # noqa: E402

B, T1, RULE = READ.B, READ.T1, READ.RULE
sys.path.insert(0, str(W.W44_G1 / "cuts"))
import readings as FINE  # noqa: E402

FINE_CELLS = READ.FINE
GUARD_CELLS = READ.GUARD
PHOTO = "photo__rrect-md__inactive"
FIXTURES = W.ROOT / "apps/reference-apple/fixtures"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def declared_bars() -> tuple[dict, dict, dict]:
    """(ladders' decisionLog8, level's decisionLog8, the amendment record), refusing unless the declaration
    on disk is the chain's last hash and its one amendment is Decision Log 8's."""
    raw = W.PART1.read_bytes()
    # The whole chain and the record's read-time validation first (declare.py's own `chain`, which runs
    # `amendment_failures`: the verbatim ruling, the post-render additive form, the superseded hash).
    sys.path.insert(0, str(EVIDENCE))
    import declare as D  # noqa: PLC0415
    c = D.Check()
    D.chain(c, "protocol", json.loads(raw))
    if c.failures:
        raise W.Refusal(f"part 1's amendment chain does not validate: {c.failures[:3]}")
    lines = [ln.split()[0] for ln in W.PART1_DIGEST.read_text().splitlines() if ln.strip()]
    if sha(raw) != lines[-1]:
        raise W.Refusal("declaration.json is not the last hash of declaration.sha256")
    record = json.loads((EVIDENCE / "amendments.json").read_text())["amendments"]
    if len(record) != 1 or not record[0]["ruling"].startswith("### Decision Log 8 ") \
            or record[0]["declarationSha256"] != lines[-1]:
        raise W.Refusal("part 1's one amendment is not Decision Log 8's at the current hash")
    items = {it["id"]: it for it in json.loads(raw)["items"]}
    return items["ladders"]["declared"]["decisionLog8"], items["level"]["declared"]["decisionLog8"], record[0]


# ---------------------------------------------------------------------------------------------------
# The bars as pure functions (tested on synthetic readings in test_reread.py)
# ---------------------------------------------------------------------------------------------------
def partition(reads_by_cell: dict, ceiling_b: float, beyond_b_max: int) -> dict:
    """Operator 1's partition clauses over `reads_by_cell` (scene -> `rule.reads` output)."""
    beyond, over_ceiling, over_not_toward = [], [], []
    for sid, r in reads_by_cell.items():
        a, ch = r["away"], r["change"]
        if a["change"] == "away" and a["growth"] > a["B"]:
            beyond.append(sid)
        if a["change"] == "away" and a["growth"] > ceiling_b * a["B"]:
            over_ceiling.append(sid)
        if ch["c"] > ch["n"] and ch["change"] != "toward":
            over_not_toward.append(sid)
    return dict(awayBeyondB=beyond, awayBeyondCeiling=over_ceiling, overAppleNotToward=over_not_toward,
                ceilingHolds=not over_ceiling, countHolds=len(beyond) <= beyond_b_max,
                overAppleToward=not over_not_toward,
                holds=not over_ceiling and len(beyond) <= beyond_b_max and not over_not_toward)


def fine_halving(fine: dict, minimum: float) -> dict:
    """Operator 2's fine-band clause: `fine` maps scene -> {native, reference, rung} on T1-fine."""
    out, ok = {}, True
    for sid, f in fine.items():
        e = f["reference"] - f["native"]
        r = (f["reference"] - f["rung"]) / e if e > 0 else None
        err = abs(f["rung"] - f["native"]) / abs(e) if e else None
        out[sid] = dict(E=e, R=r, errorRatio=err)
        ok = ok and r is not None and r >= minimum
    return dict(cells=out, holds=ok)


def guards_hold(guards: dict, floor_b: float) -> dict:
    """The guards' clause, unchanged: whole-band k >= c - floor_b x B on each guard (scene -> reading)."""
    got = {sid: (r["web"] - r["control"]) / r["B"] for sid, r in guards.items()}
    return dict(deltaInB=got, holds=all(v >= -floor_b for v in got.values()))


def outcome(per_rung: dict) -> dict:
    """(rungs meeting at both scales, at one scale only) from {label: {scale: meets}}."""
    both = [lab for lab, s in per_rung.items() if s[1] and s[2]]
    one = [lab for lab, s in per_rung.items() if (s[1] or s[2]) and not (s[1] and s[2])]
    return dict(meetsBoth=both, meetsOneScaleOnly=one)


# ---------------------------------------------------------------------------------------------------
class Captures:
    """T1-fine and T1-low off the ladder scratch's captures, through W44 G1's readings.py."""

    def __init__(self, scratch: Path):
        self.scratch, self.geometry, self.native_img, self.cache = scratch, {}, {}, {}

    @staticmethod
    def rgb(path: Path) -> np.ndarray:
        return np.asarray(Image.open(path).convert("RGB"))

    def png(self, label: str, scale: int, sid: str) -> Path:
        prof = W.PROFILE[scale]
        return self.scratch / label / f"{scale}x" / "web-captures" / prof / sid / f"{sid}__webgpu.png"

    def bands(self, label: str, scale: int, sid: str, row: dict) -> dict:
        """{native: {fine, low}, web: {fine, low}, webSha256} for the rung's capture of one cell, admitted
        first against its matrix row: the capture's sidecar must name the row's capturePath (which carries
        the candidate's documents), so a capture copied in from another rung is refused."""
        key = (label, scale, sid)
        if key not in self.cache:
            prof = W.PROFILE[scale]
            meta = json.loads((self.png(label, scale, sid).parent / "cell__webgpu.json").read_text())
            if meta.get("capturePath") != row["key"]["web"]["capturePath"]:
                raise W.Refusal(f"{label} {scale}x {sid}: the capture names another render than its row")
            if (scale, sid) not in self.geometry:
                self.native_img[(scale, sid)] = self.rgb(FIXTURES / prof / f"{sid}.png")
                self.geometry[(scale, sid)] = FINE.cell_geometry(prof, sid, self.native_img[(scale, sid)])
            path = self.png(label, scale, sid)
            got = FINE.read(prof, sid, self.native_img[(scale, sid)], self.rgb(path), self.geometry[(scale, sid)])
            self.cache[key] = dict(native={b: got["native"][b] for b in ("fine", "low")},
                                   web={b: got["web"][b] for b in ("fine", "low")},
                                   webSha256=sha(path.read_bytes()))
        return self.cache[key]


def rule_cell(scale: int, sid: str, reading: dict, cap: Captures, label: str, rows: dict, control: dict) -> dict:
    """The landing rule's cell for one thick or fine cell: whole-band T1, and a T cell's two bands."""
    prof = W.PROFILE[scale]
    entry = READ.BARS[(prof, sid)]
    cell = dict(scene=sid, stratum=T1.stratum(sid), native=reading["native"], reference=reading["control"],
                candidate=reading["web"], bar=entry["bar"], code=entry["code"])
    if cell["stratum"] == "T":
        key = (prof, sid)
        k, c = cap.bands(label, scale, sid, rows[key]), cap.bands("control", scale, sid, control[key])
        cell["bands"] = {b: dict(native=k["native"][b], reference=c["web"][b], candidate=k["web"][b])
                         for b in ("fine", "low")}
    return cell


def brief(r: dict) -> dict:
    return {k: r[k] for k in ("n", "c", "k", "B", "growth", "change")} | dict(growthInB=r["growth"] / r["B"])


def main() -> int:
    bars, level_bar, amendment = declared_bars()
    op1, op2, joint = bars["operator 1"], bars["operator 2"], bars["joint"]
    protocol = LADDER.protocol()
    results = json.loads((HERE / "results.json").read_text())
    if results["protocolSha256"] != W.file_sha(LADDER.PROTOCOL_PATH):
        raise W.Refusal("results.json was not read under the hashed protocol")
    if results["control"]["verdict"] != "IDENTICAL":
        raise W.Refusal("the control was not read IDENTICAL; nothing is re-read")
    READ.CONF.update(scratch=LADDER.SCRATCH, candidates=LADDER.CANDIDATES)
    rungs = {r["label"]: r for r in LADDER.rungs(protocol, resolve=True)}
    sets = protocol["sets"]
    control_rows = READ.rows_of("control")
    READ.admit("control", control_rows, rungs["control"]["cells"], sets)
    cap = Captures(LADDER.SCRATCH)
    pa = READ.point_a(protocol)
    lad_i = next(l for l in protocol["ladders"] if l["id"] == "i")
    thick = lad_i["reads"]["thick"]
    thin = READ.thin_cells(json.loads(W.LADDER_CELLS.read_text())["ladders"]["i"]["rest"], pa)

    # The instrument's two cross-checks.
    diag = {(c["scale"], c["scene"]): c for c in json.loads((EVIDENCE / "diagnostic/reading.json").read_text())["rows"]}
    checks = []
    for (s, sid), row in sorted(diag.items()):
        got = cap.bands("control", s, sid, control_rows[(W.PROFILE[s], sid)])
        checks.append(dict(what=f"control T1-fine {s}x {sid} against diagnostic/reading.json",
                           equal=got["web"]["fine"] == row["fine"]["control"]
                           and got["native"]["fine"] == row["fine"]["native"]))
    tb = json.loads(W.W46_T_BANDS.read_text())
    for e in tb["entries"]:
        if e["scene"] in thick:
            s = B.scale_of(e["profile"])
            got = cap.bands("control", s, e["scene"], control_rows[(e["profile"], e["scene"])])
            checks.append(dict(what=f"control bands {s}x {e['scene']} against W46 G2's d0219cd684bf T-band fixture",
                               equal=all(got["web"][b] == e["bands"][b]["web"] and got["native"][b] == e["bands"][b]["native"]
                                         for b in ("fine", "low"))))
    if not checks or not all(c["equal"] for c in checks):
        raise W.Refusal(f"the fine reader does not reproduce its references: {[c for c in checks if not c['equal']]}")

    out = dict(schema="w47-ladder-reread-1",
               what="W47 G0: the ladders re-read under part 1's bars as amended once under Decision Log 8, on the "
                    "same renders; protocol.json's bars and results.json's readings stand beside it",
               declarationSha256=amendment["declarationSha256"], supersedes=amendment["supersedes"],
               protocolSha256=results["protocolSha256"], resultsSha256=sha((HERE / "results.json").read_bytes()),
               readers={str(p.relative_to(W.ROOT)): sha(p.read_bytes()) for p in (
                   W.READINGS_PATH, EVIDENCE / "cuts/rule.py", HERE / "read.py", Path(__file__))},
               instrument=checks, bars=bars, levelBar=level_bar, rungs={})
    per1, per2 = {}, {}
    for label, res in results["rungs"].items():
        if res["ladder"] not in ("i", "iii", "iv"):
            continue
        rows = READ.rows_of(label)
        READ.admit(label, rows, rungs[label]["cells"], sets)
        cells = {(B.scale_of(p), s): READ.reading(p, s, row, control_rows[(p, s)]) for (p, s), row in rows.items()}
        if {f"{s}x/{sid}": v for (s, sid), v in cells.items()} != res["cells"]:
            raise W.Refusal(f"{label}: the rows no longer give results.json's readings")
        entry = dict(ladder=res["ladder"], overrides=res["overrides"], perScale={})
        for s in (1, 2):
            if res["ladder"] == "i":
                reads = {sid: RULE.reads(rule_cell(s, sid, cells[(s, sid)], cap, label, rows, control_rows)) for sid in thick}
                part = partition(reads, op1["awayCeilingB"], op1["awayBeyondBMax"])
                old = READ.bar_i(cells, thick, thin, pa, res["level"]["L1passes"])["perScale"][s]
                l1 = res["level"]["L1passes"]
                entry["perScale"][s] = dict(
                    thick={sid: dict(stratum=T1.stratum(sid),
                                     changeBand=brief(reads[sid]["change"]), awayBand=brief(reads[sid]["away"]),
                                     wholeBand=dict(kMinusCInB=(cells[(s, sid)]["web"] - cells[(s, sid)]["control"])
                                                    / cells[(s, sid)]["B"],
                                                    gInB=cells[(s, sid)]["g"] / cells[(s, sid)]["B"]))
                           for sid in thick},
                    partition=part, thinGain=old["thinGain"], pointAThinGain=old["pointAThinGain"],
                    thinKeepsHalf=old["thinKeepsHalf"], L1passes=l1,
                    meets=part["holds"] and old["thinKeepsHalf"] and bool(l1))
            else:
                fine = {}
                for sid in FINE_CELLS:
                    k = cap.bands(label, s, sid, rows[(W.PROFILE[s], sid)])
                    c = cap.bands("control", s, sid, control_rows[(W.PROFILE[s], sid)])
                    fine[sid] = dict(native=k["native"]["fine"], reference=c["web"]["fine"], rung=k["web"]["fine"])
                halving = fine_halving(fine, op2["fineExcessRemovedMin"] if res["ladder"] == "iii"
                                       else joint["fineExcessRemovedMin"])
                for sid in FINE_CELLS:
                    halving["cells"][sid].update(fine[sid], wholeFallInB=-cells[(s, sid)]["g"] / cells[(s, sid)]["B"],
                                                 wholeRatio=cells[(s, sid)]["ratio"],
                                                 wholeControlRatio=cells[(s, sid)]["controlRatio"])
                beside = {}
                for sid in sorted({sid for (sc, sid) in cells if sc == s} - set(FINE_CELLS)):
                    k = cap.bands(label, s, sid, rows[(W.PROFILE[s], sid)])
                    c = cap.bands("control", s, sid, control_rows[(W.PROFILE[s], sid)])
                    r = cells[(s, sid)]
                    beside[sid] = dict(wholeGInB=None if r["g"] is None else r["g"] / r["B"], wholeRatio=r["ratio"],
                                       fine=dict(native=k["native"]["fine"], reference=c["web"]["fine"],
                                                 rung=k["web"]["fine"]))
                if res["ladder"] == "iii":
                    g = guards_hold({sid: cells[(s, sid)] for sid in GUARD_CELLS}, op2["guardFloorB"])
                    entry["perScale"][s] = dict(fine=halving, guards=g, beside=beside,
                                                meets=halving["holds"] and g["holds"])
                else:
                    reads = {sid: RULE.reads(rule_cell(s, sid, cells[(s, sid)], cap, label, rows, control_rows)) for sid in FINE_CELLS}
                    photo = cells[(s, PHOTO)]
                    floor = pa[(s, PHOTO)]["ratio"]
                    entry["perScale"][s] = dict(
                        fine=halving, partitionReads={sid: dict(changeBand=brief(r["change"]), awayBand=brief(r["away"]))
                                                      for sid, r in reads.items()},
                        reads=reads, photo=dict(
                            ratio=photo["ratio"], pointA=floor, holds=photo["ratio"] >= floor,
                            # Beside, deciding nothing: the web SD's distance from point A's, in its bars.
                            deltaFromPointAInBars=(photo["web"] - pa[(s, PHOTO)]["candidate"]) / photo["bar"]),
                        beside=beside)
        if res["ladder"] == "iv":
            # The partition over the four cells together (both scales), then each component.
            by_scale = {s: entry["perScale"][s].pop("reads") for s in (1, 2)}
            reads4 = {f"{s}x/{sid}": by_scale[s][sid] for s in (1, 2) for sid in FINE_CELLS}
            part = partition(reads4, joint["awayCeilingB"], joint["awayBeyondBMax"])
            entry["joint"] = dict(partition=part,
                                  fineHalving={s: entry["perScale"][s]["fine"]["holds"] for s in (1, 2)},
                                  photoHolds={s: entry["perScale"][s]["photo"]["holds"] for s in (1, 2)})
            entry["joint"]["meets"] = (part["holds"] and all(entry["joint"]["fineHalving"].values())
                                       and all(entry["joint"]["photoHolds"].values()))
        else:
            entry["meetsAt"] = [s for s in (1, 2) if entry["perScale"][s]["meets"]]
            (per1 if res["ladder"] == "i" else per2)[label] = {s: entry["perScale"][s]["meets"] for s in (1, 2)}
        if res["ladder"] == "i":
            lv = res["level"]
            entry["level"] = dict(L1passes=lv["L1passes"], maxError=lv["maxError"], maxGrowth=lv["maxGrowth"],
                                  unexplained=[x for x in lv["excesses"] if x["attribution"] == "unexplained"],
                                  note="read beside L1 under Decision Log 8 item 4; gates nothing")
        out["rungs"][label] = entry

    o1 = outcome(per1)
    tap = {lab: v for lab, v in per2.items() if not lab.startswith("iii-b")}
    body = {lab: v for lab, v in per2.items() if lab.startswith("iii-b")}
    o2, ob = outcome(tap), outcome(body)
    sep1, sep2 = bool(o1["meetsBoth"]), bool(o2["meetsBoth"]) or bool(ob["meetsBoth"])
    out["operators"] = {
        "operator 1": dict(separates=sep1, **o1),
        "operator 2": dict(separates=bool(o2["meetsBoth"]), bodyWidthMeets=bool(ob["meetsBoth"]),
                           tap=o2, body=ob),
        "joint": dict(meets=out["rungs"]["iv-joint"]["joint"]["meets"]) if "iv-joint" in out["rungs"] else None}
    one_scale = o1["meetsOneScaleOnly"] + o2["meetsOneScaleOnly"] + ob["meetsOneScaleOnly"]
    if sep1 and sep2:
        verdict = "BOTH separate: part 2 is drafted and hashed"
    elif sep1 or sep2:
        verdict = "ONE separates (" + ("operator 1" if sep1 else "operator 2") + "): STOP for the parent"
    else:
        verdict = "NEITHER separates: the wave closes at G0 with the finding"
    if one_scale:
        verdict += f"; rungs meeting at one scale only, named for the parent: {one_scale}"
    out["outcome"] = verdict
    (HERE / "reread.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    (HERE / "reread.txt").write_text(report(out))
    print(report(out))
    return 0


def f(x, spec="+.2f"):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else format(x, spec)


def report(r: dict) -> str:
    L = [f"W47 G0: the ladders re-read under Decision Log 8 (part 1 {r['declarationSha256'][:12]}, superseding "
         f"{r['supersedes'][:12]}); same renders, no new render",
         f"instrument: {sum(c['equal'] for c in r['instrument'])} of {len(r['instrument'])} cross-checks equal "
         "(the control's T1-fine against the diagnostic; its bands against W46 G2's d0219 T-band fixture)", "",
         "(i) operator 1: the rule's partition on the five thick rest cells. Per cell: change-band growth in B and "
         "its partition (O/U = over/under Apple at the reference); away-band growth in B for the T cell",
         "    cells: " + ", ".join(r["rungs"]["i-a0.7"]["perScale"][1]["thick"]) if "i-a0.7" in r["rungs"] else ""]
    for lab, e in r["rungs"].items():
        if e["ladder"] != "i":
            continue
        for s in (1, 2):
            p = e["perScale"][s]
            cells = []
            for sid, c in p["thick"].items():
                ch = c["changeBand"]
                tag = "O" if ch["c"] > ch["n"] else "U"
                extra = f"/low {c['awayBand']['growthInB']:+.2f}" if c["stratum"] == "T" else ""
                cells.append(f"{tag}{ch['growthInB']:+.2f} {ch['change'][:3]}{extra}")
            pt = p["partition"]
            L.append(f"  {lab:<18} {s}x  " + " | ".join(cells)
                     + f"  -> >3B {len(pt['awayBeyondCeiling'])}, >B {len(pt['awayBeyondB'])}, over-not-toward "
                       f"{len(pt['overAppleNotToward'])}; thin {p['thinGain']:.4f}/{p['pointAThinGain']:.4f} "
                       f"{'keeps' if p['thinKeepsHalf'] else 'LOSES'}; L1 {'ok' if p['L1passes'] else 'FAILS'}"
                       f"  {'MEETS' if p['meets'] else 'no'}")
        lv = e["level"]
        L.append(f"  {'':<18}     level beside L1 (max error {lv['maxError']:.4f}, growth {lv['maxGrowth']:+.4f}): "
                 + ("; ".join(f"{x['cell'].split('/')[0].split('-')[3]} {x['cell'].split('/')[1]} {x['excess'][0]}"
                              for x in lv["unexplained"]) or "no unexplained excess"))
    L += ["", "(iii) operator 2: per fine cell R = share of the T1-fine excess removed (bar >= 0.5), the fine-band "
          "error ratio, and the whole-band fall -g/B; guards' whole-band delta in B (floor -1)"]
    for lab, e in r["rungs"].items():
        if e["ladder"] not in ("iii", "iv"):
            continue
        for s in (1, 2):
            p = e["perScale"][s]
            fine = " | ".join(f"R {f(c['R'], '.3f')} err x{f(c['errorRatio'], '.3f')} whole {f(c['wholeFallInB'])}B"
                              for c in p["fine"]["cells"].values())
            if e["ladder"] == "iii":
                g = p["guards"]["deltaInB"]
                L.append(f"  {lab:<10} {s}x  {fine}  guards {' / '.join(f(v) for v in g.values())}  "
                         f"{'MEETS' if p['meets'] else 'no'}")
            else:
                pr = " | ".join(f"{c['changeBand']['change'][:3]} g {c['changeBand']['growthInB']:+.2f}B"
                                for c in p["partitionReads"].values())
                L.append(f"  {lab:<10} {s}x  {fine}  partition {pr}  photo x{p['photo']['ratio']:.3f} "
                         f"(point A x{p['photo']['pointA']:.4f}; {p['photo']['deltaFromPointAInBars']:+.2f} bar from it) "
                         f"{'holds' if p['photo']['holds'] else 'BELOW'}")
        if e["ladder"] == "iv":
            j = e["joint"]
            L.append(f"  joint: partition {'holds' if j['partition']['holds'] else 'FAILS'} "
                     f"({json.dumps({k: j['partition'][k] for k in ('awayBeyondB', 'awayBeyondCeiling', 'overAppleNotToward')})}); "
                     f"fine halving {j['fineHalving']}; photo {j['photoHolds']}  {'MEETS' if j['meets'] else 'no'}")
    L += ["", f"operator 1: {json.dumps(r['operators']['operator 1'])}",
          f"operator 2: {json.dumps(r['operators']['operator 2'])}",
          f"joint: {json.dumps(r['operators']['joint'])}", "", f"OUTCOME: {r['outcome']}"]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
