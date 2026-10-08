#!/usr/bin/env python3.12
"""W50's fixed 1,600-frame bed. Generation and verification do not launch the native app.

The W43 plan schema is retained as a transport, not as a W43 declaration. Its validator and
W42-calibrated estimator are reused without changing historical code. Operational sentinels
are duplicated identities so the harness's sorted order really brackets each repetition.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
W43 = ROOT / 'packages/calibration/results/2026-10-01-w43-g0-declaration/bed/sitting'
LEVELS = (*range(9), 12, 20, 28, 40, 64)
CALIBRATION = {0, 2, 4, 8, 28, 40, 64}
VALIDATION = {1, 3, 5, 6, 12}
MODS = {}


def load(name, path):
    if name not in MODS:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        MODS[name] = mod
    return MODS[name]


def pass_spec():
    p = load('w50_pass_spec', W43 / 'pass-spec.py')
    p.SITTINGS = ('g1',)
    p.CLOSE_ROLE = 'bridge-w50-canonical'
    p.BED_DIR = HERE
    return p


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(doc):
    return (json.dumps(doc, indent=2, allow_nan=False) + '\n').encode()


def committed(rel):
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'HEAD:{rel}'])
    if (ROOT / rel).read_bytes() != raw:
        raise ValueError(f'Committed reference changed: {rel}')
    return raw


def canonical():
    return json.loads(committed('apps/reference-apple/scenes.json'))


def key(scale, glass):
    return f'apple-macos-27.0-{scale}x-dark-standard-glass{glass:g}'


def cell_specs():
    for span in (44, 96, 160):
        for level in LEVELS:
            role = 'calibration' if level in CALIBRATION else ('validation' if level in VALIDATION else 'blind')
            yield dict(background=f'grey-{level:03}', level=level, span=span, role=role, family='uniform')
    for span in (128, 224):
        for level in (0, 4, 28, 64):
            yield dict(background=f'grey-{level:03}', level=level, span=span,
                       role='validation' if span == 128 else 'blind', family='span')
    for span in (96, 160, 224):
        yield dict(background='impulse-sparse', span=span, family='structured',
                   role={96: 'calibration', 160: 'validation', 224: 'blind'}[span])
        yield dict(background='checker-low', span=span, family='structured', role='blind')


def build():
    canonical_doc = canonical()
    backgrounds = {f'grey-{v:03}': dict(kind='solid', srgb=[v]*3) for v in LEVELS}
    backgrounds.update({'impulse-sparse': dict(kind='impulse', background=[0]*3, foreground=[255]*3,
                                              size=4, spacing=96),
                        'checker-low': dict(kind='checkerboard', cell=16, a=[0]*3, b=[8]*3)})
    sizes = {44: [120, 44], 96: [168, 96], 128: [224, 128], 160: [280, 160], 224: [392, 224]}
    components = {'none': dict(kind='none')}
    components.update({f'span-{s}': (dict(kind='capsule', size=size) if s == 44 else
                                   dict(kind='rrect', size=size, radius=s*0.2125)) for s, size in sizes.items()})
    scenes, split = [], {r: [] for r in ('calibration', 'validation', 'holdout', 'recorded', 'probe')}
    specs = list(cell_specs())
    for state in ('rest', 'inactive'):
        for c in specs:
            sid = f'cell-{c["background"]}-s{c["span"]:03}__{state}'
            scenes.append(dict(id=sid, background=c['background'], component=f'span-{c["span"]}', state=state))
            split['holdout' if c['role'] == 'blind' else c['role']].append(sid)
        for bg in backgrounds:
            sid = f'ref-{bg}__{state}'
            scenes.append(dict(id=sid, background=bg, component='none', state=state))
            # Dependency membership lives in manifest.json, not a misleading public role label.
            split['recorded'].append(sid)
        for end in ('00-open', 'zz-close'):
            for v in (0, 64):
                sid = f'{end}-grey-{v:03}__{state}'
                scenes.append(dict(id=sid, background=f'grey-{v:03}', component='span-160', state=state))
                split['recorded'].append(sid)
    scenes.sort(key=lambda s: s['id'])
    doc = dict(version=1, canvas=dict(width=512, height=384), backgrounds=backgrounds,
               components=components, states={s: canonical_doc['states'][s] for s in ('rest', 'inactive')},
               scenes=scenes, split=split, profiles=[dict(key=key(scale, glass), colorScheme='dark',
               a11y='standard', scenes=[s['id'] for s in scenes]) for scale in (1, 2) for glass in (0.5, 0.25)])
    manifest = dict(schema='w50-native-bed-1', canvas=doc['canvas'], cells=[], references=[],
                    sentinels=dict(levels=[0, 64], span=160, perRun=4),
                    repeatRule=dict(runs=3, maxRequiredSpreadCodes=1, barFloorCodes=0.5),
                    supports=dict(deep='supplied native path, >=8 CSS px inward',
                                  center='central 8x8 CSS px', impulse='deep8 and >=24 CSS px from dot'))
    passes, closes = [], []
    for scale in (1, 2):
        for glass in (0.5, 0.25):
            for pose, state in (('active', 'rest'), ('receded', 'inactive')):
                profile = key(scale, glass)
                tag = f'x{glass:g}-{scale}x-{pose}'
                ids = [s['id'] for s in scenes if s['state'] == state and not s['id'].startswith('ref-')]
                refs = [s['id'] for s in scenes if s['state'] == state and s['id'].startswith('ref-')]
                for c in specs:
                    sid = f'cell-{c["background"]}-s{c["span"]:03}__{state}'
                    manifest['cells'].append(dict(c, id=f'{profile}/{sid}', scene=sid, profile=profile,
                        pose=pose, scale=scale, glass=glass, passName=f'bed-{tag}',
                        reference=f'{profile}/ref-{c["background"]}__{state}', runs=[1, 2, 3]))
                for bg in backgrounds:
                    roles = sorted({c['role'] for c in specs if c['background'] == bg})
                    sid = f'ref-{bg}__{state}'
                    manifest['references'].append(dict(id=f'{profile}/{sid}', scene=sid, profile=profile,
                        background=bg, roles=roles, passName=f'bed-{tag}', run=1))
                bridge_ids = [f'{b}__rrect-lg__{state}' for b in ('dark-solid', 'impulse')]
                bridges = {}
                for sid in bridge_ids:
                    rel = f'apps/reference-apple/fixtures/{profile}/{sid}.png'
                    bridges[f'{profile}/{sid}'] = dict(reference=dict(path=rel, sha256=sha(committed(rel))))
                base = dict(kind='capture', role='bridge-w50-canonical', glass=glass, scale=scale,
                            pose=pose, source='canonical', runs=1, protocol='normal', profiles={profile: bridge_ids},
                            publish=False)
                passes.append(dict(base, name=f'open-{tag}', bridge=dict(stop=True, cells=bridges)))
                passes.append(dict(name=f'bed-{tag}', kind='capture', role='low-end', glass=glass, scale=scale,
                    pose=pose, source='w50', runs=3, protocol='normal', profiles={profile: ids},
                    run1Only={profile: refs}, publish=False))
                closes.append(dict(base, name=f'close-{tag}', bridge=dict(stop=False, cells=bridges), runAfterCut=True))
    plan = dict(schema='w43-sitting-plan-1', sitting='g1', sources={
        'w50': dict(path=str((HERE/'scenes-w50.json').relative_to(ROOT)), sha256=sha(encoded(doc))),
        'canonical': dict(path='apps/reference-apple/scenes.json',
                          sha256=sha(committed('apps/reference-apple/scenes.json')))}, passes=passes+closes)
    pass_spec().validate_plan(plan, {'w50': doc, 'canonical': canonical_doc})
    return doc, manifest, plan


def products():
    doc, manifest, plan = build()
    timing = load('w50_timing', W43/'timing.py')
    timing.pass_spec = pass_spec
    rates = timing.measure()
    price = timing.price(plan, {'w50': doc, 'canonical': canonical()}, rates)
    price['reservedHours'] = round(price['exactTotalSeconds'] * 1.1 / 3600 + 0.5, 3)
    price['allowance'] = '10% stop loss plus 30 minutes setup, slider/display restore and grant handling'
    return {'scenes-w50.json': doc, 'manifest.json': manifest, 'sitting-g1.json': plan,
            'timing.json': dict(rates=rates, price=price)}


def verify():
    """The declaration's callable seam: derive/validate first, then return all input byte hashes."""
    hashes = {}
    for name, value in products().items():
        raw = encoded(value)
        if (HERE/name).read_bytes() != raw:
            raise ValueError(f'Bed differs from its generator: {name}')
        hashes[str((HERE/name).relative_to(ROOT))] = sha(raw)
    return hashes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('write', 'check'))
    args = parser.parse_args()
    if args.command == 'write':
        for name, value in products().items():
            path = HERE/name
            if path.exists() and path.read_bytes() != encoded(value):
                raise ValueError(f'Refuse overwrite of existing declaration product: {path}')
            path.write_bytes(encoded(value))
    else:
        verify()
    print(json.dumps(products()['timing.json']['price']['totals']))
