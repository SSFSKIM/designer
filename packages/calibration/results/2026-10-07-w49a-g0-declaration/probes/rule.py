"""W49a: the landing rule (Decision Log 2), the selection rule (Decision Log 4) and the authority report (X74),
as arithmetic over T1 cells (charter `2026-10-07-w49-authorised-list-repair.md`). Hashed in part 2 by file
SHA-256 before any probe render; part 2 admits no amendment after a gate read.

**The per-cell arithmetic is W44 G1's `t1.classify`, imported by path and pinned** (`T1_PATH`): `B = max(code,
2·bar)`, growth `g = |k - n| - |c - n|`, and the change partition `unchanged` / `toward` / `away` / `overshoot`.
A T cell reads its fidelity and change on T1-fine and its away clause on T1-low (W44 G1, W46's `rule.reads`),
every other cell on T1. Nothing here changes T1's statistic, bar or arithmetic (DL1).

**The cells.** Per dark 0.25 profile (one per scale), WebGPU tier. A point's cell carries `native` n, the
`d0219cd684bf` reading (the cut's `reference`) and the point's reading k. Beside it, the cell's `b2d074d2df24`
reading is the W48 exposure cut's `candidate` (read 8; `B2D074_CUT`, pinned). Family R moves only the receded
document, so a rest cell, and any cell a probe does not render, reads `b2d074d2df24` by construction; the
reproduction control below holds the probes to that.

**DL2, per profile** (all binding; a point that fails any clause at either scale is not a landing):
  (a) repair:     `checkerboard-64__rrect-lg__inactive`, against d0219, g <= B. Its withheld siblings
                  `checkerboard-32__rrect-lg__inactive` (referee) and `photo__rrect-lg__inactive` (holdout) are
                  read once, at read 9, on the selected point only.
  (b) flattered:  `hc-text__`, `impulse__` and `checkerboard-8__rrect-lg__inactive`, against d0219, g <= B.
  (c) no new trade: every other cell, against b2d074, zero cells `away` with g > B (and so none past 3 B).
  (d) halvings:   W48's that held, against d0219 as W48 read them (every partition): C rest at both scales and
                  F inactive at 1x, the target aggregate A <= A_ref / 2 (W46's `target_aggregate`). At the gate
                  a withheld cell R cannot move (rest pose, or span <= 96, where farS = 0) enters at its read-8
                  value, which it reads by construction; read 9 re-reads it.
**X75** is the builder's refusal: no point that draws opaque glass exists to be read.

**X74 (the authority report).** Over a probe's points, a cell that reads ONE distinct value is outside the
family's reach and is named, with the reason when the arithmetic predicts it (farS = 0 at span <= 96). The
objective excludes those cells by this declaration. They are also the reproduction control: each must read its
`b2d074d2df24` value within `CONTROL_TOLERANCE_BAR` of its bar, or the probe set is VOID and nothing is selected.

**DL4 (the selection).** Per scale, separably (a dpr-1 cell reads only `tintAlphaFar1x`, a dpr-2 cell only
`tintAlphaFar2x`; `rampAtScale` at exactly 1 and 2): among the points that meet DL2 at that scale, the minimum of
the objective, the median over the reachable gate cells of |log((k + ε)/(n + ε))| with ε the cell's code; points
within τ of the minimum are tied, τ the median of log(1 + bar/(n + ε)) over the same cells; among tied points,
the LARGEST far delta (the smallest departure from the shipped bytes). The landing point is (far1x, far2x) of the
two scales' selections. A scale with no point meeting DL2 makes the verdict NEITHER: W49a closes at the finding
and the parent asks the user. Points that fail are reported, never selected.
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
T1_PATH = RESULTS / "2026-10-03-w44-g1-refit" / "cuts" / "t1.py"
B2D074_CUT = RESULTS / "2026-10-06-w48-g1-refit" / "cuts" / "cut-025-w48-dl9-exposure.json.gz"
PROFILES = {1: "apple-macos-27.0-1x-dark-standard-glass0.25", 2: "apple-macos-27.0-2x-dark-standard-glass0.25"}
REPAIR_GATE = "checkerboard-64__rrect-lg__inactive"
REPAIR_WITHHELD = ("checkerboard-32__rrect-lg__inactive", "photo__rrect-lg__inactive")
FLATTERED = ("hc-text__rrect-lg__inactive", "impulse__rrect-lg__inactive", "checkerboard-8__rrect-lg__inactive")
HALVINGS = {1: (("C", "rest"), ("F", "inactive")), 2: (("C", "rest"),)}
CEILING_B = 3.0
CONTROL_TOLERANCE_BAR = 0.1
SPAN = {"capsule-button": 44, "rrect-sm": 32, "rrect-md": 96, "rrect-ml": 128, "rrect-lg": 160,
        "glass-over-glass": 130, "toolbar-group": 44}


def _t1():
    """W44 G1's `classify` and the two constants it reads, executed from `t1.py`'s own source. The module
    itself imports W44's bindings through `bed`, which a W49a reader has no business loading, so only these
    three statements are taken, by their AST nodes, and run; their bytes are W44's (part 1 pins the file)."""
    import ast
    import types
    source = T1_PATH.read_text()
    tree = ast.parse(source)
    keep = [node for node in tree.body
            if (isinstance(node, ast.FunctionDef) and node.name == "classify")
            or (isinstance(node, ast.Assign) and any(getattr(t, "id", None) in ("RATIO_CLAUSE", "EQUAL")
                                                      for t in node.targets))]
    if len(keep) != 3:
        raise RuntimeError(f"{T1_PATH}: expected classify, RATIO_CLAUSE and EQUAL, found {len(keep)} nodes")
    module = types.ModuleType("w44_t1_classify")
    exec(compile(ast.Module(body=keep, type_ignores=[]), str(T1_PATH), "exec"), module.__dict__)
    return module


T1 = _t1()


def b2d074_cells() -> dict:
    """(scale, scene) -> the W48 exposure cut's dark WebGPU T1 cell (its `candidate` is b2d074d2df24)."""
    cut = json.load(gzip.open(B2D074_CUT))
    return {(c["scale"], c["scene"]): c for c in cut["T1"]["cells"]
            if c["tier"] == "webgpu" and c["profile"] in PROFILES.values()}


def bands_of(cell: dict, k_cell: dict | None = None) -> tuple[dict, dict]:
    """(change band, away band) values {n, k, bar, code} of one cell: T1 for F, C, P; T1-fine and T1-low for T.
    `k_cell` supplies k (and k's bands) when it differs from `cell` (a b2d074 reading read as the candidate)."""
    k_cell = k_cell or cell
    if cell["stratum"] != "T":
        whole = dict(n=cell["native"], k=k_cell["candidate"])
        return whole, whole
    if "bands" not in cell or "bands" not in k_cell:
        raise ValueError(f"{cell['scene']}: a T cell with no band reading")
    fine = dict(n=cell["bands"]["fine"]["native"], k=k_cell["bands"]["fine"]["candidate"])
    low = dict(n=cell["bands"]["low"]["native"], k=k_cell["bands"]["low"]["candidate"])
    return fine, low


def ref_band(cell: dict, which: str, column: str) -> float:
    """The reference value of a band: `column` 'reference' (d0219) or 'candidate' (b2d074, from its cut)."""
    if cell["stratum"] != "T":
        return cell[column]
    return cell["bands"]["fine" if which == "change" else "low"][column]


def classify(n, c, k, bar, code) -> dict:
    return T1.classify(n, c, k, bar, code)


def reading(cell: dict, b2d: dict) -> dict:
    """One point cell read against d0219 and against b2d074, on its change and away bands."""
    change, away = bands_of(cell)
    bar, code = cell["bar"], cell["code"]
    out = dict(scene=cell["scene"], scale=cell["scale"], stratum=cell["stratum"], pose=cell["pose"],
               partition=cell["partition"], native=cell["native"], k=cell["candidate"], d0219=cell["reference"],
               b2d074=b2d["candidate"], bar=bar, code=code)
    for ref, column, source in (("d0219", "reference", cell), ("b2d074", "candidate", b2d)):
        ch = classify(change["n"], ref_band(source, "change", column), change["k"], bar, code)
        aw = classify(away["n"], ref_band(source, "away", column), away["k"], bar, code)
        out[ref] = dict(change=ch["change"], growthInB=ch["growth"] / ch["B"], fidelity=ch["fidelity"],
                        awayChange=aw["change"], awayGrowthInB=aw["growth"] / aw["B"])
    out["d0219Value"], out["b2d074Value"] = cell["reference"], b2d["candidate"]
    return out


def target_aggregate(rows: list[tuple[float, float, float, float]]) -> dict | None:
    """W46's `target_aggregate` on (n, c, k, code) rows: A and A_ref, the medians of |log((x + ε)/(n + ε))|."""
    if not rows:
        return None
    le = lambda x, n, e: abs(math.log((x + e) / (n + e)))  # noqa: E731
    a = statistics.median(le(k, n, e) for n, c, k, e in rows)
    a_ref = statistics.median(le(c, n, e) for n, c, k, e in rows)
    return dict(cells=len(rows), A=a, referenceA=a_ref, halved=a <= 0.5 * a_ref)


def moved_by_r(scene: str) -> bool:
    """Whether family R can move a cell at all: the receded pose and a surface span above the knee (96)."""
    return "__inactive" in scene and SPAN.get(scene.split("__")[1], 0) > 96


def evaluate_profile(point_cells: list[dict], scale: int, b2d: dict, partitions=("gate",)) -> dict:
    """DL2 on one profile. `point_cells` are the point's rendered T1 cells at `scale`; every in-scope cell the
    point did not render (the rest pose, and in a gate read the withheld cells) reads b2d074 by construction
    and is taken from `b2d`, which `moved_by_r` must agree with."""
    rendered = {c["scene"]: c for c in point_cells if c["scale"] == scale and c["tier"] == "webgpu"
                and c["profile"] == PROFILES[scale]}
    scope = {s: c for (sc, s), c in b2d.items() if sc == scale and c["partition"] in partitions}
    unread = sorted(s for s in scope if s not in rendered and moved_by_r(s))
    rows = []
    for scene, base in sorted(scope.items()):
        cell = rendered.get(scene)
        if cell is None:
            cell = dict(base, candidate=base["candidate"])                 # b2d074 by construction
            if "bands" in base:
                cell["bands"] = base["bands"]
        rows.append(reading(cell, base))
    by = {r["scene"]: r for r in rows}
    fails = []
    if REPAIR_GATE in by and by[REPAIR_GATE]["d0219"]["awayGrowthInB"] > 1:
        fails.append(f"(a) {REPAIR_GATE} {by[REPAIR_GATE]['d0219']['awayGrowthInB']:+.2f} B against d0219")
    for scene in REPAIR_WITHHELD:
        if scene in by and by[scene]["d0219"]["awayGrowthInB"] > 1:
            fails.append(f"(a) {scene} {by[scene]['d0219']['awayGrowthInB']:+.2f} B against d0219")
    for scene in FLATTERED:
        if scene in by and by[scene]["d0219"]["awayGrowthInB"] > 1:
            fails.append(f"(b) {scene} {by[scene]['d0219']['awayGrowthInB']:+.2f} B against d0219")
    special = {REPAIR_GATE, *REPAIR_WITHHELD, *FLATTERED}
    away = sorted(((r["scene"], r["b2d074"]["awayGrowthInB"]) for r in rows if r["scene"] not in special
                   and r["b2d074"]["awayChange"] == "away" and r["b2d074"]["awayGrowthInB"] > 1),
                  key=lambda x: -x[1])
    for scene, g in away:
        fails.append(f"(c) {scene} {g:+.2f} B against b2d074" + (" (past 3 B)" if g > CEILING_B else ""))
    halvings = {}
    for stratum, pose in HALVINGS[scale]:
        members = []
        for (sc, s), base in b2d.items():
            if sc != scale or base["stratum"] != stratum or base["pose"] != pose:
                continue
            k = rendered[s]["candidate"] if s in rendered else base["candidate"]
            if s not in rendered and moved_by_r(s):
                unread.append(s)
            members.append((base["native"], base["reference"], k, base["code"]))
        agg = target_aggregate(members)
        halvings[f"{stratum} {pose}"] = agg
        if agg is not None and not agg["halved"]:
            fails.append(f"(d) {stratum} {pose} A {agg['A']:.4f} above half of d0219's {agg['referenceA']:.4f}")
    return dict(scale=scale, profile=PROFILES[scale], partitions=list(partitions), cells=len(rows),
                unread=sorted(set(unread)), meets=not fails and not unread, failures=fails,
                awayBeyondB=[dict(scene=s, growthInB=g) for s, g in away], halvings=halvings, perCell=rows)


def authority(points: dict[str, list[dict]], scale: int, b2d: dict) -> dict:
    """X74 over one probe's points at one scale: distinct readings per rendered cell; the cells outside reach,
    with the predicted reason; the reproduction control on those cells."""
    values: dict[str, set] = {}
    for cells in points.values():
        for c in cells:
            if c["scale"] == scale:
                values.setdefault(c["scene"], set()).add(c["candidate"])
    outside, reach, control = [], [], []
    for scene, vals in sorted(values.items()):
        if len(vals) > 1:
            reach.append(scene)
            continue
        predicted = not moved_by_r(scene)
        outside.append(dict(scene=scene, reason="farS = 0 at span <= 96 (predicted)" if predicted
                            else "UNEXPLAINED: the arithmetic predicts R moves it"))
        base = b2d[(scale, scene)]
        delta = abs(next(iter(vals)) - base["candidate"])
        control.append(dict(scene=scene, delta=delta, bar=base["bar"],
                            holds=delta <= CONTROL_TOLERANCE_BAR * base["bar"]))
    void = [c["scene"] for c in control if not c["holds"]]
    return dict(scale=scale, reach=reach, outside=outside, control=control,
                verdict="VOID: the control cells do not reproduce b2d074d2df24" if void else "control holds",
                voidCells=void)


def objective(cells: list[dict], scale: int, reach: list[str]) -> tuple[float | None, float | None]:
    mine = [c for c in cells if c["scale"] == scale and c["scene"] in reach and c["partition"] == "gate"]
    if not mine:
        return None, None
    le = lambda x, n, e: abs(math.log((x + e) / (n + e)))  # noqa: E731
    a = statistics.median(le(c["candidate"], c["native"], c["code"]) for c in mine)
    tau = statistics.median(math.log(1 + c["bar"] / (c["native"] + c["code"])) for c in mine)
    return a, tau


def select(points: dict[str, tuple[float, list[dict]]], b2d: dict) -> dict:
    """DL4 over P2's points: `points` maps a label to (far, its rendered T1 cells at both scales)."""
    out = dict(scales={}, verdict=None, landing=None)
    chosen = {}
    for scale in (1, 2):
        auth = authority({k: v[1] for k, v in points.items()}, scale, b2d)
        rows = []
        for label, (far, cells) in points.items():
            ev = evaluate_profile(cells, scale, b2d)
            obj, tau = objective(cells, scale, auth["reach"])
            rows.append(dict(label=label, far=far, meets=ev["meets"], objective=obj, tau=tau,
                             failures=ev["failures"], unread=ev["unread"], halvings=ev["halvings"]))
        passing = [r for r in rows if r["meets"] and r["objective"] is not None]
        selected = None
        if auth["voidCells"]:
            reason = auth["verdict"]
        elif not passing:
            reason = "no point meets DL2 at this scale"
        else:
            best = min(r["objective"] for r in passing)
            tau = passing[0]["tau"]
            tied = [r for r in passing if r["objective"] <= best + tau]
            selected = max(tied, key=lambda r: r["far"])
            reason = (f"minimum objective {best:.4f}, tie τ {tau:.4f}, {len(tied)} tied; the largest far "
                      f"{selected['far']:g}")
        chosen[scale] = selected
        out["scales"][f"{scale}x"] = dict(authority=auth, points=sorted(rows, key=lambda r: r["far"]),
                                          selected=None if selected is None else selected["label"],
                                          why=reason)
    if all(chosen.values()):
        out["verdict"] = "LANDING CANDIDATE (pending read 9 on the withheld cells)"
        out["landing"] = dict(tintAlphaFar1x=chosen[1]["far"], tintAlphaFar2x=chosen[2]["far"])
    else:
        out["verdict"] = "NEITHER: W49a closes at the finding and the parent asks the user (DL4)"
    return out
