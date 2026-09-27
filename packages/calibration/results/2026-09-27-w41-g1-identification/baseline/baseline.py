"""W41 step 1: public-backdrop preparation and shipped complete-composite baseline.

No candidate, receipt, canonical writer or native capture. Native transfer is a
separate operation after a web freeze and reads only through the cal/val guard.
"""
import argparse
import datetime
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
ROOT = RESULTS.parents[2]
G0 = RESULTS / '2026-09-27-w41-g0-declaration'
W39 = RESULTS / '2026-09-26-w39-g0-colour-edge-bed'
CAPTURES = Path('/Users/new/vitrea-w41/g1-captures/baseline')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module('baseline_runner', G0 / 'exposure/runner.py')
sys.path.insert(0, str(G0 / 'instrument'))
import instrument as m
import rendered
x6 = load_module('baseline_x6', HERE.parent / 'x6/observe.py')
wave = runner.boundary.default_wave()
sha = runner.sha
load = runner.load
stable = runner.stable


def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def raster(background, scale, size):
    width, height = size
    shape = (height * scale, width * scale, 3)
    if background['kind'] == 'solid':
        return np.broadcast_to(background['srgb'], shape).astype(np.uint8).copy()
    if background['kind'] != 'linear-gradient':
        raise ValueError('undeclared background kind')
    y, x = np.mgrid[:shape[0], :shape[1]]
    nx, ny = np.cos(np.deg2rad(background['angle'])), np.sin(np.deg2rad(background['angle']))
    t = np.clip(.5 + (((x + .5) / scale - width / 2) * nx +
                      ((y + .5) / scale - height / 2) * ny) /
                (abs(nx) * width + abs(ny) * height), 0, 1)
    return np.floor(np.asarray(background['from']) * (1 - t[..., None]) +
                    np.asarray(background['to']) * t[..., None] + .5).astype(np.uint8)


def scope():
    planned, _ = wave.launch_plan(('calibration', 'validation'))
    declared = sorted(c for c in wave.cells if c.split('/', 1)[1] in planned)
    admitted, _ = runner.admitted_scope(ROOT, wave)
    included = sorted(set(declared) & set(admitted['rendered']))
    return included, {c: 'not admitted by fixed archive inventory'
                      for c in declared if c not in included}


def component(cell):
    profile, sid = cell.split('/', 1)
    comp_id = wave.scenes[sid]['component']
    paths = load(W39 / 'supplied-paths.json')['components'][comp_id]
    return {**wave.component(sid), 'suppliedPaths': paths}, int(re.search(r'-(1|2)x-', profile)[1])


def project(cell, png):
    """Web only; supplied paths are committed public geometry metadata, never native pixels."""
    rgb = rendered.read_capture(png)
    if tuple(rgb.shape[:2][::-1]) != runner.dimension(wave, cell):
        raise ValueError('wrong web frame dimensions')
    comp, scale = component(cell)
    shapes = m.readers.shapes_of(comp)
    geo = m.readers.geometry(rgb.shape[:2], shapes, scale)
    members = []
    for member in range(len(shapes)):
        deep = m.readers.deep_body(rgb, geo, member)
        bins, labels = m.readers.edge_bins(geo, member)
        members.append({'member': member, 'deep': deep,
                        'bins': m.readers.read_bins(rgb, bins, labels, deep)})
    result = {'cell': cell, 'scale': scale, 'members': members,
              'composite': 'complete opaque web frame; active shadow included'}
    background = wave.spec['backgrounds'][wave.scenes[cell.split('/', 1)[1]]['background']]
    if background['kind'] == 'linear-gradient':
        ref = raster(background, scale, (wave.spec['canvas']['width'], wave.spec['canvas']['height']))
        # The instrument has a seven-frame interface. These are deterministic copies
        # of ONE web projection, not seven observed repeats or a measured repeat bar.
        strip = m.gradient_strip(np.repeat(rgb[None], 7, axis=0),
                                 np.repeat(ref[None], 7, axis=0), shapes[0], scale)
        result['strip'] = {k: strip[k] for k in
                           ['yCSS', 'depthCSS', 'pixelsPerRow', 'reference', 'memoRowMean']}
        result['strip']['web'] = strip['native']
        result['strip']['referenceOrigin'] = 'generated public sRGB raster'
    return result



def transfer_projection(cell, png, payloads):
    """Array-only transfer; the caller owns admission of all seven native payloads."""
    comp, scale = component(cell)
    if any(m.readers.shapes_of(p['component']) != m.readers.shapes_of(comp) for p in payloads):
        raise ValueError('native supplied geometry differs from frozen web projection')
    result = rendered.score_capture(png, payloads)
    web = rendered.read_capture(png)
    native = np.array([p['rgb'] for p in payloads], float)
    shapes = m.readers.shapes_of(comp)
    geo = m.readers.geometry(web.shape[:2], shapes, scale)
    interior = []
    for member in range(len(shapes)):
        bins, labels = m.readers.edge_bins(geo, member)
        for i, b in enumerate(bins):
            if b['part'] != 'boundary' and b['shell'] < 0:
                mask = labels == i
                interior.append({**b, 'score': m.score_bin(web[mask], native[:, mask])})
    result['interiorTransfer'] = interior
    background = wave.spec['backgrounds'][wave.scenes[cell.split('/', 1)[1]]['background']]
    if background['kind'] == 'linear-gradient':
        strip = m.gradient_strip(native, np.array([p['noGlass'] for p in payloads]), shapes[0], scale)
        projected = project(cell, png)['strip']
        web_rows = np.asarray(projected['web'])
        native_rows = np.asarray(strip['runs'])
        result['stripTransfer'] = {'native': strip, 'shipped': projected, 'rows': [
            {'yCSS': y, 'score': m.score_bin(web_rows[i:i+1], native_rows[:, i:i+1], minimum=1)}
            for i, y in enumerate(strip['yCSS'])]}
    return result


def transfer():
    frozen = load(HERE / 'frozen-baseline.json')
    record = load(HERE / 'preparation.json')
    verify_preparation(record)
    verify_authority(record)
    verify_frozen(record, frozen)
    archive = load_module('baseline_archive', W39 / 'w39_archive.py')
    reader = wave.reader(Path((G0 / 'archive-root.txt').read_text().strip()),
                         roles=('calibration', 'validation'))
    if reader.generation != runner.INVENTORY_SHA: raise ValueError('wrong native archive generation')
    summaries = {}
    for cell, capture in sorted(frozen['captures'].items()):
        if wave.roles[cell.split('/', 1)[1]] not in ('calibration', 'validation'):
            raise PermissionError('baseline transfer never reads holdout')
        png = Path(capture['png'])
        if sha(png) != capture['pngSha256']: raise ValueError('baseline pixel bytes changed')
        runs, states = archive.unbundle(reader.read(cell, 'crop'))
        admitted = [r for r in runs if r['admitted']]
        if len(admitted) != 7 or len({r['run'] for r in admitted}) != 7:
            raise ValueError('seven distinct admitted native repeats required')
        unpacked = {k: archive.unpack(v) for k, v in states.items()}
        data = transfer_projection(cell, png, [unpacked[r['state']] for r in admitted])
        data.update(cell=cell, role=wave.roles[cell.split('/', 1)[1]],
                    nativeRuns=[{'run': r['run'], 'state': r['state']} for r in admitted],
                    baselinePngSha256=capture['pngSha256'])
        profile, sid = cell.split('/', 1)
        path = HERE / 'transfer' / profile / (sid + '.json.gz')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f: f.write(gzip.compress(stable(data).encode(), mtime=0))
        summaries[cell] = {'report': str(path.relative_to(ROOT)), 'sha256': sha(path),
                           'deepMembers': len(data['deep']), 'exteriorBins': len(data['exterior']),
                           'interiorBins': len(data['interiorTransfer']),
                           'stripRows': len(data.get('stripTransfer', {}).get('rows', []))}
    save(HERE / 'transfer-inventory.json', {'recordedAt': stamp(), 'cells': summaries,
         'frozenBaselineSha256': sha(HERE / 'frozen-baseline.json'),
         'nativeGeneration': reader.generation, 'roles': ['calibration', 'validation']})
    print('Transferred', len(summaries), 'baseline cells through guarded native cal/val reads')



def prepare():
    directory = HERE / 'generated-backdrops'
    directory.mkdir()
    backgrounds = {}
    hashes = {}
    size = (wave.spec['canvas']['width'], wave.spec['canvas']['height'])
    for name, definition in sorted(wave.spec['backgrounds'].items()):
        for scale in (1, 2):
            filename = f'{name}@{scale}x.png'
            Image.fromarray(raster(definition, scale, size)).save(directory / filename)
            backgrounds[f'{name}@{scale}x'] = filename
            hashes[filename] = sha(directory / filename)
    save(directory / 'manifest.json', {'schema': 1, 'backgrounds': backgrounds})
    verifier = load_module('baseline_background_verify', W39 / 'verify-backgrounds.py')
    save(HERE / 'generated-background-verification.json', verifier.verify(directory))
    cells, excluded = scope()
    profiles = {}
    for profile in sorted({c.split('/', 1)[0] for c in cells}):
        scheme = next(p['colorScheme'] for p in wave.spec['profiles'] if p['key'] == profile)
        prefix = 'packages/calibration/profiles/apple-macos-27.0-1x-' + scheme + '-standard-glass0.5'
        profiles[profile] = {'material': prefix + '.json', 'receded': prefix + '-receded.json'}
    sources = {p: runner.committed(ROOT, p) for p in runner.sources(ROOT)}
    documents = {p: runner.committed(ROOT, p) for pair in profiles.values() for p in pair.values()}
    runtime = {}
    for p in sorted((ROOT / runner.POLICY_DIST).rglob('*.js')):
        relative = str(p.relative_to(ROOT))
        snapshot = HERE / 'policy-runtime' / p.relative_to(ROOT / runner.POLICY_DIST)
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open('xb') as f: f.write(p.read_bytes())
        runtime[relative] = {'sha256': sha(p), 'snapshot': str(snapshot.relative_to(ROOT))}
    record = {'preparedAt': stamp(), 'sourceRevision': runner.git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
              'cells': cells, 'excludedCells': excluded, 'profiles': profiles,
              'documents': documents, 'sources': sources, 'runtimeArtifacts': runtime,
              'generatedBackgrounds': hashes, 'scenesSha256': wave.scenes_sha,
              'splitSha256': wave.split_sha, 'inventorySha256': runner.INVENTORY_SHA,
              'backdrops': str(directory.relative_to(ROOT)),
              'provenance': 'All rasters generated from public W39 scene definitions; no native payload read.'}
    save(HERE / 'preparation.json', record)
    print('Prepared', len(cells), 'admitted cal/val cells;', len(backgrounds), 'public rasters')


def verify_preparation(record):
    if set(runner.sources(ROOT)) != set(record['sources']):
        raise ValueError('source inventory changed since pre-W41 baseline preparation')
    for name, digest in {**record['sources'], **record['documents']}.items():
        if sha(ROOT / name) != digest: raise ValueError('source/document changed: ' + name)
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / runner.POLICY_DIST).rglob('*')
              if p.is_file() and p.suffix in ('.js', '.mjs', '.cjs')}
    if actual != set(record['runtimeArtifacts']): raise ValueError('policy module inventory changed')
    for name, info in record['runtimeArtifacts'].items():
        if sha(ROOT / name) != info['sha256']: raise ValueError('policy runtime changed: ' + name)
    for name, digest in record['generatedBackgrounds'].items():
        if sha(ROOT / record['backdrops'] / name) != digest: raise ValueError('backdrop changed: ' + name)
    cells, _ = scope()
    if cells != record['cells']: raise ValueError('baseline membership changed')


def authority_inputs(record):
    return [HERE / 'preparation.json', ROOT / record['backdrops'] / 'manifest.json',
            W39 / 'supplied-paths.json', HERE / 'baseline.py', HERE.parent / 'x6/observe.py']


def seal_authority(record):
    # Seal after committing this projection and X6 guard; do not rewrite preparation evidence.
    for path in authority_inputs(record)[-2:]:
        runner.committed(ROOT, str(path.relative_to(ROOT)))
    save(HERE / 'authority.json', {'schema': 1, 'sealedAt': stamp(),
         'preparationSha256': sha(HERE / 'preparation.json'),
         'inputs': {str(path.relative_to(ROOT)): sha(path) for path in authority_inputs(record)}})


def verify_authority(record):
    path = HERE / 'authority.json'
    if not path.is_file(): raise ValueError('authority seal missing')
    try:
        runner.committed(ROOT, str(path.relative_to(ROOT)))
    except ValueError as error:
        raise ValueError('authority seal is not committed unchanged') from error
    authority = load(path)
    expected = {str(p.relative_to(ROOT)): p for p in authority_inputs(record)}
    if (authority['schema'] != 1 or authority['preparationSha256'] != sha(HERE / 'preparation.json')
            or set(authority['inputs']) != set(expected)):
        raise ValueError('authority inventory or preparation changed')
    for name, source in expected.items():
        if sha(source) != authority['inputs'][name]:
            raise ValueError('authority input changed: ' + name)


def verify_capture_authority(record, digest):
    verify_authority(record)
    if sha(HERE / 'authority.json') != digest:
        raise ValueError('authority changed during baseline capture')


def verify_frozen(record, frozen):
    try:
        runner.committed(ROOT, str((HERE / 'frozen-baseline.json').relative_to(ROOT)))
    except ValueError as error:
        raise ValueError('frozen baseline is not committed unchanged') from error
    if sha(HERE / 'preparation.json') != frozen['preparationSha256']:
        raise ValueError('baseline preparation changed after freeze')
    if sha(HERE / 'authority.json') != frozen['authoritySha256']:
        raise ValueError('baseline authority changed after freeze')
    if set(frozen['captures']) != set(record['cells']):
        raise ValueError('incomplete baseline freeze')
    for cell, capture in frozen['captures'].items():
        profile, sid = cell.split('/', 1)
        expected = HERE / 'projections' / profile / (sid + '.json')
        if capture['projection'] != str(expected.relative_to(ROOT)) or \
                sha(expected) != capture['projectionSha256']:
            raise ValueError('frozen projection changed: ' + cell)
        png = Path(capture['png'])
        if sha(png) != capture['pngSha256']:
            raise ValueError('baseline pixel bytes changed: ' + cell)
        for name, digest in [('cell__webgpu.json', capture['cellSha256']),
                             ('report__webgpu.json', capture['reportSha256'])]:
            if sha(png.parent / name) != digest:
                raise ValueError('frozen capture descriptor changed: ' + cell)


def capture():
    record = load(HERE / 'preparation.json')
    verify_preparation(record)
    verify_authority(record)
    authority_sha = sha(HERE / 'authority.json')
    # One fresh X6 check immediately before each backend process; no bypass token.
    # The backend starts exactly one full Chromium process per invocation.
    if CAPTURES.exists(): raise FileExistsError('baseline capture root already reserved')
    started = stamp()
    captures = {}
    env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
    env.update(VITREA_SCENES=str(wave.scenes_path),
               VITREA_FIXTURES=str(ROOT / record['backdrops']),
               VITREA_WEB_CAPTURES=str(CAPTURES), VITREA_ALLOW_FALLBACK_ADAPTER='0')
    for profile, documents in sorted(record['profiles'].items()):
        verify_preparation(record)
        verify_capture_authority(record, authority_sha)
        definition = next(p for p in wave.spec['profiles'] if p['key'] == profile)
        scale = int(re.search(r'-(1|2)x-', profile)[1])
        ids = [c.split('/', 1)[1] for c in record['cells'] if c.startswith(profile + '/')]
        command = ['pnpm', '--dir', str(ROOT / 'packages/calibration'), 'exec', 'tsx',
                   'scripts/capture-web.ts', *ids, '--renderer', 'webgpu', '--color-scheme',
                   definition['colorScheme'], '--scale', str(scale), '--out', str(CAPTURES / profile),
                   '--material-profile', str(ROOT / documents['material']),
                   '--receded-profile', str(ROOT / documents['receded'])]
        check = x6.observe()
        save(HERE.parent / 'x6' / f'prelaunch-{profile}-{uuid.uuid4().hex}.json', check)
        if not check['verdict']['passes']: raise PermissionError('X6 refused; no browser launched')
        verify_capture_authority(record, authority_sha)
        if not CAPTURES.exists():
            CAPTURES.mkdir(parents=True, exist_ok=False)
        save(HERE / f'command-{profile}.json', {'at': stamp(), 'argv': command,
                                              'VITREA': {k: v for k, v in env.items() if k.startswith('VITREA_')}})
        with (HERE / f'capture-{profile}.txt').open('x') as log:
            subprocess.run(command, env=env, check=True, stdout=log, stderr=subprocess.STDOUT)
        verify_preparation(record)
        verify_capture_authority(record, authority_sha)
        for sid in ids:
            directory = CAPTURES / profile / sid
            identity = profile + '/' + sid
            cell = load(directory / 'cell__webgpu.json')
            report = load(directory / 'report__webgpu.json')
            if (cell['sceneId'] != sid or cell['renderer'] != 'webgpu' or cell['engine'] != 'chromium'
                    or cell['colorSpace'] != 'srgb' or cell['pixelSize'] != list(runner.dimension(wave, identity))
                    or cell['deterministic'] is not True or cell['repeatNoise'] != 0
                    or report['fallback'] is not None or report['problems']):
                raise ValueError('invalid actual WebGPU capture descriptor: ' + identity)
            for key, field in [('material', 'materialProfile'), ('receded', 'recededProfile')]:
                if report[field]['sha256'] != record['documents'][documents[key]][:12]:
                    raise ValueError('capture drew different material document')
            path = directory / (sid + '__webgpu.png')
            projection = HERE / 'projections' / profile / (sid + '.json')
            save(projection, project(identity, path))
            verify_capture_authority(record, authority_sha)
            captures[identity] = {'png': str(path), 'pngSha256': sha(path),
                                 'cellSha256': sha(directory / 'cell__webgpu.json'),
                                 'reportSha256': sha(directory / 'report__webgpu.json'),
                                 'projection': str(projection.relative_to(ROOT)),
                                 'projectionSha256': sha(projection)}
    verify_preparation(record)
    verify_capture_authority(record, authority_sha)
    if set(captures) != set(record['cells']): raise ValueError('incomplete baseline')
    save(HERE / 'frozen-baseline.json', {'startedAt': started, 'frozenAt': stamp(),
         'sourceRevision': record['sourceRevision'], 'preparationSha256': sha(HERE / 'preparation.json'),
         'authoritySha256': authority_sha, 'captures': captures,
         'candidateOperators': 'none', 'candidateRenders': 'none'})
    print('FROZEN', len(captures), sha(HERE / 'frozen-baseline.json'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['prepare', 'seal-authority', 'capture', 'transfer'])
    args = p.parse_args()
    if args.operation == 'seal-authority':
        record = load(HERE / 'preparation.json')
        verify_preparation(record)
        seal_authority(record)
    else:
        {'prepare': prepare, 'capture': capture, 'transfer': transfer}[args.operation]()


if __name__ == '__main__': main()
