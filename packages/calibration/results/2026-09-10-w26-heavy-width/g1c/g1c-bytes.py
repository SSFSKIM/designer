"""W26 G1c — is a rung byte-identical to the canonical 0.14.0 captures, per row?

WHY THIS IS THE FIRST THING RUN. The control rung names `sizeHeavyTapSigma` = 13.418 at dpr 1,
which W26 Decision Log 3 (c) measured as the width the clamped chain tap already draws there. If
that is true, every 1x row of the control rung must come out of the renderer BIT FOR BIT the same
as the canonical 0.14.0 capture — and if it does not, the ladder below it is being read against a
material that already moved. The check costs nothing and it is the difference between a control and
an assumption.

The canonical `web-captures/` are read-only and live in the shared checkout (they are gitignored and
belong to the capture machine); nothing here writes to them.

    g1c-bytes.py <rung> [<rung> ...] [--profile KEY ...]
"""

import argparse
import hashlib
import os
import sys

SCRATCH = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1c"
CANONICAL = os.environ.get(
    "VITREA_CANONICAL_CAPTURES",
    "/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
PROFILES = ("apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard",
            "apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard")


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def compare(rung, profile):
    root = os.path.join(SCRATCH, rung, "web-captures", profile)
    if not os.path.isdir(root):
        return None
    same = diff = missing = 0
    movers = []
    for scene in sorted(os.listdir(root)):
        name = f"{scene}__webgpu.png"
        a = os.path.join(root, scene, name)
        b = os.path.join(CANONICAL, profile, scene, name)
        if not os.path.exists(a):
            continue
        if not os.path.exists(b):
            missing += 1
            continue
        if digest(a) == digest(b):
            same += 1
        else:
            diff += 1
            movers.append(scene)
    return same, diff, missing, movers


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("rungs", nargs="+")
    ap.add_argument("--profile", action="append", default=None)
    args = ap.parse_args(argv)
    profiles = args.profile or list(PROFILES)
    for rung in args.rungs:
        for profile in profiles:
            out = compare(rung, profile)
            if out is None:
                continue
            same, diff, missing, movers = out
            tag = "IDENTICAL" if diff == 0 else f"{diff} MOVED"
            print(f"  {rung:>6} {profile:>40}  {same:3d} identical  {tag}"
                  + (f"  (no canonical: {missing})" if missing else ""))
            for scene in movers[:8]:
                print(f"        {scene}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
