"""W18 G0 (b) — the per-term attribution table.

Reads the per-configuration separation JSONs that `separation.ts` writes over each decline's pair of
capture roots, and reports how the CSS-minus-GPU difference MOVES when a term is declined.

The quantity is deliberately a difference of differences. `delta(config) = CSS − GPU` under one
profile document, and a term's share is `delta(default) − delta(no-term)`: what the residual loses
when that term is taken out of both tiers at once. A term the two tiers agree about contributes
nothing to this however large it is on either tier alone, which is the whole reason the declines are
rendered on both sides rather than on the renderer only.

The charter's clause for (b) is that the single-term shares sum to the whole within 0.003, where the
whole is `delta(default) − delta(all-declined)` over the charter's five terms. The sum and the
remainder are both printed; `no-outer-shadow` is reported beside them and is NOT in the sum, because
it is a sixth decline this spike added after (a) put a term on the neighbours and it is not one of
the five the clause is stated over.

Usage: `python attribution.py <partsDir> <dpr>`, or with no argument both scales.
"""

import json
import sys
from pathlib import Path

FIVE = ["no-lens", "no-rim", "no-highlight", "no-lift", "no-inner-shadow"]
CONFIGS = ["default", *FIVE, "no-outer-shadow", "all-declined"]


def deltas(parts: Path, config: str, dpr: int):
    rows = json.loads((parts / f"attr-{config}-{dpr}x.json").read_text())
    out = {}
    for row in rows:
        if "skipped" in row:
            continue
        out[row["scene"]] = row["whole"]["declared"]["delta"]
    return out


def main() -> None:
    parts = Path(sys.argv[1])
    scales = [int(sys.argv[2])] if len(sys.argv) > 2 else [1, 2]
    for dpr in scales:
        table = {config: deltas(parts, config, dpr) for config in CONFIGS}
        scenes = list(table["default"])
        head = f"{'scene':40s} {'default':>9s} {'all-dec':>9s} {'whole':>9s}"
        head += "".join(f" {c.replace('no-', ''):>9s}" for c in FIVE)
        head += f" {'sum':>9s} {'sum-whole':>10s} {'outerShad':>10s}"
        print(f"=== dpr {dpr}: CSS − GPU, and what each decline moves it by ===")
        print(head)
        for scene in scenes:
            base = table["default"][scene]
            whole = base - table["all-declined"][scene]
            shares = [base - table[c][scene] for c in FIVE]
            line = f"{scene:40s} {base:+9.4f} {table['all-declined'][scene]:+9.4f} {whole:+9.4f}"
            line += "".join(f" {s:+9.4f}" for s in shares)
            line += f" {sum(shares):+9.4f} {sum(shares) - whole:+10.5f}"
            line += f" {base - table['no-outer-shadow'][scene]:+10.4f}"
            print(line)
        print()


if __name__ == "__main__":
    main()
