"""Per-browser X6 gate: synthetic facts/processes and scratch receipts only."""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from PIL import Image
import runner
import test_runner as harness
from test_domain import evidence, records

OBSERVER = 'packages/calibration/results/2026-09-27-w41-g1-identification/x6/observe.py'
DEPENDENCY = 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/record-machine.py'


def reading():
    def command(stdout):
        return {'command':['synthetic'], 'exitCode':0, 'stdout':stdout, 'stderr':''}
    return {'recordedAt':'2026-09-27T00:00:00Z',
        'settings':{k:command(v) for k,v in [('reduceTransparency','0'),
                    ('increaseContrast','0'),('NSGlassTintAmount','0.5')]},
        'processCensus':{**command('1 0 synthetic'), 'usable':True, 'foreignProcesses':[]},
        'foreignProcesses':[], 'foreignProcessCount':0,
        'idle':command('"HIDIdleTime" = 60000000000'),
        'verdict':{'passes':True,'facts':{},'idleSeconds':60,'refusals':[]}}


class X6Tests(harness.ExposureTests):
    def setUp(self):
        super().setUp()
        first=self.cells[0]
        other=next(c for c in runner.cells_for(self.wave,('calibration',),True)
                   if c.split('/')[0]!=first.split('/')[0] and c.split('/')[1]==first.split('/')[1])
        self.cells=sorted([first,other])
        evidence(self,self.cells)
        runtime=runner.load(self.root/'config.json');runtime['fixtures']='generated'
        self.put('config.json',runtime)
        self.put('predictions.json',{'cells':{c:[80,90,100] for c in self.cells}})
        self.put('rendered.json',{'cells':{c:{'png':'0.png','projection':'0.json'} for c in self.cells}})
        self.put('survival.json',{k:{c:True for c in self.cells} for k in ('numerical','rendered','veto')})
        for name in (OBSERVER,DEPENDENCY):self.put(name,(runner.ROOT/name).read_text())
        self.commit()
        self.manifest=runner.freeze(self.root,self.wave,self.candidates,config='config.json',
            scorer='scorer.py',declaration='declaration.txt',closure='closure.json',dry_cells=self.cells)
        self.put('frozen.json',self.manifest);self.commit()
        self.order=[];self.synced=set()

    def launch(self,command,env,check):
        destination=Path(command[command.index('--out')+1]);profile=destination.name
        gate=destination.parent/f'x6-{profile}.json'
        self.assertTrue(gate.exists(),'durable X6 evidence must precede subprocess')
        self.assertIn(gate.stat().st_ino,self.synced)
        self.assertIn(gate.parent.stat().st_ino,self.synced)
        self.assertEqual(runner.load(gate)['status'],'passed')
        self.order.append('launch:'+profile)
        for identity in self.cells:
            if identity.split('/')[0]!=profile:continue
            sid=identity.split('/')[1];directory=destination/sid;directory.mkdir(parents=True)
            Image.new('RGB',(2,2),(80,90,100)).save(directory/(sid+'__webgpu.png'))
            row=records(self.wave,[identity],self.root)[identity]
            for prefix,key in [('cell','descriptor'),('report','report')]:
                (directory/f'{prefix}__webgpu.json').write_text(json.dumps(row[key]))

    def invoke(self,observations):
        # Fake time is shared with the bounded-wait regressions; never sleep in tests.
        from test_x6_wait import WaitTests
        return WaitTests.invoke(self,observations)

    def test_each_profile_gets_fresh_durable_observation_before_launch(self):
        result=self.invoke([reading(),reading()])
        self.assertEqual(result['status'],'complete')
        self.assertEqual(self.order,['observe','launch:'+self.cells[0].split('/')[0],
                                    'observe','launch:'+self.cells[1].split('/')[0]])
        self.assertEqual(len([p for p in (self.output/'standin').glob('x6-*.json') if '-observation-' not in p.name]),2)

    def test_bad_second_profile_spends_and_never_launches_or_retries(self):
        bad=reading();bad['settings']['increaseContrast']['stdout']='1'
        with self.assertRaisesRegex(PermissionError,'X6'):
            self.invoke([reading(),bad])
        self.assertEqual(self.order[:2],['observe','launch:'+self.cells[0].split('/')[0]])
        self.assertEqual(self.order[2:],['observe']*121)
        self.assertEqual(sum(self.sleeps),3600)
        self.assertEqual(self.events(),['begin','failed'])
        self.assertEqual(runner.load(self.output/'standin'/f'x6-{self.cells[1].split("/")[0]}.json')['status'],'deadline-exceeded')
        with self.assertRaisesRegex(PermissionError,'spent'):self.invoke([reading()])

    def test_observer_error_records_unknown_facts_and_spends(self):
        with self.assertRaisesRegex(RuntimeError,'synthetic observation failed'):
            self.invoke([RuntimeError('synthetic observation failed')])
        gate=runner.load(self.output/'standin'/f'x6-{self.cells[0].split("/")[0]}-observation-0001.json')
        self.assertEqual(gate['status'],'observation-error')
        self.assertIsNone(gate['observation']);self.assertIsNone(gate['verdict'])
        self.assertEqual(gate['error']['type'],'RuntimeError')
        self.assertEqual(self.order,['observe']);self.assertEqual(self.events(),['begin','failed'])

    def test_each_raw_fact_can_refuse_even_with_stale_pass_verdict(self):
        variants=[]
        for key,value in [('reduceTransparency','1'),('increaseContrast','1'),
                          ('NSGlassTintAmount','0.4')]:
            bad=reading();bad['settings'][key]['stdout']=value;variants.append((key,bad))
        bad=reading();bad['foreignProcesses']=[['999','1','Chromium']]
        variants.append(('foreign',bad))
        bad=reading();bad['processCensus']['usable']=False;variants.append(('census',bad))
        bad=reading();bad['idle']['stdout']='"HIDIdleTime" = 59999999999'
        variants.append(('idle',bad))
        for name,bad in variants:
            with self.subTest(fact=name):
                self.log=Path(self.tmp.name)/f'{name}-receipt.jsonl'
                self.output=Path(self.tmp.name)/f'{name}-output';self.order=[]
                with self.assertRaisesRegex(PermissionError,'X6'):self.invoke([bad])
                self.assertEqual(self.order,['observe']*121)
                self.assertEqual(sum(self.sleeps),3600)
                self.assertEqual(self.events(),['begin','failed'])

    def test_record_failure_prevents_launch(self):
        real_persist=runner.persist
        def fail(path,value):
            if path.name.startswith('x6-'):raise OSError('synthetic fsync failed')
            return real_persist(path,value)
        with patch.object(runner,'persist',side_effect=fail):
            with self.assertRaisesRegex(OSError,'fsync failed'):self.invoke([reading()])
        self.assertEqual(self.order,['observe']);self.assertEqual(self.events(),['begin','failed'])


class X6FreezeTests(harness.ProductionScopeTests):
    def setUp(self):
        super().setUp()
        # The real source remains outside this temporary repository after guards relocate.
        base=Path(__file__).resolve().parents[5]
        for name in (OBSERVER,DEPENDENCY):self.put(name,(base/name).read_text())
        self.commit()

    def test_required_observer_and_dependency_cannot_be_omitted(self):
        for name in (OBSERVER,DEPENDENCY):
            path=self.root/name;data=path.read_bytes();path.unlink();self.commit()
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'X6'):
                self.freeze()
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);self.commit()

    def test_observer_inputs_are_committed_and_verified_before_begin(self):
        manifest=self.freeze()
        for name in (OBSERVER,DEPENDENCY):self.assertIn(name,manifest['files'])
        self.put('frozen.json',manifest);self.commit()
        self.put(DEPENDENCY,(self.root/DEPENDENCY).read_text()+'\n# changed\n')
        with self.assertRaisesRegex(ValueError,'uncommitted frozen input'):
            runner.verify(self.root,self.wave,self.root/'frozen.json','production')


def load_tests(loader,standard_tests,pattern):
    return unittest.TestSuite(loader.loadTestsFromName(name,cls)
        for cls in (X6Tests,X6FreezeTests) for name in cls.__dict__ if name.startswith('test_'))
