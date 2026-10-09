"""The real unchanged judge behind the recovery witness, using its synthetic miniature bed."""
import copy
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent


def source(path, name):
    m = types.ModuleType(name); m.__file__ = str(path); sys.modules[name] = m
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), m.__dict__)
    return m


W = source(HERE/'witness.py', 'analysis2_pipeline_witness')
F = source(HERE.parent/'judge/test_live.py', 'analysis2_pipeline_fixtures')


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.world = F.World(self); self.world.install(self)
        self.before = self.world.context('gate')
        self.after = self.world.context('gate')
        self.old = Path(self.before['output'])/'measurement'
        self.new = Path(self.after['output'])/'measurement'
        old = self.world.measured(self.before)
        self.write_keys(old, self.old)
        (self.old/'phase.json').unlink()
        self.manifest = {'count': len(old['rows']), 'files': [
            {**W.pin(p), 'bytes': p.stat().st_size} for p in sorted(self.old.iterdir())]}
        self.expected = [[row[k] for k in W.KEY] for row in old['rows']]
        self.old_authority = self.bindings(old)
        self.judged = 0
        self.marker = Path(self.after['executionClaim']['path']); self.marker.unlink()

    def bindings(self, body): return {k: copy.deepcopy(body[k]) for k in W.AUTHORITY}

    def write_keys(self, body, folder):
        for row in body['rows']:
            key = [row[k] for k in W.KEY]
            W.write_once(folder/W.filename(key), {
                'schema': 'w50-keyed-measurement-evidence-1', 'phase': 'gate',
                **self.bindings(body), 'cohort': body['cohort'], 'config': body['config'], 'row': row})

    def pipeline(self, mutate=False):
        state = {}
        def measure():
            self.after['executionClaim'] = W.pin(self.marker)
            body = self.world.measured(self.after)
            self.write_keys(body, self.new)
            state['binding'] = self.bindings(body)
            if mutate:
                p = self.new/W.filename(self.expected[0]); value = W.parse(p.read_bytes())
                value['row']['unexpectedNonAuthorityField'] = True
                p.write_bytes(W.encode(value))
            return body
        def witness():
            return W.compare(self.manifest, self.old, self.new, self.expected,
                             self.old_authority, state['binding'])
        def judge(measured):
            self.judged += 1
            report = self.world.run(self.after, measured)
            self.world.validate(self.after, report)
            return report
        return W.once(self.marker, {'analysis': 2}, measure, witness, judge)

    def test_exact_witness_then_real_judge_and_unchanged_report_validator(self):
        result = self.pipeline()
        self.assertEqual(result['status'], 'PASS_EXPOSED_OWNER_PENDING')
        self.assertEqual(result['witness']['count'], self.manifest['count'])
        self.assertEqual(self.judged, 1)
        with self.assertRaises(FileExistsError): self.pipeline()
        self.assertEqual(self.judged, 1)

    def test_single_non_authority_field_prevents_actual_judge(self):
        self.assertEqual(self.pipeline(mutate=True)['status'], 'NEITHER')
        self.assertEqual(self.judged, 0)


if __name__ == '__main__': unittest.main()
