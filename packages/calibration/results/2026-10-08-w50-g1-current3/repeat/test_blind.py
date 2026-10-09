"""Exercise real one-shot preparation/dispatcher code on an entirely synthetic archive."""
import copy
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
FIT=HERE.parents[1]/'2026-10-08-w50-g1-fit'


def source(path,name):
    m=types.ModuleType(name);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
    return m


S=source(HERE/'sources.py','repeat_blind_sources')
F=source(FIT/'exposure/test_prepare.py','repeat_blind_fixture')


class BlindTests(unittest.TestCase):
    def setUp(self):
        old=sys.modules.get('w50_g1_dispatch')
        def restore():
            if old is None: sys.modules.pop('w50_g1_dispatch',None)
            else: sys.modules['w50_g1_dispatch']=old
        self.addCleanup(restore)
        self.fixture=F.ExposureTests('test_one_shot_blind_read_keeps_original_roles_real_supports_and_hash_pinned_fixtures')
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.artifacts=self.fixture.prepare()
        self.report=json.loads(Path(self.artifacts['nativeRead']['path']).read_bytes())
        cell=next(c for c in self.report['cells'] if c['family']=='structured')
        self.row=dict(profile=cell['profile'],renderer='webgpu',scene=cell['scene'],role='blind',
            statistic='T1-full-silhouette',nativeIdentity=cell['id'],referenceIdentity=cell['reference'])
        self.run=dict(self.fixture.run,nativeExposureConfig=self.fixture.pin(self.fixture.config))

    def test_actual_preparation_chain_supplies_original_blind_supports(self):
        cell,dependency,export,provenance=S.blind_cell(self.fixture.context,self.run,self.row,self.fixture.scenes)
        self.assertEqual(cell['role'],'blind')
        self.assertEqual([r['run'] for r in cell['runs']],[1,2,3])
        self.assertEqual(provenance['nativeExposure'],self.artifacts['artifactManifest'])
        self.assertEqual(dependency['cell'],cell['reference'])
        self.assertEqual(export,Path(self.artifacts['export']['path']))

    def test_foreign_context_refuses_before_artifact_or_report_open(self):
        foreign=dict(self.fixture.context,phase='fit')
        with patch.object(S.R,'file_pin',side_effect=AssertionError('premature artifact open')):
            with self.assertRaises(ValueError):S.blind_cell(foreign,self.run,self.row,self.fixture.scenes)

    def test_same_report_with_changed_dispatcher_claim_is_not_authority(self):
        claim_path=Path(self.artifacts['claim']['path'])
        claim=json.loads(claim_path.read_bytes())
        claim['batch']['path']=str(self.fixture.base/'another-batch.json')
        claim_path.write_text(json.dumps(claim))
        with self.assertRaises(ValueError):
            S.blind_cell(self.fixture.context,self.run,self.row,self.fixture.scenes)

    def test_blind_report_cannot_substitute_foreign_archive_index(self):
        index=Path(self.fixture.archive)/'index.json'
        doc=json.loads(index.read_bytes());doc['files'][0]['sha256']='f'*64
        index.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            S.blind_cell(self.fixture.context,self.run,self.row,self.fixture.scenes)

if __name__=='__main__':unittest.main()
