#!/usr/bin/env python3.12
"""W42 G2 step 4: assemble a document set's scratch stages (one per scheme) from its `compare` runs.

    stage.py <set>        -> SCRATCH/stages/<set>-light, SCRATCH/stages/<set>-dark

A stage here has the W40 layout the gate's referees and owner runner read (`membership.json`,
`matrix.json`), in the shape the G0 gate proved a G2 stage has (`gate/owner/proof.txt`, the `-g2`
stages): the WebGPU tier, the CURRENT generation's membership of each profile (its holdout declared
and not held), every non-holdout member rendered by `render.py canon` at the set's documents. The
membership is the current rows' rather than `matrix stage`'s declaration because the current
generation holds 55 of the manifest's 87 probe fixtures per standard profile and none for the two
accessibility profiles; a stage of a different membership would change what the owner test's tables
count in the base and the candidate alike. `matrix.json` is a schema-5 envelope of the compare rows'
own bytes. Nothing is published: this is never a `matrix publish` input.
"""
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
sys.path.insert(0, str(CAL / 'results/2026-09-26-w40-g0-generations'))
import matrix_store as store  # noqa: E402

sys.path.insert(0, str(HERE))
import render  # noqa: E402

SCRATCH = render.SCRATCH
SCHEMES = {'light': render.CANON_PROFILES[:4], 'dark': render.CANON_PROFILES[4:]}


def document(path):
    return dict(path=path, sha256=render.sha(render.REPO / path)[:12])


def build(name):
    docs = render.documents(name)
    index = json.loads((CAL / 'results/generations/index.json').read_text())
    report = {}
    for scheme, profiles in SCHEMES.items():
        target = SCRATCH / 'stages' / f'{name}-{scheme}'
        if target.exists():
            raise SystemExit(f'{target} exists')
        active, receded = (document(p) for p in docs[scheme])
        raw, members = [], []
        for profile in profiles:
            current = json.loads((CAL / 'results/generations' / index['currentByProfile'][profile]).read_text())
            mine = [c for c in current['cells'] if c['key']['profileKey'] == profile
                    and c['key']['web']['renderer'] == 'webgpu']
            members += [dict(profileKey=profile, renderer='webgpu', fixtureSet=c['fixtureSet'],
                             sceneId=c['key']['sceneId']) for c in mine]
            rows = store.load_current_rows(matrix_path=str(SCRATCH / 'canon' / name / 'matrices' / f'{profile}.json'))
            want = {(c['fixtureSet'], c['key']['sceneId']) for c in mine if c['fixtureSet'] != 'holdout'}
            got = {(r['fixtureSet'], r['key']['sceneId']) for r in rows}
            if got != want:
                raise SystemExit(f'{name} {profile}: rendered {len(got)} members, current non-holdout {len(want)}; '
                                 f'missing {sorted(want - got)[:3]}, extra {sorted(got - want)[:3]}')
            for r in rows:
                named = {kind: (path, sha) for kind, path, sha in store.documents(r)}
                if named != {'materialProfile': (active['path'], active['sha256']),
                             'recededProfile': (receded['path'], receded['sha256'])}:
                    raise SystemExit(f'{name} {profile} {r["key"]["sceneId"]}: names {named}')
                if r['key']['web']['renderer'] != 'webgpu':
                    raise SystemExit(f'{name} {profile} {r["key"]["sceneId"]}: fell back to {r["key"]["web"]["renderer"]}')
                raw.append(store._RAW[id(r)])
        target.mkdir(parents=True)
        (target / 'matrix.json').write_bytes(b'{\n  "schemaVersion": 5,\n  "cells": [\n    ' +
                                             b',\n    '.join(raw) + b'\n  ]\n}\n')
        membership = dict(schemaVersion=1, profiles=list(profiles), tiers=['webgpu'],
                          sets=sorted({m['fixtureSet'] for m in members}), active=active, receded=receded,
                          cells=members)
        (target / 'membership.json').write_text(json.dumps(membership, indent=2) + '\n')
        report[scheme] = dict(stage=str(target), rows=len(raw), declared=len(members),
                              holdoutDeclaredNotHeld=sum(m['fixtureSet'] == 'holdout' for m in members),
                              active=active, receded=receded,
                              matrixSha256=render.sha(target / 'matrix.json'))
    print(json.dumps(report, indent=1))
    return report


if __name__ == '__main__':
    build(sys.argv[1])
