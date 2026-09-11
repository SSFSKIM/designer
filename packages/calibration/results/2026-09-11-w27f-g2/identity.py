"""W27f G2: did anything the ledger already measured move at the landing head?

Stop S3 of `declaration.md` asks whether the sampled path is byte-identical to
its claims §5.131 §8 record. This answers that, and more than that: the G1
readings carry a PNG digest for **every** arm of every scene, so the comparison
is run across all seven and reported per arm rather than only on the two the
stop names. An arm that moved is named with its scenes; an arm that did not is
counted.

This decides nothing about the bound. Its job is to say whether the read at this
head is the configuration claims §5.131 measured, so that a miss on the bound
can be attributed — a material that moved, or a bed that did.

    python identity.py --scratch /tmp/w27f-g2 --out identity.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent

# The G1 readings this gate re-reads. Each is committed evidence; neither is
# written by this script.
SOURCES = {
    "candidate": RESULTS / "2026-09-10-w27f-g1-candidate.json",
    "holdout": RESULTS / "2026-09-10-w27f-g1-holdout.json",
}

# Stop S3's own two arms: the texture-sampled route, with and without the hint.
# §5.131 §8 states 20/20 identical for each of them in each scheme, and says in
# the same breath not to extend the statement to whole stack composites.
SAMPLED_ARMS = ("sampled", "sampled-hint")


def digests(reading):
    """`{scheme: {scene: {arm: sha256}}}` out of a reading, ignoring the native rows."""
    out = {}
    for scheme, record in reading.get("schemes", {}).items():
        rows = {}
        for row in record.get("rows", []):
            arms = {}
            for arm, value in row.get("readings", {}).items():
                if arm == "native":
                    continue
                sha = value.get("sha256")
                if sha is not None:
                    arms[arm] = sha
            rows[row["scene"]] = arms
        out[scheme] = rows
    return out


def compare(before, after):
    """Per scheme and arm: which scenes reproduce, which moved, which are absent."""
    report = {}
    for scheme, rows in after.items():
        old = before.get(scheme, {})
        arms = {}
        for scene, got in rows.items():
            for arm, sha in got.items():
                entry = arms.setdefault(arm, {"identical": [], "moved": [], "noRecord": []})
                recorded = old.get(scene, {}).get(arm)
                if recorded is None:
                    entry["noRecord"].append(scene)
                elif recorded == sha:
                    entry["identical"].append(scene)
                else:
                    entry["moved"].append({"scene": scene, "recorded": recorded, "read": sha})
        for entry in arms.values():
            entry["identical"].sort()
            entry["noRecord"].sort()
            entry["moved"].sort(key=lambda m: m["scene"])
        report[scheme] = arms
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", type=Path, default=Path("/tmp/w27f-g2"))
    parser.add_argument("--out", type=Path, default=HERE / "identity.json")
    args = parser.parse_args()

    phases, stops = {}, []
    for phase, source in SOURCES.items():
        reading = json.loads((args.scratch / phase / "reading.json").read_text())
        recorded = json.loads(source.read_text())
        report = compare(digests(recorded), digests(reading))
        phases[phase] = {
            "comparedAgainst": source.name,
            "nonDeterministicCaptures": {
                scheme: record.get("nonDeterministicCaptures")
                for scheme, record in reading.get("schemes", {}).items()
            },
            "arms": report,
        }
        for scheme, arms in report.items():
            for arm, entry in arms.items():
                if entry["moved"] and arm in SAMPLED_ARMS:
                    stops.append(
                        f"S3 {phase}/{scheme}/{arm}: {len(entry['moved'])} of "
                        f"{len(entry['moved']) + len(entry['identical'])} cells moved — "
                        + ", ".join(m["scene"] for m in entry["moved"]))
        for scheme, noise in phases[phase]["nonDeterministicCaptures"].items():
            if noise:
                stops.append(f"S4 {phase}/{scheme}: non-deterministic captures {noise}")

    result = {"gate": "W27f G2", "scratch": str(args.scratch), "phases": phases, "stops": stops,
              "identity": "unmoved" if not stops else "moved"}
    args.out.write_text(f"{json.dumps(result, indent=1)}\n")

    for phase, record in phases.items():
        for scheme, arms in record["arms"].items():
            for arm in sorted(arms):
                entry = arms[arm]
                mark = "MOVED" if entry["moved"] else "identical"
                extra = f" (+{len(entry['noRecord'])} with no record)" if entry["noRecord"] else ""
                print(f"{phase:9s} {scheme:5s} {arm:17s} "
                      f"{len(entry['identical'])}/{len(entry['identical']) + len(entry['moved'])} "
                      f"{mark}{extra}")
    print()
    for stop in stops:
        print(f"  {stop}")
    print(f"identity: {result['identity']}")


if __name__ == "__main__":
    main()
