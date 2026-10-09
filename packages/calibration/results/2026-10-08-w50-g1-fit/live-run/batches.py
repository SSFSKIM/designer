"""The W50 G1 LIVE fit, gate and exposure batch documents, derived from sealed declarations.

Nothing here chooses a cell. Every membership is read from the sealed LIVE root and the G0
declarations it pins (W50 charter DL4, DL5 (b)-(d)):

* gate: exactly the root's phaseDependencies.gateKeys cells, the exposed population DL5d leaves
  outside every withheld physical (profile, scene) closure;
* exposure: exactly its exposureKeys cells, the new blind split plus the historical prediction
  checks and the exposed rows DL5d defers with them;
* fit: the gate cells whose declared split set is calibration or validation (part 2's fitData,
  "Native calibration/validation only"), on both scene sources. The canonical calibration and
  validation scenes are in it, so the canonical capture transport, its measurement and the
  judge's routing of canonical rows run in the recoverable fit before the one-shot gate.

A scene's split set is read from its own scene document: the new bed's scenes-w50.json or the
canonical apps/reference-apple/scenes.json, both pinned by part 2. A run's sets are exactly the
split sets of its scenes. The transports' content-bound run fields are copied from the batches
the root's current composition drew with, never typed here: a new-bed run takes the fixtures of
the current run with its (profile, pose) and the shared web source closure; a canonical run
takes the canonical batch's native manifest and closure. An exposure new-bed run takes the
metadata-only fixture plan the native role verifies (exposure/prepare.read_fixture_plan) under
the exposure's own output, and every exposure run its registered same-position baseline.

New-bed runs hold one pose each (their fixtures name one pose tree; live/router.fixture_keys);
canonical runs group by (profile, renderer). captureRoot and matrixPath are absent: LIVE derives
both per member beneath the phase output (lifecycle.Store._member).

ownerIntrinsicRecords (gate and exposure) pins one document the owner reads for X76 (owner/
intrinsic.ts IntrinsicInputs; DL5m 5, DL5o): {candidateDeclarations: the cohort, recededRecords:
{'0.25', '0.5'}}, each position's four records being
* beforeActive / beforeReceded: the G0 references' current-generation dark documents of that
  position (references.json generations), the pair every current row is stamped with;
* activeEntries: {endpointSha256 of the candidate active.dark file, retainedMeasuredEntries:
  every leaf-keyed before-active entry with status exactly 'measured', verbatim, fittedEntries:
  the candidate active document's own fitted chart records};
* methods: {endpointSha256 of the candidate receded.dark file, methods: {held: reading} for
  every 'held' record the candidate receded document carries, plus each chart leaf's method}.
The candidate documents carry those records themselves (fit/candidate.ts, DL5o), so nothing
here is authored: the envelopes are read off the candidate and the G0 pair. A family-keyed
historical entry (status beginning 'measured' whose key is not a patch leaf or whose value is
an object) is never retained; the owner port admits it as that family's hold (DL5o (a)). A
leaf-keyed one whose value is not its patch leaf cannot be retained or omitted: Blocked.

No statistic is read or printed here; the archive index read by the exposure plan is metadata.
"""
import copy
import json
import os
from pathlib import Path
import re
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
RESULTS = FIT.parent
CURRENT3 = RESULTS/'2026-10-08-w50-g1-current3'
PREPARE = FIT/'exposure/prepare.py'
SCHEMA = 'w50-g1-batch-1'
KEY = ('profile', 'renderer', 'scene', 'statistic')
WITHHELD = {'blind', 'historical-prediction-check'}
SETS = ('calibration', 'validation', 'recorded', 'probe', 'holdout')
FIT_SETS = ('calibration', 'validation')
FIT_DATA = 'Native calibration/validation only'
CANONICAL_SCENES = 'apps/reference-apple/scenes.json'
PROFILE = re.compile(r'apple-macos-27\.0-([12])x-dark-standard-glass(0\.25|0\.5)')
PHASES = ('fit', 'gate', 'exposure')


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


# current3's sealed mechanics: pins, seals and the DL5d table derivation.
D = source(CURRENT3/'execution/dispatch.py', 'w50_live_run_batch_mechanics')


def plain(pin):
    """A batch pin is exactly {path, sha256}; LIVE compares owner declarations by that shape."""
    return {'path': pin['path'], 'sha256': pin['sha256']}


class Declarations:
    """The sealed root and the declarations it pins, read once."""

    def __init__(self, root_path, root, scenes=None):
        """scenes: {'w50', 'canonical'} scene documents. Omitted (always, outside tests), they
        are the two documents part 2 pins, beside its fitData declaration."""
        self.root_path = Path(root_path).resolve(); self.root = root
        self.repo = Path(root['repo']).resolve()
        cells = D.load(D.checked(self.repo, root['references']))['cells']
        self.dependencies = D.verify_phase_dependencies(root, cells)
        self.rows = {tuple(c[k] for k in KEY): c for c in cells}
        if scenes is None:
            two_path = D.checked(self.repo, root['partTwo'])
            part_two = D.load(two_path)
            if not part_two['candidateDomain']['fitData'].startswith(FIT_DATA):
                raise ValueError('Part 2 no longer declares calibration/validation fit data')
            pins = {p['path']: p for p in part_two['sources']}
            newbed = str((two_path.parent/'bed/scenes-w50.json').relative_to(self.repo))
            if newbed not in pins or CANONICAL_SCENES not in pins:
                raise ValueError('Part 2 does not pin both scene documents')
            scenes = {'w50': D.load(D.checked(self.repo, pins[newbed])),
                      'canonical': D.load(D.checked(self.repo, pins[CANONICAL_SCENES]))}
        self.scenes = scenes
        self.by_id = {name: {s['id']: s for s in doc['scenes']} for name, doc in self.scenes.items()}

    @classmethod
    def sealed(cls, root_path, scenes=None):
        return cls(root_path, D.sealed(root_path), scenes)

    def scene_source(self, scene):
        found = [name for name, ids in self.by_id.items() if scene in ids]
        if len(found) != 1: raise ValueError('A scene must belong to exactly one scene document')
        return found[0]

    def split(self, scene):
        doc = self.scenes[self.scene_source(scene)]
        roles = [k for k, ids in doc['split'].items() if not k.startswith('$') and scene in ids]
        if len(roles) != 1 or roles[0] not in SETS: raise ValueError('A scene needs exactly one declared split set')
        return roles[0]

    def pose(self, scene):
        state = self.by_id[self.scene_source(scene)][scene]['state']
        return 'receded' if state == 'inactive' else 'active'

    def cells(self, phase):
        """The phase's (profile, renderer, scene) cells, sorted."""
        if phase not in PHASES: raise ValueError('Unknown LIVE phase')
        keys = self.dependencies['exposureKeys' if phase == 'exposure' else 'gateKeys']
        cells = sorted({tuple(k[:3]) for k in keys})
        if phase == 'fit':
            cells = [c for c in cells if self.split(c[2]) in FIT_SETS]
            if any(self.rows[k]['role'] in WITHHELD for k in self.rows if k[:3] in set(cells)):
                raise ValueError('A withheld row reached the fit population')
        return cells

    def baselines(self):
        """The root's registered same-cell baselines by glass position."""
        out = {}
        for pin in self.root['baselineDocuments']:
            position = D.load(D.checked(self.repo, pin)).get('glassTintAmount')
            if position in out: raise ValueError('Two baselines at one position')
            out[position] = plain(pin)
        if set(out) != {.25, .5}: raise ValueError('Baselines must cover both positions')
        return out


def position(profile):
    match = PROFILE.fullmatch(profile)
    if not match: raise ValueError('Not a dark macOS 27 standard profile')
    return float(match[2])


def transport_fields(decl):
    """Content-bound run fields from the batches the root's current composition drew with.

    Returns {'w50': {'webSourceClosure', 'fixtures': {profile|pose: fixtures}},
             'canonical': {'webSourceClosure', 'nativeManifest'}}. Each value must be one value
    across the current runs that carry it, and each batch must be a root input."""
    composition = D.load(D.checked(decl.repo, decl.root['currentComposition']))
    found = {'w50': {'webSourceClosure': set(), 'fixtures': {}},
             'canonical': {'webSourceClosure': set(), 'nativeManifest': set()}}
    for chain in composition['chains']:
        if chain['batch'] not in decl.root['inputs']: raise ValueError('Current batch is not a root input')
        for run in D.load(D.checked(decl.repo, chain['batch']))['runs']:
            name = run['sceneSource']
            found[name]['webSourceClosure'].add(json.dumps(run['webSourceClosure'], sort_keys=True))
            if name == 'canonical':
                found[name]['nativeManifest'].add(json.dumps(run['nativeManifest'], sort_keys=True))
                continue
            poses = {decl.pose(s) for s in run['scenes']}
            if len(poses) != 1: raise ValueError('A current new-bed run holds one pose')
            key = run['profile']+'|'+poses.pop()
            fixtures = json.dumps(run['fixtures'], sort_keys=True)
            if found[name]['fixtures'].setdefault(key, fixtures) != fixtures:
                raise ValueError('Current runs of one profile and pose disagree on fixtures')
    out = {}
    for name, fields in found.items():
        out[name] = {}
        for field, values in fields.items():
            if field == 'fixtures':
                out[name][field] = {k: json.loads(v) for k, v in sorted(values.items())}
                continue
            if len(values) != 1: raise ValueError(f'Current {name} runs need one {field}')
            out[name][field] = json.loads(values.pop())
    for name in out:
        if out[name]['webSourceClosure'] not in decl.root['inputs']:
            raise ValueError('Web source closure is not a root input')
    return out


def exposure_plans(decl, output):
    """The native role's own metadata-only fixture plan for this exposure output: the archive
    index's identities and hashes, no frame opened (exposure/prepare.read_fixture_plan)."""
    config_pin = decl.root['instruments']['native']['config']
    config = D.load(D.checked(decl.repo, config_pin))
    prepare = source(PREPARE, 'w50_live_run_exposure_plan')
    manifest = D.load(D.checked(decl.repo, config['manifest']))
    scenes = D.load(D.checked(decl.repo, config['scenes']))
    plans = prepare.read_fixture_plan(Path(config['archiveRoot'])/'index.json', config['archiveIndexSha256'],
                                      manifest, scenes, Path(output).resolve()/'native-blind')
    return config_pin, {k: {f: plan[f] for f in ('path', 'manifestSha256', 'backgrounds')} for k, plan in plans.items()}


def _id(phase, profile, renderer, name, pose):
    scale, glass = PROFILE.fullmatch(profile).groups()
    return '-'.join(x for x in (phase, scale+'x', 'glass'+glass.replace('.', ''), renderer, name, pose) if x)


def runs(decl, phase, cohort, numerical, transport, exposure=None):
    """The phase's runs over cohort (one candidate document per position)."""
    groups = {}
    for profile, renderer, scene in decl.cells(phase):
        name = decl.scene_source(scene)
        pose = decl.pose(scene) if name == 'w50' else ''
        groups.setdefault((name, profile, renderer, pose), []).append(scene)
    baselines = decl.baselines() if phase == 'exposure' else None
    out = []
    for (name, profile, renderer, pose), scenes in sorted(groups.items()):
        at = position(profile)
        sets = {decl.split(s) for s in scenes}
        run = {'id': _id(phase, profile, renderer, name, pose), 'profile': profile, 'renderer': renderer,
               'sceneSource': name, 'scenes': sorted(scenes), 'sets': [s for s in SETS if s in sets],
               'candidate': plain(cohort[at]), 'numericalReferee': plain(numerical),
               'webSourceClosure': copy.deepcopy(transport[name]['webSourceClosure'])}
        if name == 'canonical':
            run['nativeManifest'] = copy.deepcopy(transport[name]['nativeManifest'])
        elif phase == 'exposure':
            config_pin, plans = exposure
            run['nativeExposureConfig'] = copy.deepcopy(config_pin)
            run['fixtures'] = copy.deepcopy(plans[profile+'|'+pose])
        else:
            fixtures = transport[name]['fixtures'].get(profile+'|'+pose)
            if fixtures is None: raise ValueError('No current fixtures for this profile and pose')
            scale = int(PROFILE.fullmatch(profile)[1])
            for scene in scenes:
                background = decl.by_id['w50'][scene]['background']
                if f'{background}@{scale}x' not in fixtures['backgrounds']:
                    raise ValueError('Current fixtures lack a scene backdrop')
            run['fixtures'] = copy.deepcopy(fixtures)
        if phase == 'exposure':
            run['baselineCandidate'] = copy.deepcopy(baselines[at])
        out.append(run)
    return out


def build(decl, phase, candidate, transport, intrinsic=None, exposure=None):
    """One batch document. candidate is the run record's {cohort: [{position,path,sha256}],
    numericalReferee}; intrinsic the owner records pin (gate, exposure); exposure the
    (config pin, plans) pair from exposure_plans (exposure only)."""
    cohort = {}
    for item in candidate['cohort']:
        if item['position'] in cohort: raise ValueError('Two candidates at one position')
        cohort[item['position']] = item
    if set(cohort) != {.25, .5}: raise ValueError('The cohort needs both positions')
    if (phase == 'exposure') != (exposure is not None) or (phase == 'fit') != (intrinsic is None):
        raise ValueError('Exposure plans belong to the exposure; owner records to gate and exposure')
    doc = {'schema': SCHEMA, 'phase': phase, 'cohort': [plain(cohort[p]) for p in (.25, .5)],
           'runs': runs(decl, phase, cohort, candidate['numericalReferee'], transport, exposure)}
    if intrinsic is not None: doc['ownerIntrinsicRecords'] = plain(intrinsic)
    return doc


CHART = ('lowEndStrength', 'lowEnd44', 'lowEnd96', 'lowEnd160')
SLOTS = ('active.dark', 'receded.dark')


class Blocked(ValueError):
    """A position's X76 records cannot be read off its candidate and G0 pair."""


def flatten(node, prefix='', out=None):
    """owner/intrinsic.ts flatten: nested objects become dotted leaves; arrays are values."""
    out = {} if out is None else out
    for key, value in node.items():
        path = f'{prefix}.{key}' if prefix else key
        if isinstance(value, dict): flatten(value, path, out)
        else: out[path] = value
    return out


def family(key, entry, leaves):
    """The owner port's family-keyed historical entry (DL5o (a); the rule X1's port applies)."""
    status = entry.get('status')
    return isinstance(status, str) and status.startswith('measured') and \
        (key not in leaves or isinstance(entry.get('value'), dict))


def owner_envelopes(before_active, candidate_active, candidate_receded, active_sha, receded_sha):
    """(activeEntries, methods) envelopes from parsed documents and the candidate endpoint shas."""
    leaves = flatten(before_active['patch'])
    retained = {}
    for key, entry in (before_active.get('entries') or {}).items():
        if not isinstance(entry, dict) or family(key, entry, leaves) or entry.get('status') != 'measured': continue
        if 'value' not in entry or entry['value'] != leaves[key]:
            raise Blocked(f'Leaf-keyed record {key} is not its patch leaf')
        retained[key] = copy.deepcopy(entry)
    fitted, methods = {}, {}
    for leaf in CHART:
        if leaf in candidate_active['patch']:
            entry = candidate_active.get('entries', {}).get(leaf)
            if not isinstance(entry, dict) or entry.get('status') != 'measured' or \
                    entry.get('value') != candidate_active['patch'][leaf] or not entry.get('method'):
                raise ValueError(f'The candidate active document carries no fitted record for {leaf}')
            fitted[leaf] = copy.deepcopy(entry)
    for leaf, entry in (candidate_receded.get('entries') or {}).items():
        if isinstance(entry, dict) and entry.get('status') == 'held' and isinstance(entry.get('reading'), list):
            methods[leaf] = {'held': copy.deepcopy(entry['reading'])}
    for leaf in CHART:
        if leaf in candidate_receded['patch']:
            entry = candidate_receded.get('entries', {}).get(leaf)
            if not isinstance(entry, dict) or entry.get('status') != 'measured' or not entry.get('method'):
                raise ValueError(f'The candidate receded document carries no fitted record for {leaf}')
            methods[leaf] = copy.deepcopy(entry['method'])
    return ({'endpointSha256': active_sha, 'retainedMeasuredEntries': retained, 'fittedEntries': fitted},
            {'endpointSha256': receded_sha, 'methods': methods})


def _candidate(repo, pin):
    path = D.checked(repo, plain(pin)); document = D.load(path); out = {}
    for slot in SLOTS:
        item = document['endpoints'][slot]
        endpoint = (path.parent/item['path']).resolve()
        out[slot] = (D.load(D.checked(repo, {'path': str(endpoint.relative_to(repo)), 'sha256': item['sha256']})),
                     item['sha256'])
    return document.get('glassTintAmount'), out


def _before_pair(repo, references_pin, position):
    inventory = D.load(D.checked(repo, references_pin))
    generations = {c['currentGeneration'] for c in inventory['cells'] if c['profile'].endswith(f'-glass{position}')}
    if len(generations) != 1: raise ValueError('A position needs one current generation')
    documents = inventory['generations'][generations.pop()]['documents']
    return {slot: {'path': documents[slot]['path'], 'sha256': documents[slot]['sha256']} for slot in SLOTS}


def owner_intrinsic_records(repo, references_pin, cohort, directory):
    """Write every position's two envelopes and the ownerIntrinsicRecords document under
    `directory` (inside the repository) and return its pin. Every position is read before any
    file is written, so a Blocked position leaves nothing behind."""
    repo = Path(repo).resolve(); cohort = [plain(c) for c in cohort]
    planned = {}
    for pin in cohort:
        position, endpoints = _candidate(repo, pin)
        before = _before_pair(repo, references_pin, position)
        planned[str(position)] = (before, owner_envelopes(
            D.load(D.checked(repo, before['active.dark'])), endpoints['active.dark'][0],
            endpoints['receded.dark'][0], endpoints['active.dark'][1], endpoints['receded.dark'][1]))
    if set(planned) != {'0.25', '0.5'}: raise ValueError('The cohort needs both positions')
    records = {}
    for position, (before, (active, methods)) in sorted(planned.items()):
        folder = Path(directory)/f'glass{position}'
        records[position] = {'beforeActive': before['active.dark'], 'beforeReceded': before['receded.dark'],
                             'methods': D.pin(repo, write_once(folder/'receded-methods.json', methods)),
                             'activeEntries': D.pin(repo, write_once(folder/'active-entries.json', active))}
    return D.pin(repo, write_once(Path(directory)/'owner-intrinsic-records.json',
                                  {'candidateDeclarations': cohort, 'recededRecords': records}))


def members(batch):
    """(profile, renderer, scene) cells a batch draws."""
    return sorted((r['profile'], r['renderer'], s) for r in batch['runs'] for s in r['scenes'])


def write_once(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        json.dump(value, handle, indent=2, allow_nan=False); handle.write('\n')
        handle.flush(); os.fsync(handle.fileno())
    return path
