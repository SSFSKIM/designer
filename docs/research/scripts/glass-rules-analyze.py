#!/usr/bin/env python3
"""The verdict on the six materialist demos (spec: docs/doperpowers/specs/2026-09-27-materialist-
proof.md, "B. The instrument": the four readings and the pass line), and with `--rules spatial` on
the spatial-register pages (2026-09-27-materialist-spatial-register.md, "B. The rulebook and the
instrument"; the last paragraph below).

    python3 glass-rules-analyze.py [--rules instrument|spatial] [--out results.md]

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

With `--rules spatial` the same readings run on the spatial rulebook (`glass-rules.py --rules
spatial`), its data directory and its pages, and everything above holds but the rulebook and the
line. Each rule prints with what it is to the six's: `= rN` repeats instrument rule rN verbatim,
`~ rN` adapts it, `new` is the register's own. The three assigned readings follow whichever item
repeats r18, r19 or r23; r18's is the audit's per-line contrast on the glyph-suppressed captures
(`lineContrast`), the worst line gating, over every state the audit read. The pass line: every
rule tagged `[environment]`, `[layer]` or `[material]` holds; at least 88 % of the rulebook holds
(the 2.3 line's 22 of 25 as a proportion, rounded up); zero diagnostics; zero findings in
`banSubset` and `banSubsetSpatial` together; every text line on glass passes its floor in every
state read; and no clause reads UNREAD. A rule on which most raters answered 0 with evidence
beginning "unread:" (the rater prompt's third value, inside the 0/1 answer) reads UNREAD: it is
neither held nor failed, its missing state is printed, and it blocks the verdict. A read the page
did not make possible — a CSS tier its
`?tier=css` switch never reached, phases it never exposed (unless the source review declares the
environment static, `"environmentStatic": true`), a receded pose that never resolved — prints
UNREAD and blocks the verdict rather than shrinking what was tested. Per page the report also
prints the glass coverage, each host's drawn level and environment ring against the dead band in
every state, and each group's CSS body on the CSS tier. A rating file recording another rulebook
(`"rules_set"`) is not read.
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
_parser.add_argument("--rules", choices=gr.RULE_SET_NAMES, default="instrument",
                     help="the rulebook: instrument (the six demos) or spatial (the "
                          "spatial-register pages)")
_parser.add_argument("--out", default=None,
                     help="where results.md goes; default the rulebook's data directory")
_args = _parser.parse_args()
gr.select(_args.rules)
outp = _args.out or os.path.join(gr.DATA, "results.md")
SPATIAL = gr.RULES_SET == "spatial"

RULE_KEYS = [k for k, *_ in gr.RULES]
RULE_TAG = {k: t for k, t, _, _ in gr.RULES}
FATAL = set(gr.FATAL_TAGS)
FATAL_KEYS = [k for k in RULE_KEYS if RULE_TAG[k] in FATAL]
ASSIGNED = list(gr.ASSIGNED)            # r18, r19, r23, or the spatial items that repeat them
PANEL_KEYS = [k for k in RULE_KEYS if k not in ASSIGNED]
N_RULES = len(RULE_KEYS)
# The 2.3 line is 22 of 25; the spatial rulebook carries it as that proportion, 88 %, rounded up in
# integers, since a float product can land a hair above a whole number and move the floor by one.
HOLD_FLOOR = -(-88 * N_RULES // 100)
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


SKIPPED = []                            # rating files that recorded another rulebook


def load_ratings():
    """Every rater's files, keyed rater → slug → {"rules", "evidence"}, with the demo order each
    file recorded. A missing rule is simply absent rather than guessed, so a half-collected panel
    reads as far as it goes. A file that records a different rulebook than the one being read is
    passed over and listed, whatever its keys."""
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
            if rec.get("rules_set") not in (None, gr.RULES_SET):
                SKIPPED.append(f"{rater}/{f} ({rec.get('rules_set')})")
                continue
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


def assigned_r23(slug, key="r23"):
    """(held, evidence) from the source review's `r23`, or, on the spatial rulebook, the key of the
    item that repeats it where the reviewer wrote that instead."""
    r = reviews.get(slug)
    if r is None:
        return None, "no source review"
    if r.get("error"):
        return None, r["error"]
    v = _int(r.get("r23", r.get(key)))
    return (None if v not in (0, 1) else bool(v)), str(r.get("evidence") or "")[:300]


def all_observed(checks):
    """A known failure fails; a missing observation cannot pass."""
    if any(c is False for c in checks):
        return False
    return True if all(c is True for c in checks) else None


def assigned(slug):
    """The assigned readings keyed by the rulebook's own keys: r18, r19 and r23 on the six's, the
    items that repeat them on the spatial one, where r18 is read per line."""
    a = audits.get(slug)
    out = {}
    for k in ASSIGNED:
        rn = gr.SAME_AS.get(k, k)
        out[k] = ((line_reading(a) if SPATIAL else assigned_r18(a)) if rn == "r18" else
                  assigned_r19(a) if rn == "r19" else assigned_r23(slug, k))
    return out


# ---------- the spatial register's reads ----------

def line_reads(a):
    """Every per-line contrast reading the audit holds, as (where, summary), in pass order: the
    two scheme passes and their phases, the reduced capture, the CSS tier and its phases, the
    receded pose."""
    sch = a.get("schemes") or {}
    places = []
    for s in ("light", "dark"):
        places.append((s, (sch.get(s) or {}).get("lineContrast")))
        places.append((f"{s} phases", ((sch.get(s) or {}).get("phases") or {}).get("lineContrast")))
    css = a.get("cssTier") or {}
    places += [("reduced", (a.get("reduced") or {}).get("lineContrast")),
               ("css", css.get("lineContrast")),
               ("css phases", (css.get("phases") or {}).get("lineContrast")),
               ("receded", (a.get("receded") or {}).get("lineContrast"))]
    return [(w, x) for w, x in places if x]


def line_reading(a):
    """(held, evidence) for text on glass read per line box: held when every line in every state
    read passes its floor, the worst line gating; unread without both schemes' readings."""
    if a is None or a.get("error"):
        return None, "no audit" if a is None else str(a["error"])
    sch = a.get("schemes") or {}
    missing = [s for s in ("light", "dark") if not (sch.get(s) or {}).get("lineContrast")]
    if missing:
        return None, "no per-line reading in the " + " or ".join(missing) + " scheme pass"
    reads = line_reads(a)
    parts = []
    for where, x in reads:
        w = x.get("worst")
        parts.append(f"{where} {x['pass']}/{x['lines']}"
                     + (f", worst {w['ratio']} against {w['floor']}" if w else ""))
    lines = sum(x["lines"] for _, x in reads)
    if lines == 0:
        parts.append("vacuous: no text on glass was on screen to read")
    return all(x["pass"] == x["lines"] for _, x in reads), "; ".join(parts)


def failing_lines(a):
    """Every failing line the audit kept, with where it was read."""
    return [(w, f) for w, x in line_reads(a or {}) for f in x.get("fails") or []]


def spatial_ban(a):
    """The audit's `banSubsetSpatial` findings; None where the audit predates the spatial reads."""
    b = a.get("banSubsetSpatial")
    return None if b is None else (b.get("findings") or [])


def phase_read(slug, a):
    """(met, note) for the environment's phases: read where the page offered them and every one
    was shown; met without them only where the source review declares the environment static."""
    sch = a.get("schemes") or {}
    if "phasesHook" not in a:
        return None, "UNREAD: the audit predates the phase pass"
    if not a.get("phasesHook"):
        if (reviews.get(slug) or {}).get("environmentStatic") is True:
            return True, "no phases offered; the source review declares one environment state"
        return None, ("UNREAD: the page exposes no window.__glassDemo.phases() and setPhase(id), "
                      "and no source review declares its environment static")
    notes, ok = [], True
    for s in ("light", "dark"):
        p = (sch.get(s) or {}).get("phases") or {}
        if not p.get("ids"):
            return None, f"UNREAD: the {s} phase pass read no phases ({p.get('error', 'no ids')})"
        shown = p.get("shown") or []
        bad = [x for x in shown if x.get("status") != "captured"]
        if bad:
            ok = False
        notes.append(f"{s} {len(shown) - len(bad)} of {len(p['ids'])} captured"
                     + (f" of {p['total']} offered" if p.get("total", 0) > len(p["ids"]) else "")
                     + (f"; {bad[0]['status']}" if bad else ""))
    return (True if ok else None), ("" if ok else "UNREAD: ") + "; ".join(notes)


def css_read(a):
    """(met, note) for the CSS tier: read when the page's ?tier=css switch put every group on it."""
    c = a.get("cssTier")
    if c is None:
        return None, "UNREAD: the audit predates the CSS-tier pass"
    groups = ", ".join(f"{g['id']} {g.get('renderer')}/{g.get('cssBody')}"
                       for g in c.get("groups") or [])
    if c.get("status") == "ran":
        return True, "groups " + (groups or "none")
    if c.get("status") == "not-honoured":
        return None, "UNREAD: ?tier=css not honoured (" + (groups or "no groups") + ")"
    return None, f"UNREAD: CSS-tier pass {c.get('status')}"


def receded_read(a):
    """(met, note) for the receded pose: read when the root resolved `inactive`."""
    r = a.get("receded")
    if r is None:
        return None, "UNREAD: the audit predates the receded pass"
    if r.get("status") == "ran" and r.get("windowActivation") == "inactive":
        x = r.get("lineContrast") or {}
        return True, f"windowActivation inactive; lines {x.get('pass')}/{x.get('lines')}"
    return None, (f"UNREAD: receded pass {r.get('status')}, windowActivation "
                  f"{r.get('windowActivation')}")


def host_levels(a):
    """Every host-level read the audit holds, as (where, read), `where` naming pass and state."""
    sch = a.get("schemes") or {}
    places = []
    for s in ("light", "dark"):
        places.append((s, (sch.get(s) or {}).get("hostLuminance")))
        places.append((s, ((sch.get(s) or {}).get("phases") or {}).get("hostLuminance")))
    css = a.get("cssTier") or {}
    places += [("reduced", (a.get("reduced") or {}).get("hostLuminance")),
               ("css", css.get("hostLuminance")),
               ("css", (css.get("phases") or {}).get("hostLuminance")),
               ("receded", (a.get("receded") or {}).get("hostLuminance"))]
    return [(w if w == "reduced" else f"{w}/{r['state']}", r)
            for w, h in places if h for r in h.get("reads") or []]


def unread_votes(slug, key):
    """The raters that answered a rule 0 and began its evidence "unread:": the rater prompt's third
    value, kept inside the 0/1 answer so the answers stay comparable with the six's."""
    return [r for r, v in votes(slug, key) if v == 0
            and ratings[r][slug]["evidence"].get(key, "").strip().lower().startswith("unread:")]


def panel_unread(slug, key):
    """On the spatial rulebook, whether the panel reads a rule UNREAD: strictly more than half the
    raters that answered it said the state it needs was neither captured nor recorded. A tie is
    not a majority, and the rule is then read as held or failed like any other."""
    if not SPATIAL:
        return False
    vs = votes(slug, key)
    return bool(vs) and len(unread_votes(slug, key)) * 2 > len(vs)


def readings(slug):
    """Both counts. The panel-only reading takes the majority on all 25; the assigned reading takes
    it on the 22 capture-visible rules and the assigned readings on r18, r19 and r23. On the
    spatial rulebook a capture-visible rule the panel reads UNREAD is neither held nor failed in
    the assigned count: it is unread, as a missing assigned reading is, and blocks the verdict."""
    maj = {k: majority(slug, k) for k in RULE_KEYS}
    asg = assigned(slug)
    # Only a rule the PANEL answers can be read UNREAD by the panel. On an assigned rule (s18, s19,
    # s21) the audit or the source review is the answer the spec declared before any capture
    # existed, and the panel's answer prints beside it for comparison, so a rater majority saying
    # "unread:" there names a capture the panel lacked, not a read the verdict lacks; it is listed
    # under the assigned table, and it does not block.
    panel_unread_keys = [k for k in PANEL_KEYS if panel_unread(slug, k)]
    panel_unread_assigned = [k for k in ASSIGNED if panel_unread(slug, k)]
    used = {k: ((None if k in panel_unread_keys else maj[k][0]) if k in PANEL_KEYS
                else asg[k][0]) for k in RULE_KEYS}
    return {
        "majority": maj, "assigned": asg, "used": used, "panelUnread": panel_unread_keys,
        "panelUnreadAssigned": panel_unread_assigned,
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
         f"all {N_RULES} rules answered" if complete else "missing/partial: " + ", ".join(missing)),
        ("assigned readings present", True if not unread_asg else None,
         f"{', '.join(ASSIGNED)} read" if not unread_asg else "unread: " + ", ".join(unread_asg)),
        (f"at least {HOLD_FLOOR} of {N_RULES} held (assigned count)",
         len(d["held"]) >= HOLD_FLOOR if complete and not unread_asg else None,
         f"{len(d['held'])} of {N_RULES} held"
         + ("" if complete and not unread_asg else " (provisional)")),
    ]
    if SPATIAL:
        return spatial_verdict(slug, d, a, clauses, complete)
    clauses.append(
        ("no [layer] or [material] rule fails", not d["fatalFailed"] if complete else None,
         ", ".join(d["fatalFailed"]) or "none failed in available answers"))
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


def spatial_verdict(slug, d, a, clauses, complete):
    """The spatial pass line on the assigned count. Every fatal-tag rule must hold, not merely not
    fail; the text clause gates on the worst line in every state read; and a read the page did not
    make possible is UNREAD, which blocks the verdict as a missing panel answer does."""
    # The count: an UNREAD rule is out of both the held and the failed tally, so the floor is met
    # once the held rules reach it and missed once the failed ones put it out of reach; between
    # the two it waits on the unread rules.
    held, lost = len(d["held"]), len(d["failed"])
    unread_asg = [k for k in ASSIGNED if d["used"][k] is None]
    clauses[2] = (clauses[2][0],
                  (True if held >= HOLD_FLOOR else False if lost > N_RULES - HOLD_FLOOR else None)
                  if complete and not unread_asg else None,
                  f"{held} of {N_RULES} held, {lost} failed"
                  + (f", {len(d['unread'])} unread" if d["unread"] else "")
                  + ("" if complete and not unread_asg else " (provisional)"))
    pu = d["panelUnread"]
    clauses.append(("no rule reads UNREAD on the panel",
                    True if complete and not pu else None,
                    ("UNREAD: " + ", ".join(pu) if pu else "none")
                    + ("" if complete else " (provisional)")))
    fatal_used = [d["used"][k] for k in FATAL_KEYS]
    failed = [k for k in FATAL_KEYS if d["used"][k] is False]
    unread = [k for k in FATAL_KEYS if d["used"][k] is None]
    note = "; ".join(([f"failed: {', '.join(failed)}"] if failed else [])
                     + ([f"unread or unanswered: {', '.join(unread)}"] if unread else []))
    clauses.append((f"every {either(gr.FATAL_TAGS)} rule holds",
                    all_observed(fatal_used) if complete else None,
                    (note or f"all {len(FATAL_KEYS)} held")
                    + ("" if complete else " (provisional)")))
    if a is None or a.get("error"):
        note = "no audit" if a is None else str(a["error"])
        for name in ("zero diagnostics, either channel", "zero ban-subset findings, both lists",
                     "every text line on glass passes, every state", "the CSS tier read",
                     "the environment's phases read", "the receded pose read"):
            clauses.append((name, None, note))
    else:
        diags = a.get("diagnostics")
        kept, excused = ban_findings(slug)
        extra = spatial_ban(a)
        held, ev = line_reading(a)
        fails = failing_lines(a)
        clauses += [
            ("zero diagnostics, either channel",
             (len(diags) == 0) if a.get("rootFound") is True and isinstance(diags, list) else None,
             ("root not reachable (window.__vitrea unset), diagnostics unread"
              if not a.get("rootFound") else
              ", ".join(sorted({f"{x['origin']}:{x['code']}" for x in diags})) or "none")),
            ("zero ban-subset findings, both lists",
             None if extra is None else len(kept) + len(extra) == 0,
             "UNREAD: the audit predates banSubsetSpatial" if extra is None else
             (", ".join(sorted({f"{f['kind']}:{f.get('property')}" for f in kept + extra}))
              or "none")
             + (f"; {len(excused)} span(s) excused by the review" if excused else "")),
            ("every text line on glass passes, every state", held,
             (f"{len(fails)} failing line(s); " if fails else "") + ev),
            ("the CSS tier read", *css_read(a)),
            ("the environment's phases read", *phase_read(slug, a)),
            ("the receded pose read", *receded_read(a)),
        ]
    return {"clauses": clauses, "pass": all(c[1] is True for c in clauses),
            "readable": all(c[1] is not None for c in clauses),
            "failed": any(c[1] is False for c in clauses)}


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


def label(k):
    """A rule's key; on the spatial rulebook with what it is to the six's rulebook."""
    if not SPATIAL:
        return k
    m = gr.MARKERS.get(k)
    return f"{k} ({m[0]} {m[1]})" if m else f"{k} (new)"


def _and(xs):
    """"a", "a and b", "a, b and c"."""
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def either(tags):
    """"[a] or [b]", "[a], [b] or [c]"."""
    t = [f"[{x}]" for x in tags]
    return t[0] if len(t) == 1 else ", ".join(t[:-1]) + " or " + t[-1]


def spatial_mechanical(s, a):
    """The spatial reads under a page's mechanical read: its own ban findings, the glass coverage,
    the CSS tier's bodies, the receded pose, the phases, the per-line contrast per pass with every
    failing line, and each host's drawn level and environment ring against the dead band in every
    state, named by the states it fell in."""
    extra, sch = spatial_ban(a), a.get("schemes") or {}
    if extra is None:
        P("Spatial reads: **none** — this audit predates them.\n")
        return
    P(f"Spatial ban findings (`banSubsetSpatial`): {len(extra)}.\n")
    for f in extra[:20]:
        P(f"- `{f['kind']}` {f.get('property')} `{md(str(f.get('value')))}`"
          + (f" ({f['role']})" if f.get("role") else "") + f" on `{md(f.get('selector') or '')}`, "
          f"text “{md(f.get('text') or '')}”, seen {', '.join(f.get('seen', []))}")
    if extra:
        P("")
    cov = [(x, (sch.get(x) or {}).get("glassCoverage")) for x in ("light", "dark")]
    P("Glass coverage of the first viewport: "
      + ", ".join(f"{x} {c['fraction']:.3f} ({c['hosts']} host(s))" if c else f"{x} unread"
                  for x, c in cov) + ".\n")
    c = a.get("cssTier") or {}
    body = lambda gs: ", ".join(f"`{g['id']}` {g.get('renderer')}/{g.get('cssBody')}"
                                for g in gs or [])
    P(f"CSS tier (`?tier=css`): {c.get('status', 'unread')}"
      + (f"; groups {body(c.get('groups'))}" if c.get("groups") else "")
      + (f"; with the menu open {body(c.get('menuGroups'))}" if c.get("menuGroups") else "") + ".")
    r = a.get("receded") or {}
    P(f"Receded pose: {r.get('status', 'unread')}, windowActivation {r.get('windowActivation')}.")
    ph = [(x, (sch.get(x) or {}).get("phases")) for x in ("light", "dark")]
    P("Phases: " + ("none offered (`phases: null`)" if not a.get("phasesHook") else
                    "; ".join(f"{x} " + (", ".join(str(i) for i in p["ids"]) if p and p.get("ids")
                                         else f"unread ({(p or {}).get('error')})")
                              for x, p in ph)) + ".\n")
    reads = line_reads(a)
    if reads:
        P("Text on glass per line box, glyphs suppressed (the worst line by its floor):\n")
        P("| pass | lines passing | worst line | states |\n|---|---|---|---|")
        for where, x in reads:
            w = x.get("worst")
            P(f"| {where} | {x['pass']}/{x['lines']} | "
              + (f"{w['ratio']} against {w['floor']} ({w['state']}, {w['nodeId']})" if w else "—")
              + f" | {', '.join(x.get('states') or [])} |")
        P("")
    # One entry per failing line of text, however many states it failed in: the same label on the
    # same surface usually fails for one reason, and the states it failed in are the evidence.
    grouped = {}
    for where, f in failing_lines(a):
        g = grouped.setdefault((f["nodeId"], f.get("text") or "", f["line"]), [])
        g.append((where, f))
    for (node, text, _), hits in list(grouped.items())[:40]:
        where, w = min(hits, key=lambda h: h[1]["ratio"] / h[1]["floor"])
        P(f"- failing line on {node}: “{md(text)}”, worst {w['ratio']} against {w['floor']} "
          f"({where} `{w['state']}`, box {w['box']}, ink {w['ink']} alpha {w.get('inkAlpha')} on "
          f"ground {w['ground']}); failed in {len(hits)} state(s): "
          + ", ".join(f"{x} `{f['state']}`" for x, f in hits))
    if len(grouped) > 40:
        P(f"- and {len(grouped) - 40} more failing line(s), each in the audit's `lineContrast.fails`")
    if grouped:
        P("")
    hosts = {}
    for where, x in host_levels(a):
        h = hosts.setdefault(x["nodeId"], {"role": x.get("role"), "label": x.get("label"),
                                           "in": [], "ring": [], "inBand": [], "ringBand": [],
                                           "states": 0})
        h["states"] += 1
        if x["inside"]["mean"] is not None:
            h["in"].append(x["inside"]["mean"])
        if x["ring"]["mean"] is not None:
            h["ring"].append(x["ring"]["mean"])
        if x["inside"]["inDeadBand"]:
            h["inBand"].append(where)
        if x["ring"]["inDeadBand"]:
            h["ringBand"].append(where)
    if hosts:
        band = ((sch.get("light") or {}).get("hostLuminance") or {}).get("band") or [0.39, 0.49]
        P(f"Each host's drawn level (inside its box) and the environment in a ring beside it, mean "
          f"encoded luminance over every state read, and the states in which each fell in the "
          f"dead band ({band[0]}–{band[1]}):\n")
        P("| host | role | inside | inside in the band | ring | ring in the band |"
          "\n|---|---|---|---|---|---|")
        span = lambda v: "—" if not v else (f"{min(v):.3f}" if min(v) == max(v)
                                            else f"{min(v):.3f}–{max(v):.3f}")
        states = lambda hit, n: ("none" if not hit else f"every state read ({n})" if len(hit) == n
                                 else ", ".join(hit))
        for nid, h in hosts.items():
            P(f"| {nid} “{md(h['label'] or '')}” | {h['role'] or '—'} | {span(h['in'])} | "
              f"{states(h['inBand'], h['states'])} | {span(h['ring'])} | "
              f"{states(h['ringBand'], h['states'])} |")
        P("")


def fmt(v, spec="{:.2f}"):
    return "—" if v is None else spec.format(v)


def cell(v):
    return "—" if v is None else ("1" if v else "0")


def md(s):
    return str(s).replace("|", "/").replace("\n", " ")


# ---------- report ----------

out = []
P = out.append
if SPATIAL:
    P("# Materialist spatial-register pages — the panel, the audit and the verdict\n")
    P("The pre-registered panel is " + ", ".join(EXPECTED_RATERS) + ". Missing or partial members "
      f"keep every verdict provisional. The rulebook is the spatial register's, {N_RULES} rules "
      f"keyed s1 to s{N_RULES}, each printed with what it is to the six's rulebook: `= rN` repeats "
      "instrument rule rN verbatim, `~ rN` adapts it, `new` is the register's own. Two counts of "
      f"{N_RULES} print for every page: the **panel-only** count and the **assigned** count (the "
      f"panel on the {len(PANEL_KEYS)} capture-visible rules, and "
      + (", ".join(label(k) for k in ASSIGNED) or "no rule") + " from the audit and the source "
      "review, as the spec declared before any capture existed). The pass line uses the assigned "
      f"count: every {either(gr.FATAL_TAGS)} rule holding, at least {HOLD_FLOOR} of {N_RULES} "
      "(88 %), zero diagnostics, zero findings on both ban lists, every text line on glass passing "
      "in every state read, and no clause UNREAD.\n")
else:
    P("# Materialist demos — the panel, the audit and the verdict\n")
    P("The pre-registered panel is " + ", ".join(EXPECTED_RATERS) + ". Missing or partial members "
      "keep every verdict provisional. Two counts of 25 print for every demo: the **panel-only** "
      "count (the 2.3 panel's pre-registered reading, comparable with its figures) and the "
      "**assigned** count (the panel on the 22 capture-visible rules, and r18, r19 and r23 from the "
      "audit and the source review, as the spec declared before any capture existed). The pass "
      "line uses the assigned count.\n")
P(f"Raters: {len(RATERS)}" + (f" ({', '.join(RATERS)})" if RATERS else "") + ". "
  f"Demos with a rule file: {sum(1 for s in COVERED if raters_of(s))} of {len(gr.SLUGS)}. "
  f"Audits: {len(audits)} of {len(gr.SLUGS)}. Source reviews: {len(reviews)} of {len(gr.SLUGS)}. "
  f"Rules: {len(RULE_KEYS)}, of which {len(FATAL_KEYS)} are tagged "
  f"{either(gr.FATAL_TAGS)} and fatal to the verdict. Rules digest "
  f"`{gr.PINNED[:16]}…` ("
  + ("the spatial rulebook's pin" if SPATIAL else "the 2.3 panel's") + ").\n")
if SKIPPED:
    P("Not read, for recording another rulebook: " + ", ".join(f"`{x}`" for x in SKIPPED) + ".\n")
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
      f"{_and(ASSIGNED)} the assigned reading follows after `→`, and that is the answer the "
      "assigned count uses.\n")
    P("| rule | tag | " + " | ".join(f"`{s}`" for s in COVERED) + " |")
    P("|---|---|" + "---|" * len(COVERED))
    for k in RULE_KEYS:
        cells = []
        for s in COVERED:
            held, yes, n = majority(s, k)
            c = "—" if held is None else f"{1 if held else 0} ({yes}/{n})"
            if panel_unread(s, k):
                c = f"UNREAD ({len(unread_votes(s, k))}/{n} unread)"
            if k in ASSIGNED:
                c += " → " + cell(assigned(s)[k][0])
            cells.append(c)
        P(f"| {label(k)} | {RULE_TAG[k]} | " + " | ".join(cells) + " |")
    P("")
    P(f"| demo | panel-only (of {N_RULES}) | assigned (of {N_RULES}) | unread in the assigned count |"
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
          f"**{len(d['panelHeld'])} of {N_RULES}**. Assigned: **{len(d['held'])} of {N_RULES}**"
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
        P(f"| {label(k)} | {cell(held)} | "
          f"{'—' if m_held is None else f'{cell(m_held)} ({yes}/{n})'} | {md(ev) or '—'} |")
    P("")
    failed_panel = [k for k in d["failed"] if k in PANEL_KEYS]
    if failed_panel:
        P("Capture-visible rules that failed:\n")
        if SPATIAL:
            P("| rule | tag | yes/n | no-votes marked unread | a rater that said no | its evidence |"
              "\n|---|---|---|---|---|---|")
        else:
            P("| rule | tag | yes/n | a rater that said no | its evidence |\n|---|---|---|---|---|")
        for k in failed_panel:
            no = [r for r, val in votes(s, k) if val == 0]
            ev = next((ratings[r][s]["evidence"].get(k) for r in no
                       if ratings[r][s]["evidence"].get(k)), "")
            _, yes, n = d["majority"][k]
            if SPATIAL:
                # The rater prompt asks a no that stands on a state nobody captured to say so.
                unread = len(unread_votes(s, k))
                P(f"| {label(k)} | {RULE_TAG[k]} | {yes}/{n} | {unread} | {no[0] if no else '—'} | "
                  f"{md(ev) or '—'} |")
            else:
                P(f"| {k} | {RULE_TAG[k]} | {yes}/{n} | {no[0] if no else '—'} | {md(ev) or '—'} |")
        P("")
    if SPATIAL and d["panelUnread"]:
        P("Rules the panel read UNREAD — most raters said the state the rule needs was neither "
          "captured nor recorded; each blocks the verdict until that state is read:\n")
        P("| rule | tag | unread/n | what the raters said was missing |\n|---|---|---|---|")
        for k in d["panelUnread"]:
            said = [f"{r}: {ratings[r][s]['evidence'][k].strip()[len('unread:'):].strip()}"
                    for r in unread_votes(s, k)]
            P(f"| {label(k)} | {RULE_TAG[k]} | {len(unread_votes(s, k))}/{len(votes(s, k))} | "
              f"{md('; '.join(said)) or '—'} |")
        P("")
    if SPATIAL and d.get("panelUnreadAssigned"):
        P("On an assigned rule a rater majority said \"unread:\" — the audit or the source review is the "
          "answer there and the panel's answer prints beside it, so this names a capture the panel "
          "lacked and does not block: "
          + ", ".join(f"{label(k)} ({len(unread_votes(s, k))}/{len(votes(s, k))} unread)"
                      for k in d["panelUnreadAssigned"]) + ".\n")
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
        if SPATIAL:
            spatial_mechanical(s, a)
    P("Verdict, clause by clause:\n")
    P("| clause | met | on |\n|---|---|---|")
    pending = "UNREAD" if SPATIAL else "not yet readable"
    for name, ok, note in v["clauses"]:
        P(f"| {name} | {'yes' if ok else ('no' if ok is False else pending)} | {md(note)} |")
    P("")
    if SPATIAL:
        unread = [name for name, ok, _ in v["clauses"] if ok is None]
        P(f"**{s}: " + ("PASSES" if v["pass"] else
                        "FAILS" + (f" (and UNREAD: {', '.join(unread)})" if unread else "")
                        if v["failed"] else
                        f"BLOCKED — UNREAD: {', '.join(unread)}") + "**\n")
    else:
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
        P(f"| {label(k)} | {RULE_TAG[k]} | {fmt(a)} | {n} | "
          f"{', '.join(str(u) for u in used) or '—'} | {note} |")
    P("")

# ---------- the line ----------

passing = [s for s in gr.SLUGS if s in COVERED and verdict(s)["pass"]]
not_read = [s for s in gr.SLUGS if s not in COVERED]
fatal = [s for s in gr.SLUGS if s in COVERED and readings(s)["fatalFailed"]
         and not panel_missing(s)]
unreadable = [s for s in gr.SLUGS if s not in COVERED or not verdict(s)["readable"]]
P("## The line\n")
if SPATIAL:
    failing = [s for s in gr.SLUGS if s in COVERED and verdict(s)["failed"]]
    blocked = [s for s in gr.SLUGS if s in COVERED and not verdict(s)["failed"]
               and not verdict(s)["pass"]]
    P(f"**{len(passing)} of {len(gr.SLUGS)} pages pass**"
      + (f" ({', '.join('`' + s + '`' for s in passing)})" if passing else "")
      + (f"; {len(failing)} fail ({', '.join(failing)})" if failing else "")
      + (f"; {len(blocked)} blocked by an UNREAD clause or an incomplete panel "
         f"({', '.join(blocked)})" if blocked else "")
      + (f"; {len(not_read)} not read at all" if not_read else "") + ". "
      + (f"**Stop and diagnose**: {len(fatal)} page(s) fail an {either(gr.FATAL_TAGS)} rule "
         f"({', '.join(fatal)}). Classify each failure by cause before anything is rewritten — the "
         "rule's text, a runtime seam, the instrument or the maker; only the first is the "
         "register's, and then the next step is a rewrite of its conditions, not a third page."
         if fatal else
         f"No page fails an {either(gr.FATAL_TAGS)} rule on a complete panel.")
      + " Two pages are a bounded demonstration that the conditions can be met; whether the skill "
      "teaches and chooses the register is the eval's claim. The user's eye is not in this report.")
    res = "\n".join(out)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    open(outp, "w", encoding="utf-8").write(res + "\n")
    print(res)
    sys.exit(0)
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
