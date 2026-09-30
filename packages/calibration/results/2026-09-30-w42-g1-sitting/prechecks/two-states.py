#!/usr/bin/env python3.12
"""The canonical cell's two launch-level states across every stored positive check (W42 G1 check 1).

two-states.py > two-states.json

Reads the raw captures, which stay outside git under ~/vitrea-w39/run and ~/vitrea-w42/g1, and
the committed canonical fixture at this checkout's HEAD. For each positive check of
checkerboard__capsule-button__rest @ apple-macos-27.0-2x-light-standard-glass0.5 it records the
frame's SHA-256, its difference from the fixture, the fixture's own attestations and the on-screen
window owners read before and after the launch. A Window Server window at level 2147483630 is
kCGCursorWindowLevel. Its presence is recorded as a correlate, not as a cause.
"""
import hashlib
import io
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[5]
REL = 'apple-macos-27.0-2x-light-standard-glass0.5/checkerboard__capsule-button__rest.png'
CANONICAL = 'apps/reference-apple/fixtures/' + REL
CURSOR = 'Window Server|2147483630'
CHECKS = {
    'w39-g1-step0-original': Path.home() / 'vitrea-w39/run/preconditions/original-positive-1',
    'w39-g1-side-pose-check-2': Path.home() / 'vitrea-w39/run/grant-checks/side-pose-check-2',
    'w39-close-original': Path.home() / 'vitrea-w39/run/grant-checks/wave-close-2',
    'w42-g1-original-positive-1': Path.home() / 'vitrea-w42/g1/prechecks/original-positive-1',
}

canonical = subprocess.run(['git', '-C', str(REPO), 'show', f'HEAD:{CANONICAL}'], capture_output=True,
                           check=True).stdout
b = np.asarray(Image.open(io.BytesIO(canonical)).convert('RGBA'), dtype=np.int16)
rows = {}
for name, run in CHECKS.items():
    raw = (run / REL).read_bytes()
    a = np.asarray(Image.open(run / REL).convert('RGBA'), dtype=np.int16)
    d = np.abs(a - b).max(axis=2)
    ys, xs = np.nonzero(d)
    before = json.loads((run / 'session-before.json').read_text())['windowOwners']
    after = json.loads((run / 'session-after.json').read_text())['windowOwners']
    fixture = json.loads((run / 'manifest.json').read_text())['profiles'][0]['fixtures'][0]
    rows[name] = dict(
        sha256=hashlib.sha256(raw).hexdigest(), byteIdenticalToFixture=raw == canonical,
        differingPixels=int((d > 0).sum()), maxAbsCode=int(d.max()),
        codeHistogram=np.bincount(d[d > 0]).tolist() if d.any() else [],
        bboxXY=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if d.any() else None,
        signedMeanRGB=[round(float(v), 3) for v in (a - b)[d > 0][:, :3].mean(axis=0)] if d.any() else None,
        capturedAt=fixture.get('capturedAt'), presentedActive=fixture.get('presentedActive'),
        materialRendered=fixture.get('materialRendered'), deterministic=fixture.get('deterministic'),
        repeatNoise=fixture.get('repeatNoise'), hidIdleSeconds=fixture.get('hidIdleSeconds'),
        cursorWindowBefore=CURSOR in before, cursorWindowAfter=CURSOR in after,
        windowOwnersBefore=before, windowOwnersAfter=after)
states = {}
for name, row in rows.items():
    states.setdefault(row['sha256'], []).append(name)
print(json.dumps(dict(canonical=CANONICAL, canonicalSha256=hashlib.sha256(canonical).hexdigest(),
                      states=states, checks=rows), indent=1, ensure_ascii=False))
