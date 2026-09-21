#!/usr/bin/env python3
"""W31 G2 — how far has a fit ever moved a leaf? (claims c9a §5.163 §2.)

The `@gpu` range sweeps have to bracket each swept leaf by "the range a fit could
reach", and a range chosen by taste is a range nobody can argue with afterwards.
This reads it off the documents instead: every macOS 27 profile document records,
per fitted entry, both the `value` it adopted and the `previous` it moved from, so
the widest ratio the project has ever moved a leaf across a material generation is
a measurement sitting in committed evidence.

A pair with a zero at either end has no ratio and is listed separately: the move
is real and the bracket it implies is "anything", which a sweep cannot express and
which the range proofs handle by bounding the leaf instead.

Run: python3 leaf-moves.py
"""

import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PROFILES = HERE.parents[1] / "profiles"


def rows() -> tuple[list, list]:
    finite, zeroed = [], []
    for path in sorted(PROFILES.glob("apple-macos-27.0-*.json")):
        document = json.loads(path.read_text())
        for entry, body in (document.get("entries") or {}).items():
            value, previous = body.get("value"), body.get("previous")
            if not isinstance(value, dict) or not isinstance(previous, dict):
                continue
            for leaf, new in value.items():
                if leaf not in previous:
                    continue
                old = previous[leaf]
                pairs = zip(new if isinstance(new, list) else [new],
                            old if isinstance(old, list) else [old])
                for index, (a, b) in enumerate(pairs):
                    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                        continue
                    row = (path.name, entry, f"{leaf}[{index}]", b, a)
                    if a == 0 or b == 0:
                        zeroed.append(row)
                    else:
                        finite.append((max(abs(a / b), abs(b / a)), *row))
    finite.sort(key=lambda r: -r[0])
    return finite, zeroed


def main() -> None:
    finite, zeroed = rows()
    widest = finite[0]
    lines = [
        "W31 G2 — the widest ratio any material leaf has moved between two",
        "generations, read off the macOS 27 documents' own `entries[].previous`.",
        "Claims c9a §5.163 §2.",
        "",
        f"{len(finite) + len(zeroed)} leaf moves recorded; {len(finite)} carry a ratio.",
        "",
        f"WIDEST: {widest[0]:.1f}x — {widest[3]} {widest[2]} {widest[4]} -> {widest[5]}",
        f"        ({widest[1]})",
        "",
        "This is the bracket `e2e/gpu/w31-range-sweeps.spec.ts` sweeps each material",
        "axis over: shipped/550, shipped/23.45, shipped, shipped*23.45, shipped*550.",
        "A fit that moved a leaf further than any fit ever has is outside what those",
        "sweeps claim, which is a bound worth stating rather than a range worth",
        "guessing.",
        "",
        "Top 12 by ratio:",
        "",
    ]
    for row in finite[:12]:
        lines.append(f"  {row[0]:9.2f}x  {row[2]:28s} {row[3]:26s} {row[4]} -> {row[5]}")
    lines += ["", f"Moves with a zero at one end ({len(zeroed)}), ratio undefined:", ""]
    for row in zeroed:
        lines.append(f"             {row[1]:28s} {row[2]:26s} {row[3]} -> {row[4]}")
    lines += [
        "",
        "A leaf that moved off zero — the scale-selective scatter's two, W30's",
        "decline turned into the dark document's adoption — is why the sweeps open",
        "`sizeHeavySecondShare` to 0.5 before sweeping the second tap's width: an",
        "inert leaf's sweep is a sweep of a multiplied zero.",
        "",
    ]
    text = "\n".join(lines)
    (HERE / "leaf-moves.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
