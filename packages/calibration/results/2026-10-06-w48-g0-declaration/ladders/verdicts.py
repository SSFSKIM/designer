#!/usr/bin/env python3.12
"""W48 G0 (d): the verdict reader (charter `2026-10-06-w48-dark-operators-fit.md`, clause 3; Decision Log 3;
X71-X73). Reads only; writes `verdicts.json` and `verdicts.txt` beside it.

    python3.12 -B verdicts.py        (from this directory; refuses before part 1 is hashed)

No pixel is read and no T1 is computed. W47's ladder evidence is read BY KEY from the two files part 1
pins (X71): `reread.json` (W47 Decision Log 8's re-read: per rung and scale, each thick cell's change
and away band as `cuts/rule.py reads()` gave them, the thin clause, L1, each fine cell's T1-fine
reference / native / rung and R, the guards' whole-band delta in B, the joint's partition reads and
photo ratio) and `results.json` (ladder (ii), which is not re-read; each rung's whole-band `moved`
flags; ladder (i)'s L1 passing rungs). Every number in `verdicts.json` is one of theirs, or recomputed
from theirs and required equal (R).

The bars are `protocol.json`'s, Decision Log 3's corrected forms (X72), taken from the protocol by key:
- **(a) operator 1**, per scale on the five thick rest cells: no away-band `away` growth beyond
  `awayCeilingB` B, at most `awayBeyondBMax` beyond B, no cell over Apple at the reference (change
  band c > n) reading `away` (`toward` and `unchanged` both admitted); the thin clause and L1 as W47
  read them.
- **(b) operator 2**, per scale: both fine cells' T1-fine excess E > 0 with R >= `fineExcessRemovedMin`;
  both guards' whole-band (k - c) / B >= -`guardFloorB`; the whole-band fall beside.
- **(c) the joint**: (a)'s partition over the four fine readings and (b)'s halving on each, the photo
  ratio against point A's reported and deciding nothing; ladder (iv) decides only name-target.
- **Separation**: a rung meets when it meets at BOTH scales. The tap and the body width are read
  separately and both may meet (no precedence). A rung meeting at one scale only is recorded; one the
  parent did not rule off the grid (`protocol.json offGrid.oneScale`) stops part 2 for the parent.

The charter's expectations (`protocol.json expected`, hashed in part 1 before this runs) are compared
with the reading and every difference is listed; nothing is absorbed.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
SCALES = (1, 2)


class Refusal(SystemExit):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def at_scale(per_scale: dict, s: int):
    """reread.json's perScale keys are JSON strings; a synthetic fixture may use ints."""
    return per_scale[str(s)] if str(s) in per_scale else per_scale[s]


# ---------------------------------------------------------------------------------------------------
# The bars, as pure functions over the files' records (tested on synthetic records in test_verdicts.py)
# ---------------------------------------------------------------------------------------------------
def partition(cells: dict, bar: dict) -> dict:
    """Bar (a)'s partition over `cells` (key -> {"change": band, "away": band}, each band
    {n, c, k, B, growth, change} as rule.reads() recorded it): away beyond B and beyond the ceiling on the
    away band; an over-Apple cell (change band c > n) reading a state the bar does not admit."""
    beyond, ceiling, over = [], [], []
    for key, r in cells.items():
        a, ch = r["away"], r["change"]
        if a["change"] == "away" and a["growth"] > a["B"]:
            beyond.append(key)
        if a["change"] == "away" and a["growth"] > bar["awayCeilingB"] * a["B"]:
            ceiling.append(key)
        if ch["c"] > ch["n"] and ch["change"] not in bar["overAppleAdmits"]:
            over.append(key)
    return dict(awayBeyondB=beyond, awayBeyondCeiling=ceiling, overAppleNotAdmitted=over,
                ceilingHolds=not ceiling, countHolds=len(beyond) <= bar["awayBeyondBMax"], overAppleHolds=not over,
                holds=not ceiling and len(beyond) <= bar["awayBeyondBMax"] and not over)


def halving(fine: dict, minimum: float) -> dict:
    """Bar (b)'s fine clause: `fine` maps cell -> {native, reference, rung, R} on T1-fine. R is recomputed as
    (reference - rung) / (reference - native) and must equal the record's (traceability)."""
    out, ok = {}, True
    for sid, f in fine.items():
        e = f["reference"] - f["native"]
        r = (f["reference"] - f["rung"]) / e if e > 0 else None
        if "R" in f and f["R"] != r:
            raise Refusal(f"{sid}: R recomputed {r!r} is not the record's {f['R']!r}")
        out[sid] = dict(native=f["native"], reference=f["reference"], rung=f["rung"], E=e, R=r,
                        meets=r is not None and r >= minimum,
                        **({"wholeFallInB": f["wholeFallInB"]} if "wholeFallInB" in f else {}))
        ok = ok and out[sid]["meets"]
    return dict(cells=out, holds=ok)


def guards(delta_in_b: dict, floor_b: float) -> dict:
    return dict(deltaInB=dict(delta_in_b), holds=all(v >= -floor_b for v in delta_in_b.values()))


def operator1_scale(p: dict, bar: dict) -> dict:
    """One scale of a ladder (i) rung: reread.json's perScale entry."""
    cells = {sid: dict(change=p["thick"][sid]["changeBand"], away=p["thick"][sid]["awayBand"]) for sid in bar["cells"]}
    part = partition(cells, bar)
    return dict(partition=part, thinGain=p["thinGain"], pointAThinGain=p["pointAThinGain"],
                thinKeepsHalf=p["thinKeepsHalf"], L1passes=p["L1passes"],
                changeGrowthInB={sid: c["change"]["growth"] / c["change"]["B"] for sid, c in cells.items()},
                changeState={sid: c["change"]["change"] for sid, c in cells.items()},
                overApple={sid: c["change"]["c"] > c["change"]["n"] for sid, c in cells.items()},
                meets=part["holds"] and bool(p["thinKeepsHalf"]) and bool(p["L1passes"]))


def operator2_scale(p: dict, bar: dict) -> dict:
    """One scale of a ladder (iii) rung."""
    fine = {sid: p["fine"]["cells"][sid] for sid in bar["fine"]}
    h = halving(fine, bar["fineExcessRemovedMin"])
    g = guards({sid: p["guards"]["deltaInB"][sid] for sid in bar["guards"]}, bar["guardFloorB"])
    return dict(fine=h, guards=g, meets=h["holds"] and g["holds"])


def joint(entry: dict, bar: dict) -> dict:
    """Ladder (iv)'s one rung: (a)'s partition over the four fine readings, (b)'s halving per scale, the
    photo ratio reported."""
    reads, halves, photo = {}, {}, {}
    for s in SCALES:
        p = at_scale(entry["perScale"], s)
        for sid in bar["cells"]:
            pr = p["partitionReads"][sid]
            reads[f"{s}x/{sid}"] = dict(change=pr["changeBand"], away=pr["awayBand"])
        halves[s] = halving({sid: p["fine"]["cells"][sid] for sid in bar["cells"]}, bar["fineExcessRemovedMin"])
        ph = p["photo"]
        photo[s] = dict(ratio=ph["ratio"], pointA=ph["pointA"], atOrAbovePointA=ph["ratio"] >= ph["pointA"],
                        deltaFromPointAInBars=ph["deltaFromPointAInBars"])
    part = partition(reads, bar)
    return dict(partition=part, halving=halves, photo=photo,
                holds=part["holds"] and all(h["holds"] for h in halves.values()),
                decides="name-target only (protocol.json decides.iv); the photo ratio is reported and decides nothing")


def outcome(per_rung: dict) -> dict:
    """(labels meeting at both scales, at one scale only) from {label: {scale: meets}}."""
    both = [lab for lab, s in per_rung.items() if s[1] and s[2]]
    one = [lab for lab, s in per_rung.items() if (s[1] or s[2]) and not (s[1] and s[2])]
    return dict(meetsBoth=both, meetsOneScaleOnly=one)


def read(protocol: dict, reread: dict, results: dict) -> dict:
    """The verdicts from the two files' records under `protocol`'s bars."""
    bars = protocol["bars"]
    rungs, flags = {}, {}
    for lid in ("i", "iii"):
        for label in protocol["ladders"][lid]["rungs"]:
            entry = reread["rungs"].get(label)
            if entry is None:
                raise Refusal(f"{label}: no re-read record; a verdict needs a reading W47 did not make (X71 STOP)")
            fn, bar = (operator1_scale, bars["operator 1"]) if lid == "i" else (operator2_scale, bars["operator 2"])
            per = {s: fn(at_scale(entry["perScale"], s), bar) for s in SCALES}
            rungs[label] = dict(ladder=lid, overrides=entry["overrides"], perScale=per,
                                meetsAt=[s for s in SCALES if per[s]["meets"]],
                                meets=all(per[s]["meets"] for s in SCALES))
            flags[label] = {s: per[s]["meets"] for s in SCALES}
    jl = protocol["ladders"]["iv"]["rungs"]
    if len(jl) != 1 or jl[0] not in reread["rungs"]:
        raise Refusal("ladder (iv): its one rung has no re-read record (X71 STOP)")
    j = joint(reread["rungs"][jl[0]], bars["joint"])
    rungs[jl[0]] = dict(ladder="iv", overrides=reread["rungs"][jl[0]]["overrides"], joint=j, meets=j["holds"])

    levers = protocol["levers"]
    o1 = outcome({lab: flags[lab] for lab in levers["operator 1"]})
    o2 = outcome({lab: flags[lab] for lab in levers["operator 2"]})
    ob = outcome({lab: flags[lab] for lab in levers["body width"]})
    ruled = {x["rung"] for x in protocol["offGrid"]["oneScale"]}
    one = o1["meetsOneScaleOnly"] + o2["meetsOneScaleOnly"] + ob["meetsOneScaleOnly"]
    unruled = [lab for lab in one if lab not in ruled]
    ruled_now_both = [lab for lab in ruled if lab in o2["meetsBoth"] + ob["meetsBoth"] + o1["meetsBoth"]]
    width = (results.get("operators") or {}).get("2x width") or {}
    lad = results.get("ladders") or {}
    ops = {
        "operator 1": dict(separates=bool(o1["meetsBoth"]), rungs=o1["meetsBoth"],
                           oneScaleOnly=o1["meetsOneScaleOnly"], complete=True),
        "operator 2": dict(separates=bool(o2["meetsBoth"]), rungs=o2["meetsBoth"], oneScaleOnly=o2["meetsOneScaleOnly"],
                           bodyWidthMeets=bool(ob["meetsBoth"]), bodyRungs=ob["meetsBoth"],
                           bodyOneScaleOnly=ob["meetsOneScaleOnly"], complete=True,
                           members=(["the tap"] if o2["meetsBoth"] else []) + (["the body width"] if ob["meetsBoth"] else [])),
        "2x width": dict(meets=bool(width.get("meets")), rungs=list(width.get("rungs") or []),
                         complete=bool(width.get("complete")), source="results.json operators['2x width'] (not re-read)"),
        "joint": dict(meets=j["holds"], partitionHolds=j["partition"]["holds"],
                      halvingHolds=all(h["holds"] for h in j["halving"].values()),
                      photoAtOrAbovePointA={s: j["photo"][s]["atOrAbovePointA"] for s in SCALES},
                      decides="name-target only"),
    }
    oneScale = dict(rungs=one, ruledOffGrid=sorted(set(one) & ruled), unruled=unruled,
                    ruledButMeetsBoth=ruled_now_both)
    flat = {lab: not any(c.get("moved") for c in r["cells"].values()) for lab, r in results["rungs"].items()}
    ladders = {
        "i": dict(complete=True, rungs=protocol["ladders"]["i"]["rungs"], meets=o1["meetsBoth"],
                  meetsAtOneScaleOnly=o1["meetsOneScaleOnly"], passingL1=list(lad.get("i", {}).get("passingL1") or [])),
        "ii": dict(complete=bool(lad.get("ii", {}).get("complete")), meets=list(lad.get("ii", {}).get("meets") or []),
                   source="results.json (not re-read)"),
        "iii": dict(complete=True, rungs=protocol["ladders"]["iii"]["rungs"], meets=o2["meetsBoth"] + ob["meetsBoth"],
                    meetsAtOneScaleOnly=o2["meetsOneScaleOnly"] + ob["meetsOneScaleOnly"]),
        "iv": dict(complete=True, meets=[jl[0]] if j["holds"] else []),
    }
    sep1, sep2 = ops["operator 1"]["separates"], ops["operator 2"]["separates"] or ops["operator 2"]["bodyWidthMeets"]
    if unruled:
        verdict = f"STOP for the parent: rungs meeting at one scale only that no ruling put off the grid: {unruled}"
    elif sep1 and sep2:
        verdict = "BOTH operators separate at both scales: part 2 is validated against these verdicts and hashed"
    elif sep1 or sep2:
        verdict = ("ONE operator separates (" + ("operator 1" if sep1 else "operator 2") +
                   "): STOP for the parent (the brief: an operator that does not separate at both scales stops G0)")
    else:
        verdict = "NEITHER operator separates: the wave closes at G0 with the finding (stop)"
    return dict(rungs=rungs, operators=ops, ladders=ladders, oneScale=oneScale, flat=flat, outcome=verdict)


def against_expected(v: dict, expected: dict) -> list[str]:
    """Each difference between the reading and the charter's expectation, stated."""
    out = []
    got = {"operator 1": v["operators"]["operator 1"]["rungs"], "operator 2": v["operators"]["operator 2"]["rungs"],
           "body width": v["operators"]["operator 2"]["bodyRungs"]}
    for name, rungs in got.items():
        want = expected[name]["meetsBoth"]
        if sorted(rungs) != sorted(want):
            out.append(f"{name}: meets at both scales {sorted(rungs)}; the charter expected {sorted(want)}")
    j, wj = v["operators"]["joint"], expected["joint"]
    if j["partitionHolds"] != wj["partitionHolds"]:
        out.append(f"joint: partition holds {j['partitionHolds']}; expected {wj['partitionHolds']}")
    if j["halvingHolds"] != wj["halvingHolds"]:
        out.append(f"joint: halving holds {j['halvingHolds']}; expected {wj['halvingHolds']}")
    below = not all(j["photoAtOrAbovePointA"].values())
    if below != wj["photoBelowPointA"]:
        out.append(f"joint: photo below point A {below}; expected {wj['photoBelowPointA']}")
    return out


# ---------------------------------------------------------------------------------------------------
def pinned_inputs() -> tuple[dict, dict, dict, dict, dict]:
    """(protocol, reread, results, part-1 record, file hashes), refusing unless part 1 is hashed and pins
    this reader, the protocol, the evidence pins and W47's two readings at the bytes on disk (clause 3:
    derived after part 1's hash by the reader part 1 pins)."""
    sys.path.insert(0, str(EVIDENCE))
    import bindings as W  # noqa: PLC0415
    digest = W.require_part(1)
    part1 = json.loads(W.PART1.read_text())
    protocol_path = W.LADDER_PROTOCOL
    protocol = json.loads(protocol_path.read_text())
    ev = protocol["evidence"]
    files = {"reader": Path(__file__).resolve(), "protocol": protocol_path, "evidence": W.ROOT / ev["pins"]["path"],
             "results": W.ROOT / ev["results"]["path"], "reread": W.ROOT / ev["reread"]["path"],
             "rungs": W.ROOT / ev["rungs"]["path"]}
    hashes = {k: sha(p.read_bytes()) for k, p in files.items()}
    for k, p in files.items():
        rel = str(p.relative_to(W.ROOT))
        if part1["sources"].get(rel) != hashes[k]:
            raise Refusal(f"part 1 ({digest[:12]}) does not pin {rel} at its bytes on disk; the verdicts are read "
                          "only by the reader part 1 pins, from the evidence part 1 pins")
    for k in ("results", "reread", "rungs"):
        if ev[k]["sha256"] != hashes[k]:
            raise Refusal(f"protocol.json's {k} pin is not the file on disk")
    pins = json.loads(files["evidence"].read_text())["w47"]
    for k in ("results", "reread"):
        if pins.get(ev[k]["path"]) != hashes[k]:
            raise Refusal(f"ladders/evidence.json does not pin {ev[k]['path']} at its bytes")
    reread = json.loads(files["reread"].read_text())
    results = json.loads(files["results"].read_text())
    if reread["resultsSha256"] != hashes["results"] or reread["protocolSha256"] != hashes["rungs"] \
            or results["protocolSha256"] != hashes["rungs"]:
        raise Refusal("reread.json and results.json do not name each other and W47's protocol")
    if results["control"]["verdict"] != "IDENTICAL" or results["control"]["identical"] != results["control"]["cells"]:
        raise Refusal("W47's control was not read IDENTICAL; no verdict is read")
    return protocol, reread, results, dict(sha256=digest), hashes


def main() -> int:
    protocol, reread, results, part1, hashes = pinned_inputs()
    v = read(protocol, reread, results)
    diffs = against_expected(v, protocol["expected"])
    out = dict(schema="w48-verdicts-1",
               what="W48 G0 (d): the verdicts under Decision Log 3's bars, read by key from W47's re-read and results "
                    "(X71), after part 1's hash; no pixel read, no render",
               declarationSha256=part1["sha256"], inputs=hashes, bars=protocol["bars"],
               **v, againstCharter=dict(differences=diffs, asPredicted=not diffs))
    (HERE / "verdicts.json").write_text(json.dumps(out, indent=1) + "\n")
    (HERE / "verdicts.txt").write_text(report(out))
    print(report(out))
    return 0


def f(x, spec="+.2f"):
    return "-" if x is None else format(x, spec)


def report(r: dict) -> str:
    L = [f"W48 G0 (d): the verdicts (part 1 {r['declarationSha256'][:12]}; reader {r['inputs']['reader'][:12]}; "
         f"reread {r['inputs']['reread'][:12]}; results {r['inputs']['results'][:12]})", "",
         "(a) operator 1, per rung and scale: each thick cell's change-band growth in B, its state (O/U = over/under "
         "Apple at the reference); away beyond B / beyond 3B / over-Apple away; thin gain; L1"]
    for lab, e in r["rungs"].items():
        if e["ladder"] != "i":
            continue
        for s in SCALES:
            p = e["perScale"][s]
            cells = " | ".join(f"{'O' if p['overApple'][sid] else 'U'}{p['changeGrowthInB'][sid]:+.2f} "
                               f"{p['changeState'][sid][:3]}" for sid in p["changeState"])
            pt = p["partition"]
            L.append(f"  {lab:<18} {s}x  {cells}  -> >B {len(pt['awayBeyondB'])}, >3B {len(pt['awayBeyondCeiling'])}, "
                     f"over-away {len(pt['overAppleNotAdmitted'])}; thin {p['thinGain']:.4f}/{p['pointAThinGain']:.4f} "
                     f"{'keeps' if p['thinKeepsHalf'] else 'LOSES'}; L1 {'ok' if p['L1passes'] else 'FAILS'}  "
                     f"{'MEETS' if p['meets'] else 'no'}")
    L += ["", "(b) operator 2, per rung and scale: R on T1-fine per fine cell (bar >= 0.5), the whole-band fall -g/B "
          "beside; guards' whole-band delta in B (floor -1)"]
    for lab, e in r["rungs"].items():
        if e["ladder"] != "iii":
            continue
        for s in SCALES:
            p = e["perScale"][s]
            fine = " | ".join(f"R {f(c['R'], '.3f')} whole {f(c.get('wholeFallInB'))}B" for c in p["fine"]["cells"].values())
            g = " / ".join(f(x) for x in p["guards"]["deltaInB"].values())
            L.append(f"  {lab:<10} {s}x  {fine}  guards {g}  {'MEETS' if p['meets'] else 'no'}")
    for lab, e in r["rungs"].items():
        if e["ladder"] != "iv":
            continue
        j = e["joint"]
        L += ["", f"(c) the joint ({lab}): partition {'holds' if j['partition']['holds'] else 'FAILS'} "
                  f"(>B {j['partition']['awayBeyondB']}, >3B {j['partition']['awayBeyondCeiling']}, over-away "
                  f"{j['partition']['overAppleNotAdmitted']}); halving "
                  + ", ".join(f"{s}x {'holds' if j['halving'][s]['holds'] else 'FAILS'} (R "
                              + " / ".join(f(c['R'], '.3f') for c in j['halving'][s]['cells'].values()) + ")" for s in SCALES)
                  + "; photo " + ", ".join(f"{s}x x{j['photo'][s]['ratio']:.4f} vs point A x{j['photo'][s]['pointA']:.4f} "
                                           f"({j['photo'][s]['deltaFromPointAInBars']:+.2f} bar)" for s in SCALES)
                  + f"  {'MEETS' if j['holds'] else 'no'} (decides name-target only)"]
    o = r["operators"]
    L += ["", f"operator 1: separates {o['operator 1']['separates']} at {o['operator 1']['rungs']}; one scale only "
              f"{o['operator 1']['oneScaleOnly']}",
          f"operator 2: the tap separates {o['operator 2']['separates']} at {o['operator 2']['rungs']}; the body width "
          f"meets {o['operator 2']['bodyWidthMeets']} at {o['operator 2']['bodyRungs']}; members {o['operator 2']['members']}; "
          f"one scale only {o['operator 2']['oneScaleOnly'] + o['operator 2']['bodyOneScaleOnly']}",
          f"ladder (ii) (not re-read): meets {o['2x width']['meets']}",
          f"one scale only: {r['oneScale']['rungs']} (ruled off the grid {r['oneScale']['ruledOffGrid']}; unruled "
          f"{r['oneScale']['unruled']})",
          "", "against the charter: " + ("as predicted" if r["againstCharter"]["asPredicted"] else
                                          "DIFFERS: " + "; ".join(r["againstCharter"]["differences"])),
          f"OUTCOME: {r['outcome']}"]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
