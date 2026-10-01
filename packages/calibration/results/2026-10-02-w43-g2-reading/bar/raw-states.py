"""W43 G2 (1): the run states of both sides of the pair, read off the raw runs by bytes.

Charter clause 7: the per-metric bar is the 0.25 runs' own run-to-run distribution, and the pair's
noise is the larger of its two sides. Before any metric is computed, this reads what the raw runs
are at the byte level, on both sides:

- the 0.25 side: G1a's four canonical passes (``~/vitrea-w43/g1a-run/bed-0.25-*``), the admitted
  ``run-1`` .. ``run-7`` of each pass, never a ``QUARANTINE-*`` directory (§5.199 §2);
- the 0.5 side: W29 G1's four standard passes (``~/vitrea-w29-27-run/standard-*``), the bed the
  0.5 fixtures were plurality-published from (§5.150).

Per cell: the distinct file SHA-256s over the runs, each with its run count, and whether the
published fixture is one of them. Nothing here reads a 0.25 cell against a 0.5 cell.

    python3.12 -B raw-states.py [--g1a ~/vitrea-w43/g1a-run] [--w29 ~/vitrea-w29-27-run]

Writes ``raw-states.json`` (every cell) and ``raw-states.txt`` (the counts) beside itself.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FIXTURES = REPO / "apps" / "reference-apple" / "fixtures"

G1A_PASSES = ["bed-0.25-1x-active", "bed-0.25-1x-receded", "bed-0.25-2x-active", "bed-0.25-2x-receded"]
W29_PASSES = ["standard-active-1x", "standard-inactive-1x", "standard-active-2x", "standard-inactive-2x"]
RUN = re.compile(r"^run-(\d+)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_side(root: Path, passes: list[str], glass: str) -> dict[str, dict]:
    cells: dict[str, dict] = {}
    for name in passes:
        pass_dir = root / name
        runs = sorted(
            (d for d in pass_dir.iterdir() if d.is_dir() and RUN.match(d.name)),
            key=lambda d: int(RUN.match(d.name).group(1)),
        )
        for run in runs:
            for profile in sorted(run.iterdir()):
                if not (profile.is_dir() and profile.name.startswith("apple-macos-27.0-")):
                    continue
                if not profile.name.endswith(f"-glass{glass}"):
                    raise SystemExit(f"{profile} is not at glass{glass}")
                for png in sorted(profile.glob("*.png")):
                    key = f"{profile.name}/{png.stem}"
                    cell = cells.setdefault(key, {"pass": name, "runs": {}})
                    cell["runs"][run.name] = sha256(png)
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    published = {
        f"{p['profileKey']}/{f['sceneId']}": f["file"]
        for p in manifest["profiles"]
        for f in p["fixtures"]
    }
    for key, cell in cells.items():
        states = collections.Counter(cell["runs"].values())
        cell["states"] = dict(states.most_common())
        fixture = published.get(key)
        cell["fixtureSha256"] = sha256(FIXTURES / fixture) if fixture else None
        cell["fixtureAmongStates"] = cell["fixtureSha256"] in states
    return cells


def summarise(label: str, cells: dict[str, dict], out: list[str]) -> None:
    runs = collections.Counter(len(c["runs"]) for c in cells.values())
    by_pass = collections.defaultdict(lambda: collections.Counter())
    for c in cells.values():
        n = len(c["states"])
        top = max(c["states"].values())
        kind = "unanimous" if n == 1 else f"{n} states, plurality {top}-of-{len(c['runs'])}"
        by_pass[c["pass"]][kind] += 1
    out.append(f"## {label}: {len(cells)} cells; runs per cell {dict(runs)}")
    for name in sorted(by_pass):
        out.append(f"  {name}: " + ", ".join(f"{k} {v}" for k, v in sorted(by_pass[name].items())))
    multi = [k for k, c in cells.items() if len(c["states"]) > 1]
    unanimous = len(cells) - len(multi)
    fixture_ok = sum(1 for c in cells.values() if c["fixtureAmongStates"])
    out.append(f"  unanimous {unanimous}, more than one state {len(multi)}")
    out.append(f"  published fixture among the cell's own run states: {fixture_ok} of {len(cells)}")
    out.append("")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--g1a", default=str(Path.home() / "vitrea-w43" / "g1a-run"))
    parser.add_argument("--w29", default=str(Path.home() / "vitrea-w29-27-run"))
    args = parser.parse_args()
    subject = read_side(Path(args.g1a), G1A_PASSES, "0.25")
    reference = read_side(Path(args.w29), W29_PASSES, "0.5")
    out: list[str] = [
        "# The raw run states of both sides, by file SHA-256 (W43 G2, charter clause 7)",
        "",
        f"0.25 side: {args.g1a} passes {', '.join(G1A_PASSES)} (run-N only, quarantines excluded)",
        f"0.5 side:  {args.w29} passes {', '.join(W29_PASSES)}",
        "",
    ]
    summarise("0.25 side (G1a, W39 side bundle, 2026-10-01)", subject, out)
    summarise("0.5 side (W29 G1, original bundle, 2026-09-18/19)", reference, out)
    paired = sum(1 for k in subject if k.replace("-glass0.25/", "-glass0.5/") in reference)
    out.append(f"0.25 cells with a 0.5 counterpart in W29's raw runs: {paired} of {len(subject)}")
    (HERE / "raw-states.txt").write_text("\n".join(out) + "\n")
    (HERE / "raw-states.json").write_text(
        json.dumps({"subject": subject, "reference": reference}, indent=1, sort_keys=True) + "\n"
    )
    print("\n".join(out))


if __name__ == "__main__":
    main()
