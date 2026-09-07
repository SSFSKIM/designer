#!/usr/bin/env python3
"""Settling experiment analysis (spec: 2026-09-05-settling-experiment.md).

    python3 analyze.py [--out results.md]

Reads manifest.json, measurements.json, topology.json, judgments.jsonl and fit.json (optional)
from figma-design-workspace/settling/ and writes results.md + results.json there. Handles partial
data: every table states how many builds and judgments it stands on.
"""
import json, re, os, sys, math, itertools, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
WS = os.environ.get("SETTLING_WS") or os.path.join(REPO, "figma-design-workspace/settling")
ARMS = ["none", "v1.1", "v2.0", "v2.1"]


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

judgm = load_dir("judgments-model")        # the second judge (a blinded model rater), one file per brief
judgm1 = load_dir("judgments-model-run1")  # its first run, fanned out per brief on a pre-fix schedule
fit = {}
_fitdir = os.path.join(WS, "fit")
if os.path.isdir(_fitdir):
    for _f in sorted(os.listdir(_fitdir)):
        if _f.endswith(".json"):
            fit.update(json.load(open(os.path.join(_fitdir, _f))))
cell = {c["id"]: c for c in manifest}
built = [c for c in manifest if c["id"] in meas and not meas[c["id"]].get("error")]

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
P(f"Builds measured: {len(built)} of {len(manifest)}. Judgments: {len(judg)} (human), {len(judgm)} (model). Topology: {'yes' if topo else 'no'}. Fit ratings: {len(fit)}.\n")

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
ag = agreement(judg, judgm)
P("### Agreement between the judges\n")
if ag["n"]:
    P(f"Pairs judged by both: {ag['n']}. Same winner on {ag['agree']} ({ag['po']:.2f}); Cohen's κ {ag['kappa']:.2f}.\n")
    P("| brief | agree | n |\n|---|---|---|")
    for b, (k, n) in sorted(ag["per_brief"].items()):
        P(f"| {b} | {k} | {n} |")
    P("")
else:
    P("No pair judged by both yet.\n")
sa = agreement(judgm1, judgm) if judgm1 else {"n": 0}
if sa["n"]:
    P("### The model judge against itself\n")
    P(f"Its first run (six raters, one per brief, on a schedule that differed per process) overlaps the batch run on {sa['n']} pairs: same winner on {sa['agree']} ({sa['po']:.2f}); Cohen's κ {sa['kappa']:.2f}.\n")

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
json.dump({"bt": bt, "armpair": {f"{a}|{b}": v for (a, b), v in armpair.items()}, "valid": {c["id"]: valid(c["id"]) for c in built},
           "shapes": {c["id"]: shapes(c["id"]) for c in built}}, open(os.path.join(WS, "results.json"), "w"), indent=1)
print(res)
