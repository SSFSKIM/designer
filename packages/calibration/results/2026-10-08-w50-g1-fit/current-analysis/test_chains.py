"""Real completed-chain and native-role validators over disposable synthetic evidence only."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
FIT = HERE.parent


def source(path, name):
    result = types.ModuleType(name); result.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), result.__dict__)
    return result


A = source(HERE/'analysis.py', 'w50_synthetic_chain_analysis')
C = source(FIT/'execution/test_current.py', 'w50_synthetic_current_fixture')
F = source(FIT/'native/test_reader.py', 'w50_synthetic_role_fixture')


class CompletedChainTests(unittest.TestCase):
    def fixture(self):
        fixture = C.CurrentOnly(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        repo = fixture.repo.resolve(); home = repo/'execution'
        batches = [fixture.batch, fixture.make_batch('impulse__rrect-ml__inactive')]
        for batch_path in batches:
            batch = C.D.load(batch_path)
            for run in batch['runs']:
                run.update(sceneSource='canonical', captureRoot=str(repo/'captures'/batch_path.stem/run['id']))
            C.write(batch_path, batch)
        f = fixture.fixture
        root = C.D.seal_current_root(fixture.repo, fixture.home, f['one'], f['two'], f['refs'], f['manifest'],
            fixture.adapter, fixture.probe, fixture.sources, f['baselines'],
            [C.D.pin(repo, p) for p in batches])
        results = []
        for batch_path in batches:
            batch = C.D.load(batch_path); contract = C.D.current_contract(root, batch_path)
            output = repo/'captures'/batch_path.stem
            claim_path = Path(str(contract)+'.started.json')
            C.write(claim_path, dict(contractSha256=C.D.sha(contract), batchSha256=C.D.sha(batch_path),
                phase='current', output=str(output), numericalAdmission=None, pid=123, gpuLease='synthetic-completed'))
            captures = []
            for run in batch['runs']:
                scene = run['scenes'][0]; artifacts = {}
                for name in ('png', 'cell', 'report'):
                    path = Path(run['captureRoot'])/(scene+'-'+name)
                    value = dict(capturePath='declarationSha256='+run['candidate']['sha256'][:12], page=dict(
                        sceneId=scene, requestedRenderer=run['renderer'], devicePixelRatio=1,
                        candidateDocument=dict(declarationSha256=run['candidate']['sha256'][:12])))
                    C.write(path, value)
                    artifacts[name] = {'path': str(path), 'sha256': C.D.sha(path)}
                captures.append(dict(profile=run['profile'], renderer=run['renderer'], scene=scene,
                    sceneSource='canonical', lane='current', candidate=run['candidate'], artifacts=artifacts))
            envelope = dict(status='CAPTURED', candidateSha256s=sorted(p['sha256'] for p in batch['cohort']),
                            captures=captures)
            receipt = C.D.admission_module(C.D.root_doc(root)).validate_captures(batch, envelope, output)
            result = Path(str(contract)+'.result.json')
            C.D.write_sealed(result, dict(contractSha256=C.D.sha(contract), claimSha256=C.D.sha(claim_path),
                report=dict(status='CAPTURED', captures=envelope), captureReceipt=receipt, captures=envelope))
            results.append(C.D.pin(repo, result))
        config = {'current': {'instrument': C.D.pin(repo, root), 'results': results}}
        return fixture, repo, root, config

    def completed(self, repo, root, config):
        with patch.object(A, 'REPO', repo), patch.object(A, 'FIT', repo/'packages/calibration/results/synthetic-fit'):
            return A.completed(config, root)

    def test_both_completed_chains_preserve_actual_gate0_candidates_and_original_pair(self):
        _, repo, root, config = self.fixture()
        admitted = self.completed(repo, root, config)
        self.assertEqual(len(admitted['members']), 4)
        self.assertEqual(len(admitted['candidates']), 2)
        for candidate in admitted['candidates'].values():
            self.assertEqual(set(candidate['originalDocumentPair']), {'active.dark', 'receded.dark'})
            for endpoint in candidate['endpoints'].values():
                self.assertEqual(endpoint['patch'], {'heldLeaf': 3})
        self.assertEqual(len(admitted['chain']), 12)

    def test_missing_second_result_and_changed_full_receipt_are_not_complete(self):
        _, repo, root, config = self.fixture()
        incomplete = copy.deepcopy(config); incomplete['current']['results'].pop()
        with self.assertRaises(ValueError): self.completed(repo, root, incomplete)
        result = C.D.load(repo/config['current']['results'][0]['path'])
        Path(result['captureReceipt']['artifacts'][0]['path']).write_text('changed')
        with self.assertRaisesRegex(ValueError, 'artifact changed'):
            self.completed(repo, root, config)

    def test_claim_substitution_is_rejected_before_capture_analysis(self):
        _, repo, root, config = self.fixture()
        result_path = repo/config['current']['results'][0]['path']
        contract = result_path.with_name(result_path.name.removesuffix('.result.json'))
        claim = Path(str(contract)+'.started.json'); value = C.D.load(claim)
        value['numericalAdmission'] = {'invented': True}; C.write(claim, value)
        with self.assertRaisesRegex(ValueError, 'claimed invocation'):
            self.completed(repo, root, config)


class NativeContractTests(unittest.TestCase):
    def test_original_native_prospective_contract_is_verified_without_reading_exports(self):
        import shutil
        fixture = source(FIT/'native/test_bootstrap.py', 'w50_synthetic_native_bootstrap')
        with tempfile.TemporaryDirectory() as td:
            helper = fixture.BootstrapTests()
            repo, native, batch = helper.fixture(td)
            helper.seal(native, batch)
            for export in json.loads(batch.read_bytes())['exports']: shutil.rmtree(export['root'])
            config = {name: C.D.pin(repo, native/filename) for name, filename in
                (('instrument', 'instrument-root.json'), ('contract', 'execution-contract.json'),
                 ('batch', 'read-batch.json'))}
            verified = A.native_contract(repo, config)
            self.assertEqual(verified, json.loads(batch.read_bytes()))
            (native/'reader.py').write_text((native/'reader.py').read_text()+'\n# changed\n')
            with self.assertRaisesRegex(ValueError, 'Changed'):
                A.native_contract(repo, config)


class NativeRoleTests(unittest.TestCase):
    def fixture(self, directory):
        repo = Path(directory).resolve(); manifest, scenes = F.bed()
        manifest_path = repo/'manifest.json'; C.write(manifest_path, manifest)
        batch = dict(inputs=dict(manifest=C.D.pin(repo, manifest_path), declaration={'sha256': F.DECLARATION}), exports=[])
        config = {'native': {'reports': {}}}
        for role in ('calibration', 'validation'):
            export = repo/role; export.mkdir()
            digest, _ = F.tree(export, role, manifest, scenes)
            report = A.M.R.read_role_export(export, digest, role, manifest, scenes,
                                           expected_declaration_sha256=F.DECLARATION)
            path = repo/(role+'.json.gz'); path.write_bytes(gzip.compress(json.dumps(report).encode(), mtime=0))
            config['native']['reports'][role] = C.D.pin(repo, path)
            batch['exports'].append(dict(role=role, root=str(export), indexSha256=digest))
        return repo, config, batch, scenes

    def test_original_report_runs_and_no_glass_dependencies_match_role_export(self):
        with tempfile.TemporaryDirectory() as td:
            repo, config, batch, scenes = self.fixture(td)
            with patch.object(A, 'REPO', repo): roles = A.native_roles(config, batch, scenes)
            self.assertEqual(set(roles), {'calibration', 'validation'})
            self.assertEqual([len(roles[r]['cells']) for r in ('calibration', 'validation')], [2, 1])

    def test_re_pinned_native_report_cannot_substitute_dependency_or_run_identity(self):
        for mutation in ('dependency', 'run', 'role', 'membership'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                repo, config, batch, scenes = self.fixture(td)
                p = repo/config['native']['reports']['calibration']['path']
                report = json.loads(gzip.decompress(p.read_bytes()))
                if mutation == 'dependency': report['dependencies'][0]['evidence']['sha256'] = '0'*64
                elif mutation == 'run': report['cells'][0]['runs'][0]['dependency'] = 'other-role'
                elif mutation == 'role': report['role'] = 'blind'
                else: report['cells'].pop()
                p.write_bytes(gzip.compress(json.dumps(report).encode(), mtime=0))
                config['native']['reports']['calibration'] = C.D.pin(repo, p)
                with patch.object(A, 'REPO', repo), self.assertRaises(ValueError):
                    A.native_roles(config, batch, scenes)


if __name__ == '__main__': unittest.main()
