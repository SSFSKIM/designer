"""Additive current-artifact completion from a completed non-promotable current instrument.

No measurement, source discovery or numeric override exists here. Original G0 rows are
retained separately and must equal the current instrument's original reference inventory.
Only its original null currentEvidence/currentMetadata slots can receive capture artifact
pins, for exact exposed keys. All roles, numeric values, history and nonnull fields survive.
The configured root and every fixed result are content-pinned before any helper executes.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
KEY = ('profile', 'renderer', 'scene', 'statistic')


def load_dispatcher(repo, config, *, verify_results=True):
    # Stdlib-first validation of the configured root and its complete repository source pins.
    # The outer reference root's permanent guard additionally checks all dynamic executions.
    import hashlib
    repo = Path(repo).resolve()
    def checked(item):
        p = (repo/item['path']).resolve()
        if not p.is_relative_to(repo) or not p.is_file() or p.is_symlink() \
                or hashlib.sha256(p.read_bytes()).hexdigest() != item.get('sha256'):
            raise ValueError('Changed current completion root/source/result pin')
        return p
    root_path = checked(config['instrument']); root = json.loads(root_path.read_bytes())
    if root.get('schema') != 'w50-g1-current-instrument-root-1' or Path(root.get('repo', '')).resolve() != repo:
        raise ValueError('Completion requires the same-repository current-only instrument')
    source_pins = root.get('closure', {}).get('sources', {})
    path = checked(root['bootstrap'])
    if path != root_path.parent/'dispatch.py' or path.name != 'dispatch.py' \
            or source_pins.get(str(path.relative_to(repo))) != root['bootstrap']['sha256']:
        raise ValueError('Current completion bootstrap is not root-pinned')
    for relative, digest in source_pins.items(): checked({'path': relative, 'sha256': digest})
    if verify_results:
        for item in config['results']: checked(item)
    spec = importlib.util.spec_from_file_location('w50_reference_current_dispatch', path)
    dispatcher = importlib.util.module_from_spec(spec); sys.modules[spec.name] = dispatcher
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), dispatcher.__dict__)
    return dispatcher, root_path


def original_endpoints(dispatcher, repo, root):
    """Current namespaces may change profileKey ONLY; original digest and all other fields hold."""
    admission = dispatcher.admission_module(root)
    part_two = dispatcher.load(dispatcher.checked(repo, root['partTwo']))
    pins = {p['path']: p for p in part_two['sources']}
    result = {}
    for candidate_pin in root['baselineDocuments']:
        position = admission.endpoints(root, candidate_pin, current=True)
        candidate_path = dispatcher.checked(repo, candidate_pin)
        candidate = dispatcher.load(candidate_path)
        endpoints = {}
        for slot, item in candidate['endpoints'].items():
            pose, scheme = slot.split('.')
            suffix = '-receded' if pose == 'receded' else ''
            original_path = (dispatcher.checked(repo, root['partTwo']).parent.parent.parent/'profiles'/
                f'apple-macos-27.0-1x-{scheme}-standard-glass{position}{suffix}.json')
            original_pin = pins.get(str(original_path.relative_to(repo)))
            if original_pin is None: raise ValueError('Current endpoint original absent from immutable G0')
            original = dispatcher.load(dispatcher.checked(repo, original_pin))
            endpoint_path = (candidate_path.parent/item['path']).resolve()
            endpoint = dispatcher.load(dispatcher.checked(repo,
                {'path': str(endpoint_path.relative_to(repo)), 'sha256': item['sha256']}))
            if {k:v for k,v in endpoint.items() if k != 'profileKey'} != \
                    {k:v for k,v in original.items() if k != 'profileKey'} \
                    or not isinstance(original.get('resolvedMaterialSha256'), str):
                raise ValueError('Current namespace changed an original endpoint field or digest')
            endpoints[slot] = {'profileKey': endpoint['profileKey'],
                              'resolvedMaterialSha256': original['resolvedMaterialSha256'],
                              'glassTintAmount': position}
        result[candidate_pin['sha256']] = endpoints
    return result


def drawn_original(dispatcher, capture, scene, endpoints):
    page = dispatcher.load(capture['artifacts']['report']['path'])['page']
    slot = ('receded' if scene['state'] == 'inactive' else 'active')+'.dark'
    endpoint = endpoints[capture['candidate']['sha256']][slot]
    materials = [page.get('material')] + [g.get('state', {}).get('materialDocument') for g in page.get('groups', [])]
    if not page.get('groups') or any(not isinstance(m, dict) or m.get('tuned') is not False \
            or any(m.get(k) != endpoint[k] for k in ('profileKey','resolvedMaterialSha256','glassTintAmount'))
            for m in materials):
        raise ValueError('Admitted current artifact does not report the original drawn gate0 endpoint')


def complete_current_projection(repo, original_rows, config, *, scenes=None):
    """Return an evidence-pin projection; never mutate original rows or synthesize readings."""
    if not isinstance(config, dict) or set(config) != {'instrument', 'results'} \
            or not isinstance(config['results'], list) or not config['results']:
        raise ValueError('Completion needs the pinned current instrument and every fixed completed result')
    repo = Path(repo).resolve()
    dispatcher, root_path = load_dispatcher(repo, config)
    chain = dispatcher.current_evidence_inputs(repo, root_path.parent, config['instrument'], config['results'])
    root = dispatcher.root_doc(root_path)
    inventory = dispatcher.load(dispatcher.checked(repo, root['references']))
    original = {tuple(row[k] for k in KEY): row for row in inventory['cells']}
    if len(original) != len(inventory['cells']) or len({tuple(r[k] for k in KEY) for r in original_rows}) != len(original_rows):
        raise ValueError('Original completion reference keys are duplicate')
    for row in original_rows:
        if original.get(tuple(row[k] for k in KEY)) != row:
            raise ValueError('Caller row/numeric override differs from the original G0 inventory')
    endpoints = original_endpoints(dispatcher, repo, root)
    captures = {}
    for result_pin in config['results']:
        result = dispatcher.sealed(dispatcher.checked(repo, result_pin))
        for capture in result['captures']['captures']:
            identity = (capture['profile'], capture['renderer'], capture['scene'])
            if capture.get('lane') != 'current' or identity in captures:
                raise ValueError('Duplicate or non-current capture in completion receipts')
            captures[identity] = capture
    selected = []
    projection = copy.deepcopy(original_rows)
    for row in projection:
        missing = [name for name in ('currentEvidence','currentMetadata') if row.get(name) is None]
        if not missing: continue
        identity = (row['profile'], row['renderer'], row['scene'])
        if row.get('role') != 'gate' or identity not in captures:
            raise ValueError('Original missing current key has no admitted exposed current capture')
        capture = captures[identity]
        if scenes is not None:
            matches = [s for s in scenes['scenes'] if s['id'] == row['scene']]
            if len(matches) != 1: raise ValueError('Completion captured an undeclared canonical scene')
            scene = matches[0]
        else:
            # Direct standalone verification must still state the pose from canonical source,
            # never infer it from a PNG. The fixed G0 canonical declaration is source-pinned.
            one = dispatcher.load(dispatcher.checked(repo, root['partOne']))
            pin = next((p for p in one['sources'] if p['path'] == 'apps/reference-apple/scenes.json'), None)
            if pin is None: raise ValueError('Completion needs the pinned original canonical scene declaration')
            doc = dispatcher.load(dispatcher.checked(repo, pin))
            scene = next(s for s in doc['scenes'] if s['id'] == row['scene'])
        drawn_original(dispatcher, capture, scene, endpoints)
        for field, artifact in (('currentEvidence','png'), ('currentMetadata','cell')):
            if field in missing: row[field] = copy.deepcopy(capture['artifacts'][artifact])
        selected.append([row[k] for k in KEY])
    return {'schema': 'w50-admitted-current-reference-projection-1', 'originalRows': copy.deepcopy(original_rows),
            'rows': projection, 'completedKeys': selected, 'currentInstrument': config['instrument'],
            'currentResults': config['results'], 'chainPins': chain,
            'policy': 'ONLY_ORIGINAL_NULL_CURRENT_ARTIFACT_PINS_NO_NUMERIC_ROLE_OR_HISTORY_CHANGE'}


def source_probe(config=None, *, repo=REPO):
    """Import the CONFIGURED root's bootstrap, not a guessed old execution pathname.

    With no completed instrument configured, pure source readiness is available but no
    dispatcher source is assumed. Once configured, only its pinned root/source metadata is
    inspected and the exact bootstrap/admission bytes are imported. Result receipts, PNGs
    and statistics are never opened during prospective discovery.
    """
    if config is None:
        return {'status': 'SOURCE_ONLY', 'bootstrap': None}
    dispatcher, root_path = load_dispatcher(repo, config, verify_results=False)
    root = json.loads(root_path.read_bytes())
    admission_path = Path(dispatcher.__file__).with_name('admission.py')
    expected = root['closure']['sources'].get(str(admission_path.relative_to(Path(repo).resolve())))
    if expected is None or dispatcher.sha(admission_path) != expected:
        raise ValueError('Configured current admission source absent from root closure')
    dispatcher.module(admission_path, 'w50_reference_current_admission_probe')
    return {'status': 'SOURCE_ONLY', 'bootstrap': root['bootstrap']}
