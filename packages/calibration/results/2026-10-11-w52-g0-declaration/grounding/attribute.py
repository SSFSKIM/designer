#!/usr/bin/env python3
"""Replay exposed W51 impulse attribution, offline; never invoke a renderer or judge.

Run with /Users/new/vitrea-w49/py/bin/python -I -B attribute.py [--check].
Historical TS helpers are extracted from SOURCE_REV into a temporary directory here,
not imported from the changing W52 runtime. Every external input is authenticated
before decoding. The output is a mechanism hypothesis with residuals, not a material
candidate, counterfactual render, gate value, or new fidelity verdict.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import tempfile

import numpy as np
from PIL import Image, __version__ as pillow_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE_REV = 'b60d63c599c3e7ca784321b14dd23c8b613ddc8a'
REPORT = ('packages/calibration/results/2026-10-10-w51-regate/evidence/'
          'gate-dl6-complete/report.json')
REPORT_SHA = 'af06fec2d652264e3e44c52d483b12dbf8b64a0de4206dba7bb9b1db0edaf128'
PROJECTION = ('packages/calibration/results/2026-10-10-w51-regate/evidence/'
              'gate-dl6/committed-clause-projection.json')
STAT = 'T1-full-silhouette'
SHAPES = ('capsule-button', 'rrect-sm', 'rrect-ml', 'rrect-lg')
INPUTS = {}
SOURCES = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def source(path):
    data = git('show', f'{SOURCE_REV}:{path}')
    SOURCES[path] = {'sha256': sha(data), 'bytes': len(data)}
    return data


def checked(pin, role):
    path = Path(pin['path'])
    if not path.is_absolute():
        path = ROOT / path
    data = path.read_bytes()
    actual = sha(data)
    if actual != pin['sha256']:
        raise ValueError(f'{role}: input changed: {path}: {actual} != {pin["sha256"]}')
    record = INPUTS.setdefault(str(path), {'sha256': actual, 'bytes': len(data), 'roles': []})
    if role not in record['roles']:
        record['roles'].append(role)
    return data


def load(pin, role):
    return json.loads(checked(pin, role))


def read_image(pin, role):
    with Image.open(io.BytesIO(checked(pin, role))) as image:
        return np.asarray(image.convert('RGB'), dtype=np.float64) / 255


def decode(x):
    return np.where(x <= .04045, x / 12.92, ((x + .055) / 1.055) ** 2.4)


def encode(x):
    x = np.maximum(x, 0)
    return np.where(x <= .0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - .055)


def luma(image):
    channels = decode(image)
    return channels[..., 0] * .2126 + channels[..., 1] * .7152 + channels[..., 2] * .0722


def chroma(image):
    r, g, b = np.moveaxis(decode(image), -1, 0)
    l = np.cbrt(.4122214708 * r + .5363325363 * g + .0514459929 * b)
    m = np.cbrt(.2119034982 * r + .6806995451 * g + .1073969566 * b)
    s = np.cbrt(.0883024619 * r + .2817188376 * g + .6299787005 * b)
    return np.stack([1.9779984951 * l - 2.428592205 * m + .4505937099 * s,
                     .0259040371 * l + .7827717662 * m - .808675766 * s], axis=-1)


def stats(values):
    """Retain both NumPy centered variance and production's sequential identity."""
    total = 0.0
    squares = 0.0
    for item in values:
        value = float(item)
        total += value
        squares += value * value
    mean = total / len(values)
    return {'count': len(values), 'mean': mean, 'numpyStdDev': float(np.std(values)),
            'sequentialStdDev': max(0.0, squares / len(values) - mean * mean) ** .5}


def field(g, x, y):
    """Float64 transcription of the historical continuous-corner field."""
    qx = np.abs(x) - g['halfW'] + g['reach']
    qy = np.abs(y) - g['halfH'] + g['reach']
    cx, cy = np.maximum(qx, 0), np.maximum(qy, 0)
    r2 = np.maximum(cx * cx + cy * cy, 1e-20)
    rho = np.sqrt(r2)
    s = 2 * cx * cy / r2
    c = (cx * cx - cy * cy) / r2
    radius = g['reach'] * (1 + s * s * sum(v * s ** i for i, v in enumerate(g['k'])))
    derivative = g['reach'] * s * sum((i + 2) * v * s ** i
                                     for i, v in enumerate(g['k'])) * 2 * c
    return ((rho + np.minimum(np.maximum(qx, qy), 0) - radius) /
            np.sqrt(1 + (derivative / np.maximum(rho, radius)) ** 2))


ORACLE = r'''
import { readFileSync } from 'node:fs';
import * as m from './packages/renderer-webgpu/src/material.ts';
import { resolveShape, fieldParams } from './packages/geometry/src/shape.ts';
const rows = JSON.parse(readFileSync(0, 'utf8'));
console.log(JSON.stringify(rows.map(r => {
  const p = m.withMaterialOverrides(m.DEFAULT_MATERIAL_PROFILE, r.patch);
  const old = m.withMaterialOverrides(p, { lowEndStrength: 0 });
  const span = Math.min(...r.component.size);
  const k = m.sizeThickness(span, p);
  const alpha = m.sizeOcclusionAlpha(
    m.spanGradedTintAlpha(p.optics.regular.tintAlpha, span, p, r.dpr), span, p);
  // These exposed impulse source means are in the linear arm of sRGB encoding.
  if (r.tone.level > .0031308) throw new Error('Impulse encoding precondition changed');
  const encodedInput = r.tone.level * 12.92;
  const far = m.sizeToneLevelFar(span, p, r.dpr);
  const collapse = m.backdropToneAdaptation(r.tone.level, k, p);
  const candidateAuthority = m.backdropToneSolveWeight(encodedInput, p);
  if (collapse !== 0 || candidateAuthority !== 1)
    throw new Error('The abbreviated DC solve needs zero collapse and full chart authority');
  const neutral = p.optics.regular.tint[0];
  if (!p.optics.regular.tint.every(v => v === neutral)) throw new Error('Not neutral');
  const nominal = (1 - alpha) * r.tone.linearLuminance + alpha * neutral;
  const oldTarget = m.backdropToneResponse(encodedInput, k, old, far, span);
  const authority = m.backdropToneSolveWeight(encodedInput, old);
  const oldNeutral = neutral + authority * (oldTarget - nominal) / alpha;
  const newTarget = m.backdropToneResponse(encodedInput, k, p, far, span);
  const newNeutral = (newTarget - (1 - alpha) * r.tone.linearLuminance) / alpha;
  // On this population neither solve clamps. Refuse rather than silently extend
  // the abbreviated DC formula to cells needing the shader's alpha correction.
  if (oldNeutral < 0 || oldNeutral > 1 || newNeutral < 0 || newNeutral > 1)
    throw new Error('DC reconstruction needs clamp/alpha branch');
  const oldDC = nominal + authority * (oldTarget - nominal);
  const shape = r.component.kind === 'capsule'
    ? { family: 'capsule', center: [0, 0], size: r.component.size }
    : { family: 'fixed-rounded-rect', center: [0, 0], size: r.component.size,
        radii: r.component.radius, profile: 'continuous' };
  return { delta: newTarget - oldDC, oldDC, newTarget, oldTarget, nominal,
    oldNeutral, newNeutral, alpha, authority, candidateAuthority, collapse, encodedInput, k,
    geom: fieldParams(resolveShape(shape)), optics: p.optics.regular,
    rimWidth: m.rimWidthAtScale(p.optics.regular, r.dpr), axis: p.rimLitAxis,
    lensSizeGainMax: p.lensSizeGainMax, sizeShadowGainMax: p.sizeShadowGainMax };
})));
'''


def oracle(rows):
    """Execute only pure helpers from pinned historical blobs; no live imports."""
    roots = ['packages/geometry/src', 'packages/policy/src']
    files = git('ls-tree', '-r', '--name-only', SOURCE_REV, '--', *roots).decode().splitlines()
    files = [p for p in files if p.endswith('.ts')]
    files += ['packages/renderer-webgpu/src/material.ts', 'packages/renderer-webgpu/src/color.ts']
    with tempfile.TemporaryDirectory(prefix='.oracle-', dir=HERE) as name:
        directory = Path(name)
        for path in files:
            data = source(path)
            if path.endswith('/material.ts'):
                data = data.replace(b'"@vitrea/policy"', b'"../../policy/src/index.ts"')
            target = directory / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (directory / 'package.json').write_text('{"type":"module"}\n')
        entry = directory / 'oracle.mjs'
        entry.write_text(ORACLE)
        tsx = ROOT / 'node_modules/.pnpm/tsx@4.20.6/node_modules/tsx/dist/esm/index.mjs'
        return json.loads(subprocess.check_output(
            ['node', '--import', str(tsx), str(entry)],
            input=json.dumps(rows).encode(), cwd=ROOT))


def selected_rows(report):
    selected = [r for r in report['cells'] if r['renderer'] == 'webgpu' and
                r['scene'] in [f'impulse__{s}__rest' for s in SHAPES] and STAT in r['readings']]
    expected = {(f'apple-macos-27.0-{scale}x-dark-standard-glass{position}',
                 f'impulse__{shape}__rest') for scale in (1, 2)
                for position in (0.25, 0.5) for shape in SHAPES}
    assert {(r['profile'], r['scene']) for r in selected} == expected and len(selected) == 16
    return sorted(selected, key=lambda r: (r['profile'], r['scene']))


def input_rows(report):
    components = json.loads(source('apps/reference-apple/scenes.json'))['components']
    rows = []
    for r in selected_rows(report):
        q = r['readings'][STAT]
        e = q['evidence']['candidate']
        measurement = load(r['evidence'], 'exposed keyed measurement')['row']
        evidence = measurement['readings'][STAT]['evidence']
        page = load(e['report'], 'exposed capture page metadata')['page']
        assert page['sceneId'] == r['scene'] and page['tint'] is None
        assert page['windowActivation'] == 'active' and page['colorScheme'] == 'dark'
        assert len(page['groups']) == 1
        group = page['groups'][0]
        assert group['state']['samplingBackend'] == 'gpu-texture'
        current = evidence['current']
        current_pin = current.get('originalCapture', current.get('capture'))
        assert current_pin is not None
        native_pin = e['originalNative']
        native = evidence['native']
        assert native.get('originalCapture', native.get('native')) == native_pin
        # Original record digests and image-byte digests have different domains.
        assert current['numericIdentity'] == q['evidence']['current']['numericIdentity']
        endpoint = e['material']['drawnEndpoint']
        document = load(endpoint, 'historical candidate active document')
        rows.append({'profile': r['profile'], 'scene': r['scene'], 'reading': q,
                     'candidateEvidence': e, 'measurementPin': r['evidence'],
                     'currentPin': current_pin, 'nativePin': native_pin,
                     'currentIdentityKind': current['captureIdentity']['kind'],
                     'nativeIdentityKind': native['captureIdentity']['kind'],
                     'tone': group['backdropTone'], 'dpr': page['devicePixelRatio'],
                     'position': page['material']['glassTintAmount'],
                     'component': components[r['scene'].split('__')[1]],
                     'patch': document['patch']})
    return rows


def evaluate(r, g):
    e, q = r['candidateEvidence'], r['reading']
    native = read_image(r['nativePin'], 'native PNG')
    background = read_image(e['originalBackground'], 'background PNG')
    current = read_image(r['currentPin'], 'original current PNG')
    candidate = read_image(e['capture'], 'exposed candidate PNG')
    assert native.shape == current.shape == candidate.shape == background.shape
    assert np.array_equal(background[..., 0], background[..., 1])
    assert np.array_equal(background[..., 1], background[..., 2])
    scale = r['dpr']
    assert native.shape[:2] == (200 * scale, 320 * scale)
    w, h = r['component']['size']
    radius = r['component'].get('radius', min(w, h) / 2)
    yy, xx = np.indices(native.shape[:2])
    x, y = (xx + .5) / scale - 160, (yy + .5) / scale - 100
    qx, qy = np.abs(x) - (w / 2 - radius), np.abs(y) - (h / 2 - radius)
    sd = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - radius
    declared = sd <= 0
    # No hole fill or erosion. Native quantization includes a few nonneutral pixels;
    # compute the chroma arm rather than assuming it cannot select extra support.
    luma_arm = np.abs(luma(native) - luma(background)) >= .02
    chroma_delta = np.linalg.norm(chroma(native) - chroma(background), axis=-1)
    chroma_only = declared & ~luma_arm & (chroma_delta >= .03)
    mask = declared & (luma_arm | (chroma_delta >= .03))
    assert not np.any(chroma_only), 'Analyst luminance-only replay no longer equivalent'
    d = field(g['geom'], x, y)
    epsilon = 1e-4
    gx = (field(g['geom'], x + epsilon, y) - field(g['geom'], x - epsilon, y)) / (2 * epsilon)
    gy = (field(g['geom'], x, y + epsilon) - field(g['geom'], x, y - epsilon)) / (2 * epsilon)
    norm = np.maximum(np.hypot(gx, gy), 1e-6)
    gx, gy = gx / norm, gy / norm
    coverage = np.clip(.5 - d * scale, 0, 1)
    inside = coverage > 0
    partial = inside & (coverage < 1)
    assert np.all(background[partial] == 0), 'Encoded unpremultiply assumes black edge backdrop'
    depth = min(8 * (1 + (g['lensSizeGainMax'] - 1) * g['k']), min(w, h) / 2)
    optics = g['optics']
    shadow = 1 - ((1 - np.clip(-d / depth, 0, 1)) ** 2 * optics['shadowDepth'] *
                  (1 + (g['sizeShadowGainMax'] - 1) * g['k']) * optics['shadowAlpha'])
    rw = np.clip(1 - np.abs(d) / g['rimWidth'], 0, 1) ** 2
    lit = np.maximum(np.abs(gx * g['axis'][0] + gy * g['axis'][1]) * 1.4142135,
                     1e-6) ** optics['rimLitExponent']
    along = np.maximum(1 + optics['rimAlongSideSlope'] * g['k'] *
                       np.clip(x * y / (w * h / 4), -1, 1), 0)
    rim = optics['rimLevelGain'] * rw * lit * along
    reconstructed = decode(current / np.maximum(coverage[..., None], 1e-6))
    values = {side: luma(image) for side, image in
              [('native', native), ('current', current), ('candidate', candidate)]}
    replay = {}
    for side, array in values.items():
        replay[side] = stats(array[mask])
        replay[side]['report'] = q[side]
        replay[side]['numpyMinusReport'] = replay[side]['numpyStdDev'] - q[side]
        replay[side]['sequentialMinusReport'] = replay[side]['sequentialStdDev'] - q[side]
    current_sd = replay['current']['numpyStdDev']
    candidate_sd = replay['candidate']['numpyStdDev']
    actual_shift = candidate_sd - current_sd
    ablations = {}
    for name, factor in [('dc', np.ones_like(d)), ('shadow', shadow),
                         ('rim', 1 + rim), ('both', shadow * (1 + rim))]:
        predicted = current.copy()
        linear = reconstructed + (g['delta'] * factor)[..., None]
        encoded = coverage[..., None] * encode(linear)
        predicted[inside] = np.round(np.clip(encoded[inside], 0, 1) * 255) / 255
        predicted_luma = luma(predicted)
        sd_predicted = float(np.std(predicted_luma[mask]))
        ablations[name] = {
            'stdDev': sd_predicted, 'shiftFromCurrent': sd_predicted - current_sd,
            'actualMinusPredicted': candidate_sd - sd_predicted,
            'explainedShiftFraction': (sd_predicted - current_sd) / actual_shift,
            'directionMatches': bool(np.sign(sd_predicted - current_sd) == np.sign(actual_shift)),
            'pixelLinearLumaRMSE': float(np.sqrt(np.mean(
                (predicted_luma[mask] - values['candidate'][mask]) ** 2))),
            'minimumPreOutputLinearOnMask': float(np.min(linear[mask])),
        }
    # Read only the explicitly named retained canonical alternative. A scalar
    # match is never used to authenticate it or to choose the primary input.
    alternative = (Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures') /
                   r['profile'] / r['scene'] / (r['scene'] + '__webgpu.png'))
    alternate_record = {'path': str(alternative), 'exists': alternative.is_file()}
    if alternative.is_file():
        data = alternative.read_bytes()
        alternate_record.update(sha256=sha(data), bytesMatchOriginal=sha(data) == r['currentPin']['sha256'])
        # If unequal, retain bytes identity without decoding an unpinned substitute.
        INPUTS[str(alternative)] = {'sha256': sha(data), 'bytes': len(data),
                                    'roles': ['retained canonical current byte comparison only']}
    masks = {'declared': declared, 'production': mask,
             'productionDeepGt8CssPx': mask & (d < -8),
             'declaredDeepGt8CssPx': declared & (d < -8)}
    support = {}
    for name, selected in masks.items():
        support[name] = {'count': int(np.count_nonzero(selected)),
                         'maskSha256': sha(selected.astype(np.uint8).tobytes())}
        if np.any(selected):
            support[name]['scalars'] = {side: stats(array[selected]) for side, array in values.items()}
    # The twelve cells whose error grew in the requested attribution population.
    error_growth = abs(q['candidate'] - q['native']) - abs(q['current'] - q['native'])
    return {'key': [r['profile'], 'webgpu', r['scene'], STAT],
            'position': r['position'], 'scale': scale, 'sourceModel': g,
            'sourceTone': r['tone'], 'productionMask': support,
            'supportNotes': {'deepDistance': 'historical renderer continuous SDF, CSS px',
                             'native32Linear': float(decode(np.array(32 / 255))),
                             'maskThreshold': .02, 'chromaThreshold': .03,
                             'additionalChromaArmPixels': int(np.count_nonzero(chroma_only)),
                             'maximumChromaDeltaInDeclaredRegion': float(np.max(chroma_delta[declared])),
                             'maskIsErodedOrFilled': False},
            'replay': replay, 'actualShift': actual_shift, 'reportNativeErrorGrowth': error_growth,
            'losingRequestedCell': error_growth > 0,
            'ablations': ablations,
            'provenance': {'currentPng': r['currentPin'], 'nativePng': r['nativePin'],
                           'candidatePng': e['capture'], 'measurement': r['measurementPin'],
                           'currentIdentityKind': r['currentIdentityKind'],
                           'nativeIdentityKind': r['nativeIdentityKind'],
                           'currentNumericIdentity': q['evidence']['current']['numericIdentity'],
                           'nativeNumericIdentity': q['evidence']['native']['numericIdentity'],
                           'retainedCanonicalAlternative': alternate_record}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='recompute and compare, without output writes')
    args = parser.parse_args()
    report = load({'path': REPORT, 'sha256': REPORT_SHA}, 'committed exposed W51 report')
    projection_bytes = source(PROJECTION)
    projection = load({'path': PROJECTION, 'sha256': sha(projection_bytes)}, 'exposed scalar projection')
    assert projection['sourceReport']['sha256'] == REPORT_SHA
    for path in ['packages/renderer-webgpu/src/wgsl/optics.ts',
                 'packages/calibration/cli/measure.ts', 'packages/calibration/src/component-region.ts',
                 'packages/calibration/src/silhouette.ts', 'packages/calibration/src/metrics/material.ts',
                 'packages/calibration/src/image.ts', 'packages/calibration/src/color.ts',
                 'packages/platform-web/src/host.ts',
                 'packages/calibration/results/2026-10-08-w50-g1-fit/measurement/projection.py',
                 'pnpm-lock.yaml']:
        source(path)
    rows = input_rows(report)
    models = oracle(rows)
    evidence = [evaluate(row, model) for row, model in zip(rows, models, strict=True)]
    losing = [row for row in evidence if row['losingRequestedCell']]
    assert len(losing) == 12
    assert all(row['ablations']['both']['directionMatches'] for row in evidence)
    replay_error = max(abs(row['replay'][side]['numpyMinusReport'])
                       for row in evidence for side in ('native', 'current', 'candidate'))
    assert replay_error < 1e-12
    summary = {'cells': len(evidence), 'losingRequestedCells': len(losing),
               'correctPredictedDirections': sum(row['ablations']['both']['directionMatches']
                                                for row in evidence),
               'losingExplainedFractionRange': [min(row['ablations']['both']['explainedShiftFraction']
                                                    for row in losing),
                                               max(row['ablations']['both']['explainedShiftFraction']
                                                    for row in losing)],
               'losingMaxAbsoluteSigmaResidual': max(abs(row['ablations']['both']['actualMinusPredicted'])
                                                     for row in losing),
               'maximumNativeCurrentCandidateReplayDiscrepancy': replay_error}
    result = {'schema': 'w52-exposed-impulse-source-attribution-1',
              'sourceRevision': SOURCE_REV, 'summary': summary,
              'meaning': 'Offline reconstruction of W51, not a rendered W52 candidate or acceptance result.',
              'formula': 'delta * shadowKeep * (1 + rimLevelGain * squaredRimWeight * lit * along)',
              'ablations': {'dc': 'delta only', 'shadow': 'delta * shadowKeep',
                            'rim': 'delta * (1 + rimLevelGain * squaredRimWeight * lit * along)',
                            'both': 'delta * shadowKeep * (1 + rimLevelGain * squaredRimWeight * lit * along)'},
              'limitations': [
                  'The group/source DC solve is source-owned; no coefficient is fitted to candidate pixels.',
                  'The predicted image starts from an 8-bit current capture, not the unrounded shader buffer.',
                  'The oracle uses float64 geometry, finite-difference normals and NumPy ties-to-even rounding; '
                  'WGSL float32, pixel coverage and browser quantization are not replicated bit-exactly.',
                  'Coverage reconstruction assumes a black edge backdrop; this is asserted for every cell.',
                  'The mask is the production un-eroded native luminance-delta mask inside the declared '
                  'circular rounded rectangle; deep counts use the renderer continuous SDF, not mask erosion.',
                  'The dark32 body is below the mask threshold. Full-silhouette T1 is often rim-heavy and '
                  'is not an isolated deep-body transfer function.',
                  'Current/native frozen-reference-record numeric identities are JSON record binders, not '
                  'PNG byte hashes. OriginalCapture pins authenticate those images separately.',
                  'Residuals remain unexplained; matching directions and rough magnitude do not prove '
                  'a W52 operator passes per-cell, aggregate, tint, CSS or exposure contracts.'
              ], 'rows': evidence}
    pins = {'schema': 'w52-grounding-input-pins-1', 'sourceRevision': SOURCE_REV,
            'scriptSha256': sha(Path(__file__).read_bytes()),
            'sourceBlobs': dict(sorted(SOURCES.items())), 'inputs': dict(sorted(INPUTS.items())),
            'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                            'pillow': pillow_version,
                            'node': subprocess.check_output(['node', '--version']).decode().strip(),
                            'tsx': '4.20.6'},
            'reproduce': '/Users/new/vitrea-w49/py/bin/python -I -B ' + str(Path(__file__)) + ' --check'}
    for filename, value in [('attribution.json', result), ('pins.json', pins)]:
        encoded = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
        path = HERE / filename
        if args.check:
            assert path.read_bytes() == encoded, f'{filename}: deterministic replay differs'
        else:
            path.write_bytes(encoded)
    print(json.dumps(summary, indent=2))
    print('independent offline replay: ' + ('matches committed artifacts' if args.check else 'written'))


if __name__ == '__main__':
    main()
