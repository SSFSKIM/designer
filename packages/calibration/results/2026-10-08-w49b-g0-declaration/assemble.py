#!/usr/bin/env python3.12
"""Assemble W49b before first render; the declarations themselves are sealed by declare.py."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


if any((HERE / f'{p}.sha256').exists() for p in ('declaration', 'fit-declaration')):
    raise SystemExit('Existing seal; assembly is closed')
paths = set()
for subtree in ('tools', 'native-bed', 'batches'):
    paths.update(p for p in (HERE / subtree).rglob('*') if p.is_file() and
                 '__pycache__' not in p.parts and p.suffix != '.pyc')
for name in ('references.json', 'rulings.txt', 'declare.py', 'test_declare.py', 'assemble.py'):
    paths.add(HERE / name)
paths.update(p for p in (HERE / 'checks').iterdir() if p.suffix in ('.py', '.ts'))
for rel in ('packages/renderer-webgpu/src/material.ts', 'packages/renderer-webgpu/src/pyramid.ts',
            'packages/renderer-webgpu/src/pyramid-plan.ts', 'packages/renderer-webgpu/src/renderer.ts',
            'packages/renderer-webgpu/src/passes.ts', 'packages/renderer-webgpu/src/texture-pool.ts',
            'packages/renderer-webgpu/src/wgsl/optics.ts', 'packages/platform-web/src/optics.ts',
            'packages/calibration/scripts/no-opaque-glass.ts',
            'packages/calibration/scripts/material-profile-file.ts',
            'packages/calibration/scripts/candidate-document.ts',
            'packages/calibration/test/tier-coherence.test.ts',
            'packages/renderer-webgpu/test/w49b-bandwidth.test.ts',
            'packages/renderer-webgpu/test/w49b-transmission-top.test.ts',
            'packages/renderer-webgpu/test/frame-composition.test.ts',
            'packages/renderer-webgpu/e2e/gpu/w49b-bandwidth.spec.ts',
            'packages/renderer-webgpu/e2e/gpu/w49b-identity.spec.ts',
            'packages/renderer-webgpu/e2e/bench/w49b.spec.ts',
            'packages/renderer-webgpu/e2e/fixtures/harness.ts',
            'packages/calibration/results/2026-10-01-w43-g0-declaration/memo-f/MEMO.md'):
    paths.add(ROOT / rel)
paths.update((ROOT / 'packages/calibration/profiles').glob('apple-macos-*-1x-*-standard*.json'))
sources = [dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for p in sorted(paths)]
part1 = dict(schema='w49b-declaration-1', current='b2d074d2df24-940384c06f73',
    scope='G0 inert operators, prospective identifying ladders and native declaration; no fit/publication/native capture',
    sources=sources,
    families={
        'D': dict(leaves=['tintAlphaSpanMax', 'tintAlphaSpanMax2x'], identity=0,
            law='Resolve zero anchors to their own scatter tops before DPR interpolation; alpha far smoothstep has independent top; exact old path when resolved tops agree.',
            targets='Six active thick entries; the scatter-top companion can also reach thin/mid controls.'),
        'W': dict(leaves=['sizeHeavySecondSigmaFar1x', 'sizeHeavySecondSigmaFar2x'], identity=0,
            law='secondary=G(sigma2)+H(span)*(G(sigma2+delta)-G(sigma2)); H is existing scatter far smoothstep; then apply existing signed share.',
            targets='Three inactive impulse entries, with prior coarse repairs protected; fourth inactive target is withheld checker32-lg2x.'),
        'S': dict(leaves=['backdropCaptureScale'], identity=1,
            law='Uniform source resolution multiplier applied AFTER the policy cap, BEFORE analysis/body/scatter. Existing import resamples; physical blur units retained.',
            rungs=[1, 0.5, 0.25, 0.125], firstLiveRung=0.5,
            nativeFact='Memo F bd.scale=.5 on every measured glass0.25 shape, both poses/schemes/scales; reconstruction kernel is unidentified.',
            targets='Same target/protection accounting as W and D; additionally read ml/lg impulse halo support and deep mean. No claim of an attested span-dependent scale at0.25.'),
    },
    css=dict(D='mirrored per surface', W='declined with absent second tap',
             S='declined: backdrop-filter exposes no capture-resolution control; no alpha/blur surrogate'),
    predictions='batches/identification.json; every point registered before any ladder render',
    nativeBed='native-bed/bed-declaration.json; X5 not lifted by this declaration',
    separatingRule={
        'D':'At least one combined D rung repairs the six active historical entries at both scales; every affected visible gate constraint passes.',
        'W':'At least one W rung repairs all three inactive impulse entries; visible W49a repairs remain repaired; every affected visible gate constraint passes.',
        'S':'Apply the same per-target and protected-cell intersections to its uniform rungs; halo resemblance alone is not separation.',
        'protectedFive':'No absolute error growth against current (0, not B), regardless of direction or overshoot.',
        'general':'No absolute-error growth >B against current, no new >3B; existing historical repairs retain <=B.',
        'withheld':'Four standing constraints are UNMEASURED: checker32-lg-inactive1x/2x, photo-lg-inactive1x/2x. They are predicted before the single frozen exposure, never rendered in G0.',
        'preference':'When S and W both clear the same separation/protection clauses, S wins (DL2).',
        'outcome':'PASS-to-fit only with a separating route for every reachable binding target, named family/domain, and withheld predictions. Otherwise STOP-at-finding; finite ladder failure is not global infeasibility.',
    })
write('declaration.json', part1)
part2 = dict(schema='w49b-fit-declaration-1', partOneSha256=sha(HERE / 'declaration.json'),
    sources=sources, noPostGateAmendment=True,
    onFailure='NEITHER: no seal, no publication, no re-selection',
    rule={
        'bindingTen':'Historical absolute-error growth <=B against each registry reference, including the frozen exposure.',
        'priorFive':'Historical absolute-error growth <=B; do not silently reauthorise a removed regression.',
        'protectedFive':'Remain listed; no absolute-error growth against W49a current; historical targets retained independently but not newly required <=B.',
        'allCells':'Every154 darkWebGPU T1 cell retained. Regression T1-low on T, fidelity T1-fine on T. Current growth <=B including overshoots; no new >3B.',
        'achievedStrata':'Retain W48 C-rest halvings at1x/2x and F-inactive halving1x vsd0219; P1x/2x and F-inactive2x stay named misses, with no aggregate worsening.',
        'otherRows':'Current owner M2/L1/E2/coherence contracts plus X75/X76; inspect native/current/candidate pixels and report any new visible gap.',
        'registry':'All20 entries remain independently discoverable when authorisations are removed. Fifteen enforced historical repairs; five protected historical targets retain their authorisations. Empty-exception proof is a synthetic future fully repaired case.',
        'exposure':'New native blind holdout if X5 capture occurs; otherwise read10 is a non-blind prediction check. One frozen point once; failure stops.',
    },
    fitDomain={
        'admission':'Only families meeting part1 separation are admitted; no new operator or conditioning statistic.',
        'D':{'active.tintAlphaSpanMax':[160], 'active.tintAlphaSpanMax2x':[160],
             'active.sizeScatterSpanMax':[160,192,256], 'active.sizeScatterSpanMax2x':[160,192,256]},
        'W':{'receded.tintAlphaSpanMax':[160], 'receded.tintAlphaSpanMax2x':[160],
             'receded.sizeHeavySecondSigmaFar1x':[0,3,4,5], 'receded.sizeHeavySecondSigmaFar2x':[0,3,4,5],
             'receded.tintAlphaFar1x':[0.09,0.10], 'receded.tintAlphaFar2x':[0.09,0.10],
             'receded.sizeScatterSpanMax':[128,160], 'receded.sizeScatterSpanMax2x':[128,160]},
        'S':{'active.backdropCaptureScale':[1,0.5,0.25,0.125],
             'receded.backdropCaptureScale':[1,0.5,0.25,0.125]},
        'held':'Every other leaf stays W49a current; receded inherited holds explicit. Finite values only; no interpolation or added values after reading.'},
    selection={
        'eligible':'Intersection of every binding clause at both scales; never impute withheld cells during fitting.',
        'primary':'Minimum median abs(log((candidate+epsilon)/(native+epsilon))) over predeclared gate T1 cells; epsilon is that cell\'s one-code linear-light tolerance. Use T1-fine on T.',
        'tie':'Within median(log(1+B/(native+epsilon))) of minimum, choose minimum squared Euclidean coefficient distance from current, each axis divided by its declared max-min range; fixed axes contribute zero. Then lexicographic candidate id.',
        'familyTie':'When S and W meet the same separation and landing clauses, prefer S before numerical ranking (DL2).',
        'freeze':'One point, explicit per-cell predictions before exposure; no post-gate amendment or re-selection.'})
write('fit-declaration.json', part2)
print(f'assembled two unsealed parts, {len(sources)} source pins each')
