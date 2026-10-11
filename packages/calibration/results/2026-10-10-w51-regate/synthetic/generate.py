"""W51-DL3 independent synthetic reference fixture, not Apple measurements.

Only arrays and the existing pure statistic reader produce the evidence. This generator
never opens a real capture, generation, gate result, blind payload or candidate document.
Apple-shaped profile strings are dimension/material SELECTORS, not evidence identities;
the separately named dataset, every scene/component and every fixture generation are new.
The held candidate is supplied separately by the actual instrument, never generated here.

Run with the scientific Python and -I -B. Outputs stay beneath this synthetic directory.
No capture, rendering, execution seal or source authority is created by this command.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import types

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
FIT = HERE.parent.parent/'2026-10-08-w50-g1-fit'
KEY = ('profile', 'renderer', 'scene', 'statistic')
CANVAS = {'width': 320, 'height': 200}
COMPONENT = {'kind': 'rrect', 'size': [208, 112], 'radius': 22}
ORIGIN = 'synthetic'
CURRENT = 'w51-synthetic-current'
REFERENCE = 'w51-synthetic-reference'


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def pin(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))
    return pin(path)


def png(path, rgb):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb).save(path, format='PNG', optimize=False)
    return pin(path)


def statistics():
    path = FIT/'references/statistics.py'
    module = types.ModuleType('w51_synthetic_canonical_statistics')
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def profile(scale, position):
    return f'apple-macos-27.0-{scale}x-dark-standard-glass{position}'


def scene(kind):
    return 'w51-synthetic-'+kind+'__rrect-synthetic__'+('inactive' if kind == 'fine' else 'rest')


def members():
    return [(profile(scale, '0.25'), scale, kind) for scale in (1, 2)
            for kind in ('impulse', 'fine', 'photo')] + [
                (profile(1, '0.5'), 1, 'impulse'), (profile(2, '0.5'), 2, 'text')]


def background(kind, scale):
    """Procedural backgrounds independent of every existing native/web fixture byte."""
    yy, xx = np.indices((CANVAS['height']*scale, CANVAS['width']*scale))
    x, y = (xx+.5)/scale, (yy+.5)/scale
    if kind == 'impulse':
        value = np.zeros((*xx.shape, 3), dtype=np.uint8)
        value[(abs(x-CANVAS['width']/2) < 2) & (abs(y-CANVAS['height']/2) < 2)] = [241, 217, 193]
        return value
    if kind == 'fine':
        v = 27+151*((np.floor(x/7)+np.floor(y/7)) % 2)
        return np.stack([v, v*.88+7, v*.71+13], axis=-1).astype(np.uint8)
    if kind == 'photo':
        # Deterministic multiscale colour fields, not a photograph or copied image.
        broad = 78+27*np.sin(x/43)+21*np.cos(y/29)+18*np.sin((x+y)/61)
        detail = 13*np.sin(x/3.7)*np.cos(y/5.1)+7*np.sin((2*x-y)/2.3)
        return np.clip(np.stack([broad+detail, broad*.8+detail*.6+17,
                                broad*.6-detail*.4+29], axis=-1), 0, 255).astype(np.uint8)
    if kind == 'text':
        # Block-glyph strokes, not system font rasterisation; both low and fine bands exist.
        glyph = ((np.floor(x) % 13 < 2) | (np.floor(y) % 11 < 2)) & (np.floor(y/22) % 2 == 0)
        v = 41+18*np.sin(x/39)+12*np.cos(y/31)+111*glyph
        return np.repeat(np.clip(v[..., None], 0, 255), 3, axis=2).astype(np.uint8)
    raise ValueError('Unknown synthetic background')


def image(background_rgb, scale, kind, side, run=1):
    """An independent artificial body, deliberately not a vitrea/Apple material model."""
    yy, xx = np.indices(background_rgb.shape[:2], dtype=float)
    x = abs((xx+.5)/scale-CANVAS['width']/2)-(COMPONENT['size'][0]/2-COMPONENT['radius'])
    y = abs((yy+.5)/scale-CANVAS['height']/2)-(COMPONENT['size'][1]/2-COMPONENT['radius'])
    distance = np.hypot(np.maximum(x, 0), np.maximum(y, 0)) + np.minimum(np.maximum(x, y), 0)
    mask = distance <= COMPONENT['radius']
    width, gain, floor = {'native': (1.7, .44, 29), 'current': (2.1, .53, 35),
                          'reference': (2.8, .64, 41)}[side]
    blurred = gaussian_filter(background_rgb.astype(float), (width*scale, width*scale, 0), mode='reflect')
    wave = 3*np.sin((xx+.5)/(19*scale))+2*np.cos((yy+.5)/(23*scale))
    # Seven independently stored repeats have deterministic small level perturbations.
    delta = (0, 1, -1, 0, 1, -1, 0)[run-1] if side == 'native' else 0
    body = np.clip(np.rint(floor+gain*blurred+wave[..., None]+delta), 0, 255).astype(np.uint8)
    result = background_rgb.copy()
    result[mask] = body[mask]
    return result


def scene_document():
    kinds = ('impulse', 'fine', 'photo', 'text')
    return {'version': 1, 'dataOrigin': ORIGIN, 'dataset': 'w51-synthetic',
        '$comment': 'Generated arrays only; profile keys select dimensions/material, not Apple evidence.',
        'canvas': CANVAS, 'components': {'rrect-synthetic': COMPONENT},
        'backgrounds': {'w51-synthetic-'+kind: {'kind': 'impulse' if kind == 'impulse' else 'image',
            'dataOrigin': ORIGIN, 'source': 'generated PNG dependency'} for kind in kinds},
        'states': {'rest': {}, 'inactive': {}}, 'tints': {},
        'scenes': [{'id': scene(kind), 'background': 'w51-synthetic-'+kind,
                    'component': 'rrect-synthetic', 'state': 'inactive' if kind == 'fine' else 'rest'}
                   for kind in kinds],
        'profiles': [{'key': p, 'colorScheme': 'dark', 'a11y': 'standard', 'dataOrigin': ORIGIN,
                      'scenes': [scene(kind) for pp, _, kind in members() if pp == p]}
                     for p in sorted({p for p, _, _ in members()})],
        'split': {'calibration': [scene(k) for k in kinds], 'validation': [], 'holdout': [],
                  'recorded': [], 'probe': []}}


def build(output):
    output = Path(output).resolve()
    if not output.is_relative_to(HERE) or output == HERE:
        raise ValueError('Synthetic outputs must stay in a child of the owned synthetic directory')
    output.mkdir(parents=True, exist_ok=True)
    S = statistics()
    scenes = scene_document()
    scenes_pin = write(output/'scenes.json', scenes)
    manifest_pin = write(output/'native-manifest.json', {'schema': 'w51-synthetic-native-manifest-1',
        'dataOrigin': ORIGIN, 'cells': [], 'references': [], 'canvas': CANVAS,
        'note': 'No newbed or Apple/native-capture rows; canonical fixture records own all pixels.'})
    batch_pin = write(output/'native-batch.json', {'schema': 'w50-native-read-batch-1',
        'dataOrigin': ORIGIN, 'inputs': {'scenes': scenes_pin, 'manifest': manifest_pin}, 'runs': []})
    reports = {role: write(output/('native-'+role+'.json'), {
        'schema': 'w50-native-role-read-1', 'dataOrigin': ORIGIN, 'role': role, 'cells': [],
        'note': 'Empty by declaration: this fixture has only canonical rows, no newbed reads.'})
        for role in ('calibration', 'validation')}
    fixture_root = output/'native-fixtures'
    backgrounds = {}
    images = []
    for p, scale, kind in members():
        directory = output/'pixels'/p/scene(kind)
        bg = background(kind, scale)
        pins = {'background': png(directory/'background.png', bg)}
        generated = {side: image(bg, scale, kind, side) for side in ('native', 'current', 'reference')}
        for side, rgb in generated.items():
            pins[side] = png(directory/(side+'.png'), rgb)
        # The real native-admission transport requires this exact fixture-root layout.
        # These bytes still come only from the arrays above, not a native capture.
        pins['native'] = png(fixture_root/p/(scene(kind)+'.png'), generated['native'])
        name = 'w51-synthetic-'+kind+'@'+str(scale)+'x'
        background_path = fixture_root/'backgrounds'/(name+'.png')
        png(background_path, bg)
        backgrounds[name] = str(background_path.relative_to(fixture_root))
        pins['currentMetadata'] = write(directory/'current.json', {'dataOrigin': ORIGIN,
            'schema': 'w51-synthetic-current-fixture-1', 'sceneId': scene(kind), 'profile': p,
            'renderer': 'webgpu', 'colorSpace': 'srgb', 'pixelSize': [CANVAS['width']*scale, CANVAS['height']*scale],
            'capturePath': 'SYNTHETIC_ARRAY_FIXTURE_NOT_A_CAPTURE', 'image': pins['current']})
        # The 0.25 fine cell retains its F full-T1 target and adds the same Gaussian-band
        # reading as text, so the unchanged frozen-low projection has its own rehearsal key.
        bands = kind == 'text' or (kind == 'fine' and scale == 2 and p.endswith('glass0.25'))
        options = {'text': bands, 'impulse': kind == 'impulse'}
        published = S.canonical_read(generated['native'], bg, COMPONENT, CANVAS, scale,
                                     web_rgb=generated['current'], **options)
        old = S.canonical_read(generated['native'], bg, COMPONENT, CANVAS, scale,
                              web_rgb=generated['reference'], **options)
        repeats = []
        for run in range(1, 8):
            rgb = image(bg, scale, kind, 'native', run)
            frame = png(directory/f'repeat-{run}.png', rgb)
            repeats.append({'label': 'r'+str(run), 'run': run, 'dataOrigin': ORIGIN,
                'frame': frame, 'background': pins['background'],
                'reading': S.canonical_read(rgb, bg, COMPONENT, CANVAS, scale, **options)})
        readings = S.evidence_reading(published, [r['reading'] for r in repeats])
        if any(r['status'] != 'MEASURED' for r in readings.values()):
            raise ValueError('A generated canonical support is empty')
        images.append({'profile': p, 'scale': scale, 'kind': kind, 'pins': pins,
                       'published': published, 'old': old, 'runs': repeats, 'readings': readings})
    fixture_manifest_pin = write(fixture_root/'manifest.json', {
        'schemaVersion': 2, 'sceneSpecVersion': scenes['version'], 'dataOrigin': ORIGIN,
        'backgrounds': backgrounds, 'caveats': [
            'SYNTHETIC arrays, not Apple measurements. materialRendered means the generated body is present.',
            'capturedAt is a fixed schema-compatible synthetic epoch, not a capture timestamp.'],
        'profiles': [{'profileKey': p, 'dataOrigin': ORIGIN, 'colorScheme': 'dark',
            'a11yMode': 'standard', 'display': {'actualBackingScale': scale},
            'fixtures': [{'sceneId': scene(im['kind']), 'profile': p, 'dataOrigin': ORIGIN,
                'file': str(Path(im['pins']['native']['path']).relative_to(fixture_root)),
                'fixtureSet': 'calibration', 'materialRendered': True,
                'captureMethod': 'synthetic-array-generator',
                'capturedAt': '1970-01-01T00:00:00.000Z'} for im in images if im['profile'] == p]}
            for p, scale in sorted({(p, scale) for p, scale, _ in members()})]})
    generations = {}
    for generation, side in ((CURRENT, 'current'), (REFERENCE, 'reference')):
        identities = {}
        for pose in ('active', 'receded'):
            identities[pose+'.dark'] = write(output/'identities'/(generation+'-'+pose+'.json'), {
                'schema': 'w51-synthetic-fixture-identity-1', 'dataOrigin': ORIGIN,
                'generation': generation, 'pose': pose, 'materialDocument': False,
                'meaning': 'Identity of generated reference arrays, never frozen candidate bytes.',
                'images': [im['pins'][side] for im in images
                           if (im['kind'] == 'fine') == (pose == 'receded')]})
        generations[generation] = {'dataOrigin': ORIGIN, 'fixtureIdentityPins': identities,
            'documentPair': {slot: item['sha256'] for slot, item in identities.items()}}
    pair = generations[CURRENT]['documentPair']
    rows, records, cuts = [], [], []
    for im in images:
        p, kind = im['profile'], im['kind']
        primary = 'T1-low' if kind == 'text' else 'T1-full-silhouette'
        names = [primary]+(['low-end-path-level'] if kind == 'impulse' else [])
        if primary != 'T1-low' and 'T1-low' in im['readings']:
            names.append('T1-low')
        stratum = {'impulse': 'C', 'fine': 'F', 'photo': 'P', 'text': 'T'}[kind]
        for name in names:
            row = {'profile': p, 'renderer': 'webgpu', 'scene': scene(kind), 'statistic': name,
                'dataOrigin': ORIGIN, 'role': 'gate', 'currentGeneration': CURRENT,
                'currentDocumentPair': copy.deepcopy(pair), 'historical': [], 'status': 'MEASURED',
                'nativeEvidence': im['pins']['native'], 'currentEvidence': im['pins']['current'],
                'currentMetadata': im['pins']['currentMetadata'], 'currentMaxGrowthInB': 1}
            if name == 'low-end-path-level':
                row.update(support='supplied path deep8/far24; encoded-luma mean and median', B=None)
            else:
                reading = im['readings'][name]
                fidelity_name = 'T1-fine' if name == 'T1-low' else name
                fidelity = im['readings'][fidelity_name]
                row.update(stratum=stratum, support=reading['support'],
                    **{k: reading[k] for k in ('native', 'current', 'B')},
                    fidelity={'statistic': fidelity_name, 'native': fidelity['native'],
                              'current': fidelity['current'],
                              'reference': im['old']['web']['statistics'][fidelity_name]['value']})
                if p.endswith('glass0.25') and name == 'T1-full-silhouette':
                    cuts.append({'profile': p, 'scene': scene(kind), 'tier': 'webgpu',
                        'scale': im['scale'], 'pose': 'inactive' if kind == 'fine' else 'rest',
                        'stratum': stratum, 'native': row['native'], 'candidate': row['current'],
                        'reference': row['fidelity']['reference'], 'B': row['B'],
                        'code': reading['repeat']['code'], 'bar': reading['repeat']['bar'], 'dataOrigin': ORIGIN})
            rows.append(row)
            records.append({**{k: row[k] for k in KEY}, 'dataOrigin': ORIGIN, 'role': 'gate',
                'status': 'MEASURED', 'row': copy.deepcopy(row), 'reference': copy.deepcopy(row),
                'readings': im['readings'], 'publishedReading': im['published'], 'runs': im['runs'],
                'pins': {**im['pins'], 'scenes': scenes_pin, 'publishedManifest': fixture_manifest_pin},
                'source': {'kind': 'synthetic', 'selectedRuns': ['r1', 'r4', 'r7'],
                           'frameHashBinding': 'own independently generated array PNGs'}})
    rows.sort(key=lambda r: tuple(r[k] for k in KEY))
    records.sort(key=lambda r: tuple(r[k] for k in KEY))
    inventory = {'schema': 'w50-reference-inventory-1', 'dataOrigin': ORIGIN,
                 'dataset': 'w51-synthetic', 'generations': generations, 'cells': rows}
    inventory_pin = write(output/'inventory.json', inventory)
    write(output/'completed-references.json', inventory)
    write(output/'canonical-reference-evidence.json', {'schema': 'w50-canonical-reference-evidence-1',
        'dataOrigin': ORIGIN, 'partitions': {'gate': records, 'historical-prediction-check': [],
                                          'reference-only': []}})
    composition_pin = write(output/'current-composition.json', {
        'schema': 'w51-synthetic-current-composition-1', 'dataOrigin': ORIGIN,
        'source': 'generated array PNG fixtures, not a completed capture instrument',
        'members': [im['pins']['current'] for im in images]})
    write(output/'completed-current-evidence.json', {'schema': 'w50-completed-current-evidence-2',
        'status': 'EVIDENCE_ONLY', 'dataOrigin': ORIGIN, 'currentComposition': composition_pin,
        'originals': {'references': inventory_pin, 'scenes': scenes_pin},
        'native': {'batch': batch_pin, 'reports': reports}, 'referenceEvidence': []})
    cut_pin = write(output/'targets-cut.json', {'dataOrigin': ORIGIN, 'T1': {'cells': cuts}})
    write(output/'targets-config.json', {'schema': 'w50-target-contract-config-1',
        'inventory': inventory_pin, 'cut': cut_pin, 'currentGeneration': CURRENT, 'w48Generation': REFERENCE})
    keys = [[row[k] for k in KEY] for row in rows]
    physical = sorted({tuple(k[:3]) for k in keys})
    write(output/'population.json', {'schema': 'w51-population-1', 'phase': 'rehearsal',
        'dataset': 'synthetic', 'dataOrigin': ORIGIN, 'populationClass': 'SYNTHETIC',
        'sourceInventory': inventory_pin, 'physicalCount': len(physical), 'statisticCount': len(keys),
        'physicalCells': [list(k) for k in physical], 'statisticKeys': keys,
        'originalMetadata': [{**{k: row[k] for k in KEY}, 'role': row['role'],
            'support': row['support'], 'sceneSource': 'canonical'} for row in rows],
        'coverage': {'reportedKeys': 0, 'eligibleEmptySupportKeys': 0}})
    files = [pin(p) for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'fixture.json']
    return write(output/'fixture.json', {'schema': 'w51-synthetic-fixture-1', 'dataOrigin': ORIGIN,
        'dataset': 'w51-synthetic', 'physicalCount': len(physical), 'statisticCount': len(keys),
        'fixtureRoot': str(fixture_root), 'fixtureManifest': fixture_manifest_pin,
        'profileKeyMeaning': 'Dimension/material selectors only; not Apple measurement provenance.',
        'candidatePolicy': 'Original frozen candidate supplied separately and unchanged.',
        'files': files})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE/'generated')
    args = parser.parse_args()
    result = build(args.out)
    print(json.dumps({'fixture': result, 'physicalCount': 8, 'statisticCount': 12}, sort_keys=True))
