"""W26 G0 — byte identity between two capture roots, per scene, per profile.

The inert default's proof: a rung captured with the three candidate taps present but at their
defaults must reproduce the bytes of the same rows captured before the mechanism existed, and the
canonical `web-captures/` in the main checkout is what the 0.14.0 bed's bytes actually are. Both
roots are read; nothing is written. Read-only on the canonical root (X2).

    g0-bytes.py <root-a> <root-b> [--only SUBSTR]
"""

import hashlib
import os
import sys


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:12]


def main(argv):
    a, b = argv[0], argv[1]
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1]
    same = diff = missing = 0
    for profile in sorted(os.listdir(b)):
        pb = os.path.join(b, profile)
        if not os.path.isdir(pb):
            continue
        for scene in sorted(os.listdir(pb)):
            if only is not None and only not in scene:
                continue
            name = f"{scene}__webgpu.png"
            fa = os.path.join(a, profile, scene, name)
            fb = os.path.join(pb, scene, name)
            if not (os.path.exists(fa) and os.path.exists(fb)):
                print(f"  MISSING  {profile:44} {scene}")
                missing += 1
                continue
            da, db = digest(fa), digest(fb)
            if da == db:
                same += 1
            else:
                diff += 1
                print(f"  DIFFER   {profile:44} {scene:44} {da} {db}")
    print(f"{same} identical, {diff} differing, {missing} missing")
    return 1 if diff or missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
