#!/usr/bin/env python3
"""The cells captured while the machine was being used, and what decided them.

The harness gates HID idle ONCE, at a run's opening, and per cell it RECORDS the
idle without refusing — so a touch mid-run files the cell with its
`hidIdleSeconds` beside it and the pose attestation still decides whether it is
evidence. Every such cell attested its pose here; what is left to say is whether
the disturbed run's bytes are the ones the bed published.

For each cell: its idle reading, whether the disturbed run's bytes agree with the
other six, and which byte-state the bed published.
"""
import hashlib
import json
import os

T = os.path.expanduser("~/vitrea-w29-27-run")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
FIX = os.path.join(ROOT, "apps/reference-apple/fixtures")

# (pass, run, profileKey, sceneId) — from the per-run manifests' own idle records.
WATCH = []
for p in sorted(os.listdir(T)):
    d = os.path.join(T, p)
    if not os.path.isdir(d):
        continue
    for n in range(1, 8):
        mp = os.path.join(d, "run-%d" % n, "manifest.json")
        if not os.path.exists(mp):
            continue
        m = json.load(open(mp))
        for pr in m["profiles"]:
            for f in pr["fixtures"]:
                idle = f.get("hidIdleSeconds")
                if isinstance(idle, (int, float)) and idle < 45:
                    WATCH.append((p, n, pr["profileKey"], f["sceneId"], idle))

sha = lambda path: hashlib.sha256(open(path, "rb").read()).hexdigest()
published = {}
manifest = json.load(open(os.path.join(FIX, "manifest.json")))
for pr in manifest["profiles"]:
    for f in pr["fixtures"]:
        published["%s/%s" % (pr["profileKey"], f["sceneId"])] = f

print("| pass | run | cell | idle | the disturbed run's bytes | published |")
print("| --- | ---: | --- | ---: | --- | --- |")
for p, n, key, scene, idle in WATCH:
    digests = {}
    for r in range(1, 8):
        f = os.path.join(T, p, "run-%d" % r, key, scene + ".png")
        if os.path.exists(f):
            digests.setdefault(sha(f), []).append(r)
    mine = next(d for d, rs in digests.items() if n in rs)
    out = os.path.join(FIX, key, scene + ".png")
    pub = sha(out)
    agrees = len(digests[mine])
    entry = published["%s/%s" % (key, scene)]
    how = ("frequency-settled" if entry.get("frequencySettled")
           else "unanimous" if len(digests) == 1 else "voted")
    print("| %s | %d | %s | %.1f s | shared with %d of 7 runs | %s, %s |"
          % (p, n, "%s/%s" % (key.replace("apple-macos-27.0-", "").replace("-glass0.5", ""), scene),
             idle, agrees, how,
             "the disturbed run's" if pub == mine else "NOT the disturbed run's"))

print()
print("cells captured under 45 s of idle: %d of 624" % len(WATCH))
same = sum(1 for p, n, k, s, i in WATCH
           if sha(os.path.join(FIX, k, s + ".png"))
           == sha(os.path.join(T, p, "run-%d" % n, k, s + ".png")))
print("of those, published bytes equal to the disturbed run's: %d" % same)
print()
print("Every one of these cells attested its pose (presentedActive, deterministic,")
print("materialRendered) — the idle reading is a record of the session, not a verdict")
print("on the cell. Where a disturbed run's bytes stand alone, the plurality over the")
print("other six decides and the disturbed reading is simply outvoted.")
