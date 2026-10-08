"""Prospective config selection over disposable source trees; no real evidence is opened."""
import copy
import json
from pathlib import Path
import types
import tempfile
import unittest

HERE=Path(__file__).resolve().parent


def module(path,name):
    value=types.ModuleType(name);value.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),value.__dict__)
    return value


T=module(HERE/'test_run.py','composed_reference_run_fixture')


class ComposedRunTests(unittest.TestCase):
    def fixture(self,directory,selection):
        repo,home,batch,path=T.RunTests().fixture(directory)
        config=json.loads(path.read_bytes());config.update(selection);T.write(path,config)
        doc=json.loads(batch.read_bytes());doc['inputs']['config']['sha256']=T.sha(path);T.write(batch,doc)
        return module(home/'run.py','composed_reference_entry'),repo,home,batch

    def test_composition_config_is_admitted_prospectively_without_opening_results(self):
        with tempfile.TemporaryDirectory() as td:
            pin={'path':'not-yet-read/composition.json','sha256':'a'*64}
            entry,_,_,batch=self.fixture(td,{'currentComposition':pin})
            _,config,rows,_=entry.batch_metadata(batch)
            self.assertEqual(config['currentComposition'],pin)
            self.assertEqual(len(rows),1)

    def test_single_root_config_remains_the_same_shape(self):
        with tempfile.TemporaryDirectory() as td:
            config={'instrument':{'path':'old/root.json','sha256':'b'*64},
                    'results':[{'path':'old/result.json','sha256':'c'*64}]}
            entry,_,_,batch=self.fixture(td,{'currentCompletion':config})
            self.assertEqual(entry.batch_metadata(batch)[1]['currentCompletion'],config)

    def test_unknown_absolute_partial_or_dual_completion_config_refuses(self):
        pin={'path':'composition.json','sha256':'a'*64}
        for selection in ({'currentComposition':{'path':'/absolute/composition.json','sha256':'a'*64}},
                          {'currentComposition':{'path':'composition.json'}},
                          {'currentComposition':{**pin,'root':'fake'}},
                          {'currentComposition':pin,'currentCompletion':None},
                          {'currentComposition':pin,'currentCompletion':{'instrument':pin,'results':[pin]}}):
            with self.subTest(selection=selection),tempfile.TemporaryDirectory() as td:
                entry,_,_,batch=self.fixture(td,selection)
                with self.assertRaises(ValueError):entry.batch_metadata(batch)

    def test_execute_selects_composed_projection_without_changing_reader_config_or_original_rows(self):
        with tempfile.TemporaryDirectory() as td:
            entry,_,_,_=self.fixture(td,{})
            rows=[dict(profile='p',renderer='webgpu',scene='scene',statistic='T1-low',role='gate',
                       currentEvidence=None,currentMetadata=None,native=.2,current=.3,B=.01,historical=[])]
            before=copy.deepcopy(rows);projected=copy.deepcopy(rows)
            projected[0].update(currentEvidence={'path':'synthetic.png','sha256':'a'*64},
                                currentMetadata={'path':'synthetic.json','sha256':'b'*64})
            composition={'path':'composition.json','sha256':'c'*64};calls=[]
            class Completion:
                def complete_current_projection(self,repo,original,pin,*,scenes):
                    calls.append(('projection',original,pin,scenes))
                    return dict(schema='w50-admitted-current-reference-projection-2',originalRows=original,rows=projected)
            class Reader:
                def json_pin(self,pin):return {'scenes':'synthetic source declaration'}
                def read_references(self,selected,config):
                    calls.append(('reader',selected,config));return {'partitions':{'gate':[]}}
            def source(name,path):
                if path.name=='canonical.py':return Reader()
                if path.name=='composed_completion.py':return Completion()
                raise AssertionError('Wrong completion implementation selected')
            entry.source=source
            config={'currentComposition':composition,'scenes':{'path':'scenes','sha256':'d'*64},
                    'fixtureRoot':'/synthetic/fixtures','w29':{'root':'/synthetic/w29'},'w43':{'root':'/synthetic/w43'}}
            report=entry.execute({'inputs':{},'selectedKeys':[]},config,rows,{'batch':{},'contract':{},'sources':{}},
                                 'e'*64,Path(td)/'output.json')
            self.assertEqual(rows,before)
            self.assertEqual(calls,[('projection',before,composition,{'scenes':'synthetic source declaration'}),
                                    ('reader',projected,config)])
            self.assertEqual(report['originalReferences'],before)
            self.assertEqual(report['currentArtifactProjection']['rows'],projected)


if __name__=='__main__':unittest.main()
