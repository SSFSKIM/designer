"""Synthetic JSON phase rows only; never read an inventory, report, image or blind statistic."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
INVENTORY='e'*64
PROFILE='apple-macos-27.0-1x-dark-standard-glass0.25'
KEY=('profile','renderer','scene','statistic')


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def evidence(side, name, *, history=False):
    pair=None if side=='native' else {'activeSha256':'a'*64,'recededSha256':'b'*64}
    if side=='candidate':pair={'activeSha256':'f'*64,'recededSha256':'0'*64}
    if history:pair={'activeSha256':'1'*64,'recededSha256':'2'*64}
    kind='frozen-reference-record' if history else 'native-three-run-cohort' if side=='native' else 'png'
    identity={'kind':kind,'digest':digest({'side':side,'kind':kind})}
    if kind=='native-three-run-cohort':identity['runs']=[{'run':r,'sha256':str(r)*64} for r in (1,2,3)]
    elif kind=='png':identity['pin']={'path':side+'.png','sha256':identity['digest']}
    return {'captureIdentity':identity,'numericIdentity':{'captureSha256':identity['digest'],
            'statisticSha256':digest({'side':side,'statistic':name}),'documentPair':pair}}


def reading(name, native, current, candidate, *, units=None, code=None, bar=None, bound=None):
    channel=name.endswith('-channel-median')
    units=units or ('encoded-RGB-codes' if channel else 'linear-luma' if name.startswith('T1-') else 'encoded-luma-codes')
    support={'deep8-channel-median':'deep8','central8-channel-median':'center8',
             'deep8-far24-luma-mean':'deep8_far24','deep8-far24-luma-median':'deep8_far24',
             'T1-full-silhouette':'full-silhouette','T1-low':'eroded4','T1-fine':'eroded4'}[name]
    code=(.03125 if units=='linear-luma' else 1) if code is None else code
    bar=code/2 if bar is None else bar
    bound=max(code,2*bar) if bound is None else bound
    return dict(units=units,support=support,measurementStatus='MEASURED',nativeMeasurementStatus='MEASURED',
        currentMeasurementStatus='MEASURED',candidateMeasurementStatus='MEASURED',native=native,current=current,
        candidate=candidate,code=code,bar=bar,B=bound,originalBudgetB=None,nativeRepeat={'synthetic':True},
        nativeSupportWitnesses=[],required=True,reported=False,eligibleEmptySupport=False,
        evidence={s:evidence(s,name) for s in ('native','current','candidate')})


def row(name='deep8-channel-median', *, source='w50', family='uniform', renderer='webgpu', input_code=4,
        scene=None, native=None, current=None, candidate=None):
    if scene is None:
        scene='cell-grey-004-s096__rest' if source=='w50' else 'checkerboard__rrect-md__rest'
    channel=name.endswith('-channel-median')
    native=[20]*3 if native is None and channel else .25 if native is None else native
    current=copy.deepcopy(native) if current is None else current
    candidate=copy.deepcopy(native) if candidate is None else candidate
    original=dict(profile=PROFILE,renderer=renderer,scene=scene,statistic=name,role='calibration',
                  support='original supplied support prose',B=None,historical=[],
                  currentGeneration='full-pair-generation',currentDocumentPair={'active.dark':'a'*64,'receded.dark':'b'*64})
    return dict(**{k:original[k] for k in KEY},role=original['role'],originalReference=copy.deepcopy(original),
        reference=copy.deepcopy(original),historical=[],sceneSource=source,family=family,inputCode=input_code,
        span=96,pose='active',scale=1,position=.25,support=original['support'],
        currentGeneration=original['currentGeneration'],currentDocumentPair=original['currentDocumentPair'],
        readings={name:reading(name,native,current,candidate)})


def key(item):return tuple(item[k] for k in KEY)


def frozen_operands(item):
    """Mirror the source-owned original-operand schema using synthetic frozen records only."""
    name=item['statistic'];value=item['readings'][name]
    for reference in (item['originalReference'],item['reference']):
        reference.update(native=value['native'],current=value['current'])
    value['sourceReading']=copy.deepcopy(value)
    value['routingOperands']='ORIGINAL_INVENTORY'
    for side in ('native','current'):
        binding=dict(kind='frozen-reference-record',inventory={'path':'original.json','sha256':INVENTORY},
                     key=list(key(item)),side=side,original=copy.deepcopy(item['originalReference']))
        token=digest(binding)
        pair=None if side=='native' else {'activeSha256':'a'*64,'recededSha256':'b'*64}
        value['evidence'][side]=dict(captureIdentity={**binding,'digest':token},numericIdentity={
            'captureSha256':token,'statisticSha256':digest({'side':side,'value':value[side]}),'documentPair':pair})
    full=name=='T1-full-silhouette'
    estimator='PRODUCTION_TS_INTERIOR_LEVEL' if full else 'CANONICAL_NUMPY_GAUSSIAN_LOW'
    value['candidateEstimator']=estimator
    value['evidence']['candidate']['productionStatistic']=dict(estimator=estimator,statistic=name,
        producer='packages/calibration/src/metrics/material.ts#interiorLevel' if full else
            'packages/calibration/results/2026-10-08-w50-g1-fit/references/statistics.py#canonical_read',
        field='material.interiorStdDevWeb' if full else 'web.statistics.T1-low',reading='first',
        capture=copy.deepcopy(value['evidence']['candidate']['captureIdentity']['pin']),
        matrix={'path':'candidate-matrix.json','sha256':'7'*64},scene=item['scene'],
        units='linear-luma',value=value['candidate'])
    return value


class RulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('w50_rules_test',HERE/'rules.py')
        cls.r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.r;spec.loader.exec_module(cls.r)

    def route(self,item,**policy):
        return self.r.route_row(item,inventory_sha256=INVENTORY,**policy)

    def test_webgpu_absolute_channels_do_not_cancel_and_css_is_own_current_error_growth(self):
        gpu=row(candidate=[22,18,20]);out=self.route(gpu)
        self.assertEqual(out['status'],'EXCEEDS')
        self.assertEqual(out['failures'],['absolute-level:deep8-channel-median'])
        self.assertEqual([c['error'] for c in out['checks'][0]['comparison']['components']],[2,2,0])
        css=row(renderer='css',current=[25]*3,candidate=[14]*3)
        out=self.route(css)
        self.assertEqual(out['status'],'WITHIN')
        self.assertEqual(out['checks'][0]['comparison']['components'][0]['growth'],1)
        self.assertEqual(out['diagnostics'][0]['comparison']['components'][0]['error'],6)
        self.assertEqual(out['diagnostics'][0]['comparison']['status'],'DIAGNOSTIC')
        css['readings']['deep8-channel-median']['candidate']=[13.9]*3
        self.assertEqual(self.route(css)['status'],'EXCEEDS')

    def test_input64_is_diagnostic_both_tiers_without_css_growth_or_native_bound(self):
        for tier in ('webgpu','css'):
            item=row(renderer=tier,input_code=64,scene='cell-grey-064-s096__rest',candidate=[200]*3)
            out=self.route(item)
            self.assertEqual(out['status'],'DIAGNOSTIC')
            self.assertEqual(out['checks'],[])
            self.assertEqual(out['failures'],[])
            self.assertTrue(all(c['bound'] is None for d in out['diagnostics'] for c in d['comparison']['components']))
            self.assertEqual(out['numericalIdentity'],'REQUIRED_SEPARATE_JOIN_REFEREE')

    def test_compound_impulse_retains_one_original_key_and_separate_mean_median_intersection(self):
        item=row(source='canonical',family='impulse',name='deep8-far24-luma-mean',input_code=None,
                 scene='impulse__rrect-lg__inactive',native=20,current=22,candidate=20)
        item['statistic']=item['originalReference']['statistic']=item['reference']['statistic']='low-end-path-level'
        item['readings']['deep8-far24-luma-median']=reading('deep8-far24-luma-median',20,22,22)
        out=self.route(item)
        self.assertEqual(key(out),key(item))
        self.assertEqual(len(out['checks']),2)
        self.assertEqual([c['comparison']['status'] for c in out['checks']],['WITHIN','EXCEEDS'])
        self.assertEqual(out['status'],'EXCEEDS')
        self.assertEqual(out['sourceReadings'],item['readings'])
        with self.assertRaises(ValueError):self.route({**item,'readings':{'deep8-far24-luma-mean':item['readings']['deep8-far24-luma-mean']}})
        item['readings']['deep8-far24-luma-median']['evidence']['candidate']=evidence('current','other')
        with self.assertRaises(ValueError):self.route(item)

    def test_newbed_structured_t1_both_tiers_without_absolute_texture_gate(self):
        for tier in ('webgpu','css'):
            item=row('T1-full-silhouette',family='structured',renderer=tier,input_code=None,
                scene='cell-impulse-sparse-s096__rest',native=.25,current=.375,candidate=.39)
            out=self.route(item)
            self.assertEqual(out['status'],'WITHIN')
            self.assertEqual(out['checks'][0]['rule'],'newbed-structured-T1-growth')
            self.assertEqual(out['diagnostics'][0]['comparison']['status'],'DIAGNOSTIC')
            item['readings']['T1-full-silhouette']['candidate']=.5
            self.assertEqual(self.route(item)['status'],'EXCEEDS')

    def test_separate_newbed_structured_luma_keys_use_native_bounds_without_inventing_a_companion(self):
        rows=[]
        for name,value in (('deep8-far24-luma-mean',20),('deep8-far24-luma-median',22)):
            rows.append(row(name,family='structured',input_code=None,scene='cell-impulse-sparse-s096__rest',
                            native=20,current=22,candidate=value))
        out=self.r.route_rows(rows,inventory_sha256=INVENTORY)
        self.assertEqual([key(r) for r in out],[key(r) for r in rows])
        self.assertEqual([r['status'] for r in out],['WITHIN','EXCEEDS'])
        self.assertTrue(all(len(r['checks'])==1 for r in out))

    def test_compound_css_checks_share_the_same_first_capture_and_documents(self):
        item=row(source='canonical',family='impulse',renderer='css',name='deep8-far24-luma-mean',input_code=None,
                 scene='impulse__rrect-lg__inactive',native=20,current=22,candidate=20)
        item['statistic']=item['originalReference']['statistic']=item['reference']['statistic']='low-end-path-level'
        item['readings']['deep8-far24-luma-median']=reading('deep8-far24-luma-median',20,22,20)
        self.assertEqual(self.route(item)['status'],'WITHIN')
        item['readings']['deep8-far24-luma-median']['evidence']['candidate']=evidence('current','other')
        with self.assertRaises(ValueError):self.route(item)

    def test_wrong_fine_units_and_missing_current_diagnostic_cannot_count_as_complete_evidence(self):
        item=row('T1-low',source='canonical',family='texture',input_code=None,scene='hc-text-7__rrect-lg__rest')
        item['readings']['T1-fine']=reading('T1-fine',20,20,20,units='encoded-luma-codes')
        with self.assertRaises(ValueError):self.route(item)
        held=row(input_code=64,scene='cell-grey-064-s096__rest')
        v=held['readings'][held['statistic']];v.update(currentMeasurementStatus='UNMEASURED',current=None)
        out=self.route(held)
        self.assertEqual(out['status'],'UNMEASURED');self.assertFalse(out['complete'])

    def test_canonical_t1_low_keeps_fine_diagnostic_and_regression_is_webgpu_only(self):
        for tier in ('webgpu','css'):
            item=row('T1-low',source='canonical',family='texture',renderer=tier,input_code=None,
                scene='hc-text-7__rrect-lg__rest',native=.25,current=.375,candidate=.39)
            item['readings']['T1-fine']=reading('T1-fine',.01,.01,.8)
            out=self.route(item)
            self.assertEqual(out['status'],'WITHIN' if tier=='webgpu' else 'DIAGNOSTIC')
            self.assertEqual(len(out['checks']),1 if tier=='webgpu' else 0)
            self.assertTrue(any(d['statistic']=='T1-fine' for d in out['diagnostics']))
            self.assertEqual(out['failures'],[])
        item['readings'].pop('T1-fine')
        with self.assertRaises(ValueError):self.route(item)

    def test_frozen_primary_t1_B_is_not_replaced_by_fresh_native_bundle(self):
        item=row('T1-full-silhouette',source='canonical',family='texture',input_code=None,
                 native=.25,current=.375,candidate=.5)
        value=item['readings']['T1-full-silhouette'];value['originalBudgetB']=.125
        item['originalReference']['B']=item['reference']['B']=.125
        frozen_operands(item)
        out=self.route(item)
        self.assertEqual(out['status'],'WITHIN')
        self.assertEqual(out['checks'][0]['comparison']['components'][0]['bound'],.125)
        self.assertEqual(out['sourceReadings']['T1-full-silhouette']['code'],.03125)
        self.assertEqual(out['sourceReadings']['T1-full-silhouette']['bar'],.015625)
        self.assertEqual(out['sourceReadings']['T1-full-silhouette']['B'],.03125)
        value['candidate']=.5001
        value['evidence']['candidate']['productionStatistic']['value']=.5001
        self.assertEqual(self.route(item)['status'],'EXCEEDS')
        value['originalBudgetB']=.25
        with self.assertRaises(ValueError):self.route(item)

    def test_omitting_original_T1_budget_cannot_advance_to_a_larger_fresh_native_budget(self):
        item=row('T1-full-silhouette',source='canonical',family='texture',input_code=None,
                 native=.25,current=.375,candidate=.5)
        item['originalReference']['B']=item['reference']['B']=.03125
        v=item['readings']['T1-full-silhouette'];v.update(bar=.125,B=.25,originalBudgetB=None)
        with self.assertRaises(ValueError):self.route(item)

    def test_own_history_uses_original_full_pair_frozen_normalized_cap_not_candidate_baseline(self):
        item=row('T1-full-silhouette',source='canonical',family='texture',input_code=None,
                 native=.25,current=.375,candidate=.5)
        value=item['readings']['T1-full-silhouette'];value['originalBudgetB']=.125
        item['originalReference']['B']=item['reference']['B']=.125
        historical=dict(generation='own-history',value=.3125,enforced=True,maxGrowthInB=1,
                        frozenCurrentGrowthInB=.5,documentPair={'active.dark':'1'*64,'receded.dark':'2'*64})
        for container in (item,item['reference'],item['originalReference']):container['historical']=[copy.deepcopy(historical)]
        value['evidence']['historical']=[dict(evidence('historical','T1-full-silhouette',history=True),original=historical)]
        frozen_operands(item)
        out=self.route(item)
        self.assertEqual(out['status'],'EXCEEDS')
        self.assertEqual(out['failures'],['own-history[0]:T1-full-silhouette'])
        self.assertEqual(out['checks'][1]['comparison']['components'][0]['bound'],.125)
        self.assertEqual(out['sourceHistorical'],[historical])
        value['evidence']['historical'][0]['numericIdentity']['documentPair']['activeSha256']='9'*64
        with self.assertRaises(ValueError):self.route(item)

    def test_missing_frozen_history_measurement_is_unmeasured_without_a_substituted_zero(self):
        item=row('T1-full-silhouette',source='canonical',family='texture',input_code=None)
        historical=dict(generation='own-history',value=None,enforced=True,maxGrowthInB=None,
                        frozenCurrentGrowthInB=None,documentPair={'active.dark':'1'*64,'receded.dark':'2'*64})
        for container in (item,item['reference'],item['originalReference']):container['historical']=[copy.deepcopy(historical)]
        item['readings']['T1-full-silhouette']['evidence']['historical']=[dict(
            evidence('historical','T1-full-silhouette',history=True),original=historical)]
        out=self.route(item)
        self.assertEqual(out['status'],'UNMEASURED')
        self.assertFalse(out['complete'])
        self.assertIsNone(out['sourceHistorical'][0]['value'])

    def test_original_TS_operands_keep_unchanged_candidate_within_its_attained_historical_cap(self):
        import math
        native,current,historical_value=.125,.25,.125
        item=row('T1-full-silhouette',source='canonical',family='texture',input_code=None,
                 native=native,current=current,candidate=current)
        value=item['readings'][item['statistic']];value['originalBudgetB']=.03125
        item['originalReference']['B']=item['reference']['B']=.03125
        historical=dict(generation='own-history',value=historical_value,enforced=True,maxGrowthInB=4,
            frozenCurrentGrowthInB=4,documentPair={'active.dark':'1'*64,'receded.dark':'2'*64})
        for holder in (item,item['reference'],item['originalReference']):holder['historical']=[copy.deepcopy(historical)]
        value['evidence']['historical']=[dict(evidence('historical',item['statistic'],history=True),original=historical)]
        frozen_operands(item)
        source=value['sourceReading']
        source['native']=math.nextafter(native,1)
        source['current']=math.nextafter(current,1)
        source['candidate']=math.nextafter(current,1)
        original=copy.deepcopy(item)
        out=self.route(item)
        historical_check=next(c for c in out['checks'] if c['rule']=='own-history[0]')
        self.assertEqual(out['status'],'WITHIN')
        self.assertEqual(historical_check['comparison']['status'],'WITHIN')
        self.assertEqual(historical_check['comparison']['components'][0]['bound'],.125)
        self.assertEqual(item,original)
        self.assertEqual(out['sourceReadings'][item['statistic']]['sourceReading'],source)
        value['candidate']=math.nextafter(current,1)
        value['evidence']['candidate']['productionStatistic']['value']=value['candidate']
        self.assertEqual(next(c for c in self.route(item)['checks'] if c['rule']=='own-history[0]')['comparison']['status'],'EXCEEDS')
        value['current']=source['current']
        with self.assertRaises(ValueError):self.route(item)

    def test_frozen_primary_and_fine_associate_via_unchanged_source_reading_not_record_digest(self):
        item=row('T1-low',source='canonical',family='texture',input_code=None,
                 scene='hc-text-7__rrect-lg__rest',native=.125,current=.25,candidate=.25)
        item['originalReference']['B']=item['reference']['B']=.03125
        primary=item['readings']['T1-low'];primary['originalBudgetB']=.03125
        item['readings']['T1-fine']=reading('T1-fine',.01,.02,.02)
        frozen_operands(item)
        out=self.route(item)
        self.assertEqual(out['status'],'WITHIN')
        self.assertTrue(any(c['statistic']=='T1-fine' for c in out['diagnostics']))
        primary['candidateEstimator']='UNATTESTED_RECOMPUTATION'
        with self.assertRaises(ValueError):self.route(item)

    def test_frozen_primary_candidate_and_current_keep_their_actual_document_pairs(self):
        def frozen(name):
            item=row(name,source='canonical',family='texture',input_code=None,
                     scene='hc-text-7__rrect-lg__rest',native=.125,current=.25,candidate=.25)
            item['originalReference']['B']=item['reference']['B']=.03125
            item['readings'][name]['originalBudgetB']=.03125
            if name=='T1-low':item['readings']['T1-fine']=reading('T1-fine',.01,.02,.02)
            frozen_operands(item)
            return item,item['readings'][name]
        for name in ('T1-low','T1-full-silhouette'):
            item,_=frozen(name);self.assertEqual(self.route(item)['status'],'WITHIN')
            # The primary candidate's numeric document pair must be its diagnostic's pair.
            item,value=frozen(name)
            value['evidence']['candidate']['numericIdentity']['documentPair']={'activeSha256':'9'*64,'recededSha256':'0'*64}
            with self.assertRaises(ValueError):self.route(item)
            # So must its whole capture identity, not only the PNG pin.
            item,value=frozen(name)
            value['evidence']['candidate']['captureIdentity']['extra']='relabelled'
            with self.assertRaises(ValueError):self.route(item)
            # The frozen current operand belongs to the row's own current document pair.
            item,value=frozen(name)
            value['evidence']['current']['numericIdentity']['documentPair']={'activeSha256':'9'*64,'recededSha256':'b'*64}
            with self.assertRaises(ValueError):self.route(item)

    def test_frozen_t1_low_candidate_value_equals_its_source_diagnostic(self):
        item=row('T1-low',source='canonical',family='texture',input_code=None,
                 scene='hc-text-7__rrect-lg__rest',native=.125,current=.25,candidate=.25)
        item['originalReference']['B']=item['reference']['B']=.03125
        primary=item['readings']['T1-low'];primary['originalBudgetB']=.03125
        item['readings']['T1-fine']=reading('T1-fine',.01,.02,.02)
        frozen_operands(item)
        self.assertEqual(self.route(item)['status'],'WITHIN')
        primary['candidate']=.25+1/1024
        primary['evidence']['candidate']['productionStatistic']['value']=primary['candidate']
        with self.assertRaises(ValueError):self.route(item)

    def test_exact_reported_keys_only_and_empty_T1_retains_three_zero_witnesses_not_zero_value(self):
        item=row('T1-full-silhouette',family='span',scene='cell-grey-000-s128__inactive',input_code=0)
        v=item['readings']['T1-full-silhouette']
        v.update(reported=True,eligibleEmptySupport=True,required=False,B=None,measurementStatus='UNMEASURED_EMPTY_SUPPORT',
            nativeMeasurementStatus='UNMEASURED_EMPTY_SUPPORT',currentMeasurementStatus='UNMEASURED_EMPTY_SUPPORT',
            candidateMeasurementStatus='UNMEASURED_EMPTY_SUPPORT',native=None,current=None,candidate=None)
        empty_hash=hashlib.sha256(bytes(384*512//8)).hexdigest()
        v['nativeSupportWitnesses']=[dict(run=r,pixels=0,maskShape=[384,512],maskPackedBitsSha256=empty_hash) for r in (1,2,3)]
        out=self.route(item,reported_keys=[key(item)],empty_support_keys=[key(item)])
        self.assertEqual(out['status'],'UNMEASURED_EMPTY_SUPPORT')
        self.assertEqual(out['failures'],[])
        self.assertIsNone(out['sourceReadings']['T1-full-silhouette']['candidate'])
        self.assertEqual(out['emptySupportWitnesses'],v['nativeSupportWitnesses'])
        with self.assertRaises(ValueError):self.route(item,reported_keys=[key(item)])
        with self.assertRaises(ValueError):self.route(item)
        v['nativeSupportWitnesses'][0]['pixels']=1
        with self.assertRaises(ValueError):self.route(item,reported_keys=[key(item)],empty_support_keys=[key(item)])

    def test_reported_nonempty_controls_have_no_B_gate_and_cannot_exempt_level_rows(self):
        item=row('deep8-far24-luma-mean',family='span',scene='cell-grey-028-s128__rest',input_code=28,
                 native=20,current=20,candidate=200)
        v=item['readings'][item['statistic']];v.update(reported=True,required=False,B=None)
        out=self.route(item,reported_keys=[key(item)])
        self.assertEqual(out['status'],'DIAGNOSTIC');self.assertEqual(out['checks'],[])
        level=row();level['readings'][level['statistic']]['reported']=True
        with self.assertRaises(ValueError):self.route(level,reported_keys=[key(level)])

    def test_missing_required_reading_is_unmeasured_and_owner_keys_are_explicitly_deferred(self):
        item=row();v=item['readings'][item['statistic']]
        v.update(candidateMeasurementStatus='UNMEASURED',measurementStatus='UNMEASURED',candidate=None)
        out=self.route(item)
        self.assertEqual(out['status'],'UNMEASURED');self.assertTrue(out['unmeasured'])
        owner=row(source='canonical',family='solid');owner['statistic']='owner-contracts';owner['readings']={}
        for c in (owner['originalReference'],owner['reference']):c['statistic']='owner-contracts'
        out=self.route(owner)
        self.assertEqual(out['status'],'OWNER_CONTRACT_REQUIRED')
        self.assertEqual(out['checks'],[])
        self.assertFalse(out['complete'])

    def test_numeric_evidence_retains_cohort_and_frozen_record_kinds_not_PNG_capture_claims(self):
        for side,kind in (('native','native-three-run-cohort'),('historical','frozen-reference-record'),('candidate','png')):
            record=evidence(side,'T1-full-silhouette',history=side=='historical')
            typed=self.r._evidence(record,side)
            self.assertEqual(typed.source_kind,kind)
            self.assertEqual(typed.source_sha256,record['captureIdentity']['digest'])

    def test_duplicate_original_keys_wrong_side_identity_and_unknown_stats_refuse_without_I_O(self):
        item=row()
        with patch.object(Path,'read_bytes',side_effect=AssertionError('evidence I/O')):
            self.assertEqual(self.route(item)['status'],'WITHIN')
            with self.assertRaises(ValueError):self.r.route_rows([item,item],inventory_sha256=INVENTORY)
        altered=copy.deepcopy(item)
        altered['readings'][altered['statistic']]['evidence']['candidate']['captureIdentity']['digest']='0'*64
        with self.assertRaises(ValueError):self.route(altered)
        altered['readings']['unknown']=altered['readings'].pop(altered['statistic'])
        with self.assertRaises(ValueError):self.route(altered)

    def test_full_union_targets_keep_source_code_not_B_and_missing_members_are_unmeasured(self):
        n=self.r.N
        contract={}
        for target,scale in self.r.TARGETS:
            names=['checkerboard__rrect-md__rest'] if target=='C rest' else \
                ['checkerboard-8__rrect-lg__inactive'] if target=='F inactive' else \
                ['photo__rrect-md__rest','photo__rrect-md__inactive']
            cells=[]
            for scene in names:
                identity=n.RowIdentity(PROFILE.replace('-1x-',f'-{scale}x-'),'webgpu',scene,
                                       'T1-full-silhouette','full-silhouette')
                def typed(value,side):return n.Reading('MEASURED','linear-luma',value,
                    self.r._evidence(evidence(side,'T1-full-silhouette',history=side=='historical'),side))
                reference=n.Reference(identity,INVENTORY,typed(0,'native'),typed(.0625,'current'),
                                      .03125,.0625,.125)
                cells.append(n.AggregateCell(reference,n.Candidate(identity,typed(.125,'candidate')),
                                             typed(.5,'historical')))
            contract[(target,scale)]={'cells':cells,'expectedKeys':tuple(c.reference.identity for c in cells)}
        out=self.r.route_targets(contract,full_union=True)
        import math
        self.assertTrue(all(c['status']=='EXCEEDS' for c in out))
        self.assertTrue(all(abs(c['candidate']-math.log(5))<1e-12 for c in out))
        contract[('P',1)]['cells'].pop()
        partial=self.r.route_targets(contract,full_union=True)
        self.assertEqual(next(c for c in partial if (c['target'],c['scale'])==('P',1))['status'],'UNMEASURED')
        with self.assertRaises(ValueError):self.r.route_targets(contract,full_union='gate')

    def test_six_targets_wait_for_full_union_and_do_not_create_an_aggregate_from_partial_cells(self):
        out=self.r.route_targets(None,full_union=False)
        self.assertEqual(len(out),6)
        self.assertEqual({(r['target'],r['scale']) for r in out},
                         {(t,s) for t in ('C rest','F inactive','P') for s in (1,2)})
        self.assertTrue(all(r['status']=='PENDING_FULL_UNION' for r in out))
        with self.assertRaises(ValueError):self.r.route_targets(None,full_union=True)


if __name__=='__main__':unittest.main()
