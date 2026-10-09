"""Synthetic dispatcher leases only; no material documents, captured pixels or owner readings."""
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import subprocess
import venv
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def pin(path):
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


class LiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()/'repo'
        self.here = self.repo/'packages/calibration/results/2026-10-08-w50-g1-fit/owner-candidate'
        self.here.mkdir(parents=True)
        (self.here.parent/'package.json').write_text('{"type":"module"}\n')
        for name in ('live.py', 'live-node.mjs', 'live-python.py', 'live-python-shim', 'live-probe.mjs'):
            shutil.copyfile(HERE/name, self.here/name)
        (self.here/'live-python-shim').chmod(0o755)
        self.venv = Path(self.temp.name).resolve()/'venv'
        venv.EnvBuilder(with_pip=False, symlinks=True).create(self.venv)
        self.python = self.venv/'bin/python'
        (self.here/'bridge.ts').write_text('export const executeRequest = () => ({cells:{}, aggregates:{}, intrinsic:{}, provenance:{}, noNewTrade:"synthetic"});\n')
        for dirname, names in [('owner', ['node-guard.mjs']), ('web', ['node-guard.mjs', 'vite-guard.mjs']),
                               ('execution', ['guard.py'])]:
            target = self.here.parent/dirname
            target.mkdir()
            for name in names:
                shutil.copyfile(HERE.parent/dirname/name, target/name)
        self.live = module(self.here/'live.py', 'synthetic_owner_live')
        # This is the actual dispatcher implementation, not a fake production authority.
        self.dispatch = module(HERE.parent/'execution/dispatch.py', 'w50_g1_dispatch')
        self.addCleanup(lambda: sys.modules.pop('w50_g1_dispatch', None))
        self.output = Path(self.temp.name).resolve()/'output'
        self.output.mkdir()
        self.dispatch.GPU_LOCK = Path(self.temp.name)/'synthetic-lease'
        token = 'synthetic-disposable-lease'
        self.dispatch.GPU_LOCK.write_text(token)
        stat = self.dispatch.GPU_LOCK.stat()
        self.dispatch._LEASE = {'identity': (stat.st_dev, stat.st_ino), 'token': token}
        self.doc = self.put('candidate.json', {'syntheticDeclaration': True})
        source_paths = [p for p in self.here.parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        sources = [{'path': str(p.relative_to(self.repo)), 'sha256': pin(p)['sha256']} for p in source_paths]
        node = pin(Path(shutil.which('node')).resolve())
        tsx = pin((HERE.parents[2]/'node_modules/tsx/dist/esm/api/index.mjs').resolve())
        import subprocess
        version = subprocess.check_output([node['path'], '-p', 'process.version'], text=True).strip()
        self.closure = self.put('closure.json', {'schema': 'w50-owner-candidate-runtime-1',
            'sources': sources, 'exercise': 'synthetic source-only', 'probe': pin(self.here/'live-probe.mjs'),
            'toolchain': {'node': node, 'tsx': tsx}, 'nodeEnvironment': {'version': version,
                'executable': node['path'], 'executableSha256': node['sha256']}})
        self.config = self.put('config.json', {
            'schema': 'w50-owner-candidate-config-1',
            'ownerInputs': self.put('inputs.json', {}),
            'completedOwnerReferences': self.put('references.json', {}),
            'originalInventory': self.put('inventory.json', {}),
            'frozenSourceClosure': self.put('frozen.json', {'sources': []}),
            'sourcePins': {}, 'runtimeClosure': self.closure,
            'node': pin(Path(shutil.which('node')).resolve()),
            'interpreter': pin(self.python),
            'pythonLaunch': str(self.python), 'pythonPrefix': str(self.venv),
            'pythonVenvConfig': pin(self.venv/'pyvenv.cfg'),
            'python': str(self.here/'live-python-shim'),
            'pythonEnvironment': {},
            'tsx': pin((HERE.parents[2]/'node_modules/tsx/dist/esm/api/index.mjs').resolve()),
        })
        self.root = self.put('root.json', {'repo': str(self.repo), 'inputs': [self.config, self.closure]})
        self.intrinsic = self.put('intrinsic.json', {'syntheticRecords': []})
        self.batch = self.put('batch.json', {'phase': 'exposure', 'cohort': [self.doc],
            'ownerIntrinsicRecords': self.intrinsic})
        self.gate_batch = self.put('gate-batch.json', {'phase': 'gate', 'cohort': [self.doc],
            'ownerIntrinsicRecords': self.intrinsic})
        self.gate_contract = self.put('gate.json', {'phase': 'gate', 'cohort': [self.doc],
            'executionRootSha256': self.root['sha256'], 'batch': self.gate_batch})
        self.gate_captures = {'status': 'CAPTURED', 'runs': [], 'synthetic': {'exact': ['gate', 1]}}
        self.gate_result = self.put('gate.json.result.json', {'contractSha256': self.gate_contract['sha256'],
            'captures': self.gate_captures})
        self.contract = self.put('contract.json', {'phase': 'exposure', 'cohort': [self.doc],
            'batch': self.batch, 'executionRootSha256': self.root['sha256'],
            'gateContract': self.gate_contract, 'gateResult': self.gate_result})
        self.claim = self.put('contract.json.started.json', {'phase': 'exposure',
            'contractSha256': self.contract['sha256'], 'batchSha256': self.batch['sha256'],
            'pid': os.getpid(), 'output': str(self.output), 'gpuLease': token})
        self.context = {'repo': str(self.repo), 'executionRoot': self.root['path'],
            'contract': self.contract['path'], 'batchPath': self.batch['path'],
            'batch': self.read(self.batch), 'phase': 'exposure', 'output': str(self.output),
            'inputs': [self.config, self.closure], 'gateResult': self.gate_result,
            'gateCaptures': self.gate_captures, 'ownerUnionKeys': [], 'expectedCells': [],
            'unionExpectedCells': []}
        self.mark()
        self.captures = {'status': 'CAPTURED', 'runs': [], 'synthetic': {'exact': ['exposure', 2]}}
        self.child = patch.object(self.live.subprocess, 'run', return_value=type('Result', (), {
            'returncode': 0, 'stdout': json.dumps({'cells': {}, 'aggregates': {}, 'intrinsic': {},
                'provenance': {}, 'noNewTrade': 'synthetic'}), 'stderr': ''})()).start()
        self.addCleanup(patch.stopall)

    def put(self, name, value):
        path = self.repo/name
        path.write_text(json.dumps(value, sort_keys=True)+'\n')
        return pin(path)

    def read(self, item):
        return json.loads(Path(item['path']).read_text())

    def activate(self):
        self.dispatch._ACTIVE = (self.context, copy.deepcopy(self.context), self.contract['sha256'],
            self.batch['sha256'], True, self.read(self.root), None)

    def mark(self, **changes):
        """(Re)write LIVE's full-union analysis marker for the current contract, held by this
        process and synthetic lease, and issue the context under it."""
        path = Path(self.contract['path']+'.phase')/'analysis.started.json'
        path.parent.mkdir(exist_ok=True)
        value = {'schema': 'w50-live-analysis-claim-1', 'logicalContract': self.contract,
            'captures': self.batch, 'pid': os.getpid(), 'gpuLease': self.dispatch._LEASE['token'],
            'output': str(self.output), **changes}
        path.write_text(json.dumps(value, sort_keys=True)+'\n')
        self.execution = pin(path)
        self.context['executionClaim'] = self.execution
        self.activate()

    def test_genuine_snapshot_preserves_bundles_and_is_exclusive(self):
        before = copy.deepcopy((self.captures, self.context))
        result = self.live.evaluate(self.context, self.captures, self.config)
        snapshot = self.read(result['snapshot'])
        self.assertEqual(snapshot['exposureCaptures'], self.captures)
        self.assertEqual(snapshot['gateCaptures'], self.gate_captures)
        self.assertEqual(snapshot['claim'], self.claim)
        self.assertEqual(snapshot['executionClaim'], self.execution)
        self.assertEqual(snapshot['cohort'], [self.doc])
        self.assertEqual(before, (self.captures, self.context))
        self.assertFalse(Path(self.contract['path']+'.result.json').exists())
        with self.assertRaises(FileExistsError):
            self.live.evaluate(self.context, self.captures, self.config)
        self.assertEqual(self.child.call_count, 1)

    def test_copied_context_has_no_capability(self):
        with self.assertRaisesRegex(ValueError, 'capability'):
            self.live.evaluate(copy.deepcopy(self.context), self.captures, self.config)
        self.child.assert_not_called()

    def test_gate_refuses_before_owner_artifact_reads(self):
        self.context['phase'] = 'gate'
        self.activate()
        Path(self.config['path']).unlink()
        with self.assertRaisesRegex(ValueError, 'exposure'):
            self.live.evaluate(self.context, self.captures, self.config)
        self.child.assert_not_called()

    def test_unregistered_config_refuses(self):
        other = self.put('other.json', self.read(self.config))
        with self.assertRaisesRegex(ValueError, 'registered'):
            self.live.evaluate(self.context, self.captures, other)
        self.child.assert_not_called()

    def test_logical_claim_pid_is_the_first_attempt_and_is_not_this_process(self):
        # LIVE writes the logical claim once, in whichever attempt ran first.
        claim = self.read(self.claim); claim.update(pid=-1, gpuLease='an earlier attempt lease')
        self.claim = self.put('contract.json.started.json', claim)
        result = self.live.evaluate(self.context, self.captures, self.config)
        self.assertEqual(self.read(result['snapshot'])['claim'], self.claim)

    def test_execution_claim_must_be_this_process_lease_marker(self):
        for changes in ({'pid': -1}, {'gpuLease': 'another lease'}, {'output': '/elsewhere'},
                        {'schema': 'w50-live-attempt-1'}, {'logicalContract': self.batch}):
            with self.subTest(changes=changes):
                self.mark(**changes)
                with self.assertRaisesRegex(ValueError, 'analysis claim'):
                    self.live.evaluate(self.context, self.captures, self.config)
        self.mark()
        attempt = Path(self.contract['path']+'.phase')/'attempts/000001/started.json'
        attempt.parent.mkdir(parents=True)
        attempt.write_text(Path(self.execution['path']).read_text())
        self.context['executionClaim'] = pin(attempt); self.activate()
        with self.assertRaisesRegex(ValueError, 'analysis claim'):
            self.live.evaluate(self.context, self.captures, self.config)
        self.child.assert_not_called()

    def test_changed_root_claim_and_gate_cohort_refuse(self):
        for target, field, value in [(self.root, 'inputs', []), (self.claim, 'phase', 'gate'),
                                     (self.claim, 'output', '/elsewhere'),
                                     (self.gate_contract, 'cohort', [])]:
            with self.subTest(field=field):
                path = Path(target['path']); original = path.read_bytes()
                changed = self.read(target); changed[field] = value
                path.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    self.live.evaluate(self.context, self.captures, self.config)
                path.write_bytes(original)
        self.child.assert_not_called()

    def test_compiler_environment_does_not_reach_child(self):
        with patch.dict(os.environ, {'ESBUILD_BINARY_PATH': '/bad/compiler', 'NODE_OPTIONS': '--require=/bad',
                                     'PYTHONPATH': '/bad', 'TSX_TSCONFIG_PATH': '/bad'}):
            self.live.evaluate(self.context, self.captures, self.config)
        env = self.child.call_args.kwargs['env']
        for key in ('ESBUILD_BINARY_PATH', 'NODE_OPTIONS', 'PYTHONPATH', 'TSX_TSCONFIG_PATH'):
            self.assertNotIn(key, env)

    def test_real_child_runs_only_from_live_writer(self):
        patch.stopall()
        result = self.live.evaluate(self.context, self.captures, self.config)
        self.assertEqual(result['report']['noNewTrade'], 'synthetic')
        request = json.dumps({'snapshot': result['snapshot'], 'config': self.config})
        env = self.live.child_environment(result['snapshot'], self.read(self.config), self.config)
        env['W50_OWNER_LIVE_ROOT_SHA256'] = self.root['sha256']
        # A second unrelated launcher is not the claim's dispatcher parent.
        script = 'import subprocess,sys; p=subprocess.run(sys.argv[1:],input=sys.stdin.read(),text=True,capture_output=True); print(p.stderr); sys.exit(p.returncode)'
        child = self.live.subprocess.run([sys.executable, '-I', '-c', script,
            self.read(self.config)['node']['path'], str(self.here/'live-node.mjs')],
            input=request, text=True, capture_output=True, env=env)
        self.assertNotEqual(child.returncode, 0)
        self.assertIn('live parent', child.stdout)

    def refresh(self):
        # Re-register a wholly synthetic prospective chain after changing test source.
        closure = self.read(self.closure)
        for source in closure['sources']:
            source['sha256'] = pin(self.repo/source['path'])['sha256']
        self.closure = self.put('closure.json', closure)
        config = self.read(self.config); config['runtimeClosure'] = self.closure
        self.config = self.put('config.json', config)
        self.root = self.put('root.json', {'repo': str(self.repo), 'inputs': [self.config, self.closure]})
        gate = self.read(self.gate_contract); gate['executionRootSha256'] = self.root['sha256']
        self.gate_contract = self.put('gate.json', gate)
        result = self.read(self.gate_result); result['contractSha256'] = self.gate_contract['sha256']
        self.gate_result = self.put('gate.json.result.json', result)
        contract = self.read(self.contract)
        contract.update(executionRootSha256=self.root['sha256'], gateContract=self.gate_contract,
                        gateResult=self.gate_result, batch=self.batch)
        self.contract = self.put('contract.json', contract)
        claim = self.read(self.claim); claim.update(contractSha256=self.contract['sha256'],
                                                   batchSha256=self.batch['sha256'])
        self.claim = self.put('contract.json.started.json', claim)
        self.context.update(inputs=[self.config, self.closure], gateResult=self.gate_result,
                            batch=self.read(self.batch))
        self.mark()

    def test_real_child_refuses_unsealed_cjs_reader(self):
        patch.stopall()
        (self.repo/'unsealed.cjs').write_text('module.exports = {forged: true};')
        (self.here/'bridge.ts').write_text('import {createRequire} from "node:module"; '
            'const require=createRequire(import.meta.url); '
            'export function executeRequest(){ return require(process.cwd()+"/unsealed.cjs"); }')
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'Unsealed|unsealed'):
            self.live.evaluate(self.context, self.captures, self.config)
        self.assertFalse((self.output/'owner-candidate.report.json').exists())

    def test_gate_frozen_intrinsic_pin_cannot_change_at_exposure(self):
        batch = self.read(self.batch)
        batch['ownerIntrinsicRecords'] = self.put('different-intrinsic.json', {'syntheticRecords': [1]})
        self.batch = self.put('batch.json', batch)
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'intrinsic records'):
            self.live.evaluate(self.context, self.captures, self.config)
        self.child.assert_not_called()

    def prepare_venv_edge(self):
        patch.stopall()
        edge = self.here.parent/'owner/edge.py'
        edge.write_text('import json, sys, synthetic_venv_only\n'
            'print(json.dumps({"executable":sys.executable,"prefix":sys.prefix,'
            '"module":synthetic_venv_only.VALUE}))\n')
        site = subprocess.check_output([str(self.python), '-I', '-c',
            'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip()
        (Path(site)/'synthetic_venv_only.py').write_text('VALUE = "venv-only"\n')
        closure = self.read(self.closure)
        closure['sources'].append({'path': str(edge.relative_to(self.repo)), 'sha256': pin(edge)['sha256']})
        self.closure = self.put('closure.json', closure)
        config = self.read(self.config)
        config['pythonEnvironment'] = json.loads(subprocess.check_output([
            str(self.python), '-I', '-B', '-c', 'import runpy,json; '
            'print(json.dumps(runpy.run_path('+repr(str(self.here.parent/'execution/guard.py'))+
            ')["environment"]()))'], text=True))
        self.config = self.put('config.json', config)
        self.refresh()
        self.shim_env = self.live.child_environment({'path': '/not-read', 'sha256': '0'*64},
                                                   self.read(self.config), self.config)
        return edge

    def run_shim(self, launch=None):
        env = dict(self.shim_env)
        env['W50_OWNER_LIVE_CONFIG_SHA256'] = self.config['sha256']
        env['W50_OWNER_LIVE_NODE_PID'] = str(os.getpid())
        if launch is not None:
            env['W50_OWNER_LIVE_PYTHON'] = str(launch)
        return subprocess.run([str(self.here/'live-python-shim'), '-I', '-B',
            str(self.here.parent/'owner/edge.py'), '--contracts'],
            text=True, capture_output=True, env=env)

    def test_real_shim_preserves_lexical_venv_launch_and_site_packages(self):
        self.prepare_venv_edge()
        result = self.run_shim()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'executable': str(self.python),
            'prefix': str(self.venv), 'module': 'venv-only'})

    def test_real_node_to_shim_preserves_venv(self):
        self.prepare_venv_edge()
        (self.here/'bridge.ts').write_text('import {spawnSync} from "node:child_process"; '
            'export function executeRequest(){const p=spawnSync('+json.dumps(str(self.here/'live-python-shim'))+
            ',["-I","-B",'+json.dumps(str(self.here.parent/'owner/edge.py'))+',"--contracts"],'
            '{encoding:"utf8"});if(p.status)throw Error(p.stderr);return {cells:{},aggregates:{},'
            'intrinsic:{},provenance:{},noNewTrade:JSON.parse(p.stdout)};}')
        self.refresh()
        result = self.live.evaluate(self.context, self.captures, self.config)
        self.assertEqual(result['report']['noNewTrade'], {'executable': str(self.python),
            'prefix': str(self.venv), 'module': 'venv-only'})

    def test_shim_rejects_alternate_lexical_launch_even_with_same_target(self):
        self.prepare_venv_edge()
        alias = self.venv/'bin/alternate-python'
        alias.symlink_to(self.python)
        result = self.run_shim(alias)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('launch', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_shim_rejects_wrong_prefix_before_edge(self):
        self.prepare_venv_edge()
        config = self.read(self.config); config['pythonPrefix'] = str(self.venv/'wrong')
        self.config = self.put('config.json', config)
        result = self.run_shim(self.python)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('prefix', result.stderr.lower())
        self.assertEqual(result.stdout, '')

    def test_changed_venv_config_refuses_before_edge(self):
        self.prepare_venv_edge()
        with (self.venv/'pyvenv.cfg').open('a') as handle:
            handle.write('\n# changed after binding\n')
        result = self.run_shim(self.python)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Changed', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_changed_launch_target_refuses_before_child(self):
        self.prepare_venv_edge()
        other = self.venv/'other-python'
        shutil.copyfile(self.python.resolve(), other)
        self.python.unlink(); self.python.symlink_to(other)
        with patch.object(self.live.subprocess, 'run') as child:
            with self.assertRaisesRegex(ValueError, 'launch'):
                self.live.evaluate(self.context, self.captures, self.config)
            child.assert_not_called()

    def test_python_guard_refuses_late_dynamic_source_reader(self):
        edge = self.prepare_venv_edge()
        rogue = self.repo/'late.py'
        rogue.write_text('raise RuntimeError("must never execute")')
        edge.write_text('from pathlib import Path\nPath('+repr(str(rogue))+').read_bytes()\n')
        self.refresh()
        result = self.run_shim()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('late.py', result.stderr)
        self.assertNotIn('must never execute', result.stderr)

    def test_python_image_admission_is_same_cell_not_extension(self):
        edge = module(HERE/'live-python.py', 'synthetic_edge_images')
        candidate = self.put('synthetic-candidate.png', {'syntheticBytes': 1})
        native = self.put('synthetic-native.png', {'syntheticBytes': 2})
        reference = self.put('synthetic-reference.png', {'syntheticBytes': 3})
        profile = 'apple-macos-27.0-1x-dark-standard-glass0.25'
        key = profile+'/webgpu/synthetic'
        inputs = {'captures': {key: {'native': native}}, 'referenceCaptures': {key: {'web': reference}}}
        snapshot = {'cohort': [self.doc], 'gateCaptures': {'captures': []},
            'exposureCaptures': {'captures': [{'sceneSource': 'canonical', 'lane': 'candidate',
                'profile': profile, 'scene': 'synthetic', 'renderer': 'webgpu', 'candidate': self.doc,
                'artifacts': {'png': candidate}}]}}
        request = {'identity': [profile, 'synthetic'], 'native': native,
                   'current': reference, 'candidate': candidate}
        self.assertEqual(len(edge.edge_images(request, inputs, snapshot)), 3)
        request['candidate'] = self.put('foreign-but-pinned.png', {'syntheticBytes': 4})
        with self.assertRaisesRegex(ValueError, 'same-cell'):
            edge.edge_images(request, inputs, snapshot)

    # Metadata-only preflight (pre-seal review P1) -------------------------------------------
    PROBE = '{"exercise":"synthetic source-only","pixels":"NONE"}\n'

    def exercised(self, evidence=None):
        """Record a synthetic exercise for the closure and, optionally, owner inputs whose
        evidence pins name files; the probe launch itself is faked by probe()."""
        closure = self.read(self.closure)
        closure['exerciseSha256'] = hashlib.sha256(self.PROBE.encode()).hexdigest()
        self.closure = self.put('closure.json', closure)
        if evidence is not None:
            config = self.read(self.config)
            config['ownerInputs'] = self.put('inputs.json', {'captures': {'k': {'web': evidence}}})
            config['completedOwnerReferences'] = self.put('references.json', {'cells': [{'evidence': [evidence]}]})
            self.config = self.put('config.json', config)
        self.refresh()

    def probe(self, stdout=None, returncode=0, intrinsic=None):
        """Fake both pre-marker launches: the source-only probe (live-probe.mjs) answers `stdout`,
        the intrinsic request (live-node.mjs) answers `intrinsic` (admission by default)."""
        launches = []
        def run(args, **kwargs):
            launches.append((list(args), kwargs['env'], kwargs.get('input')))
            if str(args[-1]).endswith('live-node.mjs'):
                code, out = intrinsic or (0, self.live.INTRINSIC_ADMITTED)
                return type('Result', (), {'returncode': code, 'stderr': 'synthetic intrinsic refusal', 'stdout': out})()
            return type('Result', (), {'returncode': returncode, 'stderr': 'synthetic probe refusal',
                                       'stdout': self.PROBE if stdout is None else stdout})()
        patch.stopall()
        patch.object(self.live.subprocess, 'run', side_effect=run).start()
        return launches

    @contextlib.contextmanager
    def creation_context(self):
        """LIVE's context at the exposure's creation: no contract, output or claim exists yet.
        (This suite's original dispatcher hashes the contract in require_context; LIVE's own
        owner-admission capability is exercised in live-roles/test_owner.py.)"""
        context = {**self.context, 'contract': None, 'output': None, 'executionClaim': None, 'logicalClaim': None}
        def genuine(value):
            if value is not context: raise ValueError('no dispatcher capability')
            return value
        with patch.object(self.dispatch, 'require_context', genuine):
            yield context

    def test_preflight_admits_at_creation_and_before_each_marker_and_writes_nothing(self):
        evidence = self.put('evidence.png', {'syntheticBytes': 5})
        self.exercised(evidence)
        launches = self.probe()
        before = sorted((str(p), p.read_bytes()) for p in Path(self.temp.name).rglob('*') if p.is_file())
        expected = {'admitted': True, 'evidencePins': 1}
        self.assertEqual(self.live.preflight(self.context, self.config), expected)
        with self.creation_context() as context:
            self.assertEqual(self.live.preflight(context, self.config), expected)
        after = sorted((str(p), p.read_bytes()) for p in Path(self.temp.name).rglob('*') if p.is_file())
        self.assertEqual(before, after)
        self.assertEqual(len(launches), 4)
        node = self.read(self.config)['node']['path']
        for (args, env, _), (intrinsic, ienv, request) in zip(launches[::2], launches[1::2]):
            self.assertEqual(args, [node, '--import', str(self.here.parent/'owner/node-guard.mjs'), str(self.here/'live-probe.mjs')])
            self.assertEqual((env['W50_WEB_CLOSURE'], env['W50_WEB_CLOSURE_SHA256']),
                             (self.closure['path'], self.closure['sha256']))
            self.assertNotIn('W50_OWNER_LIVE_SNAPSHOT', env)
            # The intrinsic request follows the probe: root and batch bound by content.
            self.assertEqual(intrinsic, [node, str(self.here/'live-node.mjs')])
            self.assertEqual(json.loads(request), {'config': self.config, 'root': self.root, 'batch': self.batch})
            self.assertEqual((ienv['W50_OWNER_LIVE_ROOT_SHA256'], ienv['W50_OWNER_LIVE_BATCH_SHA256']),
                             (self.root['sha256'], self.batch['sha256']))
            self.assertNotIn('W50_OWNER_LIVE_SNAPSHOT', ienv)

    def test_preflight_refuses_owner_drift_before_any_marker(self):
        evidence = self.put('evidence.png', {'syntheticBytes': 5})
        self.exercised(evidence)
        original = Path(evidence['path']).read_bytes()
        def changed_evidence():
            Path(evidence['path']).write_bytes(original+b' '); return lambda: Path(evidence['path']).write_bytes(original)
        def missing_evidence():
            aside = Path(evidence['path']+'.aside'); Path(evidence['path']).rename(aside)
            return lambda: aside.rename(evidence['path'])
        def changed_source():
            bridge = self.here/'bridge.ts'; raw = bridge.read_bytes(); bridge.write_bytes(raw+b'\n')
            return lambda: bridge.write_bytes(raw)
        def changed_intrinsic():
            path = Path(self.intrinsic['path']); raw = path.read_bytes(); path.write_bytes(raw+b' ')
            return lambda: path.write_bytes(raw)
        cases = [(changed_evidence, 'Changed owner evidence pin', None), (missing_evidence, 'Missing owner evidence', None),
                 (changed_source, 'Changed', None), (changed_intrinsic, 'Changed', None),
                 (lambda: (lambda: None), 'no longer reproduces', '{"exercise":"other"}\n'),
                 (lambda: (lambda: None), 'probe refused', None)]
        for index, (drift, message, stdout) in enumerate(cases):
            for creation in (False, True):
                with self.subTest(case=index, creation=creation), \
                        (self.creation_context() if creation else contextlib.nullcontext(self.context)) as context:
                    launches = self.probe(stdout, returncode=1 if message == 'probe refused' else 0)
                    restore = drift()
                    try:
                        with self.assertRaisesRegex(ValueError, message):
                            self.live.preflight(context, self.config)
                    finally:
                        restore()
                    self.assertFalse(any('live-node.mjs' in ' '.join(a) for a, *_ in launches))
        self.assertFalse((self.output/'owner-candidate.snapshot.json').exists())

    def test_preflight_rechecks_the_exposure_contract_once_it_exists(self):
        self.exercised()
        self.probe()
        path = Path(self.claim['path']); raw = path.read_bytes()
        changed = self.read(self.claim); changed['output'] = '/elsewhere'
        path.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, 'Changed exposure claim'):
            self.live.preflight(self.context, self.config)
        with self.creation_context() as context:
            self.assertEqual(self.live.preflight(context, self.config)['admitted'], True)
        path.write_bytes(raw)
        self.assertEqual(self.live.preflight(self.context, self.config)['admitted'], True)

    def test_preflight_runs_the_intrinsic_request_at_the_gates_creation_and_refuses_on_it(self):
        """Second pre-seal review P1: the frozen engine's refusal of the batch's intrinsic records
        refuses the admission, at the gate's creation as at the exposure's; nothing is written."""
        self.exercised()
        gate = {**self.context, 'phase': 'gate', 'batchPath': self.gate_batch['path'], 'batch': self.read(self.gate_batch),
                'gateResult': None, 'gateCaptures': None}
        for context in (gate, self.context):
            with self.subTest(phase=context['phase']):
                launches = self.probe()
                with self.creation_context() as created:
                    created.update({k: context[k] for k in ('phase', 'batchPath', 'batch', 'gateResult', 'gateCaptures')})
                    self.assertEqual(self.live.preflight(created, self.config)['admitted'], True)
                    self.assertEqual(json.loads(launches[-1][2])['batch'], pin(Path(context['batchPath'])))
                    for answer, message in (((1, ''), 'refused the intrinsic records'),
                                            ((0, '{"intrinsic":{"X76":"within"}}\n'), 'no admission')):
                        self.probe(intrinsic=answer)
                        with self.assertRaisesRegex(ValueError, message):
                            self.live.preflight(created, self.config)
        launches = self.probe()
        with self.creation_context() as created:
            created.update(phase='fit', gateResult=None)
            self.live.preflight(created, self.config)
        self.assertFalse(any('live-node.mjs' in ' '.join(a) for a, *_ in launches))

    def test_preflight_refuses_an_existing_exclusive_owner_output(self):
        """Second pre-seal review P3: evaluate opens both files exclusively after the analysis
        marker, so one already present refuses the admission before it."""
        self.exercised(); self.probe()
        for name in ('owner-candidate.snapshot.json', 'owner-candidate.report.json'):
            with self.subTest(name=name):
                path = self.output/name; path.symlink_to(self.output/'absent-target')
                with self.assertRaisesRegex(ValueError, 'exclusive output already exists'):
                    self.live.preflight(self.context, self.config)
                path.unlink()
        self.assertEqual(self.live.preflight(self.context, self.config)['admitted'], True)

    def test_real_child_answers_the_intrinsic_request_only_when_bound(self):
        """The real live-node.mjs bootstrap's intrinsic branch: it admits through the bridge's
        checkIntrinsicRecords, carries the bridge's refusal, and refuses an unbound request."""
        patch.stopall()
        self.exercised()
        (self.here/'bridge.ts').write_text('export const executeRequest = () => ({});\n'
            'export function checkIntrinsicRecords(request: any) {\n'
            '  if (process.env.W50_SYNTHETIC_REFUSE) throw Error("synthetic engine refusal");\n'
            '  return {intrinsic: "ADMITTED"};\n}\n')
        self.refresh()
        config = self.read(self.config)
        self.live.intrinsic_probe(config, self.config, self.root, self.batch)
        env = self.live.live_environment(config, self.config)
        env.update(W50_OWNER_LIVE_ROOT_SHA256=self.root['sha256'], W50_OWNER_LIVE_BATCH_SHA256='0'*64)
        child = subprocess.run([config['node']['path'], str(self.here/'live-node.mjs')], text=True, capture_output=True,
            input=json.dumps({'config': self.config, 'root': self.root, 'batch': self.batch}), env=env, cwd=self.repo)
        self.assertNotEqual(child.returncode, 0); self.assertIn('not bound', child.stderr)
        # The seam binds root and batch itself; the bridge's own refusal reaches the caller.
        with patch.object(self.live, 'live_environment', lambda *a: {**env, 'W50_SYNTHETIC_REFUSE': '1'}):
            with self.assertRaisesRegex(ValueError, 'synthetic engine refusal'):
                self.live.intrinsic_probe(config, self.config, self.root, self.batch)

    def test_node_probe_reproduces_a_fresh_discovery_exercise(self):
        """The real live-probe.mjs, launched as preflight launches it, against a closure the real
        discovery (live-discover.mjs) exercised just now: stdout reproduces exerciseSha256."""
        patch.stopall()
        real = HERE.parents[4]
        node = pin(Path(shutil.which('node')).resolve())
        tsx = pin((HERE.parents[2]/'node_modules/tsx/dist/esm/api/index.mjs').resolve())
        scratch = Path(self.temp.name).resolve()
        script = ('import fs from "node:fs";import {createHash} from "node:crypto";'
            'const m=await import(process.argv[1]);const s=m.candidateSources();const p=process.argv[2];'
            'fs.writeFileSync(p,JSON.stringify(s));const raw=fs.readFileSync(p);'
            'const pin={path:fs.realpathSync(p),sha256:createHash("sha256").update(raw).digest("hex")};'
            'const out=m.exerciseRuntime(process.argv[3],pin,JSON.parse(process.argv[4]),process.argv[5]);'
            'process.stdout.write(JSON.stringify(out));')
        found = subprocess.run([node['path'], '--input-type=module', '-e', script, str(HERE/'live-discover.mjs'),
            str(scratch/'static.json'), str(real), json.dumps({'node': node, 'tsx': tsx}), str(scratch/'runtime.json')],
            text=True, capture_output=True, cwd=real)
        self.assertEqual(found.returncode, 0, found.stderr[-2000:])
        runtime = json.loads(found.stdout)
        closure = json.loads(Path(runtime['path']).read_text())
        live = module(HERE/'live.py', 'real_owner_live_probe')
        live.node_probe({'node': node, 'tsx': tsx}, runtime, closure)
        closure['exerciseSha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'no longer reproduces'):
            live.node_probe({'node': node, 'tsx': tsx}, runtime, closure)

    def test_closure_mutation_refuses_before_child(self):
        (self.here/'bridge.ts').write_text('throw Error("changed");')
        with self.assertRaisesRegex(ValueError, 'Changed'):
            self.live.evaluate(self.context, self.captures, self.config)
        self.child.assert_not_called()


if __name__ == '__main__':
    unittest.main()
