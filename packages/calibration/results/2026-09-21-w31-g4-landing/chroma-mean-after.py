#!/usr/bin/env python3
"""W31 G4 review closure — the MEAN chroma statistic's after-values (claims §5.165 §9, finding R5).

    python3 chroma-mean-after.py            # writes chroma-mean-after.txt

The READMEs and the CHANGELOG state what 0.21.0 fixed in the MEAN statistic —
"about half of them in the light material and a tenth in the dark one", against a
reference that keeps 0.71–0.83 and 0.90–0.97 of its own. Those are ratio (ii),
`interiorChromaMeanWeb / interiorChromaMeanBackdrop`, the raw per-pixel chroma
mean over the backdrop's (charter, the instrument). The wave then FITTED a
different statistic — `R`, the chroma-to-structure spread ratio — because the
spread is what the eye reads and because the blur cancels in it. So every
published "before" is in a statistic no published "after" is given in, and a
reader has no way to close the sentence.

This reads the after-values off the committed `results/matrix.json` on exactly
the bed `chroma-cut.py` declares — the untinted `photo` cells of the four macOS 27
standard profiles at both scales, `calibration` + `validation`, WebGPU tier, at
the shipped document bytes, the two poses separated — and prints them per bed
beside the reference's own. It re-uses `chroma-cut.py`'s selection by importing
it, rather than restating it, so the two cannot drift.

Nothing here is a bound and nothing here gates: the adopted rows are M1 and M2
and they are stated over `R`. This is the record's missing column.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent

_spec = importlib.util.spec_from_file_location("chroma_cut", HERE / "chroma-cut.py")
assert _spec is not None and _spec.loader is not None
chroma_cut = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chroma_cut)


def value(cell: dict, field: str) -> float | None:
    entry = (cell.get("material") or {}).get(field)
    return entry["value"] if isinstance(entry, dict) else None


def main() -> int:
    shipped = chroma_cut.shipped_document_hashes()
    matrix = json.loads((PACKAGE / "results" / "matrix.json").read_text())
    if matrix.get("schemaVersion") != 5:
        raise SystemExit(f"chroma-mean-after: matrix schema {matrix.get('schemaVersion')}")

    # The bed, by `chroma-cut.py`'s own predicate and not by a restatement of it.
    bed = chroma_cut.bed_rows(matrix["cells"], shipped)
    by_key = {
        (cell["key"]["profileKey"], cell["key"]["sceneId"]): cell
        for cell in matrix["cells"]
        if (cell["key"]["profileKey"], cell["key"]["sceneId"]) in bed
        and cell["key"]["web"]["renderer"] == "webgpu"
        and cell.get("fixtureSet") in ("calibration", "validation")
        and chroma_cut.at_a_shipped_document(cell, shipped)
    }

    rows = []
    for key, row in sorted(bed.items()):
        cell = by_key[key]
        backdrop = value(cell, "interiorChromaMeanBackdrop")
        web = value(cell, "interiorChromaMeanWeb")
        native = value(cell, "interiorChromaMeanNative")
        if backdrop is None or web is None or native is None:
            raise SystemExit(f"chroma-mean-after: {key} carries no mean chroma field")
        rows.append(
            {
                **row,
                "webOverBackdrop": web / backdrop,
                "nativeOverBackdrop": native / backdrop,
            }
        )

    shipped_27 = {
        name: digest
        for name, digest in chroma_cut.shipped_document_hashes().items()
        if "macos-27.0" in name
    }
    report = [
        "W31 G4 review closure — ratio (ii), the MEAN chroma statistic, AFTER the fit",
        "(claims §5.165 §9, finding R5).",
        "",
        "ratio (ii) = interiorChromaMean{Web,Native} / interiorChromaMeanBackdrop, read off",
        "the committed results/matrix.json on chroma-cut.py's own declared bed.",
        "",
        f"shipped macOS 27 documents: {json.dumps(shipped_27, sort_keys=True)}",
        "",
        "The BEFORE column is not computable here and is not recomputed: the pre-fit",
        "generation predates this instrument, so those rows carry no chroma field at all",
        "(claims §5.164 §4, N15). It is quoted from claims §5.161 §3 as its own review",
        "closure corrects it (finding N4's declared-bed table), which is the same bed.",
        "The NATIVE column is the cross-check that it is: the reference does not move",
        "with the fit, so this run's native ranges must reproduce §5.161 §3's exactly.",
        "",
        "bed                n   web BEFORE       web AFTER     |   native (this run)   native (§5.161 §3)",
    ]
    # claims §5.161 §3, the review closure's N4 table: the declared bed, web / native.
    BEFORE = {
        "light|active": ((0.2385, 0.3121), (0.7180, 0.8329)),
        "light|inactive": ((0.2526, 0.3304), (0.7089, 0.8164)),
        "dark|active": ((0.1059, 0.1137), (0.9173, 0.9732)),
        "dark|inactive": ((0.1144, 0.1227), (0.9030, 0.9060)),
    }
    beds: dict[str, list[dict]] = {}
    for row in rows:
        beds.setdefault(f"{row['scheme']}|{row['pose']}", []).append(row)
    agrees = True
    for bed_key in ("light|active", "light|inactive", "dark|active", "dark|inactive"):
        group = beds[bed_key]
        web = [row["webOverBackdrop"] for row in group]
        nat = [row["nativeOverBackdrop"] for row in group]
        before_web, before_native = BEFORE[bed_key]
        same = (
            abs(min(nat) - before_native[0]) < 5e-5 and abs(max(nat) - before_native[1]) < 5e-5
        )
        agrees = agrees and same
        report.append(
            f"{bed_key:<16} {len(group):>2}   {before_web[0]:.4f}-{before_web[1]:.4f}   "
            f"{min(web):.4f}-{max(web):.4f}   |   {min(nat):.4f}-{max(nat):.4f}   "
            f"{before_native[0]:.4f}-{before_native[1]:.4f}  {'agrees' if same else 'MOVED'}"
        )
    report += [
        "",
        f"the native cross-check: {'all four beds agree to <5e-5' if agrees else 'A BED MOVED'}",
    ]

    report += [
        "",
        "per cell:",
        "",
        f"{'profile':<52}{'scene':<34}{'web (ii)':>10}{'native (ii)':>13}",
    ]
    for row in sorted(rows, key=lambda r: (r["scheme"], r["pose"], -r["webOverBackdrop"])):
        report.append(
            f"{row['profile']:<52}{row['scene']:<34}"
            f"{row['webOverBackdrop']:>10.4f}{row['nativeOverBackdrop']:>13.4f}"
        )

    text = "\n".join(report) + "\n"
    (HERE / "chroma-mean-after.txt").write_text(text)
    print(text)
    return 0 if agrees else 1


if __name__ == "__main__":
    raise SystemExit(main())
