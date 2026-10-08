#!/usr/bin/env python3
"""Assemble unsealed W50 parts on the combined tree; never capture, measure or seal."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def assemble():
    if any((HERE / f'{p}.sha256').exists() for p in ('declaration', 'fit-declaration')):
        raise ValueError('Existing seal: assembly is closed')
    spec = importlib.util.spec_from_file_location('w50_declare', HERE / 'declare.py')
    D = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(D)
    required = ['bed/manifest.json', 'bed/scenes-w50.json', 'bed/sitting-g1.json', 'bed/timing.json',
                'references.json', 'rulings.txt']
    for name in required:
        if not (HERE / name).is_file():
            raise ValueError(f'Missing assembly input: {name}')
    excluded = {'declaration.json', 'fit-declaration.json', 'declaration.sha256',
                'fit-declaration.sha256', 'pre-fit-evidence.json', 'pre-fit-evidence.sha256'}
    paths = {p for p in HERE.rglob('*') if p.is_file() and p.name not in excluded and
             '__pycache__' not in p.parts and p.suffix != '.pyc' and not p.name.startswith('grant-check')}
    paths.update((ROOT / 'packages/renderer-webgpu/src').rglob('*.ts'))
    paths.update((ROOT / 'packages/platform-web/src').rglob('*.ts'))
    paths.update((ROOT / 'packages/calibration/scripts').rglob('*.ts'))
    paths.update((ROOT / 'packages/calibration/src').rglob('*.ts'))
    paths.update((ROOT / 'packages/calibration/profiles').glob('apple-macos-*-1x-*-standard*.json'))
    for rel in ['packages/calibration/test/tier-coherence.test.ts',
                'packages/calibration/test/adopted-thresholds.test.ts',
                'apps/reference-apple/scenes.json',
                'packages/calibration/results/2026-10-02-w43-g3-refit/stage/census.py']:
        paths.add(ROOT / rel)
    sources = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in sorted(paths)]
    family = {
        'gate': 'lowEndStrength', 'identity': 0,
        'leaves': ['lowEnd44', 'lowEnd96', 'lowEnd160'],
        'inputCodes': [0, 8, 28, 40], 'spanRows': [44, 96, 160],
        'ordinates': 'Encoded neutral output normalized to [0,1]; four independent dark endpoints',
        'interpolation': 'Piecewise linear input and span; hold outer span rows; no DPR coefficients',
        'join': {'inputCode': 64, 'free': False,
                 'ordinate': 'encode(OLD tone_response(64/255, actual span, endpoint)); never interpolate joins',
                 'bridge': 'Linear encoded output from measured40 at actual span to old-law64 at actual span',
                 'atAndAbove64': 'Exact old arithmetic'},
        'authority': 'Full below64 only where old tone solve is eligible; preserve strength folds and '
                     'no-tone/no-sample, alpha, zero/full collapse and policy stand-downs',
        'failure': 'Any negative pre-clamp neutral channel, fixed64 below measured40, dense drawdown '
                   'failure or measured gate failure is NEITHER, not a clamping success',
        'held': 'Existing group/source/silhouette arguments, alpha, scatter, chroma, composition and '
                'all other material leaves remain current',
        'css': 'Same target and authority per surface before existing projection; no new layer/tap; '
               'no silent CSS decline',
    }
    part1 = {'schema': 'w50-declaration-1', 'scope': ['dark.glass0.25', 'dark.glass0.5'],
        'sources': sources, 'rulings': 'rulings.txt', 'family': family,
        'identity': 'One identity-table gate-group; all ten digests and all goldens identical at gate0; '
                    'light and26.5 remain at gate0 after fit',
        'references': 'references.json',
        'native': {'manifest': 'bed/manifest.json', 'sitting': 'bed/sitting-g1.json',
                   'timing': 'bed/timing.json', 'bundle': '/Users/new/vitrea-w39/side/VitreaReference.app',
                   'admission': 'Positive non-interactive grant check before any launch; unchanged side bundle; '
                                'original bundle never rebuilt; classifying census and W43 protections'},
        'split': {'coreCalibration': [0,2,4,8,28,40,64], 'coreValidation': [1,3,5,6,12],
                  'coreBlind': [7,20], 'span128': 'validation', 'span224': 'blind',
                  'sparseImpulse': {'96':'calibration','160':'validation','224':'blind'},
                  'lowChecker': 'blind at all spans',
                  'dependencies': 'Exclusive blind no-glass references guarded; shared calibration '
                                  'references copied by role; archive by hash before fitting'},
        'bar': {'formula': 'max(0.5 code, half largest admitted run-to-run separation)',
                'noiseStop': 'Native spread >1 code in required population stops; no extra runs without ruling'},
        'predictions': {'kind': 'Analytical scalar proxies only, NOT rendered or fitted results',
            'receded025_ml_lg': [19.90,20.38], 'receded05_ml_lg': [20.16,20.28],
            'active025_range': [31.85,32.33],
            'caveat': '[28,28,30] scalar proxy is not measured neutral28; residual blur/rim/tint omitted'},
        'contracts': {'native': 'bed/execution-contract.json', 'web': 'audit/execution-contract.json',
                      'sidecarsRequired': True, 'rendererInternalBinding': True,
                      'closure': 'Dry-exercised transitive imports, checked again in the live process'},
        'sealPhases': 'Operational parts before new native pixels; append-only pre-fit evidence binds '
                      'known reference identities, complete exposed readings and archive-only blind identities '
                      'before fitting; fixed batches before each authorised rendering phase'}
    write('declaration.json', part1)
    part2 = {'schema': 'w50-fit-declaration-1', 'partOneSha256': sha(HERE / 'declaration.json'),
        'sources': sources, 'noPostGateAmendment': True, 'onFailure': D.FAILURE,
        'conditionalX41': D.X41_SCOPE, 'references': 'references.json',
        'requiredEvidence': ['nativeArchive', 'repeatBar', 'referenceCompletion', 'dark05Bands',
            'active05ScratchBaselines', 'identityDigestsGoldens', 'numericalRehearsal',
            'shaderCpuAgreement', 'negativeNeutralDiagnostic', 'newBedRendererAdapter',
            'executionClosure', 'independentReview'],
        'candidateDomain': {'strength': 1, 'endpoints': ['active.dark.0.25','receded.dark.0.25',
            'active.dark.0.5','receded.dark.0.5'], 'rows': [44,96,160], 'inputCodes': [0,8,28,40],
            'ordinateRange': [0,1], 'rankingNormalisationRange': 1,
            'constraint': 'Finite nondecreasing row ordinates; fixed64 must not be lower at any tested span; '
                          'no new knots, DPR leaves, spatial argument or changed support',
            'fitData': 'Native calibration/validation only, within declared family; no blind or historical '
                       'prediction-check exploration', 'batch': 'Frozen content-addressed runs before first candidate gate'},
        'landing': {
            'lowLevel': 'Every new uniform input0–40: per-channel deep8 AND central8 median error <=max(1 code,2*bar)',
            'monotonicity': {'inputCodes': [0,64], 'stepCode': 1/64, 'integerSpans': [32,224],
                'domain': 'Both positions/poses/scales, composed pre-quantised CPU uniform response',
                'maxRunningDrawdownCode': 0.0001, 'shaderCpuMaxErrorCode': 0.001},
            'structured': 'Untinted impulse ml/lg at both scales/positions: deep8/far24 encoded-luma mean '
                'AND median within max(1,2*bar); no empty/tiny support. All untinted single-shape dark-solid '
                'per-channel path deep median, including empty detected L1 masks. New structured cells '
                'level clauses AND <=B T1 error growth against own pre-fit current; report absolute error.',
            'dark025T1': 'Every current T1 cell <=B error growth against W49a current; T fine fidelity, '
                'T low regression. Historical entries retain own references and max(B,current historical '
                'growth) caps; repaired entries remain <=B.',
            'aggregates': 'Keep W48 C-rest halvings at1x/2x and F-inactive halving at1x; named P and2x '
                'F-inactive misses cannot worsen against current.',
            'dark05T1': 'Same <=B growth against own frozen current, own pre-fit bands/B; report absolute '
                'misses; adopt regression stop only, not invented prior adoption.',
            'ownerAxes': 'M1/M2/C1/X1/L1/E2/coherence/X75/X76 retain applicable owner contracts and '
                'exclusions; mid-dark69, photo/checkers/text/tinted/pressed/composite/a11y remain in gate.',
            'css': 'Same law; no low-end level-error growth beyond1 code; existing coherence passes or stop.',
            'visual': 'Native/current/candidate impulse, dark-solid, near-black and demo/harness at1x/2x; '
                'new visible contour, plateau, cast or texture defect is a parent stop.',
            'intersection': 'Failure at either position, pose or scale is NEITHER; no exception landing'},
        'selection': ['Minimum worst exposed low-end level error', 'Minimum mean absolute low-end level error',
                      'Minimum squared normalized coefficient distance from current over range[0,1]',
                      'Lexicographic candidate id'],
        'exposure': 'Freeze one passing candidate. New blind and historical exposed prediction checks '
                    'read once; must pass independently. No re-fit, re-selection, changed reference or amendment.',
        'retirement': {'dark025': 'web-captures-superseded/b2d074d2df24-940384c06f73/',
                       'preserveW48': 'web-captures-superseded/b2d074d2df24/',
                       'identity': 'Every retired tree bound by full active/receded pair; old aliases unchanged'}}
    write('fit-declaration.json', part2)
    print(f'Assembled two UNSEALED parts with {len(sources)} source pins; no execution authorised')


if __name__ == '__main__':
    assemble()
