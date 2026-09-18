#!/usr/bin/env python3
"""The per-run attestation audit, over a probe's scratch runs.

The same four-part rule `run-sitting.sh` applies to a pass: every cell must be
`deterministic` and `materialRendered`, and must attest its pose — `presentedActive`
for an active run, and for an inactive run `presentedActive: false` plus a
`presentation` block reading `inactive`, not key, not active.

A probe is not a bed, so nothing here is quarantined. But a probe that compares two
configurations has to know which of its runs reached the pose it claims, because a
run that lost the pose differs from its neighbours by the pose — and that
difference would otherwise be read as the difference the probe is about.

    audit-runs.py <run-dir> [<run-dir> ...]
"""
import json
import os
import sys

bad = 0
for d in sys.argv[1:]:
    path = os.path.join(d, "manifest.json")
    if not os.path.exists(path):
        print(f"{d}: NO MANIFEST")
        bad += 1
        continue
    m = json.load(open(path))
    fixtures = [f for p in m["profiles"] for f in p["fixtures"]]
    # Which rule to apply is read off the run's own record, never off the
    # directory name. An inactive run writes a `presentation` block whose
    # `declaredPose` says what it set out to be; an active run writes none. A path
    # that happens to contain the word would make the audit's verdict depend on
    # how a scratch directory was named, which is the one input it must not have.
    inactive = any((f.get("presentation") or {}).get("declaredPose") == "inactive"
                   for f in fixtures)
    ok, problems = 0, []
    for f in fixtures:
        pres = f.get("presentation") or {}
        good = f.get("deterministic") and f.get("materialRendered")
        if inactive:
            good = (good and f.get("presentedActive") is False
                    and pres.get("observedPose") == "inactive"
                    and pres.get("isKeyWindow") is False
                    and pres.get("appIsActive") is False)
        else:
            good = good and bool(f.get("presentedActive"))
        if good:
            ok += 1
        else:
            problems.append(f"{f['sceneId']}(active={f.get('presentedActive')},"
                            f"idle={f.get('hidIdleSeconds'):.1f})")
    verdict = "attested" if ok == len(fixtures) else "FAILED"
    print(f"{d}: {verdict} {ok}/{len(fixtures)}" + (f"  {'; '.join(problems)}" if problems else ""))
    if ok != len(fixtures):
        bad += 1
print(f"\n{bad} of {len(sys.argv) - 1} runs failed the audit")
sys.exit(1 if bad else 0)
