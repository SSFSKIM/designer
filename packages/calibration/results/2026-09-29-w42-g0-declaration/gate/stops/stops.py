#!/usr/bin/env python3
"""W42 G0 gate: run the two directional stops on a candidate capture tree (charter clause 10).

    OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3.12 -B stops.py \\
        --candidate-root DIR [--shipped-root DIR] [--document FILE ...] \\
        [--stop halo|chroma|both] --out RUN.json [--text RUN.txt]
    ... --candidate-root SHIPPED --baseline      # native against shipped, stamped "baseline"

The candidate tree holds `<profile>/<scene>/<scene>__webgpu.png` and `cell__webgpu.json` for the
populations `stops-declaration.json` lists; the shipped tree defaults to the canonical capture
tree. One JSON per run: per cell the statistic on native, shipped and candidate, both distances,
the verdict (pass / FAIL / UNMEASURED) and a summary, stamped with the candidate's admission
(the documents its captures name). Exit 0 when every stop passes, 1 when any cell FAILs or is
UNMEASURED, and a refusal (exit 1 with the reason) when a capture or the declaration is not
admissible.

Since 2026-09-30 (the gate review of b151aff4, finding 10) every document a candidate's captures
name that is not shipped must be declared with --document, and a candidate whose every scheme
names the shipped documents is refused: the shipped render passes the bar by construction.
`--baseline` is the one run that reads the shipped tree against itself, and only with
--candidate-root equal to --shipped-root; it is stamped "baseline", never "candidate".
"""
from __future__ import annotations

import argparse
import datetime
import statistics
import sys
from pathlib import Path

import stops_common as common

STOP_NAMES = {"halo": "stopH", "chroma": "stopP"}


def endpoint(cell: dict) -> str:
    return f"{cell['scheme']} {cell['pose']}"


def headline(stop: dict, names: tuple[str, ...]) -> list[str]:
    """Per endpoint and statistic: native and shipped medians, and the shipped/native range."""
    lines = []
    by_endpoint: dict[str, list[dict]] = {}
    for cell in stop["cells"]:
        by_endpoint.setdefault(endpoint(cell), []).append(cell)
    for name in names:
        for key in ("light active", "light receded", "dark active", "dark receded"):
            cells = by_endpoint.get(key, [])
            pairs = [(c["statistics"][name]["native"], c["statistics"][name]["shipped"],
                      c["statistics"][name]["candidate"]) for c in cells
                     if c["statistics"][name]["native"] is not None]
            if not pairs:
                continue
            nat = [p[0] for p in pairs]
            ship = [p[1] for p in pairs]
            cand = [p[2] for p in pairs if p[2] is not None]
            scale = 1e3 if stop is not None and name in ("F", "M") else 1.0
            fmt = (lambda v: f"{v * scale:6.2f}")
            line = (f"  {name:<8}{key:<15}{len(pairs):>3} cells  native {fmt(min(nat))}.."
                    f"{fmt(max(nat))} (median {fmt(statistics.median(nat))})  shipped "
                    f"{fmt(min(ship))}..{fmt(max(ship))} (median "
                    f"{fmt(statistics.median(ship))})")
            if cand and cand != ship:
                line += (f"  candidate {fmt(min(cand))}..{fmt(max(cand))} (median "
                         f"{fmt(statistics.median(cand))})")
            lines.append(line)
    return lines


def table(stop: dict, names: tuple[str, ...], scale: float, unit: str) -> list[str]:
    head = (f"  {'profile':<44}{'scene':<46}{'stat':<9}{'native':>9}{'shipped':>9}"
            f"{'cand':>9}{'dShip':>8}{'dCand':>8}{'res':>8}  verdict")
    lines = [f"  (values {unit})", head]
    for cell in stop["cells"]:
        for name in names:
            s = cell["statistics"][name]
            val = (lambda v: f"{'-':>9}" if v is None else f"{v * scale:9.3f}")
            dist = (lambda v: f"{'-':>8}" if v is None else f"{v * scale:8.3f}")
            lines.append(f"  {cell['profile']:<44}{cell['scene']:<46}{name:<9}{val(s['native'])}"
                         f"{val(s['shipped'])}{val(s['candidate'])}{dist(s['dShip'])}"
                         f"{dist(s['dCand'])}{dist(s['res'])}  {s['verdict']}")
    return lines


def render_text(run: dict) -> str:
    out = [f"# {run['what']}",
           f"# generated {run['generatedAt']}",
           f"# declaration {run['provenance']['declaration']['path']} "
           f"sha256:{run['provenance']['declaration']['sha256']}",
           f"# shipped root   {run['shippedRoot']}",
           f"# candidate root {run['candidateRoot']}",
           f"# admission: mode {run['admission']['mode']}, candidate names the shipped documents: "
           f"{run['admission']['candidateNamesShippedDocuments']}"]
    for doc in run["admission"]["documents"]:
        out.append(f"#   {doc['kind']}={doc['path']} sha256:{doc['sha256']} "
                   f"({', '.join(doc['schemes'])}; shipped document: {doc['isShippedDocument']})")
    out.append(f"# SUMMARY: {run['summary']['verdict']}  "
               + "  ".join(f"{k} {v['verdict']} {v['counts']}"
                           for k, v in run["summary"]["stops"].items()))
    if "halo" in run["stops"]:
        stop = run["stops"]["halo"]
        out += ["", f"## Stop H, {stop['name']}: {stop['verdict']} {stop['counts']}",
                "## headline per endpoint (codes; floor in absolute codes)"]
        out += headline(stop, ("peak", "annulus", "floor"))
        out += [""] + table(stop, ("peak", "annulus", "floor"), 1.0, "codes")
    if "chroma" in run["stops"]:
        stop = run["stops"]["chroma"]
        out += ["", f"## Stop P, {stop['name']}: {stop['verdict']} {stop['counts']}",
                "## headline per endpoint (OKLab (a, b) x 1e3)"] + headline(stop, ("F", "M"))
        out += [""] + table(stop, ("F", "M"), 1e3, "OKLab (a, b) x 1e3")
        out += ["", "  native channels >= 250 or <= 5 (fraction of deep pixels):"]
        for cell in stop["cells"]:
            if cell["nativeCensoredFraction"] > 0:
                out.append(f"    {cell['profile']:<44}{cell['scene']:<40}"
                           f"{cell['nativeCensoredFraction']:.3f}")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--shipped-root", type=Path, default=common.CANONICAL_CAPTURES)
    parser.add_argument("--document", type=Path, action="append", default=[],
                        help="a scratch document the candidate captures must name by hash")
    parser.add_argument("--stop", choices=("halo", "chroma", "both"), default="both")
    parser.add_argument("--baseline", action="store_true",
                        help="read the shipped tree against itself (native against shipped): "
                             "--candidate-root must be --shipped-root; stamped baseline")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--text", type=Path, default=None)
    args = parser.parse_args(argv)

    trees = common.Trees(args.shipped_root.resolve(), args.candidate_root.resolve(),
                         [p.resolve() for p in args.document], baseline=args.baseline)
    trees.check_roots()
    stops = {}
    if args.stop in ("halo", "both"):
        import halo
        stops["halo"] = halo.read(trees)
    if args.stop in ("chroma", "both"):
        import chroma_band
        stops["chroma"] = chroma_band.read(trees)
    admission = trees.admission()
    verdict = common.combine([s["verdict"] for s in stops.values()])
    run = dict(
        what="W42 G0 directional stops (charter clause 10): no cell farther from Apple than the "
             "shipped render at the statistic's declared resolution",
        generatedAt=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        provenance=common.provenance(),
        shippedRoot=str(trees.shipped_root),
        candidateRoot=str(trees.candidate_root),
        shippedDocuments={scheme: [dict(kind=k, path=p, sha256=h) for k, p, h in named]
                          for scheme, named in sorted(trees.shipped_named.items())},
        admission=admission,
        summary=dict(verdict=verdict,
                     stops={k: dict(verdict=v["verdict"], counts=v["counts"])
                            for k, v in stops.items()}),
        stops=stops,
    )
    args.out.write_text(common.dump_json(run))
    text = render_text(run)
    if args.text:
        args.text.write_text(text)
    print(text.split("\n## ")[0])
    print(f"-> {args.out}" + (f", {args.text}" if args.text else ""))
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
