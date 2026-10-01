#!/usr/bin/env python3.12
"""W43 G0 (e): the in-sitting bridge cells, declared (charter clause 3; Design "The bridges"; X43).

    python3.12 -B declare-bridges.py          # writes bridge-cells.json
    python3.12 -B declare-bridges.py check    # re-derives it and compares, byte for byte

Each sitting captures, at the slider's 0.5 and nowhere else:
- **W42's two sentinel cells** (`f-impulse-rrect-md`, `f-checker64-rrect-lg`, from W42's pinned scenes
  file), long protocol, three runs per endpoint, at the sitting's OPENING and again at its CLOSE. Their
  reference frames are W42 G1's sentinel rows in `w42-archive` (probe role, through the guarded Reader).
  G1a takes all eight endpoints (both scales), G1b the four 2x endpoints.
- **Six canonical cells per canonical pass**, three runs, at the OPENING only, against their committed
  `-glass0.5` fixtures. A canonical pass is one scale and one pose, both schemes (W29's passes), so G1a
  has four passes and G1b, whose cells are all 2x, two.

The six canonical cells are chosen for what G0 (b)'s bridge did not cover (X43: no 0.25-against-0.5
claim is stated for a cell type no bridge covered). G0 (b) covered the two-level checker on rrect-md
(2x), the pitch-64 checker on rrect-lg, the impulse on rrect-md in light and photo on rrect-md (2x).
These add uniform backdrops on the capsule and rrect-lg (the exterior shadow's largest span), an
author tint on photo and on the checker, the saturated mid-chroma solid, and text on the smallest shape,
in both schemes and both poses at both scales. Every one is a calibration, validation or probe scene of the
canonical split (never holdout or recorded), declared in both poses of its scheme at both scales.

The metric is the charter's: a cell AGREES when one of its runs is pixel-identical to its reference frame
(byte identity), or else when every region statistic of its plurality frame lies within max(1 code, bar)
of the reference's, with W42's instrument unchanged (`forward.Cell` at the cell's geometry; masks `n` and
`w` when active, `n` when receded; `regions.statistics`) and the bar W39's, 0.5 + half the largest
pairwise separation of the run medians. G0 (b)'s `bridge/bridge.py` is that reader on existing evidence.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SCENES = ROOT / 'apps/reference-apple/scenes.json'
FIXTURES = ROOT / 'apps/reference-apple/fixtures'
W42_SCENES = ROOT / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/scenes-w42-body.json'
W42_SCENES_SHA = '4aa06af90eb527b249fdede3d7d102b06c027069552c07dfc7456b7bd2c43ca0'
OUT = HERE / 'bridge-cells.json'
SENTINELS = ('f-impulse-rrect-md', 'f-checker64-rrect-lg')
CANONICAL = {'light': ('dark-solid__capsule-button', 'photo__capsule-button@tint-orange',
                       'mid-chroma-solid__rrect-md'),
             'dark': ('dark-solid__rrect-lg', 'checkerboard__capsule-button@tint-orange', 'hc-text__rrect-sm')}
RUNS = 3
SITTINGS = {'G1a': (2, 1), 'G1b': (2,)}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def scene_id(cell, pose):
    base, _, tint = cell.partition('@')
    state = 'rest' if pose == 'active' else 'inactive'
    return f'{base}__{state}' + (f'-{tint}' if tint else '')


def build():
    spec = json.loads(SCENES.read_text())
    roles = {s: r for r, ids in spec['split'].items() if not r.startswith('$') for s in ids}
    members = {p['key']: set(p['scenes']) for p in spec['profiles']}
    if sha(W42_SCENES.read_bytes()) != W42_SCENES_SHA:
        raise SystemExit("W42's scenes file is not the pinned one")
    w42 = {s['id'] for s in json.loads(W42_SCENES.read_text())['scenes']}
    canonical, fixtures = {}, {}
    for scale in (2, 1):
        for pose in ('active', 'receded'):
            rows = []
            for scheme, cells in CANONICAL.items():
                profile = f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'
                for cell in cells:
                    sid = scene_id(cell, pose)
                    if sid not in members[profile]:
                        raise SystemExit(f'{sid} is not declared in {profile}')
                    if roles[sid] not in ('calibration', 'validation', 'probe'):
                        raise SystemExit(f'{sid} is {roles[sid]}: a bridge never reads a holdout or recorded fixture')
                    path = FIXTURES / profile / f'{sid}.png'
                    fixtures[f'{profile}/{sid}'] = sha(path.read_bytes())
                    rows.append(dict(profile=profile, scene=sid, role=roles[sid]))
            canonical[f'{scale}x-{pose}'] = rows
    sentinels = {}
    for scale in (2, 1):
        for scheme in ('light', 'dark'):
            for pose in ('active', 'receded'):
                state = 'rest' if pose == 'active' else 'inactive'
                ids = [f'{c}__{state}' for c in SENTINELS]
                missing = [i for i in ids if i not in w42]
                if missing:
                    raise SystemExit(f'not W42 scene ids: {missing}')
                sentinels[f'{scale}x-{scheme}-{pose}'] = dict(
                    profile=f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5', scenes=ids,
                    reference='w42-archive, W42 G1 sentinel rows (long protocol, 3 runs), probe role')
    plan = {}
    for sitting, scales in SITTINGS.items():
        s_eps = [k for k in sentinels if int(k[0]) in scales]
        c_passes = [k for k in canonical if int(k[0]) in scales]
        per_open = len(s_eps) * len(SENTINELS) * RUNS
        plan[sitting] = dict(
            scales=[f'{s}x' for s in scales], sentinelEndpoints=s_eps, canonicalPasses=c_passes,
            captures=dict(sentinelsOpening=per_open, sentinelsClose=per_open,
                          canonicalOpening=sum(len(canonical[p]) for p in c_passes) * RUNS,
                          total=2 * per_open + sum(len(canonical[p]) for p in c_passes) * RUNS))
    return dict(
        schema='w43-bridge-cells-1', charter='docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md',
        slider=0.5, runs=RUNS,
        sentinels=dict(cells=list(SENTINELS), scenesFile=dict(path=str(W42_SCENES.relative_to(ROOT)), sha256=W42_SCENES_SHA),
                       protocol='long', when='opening and close of each sitting', byEndpoint=sentinels),
        canonical=dict(cells=CANONICAL, when='opening of each sitting', byPass=canonical,
                       scenesSha256=sha(SCENES.read_bytes()), fixtureSha256=dict(sorted(fixtures.items()))),
        coveredByG0b=['checkerboard__rrect-md (2x, all four window states)', 'checkerboard-64__rrect-lg (1x and 2x)',
                      'impulse__rrect-md (light, 1x and 2x)', 'photo__rrect-md (2x)'],
        metric=dict(agree='a run pixel-identical to the reference frame; else every region statistic of the plurality '
                          'frame within max(1 code, bar) of the reference', bar='0.5 + 0.5 x the largest pairwise '
                          'separation of the run medians, per cell, region statistic and channel',
                    regions="W42's instrument unchanged: forward.Cell at the cell's geometry, masks n and w active, n "
                            'receded; regions.statistics', reader='bridge/bridge.py (G0 (b))'),
        stops={'before the sittings': 'a disagreement goes to the user before the declaration is hashed (G0 (b): none)',
               'at an opening': 'stops that sitting before any capture away from 0.5',
               'at a close': "voids nothing already admitted; G2 reads that sitting's claims against 0.5 as unbridged "
                             '(X43) and the user rules before G3 opens'},
        sittings=plan)


def main(argv):
    text = json.dumps(build(), indent=2) + '\n'
    if len(argv) > 1 and argv[1] == 'check':
        ok = OUT.exists() and OUT.read_text() == text
        print('check: ' + ('bridge-cells.json is this generator\'s output' if ok else 'MISMATCH'))
        return 0 if ok else 1
    OUT.write_text(text)
    print(json.dumps(json.loads(text)['sittings'], indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
