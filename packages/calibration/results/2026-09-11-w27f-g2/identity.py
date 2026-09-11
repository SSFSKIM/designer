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

Two stops are decided here and they are reported apart. **S3** asks whether the
sampled path's digests moved; **S4** asks whether the instrument repeats itself.
They fail for different reasons, they are answered by different evidence, and a
single verdict over both says "moved" on a head where nothing moved. Stops S1 and
S2 — the bound's own clauses — belong to `verdict.py` and are not touched here.

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

# What this gate may say about a stop it trips, and what it may not. The
# declaration worded S4 without scoping it and forbade re-interpreting a bound
# after it is declared; W27 Decision Log 13 is the user's own precedent on that
# move. So a tripped S4 is recorded here as tripped and unresolved, with the
# gate's reading of it carried as a recommendation. An evidence file that
# silently resolved its own stop would be the thing the rule exists to prevent.
S4_AS_DECLARED = ('declaration.md §6: "Any capture is not byte-repeatable over its two loads, or '
                  'any capture reports a diagnostic." The wording is unscoped, and the same '
                  'section forbids narrowing a clause after the read.')
S4_RECOMMENDATION = (
    "The gate recommends, and does not rule, that an instrument stop be read as scoped to the arms "
    "the bound is stated on: contract X1 makes every measured claim a WebGPU-tier claim and the "
    "CSS tier a record, and the capture that tripped this is a record-only CSS arm on one cell, "
    "byte-repeatable on every arm the bound touches. That is an argument for a future gate's "
    "wording, not a licence to narrow this one's.")
S4_RULING = ("Unresolved. Narrowing a declared stop after the read is the user's decision under "
             "W27 Decision Log 13 — a bound is not re-interpreted after it is declared.")


def digests(reading):
    """`{scheme: {scene: {arm: sha256}}}` out of a reading, ignoring the native rows.

    An arm whose capture carries no digest is kept with `None` rather than
    dropped. A dropped arm is indistinguishable from an arm that was never asked
    for, and this comparison's whole value is that it can tell those apart.
    """
    out = {}
    for scheme, record in reading.get("schemes", {}).items():
        rows = {}
        for row in record.get("rows", []):
            rows[row["scene"]] = {arm: value.get("sha256")
                                  for arm, value in row.get("readings", {}).items()
                                  if arm != "native"}
        out[scheme] = rows
    return out


def compare(before, after):
    """Per scheme and arm: which scenes reproduce, which moved, which are absent.

    The comparison iterates the **record**, not the read. Iterating the read
    makes absence look like agreement: a capture that was truncated, or an arm
    whose digest went missing, simply produces no entry, no count and no stop,
    and the phase still reports "identical" over whatever survived.

    Absence has two shapes and they are not the same fact. A scene the read did
    not touch at all is a scope decision — this gate deliberately reads two of
    the ten holdout scenes (`declaration.md` §0) — and is reported as `notRead`.
    A scene the read *did* touch but which is missing an arm the record has, or
    whose arm came back without a digest, is a truncated capture: the read
    claimed that scene and did not deliver it. Those are `truncated`, and they
    stop the comparison.
    """
    report = {}
    for scheme in sorted(set(before) | set(after)):
        old, new = before.get(scheme, {}), after.get(scheme, {})
        arms, not_read, truncated = {}, {}, []
        for scene in sorted(set(old) | set(new)):
            recorded_arms, read_arms = old.get(scene, {}), new.get(scene)
            if read_arms is None or not any(sha is not None for sha in read_arms.values()):
                if recorded_arms:
                    not_read[scene] = sorted(recorded_arms)
                continue
            for arm in sorted(set(recorded_arms) | set(read_arms)):
                recorded, sha = recorded_arms.get(arm), read_arms.get(arm)
                if recorded is None and sha is None:
                    continue
                entry = arms.setdefault(arm, {"identical": [], "moved": [], "noRecord": []})
                if sha is None:
                    truncated.append({"scene": scene, "arm": arm,
                                      "why": "the record has this arm and the read does not"
                                             if arm not in read_arms
                                             else "the read carries this arm with no digest"})
                elif recorded is None:
                    entry["noRecord"].append(scene)
                elif recorded == sha:
                    entry["identical"].append(scene)
                else:
                    entry["moved"].append({"scene": scene, "recorded": recorded, "read": sha})
        for entry in arms.values():
            entry["identical"].sort()
            entry["noRecord"].sort()
            entry["moved"].sort(key=lambda m: m["scene"])
        report[scheme] = {"arms": arms, "notRead": not_read, "truncated": truncated}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", type=Path, default=Path("/tmp/w27f-g2"))
    parser.add_argument("--out", type=Path, default=HERE / "identity.json")
    args = parser.parse_args()

    phases = {}
    sampled_stops, instrument_stops, coverage_stops = [], [], []
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
            "arms": {scheme: block["arms"] for scheme, block in report.items()},
            "notRead": {scheme: block["notRead"] for scheme, block in report.items()},
            "truncated": {scheme: block["truncated"] for scheme, block in report.items()},
        }
        for scheme, block in report.items():
            for arm, entry in block["arms"].items():
                if entry["moved"] and arm in SAMPLED_ARMS:
                    sampled_stops.append(
                        f"S3 {phase}/{scheme}/{arm}: {len(entry['moved'])} of "
                        f"{len(entry['moved']) + len(entry['identical'])} cells moved — "
                        + ", ".join(m["scene"] for m in entry["moved"]))
            for case in block["truncated"]:
                coverage_stops.append(
                    f"coverage {phase}/{scheme}/{case['arm']}: {case['scene']} — {case['why']}")
        for scheme, noise in phases[phase]["nonDeterministicCaptures"].items():
            if noise:
                instrument_stops.append(f"S4 {phase}/{scheme}: non-deterministic captures {noise}")

    result = {
        "gate": "W27f G2",
        "scratch": str(args.scratch),
        # S3 and S4 are two different questions about two different things, and
        # one field for both is why an earlier run of this file reported
        # `identity: moved` on a head where no sampled digest had moved at all.
        # The bound's own stops, S1 and S2, are not decided here: verdict.json
        # decides those.
        "scope": "S3 (the sampled path's digests) and S4 (the instrument's repeatability). "
                 "Clause A and Clause B — stops S1 and S2 — are decided in verdict.json.",
        "phases": phases,
        "coverageStops": coverage_stops,
        "sampledPathStops": sampled_stops,
        "instrumentStops": instrument_stops,
        "sampledPathIdentity": "unmoved" if not (sampled_stops or coverage_stops) else "moved",
        "instrumentRepeatability": "byte-repeatable" if not instrument_stops
                                   else "one or more captures are not byte-repeatable",
        "unresolvedStops": [] if not instrument_stops else [
            {"stop": "S4", "declaredAs": S4_AS_DECLARED, "tripped": instrument_stops,
             "gateRecommendation": S4_RECOMMENDATION, "ruling": S4_RULING}],
    }
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
            not_read = record["notRead"][scheme]
            if not_read:
                print(f"{phase:9s} {scheme:5s} {'not read':17s} {len(not_read)} recorded scenes "
                      "outside this gate's scope: " + ", ".join(sorted(not_read)))
    print()
    for stop in coverage_stops + sampled_stops + instrument_stops:
        print(f"  {stop}")
    print(f"sampled path: {result['sampledPathIdentity']}    "
          f"instrument: {result['instrumentRepeatability']}")


if __name__ == "__main__":
    main()
