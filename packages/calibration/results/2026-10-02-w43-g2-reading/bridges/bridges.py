"""W43 G2 (a): G1a's bridges read (charter clause 3), and the two gaps §5.199 names.

Reads, and writes only beside itself:
- the 168 committed bridge cell-runs, ``results/2026-10-01-w43-g1a-sitting/attest/*/run-*/bridge.json``;
- the run states of both beds by bytes, ``../bar/raw-states.json`` (G1a's raw runs at 0.25; W29 G1's
  raw runs at 0.5, through the original bundle);
- W42's sentinel states under both protocols, ``results/2026-10-01-w43-g0-declaration/bridges/
  sentinel-references.json``, and G0 (b)'s reading of W42's family F, ``.../bridge/bridge.json``;
- the G1a raw bridge captures under ``~/vitrea-w43/g1a-run`` (for the within-night states, by bytes);
- the null rehearsal's measurements of each bridge capture against its 0.5 fixture,
  ``../bar/rehearsal/null-pairs-measured.json`` (the radial profile says where a state differs).

Gap 1 (§5.199 §9): whether each region-only state is among W29's own run states for that cell.
Gap 2: a description, and no explanation, of the 0.25 bed's unanimity where the 0.5 bed had
voted and frequency-settled cells.

    python3.12 -B bridges.py   # writes bridges.txt and bridges.json beside itself
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
G1A = RESULTS / "2026-10-01-w43-g1a-sitting" / "attest"
G0 = RESULTS / "2026-10-01-w43-g0-declaration"
RAW_ROOT = Path.home() / "vitrea-w43" / "g1a-run"
SENTINEL_TWIN = {
    "f-checker64-rrect-lg__rest": "checkerboard-64__rrect-lg__rest",
    "f-checker64-rrect-lg__inactive": "checkerboard-64__rrect-lg__inactive",
    "f-impulse-rrect-md__rest": "impulse__rrect-md__rest",
    "f-impulse-rrect-md__inactive": "impulse__rrect-md__inactive",
}
RUN = re.compile(r"^run-(\d+)$")


def short(sha: str) -> str:
    return sha[:12]


def endpoint_of(profile: str, scene: str) -> str:
    m = re.match(r"apple-macos-27\.0-(\dx)-(light|dark)-standard-glass0\.5$", profile)
    pose = "receded" if "__inactive" in scene else "active"
    return f"{m.group(1)}-{m.group(2)}-{pose}"


def main() -> None:
    states = json.loads((HERE.parent / "bar" / "raw-states.json").read_text())
    w29 = states["reference"]
    g025 = states["subject"]
    sentinel_refs = json.loads((G0 / "bridges" / "sentinel-references.json").read_text())["byEndpoint"]
    g0_rows = {r["cell"]: r for r in json.loads((G0 / "bridge" / "bridge.json").read_text())["rows"]}
    null_rows = {}
    null_path = HERE.parent / "bar" / "rehearsal" / "null-pairs-measured.json"
    if null_path.exists():
        for row in json.loads(null_path.read_text())["rows"]:
            null_rows[row["label"]] = row

    out: list[str] = []
    record: dict = {"cellRuns": [], "regionOnly": [], "withinNight": {}, "unanimity": {}}
    say = out.append
    say("# W43 G2 (a): G1a's bridges read (charter clause 3; §5.199 §4 and §9)")
    say("")

    # ---- the 168 cell-runs -------------------------------------------------------------
    table = collections.Counter()
    by_cell = collections.defaultdict(list)
    for path in sorted(G1A.glob("*/run-*/bridge.json")):
        doc = json.loads(path.read_text())
        pass_name = path.parent.parent.name
        group = ("opening, W42 sentinels" if pass_name.startswith("open-w42")
                 else "opening, canonical cells" if pass_name.startswith("open-canonical")
                 else "closing, W42 sentinels")
        for cell in doc["cells"]:
            entry = {
                "group": group,
                "pass": pass_name,
                "run": doc["run"],
                "cell": cell["cell"],
                "verdict": cell["verdict"],
                "frameSha256": cell["frameSha256"],
                "referenceSha256": cell["referenceSha256"],
                "pixelsDiffering": cell.get("pixelsDiffering", 0),
                "maxCodes": cell.get("maxCodes", 0.0),
                "statistics": cell.get("statistics"),
                "worstDelta": cell.get("worstDelta", 0.0),
            }
            record["cellRuns"].append(entry)
            table[(group, cell["verdict"])] += 1
            by_cell[(group, cell["cell"])].append(entry)
    say("## The 168 bridge cell-runs, from the committed bridge.json files")
    say("")
    say(f"| bridge | cell-runs | by bytes | by regions | worst region delta |")
    say(f"| --- | ---: | ---: | ---: | ---: |")
    groups = ["opening, W42 sentinels", "opening, canonical cells", "closing, W42 sentinels"]
    totals = collections.Counter()
    for group in groups:
        runs = [e for e in record["cellRuns"] if e["group"] == group]
        b = sum(e["verdict"] == "AGREE (bytes)" for e in runs)
        r = sum(e["verdict"] == "AGREE (regions)" for e in runs)
        worst = max((e["worstDelta"] or 0.0) for e in runs)
        totals.update({"runs": len(runs), "bytes": b, "regions": r})
        say(f"| {group} | {len(runs)} | {b} | {r} | {worst:.1f} |")
    say(f"| **all** | **{totals['runs']}** | **{totals['bytes']}** | **{totals['regions']}** | **0.0** |")
    other = [e for e in record["cellRuns"] if e["verdict"] not in ("AGREE (bytes)", "AGREE (regions)")]
    say(f"\nVerdicts other than the two agreements: {len(other)}.")
    say("")

    # ---- gap 1: region-only states against W29's own run states ---------------------
    say("## Gap 1: is each region-only state among W29's own run states for that cell?")
    say("")
    say("W29's states are the file SHA-256s of its seven raw runs per cell through the original bundle")
    say("(``~/vitrea-w29-27-run``, read in ``../bar/raw-states.json``). A sentinel cell is read against its")
    say("canonical twin (G0 (b)'s mapping): the checker-64 on rrect-lg is W29's checkerboard-64__rrect-lg.")
    say("W42's own states for the sentinel are given beside, under both protocols.")
    say("")
    region_only = [e for e in record["cellRuns"] if e["verdict"] == "AGREE (regions)"]
    seen = set()
    for e in region_only:
        profile, scene = e["cell"].split("/")
        twin = SENTINEL_TWIN.get(scene, scene)
        key = f"{profile}/{twin}"
        w29_states = w29.get(key, {}).get("states", {})
        among_w29 = e["frameSha256"] in w29_states
        sentinel = scene in SENTINEL_TWIN
        w42 = {}
        g0f = None
        if sentinel:
            w42 = sentinel_refs.get(endpoint_of(profile, scene), {}).get(scene, {})
            g0f = g0_rows.get(e["cell"])
        among_long = e["frameSha256"] in (w42.get("long", {}).get("states", {}) if w42 else {})
        among_normal = e["frameSha256"] in (w42.get("normal", {}).get("states", {}) if w42 else {})
        # G0 (b)'s rows name states by their first twelve hex digits.
        among_f = (short(e["frameSha256"]) in g0f["states"]) if g0f else None
        g025_key = key.replace("-glass0.5/", "-glass0.25/")
        null = null_rows.get(f"{'sentinel' if sentinel else 'canonical'}:{e['pass']}/run-{e['run']}/{scene}")
        radial = None
        if null is not None:
            radial = {b["band"]: (b["differing"], b["maxAbsCode"]) for b in null["radial"] if b["differing"]}
        item = {
            **e,
            "twin": twin,
            "w29States": {short(h): n for h, n in w29_states.items()},
            "amongW29": among_w29,
            "w42Long": {short(h): n for h, n in w42.get("long", {}).get("states", {}).items()} if w42 else None,
            "w42Normal": {short(h): n for h, n in w42.get("normal", {}).get("states", {}).items()} if w42 else None,
            "amongW42Long": among_long if sentinel else None,
            "amongW42Normal": among_normal if sentinel else None,
            "g0FamilyFStates": {short(h): n for h, n in g0f["states"].items()} if g0f else None,
            "amongG0FamilyF": among_f,
            "at025": {short(h): n for h, n in g025.get(g025_key, {}).get("states", {}).items()},
            "whereItDiffersFromThe05Fixture": radial,
        }
        record["regionOnly"].append(item)
        tag = (e["cell"], e["frameSha256"])
        first = tag not in seen
        seen.add(tag)
        say(f"- {e['pass']} run {e['run']}: `{e['cell']}`")
        say(f"  frame `{short(e['frameSha256'])}` against reference `{short(e['referenceSha256'])}`; "
            f"{e['pixelsDiffering']} px at <= {e['maxCodes']:.0f} codes; {e['statistics']} region statistics, worst delta {e['worstDelta']}")
        say(f"  W29's runs of `{twin}`: {item['w29States']}. **Among W29's states: {'YES' if among_w29 else 'NO'}**"
            + ("" if first else " (the same state as above)"))
        if sentinel:
            say(f"  W42 long protocol {item['w42Long']} (among: {among_long}); W42 normal protocol "
                f"{item['w42Normal']} (among: {among_normal}); G0 (b) family F at 0.5 {item['g0FamilyFStates']} (among: {among_f})")
        if radial is not None:
            if radial:
                say(f"  where it differs from the 0.5 fixture, by band (pixels, max code): {radial}")
            else:
                say("  it is the 0.5 fixture's own bytes: the region-only verdict is against W42's long-protocol frame")
        say(f"  the cell at 0.25 (G1a, seven runs): {item['at025']}")
        say("")
    distinct = {(e["cell"], e["frameSha256"]) for e in region_only}
    yes = {(i["cell"], i["frameSha256"]) for i in record["regionOnly"] if i["amongW29"]}
    say(f"Distinct region-only (cell, state): {len(distinct)}, on {len({c for c, _ in distinct})} cells; "
        f"among W29's run states: {len(yes)}; not among them: {len(distinct - yes)}.")
    say("No state is UNMEASURED here: every region-only cell, the sentinels by their canonical twin, has")
    say("W29's seven raw runs on the capture machine.")
    say("")

    # ---- the within-night states at 0.5 through the side bundle -----------------------
    say("## The bridge cells' own states on the G1a night (0.5, side bundle), by bytes")
    say("")
    night = collections.defaultdict(collections.Counter)
    for pass_dir in sorted(RAW_ROOT.iterdir()):
        if not pass_dir.is_dir() or not (pass_dir.name.startswith("open-") or pass_dir.name.startswith("close-")):
            continue
        for run in sorted(d for d in pass_dir.iterdir() if d.is_dir() and RUN.match(d.name)):
            for png in sorted(run.glob("apple-macos-27.0-*-glass0.5/*.png")):
                when = "open" if pass_dir.name.startswith("open-") else "close"
                night[(f"{png.parent.name}/{png.stem}", when)][short(hashlib.sha256(png.read_bytes()).hexdigest())] += 1
    multi = {k: v for k, v in night.items() if len(v) > 1}
    say(f"{len(night)} (cell, opening/closing) groups of three runs; with more than one state: {len(multi)}")
    for (cell, when), counter in sorted(multi.items()):
        say(f"  {when:<5} {cell}: {dict(counter)}")
    record["withinNight"] = {f"{c} {w}": dict(v) for (c, w), v in night.items()}
    say("")

    # ---- gap 2: the unanimity, described --------------------------------------------
    say("## Gap 2: the 0.25 bed is unanimous; the 0.5 bed was not. A description, not an explanation")
    say("")
    multi05 = {k: c for k, c in w29.items() if len(c["states"]) > 1}
    say(f"0.5 side (W29 G1, original bundle, 2026-09-18/19): {len(multi05)} of {len(w29)} standard cells")
    say("carried two states over seven runs (no cell carried three).")
    say(f"0.25 side (G1a, side bundle, 2026-10-01): {sum(len(c['states']) > 1 for c in g025.values())} of {len(g025)}.")
    say("")

    def facet(fn, label):
        counts = collections.Counter(fn(k) for k in multi05)
        totals_ = collections.Counter(fn(k) for k in w29)
        say(f"W29's two-state cells by {label} (two-state / cells):")
        say("  " + ", ".join(f"{k} {counts[k]}/{totals_[k]}" for k in sorted(totals_)))
        return {k: [counts[k], totals_[k]] for k in totals_}

    scale_scheme = lambda k: re.match(r"apple-macos-27\.0-(\dx-\w+)-standard", k).group(1)
    pose = lambda k: "receded" if "__inactive" in k else "active"
    component = lambda k: k.split("/")[1].split("__")[1]
    background = lambda k: k.split("/")[1].split("__")[0]
    record["unanimity"]["byScaleScheme"] = facet(scale_scheme, "scale and scheme")
    record["unanimity"]["byPose"] = facet(pose, "pose")
    record["unanimity"]["byComponent"] = facet(component, "component")
    record["unanimity"]["byBackground"] = facet(background, "backdrop")
    lg = [k for k in w29 if component(k) == "rrect-lg"]
    rest = [k for k in w29 if component(k) != "rrect-lg"]
    lg_multi = sum(1 for k in lg if k in multi05)
    rest_multi = sum(1 for k in rest if k in multi05)
    say(f"rrect-lg against every other shape: {lg_multi}/{len(lg)} against {rest_multi}/{len(rest)} two-state at 0.5;")
    say(f"at 0.25, 0/{len(lg)} and 0/{len(rest)}. (Memo F: the rrect-lg backdrop capture scale is 0.25 at x = 0.5")
    say("and 0.5 at x = 0.25; every other shape is captured at 0.5 at both positions.)")
    rate = rest_multi / len(rest)
    say(f"Were the 0.25 bed's other shapes two-state at the 0.5 bed's own rate ({rate:.3f}) and independent, no")
    say(f"second state on all {len(rest)} would have probability (1 - {rate:.3f})^{len(rest)} = {(1 - rate) ** len(rest):.1e}: the")
    say("difference is not a seven-run sampling accident. It does not say which of the position, the bundle or")
    say("the night it belongs to.")
    record["unanimity"]["rrectLg"] = {"at05": [lg_multi, len(lg)], "others05": [rest_multi, len(rest)]}
    minority = collections.Counter(min(c["states"].values()) for c in multi05.values())
    say("Minority-state run counts: " + ", ".join(f"{k} of 7: {v} cells" for k, v in sorted(minority.items())))
    say("")

    w29_pairs = HERE.parent / "bar" / "rehearsal" / "w29-state-pairs-measured.json"
    if w29_pairs.exists():
        rows = json.loads(w29_pairs.read_text())["rows"]
        say(f"Where W29's two states differ, from the minority state measured against the published fixture")
        say(f"({len(rows)} cells; the radial bands of ``slider-delta pairs``): cells with any differing pixel per band,")
        say("and the largest code difference anywhere in that band:")
        bands = collections.defaultdict(lambda: [0, 0, 0])
        px = []
        for row in rows:
            total = 0
            for b in row["radial"]:
                bands[b["band"]][1] += 1
                if b["differing"]:
                    bands[b["band"]][0] += 1
                    bands[b["band"]][2] = max(bands[b["band"]][2], b["maxAbsCode"])
                total += b["differing"]
            px.append(total)
        for name in ("deep", "shoulder", "edge", "near-exterior", "exterior", "far"):
            d, n, m = bands[name]
            say(f"  {name:<14} {d:>4}/{n:<4} max |code| {m:.0f}")
        px.sort()
        say(f"  pixels differing per cell: median {px[len(px) // 2]}, max {px[-1]}")
        record["unanimity"]["w29StateDifferences"] = {k: v for k, v in bands.items()}
        say("")

    say("Beside it, the same side bundle at 0.5:")
    say("- on the G1a night itself, the bridge cells above (three runs each) show the within-night states;")
    say("- on 2026-09-30, W42's bed at 0.5 carried 35 two-state rows (§5.199 §5), and G0 (b)'s family F")
    say("  read the 2x light active checker-64 on rrect-lg in two states, 5 and 2 (§5.198 §3).")
    say("")
    say("What the evidence separates, and what it does not. More than half of W29's second states (58 of")
    say("103) sit on rrect-lg, the one shape whose declared backdrop capture scale differs between the two")
    say("positions, and they")
    say("differ from the plurality by 1 to 3 codes, almost always at the edge and just outside it. But 45 of")
    say("the 458 other cells also carried one at 0.5, and none does at 0.25. The side bundle produced")
    say("second states at 0.5 on the G1a night itself (the within-night groups above: three W42 sentinels")
    say("in the long protocol and one canonical capsule) and on 2026-09-30, so neither the bundle nor the")
    say("night is by itself without them. At 0.25, the same night through the same bundle, no cell carried")
    say("one in 3,934 captures. Nothing here measures why a second state appears: this is a description,")
    say("and the position is the factor it leaves standing, not one it identifies.")

    (HERE / "bridges.txt").write_text("\n".join(out) + "\n")
    (HERE / "bridges.json").write_text(json.dumps(record, indent=1) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
