"""Synthetic completion tests: missing numbers must never count as measurements."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prefit', HERE / 'prefit.py')
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


class Completion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        source = self.repo / 'pixels'; source.write_bytes(b'synthetic pixels')
        pin = {'path': 'pixels', 'sha256': P.sha(source)}
        self.cell = dict(profile='p', renderer='webgpu', scene='s', statistic='deep8-channel-median',
                         role='calibration', support='deep8', currentGeneration='g',
                         currentDocumentPair={'active': 'a'}, historical=[], nativeEvidence=pin,
                         currentEvidence=pin, B=None, status='UNMEASURED', nativeIdentity='id')
        self.original = {'schema': 'references', 'cells': [self.cell], 'generations': {'g': 'fixed'}}
        self.done = copy.deepcopy(self.original)
        self.done['cells'][0].update(native=[1, 2, 3], current=[2, 3, 4], B=1, status='MEASURED')

    def check(self, done=None, exemptions=()):
        P.validate_completion(self.original, self.done if done is None else done,
                              list(exemptions), self.repo)

    def test_valid_channel_reading(self):
        self.check()

    def test_missing_nonfinite_and_wrong_shape_readings_fail(self):
        for value in (None, [], [1, 2], [1, 2, float('nan')], True, {'ready': True}):
            with self.subTest(value=value):
                bad = copy.deepcopy(self.done); bad['cells'][0]['native'] = value
                with self.assertRaises(ValueError): self.check(bad)

    def test_every_original_field_and_order_survives(self):
        for field in ('support', 'nativeIdentity', 'currentGeneration', 'historical'):
            bad = copy.deepcopy(self.done); bad['cells'][0][field] = 'changed'
            with self.subTest(field=field), self.assertRaises(ValueError): self.check(bad)
        bad = copy.deepcopy(self.done); bad['generations'] = {}
        with self.assertRaises(ValueError): self.check(bad)

    def test_known_numbers_cannot_be_replaced(self):
        self.original['cells'][0]['native'] = [1, 2, 3]
        self.done['cells'][0]['native'] = [1, 2, 4]
        with self.assertRaises(ValueError): self.check()

    def test_blind_remains_identity_only(self):
        self.original['cells'][0]['role'] = 'blind'
        row = self.done['cells'][0]; row.update(role='blind', status='SEALED_BLIND', B=None)
        row.pop('native'); row.pop('current')
        self.check()
        row['native'] = [1, 2, 3]
        with self.assertRaises(ValueError): self.check()

    def test_reported_exemption_still_requires_values(self):
        for doc in (self.original, self.done):
            doc['cells'][0]['statistic'] = 'T1-full-silhouette'
        row = self.done['cells'][0]; row.update(native=0, current=0, status='REPORTED', B=None)
        key = list(P.key(row))
        self.check(exemptions=[key])
        row.pop('current')
        with self.assertRaises(ValueError): self.check(exemptions=[key])

    def test_low_end_path_shape_is_not_any_nonempty_object(self):
        for doc in (self.original,self.done):
            doc['cells'][0].update(statistic='low-end-path-level',scene='impulse__rrect-lg__rest')
        row=self.done['cells'][0]
        row.update(native={'deep8Far24LumaMean':1, 'deep8Far24LumaMedian':2},
                   current={'deep8Far24LumaMean':2, 'deep8Far24LumaMedian':3},
                   fidelity={'deep8Far24LumaMean':1, 'deep8Far24LumaMedian':1})
        self.check()
        row.update(native={'placeholder':1},current={'placeholder':1})
        with self.assertRaises(ValueError): self.check()

    def test_fidelity_shape_cannot_be_placeholder(self):
        self.done['cells'][0]['fidelity']={'placeholder':1}
        with self.assertRaises(ValueError): self.check()

    def test_blind_extra_statistics_cannot_be_smuggled_in_metadata(self):
        self.original['cells'][0]['role']='blind'
        row=self.done['cells'][0]; row.update(role='blind',status='SEALED_BLIND',B=None)
        row.pop('native'); row.pop('current'); row['mean']=123
        with self.assertRaises(ValueError): self.check()

    def empty_fixture(self, blind=False):
        import base64,hashlib
        profile='apple-macos-27.0-1x-dark-standard-glass0.25'
        scene='cell-grey-004-s224__inactive' if blind else 'cell-grey-004-s128__inactive'
        for doc in (self.original,self.done):
            doc['cells'][0].update(profile=profile,scene=scene,statistic='T1-full-silhouette',
                                    role='blind' if blind else 'calibration')
        row=self.done['cells'][0]
        row.update(status='UNMEASURED_EMPTY_SUPPORT',native=None,current=None,fidelity=None,value=None,B=None)
        raw=bytes(512*384//8)
        support=dict(status='UNMEASURED_EMPTY_SUPPORT',pixels=0,maskShape=[384,512],
                     maskPackedBitsSha256=hashlib.sha256(raw).hexdigest(),
                     maskPackedBitsBase64=base64.b64encode(raw).decode())
        runs=[dict(run=i,readings={'supports':{'full-silhouette':copy.deepcopy(support)},
                    'statistics':{'T1-full-silhouette':{'status':'UNMEASURED_EMPTY_SUPPORT','value':None}}}) for i in (1,2,3)]
        native={'schema':'w50-native-role-read-1','role':row['role'],'canvas':{'width':512,'height':384},
                'cells':[dict(profile=profile,scene=scene,role=row['role'],runs=runs)]}
        path=self.repo/'native-read.json'; path.write_text(json.dumps(native))
        witness={'schema':'w50-empty-native-support-witness-1','profile':profile,'scene':scene,
                 'nativeRead':{'path':path.name,'sha256':P.sha(path)}}
        w=self.repo/'empty-witness.json'; w.write_text(json.dumps(witness))
        row['emptySupportWitness']={'path':w.name,'sha256':P.sha(w)}
        return list(P.key(row))

    def test_empty_native_support_has_narrow_content_pinned_exception(self):
        key=self.empty_fixture()
        P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[key])
        with self.assertRaises(ValueError):
            P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[])
        self.done['cells'][0]['native']=0
        with self.assertRaises(ValueError):
            P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[key])

    def test_nonempty_or_wrong_identity_witness_never_licenses_null_reading(self):
        key=self.empty_fixture(); row=self.done['cells'][0]
        for mutation in ('pixels','identity','runs','bits'):
            self.empty_fixture(); path=self.repo/'native-read.json'; native=json.loads(path.read_text())
            if mutation=='pixels': native['cells'][0]['runs'][0]['readings']['supports']['full-silhouette']['pixels']=1
            if mutation=='identity': native['cells'][0]['scene']='another'
            if mutation=='runs': native['cells'][0]['runs'].pop()
            if mutation=='bits':
                import base64,hashlib
                raw=b'\x80'+bytes(512*384//8-1)
                support=native['cells'][0]['runs'][0]['readings']['supports']['full-silhouette']
                support.update(maskPackedBitsBase64=base64.b64encode(raw).decode(),maskPackedBitsSha256=hashlib.sha256(raw).hexdigest())
            path.write_text(json.dumps(native)); witness_path=self.repo/'empty-witness.json'
            witness=json.loads(witness_path.read_text()); witness['nativeRead']['sha256']=P.sha(path)
            witness_path.write_text(json.dumps(witness)); row['emptySupportWitness']['sha256']=P.sha(witness_path)
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[key])

    def test_empty_witness_can_pin_gzipped_native_json_without_changing_values(self):
        import gzip
        key=self.empty_fixture(); row=self.done['cells'][0]
        native=self.repo/'native-read.json'; packed=self.repo/'native-read.json.gz'
        packed.write_bytes(gzip.compress(native.read_bytes(),mtime=0))
        witness_path=self.repo/'empty-witness.json'; witness=json.loads(witness_path.read_text())
        witness['nativeRead']={'path':packed.name,'sha256':P.sha(packed)}
        witness_path.write_text(json.dumps(witness)); row['emptySupportWitness']['sha256']=P.sha(witness_path)
        native.unlink()
        P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[key])
        packed.write_bytes(packed.read_bytes()+b'changed')
        with self.assertRaises(ValueError):
            P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[key])

    def test_eligible_nonempty_rows_still_require_computed_values(self):
        key=self.empty_fixture(); row=self.done['cells'][0]
        row.update(status='REPORTED',native=.1,current=.2,fidelity=.1,value=.1)
        row.pop('emptySupportWitness')
        P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[key])
        row['current']=None
        with self.assertRaises(ValueError):
            P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[key])

    def test_blind_eligibility_does_not_allow_prefit_witness_or_statistics(self):
        key=self.empty_fixture(blind=True)
        with self.assertRaises(ValueError):
            P.validate_completion(self.original,self.done,[key],self.repo,empty_support_keys=[key])

    def test_empty_eligibility_is_exact_identity_list_not_general_span_waiver(self):
        exposed=self.empty_fixture(); first=copy.deepcopy(self.original['cells'][0])
        blind=self.empty_fixture(blind=True); second=copy.deepcopy(self.original['cells'][0])
        refs={'cells':[first,second]}
        manifest={'cells':[dict(profile=c['profile'],scene=c['scene'],family='span',pose='receded',
                               level=4,background='grey-004',role=c['role'],span=128 if i==0 else 224)
                           for i,c in enumerate(refs['cells'])]}
        P.validate_empty_eligibility(refs,manifest,[exposed,blind],[exposed,blind])
        for wrong in ([exposed],[exposed,blind,exposed],[]):
            with self.assertRaises(ValueError): P.validate_empty_eligibility(refs,manifest,[exposed,blind],wrong)
        manifest['cells'][0]['level']=64; manifest['cells'][0]['background']='grey-064'
        with self.assertRaises(ValueError): P.validate_empty_eligibility(refs,manifest,[exposed,blind],[exposed,blind])

    def test_exemptions_exactly_match_neutral_span_extra_rows(self):
        manifest = {'cells': [dict(profile='p', scene='s', family='span', span=128,
                                  background='grey-004', level=4)]}
        refs = copy.deepcopy(self.original)
        for statistic in ('deep8-channel-median', 'deep8-far24-luma-mean', 'T1-full-silhouette'):
            row = copy.deepcopy(self.cell); row['statistic'] = statistic; refs['cells'].append(row)
        expected = [['p', 'webgpu', 's', 'deep8-far24-luma-mean'],
                    ['p', 'webgpu', 's', 'T1-full-silhouette']]
        P.validate_exemptions(refs, manifest, expected)
        for wrong in (expected[:-1], expected + [list(P.key(self.cell))]):
            with self.assertRaises(ValueError): P.validate_exemptions(refs, manifest, wrong)


if __name__ == '__main__':
    unittest.main()
