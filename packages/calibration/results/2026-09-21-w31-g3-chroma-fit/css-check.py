#!/usr/bin/env python3
"""W31 G3 — does the CSS tier's derived term add REACH? (Decision Log 2 (b); claims §5.164 §5.)

    python3 css-check.py <before-matrix-or-label> <after-label>

The question the ruling asks is not "does the term change the tier" — a gain on
`saturate()` obviously does — but whether it moves ratio (ii), the body's mean
per-pixel chroma over the raw backdrop's, TOWARD the reference's, without moving
the level or the structure. So this prints, per scheme per pose, on the `dom`
tier only:

  ratio (ii) native   what Apple's body carries of its backdrop's chroma
  ratio (ii) web      what this tier carries, before and after
  reach               (after − before) / (native − before): the share of the gap
                      the derived term closes. 0 is "carries nothing"; 1 is the
                      reference; above 1 is an overshoot and is as much a miss.
  R                   the declared statistic, for the record — NOT the objective
                      on this tier, which claims §5.161 §7 (g) (ii) refuses to
                      gate for the structure stop's own reason
  |Δlevel|, sd        the two stops, which bind on BOTH tiers

`chroma-fit.py` is imported rather than restated, so the two readers cannot
disagree about what a row is or about which rows the bed holds.
"""
from __future__ import annotations

import importlib.util
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("chroma_fit", HERE / "chroma-fit.py")
cf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cf)


def dom_bed(rows):
    return [
        r
        for r in rows
        if r["backdrop"] == "photo"
        and not r["tinted"]
        and r["renderer"] == "css"
        and r["scheme"] is not None
        and r["set"] in ("calibration", "validation")
        and r["ratio2Web"] is not None
    ]


def main() -> int:
    before = dom_bed(cf.collect([sys.argv[1]]))
    after = dom_bed(cf.collect([sys.argv[2]]))
    index = {(r["profile"], r["scene"]): r for r in before}

    print("== the CSS tier's derived term: does it add reach? ==")
    print(f"{'scheme':<7}{'pose':<10}{'n':>4}{'r2 native':>11}{'r2 before':>11}{'r2 after':>11}"
          f"{'reach':>9}{'R before':>10}{'R after':>10}")
    for scheme in ("light", "dark"):
        for pose in ("active", "inactive"):
            group = [r for r in after if r["scheme"] == scheme and r["pose"] == pose]
            pairs = [(index.get((r["profile"], r["scene"])), r) for r in group]
            pairs = [(b, a) for b, a in pairs if b is not None]
            if not pairs:
                continue
            n = statistics.median([a["ratio2Native"] for _, a in pairs])
            wb = statistics.median([b["ratio2Web"] for b, _ in pairs])
            wa = statistics.median([a["ratio2Web"] for _, a in pairs])
            reach = (wa - wb) / (n - wb) if abs(n - wb) > 1e-9 else float("nan")
            rb = statistics.median([b["R"] for b, _ in pairs if b["R"] is not None])
            ra = statistics.median([a["R"] for _, a in pairs if a["R"] is not None])
            print(f"{scheme:<7}{pose:<10}{len(pairs):>4}{n:>11.4f}{wb:>11.4f}{wa:>11.4f}"
                  f"{reach:>9.3f}{rb:>10.4f}{ra:>10.4f}")

    print("\n== the stops on this tier, per cell ==")
    print(f"{'profile':<50}{'scene':<38}{'|d|before':>11}{'|d|after':>10}{'growth':>9}"
          f"{'sd %':>9}{'r2 before':>11}{'r2 after':>10}")
    worst_level = worst_growth = worst_sd = 0.0
    failures = 0
    for a in sorted(after, key=lambda r: (r["profile"], r["scene"])):
        b = index.get((a["profile"], a["scene"]))
        if b is None:
            continue
        db = abs((b["levelWeb"] or 0) - (b["levelNative"] or 0))
        da = abs((a["levelWeb"] or 0) - (a["levelNative"] or 0))
        sb, sa = b["structureWeb"] or 0, a["structureWeb"] or 0
        pct = (sa - sb) / sb * 100 if sb else 0.0
        worst_level = max(worst_level, da)
        worst_growth = max(worst_growth, da - db)
        worst_sd = max(worst_sd, abs(pct))
        flag = ""
        if da > 0.055:
            flag, failures = flag + " LEVEL>0.055", failures + 1
        if da - db > 0.005:
            flag, failures = flag + " GROWTH>0.005", failures + 1
        if abs(pct) > 2.0:
            flag, failures = flag + " STRUCTURE>2%", failures + 1
        print(f"{a['profile']:<50}{a['scene']:<38}{db:>11.5f}{da:>10.5f}{da - db:>9.5f}"
              f"{pct:>9.3f}{(b['ratio2Web'] or 0):>11.4f}{(a['ratio2Web'] or 0):>10.4f}{flag}")
    print(f"\nworst |Δlevel| {worst_level:.5f} (stop 0.055); worst growth {worst_growth:+.5f} "
          f"(stop 0.005); worst |Δstructure| {worst_sd:.3f} % (stop 2 %)")
    print(f"stop failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
