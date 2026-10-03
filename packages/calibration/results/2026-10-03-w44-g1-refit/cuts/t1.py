"""W44 G1 step 0: T1 with the text stratum promoted (charter Decision Log 7 item 3), G0's T1
(`results/2026-10-03-w44-g0-declaration/cuts/t1.py`) copied and extended; G0's committed copy,
which part 1 pins, is untouched. Part 2's one amendment pins THIS file, before any fit render.

What changes, each executing an item of Decision Log 7 (charter v1.3, `ea487a17`):
  - **Four strata.** `hc-text-7` leaves F and is the text stratum T (item 3). F is the fine
    pitches (`checkerboard-4`, `-8`), C and P as before.
  - **T's two bands are its outputs.** On T1 a T cell under-reads (the broad text bar is
    under-passed) while its fine band reads several times over (the glyph edges are over-passed),
    so one statistic measures the mixture. A T cell is read on two bands of one image (G1
    `readings.py`): **T1-fine**, the SD of the sigma 4 device px residual over the native silhouette
    eroded 4 CSS px, and **T1-low**, the SD of the sigma 4 low-pass over the same support. Each band
    carries T1's three outputs per cell (`classify` on the band's native, c05 and candidate values,
    at the cell's own bar and code: the seven runs are pixel-identical, so every statistic's
    run-to-run separation is 0 and the bar is 0.5 code for the bands as for T1). The cell's
    FIDELITY and CHANGE are T1-fine's; its `away` veto reads T1-low's; T1 itself is recorded.
  - **The landing scope is F u T u C u P** (`landing`): every F cell within for the full close (no
    T cell is required within); no cell away with g > B, a T cell's read on T1-low; no cell
    overshoot, a T cell's read on T1-fine. A T cell in the scope with no band reading is
    UNMEASURED, never a pass.
  - **The selection metric and the move objectives read F u C u P** (`selection_metric`,
    `move_objective`): the charter's selection rule names those three strata, and T is outside them.
  - **The moves' cells and within clauses** (`in_move`, `within_clause`), as part 2 states them
    after the amendment: move 1 the rest mid and thick cells, its clause every F and every
    pitch-16 (`checkerboard`) cell within (item 2: the photo cells out of the clause, still in the
    regression budget); move 2 the rest thin cells and move 3 every inactive cell, each clause
    every F, C and P cell within. A T cell is read on its bands in every move and is never
    required within.

G0's text follows, unchanged; where it says three strata, this file has four.

W44 G0 (a): T1, the texture row (charter Design "T1", MARKED; Decision Log 2).

**Statistic.** The driver's `interiorStdDev`: the luminance SD in LINEAR light over the NATIVE
silhouette bounded to the declared region (rim and lens band included), read off each row as
`material.interiorStdDev{Native,Web}.value`. Web against native on the same cell. Nothing here
recomputes it; `../port/` proves the port that the bar and the readings use reproduces it.

**Population.** Every scene a profile declares whose backdrop is one of `T1_BACKDROPS`, in every
set, at both scales and both tiers; drawn from `scenes.json`, never from the bed. Gated: the two
light 0.25 profiles on the WebGPU tier. Read: the same profiles' CSS tier, the dark 0.25 profiles
and the 0.5 profiles. Three strata: F the fine pitches, C the coarse ones, P the photo. Each
member is in one partition: `holdout` (canonical split), `referee` (`referees/referees.json`) or
`gate` (everything else).

**Bar and the absolute bound.** Per cell from `../bar/t1-bar.json` (the seven G1a runs): `bar` and
`code`, the linear step of one sRGB code at the cell's native interior mean. A cell with no bar
entry (a 0.5 profile) is read with `bar = 0.5 code`, the floor, and marked `barFloorAssumed`.

**Three outputs per cell** (n native, c the c05 reading, k the candidate's):
    B = max(1 code, 2 bar);  e(x) = |x - n|;  g = e(k) - e(c);  delta = |k - c|
  1. fidelity  `within` if e(k) <= B, or if n >= 1 code and |k / n - 1| <= 0.10; else `miss`
               (reported with the signed k - n).
  2. change    by precedence: `unchanged` if delta <= bar; else `overshoot` if (k - n)(c - n) < 0
               and the cell is a miss; else `toward` if g < 0, or g = 0 with a sign change (an
               equal-error crossing; "g = 0" read to `EQUAL`, 1e-12); else `away`.
  3. aggregates per stratum x scale x tier x pose: the median of |log((k + eps) / (n + eps))|,
               eps = 1 code (the cell's own), and the count of each fidelity and change state;
               `aggregates` over the gate partition (what a stage holds before the exposure),
               `aggregatesAllRead` over every partition the bed carried.

`classify` is the one implementation of outputs 1 and 2; the four examples the charter pins are
tests (`test_t1.py`).
"""
from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import bed as B

HERE = Path(__file__).resolve().parent
BAR_PATH = B.G0 / "bar" / "t1-bar.json"
STRATA = {"F": ("checkerboard-4", "checkerboard-8"),
          "T": ("hc-text-7",),
          "C": ("checkerboard", "checkerboard-lc16", "checkerboard-32", "checkerboard-64", "hc-text",
                "hc-text-28", "impulse"),
          "P": ("photo",)}
T1_BACKDROPS = tuple(b for s in STRATA.values() for b in s)
GATED_PROFILES = ("apple-macos-27.0-1x-light-standard-glass0.25",
                  "apple-macos-27.0-2x-light-standard-glass0.25")
GATED_TIER = "webgpu"
RATIO_CLAUSE = 0.10
# "g = 0" is read to this tolerance, far below any code (one code is above 3e-4 everywhere): an
# equal-error crossing posed in decimals lands a few ulps either side of zero in binary floats.
EQUAL = 1e-12
FIDELITY = ("within", "miss")
CHANGE = ("unchanged", "toward", "overshoot", "away")
# The text stratum's two bands (Decision Log 7 item 3): which band each of a T cell's landing
# clauses reads. Fidelity and change are T1-fine's; the `away` veto is T1-low's.
BANDS = ("fine", "low")
T_READS = {"fidelity": "fine", "change": "fine", "overshoot": "fine", "away": "low"}
# The moves' cells (part 2 after its amendment): pose and span classes, at 2x light WebGPU, gate
# partition. `None` is every span.
MOVES = {"move1": dict(pose="rest", spans=("mid", "thick")),
         "move2": dict(pose="rest", spans=("thin",)),
         "move3": dict(pose="inactive", spans=None)}
SELECTION_STRATA = ("F", "C", "P")


def stratum(sid: str) -> str:
    bg = B.SCENES.by_id[sid]["background"]
    return next(k for k, v in STRATA.items() if bg in v)


def span_class(sid: str) -> str:
    s = B.SCENES.span(sid)
    return "thin" if s <= 44 else "mid" if s == 96 else "thick" if 128 <= s <= 160 else "other"


def pose(sid: str) -> str:
    return "inactive" if B.SCENES.inactive(sid) else "rest"


def population(profiles) -> list[tuple[str, str]]:
    return [(p, sid) for p in profiles for sid in B.SCENES.declared(p)
            if B.SCENES.by_id[sid]["background"] in T1_BACKDROPS]


def partition(profile: str, sid: str, held: set) -> str:
    if (profile, sid) in held:
        return "referee"
    return "holdout" if B.SCENES.role[sid] == "holdout" else "gate"


def code_step(mean: float) -> float:
    """The linear step of one sRGB code at linear level `mean` (`port/interior.code_step`)."""
    if mean <= 0.0031308:
        return 1 / (255 * 12.92)
    encoded = 1.055 * mean ** (1 / 2.4) - 0.055
    return 2.4 / 1.055 * ((encoded + 0.055) / 1.055) ** 1.4 / 255


def load_bars(path: Path = BAR_PATH) -> dict:
    body = json.loads(path.read_bytes())
    return {(c["profile"], c["scene"]): dict(bar=c["bar"], code=c["code"], status=c["status"])
            for c in body["table"]}


def classify(n: float, c: float, k: float, bar: float, code: float) -> dict:
    """T1's outputs 1 and 2 for one cell (the module docstring; the charter's Design "T1")."""
    B_ = max(code, 2 * bar)
    e_k, e_c = abs(k - n), abs(c - n)
    g, delta = e_k - e_c, abs(k - c)
    within = e_k <= B_ or (n >= code and abs(k / n - 1) <= RATIO_CLAUSE)
    fidelity = "within" if within else "miss"
    crossed = (k - n) * (c - n) < 0
    if delta <= bar:
        change = "unchanged"
    elif crossed and fidelity == "miss":
        change = "overshoot"
    elif g < -EQUAL or (abs(g) <= EQUAL and crossed):
        change = "toward"
    else:
        change = "away"
    return dict(B=B_, fidelity=fidelity, signed=k - n, change=change, errorCandidate=e_k,
                errorReference=e_c, growth=g, displacement=delta, crossed=crossed)


def log_error(x: float, n: float, code: float) -> float:
    return abs(math.log((x + code) / (n + code)))


def cut(bed_rows, reference_rows, profiles, bars, held, tiers=("webgpu", "css"),
        partitions=("gate", "referee", "holdout"), bands=None, reference_bands=None) -> dict:
    """T1 over `profiles` x `tiers`: the per-cell outputs and the aggregates.

    `bed_rows` is the candidate's (k), `reference_rows` the c05 rows (c), both lists of matrix rows.
    `partitions` names which partitions this bed is expected to carry: a member of one of them with
    no row is UNMEASURED (`noRow`); a member of another is `notRead` (e.g. the holdout and the
    referees before the exposure).

    W44 G1: `bands` and `reference_bands` map (profile, tier, scene) to the band readings of the
    candidate's capture and of the c05 capture, each {"fine": {"native", "web"}, "low": {...}}
    (`readings.read`'s native and web sides). Where both are given for a cell, the cell carries
    `bands`: T1's outputs 1 and 2 on each band, at the cell's bar and code. A band's native value
    must agree between the two readings (the same fixture, the same support)."""
    here = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r for r in bed_rows}
    ref = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
           for r in reference_rows}
    cells, no_row, not_read, unmeasured, missing = [], [], [], [], []
    for tier in tiers:
        for profile, sid in population(profiles):
            part = partition(profile, sid, held)
            label = f"{profile} {tier} {sid}"
            if part not in partitions:
                not_read.append(label)
                continue
            row, rrow = here.get((profile, tier, sid)), ref.get((profile, tier, sid))
            where = dict(profile=profile, tier=tier, scene=sid, partition=part, stratum=stratum(sid),
                         scale=B.scale_of(profile), scheme=B.scheme_of(profile), pose=pose(sid))
            if row is None:
                no_row.append(label)
                missing.append(dict(where, reason="no row"))
                continue
            n = B.value(row, "material", "interiorStdDevNative")
            k = B.value(row, "material", "interiorStdDevWeb")
            c = B.value(rrow, "material", "interiorStdDevWeb")
            nc = B.value(rrow, "material", "interiorStdDevNative")
            mean = B.value(row, "material", "interiorMeanNative")
            if None in (n, k, c, mean):
                unmeasured.append(label)
                missing.append(dict(where, reason="no reading" if rrow is not None else "no reference row"))
                continue
            if nc != n:
                raise SystemExit(f"T1: {label}: the reference row's native SD {nc} is not this row's {n}")
            entry = bars.get((profile, sid))
            if entry is None:
                code = code_step(mean)
                bar, assumed = 0.5 * code, True
            else:
                code, bar, assumed = entry["code"], entry["bar"], False
                if abs(code - code_step(mean)) > 1e-12:
                    raise SystemExit(f"T1: {label}: the bar file's code {code} is not this row's "
                                     f"{code_step(mean)}")
            out = classify(n, c, k, bar, code)
            band = band_outputs(bands, reference_bands, (profile, tier, sid), bar, code, label)
            cells.append(dict(
                profile=profile, tier=tier, scene=sid, set=B.SCENES.role[sid], partition=part,
                stratum=stratum(sid), scale=B.scale_of(profile), scheme=B.scheme_of(profile),
                pose=pose(sid), spanClass=span_class(sid), native=n, reference=c, candidate=k,
                ratio=k / n if n else None, referenceRatio=c / n if n else None, bar=bar, code=code,
                barFloorAssumed=assumed, logError=log_error(k, n, code),
                referenceLogError=log_error(c, n, code), **out, **({"bands": band} if band else {})))
    return dict(cells=cells, noRow=no_row, notRead=len(not_read), unmeasured=unmeasured, missing=missing,
                aggregates=aggregates([c for c in cells if c["partition"] == "gate"]),
                aggregatesAllRead=aggregates(cells),
                bandAggregates=band_aggregates([c for c in cells if c["partition"] == "gate"]))


def band_outputs(bands, reference_bands, key, bar, code, label) -> dict | None:
    """T1's outputs 1 and 2 on each band of one cell, or None when either reading is absent."""
    if not bands or not reference_bands or key not in bands or key not in reference_bands:
        return None
    here, ref = bands[key], reference_bands[key]
    out = {}
    for name in BANDS:
        n, k = here[name]["native"], here[name]["web"]
        rn, c = ref[name]["native"], ref[name]["web"]
        if None in (n, k, c):
            return None
        if abs(rn - n) > 1e-12:
            raise SystemExit(f"T1 {name}: {label}: the reference capture's native band {rn} is not this "
                             f"cell's {n}")
        out[name] = dict(native=n, reference=c, candidate=k, ratio=k / n if n else None,
                         referenceRatio=c / n if n else None, logError=log_error(k, n, code),
                         referenceLogError=log_error(c, n, code), **classify(n, c, k, bar, code))
    return out


def band_aggregates(cells) -> dict:
    """Output 3 on each band, over the cells that carry band readings."""
    groups = defaultdict(list)
    for c in cells:
        if "bands" not in c:
            continue
        for name in BANDS:
            b = c["bands"][name]
            groups[f"{name} {c['stratum']} {c['scale']}x {c['scheme']} {c['tier']} {c['pose']}"].append(b)
    out = {}
    for key, group in sorted(groups.items()):
        out[key] = dict(cells=len(group),
                        medianLogError=statistics.median(b["logError"] for b in group),
                        referenceMedianLogError=statistics.median(b["referenceLogError"] for b in group),
                        fidelity=dict(Counter(b["fidelity"] for b in group)),
                        change=dict(Counter(b["change"] for b in group)))
    return out


def aggregates(cells) -> dict:
    groups = defaultdict(list)
    for c in cells:
        groups[f"{c['stratum']} {c['scale']}x {c['scheme']} {c['tier']} {c['pose']}"].append(c)
        groups[f"{c['stratum']} {c['scale']}x {c['scheme']} {c['tier']} both"].append(c)
    out = {}
    for key, group in sorted(groups.items()):
        out[key] = dict(cells=len(group),
                        medianLogError=statistics.median(c["logError"] for c in group),
                        referenceMedianLogError=statistics.median(c["referenceLogError"] for c in group),
                        fidelity=dict(Counter(c["fidelity"] for c in group)),
                        change=dict(Counter(c["change"] for c in group)))
    return out


def in_landing_scope(c) -> bool:
    return (c["tier"] == GATED_TIER and c["scale"] == 2 and c["scheme"] == "light"
            and c["profile"] in GATED_PROFILES and c["partition"] == "gate")


def landing_reads(c) -> dict:
    """What the landing reads of one cell: T1's outputs, or for a T cell its bands' (Decision Log 7
    item 3). None for a T cell with no band reading."""
    if c["stratum"] != "T":
        return dict(fidelity=c["fidelity"], change=c["change"], awayChange=c["change"],
                    awayGrowth=c["growth"], awayB=c["B"])
    if "bands" not in c:
        return None
    fine, low = c["bands"][T_READS["fidelity"]], c["bands"][T_READS["away"]]
    return dict(fidelity=fine["fidelity"], change=fine["change"], awayChange=low["change"],
                awayGrowth=low["growth"], awayB=low["B"])


def landing(cells, missing=()) -> dict:
    """Decision Log 4's landing rule, T1's clauses only, on the cells it names: WebGPU, 2x light,
    both poses, F u T u C u P less the referees (the gate partition). The referee clauses read the
    exposure and "every other adopted row" reads the other cuts; both are reported as outside
    this evaluation, never assumed.

    `missing` is the cut's `missing` list. A member of the scope with no row or no reading makes
    the verdict UNMEASURED, never a landing: the full close needs every F cell and the budget
    needs every C and P cell, and an absent reading is neither (W43's rule: no verdict passes
    while a member is UNMEASURED; the review of W44 G0 (a)-(d)). A T cell with no band reading is
    absent in the same way (W44 G1: its clauses read its bands).

    The text stratum (Decision Log 7 item 3): a T cell is never required within; its overshoot is
    T1-fine's and its away-beyond-B is T1-low's."""
    scope = [c for c in cells if in_landing_scope(c)]
    absent = [m for m in missing if in_landing_scope(m)]
    absent += [dict(c, reason="no band reading") for c in scope if c["stratum"] == "T" and "bands" not in c]
    reads = {id(c): landing_reads(c) for c in scope}
    read = [c for c in scope if reads[id(c)] is not None]
    f = [c for c in read if c["stratum"] == "F"]
    away_beyond = [c for c in read if reads[id(c)]["awayChange"] == "away"
                   and reads[id(c)]["awayGrowth"] > reads[id(c)]["awayB"]]
    overshoot = [c for c in read if reads[id(c)]["change"] == "overshoot"]
    f_agg = statistics.median(c["logError"] for c in f) if f else None
    f_ref = statistics.median(c["referenceLogError"] for c in f) if f else None
    named = lambda sel: [f"{c['scene']} {c['scale']}x" for c in sel]  # noqa: E731
    full = (not absent and bool(f) and all(c["fidelity"] == "within" for c in f)
            and not away_beyond and not overshoot)
    improvement = (not absent and bool(f) and f_agg <= 0.5 * f_ref and not away_beyond and not overshoot)
    c_p = [c for c in read if c["stratum"] in ("C", "P")]
    t = [c for c in read if c["stratum"] == "T"]
    return dict(
        scope="WebGPU, 2x light, both poses, F u T u C u P, gate partition (referees and holdout apart); "
              "a T cell's fidelity and change on T1-fine, its away on T1-low",
        cells=len(scope), fCells=len(f), tCells=len(t),
        unmeasuredInScope=[f"{m['scene']} {m['scale']}x ({m['reason']})" for m in absent],
        fAggregate=f_agg, fAggregateReference=f_ref,
        fNotWithin=named(c for c in f if c["fidelity"] != "within"),
        awayBeyondB=named(away_beyond), overshoot=named(overshoot),
        regressionBudget=dict(
            namedMissUnchanged=named(c for c in c_p if c["fidelity"] == "miss" and c["change"] == "unchanged"),
            namedRegressionWithinB=named(c for c in c_p if c["change"] == "away" and c["growth"] <= c["B"]),
            textLowAwayWithinB=named(c for c in t if reads[id(c)]["awayChange"] == "away"
                                     and reads[id(c)]["awayGrowth"] <= reads[id(c)]["awayB"])),
        textCells=[dict(scene=c["scene"], scale=c["scale"], pose=c["pose"],
                        t1=dict(fidelity=c["fidelity"], change=c["change"], native=c["native"],
                                reference=c["reference"], candidate=c["candidate"]),
                        fine={k: c["bands"]["fine"][k] for k in ("fidelity", "change", "native", "reference",
                                                                  "candidate", "growth", "B")},
                        low={k: c["bands"]["low"][k] for k in ("fidelity", "change", "native", "reference",
                                                                "candidate", "growth", "B")})
                   for c in t],
        fullCloseT1Clauses=full, improvementT1Clauses=improvement,
        verdict=(f"UNMEASURED: {len(absent)} cells of the landing scope have no reading" if absent else
                 "FULL CLOSE (T1 clauses)" if full else
                 "IMPROVEMENT LANDING (T1 clauses)" if improvement else "NEITHER: closes at the finding"),
        outside="the referees' clause (read at the exposure) and every other adopted row are not "
                "evaluated here")


def selection_metric(cells, where=None) -> float | None:
    """The selection rule's metric, as the charter states it (Design, "The selection rule"): the
    median |log(web / native)| over F u C u P at 2x WebGPU light, the landing scope's cells; T is
    outside F u C u P and is not read (W44 G1, Decision Log 7 item 3). `where`, a predicate on a
    cell, restricts it: the move objective is this metric over the move's cells. No
    regularisation: that is the aggregates' (output 3), not the rule's. Every T1 cell has a
    positive native SD; a cell whose web SD is 0 has no log and is left out (none on c05)."""
    sel = [abs(math.log(c["candidate"] / c["native"])) for c in cells
           if in_landing_scope(c) and c["stratum"] in SELECTION_STRATA and (where is None or where(c))
           and c["candidate"] > 0 and c["native"] > 0]
    return statistics.median(sel) if sel else None


def in_move(c, move: str) -> bool:
    """A landing-scope cell of `move`'s cells (part 2 after its amendment)."""
    m = MOVES[move]
    return (in_landing_scope(c) and c["pose"] == m["pose"]
            and (m["spans"] is None or c["spanClass"] in m["spans"]))


def move_objective(cells, move: str) -> float | None:
    """The move objective: the selection metric restricted to the move's cells (F u C u P)."""
    return selection_metric(cells, where=lambda c: in_move(c, move))


def within_clause(cells, move: str, missing=()) -> dict:
    """The move's within clause on T1's fidelity output. Move 1: every F cell and every pitch-16
    (`checkerboard`) cell of the move within (Decision Log 7 item 2: the photo cells are out of the
    clause). Moves 2 and 3: every F, C and P cell of the move within. A T cell is never required
    within (item 3); a clause member with no reading makes the clause UNMEASURED."""
    members = [c for c in cells if in_move(c, move) and c["stratum"] in SELECTION_STRATA]
    if move == "move1":
        members = [c for c in members if c["stratum"] == "F"
                   or B.SCENES.by_id[c["scene"]]["background"] == "checkerboard"]
    absent = [m for m in missing if in_landing_scope(m) and m["stratum"] in SELECTION_STRATA
              and m["pose"] == MOVES[move]["pose"]
              and (MOVES[move]["spans"] is None or span_class(m["scene"]) in MOVES[move]["spans"])
              and (move != "move1" or m["stratum"] == "F"
                   or B.SCENES.by_id[m["scene"]]["background"] == "checkerboard")]
    not_within = [f"{c['scene']} {c['scale']}x" for c in members if c["fidelity"] != "within"]
    return dict(move=move, members=len(members), notWithin=not_within,
                unmeasured=[f"{m['scene']} {m['scale']}x" for m in absent],
                verdict=("UNMEASURED" if absent or not members else
                         "WITHIN" if not not_within else "NOT WITHIN"))


def selection_tie(cells) -> float | None:
    """"A tie within the bar", on the metric's own scale: the median over the same cells of
    log(1 + bar / native), what one bar of displacement is worth in |log(web / native)|."""
    sel = [math.log(1 + c["bar"] / c["native"]) for c in cells
           if in_landing_scope(c) and c["stratum"] in SELECTION_STRATA and c["native"] > 0]
    return statistics.median(sel) if sel else None
