"""Synthetic retained artifacts only; never historical captures or native reports."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from PIL import Image

P=Path(__file__).with_name('admission.py')
A=types.ModuleType('repeat_admission_test'); A.__file__=str(P)
exec(compile(P.read_bytes(),str(P),'exec'),A.__dict__)


def pin(path, raw):
    path.write_bytes(raw)
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest())


def doc(path,value): return pin(path,(json.dumps(value)+'\n').encode())


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve(); self.folder=self.root/'capture'/'p'/'s'; self.folder.mkdir(parents=True)
        self.context={'output':str(self.root)}
        self.run={'captureRoot':str(self.root/'capture'),'profile':'p','renderer':'css',
                  'candidate':{'path':'candidate','sha256':'a'*64},'sceneSource':'canonical','scenes':['s']}
        buf=io.BytesIO(); Image.new('RGBA',(320,200),(20,20,20,255)).save(buf,format='PNG')
        self.png=buf.getvalue(); self.page={'actual':'synthetic first page'}
        self.pair=dict(schema=1,kind='w50-retained-repeat-pair',reading='first',scene='s',renderer='css',
                      deterministic=True,repeatNoise=0)
        for side,suffix in [('first',''),('second','__repeat')]:
            self.pair[side]={'image':pin(self.folder/f's__css{suffix}.png',self.png),
                            'report':doc(self.folder/f'page__css__{side}.json',self.page)}
        self.record={k:copy.deepcopy(self.run[k]) for k in ('profile','renderer','candidate','sceneSource')}
        self.record.update(scene='s',lane='candidate',artifacts={'png':self.pair['first']['image'],
            'report':doc(self.folder/'report__css.json',{'page':self.page}),
            'cell':doc(self.folder/'cell__css.json',{'renderer':'css','colorSpace':'srgb',
                                                   'deterministic':True,'repeatNoise':0})})
        self.pairpin=doc(self.folder/'repeat__css.json',self.pair)
        # Real profiles are structurally checked by admission; pure artifact checking uses explicit scale.
        self.record['profile']=self.run['profile']='apple-macos-27.0-1x-dark-standard-glass0.25'
        target=self.root/'capture'/self.run['profile']; self.folder.parent.rename(target)
        self.folder=target/'s'
        for member in ('first','second'):
            for key in ('image','report'):
                self.pair[member][key]['path']=str(self.folder/Path(self.pair[member][key]['path']).name)
        for key in self.record['artifacts']:
            self.record['artifacts'][key]['path']=str(self.folder/Path(self.record['artifacts'][key]['path']).name)
        self.pairpin=doc(self.folder/'repeat__css.json',self.pair)

    def test_both_actual_files_and_reports_are_pinned(self):
        result=A.read_pair(self.context,self.run,self.record,self.pairpin)
        self.assertTrue(result['identical'])
        Path(self.pair['second']['report']['path']).write_text('{}')
        with self.assertRaises(ValueError): A.read_pair(self.context,self.run,self.record,self.pairpin)

    def test_second_cannot_alias_first_or_escape_real_output(self):
        self.pair['second']['image']=self.pair['first']['image']
        changed=doc(self.folder/'repeat__css.json',self.pair)
        with self.assertRaises(ValueError): A.read_pair(self.context,self.run,self.record,changed)

    def test_original_deterministic_false_is_never_relabelled(self):
        self.pair['deterministic']=False
        changed=doc(self.folder/'repeat__css.json',self.pair)
        with self.assertRaises(ValueError): A.read_pair(self.context,self.run,self.record,changed)

    def test_actual_second_geometry_is_checked_not_its_filename(self):
        buf=io.BytesIO(); Image.new('RGBA',(319,200)).save(buf,format='PNG')
        self.pair['second']['image']=pin(self.folder/'s__css__repeat.png',buf.getvalue())
        self.pair['deterministic']=False
        changed=doc(self.folder/'repeat__css.json',self.pair)
        with self.assertRaises(ValueError): A.read_pair(self.context,self.run,self.record,changed)

    def test_fault_receipt_survives_refusal_and_is_never_an_admission(self):
        # Isolate write-once orchestration; artifact validation above uses actual PNG/report bytes.
        # The raised comparison represents a measured synthetic fault, not a mocked success.
        from unittest.mock import patch
        from types import SimpleNamespace
        self.context['executionRoot']=str(self.root/'root.json')
        self.context['contract']=str(self.root/'contract.json')
        self.context['batchPath']=str(self.root/'batch.json')
        for key in ('executionRoot','contract','batchPath'):
            Path(self.context[key]).write_text('{}')
        Path(self.context['contract']+'.started.json').write_text('{"synthetic":true}')
        config_pin=doc(self.root/'config.json',{'schema':'synthetic'})
        self.context['repeatAdmission']={'config':config_pin}
        dispatcher=SimpleNamespace(require_context=lambda context:None)
        rows=[dict(statistic='T1-full-silhouette')]
        retained=A.read_pair(self.context,self.run,self.record,self.pairpin)
        try:
            A.C.compare_statistics(
                {'x':dict(value=0,units='encoded-luma-codes',support='deep8',repeat={'bar':.5},provenance={'synthetic':True})},
                {'x':dict(value=.2,units='encoded-luma-codes',support='deep8',repeat={'bar':.5},provenance={'synthetic':True})})
        except A.C.InstrumentFault as error:
            fault=error
        with patch.object(A,'authority',return_value=(dispatcher,{},rows,{})), \
                patch.object(A,'validate_reports'), patch.object(A,'proof_body',side_effect=fault):
            with self.assertRaises(A.C.InstrumentFault):
                A.admit_pair(self.context,self.run,self.record,self.pairpin)
        fault_path=retained['folder']/'repeat-fault__css.json'
        proof=json.loads(fault_path.read_bytes())
        self.assertEqual(proof['status'],'INSTRUMENT_FAULT')
        self.assertEqual(proof['differences']['x']['difference'],.2)
        self.assertEqual(proof['pair'],self.pair)
        self.assertIn('claim',proof)
        self.assertFalse((retained['folder']/'repeat-admission__css.json').exists())
        self.record['repeatPair']=self.pairpin
        self.record['repeatAdmission']={'path':str(fault_path),'sha256':hashlib.sha256(fault_path.read_bytes()).hexdigest()}
        with patch.object(A,'authority',return_value=(dispatcher,{},rows,{})),patch.object(A,'validate_reports'):
            with self.assertRaises(A.C.InstrumentFault):A.verify_receipt(self.context,self.run,self.record)

    def test_no_context_cannot_mint_proof_even_for_identical_bytes(self):
        with self.assertRaises(ValueError): A.admit_pair(self.context,self.run,self.record,self.pairpin)

if __name__=='__main__':unittest.main()
