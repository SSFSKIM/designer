"""Pre-render W50 initializer/argument binder, not a fit/gate dispatcher or optimizer loop.

Public API: initialize(execution_root) returns ONE joint analytical proposal;
assemble(execution_root) uses the production candidate builder for that proposal;
bind_arguments(execution_root, evaluation_cohort) writes an additive G0-schema cohort.
No observations, coefficients, joins, report paths or sampling overrides are public inputs.

Prospective integration (nothing is configured or sealed by this module): the LIVE root registers
instruments.initializer={entrypoint:this file's pin,config:its input document pin}; both belong
to root.inputs and this Python source belongs to its source closure. Its separate instruments.fit
remains the live evaluate(context,captures) adapter, not this pre-render entrypoint. The PYTHON closure
includes inputs.py/uniform.py and their exercised Python imports only. Node/TS sources live in a
SEPARATELY exercised runtime closure, pinned as a root INPUT, never in the Python observed set.
Root inputs also include the explicitly registered initializer config and every referenced evidence/document pin.
That input has exactly schema='w50-fit-initializer-inputs-1', completedCurrent={path,sha256},
runtime={closure:{path,sha256},node:{path,sha256}} (node uses its canonical absolute path), and output (a fresh
repository-relative directory UNDER this fit directory, needed by G0's relative-pin schema).
completedCurrent must equal root.currentEvidence: the authoritative schema2 read of
root.currentComposition's genuine ordered instrument/result chains, authenticated again through
dispatcher.current_evidence after prefit. There is no schema1/singular-current-root compatibility
path. The original external capture/report pins remain intact; no numeric map can substitute.

Every public operation verifies the sealed live root and real dispatcher.verify_prefit BEFORE
opening native report values or loading the solver. A live capture context cannot be required
here: the first candidate and numerical cohort must exist before that context can be issued.
There is deliberately no evaluate(context,captures) placeholder or whole-gate PASS result.
"""
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import types

HERE = Path(__file__).resolve().parent


def _sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load(path):
    raw = Path(path).read_bytes()
    if str(path).endswith('.gz'): raw = gzip.decompress(raw)
    def invalid(value): raise ValueError('Nonfinite input: '+value)
    return json.loads(raw, parse_constant=invalid)


def _source(path, name):
    result = types.ModuleType(name); result.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec'), result.__dict__)
    return result


def _checked(repo, pin):
    if not isinstance(pin, dict) or not isinstance(pin.get('path'), str):
        raise ValueError('Missing configured content pin')
    path = (repo/pin['path']).resolve()
    if not path.is_relative_to(repo) or not path.is_file() or _sha(path) != pin.get('sha256'):
        raise ValueError('Changed or missing root-bound input/source')
    return path


def _pin(repo, path): return {'path': str(Path(path).relative_to(repo)), 'sha256': _sha(path)}


def _bootstrap(root_path):
    """Read root metadata/source hashes only; native evidence remains behind verify_prefit."""
    root_path = Path(root_path).resolve()
    root = _load(root_path); repo = Path(root['repo']).resolve()
    sidecar = Path(str(root_path)+'.sha256')
    if sidecar.read_text() != f'{_sha(root_path)}  {root_path.name}\n':
        raise ValueError('Configured live root has no matching seal')
    bootstrap = _checked(repo, root['bootstrap'])
    if bootstrap != root_path.parent/'dispatch.py':
        raise ValueError('Root bootstrap must be its sealed sibling dispatcher')
    sources = root['closure']['sources']
    for path, digest in sources.items(): _checked(repo, {'path': path, 'sha256': digest})
    for path in (Path(__file__).resolve(), bootstrap, root_path.parent/'guard.py'):
        if sources.get(str(path.relative_to(repo))) != _sha(path):
            raise ValueError('Fitting/bootstrap source absent from configured closure')
    guard = _source(root_path.parent/'guard.py', 'w50_initializer_guard')
    if guard.environment() != root['closure']['environment']:
        raise ValueError('Initializer interpreter/environment differs from its sealed closure')
    guard.enforce(repo, sources)
    return _source(bootstrap, 'w50_initializer_dispatch')


def _admit(root_path):
    dispatcher = _bootstrap(root_path)
    root = dispatcher.root_doc(root_path)
    if (root.get('schema') != 'w50-g1-execution-root-1' or
            root.get('lifecycle') != 'logical-phase-attempts-1' or
            any(k in root for k in ('currentInstrument', 'currentResults'))):
        raise ValueError('Only the composed-current live lifecycle root may initialize candidates')
    repo = Path(root['repo']).resolve()
    initializer = root.get('instruments', {}).get('initializer', {})
    own = _pin(repo, Path(__file__).resolve())
    if (set(initializer) != {'entrypoint', 'config'} or initializer.get('entrypoint') != own or
            any(item not in root.get('inputs', []) for item in initializer.values())):
        raise ValueError('Root does not register this exact initializer fit source and config')
    prefit = dispatcher.verify_prefit(root_path, root)
    # The first native/config/solver read in this entrypoint is strictly AFTER this call.
    return dispatcher, root, repo, prefit


def _registered(root, repo, pin):
    if pin not in root['inputs']:
        raise ValueError('Initializer evidence/input was not prospectively root-bound')
    return _checked(repo, pin)


def _state(root_path):
    dispatcher, root, repo, prefit = _admit(root_path)
    config_pin = root['instruments']['initializer']['config']
    config = _load(_registered(root, repo, config_pin))
    if set(config) != {'schema', 'completedCurrent', 'output', 'runtime'} or config['schema'] != 'w50-fit-initializer-inputs-1':
        raise ValueError('Initializer config cannot supply coefficients, values or numeric overrides')
    _runtime_spec(root, repo, config)
    if config['completedCurrent'] != root['currentEvidence']:
        raise ValueError('Initializer must use the live root currentEvidence pin')
    _registered(root, repo, config['completedCurrent'])
    # This API re-admits the genuine composition: ordered actual instruments/results and
    # every chain pin are checked by the source-owned authority, never flattened here.
    completed = dispatcher.current_evidence(root_path, root)
    if (completed.get('schema') != 'w50-completed-current-evidence-2' or
            completed.get('status') != 'EVIDENCE_ONLY' or 'currentInstrument' in completed or
            completed.get('currentComposition') != root['currentComposition'] or
            completed.get('originals', {}).get('references') != root['references']):
        raise ValueError('Initializer requires the authenticated composed-current evidence2 read')
    output = (repo/config['output']).resolve()
    if not output.is_relative_to(HERE) or output == HERE:
        raise ValueError('Generated candidate/numerical outputs must stay in configured fit scratch')
    inventory = _load(_checked(repo, root['references']))
    manifest = _load(_checked(repo, root['manifest']))
    scenes_pin = completed['originals']['scenes']
    scenes = _load(_registered(root, repo, scenes_pin))
    native_batch = _load(_registered(root, repo, completed['native']['batch']))
    if native_batch.get('inputs', {}).get('manifest') != root['manifest'] or \
            native_batch.get('inputs', {}).get('declaration') != root['partOne'] or \
            native_batch.get('inputs', {}).get('scenes') != scenes_pin:
        raise ValueError('Native reports do not name this original declaration/manifest/scenes')
    source = HERE/'inputs.py'
    if root['closure']['sources'].get(str(source.relative_to(repo))) != _sha(source):
        raise ValueError('Selection/binding source is outside the configured closure')
    inputs = _source(source, 'w50_initializer_inputs')
    return dict(dispatcher=dispatcher, root=root, repo=repo, prefit=prefit, config=config,
                completed=completed, output=output, inventory=inventory, manifest=manifest,
                scenes=scenes, nativeBatch=native_batch, inputs=inputs, rootPath=str(Path(root_path).resolve()))


def _runtime_spec(root, repo, config):
    runtime = config.get('runtime', {})
    if set(runtime) != {'closure', 'node'}:
        raise ValueError('Separate exercised runtime closure and pinned Node executable required')
    path = _registered(root, repo, runtime['closure']); closure = _load(path)
    if closure.get('schema') != 'w50-fit-runtime-closure-1' or closure.get('exercise', {}).get('status') != \
            'SYNTHETIC_PRODUCTION_BRIDGE_EXERCISED':
        raise ValueError('Runtime closure must exercise the production bridge on synthetic documents')
    sources = {p['path']:p['sha256'] for p in closure.get('sources', [])}
    if not sources or len(sources) != len(closure['sources']):
        raise ValueError('Missing or duplicate runtime source inventory')
    for source, digest in sources.items(): _checked(repo, {'path':source,'sha256':digest})
    if closure['exercise'].get('probe') != _pin(repo, HERE/'runtime-probe.ts') or \
            closure['exercise'].get('branches') != {'fixedJoinEndpoints':4,'builtCandidates':2,
                                                   'heldTransfers':2,'heldMutationRefusals':2}:
        raise ValueError('Runtime exercise must bind the actual complete production probe')
    for source in (HERE/'runtime-entry.mjs', HERE/'runtime-bridge.ts', HERE/'runtime-probe.ts',
                   HERE.parent/'owner/node-guard.mjs', HERE.parent/'web/node-guard.mjs'):
        if sources.get(str(source.relative_to(repo))) != _sha(source):
            raise ValueError('Missing fitting runtime/probe/guard source')
    node_pin = runtime['node']; node = Path(node_pin['path'])
    if (not node.is_absolute() or str(node.resolve()) != str(node) or not node.is_file() or
            _sha(node) != node_pin.get('sha256') or node_pin != closure.get('node')):
        raise ValueError('Node executable differs from the exercised runtime environment')
    return path, node


def _child_environment(repo, closure, digest):
    # Owner/web guard discipline: never inherit Node/tsx/esbuild compiler overrides.
    env = {key:os.environ[key] for key in ('HOME','TMPDIR','TMP','TEMP') if key in os.environ}
    env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin', LC_ALL='C', TSX_DISABLE_CACHE='1',
               W50_WEB_ROOT=str(repo), W50_WEB_CLOSURE=str(closure), W50_WEB_CLOSURE_SHA256=digest)
    return env


def _bridge(state, operation, **kwargs):
    repo, root = state['repo'], state['root']
    closure, node = _runtime_spec(root, repo, state['config'])
    runtime_pin = state['config']['runtime']['closure']
    request = dict(operation=operation, executionRoot=state['rootPath'], runtimeClosure=runtime_pin, **kwargs)
    got = subprocess.run([str(node), '--import', str(HERE.parent/'owner/node-guard.mjs'),
                          '--import', 'tsx', str(HERE/'runtime-entry.mjs')], cwd=repo/'packages/calibration',
                         env=_child_environment(repo, closure, runtime_pin['sha256']),
                         input=json.dumps(request, allow_nan=False), text=True, capture_output=True, check=True)
    return json.loads(got.stdout)


def _baselines(state):
    repo = state['repo']; result = []
    for item in state['root']['baselineDocuments']:
        path = _checked(repo, item)
        doc = _load(path); position = doc.get('glassTintAmount')
        result.append(dict(position=position, **item))
    state['inputs']._cohort(result)
    return result


def initialize(execution_root):
    """One joint analytical proposal; no caller numeric overrides and no gate selection."""
    state = _state(execution_root)
    report_pins = state['completed']['native']['reports']
    if set(report_pins) != {'calibration', 'validation'}:
        raise ValueError('Only the two exposed native reports may identify the chart')
    reports = {role: _load(_registered(state['root'], state['repo'], item)) for role, item in report_pins.items()}
    observations = state['inputs'].uniform_observations(state['manifest'], state['scenes'], reports,
                                                       state['inventory'], state['root']['partOne']['sha256'])
    joins = {}
    baselines = _baselines(state)
    for baseline in baselines:
        proof = _bridge(state, 'joins', baseline={k:baseline[k] for k in ('path','sha256')})
        if proof['position'] != baseline['position']:
            raise ValueError('Pinned gate0 fixed joins name another position')
        joins.update(proof['joins'])
    joins = state['inputs'].join_observations(joins)
    solver_path = HERE/'uniform.py'
    if state['root']['closure']['sources'].get(str(solver_path.relative_to(state['repo']))) != _sha(solver_path):
        raise ValueError('Joint solver absent from source closure')
    solver = _source(solver_path, 'w50_joint_initializer')
    result = solver.fit_joint(observations, joins=joins)
    result['analyticalScore'] = solver.score_joint(observations, result['endpoints'])
    state['dispatcher'].verify_prefit(execution_root, state['root'])
    return dict(schema='w50-analytical-initializer-1', status='ANALYTICAL_PROPOSAL_ONLY',
        preFitEvidence=state['prefit'], sourceEvidence=state['config']['completedCurrent'],
        nativeReports=copy.deepcopy(report_pins), capturedCohort=baselines,
        observationIdentitySha256=state['inputs'].digest(observations),
        fixedJoinsSha256=state['inputs'].digest(joins), **result)


def _write_once(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n')
        stream.flush(); os.fsync(stream.fileno())


def _provenance(state, result, digest):
    """The method lines DL5o's fitted chart records carry: pins and digests only, no value."""
    reports = result['nativeReports']
    return ['W50 G1 analytical initializer (fit/execution.py initialize, fit/uniform.py fit_joint): '
            f'initializer proposal digest {digest}',
            f"part 2 sha256 {state['root']['partTwo']['sha256']}; pre-fit evidence "
            f"{result['preFitEvidence']['path']} sha256 {result['preFitEvidence']['sha256']}",
            'native reports ' + '; '.join(f"{role} {reports[role]['path']} sha256 {reports[role]['sha256']}"
                                         for role in sorted(reports)),
            f"observations sha256 {result['observationIdentitySha256']}; fixed64 joins sha256 "
            f"{result['fixedJoinsSha256']}"]


def assemble(execution_root):
    """Build exactly the initializer proposal through the production builder, not a seal.
    Each candidate carries DL5o's X76 records, the fitted ones naming this proposal."""
    result = initialize(execution_root)
    state = _state(execution_root)
    digest = state['inputs'].digest(result)
    destination = state['output']/'candidates'/digest
    cohort = []
    for baseline in result['capturedCohort']:
        position = baseline['position']
        charts = {pose: result['endpoints'][f'{pose}.dark.{position}'] for pose in ('active','receded')}
        item = _bridge(state, 'build', baseline={k:baseline[k] for k in ('path','sha256')},
                       charts=charts, output=str(destination/str(position)),
                       provenance=_provenance(state, result, digest))
        cohort.append(dict(position=position, **_pin(state['repo'], Path(item['path']))))
    _write_once(destination/'initializer.json', result)
    return dict(status='UNSEALED_ANALYTICAL_CANDIDATE', cohort=cohort,
                initializer=_pin(state['repo'], destination/'initializer.json'))


def bind_arguments(execution_root, evaluation_cohort):
    """Bind frozen sampled arguments to evaluated bytes only after held-material proof."""
    state = _state(execution_root); inputs = state['inputs']; repo = state['repo']
    before = _baselines(state); after = inputs._cohort(evaluation_cohort)
    for item in after.values(): _checked(repo, item)
    proofs = []
    for baseline in before:
        b = {k:baseline[k] for k in ('path','sha256')}
        proof = _bridge(state, 'transfer', baseline=b, evaluation=after[baseline['position']])
        # The runtime resolves absolute paths for reading; persistent identities stay the exact pins.
        proof.update(capturedCandidate=b, evaluationCandidate=after[baseline['position']])
        proofs.append(proof)
    guard_path = _checked(repo, state['root']['partTwo']).parent/'audit/numerical_guard.py'
    if state['root']['closure']['sources'].get(str(guard_path.relative_to(repo))) != _sha(guard_path):
        raise ValueError('Original numerical guard absent from prospective source closure')
    guard = _source(guard_path, 'w50_fit_numerical_guard')
    required = guard.required_arguments(state['inventory'])
    records = state['completed']['arguments']
    for record in records:
        guard.validate_tone_values(record)
        # Hash the actual original files, without decoding/re-rendering/relabeling them.
        for name in ('capture','report'):
            item = inputs.pin(record.get('provenance', {}).get(name)); path = Path(item['path'])
            path = path if path.is_absolute() else repo/path
            if not path.is_file() or _sha(path) != item['sha256']:
                raise ValueError('Original captured gate0 argument evidence changed')
    wrapped = inputs.evaluation_arguments(records, required, before, evaluation_cohort, proofs,
                                          state['config']['completedCurrent'])
    state['dispatcher'].verify_prefit(execution_root, state['root'])
    output = state['output']/'numerical'/inputs.digest(evaluation_cohort)
    output.mkdir(parents=True, exist_ok=False)
    for index, record in enumerate(wrapped):
        path = output/f'argument-{index:04}.json'
        _write_once(path, {'schema':'w50-measured-tone-argument-1', **record})
        record['evidence'] = _pin(repo, path)
    manifest = dict(schema='w50-structured-arguments-1', candidateSha256s=sorted(p['sha256'] for p in after.values()),
                    references=state['root']['references'], requiredIds=sorted(required), records=wrapped)
    _write_once(output/'arguments.json', manifest)
    cohort = dict(schema='w50-numerical-cohort-1', candidates=copy.deepcopy(evaluation_cohort),
                  structuredArguments=_pin(repo, output/'arguments.json'))
    _write_once(output/'cohort.json', cohort)
    return dict(status='EVALUATION_ARGUMENT_BINDING_ONLY', cohort=_pin(repo, output/'cohort.json'),
                argumentManifest=_pin(repo, output/'arguments.json'),
                capturedEvidence=state['config']['completedCurrent'], preFitEvidence=state['prefit'])
