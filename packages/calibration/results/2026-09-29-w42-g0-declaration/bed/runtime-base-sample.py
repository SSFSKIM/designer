#!/usr/bin/env python3.12
"""Declare the canonical cells G2 re-renders to prove its runtime base (charter clause 8, X37).

Clause 8: "a sample of the canonical bed declared in G0 (every backdrop kind, both scales,
both poses, both schemes), rendered with the SHIPPED documents at G2's base ... byte-identical
to the canonical capture tree, after check-capture-tree exits 0 on that tree".

The sample is one cell per canonical backdrop KIND (solid, checkerboard, impulse,
synthetic-photo, text-rows) in each of the four macOS 27 standard profiles and both poses:
5 x 4 x 2 = 40 WebGPU renders. Every cell is chosen from the canonical calibration or probe
roles (plus impulse, calibration on the capsule), never holdout or recorded, and must exist
in the profile and in the canonical capture tree. The solid is the scheme's own system
backdrop (light-solid in light, dark-solid in dark; light-solid is not in the dark
profiles); the text-rows cell is the probe hc-text-7 on rrect-md, because hc-text on the
capsule and rrect-md is canonical holdout.

This script reads declaration files and, for the record, the SHA-256 of each sample PNG in the
canonical tree as it stood when G0 declared it (web renders of calibration/probe cells; no
native pixel). It proves nothing: G2 runs check-capture-tree, renders the sample with the
shipped documents at its base and requires byte identity (X37); it repeats that whenever the
base moves before G3's seal.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROFILES = [f'apple-macos-27.0-{s}x-{c}-standard-glass0.5' for s in (1, 2) for c in ('light', 'dark')]
KINDS = {
    'solid': {'light': 'light-solid__rrect-md', 'dark': 'dark-solid__rrect-md'},
    'checkerboard': 'checkerboard__rrect-md',
    'impulse': 'impulse__capsule-button',
    'synthetic-photo': 'photo__rrect-md',
    'text-rows': 'hc-text-7__rrect-md',
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tree', type=Path, required=True,
                    help='the canonical web-captures tree (on the capture machine, gitignored)')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    spec = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())
    roles = {sid: role for role, ids in spec['split'].items() if not role.startswith('$') for sid in ids}
    members = {p['key']: set(p['scenes']) for p in spec['profiles']}
    cells, problems = [], []
    for profile in PROFILES:
        scheme = 'light' if '-light-' in profile else 'dark'
        for kind, base in KINDS.items():
            base = base[scheme] if isinstance(base, dict) else base
            bg = spec['backgrounds'][base.split('__')[0]]['kind']
            if bg != kind:
                problems.append(f'{base}: background kind {bg}, not {kind}')
            for state in ('rest', 'inactive'):
                sid = f'{base}__{state}'
                role = roles.get(sid)
                if role not in ('calibration', 'validation', 'probe'):
                    problems.append(f'{sid}: role {role} is not admissible in the sample')
                if sid not in members[profile]:
                    problems.append(f'{sid}: not in {profile}')
                png = args.tree / profile / sid / f'{sid}__webgpu.png'
                report = args.tree / profile / sid / 'report__webgpu.json'
                row = dict(profile=profile, scene=sid, kind=kind, pose='active' if state == 'rest' else 'receded',
                           role=role, renderer='webgpu', png=str(png.relative_to(args.tree)))
                if png.is_file():
                    row['sha256AtG0'] = hashlib.sha256(png.read_bytes()).hexdigest()
                    r = json.loads(report.read_text())
                    row['documentsAtG0'] = dict(material=r['materialProfile']['sha256'],
                                                receded=(r.get('recededProfile') or {}).get('sha256'))
                else:
                    problems.append(f'{png}: absent from the canonical tree')
                cells.append(row)
    value = dict(
        schema='w42-runtime-base-sample-1', clause='charter clause 8; X37',
        rule='one cell per canonical backdrop kind x the four macOS 27 standard profiles x both poses; '
             'WebGPU; canonical calibration/validation/probe roles only (no holdout, no recorded)',
        count=len(cells), cells=cells,
        canonicalScenesSha256=hashlib.sha256((ROOT / 'apps/reference-apple/scenes.json').read_bytes()).hexdigest(),
        tree='packages/calibration/web-captures in the capture machine\'s main checkout (gitignored)',
        proofInG2=['pnpm --filter @vitrea/calibration run check-capture-tree exits 0 on the tree',
                   'render every sample cell with the SHIPPED documents at G2\'s base (capture-web.ts, '
                   'WebGPU, full Chromium, fallback adapter refused) into scratch',
                   'require PNG byte identity against the tree; any difference is attributed and resolved '
                   'before any candidate render (X37); repeat whenever the base moves before the seal'],
        note='sha256AtG0 records the tree when G0 declared the sample; the proof compares against the tree '
             'G2 finds after check-capture-tree exits 0, not against this record',
        problems=problems)
    args.out.write_text(json.dumps(value, indent=1) + '\n')
    print(json.dumps(dict(count=len(cells), problems=problems), indent=1))
    raise SystemExit(1 if problems else 0)


if __name__ == '__main__':
    main()
