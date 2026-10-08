"""Prospective exposure-only owner seam. No root, capture or owner read runs on import.

The dispatcher owns the live Python closure and GPU lease. The separately registered Node
closure owns the owner algorithm, compiler boundary and Python edge subprocess. The full
judge, not this wrapper, decides PASS/NEITHER. A snapshot is evidence, not a reusable lease.

Two claims are bound. The LOGICAL claim (contract.started.json) names the phase, contract,
batch, output and numerical admission; LIVE writes it once, in whichever attempt first ran, so
its pid/lease are that attempt's and are not compared here. The EXECUTION claim the dispatcher
issued this context under must be the exclusive full-union analysis marker held by this very
process and lease (DL5k: no analytical read before that marker); the snapshot carries it and
the Node child rechecks it against its own parent.

preflight(context, config_pin) is the same seam's metadata-only admission (pre-seal review P1).
The owner is first exercised after the exposure's irreversible analysis marker, so any drift
there (a changed TS source, a Node or Python upgrade, a moved superseded capture) would end the
one exposure with no result. preflight runs, before any marker, every config, root, runtime
closure and source check evaluate makes, hashes every transitive {path, sha256} pin of the
owner inputs and completed owner references as the referee's pinnedBytes reads them, and runs
the Node closure's fixed source-only probe, whose stdout must reproduce the recorded exercise
byte for byte. It decodes no image, computes no statistic, writes nothing and returns metadata.
Where the exposure contract already exists it adds evaluate's contract, logical claim, gate and
intrinsic-record checks. evaluate repeats all of it after the marker.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pin(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': sha(path)}


def checked(item, repo=None):
    if not isinstance(item, dict) or set(item) != {'path', 'sha256'} or not isinstance(item['path'], str) \
            or not re.fullmatch('[0-9a-f]{64}', item.get('sha256', '')):
        raise ValueError('Malformed content pin')
    path = Path(item['path'])
    if repo is not None and not path.is_absolute():
        path = Path(repo)/path
    if not path.is_absolute() or path.resolve() != path or sha(path) != item['sha256']:
        raise ValueError('Changed or noncanonical pinned file: '+str(path))
    return path


def load(path):
    def invalid(value):
        raise ValueError('Nonfinite JSON: '+value)
    return json.loads(Path(path).read_text(), parse_constant=invalid)


def normalized(item, repo):
    return pin(checked(item, repo))


def registered(item, inputs, repo):
    value = normalized(item, repo)
    if not any(normalized(other, repo) == value for other in inputs):
        raise ValueError('Owner config/runtime is not registered in live root inputs')
    return value


def source_map(repo, closure):
    sources = {}
    for item in closure['sources']:
        rel = item['path']
        if Path(rel).is_absolute() or '..' in Path(rel).parts or rel in sources:
            raise ValueError('Malformed or duplicate runtime source')
        checked(item, repo)
        sources[rel] = item['sha256']
    return sources


def python_launch(config):
    # The byte pin names the executable target, not the venv entrypoint. Resolving the
    # launch path would discard pyvenv.cfg and silently select the base environment.
    target = checked(config['interpreter'])
    launch, prefix = config['pythonLaunch'], config['pythonPrefix']
    if not isinstance(launch, str) or not os.path.isabs(launch) \
            or os.path.normpath(launch) != launch or Path(launch).resolve() != target:
        raise ValueError('Live Python launch differs from pinned interpreter')
    if not isinstance(prefix, str) or not os.path.isabs(prefix) \
            or str(Path(prefix).resolve()) != prefix or Path(launch).parent != Path(prefix)/'bin' \
            or checked(config['pythonVenvConfig']) != Path(prefix)/'pyvenv.cfg':
        raise ValueError('Live Python prefix/config differs from launch')
    return launch


def child_environment(snapshot, config, config_pin):
    # Compiler escape hatches, including ESBUILD_BINARY_PATH and CJS preload routes,
    # never cross this allowlist. No ambient Python/Node options or compiler cache.
    env = {key: os.environ[key] for key in ('HOME', 'TMPDIR', 'TMP', 'TEMP') if key in os.environ}
    env.update({'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LC_ALL': 'C', 'TSX_DISABLE_CACHE': '1',
        'W50_WEB_ROOT': str(ROOT), 'W50_WEB_CLOSURE': config['runtimeClosure']['path'],
        'W50_WEB_CLOSURE_SHA256': config['runtimeClosure']['sha256'],
        'W50_OWNER_LIVE_CONFIG': config_pin['path'], 'W50_OWNER_LIVE_CONFIG_SHA256': config_pin['sha256'],
        'W50_OWNER_LIVE_SNAPSHOT': snapshot['path'],
        'W50_OWNER_LIVE_SNAPSHOT_SHA256': snapshot['sha256'],
        'W50_OWNER_LIVE_PYTHON': python_launch(config)})
    return env


def _authority(context, config_pin):
    """Config, root and Node runtime closure: every evaluate check that needs no contract."""
    repo = Path(context['repo']).resolve()
    if repo != ROOT:
        raise ValueError('Owner wrapper is outside the live repository')
    config_pin = registered(config_pin, context['inputs'], repo)
    config = load(checked(config_pin))
    if config.get('schema') != 'w50-owner-candidate-config-1':
        raise ValueError('Unknown prospective owner config')
    root_pin = pin(context['executionRoot'])
    root = load(root_pin['path'])
    if root['inputs'] != context['inputs'] or Path(root['repo']).resolve() != repo:
        raise ValueError('Changed live root/contract/batch binding')
    registered(config_pin, root['inputs'], repo)
    runtime_pin = registered(config['runtimeClosure'], root['inputs'], repo)
    if runtime_pin != config['runtimeClosure']:
        raise ValueError('Runtime closure must use an absolute canonical pin')
    closure = load(checked(runtime_pin))
    if closure.get('schema') != 'w50-owner-candidate-runtime-1' \
            or closure.get('exercise') != 'synthetic source-only' \
            or closure.get('toolchain') != {'node': config['node'], 'tsx': config['tsx']} \
            or closure.get('probe') != pin(HERE/'live-probe.mjs'):
        raise ValueError('Node runtime closure has no matching source-only exercise')
    sources = source_map(repo, closure)
    required = [HERE/'live.py', HERE/'live-node.mjs', HERE/'live-python.py', HERE/'live-python-shim',
        HERE/'bridge.ts', HERE.parent/'owner/node-guard.mjs', HERE.parent/'web/node-guard.mjs',
        HERE.parent/'web/vite-guard.mjs', HERE.parent/'execution/guard.py']
    for path in required:
        if sources.get(str(path.relative_to(repo))) != sha(path):
            raise ValueError('Runtime closure omits required live boundary source: '+str(path))
    for key in ('ownerInputs', 'completedOwnerReferences', 'originalInventory',
                'frozenSourceClosure', 'node', 'interpreter', 'tsx'):
        checked(config[key])
    python_launch(config)
    if config['python'] != str(HERE/'live-python-shim'):
        raise ValueError('Only the fixed live guarded Python shim is admitted')
    for rel, item in config['sourcePins'].items():
        if str(checked(item).relative_to(repo)) != rel or sources.get(rel) != item['sha256']:
            raise ValueError('Frozen owner authority missing from runtime closure')
    return repo, config_pin, config, root_pin, root, runtime_pin, closure


def _exposure(context, repo, root_pin, root):
    """The exposure contract's root/batch binding, its logical claim, the same-cohort gate and
    the frozen intrinsic records: evaluate's checks that need the sealed exposure contract."""
    contract_pin, batch_pin = pin(context['contract']), pin(context['batchPath'])
    contract, batch = load(contract_pin['path']), load(batch_pin['path'])
    if contract.get('executionRootSha256') != root_pin['sha256'] or batch != context['batch'] \
            or contract.get('phase') != 'exposure' or contract['cohort'] != batch['cohort'] \
            or normalized(contract['batch'], repo) != batch_pin:
        raise ValueError('Changed live root/contract/batch binding')
    claim_pin = pin(context['contract']+'.started.json')
    claim = load(claim_pin['path'])
    if any(claim.get(k) != v for k, v in {
        'contractSha256': contract_pin['sha256'], 'batchSha256': batch_pin['sha256'],
        'phase': 'exposure', 'output': context['output']}.items()):
        raise ValueError('Changed exposure claim')
    gate_pin = normalized(context['gateResult'], repo)
    gate = load(checked(gate_pin))
    gate_contract_pin = normalized(contract['gateContract'], repo)
    gate_contract = load(checked(gate_contract_pin))
    if normalized(contract['gateResult'], repo) != gate_pin \
            or gate.get('contractSha256') != gate_contract_pin['sha256'] \
            or gate_contract.get('executionRootSha256') != root_pin['sha256'] \
            or gate_contract.get('phase') != 'gate' or gate_contract.get('cohort') != batch['cohort'] \
            or gate.get('captures') != context['gateCaptures']:
        raise ValueError('Changed same-cohort gate capture authority')
    gate_batch = load(checked(gate_contract['batch'], repo))
    intrinsic_pin = normalized(batch['ownerIntrinsicRecords'], repo)
    if gate_batch.get('phase') != 'gate' or gate_batch.get('cohort') != batch['cohort'] \
            or gate_batch.get('ownerIntrinsicRecords') != batch['ownerIntrinsicRecords']:
        raise ValueError('Exposure intrinsic records differ from the frozen gate batch')
    return contract_pin, batch_pin, contract, batch, claim_pin, gate_pin, intrinsic_pin


def _evidence_pins(value, out):
    if isinstance(value, dict):
        if set(value) == {'path', 'sha256'} and isinstance(value['path'], str):
            out.add((value['path'], value['sha256']))
        for item in value.values():
            _evidence_pins(item, out)
    elif isinstance(value, list):
        for item in value:
            _evidence_pins(item, out)
    return out


def evidence_walk(config, repo):
    """Every {path, sha256} pin inside the owner inputs and completed owner references, hashed
    as the referee's pinnedBytes reads them (cwd = repo). Bytes only; no decode, no statistic."""
    pins = set()
    for key in ('ownerInputs', 'completedOwnerReferences'):
        _evidence_pins(load(checked(config[key])), pins)
    for path, digest in sorted(pins):
        target = Path(path) if Path(path).is_absolute() else Path(repo)/path
        if not re.fullmatch('[0-9a-f]{64}', digest) or not target.is_file():
            raise ValueError('Missing owner evidence pin: '+path)
        with target.open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != digest:
                raise ValueError('Changed owner evidence pin: '+path)
    return len(pins)


def node_probe(config, runtime_pin, closure):
    """The Node closure's fixed source-only probe, launched as live-discover.mjs exercised it.
    Its stdout (source binding, empty synthetic membership, Node identity) must reproduce the
    recorded exercise byte for byte; no owner input, candidate or capture reaches it."""
    probe = checked(closure['probe'])
    env = {key: os.environ[key] for key in ('HOME', 'TMPDIR', 'TMP', 'TEMP') if key in os.environ}
    env.update({'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LC_ALL': 'C', 'TSX_DISABLE_CACHE': '1',
        'W50_WEB_ROOT': str(ROOT), 'W50_WEB_CLOSURE': runtime_pin['path'],
        'W50_WEB_CLOSURE_SHA256': runtime_pin['sha256'],
        'W50_OWNER_PROBE_TSX': config['tsx']['path'], 'W50_OWNER_PROBE_TSX_SHA256': config['tsx']['sha256']})
    result = subprocess.run([config['node']['path'], '--import', str(HERE.parent/'owner/node-guard.mjs'), str(probe)],
        text=True, capture_output=True, check=False, cwd=ROOT, env=env)
    if result.returncode:
        raise ValueError('Node owner closure probe refused: '+(result.stderr.strip().splitlines() or [''])[-1])
    if hashlib.sha256(result.stdout.encode()).hexdigest() != closure.get('exerciseSha256'):
        raise ValueError('Node owner closure no longer reproduces its recorded source-only exercise')
    for item in (runtime_pin, closure['probe'], config['node'], config['tsx']):
        checked(item)


def preflight(context, config_pin):
    """Metadata-only owner admission before any marker (module docstring); {admitted, pins}."""
    dispatch = sys.modules.get('w50_g1_dispatch')
    if dispatch is None:
        raise ValueError('No live dispatcher capability')
    dispatch.require_context(context)
    repo, config_pin, config, root_pin, root, runtime_pin, closure = _authority(context, config_pin)
    if context.get('phase') == 'exposure':
        if load(context['batchPath']) != context['batch']:
            raise ValueError('Changed live root/contract/batch binding')
        checked(context['batch']['ownerIntrinsicRecords'], repo)
        gate = load(checked(normalized(context['gateResult'], repo)))
        if gate.get('captures') != context['gateCaptures']:
            raise ValueError('Changed same-cohort gate capture authority')
        if context.get('contract') is not None:
            _exposure(context, repo, root_pin, root)
            output = Path(context['output'])
            if not output.is_absolute() or output.resolve() != output or not output.is_dir() \
                    or output.is_relative_to(repo):
                raise ValueError('Snapshot requires the live external output directory')
    count = evidence_walk(config, repo)
    node_probe(config, runtime_pin, closure)
    source_map(repo, closure)
    dispatch.require_context(context)
    return {'admitted': True, 'evidencePins': count}


def evaluate(context, captures, config_pin):
    """Return {report: OwnerReport, snapshot: Pin}, never a full referee verdict."""
    if context.get('phase') != 'exposure':
        raise ValueError('Candidate owner requires exposure; gate belongs to the full judge')
    dispatch = sys.modules.get('w50_g1_dispatch')
    if dispatch is None:
        raise ValueError('No live dispatcher capability')
    dispatch.require_context(context)
    repo, config_pin, config, root_pin, root, runtime_pin, closure = _authority(context, config_pin)
    contract_pin, batch_pin, contract, batch, claim_pin, gate_pin, intrinsic_pin = \
        _exposure(context, repo, root_pin, root)
    execution_pin = normalized(context.get('executionClaim'), repo)
    execution = load(execution_pin['path'])
    if execution_pin['path'] != str(Path(contract_pin['path']+'.phase')/'analysis.started.json') \
            or execution.get('schema') != 'w50-live-analysis-claim-1' \
            or execution.get('logicalContract') != contract_pin or execution.get('pid') != os.getpid() \
            or execution.get('gpuLease') != dispatch._LEASE['token'] or execution.get('output') != context['output']:
        raise ValueError('Owner needs the full-union analysis claim held by this live lease owner')
    if captures.get('status') != 'CAPTURED':
        raise ValueError('Exposure bundle is not completed captures')
    output = Path(context['output'])
    if not output.is_absolute() or output.resolve() != output or not output.is_dir() \
            or output.is_relative_to(repo):
        raise ValueError('Snapshot requires the live external output directory')
    snapshot = {'schema': 'w50-owner-live-capture-union-1', 'phase': 'exposure',
        'executionRoot': root_pin, 'contract': contract_pin, 'batch': batch_pin, 'claim': claim_pin,
        'executionClaim': execution_pin,
        'config': config_pin, 'gateResult': gate_pin, 'output': str(output),
        'cohort': batch['cohort'], 'ownerIntrinsicRecords': intrinsic_pin,
        'ownerUnionKeys': context['ownerUnionKeys'],
        'expectedExposureCells': context['expectedCells'], 'unionExpectedCells': context['unionExpectedCells'],
        'gateCaptures': context['gateCaptures'], 'exposureCaptures': captures}
    raw = json.dumps(snapshot, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()+b'\n'
    dispatch.require_context(context)
    path = output/'owner-candidate.snapshot.json'
    with path.open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    snapshot_pin = pin(path)
    env = child_environment(snapshot_pin, config, config_pin)
    env['W50_OWNER_LIVE_ROOT_SHA256'] = root_pin['sha256']
    result = subprocess.run([config['node']['path'], str(HERE/'live-node.mjs')],
        input=json.dumps({'snapshot': snapshot_pin, 'config': config_pin}), text=True,
        capture_output=True, check=False, cwd=repo, env=env)
    dispatch.require_context(context)
    # The child cannot silently replace any launch authority while producing its report.
    for item in (snapshot_pin, claim_pin, execution_pin, root_pin, config_pin, runtime_pin, gate_pin):
        checked(item)
    source_map(repo, closure)
    if result.returncode:
        raise ValueError('Candidate owner child refused: '+result.stderr.strip())
    report = json.loads(result.stdout)
    required_report = {'cells', 'aggregates', 'provenance', 'intrinsic', 'noNewTrade'}
    if not isinstance(report, dict) or not required_report <= set(report) \
            or set(report) - required_report - {'liveUnion'}:
        raise ValueError('Owner child did not return an OwnerReport')
    report_path = output/'owner-candidate.report.json'
    with report_path.open('x') as handle:
        json.dump(report, handle, sort_keys=True, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    return {'report': report, 'snapshot': snapshot_pin}
