"""Synthetic PNG/provenance tests; no sealed native reader or real captures execute."""
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('native_evidence',HERE/'native_evidence.py')
N=importlib.util.module_from_spec(spec);spec.loader.exec_module(N)


def png(width=512,height=384):
    def chunk(name,data):return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+\
        chunk(b'IDAT',zlib.compress((b'\0'+b'\x10\x10\x10'*width)*height))+chunk(b'IEND',b'')


class NativeEnvelope(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name);self.export=self.repo/'export';self.export.mkdir()
        self.row=dict(profile='apple-macos-27.0-1x-dark-standard-glass0.25',renderer='webgpu',
            scene='cell-grey-004-s096__rest',statistic='deep8-channel-median',role='calibration',
            nativeIdentity='apple-macos-27.0-1x-dark-standard-glass0.25/cell-grey-004-s096__rest',
            referenceIdentity='apple-macos-27.0-1x-dark-standard-glass0.25/ref-grey-004__rest',
            support='ORIGINAL supplied path prose',native=[1,2,3])
        self.declaration=self.put('declaration.json',{'synthetic':'declaration'})
        self.manifest=self.put('manifest.json',{'synthetic':'manifest'})
        rows=[];runs=[]
        for i in (1,2,3):
            rel=f'pass/run-{i}/{self.row["profile"]}/{self.row["scene"]}.png'
            p=self.export/rel;p.parent.mkdir(parents=True);p.write_bytes(png())
            evidence=dict(path=rel,sha256=N.sha(p),roles=['calibration'],kind='frame',cell=self.row['nativeIdentity'],run=i,
                declarationSha256=self.declaration['sha256'],manifestSha256='a'*64,
                native={'sceneId':self.row['scene'],'file':self.row['nativeIdentity']+'.png','width':512,'height':384})
            rows.append(evidence);runs.append(dict(run=i,evidence=copy.deepcopy(evidence),dependency=self.row['referenceIdentity'],readings={}))
        dep_path=self.export/'reference.png';dep_path.write_bytes(png())
        dependency=dict(path='reference.png',sha256=N.sha(dep_path),roles=['calibration'],kind='frame',
            cell=self.row['referenceIdentity'],run=1,declarationSha256=self.declaration['sha256'],manifestSha256='a'*64,
            native={'sceneId':self.row['referenceIdentity'].split('/')[-1],
                    'file':self.row['referenceIdentity']+'.png','width':512,'height':384})
        self.index={'schema':'w50-role-archive-1','files':rows+[dependency]}
        self.index_pin=self.put('export/index.json',self.index)
        self.report=dict(schema='w50-native-role-read-1',role='calibration',indexSha256=self.index_pin['sha256'],
            declarationSha256=self.declaration['sha256'],canvas={'width':512,'height':384},ready=True,stops=[],
            dependencies=[{'id':self.row['referenceIdentity'],'evidence':dependency}],cells=[dict(profile=self.row['profile'],scene=self.row['scene'],role='calibration',id=self.row['nativeIdentity'],
                reference=self.row['referenceIdentity'],runs=runs,statistics={self.row['statistic']:{'value':[1,2,3]}})])
        self.native_read=self.put_gz('native-read.json.gz',self.report)
        self.export_record={'role':'calibration','root':str(self.export),'indexSha256':self.index_pin['sha256']}
        self.batch=self.put('batch.json',{'schema':'w50-native-read-batch-1','inputs':{
            'declaration':self.declaration,'manifest':self.manifest},'exports':[self.export_record]})
        self.envelope={k:self.row[k] for k in ('profile','scene','nativeIdentity','referenceIdentity','role','support','statistic')}
        self.envelope.update(schema='w50-native-three-run-evidence-1',runs=copy.deepcopy(rows),
            nativeRead=self.native_read,nativeBatch=self.batch,nativeExport=self.export_record)
        self.envelope_pin=self.put('envelope.json',self.envelope)

    def put(self,name,value):
        path=self.repo/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value)+'\n')
        return {'path':str(path),'sha256':N.sha(path)}

    def put_gz(self,name,value):
        path=self.repo/name;path.write_bytes(gzip.compress(json.dumps(value).encode(),mtime=0))
        return {'path':str(path),'sha256':N.sha(path)}

    def check(self):
        checker=N.NativeEvidence(self.repo,self.manifest)
        checker.validate(self.row,self.envelope_pin)
        checker.finish()

    def test_completed_reference_uses_envelope_and_preserves_original_support(self):
        spec=importlib.util.spec_from_file_location('prefit_native',HERE/'prefit.py')
        P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
        original={k:v for k,v in self.row.items() if k!='native'}
        original.update(nativeEvidence=None,currentEvidence=None,currentMetadata=None,B=None,status='UNMEASURED',
                        currentDocumentPair={'active.dark':'a'*64,'receded.dark':'b'*64},historical=[])
        current=self.repo/'current.png';current.write_bytes(png())
        completed={**original,'native':[1,2,3],'current':[2,3,4],'B':1,'status':'MEASURED',
                   'nativeEvidence':self.envelope_pin,'currentEvidence':{'path':str(current),'sha256':N.sha(current)}}
        refs={'inputs':{'bed':self.manifest},'cells':[original]}
        P.validate_completion(refs,{'inputs':refs['inputs'],'cells':[completed]},[],self.repo)
        completed['nativeEvidence']=self.envelope['runs']
        with self.assertRaises(ValueError):P.validate_completion(refs,{'inputs':refs['inputs'],'cells':[completed]},[],self.repo)

    def test_actual_additive_producer_schema_round_trips_through_consumer(self):
        producer_path=HERE.parents[1]/'2026-10-08-w50-g1-fit/current-analysis/native_evidence.py'
        spec=importlib.util.spec_from_file_location('actual_native_envelope_producer',producer_path)
        producer=importlib.util.module_from_spec(spec);spec.loader.exec_module(producer)
        provenance={name:copy.deepcopy(self.envelope[name]) for name in ('nativeRead','nativeBatch','nativeExport')}
        for name in ('nativeRead','nativeBatch'):
            provenance[name]['path']=str(Path(provenance[name]['path']).relative_to(self.repo))
        result=producer.envelope(self.row,self.report['cells'][0],provenance)
        self.envelope_pin=self.put('producer-envelope.json',result)
        self.check()

    def test_three_native_runs_are_bound_without_replacing_original_support(self):
        self.check();self.assertEqual(self.envelope['support'],'ORIGINAL supplied path prose')

    def test_missing_run_changed_dependency_support_and_identity_refuse(self):
        for field,value in [('runs',self.envelope['runs'][:2]),('support','deep8'),('nativeIdentity','other'),('role','blind')]:
            original=copy.deepcopy(self.envelope);self.envelope[field]=value
            self.envelope_pin=self.put('envelope.json',self.envelope)
            with self.subTest(field=field),self.assertRaises(ValueError):self.check()
            self.envelope=original

    def test_repeated_nested_run_cannot_impersonate_three_ordered_runs(self):
        self.check()
        runs=self.report['cells'][0]['runs']
        # Each nested record is authentic run-1 archive evidence; only its placement under
        # the outer run-2/run-3 labels is false. Re-pin the report/envelope, not the archive.
        first=copy.deepcopy(runs[0]['evidence'])
        for run in runs:run['evidence']=copy.deepcopy(first)
        self.envelope['runs']=[r['evidence'] for r in runs]
        self.envelope['nativeRead']=self.put_gz('native-read.json.gz',self.report)
        self.envelope_pin=self.put('envelope.json',self.envelope)
        with self.assertRaisesRegex(ValueError,'run'):self.check()

    def test_report_index_and_actual_png_must_agree(self):
        p=self.export/self.index['files'][0]['path'];p.write_bytes(b'not a PNG')
        with self.assertRaises(ValueError):self.check()

    def test_document_as_png_is_rejected_even_if_all_hashes_are_recomputed(self):
        p=self.export/self.index['files'][0]['path'];p.write_text('{"profileKey":"pretend image"}')
        digest=N.sha(p)
        self.index['files'][0]['sha256']=digest
        self.report['cells'][0]['runs'][0]['evidence']['sha256']=digest
        self.envelope['runs'][0]['sha256']=digest
        self.index_pin=self.put('export/index.json',self.index)
        self.report['indexSha256']=self.index_pin['sha256']
        self.envelope['nativeRead']=self.put_gz('native-read.json.gz',self.report)
        self.export_record['indexSha256']=self.index_pin['sha256']
        self.envelope['nativeBatch']=self.put('batch.json',{'schema':'w50-native-read-batch-1','inputs':{
            'declaration':self.declaration,'manifest':self.manifest},'exports':[self.export_record]})
        self.envelope_pin=self.put('envelope.json',self.envelope)
        with self.assertRaisesRegex(ValueError,'PNG'):self.check()

    def test_scalar_or_one_run_is_not_the_native_aggregate(self):
        self.row['native']=[1,2,4]
        with self.assertRaises(ValueError):self.check()

    def test_blind_native_cannot_be_opened_via_exposed_batch_envelope(self):
        self.row['role']='blind'
        with self.assertRaises(ValueError):self.check()


if __name__=='__main__':unittest.main()
