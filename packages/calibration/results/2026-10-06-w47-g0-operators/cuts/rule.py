"""W47 G0 (c), (d): W46's binding of W45's landing rule (`results/2026-10-05-w46-g0-declaration/cuts/rule.py`),
ported by copy for W47 (charter Design "The landing rule", MARKED: "W46's Design 'The landing rule'
applies verbatim"; Decision Logs 1 and 4). W46's committed copy is untouched.

W47 changes no clause, constant or target: the reference `d0219cd684bf`, `B = max(1 code, 2·bar)` at
bar 0.5, the dark WebGPU scope per profile, the gated and reported groups per scale (F rest 10, C rest
28, C inactive 14, P rest 4, P inactive 5, T rest 3 gated; F inactive reported with two gate cells;
T inactive none), the budget of three cells away beyond B and none past 3B per profile, and W46's
three targets — P (both poses, pooled into one aggregate as W46's port read "P both poses"), C rest
and F inactive — each halved per profile (Decision Log 4: "W46's three targets ... each halved per
profile"). The stage clauses are W46's (stage 1 the rest cells, stage 2 the inactive cells).

W46 G0's text follows, unchanged; where it says W46 it is W47.

W46 G0 (c): W45's landing rule (`results/2026-10-03-w45-g0-operator/cuts/rule.py`, charter Decision
Log 3 there), ported and bound to the dark 0.25 profiles (W46 charter Design "The landing rule",
MARKED; Decision Log 3). W45's committed copy is untouched.

**What is unchanged** (Decision Log 3: "W45's growth-only rule unchanged"): the per-cell arithmetic
(`t1.classify`, shared by path from W44 G1 and pinned), the growth-only partition `unchanged` /
`toward` / `away` with no crossing state, the band per stratum (F, C, P on T1; T on T1-fine, its
`away` on T1-low), the aggregate `A = median |log((k + ε)/(n + ε))|` per stratum × pose with ε the
cell's own code and its tolerance `τ = median log(1 + bar/(n + ε))`, a group GATED at three or more
GATE cells (the exposure's referee and holdout members enter the aggregate and never the count), and
the budget's constants: at most `BUDGET_COUNT` cells `away` with `g > B`, none with
`g > BUDGET_CEILING_B · B`. `B = max(1 code, 2·bar)` with the bar 0.5 code (W44 G0's measurement,
77 cells per dark scale).

**What W46 binds** (Design "The landing rule"):
  - **The reference** is `d0219cd684bf` (the cut's `reference` column on every cell).
  - **The scope** is the WebGPU tier of the two DARK 0.25 profiles, F ∪ T ∪ C ∪ P, in the
    partitions the read admits (the gate before the exposure; the referees and holdout added at it).
  - **Per profile.** The budget is "over the whole gated population per profile" (Decision Log 3),
    and the gated groups are counted per scale (F rest 10, T rest 3, C rest 28, C inactive 14,
    P rest 4, P inactive 5 gated; F inactive 2 reported; T inactive none at the gate). So every
    clause is evaluated per profile, and the wave's verdict is the weaker of the two profiles'.
  - **Three targets** replace W45's single F stratum (Decision Log 4): P (both poses pooled),
    C rest and F inactive, each an aggregate of its own over its cells with the same arithmetic.
    FULL CLOSE needs every target cell within; the IMPROVEMENT LANDING needs each target's
    aggregate at most half of the reference's. Both need every gated group's `A ≤ A_ref + τ` and
    the budget. The targets pooled over both scales are reported beside, and decide nothing.
  - **The stages' objectives** (Design "The moves"): W44's selection metric (median
    |log(web/native)| over F ∪ C ∪ P, `t1.selection_metric`'s arithmetic on W46's scope, both
    scales pooled) on a stage's cells; stage 1 the rest cells, stage 2 the inactive cells. Its tie
    is the same median of `log(1 + bar/native)` over the stage's DECLARED cells (the cell set is
    stated, never what a point happened to render: the W44 tracker note). The stage's within clause
    is its target cells within: stage 1 P rest and C rest, stage 2 P inactive and F inactive.

The referees' clause (within, or an unchanged miss, at the exposure), "every other adopted row" and
the exposure's holdout-miss ruling are outside this evaluation and reported as such.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict

import t1

BUDGET_COUNT = 3
BUDGET_CEILING_B = 3.0
GATING_MIN_CELLS = 3
STRATA = ("F", "T", "C", "P")
POSES = ("rest", "inactive")
SCOPE_PROFILES = ("apple-macos-27.0-1x-dark-standard-glass0.25", "apple-macos-27.0-2x-dark-standard-glass0.25")
SCOPE_TIER = "webgpu"
REFERENCE = "d0219cd684bf"
TARGETS = {"P": (("P", "rest"), ("P", "inactive")),
           "C rest": (("C", "rest"),),
           "F inactive": (("F", "inactive"),)}
SELECTION_STRATA = ("F", "C", "P")
# The stages' cells and within clauses (Design "The moves"): stage 1 the active document's, read on
# the rest cells; stage 2 the receded document's, read on the inactive cells.
STAGES = {"stage1": dict(pose="rest", within=(("P", "rest"), ("C", "rest"))),
          "stage2": dict(pose="inactive", within=(("P", "inactive"), ("F", "inactive")))}


def growth_change(n: float, c: float, k: float, bar: float) -> str:
    """X54's partition: `unchanged`, `toward` or `away`, by error growth alone."""
    if abs(k - c) <= bar:
        return "unchanged"
    return "toward" if abs(k - n) - abs(c - n) <= t1.EQUAL else "away"


def in_scope(cell: dict, partitions=("gate",), profile: str | None = None) -> bool:
    return (cell["tier"] == SCOPE_TIER and cell["profile"] in SCOPE_PROFILES
            and (profile is None or cell["profile"] == profile)
            and cell["partition"] in partitions)


def reads(cell: dict) -> dict | None:
    """What the rule reads of one cell: its change band (fidelity, change, aggregate) and its away
    band. None for a T cell with no band reading."""
    def band(n, c, k):
        out = t1.classify(n, c, k, cell["bar"], cell["code"])
        return dict(n=n, c=c, k=k, bar=cell["bar"], code=cell["code"], B=out["B"],
                    fidelity=out["fidelity"], growth=out["growth"], displacement=out["displacement"],
                    change=growth_change(n, c, k, cell["bar"]))
    if cell["stratum"] != "T":
        whole = band(cell["native"], cell["reference"], cell["candidate"])
        return dict(change=whole, away=whole)
    if "bands" not in cell:
        return None
    fine, low = cell["bands"]["fine"], cell["bands"]["low"]
    return dict(change=band(fine["native"], fine["reference"], fine["candidate"]),
                away=band(low["native"], low["reference"], low["candidate"]))


def log_error(x: float, n: float, eps: float) -> float:
    return abs(math.log((x + eps) / (n + eps)))


def group_aggregate(reads_of: list[dict], gate_cells: int) -> dict:
    a = statistics.median(log_error(r["k"], r["n"], r["code"]) for r in reads_of)
    a_ref = statistics.median(log_error(r["c"], r["n"], r["code"]) for r in reads_of)
    tau = statistics.median(math.log(1 + r["bar"] / (r["n"] + r["code"])) for r in reads_of)
    return dict(cells=len(reads_of), gateCells=gate_cells, A=a, referenceA=a_ref, tau=tau,
                gated=gate_cells >= GATING_MIN_CELLS, holds=a <= a_ref + tau)


def target_aggregate(reads_of: list[dict]) -> dict | None:
    if not reads_of:
        return None
    a = statistics.median(log_error(r["k"], r["n"], r["code"]) for r in reads_of)
    a_ref = statistics.median(log_error(r["c"], r["n"], r["code"]) for r in reads_of)
    return dict(cells=len(reads_of), A=a, referenceA=a_ref, halved=a <= 0.5 * a_ref)


def is_target(c: dict) -> str | None:
    return next((t for t, groups in TARGETS.items() if (c["stratum"], c["pose"]) in groups), None)


def evaluate_profile(cells: list, missing, partitions, profile: str) -> dict:
    scope = [c for c in cells if in_scope(c, partitions, profile)]
    absent = [f"{m['scene']} ({m['reason']})" for m in missing if in_scope(m, partitions, profile)]
    absent += [f"{c['scene']} (no band reading)" for c in scope if c["stratum"] == "T" and "bands" not in c]
    got = {id(c): reads(c) for c in scope}
    read = [c for c in scope if got[id(c)] is not None]

    partition = {s: defaultdict(int) for s in ("unchanged", "toward", "away")}
    per_cell = []
    for c in read:
        r = got[id(c)]
        partition[r["change"]["change"]][c["stratum"]] += 1
        a = r["away"]
        per_cell.append(dict(
            scene=c["scene"], stratum=c["stratum"], pose=c["pose"], partition=c["partition"],
            target=is_target(c), fidelity=r["change"]["fidelity"], change=r["change"]["change"],
            native=r["change"]["n"], reference=r["change"]["c"], candidate=r["change"]["k"],
            growthInB=r["change"]["growth"] / r["change"]["B"],
            awayChange=a["change"], awayGrowthInB=a["growth"] / a["B"],
            band="T1" if c["stratum"] != "T" else "T1-fine (away on T1-low)"))

    groups = {}
    for s in STRATA:
        for p in POSES:
            cells_of = [c for c in read if c["stratum"] == s and c["pose"] == p]
            if cells_of:
                groups[f"{s} {p}"] = group_aggregate([got[id(c)]["change"] for c in cells_of],
                                                     sum(1 for c in cells_of if c["partition"] == "gate"))
    gated_fail = [k for k, g in groups.items() if g["gated"] and not g["holds"]]
    reported_over = [k for k, g in groups.items() if not g["gated"] and not g["holds"]]

    over_b = sorted(((c["scene"], got[id(c)]["away"]["growth"] / got[id(c)]["away"]["B"]) for c in read
                     if got[id(c)]["away"]["change"] == "away"
                     and got[id(c)]["away"]["growth"] > got[id(c)]["away"]["B"]), key=lambda x: -x[1])
    over_ceiling = [x for x in over_b if x[1] > BUDGET_CEILING_B]
    budget = len(over_b) <= BUDGET_COUNT and not over_ceiling

    targets = {t: target_aggregate([got[id(c)]["change"] for c in read if is_target(c) == t]) for t in TARGETS}
    target_not_within = {t: [c["scene"] for c in read if is_target(c) == t
                             and got[id(c)]["change"]["fidelity"] != "within"] for t in TARGETS}
    every_target = all(targets[t] is not None for t in TARGETS)
    aggregates_hold = not gated_fail
    full = every_target and not any(target_not_within.values()) and aggregates_hold and budget
    improvement = every_target and all(targets[t]["halved"] for t in TARGETS) and aggregates_hold and budget
    if absent:
        verdict = f"UNMEASURED: {len(absent)} member(s) of the scope have no reading"
    elif full:
        verdict = "FULL CLOSE"
    elif improvement:
        verdict = "IMPROVEMENT LANDING"
    else:
        verdict = "NEITHER: closes at the finding"
    why = []
    if not absent and not full:
        for t in TARGETS:
            if not every_target:
                why.append("a target has no cell in the scope")
                break
            if target_not_within[t]:
                why.append(f"full close: target {t}: {len(target_not_within[t])} cell(s) not within")
            if not targets[t]["halved"]:
                why.append(f"improvement: target {t} aggregate {targets[t]['A']:.4f} above half of the "
                           f"reference's {targets[t]['referenceA']:.4f}")
        if gated_fail:
            why.append("aggregate: " + ", ".join(
                f"{k} A {groups[k]['A']:.4f} > {groups[k]['referenceA']:.4f} + τ {groups[k]['tau']:.4f}"
                for k in gated_fail))
        if len(over_b) > BUDGET_COUNT:
            why.append(f"budget count: {len(over_b)} cells away beyond B (at most {BUDGET_COUNT})")
        if over_ceiling:
            why.append(f"budget ceiling: {len(over_ceiling)} cell(s) beyond {BUDGET_CEILING_B:g} B")
    return dict(
        profile=profile, cells=len(scope), read=len(read), unmeasured=absent,
        partition={k: dict(v, total=sum(v.values())) for k, v in partition.items()},
        groups=groups, gatedAggregateFailures=gated_fail, reportedAggregateOver=reported_over,
        targets=targets, targetNotWithin=target_not_within,
        awayBeyondB=[dict(scene=s, growthInB=g) for s, g in over_b],
        awayBeyondCeiling=[dict(scene=s, growthInB=g) for s, g in over_ceiling],
        budgetHolds=budget, fullClose=full and not absent, improvement=improvement and not absent,
        verdict=verdict, why=why, perCell=per_cell)


ORDER = ("UNMEASURED", "NEITHER", "IMPROVEMENT LANDING", "FULL CLOSE")


def rank(verdict: str) -> int:
    return next(i for i, v in enumerate(ORDER) if verdict.startswith(v))


def evaluate(cells: list, missing=(), partitions=("gate",)) -> dict:
    """The landing rule on `cells` (`t1.cut`'s, with the reference d0219cd684bf), per dark profile,
    in the scope `partitions` admits; the verdict is the weaker profile's."""
    per = {p: evaluate_profile(cells, missing, partitions, p) for p in SCOPE_PROFILES}
    weakest = min(per.values(), key=lambda r: rank(r["verdict"]))
    if weakest["verdict"].startswith("UNMEASURED"):
        verdict = "UNMEASURED: " + "; ".join(f"{p.split('-')[3]} {r['verdict']}" for p, r in per.items()
                                            if r["verdict"].startswith("UNMEASURED"))
    else:
        verdict = weakest["verdict"]
    pooled = {}
    scope = [c for c in cells if in_scope(c, partitions)]
    for t in TARGETS:
        rs = [reads(c)["change"] for c in scope if is_target(c) == t and reads(c) is not None]
        pooled[t] = target_aggregate(rs)
    return dict(
        scope=f"{SCOPE_TIER}, the dark 0.25 profiles {', '.join(SCOPE_PROFILES)}, each evaluated alone, "
              f"both poses, F ∪ T ∪ C ∪ P, partitions {', '.join(partitions)}; T on T1-fine (away on T1-low); "
              f"reference {REFERENCE}",
        constants=dict(budgetCount=BUDGET_COUNT, budgetCeilingB=BUDGET_CEILING_B,
                       gatingMinCells=GATING_MIN_CELLS),
        targets={t: [f"{s} {p}" for s, p in g] for t, g in TARGETS.items()},
        profiles=per, verdict=verdict, pooledTargets=pooled,
        outside="the referees' clause (at the exposure), every other adopted row, and the exposure's "
                "holdout-miss ruling are not evaluated here; the pooled targets decide nothing")


def in_stage(cell: dict, stage: str, partitions=("gate",)) -> bool:
    return in_scope(cell, partitions) and cell["pose"] == STAGES[stage]["pose"]


def selection_metric(cells: list, where=None) -> float | None:
    """`t1.selection_metric`'s arithmetic on W46's (W47's) scope: the median |log(web/native)| over F ∪ C ∪ P,
    gate partition, both dark scales pooled; `where` restricts it."""
    sel = [abs(math.log(c["candidate"] / c["native"])) for c in cells
           if in_scope(c) and c["stratum"] in SELECTION_STRATA and (where is None or where(c))
           and c["candidate"] > 0 and c["native"] > 0]
    return statistics.median(sel) if sel else None


def stage_objective(cells: list, stage: str) -> float | None:
    return selection_metric(cells, where=lambda c: in_stage(c, stage))


def stage_tie(cells: list, stage: str) -> float | None:
    """The tie on the metric's own scale, over the stage's cells. `native` and `bar` are the cell's,
    not the candidate's, so any complete read of the stage gives one value: the search takes it from
    the reference's own cut (`search.stage_tie_of`), never from a point's partial render."""
    sel = [math.log(1 + c["bar"] / c["native"]) for c in cells
           if in_stage(c, stage) and c["stratum"] in SELECTION_STRATA and c["native"] > 0]
    return statistics.median(sel) if sel else None


def stage_within(cells: list, stage: str, missing=()) -> dict:
    """The stage's within clause on T1's fidelity: every TARGET cell of the stage within (stage 1 P
    rest and C rest; stage 2 P inactive and F inactive). A member with no reading makes it UNMEASURED."""
    groups = STAGES[stage]["within"]
    members = [c for c in cells if in_stage(c, stage) and (c["stratum"], c["pose"]) in groups]
    absent = [m for m in missing if in_scope(m) and (m["stratum"], m["pose"]) in groups]
    not_within = [f"{c['scene']} {c['scale']}x" for c in members if c["fidelity"] != "within"]
    return dict(stage=stage, members=len(members), notWithin=not_within,
                unmeasured=[f"{m['scene']} {m['scale']}x" for m in absent],
                verdict="UNMEASURED" if absent or not members else "WITHIN" if not not_within else "NOT WITHIN")
