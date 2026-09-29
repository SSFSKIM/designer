"""Cumulative exposure waiting budget; clock and OS facts are synthetic."""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import runner
from test_x6 import X6Tests, reading


class WaitTests(X6Tests):
    def invoke(self,observations,mutate_sleep=None,capture_seconds=0):
        values=iter(observations);last=None;self.clock=0;self.sleeps=[]
        def observe():
            nonlocal last
            self.order.append('observe')
            last=next(values,last)
            if isinstance(last,Exception):raise last
            return deepcopy(last)
        def sleep(seconds):
            self.sleeps.append(seconds);self.clock+=seconds
            if mutate_sleep:mutate_sleep()
        real_run=runner.subprocess.run;real_fsync=os.fsync
        def fsync(fd):real_fsync(fd);self.synced.add(os.fstat(fd).st_ino)
        def process(command,**kwargs):
            if command[0]=='git':return real_run(command,**kwargs)
            result=self.launch(command,**kwargs);self.clock+=capture_seconds;return result
        def capture(request):
            with patch.object(runner,'observe_x6',side_effect=observe), \
                    patch.object(runner.subprocess,'run',side_effect=process):
                return runner.capture_web(request)
        import time
        with patch.object(time,'monotonic',side_effect=lambda:self.clock), \
                patch.object(time,'sleep',side_effect=sleep), \
                patch.object(runner.os,'fsync',side_effect=fsync):
            return self.run_exposure(capture=capture)

    def test_failed_facts_wait_then_capture_once_with_all_observations_durable(self):
        bad=reading();bad['idle']['stdout']='"HIDIdleTime" = 0'
        result=self.invoke([bad,reading(),reading()])
        self.assertEqual(result['status'],'complete');self.assertEqual(self.sleeps,[30])
        self.assertEqual(self.order,['observe','observe','launch:'+self.cells[0].split('/')[0],
                                    'observe','launch:'+self.cells[1].split('/')[0]])
        logs=sorted((self.output/'standin').glob('x6-*-observation-*.json'))
        self.assertEqual(len(logs),3)
        self.assertEqual([runner.load(p)['status'] for p in logs],['waiting','passed','passed'])

    def test_budget_is_shared_between_profiles_and_excludes_capture_time(self):
        bad=reading();bad['settings']['increaseContrast']['stdout']='1'
        # First profile spends1800s waiting; second may spend only remaining1800s.
        with self.assertRaisesRegex(PermissionError,'budget'):
            self.invoke([bad]*60+[reading()]+[bad],capture_seconds=7200)
        self.assertEqual(sum(self.sleeps),3600)
        self.assertEqual(len([x for x in self.order if x.startswith('launch:')]),1)
        self.assertEqual(self.events(),['begin','failed'])
        with self.assertRaisesRegex(PermissionError,'spent'):self.invoke([reading()])

    def test_snapshot_mutation_while_waiting_blocks_launch(self):
        bad=reading();bad['idle']['stdout']='"HIDIdleTime" = 0'
        def mutate():self.put('parameters.json',{'gain':999})
        with self.assertRaisesRegex(ValueError,'frozen|uncommitted'):
            self.invoke([bad,reading()],mutate_sleep=mutate)
        self.assertFalse(any(x.startswith('launch:') for x in self.order))
        self.assertEqual(self.events(),['begin','failed'])

    def test_prebegin_bad_facts_never_open_receipt_or_wait(self):
        bad=reading();bad['settings']['increaseContrast']['stdout']='1'
        # Relocate only preflight's manifest verifier; the actual production branch
        # must gate before any Receipt construction. No production log is passed.
        with patch.object(runner,'verify',return_value=self.manifest), \
                patch.object(runner,'observe_x6',return_value=bad), \
                patch.object(runner.boundary,'Receipt') as receipt:
            with self.assertRaisesRegex(PermissionError,'X6'):
                runner._run(self.root,self.wave,self.root/'frozen.json',self.log,self.output,
                            self.capture,self.project,self.score,'production')
            receipt.assert_not_called()
        self.assertFalse(self.log.exists())
        row=runner.load(self.output/'x6-prebegin.json')
        self.assertEqual(row['status'],'refused')


def load_tests(loader,standard_tests,pattern):
    return unittest.TestSuite(loader.loadTestsFromName(name,WaitTests)
                             for name in WaitTests.__dict__ if name.startswith('test_'))
