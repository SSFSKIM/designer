"""W44 G0 (a): T1, the texture row (charter Design "T1", MARKED; Decision Log 2).

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
BAR_PATH = B.EVIDENCE / "bar" / "t1-bar.json"
STRATA = {"F": ("checkerboard-4", "checkerboard-8", "hc-text-7"),
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
        partitions=("gate", "referee", "holdout")) -> dict:
    """T1 over `profiles` x `tiers`: the per-cell outputs and the aggregates.

    `bed_rows` is the candidate's (k), `reference_rows` the c05 rows (c), both lists of matrix rows.
    `partitions` names which partitions this bed is expected to carry: a member of one of them with
    no row is UNMEASURED (`noRow`); a member of another is `notRead` (e.g. the holdout and the
    referees before the exposure)."""
    here = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r for r in bed_rows}
    ref = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
           for r in reference_rows}
    cells, no_row, not_read, unmeasured = [], [], [], []
    for tier in tiers:
        for profile, sid in population(profiles):
            part = partition(profile, sid, held)
            label = f"{profile} {tier} {sid}"
            if part not in partitions:
                not_read.append(label)
                continue
            row, rrow = here.get((profile, tier, sid)), ref.get((profile, tier, sid))
            if row is None:
                no_row.append(label)
                continue
            n = B.value(row, "material", "interiorStdDevNative")
            k = B.value(row, "material", "interiorStdDevWeb")
            c = B.value(rrow, "material", "interiorStdDevWeb")
            nc = B.value(rrow, "material", "interiorStdDevNative")
            mean = B.value(row, "material", "interiorMeanNative")
            if None in (n, k, c, mean):
                unmeasured.append(label)
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
            cells.append(dict(
                profile=profile, tier=tier, scene=sid, set=B.SCENES.role[sid], partition=part,
                stratum=stratum(sid), scale=B.scale_of(profile), scheme=B.scheme_of(profile),
                pose=pose(sid), spanClass=span_class(sid), native=n, reference=c, candidate=k,
                ratio=k / n if n else None, referenceRatio=c / n if n else None, bar=bar, code=code,
                barFloorAssumed=assumed, logError=log_error(k, n, code),
                referenceLogError=log_error(c, n, code), **out))
    return dict(cells=cells, noRow=no_row, notRead=len(not_read), unmeasured=unmeasured,
                aggregates=aggregates([c for c in cells if c["partition"] == "gate"]),
                aggregatesAllRead=aggregates(cells))


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


def landing(cells) -> dict:
    """Decision Log 4's landing rule, T1's clauses only, on the cells it names: WebGPU, 2x light,
    both poses, F u C u P less the referees (the gate partition). The referee clauses read the
    exposure and "every other adopted row" reads the other cuts; both are reported as outside
    this evaluation, never assumed."""
    scope = [c for c in cells if c["tier"] == GATED_TIER and c["scale"] == 2 and c["scheme"] == "light"
             and c["profile"] in GATED_PROFILES and c["partition"] == "gate"]
    f = [c for c in scope if c["stratum"] == "F"]
    away_beyond = [c for c in scope if c["change"] == "away" and c["growth"] > c["B"]]
    overshoot = [c for c in scope if c["change"] == "overshoot"]
    f_agg = statistics.median(c["logError"] for c in f) if f else None
    f_ref = statistics.median(c["referenceLogError"] for c in f) if f else None
    named = lambda sel: [f"{c['scene']} {c['scale']}x" for c in sel]  # noqa: E731
    full = bool(f) and all(c["fidelity"] == "within" for c in f) and not away_beyond and not overshoot
    improvement = (bool(f) and f_agg <= 0.5 * f_ref and not away_beyond and not overshoot)
    c_p = [c for c in scope if c["stratum"] in ("C", "P")]
    return dict(
        scope="WebGPU, 2x light, both poses, F u C u P, gate partition (referees and holdout apart)",
        cells=len(scope), fCells=len(f),
        fAggregate=f_agg, fAggregateReference=f_ref,
        fNotWithin=named(c for c in f if c["fidelity"] != "within"),
        awayBeyondB=named(away_beyond), overshoot=named(overshoot),
        regressionBudget=dict(
            namedMissUnchanged=named(c for c in c_p if c["fidelity"] == "miss" and c["change"] == "unchanged"),
            namedRegressionWithinB=named(c for c in c_p if c["change"] == "away" and c["growth"] <= c["B"])),
        fullCloseT1Clauses=full, improvementT1Clauses=improvement,
        verdict=("FULL CLOSE (T1 clauses)" if full else
                 "IMPROVEMENT LANDING (T1 clauses)" if improvement else "NEITHER: closes at the finding"),
        outside="the referees' clause (read at the exposure) and every other adopted row are not "
                "evaluated here")


def selection_metric(cells) -> float | None:
    """The selection rule's metric: the median |log((k + eps) / (n + eps))| over F u C u P at 2x
    WebGPU light, gate partition (the T1 aggregate's regularisation; declared in the draft)."""
    sel = [c["logError"] for c in cells if c["tier"] == GATED_TIER and c["scale"] == 2
           and c["scheme"] == "light" and c["partition"] == "gate"]
    return statistics.median(sel) if sel else None


def selection_tie(cells) -> float | None:
    """The tie width: the bar on the aggregate's scale, the median over the same cells of
    log((n + bar + eps) / (n + eps))."""
    sel = [math.log((c["native"] + c["bar"] + c["code"]) / (c["native"] + c["code"])) for c in cells
           if c["tier"] == GATED_TIER and c["scale"] == 2 and c["scheme"] == "light" and c["partition"] == "gate"]
    return statistics.median(sel) if sel else None
