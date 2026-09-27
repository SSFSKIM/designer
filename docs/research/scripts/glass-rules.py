#!/usr/bin/env python3
"""The panel's rule reading for the six materialist demos (spec: docs/doperpowers/specs/
2026-09-27-materialist-proof.md, "B. The instrument", reading 2).

    python3 glass-rules.py prompt <rater> [<slug>,…]   one rater's prompt over the demos with captures
    python3 glass-rules.py rules                       the 25 items with their tags

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

Two environment overrides point a dry run at scratch without writing into committed evidence:
GLASS_CAPTURES (default `figma-design-workspace/materialist-proof/captures` at the repository root)
and GLASS_DATA (default the data directory above).
"""
import os, sys, re, json, random, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))

REFERENCE = os.path.join(REPO, "docs/research/2026-09-10-liquid-glass-design-language.md")
REFERENCE_SECTION = "## Rules a page can be checked against"
BRIEFS_SPEC = os.path.join(REPO, "docs/doperpowers/specs/2026-09-10-liquid-glass-into-the-skill.md")
TAIL_SPEC = os.path.join(REPO, "docs/doperpowers/specs/2026-09-27-materialist-proof.md")
CAPTURES_DIR = (os.environ.get("GLASS_CAPTURES")
                or os.path.join(REPO, "figma-design-workspace/materialist-proof/captures"))
DATA = (os.environ.get("GLASS_DATA")
        or os.path.join(REPO, "docs/research/data/2026-09-27-materialist-proof"))

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

# The digest of the twenty-five rules as parsed from the memo's section — the key, the tag and the
# text of each. It is pinned rather than merely computed because a rating file records `r7` and not
# the rule's words: if the list is edited or renumbered, every rating already collected means
# something else. A mismatch is a decision to make and record, not a number to update in passing.
# This is the 2.3 panel's own pin (f13ab38c, glass-rules.py), reproduced from the memo on 2026-09-27.
RULES_SHA256 = "fe05c2bd00c10c60c7936351642d90dd7b8a4bcd8d26a25a99c040ca84c7d215"

_RULE_START = re.compile(r"^\s*(\d{1,2})\.\s+`\[([a-z]+)\]`\s+(.*)$")
# The memo cites with inline links, one or more, sometimes marked secondary, as the item's last
# parenthesis: "([HIG Materials](https://…), [WWDC25 284](https://…))".
_LINK = r"\[[^\]]+\]\([^)\s]+\)"
_CITATION = re.compile(r"\s*\((?:\*secondary\*:\s*)?(" + _LINK + r"(?:,\s*" + _LINK + r")*)\)\s*$")
_LINK_LABEL = re.compile(r"\[([^\]]+)\]\(")


def parse_rules(path=None):
    """The 25 rules as (key, tag, text, sources): the numbered list items under the section
    heading, unwrapped to one line, with the trailing citation taken off the text and its link
    labels kept as the sources. Anything but exactly r1 to r25 means the section moved and is an
    error, not a shorter rubric."""
    path = path or REFERENCE
    lines = open(path, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == REFERENCE_SECTION)
    except StopIteration:
        raise SystemExit(f"glass-rules: no '{REFERENCE_SECTION}' section in {path}")
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
        # Anything else is the section's opening prose or a blank line, and is passed over.
    out = []
    for n, tag, text in items:
        c = _CITATION.search(text)
        sources = _LINK_LABEL.findall(c.group(1)) if c else []
        out.append((f"r{n}", tag, _CITATION.sub("", text).strip(), sources))
    if len(out) != 25 or [k for k, *_ in out] != [f"r{n}" for n in range(1, 26)]:
        raise SystemExit(
            f"glass-rules: {path} gave {len(out)} rule items, not r1–r25; the section moved")
    return out


def digest(rules):
    """The pinned digest's input: key, tag and text of every rule, tab-separated, one per line."""
    return hashlib.sha256(
        "\n".join(f"{k}\t{t}\t{x}" for k, t, x, _ in rules).encode("utf-8")).hexdigest()


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


RULES = load_rules()
TAGS = sorted({t for _, t, _, _ in RULES})
# The tags whose failure the pass line treats as fatal: a page failing one of these is not this
# language whatever else it does.
FATAL_TAGS = ["layer", "material"]
# The three rules a static capture cannot show, assigned to a mechanical or source reading before
# any capture existed (spec B, reading 2). The analyzer reads them; the panel answers them anyway.
ASSIGNED = {
    "r18": "the audit's contrast sample in both schemes",
    "r19": "the audit's reduced-transparency pass and its increased-contrast, reduced-motion and "
           "forced-colours passes",
    "r23": "the source reviewer, against the spec's three motion criteria",
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


BRIEFS = load_briefs()
SLUGS = list(BRIEFS)


def captures(slug):
    """The capture files that exist for a demo, as (path, what it shows), in reading order."""
    d = os.path.join(CAPTURES_DIR, slug)
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
    carrying no capture is an error, since there is nothing to rate, while the default list simply
    passes over a demo that has not been built or audited yet."""
    if slugs:
        for s in slugs:
            if s not in BRIEFS:
                raise SystemExit(f"glass-rules: unknown demo {s!r}; the six are {', '.join(SLUGS)}")
            if not captures(s):
                raise SystemExit(f"glass-rules: {s} has no captures under "
                                 f"{os.path.join(CAPTURES_DIR, s)}")
        return list(slugs)
    return [s for s in SLUGS if captures(s)]


def prompt(rater, slugs=None):
    """One rater's prompt over the demos: the blinded instruction, then a section per demo in the
    rater's own order carrying the brief and the captures, then the 25 rules and the shape of the
    file to write per demo."""
    order = order_for(rater, available(slugs))
    if not order:
        raise SystemExit(f"glass-rules: no demo under {CAPTURES_DIR} carries a capture yet. Run "
                         "glass-audit.mjs over the gallery pages with --out pointing there before "
                         "asking for a rater's prompt.")
    out = os.path.join(DATA, "rules", rater, "<slug>.json")
    L = [
        "You are a blinded rater for a design experiment. Each page below was built by a different "
        "builder from its own brief, under one design skill; you do not know which builder made "
        "which and must not try to find out. Rate from the captures alone: open nothing else — not "
        "the page's source under `apps/demo/`, not its DESIGN.md, not any audit JSON or anything "
        f"under `{os.path.relpath(DATA, REPO)}` — and do not run git. What the page's own notes "
        "claim about itself is not evidence; what the captures show is.",
        "",
        f"The {len(order)} pages, in the order to read and rate them, each with the brief it was "
        "built from and the captures taken of it, in both colour schemes. Read every capture of "
        f"every page once before rating any page: the {len(order)} pages are the frame for every "
        "rating.",
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
    shape = {
        "rater": rater, "slug": "<slug>", "order": order,
        "rules": {k: "<0|1>" for k, *_ in RULES},
        "evidence": {k: "<clause>" for k, *_ in RULES},
    }
    L += [
        "",
        "For each of the 25 rules give one short clause of evidence — what on the page decided the "
        "answer, naming the surface, the region and the scheme you read it from.",
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
            print(f"{k}\t[{t}]\t{x}" + (f"  ({', '.join(src)})" if src else "")
                  + (f"  [assigned: {ASSIGNED[k]}]" if k in ASSIGNED else ""))
        counts = ", ".join(f"{t} {sum(1 for _, tg, _, _ in RULES if tg == t)}" for t in TAGS)
        print(f"\n25 rules; by tag: {counts}. Fatal tags: {', '.join(FATAL_TAGS)}. "
              f"Assigned: {', '.join(ASSIGNED)}.")
        print(f"digest {digest(RULES)} (pinned {RULES_SHA256})")
    else:
        print(__doc__)
