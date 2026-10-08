"""Archived proof semantics only, using synthetic retained files and chain-bound metadata.

The consumer authenticates the completed chain before this API and independently validates both
returned reports afterward. The parity test isolates that already-tested live authority boundary;
it neither grants a fabricated context in production nor replaces proof/artifact checks with mocks.
"""
import copy
import hashlib
import io
import json
from pathlib import Path
import types
import unittest
from unittest.mock import patch
from PIL import Image

HERE=Path(__file__).resolve().parent
P=HERE/'test_admission.py'
F=types.ModuleType('repeat_archive_files');F.__file__=str(P)
exec(compile(P.read_bytes(),str(P),'exec'),F.__dict__)
A=F.A


class ArchivedTests(unittest.TestCase):
    def setUp(self):
        self.f=F.ArtifactTests('test_both_actual_files_and_reports_are_pinned')
        self.f.setUp();self.addCleanup(self.f.doCleanups)
        f=self.f
        for key in ('executionRoot','contract','batchPath'):
            f.context[key]=str(f.root/(key+'.json'));Path(f.context[key]).write_text('{}')
        config=F.doc(f.root/'config.json',{'schema':'synthetic-config'})
        f.context['repeatAdmission']={'config':config}
        self.rows=[dict(profile=f.record['profile'],renderer='css',scene='s',statistic='T1-low')]
        self.binding=dict(executionRootSha256=A.sha(b'{}'),contractSha256=A.sha(b'{}'),
            batchSha256=A.sha(b'{}'),config=config,declaredRows=self.rows,canonicalBackgroundKind='solid')
        self.install(False)

    def install(self, nonidentical):
        f=self.f
        if nonidentical:
            image=Image.open(io.BytesIO(f.png)).convert('RGBA');image.putpixel((0,0),(21,20,20,255))
            stream=io.BytesIO();image.save(stream,format='PNG')
            f.pair['second']['image']=F.pin(f.folder/'s__css__repeat.png',stream.getvalue())
        f.pair.update(deterministic=not nonidentical,repeatNoise=1/(320*200*4) if nonidentical else 0)
        f.record['artifacts']['cell']=F.doc(f.folder/'cell__css.json',dict(
            renderer='css',colorSpace='srgb',deterministic=f.pair['deterministic'],repeatNoise=f.pair['repeatNoise']))
        f.pairpin=F.doc(f.folder/'repeat__css.json',f.pair);f.record['repeatPair']=f.pairpin
        differences={}
        if nonidentical:
            common=dict(units='linear-luma',support={'originalNativeMask':'synthetic'},
                        nativeRepeat={'bar':.002},provenance={'source':'synthetic-own-seven'})
            for name in ('T1-low','T1-fine'):
                differences[name]=dict(common,first=.01,second=.01,difference=0.,limit=.0002)
        self.proof=dict(schema='w50-repeat-admission-1',kind='retained-repeat-pair',reading='first',
            **A.identity(f.record),mode='native-repeat-band' if nonidentical else 'byte-identical',
            manifest=f.pairpin,config=self.binding['config'],pair=copy.deepcopy(f.pair),
            originalArtifacts=copy.deepcopy(f.record['artifacts']),differences=differences,
            declaredStatistics=['T1-low'],rule='every statistic/channel/cut <= 0.1 native repeat bar; never 0.1 B',
            **{k:self.binding[k] for k in ('executionRootSha256','contractSha256','batchSha256')})
        self.repin()

    def repin(self):
        f=self.f
        f.record['repeatAdmission']=F.doc(f.folder/'repeat-admission__css.json',self.proof)

    def read(self):
        f=self.f
        return A.verify_archived_pair(self.binding,f.run,f.record,f.context['output'])

    def test_live_and_archive_share_semantics_without_native_read_or_root_rehash(self):
        f=self.f
        for nonidentical in (False,True):
            self.install(nonidentical)
            with patch.object(A.S,'newbed_pair',side_effect=AssertionError('native reread')), \
                    patch.object(A.S,'canonical_pair',side_effect=AssertionError('native reread')):
                archived=self.read()
                self.assertEqual(archived['proof'],self.proof)
                self.assertEqual(archived['pages'],[f.page,f.page])
                self.assertEqual(archived['envelope'],{'page':f.page})
                guard=types.SimpleNamespace(require_context=lambda context:None)
                with patch.object(A,'authority',return_value=(guard,{},self.rows,{})), \
                        patch.object(A,'validate_reports') as reports, \
                        patch.object(A,'receipt_binding',return_value=self.binding):
                    live=A.verify_receipt(f.context,f.run,f.record)
                self.assertEqual(live,archived['proof']);reports.assert_called_once()
        # Authenticated digests are inputs, not an invitation to revisit a whole current root per cell.
        for key in ('executionRoot','contract','batchPath'):Path(f.context[key]).unlink()
        self.assertEqual(self.read()['proof'],self.proof)

    def test_changed_pins_identity_and_fault_proofs_refuse(self):
        for name,value in [('reading','second'),('contractSha256','f'*64),
                           ('schema','w50-repeat-fault-1'),('declaredStatistics',[])]:
            self.install(False);self.proof[name]=value;self.repin()
            with self.subTest(name=name),self.assertRaises(ValueError):self.read()
        self.install(False)
        Path(self.f.pair['second']['report']['path']).write_text('{}')
        with self.assertRaises(ValueError):self.read()

    def test_omitted_band_or_relaxed_numerical_law_refuses(self):
        self.install(True);del self.proof['differences']['T1-fine'];self.repin()
        with self.assertRaises(ValueError):self.read()
        self.install(True);self.proof['differences']['T1-fine']['limit']=.1;self.repin()
        with self.assertRaises(ValueError):self.read()
        self.install(True);self.proof['differences']['T1-fine']['second']=.011;self.repin()
        with self.assertRaises(ValueError):self.read()

if __name__=='__main__':unittest.main()
