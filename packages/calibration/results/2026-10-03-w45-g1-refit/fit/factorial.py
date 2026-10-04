#!/usr/bin/env python3.12
"""W45 G1, the continuation the parent ruled on 2026-10-04 (claims §5.206 §11): stage 1 as the
permitted full factorial of part 2's `deep` family, on its declared grids, from both starting
points; then stage 2 re-run from each path's new stage-1 point, the joint re-read and the
selection, all with part 2 `e6874e02…` unchanged.

    python3.12 -B factorial.py plan                  the points, checked against part 2; renders nothing
    python3.12 -B factorial.py stage1 c05|joint      render, read, decide (path/factorial/<lineage>/stage1-factorial.json)
    python3.12 -B factorial.py thick c05|joint       the tied thick/far pass from the factorial's decision,
                                                     and the stage-1 record (path/factorial/<lineage>/stage1.json)
    python3.12 -B factorial.py full LABEL ...        the rest of the fit map on each label's measuring twin
    python3.12 -B factorial.py stage2 c05|joint      search.stage("stage2") from the new stage-1 point,
                                                     written under path/factorial/ (search_g1's label mark)
    python3.12 -B factorial.py joint                 joint.py and finding.py on path/factorial/

**Part 2 as hashed permits it.** Stage 1 is one move with one family (`deep`) whose six searched
leaves and one fixed leaf are listed with their grids, and `searchProcedure` says "a full factorial
sweep of a stage's grids is permitted and is not required". The ruled sub-grid of that factorial
visits only declared grid values, and every point is checked by the fit driver's own
`check_overrides` (each leaf's domain and the operator's joint domain [−share, 0]) and against
each leaf's declared grid before anything is built.

**The operator's grid is ABSOLUTE.** Part 2 declares `sizeHeavySecondShareFar2x` on
{0, −0.25, −0.5, −0.75, −1} with `domainLowerIsMinus` and no `domainRelativeTo`. So the ruling's
"delta ∈ {−0.5, −0.75, −1}·share" is taken as the declared grid values whose fraction of the share
lies in [−1, −0.5]. That gives share 0.25 → {−0.25}; 0.5 → {−0.25, −0.5}; 0.75 → {−0.5, −0.75}.
The joint point's ruled {−0.25, −0.5, −0.75, −1}·0.5 gives {−0.25, −0.5}. Off-grid products
(−0.125, −0.1875, −0.375, −0.5625) are not visited: "no new grid value".

**What each path holds.** The leaves the ruling does not sweep stay at the path's current
values: the thick/far starts at c05's 0.21 (both paths' landed stage-1 points carry it); the
joint path's floor at its own 1; the fixed 1x width at 0. The thick/far pass afterwards is the
procedure's second pass (at most two), a coordinate step from the factorial's decision.

**The decision** is part 2's `selectionRule.withinAStage` through the pinned `search.decide`,
over the points this stage-1 search produced (the factorial and its thick/far pass). The
coordinate run's records under `path/<lineage>/` stay as they are.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import search_g1  # noqa: E402,F401  (patches search.label_of: the `rc` receded mark)
import search  # noqa: E402
import fit  # noqa: E402

OUT = HERE / "path" / "factorial"
FLOOR, TOP, SHARE, WIDTH, DELTA = ("sizeScatterFloor2x", "sizeScatterSpanMax2x", "sizeHeavySecondShare",
                                   "sizeHeavySecondSigma2x", "sizeHeavySecondShareFar2x")
RULED = {
    "c05": dict(floor=(0.5, 1.0), share=(0.25, 0.5, 0.75), width=(2, 3), fractions=(-0.5, -1.0), top=(128, 160, 192)),
    "joint": dict(floor=(None,), share=(0.5,), width=(2, 3, 5), fractions=(-0.25, -1.0), top=(128, 160, 192)),
}
BASE = {"c05": "start-c05", "joint": "start-joint"}


def deep() -> dict:
    return search.move_of("stage1")["families"]["deep"]


def grid(leaf: str) -> list:
    return deep()["leaves"][leaf]["grid"]


def deltas(share: float, a: float, b: float) -> list:
    """The declared grid values in [−share, 0] whose fraction of the share lies between a and b."""
    lo, hi = min(a, b), max(a, b)
    return [d for d in grid(DELTA) if d != 0 and d >= -share and lo - 1e-9 <= d / share <= hi + 1e-9]


def points(start: str) -> list[dict]:
    r = RULED[start]
    base = search.merged(search.base_overrides(BASE[start]), search.fixed_of(deep()))
    out = []
    for floor, share, width, top in itertools.product(r["floor"], r["share"], r["width"], r["top"]):
        for d in deltas(share, *r["fractions"]):
            leaves = {SHARE: share, WIDTH: width, DELTA: d, TOP: top}
            if floor is not None:
                leaves[FLOOR] = floor
            out.append(search.with_leaf(base, "active.light", leaves))
    for ov in out:
        for leaf, value in ov["active.light"].items():
            spec = deep()["leaves"].get(leaf)
            if spec is not None and value not in spec["grid"] and not any(
                    value in deep()["leaves"][k]["grid"] for k in deep()["leaves"] if leaf in k.split("+")):
                raise fit.W.Refusal(f"{leaf}={value} is not on part 2's declared grid {spec['grid']}")
        fit.check_overrides(ov)
    return out


def labels(start: str, cands: list[dict]) -> list[str]:
    base = search.merged(search.base_overrides(BASE[start]), search.fixed_of(deep()))
    return [search.label_of(start, "stage1", ov, base) for ov in cands]


def plan() -> dict:
    out = {}
    for start in RULED:
        cands = points(start)
        out[start] = dict(points=len(cands), labels=labels(start, cands),
                          deltaPerShare={str(s): deltas(s, *RULED[start]["fractions"]) for s in RULED[start]["share"]})
    return out


def run_points(start: str, cands: list[dict], family: str) -> list[str]:
    return search.Runner().points(cands, labels(start, cands), "stage1", family, start, "stage1")


def table(start: str, names: list[str]) -> list[dict]:
    rows = []
    for label in dict.fromkeys(names):
        measured = fit.measured_label(label)
        reading = search.summary_of(measured)["stages"]["stage1"]
        rows.append(dict(label=label, measuredBy=measured, objective=search.scope_objective(label, "stage1"),
                         within=reading["within"], notWithin=reading["notWithin"],
                         overrides=search.base_overrides(label)["active.light"]))
    return sorted(rows, key=lambda r: r["objective"])


def stage1(start: str) -> int:
    cands = points(start)
    names = run_points(start, cands, "factorial")
    decision = search.decide(search.move_of("stage1"), start, names)
    (OUT / start).mkdir(parents=True, exist_ok=True)
    record = dict(what="W45 G1 continuation: stage 1's permitted factorial (the parent's ruling, 2026-10-04)",
                  start=start, ruled=RULED[start], points=table(start, names), decision=decision)
    (OUT / start / "stage1-factorial.json").write_text(json.dumps(record, indent=1) + "\n")
    print(start, "factorial", len(names), "points; landed", decision["landed"], decision["within"])
    return 0


def thick(start: str) -> int:
    fac = json.loads((OUT / start / "stage1-factorial.json").read_text())
    landed = fac["decision"]["landed"]
    current = search.base_overrides(landed)
    key = "sizeScatterRampStartThick2x+sizeScatterRampStartFar2x"
    cands = search.sweep_candidates(deep(), key, current)
    names = run_points(start, cands, "deep")
    move = search.move_of("stage1")
    every = [p["label"] for p in fac["points"]] + names
    decision = search.decide(move, start, every)
    best = min(names, key=lambda n: search.scope_objective(n, "stage1"))
    base = search.base_overrides(BASE[start])
    record = dict(decision, base=BASE[start], components=[
        dict(family="deep", scope="stage1", **{"from": base}, best=fac["decision"]["landed"],
             bestOverrides=search.base_overrides(fac["decision"]["landed"]), points=[p["label"] for p in fac["points"]],
             procedure="the permitted full factorial over the ruled sub-grid (pass 1)"),
        dict(family="deep", scope="stage1", **{"from": current}, best=best, bestOverrides=search.base_overrides(best),
             points=names, procedure="the tied thick/far starts swept from the factorial's decision (pass 2)")],
        composed=search.base_overrides(decision["landed"]))
    (OUT / start / "stage1.json").write_text(json.dumps(record, indent=1) + "\n")
    print(start, "stage 1 landed", decision["landed"], decision["within"])
    return 0


def full(names: list[str]) -> int:
    for label in names:
        twin = fit.measured_label(label)
        code = fit.render(twin, "rest-of-fit")
        if code not in (0, 1):
            raise fit.W.Refusal(f"{twin}: rest-of-fit exit {code}")
        fit.read(twin)
    return 0


def stage2(start: str) -> int:
    """Stage 2 from the new stage-1 point. Its labels are relative to that base, so the coordinate
    run's stage-2 labels (`c-s2-t0.46`, …) would name other overrides here and the driver refuses
    them; the continuation's stage-2 points are marked `s2x` (a label only, as `search_g1`'s)."""
    base = json.loads((OUT / start / "stage1.json").read_text())["landed"]
    # The stage records go under path/factorial/; the recovered objectives stay where the pinned
    # recover.py writes them (path/recovered.json). Redirecting PATH alone also redirected that
    # lookup, so a partial stage-2 render could not have resumed (the review of the continuation,
    # P2; no stage-2 render of the continuation was partial, so nothing recorded depended on it).
    recovered = search.recovered_points()
    search.recovered_points = lambda: (lambda path: json.loads(path.read_text())["points"] if path.exists() else {})(
        fit.G1 / "path" / "recovered.json")
    assert search.recovered_points() == recovered
    search.PATH = OUT
    search.STAGE_SHORT = dict(search.STAGE_SHORT, stage2="s2x")
    record = search.stage("stage2", start, base)
    print(start, "stage 2 landed", record["landed"], record["within"])
    return 0


def joint() -> int:
    import finding
    import joint as J
    J.PATH = OUT
    finding.PATH = OUT
    J.main(["joint.py"])
    return 0


def report() -> int:
    """The continuation's numbers for the ledger and the gate report: each path's factorial ten best
    by stage-1 objective with the landing rule on its full fit map (cut by W45's cuts, never
    re-derived), the final points' T cells and their moved leaves per document against c05."""
    import gzip
    lines, out = [], {}
    c05 = {s: json.loads((fit.CAL / "profiles" / f"apple-macos-27.0-1x-light-standard-glass0.25{x}.json").read_text())["patch"]
           for s, x in (("active.light", ""), ("receded.light", "-receded"))}
    for start in RULED:
        fac = json.loads((OUT / start / "stage1-factorial.json").read_text())
        rows = []
        lines.append(f"== {start}: the factorial's ten best by stage-1 objective, the landing rule on each full fit map")
        for p in fac["points"][:10]:
            m = fit.measured_label(p["label"])
            r = json.loads(gzip.open(fit.G1 / "candidates" / m / "cuts.json.gz").read())["T1"]["rule"]
            row = dict(label=p["label"], objective=p["objective"], verdict=r["verdict"], read=r["read"],
                       fAggregate=r["fAggregate"], awayBeyondB=len(r["awayBeyondB"]),
                       beyondCeiling=len(r["awayBeyondCeiling"]), gatedOver=r["gatedAggregateFailures"])
            rows.append(row)
            lines.append(f"  {p['label']:<40} {p['objective']:.4f}  {r['verdict'][:7]:<7} read {r['read']}/94 "
                         f"F {r['fAggregate']:.4f}  away>B {len(r['awayBeyondB']):>2}  >3B {len(r['awayBeyondCeiling']):>2}  "
                         f"gated over {r['gatedAggregateFailures'] or 'none'}")
        out[start] = dict(best10=rows)
    j = json.loads((OUT / "joint.json").read_text())
    for start, p in j["paths"].items():
        spec = json.loads((fit.G1 / "specs" / f"{p['joint']}.json").read_text())["overrides"]
        moves = {slot: {k: [c05[slot].get(k), v] for k, v in leaves.items() if c05[slot].get(k) != v}
                 for slot, leaves in spec.items()}
        summ = json.loads((fit.G1 / "candidates" / fit.measured_label(p["joint"]) / "summary.json").read_text())
        tcells = {sid: {b: {k: c["bands"][b][k] for k in ("native", "reference", "candidate", "fidelity", "change",
                                                         "growth", "B")} for b in ("fine", "low")}
                  for sid, c in summ["cells"].items() if c["stratum"] == "T"}
        out[start].update(final=p["joint"], movedFromC05=moves, tCells=tcells)
        lines.append(f"== {start} final {p['joint']}: moved from c05 (from, to)")
        for slot, mv in moves.items():
            lines.append(f"  {slot}: " + "; ".join(f"{k} {a} -> {b}" for k, (a, b) in sorted(mv.items())))
        for sid, b in sorted(tcells.items()):
            f, lo = b["fine"], b["low"]
            lines.append(f"  {sid:<28} fine n {f['native']:.4f} c05 {f['reference']:.4f} k {f['candidate']:.4f} "
                         f"{f['fidelity']}; low n {lo['native']:.4f} c05 {lo['reference']:.4f} k {lo['candidate']:.4f} "
                         f"g {lo['growth'] / lo['B']:+.2f} B")
    (OUT / "report.json").write_text(json.dumps(out, indent=1) + "\n")
    (OUT / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


def main(argv) -> int:
    fit.preflight()
    verb = argv[1] if len(argv) > 1 else ""
    if verb == "plan":
        p = plan()
        print(json.dumps({k: dict(points=v["points"], deltaPerShare=v["deltaPerShare"]) for k, v in p.items()}))
        (OUT / "plan.json").parent.mkdir(parents=True, exist_ok=True)
        (OUT / "plan.json").write_text(json.dumps(p, indent=1) + "\n")
        return 0
    if verb == "stage1":
        return stage1(argv[2])
    if verb == "thick":
        return thick(argv[2])
    if verb == "full":
        return full(argv[2:])
    if verb == "stage2":
        return stage2(argv[2])
    if verb == "joint":
        return joint()
    if verb == "report":
        return report()
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
