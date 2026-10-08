"""Initializer's schema2 consumer on genuine two-chain source boundaries, synthetic pins only.

This exercises the producer's actual composition index/anchor projection and the live
current_evidence API after an admitted-root boundary. It does not pretend to replay799 real
captures or create/seal a live root; the root's expensive admission remains its own tests.
"""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent


def source(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


E=source(HERE/'execution.py','w50_initializer_composed')
F=source(HERE.parent/'current-analysis-composed/test_analysis.py','w50_actual_composed_fixture')
A=F.source(HERE.parent/'current-analysis-composed/analysis.py','w50_actual_composed_producer')
LIVE=source(HERE.parent/'live-execution/dispatch.py','w50_actual_live_current_api')


class ComposedCurrentConsumer(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name).resolve();self.fit=self.repo/'fit';self.fit.mkdir()
        shutil.copyfile(HERE/'inputs.py',self.fit/'inputs.py')
        def put(name,value):
            path=self.repo/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(value));return {'path':name,'sha256':E._sha(path)}
        self.put=put
        refs=put('original-references.json',{'cells':[]})
        bed=put('manifest.json',{'cells':[]});scenes=put('scenes.json',{'scenes':[]})
        one=put('part-one.json',{'synthetic':'declaration'})
        batch=put('native-batch.json',{'inputs':{'manifest':bed,'scenes':scenes,'declaration':one}})
        raw,manifest,composition=F.topology()
        # Source-owned indexing keeps the actual two roots/results and every original chain pin.
        admitted=A.index_composition(raw,manifest,composition)
        anchors=A.anchors(admitted)
        self.evidence=dict(schema='w50-completed-current-evidence-2',status='EVIDENCE_ONLY',**anchors,
            originals={'references':refs,'scenes':scenes},native={'batch':batch})
        evidence_pin=put('completed-evidence2.json',self.evidence)
        self.config={'schema':'w50-fit-initializer-inputs-1','completedCurrent':evidence_pin,
                     'runtime':{'synthetic':'unused in this consumer test'},'output':'fit/generated'}
        config_pin=put('registered/initializer.json',self.config)
        self.root=dict(schema='w50-g1-execution-root-1',lifecycle='logical-phase-attempts-1',repo=str(self.repo),
            currentComposition=composition,currentEvidence=evidence_pin,references=refs,manifest=bed,partOne=one,
            instruments={'initializer':{'entrypoint':{'path':'fit/execution.py','sha256':'a'*64},'config':config_pin}},
            inputs=[config_pin,evidence_pin,scenes,batch],
            closure={'sources':{'fit/inputs.py':E._sha(self.fit/'inputs.py')}})
        self.prefit={'path':'pre-fit-evidence.json','sha256':'b'*64}
        self.events=[]
        self.dispatcher=types.SimpleNamespace(current_evidence=self.current_evidence)

    def current_evidence(self,path,doc):
        self.events.append('authenticated-composition')
        # Actual public getter; root_doc's full authority was supplied at _admit, not forged
        # by flattening the producer's anchors into a made-up currentInstrument field.
        with patch.object(LIVE,'root_doc',return_value=self.root), \
             patch.object(LIVE,'checked',side_effect=lambda repo,p:E._checked(Path(repo),p)), \
             patch.object(LIVE,'load',side_effect=E._load):
            return LIVE.current_evidence(path,doc)

    def state(self):
        def admitted(path):
            self.events.append('verified-prefit')
            return self.dispatcher,self.root,self.repo,self.prefit
        with patch.object(E,'HERE',self.fit),patch.object(E,'_admit',side_effect=admitted), \
             patch.object(E,'_runtime_spec',return_value=None):
            return E._state('synthetic-live-root')

    def test_schema2_uses_actual_ordered_composition_without_virtual_current_root(self):
        result=self.state()
        self.assertEqual(result['completed'],self.evidence)
        self.assertEqual(self.events,['verified-prefit','authenticated-composition'])
        self.assertEqual(result['completed']['currentInstruments'],self.evidence['currentInstruments'])
        self.assertEqual(result['completed']['currentResults'],self.evidence['currentResults'])
        self.assertEqual(result['completed']['chainPins'],self.evidence['chainPins'])
        self.assertNotIn('currentInstrument',result['completed'])
        self.assertNotIn('currentResults',self.root)

    def test_schema2_is_not_rejected_even_when_config_uses_the_old_filename(self):
        p=self.put('fit/initializer-inputs.json',self.config)
        self.root['inputs'][0]=p;self.root['instruments']['initializer']['config']=p
        self.assertEqual(self.state()['completed']['schema'],'w50-completed-current-evidence-2')

    def test_config_cannot_select_a_different_completed_evidence_pin(self):
        self.config['completedCurrent']=self.put('other-evidence.json',self.evidence)
        p=self.put('registered/initializer.json',self.config)
        self.root['inputs'][0]=p;self.root['instruments']['initializer']['config']=p
        with self.assertRaisesRegex(ValueError,'currentEvidence'):self.state()
        self.assertEqual(self.events,['verified-prefit'])

    def test_no_schema1_or_changed_composition_fallback(self):
        for mutation in ('schema','composition','virtual-root'):
            with self.subTest(mutation=mutation):
                wrong=copy.deepcopy(self.evidence)
                if mutation=='schema':wrong['schema']='w50-completed-current-evidence-1'
                elif mutation=='composition':wrong['currentComposition']={'path':'other','sha256':'9'*64}
                else:wrong['currentInstrument']=wrong['currentInstruments'][0]
                with patch.object(self.dispatcher,'current_evidence',return_value=wrong):
                    with self.assertRaises(ValueError):self.state()

    def test_real_composition_boundary_refuses_reordered_or_reassigned_chains(self):
        for mutation in ('root-order','result-order','member-owner'):
            raw,manifest,composition=F.topology()
            if mutation=='root-order':raw['roots'].reverse()
            elif mutation=='result-order':raw['resultDocuments'].reverse()
            else:raw['members'][0]['instrument']=raw['roots'][1]['pin']
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                A.index_composition(raw,manifest,composition)


if __name__=='__main__':unittest.main()
