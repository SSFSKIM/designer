#!/usr/bin/env python3
"""provenance.json: the run directories, their manifests' digests and their timestamps."""
import hashlib
import json
import os

T = os.path.expanduser("~/vitrea-w29-27-run")
OUT = ("/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a5a7ffc7b0fe57fb9/"
       "packages/calibration/results/2026-09-18-w29-g1-bed/provenance.json")
PASSES = ["standard-active-2x", "standard-inactive-2x", "standard-active-1x",
          "standard-inactive-1x", "increased-contrast-active-1x",
          "increased-contrast-inactive-1x", "reduced-transparency-active-1x",
          "reduced-transparency-inactive-1x"]

doc = {
    "gate": "W29 G1 Part B; acceptance clause 2; claims 5.150",
    "note": ("The raw runs stay on the capture machine, as a sitting's snapshots do. This names "
             "them, digests each run's manifest so the published bed can be traced back to the "
             "run that produced it, and records the first and last cell each run captured."),
    "sittingDir": "~/vitrea-w29-27-run",
    "passes": {},
}
for p in PASSES:
    runs = []
    for n in range(1, 8):
        d = os.path.join(T, p, "run-%d" % n)
        raw = open(os.path.join(d, "manifest.json"), "rb").read()
        m = json.loads(raw)
        stamps = sorted(f["capturedAt"] for pr in m["profiles"] for f in pr["fixtures"])
        runs.append({
            "run": "run-%d" % n,
            "manifestSha256": hashlib.sha256(raw).hexdigest(),
            "cells": sum(len(pr["fixtures"]) for pr in m["profiles"]),
            "firstCapturedAt": stamps[0],
            "lastCapturedAt": stamps[-1],
            "attestReadSha256": hashlib.sha256(
                open(os.path.join(d, "attest.read"), "rb").read()).hexdigest(),
            "attestCloseSha256": hashlib.sha256(
                open(os.path.join(d, "attest.close"), "rb").read()).hexdigest(),
        })
    doc["passes"][p] = {
        "runs": runs,
        "profiles": sorted({pr["profileKey"] for pr in
                            json.load(open(os.path.join(T, p, "run-1", "manifest.json")))["profiles"]}),
        "passSpec": "%s.scenes-27.json" % p,
        "passSpecSha256": hashlib.sha256(
            open(os.path.join(T, "%s.scenes-27.json" % p), "rb").read()).hexdigest(),
    }
open(OUT, "w").write(json.dumps(doc, indent=2) + "\n")
print("wrote", OUT)
for p in PASSES:
    r = doc["passes"][p]["runs"]
    print("%-34s %d runs, %d cells each, %s .. %s"
          % (p, len(r), r[0]["cells"], r[0]["firstCapturedAt"], r[-1]["lastCapturedAt"]))
