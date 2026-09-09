#!/usr/bin/env python3
"""The panel's rule reading for the six Liquid Glass demos (spec: docs/doperpowers/specs/
2026-09-10-liquid-glass-into-the-skill.md, "C. The audit", reading 1).

    python3 glass-rules.py prompt <rater> [<slug>,…]   one rater's prompt over the demos with captures
    python3 glass-rules.py rules                       the 25 items with their tags

The items are the twenty-five rules of `skills/designer/references/liquid-glass.md` §9, parsed out
of the reference itself so the panel rates the list the skill actually ships, and pinned by
RULES_SHA256 so an edit to the reference cannot silently change what a recorded rating meant. The
briefs are read from `glass-demos.mjs`, which is where the builders' briefs live; nothing here
duplicates them.

A rater reads all six demos before rating any of them, in a demo order shuffled by a seed derived
from its name and recorded in every file it writes — the quality instrument's convention
(`settling/rubric.py`), for the same reason: the order a page is seen in is a rating effect, and
one that is recorded can be estimated later. It sees the capture files and the slugs only. Output,
one file per (rater, demo):

    docs/research/data/2026-09-10-liquid-glass-demos/rules/<rater>/<slug>.json
    {"rater": "…", "slug": "…", "order": ["slug", …],
     "rules": {"r1": 0|1, …, "r25": 0|1}, "evidence": {"r1": "…", …},
     "quality": {"a1": 1–7, …, "e1": 1–7}}

The quality items are the instrument's own a1–a4, d1 and e1 on their own scales, rated on the same
captures by the same panel, so the demos land beside the settling arms on the same instrument
rather than on a scale invented here. `glass-rules-analyze.py` reads these files and the mechanical
`audit.json` beside each demo and writes the verdict.
"""
import os, sys, re, json, random, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, os.path.join(HERE, "settling"))
import rubric                      # the quality instrument's items, statements and scales

REFERENCE = os.path.join(REPO, "skills/designer/references/liquid-glass.md")
DEMOS_JS = os.path.join(HERE, "glass-demos.mjs")
# The demo directory and the wave's data directory, both overridable so a dry run of the prompt or
# the report can be pointed at scratch without writing into the committed evidence.
DEMOS = os.environ.get("GLASS_DEMOS") or os.path.join(REPO, "apps/demos")
DATA = (os.environ.get("GLASS_DATA")
        or os.path.join(REPO, "docs/research/data/2026-09-10-liquid-glass-demos"))

# The captures `glass-audit.mjs` writes beside a demo, in the order a rater should read them, each
# with the sentence that says what it shows. A page that offers no menu and a run that could not
# reach the runtime leave some of them absent, and the prompt names only the ones on disk.
CAPTURES = [
    ("shot-fv.png", "the first viewport, 1440 × 900 at scroll 0"),
    ("shot-full.png", "the full page"),
    ("tile-2.png", "the second viewport at native resolution"),
    ("tile-3.png", "the third viewport at native resolution"),
    ("shot-menu.png", "the page with its menu or platter open"),
    ("shot-reduced.png", "the first viewport with reduced transparency asked of the runtime"),
]
QUALITY_KEYS = ["a1", "a2", "a3", "a4", "d1", "e1"]
QUALITY_ITEMS = [it for it in rubric.ITEMS if it[0] in QUALITY_KEYS]

# The digest of the twenty-five rules as parsed from §9 — the key, the tag and the text of each.
# It is pinned rather than merely computed because a rating file records `r7` and not the rule's
# words: if the reference's list is edited or renumbered, every rating already collected means
# something else. A mismatch is a decision to make and record, not a number to update in passing.
RULES_SHA256 = "fe05c2bd00c10c60c7936351642d90dd7b8a4bcd8d26a25a99c040ca84c7d215"

_RULE_START = re.compile(r"^\s*(\d{1,2})\.\s+`\[([a-z]+)\]`\s+(.*)$")
_CITATION = re.compile(r"\s*\((?:\*secondary\*:\s*)?\[([^\]]+)\]\[[^\]]+\]\)\s*$")


def parse_rules(path=None):
    """The 25 rules of §9 as (key, tag, text, source): the numbered list items under the section
    heading, unwrapped to one line, with the trailing citation link taken off the text and kept as
    the source. Anything but exactly 25 items means the section moved and is an error, not a
    shorter rubric."""
    path = path or REFERENCE
    lines = open(path, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("## 9."))
    except StopIteration:
        raise SystemExit(f"glass-rules: no '## 9.' section in {path}")
    items = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        m = _RULE_START.match(line)
        if m:
            items.append([int(m.group(1)), m.group(2), m.group(3).strip()])
        elif items and line.startswith("   ") and line.strip():
            items[-1][2] += " " + line.strip()      # a wrapped continuation of the item above
        elif items and line.strip():
            break                                    # the prose that closes the list
        # Anything else is the section's opening prose or a blank line, and is passed over.
    out = []
    for n, tag, text in items:
        c = _CITATION.search(text)
        source = c.group(1) if c else None
        out.append((f"r{n}", tag, _CITATION.sub("", text).strip(), source))
    if len(out) != 25 or [k for k, *_ in out] != [f"r{n}" for n in range(1, 26)]:
        raise SystemExit(
            f"glass-rules: {path} §9 gave {len(out)} items, not r1–r25; the section moved")
    return out


def digest(rules):
    """The pinned digest's input: key, tag and text of every rule, tab-separated, one per line."""
    return hashlib.sha256(
        "\n".join(f"{k}\t{t}\t{x}" for k, t, x, _ in rules).encode("utf-8")).hexdigest()


def load_rules(check=True, path=None):
    rules = parse_rules(path)
    got = digest(rules)
    if check and RULES_SHA256 not in ("PLACEHOLDER", got):
        raise SystemExit(
            f"glass-rules: {os.path.relpath(path or REFERENCE, REPO)} §9 has changed.\n"
            f"  pinned  {RULES_SHA256}\n  found   {got}\n"
            "Ratings already collected are keyed r1–r25 against the pinned list. Re-pin "
            "RULES_SHA256 in glass-rules.py with the reason, and say in the wave's spec what the "
            "already-collected files now stand for.")
    return rules


RULES = load_rules()
TAGS = sorted({t for _, t, _, _ in RULES})
# The tags whose failure the spec's pass line treats as fatal: a page failing one of these is not
# this language whatever else it does.
FATAL_TAGS = ["layer", "material"]

_JS_STR = r'"(?:[^"\\]|\\.)*"'
_BRIEF_LINE = re.compile(rf"^\s*({_JS_STR}):\s*({_JS_STR}),\s*$")
_TAIL_LINE = re.compile(rf"^const TAIL\s*=\s*({_JS_STR});\s*$")


def load_briefs(path=None):
    """The six briefs and the shared tail, read out of `glass-demos.mjs` — the builders' prompt
    generator is the one place a brief is written, and the rater must see the same words the
    builder saw. Returns the slugs in the file's order and the full brief text per slug."""
    path = path or DEMOS_JS
    text = open(path, encoding="utf-8").read()
    body = text.split("const BRIEFS = {", 1)[1].split("\n};", 1)[0]
    briefs = {}
    for line in body.splitlines():
        m = _BRIEF_LINE.match(line)
        if m:
            briefs[json.loads(m.group(1))] = json.loads(m.group(2))
    tail = next((json.loads(m.group(1)) for m in map(_TAIL_LINE.match, text.splitlines()) if m), "")
    if len(briefs) != 6:
        raise SystemExit(f"glass-rules: {path} gave {len(briefs)} briefs, not 6")
    return {s: b + tail for s, b in briefs.items()}


BRIEFS = load_briefs()
SLUGS = list(BRIEFS)


def captures(slug):
    """The capture files that exist beside a demo, as (path, what it shows), in reading order."""
    d = os.path.join(DEMOS, slug)
    return [(os.path.join(d, f), what) for f, what in CAPTURES if os.path.exists(os.path.join(d, f))]


def seed_for(rater):
    return int(hashlib.sha256(f"glass-rules|{rater}".encode()).hexdigest()[:8], 16)


def order_for(rater, slugs):
    """The rater's demo order: a shuffle of the demos it rates, seeded by its name so the same
    rater always reads them in the same order and the order is reproducible from the name alone."""
    order = list(slugs)
    random.Random(seed_for(rater)).shuffle(order)
    return order


def available(slugs=None):
    """The demos to rate: those with at least one capture on disk. A slug asked for by name and
    carrying no capture is an error — there is nothing to rate — while the default list simply
    passes over a demo that has not been built or audited yet."""
    if slugs:
        for s in slugs:
            if s not in BRIEFS:
                raise SystemExit(f"glass-rules: unknown demo {s!r}; the six are {', '.join(SLUGS)}")
            if not captures(s):
                raise SystemExit(f"glass-rules: {s} has no captures under {os.path.join(DEMOS, s)}")
        return list(slugs)
    return [s for s in SLUGS if captures(s)]


def prompt(rater, slugs=None):
    """One rater's prompt over the demos: the blinded instruction, then a section per demo in the
    rater's own order carrying the brief and the captures, then the 25 rules, the six quality items
    and the shape of the file to write per demo."""
    order = order_for(rater, available(slugs))
    if not order:
        raise SystemExit(f"glass-rules: no demo under {DEMOS} carries a capture; build the demos "
                         "and run glass-audit.mjs over them before asking for a rater's prompt")
    out = os.path.join(DATA, "rules", rater, "<slug>.json")
    L = [
        "You are a blinded rater for a design experiment. Each page below was built by a different "
        "builder from its own brief, under one design skill; you do not know which builder made "
        "which and must not try to find out. Rate from the captures alone: open nothing else under "
        f"`{DEMOS}` — not the page's HTML, not its DESIGN.md, not its audit.json — and do not run "
        "git. What the page's own notes claim about itself is not evidence; what the captures show "
        "is.",
        "",
        f"The {len(order)} pages, in the order to read and rate them, each with the brief it was "
        "built from and the captures taken of it. Read every capture of every page once before "
        f"rating any page: the {len(order)} pages are the frame for every rating.",
        "",
    ]
    for n, slug in enumerate(order, 1):
        caps = captures(slug)
        L += [f"### {n}. {slug}", "", f'Brief (verbatim): "{BRIEFS[slug]}"', "", "Captures:"]
        L += [f"- `{p}` — {what}" for p, what in caps]
        L.append("")
    L += [
        "Then answer, for every page in that order, the 25 rules below. Each is yes or no on the "
        "rendered page: **1** the rule holds on this page, **0** it does not. Judge the page in "
        "front of you rather than the page you would have built, and answer from the captures you "
        "were given — a rule you cannot see holding in them does not hold. Two of the rules name "
        "system primitives the web does not have, the scroll edge effect (r15) and the background "
        "extension effect with safe-area insets (r21): a page holds them by building the "
        "equivalent, and a page that skipped them has failed them rather than been excused from "
        "them. The tag in brackets is the rule's kind; it does not change how you answer.",
        "",
    ]
    L += [f"- {k} [{t}]: {x}" for k, t, x, _ in RULES]
    L += [
        "",
        "Then rate every page on the six quality items below, on the scales given, in the same "
        "page order. Rate structure, craft and fit as a designer handing the work to the client "
        "who wrote the brief; use the whole scale, and judge each page against its own brief "
        "rather than against another page's. These six take no evidence.",
        "",
    ]
    L += [f"- {k} ({block}) [{scale}]: {text}" for k, block, text, scale in QUALITY_ITEMS]
    shape = {
        "rater": rater, "slug": "<slug>", "order": order,
        "rules": {k: "<0|1>" for k, *_ in RULES},
        "evidence": {k: "<clause>" for k, *_ in RULES},
        "quality": {k: "<1–7>" for k in QUALITY_KEYS},
    }
    L += [
        "",
        "For each of the 25 rules give one short clause of evidence — what on the page decided the "
        "answer, naming the surface or the region you read it from. No evidence for the quality "
        "items.",
        "",
        f"Write one file per page, JSON, to `{out}` with `<slug>` the page's slug above (create the "
        "directories; overwrite the file), each in exactly this shape, numbers as JSON numbers and "
        "`order` copied as it stands:",
        json.dumps(shape, ensure_ascii=False),
        "",
        "Then report in under 120 words: which pages held the most and the fewest rules, any rule "
        "no page held, and any rule you found you could not answer from the captures. Do not "
        "modify anything else.",
    ]
    return "\n".join(L)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "prompt" and len(sys.argv) > 2:
        args = sys.argv[3:]
        slugs = [s for a in args for s in a.split(",") if s]
        print(prompt(sys.argv[2], slugs or None))
    elif cmd == "rules":
        for k, t, x, src in RULES:
            print(f"{k}\t[{t}]\t{x}" + (f"  ({src})" if src else ""))
        counts = ", ".join(f"{t} {sum(1 for _, tg, _, _ in RULES if tg == t)}" for t in TAGS)
        print(f"\n25 rules; by tag: {counts}. Fatal tags: {', '.join(FATAL_TAGS)}.")
        print(f"digest {digest(RULES)}")
    else:
        print(__doc__)
