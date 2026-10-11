"""Regression checks for data-only W52 membership and prospective comparator declarations."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
W51 = REPO / 'packages/calibration/results/2026-10-10-w51-regate'
KEY = ('profile', 'renderer', 'scene', 'statistic')


class PopulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = HERE / 'build.py'
        if not path.exists():
            raise AssertionError('W52 data builder has not been implemented')
        spec = importlib.util.spec_from_file_location('w52_populations', path)
        cls.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.builder)
        cls.sources = cls.builder.load_sources()
        cls.outputs = cls.builder.derive(cls.sources)

    def test_membership_is_exact_not_merely_same_counts(self):
        for phase, name, count, keys in (
            ('rehearsal', 'fit-population.json', 840, 1856),
            ('gate', 'gate-population.json', 1341, 2553),
            ('exposure', 'exposure-population.json', 322, 974),
        ):
            source = json.loads((W51 / f'declaration-v2/{phase}-population.json').read_text())
            actual = self.outputs[name]
            self.assertEqual(actual['physicalCells'], source['physicalCells'])
            self.assertEqual(actual['statisticKeys'], source['statisticKeys'])
            self.assertEqual(actual['originalMetadata'], source['originalMetadata'])
            self.assertEqual((actual['physicalCount'], actual['statisticCount']), (count, keys))

    def test_referees_add_only_named_nonblind_extra_twelve(self):
        refs = self.outputs['impulse-referees.json']
        expected = sorted([
            [f'apple-macos-27.0-{scale}x-dark-standard-glass{position}', 'webgpu',
             f'impulse__{shape}__rest']
            for scale in (1, 2) for position in ('0.25', '0.5')
            for shape in ('capsule-button', 'rrect-sm', 'rrect-ml', 'rrect-lg')
        ])
        self.assertEqual(refs['physicalCells'], expected)
        fit = self.outputs['fit-population.json']
        union = self.outputs['fit-time-union.json']
        self.assertEqual(list(map(tuple, union['physicalCells'])), sorted(set(map(tuple, fit['physicalCells'])) |
                                                       set(map(tuple, expected))))
        self.assertEqual(list(map(tuple, union['statisticKeys'])), sorted(set(map(tuple, fit['statisticKeys'])) |
                                                       set(map(tuple, refs['statisticKeys']))))
        self.assertEqual((len(refs['overlapPhysicalCells']), len(refs['extraPhysicalCells']),
                          len(refs['extraStatisticKeys'])), (4, 12, 22))
        self.assertEqual((union['physicalCount'], union['statisticCount']), (852, 1878))
        self.assertEqual(refs['gateBlindness'], 'NON_BLIND_READ_AT_FIT')
        self.assertEqual(self.outputs['gate-population.json']['nonBlindRefereePhysicalCells'], expected)
        self.assertEqual(self.outputs['rehearsal.json']['population'], 'fit-population.json')
        self.assertEqual(self.outputs['rehearsal.json']['statisticCount'], 1856)

    def test_gate_and_exposure_remain_disjoint_and_complete(self):
        gate = self.outputs['gate-population.json']; exposure = self.outputs['exposure-population.json']
        self.assertFalse(set(map(tuple, gate['physicalCells'])) & set(map(tuple, exposure['physicalCells'])))
        self.assertEqual(list(map(tuple, self.outputs['full-union.json']['statisticKeys'])),
                         sorted(map(tuple, gate['statisticKeys'] + exposure['statisticKeys'])))
        self.assertEqual(self.outputs['full-union.json']['statisticCount'], 3527)

    def test_each_history_retains_originals_and_uses_only_its_own_current_value(self):
        table = self.outputs['own-history.json']
        self.assertEqual(table['gateInventory'], {'comparisons': 16, 'occupied': 14})
        self.assertEqual(table['exposureStaticInventory'], {'comparisons': 4, 'occupied': 1})
        self.assertEqual(len(table['comparisons']), 20)
        originals = {tuple(r[k] for k in KEY): r for r in self.sources['inventory']['cells']}
        for record in table['comparisons']:
            source = originals[tuple(record['key'])]
            history = source['historical'][record['historyIndex']]
            self.assertEqual(record['originalReference'], source)
            self.assertEqual(record['historicalWitness']['original'], history)
            self.assertEqual(record['originalOperands']['native'], source['native'])
            self.assertEqual(record['originalOperands']['historicalValue'], history['value'])
            raw = abs(source['current']-source['native']) - abs(history['value']-source['native'])
            self.assertEqual(record['originalOperands']['currentGrowth'], raw)
            self.assertEqual(record['originalOperands']['cap'], max(source['B'], raw))
            prospective = record['prospective']
            if record['occupied']:
                self.assertEqual(prospective['referenceValue'], source['current'])
                self.assertEqual(prospective['referenceDocumentPair'], source['currentDocumentPair'])
                self.assertEqual(prospective['bound']['base'], source['B'])
                self.assertEqual(prospective['action'], 'CURRENT_GENERATION_WITH_B_HEADROOM')
            else:
                self.assertEqual(prospective['referenceValue'], history['value'])
                self.assertEqual(prospective['bound']['base'], max(source['B'], raw))
                self.assertEqual(prospective['action'], 'RETAIN_HISTORY_AND_CAP')

    def test_gate_histories_preserve_exact_exposed_measurement_witnesses(self):
        records = self.outputs['own-history.json']['comparisons']
        for record in records:
            if record['membership'] != 'gate':
                continue
            row = self.sources['historyRows'][tuple(record['key'])]['row']
            self.assertEqual(record['historicalWitness'],
                             row['readings'][row['statistic']]['evidence']['historical'][record['historyIndex']])
            self.assertEqual(record['originalReference'], row['originalReference'])
        unoccupied = [r['key'] for r in records if r['membership'] == 'gate' and not r['occupied']]
        self.assertEqual([r[2] for r in unoccupied], ['checkerboard-64__rrect-lg__inactive'] * 2)

    def test_costs_keep_every_original_value_without_automatic_exception_permission(self):
        output = self.outputs['texture-costs.json']
        declared = self.sources['policy']['exceptions']
        expected = [e for e in declared if e['key'][3] == 'T1-full-silhouette']
        self.assertEqual([r['key'] for r in output['costs']], [e['key'] for e in expected])
        self.assertEqual(len(expected), 18)
        for record, original in zip(output['costs'], expected):
            self.assertEqual(record['w51DeclaredCost'], original)
            self.assertEqual(record['prospective']['referenceValue'], original['readings']['T1-full-silhouette']['current'])
            self.assertEqual(record['prospective']['bound']['base'], original['readings']['T1-full-silhouette']['B'])
            self.assertEqual(record['prospective']['bound']['multiplier'], 1)
        self.assertEqual(output['genericT1GrowthMultiplier'], 2)
        self.assertEqual(output['w52Exceptions'], [])
        self.assertEqual(output['numericalEpsilon']['function'], 'less_equal')
        self.assertEqual(output['numericalEpsilon']['source'], self.sources['pins']['precision'])

    def test_memberships_restore_w51_cost_keys_to_strata(self):
        output = self.outputs['aggregate-memberships.json']
        members = {tuple(m['key']) for a in output['aggregates'] for m in a['members']}
        for e in self.sources['policy']['exceptions']:
            self.assertIn(tuple(e['key']), members)
        self.assertEqual(output['excludedExceptionKeys'], [])
        for a in output['aggregates']:
            self.assertFalse(any(k in m for m in a['members'] for k in ('native', 'current', 'candidate')))
        for original in self.sources['policy']['aggregates']:
            actual = next(a for a in output['aggregates'] if a['id'] == original['id'])
            expected_members = {(tuple(m['key']), m['statistic'], m['component']) for m in original['members']}
            gate_members = {(tuple(m['key']), m['statistic'], m['component']) for m in actual['members']
                            if m['membership'] == 'gate'}
            self.assertTrue(expected_members <= gate_members)
            extra = {k for k, _, _ in gate_members - expected_members}
            self.assertTrue(extra <= {tuple(e['key']) for e in self.sources['policy']['exceptions']})

    def test_full_union_adds_only_four_exposure_text_strata_and_covers_every_key(self):
        data = self.outputs['aggregate-memberships.json']
        prior_ids = {a['id'] for a in self.sources['policy']['aggregates']}
        extra = [a for a in data['aggregates'] if a['id'] not in prior_ids]
        self.assertEqual({a['id'] for a in extra}, {
            f't1/pose=inactive/position={position}/renderer=webgpu/scale={scale}/stratum=T/median-log-ratio'
            for position in (0.25, 0.5) for scale in (1, 2)
        })
        self.assertTrue(all(m['membership'] == 'exposure' for a in extra for m in a['members']))
        covered = {tuple(m['key']) for a in data['aggregates'] for m in a['members']}
        covered.update(map(tuple, data['ownerContractKeys']))
        covered.update(tuple(e['key']) for e in data['exclusions'])
        self.assertEqual(covered, set(map(tuple, self.outputs['full-union.json']['statisticKeys'])))

    def test_missing_or_duplicate_source_member_is_rejected(self):
        for mutation in ('remove', 'duplicate'):
            bad = copy.deepcopy(self.sources)
            keys = bad['gate']['statisticKeys']
            if mutation == 'remove':
                keys.pop()
            else:
                keys.append(keys[0])
            with self.assertRaises(ValueError):
                self.builder.derive(bad)

    def test_source_bytes_cannot_be_mutated_then_reaccepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); (root / 'source.json').write_text('{}\n')
            pin = {'path': 'source.json', 'sha256': self.builder.sha(root / 'source.json')}
            self.assertEqual(self.builder.read_source(pin, root), {})
            (root / 'source.json').write_text('{"altered":true}\n')
            with self.assertRaisesRegex(ValueError, 'source hash'):
                self.builder.read_source(pin, root)

    def test_checker_rejects_membership_and_operand_and_authority_mutations(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp).resolve()
            self.builder.write_outputs(self.outputs, directory)
            self.builder.check_outputs(directory, self.sources)
            for name, mutate in (
                ('fit-time-union.json', lambda d: d['statisticKeys'].pop()),
                ('own-history.json', lambda d: d['comparisons'][0]['prospective'].update(referenceValue=0)),
                ('texture-costs.json', lambda d: d.update(w52Exceptions=self.sources['policy']['exceptions'])),
                ('gate-population.json', lambda d: d.update(captureAuthority=True)),
            ):
                changed = copy.deepcopy(self.outputs[name]); mutate(changed)
                (directory / name).write_bytes(self.builder.encoded(changed))
                with self.assertRaisesRegex(ValueError, 'projection'):
                    self.builder.check_outputs(directory, self.sources)
                (directory / name).write_bytes(self.builder.encoded(self.outputs[name]))

    def test_every_artifact_is_unsealed_without_capture_authority(self):
        for document in self.outputs.values():
            self.assertEqual(document['status'], 'UNSEALED_DATA_SCAFFOLD_ONLY')
            self.assertIs(document['captureAuthority'], False)


if __name__ == '__main__':
    unittest.main()
