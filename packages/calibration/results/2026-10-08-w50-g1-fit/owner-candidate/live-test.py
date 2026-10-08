"""Synthetic dispatcher leases only; no material documents, captured pixels or owner readings."""
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
        self.activate()
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

    def test_genuine_snapshot_preserves_bundles_and_is_exclusive(self):
        before = copy.deepcopy((self.captures, self.context))
        result = self.live.evaluate(self.context, self.captures, self.config)
        snapshot = self.read(result['snapshot'])
        self.assertEqual(snapshot['exposureCaptures'], self.captures)
        self.assertEqual(snapshot['gateCaptures'], self.gate_captures)
        self.assertEqual(snapshot['claim'], self.claim)
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

    def test_changed_root_claim_and_gate_cohort_refuse(self):
        for target, field, value in [(self.root, 'inputs', []), (self.claim, 'pid', -1),
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
        self.activate()

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

    def test_closure_mutation_refuses_before_child(self):
        (self.here/'bridge.ts').write_text('throw Error("changed");')
        with self.assertRaisesRegex(ValueError, 'Changed'):
            self.live.evaluate(self.context, self.captures, self.config)
        self.child.assert_not_called()


if __name__ == '__main__':
    unittest.main()
