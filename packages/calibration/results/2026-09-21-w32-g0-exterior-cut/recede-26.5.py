#!/usr/bin/env python3
"""W32 G0 review closure — the recede census on BOTH generations, and the macOS 27
population counted (claims §5.166 §10, findings B1 and N16).

    python3 recede-26.5.py > recede-26.5.txt      # writes recede-26.5.json beside it

§5.166 §7 recorded that Apple's receded window removes no light at all from 3 CSS px
outward on the macOS 27 bed, and left the reader to wonder whether that is something
macOS 27 does. It is not. The same census over the FROZEN macOS 26.5 rows reads the
same thing on every one of them, so the recede has never been an outer shadow on this
bed and the finding is about the material Apple ships rather than about a version of
it. This file is the read that says so.

**It is a READ of committed evidence and of nothing else** (W32 X1, X2, X5). Nothing
under a macOS 26.5-keyed path is written; no capture is taken; no profile, golden,
bound or row of `results/matrix.json` moves. The frozen rows are read at
`--at-documents any` for the reason `exterior-cut.py`'s own `readings()` gives: a
frozen row names a document that is by definition not one of the four this generation
ships, so the `shipped` filter would drop every one of them.

**The instrument is `exterior-cut.py`'s, imported rather than copied.** A second
implementation of the admitted-band rule would be a second thing to keep true, and the
census's whole point is that it is the same statistic read on a different generation.
The one thing overridden is the module's `GENERATION` prefix, which is the only place
the macOS 27 generation is named; the override is scoped to the call and restored, so
§4's macOS 27 half is read through the module in its shipped state.

§4 exists for a different finding. §5.166 §7 said "100 of 100" of a population that is
**121** non-holdout inactive WebGPU rows, and 153 with the holdout admitted. Both
counts are printed here, with the three holdout bands that are the only entries on
either count whose native `a` is not exactly 1.
"""
from __future__ import annotations

import importlib.util
import json
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("w32_exterior_cut", HERE / "exterior-cut.py")
assert _spec is not None and _spec.loader is not None
xc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xc)

FROZEN = "apple-macos-26.5-"
SHIPPED = "apple-macos-27.0-"


@contextmanager
def generation(prefix: str):
    """Read one generation through the shipped instrument, then put it back."""
    before = xc.GENERATION
    xc.GENERATION = prefix
    try:
        yield
    finally:
        xc.GENERATION = before


def load(prefix: str, at_documents: str, with_holdout: bool) -> list[dict]:
    scenes = json.loads(xc.SCENES.read_text())
    span_of = xc.spans_of(scenes["components"])
    with generation(prefix):
        rows = xc.readings(xc.MATRIX, span_of, at_documents, with_holdout)
    for row in rows:
        shape = xc.shape_error(row, "all")
        row["bands"] = shape["bands"]
        row["admitted"] = shape["admitted"]
        row["bandsUsed"] = shape["bandsUsed"]
        row["window"] = xc.window_departure(row)
    return rows


def inactive(rows: list[dict], with_holdout: bool) -> list[dict]:
    return [r for r in rows
            if r["state"] == "inactive" and r["tier"] == "webgpu" and r["bands"]
            and (with_holdout or r["set"] != xc.HOLDOUT)]


def flat(row: dict, side: str) -> bool:
    """§12c's own predicate, transcribed from `exterior-cut.py` and not imported.

    It is defined inside that file's §12c as a closure, so there is nothing to
    import; the two must say the same thing, and the doc comment there is the
    argument for reading the LEVEL rather than the slope.
    """
    entries = xc.affine(row["shadow"], side, "all")
    got = [entries[b] for b in xc.admitted_bands(row, "all") if b in entries]
    return bool(got) and all(
        e["renderedLevelLinear"] == e["backdropMeanLinear"] for e in got)


def edge(rows: list[dict], side: str) -> list[float]:
    out = []
    for row in rows:
        entry = xc.affine(row["shadow"], side, "all").get("0-3")
        if entry is not None:
            out.append(entry["backdropMeanLinear"] - entry["renderedLevelLinear"])
    return out


def census(rows: list[dict], title: str) -> list[dict]:
    print(title)
    print("-" * 160)
    print(f"    {'bed':<38}{'span':>5}{'n':>4}{'nat flat':>10}{'web flat':>10}"
          f"{'0-3 nat':>11}{'0-3 web':>11}{'σ nat':>8}{'σ web':>8}"
          f"{'win nat':>11}{'win web':>11}")
    out = []
    for bed in xc.bed_order(rows):
        for span in xc.SPANS:
            here = [r for r in rows if r["bed"] == bed and r["span"] == span]
            if not here:
                continue
            native_edge, web_edge = edge(here, "Native"), edge(here, "Web")
            sigma_n = sum(1 for r in here
                          if xc.value(r["shadow"], "falloffSigmaNative") is not None)
            sigma_w = sum(1 for r in here
                          if xc.value(r["shadow"], "falloffSigmaWeb") is not None)
            win_n = [r["window"]["native"] for r in here if r["window"]["native"] is not None]
            win_w = [r["window"]["web"] for r in here if r["window"]["web"] is not None]
            record = {
                "bed": bed, "span": span, "n": len(here),
                "nativeFlat": sum(1 for r in here if flat(r, "Native")),
                "webFlat": sum(1 for r in here if flat(r, "Web")),
                "edge03Native": xc.upper_middle(native_edge) if native_edge else None,
                "edge03Web": xc.upper_middle(web_edge) if web_edge else None,
                "sigmaNative": sigma_n, "sigmaWeb": sigma_w,
                "windowNative": xc.upper_middle(win_n) if win_n else None,
                "windowWeb": xc.upper_middle(win_w) if win_w else None,
            }
            out.append(record)
            print(f"    {bed:<38}{span:>5}{len(here):>4}"
                  f"{f'{record["nativeFlat"]}/{len(here)}':>10}"
                  f"{f'{record["webFlat"]}/{len(here)}':>10}"
                  f"{record['edge03Native']:>11.5f}{record['edge03Web']:>11.5f}"
                  f"{f'{sigma_n}/{len(here)}':>8}{f'{sigma_w}/{len(here)}':>8}"
                  f"{record['windowNative']:>11.6f}{record['windowWeb']:>11.6f}")
    print()
    return out


def odd_slopes(rows: list[dict]) -> list[dict]:
    """Every admitted band whose NATIVE slope is not exactly 1."""
    out = []
    for row in rows:
        entries = xc.affine(row["shadow"], "Native", "all")
        for band in xc.admitted_bands(row, "all"):
            entry = entries.get(band)
            if entry is None:
                continue
            slope = entry.get("slopeALinear")
            if slope is not None and slope != 1.0:
                out.append({"set": row["set"], "bed": row["bed"], "span": row["span"],
                            "scene": row["scene"], "band": band, "a": slope,
                            "c": entry.get("interceptCLinear")})
    return out


def main() -> int:
    print("W32 G0 review closure — the recede on both generations (claims §5.166 §10)")
    print("=" * 160)
    print()
    print(f"Matrix:   {xc.MATRIX}")
    print("Read:     committed evidence only. No capture, no browser, nothing written")
    print("          under a macOS 26.5-keyed path (W32 X1, X2, X5).")
    print()

    frozen = load(FROZEN, "any", with_holdout=False)
    frozen_inactive = inactive(frozen, with_holdout=False)
    documents = sorted({r["document"] for r in frozen})

    print("§1. The frozen bed, and the documents its rows name")
    print("-" * 160)
    print(f"  {len(frozen)} macOS 26.5 rows carry a shadow axis, read at `--at-documents any`")
    print("  because a frozen row names a document this generation does not ship.")
    for document in documents:
        print(f"    {sum(1 for r in frozen if r['document'] == document):>4}  {document}")
    print(f"  Of them, {len(frozen_inactive)} are INACTIVE, on the WebGPU tier, non-holdout,")
    print("  and identify at least one admitted band — the population §5.166 §7's sentence")
    print("  is stated over, on the generation it was not stated over.")
    print()

    print("§2. The census: does Apple's receded window remove light from 3 CSS px outward?")
    print("-" * 160)
    print("  `nat flat` counts the rows whose NATIVE render equals its backdrop, to the axis's")
    print("  six written decimals, in EVERY admitted band. `0-3 nat` is the native departure in")
    print("  the body's own edge band beside it, `σ nat` how many rows resolve a native falloff")
    print("  σ at all, and `win nat` the native window-restricted departure over 3–48 CSS px.")
    print("  The columns are §12c's of `exterior-cut.txt` with the window departure added.")
    print()
    frozen_rows = census(frozen_inactive, "  macOS 26.5, inactive, WebGPU, non-holdout")

    shipped = load(SHIPPED, "shipped", with_holdout=True)
    shipped_nonholdout = inactive(shipped, with_holdout=False)
    shipped_all = inactive(shipped, with_holdout=True)

    print("§3. The same statistic over the two populations, counted")
    print("-" * 160)
    print("  §5.166 §7 wrote '100 of 100'. The population is larger on both counts and the")
    print("  verdict is unchanged on every one of them; the count is the correction.")
    print()
    for label, population in (("macOS 26.5, non-holdout", frozen_inactive),
                              ("macOS 27, non-holdout", shipped_nonholdout),
                              ("macOS 27, holdout admitted", shipped_all)):
        native = sum(1 for r in population if flat(r, "Native"))
        zero = sum(1 for r in population
                   if r["window"]["native"] is not None and r["window"]["native"] == 0)
        sigma = sum(1 for r in population
                    if xc.value(r["shadow"], "falloffSigmaNative") is not None)
        print(f"  {label:<30}  rows {len(population):>4}   native flat {native}/{len(population)}"
              f"   native window departure exactly 0 on {zero}/{len(population)}"
              f"   `falloffSigmaNative` on {sigma}/{len(population)}")
    print()
    print("  Every admitted band whose native `a` is not exactly 1.000000, on either count:")
    odd = {"frozen": odd_slopes(frozen_inactive), "shipped": odd_slopes(shipped_all)}
    for label, entries in odd.items():
        if not entries:
            print(f"    {label}: none")
            continue
        for entry in entries:
            print(f"    {label}: {entry['set']:<10}{entry['bed']:<12}span {entry['span']:>4}"
                  f"  {entry['scene']:<44}{entry['band']:>7}  a = {entry['a']:.6f}"
                  f"  c = {entry['c']}")
    print()

    print("§4. What this makes of §5.166 §7")
    print("-" * 160)
    print("  The recede's native exterior is empty beyond 3 CSS px on the FROZEN bed too, so")
    print("  the finding is not a macOS 27 behaviour and clause 4's zero denominator is not a")
    print("  property of this generation's documents. What lives in `0-3` is a contour hairline")
    print("  on both generations; `recede-cross-section.txt` reads it pixel by pixel.")
    print()

    (HERE / "recede-26.5.json").write_text(json.dumps({
        "source": str(xc.MATRIX),
        "read": "committed evidence only; no capture (W32 X2, X5)",
        "frozenDocuments": documents,
        "frozen": {"rows": len(frozen), "inactiveWebgpuNonHoldout": len(frozen_inactive),
                   "census": frozen_rows},
        "shipped": {"inactiveWebgpuNonHoldout": len(shipped_nonholdout),
                    "inactiveWebgpuWithHoldout": len(shipped_all)},
        "nativeSlopesNotOne": odd,
    }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
