#!/usr/bin/env python3.12
"""A G1a-shaped STAND-IN for the declaration G0 (e) writes: test and rehearsal material, never
the declaration, never hashed, never read by a sitting.

The tooling reads a declared plan (pass-spec.py), and the plan does not exist until (e) hashes
it. The suites, the red/green proofs and the timing rehearsal need one of the charter's shape
now, so this module builds it from committed files:

- `scenes_v8_stand_in()`: the canonical scenes.json with the four `-glass0.25` standard profiles
  added as copies of their 0.5 counterparts' scene lists, which is what the charter says version
  8 is ("a diff against version 7 is four entries and a note"; Design, the generation's bed);
- `g1a_plan(...)`: G1a's order as the charter states it (Design, "The two sittings"): at 0.5 the
  side's pose check, W42's two sentinels per endpoint at three runs (long protocol) and six
  canonical bridge cells per canonical pass at three runs, at both scales; at 0.25 dump sentinels
  (six scenes per endpoint, 48 in all) and the four canonical passes (active 162 and receded 119
  cells per scale) at seven runs, 2x at mode 68 then 1x at mode 69; at 0.5 the closing W42
  sentinels at both scales. Which six cells bridge and which six scenes are dumped are THIS
  module's arbitrary picks (the first untinted ones in id order); (e) declares the real ones.
"""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
CANONICAL = 'apps/reference-apple/scenes.json'
W42_SCENES = 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/scenes-w42-body.json'
W42_SENTINELS = ('f-impulse-rrect-md', 'f-checker64-rrect-lg')
POSE_CHECK_FRAMES = ('204f21f0362d3226f7e28690be7c61ece0848931c89062e8a888f1ade22d4033',
                     '6c15311b06af50a17141c54d7a71645cf63518c844b61d113b9426e15bcbf1d0')


def key(scale, scheme, glass):
    return f'apple-macos-27.0-{scale}x-{scheme}-standard-glass{glass}'


def scenes_v8_stand_in(base=None):
    doc = copy.deepcopy(base if base is not None else json.loads((REPO / CANONICAL).read_text()))
    have = {p['key'] for p in doc['profiles']}
    for scale in (1, 2):
        for scheme in ('light', 'dark'):
            source = next(p for p in doc['profiles'] if p['key'] == key(scale, scheme, '0.5'))
            if key(scale, scheme, '0.25') not in have:
                doc['profiles'].append(dict(key=key(scale, scheme, '0.25'), colorScheme=scheme,
                                            a11y=source['a11y'], scenes=list(source['scenes'])))
    doc['$comment-w43-stand-in'] = 'A W43 test stand-in for scenes.json version 8; not the declaration.'
    return doc


def receded(sid):
    return sid.rsplit('__', 1)[-1].startswith('inactive')


def untinted(sid):
    state = sid.rsplit('__', 1)[-1]
    return state in ('rest', 'inactive')


def pose_lists(doc, scale, glass, pose):
    out = {}
    for scheme in ('light', 'dark'):
        k = key(scale, scheme, glass)
        profile = next(p for p in doc['profiles'] if p['key'] == k)
        out[k] = sorted(s for s in profile['scenes'] if receded(s) == (pose == 'receded'))
    return out


def g1a_plan(canonical_doc, canonical_sha, w42_sha, bridge_cells=6, dump_scenes=6, runs=7):
    """The stand-in plan over a v8-shaped canonical document (`canonical_sha` names its bytes)."""
    passes = []

    def capture(name, glass, scale, pose, source, profiles, n, protocol='normal', **extra):
        passes.append(dict(name=name, kind='capture', role=extra.pop('role'), glass=glass, scale=scale, pose=pose,
                           source=source, runs=n, protocol=protocol, profiles=profiles, **extra))

    def opening_or_closing(phase, scale, canonical=True):
        for scheme in ('light', 'dark'):
            for pose in ('active', 'receded'):
                state = 'rest' if pose == 'active' else 'inactive'
                capture(f'{phase}-w42-{scale}x-{scheme}-{pose}', 0.5, scale, pose, 'w42',
                        {key(scale, scheme, '0.5'): sorted(f'{c}__{state}' for c in W42_SENTINELS)}, 3, 'long',
                        role='bridge-w42-sentinel')
        if canonical:
            for pose in ('active', 'receded'):
                lists = pose_lists(canonical_doc, scale, '0.5', pose)
                picked, total = {}, 0
                for k in sorted(lists):
                    take = [s for s in lists[k] if untinted(s)][:bridge_cells // 2]
                    picked[k] = take
                    total += len(take)
                capture(f'{phase}-canonical-{scale}x-{pose}', 0.5, scale, pose, 'canonical', picked, 3,
                        role='bridge-canonical')

    capture('pose-check', 0.5, 2, 'active', 'canonical',
            {key(2, 'light', '0.5'): ['checkerboard__capsule-button__rest']}, 1, role='pose-check',
            expect={f'{key(2, "light", "0.5")}/checkerboard__capsule-button__rest': list(POSE_CHECK_FRAMES)})
    opening_or_closing('open', 2)
    opening_or_closing('open', 1)
    for scale in (2, 1):
        for scheme in ('light', 'dark'):
            for pose in ('active', 'receded'):
                k = key(scale, scheme, '0.25')
                profile = next(p for p in canonical_doc['profiles'] if p['key'] == k)
                rest = sorted(s for s in profile['scenes'] if s.endswith('__rest'))[:dump_scenes]
                passes.append(dict(name=f'dump-0.25-{scale}x-{scheme}-{pose}', kind='dump', role='dump-sentinel',
                                   glass=0.25, scale=scale, pose=pose, source='canonical', profile=k, scenes=rest))
        for pose in ('active', 'receded'):
            capture(f'bed-0.25-{scale}x-{pose}', 0.25, scale, pose, 'canonical',
                    pose_lists(canonical_doc, scale, '0.25', pose), runs, role='bed', publish=True)
    opening_or_closing('close', 1, canonical=False)
    opening_or_closing('close', 2, canonical=False)
    return dict(schema='w43-sitting-plan-1', sitting='g1a',
                **{'$comment': 'A W43 stand-in for the G1a plan (bed/sitting/stand_in.py); not the declaration.'},
                sources=dict(canonical=dict(path=CANONICAL, sha256=canonical_sha),
                             w42=dict(path=W42_SCENES, sha256=w42_sha)),
                passes=passes)


def encode(doc):
    return (json.dumps(doc, indent=2) + '\n').encode()


def build(repo=REPO):
    """(canonical bytes, w42 bytes, plan) for a checkout whose canonical file is to be the stand-in."""
    canonical = encode(scenes_v8_stand_in(json.loads((Path(repo) / CANONICAL).read_text())))
    w42 = (Path(repo) / W42_SCENES).read_bytes()
    plan = g1a_plan(json.loads(canonical), hashlib.sha256(canonical).hexdigest(), hashlib.sha256(w42).hexdigest())
    return canonical, w42, plan


def sources_of(plan, canonical, w42):
    return dict(canonical=json.loads(canonical), w42=json.loads(w42))


if __name__ == '__main__':
    import importlib.util
    spec = importlib.util.spec_from_file_location('w43_pass_spec_stand_in', HERE / 'pass-spec.py')
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    canonical, w42, plan = build()
    sources = sources_of(plan, canonical, w42)
    P.validate_plan(plan, sources)
    print(json.dumps(P.plan_counts(plan, sources)['totals'], indent=2))
