"""W43 G2 stage two: G1b's bridges read (charter clause 3; §5.199b §4), beside G1a's.

Reads, and writes only beside itself:
- G1b's 84 committed bridge cell-runs, ``results/2026-10-02-w43-g1b-sitting/attest/*/run-*/bridge.json``;
- G1b's bar (``results/2026-10-02-w43-g1b-sitting/bar/bar.json.gz``, JSON SHA-256 565b33b1...), read from
  the archive before this child: its bridge strata;
- G1a's 168 bridge cell-runs and stage one's reading of them (``../bridges/bridges.json``);
- W29's raw run states at 0.5 (``../bar/raw-states.json``) and W42's sentinel states under both protocols
  (``results/2026-10-01-w43-g0-declaration/bridges/sentinel-references.json``);
- stage one's measurement of G1a's bridge captures against the 0.5 fixtures under the hashed native-delta
  bar (``../bar/rehearsal/null-pairs-measured.json``; bar-declaration.md a8659d7e...).

For every G1b cell-run: its frame against G1a's frames of the same cell at the same point (opening or
closing), against W29's and W42's states, and, where the frame is one G1a produced, the native-delta reading
stage one already took of that same frame. A frame equal by SHA-256 to one already measured needs no new
measurement: the metrics are a function of the pixels.

    python3.12 -B bridges-g1b.py   # writes bridges-g1b.txt and bridges-g1b.json
"""

from __future__ import annotations

import collections
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVID = HERE.parent
RESULTS = EVID.parent
G1B = RESULTS / "2026-10-02-w43-g1b-sitting"
G0 = RESULTS / "2026-10-01-w43-g0-declaration"
SENTINEL_TWIN = {
    "f-checker64-rrect-lg__rest": "checkerboard-64__rrect-lg__rest",
    "f-checker64-rrect-lg__inactive": "checkerboard-64__rrect-lg__inactive",
    "f-impulse-rrect-md__rest": "impulse__rrect-md__rest",
    "f-impulse-rrect-md__inactive": "impulse__rrect-md__inactive",
}


def short(sha: str) -> str:
    return sha[:12]


def group_of(pass_name: str) -> str:
    if pass_name.startswith("open-w42"):
        return "opening, W42 sentinels"
    if pass_name.startswith("open-canonical"):
        return "opening, canonical cells"
    return "closing, W42 sentinels"


def endpoint_of(cell: str) -> str:
    profile, scene = cell.split("/")
    scale, scheme = profile.split("-")[3:5]
    return f"{scale}-{scheme}-{'receded' if '__inactive' in scene else 'active'}"


def main() -> None:
    out: list[str] = []
    say = out.append
    record: dict = {"cellRuns": [], "g1bBarBridgeStrata": {}, "againstG1a": {}}

    runs = []
    for path in sorted(G1B.glob("attest/*/run-*/bridge.json")):
        doc = json.loads(path.read_text())
        for cell in doc["cells"]:
            runs.append({
                "group": group_of(path.parent.parent.name),
                "pass": path.parent.parent.name,
                "run": doc["run"],
                "cell": cell["cell"],
                "verdict": cell["verdict"],
                "frameSha256": cell["frameSha256"],
                "referenceSha256": cell["referenceSha256"],
                "pixelsDiffering": cell.get("pixelsDiffering", 0),
                "maxCodes": cell.get("maxCodes", 0.0),
                "statistics": cell.get("statistics"),
                "worstDelta": cell.get("worstDelta", 0.0),
            })
    g1a = json.loads((EVID / "bridges" / "bridges.json").read_text())["cellRuns"]
    w29 = json.loads((EVID / "bar" / "raw-states.json").read_text())["reference"]
    sentinels = json.loads((G0 / "bridges" / "sentinel-references.json").read_text())["byEndpoint"]
    null_rows = json.loads((EVID / "bar" / "rehearsal" / "null-pairs-measured.json").read_text())["rows"]
    null_by_frame = {}
    for row in null_rows:
        # the null pairs name their subject image by path; stage one's G1a bridge frames are the same bytes
        null_by_frame.setdefault(row["label"], row)

    say("# W43 G2 stage two: G1b's bridges read (clause 3; §5.199b §4), beside G1a's (§5.200 §3)")
    say("")
    say("## The 84 cell-runs, from the committed bridge.json files, beside G1a's 2x cell-runs")
    say("")
    say("| bridge | G1b cell-runs | by bytes | by regions | worst region delta | G1a's 2x cell-runs | by bytes | by regions |")
    say("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    totals = collections.Counter()
    for group in ("opening, W42 sentinels", "opening, canonical cells", "closing, W42 sentinels"):
        b = [r for r in runs if r["group"] == group]
        a = [r for r in g1a if r["group"] == group and "-2x-" in r["cell"]]
        row = (len(b), sum(r["verdict"] == "AGREE (bytes)" for r in b), sum(r["verdict"] == "AGREE (regions)" for r in b),
               max((r["worstDelta"] or 0.0) for r in b), len(a), sum(r["verdict"] == "AGREE (bytes)" for r in a),
               sum(r["verdict"] == "AGREE (regions)" for r in a))
        totals.update(dict(zip(("b", "bb", "br", "x", "a", "ab", "ar"), row)))
        say(f"| {group} | {row[0]} | {row[1]} | {row[2]} | {row[3]:.1f} | {row[4]} | {row[5]} | {row[6]} |")
    say(f"| **all** | **{totals['b']}** | **{totals['bb']}** | **{totals['br']}** | **0.0** | **{totals['a']}** | "
        f"**{totals['ab']}** | **{totals['ar']}** |")
    other = [r for r in runs if r["verdict"] not in ("AGREE (bytes)", "AGREE (regions)")]
    say(f"\nG1b verdicts other than the two agreements: {len(other)}.")
    say("")

    say("## Every G1b frame against G1a's, W29's and W42's states of the same cell")
    say("")
    g1a_frames = collections.defaultdict(collections.Counter)
    for r in g1a:
        when = "open" if r["group"].startswith("opening") else "close"
        g1a_frames[(r["cell"], when)][r["frameSha256"]] += 1
    g1b_frames = collections.defaultdict(collections.Counter)
    for r in runs:
        when = "open" if r["group"].startswith("opening") else "close"
        g1b_frames[(r["cell"], when)][r["frameSha256"]] += 1
    say(f"{'cell':<78} {'when':<5} {'G1b states':<22} {'G1a states':<30} {'in G1a':<6} {'in W29':<6} W42 long/normal")
    for (cell, when), counter in sorted(g1b_frames.items()):
        profile, scene = cell.split("/")
        twin = SENTINEL_TWIN.get(scene, scene)
        w29_states = w29.get(f"{profile}/{twin}", {}).get("states", {})
        a_states = g1a_frames.get((cell, when), collections.Counter())
        in_a = all(f in a_states for f in counter)
        in_w29 = all(f in w29_states for f in counter) if w29_states else None
        w42 = ""
        if scene in SENTINEL_TWIN:
            ref = sentinels.get(endpoint_of(cell), {}).get(scene, {})
            long_ = ref.get("long", {}).get("states", {})
            normal = ref.get("normal", {}).get("states", {})
            w42 = (f"{'Y' if all(f in long_ for f in counter) else 'n'}/"
                   f"{'Y' if all(f in normal for f in counter) else 'n'}")
        say(f"{cell:<78} {when:<5} {str({short(k): v for k, v in counter.items()}):<22} "
            f"{str({short(k): v for k, v in a_states.items()}):<30} {'Y' if in_a else 'n':<6} "
            f"{'—' if in_w29 is None else ('Y' if in_w29 else 'n'):<6} {w42}")
        record["againstG1a"][f"{cell} {when}"] = {
            "g1b": dict(counter), "g1a": dict(a_states), "allInG1a": in_a, "allInW29": in_w29, "w42LongNormal": w42,
        }
    say("")
    in_a = sum(1 for v in record["againstG1a"].values() if v["allInG1a"])
    long_ok = [v for v in record["againstG1a"].values() if v["w42LongNormal"]]
    say(f"G1b groups whose every frame is one G1a produced at the same bridge point: {in_a} of {len(g1b_frames)}; "
        f"sentinel groups on a W42 long-protocol state: {sum(1 for v in long_ok if v['w42LongNormal'].startswith('Y'))} "
        f"of {len(long_ok)}.")
    multi = {k: v for k, v in g1b_frames.items() if len(v) > 1}
    say(f"(cell, opening/closing) groups of three runs at G1b with more than one state: {len(multi)}")
    say("")

    say("## The region-only cell-runs, under the hashed bars")
    say("")
    region = [r for r in runs if r["verdict"] == "AGREE (regions)"]
    for r in region:
        profile, scene = r["cell"].split("/")
        same_in_g1a = [a for a in g1a if a["cell"] == r["cell"] and a["frameSha256"] == r["frameSha256"]]
        say(f"- {r['pass']} run {r['run']}: `{r['cell']}` frame `{short(r['frameSha256'])}` against `{short(r['referenceSha256'])}`;"
            f" {r['pixelsDiffering']} px at <= {r['maxCodes']:.0f} codes; {r['statistics']} region statistics, worst delta {r['worstDelta']}")
        if same_in_g1a:
            labels = [f"canonical:{a['pass']}/run-{a['run']}/{scene}" for a in same_in_g1a]
            measured = [null_by_frame[label] for label in labels if label in null_by_frame]
            say(f"  the same frame as G1a's {', '.join(a['pass'] + ' run ' + str(a['run']) for a in same_in_g1a)}")
            if measured:
                m = measured[0]
                moved = sorted(k for k, v in m["moved"].items() if v)
                say(f"  stage one measured that frame against the 0.5 fixture under the native-delta bar (a8659d7e...):"
                    f" {len(moved)} metrics read moved, at bodyLevelDelta {m['metrics']['bodyLevelDelta']:.2e},"
                    f" interiorMeanDelta {m['metrics']['interiorMeanDelta']:.2e},"
                    f" highlightBinDeltaMax {m['metrics']['highlightBinDeltaMax']:.2e}; the bridge null's own ceiling")
        say(f"  W29's runs of the cell: {{{', '.join(f'{short(k)}: {v}' for k, v in w29.get(r['cell'], {}).get('states', {}).items())}}}")
        say("")

    say("## G1b's own bar on its bridge strata (bar.json.gz, read from the archive; §5.199b §5)")
    say("")
    bar = json.loads(gzip.decompress((G1B / "bar" / "bar.json.gz").read_bytes()))
    strata = collections.defaultdict(collections.Counter)
    for row in bar["rows"]:
        if row["stratum"] in ("open-canonical", "open-w42", "close-w42"):
            strata[row["stratum"]][row["status"].split(":")[0]] += 1
            strata[row["stratum"]][f"bar {row['bar']}"] += 1
    for name, counter in sorted(strata.items()):
        say(f"  {name:<15} " + ", ".join(f"{k} {v}" for k, v in sorted(counter.items())))
        record["g1bBarBridgeStrata"][name] = dict(counter)
    say("")
    say("Every G1b bridge cell is unanimous over its three runs, so its bar is exactly 0.5 code and the")
    say("clause 3 tolerance max(1 code, bar) is one code; every region agreement above sits at delta 0.0.")
    record["cellRuns"] = runs
    (HERE / "bridges-g1b.txt").write_text("\n".join(out) + "\n")
    (HERE / "bridges-g1b.json").write_text(json.dumps(record, indent=1) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
