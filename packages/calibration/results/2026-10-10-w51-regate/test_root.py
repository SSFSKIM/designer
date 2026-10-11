"""Population authority must never omit a companion or admit a withheld physical cell."""
import copy
import importlib.util
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent

def module():
    spec = importlib.util.spec_from_file_location('w51_root_test', HERE/'root.py')
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value

class PopulationTests(unittest.TestCase):
    def setUp(self):
        self.root = module()
        self.rows = [dict(profile='p', renderer='webgpu', scene='a', statistic=s, role='gate')
                     for s in ('T1-full-silhouette', 'low-end-path-level')]
        self.rows += [dict(profile='p', renderer=t, scene='b', statistic='T1-low', role=r)
                      for t, r in [('webgpu', 'historical-prediction-check'), ('css', 'gate')]]
        self.deps = {'gateKeys': [['p','webgpu','a',s] for s in ('T1-full-silhouette','low-end-path-level')],
                     'exposureKeys': [['p',t,'b','T1-low'] for t in ('webgpu','css')],
                     'pendingOwnerKeys': [], 'ownerUnionKeys': [],
                     'groups': [{'profile':'p','scene':'b','withheldKeys':[['p','webgpu','b','T1-low']]}]}
        self.population = {'physicalCells': [['p','webgpu','a']], 'physicalCount': 1,
                           'statisticKeys': self.deps['gateKeys'], 'statisticCount': 2}

    def test_whole_original_key_group_and_global_pending_population_survive(self):
        before = copy.deepcopy(self.deps)
        got = self.root.population_dependencies(self.rows, self.deps, self.population)
        self.assertEqual(got, before)
        self.assertEqual(self.deps, before)

    def test_missing_companion_refuses(self):
        self.population['statisticKeys'] = self.population['statisticKeys'][:1]
        self.population['statisticCount'] = 1
        with self.assertRaisesRegex(ValueError, 'companion'):
            self.root.population_dependencies(self.rows, self.deps, self.population)

    def test_withheld_opposite_tier_refuses(self):
        self.population = {'physicalCells': [['p','css','b']], 'physicalCount':1,
                           'statisticKeys': [['p','css','b','T1-low']], 'statisticCount':1}
        with self.assertRaisesRegex(ValueError, 'withheld'):
            self.root.population_dependencies(self.rows, self.deps, self.population)

    def test_duplicate_capture_refuses(self):
        self.population['physicalCells'] *= 2
        self.population['physicalCount'] = 2
        with self.assertRaises(ValueError):
            self.root.population_dependencies(self.rows, self.deps, self.population)

class NamedPopulationBindingTests(unittest.TestCase):
    def test_registered_gate_cannot_be_relabelled_as_the_real_rehearsal(self):
        root = module()
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory).resolve()
            def put(name, value):
                path = home/name; path.write_bytes(root.encoded(value))
                return {'path':name, 'sha256':root.sha(path)}
            fit = put('fit840.json', {'statisticKeys':[['p','webgpu','fit','T1']]})
            gate = put('gate1341.json', {'statisticKeys':[['p','webgpu','fit','T1'],
                                                        ['p','webgpu','unread','T1']]})
            synthetic = put('synthetic.json', {'statisticKeys':[['toy','webgpu','toy','T1']]})
            populations = {'real-rehearsal':{'dataset':'real', 'manifest':fit},
                           'gate':{'dataset':'real', 'manifest':gate},
                           'synthetic-rehearsal':{'dataset':'synthetic', 'manifest':synthetic}}
            charter = put('charter-seal-dl5.json', {'populations':populations})
            fit_batch = put('fit-batch.json', {'members':fit})
            gate_batch = put('gate-batch.json', {'members':gate})
            path = home/'draft.json'
            doc = {'schema':'w51-execution-root-1', 'repo':str(home), 'rootPath':str(path),
                   'inputs':[fit,gate,synthetic,charter,fit_batch,gate_batch],
                   'closure':{'sources':{}}, 'charter':charter,
                   'populations':copy.deepcopy(populations),
                   'batches':{'real-rehearsal':fit_batch, 'gate':gate_batch}}
            # Earlier charter-commit verification is independent of this named-population
            # boundary. Stop at the next source admission rather than fabricate a live root.
            class NextAdmission(Exception): pass
            with patch.object(root, 'REPO', home), patch.object(root, 'HERE', home), \
                    patch.object(root, 'verify_charter'), \
                    patch.object(root, 'source', side_effect=NextAdmission):
                with self.assertRaises(NextAdmission):
                    root.validate_body(path, doc, 'real-rehearsal', home.parent/'unused-output')
                doc['populations']['real-rehearsal'] = copy.deepcopy(populations['gate'])
                doc['batches']['real-rehearsal'] = gate_batch
                with self.assertRaisesRegex(ValueError, 'population.*charter'):
                    root.validate_body(path, doc, 'real-rehearsal', home.parent/'unused-output')

if __name__ == '__main__': unittest.main()
