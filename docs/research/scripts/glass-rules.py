#!/usr/bin/env python3
"""The panel's rule reading for the materialist demos, on either of two rulebooks (specs:
docs/doperpowers/specs/2026-09-27-materialist-proof.md, "B. The instrument", reading 2, and
2026-09-27-materialist-spatial-register.md, "B. The rulebook and the instrument").

    python3 glass-rules.py [--rules R] prompt <rater> [<slug>,…]   one rater's prompt over the
                                                                   demos with captures
    python3 glass-rules.py [--rules R] rules                       the items with their tags
    python3 glass-rules.py [--rules R] pin                         the section's digest and count

`--rules` names the rulebook: `instrument`, the default, or `spatial`. Everything from here to the
paragraph on the spatial rulebook is the instrument rulebook, as it stood before the second one
existed; with the default nothing it prints or writes has changed.

The items are the twenty-five rules of `docs/research/2026-09-10-liquid-glass-design-language.md`,
section "Rules a page can be checked against", parsed out of the memo itself and pinned by
RULES_SHA256 so an edit to the memo cannot silently change what a recorded rating meant. The 2.3
panel read the same list out of the designer's `references/liquid-glass.md` §9, which was never
merged; the digest below is the one that panel pinned, and it reproduces here from the memo, so the
twenty-five items this panel answers are word for word the twenty-five the 2.3 panel answered (only
the citations after each item differ, and they are not part of the digest).

The briefs are the 2.3 spec's "The six briefs", read out of
`docs/doperpowers/specs/2026-09-10-liquid-glass-into-the-skill.md`, with the shared tail this
initiative's spec replaced them with ("A. The six demos": the deliverable is a page of the vitrea
demo site rather than one served HTML file). A rater sees the words the maker saw; nothing here
duplicates them.

A rater reads all six demos before rating any of them, in a demo order shuffled by a seed derived
from its name and recorded in every file it writes, because the order a page is seen in is a rating
effect, and one that is recorded can be estimated later. It sees the capture files and the slugs
only. The captures are `glass-audit.mjs`'s, taken in both colour schemes, and they live outside the
repository (`figma-design-workspace/` is gitignored; the committed evidence is their hashes in each
demo's audit JSON). Output, one file per (rater, demo):

    docs/research/data/2026-09-27-materialist-proof/rules/<rater>/<slug>.json
    {"rater": "…", "slug": "…", "order": ["slug", …],
     "rules": {"r1": 0|1, …, "r25": 0|1}, "evidence": {"r1": "…", …}}

The 2.3 panel's quality items (a1 to a4, d1, e1) are dropped (this spec's Decision Log 4): their
scale's calibration round never ran. Three rules are read elsewhere as well, declared before any
capture existed (ASSIGNED below), but the panel still answers them blind and on the 2.3 panel's
instruction, so their answers stay comparable and print beside the assigned readings.
`glass-rules-analyze.py` reads these files, the audits and the source reviews, and writes the
verdict.

The spatial rulebook (`--rules spatial`) is the one the spatial-register pages are read on: the
numbered section "Rules a spatial-register page can be checked against" of
`docs/research/2026-09-27-glass-as-surface-prior-art.md`, items s1 to sN, each tagged. An item that
repeats an instrument rule carries its number after the tag, `(= r18)`, and must repeat that rule's
tag and words exactly, which is what makes the per-rule comparison with the six direct; the parser
refuses one that does not. An item that adapts one carries `(~ r15)` and is held to nothing but the
number. A table before the items (the rules the register replaces) is passed over. The section is
pinned by SPATIAL_RULES_SHA256 as the twenty-five are by RULES_SHA256; until that is set, `prompt`
refuses, and `pin` prints the digest to set it to. The briefs are the two quoted in the spatial
spec's "C. The two pages", each with the shared tail quoted there. The order, the seed and the yes/no
answer are the instrument panel's. Two things are wider, because the rulebook reads them: the rater
is handed the page's record (its `DESIGN.md`), which several rules ask a recorded value of, and the
spatial passes' captures of the states the rules name (the inner scrollers, the environment's
phases, the CSS tier, forced colours). Output goes to `docs/research/data/2026-09-27-materialist-
spatial-register/rules/<rater>/<slug>.json`, keyed s1 to sN and recording `"rules_set": "spatial"`;
the captures are read from `figma-design-workspace/materialist-spatial-register/captures`.

Two environment overrides point a dry run at scratch without writing into committed evidence:
GLASS_CAPTURES (default the selected rulebook's captures directory at the repository root) and
GLASS_DATA (default its data directory).
"""
import os, sys, re, json, random, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))

REFERENCE = os.path.join(REPO, "docs/research/2026-09-10-liquid-glass-design-language.md")
REFERENCE_SECTION = "## Rules a page can be checked against"
BRIEFS_SPEC = os.path.join(REPO, "docs/doperpowers/specs/2026-09-10-liquid-glass-into-the-skill.md")
TAIL_SPEC = os.path.join(REPO, "docs/doperpowers/specs/2026-09-27-materialist-proof.md")

SPATIAL_REFERENCE = os.path.join(REPO, "docs/research/2026-09-27-glass-as-surface-prior-art.md")
SPATIAL_SECTION = "## Rules a spatial-register page can be checked against"
SPATIAL_SPEC = os.path.join(REPO, "docs/doperpowers/specs/2026-09-27-materialist-spatial-register.md")
SPATIAL_BRIEFS_SECTION = "### C. The two pages"
# The page's own record, which the spatial rulebook reads beside the captures.
SPATIAL_RECORD = "apps/demo/src/gallery/{slug}/DESIGN.md"

RULE_SET_NAMES = ("instrument", "spatial")
# Each rulebook's default directories: its captures (outside the repository) and its data.
RULE_SET_DIRS = {
    "instrument": ("figma-design-workspace/materialist-proof/captures",
                   "docs/research/data/2026-09-27-materialist-proof"),
    "spatial": ("figma-design-workspace/materialist-spatial-register/captures",
                "docs/research/data/2026-09-27-materialist-spatial-register"),
}

# The captures `glass-audit.mjs` writes per demo, in the order a rater should read them, each with
# the sentence that says what it shows. The two schemes of one view sit together so a rater compares
# them in place. A page that offers no menu leaves its two menu captures absent, and the prompt names
# only the files on disk. The audit's further captures (increased contrast, forced colours) are
# evidence for the assigned r19 reading and the user's eye, not part of the panel's capture set.
CAPTURES = [
    ("shot-fv-light.png", "the first viewport, 1440 × 900 at scroll 0, light scheme"),
    ("shot-fv-dark.png", "the first viewport, 1440 × 900 at scroll 0, dark scheme"),
    ("shot-full-light.png", "the full page as one stitched capture, light scheme — a fixed plane "
                            "and the floating bars appear once, at the top; read it for the "
                            "sheet's whole composition"),
    ("shot-full-dark.png", "the full page as one stitched capture, dark scheme"),
    ("tile-2-light.png", "the second screen as a viewport capture, the window scrolled to 900, "
                         "light scheme — the bars in place over whatever has passed beneath them"),
    ("tile-2-dark.png", "the second screen, scrolled to 900, dark scheme"),
    ("tile-3-light.png", "the third screen as a viewport capture, scrolled to 1800, light scheme"),
    ("tile-3-dark.png", "the third screen, scrolled to 1800, dark scheme"),
    ("shot-menu-light.png", "the page with its menu or platter open, light scheme"),
    ("shot-menu-dark.png", "the page with its menu or platter open, dark scheme"),
    ("shot-reduced.png", "the first viewport with transparency reduced (the page's own switch "
                         "where it has one), light scheme"),
]

# The spatial pages' captures: the same files in the same order, the two sentences that describe
# the instrument register's floating bars said without them, then the states the spatial rulebook
# names, which exist only where the page has them (`spatial_captures` finds them on disk).
SPATIAL_CAPTURES = [
    (f, {"shot-full-light.png": "the full page as one stitched capture, light scheme — anything "
                                "fixed to the viewport appears once, at the top; read it for the "
                                "page's whole composition",
         "tile-2-light.png": "the second screen as a viewport capture, the document scrolled to "
                             "900, light scheme — whatever is fixed stays in place over whatever "
                             "has passed beneath it"}.get(f, what))
    for f, what in CAPTURES
]

# The digest of the twenty-five rules as parsed from the memo's section — the key, the tag and the
# text of each. It is pinned rather than merely computed because a rating file records `r7` and not
# the rule's words: if the list is edited or renumbered, every rating already collected means
# something else. A mismatch is a decision to make and record, not a number to update in passing.
# This is the 2.3 panel's own pin (f13ab38c, glass-rules.py), reproduced from the memo on 2026-09-27.
RULES_SHA256 = "fe05c2bd00c10c60c7936351642d90dd7b8a4bcd8d26a25a99c040ca84c7d215"

# The spatial rulebook's digest, over the same fields plus each item's marker. It was None until
# the section was final: `pin` prints the value to set, and `prompt` refuses while it is unset,
# because a rating keyed `s7` against a list still being written means nothing once the list moves.
# Pinned 2026-09-27 from the memo's committed section: 30 items, 17 repeating an instrument rule
# (=), 2 adapting one (s16 ~ r15, s20 ~ r22), 11 the register's own, before any capture existed.
SPATIAL_RULES_SHA256 = "f145f17fea11e48fb55155d7c88acdf545522b47047b17bb208c871b43df3219"

# The spatial rulebook's tags (the spec's B), of which the first three are fatal to a page.
SPATIAL_TAGS = ["environment", "layer", "material", "geometry", "grouping", "legibility", "layout",
                "motion", "colour"]
SPATIAL_FATAL_TAGS = ["environment", "layer", "material"]

_RULE_START = re.compile(r"^\s*(\d{1,2})\.\s+`\[([a-z]+)\]`\s+(.*)$")
# The memo cites with inline links, one or more, sometimes marked secondary, as the item's last
# parenthesis: "([HIG Materials](https://…), [WWDC25 284](https://…))".
_LINK = r"\[[^\]]+\]\([^)\s]+\)"
_CITATION = re.compile(r"\s*\((?:\*secondary\*:\s*)?(" + _LINK + r"(?:,\s*" + _LINK + r")*)\)\s*$")
_LINK_LABEL = re.compile(r"\[([^\]]+)\]\(")
# A spatial item's marker, after its tag: `(= r18)` repeats an instrument rule, `(~ r15)` adapts one.
_MARKER = re.compile(r"^`?\(([=~])\s*(r\d{1,2})\)`?\s+(.*)$")


def _section_items(path, section):
    """The numbered list items under a section heading as [number, tag, text], each unwrapped to
    one line; None when the heading is not in the file."""
    lines = open(path, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == section)
    except StopIteration:
        return None
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
            break                                    # prose that closes the list
        # Anything else is the section's opening prose or table, or a blank line, and is passed over.
    return items


def parse_rules(path=None):
    """The 25 rules as (key, tag, text, sources): the numbered list items under the section
    heading, unwrapped to one line, with the trailing citation taken off the text and its link
    labels kept as the sources. Anything but exactly r1 to r25 means the section moved and is an
    error, not a shorter rubric."""
    path = path or REFERENCE
    items = _section_items(path, REFERENCE_SECTION)
    if items is None:
        raise SystemExit(f"glass-rules: no '{REFERENCE_SECTION}' section in {path}")
    out = []
    for n, tag, text in items:
        c = _CITATION.search(text)
        sources = _LINK_LABEL.findall(c.group(1)) if c else []
        out.append((f"r{n}", tag, _CITATION.sub("", text).strip(), sources))
    if len(out) != 25 or [k for k, *_ in out] != [f"r{n}" for n in range(1, 26)]:
        raise SystemExit(
            f"glass-rules: {path} gave {len(out)} rule items, not r1–r25; the section moved")
    return out


def digest(rules, markers=None):
    """The pinned digest's input: key, tag and text of every rule, tab-separated, one per line. A
    spatial item with a marker adds it as a fourth field (`= r18`, `~ r15`), since which instrument
    rule an item stands for is part of what its rating means; the instrument list has none, so its
    input is what it always was."""
    markers = markers or {}
    return hashlib.sha256("\n".join(
        f"{k}\t{t}\t{x}" + (f"\t{markers[k][0]} {markers[k][1]}" if k in markers else "")
        for k, t, x, _ in rules).encode("utf-8")).hexdigest()


def load_rules(check=True, path=None):
    rules = parse_rules(path)
    got = digest(rules)
    if check and got != RULES_SHA256:
        raise SystemExit(
            f"glass-rules: the rules in {os.path.relpath(path or REFERENCE, REPO)} have changed.\n"
            f"  pinned  {RULES_SHA256}\n  found   {got}\n"
            "Ratings are keyed r1–r25 against the pinned list, and the pin is what makes this "
            "panel comparable with the 2.3 panel. Re-pin RULES_SHA256 here with the reason, and "
            "say in the initiative's spec what the collected files now stand for.")
    return rules


def _strip_citation(text):
    """A spatial item's words and its citation: the last parenthesis of the item when it closes
    the item and follows the end of a sentence. The spatial memo cites links, section references
    and code paths together, and prose after them ("; the count ceiling is this register's
    authoring choice"), so the instrument's links-only pattern would leave most of its citations
    on the words; a parenthesis inside a sentence, such as r5's "(≈35% black over bright
    content)", is followed by the sentence's full stop and is words."""
    t = text.rstrip()
    if not t.endswith(")"):
        return t, None
    depth = 0
    for i in range(len(t) - 1, -1, -1):
        depth += {")": 1, "(": -1}.get(t[i], 0)
        if depth == 0:
            head = t[:i].rstrip()
            if head.endswith((".", "!", "?")):
                return head, t[i + 1:-1].strip()
            return t, None
    return t, None


def parse_spatial_rules(path=None):
    """The spatial rules as (key, tag, text, sources) and their markers as {key: ("=" | "~",
    "rN")}. The items must be numbered 1 to N in order, tagged from SPATIAL_TAGS, and each marker
    must name an instrument rule no other item names; an `=` item must carry that rule's tag and
    words exactly (whitespace aside), or the comparison its number promises is not direct."""
    path = path or SPATIAL_REFERENCE
    items = _section_items(path, SPATIAL_SECTION)
    if items is None:
        raise SystemExit(
            f"glass-rules: the spatial rulebook's section '{SPATIAL_SECTION}' is not in "
            f"{os.path.relpath(path, REPO)} yet. The rulebook is written into that memo before any "
            "capture exists (the spatial-register spec, B); once it lands, "
            "`glass-rules.py --rules spatial pin` prints its digest for SPATIAL_RULES_SHA256.")
    if not items or [n for n, *_ in items] != list(range(1, len(items) + 1)):
        raise SystemExit(f"glass-rules: the items of '{SPATIAL_SECTION}' are numbered "
                         f"{[n for n, *_ in items]}, not 1 to N in order")
    by_key = {k: (t, x) for k, t, x, _ in INSTRUMENT_RULES}
    words = lambda s: " ".join(s.split())
    out, markers = [], {}
    for n, tag, text in items:
        key = f"s{n}"
        if tag not in SPATIAL_TAGS:
            raise SystemExit(f"glass-rules: {key} is tagged [{tag}], which is not one of the "
                             f"spatial rulebook's tags ({', '.join(SPATIAL_TAGS)})")
        m = _MARKER.match(text)
        if m:
            kind, rn, text = m.group(1), m.group(2), m.group(3)
            if rn not in by_key:
                raise SystemExit(f"glass-rules: {key} is marked ({kind} {rn}), and there is no {rn}")
            twin = next((k for k, (_, r) in markers.items() if r == rn), None)
            if twin:
                raise SystemExit(f"glass-rules: {key} and {twin} both stand for {rn}")
            markers[key] = (kind, rn)
        body, cite = _strip_citation(text)
        if m and kind == "=" and (tag, words(body)) != (by_key[rn][0], words(by_key[rn][1])):
            raise SystemExit(
                f"glass-rules: {key} is marked (= {rn}) but does not repeat it.\n"
                f"  {rn}  [{by_key[rn][0]}] {by_key[rn][1]}\n  {key}  [{tag}] {body}\n"
                "An item marked (=) repeats the instrument rule's tag and words exactly; one that "
                "changes them is adapted and is marked (~).")
        # The citation as it reads, each link reduced to its label, for `rules` to print.
        sources = [" ".join(re.sub(_LINK, lambda l: _LINK_LABEL.match(l.group(0)).group(1),
                                   cite).split())] if cite else []
        out.append((key, tag, body, sources))
    return out, markers


INSTRUMENT_RULES = load_rules()
# The three rules a static capture cannot show, assigned to a mechanical or source reading before
# any capture existed (spec B, reading 2). The analyzer reads them; the panel answers them anyway.
INSTRUMENT_ASSIGNED = {
    "r18": "the audit's contrast sample in both schemes",
    "r19": "the audit's reduced-transparency pass and its increased-contrast, reduced-motion and "
           "forced-colours passes",
    "r23": "the source reviewer, against the spec's three motion criteria",
}
# The spatial pages' r18 is read per line box on the glyph-suppressed twin, the worst line gating;
# r19 and r23 are read as for the six (the spatial-register spec, B).
SPATIAL_ASSIGNED = {
    "r18": "the audit's per-line contrast, glyphs suppressed, the worst line gating, in both "
           "schemes and every captured state",
    "r19": INSTRUMENT_ASSIGNED["r19"],
    "r23": INSTRUMENT_ASSIGNED["r23"],
}

_BRIEF_START = re.compile(r"^(\d)\.\s+`([a-z-]+)`\s+—\s+(.*)$")


def load_briefs(path=None, tail_path=None):
    """The six briefs, each with this initiative's tail, keyed by slug in the 2.3 spec's order.
    The briefs are the numbered items of the 2.3 spec's "The six briefs"; the tail is the quoted
    sentence after "The tail now reads:" in this initiative's spec, with its `<slug>` filled in."""
    path, tail_path = path or BRIEFS_SPEC, tail_path or TAIL_SPEC
    lines = open(path, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## The six briefs")
    except StopIteration:
        raise SystemExit(f"glass-rules: no '## The six briefs' section in {path}")
    briefs, current = {}, None
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        m = _BRIEF_START.match(line)
        if m:
            current = m.group(2)
            briefs[current] = m.group(3).strip()
        elif current and line.startswith("   ") and line.strip():
            # A line broken after a compound's hyphen ("route-and-" / "status") rejoins without
            # a space, which is how the 2.3 builders' copy in glass-demos.mjs reads it.
            joint = "" if re.search(r"\w-$", briefs[current]) else " "
            briefs[current] += joint + line.strip()
        elif line.strip():
            current = None                           # a heading or prose between the two lists
    if len(briefs) != 6:
        raise SystemExit(f"glass-rules: {path} gave {len(briefs)} briefs, not 6")
    spec = " ".join(open(tail_path, encoding="utf-8").read().split())
    m = re.search(r'The tail now reads: "(.+?)"', spec)
    if not m:
        raise SystemExit(f"glass-rules: no 'The tail now reads: \"…\"' sentence in {tail_path}")
    tail = m.group(1)
    return {s: f"{b} {tail.replace('<slug>', s)}" for s, b in briefs.items()}


def load_spatial_briefs(path=None):
    """The two spatial briefs, each with the spatial spec's shared tail, keyed by slug in the
    spec's order. They are the quoted sentences after each bolded `**7. `slug`**` in "C. The two
    pages" (read by that title), and the tail is the one quoted after `**Shared tail**` there,
    `<slug>` filled in. The
    section's lines are rejoined as the instrument briefs are, a line broken after a compound's
    hyphen without a space; the words are otherwise as the spec has them, markdown included."""
    path = path or SPATIAL_SPEC
    lines = open(path, encoding="utf-8").read().splitlines()
    # The heading may carry the goal it belongs to after the title, "(G3)".
    title = lambda l: l.strip() == SPATIAL_BRIEFS_SECTION or l.strip().startswith(
        SPATIAL_BRIEFS_SECTION + " (")
    try:
        start = next(i for i, l in enumerate(lines) if title(l))
    except StopIteration:
        raise SystemExit(f"glass-rules: no '{SPATIAL_BRIEFS_SECTION}' section in {path}")
    text = ""
    for line in lines[start + 1:]:
        if line.startswith("## ") or line.startswith("### "):
            break
        s = line.strip()
        text += ("" if re.search(r"\w-$", text) else " ") + s if s else "\n\n"
    briefs = dict(re.findall(r'\*\*\d+\.\s+`([a-z-]+)`\*\*[^"\n]*"([^"]+)"', text))
    if len(briefs) != 2:
        raise SystemExit(f"glass-rules: {path} gave {len(briefs)} spatial briefs, not 2")
    m = re.search(r'\*\*Shared tail\*\*[^"\n]*"([^"]+)"', text)
    if not m:
        raise SystemExit(f"glass-rules: no '**Shared tail** … \"…\"' in {path}, section C")
    clean = lambda s: " ".join(s.split())
    return {s: f"{clean(b)} {clean(m.group(1)).replace('<slug>', s)}" for s, b in briefs.items()}


def select(name, require_pin=True):
    """Make one rulebook the module's: its items and markers, tags, fatal tags, assigned readings,
    briefs, slugs, directories and capture list, under the names the rest of this file and the
    analyzer read. The instrument rulebook is selected at import, so a reader that never asks for
    another sees exactly what it always did. The spatial one checks its pin unless `require_pin`
    is off, which is how `rules` and `pin` show a list that is not yet pinned."""
    global RULES_SET, RULES, MARKERS, SAME_AS, TAGS, FATAL_TAGS, ASSIGNED, BRIEFS, SLUGS
    global CAPTURES_DIR, DATA, PINNED, SECTION_SOURCE
    if name not in RULE_SET_NAMES:
        raise SystemExit(f"glass-rules: --rules is instrument or spatial, not {name!r}")
    if name == "instrument":
        rules, markers, pinned = INSTRUMENT_RULES, {}, RULES_SHA256
        fatal, assigned_from = ["layer", "material"], INSTRUMENT_ASSIGNED
        briefs = load_briefs()
        source = (REFERENCE, REFERENCE_SECTION)
    else:
        rules, markers = parse_spatial_rules()
        pinned, got = SPATIAL_RULES_SHA256, digest(rules, markers)
        if require_pin and pinned is None:
            raise SystemExit(
                "glass-rules: the spatial rulebook is not pinned yet (SPATIAL_RULES_SHA256 is None). "
                "A rating file records `s7` and not the rule's words, so no prompt is issued and no "
                "rating is read until the list is: run `glass-rules.py --rules spatial pin`, check "
                f"the {len(rules)} items it reports, and set SPATIAL_RULES_SHA256 in this file to "
                "the digest it prints, with the date.")
        if require_pin and got != pinned:
            raise SystemExit(
                f"glass-rules: the spatial rules in {os.path.relpath(SPATIAL_REFERENCE, REPO)} have "
                f"changed.\n  pinned  {pinned}\n  found   {got}\n"
                "Ratings are keyed s1–sN against the pinned list. Re-pin SPATIAL_RULES_SHA256 here "
                "with the reason, and say in the spatial-register spec what the collected files now "
                "stand for.")
        fatal = SPATIAL_FATAL_TAGS
        by_rn = {rn: k for k, (kind, rn) in markers.items() if kind == "="}
        assigned_from = {by_rn[rn]: why for rn, why in SPATIAL_ASSIGNED.items() if rn in by_rn}
        assigned_from = {k: assigned_from[k] for k, *_ in rules if k in assigned_from}
        briefs = load_spatial_briefs()
        source = (SPATIAL_REFERENCE, SPATIAL_SECTION)
    captures_default, data_default = RULE_SET_DIRS[name]
    RULES_SET, RULES, MARKERS, PINNED, SECTION_SOURCE = name, rules, markers, pinned, source
    # The instrument rule each spatial item repeats verbatim; the assigned readings follow it.
    SAME_AS = {k: rn for k, (kind, rn) in markers.items() if kind == "="}
    TAGS = sorted({t for _, t, _, _ in rules})
    # The tags whose failure the pass line treats as fatal: a page failing one of these is not this
    # language whatever else it does.
    FATAL_TAGS = fatal
    ASSIGNED = dict(assigned_from)
    BRIEFS, SLUGS = briefs, list(briefs)
    CAPTURES_DIR = (os.environ.get("GLASS_CAPTURES") or os.path.join(REPO, captures_default))
    DATA = (os.environ.get("GLASS_DATA") or os.path.join(REPO, data_default))


select("instrument")


def spatial_captures(d):
    """The spatial states' captures on disk in one demo's directory, in reading order, each with
    what it shows: every inner scroller scrolled half-way and to its end (its top is the first
    viewport), then the environment's phases, then the CSS tier, then forced colours. The
    glyph-suppressed twins the audit reads from are not the page and are not shown."""
    if not os.path.isdir(d):
        return []
    files = set(os.listdir(d))
    num = lambda f: [int(x) for x in re.findall(r"\d+", f)]
    out = []
    scrollers = sorted({int(m.group(1)) for f in files
                        if (m := re.match(r"scroller-(\d+)-(?:top|middle|bottom)-light\.png$", f))})
    for n in scrollers:
        for pos, where in (("middle", "scrolled half-way"), ("bottom", "scrolled to its end")):
            for scheme in ("light", "dark"):
                f = f"scroller-{n}-{pos}-{scheme}.png"
                if f in files:
                    out.append((f, f"inner scroller {n}, {where}, the first viewport otherwise at "
                                   f"rest, {scheme} scheme"))
    for f in sorted((f for f in files if re.match(r"phase-\d+-(?:light|dark)\.png$", f)),
                    key=lambda f: (num(f), "dark" in f)):
        i, scheme = num(f)[0], "dark" if "dark" in f else "light"
        out.append((f, f"the environment's phase {i} (the page's own phase switch), the first "
                       f"viewport, {scheme} scheme"))
    for f, what in (("css-fv.png", "the first viewport on the CSS tier (the page's ?tier=css "
                                   "switch), light scheme"),
                    ("css-menu.png", "the menu or platter open on the CSS tier, light scheme"),
                    ("shot-forced.png", "the first viewport under forced colours, light scheme")):
        if f in files:
            out.append((f, what))
    return out


def captures(slug):
    """The capture files that exist for a demo, as (path, what it shows), in reading order."""
    d = os.path.join(CAPTURES_DIR, slug)
    listed = SPATIAL_CAPTURES if RULES_SET == "spatial" else CAPTURES
    out = [(os.path.join(d, f), what) for f, what in listed if os.path.exists(os.path.join(d, f))]
    if RULES_SET == "spatial":
        out += [(os.path.join(d, f), what) for f, what in spatial_captures(d)]
    return out


def record(slug):
    """The spatial page's record, when it exists: the repository path a rater is handed."""
    p = SPATIAL_RECORD.format(slug=slug)
    return p if os.path.exists(os.path.join(REPO, p)) else None


def seed_for(rater):
    return int(hashlib.sha256(f"glass-rules|{rater}".encode()).hexdigest()[:8], 16)


def order_for(rater, slugs):
    """The rater's demo order: a shuffle of the demos it rates, seeded by its name so the same
    rater always reads them in the same order and the order is reproducible from the name alone."""
    order = list(slugs)
    random.Random(seed_for(rater)).shuffle(order)
    return order


_COUNT = {2: "two", 6: "six"}


def available(slugs=None):
    """The demos to rate: those with at least one capture on disk. A slug asked for by name and
    carrying no capture is an error, since there is nothing to rate, while the default list simply
    passes over a demo that has not been built or audited yet."""
    if slugs:
        for s in slugs:
            if s not in BRIEFS:
                raise SystemExit(f"glass-rules: unknown demo {s!r}; the "
                                 f"{_COUNT.get(len(SLUGS), len(SLUGS))} are {', '.join(SLUGS)}")
            if not captures(s):
                raise SystemExit(f"glass-rules: {s} has no captures under "
                                 f"{os.path.join(CAPTURES_DIR, s)}")
        return list(slugs)
    return [s for s in SLUGS if captures(s)]


def _and(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def prompt(rater, slugs=None):
    """One rater's prompt over the demos: the blinded instruction, then a section per demo in the
    rater's own order carrying the brief and the captures, then the rules and the shape of the
    file to write per demo. The spatial prompt is the instrument one with the rulebook named, the
    page's record handed over beside the captures, and its own rules and keys."""
    spatial = RULES_SET == "spatial"
    order = order_for(rater, available(slugs))
    if not order:
        raise SystemExit(f"glass-rules: no demo under {CAPTURES_DIR} carries a capture yet. Run "
                         "glass-audit.mjs over the gallery pages with --out pointing there before "
                         "asking for a rater's prompt.")
    out = os.path.join(DATA, "rules", rater, "<slug>.json")
    n_rules = len(RULES)
    if spatial:
        L = [
            "You are a blinded rater for a design experiment. Each page below was built by a "
            "different builder from its own brief, under one design skill; you do not know which "
            "builder made which and must not try to find out. Rate from the captures and the "
            "page's record alone: open nothing else — not the page's source under `apps/demo/` "
            "beyond the one record named for it, not any audit JSON or anything under "
            f"`{os.path.relpath(DATA, REPO)}` — and do not run git. The record is the page's own "
            "account of what it did; it is evidence for what a rule asks to be recorded (a value, "
            "a declaration, what is stated as uncalibrated) and never for what the captures "
            "should show.",
            "",
        ]
    else:
        L = [
            "You are a blinded rater for a design experiment. Each page below was built by a "
            "different builder from its own brief, under one design skill; you do not know which "
            "builder made which and must not try to find out. Rate from the captures alone: open "
            "nothing else — not the page's source under `apps/demo/`, not its DESIGN.md, not any "
            f"audit JSON or anything under `{os.path.relpath(DATA, REPO)}` — and do not run git. "
            "What the page's own notes claim about itself is not evidence; what the captures show "
            "is.",
            "",
        ]
    L += [
        f"The {len(order)} pages, in the order to read and rate them, each with the brief it was "
        "built from and the captures taken of it, in both colour schemes. Read every capture of "
        f"every page once before rating any page: the {len(order)} pages are the frame for every "
        "rating.",
        "",
    ]
    for n, slug in enumerate(order, 1):
        caps = captures(slug)
        L += [f"### {n}. {slug}", "", f'Brief (verbatim): "{BRIEFS[slug]}"', ""]
        if spatial:
            rec = record(slug)
            L += [f"Record: `{rec}`" if rec else "Record: none on disk — a rule that asks for a "
                  "recorded value has nothing to read it from.", ""]
        L.append("Captures:")
        L += [f"- `{p}` — {what}" for p, what in caps]
        L.append("")
    if spatial:
        scroll = [k for k, t, x, _ in RULES
                  if MARKERS.get(k, ("", ""))[1] == "r15" or re.search(r"scroll[- ]edge", x, re.I)]
        edge = (f"{'A rule' if len(scroll) == 1 else 'Rules'} naming the scroll edge effect "
                f"({_and(scroll)}) {'names' if len(scroll) == 1 else 'name'} a system primitive the "
                "web does not have: a page holds it by building the equivalent, and a page that "
                "skipped it has failed rather than been excused. ") if scroll else ""
        L += [
            f"Then answer, for every page in that order, the {n_rules} rules below. They are the "
            "spatial register's rulebook, “Rules a spatial-register page can be checked against”, "
            f"keyed s1 to s{n_rules}: the rules for an interface made of glass set into an "
            "environment, the register each brief above names. Each is yes or no on the rendered "
            "page: **1** the rule holds on this page, **0** it does not. Judge the page in front of "
            "you rather than the page you would have built, and answer from the captures and the "
            "record you were given — a rule you cannot see holding in them does not hold, and where "
            "the state it needs was not captured or recorded, begin its evidence with “unread:”. "
            + edge + "The tag in brackets is the rule's kind; it does not change how you answer.",
            "",
        ]
    else:
        L += [
            "Then answer, for every page in that order, the 25 rules below. Each is yes or no on the "
            "rendered page: **1** the rule holds on this page, **0** it does not. Judge the page in "
            "front of you rather than the page you would have built, and answer from the captures "
            "you were given — a rule you cannot see holding in them does not hold. Two of the rules "
            "name system primitives the web does not have, the scroll edge effect (r15) and the "
            "background extension effect with safe-area insets (r21): a page holds them by building "
            "the equivalent, and a page that skipped them has failed them rather than been excused "
            "from them. The tag in brackets is the rule's kind; it does not change how you answer.",
            "",
        ]
    L += [f"- {k} [{t}]: {x}" for k, t, x, _ in RULES]
    shape = {"rater": rater}
    if spatial:
        shape["rules_set"] = "spatial"
    shape.update({
        "slug": "<slug>", "order": order,
        "rules": {k: "<0|1>" for k, *_ in RULES},
        "evidence": {k: "<clause>" for k, *_ in RULES},
    })
    L += [
        "",
        f"For each of the {n_rules} rules give one short clause of evidence — what on the page "
        "decided the answer, naming the surface, the region and the scheme you read it from.",
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


def _rules_option(argv):
    """`--rules X` or `--rules=X` wherever it stands, taken off the line; the rest is the command
    exactly as it was before the option existed."""
    name, rest, i = "instrument", [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--rules":
            if i + 1 >= len(argv):
                raise SystemExit("glass-rules: --rules needs instrument or spatial")
            name, i = argv[i + 1], i + 2
        elif a.startswith("--rules="):
            name, i = a.split("=", 1)[1], i + 1
        else:
            rest.append(a)
            i += 1
    if name not in RULE_SET_NAMES:
        raise SystemExit(f"glass-rules: --rules is instrument or spatial, not {name!r}")
    return name, rest


def _marker(k):
    return f"({MARKERS[k][0]} {MARKERS[k][1]}) " if k in MARKERS else ""


if __name__ == "__main__":
    name, argv = _rules_option(sys.argv[1:])
    cmd = argv[0] if argv else ""
    if cmd == "prompt" and len(argv) > 1:
        select(name)
        slugs = [s for a in argv[2:] for s in a.split(",") if s]
        print(prompt(argv[1], slugs or None))
    elif cmd == "rules":
        select(name, require_pin=False)
        for k, t, x, src in RULES:
            print(f"{k}\t[{t}]\t{_marker(k)}{x}" + (f"  ({', '.join(src)})" if src else "")
                  + (f"  [assigned: {ASSIGNED[k]}]" if k in ASSIGNED else ""))
        counts = ", ".join(f"{t} {sum(1 for _, tg, _, _ in RULES if tg == t)}" for t in TAGS)
        print(f"\n{len(RULES)} rules; by tag: {counts}. Fatal tags: {', '.join(FATAL_TAGS)}. "
              f"Assigned: {', '.join(ASSIGNED)}.")
        print(f"digest {digest(RULES, MARKERS)} (pinned {PINNED})")
    elif cmd == "pin":
        select(name, require_pin=False)
        got = digest(RULES, MARKERS)
        path, section = SECTION_SOURCE
        same = [k for k, (kind, _) in MARKERS.items() if kind == "="]
        adapted = [k for k, (kind, _) in MARKERS.items() if kind == "~"]
        counts = ", ".join(f"{t} {sum(1 for _, tg, _, _ in RULES if tg == t)}" for t in TAGS)
        print(f"{name} rulebook: '{section}' in {os.path.relpath(path, REPO)}")
        print(f"{len(RULES)} items, {RULES[0][0]} to {RULES[-1][0]}; by tag: {counts}")
        if MARKERS:
            print(f"repeated verbatim (=): {len(same)}; adapted (~): {len(adapted)} "
                  f"({', '.join(f'{k} ~ {MARKERS[k][1]}' for k in adapted) or 'none'}); "
                  f"the register's own: {len(RULES) - len(MARKERS)}")
        print(f"fatal tags: {', '.join(FATAL_TAGS)} "
              f"({sum(1 for _, t, _, _ in RULES if t in FATAL_TAGS)} rules); assigned: "
              + (", ".join(f"{k} (= {SAME_AS.get(k, k)})" if k in SAME_AS else k for k in ASSIGNED)
                 or "none"))
        print(f"digest {got}")
        if PINNED is None:
            print(f"not pinned: once the section is final, set SPATIAL_RULES_SHA256 = \"{got}\" in "
                  "glass-rules.py, with the date")
        elif PINNED == got:
            print("matches the pin")
        else:
            print(f"differs from the pin {PINNED}: the section changed after it was pinned")
            sys.exit(1)
    else:
        print(__doc__)
