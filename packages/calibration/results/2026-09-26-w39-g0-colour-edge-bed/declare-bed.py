#!/usr/bin/env python3
"""Reproduce the W39 declaration from its pre-capture cell lists; never tune pixels."""
import copy
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ROLES = ('calibration', 'validation', 'holdout')


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shape(size=(120, 44), position=(160, 140), kind='capsule-circular', opaque=False, fill=255):
    result = dict(kind=kind, size=list(size), position=list(position))
    if kind == 'rrect':
        result['radius'] = 22
    if opaque:
        result.update(opaque=True, fillSRGB=[fill] * 3)
    return result


def phase_shapes(scale, integer=False):
    rows = [('zero', 'zero', (120, 44))]
    for axis in ('x', 'y'):
        for n in (1, 2, 3):
            size = (120 + n / (4 * scale), 44) if axis == 'x' else (120, 44 + n / (4 * scale))
            rows.append((f'{axis}{n}', axis, size))
    if integer:
        rows.extend([('x-integer', 'x', (121, 44)), ('y-integer', 'y', (120, 45))])
    return [(name, axis, shape(size, (100 + size[0] / 2, 118 + size[1] / 2), 'rrect'))
            for name, axis, size in rows]


def document(backgrounds, components, scenes, preflight=False):
    profiles = []
    for scale in (1, 2):
        for scheme in (('light',) if preflight else ('light', 'dark')):
            profiles.append(dict(key=f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5',
                colorScheme=scheme, a11y='standard',
                scenes=[s['id'] for s in scenes if s.get('$scale', scale) == scale]))
    return dict(version=1, canvas=dict(width=320, height=280), backgrounds=backgrounds,
        components=components, scenes=scenes, profiles=profiles, tints={},
        split=dict(calibration=[], validation=[], holdout=[], probe=[s['id'] for s in scenes]),
        **{'$comment': dict(purpose='W39 probe-only preflight' if preflight else 'W39 colour and signed edge identification',
            phase='Separate 1x/2x component and scene variants keep device-quarter increments divided by scale without adding a scale-keyed native size parser.',
            registration='Colour cells borrow g128 centre circular-120 opaque registration; ordinary fill does not attest glass coverage.',
            bridge='g128 centre, red and green circular-120 bridge W34 geometry/backdrop at a DIFFERENT 320x280 canvas, never identical captures.',
            reference='Colour no-glass scenes run only in run1 of each normal pass; edge references run every normal run.',
            split='Fixture roles probe only. Identification split.json is independent and receipt guarded.')})


def semantic_shape(c):
    # Compare relative geometry, independent of canvas/position/pose/tint. This
    # conservative twin audit must not launder an old holdout through translation.
    return {k: v for k, v in c.items() if k in ('kind', 'size', 'radius')}


def main():
    colours = json.loads((HERE / 'colour-cells.json').read_text())
    edge = json.loads((HERE / 'edge-cells.json').read_text())
    assert len(colours) == 61 and all(40 <= v <= 150 for c in colours for v in c['srgb'])
    bg = {f'g{v}': dict(kind='solid', srgb=[v] * 3) for v in (128, 255)}
    bg.update({f'v{a}': dict(kind='linear-gradient', **{'from': [64] * 3, 'to': [192] * 3}, angle=a) for a in (90, 270)})
    bg.update({c['id']: dict(kind='solid', srgb=c['srgb']) for c in colours})
    bg.update(red=dict(kind='solid', srgb=[192, 32, 32]), green=dict(kind='solid', srgb=[32, 192, 32]))
    components = {'none': dict(kind='none'), 'colour-circular': shape()}
    base = []
    for cell in edge:
        name = cell['id']; opaque = name.endswith('-opaque'); kind = cell['component']
        if kind == 'none':
            component = 'none'
        else:
            component = name
            fill = 0 if cell['background'] == 'g255' else 255
            if kind.startswith('column'):
                # Two distinguishable fills keep both ordinary-fill paths measurable.
                components[name] = dict(kind='column', items=[
                    shape(position=p, opaque=opaque, fill=(255 if i == 0 else 0))
                    for i, p in enumerate(cell['position'])])
            else:
                size = tuple(map(int, re.search(r'(\d+)x(\d+)', kind).groups()))
                components[name] = shape(size, cell['position'], 'rrect' if kind.startswith('rrect') else 'capsule-circular', opaque, fill)
        role = 'calibration'
        if name.startswith(('g255-b-c44', 'g255-c-circular-200x44', 'g128-c-capsule-circular-160x96')):
            role = 'holdout'
        elif any(part in name for part in ('rrect-120x96', 'capsule-circular-120x96', 'capsule-circular-96x96')):
            role = 'validation'
        row = dict(id=name, background=cell['background'], component=component,
                   **{'$class': 'edge', '$role': role})
        if kind != 'none':
            row['$pair'] = name[:-7] if opaque else name + '-opaque'
        if name == 'g128-c-c44':
            row['$bridge'] = True
        base.append(row)
    for c in colours + [dict(id='red', role='calibration'), dict(id='green', role='calibration')]:
        role = 'holdout' if c['role'] == 'held-out-colour' else c['role']
        base.append(dict(id=c['id'] + '-colour', background=c['id'], component='colour-circular',
                         **{'$class': 'colour', '$role': role, '$bridge': c['id'] in ('red', 'green')}))
        base.append(dict(id=c['id'] + '-ref', background=c['id'], component='none',
                         **{'$class': 'colour-reference', '$role': role}))
    for scale in (1, 2):
        for name, axis, component in phase_shapes(scale):
            for opaque in (False, True):
                cid = f'phase-{scale}x-{name}' + ('-opaque' if opaque else '')
                comp = copy.deepcopy(component)
                if opaque:
                    comp.update(opaque=True, fillSRGB=[255] * 3)
                components[cid] = comp
                base.append(dict(id=cid, background='g128', component=cid,
                    **{'$class': 'phase', '$scale': scale, '$phaseAxis': axis,
                       '$role': 'calibration', '$pair': cid[:-7] if opaque else cid + '-opaque'}))
    scenes = []
    split = dict(schema='w39-split-1', calibration=[], validation=[], holdout=[], dependencies={})
    for pose in ('rest', 'inactive'):
        for row in base:
            s = {k: v for k, v in row.items() if k != '$role'}
            s.update(id=row['id'] + '__' + pose, state=pose)
            if '$pair' in s:
                s['$pair'] += '__' + pose
            scenes.append(s); split[row['$role']].append(s['id'])
            c = components[s['component']]
            native_control = c['kind'] == 'none' or c.get('opaque') or any(m.get('opaque') for m in c.get('items', []))
            if not native_control:
                colour = row['$class'] == 'colour'
                opaque = 'g128-c-c44-opaque' if colour else row['id'] + '-opaque'
                reference = s['background'] + '-ref'
                split['dependencies'][s['id']] = dict(noGlass=reference + '__' + pose, opaque=opaque + '__' + pose)
    spec = document(bg, components, scenes)
    # Read declaration files only. W34 identification holdout membership is not
    # pixel data; audit it without deserialising any archive payload.
    canonical = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())
    w34 = json.loads((ROOT / 'apps/reference-apple/scenes-w34-contour.json').read_text())
    audit = []
    excluded = set()
    for s in scenes:
        c = components[s['component']]
        if c['kind'] == 'none' or c.get('opaque') or c['kind'] == 'column':
            continue
        matches = []
        for source, old in [('canonical', canonical), ('W34', w34)]:
            roles = {sid: role for role, ids in old['split'].items() if not role.startswith('$') for sid in ids}
            for previous in old['scenes']:
                pc = old['components'][previous['component']]
                if pc.get('opaque') or previous.get('label'):
                    continue
                if semantic_shape(c) == semantic_shape(pc) and bg[s['background']] == old['backgrounds'][previous['background']]:
                    matches.append(dict(source=source, scene=previous['id'], role=roles.get(previous['id']),
                        sameCanvas=old['canvas'] == spec['canvas'], canvas=old['canvas'],
                        disposition='BRIDGE: same geometry/backdrop, different canvas' if source == 'W34' and s.get('$bridge') else 'semantic twin'))
                    if source == 'canonical' and roles.get(previous['id']) == 'holdout':
                        excluded.add(s['id'])
                        if '$pair' in s:
                            excluded.add(s['$pair'])
        audit.append(dict(scene=s['id'], matches=matches))
    for sid in excluded:
        for role in ROLES:
            if sid in split[role]:
                split[role].remove(sid)
        split['holdout'].append(sid)
    for role in ROLES:
        split[role].sort()
    precomponents = {}; prescenes = []
    for scale in (1, 2):
        for name, axis, component in phase_shapes(scale, integer=True):
            for opaque in (False, True):
                cid = f'preflight-{scale}x-{name}' + ('-opaque' if opaque else '')
                comp = copy.deepcopy(component)
                if opaque:
                    comp.update(opaque=True, fillSRGB=[255] * 3)
                precomponents[cid] = comp
                prescenes.append(dict(id=cid + '__rest', background='g128', component=cid, state='rest',
                    **{'$class': 'preflight', '$scale': scale, '$phaseAxis': axis,
                       '$geometry': name, '$pair': (cid[:-7] if opaque else cid + '-opaque') + '__rest'}))
    preflight = document({'g128': bg['g128']}, precomponents, prescenes, preflight=True)
    paths = [ROOT / 'apps/reference-apple/scenes-w39-colour-edge.json', ROOT / 'apps/reference-apple/scenes-w39-preflight.json']
    write(paths[0], spec); write(paths[1], preflight); write(HERE / 'split.json', split)
    write(HERE / 'semantic-twin-audit.json', dict(canonicalScenesSha256=sha(ROOT / 'apps/reference-apple/scenes.json'),
        w34ScenesSha256=sha(ROOT / 'apps/reference-apple/scenes-w34-contour.json'), rows=audit,
        compared=['relative geometry', 'backdrop declaration'], ignoredConservatively=['position', 'canvas', 'pose', 'tint'],
        excludedFromCalibrationAndValidation=sorted(excluded), holdoutPixelsOpened=False))
    write(HERE / 'pins.json', dict(scenesSha256=sha(paths[0]), preflightScenesSha256=sha(paths[1]),
        splitSha256=sha(HERE / 'split.json'), boundsDeclarationSha256=sha(HERE / 'bounds-declaration.txt')))
    print(json.dumps(dict(scenes=len(scenes), preflight=len(prescenes), split={r: len(split[r]) for r in ROLES},
                         canonicalHoldoutTwins=sorted(excluded))))


if __name__ == '__main__':
    main()
