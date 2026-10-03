"""W45 G0 (c): the landing rule (charter Design "The landing rule", MARKED; Decision Log 3; X54, X55).

It reads the cells W44 G1's `t1.cut` produces (`results/2026-10-03-w44-g1-refit/cuts/t1.py`, shared
by path and pinned: its `classify`, `code_step` and `log_error` are the arithmetic) and decides a
landing. Nothing here renders or reads a row.

**Per cell** as W44: `n` native, `c` c05, `k` candidate, `e(x) = |x − n|`, `g = e(k) − e(c)`,
`B = max(1 code, 2 bar)`, `δ = |k − c|`; fidelity `within` by `B` or 10 % (`t1.classify`'s).

**Change, a partition by error growth alone** (X54): `unchanged` if `δ ≤ bar`; else `toward` if
`g ≤ 0` (read to `t1.EQUAL`, as W44 reads "g = 0"); else `away` with `g`. No crossing state.

**The band per stratum, declared** (W44 Decision Log 7): F, C and P read T1; T reads T1-fine for
fidelity, change and its aggregate, and T1-low for `away` only. Raw T1 on a T cell is recorded and
read by no clause.

**The aggregate per stratum × pose**: `A = median |log((k + ε) / (n + ε))|` over the group on the
group's band, `ε` = the cell's own code; c05's `A` the same median with `c` for `k`; the tolerance
`τ = median log(1 + bar / (n + ε))`. A group with at least `GATING_MIN_CELLS` cells is GATED (its
`A` at most c05's `A + τ`), otherwise REPORTED.

**The budget**, one over the whole population in scope: at most `BUDGET_COUNT` cells `away` with
`g > B` (a T cell's on T1-low), none with `g > BUDGET_CEILING_B · B`, each named. Fixed before the
rehearsal (X55); the rehearsal reports and does not tune them.

**Verdicts** on the scope (WebGPU, 2x light, both poses, F ∪ T ∪ C ∪ P, the partitions the read
admits: the gate before the exposure, the referees and holdout added at it):
  - FULL CLOSE: every F cell within; every gated group's `A ≤ A_c05 + τ`; the budget holds.
  - IMPROVEMENT LANDING: the F aggregate (both poses pooled) at most half of c05's; every gated
    group's `A ≤ A_c05 + τ`; the budget holds; every F cell not within named.
  - UNMEASURED: a member of the scope has no reading (no row, no reading, or a T cell without its
    bands); never a landing.
  - NEITHER otherwise: the wave closes at the finding.
The referees' clause (within, or an unchanged miss, at the exposure), "every other adopted row"
and the exposure's holdout-miss ruling are outside this evaluation and reported as such.
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
SCOPE_PROFILE = "apple-macos-27.0-2x-light-standard-glass0.25"
SCOPE_TIER = "webgpu"

# W45's two stages over the moves' cells (Design "The moves"; Decision Log 4). Stage 1 is the
# span-graded deep composition on the rest mid and thick cells, its within clause every F and
# pitch-16 (`checkerboard`) cell of the stage; stage 2 the thin start and the receded overrides,
# on the rest thin cells and every inactive cell, each part's clause every F, C and P cell within.
STAGES = {
    "stage1": (dict(pose="rest", spans=("mid", "thick")),),
    "stage2": (dict(pose="rest", spans=("thin",)), dict(pose="inactive", spans=None)),
}


def growth_change(n: float, c: float, k: float, bar: float) -> str:
    """X54's partition: `unchanged`, `toward` or `away`, by error growth alone."""
    if abs(k - c) <= bar:
        return "unchanged"
    return "toward" if abs(k - n) - abs(c - n) <= t1.EQUAL else "away"


def in_scope(cell: dict, partitions=("gate",)) -> bool:
    return (cell["tier"] == SCOPE_TIER and cell["profile"] == SCOPE_PROFILE
            and cell["partition"] in partitions)


def reads(cell: dict) -> dict | None:
    """What the rule reads of one cell: its change band (fidelity, change, aggregate) and its away
    band, each as (n, c, k, bar, code, B, fidelity). None for a T cell with no band reading."""
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


def group_aggregate(reads_of: list[dict]) -> dict:
    """A, c05's A and τ over one group's change bands (each with its own ε = code)."""
    a = statistics.median(log_error(r["k"], r["n"], r["code"]) for r in reads_of)
    a_ref = statistics.median(log_error(r["c"], r["n"], r["code"]) for r in reads_of)
    tau = statistics.median(math.log(1 + r["bar"] / (r["n"] + r["code"])) for r in reads_of)
    return dict(cells=len(reads_of), A=a, referenceA=a_ref, tau=tau,
                gated=len(reads_of) >= GATING_MIN_CELLS,
                holds=a <= a_ref + tau)


def evaluate(cells: list, missing=(), partitions=("gate",)) -> dict:
    """The landing rule on `cells` (`t1.cut`'s), in the scope `partitions` admits."""
    scope = [c for c in cells if in_scope(c, partitions)]
    absent = [f"{m['scene']} ({m['reason']})" for m in missing if in_scope(m, partitions)]
    absent += [f"{c['scene']} (no band reading)" for c in scope if c["stratum"] == "T" and "bands" not in c]
    got = {id(c): reads(c) for c in scope}
    read = [c for c in scope if got[id(c)] is not None]
    name = lambda c: c["scene"]  # noqa: E731

    partition = {s: defaultdict(int) for s in ("unchanged", "toward", "away")}
    per_cell = []
    for c in read:
        r = got[id(c)]
        partition[r["change"]["change"]][c["stratum"]] += 1
        a = r["away"]
        per_cell.append(dict(
            scene=c["scene"], stratum=c["stratum"], pose=c["pose"], partition=c["partition"],
            fidelity=r["change"]["fidelity"], change=r["change"]["change"],
            native=r["change"]["n"], reference=r["change"]["c"], candidate=r["change"]["k"],
            growthInB=r["change"]["growth"] / r["change"]["B"],
            awayChange=a["change"], awayGrowthInB=a["growth"] / a["B"],
            band="T1" if c["stratum"] != "T" else "T1-fine (away on T1-low)"))

    groups = {}
    for s in STRATA:
        for p in POSES:
            members = [got[id(c)]["change"] for c in read if c["stratum"] == s and c["pose"] == p]
            if members:
                groups[f"{s} {p}"] = group_aggregate(members)
    gated_fail = [k for k, g in groups.items() if g["gated"] and not g["holds"]]
    reported_over = [k for k, g in groups.items() if not g["gated"] and not g["holds"]]

    away = [(c, got[id(c)]["away"]) for c in read]
    over_b = sorted(((name(c), a["growth"] / a["B"]) for c, a in away
                     if a["change"] == "away" and a["growth"] > a["B"]), key=lambda x: -x[1])
    over_ceiling = [x for x in over_b if x[1] > BUDGET_CEILING_B]
    budget = len(over_b) <= BUDGET_COUNT and not over_ceiling

    f = [got[id(c)]["change"] for c in read if c["stratum"] == "F"]
    f_agg = statistics.median(log_error(r["k"], r["n"], r["code"]) for r in f) if f else None
    f_ref = statistics.median(log_error(r["c"], r["n"], r["code"]) for r in f) if f else None
    f_not_within = [name(c) for c in read if c["stratum"] == "F" and got[id(c)]["change"]["fidelity"] != "within"]

    aggregates_hold = not gated_fail
    full = bool(f) and not f_not_within and aggregates_hold and budget
    improvement = bool(f) and f_agg <= 0.5 * f_ref and aggregates_hold and budget
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
        if f_not_within:
            why.append(f"full close: {len(f_not_within)} F cell(s) not within")
        if f and f_agg > 0.5 * f_ref:
            why.append(f"improvement: F aggregate {f_agg:.4f} above half of c05's {f_ref:.4f}")
        if gated_fail:
            why.append("aggregate: " + ", ".join(
                f"{k} A {groups[k]['A']:.4f} > {groups[k]['referenceA']:.4f} + τ {groups[k]['tau']:.4f}"
                for k in gated_fail))
        if len(over_b) > BUDGET_COUNT:
            why.append(f"budget count: {len(over_b)} cells away beyond B (at most {BUDGET_COUNT})")
        if over_ceiling:
            why.append(f"budget ceiling: {len(over_ceiling)} cell(s) beyond {BUDGET_CEILING_B:g} B")
    return dict(
        scope=f"{SCOPE_TIER}, 2x light ({SCOPE_PROFILE}), both poses, F ∪ T ∪ C ∪ P, partitions "
              f"{', '.join(partitions)}; T on T1-fine (away on T1-low)",
        constants=dict(budgetCount=BUDGET_COUNT, budgetCeilingB=BUDGET_CEILING_B,
                       gatingMinCells=GATING_MIN_CELLS),
        cells=len(scope), read=len(read), unmeasured=absent,
        partition={k: dict(v, total=sum(v.values())) for k, v in partition.items()},
        groups=groups, gatedAggregateFailures=gated_fail, reportedAggregateOver=reported_over,
        fAggregate=f_agg, fAggregateReference=f_ref, fHalved=None if f_agg is None else f_agg <= 0.5 * f_ref,
        fNotWithin=f_not_within,
        awayBeyondB=[dict(scene=s, growthInB=g) for s, g in over_b],
        awayBeyondCeiling=[dict(scene=s, growthInB=g) for s, g in over_ceiling],
        budgetHolds=budget, fullClose=full and not absent, improvement=improvement and not absent,
        verdict=verdict, why=why, perCell=per_cell,
        outside="the referees' clause (at the exposure), every other adopted row, and the exposure's "
                "holdout-miss ruling are not evaluated here")


def in_stage(cell: dict, stage: str) -> bool:
    return in_scope(cell) and any(
        cell["pose"] == part["pose"] and (part["spans"] is None or cell["spanClass"] in part["spans"])
        for part in STAGES[stage])


def stage_objective(cells: list, stage: str) -> float | None:
    """W44's selection metric (`t1.selection_metric`: median |log(web / native)| over F ∪ C ∪ P)
    restricted to the stage's cells — the search's objective, read on the move's cells."""
    return t1.selection_metric(cells, where=lambda c: in_stage(c, stage))


def stage_tie(cells: list, stage: str) -> float | None:
    """W44's tie on the metric's own scale, over the stage's cells."""
    sel = [math.log(1 + c["bar"] / c["native"]) for c in cells
           if in_stage(c, stage) and c["stratum"] in t1.SELECTION_STRATA and c["native"] > 0]
    return statistics.median(sel) if sel else None


def stage_within(cells: list, stage: str, missing=()) -> dict:
    """The stage's within clause on T1's fidelity: stage 1 every F and pitch-16 (`checkerboard`)
    cell of the stage; stage 2 every F, C and P cell. A T cell is never required within; a member
    with no reading makes the clause UNMEASURED."""
    def member(c):
        if c["stratum"] not in t1.SELECTION_STRATA:
            return False
        if stage == "stage1":
            return c["stratum"] == "F" or t1.B.SCENES.by_id[c["scene"]]["background"] == "checkerboard"
        return True
    members = [c for c in cells if in_stage(c, stage) and member(c)]
    absent = [m for m in missing if in_scope(m) and member(m) and any(
        m["pose"] == part["pose"] and (part["spans"] is None or t1.span_class(m["scene"]) in part["spans"])
        for part in STAGES[stage])]
    not_within = [c["scene"] for c in members if c["fidelity"] != "within"]
    return dict(stage=stage, members=len(members), notWithin=not_within,
                unmeasured=[m["scene"] for m in absent],
                verdict="UNMEASURED" if absent or not members else "WITHIN" if not not_within else "NOT WITHIN")
