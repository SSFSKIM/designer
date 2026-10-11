"""DL5's primary caps change; frozen readings and independent history never do."""
import copy
import hashlib
import json
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).resolve().parent
OLD = HERE.parent/'2026-10-08-w50-g1-fit/judge'
F = runpy.run_path(str(OLD/'test_rules.py'))
R = runpy.run_path(str(HERE/'judge_rules.py'))


def digest(value):
    return hashlib.sha256((json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()).hexdigest()


def policy(exceptions=(), aggregates=(), origin='synthetic'):
    return dict(schema='w51-dl5-policy-1', dataOrigin=origin,
        completePopulation={'path': 'population.json', 'sha256': '1'*64},
        primaryT1GrowthMultiplier=2, exceptions=list(exceptions), aggregates=list(aggregates),
        completeKeys=[list(k) for k in sorted({tuple(m['key']) for g in aggregates for m in g['members']}
                                             | {tuple(e['key']) for e in exceptions})], sources=[])


def route(row, p=None):
    p = policy() if p is None else p
    return R['route_row'](row, inventory_sha256=F['INVENTORY'],
                          landing_policy=p, policy_sha256=digest(p))


class DL5RulesTests(unittest.TestCase):
    def test_primary_growth_is_two_stored_b_without_rewriting_reference_or_native_bar(self):
        for tier in ('webgpu', 'css'):
            for growth, status in ((1.5, 'WITHIN'), (2.1, 'EXCEEDS')):
                row = F['row']('T1-full-silhouette', family='structured', renderer=tier,
                    scene='cell-impulse-sparse-s096__rest', native=.25, current=.375,
                    candidate=.375+growth*.03125)
                before = copy.deepcopy(row)
                result = route(row)
                self.assertEqual(result['status'], status)
                self.assertEqual(result['checks'][0]['comparison']['components'][0]['bound'], .0625)
                self.assertEqual(result['sourceReadings'], before['readings'])
                self.assertEqual(result['reference'], before['reference'])
                self.assertEqual(row, before)
                if growth == 1.5:
                    self.assertEqual(R['route_row'](row, inventory_sha256=F['INVENTORY'])['status'], 'EXCEEDS')

    def test_exact_real_declared_costs_pass_and_each_worse_component_fails(self):
        costs = json.loads((HERE/'declaration-v3/declared-costs.json').read_text())['exceptions']
        p = policy(costs, origin='measured-native')
        for exception in costs:
            with self.subTest(key=exception['key']):
                pin = exception['measurement']
                raw = Path(pin['path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), pin['sha256'])
                evidence = json.loads(raw)
                row = evidence['row']
                kwargs = dict(inventory_sha256=evidence['referenceInventory']['sha256'],
                              landing_policy=p, policy_sha256=digest(p))
                before = copy.deepcopy(row)
                routed = R['route_row'](row, **kwargs)
                self.assertEqual(routed['status'], 'WITHIN')
                self.assertEqual(routed['sourceReadings'], before['readings'])
                self.assertEqual(routed['reference'], before['reference'])
                self.assertEqual(routed['sourceHistorical'], before.get('historical', []))
                self.assertEqual(row, before)
                failed = exception['failedComparisons'][0]
                name = failed['statistic']
                value = row['readings'][name]
                if name.startswith('T1'):
                    direction = 1 if value['candidate'] >= value['native'] else -1
                    value['candidate'] += direction * 1e-10
                    production = value['evidence']['candidate'].get('productionStatistic')
                    if production: production['value'] = value['candidate']
                else:
                    direction = 1 if value['candidate'][2] >= value['native'][2] else -1
                    value['candidate'][2] += direction * 1e-10
                self.assertEqual(R['route_row'](row, **kwargs)['status'], 'EXCEEDS')

    def test_blue_exception_does_not_raise_red_or_green(self):
        costs = json.loads((HERE/'declaration-v3/declared-costs.json').read_text())['exceptions']
        p = policy(costs, origin='measured-native')
        exception = next(e for e in costs if e['failedComparisons'][0]['rule'] == 'absolute-level')
        evidence = json.loads(Path(exception['measurement']['path']).read_text())
        for component in (0, 1):
            row = copy.deepcopy(evidence['row'])
            value = row['readings'][exception['failedComparisons'][0]['statistic']]
            value['candidate'][component] = value['native'][component]+1.5
            out = R['route_row'](row, inventory_sha256=evidence['referenceInventory']['sha256'],
                                landing_policy=p, policy_sha256=digest(p))
            self.assertEqual(out['status'], 'EXCEEDS')
            self.assertEqual([c['bound'] for c in out['checks'][0]['comparison']['components']], [1, 1, 2])

    def test_historical_caps_are_not_multiplied_even_when_primary_passes(self):
        for repaired in (False, True):
            row = F['row']('T1-full-silhouette', source='canonical', family='texture',
                          native=.25, current=.375, candidate=.5)
            value = row['readings'][row['statistic']]
            value['originalBudgetB'] = .125
            row['originalReference']['B'] = row['reference']['B'] = .125
            history = dict(generation='own-history', value=.3125, enforced=True, maxGrowthInB=1,
                frozenCurrentGrowthInB=.5, repaired=repaired,
                documentPair={'active.dark':'1'*64, 'receded.dark':'2'*64})
            for container in (row, row['reference'], row['originalReference']):
                container['historical'] = [copy.deepcopy(history)]
            value['evidence']['historical'] = [dict(F['evidence']('historical', row['statistic'], history=True), original=history)]
            F['frozen_operands'](row)
            out = route(row)
            self.assertEqual(out['failures'], ['own-history[0]:T1-full-silhouette'])
            self.assertEqual(out['checks'][0]['comparison']['components'][0]['bound'], .25)
            self.assertEqual(out['checks'][1]['comparison']['components'][0]['bound'], .125)
            self.assertEqual(out['sourceHistorical'], [history])

    def test_missing_candidate_cannot_pass_relaxed_cap(self):
        row = F['row']('T1-full-silhouette', family='structured', scene='cell-impulse-sparse-s096__rest')
        row['readings'][row['statistic']].update(candidate=None, candidateMeasurementStatus='UNMEASURED')
        self.assertEqual(route(row)['status'], 'UNMEASURED')

    def test_declared_exception_cannot_waive_an_absent_routed_comparison(self):
        costs = json.loads((HERE/'declaration-v3/declared-costs.json').read_text())['exceptions']
        exception = next(e for e in costs if e['key'][1] == 'css')
        evidence = json.loads(Path(exception['measurement']['path']).read_text())
        row = evidence['row']
        # Misrouting this exact CSS key as canonical removes its primary T1 check. The
        # declaration cannot turn the resulting diagnostic-only route into an exception pass.
        row['sceneSource'] = 'canonical'
        p = policy(costs, origin='measured-native')
        with self.assertRaisesRegex(ValueError, 'does not match its routed comparison'):
            R['route_row'](row, inventory_sha256=evidence['referenceInventory']['sha256'],
                           landing_policy=p, policy_sha256=digest(p))

    def test_changed_or_unexpected_exception_fails_authenticated_policy_boundary(self):
        costs = json.loads((HERE/'declaration-v3/declared-costs.json').read_text())['exceptions']
        original = policy(costs, origin='measured-native')
        for mutation in ('cap', 'extra', 'removed'):
            p = copy.deepcopy(original)
            if mutation == 'cap': p['exceptions'][0]['failedComparisons'][0]['components'][0]['growth'] += 1e-10
            elif mutation == 'extra': p['exceptions'].append(copy.deepcopy(costs[0]))
            else: p['exceptions'].pop()
            with self.assertRaisesRegex(ValueError, 'policy.*hash|policy.*digest'):
                R['route_rows']([], inventory_sha256=F['INVENTORY'], landing_policy=p,
                                policy_sha256=digest(original))


if __name__ == '__main__': unittest.main()
