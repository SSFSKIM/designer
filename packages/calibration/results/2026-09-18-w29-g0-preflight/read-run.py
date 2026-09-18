#!/usr/bin/env python3
"""Summarise one scratch run's manifest: the machine it attests, and the honesty
fields per cell.

G0 runs the harness into scratch roots rather than into the bed, so nothing here
reads or writes `apps/reference-apple/fixtures/`. What it prints is the run's own
attestation — the hardware block (which on 27 is the harness's own reading of the
OS), the display block (name and colour profile, the fields the 26.5 profiles
carry), and per cell `materialRendered`, `deterministic`, `presentedActive`, the
observed pose and the HID idle at the moment of capture.
"""
import json
import sys

for path in sys.argv[1:]:
    m = json.load(open(path))
    print(f"== {path}")
    print("   hardware:", json.dumps(m.get("hardware"), ensure_ascii=False))
    for p in m["profiles"]:
        print(f"   profile {p['profileKey']}: display={json.dumps(p.get('display'), ensure_ascii=False)}")
        for f in p["fixtures"]:
            pres = f.get("presentation") or {}
            print(f"     {f['sceneId']}: material={f.get('materialRendered')} "
                  f"deterministic={f.get('deterministic')} repeatNoise={f.get('repeatNoise')} "
                  f"active={f.get('presentedActive')} pose={pres.get('observedPose')} "
                  f"key={pres.get('isKeyWindow')} appActive={pres.get('appIsActive')} "
                  f"idle={f.get('hidIdleSeconds')} sha={str(f.get('sha256'))[:16]} "
                  f"identicalToBackground={f.get('identicalToBackground')}")
    for c in m.get("caveats") or []:
        print("   CAVEAT:", c[:160])
