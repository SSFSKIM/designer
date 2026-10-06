#!/usr/bin/env python3.12
"""W48 G0 (a): W47's ladder evidence as one content-addressed archive of record (charter
`2026-10-06-w48-dark-operators-fit.md`, X71; Decision Log 2): produce, pack, fetch, verify.

W42's `results/2026-09-29-w42-g0-declaration/bed/sitting/w42_archive.py` is the model (its pack,
fetch, member check and tree verification are carried in its form; W42's file is not edited). What
the W48 producer archives is not a native sitting but a scratch render tree, so its sections are:

- `ladders/`: every file of `~/vitrea-w47/g0-ladders/` at its relative path, the capture and alpha
  PNGs, the scratch matrices, the `cell__webgpu.json` sidecars and reports, the control's
  `merged-captures/` (hard links in the raw tree, regular files here) and the rung specs.
- `drive/`: the drive's committed record from W47's `ladders/` (`logs/`, `drive.jsonl`,
  `runs.jsonl`), byte-identical to the committed files.
- `reference/`: the canonical `d0219cd684bf` subset the control's identity check reads, the WebGPU
  capture, alpha PNG and `cell__webgpu.json` sidecar of every control cell (71 per scale, both
  scales), copied from the canonical capture tree and never from the ladder's control. Each sidecar
  must name `d0219cd684bf`'s active and `f0b36a71772a`'s receded document, or nothing is produced.

`inventory.json` lists every file by section with its SHA-256 and size; the tree IS the inventory
(`verify_tree`). The asset is the deterministic PAX tar of the tree (sorted, mtime 0, owner-free)
through `zstd -19 -T1`, named by its own SHA-256; it is written outside the repository.

    python3.12 -B w47_ladders_archive.py produce --out <dir>     (raw root and canonical tree read)
    python3.12 -B w47_ladders_archive.py pack <dir> --out-dir <dir>
    python3.12 -B w47_ladders_archive.py fetch --asset <name> --sha256 <hex> [--source <file>] [--cache <dir>]
    python3.12 -B w47_ladders_archive.py verify-tree <root>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent                                   # results/2026-10-06-w48-g0-declaration
REPO = EVIDENCE.parents[3]
W47 = EVIDENCE.parent / "2026-10-06-w47-g0-operators"
W47_LADDERS = W47 / "ladders"
RAW_ROOT = Path.home() / "vitrea-w47" / "g0-ladders"
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
SCHEMA = "w47-ladders-archive-1"
TAG = "w47-ladders-archive"
PREFIX = "w47-ladders-archive-"
SUFFIX = ".tar.zst"
TOP = "archive"
LIMIT = 2 * 1024 ** 3
GH_REPO = "SSFSKIM/designer"
ZSTD = ["zstd", "-19", "-T1", "-q", "-c"]
CACHE = Path.home() / ".cache" / "vitrea-archives"
SECTIONS = ("ladders", "drive", "reference")
PROFILES = {1: "apple-macos-27.0-1x-dark-standard-glass0.25", 2: "apple-macos-27.0-2x-dark-standard-glass0.25"}
ACTIVE_DOC, RECEDED_DOC = "sha256:d0219cd684bf", "sha256:f0b36a71772a"


def file_sha(path, chunk=1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def refuse_repository(path) -> None:
    resolved = Path(path).resolve()
    if resolved == REPO or REPO in resolved.parents:
        raise ValueError("the archive of record is a release asset; write it outside the repository")


def files_under(root: Path) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            if (Path(dirpath) / name).is_symlink():
                raise ValueError(f"symlink in a source tree: {Path(dirpath) / name}")
        out += [(Path(dirpath) / n).relative_to(root).as_posix() for n in filenames]
    return sorted(out)


def control_cells(raw_root: Path) -> list[tuple[str, str]]:
    """(profile, scene) of every control row, both scales, from the control's own scratch matrices."""
    cells = []
    for scale, profile in PROFILES.items():
        body = json.loads((raw_root / "control" / f"{scale}x" / "matrix.json").read_bytes())
        for row in body["cells"]:
            if row["key"]["profileKey"] != profile or row["key"]["web"]["renderer"] != "webgpu":
                raise ValueError(f"control {scale}x: a row that is not {profile} WebGPU")
            cells.append((profile, row["key"]["sceneId"]))
    if len(set(cells)) != len(cells):
        raise ValueError("control: a cell named twice")
    return sorted(cells)


def reference_files(cells) -> list[tuple[str, Path]]:
    """(archive path under reference/, canonical source) for the subset; each sidecar must name the
    d0219cd684bf / f0b36a71772a pair, or the subset is not the reference."""
    out = []
    for profile, sid in cells:
        cell = CANONICAL / profile / sid
        sidecar = json.loads((cell / "cell__webgpu.json").read_text())
        path = sidecar.get("capturePath", "")
        if ACTIVE_DOC not in path or RECEDED_DOC not in path or sidecar.get("sceneId") != sid:
            raise ValueError(f"canonical {profile} {sid}: the sidecar does not name d0219cd684bf / f0b36a71772a")
        for name in (f"{sid}__webgpu.png", f"{sid}__webgpu__alpha.png", "cell__webgpu.json"):
            if not (cell / name).is_file():
                raise ValueError(f"canonical {profile} {sid}: {name} is absent")
            out.append((f"{profile}/{sid}/{name}", cell / name))
    return out


def produce(out: Path, raw_root: Path = RAW_ROOT) -> dict:
    out = Path(out).resolve()
    refuse_repository(out)
    if out.exists():
        raise ValueError(f"{out} exists; produce writes a fresh tree")
    cells = control_cells(raw_root)
    sources = {"ladders": [(rel, raw_root / rel) for rel in files_under(raw_root)],
               "drive": [(f"logs/{rel}", W47_LADDERS / "logs" / rel) for rel in files_under(W47_LADDERS / "logs")]
               + [(name, W47_LADDERS / name) for name in ("drive.jsonl", "runs.jsonl")],
               "reference": reference_files(cells)}
    inventory = dict(schema=SCHEMA, wave="W48 G0 (a)", what="W47's ladder renders (~/vitrea-w47/g0-ladders), the "
                     "drive's committed logs and the canonical d0219cd684bf reference subset of every control cell",
                     rawRoot=str(raw_root), canonicalTree=str(CANONICAL), controlCells=len(cells))
    out.mkdir(parents=True)
    for section, files in sources.items():
        rows = []
        for rel, src in files:
            dest = out / section / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            digest = file_sha(dest)
            if digest != file_sha(src):
                raise ValueError(f"{section}/{rel}: the copy differs from its source")
            rows.append(dict(path=f"{section}/{rel}", sha256=digest, bytes=dest.stat().st_size))
        inventory[section] = rows
    (out / "inventory.json").write_text(json.dumps(inventory, indent=1) + "\n")
    return dict(inventory=str(out / "inventory.json"), inventorySha256=file_sha(out / "inventory.json"),
                **{s: len(inventory[s]) for s in SECTIONS})


def verify_tree(root) -> dict:
    """Every inventory file present and intact, and nothing else: the tree IS the inventory."""
    root = Path(root)
    inventory = json.loads((root / "inventory.json").read_bytes())
    expected = {"inventory.json"}
    for section in SECTIONS:
        for row in inventory.get(section, []):
            rel = PurePosixPath(row["path"])
            if rel.is_absolute() or ".." in rel.parts or rel.parts[0] != section:
                raise ValueError("inventory path escapes its section: " + row["path"])
            path = root / rel
            if path.is_symlink() or not path.is_file():
                raise ValueError("inventory entry missing: " + row["path"])
            if path.stat().st_size != row["bytes"] or file_sha(path) != row["sha256"]:
                raise ValueError("inventory entry altered: " + row["path"])
            expected.add(str(rel))
    present = set(files_under(root))
    if present != expected:
        raise ValueError("archive tree differs from its inventory: unlisted %s, missing %s" % (
            sorted(present - expected)[:5], sorted(expected - present)[:5]))
    return dict(entries=sum(len(inventory.get(s, [])) for s in SECTIONS),
                perSection={s: len(inventory.get(s, [])) for s in SECTIONS},
                inventorySha256=file_sha(root / "inventory.json"))


def asset_name(digest: str) -> str:
    return PREFIX + digest + SUFFIX


def check_digest(digest: str) -> None:
    if not (isinstance(digest, str) and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)):
        raise ValueError("an archive is named by a full lowercase SHA-256 (64 hex digits)")


def tar_bytes_to(root, stream) -> int:
    root = Path(root)
    files = files_under(root)
    dirs = sorted({str(d) for f in files for d in PurePosixPath(f).parents if str(d) != "."})
    with tarfile.open(fileobj=stream, mode="w|", format=tarfile.PAX_FORMAT) as tar:
        def info(name, kind, size=0):
            t = tarfile.TarInfo(name)
            t.type, t.size, t.mtime, t.uid, t.gid, t.uname, t.gname = kind, size, 0, 0, 0, "", ""
            t.mode = 0o755 if kind == tarfile.DIRTYPE else 0o644
            return t
        tar.addfile(info(TOP, tarfile.DIRTYPE))
        for d in dirs:
            tar.addfile(info(f"{TOP}/{d}", tarfile.DIRTYPE))
        for f in files:
            with open(root / f, "rb") as handle:
                tar.addfile(info(f"{TOP}/{f}", tarfile.REGTYPE, (root / f).stat().st_size), handle)
    return len(files)


def pack(archive, out_dir, limit=LIMIT) -> dict:
    archive, out_dir = Path(archive).resolve(), Path(out_dir).resolve()
    refuse_repository(out_dir)
    tree = verify_tree(archive)
    out_dir.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".packing-", dir=out_dir)
    os.close(fd)
    tmp = Path(tmp)
    try:
        with open(tmp, "wb") as sink:
            zstd = subprocess.Popen(ZSTD, stdin=subprocess.PIPE, stdout=sink)
            try:
                members = tar_bytes_to(archive, zstd.stdin)
            finally:
                zstd.stdin.close()
            if zstd.wait() != 0:
                raise RuntimeError("zstd failed")
        size = tmp.stat().st_size
        if size >= limit:
            raise ValueError("asset is %d bytes; a release asset must be under %d" % (size, limit))
        digest = file_sha(tmp)
        final = out_dir / asset_name(digest)
        os.replace(tmp, final)
    finally:
        if tmp.exists():
            tmp.unlink()
    version = subprocess.run(["zstd", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    return dict(asset=asset_name(digest), path=str(final), sha256=digest, bytes=size, tarMembers=members,
                zstd=version, compression=" ".join(ZSTD[1:]), **tree)


def gh_download(tag, asset, repo, directory) -> Path:
    subprocess.run(["gh", "release", "download", tag, "--repo", repo, "--pattern", asset,
                    "--dir", str(directory)], check=True)
    return Path(directory) / asset


def safe_members(tar):
    seen = set()
    for member in tar:
        name = PurePosixPath(member.name)
        if name.is_absolute() or ".." in name.parts or not name.parts or name.parts[0] != TOP:
            raise ValueError("unsafe archive member path: " + member.name)
        if not (member.isreg() or member.isdir()):
            raise ValueError("archive member is not a regular file or directory: " + member.name)
        if str(name) in seen:
            raise ValueError("duplicate archive member: " + member.name)
        seen.add(str(name))
        yield member


def extract(tarball, destination) -> Path:
    destination = Path(destination)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".tar") as plain:
        subprocess.run(["zstd", "-d", "-q", "-c", str(tarball)], stdout=plain, check=True)
        plain.flush()
        with tarfile.open(plain.name, mode="r:") as tar:
            members = list(safe_members(tar))
            destination.mkdir()
            tar.extractall(destination, members=members, filter="data")
    return destination / TOP


def fetch(tag, asset, digest, repo=GH_REPO, cache=CACHE, download=gh_download, source=None) -> Path:
    """Fetch by the recorded name, verify the full digest BEFORE decompression, extract through a member
    check, re-check the tree against its inventory; a cache is re-checked every call."""
    check_digest(digest)
    if asset != asset_name(digest):
        raise ValueError("asset name does not carry the expected digest: " + asset)
    cache = Path(cache).expanduser().resolve()
    refuse_repository(cache)
    home = cache / digest
    root = home / "extracted" / TOP
    marker = home / "verified.json"
    if root.is_dir() and marker.is_file() and json.loads(marker.read_text()).get("sha256") == digest:
        verify_tree(root)
        return root
    home.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=home, prefix=".download-") as scratch:
        if source is not None:
            fetched = Path(scratch) / asset
            shutil.copyfile(source, fetched)
        else:
            fetched = Path(download(tag, asset, repo, scratch))
        actual = file_sha(fetched)
        if actual != digest:
            raise ValueError("digest mismatch: expected %s, fetched %s; nothing extracted" % (digest, actual))
        partial = Path(scratch) / "extracted"
        extract(fetched, partial)
        tree = verify_tree(partial / TOP)
        if (home / "extracted").exists():
            shutil.rmtree(home / "extracted")
        os.replace(partial, home / "extracted")
        os.replace(fetched, home / asset)
    marker.write_text(json.dumps(dict(sha256=digest, asset=asset, tag=tag, repo=repo,
                                      bytes=(home / asset).stat().st_size, source=str(source) if source else None,
                                      **tree), indent=2) + "\n")
    return root


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="action", required=True)
    p = sub.add_parser("produce")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--raw-root", type=Path, default=RAW_ROOT)
    k = sub.add_parser("pack")
    k.add_argument("archive", type=Path)
    k.add_argument("--out-dir", type=Path, required=True)
    v = sub.add_parser("verify-tree")
    v.add_argument("archive", type=Path)
    f = sub.add_parser("fetch")
    f.add_argument("--tag", default=TAG)
    f.add_argument("--asset", required=True)
    f.add_argument("--sha256", required=True)
    f.add_argument("--repo", default=GH_REPO)
    f.add_argument("--cache", type=Path, default=CACHE)
    f.add_argument("--source", type=Path, help="a local owner-controlled copy, verified the same way")
    args = ap.parse_args(argv)
    if args.action == "produce":
        print(json.dumps(produce(args.out, args.raw_root), indent=2))
    elif args.action == "pack":
        print(json.dumps(pack(args.archive, args.out_dir), indent=2))
    elif args.action == "verify-tree":
        print(json.dumps(verify_tree(args.archive), indent=2))
    else:
        print(fetch(args.tag, args.asset, args.sha256, args.repo, args.cache, source=args.source))
    return 0


if __name__ == "__main__":
    sys.exit(main())
