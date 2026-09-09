#!/usr/bin/env python3
"""The quality instrument's rubric (spec: 2026-09-09-quality-instrument.md): the items, the brief-fit
statements, the rater prompt, and the record shapes every other script reads.

    python3 rubric.py prompt <brief> <rater> [<seed>] [--retest]   one rater's prompt for one brief
    python3 rubric.py prompt <brief> <rater> --only e1             the revised item alone, to <brief>-revised.json
    python3 rubric.py items [<brief>]                              the item list for a brief
    python3 rubric.py anchor                                       the anchor set's page ids

A rater rates every page of one brief with all eight in view, in a page order shuffled by a seed
derived from (rater, brief, retest) and recorded in the output. It sees four captures per page and
random ids only. Output, one file per (rater, brief[, retest]):

    figma-design-workspace/settling/rubric/<rater>/<brief>[-retest].json
    {"rater": "…", "brief": "…", "seed": 1234, "order": ["id", …],
     "pages": {"<id>": {"a1": 1–7, …, "c1": 0|1, …, "d1": 1–7, "e1": 1–7, "evidence": {"a1": "…", …}}}}

The user's ratings (rate.py /rubric) go to figma-design-workspace/settling/rubric-human.jsonl, one
line per page: {"id", "brief", "pass": 1|2, "a1"…"a4", "d1", "e1", "ms", "at"} — HUMAN_KEYS only, and
pass 2 is the retest of human_retest_ids().
"""
import os, sys, json, random, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rate

SEVEN = "1 do not agree at all … 7 fully agree"
THREE = "0 absent; 1 present but deficient; 2 present and adequate"
BINARY = "0 not seen, 1 seen"
D1 = ("7 deliver as it is; 5 cosmetic fixes only (tokens, spacing, copy); 3 structural rework (a region "
      "added, moved or re-formed); 1 start over; 6, 4 and 2 between")
# e1's first wording (superseded 2026-09-10 by the one pre-registered revision; kept for the record —
# the first pass's e1 is reported beside the revised one as e1_v1):
E1_V1 = "1 this page looks like nothing I have seen for this kind of brief; 7 this is the default page for this kind of brief"
E1_V1_TEXT = "How conventional is this page for its brief?"
E1 = ("1 departs from the standard layout for its kind in its main structure; 4 the standard shell with one "
      "departure; 7 the standard layout for its kind throughout")
E1_TEXT = ("How closely does this page follow the standard layout for its kind of page — for a console, a left "
           "sidebar or top tabs, a row of summary tiles, then tables or panels; for a public page, a hero, a row "
           "of three feature cards, then stacked sections? Judge the structure, not the colours or the type.")
# The brief-independent items in rating order: (key, block, statement, scale). The b-items and the
# tone item come from BRIEF_FIT per brief and are spliced in by items_for().
ITEMS = [
    ("a1", "aesthetics", "Everything goes together on this page.", SEVEN),
    ("a2", "aesthetics", "The layout is pleasantly varied.", SEVEN),
    ("a3", "aesthetics", "The colour composition is attractive.", SEVEN),
    ("a4", "aesthetics", "The layout appears professionally designed.", SEVEN),
    ("b*", "brief fit", None, THREE),
    ("c1", "defects", "Content clipped or cut off by its container.", BINARY),
    ("c2", "defects", "Text too small or too faint to read at this size.", BINARY),
    ("c3", "defects", "An empty, placeholder or broken region (an image slot without an image, lorem, template text).", BINARY),
    ("c4", "defects", "Spacing or alignment inconsistent between like elements.", BINARY),
    ("c5", "defects", "The layout is wider than the viewport, or scrolls sideways.", BINARY),
    ("d1", "deliverability", "What would this page need before you delivered it to the client who wrote the brief?", D1),
    ("e1", "conventionality", E1_TEXT, E1),
]
# Brief fit: one fact per item on the 0–2 presence scale, and where the brief states a tone, one
# tone item on the 7-point scale (spec, The rubric, B).
BRIEF_FIT = {
    "rail": (["Every live train's position and state is visible without scrolling.",
              "Delay exceptions are separated from routine traffic and placed before it.",
              "Crew hours appear as values and times.",
              "Maintenance windows appear as values and times."], None),
    "fleet": (["Open defects are listed by vehicle.",
               "Overdue inspections are visibly distinguished from the rest.",
               "Parts on order carry an expected date or a status each.",
               "The workshop's day (bays, jobs, times) is readable as a schedule."], None),
    "pharmacy": (["Stock levels by drug are a table with quantities and a par or reorder level.",
                  "Expiring lots are shown as their own set.",
                  "Controlled-substance counts are shown as their own set.",
                  "Pending orders carry a status each."], None),
    "compare": (["The three suppliers are compared on the same criteria in one structure.",
                 "Price per axle, lead time, warranty and on-site fitting are each visible for each supplier.",
                 "There is a control to pick a supplier.",
                 "The page shows that a pick is recorded."], None),
    "rebate": (["Whether a resident qualifies is stated within the first screen.",
                "The rebate's value is stated as amounts with its conditions.",
                "The approved installers are listed.",
                "The one application form is reachable from the page."], None),
    "library": (["The sign-up is within the first screen.",
                 "Weekly book lists appear as lists of titles.",
                 "An event calendar with dates is on the page."],
                "The page reads as for children and their parents without being garish."),
    "hardware": (["Featured tools are shown with prices.",
                  "The goods are pictured (a photograph or a drawing).",
                  "Seasonal project guides are on the page.",
                  "In-store pickup is explained."],
                 "The page reads as practical and trustworthy rather than startup-slick."),
}
SEVEN_KEYS = ["a1", "a2", "a3", "a4", "t1", "d1", "e1"]   # ordinal 1–7 (t1 only where the brief has a tone)
THREE_KEYS = ["b1", "b2", "b3", "b4"]                     # ordinal 0–2 (b4 only where the brief has four facts)
BINARY_KEYS = ["c1", "c2", "c3", "c4", "c5"]              # nominal 0/1
EVIDENCE_KEYS = THREE_KEYS + ["t1"] + BINARY_KEYS + ["d1"]  # a model rater gives evidence on these only
HUMAN_KEYS = ["a1", "a2", "a3", "a4", "d1", "e1"]         # the user rates the taste-bearing items only
HUMAN_RETEST_PER_BRIEF = 2                                # pages the user rates a second time, per anchor brief


def scale_kind(key):
    """"seven", "three" or "binary": which distance the reliability statistics use for an item."""
    return "seven" if key in SEVEN_KEYS else "three" if key in THREE_KEYS else "binary"


ANCHOR_BRIEFS = ["pharmacy", "library"]
CAPTURES = ["shot-fv.png", "tile-2.png", "tile-3.png", "shot-full.png"]


def items_for(brief, keys=None):
    """The brief's items in rating order: the b-items (and t1) spliced in from BRIEF_FIT; `keys`
    restricts to a subset (the user's form)."""
    facts, tone = BRIEF_FIT[brief]; out = []
    for k, block, text, scale in ITEMS:
        if k == "b*":
            out += [(f"b{n + 1}", block, f, THREE) for n, f in enumerate(facts)]
            if tone:
                out.append(("t1", "brief fit", tone, SEVEN))
        else:
            out.append((k, block, text, scale))
    return [it for it in out if keys is None or it[0] in keys]


def cells_for(brief):
    return sorted([c for c in json.load(open(rate.MANIFEST))["cells"] if c["brief"] == brief], key=lambda c: c["id"])


def seed_for(rater, brief, retest=False):
    return int(hashlib.sha256(f"{rater}|{brief}|{'retest' if retest else 'first'}".encode()).hexdigest()[:8], 16)


def order_for(brief, seed):
    ids = [c["id"] for c in cells_for(brief)]
    random.Random(seed).shuffle(ids)
    return ids


def captures(i):
    d = os.path.join(rate.WS, "builds", i)
    return [os.path.join(d, f) for f in CAPTURES if os.path.exists(os.path.join(d, f))]


def prompt(brief, rater, seed=None, retest=False, only=None):
    """A rater's prompt for one brief. `only` names the items of a pre-registered wording revision:
    the same pages in the first pass's order, the first viewport and the full page only (the
    revised item is a structural read; the tiles serve the c-items), no evidence, written to
    <brief>-revised.json, and analyze.py swaps the revised value in over the first pass's."""
    seed = seed_for(rater, brief, retest) if seed is None else int(seed)
    order = order_for(brief, seed)
    out = os.path.join(rate.WS, "rubric", rater, brief + ("-retest" if retest else "-revised" if only else "") + ".json")
    ev = cells_for(brief)[0]["eval"]
    if only:
        its = [it for it in items_for(brief) if it[0] in only]
        L = ["You are a blinded rater for a design experiment. The pages below were built from one brief by different builders; you do not know which builder made which and must not try to find out. Open nothing under the build directories except the capture files named per page. Do not run git.",
             "", f'Brief (verbatim): "{rate.brief_text(ev)}"', "",
             "Pages, in the order to read them, each with its first viewport (1440 × 900) and its full page. Read both captures of every page once before rating any page; the eight pages are the frame for every rating.", ""]
        for i in order:
            d = os.path.join(rate.WS, "builds", i)
            L.append(f"- {i}: " + ", ".join(os.path.join(d, f) for f in ("shot-fv.png", "shot-full.png") if os.path.exists(os.path.join(d, f))))
        L += ["", f"Then rate every page on the item{'s' if len(its) > 1 else ''} below, in the page order above. Use the whole scale.", ""]
        for k, block, text, scale in its:
            L.append(f"- {k} ({block}) [{scale}]: {text}")
        shape = {k: ("<1–7>" if scale_kind(k) == "seven" else "<0–2>" if scale_kind(k) == "three" else "<0|1>") for k, *_ in its}
        L += ["", "Write the result as JSON to", f"`{out}` (create the directory; overwrite the file), in exactly this shape, numbers as JSON numbers:",
              json.dumps({"rater": rater, "brief": brief, "seed": seed, "order": order, "revised": [k for k, *_ in its], "pages": {"<id>": shape}}, ensure_ascii=False),
              "", "Then report in one sentence which pages scored highest and lowest. Do not modify anything else."]
        return "\n".join(L)
    L = ["You are a blinded rater for a design experiment. The pages below were built from one brief by different builders; you do not know which builder made which and must not try to find out. Open nothing under the build directories except the capture files named per page. Do not run git.",
         "",
         f'Brief (verbatim): "{rate.brief_text(ev)}"',
         "",
         "Pages, in the order to read them. Each has up to four captures: the first viewport (1440 × 900 at scroll 0), the second and third viewports at native resolution (tile-2, tile-3; a short page has fewer), and the full page. Read every capture of every page once before rating any page; the eight pages are the frame for every rating.",
         ""]
    for i in order:
        L.append(f"- {i}: " + ", ".join(captures(i)))
    its = items_for(brief)
    L += ["", f"Then rate every page on the {len(its)} items below, in the page order above. Rate structure, craft and fit as a designer handing the work to the client who wrote the brief; use the whole scale, and judge each page against the brief, not against a page from another brief. The c-items are answered from the captures you were given; a clip you cannot see in them is not seen.", ""]
    for k, block, text, scale in its:
        L.append(f"- {k} ({block}) [{scale}]: {text}")
    ev_keys = [k for k, *_ in its if k in EVIDENCE_KEYS]
    shape = {k: ("<1–7>" if scale_kind(k) == "seven" else "<0–2>" if scale_kind(k) == "three" else "<0|1>") for k, *_ in its}
    shape["evidence"] = {k: "<clause>" for k in ev_keys}
    L += ["", f"For {', '.join(ev_keys)} give one short clause of evidence — what on the page decided the answer; no evidence for the other items. Write the result as JSON to",
          f"`{out}` (create the directory; overwrite the file), in exactly this shape:",
          json.dumps({"rater": rater, "brief": brief, "seed": seed, "order": order, "pages": {"<id>": shape}}, ensure_ascii=False),
          "", "Then report in under 120 words: the pages with the highest and lowest d1, and any item where the pages hardly differed. Do not modify anything else."]
    return "\n".join(L)


def anchor_ids():
    return [c["id"] for b in ANCHOR_BRIEFS for c in cells_for(b)]


def human_order(brief):
    """The user's page order for one anchor brief."""
    return order_for(brief, seed_for("human", brief))


def human_retest_ids():
    """The pages the user rates a second time, after the sixteen: a seeded pick per anchor brief,
    in a fresh seeded order (spec, Raters)."""
    picks = []
    for b in ANCHOR_BRIEFS:
        rng = random.Random(seed_for("human", b, retest=True)); ids = [c["id"] for c in cells_for(b)]
        picks += rng.sample(ids, HUMAN_RETEST_PER_BRIEF)
    random.Random(seed_for("human", "retest-order", retest=True)).shuffle(picks)
    return picks


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "prompt":
        retest = "--retest" in sys.argv
        only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
        a = [x for x in sys.argv[2:] if x not in ("--retest", "--only") and not (only and x == ",".join(only))]
        print(prompt(a[0], a[1], a[2] if len(a) > 2 else None, retest, only))
    elif cmd == "items":
        b = sys.argv[2] if len(sys.argv) > 2 else "library"
        for k, block, text, scale in items_for(b): print(k, block, "|", text, "|", scale)
    elif cmd == "anchor":
        print("\n".join(anchor_ids())); print("retest:", " ".join(human_retest_ids()))
    else:
        print(__doc__)
