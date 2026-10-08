"""W50 capture evidence, never a fitter, renderer, batch locator or gate verdict.

The pure core evaluates an already decoded web image on ORIGINAL native support witnesses.
Analytical masks must hash-match every native run; T1 uses each native packed full silhouette,
never a web-detected silhouette or erosion. The native reader's three-statistic median and native
repeat bars survive unchanged. A single web capture does not manufacture a new repeat bar.

measure_capture is a live-dispatcher I/O wrapper for exposed role reports only. Its report and
native batch are root inputs; scenes are pinned by both immutable G0 parts. It opens only one
registered web member and its original no-glass dependency. Blind I/O and completed-current
bootstrap admission belong to their separate outer readers; the pure core is role-independent.
All source imports are compiled from bytes so prospective import sealing sees the real source.
"""
from __future__ import annotations

import copy
import gzip
import json
from pathlib import Path
import sys
import types

import numpy as np

HERE = Path(__file__).resolve().parent
FIT = HERE.parent


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


R = source(FIT/'native/reader.py', 'w50_measurement_native')
A = source(FIT/'web/adapter.py', 'w50_measurement_web')
N = source(FIT.parent/'2026-10-08-w50-g0-declaration/audit/numerical_guard.py',
           'w50_measurement_numerical_guard')
LEVELS = {
    'deep8-channel-median': ('deep8', 'encoded-RGB-codes', 'rgbMedianCodes'),
    'central8-channel-median': ('center8', 'encoded-RGB-codes', 'rgbMedianCodes'),
    'deep8-far24-luma-mean': ('deep8_far24', 'encoded-luma-codes', 'encodedLumaMeanCodes'),
    'deep8-far24-luma-median': ('deep8_far24', 'encoded-luma-codes', 'encodedLumaMedianCodes'),
    'T1-full-silhouette': ('full-silhouette', 'linear-luma', 'linearLumaStdDev'),
}


def _witness(record, mask):
    if record.get('maskShape') != list(mask.shape) or mask.dtype != np.bool_ \
            or record.get('pixels') != int(mask.sum()) \
            or record.get('maskPackedBitsSha256') != R.S.sha(np.packbits(mask).tobytes()):
        raise ValueError('Mask differs from the original native support witness')
    status = 'MEASURED' if mask.any() else 'UNMEASURED_EMPTY_SUPPORT'
    if record.get('status') != status:
        raise ValueError('Native support status disagrees with its exact population')
    return {key: copy.deepcopy(record[key]) for key in
            ('pixels', 'maskShape', 'maskPackedBitsSha256')}


def evaluate_native_supports(rgb, native_cell, analytical_masks, *, renderer):
    """Pure evidence on original masks; the outer caller owns content/membership admission.

    analytical_masks is the sealed native helper's deep8/center8(/deep8_far24) map, rebuilt
    from the ORIGINAL native no-glass dependency, not any web image. Every run must witness
    exactly those bytes. Per-run T1 masks are decoded directly from the native read report.
    This API opens no paths, interprets no role as permission and issues no landing verdict.
    """
    rgb = R.S.checked_rgb(rgb)
    if renderer not in ('webgpu', 'css'):
        raise ValueError('An exact measured renderer is required')
    runs = native_cell['runs']
    if [run['run'] for run in runs] != [1, 2, 3]:
        raise ValueError('Exactly three ordered original native run supports are required')
    names = set(native_cell['statistics'])
    expected = set(LEVELS) if native_cell['family'] != 'uniform' else set(list(LEVELS)[:2])
    if names != expected or any(set(run['readings']['statistics']) != names for run in runs):
        raise ValueError('Native statistic population differs from its declared family')
    supports = {LEVELS[name][0] for name in names}
    if set(analytical_masks) != supports-{'full-silhouette'}:
        raise ValueError('Exact original analytical support membership is required')
    for name in names:
        support, units, _ = LEVELS[name]
        for item in [native_cell['statistics'][name]] + [r['readings']['statistics'][name] for r in runs]:
            if item.get('support') != support or item.get('units') != units:
                raise ValueError('Native statistic support or units differ from the sealed reader')

    measured_runs, witnesses = [], {name: [] for name in names}
    for run in runs:
        original = run['readings']['supports']
        masks = dict(analytical_masks)
        if 'full-silhouette' in supports:
            masks['full-silhouette'] = R.S.decode_support(original['full-silhouette'])
        readings = {}
        for support in sorted(supports):
            mask = np.asarray(masks[support])
            if mask.shape != rgb.shape[:2] or mask.dtype != np.bool_:
                raise ValueError('Original native support dimensions differ from web PNG')
            witness = _witness(original[support], mask)
            readings[support] = R.S.read_support(rgb, mask)
            for name in names:
                if LEVELS[name][0] == support:
                    witnesses[name].append(dict(run=run['run'], **witness))
        statistics = {}
        for name in sorted(names):
            support, units, field = LEVELS[name]
            reading = readings[support]
            statistics[name] = dict(status=reading['status'], support=support, units=units,
                                    value=reading.get(field))
        measured_runs.append(dict(run=run['run'], nativeEvidence=copy.deepcopy(run['evidence']),
                                  readings=dict(supports=readings, statistics=statistics)))

    statistics = {}
    for name in sorted(names):
        native = native_cell['statistics'][name]
        values = [run['readings']['statistics'][name]['value'] for run in measured_runs]
        complete = all(value is not None for value in values)
        required = native['required']
        if not complete and (required or name != 'T1-full-silhouette'):
            raise ValueError('An empty required native support cannot certify a measurement')
        if not complete and any(w['pixels'] for w in witnesses[name]):
            raise ValueError('Optional empty T1 requires three exact zero-support witnesses')
        value = np.median(np.asarray(values, dtype=float), axis=0).tolist() if complete else None
        statistics[name] = dict(status=('UNMEASURED_EMPTY_SUPPORT' if not complete else
                                'REPORTED' if not required else 'MEASURED'),
            measurementStatus='MEASURED' if complete else 'UNMEASURED_EMPTY_SUPPORT',
            required=required, support=LEVELS[name][0], units=LEVELS[name][1], value=value,
            runValues=values, aggregation='coordinatewise-median-of-three-run-statistics',
            nativeValue=copy.deepcopy(native['value']), nativeRepeat=copy.deepcopy(native['repeat']),
            nativeSupportWitnesses=witnesses[name])
        if not required:
            statistics[name]['B'] = None
    return dict(schema='w50-web-native-support-read-1', status='MEASURED',
        profile=native_cell['profile'], renderer=renderer, scene=native_cell['scene'],
        role=native_cell['role'], pose=native_cell['pose'], scale=native_cell['scale'],
        statistics=statistics, runs=measured_runs)


def _json(raw):
    def invalid(value):
        raise ValueError('Nonfinite JSON constant: '+value)
    return json.loads(raw, parse_constant=invalid)


def _pin_bytes(pin, root, *, external=False):
    R.digest(pin.get('sha256'), 'Content pin')
    relative = pin.get('path')
    if not isinstance(relative, str):
        raise ValueError('Missing canonical content-pin path')
    if external:
        path = Path(relative)
        if not path.is_absolute() or '..' in path.parts or str(path) != relative \
                or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Capture artifact is outside admitted output')
        path = R.safe(root.resolve(), str(path.relative_to(root.resolve())))
    else:
        path = R.safe(root.resolve(), relative)
    raw = path.read_bytes()
    if R.S.sha(raw) != pin['sha256']:
        raise ValueError('Changed pinned report, image or declaration bytes')
    return raw


def _run(context, receipt, dispatcher):
    admitted = [(run, False) for run in context['batch']['runs']]
    if context['phase'] == 'exposure':
        admitted += [(dispatcher.baseline_run(run), True) for run in context['batch']['runs']
                     if run.get('baselineCandidate') in context['baselineDocuments']]
    matches = [(run, current) for run, current in admitted
               if all(receipt.get(k) == run[k] for k in ('profile', 'renderer', 'candidate'))
               and receipt.get('scene') in run['scenes']
               and receipt.get('lane') == ('current' if current else 'candidate')]
    if len(matches) != 1:
        raise ValueError('Capture receipt differs from exact admitted run/candidate/member')
    run, current = matches[0]
    dispatcher.require_render_admission(context, run, current=current)
    if receipt.get('sceneSource') != 'w50' or run.get('sceneSource') != 'w50':
        raise ValueError('Only the W50 512x384 scene source is supported')
    plan = A.scene_plan(run, context['phase'])
    spec = next(s for s in plan['scenes'] if s['scene'] == receipt['scene'])
    if receipt.get('canvas') != plan['canvas'] or receipt.get('dpr') != plan['dpr']:
        raise ValueError('Receipt canvas/scale differs from its declared profile')
    return run, plan, spec


def _scene_document(context, scenes_pin, dispatcher):
    root = dispatcher.sealed(context['executionRoot'])
    for name in ('partOne', 'partTwo'):
        part = _json(_pin_bytes(root[name], Path(context['repo'])))
        if scenes_pin not in part['sources']:
            raise ValueError('Scene declaration is not pinned by both immutable G0 parts')
    wanted = str((A.G0/'bed/scenes-w50.json').relative_to(Path(context['repo'])))
    if scenes_pin.get('path') != wanted:
        raise ValueError('Scene declaration differs from the sealed W50 source')
    return _json(_pin_bytes(scenes_pin, Path(context['repo'])))


def _native_cell(report, receipt, plan, spec, doc):
    if report.get('schema') != 'w50-native-role-read-1' or report.get('role') not in ('calibration', 'validation'):
        raise ValueError('Only exposed calibration/validation role reports are admitted; blind I/O is separate')
    if report.get('canvas') != doc['canvas'] or report.get('ready') is not True or report.get('stops') != [] \
            or report.get('supportDefinitions') != R.S.SUPPORT_DEFINITIONS \
            or report.get('repeatRule') != dict(runs=3, maxRequiredSpreadCodes=1, barFloorCodes=.5):
        raise ValueError('Native role report is not ready under the sealed canvas/support/repeat rule')
    cells = R.unique(report['cells'], 'id', 'native report cell')
    identity = receipt['profile']+'/'+receipt['scene']
    cell = cells.get(identity)
    if cell is None or any(cell.get(k) != receipt[k] for k in ('profile', 'scene')) \
            or cell.get('role') != report['role'] or cell.get('role') != spec['role'] \
            or cell.get('pose') != spec['pose'] or cell.get('scale') != plan['dpr'] \
            or cell.get('span') != spec['span'] or cell.get('glass') != plan['position'] \
            or cell.get('background') != spec['background']:
        raise ValueError('Native cell profile/scene/pose/scale/role differs from admitted capture')
    profile = next((p for p in doc['profiles'] if p['key'] == cell['profile']), None)
    if profile is None or cell['scene'] not in profile['scenes']:
        raise ValueError('Native cell is outside the sealed profile scene membership')
    return cell


def measure_capture(context, native_report_pin, receipt, scenes_pin, *, native_batch_pin):
    """Measure one admitted exposed capture; return evidence plus actual independent arguments.

    Both native pins are exact context.inputs members. native_batch_pin names the sealed native
    read batch's role export, index hash and scene/declaration inputs. Native report pins can
    name JSON or gzip-compressed role shards, never a path-selected full archive batch.
    """
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:
        raise ValueError('Measurement requires a live registered dispatcher context')
    dispatcher.require_context(context)
    if context['phase'] not in ('fit', 'gate', 'exposure'):
        raise ValueError('Completed-current measurements require their separate evidence bootstrap')
    if native_report_pin not in context['inputs'] or native_batch_pin not in context['inputs']:
        raise ValueError('Native report/batch pins are not admitted root inputs')
    run, plan, spec = _run(context, receipt, dispatcher)
    doc = _scene_document(context, scenes_pin, dispatcher)
    raw = _pin_bytes(native_report_pin, Path(context['repo']))
    report = _json(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)
    cell = _native_cell(report, receipt, plan, spec, doc)
    batch = _json(_pin_bytes(native_batch_pin, Path(context['repo'])))
    if batch.get('schema') != 'w50-native-read-batch-1' or batch['inputs'].get('scenes') != scenes_pin \
            or batch['inputs']['declaration']['sha256'] != report['declarationSha256']:
        raise ValueError('Native batch scene/declaration pins differ from the report')
    exports = [e for e in batch['exports'] if e['role'] == report['role']]
    if len(exports) != 1 or exports[0]['indexSha256'] != report['indexSha256']:
        raise ValueError('Native report index differs from its admitted role export')
    export = Path(exports[0]['root'])
    if not export.is_absolute() or export.is_symlink() or not export.is_dir():
        raise ValueError('Native dependency requires the original ordinary role export root')
    index = _json(_pin_bytes(dict(path='index.json', sha256=report['indexSha256']), export))
    deps = R.unique(report['dependencies'], 'id', 'native dependency')
    dependency = deps.get(cell['reference'])
    if dependency is None or any(r['dependency'] != cell['reference'] for r in cell['runs']):
        raise ValueError('Native cell lacks its original no-glass dependency')
    evidence = dependency['evidence']
    if index.get('schema') != 'w50-role-archive-1' or evidence not in index['files'] \
            or evidence.get('cell') != cell['reference'] or evidence.get('roles') != [report['role']] \
            or evidence.get('run') != 1 or evidence.get('kind') != 'frame':
        raise ValueError('Original no-glass row differs from the pinned role report/export')
    dependency_raw = _pin_bytes(dict(path=evidence['path'], sha256=evidence['sha256']), export)

    artifacts = receipt['artifacts']
    blobs = {}
    for name, filename in (('png', f'{receipt["scene"]}__{receipt["renderer"]}.png'),
                           ('report', f'report__{receipt["renderer"]}.json'),
                           ('cell', f'cell__{receipt["renderer"]}.json')):
        expected = Path(run['captureRoot'])/receipt['scene']/filename
        if artifacts[name].get('path') != str(expected):
            raise ValueError('Artifact path differs from exact admitted capture member')
        blobs[name] = _pin_bytes(artifacts[name], Path(context['output']), external=True)
    metadata = _json(blobs['cell'])
    if metadata.get('renderer') != run['renderer'] or metadata.get('colorSpace') != 'srgb' \
            or metadata.get('deterministic') is not True or metadata.get('repeatNoise') != 0 \
            or f'declarationSha256={run["candidate"]["sha256"][:12]}' not in metadata.get('capturePath', ''):
        raise ValueError('Capture metadata differs from admitted deterministic candidate/tier')
    candidate = A.candidate_info(run['candidate'], plan['position'])
    endpoint = candidate['endpoints'][spec['pose']+'.dark']
    resolved = {**candidate['endpoints']['active.dark']['patch'], **endpoint['patch']}
    abscissa = resolved.get('backdropToneAbscissa', 'source')
    abscissa = 'silhouette' if isinstance(abscissa, dict) else abscissa
    arguments = A.validate_report(_json(blobs['report']), run, endpoint,
                                  abscissa=abscissa, phase=context['phase'])
    for argument in arguments:
        N.validate_tone_values(argument)
    png_raw = blobs['png']
    pixels = (doc['canvas']['width']*plan['dpr'], doc['canvas']['height']*plan['dpr'])
    if png_raw[:8] != b'\x89PNG\r\n\x1a\n' or len(png_raw) < 24 \
            or tuple(int.from_bytes(png_raw[i:i+4], 'big') for i in (16, 20)) != pixels:
        raise ValueError('Pinned web PNG dimensions differ from the native canvas/profile')
    background = R.S.decode_png(dependency_raw)
    web = R.S.decode_png(png_raw)
    shape = (pixels[1], pixels[0], 3)
    if background.shape != shape or web.shape != shape:
        raise ValueError('Actual PNG dimensions differ from the declared native canvas/profile')
    scene = next(s for s in doc['scenes'] if s['id'] == receipt['scene'])
    masks = R.S.analytical_masks(doc['components'][scene['component']], doc['canvas'], plan['dpr'],
        web.shape[:2], background=background, impulse=doc['backgrounds'][scene['background']]['kind'] == 'impulse')
    if cell['family'] == 'uniform':
        del masks['deep8_far24']
    result = evaluate_native_supports(web, cell, masks, renderer=run['renderer'])
    provenance = dict(nativeRead=copy.deepcopy(native_report_pin), nativeBatch=copy.deepcopy(native_batch_pin),
        scenes=copy.deepcopy(scenes_pin), nativeDependency=copy.deepcopy(evidence),
        capture=copy.deepcopy(artifacts['png']), report=copy.deepcopy(artifacts['report']),
        cell=copy.deepcopy(artifacts['cell']), candidateDocument=copy.deepcopy(run['candidate']))
    for argument in arguments:
        argument['provenance'].update(report=copy.deepcopy(artifacts['report']),
            capture=copy.deepcopy(artifacts['png']), sceneSource='w50', scenesSha256=scenes_pin['sha256'],
            candidateDocument=copy.deepcopy(run['candidate']), baseline=receipt['lane'] == 'current',
            endpoint={k: copy.deepcopy(v) for k, v in endpoint.items() if k != 'patch'})
    result.update(evidence=provenance, arguments=arguments)
    dispatcher.require_context(context)
    return result


def source_probe():
    """Synthetic numerical paths only; no context, report, export, capture or machine read."""
    canvas = {'width': 64, 'height': 64}
    component = {'kind': 'rrect', 'size': [48, 48], 'radius': 0}
    for scale in (1, 2):
        rgb = np.zeros((64*scale, 64*scale, 3), dtype=np.uint8)
        rgb[:, 32*scale:] = 255
        bg = np.zeros_like(rgb)
        masks = R.S.analytical_masks(component, canvas, scale, rgb.shape[:2])
        for empty in (False, True):
            silhouette = np.zeros(rgb.shape[:2], dtype=bool) if empty else np.ones(rgb.shape[:2], dtype=bool)
            readings = R.S.read_frame(rgb, bg, component, canvas, scale,
                include_structured=True, silhouette_mask=silhouette)
            runs = [dict(run=n, evidence={'sha256': str(n)*64}, readings=readings) for n in (1, 2, 3)]
            cell = dict(profile='synthetic', scene='synthetic', pose='active', scale=scale,
                role='blind' if empty else 'calibration', family='span', runs=runs,
                statistics=R.aggregate_runs(runs, reported=empty))
            for renderer in ('webgpu', 'css'):
                result = evaluate_native_supports(rgb, cell, masks, renderer=renderer)
                value = result['statistics']['T1-full-silhouette']['value']
                if value != (None if empty else .5):
                    raise ValueError('Synthetic native-mask T1 exercise failed')
    for record in (dict(encodedLuminance=.1, linearLuminance=.2, rgb=[.2]*3),
                   dict(encodedLuminance=A.encode(.010022825574869039), linearLuminance=.2, rgb=[.2]*3)):
        N.validate_tone_values(record)
    return {'status': 'SOURCE_ONLY'}
