#!/usr/bin/env python3
"""The rule reading's report (spec: docs/doperpowers/specs/2026-09-10-liquid-glass-into-the-
skill.md, "C. The audit").

    python3 glass-rules-analyze.py [--out results.md]

Reads every `rules/<rater>/<slug>.json` the panel wrote under the wave's data directory and the
`audit.json` `glass-audit.mjs` left beside each demo, and writes the verdict as markdown to stdout
and to `docs/research/data/2026-09-10-liquid-glass-demos/results.md`:

  - the panel majority per rule per demo — a tie is a failure, because the pass line asks that a
    rule be held, not that it fail to be disproved — the count held of 25, and whether any rule
    tagged `[layer]` or `[material]` failed;
  - the mechanical read from `audit.json`, and the pass verdict per the spec's line;
  - Krippendorff's α per rule across the raters over the demos, nominal, because a rule is a 0/1
    observation and 0 against 1 is one disagreement whichever way round it falls;
  - the quality items — the panel's a1–a4, d1 and e1 per demo — and the d1 mean over the demos
    against the spec's 5.0.

The instrument is read while it is still being collected, so every table says what it stands on: a
majority over two raters is not the majority the pass line means, and α over three demos is not the
α a panel's reliability could be claimed from. Standard library only, and the statistics come from
the settling instrument's `reliability.py` rather than from a second implementation of them.
"""
import os, sys, json, importlib.util, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "settling"))
import reliability as rel               # krippendorff_alpha, checked against published values


def _load(name, path):
    """Import a sibling script whose file name carries a hyphen and is therefore not importable."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gr = _load("glass_rules", os.path.join(HERE, "glass-rules.py"))   # the items, the slugs, the paths

RULE_KEYS = [k for k, *_ in gr.RULES]
RULE_TAG = {k: t for k, t, _, _ in gr.RULES}
FATAL = set(gr.FATAL_TAGS)
FATAL_KEYS = [k for k in RULE_KEYS if RULE_TAG[k] in FATAL]
AESTHETIC = ["a1", "a2", "a3", "a4"]
HOLD_FLOOR = 22                          # of 25, the spec's line
MAX_FAILED = 25 - HOLD_FLOOR             # the same line as "at most three of the rules read failed"
D1_FLOOR = 5.0                           # the panel's d1 mean over the six, the initiative's clause
RULES_DIR = os.path.join(gr.DATA, "rules")

# Three rules a static capture cannot show, and the prompt tells the panel that a rule it cannot see
# holding does not hold — so every rater scored them 0 on every page, and the four-rater panel's
# first two readings said so in as many words (2026-09-10). Left in the count they would make the
# spec's "22 of 25" mean "every rule the captures can show", which is not the line the spec drew.
# The mechanical audit exists to read what captures cannot, and it measures two of the three:
#   r18 (text on glass meets the contrast floor) — the audit's rendered-pixel contrast sample, every
#       pair passing and every pair on glass passing, in the page's own colour scheme (one scheme,
#       not both; the residual is recorded in the report);
#   r19 (works with transparency reduced, contrast increased, motion reduced) — the audit's reduced
#       pass: no page error with reduced motion emulated and reduced transparency asked of the
#       runtime, the override honoured and the material moved (two of the three modes; increased
#       contrast is not emulated).
# r23 (motion: materialise, morph, press feedback) has no measurement and is UNREAD — neither held
# nor failed — and the line is applied as "at most three of the rules read failed". The panel-only
# reading, exactly as pre-registered, is printed beside this one so the amendment is visible.
MECHANICAL_RULES = {
    "r18": lambda a: (a.get("contrast") or {}).get("rate") == 1
                     and (a.get("contrast") or {}).get("onGlassPass") == (a.get("contrast") or {}).get("onGlass"),
    "r19": lambda a: bool((a.get("reduced") or {}).get("ok"))
                     and bool((a.get("reduced") or {}).get("overrideHonoured"))
                     and bool((a.get("reduced") or {}).get("materialMoved")),
}
UNSHOWABLE_RULES = ["r23"]


def _int(v):
    """A recorded answer as an int, or None. A rater may write "1" or true where the shape asks for
    1; every scale here is integral, so one integer is the value and anything else is not read."""
    if isinstance(v, bool):
        return int(v)
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def load_ratings():
    """Every rater's files, keyed rater → slug → {"rules", "evidence", "quality"}, with the demo
    order each file recorded. A missing rule or quality item is simply absent rather than guessed,
    so a half-collected panel reads as far as it goes."""
    ratings, orders = {}, {}
    if not os.path.isdir(RULES_DIR):
        return ratings, orders
    for rater in sorted(os.listdir(RULES_DIR)):
        rd = os.path.join(RULES_DIR, rater)
        if not os.path.isdir(rd):
            continue
        for f in sorted(os.listdir(rd)):
            if not f.endswith(".json"):
                continue
            rec = json.load(open(os.path.join(rd, f), encoding="utf-8"))
            slug = rec.get("slug") or f[:-5]
            rules = {k: _int(v) for k, v in (rec.get("rules") or {}).items() if k in RULE_KEYS}
            quality = {k: _int(v) for k, v in (rec.get("quality") or {}).items()
                       if k in gr.QUALITY_KEYS}
            ratings.setdefault(rater, {})[slug] = {
                "rules": {k: v for k, v in rules.items() if v in (0, 1)},
                "evidence": {k: str(v) for k, v in (rec.get("evidence") or {}).items()
                             if k in RULE_KEYS and v},
                "quality": {k: v for k, v in quality.items() if v is not None},
            }
            if rec.get("order"):
                orders.setdefault(rater, {})[slug] = list(rec["order"])
    return ratings, orders


def load_audits(slugs):
    """The mechanical audit beside each demo, keyed by slug; a demo never audited is absent."""
    out = {}
    for s in slugs:
        p = os.path.join(gr.DEMOS, s, "audit.json")
        if os.path.exists(p):
            try:
                out[s] = json.load(open(p, encoding="utf-8"))
            except json.JSONDecodeError as e:
                out[s] = {"error": f"unreadable audit.json: {e}"}
    return out


ratings, orders = load_ratings()
RATERS = sorted(ratings)
# The demos the report covers: the six the briefs name, plus any slug a rater or an audit produced
# that the brief list does not — a file under an unknown slug is evidence and is not dropped.
SLUGS = list(gr.SLUGS) + sorted(
    {s for r in ratings.values() for s in r} - set(gr.SLUGS))
audits = load_audits(SLUGS)
COVERED = [s for s in SLUGS if any(s in ratings[r] for r in RATERS) or s in audits]


def raters_of(slug):
    """The raters that recorded at least one rule answer for a demo."""
    return [r for r in RATERS if ratings[r].get(slug, {}).get("rules")]


def votes(slug, key):
    """The panel's answers to one rule on one demo, as (rater, 0|1) pairs."""
    return [(r, ratings[r][slug]["rules"][key]) for r in raters_of(slug)
            if key in ratings[r][slug]["rules"]]


def majority(slug, key):
    """(held, yes, n) for one rule on one demo: held is True when strictly more than half the
    raters that answered said the rule holds, False when they did not — a tie is a failure — and
    None when nobody answered it, which is an unread rule and not a failed one."""
    vs = [v for _, v in votes(slug, key)]
    if not vs:
        return (None, 0, 0)
    yes = sum(vs)
    return (yes * 2 > len(vs), yes, len(vs))


def demo_reading(slug, panel_only=False):
    """One demo's whole reading: the majority per rule, the count held, the rules that failed, the
    fatal-tag failures, and how much of the rubric was answered at all. With `panel_only` the
    reading is the pre-registered one, every rule from the panel; otherwise r18 and r19 come from
    the mechanical audit where one exists and r23 is unread (see MECHANICAL_RULES)."""
    maj = {k: majority(slug, k) for k in RULE_KEYS}
    if not panel_only:
        a = audits.get(slug)
        for k, read_it in MECHANICAL_RULES.items():
            if a is not None and not a.get("error"):
                maj[k] = (bool(read_it(a)), None, "audit")
        for k in UNSHOWABLE_RULES:
            maj[k] = (None, 0, 0)
    read = [k for k in RULE_KEYS if maj[k][0] is not None]
    held = [k for k in RULE_KEYS if maj[k][0] is True]
    failed = [k for k in RULE_KEYS if maj[k][0] is False]
    return {
        "majority": maj, "read": read, "held": held, "failed": failed,
        "fatalFailed": [k for k in failed if RULE_TAG[k] in FATAL],
        "unread": [k for k in RULE_KEYS if maj[k][0] is None],
        "raters": raters_of(slug),
    }


def mechanical(slug):
    """The mechanical read of one demo's `audit.json`, or None when it was never audited. The
    renderer is taken from the groups that actually drew rather than from what the page asked
    for — `glass-audit.mjs` reports the resolved `GlassGroupState`, which is the honest one."""
    a = audits.get(slug)
    if a is None:
        return None
    groups = a.get("groups") or []
    reduced = a.get("reduced") or {}
    return {
        "error": a.get("error"),
        "errors": len(a.get("errors") or []),
        "overflowCapture": a.get("overflowCapture"),
        "gateMechanical": a.get("gateMechanical"),
        "renderers": sorted({g.get("renderer") for g in groups if g.get("renderer")}),
        "groups": len(groups),
        "diagnostics": len(a.get("diagnostics") or []),
        "diagnosticCodes": sorted({d.get("code") for d in (a.get("diagnostics") or [])
                                   if isinstance(d, dict) and d.get("code")}),
        "rootFound": a.get("rootFound"),
        "reducedOk": reduced.get("ok"),
        "reducedHonoured": reduced.get("overrideHonoured"),
        "surfaces": a.get("surfaces"),
    }


def verdict(slug):
    """The spec's pass line, clause by clause: at least 22 of the 25 rules held by panel majority,
    no `[layer]` or `[material]` rule failed, no group diagnostic in the mechanical read, and the
    page still working with transparency reduced. A clause whose data has not arrived is unknown
    rather than met, and a demo passes only when all four are met."""
    d, m = demo_reading(slug), mechanical(slug)
    clauses = []
    if not d["read"]:
        clauses.append(("at least 22 of 25 held", None, "no rule answers yet"))
    else:
        # The line as "at most three of the rules read failed": a rule nobody has read yet can still
        # fail, so the clause is met only once the rules still unread could not push the failures
        # past three, and lost as soon as they already have. r23 is unread by design (no
        # measurement) and is counted among neither.
        n, f = len(d["held"]), len(d["failed"])
        u = [k for k in d["unread"] if k not in UNSHOWABLE_RULES]
        ok = True if f <= MAX_FAILED and not u else (False if f > MAX_FAILED else None)
        clauses.append((f"at most {MAX_FAILED} of the rules read failed (22 of 25)",
                        ok, f"{n} held, {f} failed, {len(d['read'])} read"
                        + (f", unread: {', '.join(u)}" if u else "")
                        + f", not measurable: {', '.join(UNSHOWABLE_RULES)}"))
    if not d["read"]:
        clauses.append(("no [layer] or [material] rule fails", None, "no rule answers yet"))
    else:
        unread_fatal = [k for k in d["unread"] if RULE_TAG[k] in FATAL]
        ok = None if (unread_fatal and not d["fatalFailed"]) else not d["fatalFailed"]
        note = ("none failed" if not d["fatalFailed"] else ", ".join(d["fatalFailed"]))
        if unread_fatal:
            note += f"; unread: {', '.join(unread_fatal)}"
        clauses.append(("no [layer] or [material] rule fails", ok, note))
    if m is None or m.get("error"):
        clauses.append(("no group diagnostic", None,
                        "no audit.json" if m is None else str(m.get("error"))))
        clauses.append(("works with transparency reduced", None,
                        "no audit.json" if m is None else str(m.get("error"))))
    else:
        clauses.append(("no group diagnostic", m["diagnostics"] == 0,
                        f"{m['diagnostics']} reported"
                        + (": " + ", ".join(m["diagnosticCodes"]) if m["diagnosticCodes"] else "")))
        clauses.append(("works with transparency reduced", m["reducedOk"],
                        f"reduced pass ok={m['reducedOk']}, override honoured="
                        f"{m['reducedHonoured']}"))
    passed = all(c[1] is True for c in clauses)
    return {"clauses": clauses, "pass": passed,
            "readable": all(c[1] is not None for c in clauses)}


def alpha_for(key):
    """Krippendorff's α for one rule across the panel, the demos as the units. Nominal: the answer
    is 0 or 1 and there is no ordering for an ordinal metric to exploit. Returns the α, the number
    of units it was pairable on, and the set of values the panel used — a rule every rater held on
    every demo has no variation for chance to explain, and its α of 1.0 says agreement rather than
    reliability, so the caller prints that it was constant."""
    units = {}
    for s in COVERED:
        vs = votes(s, key)
        if len(vs) >= 2:
            units[s] = {r: v for r, v in vs}
    a = rel.krippendorff_alpha(units, "nominal") if units else None
    used = sorted({v for u in units.values() for v in u.values()})
    return a, len(units), used


def q_mean(slug, key):
    """The panel mean of one quality item on one demo, over the raters that rated it."""
    vs = [ratings[r][slug]["quality"][key] for r in RATERS
          if key in ratings[r].get(slug, {}).get("quality", {})]
    return st.mean(vs) if vs else None


def q_raters(slug):
    return [r for r in RATERS if ratings[r].get(slug, {}).get("quality")]


def aesthetics(slug):
    """The panel's a1–a4 total as the instrument computes it: each rater's mean of the four, then
    the mean over the raters. A rater missing one of the four does not contribute a partial total."""
    per = []
    for r in RATERS:
        q = ratings[r].get(slug, {}).get("quality", {})
        if all(k in q for k in AESTHETIC):
            per.append(st.mean([q[k] for k in AESTHETIC]))
    return st.mean(per) if per else None


def fmt(v, spec="{:.2f}"):
    return "—" if v is None else spec.format(v)


def yn(v):
    return "—" if v is None else ("yes" if v else "no")


# ---------- report ----------

out = []
P = out.append
P("# Liquid Glass demos — the panel's rule reading\n")
P(f"Raters: {len(RATERS)}" + (f" ({', '.join(RATERS)})" if RATERS else "") + ". "
  f"Demos with a rule file: {sum(1 for s in COVERED if raters_of(s))} of {len(gr.SLUGS)}. "
  f"Demos with an audit.json: {len(audits)} of {len(gr.SLUGS)}. "
  f"Rules: {len(RULE_KEYS)}, of which {len(FATAL_KEYS)} are tagged "
  f"{' or '.join('[' + t + ']' for t in gr.FATAL_TAGS)} and fatal to the verdict.\n")
if not RATERS:
    P(f"No rule files found under `{RULES_DIR}`. Every table below is empty; run "
      "`glass-rules.py prompt <rater>` and collect the panel first.\n")
missing = [s for s in gr.SLUGS if s not in COVERED]
if missing:
    P("Not read at all yet: " + ", ".join(f"`{s}`" for s in missing) + ".\n")
if COVERED:
    P("The panel per demo, and the demo order each rater recorded:\n")
    P("| demo | raters with rules | raters with quality | audit.json |\n|---|---|---|---|")
    for s in COVERED:
        P(f"| `{s}` | {len(raters_of(s))} | {len(q_raters(s))} | "
          f"{'yes' if s in audits else 'no'} |")
    P("")
for r in RATERS:
    seen = {tuple(o) for o in orders.get(r, {}).values()}
    if len(seen) == 1:
        got = list(next(iter(seen)))
        # The prompt's own shuffle over exactly the demos this rater was given, recomputed from its
        # name: a recorded order that does not reproduce it means the run was not the one the seed
        # describes, and the presentation-order effect cannot be estimated from the seed alone.
        want = gr.order_for(r, [s for s in gr.SLUGS if s in got])
        P(f"- `{r}` recorded the order {' → '.join(got)}"
          + (" — the seeded shuffle for this rater." if got == want
             else f", which is not this rater's seeded shuffle ({' → '.join(want)})."))
    elif seen:
        P(f"- `{r}` recorded more than one demo order across its files: "
          + "; ".join(" → ".join(o) for o in sorted(seen)) + ".")
    else:
        P(f"- `{r}` recorded no demo order.")
if RATERS:
    P("")

# ---------- the rule reading ----------

P("## The rule reading\n")
if not RATERS:
    P("No ratings.\n")
else:
    P(f"The panel majority per rule, as `held (yes/n)`; a tie is a failure. This table stands on "
      f"{len(RATERS)} rater(s); a rule no rater answered on a demo reads `—`.\n")
    P("| rule | tag | " + " | ".join(f"`{s}`" for s in COVERED) + " |")
    P("|---|---|" + "---|" * len(COVERED))
    for k in RULE_KEYS:
        cells = []
        for s in COVERED:
            held, yes, n = majority(s, k)
            cells.append("—" if held is None else f"{1 if held else 0} ({yes}/{n})")
        P(f"| {k} | {RULE_TAG[k]} | " + " | ".join(cells) + " |")
    P("")

for s in COVERED:
    d, m, v = demo_reading(s), mechanical(s), verdict(s)
    P(f"### `{s}`\n")
    if not d["raters"]:
        P("No rater has answered the rules for this demo.\n")
    else:
        po = demo_reading(s, panel_only=True)
        mech = [k for k in MECHANICAL_RULES if d["majority"][k][2] == "audit"]
        P(f"Raters: {len(d['raters'])} ({', '.join(d['raters'])}). Held: "
          f"**{len(d['held'])} of {len(d['read'])} read**"
          + (f" ({', '.join(mech)} from the audit; " if mech else " (")
          + f"{', '.join(UNSHOWABLE_RULES)} not measurable)"
          + (f", with {len([k for k in d['unread'] if k not in UNSHOWABLE_RULES])} rule(s) "
             "unanswered" if [k for k in d['unread'] if k not in UNSHOWABLE_RULES] else "")
          + ". Panel-only, as pre-registered: "
          f"{len(po['held'])} of {len(RULE_KEYS)}."
          + (" Fatal-tag failures: **" + ", ".join(f"{k} [{RULE_TAG[k]}]" for k in d["fatalFailed"])
             + "**." if d["fatalFailed"] else " No `[layer]` or `[material]` rule failed."))
        P("")
        if d["failed"]:
            P("Rules that failed:\n")
            P("| rule | tag | yes/n | a rater that said no | its evidence |\n|---|---|---|---|---|")
            for k in d["failed"]:
                if d["majority"][k][2] == "audit":
                    P(f"| {k} | {RULE_TAG[k]} | audit | — | the mechanical read |")
                    continue
                no = [r for r, val in votes(s, k) if val == 0]
                ev = next((ratings[r][s]["evidence"].get(k) for r in no
                           if ratings[r][s]["evidence"].get(k)), "")
                _, yes, n = d["majority"][k]
                P(f"| {k} | {RULE_TAG[k]} | {yes}/{n} | {no[0] if no else '—'} | "
                  f"{ev.replace('|', '/') if ev else '—'} |")
            P("")
    if m is None:
        P(f"Mechanical read: **no `audit.json`** under `{os.path.join(gr.DEMOS, s)}`; the "
          "diagnostic and reduced-transparency clauses cannot be read.\n")
    elif m.get("error"):
        P(f"Mechanical read: the audit recorded an error — {m['error']}.\n")
    else:
        P("Mechanical read (`audit.json`): "
          f"errors {m['errors']}; overflowCapture {yn(m['overflowCapture'])}; "
          f"gateMechanical {yn(m['gateMechanical'])}; "
          f"renderer {', '.join(m['renderers']) or '—'} over {m['groups']} group(s); "
          f"diagnostics {m['diagnostics']}"
          + (f" ({', '.join(m['diagnosticCodes'])})" if m["diagnosticCodes"] else "")
          + f"; rootFound {yn(m['rootFound'])}; surfaces "
          + f"{m['surfaces'] if m['surfaces'] is not None else '—'}.\n")
    P("Verdict, clause by clause:\n")
    P("| clause | met | on |\n|---|---|---|")
    for name, ok, note in v["clauses"]:
        P(f"| {name} | {'yes' if ok else ('no' if ok is False else 'not yet readable')} | {note} |")
    P("")
    P(f"**{s}: " + ("PASSES" if v["pass"] else
                    ("FAILS" if v["readable"] else "no verdict yet — a clause has no data"))
      + "**\n")

# ---------- agreement ----------

P("## Agreement per rule (Krippendorff's α, nominal)\n")
if len(RATERS) < 2:
    P(f"α needs two raters on a demo; the panel has {len(RATERS)}. No α is reported.\n")
else:
    units_any = [len([s for s in COVERED if len(votes(s, k)) >= 2]) for k in RULE_KEYS]
    P(f"The units are the demos and the observations are the panel's 0/1 answers, so each α below "
      f"stands on at most {max(units_any)} unit(s) — far fewer than a reliability claim wants, and "
      "the column saying how many is part of the reading. A rule the panel answered the same way "
      "on every demo has no variation for chance to explain: its α is 1.0 by construction and is "
      "marked constant.\n")
    P("| rule | tag | α | demos with ≥ 2 raters | values used | note |\n|---|---|---|---|---|---|")
    for k in RULE_KEYS:
        a, n, used = alpha_for(k)
        note = ("no pairable answer" if a is None else
                f"constant at {used[0]}" if len(used) == 1 else "")
        P(f"| {k} | {RULE_TAG[k]} | {fmt(a)} | {n} | {', '.join(str(u) for u in used) or '—'} | "
          f"{note} |")
    P("")

# ---------- the quality reading ----------

P("## The quality reading\n")
q_demos = [s for s in COVERED if q_raters(s)]
if not q_demos:
    P("No rater has recorded the quality items yet.\n")
else:
    P(f"The instrument's own items (`settling/rubric.py`), panel means over the raters that rated "
      f"each demo. This table stands on {len(q_demos)} demo(s) and {len(RATERS)} rater(s).\n")
    P("| demo | raters | a1 | a2 | a3 | a4 | a1–a4 | d1 | e1 |"
      "\n|---|---|---|---|---|---|---|---|---|")
    for s in q_demos:
        P(f"| `{s}` | {len(q_raters(s))} | " + " | ".join(fmt(q_mean(s, k)) for k in AESTHETIC)
          + f" | {fmt(aesthetics(s))} | {fmt(q_mean(s, 'd1'))} | {fmt(q_mean(s, 'e1'))} |")
    P("")
    d1s = [q_mean(s, "d1") for s in q_demos]
    d1s = [x for x in d1s if x is not None]
    if d1s:
        mean = st.mean(d1s)
        P(f"d1 mean over {len(d1s)} of {len(gr.SLUGS)} demos: **{mean:.2f}** against the "
          f"initiative's floor of {D1_FLOOR:.1f} — "
          + ("met" if mean >= D1_FLOOR else "not met")
          + ("." if len(d1s) == len(gr.SLUGS)
             else "; the floor is stated over all six, so this is a partial read.") + "\n")
    else:
        P("No d1 values recorded.\n")

# ---------- the line ----------

passing = [s for s in COVERED if verdict(s)["pass"]]
unreadable = [s for s in COVERED if not verdict(s)["readable"]]
P("## The line\n")
P(f"**{len(passing)} of {len(gr.SLUGS)} demos pass**"
  + (f" ({', '.join('`' + s + '`' for s in passing)})" if passing else "")
  + (f"; no verdict yet on {len(unreadable)} for want of data." if unreadable else ".")
  + " The initiative also asks the panel's d1 mean over the six and the user's eye on five of six;"
  " the user's comparison is not in this report.")

res = "\n".join(out)
outp = os.path.join(gr.DATA, "results.md")
if "--out" in sys.argv:
    outp = sys.argv[sys.argv.index("--out") + 1]
os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
open(outp, "w", encoding="utf-8").write(res + "\n")
print(res)
