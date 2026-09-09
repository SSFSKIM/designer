#!/usr/bin/env python3
"""Settling experiment analysis (spec: 2026-09-05-settling-experiment.md).

    python3 analyze.py [--out results.md]

Reads manifest.json, measurements.json, topology.json, judgments.jsonl and fit.json (optional)
from figma-design-workspace/settling/ and writes results.md + results.json there. Handles partial
data: every table states how many builds and judgments it stands on.
"""
import json, re, os, sys, math, random, itertools, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
WS = os.environ.get("SETTLING_WS") or os.path.join(REPO, "figma-design-workspace/settling")
ARMS = ["none", "v1.1", "v2.0", "v2.1"]
sys.path.insert(0, HERE)
import rubric, rate, reliability as rel   # the rubric's items and shapes; the schedule; the statistics


def load(name, default):
    p = os.path.join(WS, name)
    if not os.path.exists(p):
        return default
    if name.endswith(".jsonl"):
        return [json.loads(l) for l in open(p) if l.strip()]
    return json.load(open(p))


manifest = load("manifest.json", {"cells": []})["cells"]
meas = load("measurements.json", {"builds": {}})["builds"]
topo = load("topology.json", None)
judg = load("judgments.jsonl", [])
def load_dir(name):
    out = []; d = os.path.join(WS, name)
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith(".jsonl"):
                out += [json.loads(l) for l in open(os.path.join(d, f)) if l.strip()]
    return out

judgm = load_dir("judgments-model")        # the second judge (a blinded astra-medium rater), one file per brief
judgm1 = load_dir("judgments-model-run1")  # its first run, fanned out per brief on a pre-fix schedule
judgb = load_dir("judgments-model-b")      # the third judge (a blinded claude-opus rater), same pairs, same shape
# Every judge's list by name, in the order the report prints them. The human file stays the
# primary endpoint and the only one the validity gate's human clause reads.
JUDGES = [(n, j) for n, j in (("human", judg), ("astra-medium", judgm), ("claude-opus", judgb)) if j]
fit = {}
_fitdir = os.path.join(WS, "fit")
if os.path.isdir(_fitdir):
    for _f in sorted(os.listdir(_fitdir)):
        if _f.endswith(".json"):
            fit.update(json.load(open(os.path.join(_fitdir, _f))))
cell = {c["id"]: c for c in manifest}
built = [c for c in manifest if c["id"] in meas and not meas[c["id"]].get("error")]

# ---------- the rubric's ratings (spec: 2026-09-09-quality-instrument.md) ----------
# The item set is per brief: rubric.items_for splices each brief's own b-items into the fixed ones,
# and t1 where the brief states a tone. The report's item list is therefore the union over the
# briefs, ordered by the brief that carries the most items.
ITEM_KEYS = []
for _b in sorted(rubric.BRIEF_FIT, key=lambda x: (-len(rubric.items_for(x)), x)):
    for _it in rubric.items_for(_b):
        if _it[0] not in ITEM_KEYS:
            ITEM_KEYS.append(_it[0])
AESTHETIC_KEYS = [k for k, block, _, _ in rubric.ITEMS if block == "aesthetics"]
SEVEN_ITEMS = [k for k in ITEM_KEYS if k in rubric.SEVEN_KEYS]
COMPOSITES = ["aesthetics", "brief fit", "defects"]
PAGE_SCORES = ["d1", "aesthetics", "brief fit", "defects", "e1"]   # the spec's five page scores
# Only the items rated on every page can trip the one pre-registered wording revision; the b-items
# (eight pages a brief) and the rare binary c-items are reported only (spec, Acceptance).
REVISABLE = AESTHETIC_KEYS + ["d1", "e1"]
CI_ROWS = ["d1"] + COMPOSITES              # the rows whose α carries a bootstrap interval
TWO_X = ["v2.0", "v2.1"]                   # the arms the grammar reading compares
# The report's rows: the five page scores, then the items the composites are built from (d1 and e1
# are page scores already and are not printed twice).
ROWS = PAGE_SCORES + [k for k in ITEM_KEYS if k not in ("d1", "e1")]
ROW_LABEL = {
    "aesthetics": f"aesthetics (VisAWI-S total, {AESTHETIC_KEYS[0]}–{AESTHETIC_KEYS[-1]})",
    "brief fit": "brief fit (mean of the brief's b-items, 0–2)",
    "defects": "defects (count of c1–c5)",
}
# The two model families the gateway offers, matched on the rater name's prefix.
FAMILIES = [("GPT", "astra"), ("Claude", "claude")]


def family_of(rater):
    for name, prefix in FAMILIES:
        if rater.startswith(prefix):
            return name
    return "other"


def _num(v):
    """A rating as an int, or None. The pilot raters wrote "7" rather than 7, and a defect item may
    arrive as true/false; every scale in the rubric is integral, so one integer is the value."""
    if isinstance(v, bool):
        return int(v)
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def load_rubric():
    """Every rater's ratings, keyed rater → page id → {item: value}, and the page order each run
    recorded. The model raters are the directory names under rubric/ (one file per brief, plus
    <brief>-retest.json for the second shuffle); the user is rubric-human.jsonl and is called
    "human". Returns the first pass, the retest and the first pass's orders, and skips any page or
    item a file does not carry, so a half-collected panel reads as far as it goes."""
    first, retest, orders = defaultdict(dict), defaultdict(dict), defaultdict(dict)
    d = os.path.join(WS, "rubric")
    if os.path.isdir(d):
        for rater in sorted(os.listdir(d)):
            rd = os.path.join(d, rater)
            if not os.path.isdir(rd):
                continue
            revised = []
            for f in sorted(os.listdir(rd)):
                if not f.endswith(".json"):
                    continue
                rec = json.load(open(os.path.join(rd, f)))
                if f.endswith("-revised.json"):
                    revised.append(rec); continue
                into = retest if f.endswith("-retest.json") else first
                for pid, page in (rec.get("pages") or {}).items():
                    vals = {k: _num(page.get(k)) for k in ITEM_KEYS}
                    vals = {k: v for k, v in vals.items() if v is not None}
                    if vals:
                        into[rater][pid] = vals
                if into is first and rec.get("order"):
                    orders[rater][rec.get("brief", f[:-5])] = rec["order"]
            # The one pre-registered wording revision: the revised value replaces the first pass's
            # for that item, and the first pass's value is kept as <item>_v1 so both α are printed.
            for rec in revised:
                for pid, page in (rec.get("pages") or {}).items():
                    for k in rec.get("revised", []):
                        v = _num(page.get(k))
                        if v is None or pid not in first[rater]:
                            continue
                        if k in first[rater][pid]:
                            first[rater][pid][k + "_v1"] = first[rater][pid][k]
                        first[rater][pid][k] = v
    # The user's file is one line per (page, pass): pass 2 is her own retest, and a later line for
    # the same slot supersedes an earlier one, as rate.py's queue reads it.
    human = {}
    for row in load("rubric-human.jsonl", []):
        if row.get("id"):
            human[(row["id"], row.get("pass", 1))] = row
    for (pid, ps), row in human.items():
        vals = {k: _num(row.get(k)) for k in ITEM_KEYS}
        vals = {k: v for k, v in vals.items() if v is not None}
        if vals:
            (retest if ps == 2 else first)["human"][pid] = vals
    return dict(first), dict(retest), dict(orders)


rub, rub_retest, rub_orders = load_rubric()
PANEL = [r for r in sorted(rub) if r != "human"]     # the model panel; α over all pages is theirs
HUMAN = "human" if "human" in rub else None
ANCHOR = set(rubric.anchor_ids()) if manifest else set()
uiclip = load("uiclip.json", {})
rated = sorted({p for r in rub for p in rub[r] if p in cell})            # every page any rater rated
panel_rated = sorted({p for r in PANEL for p in rub[r] if p in cell})    # every page the panel rated
two_x_rated = [p for p in panel_rated if cell[p]["arm"] in TWO_X]        # the grammar reading's set


def parts_for(key, page):
    """The items a composite is built from on one page. Brief fit is per brief — each brief states
    its own facts — and the tone item t1, where a brief has one, is on the 7-point scale and is
    reported as an item of its own rather than averaged into the 0–2 mean."""
    if key == "aesthetics":
        return AESTHETIC_KEYS
    if key == "brief fit":
        return [it[0] for it in rubric.items_for(cell[page]["brief"]) if it[0] in rubric.THREE_KEYS]
    return rubric.BINARY_KEYS


def rater_score(vals, key, page):
    """One rater's value for an item or a composite on one page, or None when a part is missing.
    Defects is the count of the five observations; the other composites are means."""
    if key in COMPOSITES:
        parts = [vals.get(k) for k in parts_for(key, page)]
        if not parts or any(x is None for x in parts):
            return None
        return sum(parts) if key == "defects" else st.mean(parts)
    return vals.get(key)


def panel_mean(key, page, raters=None):
    """The page score: the mean over the raters that rated the page (the model panel by default —
    the user rates two briefs and six items, and would tilt those briefs' arms if pooled in)."""
    vs = [rater_score(rub[r][page], key, page) for r in (PANEL if raters is None else raters)
          if page in rub.get(r, {})]
    vs = [v for v in vs if v is not None]
    return st.mean(vs) if vs else None


def units_for(key, pages, raters):
    """{page: {rater: value}} for α, dropping the pages fewer than two of these raters rated."""
    u = {}
    for p in pages:
        vals = {r: rater_score(rub[r][p], key, p) for r in raters if p in rub.get(r, {})}
        vals = {r: v for r, v in vals.items() if v is not None}
        if len(vals) >= 2:
            u[p] = vals
    return u


def metric_for(key):
    """Nominal for the 0/1 defect observations; ordinal for every scale that has an order — the
    7-point items, the 0–2 brief-fit items, and the composites built from them."""
    return "nominal" if key in rubric.BINARY_KEYS else "ordinal"


def alpha_of(units, metric):
    """α over a list of units (a resample may hold the same page twice, so units are re-keyed)."""
    return rel.krippendorff_alpha({n: u for n, u in enumerate(units)}, metric)


def alpha_grouped(groups, metric, min_raters=1):
    """α over one or several groups of units: one group is the plain α, several are the per-group
    αs averaged with each group weighted by the units it contributes. A group fewer than
    `min_raters` raters rated carries no α of its own and drops out."""
    num = den = 0.0; used = 0
    for units in groups:
        if not units or len({r for u in units for r in u}) < min_raters:
            continue
        a = alpha_of(units, metric)
        if a is None:
            continue
        num += a * len(units); den += len(units); used += 1
    return (num / den if den else None), int(den), used


def alpha_ci(groups, metric, min_raters=1, n=1000, seed=0):
    """A percentile interval for α, resampling pages with replacement inside each group — the
    pages are the sample, the raters are the fixed panel."""
    groups = [g for g in groups if g]
    if not groups or sum(len(g) for g in groups) < 3:
        return (None, None)
    rng = random.Random(seed); vals = []
    for _ in range(n):
        boot = [[g[rng.randrange(len(g))] for _ in range(len(g))] for g in groups]
        a, _, _ = alpha_grouped(boot, metric, min_raters)
        if a is not None:
            vals.append(a)
    if len(vals) < n // 2:
        return (None, None)
    vals.sort()
    return (vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))])


def page_sets(key, raters):
    """The three page sets α is read over (spec, Aggregation and reliability): pooled over every
    rated page; the v2.0 and v2.1 pages the grammar reading uses; and per brief, averaged over the
    briefs at least two raters rated — pooled α is inflated by between-brief level differences that
    the within-brief comparison never touches."""
    pooled = [list(units_for(key, panel_rated, raters).values())]
    two_x = [list(units_for(key, two_x_rated, raters).values())]
    per_brief = [list(units_for(key, [p for p in panel_rated if cell[p]["brief"] == b], raters).values())
                 for b in sorted({cell[p]["brief"] for p in panel_rated})]
    return {"pooled": (pooled, 1), "2.x": (two_x, 1), "brief": (per_brief, 2)}


def family_units(key, pages, families=None):
    """{page: {family: the family's mean rating}} — each family counted once, so an α carried by
    one family agreeing with itself is visible as a low between-family α."""
    fams = families or [n for n, _ in FAMILIES]
    u = {}
    for p in pages:
        vals = {}
        for f in fams:
            rs = [r for r in PANEL if family_of(r) == f and p in rub.get(r, {})]
            vs = [rater_score(rub[r][p], key, p) for r in rs]
            vs = [v for v in vs if v is not None]
            if vs:
                vals[f] = st.mean(vs)
        if len(vals) >= 2:
            u[p] = vals
    return u


def _fmt(v, d=2):
    return "—" if v is None else f"{v:.{d}f}"


def _iv(lo, hi, d=2):
    return "" if lo is None else f" [{_fmt(lo, d)}–{_fmt(hi, d)}]"


def _ci(t, n=None, d=2):
    """A mean with its bootstrap interval and the pages it stands on, or an em dash when there was
    nothing to resample."""
    if t[0] is None:
        return "—"
    return f"{_fmt(t[0], d)} [{_fmt(t[1], d)}–{_fmt(t[2], d)}]" + ("" if n is None else f" ({n})")


def paired(lo_arm, hi_arm, keys, pages):
    """Pages of two arms matched by (brief, seed) — the design's own pairing, since a brief and a
    seed fix everything but the skill version. Returns the matched pairs and, per key, the
    per-pair difference hi − lo with the mean difference's bootstrap interval."""
    by = defaultdict(dict)
    for p in pages:
        by[(cell[p]["brief"], cell[p]["seedLabel"])][cell[p]["arm"]] = p
    pairs = [(b, sd, v[lo_arm], v[hi_arm]) for (b, sd), v in sorted(by.items())
             if lo_arm in v and hi_arm in v]
    table = {}
    for key in keys:
        diffs = []
        for b, sd, lo, hi in pairs:
            x, y = panel_mean(key, lo), panel_mean(key, hi)
            diffs.append(None if x is None or y is None else y - x)
        table[key] = (diffs, rel.bootstrap_mean_ci([x for x in diffs if x is not None]))
    return pairs, table


def mdd(diffs):
    """The minimum difference this many pairs could have detected: the 95 % half-width
    1.96·sd/√n. A paired mean under it is "not detectable here", not "none" (spec)."""
    xs = [x for x in diffs if x is not None]
    return None if len(xs) < 2 else 1.96 * st.stdev(xs) / math.sqrt(len(xs))


def excludes_zero(t):
    return t[1] is not None and (t[1] > 0 or t[2] < 0)


# ---------- topology lookup ----------
def topo_index():
    """The instrument's matrices are n×n arrays in the order of its builds list."""
    if not topo:
        return None, {}
    keys = {b["file"].split("/")[-2]: n for n, b in enumerate(topo["builds"])}
    return topo["matrix"], keys

matrix, tkey = topo_index()

def tdist(kind, a, b):
    if not matrix or a not in tkey or b not in tkey:
        return None
    return matrix[kind][tkey[a]][tkey[b]]

def tsig(i):
    if not topo:
        return None
    for b in topo["builds"]:
        if b["file"].split("/")[-2] == i:
            return b
    return None

# ---------- judgments: Bradley–Terry per brief, win rates per arm pair ----------
def tally(judgments):
    """wins[(winner, loser)], appearances and wins per build, arm-pair win counts, and the
    Bradley–Terry log-strengths per brief, for one judge's judgment list."""
    wins = defaultdict(int); appear = defaultdict(int); won = defaultdict(int)
    armpair = defaultdict(lambda: [0, 0])  # (armA, armB) -> [A wins, total], ordered by ARMS index
    for j in judgments:
        w, l = (j["left"], j["right"]) if j["choice"] == "left" else (j["right"], j["left"])
        if w not in cell or l not in cell:
            continue
        wins[(w, l)] += 1; appear[w] += 1; appear[l] += 1; won[w] += 1
        a, b = cell[w]["arm"], cell[l]["arm"]
        if ARMS.index(a) < ARMS.index(b):
            armpair[(a, b)][0] += 1; armpair[(a, b)][1] += 1
        else:
            armpair[(b, a)][1] += 1

    def bradley_terry(ids, iters=200):
        p = {i: 1.0 for i in ids}
        for _ in range(iters):
            new = {}
            for i in ids:
                w = sum(wins[(i, j)] for j in ids if j != i)
                denom = sum((wins[(i, j)] + wins[(j, i)]) / (p[i] + p[j]) for j in ids if j != i)
                new[i] = w / denom if denom > 0 and w > 0 else (0.05 if denom > 0 else p[i])
            s = sum(new.values()) / len(new); p = {k: v / s for k, v in new.items()}
        return {k: math.log(v) for k, v in p.items()}

    bt = {}
    for brief in sorted({c["brief"] for c in manifest}):
        ids = [c["id"] for c in built if c["brief"] == brief and appear[c["id"]] > 0]
        if len(ids) >= 2:
            bt.update(bradley_terry(ids))
    return {"wins": wins, "appear": appear, "won": won, "armpair": armpair, "bt": bt}

H = tally(judg); M = tally(judgm)
wins, appear, won, armpair, bt = H["wins"], H["appear"], H["won"], H["armpair"], H["bt"]

def majority(judge_lists):
    """One synthetic judgment per pair every listed judge decided, the winner by majority; with
    an odd number of judges there is no tie. The human's own tired-day caveat and the
    chance-level human–model agreement are why the tiebreak is a majority of three and not one
    judge overruling another (Decision Log, 2026-09-09)."""
    key = lambda j: frozenset((j["left"], j["right"]))
    win = lambda j: j["left"] if j["choice"] == "left" else j["right"]
    votes = defaultdict(list); first = {}
    for jl in judge_lists:
        for j in jl:
            votes[key(j)].append(win(j)); first.setdefault(key(j), j)
    out = []
    for k, v in votes.items():
        if len(v) < len(judge_lists):
            continue
        w = max(set(v), key=v.count)
        if v.count(w) * 2 <= len(v):
            continue  # an even split: no majority, the pair is left out
        j = first[k]
        out.append({"pair": j["pair"], "left": j["left"], "right": j["right"], "choice": "left" if w == j["left"] else "right",
                    "votes": v.count(w), "of": len(v), "judge": "majority"})
    return out

judgc = majority([j for _, j in JUDGES]) if len(JUDGES) >= 3 else []
C = tally(judgc) if judgc else None

def h2_read(T):
    """H2's two thresholds and the stop rule's quality clause from one judge's arm-pair table:
    v2.1 against v1.1 (≥ 45 %; the clause fires under 35 %) and v2.1 against none (≥ 60 %)."""
    k1, n1 = T["armpair"].get(("v1.1", "v2.1"), [0, 0]); k0, n0 = T["armpair"].get(("none", "v2.1"), [0, 0])
    r1 = (n1 - k1) / n1 if n1 else None; r0 = (n0 - k0) / n0 if n0 else None
    return {"v21_vs_v11": (n1 - k1, n1, r1), "v21_vs_none": (n0 - k0, n0, r0),
            "h2": (r1 is not None and r1 >= 0.45 and r0 is not None and r0 >= 0.60), "stop": (r1 is not None and r1 < 0.35)}

def agreement(a, b):
    """Raw agreement and Cohen's kappa between two judges over the pairs both judged, keyed by
    the unordered pair so a swapped left/right still compares."""
    key = lambda j: frozenset((j["left"], j["right"]))
    win = lambda j: j["left"] if j["choice"] == "left" else j["right"]
    A = {key(j): win(j) for j in a}; B = {key(j): win(j) for j in b}
    both = [k for k in A if k in B]
    if not both:
        return {"n": 0}
    agree = sum(1 for k in both if A[k] == B[k])
    po = agree / len(both)
    # chance agreement: each judge's rate of picking the alphabetically-first id of the pair
    fa = sum(1 for k in both if A[k] == min(k)) / len(both); fb = sum(1 for k in both if B[k] == min(k)) / len(both)
    pe = fa * fb + (1 - fa) * (1 - fb)
    kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    per_brief = defaultdict(lambda: [0, 0])
    for k in both:
        j = next(x for x in a if key(x) == k); per_brief[cell[j["left"]]["brief"]][1] += 1
        if A[k] == B[k]: per_brief[cell[j["left"]]["brief"]][0] += 1
    return {"n": len(both), "agree": agree, "po": po, "kappa": kappa, "per_brief": dict(per_brief)}

def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0, 0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, (c - h) / d, (c + h) / d)

# ---------- validity gate ----------
def valid(i):
    m = meas.get(i, {})
    # The human clause (won at least one of its three pairs) applies only once all three are judged.
    return bool(m.get("gateMechanical")) and (appear[i] < 3 or won[i] >= 1)

def gate_text(i):
    m = meas.get(i, {}); parts = []
    if m.get("errors"): parts.append("js-error")
    if m.get("overflow"): parts.append("overflow")
    if m.get("placeholder"): parts.append("placeholder")
    if m.get("contrast", {}).get("rate") is not None and m["contrast"]["rate"] < 0.9: parts.append(f"contrast {m['contrast']['rate']}")
    if appear[i] >= 3 and won[i] == 0: parts.append("won 0 pairs")
    return ", ".join(parts) or "pass"

# ---------- diversity ----------
def circ_disp(hues):
    if len(hues) < 2:
        return None
    x = sum(math.cos(math.radians(h)) for h in hues) / len(hues); y = sum(math.sin(math.radians(h)) for h in hues) / len(hues)
    return round(1 - math.hypot(x, y), 3)

def fam_set(i):
    f = meas[i].get("families", {}) or {}
    return {v for v in [f.get("display"), f.get("body")] if v}

def jaccard_d(a, b):
    if not a and not b:
        return 0.0
    return 1 - len(a & b) / len(a | b)

def hue_hist(i, bins=36):
    """Hue histogram of chromatic pixels in the full-page screenshot (Design Theater's colour channel, approximated)."""
    try:
        from PIL import Image
    except ImportError:
        return None
    p = os.path.join(WS, "builds", i, "shot-full.png")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGB"); im.thumbnail((360, 3000))
    hist = [0.0] * bins; n = 0
    for r, g, b in im.getdata():
        mx, mn = max(r, g, b), min(r, g, b)
        if mx - mn < 25:
            continue
        # hue in degrees
        d = mx - mn
        if mx == r: h = (60 * ((g - b) / d) + 360) % 360
        elif mx == g: h = 60 * ((b - r) / d) + 120
        else: h = 60 * ((r - g) / d) + 240
        hist[int(h // (360 / bins)) % bins] += 1; n += 1
    if n == 0:
        return [0.0] * bins
    return [v / n for v in hist]

_hh = {}
def emd(a, b, bins=36):
    ha = _hh.setdefault(a, hue_hist(a)); hb = _hh.setdefault(b, hue_hist(b))
    if ha is None or hb is None:
        return None
    # circular 1-D EMD: minimum over rotations of the linear cumulative-difference EMD
    best = None
    for rot in range(bins):
        c = 0.0; s = 0.0
        for k in range(bins):
            c += ha[(k + rot) % bins] - hb[(k + rot) % bins]; s += abs(c)
        best = s if best is None else min(best, s)
    return round(best / bins, 4)

MEASURES = {
    "partition": lambda a, b: tdist("partition", a, b),
    "pqgram": lambda a, b: tdist("pqgram", a, b),
    "raster": lambda a, b: tdist("raster", a, b),
    "hueEMD": emd,
    "familyJaccard": lambda a, b: jaccard_d(fam_set(a), fam_set(b)),
}

def pair_mean(ids, fn, effective):
    vals = []
    for a, b in itertools.combinations(ids, 2):
        d = fn(a, b)
        if d is None:
            continue
        if effective:
            d = d * (1 if valid(a) and valid(b) else 0)
        vals.append(d)
    return (round(sum(vals) / len(vals), 3), len(vals)) if vals else (None, 0)

def arm_ids(arm, category=None, brief=None):
    return [c["id"] for c in built if c["arm"] == arm and (category is None or c["category"] == category) and (brief is None or c["brief"] == brief)]

# ---------- canonical shapes (D4) ----------
def shapes(i):
    s = tsig(i)
    if not s:
        return None
    sg = s["signature"]
    rail = any((not g.get("equal")) and (not g.get("labelFirst")) and g.get("ratios") and len(g["ratios"]) == 2 and max(g["ratios"]) / min(g["ratios"]) >= 1.5 and g["w"] > 900 and (g.get("h") is None or g["h"] >= 360) for g in s.get("grids", []))
    three = any(g["count"] == 3 and g["cols"] == 3 and not g.get("inFooter") and g["kind"] != "table" for g in s.get("groups", []))
    fv = s["firstViewport"][0] if s["firstViewport"] else None
    return {"side": sg["side"] != "none", "rail": rail, "statRow": sg["fvStatRow"], "threeUp": three, "fvCards": sg["fvCardGrid"],
            "heroBand": sg["hero"] in ("band", "text-band") or (sg["hero"] == "full" and fv and fv["role"] in ("heading", "text")),
            "dominant": fv["role"] if fv else None, "dominance": sg["dominance"], "topShare": fv["share"] if fv else None}

# ---------- report ----------
out = []
P = out.append
P("# Settling experiment — results\n")
P(f"Builds measured: {len(built)} of {len(manifest)}. Judgments: " + ", ".join(f"{len(j)} ({n})" for n, j in JUDGES) + f". Topology: {'yes' if topo else 'no'}. Fit ratings: {len(fit)}.\n")

def q_report(title, T, n):
    P(f"## {title}\n")
    P(f"{n} judgments.\n")
    P("| arm A | arm B | A wins | n | rate | 95 % Wilson |\n|---|---|---|---|---|---|")
    for (a, b), (k, m) in sorted(T["armpair"].items(), key=lambda kv: (ARMS.index(kv[0][0]), ARMS.index(kv[0][1]))):
        p, lo, hi = wilson(k, m)
        P(f"| {a} | {b} | {k} | {m} | {p:.2f} | {lo:.2f}–{hi:.2f} |")
    P("")
    P("Pooled Bradley–Terry log-strength per arm (mean over briefs with judgments; 0 = brief average):\n")
    P("| arm | mean log-strength | briefs | builds judged |\n|---|---|---|---|")
    for arm in ARMS:
        per = defaultdict(list)
        for c in built:
            if c["arm"] == arm and c["id"] in T["bt"]:
                per[c["brief"]].append(T["bt"][c["id"]])
        vals = [st.mean(v) for v in per.values()]
        P(f"| {arm} | {st.mean(vals):+.2f} | {len(vals)} | {sum(len(v) for v in per.values())} |" if vals else f"| {arm} | — | 0 | 0 |")
    P("")

q_report("Q — pairwise quality (human, blinded; the primary endpoint)", H, len(judg))
q_report("Q2 — the model judge (astra-medium, blinded; secondary)", M, len(judgm))
if judgb:
    q_report("Q3 — the third judge (claude-opus, blinded; secondary)", tally(judgb), len(judgb))
if C:
    q_report("Q★ — majority of the three judges (the tiebreak adopted 2026-09-09)", C, len(judgc))
    P(f"Unanimous on {sum(1 for j in judgc if j['votes'] == j['of'])} of {len(judgc)} pairs; the human is outvoted on "
      f"{sum(1 for j in judgc if (j['left'] if j['choice'] == 'left' else j['right']) != next((x['left'] if x['choice'] == 'left' else x['right']) for x in judg if frozenset((x['left'], x['right'])) == frozenset((j['left'], j['right']))))}.\n")

P("### H2 and the stop rule's quality clause, per judge\n")
P("| judge | v2.1 over v1.1 | v2.1 over none | H2 (≥ 45 % and ≥ 60 %) | stop clause (< 35 %) |\n|---|---|---|---|---|")
for name, T in [(n, tally(j)) for n, j in JUDGES] + ([("majority", C)] if C else []):
    r = h2_read(T); f = lambda t: f"{t[0]}/{t[1]} ({t[2]:.2f})" if t[2] is not None else "—"
    P(f"| {name} | {f(r['v21_vs_v11'])} | {f(r['v21_vs_none'])} | {'met' if r['h2'] else 'not met'} | {'fires' if r['stop'] else 'does not fire'} |")
P("")

P("### Agreement between the judges\n")
agreements = {}
for (na, ja), (nb, jb) in itertools.combinations(JUDGES, 2):
    ag = agreement(ja, jb); agreements[f"{na}|{nb}"] = ag
    if not ag["n"]:
        P(f"{na} and {nb}: no pair judged by both yet.\n"); continue
    P(f"**{na} and {nb}.** Pairs judged by both: {ag['n']}. Same winner on {ag['agree']} ({ag['po']:.2f}); Cohen's κ {ag['kappa']:.2f}. "
      + "Per brief: " + ", ".join(f"{b} {k}/{n}" for b, (k, n) in sorted(ag["per_brief"].items())) + ".\n")
sa = agreement(judgm1, judgm) if judgm1 else {"n": 0}
if sa["n"]:
    P("### The model judge against itself\n")
    P(f"Its first run (six raters, one per brief, on a schedule that differed per process) overlaps the batch run on {sa['n']} pairs: same winner on {sa['agree']} ({sa['po']:.2f}); Cohen's κ {sa['kappa']:.2f}.\n")

# ---------- R and S: the rubric (spec: 2026-09-09-quality-instrument.md) ----------
# Every table states the raters and pages it stands on: this instrument is read while it is still
# being collected, and α over two raters on one brief is not the number the acceptance floors mean.
rubric_json = {"raters": PANEL, "families": {r: family_of(r) for r in PANEL}, "human": bool(HUMAN),
               "pages": len(rated), "panelPages": len(panel_rated), "twoXPages": len(two_x_rated)}
# A superseded wording's first-pass values (<item>_v1) get their own α row when any rater has them.
SUPERSEDED = [k + "_v1" for k in REVISABLE if any((k + "_v1") in v for r in rub for v in rub[r].values())]
for _k in SUPERSEDED:
    ROW_LABEL[_k] = f"{_k[:-3]} (first wording, superseded by the revision)"
ALPHA_ROWS = ITEM_KEYS + SUPERSEDED + COMPOSITES
SCHEDULE = rate.schedule() if manifest else []


def _ols(points):
    """The slope of y on x with an intercept."""
    if len(points) < 3:
        return None
    mx = st.mean([x for x, _ in points]); my = st.mean([y for _, y in points])
    sxx = sum((x - mx) ** 2 for x, _ in points)
    return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in points) / sxx


def position_slope(key, n=1000, seed=0):
    """Every rating centred by its (rater, brief) mean and regressed on the page's 1-based position
    in that rater's recorded shuffle, pooled over raters and briefs — the presentation-order effect
    a retest on two briefs cannot estimate. The interval resamples the (rater, brief) runs, which
    are the independent units here."""
    groups = []
    for r, per in sorted(rub_orders.items()):
        for br, order in sorted(per.items()):
            pts = [(i + 1, rub[r][pg][key]) for i, pg in enumerate(order)
                   if pg in rub.get(r, {}) and key in rub[r][pg]]
            if len(pts) >= 3:
                m = st.mean([y for _, y in pts])
                groups.append([(x, y - m) for x, y in pts])
    if not groups:
        return (None, None, None, 0)
    slope = _ols([pt for g in groups for pt in g])
    rng = random.Random(seed); vals = []
    for _ in range(n):
        boot = [groups[rng.randrange(len(groups))] for _ in range(len(groups))]
        v = _ols([pt for g in boot for pt in g])
        if v is not None:
            vals.append(v)
    vals.sort()
    lo, hi = (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals))]) if len(vals) > n // 2 else (None, None)
    return (slope, lo, hi, len(groups))


def spearman_ci(xs, ys, n=1000, seed=0):
    """ρ with a percentile interval over resampled pages."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    rho = rel.spearman([x for x, _ in pairs], [y for _, y in pairs])
    if rho is None:
        return (None, None, None, len(pairs))
    rng = random.Random(seed); vals = []
    for _ in range(n):
        s_ = [pairs[rng.randrange(len(pairs))] for _ in range(len(pairs))]
        v = rel.spearman([x for x, _ in s_], [y for _, y in s_])
        if v is not None:
            vals.append(v)
    if len(vals) < n // 2:
        return (rho, None, None, len(pairs))
    vals.sort()
    return (rho, vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals))], len(pairs))


def retest_units(rater):
    """Units for the retest α: one unit per (page, item) over the 7-point items, its two ratings
    being the first and the second pass. Chance-corrected, because a rater choosing at random among
    4, 5 and 6 would pass a within-±1 share of 85 % by arithmetic (spec)."""
    u = {}
    for pg in sorted(rub_retest.get(rater, {})):
        if pg not in rub.get(rater, {}):
            continue
        for k in SEVEN_ITEMS:
            x, y = rub[rater][pg].get(k), rub_retest[rater][pg].get(k)
            if x is not None and y is not None:
                u[(pg, k)] = {"run1": x, "run2": y}
    return u


def implied_choices(rater):
    """A rater's implied forced choice on each of the settling schedule's pairs: the page with the
    higher d1 wins, an equal pair is undecided and drops out."""
    out = []
    for j in SCHEDULE:
        x = rub.get(rater, {}).get(j["left"], {}).get("d1")
        y = rub.get(rater, {}).get(j["right"], {}).get("d1")
        if x is None or y is None or x == y:
            continue
        out.append({"pair": j["pair"], "left": j["left"], "right": j["right"],
                    "choice": "left" if x > y else "right"})
    return out


def prf(pred, truth):
    """Precision and recall of a 0/1 rating against its mechanical ground truth, with the counts —
    a recall with no positive in the truth is undefined and prints as a dash."""
    tp = sum(1 for pg, v in pred.items() if v and truth.get(pg))
    fp = sum(1 for pg, v in pred.items() if v and not truth.get(pg))
    fn = sum(1 for pg, v in pred.items() if not v and truth.get(pg))
    return {"n": len(pred), "tp": tp, "fp": fp, "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "positives": sum(1 for pg in pred if truth.get(pg))}


def r_section():
    """α over three page sets and per family, the user against the panel, retest, position, the
    implied forced choice, the c-items against ground truth, and the acceptance."""
    anchor_raters = [r for r in sorted(rub) if any(pg in ANCHOR for pg in rub[r])]
    anchor_pages = sorted({pg for r in anchor_raters for pg in rub[r] if pg in ANCHOR})
    fam_counts = defaultdict(list)
    for r in PANEL:
        fam_counts[family_of(r)].append(r)
    P(f"Model panel: {len(PANEL)} rater(s) — "
      + "; ".join(f"{f} {', '.join(rs)}" for f, rs in sorted(fam_counts.items()))
      + f" — over {len(panel_rated)} of {len(manifest)} pages, {len(two_x_rated)} of them v2.0 or "
      f"v2.1. Anchor set ({' and '.join(rubric.ANCHOR_BRIEFS)}): {len(anchor_pages)} of "
      f"{len(ANCHOR)} pages rated by {len(anchor_raters)} rater(s)"
      + (", the user among them" if HUMAN else "; the user has not rated yet") + ".\n")
    P("α is Krippendorff's — ordinal on the 7-point items, on the 0–2 brief-fit items and on the "
      "composites built from them, nominal on the 0/1 defect observations — read over three page "
      "sets: pooled over every rated page, over the v2.0 and v2.1 pages the grammar reading uses, "
      "and per brief averaged with each brief weighted by its pages (briefs at least two raters "
      "rated). Pooled α is inflated by between-brief level differences the within-brief comparison "
      "never touches. d1 and the composites carry a 1000-resample interval; a b-item is a different "
      "statement in every brief and its α pools briefs by item index; t1 exists only where the "
      f"brief states a tone; the user rates {', '.join(rubric.HUMAN_KEYS)} only.\n")
    P("| item | metric | α pooled | raters × pages | α on v2.0+v2.1 | raters × pages | "
      "α per brief, weighted | briefs |")
    P("|---|---|---|---|---|---|---|---|")
    alphas = {}
    nr = lambda groups: len({r for g in groups for u in g for r in u})
    for key in ALPHA_ROWS:
        m = metric_for(key); sets_ = page_sets(key, PANEL); row = {}
        for name, (groups, min_raters) in sets_.items():
            val, npages, ngroups = alpha_grouped(groups, m, min_raters)
            lo, hi = alpha_ci(groups, m, min_raters) if key in CI_ROWS else (None, None)
            row[name] = {"alpha": val, "lo": lo, "hi": hi, "pages": npages,
                         "raters": nr(groups), "groups": ngroups}
        alphas[key] = dict(row, metric=m)
        c = lambda n: _fmt(row[n]["alpha"]) + _iv(row[n]["lo"], row[n]["hi"])
        P(f"| {ROW_LABEL.get(key, key)} | {m} | {c('pooled')} | {row['pooled']['raters']} × "
          f"{row['pooled']['pages']} | {c('2.x')} | {row['2.x']['raters']} × {row['2.x']['pages']} | "
          f"{c('brief')} | {row['brief']['groups']} |")
    P("")

    P("### The family split\n")
    P("α within each model family and between the two family means, each family counted once, so a "
      "pass carried by one family agreeing with itself shows as a low between-family α. The "
      "7-point items and the composites; the between column is ordinal over the family means.\n")
    P("| item | GPT α | Claude α | between families α | pages (pooled / v2.0+v2.1) |\n|---|---|---|---|---|")
    fams = {}
    for key in SEVEN_ITEMS + COMPOSITES:
        m = metric_for(key); row = {}
        for name, pages in (("pooled", panel_rated), ("2.x", two_x_rated)):
            for f, _pfx in FAMILIES:
                rs = [r for r in PANEL if family_of(r) == f]
                u = units_for(key, pages, rs)
                row[f"{f}|{name}"] = {"alpha": rel.krippendorff_alpha(u, m), "pages": len(u)}
            u = family_units(key, pages)
            row[f"between|{name}"] = {"alpha": rel.krippendorff_alpha(u, "ordinal"), "pages": len(u)}
        fams[key] = row
        g = lambda f: f"{_fmt(row[f + '|pooled']['alpha'])} / {_fmt(row[f + '|2.x']['alpha'])}"
        P(f"| {ROW_LABEL.get(key, key)} | {g('GPT')} | {g('Claude')} | {g('between')} | "
          f"{row['between|pooled']['pages']} / {row['between|2.x']['pages']} |")
    P("(each cell is pooled / v2.0+v2.1.)\n")

    # α charges a rater who sits higher or lower on the scale than the others as much as one who
    # orders the pages differently, and the first pass showed one lenient rater. Two readings that
    # tell the two apart, reported and not gating: each rater's mean level, and the mean pairwise
    # Spearman ρ between raters within a brief — order only — split by same-family and
    # cross-family pairs.
    P("### Level or order\n")
    P("α penalises a rater who uses the scale higher or lower than the others as much as one who "
      "orders the pages differently. Two readings that separate the two, reported and not gating: "
      "each rater's mean level over the pages the panel rated, and the mean pairwise Spearman ρ "
      "between raters within a brief (order only, level removed), for pairs from the same family "
      "and pairs across families.\n")
    lo_keys = ["d1", "e1", "aesthetics", "defects", "brief fit"]
    P("| rater | " + " | ".join(ROW_LABEL.get(k, k) for k in lo_keys) + " |\n|---|" + "---|" * len(lo_keys))
    for r in PANEL:
        cells_ = []
        for k in lo_keys:
            xs = [rater_score(rub[r][q], k, q) for q in panel_rated if q in rub[r]]
            xs = [x for x in xs if x is not None]
            cells_.append(f"{st.mean(xs):.2f}" if xs else "—")
        P(f"| {r} | " + " | ".join(cells_) + " |")
    P("")
    P("| item | within-brief ρ, same family | within-brief ρ, across families | pairs × briefs (same / across) |\n|---|---|---|---|")
    lo_briefs = sorted({cell[q]["brief"] for q in panel_rated})
    level_order = {}
    for k in lo_keys:
        same, cross = [], []
        for a, b in itertools.combinations(PANEL, 2):
            for brief in lo_briefs:
                qs = [q for q in panel_rated if cell[q]["brief"] == brief and q in rub.get(a, {}) and q in rub.get(b, {})]
                prs = [(rater_score(rub[a][q], k, q), rater_score(rub[b][q], k, q)) for q in qs]
                prs = [(x, y) for x, y in prs if x is not None and y is not None]
                if len(prs) < 4:
                    continue
                try:
                    rho = rel.spearman([x for x, _ in prs], [y for _, y in prs])
                except Exception:
                    rho = None
                if rho is None or rho != rho:
                    continue
                (same if family_of(a) == family_of(b) else cross).append(rho)
        level_order[k] = {"same": st.mean(same) if same else None, "across": st.mean(cross) if cross else None, "n": [len(same), len(cross)]}
        P(f"| {ROW_LABEL.get(k, k)} | {_fmt(level_order[k]['same'])} | {_fmt(level_order[k]['across'])} | {len(same)} / {len(cross)} |")
    P("")
    rubric_json["levelOrder"] = level_order

    P("### The user against the panel, over the anchor pages\n")
    human_panel = {}
    if not HUMAN:
        P("The user has not rated yet.\n")
    else:
        pages = [pg for pg in anchor_pages if pg in rub[HUMAN] and any(pg in rub.get(r, {}) for r in PANEL)]
        P(f"{len(pages)} anchor page(s) rated by both the user and at least one of the {len(PANEL)} "
          "model rater(s); ρ is over those pages with a 1000-resample interval, the panel side "
          "being the panel mean.\n")
        P("| item | pages | Spearman ρ | mean abs. difference |\n|---|---|---|---|")
        for key in ALPHA_ROWS:
            both = [(rater_score(rub[HUMAN][pg], key, pg), panel_mean(key, pg)) for pg in pages]
            both = [(x, y) for x, y in both if x is not None and y is not None]
            rho, lo, hi, n = spearman_ci([x for x, _ in both], [y for _, y in both])
            mad = st.mean([abs(x - y) for x, y in both]) if both else None
            human_panel[key] = {"rho": rho, "lo": lo, "hi": hi, "mad": mad, "pages": n}
            P(f"| {ROW_LABEL.get(key, key)} | {n} | {_fmt(rho)}{_iv(lo, hi)} | {_fmt(mad)} |")
        P("")

    P("### Retest — the same rater on the same pages a second time\n")
    retest = {}
    if not rub_retest:
        P("No retest data yet.\n")
    else:
        P("α between the first and the second rating, units = (page, item) over the 7-point items. "
          "Chance-corrected, because a rater drawing at random among 4, 5 and 6 passes a within-±1 "
          "share of 85 % by arithmetic; the share is printed beside α, not in place of it. The "
          "user's second pass is reported the same way and is outside the gate.\n")
        P("| rater | pages repeated | 7-point ratings | retest α | within ±1 | c-item ratings | equal |")
        P("|---|---|---|---|---|---|---|")
        for r in sorted(rub_retest):
            pages = [pg for pg in sorted(rub_retest[r]) if pg in rub.get(r, {})]
            pull = lambda keys: [(rub[r][pg][k], rub_retest[r][pg][k]) for pg in pages for k in keys
                                 if k in rub[r][pg] and k in rub_retest[r][pg]]
            seven, binary = pull(SEVEN_ITEMS), pull(rubric.BINARY_KEYS)
            u = retest_units(r)
            al = rel.krippendorff_alpha(u, "ordinal")
            w, e = rel.within_one(seven), rel.exact_agreement(binary)
            retest[r] = {"pages": len(pages), "seven": len(seven), "alpha": al, "withinOne": w,
                         "binary": len(binary), "equal": e, "isUser": r == "human"}
            P(f"| {r}{' (the user)' if r == 'human' else ''} | {len(pages)} | {len(seven)} | "
              f"{_fmt(al)} | {_fmt(w)} | {len(binary)} | {_fmt(e)} |")
        P("")

    P("### Position in the shuffle\n")
    P("Each rating centred by its (rater, brief) mean and regressed on the page's 1-based position "
      "in that rater's recorded order, pooled over raters and briefs; the interval resamples the "
      "runs. A slope of 0.1 means a page seen one place later is rated a tenth of a point higher.\n")
    pos = {}
    if not rub_orders:
        P("No recorded page orders yet.\n")
    else:
        P("| item | slope per position | 95 % CI | runs |\n|---|---|---|---|")
        for key in ALPHA_ROWS:
            if key in COMPOSITES:
                continue
            sl, lo, hi, ng = position_slope(key)
            pos[key] = {"slope": sl, "lo": lo, "hi": hi, "runs": ng}
            P(f"| {key} | {_fmt(sl, 3)} | {('—' if lo is None else f'{_fmt(lo, 3)}–{_fmt(hi, 3)}')} | {ng} |")
        P("")

    P("### Against the forced choice\n")
    forced = {}
    refs = [(n, j) for n, j in (("the user", judg), ("astra-medium forced", judgm),
                                ("claude-opus forced", judgb)) if j]
    if not SCHEDULE or not refs or not PANEL:
        P("No forced-choice judgments or no schedule to compare against yet.\n")
    else:
        P(f"Each rater's implied verdict on the settling run's {len(SCHEDULE)} pairs, taken from its "
          "d1 (higher wins, an equal pair undecided), against the forced choices actually recorded. "
          "κ is Cohen's over the pairs both sides decided. A rater whose d1 contradicts its own "
          "earlier forced choice says pointwise and pairwise elicit different things.\n")
        P("| rater | pairs decided | " + " | ".join(f"κ vs {n} (n)" for n, _ in refs) + " |")
        P("|---|---|" + "---|" * len(refs))
        for r in PANEL:
            mine = implied_choices(r); row = []
            forced[r] = {"decided": len(mine)}
            for n, ref in refs:
                ag = agreement(mine, ref)
                forced[r][n] = {"kappa": ag.get("kappa"), "n": ag["n"], "po": ag.get("po")}
                row.append("—" if not ag["n"] else f"{_fmt(ag['kappa'])} ({ag['n']})")
            P(f"| {r} | {len(mine)} of {len(SCHEDULE)} | " + " | ".join(row) + " |")
        P("")

    P("### The c-items against their mechanical ground truth\n")
    truth5 = {pg: bool(meas.get(pg, {}).get("overflowCapture")) for pg in panel_rated}
    truth3 = {pg: bool(meas.get(pg, {}).get("placeholder")) for pg in panel_rated}
    ground = {}
    if not panel_rated:
        P("No rated pages yet.\n")
    else:
        P("c5 (wider than the viewport) against `overflowCapture` and c3 (empty or placeholder "
          "region) against the gate's `placeholder`, over the rated pages. The panel row is the "
          "strict majority of the raters that rated the page. A dash is a rate with no case in its "
          "denominator — with two over-wide pages in 52, recall is read from very few positives — "
          "and the mechanical truth is narrower than the item it is held against: `placeholder` "
          "matches template text, not every empty region a rater can see, so a false positive here "
          "is as likely to be the gate missing something as the rater inventing it.\n")
        P("| rating | rater | pages | truth positives | tp | fp | fn | precision | recall |")
        P("|---|---|---|---|---|---|---|---|---|")
        for key, truth, label in (("c5", truth5, "c5 vs overflowCapture"), ("c3", truth3, "c3 vs placeholder")):
            rows = [(r, {pg: bool(rub[r][pg].get(key)) for pg in panel_rated
                         if pg in rub.get(r, {}) and key in rub[r][pg]}) for r in PANEL]
            maj = {}
            for pg in panel_rated:
                vs = [rub[r][pg][key] for r in PANEL if pg in rub.get(r, {}) and key in rub[r][pg]]
                if vs:
                    maj[pg] = sum(vs) * 2 > len(vs)
            for r, pred in rows + [("panel majority", maj)]:
                if not pred:
                    continue
                v = prf(pred, truth); ground[f"{key}|{r}"] = v
                P(f"| {label} | {r} | {v['n']} | {v['positives']} | {v['tp']} | {v['fp']} | {v['fn']} | "
                  f"{_fmt(v['precision'])} | {_fmt(v['recall'])} |")
        P("")

    P("### Acceptance of the instrument, declared before the run\n")
    verdict = lambda ok: "**met**" if ok else "not met"
    d1 = alphas["d1"]
    a_2x, a_pool = d1["2.x"], d1["pooled"]
    fam_d1 = fams.get("d1", {}).get("between|2.x", {"alpha": None, "pages": 0})
    rho = human_panel.get("d1", {})
    model_retest = {r: v for r, v in retest.items() if not v["isUser"]}
    worst = min([v["alpha"] for v in model_retest.values() if v["alpha"] is not None], default=None)
    ok = lambda v, floor: v is not None and v >= floor
    acc = {
        "alphaD1TwoX": {"floor": 0.67, "value": a_2x["alpha"], "lo": a_2x["lo"], "hi": a_2x["hi"],
                        "raters": a_2x["raters"], "pages": a_2x["pages"],
                        "pooled": a_pool["alpha"], "met": ok(a_2x["alpha"], 0.67)},
        "alphaFamilyD1": {"floor": 0.5, "value": fam_d1["alpha"], "pages": fam_d1["pages"],
                          "met": ok(fam_d1["alpha"], 0.5)},
        "rhoD1": {"floor": 0.6, "value": rho.get("rho"), "lo": rho.get("lo"), "hi": rho.get("hi"),
                  "pages": rho.get("pages", 0), "met": ok(rho.get("rho"), 0.6)},
        "retestAlpha": {"floor": 0.67, "value": worst, "raters": len(model_retest),
                        "met": worst is not None and worst >= 0.67
                               and all(v["alpha"] is not None for v in model_retest.values())},
    }
    P(f"- α ≥ 0.67 on d1 across the model panel over the {a_2x['pages']} v2.0 and v2.1 page(s): "
      f"{verdict(acc['alphaD1TwoX']['met'])} — α {_fmt(a_2x['alpha'])}{_iv(a_2x['lo'], a_2x['hi'])} "
      f"over {a_2x['raters']} rater(s) (the spec asks for 4 × 26; pooled over "
      f"{a_pool['pages']} pages it is {_fmt(a_pool['alpha'])}, which does not gate).")
    P(f"- α ≥ 0.5 on d1 between the two family means over the same pages: "
      f"{verdict(acc['alphaFamilyD1']['met'])} — α {_fmt(fam_d1['alpha'])} over "
      f"{fam_d1['pages']} page(s).")
    P(f"- Spearman ρ ≥ 0.6 between the user and the panel mean on d1: {verdict(acc['rhoD1']['met'])} "
      f"— ρ {_fmt(rho.get('rho'))}{_iv(rho.get('lo'), rho.get('hi'))} over {rho.get('pages', 0)} "
      "anchor page(s) (the spec asks for 16; the interval is printed, the point estimate gates).")
    P(f"- retest α ≥ 0.67 on the 7-point items for every model rater: "
      f"{verdict(acc['retestAlpha']['met'])} — "
      + (f"lowest of {len(model_retest)} rater(s) {_fmt(worst)}: "
         + ", ".join(f"{r} {_fmt(v['alpha'])}" for r, v in sorted(model_retest.items()))
         if model_retest else "no model-rater retest data") + ".")
    P("")
    if a_2x["alpha"] is None:
        outcome, why = "not yet readable", "The endpoint's α over the v2.0 and v2.1 pages has no value yet"
    elif all(v["met"] for v in acc.values()):
        outcome, why = "Accepted", "All four lines hold; the grammar reading runs as confirmatory"
    elif a_2x["alpha"] < 0.4:
        outcome, why = ("Stopped", "The endpoint's α over the v2.0 and v2.1 pages is under 0.4 — the "
                        "rubric is not better than the forced choice on the endpoint at this level of craft")
    else:
        outcome, why = ("Partial", "The items that clear α are usable readings; d1 is not, quality "
                        "claims about the endpoint stay unclaimable, and the grammar reading runs "
                        "as exploratory and is labelled so")
    pending = [n for n, v in acc.items() if v["value"] is None]
    P(f"**Outcome: {outcome}.** {why}. "
      + (f"Provisional: {', '.join(pending)} has no data yet, so no reading here can be Accepted "
         "until it lands. " if pending else "")
      + "The spec's Stopped is declared *after* the one permitted wording revision; whether that "
      "revision has been spent is a judgement the reader makes, not a fact in these files.\n")
    low = [k for k in REVISABLE if alphas[k]["2.x"]["alpha"] is not None and alphas[k]["2.x"]["alpha"] < 0.4]
    P("Items that could trip the one pre-registered wording revision (only "
      + ", ".join(REVISABLE) + " qualify; the b-, t- and c-items are reported only): "
      + (", ".join(f"{k} α {_fmt(alphas[k]['2.x']['alpha'])}" for k in low) if low
         else "none under α 0.4 on the v2.0 and v2.1 pages") + ".\n")
    rubric_json.update({"alpha": alphas, "families": fams, "humanPanel": human_panel,
                        "retest": retest, "position": pos, "forcedChoice": forced,
                        "cItemTruth": ground, "acceptance": acc, "outcome": outcome})


def s_section():
    by_arm = defaultdict(list)
    for pg in panel_rated:
        by_arm[cell[pg]["arm"]].append(pg)
    P(f"Page scores are the panel mean over the {len(PANEL)} model rater(s) — the user's anchor "
      "ratings are not pooled in, since they cover two briefs and six items and would tilt those "
      f"briefs' arms. {len(panel_rated)} page(s) rated of {len(manifest)}. Each cell is the mean "
      "over the arm's rated pages with a 2000-resample bootstrap 95 % interval and, in parentheses, "
      "the pages it stands on — fewer than the arm's total for an item only some briefs carry.\n")
    P("| score | " + " | ".join(f"{a} ({len(by_arm[a])} pages)" for a in ARMS) + " |")
    P("|---|" + "---|" * len(ARMS))
    arms_json = {a: {} for a in ARMS}
    for key in ROWS:
        cells_out = []
        for a in ARMS:
            vals = [v for v in (panel_mean(key, pg) for pg in by_arm[a]) if v is not None]
            t = rel.bootstrap_mean_ci(vals)
            arms_json[a][key] = {"mean": t[0], "lo": t[1], "hi": t[2], "pages": len(vals)}
            cells_out.append(_ci(t, len(vals)))
        P(f"| {ROW_LABEL.get(key, key)} | " + " | ".join(cells_out) + " |")
    P("")

    P("### d1 per brief and arm\n")
    P("Panel mean deliverability, pages in parentheses.\n")
    P("| brief | " + " | ".join(ARMS) + " |\n|---|" + "---|" * len(ARMS))
    briefs_json = {}
    for br in sorted({cell[pg]["brief"] for pg in panel_rated}):
        row = []
        for a in ARMS:
            vals = [v for v in (panel_mean("d1", pg) for pg in by_arm[a] if cell[pg]["brief"] == br)
                    if v is not None]
            briefs_json.setdefault(br, {})[a] = {"d1": st.mean(vals) if vals else None, "pages": len(vals)}
            row.append(f"{_fmt(st.mean(vals))} ({len(vals)})" if vals else "—")
        P(f"| {br} | " + " | ".join(row) + " |")
    P("")

    def signs(pairs):
        """Per rater, the sign of its own d1 difference on each pair, and how many raters share the
        sign of the panel's mean difference — a panel-mean difference cannot hide rater
        disagreement (spec)."""
        per = {}
        for r in PANEL:
            per[r] = []
            for br, sd, lo, hi in pairs:
                x, y = rub.get(r, {}).get(lo, {}).get("d1"), rub.get(r, {}).get(hi, {}).get("d1")
                per[r].append(None if x is None or y is None else (0 if y == x else (1 if y > x else -1)))
        return per

    def diff_table(lo_arm, hi_arm, keys, with_signs=False):
        """The paired difference table: one column per (brief, seed) both arms were built and rated
        on, then the mean difference over those pairs with its bootstrap interval."""
        pairs, table = paired(lo_arm, hi_arm, keys, panel_rated)
        if not pairs:
            P(f"No (brief, seed) has both {lo_arm} and {hi_arm} rated yet.\n")
            return {}, pairs, table
        P(f"{len(pairs)} pair(s), {len(PANEL)} model rater(s) a side. A positive difference favours "
          f"{hi_arm}; a dash is a pair where one side lacks the item.\n")
        head = [f"{br}·{sd}" for br, sd, _, _ in pairs]
        P("| score | " + " | ".join(head) + " | pairs | mean | 95 % CI |")
        P("|---|" + "---|" * (len(head) + 3))
        for key in keys:
            diffs, (m, lo, hi) = table[key]
            n = len([x for x in diffs if x is not None])
            P(f"| {ROW_LABEL.get(key, key)} | " + " | ".join(_fmt(x) for x in diffs) + f" | {n} | "
              + f"{_fmt(m)} | " + ("—" if m is None else f"{_fmt(lo)}–{_fmt(hi)}") + " |")
        P("")
        out = {k: {"pairs": {f"{br}·{sd}": x for (br, sd, _, _), x in zip(pairs, table[k][0])},
                   "mean": table[k][1][0], "lo": table[k][1][1], "hi": table[k][1][2]} for k in keys}
        if with_signs:
            per = signs(pairs)
            mean_sign = 0 if table["d1"][1][0] is None else (1 if table["d1"][1][0] > 0 else -1)
            agree = [sum(1 for r in PANEL if per[r][i] == mean_sign) for i in range(len(pairs))]
            P("Per rater, the sign of its own d1 difference on each pair (+ favours "
              f"{hi_arm}, · a tie, blank not rated), and how many raters carry the sign of the "
              "panel's mean difference.\n")
            P("| rater | " + " | ".join(head) + " |\n|---|" + "---|" * len(head))
            sym = {1: "+", -1: "−", 0: "·", None: ""}
            for r in PANEL:
                P(f"| {r} | " + " | ".join(sym[v] for v in per[r]) + " |")
            P("| raters on the mean's sign | " + " | ".join(str(x) for x in agree) + " |")
            P("")
            out["_signs"] = {r: per[r] for r in PANEL}
            out["_signAgreement"] = agree
        return out, pairs, table

    P("### v2.1 − v2.0, paired by brief and seed\n")
    P("The grammar reading's input (spec, The grammar reading). Paired by brief and seed label — in "
      "effect by brief, since the two arms' samplers drew different seeds and the two seeds of one "
      "arm are often near-duplicates, so the effective number of pairs is under thirteen.\n")
    paired_json, pairs21, table21 = diff_table("v2.0", "v2.1", ROWS, with_signs=True)
    if pairs21:
        diffs, (m, lo, hi) = table21["d1"]
        n = len([x for x in diffs if x is not None])
        half = mdd(diffs)
        agree = paired_json.get("_signAgreement", [])
        maj = sum(1 for x in agree if x >= 3) * 2 > len(agree) if agree else False
        confirmed = excludes_zero((m, lo, hi)) and maj
        P("**The confirmation gate.** " + (
            f"Difference confirmed: the paired d1 mean {_fmt(m)} [{_fmt(lo)}–{_fmt(hi)}] excludes "
            f"zero and at least three raters carry its sign on {sum(1 for x in agree if x >= 3)} of "
            f"{len(agree)} pairs, a majority. The grammar reading runs as confirmatory."
            if confirmed else
            f"No difference detectable at {n} pairs: the paired d1 mean is {_fmt(m)} "
            f"[{_fmt(lo)}–{_fmt(hi)}]"
            + ("" if excludes_zero((m, lo, hi)) else " and its interval covers zero")
            + (f"; three or more raters carry its sign on only {sum(1 for x in agree if x >= 3)} of "
               f"{len(agree)} pairs" if agree and not maj else "")
            + ". Steps 1–4 of the grammar reading run as exploratory and are labelled so.")
          + f" The minimum difference {n} pairs could have detected is "
          f"{_fmt(half)} of a point (1.96·sd/√n).\n")
        paired_json["_gate"] = {"confirmed": confirmed, "mean": m, "lo": lo, "hi": hi, "pairs": n,
                                "mdd": half, "signMajority": maj}

    P("### The no-skill hold\n")
    P("The settling run's hold (Decision Log 2026-09-09): `none` should not beat `v1.1`. The hold "
      "stands unless `none`'s paired d1 difference against `v1.1` is positive with its interval "
      "excluding zero; it is confirmed if the difference is negative with its interval excluding "
      "zero; between, it is not decided at this sample.\n")
    for key in ("d1", "defects"):
        cells_out = []
        for a in ("none", "v1.1"):
            vals = [v for v in (panel_mean(key, pg) for pg in by_arm[a]) if v is not None]
            cells_out.append(f"{a} {_ci(rel.bootstrap_mean_ci(vals))} over {len(vals)} page(s)")
        P(f"- {ROW_LABEL.get(key, key)}: " + "; ".join(cells_out) + ".")
    P("")
    hold_json, hold_pairs, hold_table = diff_table("v1.1", "none", ["d1", "defects"])
    if hold_pairs:
        m, lo, hi = hold_table["d1"][1]
        if excludes_zero((m, lo, hi)) and m > 0:
            hold = "does not stand"; why = "`none` beats `v1.1` on d1 with the interval excluding zero"
        elif excludes_zero((m, lo, hi)) and m < 0:
            hold = "is confirmed"; why = "`v1.1` beats `none` on d1 with the interval excluding zero"
        else:
            hold = "is not decided at this sample"; why = "the interval covers zero"
        P(f"**The hold {hold}**: none − v1.1 on d1 is {_fmt(m)} [{_fmt(lo)}–{_fmt(hi)}] over "
          f"{len(hold_pairs)} pair(s) — {why}. The minimum difference detectable here is "
          f"{_fmt(mdd(hold_table['d1'][0]))} of a point.\n")
        hold_json["_verdict"] = {"hold": hold, "mean": m, "lo": lo, "hi": hi,
                                 "pairs": len(hold_pairs), "mdd": mdd(hold_table["d1"][0])}

    uiclip_json = {}
    if uiclip:
        P("### UIClip\n")
        pages = [pg for pg in panel_rated if pg in uiclip]
        P(f"UIClip scored {len([pg for pg in uiclip if pg in cell])} page(s); the correlations are "
          f"over the {len(pages)} of them the panel has rated. It is a reported column, never in α.\n")
        P("| UIClip capture | ρ with d1 | ρ with aesthetics | pages |\n|---|---|---|---|")
        for side in ("fv", "full"):
            xs = [uiclip[pg].get(side) for pg in pages]
            rhos = {k: rel.spearman(xs, [panel_mean(k, pg) for pg in pages]) for k in ("d1", "aesthetics")}
            uiclip_json[side] = {"rhoD1": rhos["d1"], "rhoAesthetics": rhos["aesthetics"], "pages": len(pages)}
            P(f"| {side} | {_fmt(rhos['d1'])} | {_fmt(rhos['aesthetics'])} | {len(pages)} |")
        P("")
        P("| arm | UIClip fv | UIClip full | pages |\n|---|---|---|---|")
        for a in ARMS:
            ids = [pg for pg in uiclip if pg in cell and cell[pg]["arm"] == a]
            mfn = lambda side: st.mean([uiclip[pg][side] for pg in ids]) if ids else None
            uiclip_json.setdefault("arms", {})[a] = {"fv": mfn("fv"), "full": mfn("full"), "pages": len(ids)}
            P(f"| {a} | {_fmt(mfn('fv'), 3)} | {_fmt(mfn('full'), 3)} | {len(ids)} |")
        P("")

    rubric_json.update({"arms": arms_json, "briefs": briefs_json, "pairedV21V20": paired_json,
                        "noSkillHold": hold_json, "uiclip": uiclip_json})


P("## R — reliability of the rubric\n")
if not rated:
    P("No rubric data yet: no `rubric/<rater>/<brief>.json` and no `rubric-human.jsonl` under the "
      "workspace. This section and the rubric scores appear as soon as one rater's file lands, and "
      "state the raters and pages they stand on.\n")
    P("## S — rubric scores per arm\n")
    P("No rubric data yet.\n")
else:
    r_section()
    P("## S — rubric scores per arm\n")
    s_section()

P("## V — validity gate per build\n")
P("| id | brief | arm | seed | mechanical | judged | gate |\n|---|---|---|---|---|---|---|")
for c in sorted(built, key=lambda c: (c["wave"], c["brief"], ARMS.index(c["arm"]), c["seedLabel"])):
    m = meas[c["id"]]
    P(f"| {c['id']} | {c['brief']} | {c['arm']} | {c['seedLabel']} | {'pass' if m.get('gateMechanical') else 'fail'} | {won[c['id']]}/{appear[c['id']]} | {gate_text(c['id'])} |")
P("")

P("## D — diversity per arm (mean pairwise; effective = Shypula pairwise form with the gate)\n")
for scope, label in [("across", "across briefs within category"), ("within", "within brief across seeds")]:
    P(f"### {label}\n")
    P("| arm | category | pairs | " + " | ".join(f"{m} raw / eff" for m in MEASURES) + " |")
    P("|---|---|---|" + "---|" * len(MEASURES))
    for arm in ARMS:
        for category in ["console", "narrative"]:
            ids = arm_ids(arm, category)
            if scope == "across":
                # pairs from different briefs only
                fn_wrap = lambda fn: (lambda a, b: fn(a, b) if cell[a]["brief"] != cell[b]["brief"] else None)
            else:
                fn_wrap = lambda fn: (lambda a, b: fn(a, b) if cell[a]["brief"] == cell[b]["brief"] else None)
            cells_out = []; npairs = 0
            for name, fn in MEASURES.items():
                raw, n = pair_mean(ids, fn_wrap(fn), False); eff, _ = pair_mean(ids, fn_wrap(fn), True)
                npairs = max(npairs, n)
                cells_out.append(f"{raw if raw is not None else '—'} / {eff if eff is not None else '—'}")
            if npairs:
                P(f"| {arm} | {category} | {npairs} | " + " | ".join(cells_out) + " |")
    P("")

P("### D2 — accent hue dispersion and ground, per arm\n")
P("| arm | builds | accent hues | dispersion (1 − R̄) | eff. dispersion | grounds (L, hue) | dark grounds |\n|---|---|---|---|---|---|---|")
for arm in ARMS:
    ids = arm_ids(arm)
    hues = [meas[i]["accent"]["H"] for i in ids if meas[i].get("accent")]
    ehues = [meas[i]["accent"]["H"] for i in ids if meas[i].get("accent") and valid(i)]
    grounds = [f"{meas[i]['ground']['L']}/{meas[i]['ground']['H']:.0f}" for i in ids if meas[i].get("ground")]
    dark = sum(1 for i in ids if meas[i].get("ground") and meas[i]["ground"]["L"] < 0.5)
    P(f"| {arm} | {len(ids)} | {', '.join(f'{h:.0f}' for h in hues)} | {circ_disp(hues) if circ_disp(hues) is not None else '—'} | {circ_disp(ehues) if circ_disp(ehues) is not None else '—'} | {' '.join(grounds)} | {dark} |")
P("")

def accent_job(i):
    """The accent's declared job. 2.x builds name it in DESIGN.md (directional, status-only or none);
    for the other arms it is inferred from where the extractor found the accent — a chromatic
    colour on an interactive element is a directional accent, a fallback read from any element
    means the interactive layer is achromatic and the read is a status colour."""
    if cell[i]["arm"] in ("v2.0", "v2.1"):
        dp = os.path.join(WS, "builds", i, "DESIGN.md")
        if os.path.exists(dp):
            mm = re.search(r"accent job[^\n]*?\b(directional|status-only|none)\b", open(dp).read(), re.I)
            if mm:
                return mm.group(1).lower()
    where = (meas[i].get("accent") or {}).get("where")
    return "directional" if where in ("bg", "fg", "border") else "none"

P("### D2 supplement — accent job, and dispersion over directional accents only\n")
P("Added after wave five (Decision Log): on a build whose interactive layer is achromatic the "
  "extractor's fallback reads the loudest status colour, so the D2 hue list above mixes chosen "
  "accents with critical reds. Here the job is the declared one for the 2.x arms and inferred "
  "from the extractor's locus for the others.\n")
P("| arm | builds | directional | status-only | none | hues (directional) | dispersion | eff. dispersion |\n|---|---|---|---|---|---|---|---|")
for arm in ARMS:
    ids = arm_ids(arm)
    jobs = {i: accent_job(i) for i in ids}
    d = [i for i in ids if jobs[i] == "directional" and meas[i].get("accent")]
    hues = [meas[i]["accent"]["H"] for i in d]
    ehues = [meas[i]["accent"]["H"] for i in d if valid(i)]
    c = lambda k: sum(1 for j in jobs.values() if j == k)
    P(f"| {arm} | {len(ids)} | {c('directional')} | {c('status-only')} | {c('none')} | {', '.join(f'{h:.0f}' for h in hues)} | {circ_disp(hues) if circ_disp(hues) is not None else '—'} | {circ_disp(ehues) if circ_disp(ehues) is not None else '—'} |")
P("")

P("### D3 — families per arm\n")
P("| arm | display families (distinct / builds) | body families | mono |\n|---|---|---|---|")
for arm in ARMS:
    ids = arm_ids(arm)
    f = lambda k: [meas[i]["families"].get(k) for i in ids if meas[i].get("families")]
    d, b, m = f("display"), f("body"), f("mono")
    fmt = lambda xs: f"{len(set(x for x in xs if x))}/{len(xs)}: " + ", ".join(sorted(set(x for x in xs if x)))
    P(f"| {arm} | {fmt(d)} | {fmt(b)} | {fmt(m)} |")
P("")

P("### D4 — canonical shapes per arm and category\n")
P("| arm | category | n | side region | rail band ≥1.5:1 | stat row (fv) | three-up | cards (fv) | headline band | dominant share ≥ 0.4 |\n|---|---|---|---|---|---|---|---|---|---|")
for arm in ARMS:
    for category in ["console", "narrative", "pair"]:
        ids = [i for i in arm_ids(arm, category) if shapes(i)]
        if not ids:
            continue
        sh = [shapes(i) for i in ids]
        cnt = lambda k: sum(1 for s in sh if s[k])
        dom = sum(1 for s in sh if s["topShare"] is not None and s["topShare"] >= 0.4)
        P(f"| {arm} | {category} | {len(ids)} | {cnt('side')} | {cnt('rail')} | {cnt('statRow')} | {cnt('threeUp')} | {cnt('fvCards')} | {cnt('heroBand')} | {dom} |")
P("")

P("## Per-build reads\n")
P("| id | brief | arm | seed | ground | accent | hues | display / body / mono | dominant | dominance | side | stat | 3-up | height | BT |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for c in sorted(built, key=lambda c: (c["brief"], ARMS.index(c["arm"]), c["seedLabel"])):
    m = meas[c["id"]]; s = shapes(c["id"]) or {}
    fam = m.get("families", {}) or {}
    acc = m.get("accent") or {}
    P(f"| {c['id']} | {c['brief']} | {c['arm']} | {c['seedLabel']} | {m.get('ground', {}).get('hex', '—')} L{m.get('ground', {}).get('L', '')} | {acc.get('hex', '—')} h{acc.get('H', '')} | {m.get('hueCount', '')} | {fam.get('display')} / {fam.get('body')} / {fam.get('mono')} | {s.get('dominant', '—')} {s.get('topShare', '')} | {s.get('dominance', '—')} | {'y' if s.get('side') else ('band' if s.get('rail') else '')} | {'y' if s.get('statRow') else ''} | {'y' if s.get('threeUp') else ''} | {round((m.get('docHeight') or 0) / 900, 1)}vh | {('%+.2f' % bt[c['id']]) if c['id'] in bt else '—'} |")
P("")

if fit:
    P("## F — structural fit (blinded rater, secondary)\n")
    P("| arm | builds | mean yes of 5 |\n|---|---|---|")
    for arm in ARMS:
        vals = [sum(fit[i]["answers"].values()) for i in arm_ids(arm) if i in fit]
        P(f"| {arm} | {len(vals)} | {st.mean(vals):.2f} |" if vals else f"| {arm} | 0 | — |")
    P("")

# the pair (P)
pair_ids = {(c["arm"]): c["id"] for c in built if c["brief"] == "compare"}
fleet_ids = {(c["arm"], c["seedLabel"]): c["id"] for c in built if c["brief"] == "fleet"}
if pair_ids and fleet_ids:
    P("## P — fleet against compare, per arm (all four distances)\n")
    P("| arm | fleet seed | partition | raster | pqgram | sig | compare dominant | fleet dominant |\n|---|---|---|---|---|---|---|---|")
    for arm in ARMS:
        if arm not in pair_ids:
            continue
        for (a, sd), fid in sorted(fleet_ids.items()):
            if a != arm:
                continue
            cid = pair_ids[arm]
            P(f"| {arm} | {sd} | {tdist('partition', fid, cid)} | {tdist('raster', fid, cid)} | {tdist('pqgram', fid, cid)} | {tdist('sig', fid, cid)} | {(shapes(cid) or {}).get('dominant')} | {(shapes(fid) or {}).get('dominant')} |")
    P("")

res = "\n".join(out)
outp = os.path.join(WS, "results.md")
if "--out" in sys.argv:
    outp = sys.argv[sys.argv.index("--out") + 1]
open(outp, "w").write(res)
_j = lambda T: {"bt": T["bt"], "armpair": {f"{a}|{b}": v for (a, b), v in T["armpair"].items()}, "h2": h2_read(T)}
json.dump({"bt": bt, "armpair": {f"{a}|{b}": v for (a, b), v in armpair.items()}, "valid": {c["id"]: valid(c["id"]) for c in built},
           "judges": {n: _j(tally(j)) for n, j in JUDGES}, "majority": (_j(C) if C else None), "agreement": agreements,
           "shapes": {c["id"]: shapes(c["id"]) for c in built}, "rubric": rubric_json},
          open(os.path.join(WS, "results.json"), "w"), indent=1)
print(res)
