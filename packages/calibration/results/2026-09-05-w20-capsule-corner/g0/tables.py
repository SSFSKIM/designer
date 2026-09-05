"""W20 G0 — the findings' tables, printed from `contours.json` rather than typed.

A table typed by hand beside the JSON it summarises is a second record that can disagree with the
first. Every number in `g0-probe.md` comes out of here.

Usage: tables.py <contours.json>
"""

import json
import sys

NAMES = ["vitrea-clamp", "shoulder-compress", "circular-arc", "apple-overflow", "stadium"]
HEAD = {
    "vitrea-clamp": "vitrea clamp",
    "shoulder-compress": "shoulder compress",
    "circular-arc": "circular arc",
    "apple-overflow": "apple overflow",
    "stadium": "stadium",
}


def cell(row, name, key):
    c = row["candidates"].get(name)
    return "—" if c is None else f"{c[key]:.3f}"


def main():
    doc = json.load(open(sys.argv[1]))
    rows = [r for r in doc["results"] if "error" not in r]

    for background in ("light-solid", "checkerboard"):
        for key, label in (
            ("p95", "p95 native → candidate"),
            ("max", "max native → candidate"),
            ("maxCandidateToNative", "max candidate → native"),
        ):
            print(f"\n### {background}, {label} (px)\n")
            print("| component | r | ratio | " + " | ".join(HEAD[n] for n in NAMES) + " |")
            print("| --- | --- | --- | " + " | ".join("---" for _ in NAMES) + " |")
            for r in rows:
                if r["background"] != background:
                    continue
                print(
                    f"| `{r['component']}` | {r['declaredRadius']:g} | {r['ratio']:.4f} | "
                    + " | ".join(cell(r, n, key) for n in NAMES)
                    + " |"
                )

    print("\n### The corner's own numbers\n")
    print(
        "| component | r | background | points | circle-fit radius | rms | diagonal depth | "
        "implied circular radius |"
    )
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        rf = r["circleFitRadius"]
        rms = r["circleFitRms"]
        print(
            f"| `{r['component']}` | {r['declaredRadius']:g} | {r['background']} | {r['points']} | "
            f"{'—' if rf != rf else f'{rf:.2f}'} | {'—' if rms != rms else f'{rms:.3f}'} | "
            f"{r['diagonalDepth']:.2f} | {r['impliedCircularRadius']:.2f} |"
        )

    print("\n### What the instrument can separate (max distance between candidates, px)\n")
    seen = set()
    for r in rows:
        if r["component"] in seen or not r["candidateSeparation"]:
            continue
        seen.add(r["component"])
        pairs = list(r["candidateSeparation"].items())
        if not pairs:
            continue
        print(f"\n`{r['component']}` (r = {r['declaredRadius']:g})\n")
        print("| pair | max distance |")
        print("| --- | --- |")
        for k, v in pairs:
            print(f"| {k} | {v:.3f} |")


if __name__ == "__main__":
    main()
