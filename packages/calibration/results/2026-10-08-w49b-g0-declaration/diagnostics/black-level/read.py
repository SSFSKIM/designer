"""Read existing dark solid/impulse pixels only; no capture, fit, or adopted statistic change.

Run with the pinned numerical environment and Python isolation:
  /Users/new/vitrea-w49/py/bin/python -I <absolute-path-to-this-file>
  /Users/new/vitrea-w49/py/bin/python -I <absolute-path-to-this-file> --check

The geometric deep support is W44's signed distance <= -8 CSS px. The -24 CSS px
core and distance-to-impulse restrictions are diagnostics, not replacements for T1/L1.
PNG RGB bytes are read exactly like W44/pngjs: no ICC/gamma conversion. Encoded luma
is Rec.709 weighted encoded RGB (codes); linear luma decodes each channel first.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt

HERE = Path(__file__).resolve().parent
DEFAULT_WORKTREE = Path('/Users/new/vitrea-w49/b-g0')
DEFAULT_CANONICAL = Path('/Users/new/Developer/GitHub/designer')
GENERATIONS = {'0.25': 'b2d074d2df24-940384c06f73', '0.5': '0eac5b294cc2'}
BACKGROUNDS = ('dark-solid', 'mid-dark-solid', 'impulse')
COMPONENTS = ('rrect-sm', 'rrect-md', 'rrect-ml', 'rrect-lg')
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float64)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def witness(path: Path) -> dict:
    if not path.exists():
        return {'path': str(path), 'exists': False}
    raw = path.read_bytes()
    return {'path': str(path), 'exists': True, 'bytes': len(raw), 'sha256': sha(raw)}


def canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def metric_value(row: dict | None, key: str):
    if row is None:
        return None
    value = row.get('material', {}).get(key)
    return value.get('value') if isinstance(value, dict) else None


def smoothstep(a: float, b: float, x: float) -> float:
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def encode(x: float) -> float:
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def curve(x: float, xs: list, ys: list) -> float:
    """The four-anchor WGSL curve, in float64 for attribution, not a rendered oracle."""
    x = min(xs[-1], max(xs[0], x))
    h = np.diff(xs)
    d = np.diff(ys) / h
    m = [d[0], *(2 * d[i] * d[i + 1] / (d[i] + d[i + 1])
                 if d[i] * d[i + 1] > 0 else 0 for i in range(2)), d[-1]]
    i = 0 if x <= xs[1] else 1 if x <= xs[2] else 2
    t = (x - xs[i]) / h[i]
    return float(ys[i] * (1 + 2 * t) * (1 - t) ** 2
                 + m[i] * h[i] * t * (1 - t) ** 2
                 + ys[i + 1] * t ** 2 * (3 - 2 * t)
                 + m[i + 1] * h[i] * t ** 2 * (t - 1))


def tone_attribution(group: dict, patch: dict, span: float, scale: int, regular_alpha: float) -> dict:
    assert patch['backdropToneBlackStrength'] == 1 and patch['backdropToneResponseStrength'] == 1
    packed = group['state'].get('backdropToneAbscissae', [])
    assert len(packed) <= 1, 'Single shapes should have one local tone argument.'
    if packed:
        assert packed[0]['kind'] == 'silhouette', 'This diagnostic distinguishes GPU reduction from source fallback.'
        x = packed[0]['encodedLuminance']
        x_source = 'report.state.backdropToneAbscissae[0].encodedLuminance: recorded GPU reduction/readback; '
        x_source += 'silhouette-tone.ts toneReadingsFromBuffer slot i*8+4; WGSL tones.stats.x = mean.w'
    else:
        x = encode(group['backdropTone']['level'])
        x_source = 'sRGB encode(report.backdropTone.level); source-uniform x reconstructed in float64'
    # These documents name no sizeSpanMin/Max overrides. material.ts defaults are 32/96;
    # Normal accessibility policy leaves the shader's depth fold at 1. The supplied
    # path's short span is the casting span.
    size_k = smoothstep(32, 96, span)
    f = smoothstep(0, 1, size_k)
    xs = patch['backdropToneAnchorX']
    ys = [(1 - f) * a + f * b for a, b in zip(patch['backdropToneResponseThin'],
                                            patch['backdropToneResponseThick'])]
    weight = (1 - smoothstep(0, 0.003, x)) if x < 0.003 else 0.0
    authority = smoothstep(xs[0] * 0.5, xs[0], x)
    authority = (1 - weight) * authority + weight
    black = (1 - f) * patch['backdropToneBlackThin'] + f * patch['backdropToneBlackThick']
    response = (1 - weight) * curve(x, xs, ys) + weight * black
    # The source branch's toneAnchor.w is the physical linear source mean. The local
    # branch instead uses L(toneColour.rgb), exposed by the GPU readback's color.
    tone_linear_mean = (float(np.array(packed[0]['color']) @ LUMA) if packed
                        else group['backdropTone']['linearLuminance'])
    top = patch.get('sizeScatterSpanMax2x' if scale == 2 else 'sizeScatterSpanMax', 256)
    far_s = smoothstep(96, top, span)
    alpha_base = min(1, max(0, regular_alpha + patch.get(f'tintAlphaFar{scale}x', 0) * far_s))
    sized_alpha = alpha_base + patch.get('sizeOcclusionGain', 0.05) * size_k * (1 - alpha_base)
    minimum_transmitted = (1 - sized_alpha) * tone_linear_mean
    tone_luminance = packed[0]['luminance'] if packed else group['backdropTone']['level']
    tone_x = tone_luminance + patch.get('backdropToneSizeBias', 0.05) * size_k
    collapse_weight = 1 - smoothstep(patch['backdropToneLow'], patch['backdropToneHigh'], tone_x)
    assert collapse_weight == 0, 'The negative-neutral diagnostic assumes zero collapse.'
    return {
        'encodedInputX': x, 'inputProvenance': x_source,
        'branch': 'BLACK_AT_ZERO' if x == 0 else 'BLACK_CURVE_BLEND' if x < 0.003 else 'ORDINATE_CURVE',
        'blackBlendWeight': weight, 'toneAuthority': authority,
        'sizeK': size_k, 'thinThickMix': f,
        'anchorX': xs, 'thinOrdinatesLinear': patch['backdropToneResponseThin'],
        'thickOrdinatesLinear': patch['backdropToneResponseThick'],
        'sizeBlendedOrdinatesLinear': ys, 'blackOrdinateLinear': black,
        'curveResponseLinearBeforeFarLevel': curve(x, xs, ys),
        'blackCurveResponseLinearBeforeFarLevel': response,
        'neutralClampContext': {
            'regularTintAlpha': regular_alpha, 'alphaBase': alpha_base, 'sizedAlpha': sized_alpha,
            'collapseArgument': tone_x, 'collapseLow': patch['backdropToneLow'],
            'collapseHigh': patch['backdropToneHigh'], 'collapseWeight': collapse_weight,
            'toneLinearMean': tone_linear_mean, 'minimumTransmittedAggregateLinear': minimum_transmitted,
            'responseMinusTransmissionFloor': response - minimum_transmitted,
            'fullAuthorityUnclampedNeutralAtZeroCollapse': ((response - minimum_transmitted) / sized_alpha
                                                          if authority == 1 else None),
            'qualification': 'Held-algebra diagnostic, not another render: at full authority, zero collapse '
                             'and no far level, this is independent of the original neutral. A negative '
                             'result must clamp to zero; with a sampled-black far field the body then draws zero. '
                             'Partial authority (ml impulse) retains the original composition instead.',
        },
        'qualification': 'Attribution of the held curve and branch only, not a full GPU pixel solve: '
                         'authority multiplies the W9 correction; spatial sample, collapse, '
                         'neutral/alpha composition and highlights remain part of the rendered pixel.',
    }


def statistics(rgb: np.ndarray, mask: np.ndarray, P) -> dict:
    a = rgb[mask].astype(np.float64)
    if not len(a):
        return {'status': 'UNMEASURED_EMPTY_SUPPORT', 'pixels': 0}
    encoded = a @ LUMA
    linear = P.luminance(rgb)[mask]
    return {
        'status': 'MEASURED', 'pixels': int(len(a)),
        'rgbMeanCodes': a.mean(axis=0).tolist(), 'rgbMedianCodes': np.median(a, axis=0).tolist(),
        'encodedLumaMeanCodes': float(encoded.mean()),
        'encodedLumaMedianCodes': float(np.median(encoded)),
        'encodedLumaMinCodes': float(encoded.min()), 'encodedLumaMaxCodes': float(encoded.max()),
        'encodedLumaStdDevCodes': float(encoded.std()), 'linearLumaMean': float(linear.mean()),
        'linearLumaMedian': float(np.median(linear)), 'linearLumaStdDev': float(linear.std()),
    }


def run(worktree: Path, canonical: Path) -> dict:
    spec_path = worktree / 'apps/reference-apple/scenes.json'
    scenes = json.loads(spec_path.read_bytes())
    by_id = {s['id']: s for s in scenes['scenes']}
    port_path = worktree / 'packages/calibration/results/2026-10-03-w44-g0-declaration/port/interior.py'
    spec = importlib.util.spec_from_file_location('w44_interior', port_path)
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    results_root = worktree / 'packages/calibration/results'
    index_path = results_root / 'generations/index.json'
    index = json.loads(index_path.read_bytes())
    evidence = [witness(spec_path), witness(port_path), witness(index_path)]
    out = {
        'schemaVersion': 1,
        'purpose': 'Existing dark glass solid/impulse body levels; no render, fit, or T1/L1 change.',
        'environment': {'python': sys.version, **{n: importlib.metadata.version(n)
                                                 for n in ('numpy', 'scipy', 'Pillow')}},
        'inputs': evidence,
        'supportDefinitions': {
            'deep8': 'W44 signed_distance at pixel centres <= -8 * scale device px.',
            'core24': 'Same supplied-path signed_distance <= -24 * scale device px; diagnostic only.',
            'deep8_far16': 'deep8 AND >=16 CSS px centre distance to every nonzero no-glass impulse raster pixel; smaller-span supporting cut.',
            'deep8_far24': 'deep8 AND >=24 CSS px centre distance to every nonzero no-glass impulse raster pixel.',
            'core24_far24': 'core24 AND >=24 CSS px centre distance to every nonzero no-glass impulse raster pixel.',
            'deep8_far32': 'deep8 AND >=32 CSS px centre distance to every nonzero no-glass impulse raster pixel.',
            'farDistanceImplementation': 'scipy.ndimage.distance_transform_edt(~any(background RGB != 0))/scale',
            'farRestrictions': 'Selected pixels are asserted RGB [0,0,0] in the no-glass background; '
                               'this does not make the group/silhouette tone input zero.',
            'statistic': 'Encoded RGB/luma codes 0..255; linear luminance is per-channel sRGB decode '
                         'then Rec.709 weights; population means/medians on the SAME mask for both images.',
        },
        'uniformPureBlack': {
            'canonicalScene': None,
            'status': 'ABSENT_DECLARED_SCENE_AND_THICK_UNIFORM_CAPTURE',
            'solidDarkScene': scenes['backgrounds']['dark-solid'],
            'qualification': 'dark-solid is [28,28,30], not black. Impulse field is black away from dots, '
                             'but its aggregate tone input is nonzero.',
        },
        'generations': {}, 'profiles': {}, 'cells': [],
    }
    for glass, generation in GENERATIONS.items():
        matrix_path = results_root / f'generations/{generation}.json'
        matrix_raw = matrix_path.read_bytes()
        entry = index['files'][matrix_path.name]
        assert sha(matrix_raw) == entry['sha256'] and len(matrix_raw) == entry['bytes']
        assert entry['status'] == 'current'
        out['generations'][glass] = {**witness(matrix_path), 'indexEntry': entry}
        rows = json.loads(matrix_raw)['cells']
        documents = {}
        for doc_entry in entry['documents']:
            path = worktree / doc_entry['path']
            raw = path.read_bytes()
            assert sha(raw)[:12] == doc_entry['sha256']
            doc = json.loads(raw)
            documents['receded' if '-receded.json' in path.name else 'active'] = {
                **witness(path), 'document': doc,
            }
        active, receded = documents['active']['document'], documents['receded']['document']
        relevant = ('backdropToneAbscissa', 'backdropToneAnchorX', 'backdropToneResponseThin',
                    'backdropToneResponseThick', 'backdropToneResponseStrength', 'backdropToneLow',
                    'backdropToneHigh', 'backdropToneBlackStrength', 'backdropToneBlackThin',
                    'backdropToneBlackThick', 'tintAlphaFar1x', 'tintAlphaFar2x', 'sizeOcclusionGain',
                    'sizeScatterSpanMax', 'sizeScatterSpanMax2x')
        out['profiles'][glass] = {}
        for pose, doc in (('rest', active), ('inactive', receded)):
            patch = active['patch'] | (receded['patch'] if pose == 'inactive' else {})
            name = 'active' if pose == 'rest' else 'receded'
            out['profiles'][glass][pose] = {
                **{k: v for k, v in documents[name].items() if k != 'document'},
                'resolvedMaterialSha256': doc['resolvedMaterialSha256'],
                'resolvedNamedPatchLeaves': {k: patch[k] for k in relevant if k in patch},
                'blackTargetCodes': {
                    k: float(255 * (12.92 * patch[k] if patch[k] <= 0.0031308
                                   else 1.055 * patch[k] ** (1 / 2.4) - 0.055))
                    for k in ('backdropToneBlackThin', 'backdropToneBlackThick')
                },
                'qualification': 'Named/inherited patch leaves only, not a reconstructed complete default material.',
            }
        for scale in (1, 2):
            profile = f'apple-macos-27.0-{scale}x-dark-standard-glass{glass}'
            for background in BACKGROUNDS:
                bg_path = canonical / f'apps/reference-apple/fixtures/backgrounds/{background}@{scale}x.png'
                bg = P.read(bg_path)
                assert bg.shape[:2] == (200 * scale, 320 * scale)
                dots = np.any(bg != 0, axis=2)
                far_distance = distance_transform_edt(~dots) / scale if background == 'impulse' else None
                bg_info = witness(bg_path) | {
                    'nonzeroPixels': int(dots.sum()), 'zeroPixels': int((~dots).sum()),
                    'rgbMeanCodes': bg.reshape(-1, 3).mean(axis=0).tolist(),
                    'encodedLumaMeanCodes': float((bg.astype(np.float64) @ LUMA).mean()),
                    'linearLumaMean': float(P.luminance(bg).mean()),
                    'uniqueColors': np.unique(bg.reshape(-1, 3), axis=0).tolist(),
                }
                for component in COMPONENTS:
                    for pose in ('rest', 'inactive'):
                        sid = f'{background}__{component}__{pose}'
                        matches = [r for r in rows if r['key']['profileKey'] == profile
                                   and r['key']['sceneId'] == sid
                                   and r['key']['web']['renderer'] == 'webgpu']
                        assert len(matches) <= 1
                        row = matches[0] if matches else None
                        native_path = canonical / f'apps/reference-apple/fixtures/{profile}/{sid}.png'
                        cap_root = canonical / f'packages/calibration/web-captures/{profile}/{sid}'
                        web_path = cap_root / f'{sid}__webgpu.png'
                        cell_path = cap_root / 'cell__webgpu.json'
                        report_path = cap_root / 'report__webgpu.json'
                        item = {
                            'profile': profile, 'scene': sid, 'glass': float(glass), 'scale': scale,
                            'background': background, 'component': component, 'pose': pose,
                            'declaredScene': sid in by_id, 'spanCss': min(scenes['components'][component]['size']),
                            'backgroundInput': bg_info,
                            'nativeInput': witness(native_path), 'webInput': witness(web_path),
                            'cellMetadataInput': witness(cell_path), 'reportInput': witness(report_path),
                            'matrixRow': None, 'supports': {},
                        }
                        n = P.read(native_path) if native_path.exists() else None
                        w = P.read(web_path) if web_path.exists() else None
                        if row is not None:
                            assert w is not None and cell_path.exists() and report_path.exists()
                            metadata = json.loads(cell_path.read_bytes())
                            assert metadata == row['key']['web']
                            path = metadata['capturePath']
                            assert all(f'sha256:{d["sha256"]}' in path for d in entry['documents'])
                            report = json.loads(report_path.read_bytes())
                            assert report['page']['sceneId'] == sid
                            assert all(g['state']['activeRenderer'] == 'webgpu' for g in report['page']['groups'])
                            item['matrixRow'] = {
                                'generationPath': str(matrix_path),
                                'canonicalSortedJsonSha256': sha(canonical_json(row)),
                                'fixtureSet': row['fixtureSet'], 'capturedAt': row['capturedAt'],
                                'key': row['key'],
                                'adoptedInteriorMeanNative': metric_value(row, 'interiorMeanNative'),
                                'adoptedInteriorMeanWeb': metric_value(row, 'interiorMeanWeb'),
                            }
                            item['toneReadouts'] = [{
                                'id': g['id'], 'backdropTone': g.get('backdropTone'),
                                'packedSilhouette': g['state'].get('backdropToneAbscissae', []),
                            } for g in report['page']['groups']]
                            pose_patch = active['patch'] | (receded['patch'] if pose == 'inactive' else {})
                            assert not any(k in pose_patch for k in ('sizeSpanMin', 'sizeSpanMax'))
                            policy = report['page']['accessibilityPolicy']
                            assert not any(policy[k] for k in ('reducedTransparency', 'increasedContrast',
                                                              'forcedColors')), 'Normal material policy only.'
                            regular = active['patch']['optics']['regular'] | (
                                receded['patch']['optics']['regular'] if pose == 'inactive' else {})
                            assert pose_patch.get('sizeToneLevelFar', 0) == 0
                            item['toneAttribution'] = [tone_attribution(g, pose_patch, item['spanCss'],
                                                                      scale, regular['tintAlpha'])
                                                       for g in report['page']['groups']]
                        elif w is not None:
                            raise AssertionError(f'capture without current row: {profile}/{sid}')
                        item['status'] = ('MEASURED_PAIR' if row is not None and n is not None
                                          else 'NATIVE_ONLY_NO_CURRENT_WEB_ROW' if n is not None
                                          else 'ABSENT_NATIVE_AND_CURRENT_WEB')
                        if n is None and w is None:
                            out['cells'].append(item)
                            continue
                        shape = (n if n is not None else w).shape[:2]
                        component_geometry = scenes['components'][component]
                        distance = P.signed_distance(component_geometry, scenes['canvas'], scale, shape)
                        masks = {'deep8': distance <= -8 * scale, 'core24': distance <= -24 * scale}
                        if far_distance is not None:
                            masks |= {'deep8_far16': masks['deep8'] & (far_distance >= 16),
                                      'deep8_far24': masks['deep8'] & (far_distance >= 24),
                                      'core24_far24': masks['core24'] & (far_distance >= 24),
                                      'deep8_far32': masks['deep8'] & (far_distance >= 32)}
                            assert all(np.all(bg[m] == 0) for key, m in masks.items() if 'far' in key)
                        if n is not None:
                            silhouette = P.native_interior(n, bg, component_geometry, scenes['canvas'], scale)
                            item['nativeDetectedSilhouettePixels'] = int(silhouette.sum())
                        for name, mask in masks.items():
                            item['supports'][name] = {
                                'pixels': int(mask.sum()), 'maskPackedBitsSha256': sha(np.packbits(mask).tobytes()),
                                'native': statistics(n, mask, P) if n is not None else None,
                                'web': statistics(w, mask, P) if w is not None else None,
                            }
                        out['cells'].append(item)
    out['l1MissingMetricSupportAudit'] = []
    for glass, generation in GENERATIONS.items():
        rows = json.loads((results_root / f'generations/{generation}.json').read_bytes())['cells']
        for scale in (1, 2):
            profile = f'apple-macos-27.0-{scale}x-dark-standard-glass{glass}'
            bg = P.read(canonical / f'apps/reference-apple/fixtures/backgrounds/dark-solid@{scale}x.png')
            for component in ('capsule-button', 'rrect-md'):
                sid = f'dark-solid__{component}__inactive'
                native_path = canonical / f'apps/reference-apple/fixtures/{profile}/{sid}.png'
                web_path = canonical / f'packages/calibration/web-captures/{profile}/{sid}/{sid}__webgpu.png'
                n, w = P.read(native_path), P.read(web_path)
                geometry = scenes['components'][component]
                silhouette = P.native_interior(n, bg, geometry, scenes['canvas'], scale)
                assert silhouette.sum() == 0
                row = next(r for r in rows if r['key']['profileKey'] == profile
                           and r['key']['sceneId'] == sid and r['key']['web']['renderer'] == 'webgpu')
                assert metric_value(row, 'interiorMeanNative') is None
                assert metric_value(row, 'interiorMeanWeb') is None
                support = P.signed_distance(geometry, scenes['canvas'], scale, n.shape[:2]) <= -8 * scale
                out['l1MissingMetricSupportAudit'].append({
                    'profile': profile, 'scene': sid, 'nativeInput': witness(native_path),
                    'webInput': witness(web_path), 'rowSortedJsonSha256': sha(canonical_json(row)),
                    'nativeDetectedSilhouettePixels': 0, 'adoptedMeanStatus': 'UNMEASURED_EMPTY_DETECTED_MASK',
                    'pathDeep8': {'pixels': int(support.sum()), 'native': statistics(n, support, P),
                                  'web': statistics(w, support, P)},
                })
    w36 = results_root / '2026-09-24-w36-g1-black-branch'
    out['w36UniformBlackContext'] = {
        'inputs': [witness(w36 / n) for n in ('black-native.json', 'candidate-ordinates.json', 'fit.py', 'README.txt')],
        'darkNativeRecordedReadings': [r for r in json.loads((w36 / 'black-native.json').read_bytes())
                                       if '-dark-' in r['cell']],
        'declaration': 'grey-0__circular-120 is span44; fit.py explicitly says thick is extrapolated '
                       'and candidates have equal thin/thick ordinates. It provides no requested thick '
                       'uniform-black capture and cannot serve as a current dark0.25 thick measurement.',
    }
    shader = worktree / 'packages/renderer-webgpu/src/wgsl/optics.ts'
    out['mechanismEvidence'] = {
        'currentShader': witness(shader),
        'currentSourceInputs': [witness(worktree / f'packages/renderer-webgpu/src/{name}') for name in
                                ('material.ts', 'silhouette-tone.ts', 'wgsl/silhouette-tone.ts')],
        'captureQualification': 'The local source may contain inert W49b work. Its relevant unchanged '
                                'tone solve is inspected as mechanism context, not claimed as captured build provenance.',
        'blackBranch': 'encodedInput < 0.003; selected strength restores authority and blends target '
                       'toward black Thin/Thick; response at exact zero selects black targets 32 active / 20 receded codes.',
        'recededNearBlack': 'backdropToneAbscissa is silhouette; recorded GPU impulse inputs are above 0.003; '
                           'the black branch is therefore off at BOTH ml and lg. Both receded response rows '
                           'have first ordinate 0 at x=0.004. ml x~0.0034227 clamps to that zero target, but '
                           'the old solve authority is only ~0.798, leaving part of the original neutral/'
                           'alpha composition. lg x~0.0054775 has authority 1 and a very small positive '
                           'curve target ~0.0002146 linear. At lg that target is BELOW the transmitted '
                           'aggregate backdrop floor at either glass position; the full-authority '
                           'zero-collapse solve requests a negative neutral and clamps it to zero. '
                           'Read far-field pixels cannot change this aggregate input. These are not '
                           'empirical uniform-black readings.',
        'activeNearBlack': 'Reported source level reconstructs x~0.0037500 at 1x and ~0.0037310 at 2x. '
                          'At both scales it is beyond the black branch and below the first x=0.004 '
                          'curve knot. The active curve clamps to its first ordinate: 0.036 thin (sm), '
                          '0.031 thick (md/ml/lg), rather than the black branch\'s 32-code target. '
                          'Source-uniform x is reconstructed from the captured host report, not labelled '
                          'as a direct GPU readback.',
        'darkSolidSharedGap': 'Background RGB [28,28,30], linear Y=0.011711216012871265, not zero. '
                             'lg receded deep native/web means 48.1444/33.0722 codes at BOTH glass '
                             'positions and BOTH scales: 15.0722 codes too dark. It uses the ordinate '
                             'curve around the second anchor x=0.11, with thick y=0.0155, not the black branch.',
        'boundary': 'No thick uniform-black pair exists here. Thus pixels establish the impulse near-black/'
                    'spatial failure and the dark-solid residual, but do not empirically identify a thick '
                    'black ordinate or prove uniform black closes at thick spans.',
        'adoptedStatistics': 'L1/T1 unchanged. L1\'s four declared missing dark-solid means are capsule-button/'
                             'rrect-md inactive at both scales. The auxiliary audit verifies all four image pairs '
                             'and empty detected masks, at both positions. lg inactive also has no detected '
                             'silhouette/row mean but usable '
                             'supplied-path pixels outside that L1 population. Tiny/empty far-field populations '
                             'are reported by count, not extrapolated to a whole body.',
    }
    return out


def table_csv(out: dict) -> bytes:
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(['glass', 'scale', 'background', 'component', 'pose', 'status', 'support', 'pixels',
                     'native_encoded_luma_mean_codes', 'web_encoded_luma_mean_codes',
                     'native_encoded_luma_median_codes', 'web_encoded_luma_median_codes',
                     'native_linear_luma_mean', 'web_linear_luma_mean', 'native_rgb_mean_codes', 'web_rgb_mean_codes',
                     'tone_input_x', 'tone_input_provenance', 'tone_branch', 'tone_authority',
                     'first_ordinate_linear', 'curve_response_linear_before_far_level'])
    for cell in out['cells']:
        if not cell['supports']:
            writer.writerow([cell[k] for k in ('glass', 'scale', 'background', 'component', 'pose', 'status')])
        for name, support in cell['supports'].items():
            n, w = support['native'], support['web']
            values = []
            for key in ('encodedLumaMeanCodes', 'encodedLumaMedianCodes', 'linearLumaMean', 'rgbMeanCodes'):
                values.extend([None if x is None else x.get(key) for x in (n, w)])
            tone = cell.get('toneAttribution', [None])[0]
            attribution = ([tone[k] for k in ('encodedInputX', 'inputProvenance', 'branch', 'toneAuthority')]
                           + [tone['sizeBlendedOrdinatesLinear'][0], tone['curveResponseLinearBeforeFarLevel']]
                           if tone is not None else [None] * 6)
            writer.writerow([cell[k] for k in ('glass', 'scale', 'background', 'component', 'pose', 'status')]
                            + [name, support['pixels']] + values + attribution)
    return stream.getvalue().encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worktree', type=Path, default=DEFAULT_WORKTREE)
    parser.add_argument('--canonical', type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument('--check', action='store_true', help='Recompute and compare; write no files.')
    args = parser.parse_args()
    out = run(args.worktree.resolve(), args.canonical.resolve())
    outputs = {
        'readings.json': (json.dumps(out, indent=2, ensure_ascii=False) + '\n').encode(),
        'table.csv': table_csv(out),
    }
    for name, raw in outputs.items():
        path = HERE / name
        if args.check:
            assert path.read_bytes() == raw, f'recomputed {name} differs'
        else:
            path.write_bytes(raw)
    print('CHECKED' if args.check else 'WROTE', f'{len(out["cells"])} requested cells; '
          'current row/image/document provenance verified.')
    print('glass scale background component pose pixels nativeMean/webMean nativeMedian/webMedian support')
    for cell in out['cells']:
        if cell['status'] != 'MEASURED_PAIR':
            print(cell['glass'], cell['scale'], cell['background'], cell['component'], cell['pose'], cell['status'])
            continue
        name = 'deep8_far24' if cell['background'] == 'impulse' else 'deep8'
        s = cell['supports'][name]
        n, w = s['native'], s['web']
        if s['pixels'] == 0:
            print(cell['glass'], cell['scale'], cell['background'], cell['component'], cell['pose'],
                  'UNMEASURED_EMPTY_SUPPORT', name)
            continue
        print(cell['glass'], cell['scale'], cell['background'], cell['component'], cell['pose'], s['pixels'],
              f'{n["encodedLumaMeanCodes"]:.3f}/{w["encodedLumaMeanCodes"]:.3f}',
              f'{n["encodedLumaMedianCodes"]:.3f}/{w["encodedLumaMedianCodes"]:.3f}', name)


if __name__ == '__main__':
    main()
