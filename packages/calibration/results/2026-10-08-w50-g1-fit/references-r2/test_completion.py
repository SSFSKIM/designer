"""Admitted-current completion tests using real dispatcher validation over synthetic receipts."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
EXECUTION = HERE.parent/'execution'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m


class CompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.C = module('reference_current_completion', HERE/'completion.py')
        cls.fixture_module = module('reference_current_fixture', EXECUTION/'test_current.py')

    def setUp(self):
        self.fixture = self.fixture_module.CurrentOnly(); self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.f = self.fixture.fixture; self.D = self.fixture_module.D
        repo = self.fixture.repo; pin = lambda p: self.D.pin(repo, p)
        # Synthetic originals and namespace copies differ ONLY by profileKey, including digest.
        for candidate in self.f['baselines']:
            path = repo/candidate['path']; doc = json.loads(path.read_bytes())
            for slot, item in doc['endpoints'].items():
                endpoint_path = path.parent/item['path']; endpoint = json.loads(endpoint_path.read_bytes())
                scheme = slot.split('.')[1]; pose = slot.split('.')[0]
                suffix = '-receded' if pose == 'receded' else ''
                key = endpoint['profileKey']; source_key = key.replace('0.250', '0.25').replace('0.500', '0.5')
                source_path = repo/'packages/calibration/profiles'/(source_key+'.json')
                original = json.loads(source_path.read_bytes())
                original['resolvedMaterialSha256'] = ('d' if scheme == 'dark' else 'e')*16
                source_path.write_text(json.dumps(original)+'\n')
                endpoint['resolvedMaterialSha256'] = original['resolvedMaterialSha256']
                endpoint_path.write_text(json.dumps(endpoint)+'\n'); item['sha256'] = self.D.sha(endpoint_path)
            path.write_text(json.dumps(doc)+'\n'); candidate['sha256'] = self.D.sha(path)
        original_inventory = json.loads(self.f['refs'].read_bytes())
        for row in original_inventory['cells']:
            row['currentEvidence'] = row.pop('currentEvidence', None)
            row['currentMetadata'] = row.get('nativeEvidence')
            if row['profile'].endswith('-glass0.5') and '-1x-' in row['profile'] and row['scene'] == 'impulse__rrect-ml__rest':
                row.update(role='gate', currentEvidence=None, currentMetadata=None, native=.1, current=.2, B=.003,
                           fidelity={'native': .4, 'current': .5}, historical=[{'value': .6}])
        self.f['refs'].write_text(json.dumps(original_inventory)+'\n')
        scenes_path = repo/'apps/reference-apple/scenes.json'; scenes_path.parent.mkdir(parents=True)
        scenes_path.write_text(json.dumps({'scenes': [
            {'id': 'impulse__rrect-ml__rest', 'state': 'rest'},
            {'id': 'impulse__rrect-ml__inactive', 'state': 'inactive'}]})+'\n')
        for path in (self.f['one'], self.f['two']):
            doc = json.loads(path.read_bytes())
            doc['sources'] = [pin(repo/item['path']) for item in doc['sources']] + [pin(scenes_path)]
            if path == self.f['two']: doc['partOneSha256'] = self.D.sha(self.f['one'])
            path.write_text(json.dumps(doc)+'\n'); self.fixture_module.sidecar(path)
        # Extend the synthetic actual capture report with real drawn endpoint/digest fields.
        text = self.fixture.adapter.read_text()
        text = text.replace('"devicePixelRatio":1',
            '"devicePixelRatio":1,"material":{"profileKey":"apple-macos-27.0-1x-dark-standard-glass"+str(json.loads((Path(context["repo"])/run["candidate"]["path"]).read_text())["glassTintAmount"])+"00","resolvedMaterialSha256":"dddddddddddddddd","tuned":False,"glassTintAmount":json.loads((Path(context["repo"])/run["candidate"]["path"]).read_text())["glassTintAmount"]},"groups":[{"state":{"materialDocument":{"profileKey":"apple-macos-27.0-1x-dark-standard-glass"+str(json.loads((Path(context["repo"])/run["candidate"]["path"]).read_text())["glassTintAmount"])+"00","resolvedMaterialSha256":"dddddddddddddddd","tuned":False,"glassTintAmount":json.loads((Path(context["repo"])/run["candidate"]["path"]).read_text())["glassTintAmount"]}}}]')
        # .25 namespace string is .250 rather than .2500; normalize the synthetic report.
        text = text.replace('+"00"', '+("00" if json.loads((Path(context["repo"])/run["candidate"]["path"]).read_text())["glassTintAmount"]==.5 else "0")')
        self.fixture.adapter.write_text(text)
        self.fixture.sources = {str(p.relative_to(repo)): self.D.sha(p) for p in
            [self.fixture.home/n for n in ('dispatch.py','guard.py','admission.py')]+[self.fixture.adapter,self.fixture.probe]}
        self.fixture.batch = self.fixture.make_batch('exposed')
        self.instrument = self.fixture.seal(); self.contract = self.D.current_contract(self.instrument, self.fixture.batch)
        completed = self.fixture.execute(self.instrument, self.contract, self.fixture.batch)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result_path = Path(str(self.contract)+'.result.json')
        self.config = {'instrument': pin(self.instrument), 'results': [pin(result_path)]}
        self.rows = copy.deepcopy(json.loads(self.f['refs'].read_bytes())['cells'])
        for row in self.rows:
            if row['profile'].endswith('-glass0.5') and '-1x-' in row['profile'] and row['scene'] == 'impulse__rrect-ml__rest':
                row.update(role='gate', currentEvidence=None, currentMetadata=None, native=.1, current=.2, B=.003,
                           fidelity={'native': .4, 'current': .5}, historical=[{'value': .6}])
        self.repo = repo.resolve()

    def complete(self):
        return self.C.complete_current_projection(self.repo, self.rows, self.config)

    def test_source_probe_derives_relocated_bootstrap_and_does_not_open_result_receipts(self):
        import shutil
        target = self.repo/'replacement-current/execution'; target.mkdir(parents=True)
        for name in ('dispatch.py', 'admission.py'):
            shutil.copyfile(self.fixture.home/name, target/name)
        doc = json.loads(self.instrument.read_bytes())
        doc['bootstrap'] = self.D.pin(self.repo, target/'dispatch.py')
        doc['closure']['sources'] = {str((target/name).relative_to(self.repo)): self.D.sha(target/name)
                                     for name in ('dispatch.py', 'admission.py')}
        root = target/'current-instrument-root.json'; root.write_text(json.dumps(doc)+'\n')
        config = {'instrument': self.D.pin(self.repo, root),
                  'results': [{'path': 'not-present-result.json', 'sha256': '0'*64}]}
        result = self.C.source_probe(config, repo=self.repo)
        self.assertEqual(result['bootstrap'], doc['bootstrap'])
        self.assertEqual(result['status'], 'SOURCE_ONLY')

    def test_fill_only_original_null_artifact_slots_and_keep_every_other_field(self):
        before = copy.deepcopy(self.rows); projection = self.complete()
        self.assertEqual(projection['originalRows'], before)
        self.assertEqual(len(projection['completedKeys']), 1)
        for old, new in zip(before, projection['rows']):
            key = [old[k] for k in ('profile','renderer','scene','statistic')]
            if key in projection['completedKeys']:
                self.assertIsNotNone(new['currentEvidence']); self.assertIsNotNone(new['currentMetadata'])
                self.assertEqual({k:v for k,v in new.items() if k not in ('currentEvidence','currentMetadata')},
                                 {k:v for k,v in old.items() if k not in ('currentEvidence','currentMetadata')})
            else: self.assertEqual(old, new)
        self.assertTrue(projection['chainPins'])

    def test_forged_result_or_claim_and_missing_receipt_refuse_without_numeric_override(self):
        path = Path(str(self.contract)+'.result.json'); original = path.read_bytes()
        for change in ('numeric', 'claim', 'receipt'):
            with self.subTest(change=change):
                doc = json.loads(original)
                if change == 'numeric': doc['report']['analysis'] = {'native': 0}
                elif change == 'claim': doc['claimSha256'] = '0'*64
                else: doc['captureReceipt'] = {'members': [], 'artifacts': []}
                path.write_text(json.dumps(doc)+'\n'); self.fixture_module.sidecar(path)
                self.config['results'] = [self.D.pin(self.repo, path)]
                with self.assertRaises(ValueError): self.complete()
        path.write_bytes(original); self.fixture_module.sidecar(path)

    def test_namespace_doc_may_not_change_any_original_field_or_digest(self):
        doc = self.D.root_doc(self.instrument)
        candidate = doc['baselineDocuments'][1]
        value = json.loads((self.repo/candidate['path']).read_bytes())
        endpoint = (self.repo/candidate['path']).parent/value['endpoints']['active.dark']['path']
        changed = json.loads(endpoint.read_bytes()); changed['resolvedMaterialSha256'] = '0'*16
        endpoint.write_text(json.dumps(changed)+'\n')
        # Make candidate pins coherent to exercise endpoint semantic identity, not a stale
        # file-hash refusal: admission permits digest metadata, completion does not.
        value['endpoints']['active.dark']['sha256'] = self.D.sha(endpoint)
        candidate_path = self.repo/candidate['path']; candidate_path.write_text(json.dumps(value)+'\n')
        doc['baselineDocuments'][1] = self.D.pin(self.repo, candidate_path)
        with self.assertRaisesRegex(ValueError, 'endpoint field or digest'):
            self.C.original_endpoints(self.D, self.repo, doc)

    def test_caller_numeric_change_cannot_enter_the_completed_pin_projection(self):
        selected = next(r for r in self.rows if '-1x-' in r['profile'] and r['profile'].endswith('glass0.5') and
                        r['scene'] == 'impulse__rrect-ml__rest')
        selected['B'] = 100
        with self.assertRaisesRegex(ValueError, 'numeric override'):
            self.complete()

    def test_drawn_artifact_digest_must_be_original_not_just_candidate_stamp(self):
        doc = self.D.root_doc(self.instrument)
        endpoints = self.C.original_endpoints(self.D, self.repo, doc)
        result = self.D.result_for(self.contract)
        capture = next(c for c in result['captures']['captures'] if c['profile'].endswith('glass0.5'))
        path = Path(capture['artifacts']['report']['path']); report = json.loads(path.read_bytes())
        report['page']['material']['resolvedMaterialSha256'] = '0'*16
        path.write_text(json.dumps(report)+'\n')
        with self.assertRaisesRegex(ValueError, 'drawn gate0 endpoint'):
            self.C.drawn_original(self.D, capture, {'state': 'rest'}, endpoints)

    def test_historical_or_nonnull_slot_cannot_be_replaced_by_capture_projection(self):
        selected = next(r for r in self.rows if r['profile'].endswith('glass0.5') and
                        r['scene'] == 'impulse__rrect-ml__rest')
        selected['role'] = 'historical-prediction-check'
        with self.assertRaises(ValueError): self.complete()


if __name__ == '__main__': unittest.main()
