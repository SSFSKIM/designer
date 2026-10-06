#!/usr/bin/env python3.12
"""W48 G0 (a): the READ-ONLY replay of W47's ladder readings from the archive of record (charter
`2026-10-06-w48-dark-operators-fit.md`, X71; Decision Log 2).

    python3.12 -B replay.py <archive root> --out <dir>      (after `pnpm -r build`; from anywhere)

W47's `ladders/read.py` and `ladders/reread.py` run UNCHANGED, imported from W47's committed directory;
their arithmetic is not touched. This file only selects their roots and records what they read:

- **Denial first** (W39 / W42's audit hook, `w42_archive.deny`'s form, widened): before anything of
  W47's is imported, the process refuses any open, listdir or scandir under the raw ladder root
  `~/vitrea-w47/g0-ladders/` and under the live canonical capture tree, and any write, create, rename,
  link or remove under W47's evidence directory. A negative control opens a file under each denied
  root, lists each, and attempts a write into W47's directory; every attempt must raise.
- **Inputs.** The scratch root is the archive's `ladders/` (`read.main(scratch=…)`;
  `ladder.SCRATCH`, which `reread.py` reads directly). `level.identity`'s canonical root, a default
  argument bound to the live tree, is re-bound to the archive's `reference/` subset; its other
  operand is still the ladder's own control capture (`control/merged-captures`), so the identity
  compares two independently produced files. `reread.py` reads `results.json` from the replay's own
  output, not W47's committed copy.
- **Outputs.** `read.main(out=…)` writes `results.json`, `results.txt`, `selections.json` and
  `x60-evidence.json` into the replay's directory; `reread.main`, which writes beside its own source,
  is adapted by redirecting exactly its two output paths (and its one `results.json` input) to the
  replay's directory. Nothing is written into W47's directory (the hook refuses it).
- **X60 by evidence.** `read.main` runs `stage/x60.py evidence` as a subprocess, which an audit hook
  cannot follow, and whose capture-tree scan walks all of `~/vitrea-w47`, the raw root included. The
  replay runs the same `x60.main(["evidence", "--out", …])` in-process, under the hook, with its
  scan's root re-bound to the archive's `ladders/` (the ladder's own capture trees); its other three
  checks are unchanged. Its record's `captureTreesScanned` therefore names the archive's trees; the
  tail `results.json` carries does not print that list.
- **What it read.** Every scratch matrix, every row's capture, alpha PNG and sidecar, the identity's
  two PNGs per control cell and each `Captures.bands()` reading's `webSha256` are recorded in
  `captures.json` by SHA-256.
- **Equality.** `results.json`, `results.txt`, `selections.json`, `reread.json` and `reread.txt`
  must equal W47's committed files byte for byte; `x60-evidence.json` field for field but for the
  scanned trees' paths; the archive's tree must verify against its inventory before and after.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
REPO = EVIDENCE.parents[3]
W47 = EVIDENCE.parent / "2026-10-06-w47-g0-operators"
W47_LADDERS = W47 / "ladders"
RAW_ROOT = Path.home() / "vitrea-w47" / "g0-ladders"
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
OUTPUTS = ("results.json", "results.txt", "selections.json", "reread.json", "reread.txt")

sys.path.insert(0, str(EVIDENCE / "archive"))
import w47_ladders_archive as ARCHIVE  # noqa: E402

# ---------------------------------------------------------------------------------------------
# The denial (installed before any W47 module is imported)
# ---------------------------------------------------------------------------------------------
_READ_DENIED: list[str] = []
_WRITE_DENIED: list[str] = []
_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND


def _under(path, roots) -> bool:
    if not isinstance(path, (str, bytes, os.PathLike)):
        return False
    raw = os.fsdecode(path)
    p = os.path.realpath(raw)
    return any(p == d or p.startswith(d + "/") for d in roots)


def _audit(event, args):
    if event == "open":
        path, mode, flags = args
        if _under(path, _READ_DENIED):
            raise PermissionError(f"denied in the archive-only replay (read): {path}")
        writes = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            isinstance(flags, int) and flags & _WRITE_FLAGS)
        if writes and _under(path, _WRITE_DENIED):
            raise PermissionError(f"denied in the archive-only replay (write into W47's directory): {path}")
    elif event in ("os.listdir", "os.scandir"):
        if args and _under(args[0], _READ_DENIED):
            raise PermissionError(f"denied in the archive-only replay ({event}): {args[0]}")
    elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.truncate", "os.chmod", "os.utime"):
        if args and _under(args[0], _WRITE_DENIED + _READ_DENIED):
            raise PermissionError(f"denied in the archive-only replay ({event}): {args[0]}")
    elif event in ("os.rename", "os.link", "os.symlink"):
        if any(_under(a, _WRITE_DENIED + _READ_DENIED) for a in args[:2]):
            raise PermissionError(f"denied in the archive-only replay ({event}): {args[:2]}")


def install_denial(read_denied, write_denied) -> None:
    _READ_DENIED.extend(os.path.realpath(str(p)) for p in read_denied)
    _WRITE_DENIED.extend(os.path.realpath(str(p)) for p in write_denied)
    sys.addaudithook(_audit)


def negative_control() -> list[dict]:
    """Each denial must fire: an open and a listing under each read-denied root, a write into W47's."""
    probes = []

    def attempt(what, fn):
        try:
            fn()
            probes.append(dict(what=what, refused=False))
        except PermissionError as err:
            probes.append(dict(what=what, refused=True, error=str(err)[:160]))

    attempt(f"open {RAW_ROOT}/control/1x/matrix.json", lambda: open(RAW_ROOT / "control/1x/matrix.json", "rb").close())
    attempt(f"listdir {RAW_ROOT}", lambda: os.listdir(RAW_ROOT))
    first = "apple-macos-27.0-1x-dark-standard-glass0.25"
    attempt(f"open a live canonical sidecar under {CANONICAL}",
            lambda: open(CANONICAL / first / "checkerboard__capsule-button__inactive" / "cell__webgpu.json", "rb").close())
    attempt(f"scandir {CANONICAL}", lambda: list(os.scandir(CANONICAL)))
    probe = W47_LADDERS / ".w48-replay-write-probe"
    attempt(f"write {probe}", lambda: probe.write_text("x"))
    if probe.exists():
        raise SystemExit("the write probe landed in W47's directory")
    return probes


# ---------------------------------------------------------------------------------------------
def sha_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def replay(root: Path, out: Path, also_deny=()) -> dict:
    root, out = Path(root).resolve(), Path(out).resolve()
    if out == W47 or W47 in out.parents:
        raise SystemExit("the replay never writes into W47's directory")
    out.mkdir(parents=True, exist_ok=True)
    before = ARCHIVE.verify_tree(root)
    install_denial([RAW_ROOT, CANONICAL, *also_deny], [W47])
    controls = negative_control()
    for extra in also_deny:
        try:
            os.listdir(extra)
            controls.append(dict(what=f"listdir {extra}", refused=False))
        except PermissionError as err:
            controls.append(dict(what=f"listdir {extra}", refused=True, error=str(err)[:160]))
    if not all(p["refused"] for p in controls):
        raise SystemExit(f"a denial did not fire: {[p for p in controls if not p['refused']]}")

    sys.path.insert(0, str(W47))
    sys.path.insert(0, str(W47_LADDERS))
    import bindings as W  # noqa: PLC0415
    import ladder as LADDER  # noqa: PLC0415
    import read as READ  # noqa: PLC0415
    sys.path.insert(0, str(W47 / "level"))
    import level as LEVEL  # noqa: PLC0415
    if READ.level() is not LEVEL:
        raise SystemExit("read.level() is not the module the replay re-bound")

    ladders = root / "ladders"
    reference = root / "reference"
    LADDER.SCRATCH = ladders
    READ.SCRATCH = ladders

    # level.identity: the canonical root re-bound to the archive's subset; its result kept.
    seen = dict(identity=None, matrices={}, bands={})
    identity = LEVEL.identity

    def identity_from_reference(rows, captures, candidate, ref, canonical=None):
        if canonical is not None:
            raise SystemExit("level.identity was handed a canonical root; the replay binds it")
        got = identity(rows, captures, candidate, ref, canonical=reference)
        seen["identity"] = dict(captures=str(captures), canonical=str(reference), result=got)
        return got

    LEVEL.identity = identity_from_reference

    rows_of = READ.rows_of

    def rows_recorded(label):
        got = rows_of(label)
        for scale in (1, 2):
            path = READ.matrix_path(label, scale)
            seen["matrices"][f"{label}/{scale}x"] = dict(path=str(path.relative_to(root)), sha256=sha_file(path),
                                                         rows=sorted(sid for (p, sid) in got if f"-{scale}x-" in p))
        return got

    READ.rows_of = rows_recorded

    # X60 by evidence, in-process under the hook, its tree scan re-bound to the archive's ladders/.
    x60 = W.load_module("w48_replay_x60", W47 / "stage" / "x60.py")
    scan = x60.capture_trees
    x60.capture_trees = lambda root_=ladders: scan(root_)

    class Shim:
        def run(self, argv, **kw):
            if len(argv) >= 4 and Path(argv[2]) == W47 / "stage" / "x60.py" and argv[3] == "evidence":
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    code = x60.main(argv[3:])
                return types.SimpleNamespace(returncode=code, stdout=buf.getvalue(), stderr="")
            raise SystemExit(f"read.py ran an unexpected subprocess in the replay: {argv}")

    READ.subprocess = Shim()

    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        code_read = READ.main(scratch=ladders, candidates=LADDER.CANDIDATES, out=out)
    if code_read != 0:
        raise SystemExit(f"read.main exited {code_read}: {log.getvalue()[-800:]}")

    # reread.main: its results.json input and its two outputs redirected to the replay's directory.
    import reread as REREAD  # noqa: PLC0415
    if REREAD.READ is not READ:
        raise SystemExit("reread.py imported another read module")
    redirect = {W47_LADDERS / "results.json": out / "results.json",
                W47_LADDERS / "reread.json": out / "reread.json",
                W47_LADDERS / "reread.txt": out / "reread.txt"}
    bands = REREAD.Captures.bands

    def bands_recorded(self, label, scale, sid, row):
        got = bands(self, label, scale, sid, row)
        seen["bands"][f"{label}/{scale}x/{sid}"] = dict(webSha256=got["webSha256"],
                                                        capture=str(self.png(label, scale, sid).relative_to(root)))
        return got

    REREAD.Captures.bands = bands_recorded
    originals = {name: getattr(Path, name) for name in ("read_text", "read_bytes", "write_text")}

    def rebound(name):
        def method(self, *a, **k):
            target = redirect.get(Path(os.path.abspath(self)), self)
            return originals[name](target, *a, **k)
        return method

    try:
        for name in originals:
            setattr(Path, name, rebound(name))
        with contextlib.redirect_stdout(log):
            code_reread = REREAD.main()
    finally:
        for name, fn in originals.items():
            setattr(Path, name, fn)
    if code_reread != 0:
        raise SystemExit(f"reread.main exited {code_reread}")
    (out / "replay-stdout.txt").write_text(log.getvalue())
    after = ARCHIVE.verify_tree(root)

    # Equality with W47's committed readings.
    equality = []
    for name in OUTPUTS:
        a, b = (out / name).read_bytes(), (W47_LADDERS / name).read_bytes()
        equality.append(dict(file=name, committedSha256=hashlib.sha256(b).hexdigest(),
                             replaySha256=hashlib.sha256(a).hexdigest(), bytes=len(b), equal=a == b))
    mine = json.loads((out / "x60-evidence.json").read_text())
    theirs = json.loads((W47_LADDERS / "x60-evidence.json").read_text())
    rest = sorted(set(mine) | set(theirs))
    equality.append(dict(file="x60-evidence.json", equalBut=["captureTreesScanned"],
                         equal=all(mine.get(k) == theirs.get(k) for k in rest if k != "captureTreesScanned"),
                         scannedCommitted=len(theirs.get("captureTreesScanned", [])),
                         scannedReplay=len(mine.get("captureTreesScanned", []))))

    # What it read, by SHA-256: every row's capture, alpha PNG and sidecar, and the identity's PNG pairs.
    rows = {}
    for key, m in sorted(seen["matrices"].items()):
        label, scale = key.split("/")
        tree = ladders / label / scale / "web-captures"
        for sid in m["rows"]:
            prof = f"apple-macos-27.0-{scale}-dark-standard-glass0.25"
            cell = tree / prof / sid
            rows[f"{label}/{scale}/{sid}"] = {name: sha_file(cell / name) for name in (
                f"{sid}__webgpu.png", f"{sid}__webgpu__alpha.png", "cell__webgpu.json")}
    ident = seen["identity"]["result"]
    identity_pngs = {c["cell"]: {k: v for k, v in c.items() if k.startswith("png")} for c in ident["perCell"]}
    captures = dict(schema="w48-replay-captures-1", archiveInventorySha256=before["inventorySha256"],
                    matrices=seen["matrices"], rows=rows, bands=seen["bands"],
                    identity=dict(captures=str(Path(seen["identity"]["captures"]).relative_to(root)),
                                  canonical=str(Path(seen["identity"]["canonical"]).relative_to(root)),
                                  verdict=ident["verdict"], cells=ident["cells"],
                                  identical=ident["pixelAndMeasurementIdentical"], pngs=identity_pngs))
    (out / "captures.json").write_text(json.dumps(captures, indent=1, sort_keys=True) + "\n")
    record = dict(
        schema="w48-replay-1", what="W47's read.py and reread.py replayed read-only from the archive of record",
        archive=dict(root=str(root), before=before, after=after, unchanged=before == after),
        denied=dict(read=[str(RAW_ROOT), str(CANONICAL), *map(str, also_deny)], write=[str(W47)]), negativeControl=controls,
        rebound=dict(scratch="archive ladders/", identityCanonical="archive reference/",
                     identityControlOperand="archive ladders/control/merged-captures",
                     x60Scan="archive ladders/ (in-process, under the hook)",
                     rereadResultsInput="the replay's results.json"),
        tools={str(p.relative_to(REPO)): sha_file(p) for p in (
            W47_LADDERS / "read.py", W47_LADDERS / "reread.py", W47_LADDERS / "ladder.py",
            W47 / "level" / "level.py", W47 / "stage" / "x60.py", W47 / "bindings.py", Path(__file__),
            EVIDENCE / "archive" / "w47_ladders_archive.py")},
        capturesSha256=sha_file(out / "captures.json"),
        counts=dict(matrices=len(seen["matrices"]), rows=len(rows), bands=len(seen["bands"]),
                    identityCells=ident["cells"], identityIdentical=ident["pixelAndMeasurementIdentical"]),
        equality=equality, allEqual=all(e["equal"] for e in equality) and before == after)
    return record


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--also-deny", type=Path, action="append", default=[],
                    help="a further root denied for reading (the producer's output, the second copy)")
    args = ap.parse_args(argv)
    record = replay(args.root, args.out, [p.expanduser().resolve() for p in args.also_deny])
    (Path(args.out) / "replay.json").write_text(json.dumps(record, indent=1) + "\n")
    lines = [f"W48 G0 (a): W47's ladder readings replayed from the archive ({record['archive']['before']['entries']} "
             f"entries, inventory {record['archive']['before']['inventorySha256'][:12]}; tree unchanged: "
             f"{record['archive']['unchanged']})",
             "denials: " + "; ".join(f"{p['what']} -> {'refused' if p['refused'] else 'NOT REFUSED'}"
                                     for p in record["negativeControl"]),
             f"control identity: {record['counts']['identityIdentical']} of {record['counts']['identityCells']} "
             "against the archive's reference subset",
             f"read: {record['counts']['matrices']} matrices, {record['counts']['rows']} rows, "
             f"{record['counts']['bands']} band readings, each by capture SHA-256 (captures.json)"]
    lines += [f"  {e['file']:<20} {'EQUAL' if e['equal'] else 'DIFFERS'}"
              + (f" (byte for byte, sha256 {e['replaySha256'][:12]})" if "replaySha256" in e else
                 f" (field for field but {e['equalBut']}; trees scanned {e['scannedCommitted']} committed, "
                 f"{e['scannedReplay']} replay)") for e in record["equality"]]
    lines.append("REPLAY " + ("REPRODUCES W47's committed readings" if record["allEqual"] else "DOES NOT REPRODUCE"))
    (Path(args.out) / "replay.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if record["allEqual"] else 1


if __name__ == "__main__":
    sys.exit(main())
