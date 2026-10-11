"""Whole-population DL5 aggregates use declared scalars, never a convenient subset."""
import copy
import math
import json
import tempfile
import types
from pathlib import Path
import runpy
import unittest

H = runpy.run_path(str(Path(__file__).resolve().with_name('test_dl5_rules.py')))
R, F, policy, digest = (H[n] for n in ('R', 'F', 'policy', 'digest'))


def member(row, statistic=None, component=None):
    statistic = statistic or row['statistic']
    value = row['readings'][statistic]
    index = 'RGB'.index(component) if component else None
    scalar = lambda side: value[side][index] if index is not None else value[side]
    result = dict(key=list(F['key'](row)), statistic=statistic, component=component,
                  native=scalar('native'), current=scalar('current'),
                  provenance={'source': {'path':'source.json', 'sha256':'2'*64}, 'selector': statistic})
    if statistic.startswith('T1'): result['epsilon'] = .03125
    return result


def group(members, *, kind='t1', reduction='median-log-ratio', name='C', gate=True):
    return dict(id=name+'-'+reduction, kind=kind, dimensions={'stratum':name, 'pose':'rest',
        'scale':1, 'position':.25, 'renderer':'webgpu'}, gate=gate, reduction=reduction,
        timing='population-full', members=members, membershipSha256=digest(members))


def grade(rows, groups, *, complete=None, selected=None, origin='synthetic'):
    keys = [list(F['key'](r)) for r in rows]
    p = policy(aggregates=groups, origin=origin)
    p['completeKeys'] = keys if complete is None else complete
    return R['route_aggregates'](rows, landing_policy=p, policy_sha256=digest(p),
        complete_keys=keys if complete is None else complete,
        full_union={tuple(k) for k in (keys if selected is None else selected)} ==
                   {tuple(k) for k in (keys if complete is None else complete)})


class DL5AggregateTests(unittest.TestCase):
    def texture(self, name='T1-full-silhouette', candidate=.375):
        return F['row'](name, source='canonical', family='texture', native=.25,
                        current=.375, candidate=candidate)

    def test_single_member_aggregate_uses_log_ratio_without_tau_or_minimum_three(self):
        row = self.texture(candidate=.4)
        out = grade([row], [group([member(row)])])
        self.assertEqual(out['status'], 'EXCEEDS')
        score = out['aggregates'][0]
        self.assertAlmostEqual(score['candidate'], abs(math.log((.4+.03125)/(.25+.03125))))
        self.assertAlmostEqual(score['current'], abs(math.log((.375+.03125)/(.25+.03125))))
        row['readings'][row['statistic']]['candidate'] = .375
        self.assertEqual(grade([row], [group([member(row)])])['status'], 'WITHIN')

    def test_t_reads_fine_companion_not_the_low_regression_statistic(self):
        row = self.texture('T1-low', candidate=.25)
        row['readings']['T1-fine'] = F['reading']('T1-fine', .0625, .09375, .125,
                                                     code=.001, bar=.001, bound=.002)
        out = grade([row], [group([member(row, 'T1-fine')], name='T')])
        self.assertEqual(out['status'], 'EXCEEDS')
        self.assertAlmostEqual(out['aggregates'][0]['candidate'], math.log(5/3))

    def test_level_max_and_mean_have_independent_vetoes_and_exact_components(self):
        # Lower max can hide a worse mean; lower mean can hide a worse max.
        for current, candidate, statuses in (([24,20,20], [22,22,22], ['WITHIN','EXCEEDS']),
                                              ([22,22,22], [23,20,20], ['EXCEEDS','WITHIN'])):
            row = F['row'](current=current, candidate=candidate)
            members = [member(row, component=c) for c in 'RGB']
            groups = [group(members, kind='level', reduction=r) for r in ('max','mean')]
            out = grade([row], groups)
            self.assertEqual([g['status'] for g in out['aggregates']], statuses)
            self.assertEqual(out['status'], 'EXCEEDS')

    def test_missing_or_unmeasured_member_cannot_be_dropped(self):
        row = self.texture()
        second = self.texture()
        second['scene'] = 'photo__rrect-md__rest'
        groups = [group([member(row), member(second)])]
        keys = [list(F['key'](r)) for r in (row, second)]
        self.assertEqual(grade([row], groups, complete=keys, selected=keys)['status'], 'UNMEASURED')
        second['readings'][second['statistic']].update(candidate=None, candidateMeasurementStatus='UNMEASURED')
        self.assertEqual(grade([row,second], groups)['status'], 'UNMEASURED')

    def test_real_partial_is_pending_even_when_this_groups_members_are_complete(self):
        row = self.texture(candidate=.5)
        keys = [list(F['key'](row))]
        complete = keys + [['another-profile','webgpu','another-scene','T1-full-silhouette']]
        out = grade([row], [group([member(row)])], complete=complete, selected=keys,
                    origin='measured-native')
        self.assertEqual(out['status'], 'PENDING_FULL_UNION')
        self.assertEqual(out['aggregates'][0]['status'], 'PENDING_FULL_UNION')
        self.assertNotIn('candidate', out['aggregates'][0])
        self.assertEqual(grade([row], [group([member(row)])])['status'], 'EXCEEDS')
        self.assertEqual(grade([row], [group([member(row)])], origin='measured-native')['status'], 'EXCEEDS')

    def test_newbed_aggregate_reports_worse_score_without_gating(self):
        row = self.texture(candidate=.5)
        out = grade([row], [group([member(row)], kind='newbed-t1', gate=False)])
        self.assertEqual(out['status'], 'WITHIN')
        self.assertEqual(out['aggregates'][0]['status'], 'REPORTED')
        self.assertGreater(out['aggregates'][0]['candidate'], out['aggregates'][0]['current'])

    def test_declared_exception_remains_a_gated_canonical_aggregate_member(self):
        costs = json.loads((Path(__file__).resolve().parent/'declaration-v3/declared-costs.json').read_text())['exceptions']
        exception = next(e for e in costs if e['failedComparisons'][0]['rule'] == 'canonical-T1-growth')
        row = json.loads(Path(exception['measurement']['path']).read_text())['row']
        m = member(row)
        m['epsilon'] = row['readings'][row['statistic']]['code']
        p = policy(costs, [group([m])], origin='measured-native')
        p['completeKeys'] = [exception['key']]
        out = R['route_aggregates']([row], landing_policy=p, policy_sha256=digest(p),
                                   complete_keys=[exception['key']], full_union=True)
        self.assertEqual(out['status'], 'EXCEEDS')
        self.assertEqual(out['aggregates'][0]['memberCount'], 1)

    def test_median_is_not_mean_and_static_native_current_cannot_be_substituted(self):
        rows = [self.texture(candidate=k) for k in (.25, .25, .75)]
        for i, row in enumerate(rows): row['scene'] += str(i)
        groups = [group([member(row) for row in rows])]
        out = grade(rows, groups)
        self.assertEqual(out['aggregates'][0]['candidate'], 0)
        self.assertEqual(out['status'], 'WITHIN')
        for side in ('native', 'current'):
            changed = copy.deepcopy(rows)
            changed[0]['readings'][changed[0]['statistic']][side] += .001
            with self.assertRaisesRegex(ValueError, 'static operands'):
                grade(changed, groups)

    def test_compound_level_substatistics_are_each_counted_once(self):
        row = F['row']('deep8-far24-luma-mean', source='canonical', family='impulse',
                       native=20, current=24, candidate=21)
        row['statistic'] = 'low-end-path-level'
        row['readings']['deep8-far24-luma-median'] = F['reading'](
            'deep8-far24-luma-median', 20, 20, 22)
        members = [member(row, name) for name in row['readings']]
        out = grade([row], [group(members, kind='level', reduction='mean')])
        self.assertEqual(out['aggregates'][0]['candidate'], 1.5)
        self.assertEqual(out['aggregates'][0]['current'], 2)
        self.assertEqual(out['aggregates'][0]['memberCount'], 2)

    def test_mutated_membership_or_duplicate_members_fail_before_scoring(self):
        row = self.texture()
        groups = [group([member(row)])]
        groups[0]['members'][0]['epsilon'] = 2
        with self.assertRaises(ValueError): grade([row], groups)
        with self.assertRaises(ValueError): grade([row], [group([member(row), member(row)])])


class DL5JudgeInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.judge = runpy.run_path(str(Path(__file__).resolve().with_name('judge.py')))

    def test_execution_requires_policy_pin_and_binds_complete_manifest_not_group_coverage(self):
        row = F['row']()
        keys = [list(F['key'](row))]
        complete = keys + [['other','webgpu','scene','statistic']]
        with tempfile.TemporaryDirectory() as directory:
            directory = str(Path(directory).resolve())
            def write(name, value):
                path = Path(directory)/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')
                return {'path':str(path), 'sha256':digest(value)}
            complete_pin = write('complete.json', {'statisticKeys':complete})
            partial_pin = write('partial.json', {'statisticKeys':keys})
            p = policy(aggregates=[group([member(row, component='B')], kind='level', reduction='max')])
            p['completePopulation'] = complete_pin
            p['completeKeys'] = complete
            pp = write('policy.json', p)
            declaration = write('declaration-v3/declaration.json', {'policies':[pp]})
            charter = write('charter.json', {'landingPolicies':{'synthetic':pp},
                'artifacts':[pp, complete_pin, declaration]})
            config = write('judge-config.json', {'landingPolicy':pp})
            inputs = [pp, complete_pin, partial_pin, declaration, charter, config]
            root = {'landingPolicy':pp, 'inputs':inputs, 'dataOrigin':'synthetic',
                    'instruments':{'judge':{'config':config}}}
            execution = {'repo':directory, 'charter':charter, 'inputs':inputs,
                'populations':{'synthetic-rehearsal':{'dataset':'synthetic', 'manifest':complete_pin}}}
            ctx = {'inputs':inputs, 'repo':directory, 'populationPin':partial_pin,
                   'expectedCells':[dict(zip(F['KEY'], k)) for k in keys], 'phase':'gate',
                   'executionRoot':'controlled-test-root'}
            def checked(repo, pin):
                path = Path(pin['path'])
                if self.judge['sha'](path) != pin['sha256']: raise ValueError('input hash')
                return path
            live = types.SimpleNamespace(checked=checked, sealed=lambda _: execution)
            call = self.judge['landing_inputs']
            actual, full_keys, full = call(ctx, live, root, {'landingPolicy':pp})
            self.assertEqual(actual, p)
            self.assertEqual(full_keys, complete)
            self.assertFalse(full)
            with self.assertRaises(ValueError): call(ctx, live, root, {})
            with self.assertRaises(ValueError): call(ctx, live, {**root, 'landingPolicy':None}, {'landingPolicy':pp})
            ctx['populationPin'] = complete_pin
            with self.assertRaises(ValueError): call(ctx, live, root, {'landingPolicy':pp})
            ctx['expectedCells'] = [dict(zip(F['KEY'], k)) for k in complete]
            self.assertTrue(call(ctx, live, root, {'landingPolicy':pp})[2])
            changed = copy.deepcopy(p)
            changed['primaryT1GrowthMultiplier'] = 3
            Path(pp['path']).write_text(json.dumps(changed))
            with self.assertRaises(ValueError): call(ctx, live, root, {'landingPolicy':pp})


if __name__ == '__main__': unittest.main()
