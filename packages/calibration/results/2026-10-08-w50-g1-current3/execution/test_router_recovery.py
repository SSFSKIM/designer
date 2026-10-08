"""Exact partition routing with synthetic transport; no actual capture commands execute."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('recovery_fixture',HERE/'test_recovery.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
spec=importlib.util.spec_from_file_location('recovery_router',HERE.parent/'current_router.py')
Router=importlib.util.module_from_spec(spec);spec.loader.exec_module(Router)
spec=importlib.util.spec_from_file_location('recovery_dispatcher',HERE/'dispatch.py')
D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)


class RecoveryRouting(unittest.TestCase):
    def setUp(self):
        self.f=F.RecoveryPartition('runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.partition=self.f.validate();self.calls=[]
        self.context=dict(phase='current',batch=self.f.batches[0],repo=str(self.f.repo),batchPath=str(self.f.repo/'new-batch.json'))
        Path(self.context['batchPath']).write_text(json.dumps(self.context['batch']))
        self.retained=[dict(profile=r['profile'],renderer=r['renderer'],scene=r['scene'],candidate=r['candidate'],lane='current',
            origin={'kind':'retained-attempt2'},repeatAdmission={'mode':'legacy-byte-identical'},artifacts=r['artifacts'])
            for r in self.partition['retained']]
        def require(context):
            if context is not self.context:raise ValueError('Unbound test context')
        def fresh(context,run):
            require(context);i=context['batch']['runs'].index(run)
            return F.R.fresh_run(self.partition,0,i,run)
        self.dispatcher=types.SimpleNamespace(require_context=require,retained_current_records=lambda c:self.retained,
                                             fresh_current_run=fresh)
        def capture(context,run,current=False):
            require(context);self.calls.extend((run['profile'],run['renderer'],s) for s in run['scenes'])
            return [dict(profile=run['profile'],renderer=run['renderer'],scene=s,candidate=run['candidate'],lane='current',
                         repeatPair={'path':'real-pair','sha256':'a'*64},repeatAdmission={'path':'proof','sha256':'b'*64}) for s in run['scenes']]
        self.adapters={'w50':types.SimpleNamespace(_capture_run=capture),'canonical':types.SimpleNamespace(capture_run=capture)}

    def test_router_never_rerenders501_and_preserves_original672_order(self):
        with patch.dict(sys.modules,{'w50_g1_dispatch':self.dispatcher}),patch.object(Router,'adapters',return_value=self.adapters):
            result=Router.execute_current(self.context)
        self.assertEqual(result['origins'],{'retainedAttempt2':501,'freshAttempt3':171})
        expected=[tuple(r[k] for k in ('profile','renderer','scene')) for r in self.partition['fresh'] if r['sceneSource']=='w50']
        self.assertEqual(self.calls,expected)
        original=[(r['profile'],r['renderer'],s) for r in self.context['batch']['runs'] for s in r['scenes']]
        self.assertEqual([tuple(r[k] for k in ('profile','renderer','scene')) for r in result['captures']],original)
        self.assertTrue(all('repeatPair' not in r for r in result['captures'][:501]))
        self.assertEqual(result['captures'][501]['scene'],F.R.FAILED[2])

    def test_missing_retained_or_duplicate_fresh_member_fails_instead_of_recapturing(self):
        self.retained.pop()
        with patch.dict(sys.modules,{'w50_g1_dispatch':self.dispatcher}),patch.object(Router,'adapters',return_value=self.adapters):
            with self.assertRaises(ValueError):Router.execute_current(self.context)
        self.assertEqual(len(self.calls),171)

    def test_actual_dispatcher_authorizes_only_derived_remaining_slice(self):
        doc={'repo':str(self.f.repo),'currentBatches':[D.pin(self.f.repo,self.context['batchPath'])],
             'recovery':self.partition}
        old=D._ACTIVE;lease=D.GPU_LOCK
        D.GPU_LOCK=self.f.repo/'test-only-gpu.lock'
        contract=self.f.repo/'contract.json';contract.write_text('{}')
        self.context.update(contract=str(contract),executionRoot=str(self.f.directory/'current-instrument-root.json'))
        try:
            # The actual source loader must execute recovery.py from the admitted root.
            import shutil
            shutil.copyfile(HERE/'recovery.py',self.f.directory/'recovery.py')
            with D.owned_gpu_lock():
                D._ACTIVE=(self.context,copy.deepcopy(self.context),D.sha(contract),D.sha(self.context['batchPath']),True,doc,None)
                self.assertIsNone(D.fresh_current_run(self.context,self.context['batch']['runs'][0]))
                remaining=D.fresh_current_run(self.context,self.context['batch']['runs'][11])
                self.assertEqual(remaining['scenes'],self.context['batch']['runs'][11]['scenes'][39:])
                forged={**self.context['batch']['runs'][11],'scenes':['arbitrary']}
                with self.assertRaises(ValueError):D.fresh_current_run(self.context,forged)
        finally:D._ACTIVE=old;D.GPU_LOCK=lease

    def test_archival_result_cannot_fabricate_a_second_legacy_image_or_drop_retained_origin(self):
        doc={'repo':str(self.f.repo),'currentBatches':[D.pin(self.f.repo,self.context['batchPath'])],
             'recovery':self.partition,'recoveryAttempt':self.f.authority}
        records=[]
        for old in self.partition['retained']:
            origin={'kind':'retained-attempt2','ordinal':old['ordinal'],'priorRoot':self.f.authority['priorRoot'],
                    'priorClaim':self.f.authority['priorClaim'],'priorFailure':self.f.authority['priorFailure'],
                    'originalArtifacts':old['artifacts'],'originalEvidence':old['originalEvidence']}
            equality={'schema':'w50-legacy-byte-identical-1','mode':'legacy-byte-identical','reading':'first',
                      'first':old['artifacts']['png'],'originalEqualityAttestation':old['artifacts']['cell'],
                      'deterministic':True,'repeatNoise':0,'secondRetained':False}
            records.append({**{k:old[k] for k in ('profile','renderer','scene')},
                            'origin':origin,'artifacts':old['artifacts'],'repeatAdmission':equality})
        D.verify_recovery_records(self.context,{'captures':records},doc=doc)
        records[0]['repeatPair']={'path':'manufactured-second','sha256':'a'*64}
        with self.assertRaises(ValueError):D.verify_recovery_records(self.context,{'captures':records},doc=doc)
        records[0].pop('repeatPair');records.pop()
        with self.assertRaises(ValueError):D.verify_recovery_records(self.context,{'captures':records},doc=doc)

    def test_repeat_receipt_binds_both_images_reports_and_config_for_later_reads(self):
        first=self.f.put('first.png',{'synthetic':'first pixels'})
        second=self.f.put('second.png',{'synthetic':'second pixels'})
        report1=self.f.put('report1.json',{'synthetic':'first report'})
        report2=self.f.put('report2.json',{'synthetic':'second report'})
        cell=self.f.put('cell.json',{'synthetic':'actual metadata'})
        config=self.f.put('config.json',{'synthetic':'root-pinned repeat policy'})
        pair={'first':{'image':first,'report':report1},'second':{'image':second,'report':report2}}
        pair_pin=self.f.put('pair.json',pair)
        artifacts={'png':first,'report':report1,'cell':cell}
        proof=self.f.put('proof.json',{'manifest':pair_pin,'pair':pair,'originalArtifacts':artifacts,'config':config})
        record={'origin':{'kind':'fresh-attempt3'},'artifacts':artifacts,'repeatPair':pair_pin,'repeatAdmission':proof}
        pins=D.repeat_artifact_pins(self.f.repo,{'captures':[record]})
        names={Path(p['path']).name for p in pins}
        self.assertEqual(names,{'first.png','second.png','report1.json','report2.json','cell.json','config.json','pair.json','proof.json'})
        (self.f.repo/second['path']).write_bytes(b'changed second')
        with self.assertRaises(ValueError):D.repeat_artifact_pins(self.f.repo,{'captures':[record]})

    def test_all_phase_repeat_registration_refuses_missing_or_unsealed_helper(self):
        with self.assertRaises(ValueError):D.validate_repeat_registration(self.f.repo,self.f.directory,None,{})
        helper=self.f.directory.parent/'repeat/admission.py';helper.parent.mkdir();helper.write_text('# synthetic source')
        config=self.f.put('repeat-config.json',{'schema':'w50-repeat-config-1'})
        registration={'entrypoint':D.pin(self.f.repo,helper),'config':config}
        with self.assertRaises(ValueError):D.validate_repeat_registration(self.f.repo,self.f.directory,registration,{})
        D.validate_repeat_registration(self.f.repo,self.f.directory,registration,{registration['entrypoint']['path']:D.sha(helper)})
        helper.write_text('# changed')
        with self.assertRaises(ValueError):D.validate_repeat_registration(self.f.repo,self.f.directory,registration,{registration['entrypoint']['path']:registration['entrypoint']['sha256']})


if __name__=='__main__':unittest.main()
