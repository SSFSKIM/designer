"""W48 G0 (b): the two TypeScript tools whose bindings are compiled-in constants, copied from W47 with
ONLY those constants changed (charter clause 2). `build-candidate.ts` and `seal.ts` cannot be re-bound
by path: a `tsx` module has no `bindings` to install, and each hard-codes its wave's charter, G1
directory, snapshot directory, refusal pattern and the wave named in what it writes. This file is the
one statement of the change: `HEADER[name]` is prepended and `EDITS[name]` (each an exact W47 line and
its W48 replacement, applied once) is the whole diff. `generate` writes the copies; `test_ts_copies.py`
regenerates them and requires the committed bytes, so a hand edit of a copy beyond these lines fails.

The env var `W47_CANDIDATE_ROOT` keeps its name on purpose: W47's `fit/fit.py`, inherited by path
unchanged (`bindings.INHERITED`), sets it when it calls `bindings.BUILDER`, which is the W48 copy.

    python3.12 -B tools/ts_copies.py generate
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parent
W47 = G0.parent / "2026-10-06-w47-g0-operators"
_W = r"/(^|\/)2026-10-0[35]-w4[456]-[^/]*(\/|$)/.test({v}) || /(^|\/)vitrea-w4[456](\/|$)/.test({v})"
_W48 = r"/(^|\/)2026-10-0[356]-w4[4567]-[^/]*(\/|$)/.test({v}) || /(^|\/)vitrea-w4[4567](\/|$)/.test({v})"

FILES = {"build-candidate.ts": ("fit/build-candidate.ts", "fit/build-candidate.ts"),
         "seal.ts": ("seal/seal.ts", "seal/seal.ts")}

HEADER = {
    "build-candidate.ts": (
        "/**\n"
        " * W48 G0 (b): W47's builder (`results/2026-10-06-w47-g0-operators/fit/build-candidate.ts`), COPIED with only\n"
        " * its compiled-in bindings changed (charter `2026-10-06-w48-dark-operators-fit.md` clause 2): the snapshot\n"
        " * directory is W48's `documents/` (taken at 78d0211e0, byte-identical to W47's), the label grammar is W47's\n"
        " * `fit/labels.json` read by path (inherited), the refusal covers W47's evidence and `~/vitrea-w47` too, and\n"
        " * the wave a candidate names is W48. The env var stays `W47_CANDIDATE_ROOT`: W47's `fit/fit.py`, inherited\n"
        " * by path unchanged, sets it. The whole diff is `tools/ts_copies.py`; `tools/test_ts_copies.py` holds it.\n"
        " *\n"
        " *   W47_CANDIDATE_ROOT=<dir> pnpm exec tsx results/2026-10-06-w48-g0-declaration/fit/build-candidate.ts <spec.json>\n"
        " */\n"),
    "seal.ts": (
        "/**\n"
        " * W48 G0 (b): W47's seal (`results/2026-10-06-w47-g0-operators/seal/seal.ts`), COPIED with only its\n"
        " * compiled-in bindings changed (charter `2026-10-06-w48-dark-operators-fit.md` clause 2): G1 is\n"
        " * `results/2026-10-06-w48-g1-refit`, the charter W48's, the snapshots W48's `documents/`, the refusal\n"
        " * covers W47's evidence and `~/vitrea-w47` too, and the record names W48 G1 (claims §5.213). The whole\n"
        " * diff is `tools/ts_copies.py`; `tools/test_ts_copies.py` holds it.\n"
        " *\n"
        " *   pnpm exec tsx results/2026-10-06-w48-g0-declaration/seal/seal.ts <label> <method.json> \\\n"
        " *     [--candidates DIR] [--profiles DIR] [--manifest FILE]\n"
        " */\n"),
}

EDITS = {
    "build-candidate.ts": [
        ('const LABELS = JSON.parse(readFileSync(join(HERE, "labels.json"), "utf8")) as { pattern: string };',
         'const LABELS = JSON.parse(readFileSync(join(EVIDENCE, "..", "2026-10-06-w47-g0-operators", "fit", "labels.json"),\n'
         '  "utf8")) as { pattern: string };'),
        ("if (" + _W.format(v="OUT_ROOT") + ") {", "if (" + _W48.format(v="OUT_ROOT") + ") {"),
        ("  throw new Error(`${OUT_ROOT} is W44's, W45's or W46's evidence or scratch; W47 builds into its own (clause 2)`);",
         "  throw new Error(`${OUT_ROOT} is W44's, W45's, W46's or W47's evidence or scratch; W48 builds into its own (clause 2)`);"),
        ("    throw new Error(`${slot}: '${path}': the light material never moves in W47 (X60)`);",
         "    throw new Error(`${slot}: '${path}': the light material never moves in W48 (X60)`);"),
        ("    throw new Error(`${slot}: the light material never moves in W47 (X60)`);",
         "    throw new Error(`${slot}: the light material never moves in W48 (X60)`);"),
        ("  const snapshotRel = `packages/calibration/results/2026-10-06-w47-g0-operators/documents/${source.sha256.slice(0, 12)}.json`;",
         "  const snapshotRel = `packages/calibration/results/2026-10-06-w48-g0-declaration/documents/${source.sha256.slice(0, 12)}.json`;"),
        ("      `SCRATCH CANDIDATE ${spec.label}, W47 candidate (charter clauses 5-6). Not a sealed or`,",
         "      `SCRATCH CANDIDATE ${spec.label}, W48 candidate (charter clauses 6-8). Not a sealed or`,"),
        ("    recordedBy: `W47, scratch candidate ${spec.label}`,",
         "    recordedBy: `W48, scratch candidate ${spec.label}`,"),
        ('  "$comment": `W47 scratch candidate ${spec.label}: ${spec.note ?? ""}`.trim(),',
         '  "$comment": `W48 scratch candidate ${spec.label}: ${spec.note ?? ""}`.trim(),'),
        ("  name: `apple-macos-27.0-glass0.25-w47-${spec.label}`,",
         "  name: `apple-macos-27.0-glass0.25-w48-${spec.label}`,"),
    ],
    "seal.ts": [
        ('const G1 = join(PACKAGE, "results", "2026-10-06-w47-g1-refit");',
         'const G1 = join(PACKAGE, "results", "2026-10-06-w48-g1-refit");'),
        ('const CHARTER = "docs/doperpowers/specs/2026-10-06-w47-span-graded-dark-transmission.md";',
         'const CHARTER = "docs/doperpowers/specs/2026-10-06-w48-dark-operators-fit.md";'),
        ("  if (" + _W.format(v="full") + ") {", "  if (" + _W48.format(v="full") + ") {"),
        ("    throw new Error(`${what}: ${full} is W44's, W45's or W46's evidence or scratch; W47 seals its own (clause 2)`);",
         "    throw new Error(`${what}: ${full} is W44's, W45's, W46's or W47's evidence or scratch; W48 seals its own (clause 2)`);"),
        ('      "W47 G1, claims §5.212: the span-graded dark transmission and the receded fine term over",',
         '      "W48 G1, claims §5.213: the span-graded dark transmission and the receded fine term over",'),
        ('      "`supersedes`; `entries` keeps the snapshot\'s record for every leaf W47 left where it was and",',
         '      "`supersedes`; `entries` keeps the snapshot\'s record for every leaf W48 left where it was and",'),
        ('      "records each leaf W47 moved with its previous and 0.5 values. By X64 and X67 it may name",',
         '      "records each leaf W48 moved with its previous and 0.5 values. By X64 and X67 it may name",'),
        ('    recordedBy: "W47 G1",', '    recordedBy: "W48 G1",'),
        ("      gate: `W47 G1, claims §5.212; charter ${CHARTER} clauses 6-8; Decision Logs 1-7`,",
         "      gate: `W48 G1, claims §5.213; charter ${CHARTER} clauses 6-8; Decision Logs 1-7`,"),
        ('        "search procedure, tie rule and selection rule, from d0219cd684bf (results/2026-10-06-w47-g1-refit/fit/path/)",',
         '        "search procedure, tie rule and selection rule, from d0219cd684bf (results/2026-10-06-w48-g1-refit/fit/path/)",'),
        ("  what: `W47 G1: candidate ${label} sealed as the two dark -glass0.25 documents; the light two untouched (X60)`,",
         "  what: `W48 G1: candidate ${label} sealed as the two dark -glass0.25 documents; the light two untouched (X60)`,"),
    ],
}


def render(name: str) -> str:
    """The W48 copy's bytes: HEADER + W47's file with each EDITS line replaced exactly once."""
    w47_rel, _ = FILES[name]
    text = (W47 / w47_rel).read_text()
    for old, new in EDITS[name]:
        if text.count(old) != 1:
            raise SystemExit(f"{name}: the W47 line is not present exactly once: {old[:90]}")
        text = text.replace(old, new)
    return HEADER[name] + text


def generate() -> None:
    for name, (_, w48_rel) in FILES.items():
        (G0 / w48_rel).write_text(render(name))
        print(f"wrote {w48_rel}")


if __name__ == "__main__":
    if sys.argv[1:] != ["generate"]:
        print(__doc__)
        sys.exit(64)
    generate()
