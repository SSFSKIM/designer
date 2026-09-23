#!/usr/bin/env python3
"""Exercise the procedural holdout boundary on probe-role cells (§5.174)."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


class WaveBoundary(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('wave_boundary', HERE/'wave.py')
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.scenes = {'components': {'glass': {'kind':'capsule-circular','size':[120,44]},
                                      'empty':{'kind':'none'}},
            'scenes':[{'id':x,'component':'empty' if x=='control' else 'glass'}
                      for x in ['cal','val','held','control']],
            'profiles':[{'key':'profile','scenes':'all'}],
            'split':{'probe':['cal','val','held','control'],'calibration':[],
                     'validation':[],'holdout':[]}}
        self.split = {'calibration':['cal','control'],'validation':['val'],'holdout':['held']}
        self.put('scenes.json',self.scenes); self.put('split.json',self.split)
        self.pins={'scenesSha256':sha(self.root/'scenes.json'),'splitSha256':sha(self.root/'split.json')}
        self.put('pins.json',self.pins)
        entries=[]
        for cell,role in [('cal','calibration'),('val','validation'),('held','holdout')]:
            for kind in ['png','crop','statistics']:
                path=f'{role}/{cell}.{kind}'
                self.put(path,{'secret':cell})
                entries.append({'cell':'profile/'+cell,'kind':kind,'path':path,
                                'sha256':sha(self.root/path)})
        self.put('inventory.json',{'entries':entries,'scenesSha256':self.pins['scenesSha256'],
                                   'splitSha256':self.pins['splitSha256']})

    def put(self,name,value):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(value));return p

    def wave(self): return self.mod.Wave(self.root/'scenes.json',self.root/'split.json',self.root/'pins.json')

    def test_probe_role_never_bypasses_identification_holdout(self):
        wave=self.wave(); reader=wave.reader(self.root)
        self.assertEqual(json.loads(reader.read('profile/cal','statistics')),{'secret':'cal'})
        for kind in ['png','crop','statistics']:
            # Missing files prove refusal precedes payload access rather than
            # deserialising a secret and deciding not to print it afterwards.
            (self.root/f'holdout/held.{kind}').unlink()
            with self.assertRaisesRegex(PermissionError,'holdout'):
                reader.read('profile/held',kind)
        with self.assertRaisesRegex(PermissionError,'holdout'):
            wave.select(['holdout'])
        self.assertEqual(wave.launch_scenes(),['cal','val'])
        self.assertNotIn('control',wave.launch_scenes())

    def test_membership_and_both_hashes_fail_closed(self):
        for replacement in [
            {'calibration':['cal','control','held'],'validation':['val'],'holdout':['held']},
            {'calibration':['cal'],'validation':['val'],'holdout':['held']},
            {'calibration':['cal','control','phantom'],'validation':['val'],'holdout':['held']}]:
            self.put('split.json',replacement)
            self.put('pins.json',{**self.pins,'splitSha256':sha(self.root/'split.json')})
            with self.assertRaisesRegex(ValueError,'membership'):self.wave()
        self.put('split.json',self.split);self.put('pins.json',self.pins)
        with (self.root/'scenes.json').open('a') as f:f.write(' ')
        with self.assertRaisesRegex(ValueError,'scenes.*hash'):self.wave()
        self.put('scenes.json',self.scenes)
        with (self.root/'split.json').open('a') as f:f.write(' ')
        with self.assertRaisesRegex(ValueError,'split.*hash'):self.wave()

    def test_reporting_exposes_only_holdout_inventory_not_payload(self):
        reader=self.wave().reader(self.root)
        for kind in ['png','crop','statistics']:(self.root/f'holdout/held.{kind}').write_text('INVALID JSON SECRET')
        report=reader.report_inventory()
        self.assertNotIn('SECRET',json.dumps(report))
        self.assertEqual(len(report),9)
        self.assertTrue(all(set(r)=={'cell','kind','sha256','path'} for r in report))
        bad=json.loads((self.root/'inventory.json').read_text())
        bad['entries'][0]['path']='holdout/held.png';self.put('inventory.json',bad)
        with self.assertRaisesRegex(ValueError,'placement'):self.wave().reader(self.root)
        bad['scenesSha256']='wrong generation';self.put('inventory.json',bad)
        with self.assertRaisesRegex(ValueError,'generation'):self.wave().reader(self.root)

    def test_publication_keeps_holdout_diagnostics_out_of_public_manifest(self):
        spec=importlib.util.spec_from_file_location('materializer',HERE/'materialize-producer.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        source=self.root/'materialized';source.mkdir()
        fixtures=[]
        for sid in ['cal','val','held','control']:
            (source/(sid+'.png')).write_bytes(b'pixel payload')
            fixtures.append(dict(sceneId=sid,file=sid+'.png',fixtureSet='probe',
                captureMethod='screencapturekit',materialRendered=True,deterministic=True,
                presentedActive=True,chromaShift=199,diagnostic='TOP_SECRET_DIAGNOSTIC'))
        (source/'manifest.json').write_text(json.dumps(dict(
            profiles=[dict(profileKey='profile',fixtures=fixtures)],
            bedProvenance=[dict(stateFrequencies='TOP_SECRET_DIAGNOSTIC')],backgrounds={})))
        empty=self.root/'empty';empty.mkdir();(empty/'manifest.json').write_text('{"profiles": []}')
        with self.assertRaisesRegex(ValueError,'membership'):
            module.partition(empty,self.root/'must-not-publish',self.wave())
        target=self.root/'published';module.partition(source,target,self.wave())
        public=json.loads((target/'manifest.json').read_text())
        held=next(f for f in public['profiles'][0]['fixtures'] if f['sceneId']=='held')
        self.assertNotIn('diagnostic',held);self.assertNotIn('chromaShift',held)
        self.assertNotIn('bedProvenance',public)
        reader=self.wave().reader(target)
        with self.assertRaises(PermissionError):reader.read('profile/held','statistics')
        with self.assertRaises(PermissionError):reader.read('profile/held','png')
        self.assertNotIn('TOP_SECRET',json.dumps(reader.report_inventory()))

    def test_receipt_refuses_another_inventory_under_the_same_declaration(self):
        wave=self.wave()
        other=json.loads((self.root/'inventory.json').read_text())
        other['generationNote']='another generation with the same scenes and split'
        self.put('other/inventory.json',other)
        config={'scenes':wave.scenes_sha,'split':wave.split_sha,
                'generation':[sha(self.root/'inventory.json')],
                'instrument':'i','closure':'c','candidate':'candidate'}
        with self.mod.Receipt(self.root/'generation-receipt.jsonl',config).expose() as token:
            reader=wave.reader(self.root,roles=['holdout'],authorization=token)
            self.assertEqual(json.loads(reader.read('profile/held','statistics')),{'secret':'held'})
            with self.assertRaisesRegex(PermissionError,'generation'):
                wave.reader(self.root/'other',roles=['holdout'],authorization=token)
        # A repeat archive and a materialized archive may be frozen together;
        # only the explicitly named inventory hashes become readable.
        config['generation'].append(sha(self.root/'other/inventory.json'))
        for kind in ['png','crop','statistics']:
            self.put('other/holdout/held.'+kind,{'secret':'held'})
        with self.mod.Receipt(self.root/'two-inventory-receipt.jsonl',config).expose() as token:
            for root in [self.root,self.root/'other']:
                reader=wave.reader(root,roles=['holdout'],authorization=token)
                self.assertEqual(json.loads(reader.read('profile/held','statistics')),{'secret':'held'})


    def test_receipt_spends_attempt_before_payload_and_refuses_changed_candidate(self):
        wave=self.wave(); log=self.root/'receipt.jsonl'
        config={'scenes':self.pins['scenesSha256'],'split':self.pins['splitSha256'],
                'generation':[sha(self.root/'inventory.json')],'instrument':'instrument-a','closure':'closure-a',
                'candidate':{'family':'affine','coefficients':[1,2]}}
        receipt=self.mod.Receipt(log,config)
        with self.assertRaisesRegex(RuntimeError,'intentional'):
            with receipt.expose() as token:
                reader=wave.reader(self.root,roles=['holdout'],authorization=token)
                self.assertEqual(json.loads(reader.read('profile/held','statistics')),{'secret':'held'})
                raise RuntimeError('intentional failure after exposure')
        self.assertEqual([json.loads(l)['event'] for l in log.read_text().splitlines()],['begin','failed'])
        with self.assertRaisesRegex(PermissionError,'spent'):
            with receipt.expose():pass
        changed={**config,'candidate':{'family':'affine','coefficients':[1,3]}}
        with self.assertRaisesRegex(PermissionError,'spent'):
            with self.mod.Receipt(log,changed).expose():pass
        with self.assertRaisesRegex(PermissionError,'inactive'):
            wave.reader(self.root,roles=['holdout'],authorization=token)


if __name__ == '__main__':unittest.main()
