#!/usr/bin/env python3
"""The pose and run facts a `dump-layers` JSON attests, for every dump named.

A dump carries its own `isKeyWindow`, `appIsActive` and `activationPolicy`, which
is what makes the recede arm of a comparison checkable rather than assumed: two
arms that were meant to differ only in the bundle must agree on the pose, and an
arm that silently kept the active pose would otherwise read as a material change.
"""
import json
import sys

FIELDS = ["isKeyWindow", "appIsActive", "activationPolicy", "os", "colorScheme",
          "settleSeconds", "backingScaleFactor", "a11y", "scene"]

for path in sys.argv[1:]:
    d = json.load(open(path))
    print(path)
    print("   " + "  ".join(f"{f}={d.get(f)}" for f in FIELDS))
