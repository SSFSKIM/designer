"""Synthetic recovery read-root tests; all paths/payloads are temporary fixtures."""
import importlib.util
from pathlib import Path
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('successor_reads', HERE/'reads.py')
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)


class ReadBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.old = self.base/'old'; self.old.mkdir()
        self.new = self.base/'new'; self.new.mkdir()
        self.data = self.old/'capture.json'; self.data.write_text('{"synthetic":true}')
        self.item = R.W.pin(self.data)
        self.union = {'members': [{'payload': self.item, 'artifacts': [self.item]}]}

    def boundary(self): return R.Boundary(self.old, self.new, self.union)

    def test_same_pin_reads_original_and_writes_stay_fresh(self):
        with self.boundary() as b:
            self.assertEqual(b.read(lambda: self.data.read_bytes()), b'{"synthetic":true}')
            (self.new/'measurement.json').write_text('new')
            with self.assertRaises(ValueError): b.read(lambda: (self.new/'measurement.json').read_bytes())

    def test_changed_pin_wrong_union_outside_and_symlink_refuse(self):
        for case in ('changed', 'wrong-union', 'outside', 'symlink', 'ancestor-symlink'):
            with self.subTest(case=case):
                self.setUp()
                if case == 'changed': self.data.write_text('changed')
                elif case == 'wrong-union': self.union['members'][0]['artifacts'] = []; self.union['members'][0].pop('payload')
                elif case == 'outside':
                    p = self.base/'outside'; p.write_text('outside')
                    self.union['members'][0]['artifacts'] = [R.W.pin(p)]
                elif case == 'symlink':
                    p = self.old/'link'; p.symlink_to(self.data)
                    self.union['members'][0]['artifacts'] = [{'path': str(p), 'sha256': self.item['sha256']}]
                else:
                    actual = self.old/'actual'; actual.mkdir(); nested = actual/'nested'; nested.write_text('nested')
                    alias = self.old/'alias'; alias.symlink_to(actual, target_is_directory=True)
                    self.union['members'][0]['artifacts'] = [{'path': str(alias/'nested'), 'sha256': R.W.sha(nested)}]
                with self.assertRaises(ValueError):
                    with self.boundary() as b: b.read(lambda: self.data.read_bytes())

    def test_pin_reader_routes_only_external_successor_captures(self):
        context = {'phase': 'gate'}
        def genuine(ctx): self.assertIs(ctx, context)
        dispatcher = types.SimpleNamespace(require_context=genuine)
        primitive = R.source(HERE.parent/'measurement/capture.py', 'analysis2_pin_primitive')
        with self.boundary() as b:
            reader = R.PinReader(primitive._pin_bytes, b, dispatcher, context)
            self.assertEqual(reader(self.item, self.new, external=True), self.data.read_bytes())
            with self.assertRaises(ValueError): reader({**self.item, 'sha256': 'f'*64}, self.new, external=True)
            outsider = self.new/'outside.json'; outsider.write_text('{}')
            with self.assertRaises(ValueError): reader(R.W.pin(outsider), self.new, external=True)
            # Noncapture repository/native reads retain the unmodified primitive behavior.
            self.assertEqual(reader({'path': outsider.name, 'sha256': R.W.sha(outsider)}, self.new), b'{}')
            context['phase'] = 'exposure'
            with self.assertRaises(ValueError): reader(self.item, self.new, external=True)

    def test_original_writes_denied_even_outside_pure_read_call(self):
        with self.boundary() as b:
            for action in (lambda: self.data.write_text('overwrite'),
                           lambda: self.data.unlink(),
                           lambda: self.data.rename(self.new/'moved'),
                           lambda: (self.old/'newdir').mkdir()):
                with self.assertRaises(ValueError): action()
            self.assertEqual(self.data.read_text(), '{"synthetic":true}')


class RealPureHelpers(unittest.TestCase):
    def test_original_three_validators_read_same_artifacts_under_fresh_context(self):
        fixtures = R.source(HERE.parent/'measurement/test_repeat.py', 'analysis2_repeat_fixtures')
        fixture = fixtures.PairFixture(self, identical=True)
        fresh = fixture.directory/'successor'; fresh.mkdir()
        context = {**fixture.context, 'output': str(fresh), 'phase': 'gate'}
        for key in ('executionRoot', 'contract', 'batchPath'):
            target = fresh/(key+'.json'); target.write_text('{"successor":true}')
            context[key] = str(target)
        batch = {'phase': 'gate', 'cohort': [fixture.candidate], 'runs': [fixture.run]}
        context['batch'] = batch
        def genuine(ctx): self.assertIs(ctx, context)
        def resolve(ctx, record):
            genuine(ctx); self.assertEqual(record, fixture.record); return fixture.run
        dispatcher = types.SimpleNamespace(require_context=genuine, resolve_capture_run=resolve)
        artifacts = [R.W.pin(p) for p in sorted(fixture.output.rglob('*')) if p.is_file()]
        union = {'members': [{'artifacts': artifacts}]}
        original = R.source(HERE.parent/'live-execution/admission.py', 'analysis2_actual_admission')
        with R.Boundary(fixture.output, fresh, union) as boundary:
            capture_authority = {k: R.W.pin(fixture.context[k]) for k in
                                 ('executionRoot', 'contract', 'batchPath')}
            repeat = R.Repeat(fixture.P, boundary, dispatcher, context, capture_authority)
            retained = repeat.read_pair(context, fixture.run, fixture.record, fixture.record['repeatPair'])
            proof = repeat.retained_proof(str(fresh), fixture.run, fixture.record, retained)
            self.assertEqual(proof, R.W.parse(Path(fixture.record['repeatAdmission']['path']).read_bytes()))
            root = R.W.parse(fixture.root.read_bytes())
            config = R.W.parse((fixture.repo/root['repeatAdmission']['config']['path']).read_bytes())
            rows = R.W.parse((fixture.repo/config['references']['path']).read_bytes())['cells']
            binding = repeat.receipt_binding(context, fixture.run, fixture.record, config, rows)
            repeat.verify_pair_semantics(binding, fixture.run, fixture.record, retained, proof)
            for key in ('executionRoot', 'contract', 'batchPath'):
                self.assertNotEqual(context[key], fixture.context[key])
            admitted = R.Admission(original, boundary, dispatcher, context).validate_captures(batch,
                {'status': 'CAPTURED', 'candidateSha256s': [fixture.candidate['sha256']],
                 'captures': [fixture.record]}, fresh)
            self.assertTrue(admitted['members'])
            self.assertEqual(context['output'], str(fresh))
            self.assertEqual({p.name for p in fresh.iterdir()},
                             {'executionRoot.json', 'contract.json', 'batchPath.json'})
            for name in ('capture', 'fit', 'exposure', 'write', 'admit_pair'):
                self.assertFalse(hasattr(repeat, name))


if __name__ == '__main__': unittest.main()
