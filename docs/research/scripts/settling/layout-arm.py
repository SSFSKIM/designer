#!/usr/bin/env python3
"""The layout-arm run's analysis (spec: 2026-10-12-routing-ledger-and-layout-arm.md, part C).

    SETTLING_WS=…/layout-arm SETTLING_BASELINE_WS=…/settling python3 layout-arm.py [--out results.md]

Reads the run's own workspace (manifest, measurements, fit/, rubric/, each build's DESIGN.md,
ledger.jsonl and ledger-report.txt) beside the settling workspace as the baseline, and
`topology-all.json` in the run's workspace — layout-topology.mjs run once over both workspaces'
builds so the pairwise matrices cover old and new pages together. Writes results.md and
results.json. Every table states how many builds it stands on; partial data is reported as partial.

The headline is fit (the blinded structural rater's yes-of-five, read with the baseline's pages in
the same frame). Partition and pq-gram are reported and do not gate (the settling retrospective).
The rubric's d1 is exploratory at this sample and is labelled so.
"""
import json, os, re, sys, math, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
WS = os.environ.get("SETTLING_WS") or os.path.join(REPO, "figma-design-workspace/layout-arm")
BASE = os.environ.get("SETTLING_BASELINE_WS") or os.path.join(REPO, "figma-design-workspace/settling")
sys.path.insert(0, HERE)
import reliability as rel

BASE_ARMS = ["none", "v1.1", "v2.0", "v2.1"]
NEW_ARMS = []          # filled from the run's manifest
FIT_DROP = 0.3         # C1 and C3's bar, yes-of-five
ACCENT_BAND = 30


def jload(p, default):
    if not os.path.exists(p):
        return default
    return json.load(open(p))


def jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []


# ---------- the two workspaces ----------
new_cells = jload(os.path.join(WS, "manifest.json"), {"cells": []})["cells"]
base_cells = jload(os.path.join(BASE, "manifest.json"), {"cells": []})["cells"]
for c in new_cells:
    c["ws"] = WS
    if c["arm"] not in NEW_ARMS:
        NEW_ARMS.append(c["arm"])
for c in base_cells:
    c["ws"] = BASE
cells = {c["id"]: c for c in new_cells + base_cells}
ARMS = BASE_ARMS + NEW_ARMS
meas = {}
meas.update(jload(os.path.join(BASE, "measurements.json"), {"builds": {}})["builds"])
meas.update(jload(os.path.join(WS, "measurements.json"), {"builds": {}})["builds"])
built = [c for c in cells.values() if c["id"] in meas and not meas[c["id"]].get("error")]
topo = jload(os.path.join(WS, "topology-all.json"), None)
tkey = {b["file"].split("/")[-2]: n for n, b in enumerate(topo["builds"])} if topo else {}
tby = {b["file"].split("/")[-2]: b for b in topo["builds"]} if topo else {}

# Fit: the run's fit files rate old and new pages in one frame (cells.mjs fitprompt with the
# baseline); the settling run's own fit files are the baseline's earlier reading, reported beside.
fit_new, fit_old = {}, {}
for d, target in ((os.path.join(WS, "fit"), fit_new), (os.path.join(BASE, "fit"), fit_old)):
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith(".json"):
                target.update(json.load(open(os.path.join(d, f))))


def fit_score(i, table):
    r = table.get(i)
    return sum(int(v) for v in r["answers"].values()) if r else None


def build_dir(i):
    return os.path.join(cells[i]["ws"], "builds", i)


def design(i):
    p = os.path.join(build_dir(i), "DESIGN.md")
    return open(p, encoding="utf8").read() if os.path.exists(p) else ""


def arm_ids(arm, category=None, brief=None):
    return [c["id"] for c in built if c["arm"] == arm and (category is None or c["category"] == category) and (brief is None or c["brief"] == brief)]


def fmt(v, d=2):
    return "—" if v is None else (f"{v:.{d}f}" if isinstance(v, float) else str(v))


def ci(values, d=2):
    vals = [v for v in values if v is not None]
    if not vals:
        return "—"
    if len(vals) == 1:
        return f"{vals[0]:.{d}f} (1)"
    m, lo, hi = rel.bootstrap_mean_ci(vals)
    return f"{m:.{d}f} [{lo:.{d}f}–{hi:.{d}f}] ({len(vals)})"


# ---------- V: the gate (mechanical only; this run has no pairwise human clause) ----------
def gate_text(i):
    m = meas.get(i, {}); parts = []
    if m.get("errors"): parts.append("js-error")
    if m.get("overflow") or m.get("overflowCapture"): parts.append("overflow" + (" (capture)" if m.get("overflowCapture") and not m.get("overflow") else ""))
    if m.get("placeholder"): parts.append("placeholder")
    if m.get("contrast", {}).get("rate") is not None and m["contrast"]["rate"] < 0.9: parts.append(f"contrast {m['contrast']['rate']}")
    return ", ".join(parts) or "pass"


def valid(i):
    m = meas.get(i, {})
    return bool(m.get("gateMechanical")) and not m.get("overflowCapture")


# ---------- the record ----------
AXES = ["density", "criticality", "energy", "type", "material( model)?", "colou?r commitment", "accent job", "ground lightness", "ground temperature"]
LINES = ["posture", "dominant activity|activity", "unit and relation|relation", "co-visibility|covisibility", "temporal", "volume( and homogeneity)?"]


def record_read(i):
    md = design(i)
    if not md:
        return {"lines": 0, "axes": 0, "clines": 0, "rejectedVector": False, "candidates": False, "sampler": False, "signature": False}
    low = md.lower()
    return {
        "lines": md.count("\n") + 1,
        "axes": sum(1 for a in AXES if re.search(r"\b(" + a + r")\b\s*[:—\-*]", low)),
        "clines": sum(1 for l in LINES if re.search(r"\b(" + l + r")\b\s*[:—\-*]", low)),
        "rejectedVector": bool(re.search(r"rejected (coordinate )?vector", low)),
        "candidates": bool(re.search(r"\bcandidates?\b", low) and re.search(r"\bchosen\b|\brejected\b|only one candidate", low)),
        "sampler": bool(re.search(r"sampler|ingredient|seed \d{4}", low)),
        "signature": bool(re.search(r"signature element", low)),
        "accentJob": (re.search(r"accent job[^\n]{0,60}?\b(none|status-only|directional|atmospheric)\b", low) or [None, None])[1],
        "ledgerNamed": bool(re.search(r"build ledger|ledger (raised|show|flag|report|run|found|listed|had|put|name|neighbour|neighbor)|ledger[:,]? the nearest|in the ledger|nearest (same-form |prior )?build", low)),
    }


def ledger_read(i):
    d = build_dir(i)
    seed = jsonl(os.path.join(d, "ledger.jsonl"))
    rep = os.path.join(d, "ledger-report.txt")
    text = open(rep, encoding="utf8").read() if os.path.exists(rep) else ""
    reports = text.count("build ledger —")
    flags = re.findall(r"↳ (accent|ground|family|signature|form): ([^\n]+)", text)
    recorded = [e for e in seed if e.get("source") == "record"]
    fams = set()
    for k, v in flags:
        if k == "family" and (m := re.match(r"(.+?) is already", v)):
            fams.add(m.group(1).strip().lower())
    return {"seeded": len([e for e in seed if e.get("source") != "record"]), "recorded": len(recorded), "reports": reports,
            "flags": len(flags), "flagKinds": sorted({k for k, _ in flags}), "flaggedFamilies": sorted(fams),
            "flaggedHues": sorted({int(m) for k, v in flags if k == "accent" for m in re.findall(r"'s (\d+)°", v)}),
            "entry": recorded[-1] if recorded else None}


def hue_d(a, b):
    d = abs((a - b) % 360)
    return 360 - d if d > 180 else d


# ---------- D: diversity over the combined topology ----------
def tdist(kind, a, b):
    if not topo or a not in tkey or b not in tkey:
        return None
    return topo["matrix"][kind][tkey[a]][tkey[b]]


def circ_disp(hues):
    if len(hues) < 2:
        return None
    x = sum(math.cos(math.radians(h)) for h in hues) / len(hues); y = sum(math.sin(math.radians(h)) for h in hues) / len(hues)
    return round(1 - math.hypot(x, y), 3)


def pair_mean(ids, fn, effective):
    vals = []
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            v = fn(ids[a], ids[b])
            if v is None:
                continue
            vals.append(v * (1 if not effective else (valid(ids[a]) and valid(ids[b]))))
    return round(sum(vals) / len(vals), 3) if vals else None


def shapes(i):
    s = tby.get(i)
    if not s:
        return None
    sg = s["signature"]
    rail = any((not g.get("equal")) and (not g.get("labelFirst")) and g.get("ratios") and len(g["ratios"]) == 2 and max(g["ratios"]) / min(g["ratios"]) >= 1.5 and g["w"] > 900 and (g.get("h") is None or g["h"] >= 360) for g in s.get("grids", []))
    three = any(g["count"] == 3 and g["cols"] == 3 and not g.get("inFooter") and g["kind"] != "table" for g in s.get("groups", []))
    fv = s["firstViewport"][0] if s["firstViewport"] else None
    return {"side": sg["side"] != "none", "rail": rail, "statRow": sg["fvStatRow"], "threeUp": three, "fvCards": sg["fvCardGrid"],
            "heroBand": sg["hero"] in ("band", "text-band") or (sg["hero"] == "full" and fv and fv["role"] in ("heading", "text")),
            "dominant": fv["role"] if fv else None, "topShare": fv["share"] if fv else None}


# ---------- the rubric, read from the run's own rubric/ (old and new pages in one frame) ----------
def load_rubric(ws):
    out = defaultdict(dict)   # rater -> page -> {item: value}
    d = os.path.join(ws, "rubric")
    if not os.path.isdir(d):
        return out
    for rater in sorted(os.listdir(d)):
        rd = os.path.join(d, rater)
        if not os.path.isdir(rd):
            continue
        for f in sorted(os.listdir(rd)):
            if not f.endswith(".json") or "-retest" in f or "-revised" in f:
                continue
            doc = json.load(open(os.path.join(rd, f)))
            for pid, vals in doc.get("pages", {}).items():
                out[rater][pid] = {k: v for k, v in vals.items() if k != "evidence"}
    return out


rub = load_rubric(WS)


def page_score(key, page, rater):
    v = rub.get(rater, {}).get(page)
    if not v:
        return None
    try:
        if key == "aesthetics":
            return sum(float(v[k]) for k in ("a1", "a2", "a3", "a4"))
        if key == "brief fit":
            ks = [k for k in v if re.fullmatch(r"b\d", k)]
            return sum(float(v[k]) for k in ks) / len(ks) if ks else None
        if key == "defects":
            return sum(float(v[k]) for k in v if re.fullmatch(r"c\d", k))
        return float(v[key]) if key in v else None
    except (TypeError, ValueError, KeyError):
        return None


def panel_mean(key, page):
    vals = [s for r in rub for s in [page_score(key, page, r)] if s is not None]
    return sum(vals) / len(vals) if vals else None


# ---------- report ----------
out = []
P = out.append
new_built = [c for c in built if c["ws"] == WS]
P("# Layout-arm run — results\n")
P(f"New arms: {', '.join(NEW_ARMS) or 'none yet'}. New builds measured: {len(new_built)} of {len(new_cells)}. Baseline builds: {len([c for c in built if c['ws'] == BASE])} of {len(base_cells)}. Combined topology: {'yes, ' + str(len(tkey)) + ' pages' if topo else 'no'}. Fit (this run's frame): {len(fit_new)} pages. Rubric raters in this run: {len(rub)}.\n")

# V
P("## V — the gate per new build\n")
P("| id | brief | arm | seed | gate | DESIGN.md |\n|---|---|---|---|---|---|")
for c in sorted(new_built, key=lambda c: (ARMS.index(c["arm"]), c["brief"], c["seedLabel"])):
    P(f"| {c['id']} | {c['brief']} | {c['arm']} | {c['seedLabel']} | {gate_text(c['id'])} | {'yes' if meas[c['id']].get('hasDesign') else 'no'} |")
P("")
P("| arm | built | mechanical pass | contrast fails | overflow (load / capture) |\n|---|---|---|---|---|")
for arm in ARMS:
    ids = arm_ids(arm)
    if not ids:
        continue
    P(f"| {arm} | {len(ids)} | {sum(1 for i in ids if valid(i))} | {sum(1 for i in ids if (meas[i].get('contrast') or {}).get('rate') is not None and meas[i]['contrast']['rate'] < 0.9)} | {sum(1 for i in ids if meas[i].get('overflow'))} / {sum(1 for i in ids if meas[i].get('overflowCapture'))} |")
P("")

# Record discipline
P("## R — the record, per new build\n")
P("Nine axis lines and six composition lines are counted by label; the rest are presence reads of the record's own words. A record that names the ledger is one whose derivation cites a neighbour.\n")
P("| id | brief | arm | lines | §0 axes /9 | §4 lines /6 | rejected vector | candidates | sampler | signature | accent job | names the ledger |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
rec = {}
for c in sorted(new_built, key=lambda c: (ARMS.index(c["arm"]), c["brief"], c["seedLabel"])):
    r = record_read(c["id"]); rec[c["id"]] = r
    P(f"| {c['id']} | {c['brief']} | {c['arm']} | {r['lines']} | {r['axes']} | {r['clines']} | {'y' if r['rejectedVector'] else '-'} | {'y' if r['candidates'] else '-'} | {'y' if r['sampler'] else '-'} | {'y' if r['signature'] else '-'} | {r.get('accentJob') or '—'} | {'y' if r.get('ledgerNamed') else '-'} |")
P("")
for arm in NEW_ARMS:
    ids = arm_ids(arm)
    if ids:
        P(f"- {arm}: records {sum(1 for i in ids if rec[i]['lines'])} of {len(ids)}; mean lines {st.mean(rec[i]['lines'] for i in ids):.0f}; all nine axes on {sum(1 for i in ids if rec[i]['axes'] >= 9)}; all six lines on {sum(1 for i in ids if rec[i]['clines'] >= 6)}; candidates recorded on {sum(1 for i in ids if rec[i]['candidates'])}; sampler recorded on {sum(1 for i in ids if rec[i]['sampler'])}.")
P("")

# The ledger reading
ledger_arms = [a for a in NEW_ARMS if any(os.path.exists(os.path.join(WS, "builds", c["id"], "ledger.jsonl")) for c in new_cells if c["arm"] == a)]
if ledger_arms:
    P("## L — the ledger reading\n")
    P("Per build: the seeded entries the agent could see, whether it ran `nearest` (reports saved) and `record` (an entry appended), the flags it was shown, and whether what it shipped sits inside a band it was shown — the display family it was told was already used, or an accent within 30° of a flagged hue. A build that saw a flag and shipped inside the band is not a fault by itself; the record column R says whether it named the neighbour.\n")
    P("| id | brief | arm | seeded | nearest runs | flags shown (kinds) | recorded | shipped display | shipped accent | inside a shown band |\n|---|---|---|---|---|---|---|---|---|---|")
    L = {}
    for c in sorted(new_built, key=lambda c: (c["brief"], c["seedLabel"])):
        if c["arm"] not in ledger_arms:
            continue
        l = ledger_read(c["id"]); L[c["id"]] = l
        m = meas[c["id"]]
        disp = (m.get("families") or {}).get("display")
        job = rec.get(c["id"], {}).get("accentJob")
        hue = None if job in ("none", "status-only") else (m.get("accent") or {}).get("H")
        inside = []
        if disp and disp.lower() in l["flaggedFamilies"]:
            inside.append(f"family {disp}")
        if hue is not None and any(hue_d(hue, h) <= ACCENT_BAND for h in l["flaggedHues"]):
            inside.append(f"accent {round(hue)}°")
        l["inside"] = inside
        P(f"| {c['id']} | {c['brief']} | {c['arm']} | {l['seeded']} | {l['reports']} | {l['flags']} ({', '.join(l['flagKinds']) or '—'}) | {l['recorded']} | {disp or '—'} | {('none' if job in ('none', 'status-only') else (str(round(hue)) + '° ' + (job or '')) if hue is not None else '—')} | {', '.join(inside) or '—'} |")
    P("")
    for arm in ledger_arms:
        ids = [i for i in arm_ids(arm) if i in L]
        if ids:
            P(f"- {arm}: ran `nearest` on {sum(1 for i in ids if L[i]['reports'])} of {len(ids)}, appended a record on {sum(1 for i in ids if L[i]['recorded'])}, shipped inside a shown band on {sum(1 for i in ids if L[i]['inside'])}, of which {sum(1 for i in ids if L[i]['inside'] and rec[i].get('ledgerNamed'))} name the neighbour in the record.")
    # the stamp-card test: signature words shared between the two seeds of one brief, per arm
    P("")
    P("**Signature motifs across seeds** (the stamp-card test): content words of five letters or more shared by the two seeds' signature lines, per brief and arm; the settling run's derivation arms shared the stamp on the library brief and the ticket on the hardware brief.\n")
    P("| brief | arm | seed A signature | seed B signature | shared words |\n|---|---|---|---|---|")
    sigre = re.compile(r"signature element[*_ .:—-]*([^\n]+)", re.I)
    def sig_of(i):
        m = sigre.search(design(i)); s = re.sub(r"[*_`]", "", m.group(1)).strip() if m else ""
        return s[:110] + ("…" if len(s) > 110 else "")
    def words(s):
        return {w for w in re.sub(r"[^a-z\s-]", " ", s.lower()).split() if len(w) >= 5 and w not in ("signature", "element", "region", "single", "every", "their", "which", "where", "first", "there")}
    for brief in sorted({c["brief"] for c in new_built}):
        for arm in ["v2.0", "v2.1"] + NEW_ARMS:
            a = arm_ids(arm, brief=brief)
            ids_a = [i for i in a if cells[i]["seedLabel"] == "A"]; ids_b = [i for i in a if cells[i]["seedLabel"] == "B"]
            if not ids_a or not ids_b:
                continue
            sa, sb = sig_of(ids_a[0]), sig_of(ids_b[0])
            shared = sorted(words(sa) & words(sb))
            P(f"| {brief} | {arm} | {sa or '—'} | {sb or '—'} | {', '.join(shared) or '—'} |")
    P("")

# Fit
P("## F — fit, the headline\n")
if fit_new:
    P("The blinded structural rater's five yes/no questions per category, this run's reading: one rater per brief saw the baseline's eight pages and the new arms' pages in one frame. Mean yes-of-five per arm with a bootstrap interval; then the new arms paired with `v2.1` and `v2.0` by brief and seed.\n")
    P("| arm | mean yes-of-five (this frame) | pages | settling run's own reading |\n|---|---|---|---|")
    for arm in ARMS:
        ids = [i for i in arm_ids(arm) if i in fit_new]
        old = [fit_score(i, fit_old) for i in arm_ids(arm) if i in fit_old]
        if ids or old:
            P(f"| {arm} | {ci([fit_score(i, fit_new) for i in ids])} | {len(ids)} | {ci(old)} |")
    P("")
    P("Per brief (this frame):\n")
    P("| brief | " + " | ".join(ARMS) + " |\n|---|" + "---|" * len(ARMS))
    for brief in sorted({c["brief"] for c in built}):
        row = []
        for arm in ARMS:
            ids = [i for i in arm_ids(arm, brief=brief) if i in fit_new]
            row.append(", ".join(str(fit_score(i, fit_new)) for i in sorted(ids, key=lambda i: cells[i]["seedLabel"])) or "—")
        P(f"| {brief} | " + " | ".join(row) + " |")
    P("")
    for arm in NEW_ARMS:
        for ref in ("v2.1", "v2.0"):
            diffs = []
            for c in new_built:
                if c["arm"] != arm or c["id"] not in fit_new:
                    continue
                mates = [i for i in arm_ids(ref, brief=c["brief"]) if cells[i]["seedLabel"] == c["seedLabel"] and i in fit_new]
                a, b = fit_score(c["id"], fit_new), (fit_score(mates[0], fit_new) if mates else None)
                if a is not None and b is not None:
                    diffs.append(a - b)
            if diffs:
                m, lo, hi = rel.bootstrap_mean_ci(diffs) if len(diffs) > 1 else (float(diffs[0]), float(diffs[0]), float(diffs[0]))
                verdict = "inside the ±0.3 bar" if abs(m) <= FIT_DROP else ("a rise over the bar" if m > 0 else "**a drop over the bar**")
                P(f"- **{arm} − {ref}**, paired by brief and seed: {m:+.2f} [{lo:+.2f}, {hi:+.2f}] over {len(diffs)} pairs — {verdict}. Pairs: {', '.join(f'{d:+d}' for d in diffs)}.")
    P("")
else:
    P("No fit ratings in this run yet (`cells.mjs fitprompt <brief>` with SETTLING_BASELINE_WS set).\n")

# D4
if topo:
    P("## D4 — canonical shapes per arm and category (combined topology)\n")
    P("| arm | category | n | side region | rail band ≥1.5:1 | stat row (fv) | three-up | cards (fv) | headline band | dominant share ≥ 0.4 |\n|---|---|---|---|---|---|---|---|---|---|")
    for arm in ARMS:
        for cat in ("console", "narrative", "pair"):
            S = [s for s in (shapes(i) for i in arm_ids(arm, cat)) if s]
            if not S:
                continue
            P(f"| {arm} | {cat} | {len(S)} | {sum(s['side'] for s in S)} | {sum(s['rail'] for s in S)} | {sum(bool(s['statRow']) for s in S)} | {sum(s['threeUp'] for s in S)} | {sum(bool(s['fvCards']) for s in S)} | {sum(bool(s['heroBand']) for s in S)} | {sum(1 for s in S if (s['topShare'] or 0) >= 0.4)} |")
    P("")
    P("## D1 — layout distance per arm (reported, not gating)\n")
    P("Raw / effective (both builds pass the mechanical gate). Across briefs within category, then within brief across seeds.\n")
    for title, grouper in (("across briefs within category", lambda arm, cat: [arm_ids(arm, cat)]),
                           ("within brief across seeds", lambda arm, cat: [arm_ids(arm, cat, b) for b in sorted({c["brief"] for c in built if c["category"] == cat})])):
        P(f"### {title}\n")
        P("| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff |\n|---|---|---|---|---|---|")
        for arm in ARMS:
            for cat in ("console", "narrative"):
                groups = [g for g in grouper(arm, cat) if len(g) >= 2]
                if not groups:
                    continue
                row = []; npairs = 0
                for kind in ("partition", "pqgram", "raster"):
                    raws, effs = [], []
                    for g in groups:
                        r = pair_mean(g, lambda a, b: tdist(kind, a, b), False); e = pair_mean(g, lambda a, b: tdist(kind, a, b), True)
                        if r is not None:
                            raws.append(r); effs.append(e)
                    row.append(f"{fmt(st.mean(raws), 3) if raws else '—'} / {fmt(st.mean(effs), 3) if effs else '—'}")
                npairs = sum(len(g) * (len(g) - 1) // 2 for g in groups)
                P(f"| {arm} | {cat} | {npairs} | " + " | ".join(row) + " |")
        P("")

# D2 / D3
P("## D2 — accent hue dispersion per arm\n")
P("Max-chroma accent as measured, and by declared job (2.x arms, from the record; `none` and status-only excluded) where a record exists.\n")
P("| arm | builds | measured hues | dispersion | directional (by job) | hues | dispersion | status-only / none | dark grounds |\n|---|---|---|---|---|---|---|---|---|")
for arm in ARMS:
    ids = arm_ids(arm)
    if not ids:
        continue
    hues = [round(meas[i]["accent"]["H"]) for i in ids if meas[i].get("accent")]
    jobs = {i: (rec.get(i) or record_read(i)).get("accentJob") for i in ids}
    dir_ids = [i for i in ids if jobs[i] in ("directional", "atmospheric") and meas[i].get("accent")]
    dh = [round(meas[i]["accent"]["H"]) for i in dir_ids]
    P(f"| {arm} | {len(ids)} | {', '.join(map(str, hues))} | {fmt(circ_disp(hues), 3)} | {len(dir_ids)} | {', '.join(map(str, dh)) or '—'} | {fmt(circ_disp(dh), 3)} | {sum(1 for i in ids if jobs[i] in ('status-only', 'none'))} | {sum(1 for i in ids if meas[i].get('ground', {}).get('L', 1) < 0.5)} |")
P("")
P("## D3 — families per arm\n")
P("| arm | display families (distinct / builds) | body families | mono |\n|---|---|---|---|")
for arm in ARMS:
    ids = arm_ids(arm)
    if not ids:
        continue
    def fams(k):
        vals = [(meas[i].get("families") or {}).get(k) for i in ids]
        vals = [v for v in vals if v and v != "None"]
        return f"{len(set(vals))}/{len(ids)}: " + ", ".join(sorted(set(vals)))
    P(f"| {arm} | {fams('display')} | {fams('body')} | {fams('mono')} |")
P("")

# Rubric
if rub:
    P("## S — the rubric in this run's frame (exploratory for d1)\n")
    P(f"{len(rub)} rater(s): {', '.join(sorted(rub))}. Each rated a brief's baseline pages and new pages together; the baseline's earlier ratings are not pooled in. Panel mean per arm with a bootstrap interval over pages; then the new arms paired with `v2.1` and `v2.0` by brief and seed.\n")
    keys = ["d1", "brief fit", "e1", "aesthetics", "defects"]
    P("| score | " + " | ".join(ARMS) + " |\n|---|" + "---|" * len(ARMS))
    for key in keys:
        row = []
        for arm in ARMS:
            vals = [panel_mean(key, i) for i in arm_ids(arm)]
            row.append(ci(vals))
        P(f"| {key} | " + " | ".join(row) + " |")
    P("")
    for arm in NEW_ARMS:
        for ref in ("v2.1", "v2.0"):
            for key in keys:
                diffs = []
                for c in new_built:
                    if c["arm"] != arm:
                        continue
                    mates = [i for i in arm_ids(ref, brief=c["brief"]) if cells[i]["seedLabel"] == c["seedLabel"]]
                    a, b = panel_mean(key, c["id"]), panel_mean(key, mates[0]) if mates else None
                    if a is not None and b is not None:
                        diffs.append(a - b)
                if len(diffs) >= 2:
                    m, lo, hi = rel.bootstrap_mean_ci(diffs)
                    P(f"- {arm} − {ref} on {key}: {m:+.2f} [{lo:+.2f}, {hi:+.2f}] over {len(diffs)} pairs{' — the interval excludes zero' if lo > 0 or hi < 0 else ''}.")
    P("")
    # α over the frame per key, pooled
    P("α (Krippendorff, ordinal) across this run's raters over every page they rated:\n")
    P("| score | α | raters × pages |\n|---|---|---|")
    for key in keys:
        pages = sorted({p for r in rub for p in rub[r]})
        units = {p: {r: page_score(key, p, r) for r in rub if page_score(key, p, r) is not None} for p in pages}
        units = {p: v for p, v in units.items() if len(v) >= 2}
        if units:
            a = rel.krippendorff_alpha(units, "ordinal")
            P(f"| {key} | {fmt(a)} | {len(rub)} × {len(units)} |")
    P("")

text = "\n".join(out)
outp = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(WS, "results.md")
open(outp, "w").write(text)
json.dump({"newArms": NEW_ARMS, "newBuilt": [c["id"] for c in new_built], "record": rec}, open(os.path.join(WS, "results.json"), "w"), indent=1)
print(text)
