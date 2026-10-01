"""W43 G2 (1): both sides' run-to-run bars per metric, and the verdict bar they compose.

Reads, and writes nothing but its report:
- ``noise-bar-0.25.json``: the native delta's own ``bar`` command over G1a's raw runs (the 0.25
  side, 562 cells, 21 run pairs each);
- W29 G3b's ``noise-bar.json`` (the 0.5 side, 624 cells, 49 metrics; it reproduces W29 G2's
  32-metric bar exactly, ``bar-reproduction.txt`` there), read on the 562 standard cells the 0.25
  bed mirrors. Its ``bedMinimumNonZeroBar`` is used as committed: over its whole 624-cell bed,
  which is the bar W29's own verdicts were judged against.

Per metric and per signed capture reading, per side: the cells that carry it, the cells whose own
seven runs spread at all, the median and max of those spreads, and the side's fallback; then, over
the 562 0.25 cells, which side and level the declared verdict bar (the larger side) comes from.
Nothing here reads a 0.25 cell against a 0.5 cell.

    python3.12 -B bar-sides.py   # writes bar-sides.txt and bar-sides.json beside itself
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
SUBJECT = HERE / "noise-bar-0.25.json"
REFERENCE = RESULTS / "2026-09-19-w29-g3b-shadow-recede" / "noise-bar.json"


def median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def fmt(value) -> str:
    return "—" if value is None else f"{value:.3e}"


def bound(bar: dict, cell: dict | None, metric: str):
    own = ((cell or {}).get("pairwise") or {}).get(metric, {}).get("max")
    if own is None:
        return None
    if own > 0:
        return (own, "cell")
    floor = bar["bedMinimumNonZeroBar"].get(metric)
    return (0.0, "bed-zero") if floor is None else (floor, "bed-minimum")


def main() -> None:
    subject = json.loads(SUBJECT.read_text())
    reference = json.loads(REFERENCE.read_text())
    assert subject["metrics"] == reference["metrics"], "the two bars must carry the same metrics"
    metrics = subject["metrics"]
    readings = subject["captureReadings"]
    sub_cells = {f"{c['profileKey']} {c['sceneId']}": c for c in subject["cells"]}
    ref_all = {f"{c['profileKey']} {c['sceneId']}": c for c in reference["cells"]}
    ref_cells = {k: v for k, v in ref_all.items() if "-standard-glass0.5" in k}

    out: list[str] = []
    record: dict = {"metrics": {}, "readings": {}}
    say = out.append
    say("# Both sides' run-to-run bars, per metric (W43 G2, charter clause 7)")
    say("")
    say(f"0.25 side: {SUBJECT.name}: {len(subject['cells'])} cells over passes {', '.join(subject['passes'])}; "
        f"runs per cell {dict(Counter(c['runs'] for c in subject['cells']))}")
    say(f"0.5 side:  {REFERENCE.relative_to(RESULTS)}: {len(reference['cells'])} cells, "
        f"{len(ref_cells)} of them standard (the cells the 0.25 bed mirrors)")
    say("")
    say("Columns, per side: cells carrying the metric / cells whose own runs spread at all; median and")
    say("max of the non-zero own spreads; the side's fallback (its bed's smallest non-zero spread, or")
    say("'zero' where its bed resolved none). Then, over the 562 0.25 cells, where the verdict bar")
    say("(the larger side) comes from.")
    say("")
    header = (f"{'metric':<34} {'0.25 n/spread':>14} {'0.25 max':>10} {'0.25 fallback':>14} "
              f"{'0.5 n/spread':>13} {'0.5 med own':>12} {'0.5 max own':>12} {'0.5 fallback':>13}  verdict bar from")
    say(header)
    say("-" * len(header))
    for metric in metrics:
        s_vals = [c["pairwise"][metric]["max"] for c in subject["cells"] if metric in c["pairwise"]]
        r_vals = [c["pairwise"][metric]["max"] for c in ref_cells.values() if metric in c["pairwise"]]
        r_own = [v for v in r_vals if v > 0]
        s_floor = subject["bedMinimumNonZeroBar"].get(metric)
        r_floor = reference["bedMinimumNonZeroBar"].get(metric)
        r_floor_std = min(r_own) if r_own else None
        sources = Counter()
        for key, cell in sub_cells.items():
            ref_key = key.replace("-glass0.25 ", "-glass0.5 ")
            sb = bound(subject, cell, metric)
            rb = bound(reference, ref_cells.get(ref_key), metric)
            if sb is None and rb is None:
                sources["unbarred"] += 1
            elif sb is None or (rb is not None and rb[0] > sb[0]):
                sources[f"reference:{rb[1]}"] += 1
            elif rb is None or sb[0] > rb[0]:
                sources[f"subject:{sb[1]}"] += 1
            else:
                sources[f"both:{sb[1]}" if sb[1] == rb[1] else f"both:{sb[1]}/{rb[1]}"] += 1
        say(
            f"{metric:<34} {f'{len(s_vals)}/{sum(v > 0 for v in s_vals)}':>14} {fmt(max(s_vals) if s_vals else None):>10} "
            f"{('zero' if s_floor is None else fmt(s_floor)):>14} "
            f"{f'{len(r_vals)}/{len(r_own)}':>13} {fmt(median(r_own)):>12} {fmt(max(r_own) if r_own else None):>12} "
            f"{('zero' if r_floor is None else fmt(r_floor)):>13}  "
            + ", ".join(f"{k} {v}" for k, v in sorted(sources.items()))
        )
        record["metrics"][metric] = {
            "subject": {"cells": len(s_vals), "spread": sum(v > 0 for v in s_vals),
                        "max": max(s_vals) if s_vals else None, "fallback": s_floor},
            "reference": {"cells": len(r_vals), "spread": len(r_own), "medianOwn": median(r_own),
                          "maxOwn": max(r_own) if r_own else None, "fallback": r_floor,
                          "standardOnlyMinimumNonZero": r_floor_std},
            "verdictBarFrom": dict(sources),
        }
    say("")
    say("The 0.5 side's fallback is W29's committed bedMinimumNonZeroBar over its 624-cell bed. Over the")
    say("562 standard cells alone the smallest non-zero spread is never smaller (a minimum over a subset),")
    say("and it is recorded per metric in bar-sides.json as standardOnlyMinimumNonZero.")
    say("")
    say("## Signed capture readings (the recede's inputs): run-to-run spread, max - min over seven runs")
    say("")
    say(f"{'reading':<20} {'0.25 n/spread':>14} {'0.25 max':>10} {'0.5 n/spread':>13} {'0.5 med own':>12} {'0.5 max own':>12} {'0.5 min own':>12}")
    for name in readings:
        s_vals = [c["readingSpread"][name] for c in subject["cells"] if name in c["readingSpread"]]
        r_vals = [c["readingSpread"][name] for c in ref_cells.values() if name in c["readingSpread"]]
        r_own = [v for v in r_vals if v > 0]
        say(f"{name:<20} {f'{len(s_vals)}/{sum(v > 0 for v in s_vals)}':>14} {fmt(max(s_vals) if s_vals else None):>10} "
            f"{f'{len(r_vals)}/{len(r_own)}':>13} {fmt(median(r_own)):>12} {fmt(max(r_own) if r_own else None):>12} "
            f"{fmt(min(r_own) if r_own else None):>12}")
        record["readings"][name] = {
            "subject": {"cells": len(s_vals), "spread": sum(v > 0 for v in s_vals), "max": max(s_vals) if s_vals else None},
            "reference": {"cells": len(r_vals), "spread": len(r_own), "medianOwn": median(r_own),
                          "maxOwn": max(r_own) if r_own else None, "minOwn": min(r_own) if r_own else None},
        }
    say("")
    # The check W29 G2 ran on its own bar: cells whose whole-cell metrics spread at all against the
    # cells the sitting published with more than one state. Bytes and metrics, two constructions.
    states = json.loads((HERE / "raw-states.json").read_text())
    multi_bytes = {k.replace("/", " ") for k, c in states["reference"].items() if len(c["states"]) > 1}
    multi_metric = {k for k, c in ref_cells.items()
                    if any(c["pairwise"].get(m, {}).get("max", 0) > 0
                           for m in ("ssimComplement", "oklabDeltaEMean", "edgeWeightedMean"))}
    sub_multi_metric = {k for k, c in sub_cells.items()
                        if any(c["pairwise"].get(m, {}).get("max", 0) > 0 for m in metrics)}
    say("## Two constructions, cell for cell")
    say(f"0.5 side: cells with more than one raw state by bytes {len(multi_bytes)}; cells whose whole-cell")
    say(f"metrics spread at all {len(multi_metric)}; the same set: {multi_bytes == multi_metric}")
    say(f"0.25 side: cells with more than one raw state by bytes "
        f"{sum(len(c['states']) > 1 for c in states['subject'].values())}; cells with ANY metric's spread non-zero "
        f"{len(sub_multi_metric)}")
    record["constructions"] = {
        "referenceMultiStateBytes": len(multi_bytes),
        "referenceSpreadMetrics": len(multi_metric),
        "same": multi_bytes == multi_metric,
        "subjectSpreadAnyMetric": len(sub_multi_metric),
    }
    (HERE / "bar-sides.txt").write_text("\n".join(out) + "\n")
    (HERE / "bar-sides.json").write_text(json.dumps(record, indent=1) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
