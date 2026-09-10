"""W26 G3 — one capture tree against a recorded digest list, byte for byte.

Both halves of the landing's evidence are digest comparisons and this is the only copy of the
comparison. It takes a capture ROOT and a digest FILE (`sha256  path`, paths relative to a
capture root) and reports, over the intersection selected by an optional filter:

    identical / MOVED / missing on one side or the other

A MOVER is never rewritten and never explained away here: it is printed with its two digests and
its pixel delta so the landing can diagnose it (session flake vs real) beside the number.

    g3-identity.py --root <dir> --digests <file> [--only SUBSTR ...] [--exclude SUBSTR ...]
                   [--label TEXT]
"""

import argparse
import hashlib
import os
import sys


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_digests(path):
    out = {}
    for line in open(path):
        line = line.rstrip("\n")
        if not line or line.startswith(("W2", "profile", "  ", "sha256")):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            continue
        out[parts[1].strip()] = parts[0]
    return out


def walk(root):
    out = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            if not name.endswith(".png"):
                continue
            full = os.path.join(base, name)
            out[os.path.relpath(full, root)] = full
    return out


def pixel_delta(a, b):
    """Codes and pixels between two PNGs, or None when Pillow/numpy are absent."""
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        return None
    ia = np.asarray(Image.open(a).convert("RGBA"), dtype=np.int16)
    ib = np.asarray(Image.open(b).convert("RGBA"), dtype=np.int16)
    if ia.shape != ib.shape:
        return ("shape", ia.shape, ib.shape)
    d = np.abs(ia - ib)
    moved = (d.max(axis=2) > 0)
    return (int(d.max()), int(moved.sum()), int(ia.shape[0] * ia.shape[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--digests", required=True)
    ap.add_argument("--canonical-root", default=None, help="for the pixel delta on a mover")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    recorded = read_digests(args.digests)
    landed = walk(args.root)

    def keep(rel):
        if args.only and not any(s in rel for s in args.only):
            return False
        if args.exclude and any(s in rel for s in args.exclude):
            return False
        return True

    landed = {rel: full for rel, full in landed.items() if keep(rel)}
    recorded = {rel: sha for rel, sha in recorded.items() if keep(rel)}

    same, movers, missing_recorded, missing_landed = 0, [], [], []
    for rel in sorted(landed):
        if rel not in recorded:
            missing_recorded.append(rel)
            continue
        got = digest(landed[rel])
        if got == recorded[rel]:
            same += 1
        else:
            movers.append((rel, recorded[rel], got))
    for rel in sorted(recorded):
        if rel not in landed:
            missing_landed.append(rel)

    print(f"=== {args.label or args.root}")
    print(f"root                 {args.root}")
    print(f"digests              {args.digests}")
    if args.only:
        print(f"only                 {' '.join(args.only)}")
    if args.exclude:
        print(f"exclude              {' '.join(args.exclude)}")
    print(f"compared             {same + len(movers)}")
    print(f"IDENTICAL            {same}")
    print(f"MOVED                {len(movers)}")
    print(f"in the tree, not recorded   {len(missing_recorded)}")
    print(f"recorded, not in the tree   {len(missing_landed)}")
    for rel in missing_recorded[:20]:
        print(f"    + {rel}")
    for rel in missing_landed[:20]:
        print(f"    - {rel}")
    for rel, was, now in movers:
        line = f"  MOVED {rel}\n        recorded {was}\n        landed   {now}"
        if args.canonical_root:
            other = os.path.join(args.canonical_root, rel)
            if os.path.exists(other):
                line += f"\n        delta    {pixel_delta(other, landed[rel])}  (max code, pixels, of)"
        print(line)
    return 1 if movers or missing_landed else 0


if __name__ == "__main__":
    sys.exit(main())
