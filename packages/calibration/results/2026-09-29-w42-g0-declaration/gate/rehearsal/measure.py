"""W42 G0 rehearsal: re-measure a swapped capture tree with the calibration's own instrument and
assemble one scratch STAGE per colour scheme, as G2's candidate reads will be assembled.

The instrument is `compare --skip-capture` (cli/compare.ts), pointed at the tree through
`VITREA_WEB_CAPTURES` and writing a scratch `--out-matrix`: the same `measureCell` every
canonical row was measured with, the same options, and a row field-for-field equal to the
canonical row on an unchanged capture except `capturedAt` (checked on the identity tree by
`identity-check`). A stage is a W40 stage directory — `membership.json` (the declared cells,
one active/receded document pair) and `matrix.json` (the rows) — which the gate's referees read
with `--stage DIR --candidate PATH` (gate/referees/README.txt).

    python3.12 -B measure.py --tree /scratch/tree-c1 --variant c1 --out /scratch/stage-c1
    python3.12 -B measure.py --identity-check /scratch/stage-identity
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from swap import CAL, PROFILES, ROOT, SPLIT, population, store  # noqa: E402
from swap import doc_dir as S_doc_dir  # noqa: E402


def measure_profile(tree: Path, variant: str, profile: str, out: Path) -> Path:
    scheme = 'light' if '-light-' in profile else 'dark'
    docs = HERE / 'documents' / S_doc_dir(variant)
    active = docs / f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json'
    receded = docs / f'apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded.json'
    matrix = out / f'{profile}.json'
    if matrix.exists():
        matrix.unlink()
    log = out / f'{profile}.log'
    env = dict(os.environ, VITREA_WEB_CAPTURES=str(tree))
    cmd = ['pnpm', '-s', 'run', 'compare', '--', '--skip-capture', '--profile', profile,
           '--renderer', 'webgpu', '--set', 'calibration,validation,probe',
           '--material-profile', str(active.relative_to(CAL)),
           '--receded-profile', str(receded.relative_to(CAL)), '--out-matrix', str(matrix),
           '--write-partial']
    with log.open('w') as f:
        rc = subprocess.run(cmd, cwd=CAL, env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    # compare plans every manifest fixture of the profile; the canonical tree (and so the swapped
    # one) holds captures only for the rows the current union carries, so a planned cell with no
    # capture is expected and `--write-partial` writes the rest. What is required is that every
    # row of the population was measured, and nothing else was.
    want = {r['key']['sceneId'] for r in population([profile])}
    got = {r['key']['sceneId'] for r in store.load_current_rows(matrix_path=str(matrix))} \
        if matrix.exists() else set()
    # A population cell the instrument itself refuses to measure (not a missing capture, e.g.
    # "a 0.00px contour ... carries no curvature" when a candidate's body is hard to tell from
    # its backdrop) is recorded as UNMEASURED beside the stage, never silently dropped; a PROBE
    # cell may be (no adopted referee reads a probe photo), any other cell refuses the stage.
    missing = sorted(want - got)
    refused = [c for c in missing if f'{profile} / {c}: no webgpu-tier capture' not in log.read_text()]
    if got - want or set(missing) - set(refused) or any(SPLIT.get(c) != 'probe' for c in refused):
        raise SystemExit(f'measure: {profile}: compare exited {rc}; population {len(want)}, '
                         f'measured {len(got)}, missing {missing[:5]}, extra '
                         f'{sorted(got - want)[:5]}; see {log}')
    if refused:
        (out / f'{profile}.unmeasured.json').write_text(json.dumps(dict(
            profile=profile, cells=refused,
            reason='the instrument refused the candidate capture (see the log); probe cells only'),
            indent=1) + '\n')
    return matrix


def assemble(variant: str, out: Path, matrices: dict[str, Path]):
    """One stage per scheme, named by the variant's documents."""
    for scheme in ('light', 'dark'):
        stage = out / f'stage-{scheme}'
        stage.mkdir(parents=True, exist_ok=True)
        rows, cells = [], []
        for profile, path in matrices.items():
            if f'-{scheme}-' not in profile:
                continue
            for raw in store.load_current_rows(matrix_path=str(path)):
                rows.append(raw)
                cells.append(dict(profileKey=profile, renderer='webgpu', fixtureSet=raw['fixtureSet'],
                                  sceneId=raw['key']['sceneId']))
        docs = HERE / 'documents' / S_doc_dir(variant)
        import hashlib

        def doc(name):
            p = docs / name
            return dict(path=str(p.relative_to(ROOT)),
                        sha256=hashlib.sha256(p.read_bytes()).hexdigest()[:12])
        membership = dict(
            schemaVersion=1,
            profiles=sorted({c['profileKey'] for c in cells}),
            tiers=['webgpu'], sets=['calibration', 'validation', 'probe'],
            active=doc(f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json'),
            receded=doc(f'apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded.json'),
            cells=sorted(cells, key=lambda c: (c['profileKey'], c['sceneId'])),
            **{'$comment': f'W42 G0 rehearsal stage, variant {variant}: scratch, never published'})
        (stage / 'membership.json').write_text(json.dumps(membership, indent=1) + '\n')
        rows.sort(key=store.key)
        raw = (b'{\n  "schemaVersion": 5,\n  "cells": [\n    ' +
               b',\n    '.join(store._RAW[id(r)] for r in rows) + b'\n  ]\n}\n')
        (stage / 'matrix.json').write_bytes(raw)
        print(f'{stage}: {len(rows)} rows', file=sys.stderr)


def identity_check(out: Path):
    """Every identity-stage row equals its canonical row except `capturedAt` and the document
    clause the rehearsal renames (the documents differ by one comment key; see swap.py)."""
    import re
    canonical = {store.key(r): r for r in population()}
    strip = lambda s: re.sub(r'(materialProfile|recededProfile)=\S+ sha256:[0-9a-f]{12}', r'\1=DOC', s)
    n, bad = 0, []
    for scheme in ('light', 'dark'):
        for r in store.load_current_rows(matrix_path=str(out / f'stage-{scheme}' / 'matrix.json')):
            r2 = json.loads(json.dumps(r))
            key = next(k for k, c in canonical.items() if c['key']['profileKey'] == r['key']['profileKey']
                       and c['key']['sceneId'] == r['key']['sceneId'])
            c = json.loads(json.dumps(canonical[key]))
            for x in (r2, c):
                x.pop('capturedAt')
                x['key']['web']['capturePath'] = strip(x['key']['web']['capturePath'])
            n += 1
            if r2 != c:
                bad.append(f"{r['key']['profileKey']}/{r['key']['sceneId']}")
    print(f'identity rows {n}, equal to canonical except capturedAt and the document clause: '
          f'{n - len(bad)}; differing: {bad}')
    return not bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tree', type=Path)
    ap.add_argument('--variant')
    ap.add_argument('--out', type=Path)
    ap.add_argument('--profiles', default=','.join(PROFILES))
    ap.add_argument('--identity-check', type=Path)
    args = ap.parse_args()
    if args.identity_check:
        raise SystemExit(0 if identity_check(args.identity_check) else 1)
    args.out.mkdir(parents=True, exist_ok=True)
    profiles = args.profiles.split(',')
    with cf.ThreadPoolExecutor(len(profiles)) as ex:
        futures = {p: ex.submit(measure_profile, args.tree.resolve(), args.variant, p, args.out) for p in profiles}
        matrices = {p: f.result() for p, f in futures.items()}
    assemble(args.variant, args.out, matrices)


if __name__ == '__main__':
    main()
