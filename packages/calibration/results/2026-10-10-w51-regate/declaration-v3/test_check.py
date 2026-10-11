"""DL5 declarations bind source-owned operands, every member and the bounded cost list."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def module():
    spec = importlib.util.spec_from_file_location('w51_dl5_declaration_test', HERE/'build.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def fixture():
    profile = 'apple-macos-27.0-1x-dark-standard-glass0.25'
    def row(scene, statistic, **other):
        return dict(profile=profile, renderer='webgpu', scene=scene, statistic=statistic,
                    role='gate',status='MEASURED', **other)
    text = row('text__rrect__rest', 'T1-low', stratum='T', native=.1, current=.2,
               fidelity={'statistic':'T1-fine', 'native':.03, 'current':.04, 'reference':.06})
    solid = row('solid__rrect__inactive', 'low-end-path-level')
    impulse = row('impulse__rrect__rest', 'low-end-path-level')
    sparse = row('cell-impulse-sparse-s096__rest', 'T1-full-silhouette', nativeIdentity='sparse')
    grey = row('cell-grey-064-s044__rest', 'deep8-channel-median', nativeIdentity='join')
    reported = row('cell-grey-000-s128__rest', 'deep8-far24-luma-mean', nativeIdentity='reported')
    rows = [text, solid, impulse, sparse, grey, reported]
    key = lambda r: [r[n] for n in ('profile','renderer','scene','statistic')]
    keys = sorted(map(key, rows))
    def reading(native, current):
        return {'native':native, 'current':current, 'status':'MEASURED',
                'repeat':{'code':.007, 'B':.02, 'bar':.01}}
    canonical = {'partitions':{'gate':[
        dict(text, readings={'T1-fine':reading(.03,.04), 'T1-low':reading(.1,.2)}),
        dict(solid, readings={'deep8-channel-median':reading([48,48,51],[37,37,38])}),
        dict(impulse, readings={'deep8-far24-luma-mean':reading(20,32),
                               'deep8-far24-luma-median':reading(21,33)})]}}
    completed = {'cells':[dict(sparse, native=.1, current=.2,
                         nativeRepeat={'codeStepLinear':.003}),
                         dict(grey, native=[64,64,64], current=[63,63,63]),
                         dict(reported, native=20, current=32)]}
    manifest = {'cells':[{'id':'sparse','profile':profile, 'scene':sparse['scene'],
                          'family':'structured','pose':'active'},
                         {'id':'join','profile':profile, 'scene':grey['scene'],
                          'family':'uniform','pose':'active','level':64},
                         {'id':'reported','profile':profile, 'scene':reported['scene'],
                          'family':'span','pose':'active','level':0}]}
    scenes = {'scenes':[{'id':text['scene'],'state':'rest','background':'text'},
                        {'id':solid['scene'],'state':'inactive','background':'solid'},
                        {'id':impulse['scene'],'state':'rest','background':'impulse'}],
              'backgrounds':{'text':{'kind':'image'},'solid':{'kind':'solid'},
                             'impulse':{'kind':'impulse'}}}
    pins = {n:{'path':n+'.json','sha256':'a'*64} for n in
            ('population','inventory','completed','canonical','cut','manifest','scenes','costs')}
    exception = {'key':key(solid), 'failedComparisons':[{'rule':'absolute-level',
                'statistic':'deep8-channel-median','components':[{'name':'B','error':2}]}]}
    return {'dataOrigin':'measured-native','population':{'statisticKeys':keys},
            'inventory':{'cells':rows},'completed':completed,'canonical':canonical,
            'cut':{'T1':{'cells':[{'profile':profile,'tier':'webgpu','scene':text['scene'],
                                 'code':.005,'native':.13,'candidate':.14,
                                 'bands':{'fine':{'native':.03,'candidate':.04}}}]}},
            'manifest':manifest,'scenes':scenes,'reportedKeys':[key(reported)],
            'exceptions':[exception], 'pins':pins}


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.b = module()
        self.data = fixture()

    def test_text_uses_fine_values_and_cut_code_not_low_values_or_budget(self):
        policy = self.b.derive_policy(self.data)
        aggregate = next(a for a in policy['aggregates'] if a['kind']=='t1')
        member = aggregate['members'][0]
        self.assertEqual((member['statistic'],member['native'],member['current'],member['epsilon']),
                         ('T1-fine',.03,.04,.005))
        self.assertEqual(aggregate['reduction'],'median-log-ratio')
        self.assertEqual(aggregate['timing'],'gate-full')
        self.assertTrue(aggregate['gate'])

    def test_level_components_include_blue_cost_and_both_impulse_substatistics_once(self):
        policy = self.b.derive_policy(self.data)
        levels = [a for a in policy['aggregates'] if a['kind']=='level']
        self.assertEqual({a['reduction'] for a in levels},{'max','mean'})
        maximum = [m for a in levels if a['reduction']=='max' for m in a['members']]
        self.assertEqual([(m['statistic'],m['component']) for m in maximum],
                         [('deep8-channel-median','R'),('deep8-channel-median','G'),
                          ('deep8-channel-median','B'),('deep8-far24-luma-mean',None),
                          ('deep8-far24-luma-median',None)])
        self.assertEqual(policy['exceptions'], self.data['exceptions'])
        self.assertFalse(any('064' in m['key'][2] or '128' in m['key'][2] for m in maximum))

    def test_newbed_texture_stays_separate_reported_with_source_owned_epsilon(self):
        policy = self.b.derive_policy(self.data)
        aggregate = next(a for a in policy['aggregates'] if a['kind']=='newbed-t1')
        self.assertFalse(aggregate['gate'])
        self.assertEqual(aggregate['members'][0]['epsilon'],.003)
        self.assertEqual(len([a for a in policy['aggregates'] if a['kind']=='t1']),1)

    def test_dark05_uses_own_prefit_fine_operands_and_native_mean_code(self):
        data = self.data
        for name in ('inventory','completed'):
            for row in data[name]['cells']:row['profile']=row['profile'].replace('0.25','0.5')
        for rows in data['canonical']['partitions'].values():
            for row in rows:row['profile']=row['profile'].replace('0.25','0.5')
        for row in data['manifest']['cells']:row['profile']=row['profile'].replace('0.25','0.5')
        for key in data['population']['statisticKeys']+data['reportedKeys']:
            key[0]=key[0].replace('0.25','0.5')
        data['exceptions']=[]
        row=data['canonical']['partitions']['gate'][0]['readings']['T1-fine']
        row.update(native=.031,current=.042)
        aggregate=next(a for a in self.b.derive_policy(data)['aggregates'] if a['kind']=='t1')
        member=aggregate['members'][0]
        self.assertEqual((member['native'],member['current'],member['epsilon']),(.031,.042,.007))
        self.assertEqual(member['provenance']['source'],data['pins']['canonical'])

    def test_changed_members_values_epsilon_provenance_and_cap_refuse_even_rehashed(self):
        good = self.b.derive_policy(self.data)
        for action in ('missing','duplicate','wrong-key','wrong-band','wrong-epsilon',
                       'wrong-source','wrong-value','wrong-cap','dropped-exception'):
            with self.subTest(action=action):
                bad = copy.deepcopy(good)
                aggregate = next(a for a in bad['aggregates'] if a['kind']=='t1')
                member = aggregate['members'][0]
                if action=='missing':aggregate['members']=[]
                elif action=='duplicate':aggregate['members'].append(copy.deepcopy(member))
                elif action=='wrong-key':member['key'][2]='unpriced__rrect__rest'
                elif action=='wrong-band':member['statistic']='T1-low'
                elif action=='wrong-epsilon':member['epsilon']=.02
                elif action=='wrong-source':member['provenance']['source']['sha256']='b'*64
                elif action=='wrong-value':member['native']=.06
                elif action=='wrong-cap':bad['primaryT1GrowthMultiplier']=3
                else:bad['exceptions']=[]
                aggregate['membershipSha256']=self.b.digest(aggregate['members'])
                with self.assertRaises(ValueError):self.b.validate_policy(bad,self.data)

    def test_missing_required_source_reading_blocks_instead_of_dropping_member(self):
        del self.data['canonical']['partitions']['gate'][0]['readings']['T1-fine']
        with self.assertRaises(ValueError):self.b.derive_policy(self.data)

    def test_unmeasured_static_source_with_populated_numbers_still_blocks(self):
        self.data['canonical']['partitions']['gate'][0]['readings']['T1-fine']['status']='UNMEASURED'
        with self.assertRaises(ValueError):self.b.derive_policy(self.data)

    def test_synthetic_cannot_inherit_real_exceptions_and_uses_complete_population_timing(self):
        self.data['dataOrigin']='synthetic'
        with self.assertRaises(ValueError):self.b.derive_policy(self.data)
        self.data['exceptions']=[]
        policy=self.b.derive_policy(self.data)
        self.assertEqual({a['timing'] for a in policy['aggregates']},{'population-full'})
        self.assertEqual(policy['exceptions'],[])

    def test_prefit_pin_accepts_absolute_and_relative_same_location_not_another_hash(self):
        a={'path':'packages/reference.json','sha256':'a'*64}
        b={'path':str(self.b.REPO/'packages/reference.json'),'sha256':'a'*64}
        self.assertTrue(self.b.same_pin(a,b))
        self.assertFalse(self.b.same_pin(a,{**b,'sha256':'b'*64}))

    def test_real_gate_slot_refuses_build_but_old_rehearsal_markers_do_not(self):
        with tempfile.TemporaryDirectory() as folder:
            wave=Path(folder)
            slots=wave/'execution-slots';slots.mkdir()
            (slots/'real-rehearsal-old.json').write_text('{}')
            self.b.ensure_pre_gate(wave)
            (slots/'gate.json').write_text('{}')
            with self.assertRaises(ValueError):self.b.ensure_pre_gate(wave)


class RealEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=module()
        cls.real,cls.synthetic,_=cls.b.frozen_inputs()
        cls.costs=cls.b.load(HERE/'declared-costs.json')
        cls.report=cls.b.read(cls.costs['rehearsalReport'])

    def test_every_known_cost_remains_in_its_priced_or_reported_aggregate(self):
        policy=self.b.derive_policy(self.real)
        aggregate_keys={tuple(m['key']) for a in policy['aggregates'] for m in a['members']}
        self.assertTrue({tuple(e['key']) for e in policy['exceptions']} <= aggregate_keys)
        self.assertEqual(policy['completeKeys'],self.real['population']['statisticKeys'])

    def test_changed_costs_cannot_hide_behind_a_new_self_consistent_report_pin(self):
        for mutation in ('remove','duplicate','ceiling','operand','pin'):
            with self.subTest(mutation=mutation):
                costs=copy.deepcopy(self.costs)
                if mutation=='remove':costs['exceptions'].pop()
                elif mutation=='duplicate':costs['exceptions'].append(copy.deepcopy(costs['exceptions'][0]))
                elif mutation=='ceiling':costs['exceptions'][0]['failedComparisons'][0]['components'][0]['growth']+=1e-5
                elif mutation=='operand':costs['exceptions'][0]['readings']['T1-full-silhouette']['native']+=1e-5
                else:costs['exceptions'][0]['measurement']['sha256']='0'*64
                with self.assertRaises(ValueError):
                    self.b.validate_costs(costs,self.report,self.real['population'])

    def test_epsilon_uses_prefit_interior_mean_step_not_a_fine_residual_derived_step(self):
        policy=self.b.derive_policy(self.real)
        text=next(m for a in policy['aggregates'] if a['kind']=='t1' and
                  a['dimensions']['position']==.5 and a['dimensions']['stratum']=='T'
                  for m in a['members'])
        indexed=self.b.indexed([r for rows in self.real['canonical']['partitions'].values() for r in rows])
        source=indexed[tuple(text['key'])]['readings']['T1-fine']['repeat']
        self.assertEqual(text['epsilon'],source['code'])
        self.assertGreater(source['publishedNativeInteriorMean'],text['native'])
        self.assertEqual(text['provenance']['epsilon']['selector']['field'],['repeat','code'])

    def test_synthetic_and_real_sources_and_exception_authorities_stay_disjoint(self):
        real=self.b.derive_policy(self.real);synthetic=self.b.derive_policy(self.synthetic)
        self.assertEqual(synthetic['exceptions'],[])
        self.assertTrue(set(map(tuple,real['completeKeys'])).isdisjoint(map(tuple,synthetic['completeKeys'])))
        self.assertTrue(all('synthetic/generated/' in p['path'] for p in synthetic['sources']))


if __name__ == '__main__':unittest.main()
