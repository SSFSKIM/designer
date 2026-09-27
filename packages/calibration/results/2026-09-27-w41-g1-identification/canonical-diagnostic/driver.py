"""Canonical cal/val diagnostic WEB for EYE. Direct capture, no native reader or matrix."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('canonical_capture_support', HERE.parent / 'candidate-capture/driver.py')
backend = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = backend
spec.loader.exec_module(backend)
base, runner, ROOT = backend.base, backend.runner, backend.ROOT
CAPTURES = Path('/Users/new/vitrea-w41/g1-captures/canonical-diagnostic')
SCENES = ROOT / 'apps/reference-apple/scenes.json'
LABEL = 'diagnostic candidate WEB for EYE; not a canonical read or G2 material'


def fresh_plan():
    return json.loads(subprocess.check_output(['pnpm', '--dir', str(ROOT / 'packages/calibration'),
        'exec', 'tsx', str(HERE / 'plan.ts')]))


def policy(cell):
    clause = cell['pose'][2]
    values = {'reducedTransparency': False, 'increasedContrast': False, 'reducedMotion': False}
    if clause == 'accessibility=browser-preferences': return None
    if clause == 'accessibility=reducedTransparency (others explicitly off)':
        values['reducedTransparency'] = True
    elif clause == 'accessibility=reducedTransparency+increasedContrast (others explicitly off)':
        values.update(reducedTransparency=True, increasedContrast=True)
    else: raise ValueError('unrecognized recorded accessibility pose')
    return values


def command_for(cells, output):
    output = Path(output).resolve()
    if not output.is_relative_to(CAPTURES) or output == CAPTURES:
        raise ValueError('capture output must be separate diagnostic scratch')
    if not cells or len({c['profileKey'] for c in cells}) != 1: raise ValueError('one profile per launch')
    split = runner.load(SCENES)['split']
    allowed = set(split['calibration']) | set(split['validation'])
    if any(c['role'] not in ('calibration', 'validation') or c['sceneId'] not in allowed for c in cells):
        raise ValueError('canonical diagnostic admits calibration/validation only')
    cell = cells[0]
    if any(c['documents'] != cell['documents'] or c['pose'] != cell['pose'] for c in cells):
        raise ValueError('mixed document pair or pose')
    scale = re.fullmatch(r'deviceScaleFactor=(1|2)', cell['pose'][0])
    scheme = re.fullmatch(r'colorScheme=(light|dark)', cell['pose'][1])
    if not scale or not scheme: raise ValueError('invalid capture pose')
    docs = {d['kind']: d for d in cell['documents']}
    if set(docs) not in ({'materialProfile'}, {'materialProfile', 'recededProfile'}):
        raise ValueError('incomplete document pair')
    command = ['pnpm', '--dir', str(ROOT / 'packages/calibration'), 'exec', 'tsx',
        'scripts/capture-web.ts', *[c['sceneId'] for c in cells], '--renderer', 'webgpu',
        '--scale', scale[1], '--color-scheme', scheme[1], '--out', str(output),
        '--material-profile', str(ROOT / docs['materialProfile']['path'])]
    if 'recededProfile' in docs:
        command += ['--receded-profile', str(ROOT / docs['recededProfile']['path'])]
    requested = policy(cell)
    if requested is not None:
        command += ['--accessibility', 'reduced-transparency' +
                    (',increased-contrast' if requested['increasedContrast'] else '')]
    return command


def document(d):
    path = ROOT / d['path']
    if runner.sha(path)[:12] != d['sha256']: raise ValueError('planned document changed')
    value = runner.load(path)
    wrapped = 'patch' in value or 'cssTierMapping' in value
    return dict(sha256=d['sha256'], patch=value.get('patch', {}) if wrapped else value,
                **({'cssTierMapping': value.get('cssTierMapping')} if d['kind'] == 'materialProfile' else {}))


def names_value(patch):
    return any(names_value(v) if isinstance(v, dict) else True for v in patch.values())


def validate_report(cell, descriptor, report):
    """Report observed endpoint separately from patch hashes; a tuned digest is not a patch hash."""
    sid = cell['sceneId']; page = report.get('page', {})
    scale = int(cell['pose'][0].split('=')[1]); scheme = cell['pose'][1].split('=')[1]
    size = [cell['canvas']['width'] * scale, cell['canvas']['height'] * scale]
    if (descriptor.get('sceneId') != sid or page.get('sceneId') != sid or
        descriptor.get('renderer') != 'webgpu' or descriptor.get('engine') != 'chromium' or
        descriptor.get('colorSpace') != 'srgb' or descriptor.get('samplingBackend') != 'gpu-texture' or
        descriptor.get('pixelSize') != size or page.get('pixelSize') != size or
        page.get('canvas') != cell['canvas'] or page.get('requestedScale') != scale or
        page.get('devicePixelRatio') != scale or page.get('colorScheme') != scheme or
        report.get('colorScheme') != scheme or descriptor.get('deterministic') is not True or
        descriptor.get('repeatNoise') != 0 or report.get('fallback', 'missing') is not None or
        report.get('problems') != [] or page.get('problems') != [] or
        page.get('requestedBackdropMode') != 'texture' or page.get('requestedBackdropLevel', 'missing') is not None or
        page.get('adapter', {}).get('isFallback') is not False or page.get('adapter', {}).get('ok') is not True):
        raise ValueError('actual hardware WebGPU capture/profile mismatch: ' + sid)
    requested = policy(cell)
    expected_policy = requested or dict(reducedTransparency=False, increasedContrast=False, reducedMotion=False)
    if (report.get('accessibility', 'missing') != requested or
        page.get('accessibilityOverrides', 'missing') != requested or
        any(page.get('accessibilityPolicy', {}).get(k) != v for k, v in {**expected_policy, 'forcedColors': False}.items())):
        raise ValueError('actual accessibility policy mismatch')
    docs = {d['kind']: document(d) for d in cell['documents']}
    for key, expected in docs.items():
        if any((report.get(key) or {}).get(k, 'missing') != v for k, v in expected.items()):
            raise ValueError('actual document hash/patch mismatch')
    if 'recededProfile' not in docs and report.get('recededProfile', 'missing') is not None:
        raise ValueError('unexpected receded document')
    active = docs['materialProfile']['patch']
    candidate = docs['recededProfile']['patch'] if cell['state'] == 'inactive' and 'recededProfile' in docs else None
    posed = runner.merge_patch(active, candidate) if candidate is not None else active or None
    runtime_inactive = cell['state'] == 'inactive' and candidate is None
    mapping = docs['materialProfile']['cssTierMapping']
    material = dict(cell['selectedEndpoint'], tuned=names_value(posed or {}) or names_value(mapping or {}))
    if (page.get('windowActivation') != ('inactive' if runtime_inactive else 'active') or
        page.get('candidateRecededMaterialProfile', 'missing') != candidate or
        page.get('recededMaterialProfile', 'missing') != cell['runtimeRecededPatch'] or
        page.get('materialProfile', 'missing') != posed or page.get('cssTierMapping', 'missing') != mapping or
        page.get('material') != material):
        raise ValueError('actual endpoint/posed patch mismatch (digest is selected endpoint only)')
    groups = page.get('groups', [])
    if not groups or any(g.get('configuredSource') != 'texture' or
        (g.get('state') or {}).get('activeRenderer') != 'webgpu' or
        (g.get('state') or {}).get('samplingBackend') != 'gpu-texture' or
        (g.get('state') or {}).get('materialDocument') != material for g in groups):
        raise ValueError('drawn group renderer/material mismatch')


def attempt(name):
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', name): raise ValueError('unsafe attempt')
    return HERE / name


def assemble(name):
    directory = attempt(name)
    if directory.exists() or (CAPTURES / name).exists(): raise FileExistsError('fresh attempt required')
    plan = fresh_plan()
    reviewed = runner.load(HERE.parent / 'candidate-capture/reviewed-inputs.json')['files']
    backend.check_hashes(ROOT, reviewed)
    sources = backend.source_inventory(ROOT, globals())
    manifest_path = ROOT / 'apps/reference-apple/fixtures/manifest.json'
    backgrounds = runner.load(manifest_path)['backgrounds']
    backdrop_files = set()
    for cell in plan['cells']:
        scale = cell['pose'][0].split('=')[1]
        name = backgrounds.get(cell['background'] + '@' + scale + 'x', backgrounds.get(cell['background']))
        path = (manifest_path.parent / name).resolve() if name else None
        if path is None or not path.is_relative_to(manifest_path.parent / 'backgrounds'):
            raise ValueError('canonical shared background path missing or unsafe')
        backdrop_files.add(backend.relative(path))
    extras = [manifest_path, HERE / 'plan.ts', HERE.parent / 'sheets/adapter.ts',
        HERE.parents[1] / '2026-09-27-w41-g0-declaration/sheets/sheets.ts', SCENES,
        HERE.parent / 'candidate-capture/reviewed-inputs.json']
    files = set(sources) | set(reviewed) | backdrop_files | {backend.relative(p) for p in extras} | {
        d['path'] for c in plan['cells'] for d in c['documents'] + c['shippedDocuments']}
    pins = {p: runner.committed(ROOT, p) for p in files}
    directory.mkdir()
    runtime = {backend.relative(p): backend.relative(backend.snapshot(p, directory / 'policy-runtime'))
        for p in (ROOT / runner.POLICY_DIST).rglob('*') if p.is_file() and p.suffix in ('.js', '.mjs', '.cjs')}
    if runner.POLICY_DIST + '/index.js' not in runtime: raise ValueError('build policy first')
    base.save(directory / 'seal.json', dict(schema='w41-canonical-diagnostic-inputs-1', label=LABEL,
        plan=plan, sources=sources, inputs=pins, runtimeArtifacts=runtime,
        sourceRevision=runner.git(ROOT, 'rev-parse', 'HEAD').decode().strip(), nativePayloadReads=0))
    print('ASSEMBLED; commit seal and policy-runtime before capture:', directory)


def verify(name):
    directory = attempt(name)
    runner.committed(ROOT, backend.relative(directory / 'seal.json'))
    sealed = runner.load(directory / 'seal.json')
    if fresh_plan() != sealed['plan']: raise ValueError('canonical plan changed')
    runner.coverage(backend.source_inventory(ROOT, globals()), sealed['sources'], 'capture source frontier')
    backend.check_hashes(ROOT, sealed['inputs'])
    for path in sealed['inputs']: runner.committed(ROOT, path)
    runner.verify_runtime_artifacts(ROOT, sealed['runtimeArtifacts'], required=True)
    for path in sealed['runtimeArtifacts'].values(): runner.committed(ROOT, path)
    return directory, sealed


def capture(name):
    directory, sealed = verify(name)
    if (directory / 'frozen.json').exists(): raise FileExistsError('already frozen')
    seal_sha = runner.sha(directory / 'seal.json')
    def guard():
        verify(name)
        if runner.sha(directory / 'seal.json') != seal_sha: raise ValueError('seal changed')
    env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
    env.update(VITREA_SCENES=str(SCENES), VITREA_FIXTURES=str(ROOT / 'apps/reference-apple/fixtures'),
               VITREA_ALLOW_FALLBACK_ADAPTER='0')
    captures = {}; documents = {}; evidence = {}
    for profile in sorted({c['profileKey'] for c in sealed['plan']['cells']}):
        cells = [c for c in sealed['plan']['cells'] if c['profileKey'] == profile]
        out = CAPTURES / name / profile
        process = directory / 'processes' / profile
        if not (process / 'complete.json').exists():
            if out.exists(): raise FileExistsError('preserve existing partial capture; no overwrite')
            backend.launch(process, command_for(cells, out), env, guard)
        guard()
        rows = {}; reports = {}
        for cell in cells:
            sid = cell['sceneId']; folder = out / sid; identity = profile + '/' + sid
            descriptor = runner.load(folder / 'cell__webgpu.json')
            report = runner.load(folder / 'report__webgpu.json')
            validate_report(cell, descriptor, report)
            rows[identity] = dict(png=str(folder / (sid + '__webgpu.png')),
                pngSha256=runner.sha(folder / (sid + '__webgpu.png')),
                cellSha256=runner.sha(folder / 'cell__webgpu.json'),
                reportSha256=runner.sha(folder / 'report__webgpu.json'))
            reports[identity] = dict(descriptor=descriptor, report=report)
        if (process / 'complete.json').exists():
            if runner.load(process / 'complete.json')['captures'] != rows:
                raise ValueError('completed diagnostic capture changed')
        else: base.save(process / 'complete.json', dict(captures=rows, evidence=reports))
        captures.update(rows); evidence.update(reports); documents[profile] = cells[0]['documents']
    guard()
    base.save(directory / 'domain-evidence.json', dict(label=LABEL, cells=evidence,
        digestMeaning='Selected shipped endpoint, never tuned-material digest; patches/file hashes attested separately.'))
    base.save(directory / 'frozen.json', dict(schema='w41-canonical-diagnostic-web-1', label=LABEL,
        frozenAt=base.stamp(), sealSha256=seal_sha, sourceRevision=sealed['sourceRevision'],
        captureRoot=str(CAPTURES / name), documents=documents, captures=captures,
        nativePayloadReads=0, matrixRowsWritten=0, canonicalHoldoutPixelsOpened=0))
    print('FROZEN 330 diagnostic WEB captures; commit metadata before offline sheets')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['assemble', 'verify', 'capture'])
    p.add_argument('attempt')
    a = p.parse_args()
    {'assemble': assemble, 'verify': verify, 'capture': capture}[a.operation](a.attempt)
