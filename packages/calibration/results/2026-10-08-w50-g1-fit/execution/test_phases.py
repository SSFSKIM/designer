"""DL5d physical closure tests; the real fixture contains identities only, no readings."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('phase_dispatch',HERE/'dispatch.py')
D=importlib.util.module_from_spec(spec); spec.loader.exec_module(D)


def row(renderer,scene,statistic,role):
    return dict(profile='p',renderer=renderer,scene=scene,statistic=statistic,role=role,B='original-budget')


class PhysicalClosure(unittest.TestCase):
    def test_opposite_tier_owner_moves_once_without_losing_original_keys(self):
        cells=[row('webgpu','mixed','T1-full-silhouette','historical-prediction-check'),
               row('webgpu','mixed','owner-contracts','gate'),
               row('css','mixed','owner-contracts','gate'),
               row('webgpu','clear','T1-full-silhouette','gate'),
               row('css','clear','owner-contracts','gate')]
        original=copy.deepcopy(cells)
        closure=D.derive_phase_dependencies(cells)
        self.assertEqual(cells,original)
        self.assertEqual(closure['gateKeys'],[['p','webgpu','clear','T1-full-silhouette'],
                                              ['p','css','clear','owner-contracts']])
        self.assertEqual(closure['exposureKeys'],[['p','webgpu','mixed','T1-full-silhouette'],
                                                  ['p','webgpu','mixed','owner-contracts'],
                                                  ['p','css','mixed','owner-contracts']])
        self.assertEqual(closure['pendingOwnerKeys'],[['p','webgpu','mixed','owner-contracts'],
                                                     ['p','css','mixed','owner-contracts']])
        self.assertEqual(closure['ownerUnionKeys'],[['p','webgpu','mixed','owner-contracts'],
                                                   ['p','css','mixed','owner-contracts'],
                                                   ['p','css','clear','owner-contracts']])
        self.assertEqual(closure['groups'][0]['withheldKeys'],
                         [['p','webgpu','mixed','T1-full-silhouette']])

    def test_real_identity_census_keeps_all_42_pending_owners_across_24_groups(self):
        census=json.loads((HERE.parent/'identification/phase-dependency-census.json').read_text())
        cells=[r for group in census['mixedProfileSceneGroups'] for r in group['rows']]
        closure=D.derive_phase_dependencies(cells)
        self.assertEqual(len(closure['groups']),24)
        self.assertEqual(len(closure['pendingOwnerKeys']),42)
        self.assertEqual(sum(k[1]=='webgpu' for k in closure['pendingOwnerKeys']),24)
        self.assertEqual(sum(k[1]=='css' for k in closure['pendingOwnerKeys']),18)
        self.assertEqual(closure['gateKeys'],[])
        self.assertEqual(closure['exposureKeys'],[[r[k] for k in D.KEY] for r in cells])
        self.assertEqual(len({tuple(k) for k in closure['exposureKeys']}),len(cells))

    def test_owner_budget_keys_are_exact_original_owners_not_reported_exemptions(self):
        cells=[row('webgpu','a','owner-contracts','gate'),
               row('css','a','owner-contracts','historical-prediction-check'),
               row('webgpu','a','T1-full-silhouette','gate')]
        self.assertEqual(D.owner_budget_keys(cells),[['p','webgpu','a','owner-contracts'],
                                                     ['p','css','a','owner-contracts']])
        self.assertEqual(D.owner_budget_keys(cells),D.derive_phase_dependencies(cells)['ownerUnionKeys'])

    def test_table_cannot_be_caller_selected_or_drop_opposite_tier(self):
        cells=[row('webgpu','mixed','T1-full-silhouette','blind'),
               row('css','mixed','owner-contracts','gate')]
        correct=D.derive_phase_dependencies(cells)
        D.verify_phase_dependencies({'phaseDependencies':correct},cells)
        for field in ('groups','gateKeys','exposureKeys','pendingOwnerKeys','ownerUnionKeys'):
            changed=copy.deepcopy(correct)
            changed[field]=[] if correct[field] else [['invented']]
            with self.subTest(field=field),self.assertRaises(ValueError):
                D.verify_phase_dependencies({'phaseDependencies':changed},cells)
        with self.assertRaises(ValueError): D.verify_phase_dependencies({},cells)


if __name__=='__main__': unittest.main()
