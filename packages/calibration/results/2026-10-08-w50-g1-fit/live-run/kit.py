"""Test helper (not a tool): live-roles/livekit.EndToEnd's synthetic world, seen by live-run.

livekit's world registers the real dispatcher and all seven real roles over a synthetic
repository, but its declarations are not complete G0 documents: its new-bed scene document
lacks the exposed uniform cells, it has no canonical scene document, and its root has no
current composition. These give batches.py what the real part 2 and current chain give it,
derived from the world's own reference rows, so the batches built here are the ones its
dispatcher validates and runs.
"""
import copy
import importlib.util
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
FIT = HERE.parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value; spec.loader.exec_module(value); return value


K = module(FIT/'live-roles/livekit.py', 'w50_live_run_livekit')
B = module(HERE/'batches.py', 'w50_live_run_kit_batches_'+uuid.uuid4().hex)
SPLIT = {'calibration': 'calibration', 'validation': 'validation', 'blind': 'holdout',
         'historical-prediction-check': 'holdout'}


def scenes(world):
    """{'w50', 'canonical'} scene documents covering every scene the world's references name."""
    newbed = copy.deepcopy(world.scenes)
    canonical = {'scenes': [], 'split': {name: [] for name in ('calibration', 'validation', 'recorded', 'probe', 'holdout')}}
    known = {s['id'] for s in newbed['scenes']}
    roles = {}
    for row in world.rows:
        roles.setdefault(row['scene'], set()).add(row['role'])
    for scene, found in sorted(roles.items()):
        role = SPLIT[sorted(found - {'blind'} or found)[0]]
        state = 'inactive' if scene.endswith('__inactive') else 'rest'
        if scene.startswith('cell-'):
            if scene in known: continue
            background = scene.removeprefix('cell-').split('-s')[0]
            newbed['scenes'].append({'id': scene, 'background': background, 'component': 'span-96', 'state': state})
            newbed['split'][role].append(scene)
        else:
            canonical['scenes'].append({'id': scene, 'state': state})
            canonical['split'][role].append(scene)
    return {'w50': newbed, 'canonical': canonical}


def transport(world, decl):
    """The content-bound run fields a real current chain would give: the world's own closure,
    and fixtures the synthetic new-bed transport reads for every exposed (profile, pose)."""
    fixtures = {}
    for profile, renderer, scene in decl.cells('gate'):
        if decl.scene_source(scene) != 'w50': continue
        key = profile+'|'+decl.pose(scene)
        item = fixtures.setdefault(key, {'path': '/synthetic-fixtures', 'manifestSha256': 'f'*64, 'backgrounds': {}})
        background = decl.by_id['w50'][scene]['background']
        scale = 2 if '-2x-' in profile else 1
        item['backgrounds'][f'{background}@{scale}x'] = {'path': f'backgrounds/{background}@{scale}x.png', 'sha256': 'c'*64}
    return {'w50': {'webSourceClosure': world.web_closure, 'fixtures': fixtures},
            'canonical': {'webSourceClosure': world.web_closure,
                          'nativeManifest': {'path': '/synthetic/fixtures/manifest.json', 'sha256': '0'*64}}}


def candidate(world):
    """The run record batches.build reads: the world's cohort by position and its numerical report."""
    return {'cohort': [{'position': .25, **world.cohort[0]}, {'position': .5, **world.cohort[1]}],
            'numericalReferee': world.numerical}


def declarations(world):
    return B.Declarations.sealed(world.root, scenes(world))
