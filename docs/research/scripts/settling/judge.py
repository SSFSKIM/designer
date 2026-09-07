#!/usr/bin/env python3
"""The second judge for the settling experiment: a blinded model rater on one brief's pairs.

    python3 judge.py prompt <brief>[,<brief>…]   print one judge's prompt for those briefs
    python3 judge.py briefs                       list briefs with their pair counts

The pairs are rate.schedule()'s — the same 78 the human judges, same left/right — grouped by
brief so a rater reads each brief's eight pages once and decides its twelve pairs. One rater can
take several briefs in one prompt (the user's preference: batch over fan-out); it writes
figma-design-workspace/settling/judgments-model/<brief>.jsonl per brief, one line per pair in the
human file's shape plus a reason and a judge field. It sees screenshots and ids only.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rate

QUESTION = "Which would you be more likely to deliver to a client?"


def section(brief):
    pairs = [p for p in rate.schedule() if p["brief"] == brief]
    if not pairs:
        raise SystemExit("no pairs for " + brief)
    ids = sorted({p["left"] for p in pairs} | {p["right"] for p in pairs})
    out = os.path.join(rate.WS, "judgments-model", brief + ".jsonl")
    shot = lambda i, f: os.path.join(rate.WS, "builds", i, f)
    lines = [f"## Brief `{brief}`", "", f'Brief (verbatim): "{rate.brief_text(pairs[0]["eval"])}"', "",
             "Pages (id, first-viewport screenshot, full-page screenshot). Read both screenshots of every page once, before judging any of this brief's pairs:"]
    lines += [f"- {i}: {shot(i, 'shot-fv.png')} and {shot(i, 'shot-full.png')}" for i in ids]
    lines += ["", "Pairs (pair id, left page, right page):"]
    lines += [f"- {p['pair']}: left {p['left']}, right {p['right']}" for p in pairs]
    lines += ["", f"Write one JSON line per pair to `{out}` (create the directory; overwrite the file), in the order above:",
              '{"pair": "<pair id>", "brief": "' + brief + '", "left": "<left id>", "right": "<right id>", "choice": "left" or "right", "reason": "<one sentence>", "judge": "astra-medium"}', ""]
    return "\n".join(lines)


def prompt(briefs):
    head = [
        "You are a blinded visual judge for a design experiment. Pages were built from a brief by different builders; you do not know which builder made which and must not try to find out. Open nothing under the build directories except the two screenshots named per page. Judge as a designer handing work to the client who wrote the brief.",
        "",
        f'Take the briefs below one at a time. For each: read every page\'s two screenshots once, then decide each listed pair on its own, forced choice, no ties, on this one question: "{QUESTION}" Pages from one brief are never compared with another\'s.',
        "",
    ]
    tail = ["Then report in under 150 words: per brief, how many pairs went left and right, and which page won every pair it was in, if any. Do not modify anything else."]
    return "\n".join(head + [section(b) for b in briefs] + tail)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "prompt":
        print(prompt(sys.argv[2].split(",")))
    elif cmd == "briefs":
        from collections import Counter
        for b, n in Counter(p["brief"] for p in rate.schedule()).items():
            print(b, n)
    else:
        print(__doc__)
