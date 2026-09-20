#!/usr/bin/env python3
"""The append-check — W30 G1, contract X7; run before and after every generation split.

The split moves rows between files and must not change one. This proves it, and the
proof is a RECONSTRUCTION rather than a tally: the working file and every superseded
file are read back, their rows are put back in the order the before-manifest recorded,
the original file's bytes are recomposed, and the recomposition's SHA-256 is compared
to the digest the manifest took before a byte moved. A reconstruction that hashes to
the recorded digest cannot have lost a row, changed a row, or reordered one; the
per-clause assertions below say WHICH property failed when it does.

The clauses, each reported on its own line:

  rows accounted for   every row of the before-manifest appears exactly once, in the
                       file its `destination` names
  rows byte-identical  each row's canonical JSON (sorted keys, no whitespace — the
                       construction `freeze.py` hashes a row by) is the recorded digest
  26.5 untouched       the working file ON DISK holds, in its own order, exactly the
                       macOS 26.5 rows the manifest recorded, at their recorded bytes,
                       and no superseded file on disk holds one
  order preserved      the digests each file ON DISK carries, in file order, are the
                       digests the manifest sends it, in the before order
  counts add up        per profile key, retained + moved == before
  reconstruction       the recomposed original hashes to the recorded digest

**Four of the six clauses read the files, not the plan** (W30 G1 review closure,
2026-09-20). A clause computed from the manifest alone proves that the split *intended*
the right thing; the question is whether the tree *holds* it, and the two clauses that
name the invariants most worth holding — the frozen bed and the order the freeze reads
positionally — now take the rows off disk and compare them to the recorded digests.

    python3 append-check.py [--manifest before-manifest.json] [--json out.json]
"""
import hashlib
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
PACKAGE = ROOT / "packages/calibration"

# The split's own reader, so the two scripts cannot disagree about what a row is.
_spec = importlib.util.spec_from_file_location("split_generation", HERE / "split-generation.py")
_split = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_split)
canon, elements = _split.canon, _split.elements


def slices_of(path: pathlib.Path):
    raw = path.read_bytes()
    _, spans, end = elements(raw)
    prefix = raw[: spans[0][0]] if spans else None
    suffix = raw[spans[-1][1]:] if spans else None
    seps = {raw[spans[i][1]: spans[i + 1][0]] for i in range(len(spans) - 1)}
    return raw, [raw[a:b] for a, b in spans], prefix, (seps.pop() if seps else None), suffix


def main() -> int:
    argv = sys.argv[1:]
    manifest_path = HERE / "before-manifest.json"
    out_path = None
    for i, a in enumerate(argv):
        if a == "--manifest":
            manifest_path = pathlib.Path(argv[i + 1]).resolve()
        if a == "--json":
            out_path = pathlib.Path(argv[i + 1]).resolve()
    manifest = json.loads(manifest_path.read_text())
    before = manifest["rows"]

    # Read every file the manifest sends a row to, once.
    wanted = sorted({r["destination"] for r in before})
    files = {}
    for rel in wanted:
        path = PACKAGE / rel
        raw, rows, prefix, sep, suffix = slices_of(path)
        files[rel] = {
            "path": path, "raw": raw, "rows": rows,
            "prefix": prefix, "sep": sep, "suffix": suffix,
        }

    failures = []
    report = {"manifest": str(manifest_path.relative_to(ROOT)), "clauses": {}, "files": {}}

    # Each file's rows as they stand on disk: the profile key the row itself carries and
    # its canonical digest, in the file's own order. Every clause below that says
    # something about the tree reads this rather than the manifest.
    for rel, holder in files.items():
        holder["onDisk"] = [
            (parsed["key"]["profileKey"], hashlib.sha256(canon(parsed)).hexdigest())
            for parsed in (json.loads(blob) for blob in holder["rows"])
        ]

    # --- rows accounted for, and byte-identical -----------------------------------
    placed = [None] * len(before)
    for rel, holder in files.items():
        expect = [r for r in before if r["destination"] == rel]
        if len(expect) != len(holder["rows"]):
            failures.append(
                f"{rel}: holds {len(holder['rows'])} rows, manifest sends it {len(expect)}")
            continue
        for r, blob in zip(expect, holder["rows"]):
            digest = hashlib.sha256(canon(json.loads(blob))).hexdigest()
            if digest != r["rowSha256"]:
                failures.append(
                    f"{rel}: row {r['index']} ({r['profileKey']} / {r['sceneId']} / {r['tier']}) "
                    f"hashes {digest[:12]}, recorded {r['rowSha256'][:12]}")
            placed[r["index"]] = blob
    missing = [i for i, b in enumerate(placed) if b is None]
    report["clauses"]["rows accounted for"] = not missing and not failures
    report["clauses"]["rows byte-identical"] = not failures
    if missing:
        failures.append(f"{len(missing)} rows of the before-manifest were not found")

    # --- 26.5 untouched -------------------------------------------------------------
    # Read off the files. The manifest says which rows the split meant to leave alone;
    # this asks the working file what it actually holds, and the superseded files
    # whether they hold a frozen row they should never have been given.
    FROZEN = "apple-macos-26.5-"
    frozen = [r for r in before if r["profileKey"].startswith(FROZEN)]
    frozen_recorded = [r["rowSha256"] for r in frozen]
    frozen_on_disk = [
        digest for key, digest in files["results/matrix.json"]["onDisk"] if key.startswith(FROZEN)
    ]
    stowed = {
        rel: sum(1 for key, _ in holder["onDisk"] if key.startswith(FROZEN))
        for rel, holder in files.items() if rel != "results/matrix.json"
    }
    misplaced = {rel: n for rel, n in stowed.items() if n}
    ok_frozen = frozen_on_disk == frozen_recorded and not misplaced
    report["clauses"]["26.5 untouched"] = ok_frozen
    report["frozenRowCount"] = len(frozen)
    report["frozenRowsOnDisk"] = len(frozen_on_disk)
    if misplaced:
        failures.append(f"macOS 26.5 rows are in a superseded file: {misplaced}")
    if frozen_on_disk != frozen_recorded:
        failures.append(
            f"the working file holds {len(frozen_on_disk)} macOS 26.5 rows against the "
            f"manifest's {len(frozen_recorded)}, or holds them in a different order or at "
            f"different bytes")

    # --- order preserved ------------------------------------------------------------
    # Also off the files: the digest sequence each one carries against the digest
    # sequence the manifest sends it, which is content and order in one comparison.
    ok_order = True
    for rel in wanted:
        want = [r["rowSha256"] for r in before if r["destination"] == rel]
        got = [digest for _, digest in files[rel]["onDisk"]]
        if got != want:
            ok_order = False
            first = next((i for i, (a, b) in enumerate(zip(got, want)) if a != b),
                         min(len(got), len(want)))
            failures.append(
                f"{rel}: the rows on disk are not the manifest's rows in the before order "
                f"(first difference at position {first})")
    report["clauses"]["order preserved"] = ok_order

    # --- counts add up --------------------------------------------------------------
    counts = {}
    for r in before:
        entry = counts.setdefault(r["profileKey"], {"before": 0})
        entry["before"] += 1
        entry[r["destination"]] = entry.get(r["destination"], 0) + 1
    ok_counts = all(
        v["before"] == sum(n for k, n in v.items() if k != "before") for v in counts.values())
    report["clauses"]["counts add up"] = ok_counts
    report["rowsByProfileKey"] = dict(sorted(counts.items()))
    if not ok_counts:
        failures.append("the per-profile row counts do not add up")

    # --- reconstruction ---------------------------------------------------------------
    ok_recon = False
    recomposed = None
    if not missing:
        shape = files["results/matrix.json"]
        recomposed = shape["prefix"] + shape["sep"].join(placed) + shape["suffix"]
        digest = hashlib.sha256(recomposed).hexdigest()
        ok_recon = digest == manifest["matrixSha256"]
        report["reconstruction"] = {
            "sha256": digest,
            "recorded": manifest["matrixSha256"],
            "bytes": len(recomposed),
            "recordedBytes": manifest["matrixBytes"],
        }
        if not ok_recon:
            failures.append(
                f"the recomposed original hashes {digest[:12]}, recorded {manifest['matrixSha256'][:12]}")
    report["clauses"]["reconstruction"] = ok_recon

    for rel, holder in files.items():
        report["files"][rel] = {
            "rows": len(holder["rows"]),
            "bytes": len(holder["raw"]),
            "sha256": hashlib.sha256(holder["raw"]).hexdigest(),
        }

    width = max(len(c) for c in report["clauses"])
    for clause, ok in report["clauses"].items():
        print(f"{clause.ljust(width)}  {'PASS' if ok else 'FAIL'}")
    print()
    # Named in the output, because `--manifest` defaults to this directory's own
    # witness: a later split's operator who forgets the flag would otherwise read a
    # PASS for the split that already happened and take it for their own.
    print(f"manifest: {manifest_path.relative_to(ROOT)}")
    print(f"before: {manifest['rowCount']} rows, {manifest['matrixBytes']} bytes, "
          f"sha256 {manifest['matrixSha256']}")
    for rel in wanted:
        f = report["files"][rel]
        print(f"after:  {f['rows']:5d} rows, {f['bytes']:9d} bytes, sha256 {f['sha256']}  {rel}")
    print()
    print(f"{'profile key'.ljust(58)} {'before':>7} {'working':>8} {'moved':>7}")
    for pk, v in report["rowsByProfileKey"].items():
        moved = sum(n for k, n in v.items() if k not in ("before", "results/matrix.json"))
        print(f"{pk.ljust(58)} {v['before']:>7} {v.get('results/matrix.json', 0):>8} {moved:>7}")
    for line in failures:
        print("FAILURE:", line)
    report["failures"] = failures
    if out_path is not None:
        out_path.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if not failures and all(report["clauses"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
