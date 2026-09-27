#!/usr/bin/env python3
"""The verdict on the six materialist demos (spec: docs/doperpowers/specs/2026-09-27-materialist-
proof.md, "B. The instrument": the four readings and the pass line).

    python3 glass-rules-analyze.py [--out results.md]

Reads, under the initiative's data directory (GLASS_DATA overrides it, as in `glass-rules.py`):

  - `rules/<rater>/<slug>.json`, the panel's blind yes/no answers to the twenty-five rules;
  - `audit/<slug>.json`, the mechanical read `glass-audit.mjs` wrote (its `--audit-dir`);
  - `review/<slug>.json`, the source reviewer's reading of r23, in the shape
    `{"r23": 0|1, "evidence": "…", "spanExceptions": ["<selector fragment>", …]}`, the last
    optional: a surface under the 32 px floor that the page's record argues is a deliberate
    exception of its size family, named by a fragment of the audit's selector for it;

and writes the verdict as markdown to stdout and to `results.md` there:

  - per demo, the panel majority per rule — a tie is a failure, because the pass line asks that a
    rule be held, not that it fail to be disproved — and BOTH counts of 25: the panel-only count,
    which is the 2.3 panel's pre-registered reading and is comparable with its figures, and the
    assigned count, which is the panel majority on the twenty-two capture-visible rules plus the
    three readings this spec assigned before any capture existed:
      r18 from the audit's rendered-pixel contrast sample of text on glass, holding when every
          sampled pair passes in both schemes (the DOM sample is printed beside it);
      r19 from the audit's reduced-transparency pass and its three emulation passes, holding
          when all ran without a page error, each policy resolved as asked, the material moved
          under reduced transparency and no glass drew under forced colours;
      r23 from the source reviewer's file;
    the panel's own answers on those three print beside the assigned ones on every row;
  - the pass line, applied to the assigned count: at least 22 of 25, no `[layer]` or `[material]`
    rule failing, zero diagnostics on either channel and zero ban-subset findings in the audit,
    and the page working with transparency reduced;
  - Krippendorff's α per rule across the raters over the demos, nominal, because a rule is a 0/1
    observation and 0 against 1 is one disagreement whichever way round it falls.

The quality reading of the 2.3 panel (a1 to a4, d1, e1) is dropped (the spec's Decision Log 4).
The instrument is read while it is still being collected, so every table says what it stands on: a
majority over two raters is not the majority the pass line means, and no demo gets a final verdict
until the four named raters have answered it. Standard library only; the statistics come from the
settling instrument's `reliability.py` rather than from a second implementation of them.
"""
import os, sys, json, argparse, importlib.util

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

_parser = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
_parser.add_argument("--out", default=os.path.join(gr.DATA, "results.md"))
outp = _parser.parse_args().out

RULE_KEYS = [k for k, *_ in gr.RULES]
RULE_TAG = {k: t for k, t, _, _ in gr.RULES}
FATAL = set(gr.FATAL_TAGS)
FATAL_KEYS = [k for k in RULE_KEYS if RULE_TAG[k] in FATAL]
ASSIGNED = list(gr.ASSIGNED)            # r18, r19, r23
PANEL_KEYS = [k for k in RULE_KEYS if k not in ASSIGNED]
HOLD_FLOOR = 22                          # of 25, the 2.3 line
RULES_DIR = os.path.join(gr.DATA, "rules")
AUDITS_DIR = os.path.join(gr.DATA, "audit")
REVIEWS_DIR = os.path.join(gr.DATA, "review")

# The named, pre-registered panel; extra files cannot substitute for a missing member.
EXPECTED_RATERS = ("astra-high", "astra-medium", "claude-opus", "claude-sonnet")


def _int(v):
    """A recorded answer as an int, or None. A rater may write "1" or true where the shape asks for
    1; every answer here is 0 or 1, so one integer is the value and anything else is not read."""
    if isinstance(v, bool):
        return int(v)
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def _json(path):
    """A JSON file, or {"error": …} when it does not parse; None when it is absent."""
    if not os.path.exists(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"error": f"unreadable {os.path.basename(path)}: {e}"}


def load_ratings():
    """Every rater's files, keyed rater → slug → {"rules", "evidence"}, with the demo order each
    file recorded. A missing rule is simply absent rather than guessed, so a half-collected panel
    reads as far as it goes."""
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
            rec = _json(os.path.join(rd, f)) or {}
            slug = rec.get("slug") or f[:-5]
            rules = {k: _int(v) for k, v in (rec.get("rules") or {}).items() if k in RULE_KEYS}
            ratings.setdefault(rater, {})[slug] = {
                "rules": {k: v for k, v in rules.items() if v in (0, 1)},
                "evidence": {k: str(v) for k, v in (rec.get("evidence") or {}).items()
                             if k in RULE_KEYS and v},
            }
            if rec.get("order"):
                orders.setdefault(rater, {})[slug] = list(rec["order"])
    return ratings, orders


ratings, orders = load_ratings()
RATERS = [r for r in EXPECTED_RATERS if r in ratings]
# The demos the report covers: the six the briefs name, plus any slug a rater, an audit or a review
# produced that the brief list does not — a file under an unknown slug is evidence and is not dropped.
_extra = {s for r in ratings.values() for s in r}
for d in (AUDITS_DIR, REVIEWS_DIR):
    if os.path.isdir(d):
        _extra |= {f[:-5] for f in os.listdir(d) if f.endswith(".json")}
SLUGS = list(gr.SLUGS) + sorted(_extra - set(gr.SLUGS))
audits = {s: a for s in SLUGS if (a := _json(os.path.join(AUDITS_DIR, s + ".json"))) is not None}
reviews = {s: r for s in SLUGS if (r := _json(os.path.join(REVIEWS_DIR, s + ".json"))) is not None}
COVERED = [s for s in SLUGS if any(s in ratings[r] for r in RATERS) or s in audits or s in reviews]


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


def panel_missing(slug):
    """Named raters whose answers to the 25 are missing, including partially written files."""
    return [r for r in EXPECTED_RATERS
            if not all(k in ratings.get(r, {}).get(slug, {}).get("rules", {}) for k in RULE_KEYS)]


# ---------- the assigned readings ----------

def assigned_r18(a):
    """(held, evidence) from the rendered-pixel sample of text on glass in both schemes."""
    if a is None or a.get("error"):
        return None, "no audit" if a is None else str(a["error"])
    schemes = a.get("schemes") or {}
    parts, held = [], True
    for s in ("light", "dark"):
        gc = (schemes.get(s) or {}).get("glassContrast")
        if gc is None:
            return None, f"no {s} glass-contrast sample in the audit"
        dom = (schemes.get(s) or {}).get("contrast") or {}
        parts.append(f"{s} {gc['pass']}/{gc['pairs']} on glass"
                     + (f", min {gc['minRatio']}" if gc.get("minRatio") is not None else "")
                     + f" (DOM sample {dom.get('pass')}/{dom.get('checked')})")
        if gc["pass"] != gc["pairs"]:
            held = False
    if all((schemes[s]["glassContrast"]["pairs"] == 0) for s in ("light", "dark")):
        parts.append("vacuous: no text on glass was on screen to sample")
    return held, "; ".join(parts)


def reduced_ran(red):
    """Whether the reduced pass reached the material: yes through the page's switch or the runtime's
    override, no where the page's switch threw, and unread where the page offered neither — that
    is the audit contract unmet (no switch, no `window.__vitrea`), not a page shown to break."""
    if red.get("applied"):
        return True
    return False if str(red.get("method", "")).startswith("threw") else None


def assigned_r19(a):
    """(held, evidence) from the reduced-transparency pass and the three emulation passes."""
    if a is None or a.get("error"):
        return None, "no audit" if a is None else str(a["error"])
    red, emu = a.get("reduced") or {}, a.get("emulation") or {}
    checks = [
        ("reduced ran", reduced_ran(red)),
        ("reduced no page error", not red.get("errors") if "errors" in red else None),
        ("reduced policy as asked", red.get("policyAsAsked")),
        ("reduced material moved", red.get("materialMoved")),
    ]
    for kind in ("increasedContrast", "reducedMotion", "forcedColors"):
        e = emu.get(kind) or {}
        ran = e.get("status") == "ran"
        checks += [
            (f"{kind} ran", True if ran else (None if e.get("status") in (None, "unsupported",
                                                                            "not-applied") else False)),
            (f"{kind} no page error", (not e.get("errors")) if ran else None),
            (f"{kind} policy as asked", e.get("policyAsAsked") if ran else None),
        ]
    fc = emu.get("forcedColors") or {}
    checks.append(("forced colours draw no glass",
                   fc.get("glassDrawn") == 0 if fc.get("status") == "ran"
                   and fc.get("glassDrawn") is not None else None))
    held = all_observed([v for _, v in checks])
    ev = ("method " + str(red.get("method")) + "; "
          + ", ".join(f"{n}={'yes' if v else ('no' if v is False else '?')}" for n, v in checks))
    return held, ev


def assigned_r23(slug):
    r = reviews.get(slug)
    if r is None:
        return None, "no source review"
    if r.get("error"):
        return None, r["error"]
    v = _int(r.get("r23"))
    return (None if v not in (0, 1) else bool(v)), str(r.get("evidence") or "")[:300]


def all_observed(checks):
    """A known failure fails; a missing observation cannot pass."""
    if any(c is False for c in checks):
        return False
    return True if all(c is True for c in checks) else None


def assigned(slug):
    a = audits.get(slug)
    return {"r18": assigned_r18(a), "r19": assigned_r19(a), "r23": assigned_r23(slug)}


def readings(slug):
    """Both counts. The panel-only reading takes the majority on all 25; the assigned reading takes
    it on the 22 capture-visible rules and the assigned readings on r18, r19 and r23."""
    maj = {k: majority(slug, k) for k in RULE_KEYS}
    asg = assigned(slug)
    used = {k: (maj[k][0] if k in PANEL_KEYS else asg[k][0]) for k in RULE_KEYS}
    return {
        "majority": maj, "assigned": asg, "used": used,
        "panelHeld": [k for k in RULE_KEYS if maj[k][0] is True],
        "held": [k for k in RULE_KEYS if used[k] is True],
        "failed": [k for k in RULE_KEYS if used[k] is False],
        "unread": [k for k in RULE_KEYS if used[k] is None],
        "fatalFailed": [k for k in RULE_KEYS if used[k] is False and RULE_TAG[k] in FATAL],
        "raters": raters_of(slug),
    }


def ban_findings(slug):
    """The audit's ban-subset findings, less spans the source review names as deliberate."""
    a = audits.get(slug) or {}
    found = ((a.get("banSubset") or {}).get("findings")) or []
    excuse = (reviews.get(slug) or {}).get("spanExceptions") or []
    kept, excused = [], []
    for f in found:
        if f.get("kind") == "span-under-32" and any(e and e in (f.get("selector") or "")
                                                     for e in excuse):
            excused.append(f)
        else:
            kept.append(f)
    return kept, excused


def verdict(slug):
    """The pass line on the assigned count, final only once all four named raters have answered."""
    d, a = readings(slug), audits.get(slug)
    missing = panel_missing(slug)
    complete = not missing
    unread_asg = [k for k in ASSIGNED if d["used"][k] is None]
    clauses = [
        ("four-rater panel complete", True if complete else None,
         "all 25 rules answered" if complete else "missing/partial: " + ", ".join(missing)),
        ("assigned readings present", True if not unread_asg else None,
         "r18, r19, r23 read" if not unread_asg else "unread: " + ", ".join(unread_asg)),
        ("at least 22 of 25 held (assigned count)",
         len(d["held"]) >= HOLD_FLOOR if complete and not unread_asg else None,
         f"{len(d['held'])} of 25 held" + ("" if complete and not unread_asg else " (provisional)")),
        ("no [layer] or [material] rule fails", not d["fatalFailed"] if complete else None,
         ", ".join(d["fatalFailed"]) or "none failed in available answers"),
    ]
    if a is None or a.get("error"):
        note = "no audit" if a is None else str(a["error"])
        clauses += [("zero diagnostics, either channel", None, note),
                    ("zero ban-subset findings", None, note),
                    ("works with transparency reduced", None, note)]
    else:
        diags = a.get("diagnostics")
        kept, excused = ban_findings(slug)
        red = a.get("reduced") or {}
        clauses += [
            # A page that never exposed its root has had no diagnostic read, which is the audit
            # contract unmet rather than a clean channel.
            ("zero diagnostics, either channel",
             (len(diags) == 0) if a.get("rootFound") is True and isinstance(diags, list) else None,
             ("root not reachable (window.__vitrea unset), diagnostics unread"
              if not a.get("rootFound") else
              ", ".join(sorted({f"{x['origin']}:{x['code']}" for x in diags})) or "none")),
            ("zero ban-subset findings", len(kept) == 0,
             (", ".join(sorted({f"{f['kind']}:{f.get('property')}" for f in kept})) or "none")
             + (f"; {len(excused)} span(s) excused by the review" if excused else "")),
            ("works with transparency reduced",
             all_observed([reduced_ran(red), red.get("policyAsAsked"), red.get("materialMoved"),
                           not red.get("errors") if "errors" in red else None]),
             f"method {red.get('method')}; policyAsAsked={red.get('policyAsAsked')}; "
             f"materialMoved={red.get('materialMoved')}; errors={json.dumps(red.get('errors'))}"),
        ]
    return {"clauses": clauses, "pass": all(c[1] is True for c in clauses),
            "readable": all(c[1] is not None for c in clauses)}


def alpha_for(key):
    """Krippendorff's α for one rule across the panel, the demos as the units, nominal. Returns the
    α, the number of units it was pairable on, and the values the panel used — a rule every rater
    held on every demo has no variation for chance to explain, and its α of 1.0 says agreement
    rather than reliability, so the caller prints that it was constant."""
    units = {}
    for s in COVERED:
        vs = votes(s, key)
        if len(vs) >= 2:
            units[s] = {r: v for r, v in vs}
    a = rel.krippendorff_alpha(units, "nominal") if units else None
    used = sorted({v for u in units.values() for v in u.values()})
    return a, len(units), used


def fmt(v, spec="{:.2f}"):
    return "—" if v is None else spec.format(v)


def cell(v):
    return "—" if v is None else ("1" if v else "0")


def md(s):
    return str(s).replace("|", "/").replace("\n", " ")


# ---------- report ----------

out = []
P = out.append
P("# Materialist demos — the panel, the audit and the verdict\n")
P("The pre-registered panel is " + ", ".join(EXPECTED_RATERS) + ". Missing or partial members "
  "keep every verdict provisional. Two counts of 25 print for every demo: the **panel-only** count "
  "(the 2.3 panel's pre-registered reading, comparable with its figures) and the **assigned** count "
  "(the panel on the 22 capture-visible rules, and r18, r19 and r23 from the audit and the source "
  "review, as the spec declared before any capture existed). The pass line uses the assigned count.\n")
P(f"Raters: {len(RATERS)}" + (f" ({', '.join(RATERS)})" if RATERS else "") + ". "
  f"Demos with a rule file: {sum(1 for s in COVERED if raters_of(s))} of {len(gr.SLUGS)}. "
  f"Audits: {len(audits)} of {len(gr.SLUGS)}. Source reviews: {len(reviews)} of {len(gr.SLUGS)}. "
  f"Rules: {len(RULE_KEYS)}, of which {len(FATAL_KEYS)} are tagged "
  f"{' or '.join('[' + t + ']' for t in gr.FATAL_TAGS)} and fatal to the verdict. Rules digest "
  f"`{gr.RULES_SHA256[:16]}…` (the 2.3 panel's).\n")
if not RATERS:
    P(f"No rater files under `{RULES_DIR}`. The panel tables below are empty; run "
      "`glass-rules.py prompt <rater>` and collect the panel first.\n")
not_read = [s for s in gr.SLUGS if s not in COVERED]
if not_read:
    P("Not read at all yet: " + ", ".join(f"`{s}`" for s in not_read) + ".\n")
if COVERED:
    P("| demo | raters | audit | source review |\n|---|---|---|---|")
    for s in COVERED:
        P(f"| `{s}` | {len(raters_of(s))} | {'yes' if s in audits else 'no'} | "
          f"{'yes' if s in reviews else 'no'} |")
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
if not COVERED:
    P("Nothing to read yet.\n")
else:
    P("Per rule and demo: the panel majority as `held (yes/n)`, a tie a failure, `—` unanswered; on "
      "r18, r19 and r23 the assigned reading follows after `→`, and that is the answer the "
      "assigned count uses.\n")
    P("| rule | tag | " + " | ".join(f"`{s}`" for s in COVERED) + " |")
    P("|---|---|" + "---|" * len(COVERED))
    for k in RULE_KEYS:
        cells = []
        for s in COVERED:
            held, yes, n = majority(s, k)
            c = "—" if held is None else f"{1 if held else 0} ({yes}/{n})"
            if k in ASSIGNED:
                c += " → " + cell(assigned(s)[k][0])
            cells.append(c)
        P(f"| {k} | {RULE_TAG[k]} | " + " | ".join(cells) + " |")
    P("")
    P("| demo | panel-only (of 25) | assigned (of 25) | unread in the assigned count |"
      "\n|---|---|---|---|")
    for s in COVERED:
        d = readings(s)
        P(f"| `{s}` | {len(d['panelHeld'])} | {len(d['held'])} | "
          f"{', '.join(d['unread']) or '—'} |")
    P("")

for s in COVERED:
    d, a, v = readings(s), audits.get(s), verdict(s)
    P(f"### `{s}`\n")
    if d["raters"]:
        P(f"Raters: {len(d['raters'])} ({', '.join(d['raters'])}). Panel-only: "
          f"**{len(d['panelHeld'])} of 25**. Assigned: **{len(d['held'])} of 25**"
          + (" (provisional; panel incomplete)" if panel_missing(s) else "")
          + (f"; unread: {', '.join(d['unread'])}" if d["unread"] else "")
          + (". Fatal-tag failures: **" + ", ".join(d["fatalFailed"]) + "**."
             if d["fatalFailed"] else ". No fatal-tag failure in available answers."))
    else:
        P("No rater has answered the rules for this demo.")
    P("")
    P("The assigned readings, with the panel's answers beside them:\n")
    P("| rule | assigned | panel | on |\n|---|---|---|---|")
    for k in ASSIGNED:
        held, ev = d["assigned"][k]
        m_held, yes, n = d["majority"][k]
        P(f"| {k} | {cell(held)} | {'—' if m_held is None else f'{cell(m_held)} ({yes}/{n})'} | "
          f"{md(ev) or '—'} |")
    P("")
    failed_panel = [k for k in d["failed"] if k in PANEL_KEYS]
    if failed_panel:
        P("Capture-visible rules that failed:\n")
        P("| rule | tag | yes/n | a rater that said no | its evidence |\n|---|---|---|---|---|")
        for k in failed_panel:
            no = [r for r, val in votes(s, k) if val == 0]
            ev = next((ratings[r][s]["evidence"].get(k) for r in no
                       if ratings[r][s]["evidence"].get(k)), "")
            _, yes, n = d["majority"][k]
            P(f"| {k} | {RULE_TAG[k]} | {yes}/{n} | {no[0] if no else '—'} | {md(ev) or '—'} |")
        P("")
    if a is None:
        P(f"Mechanical read: **no audit** at `{os.path.join(AUDITS_DIR, s + '.json')}`.\n")
    elif a.get("error"):
        P(f"Mechanical read: **{md(a['error'])}**.\n")
    else:
        kept, excused = ban_findings(s)
        sch = a.get("schemes") or {}
        P("Mechanical read: root " + ("reachable" if a.get("rootFound") else "**not reachable**")
          + f"; {len(a.get('surfaces') or [])} surface(s); page errors {len(a.get('errors') or [])}; "
          + f"diagnostics {len(a.get('diagnostics') or [])}; ban-subset findings {len(kept)}"
          + (f" ({len(excused)} span(s) excused)" if excused else "")
          + "; colour scheme followed: "
          + ", ".join(f"{x}={(sch.get(x) or {}).get('schemeFollowed')}" for x in ("light", "dark"))
          + (f"; unknown diagnostic codes {a['unknownDiagnosticCodes']}"
             if a.get("unknownDiagnosticCodes") else "")
          + (f"; root API missing {a['api']['missing']}"
             if (a.get("api") or {}).get("missing") else "") + ".\n")
        for f in kept[:20]:
            P(f"- `{f['kind']}` {f.get('property') or ''} `{md(str(f.get('value'))[:80])}`"
              + (f" ({f['origin']})" if f.get("origin") else "")
              + f" on `{md(f.get('selector') or f.get('groupId') or '')}`, seen {', '.join(f.get('seen', []))}")
        if kept:
            P("")
        for x in a.get("diagnostics") or []:
            P(f"- diagnostic `{x['origin']}:{x['code']}` on {', '.join(x['subjects'])}: "
              f"{md(x['message'])[:160]}")
        if a.get("diagnostics"):
            P("")
    P("Verdict, clause by clause:\n")
    P("| clause | met | on |\n|---|---|---|")
    for name, ok, note in v["clauses"]:
        P(f"| {name} | {'yes' if ok else ('no' if ok is False else 'not yet readable')} | {md(note)} |")
    P("")
    P(f"**{s}: " + ("PASSES" if v["pass"] else
                    ("FAILS" if v["readable"] else
                     "no final verdict — incomplete evidence; provisional reading above"))
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

# ---------- the line ----------

passing = [s for s in gr.SLUGS if s in COVERED and verdict(s)["pass"]]
fatal = [s for s in gr.SLUGS if s in COVERED and readings(s)["fatalFailed"]
         and not panel_missing(s)]
unreadable = [s for s in gr.SLUGS if s not in COVERED or not verdict(s)["readable"]]
P("## The line\n")
P(f"**{len(passing)} of {len(gr.SLUGS)} demos pass**"
  + (f" ({', '.join('`' + s + '`' for s in passing)})" if passing else "")
  + (f"; no verdict yet on {len(unreadable)} for want of data." if unreadable else ".")
  + " The initiative meets its purpose when all six pass. "
  + (f"**Stop condition met**: {len(fatal)} demos fail a [layer] or [material] rule "
     f"({', '.join(fatal)}); the next step is a rewrite of the skill's §4 from the failures."
     if len(fatal) >= 3 else
     f"The stop condition (three or more demos failing a [layer] or [material] rule) is not met "
     f"on the evidence so far ({len(fatal)}).")
  + " The user's eye (reading 4) is not in this report.")

res = "\n".join(out)
os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
open(outp, "w", encoding="utf-8").write(res + "\n")
print(res)
