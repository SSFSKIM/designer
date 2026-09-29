"""Blind web membership and descriptor checks, with no native payload or browser."""
import copy
from contextlib import contextmanager, ExitStack
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import blind

@contextmanager
def scratch_metadata():
    """Keep live metadata mutation and all seal writes outside the evidence tree."""
    with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
        root=Path(folder);here=root/'blind';baseline=root/'baseline';w39=root/'w39'
        scenes=w39/'scenes.json';split=w39/'split.json'
        for path in [here/'blind.py',baseline/'baseline.py',baseline/'authority-v2.json',
                     baseline/'authority.json',root/'x6/observe.py',root/'backdrops/manifest.json',
                     w39/'supplied-paths.json',scenes,split]:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text('{}\n')
        record=dict(sources={},documents={},runtimeArtifacts={},generatedBackgrounds={},
                    backdrops='backdrops',cells=[],sourceRevision='scratch',
                    scenesSha256=blind.base.sha(scenes),splitSha256=blind.base.sha(split))
        blind.base.save(baseline/'preparation.json',record)
        for obj,name,value in [(blind,'ROOT',root),(blind,'HERE',here),
                               (blind,'__file__',str(here/'blind.py')),
                               (blind.base,'ROOT',root),(blind.base,'HERE',baseline),
                               (blind.base,'W39',w39),(blind.base.wave,'scenes_path',scenes),
                               (blind.base.wave,'split_path',split)]:
            stack.enter_context(patch.object(obj,name,value))
        # Git admission and baseline authority are separate contracts. Keep actual
        # preparation verification, sealing and every repeated seal check live.
        stack.enter_context(patch.object(blind.base.runner,'committed',
                            side_effect=lambda repo,name:blind.base.sha(repo/name)))
        stack.enter_context(patch.object(blind.base.runner,'sources',return_value=[]))
        stack.enter_context(patch.object(blind.base,'scope',return_value=([],{})))
        stack.enter_context(patch.object(blind.base,'verify_authority'))
        stack.enter_context(patch.object(blind,'cells',return_value=['scratch/holdout']))
        yield root,here,record,(scenes,split)

class BlindTests(unittest.TestCase):
    def test_metadata_scope_is_all64_web_heldout_cells(self):
        cells=blind.cells()
        self.assertEqual(len(cells),64)
        self.assertEqual(len(set(cells)),64)
        self.assertTrue(all(blind.base.wave.roles[c.split('/',1)[1]]=='holdout' for c in cells))
        light_receded=[c for c in cells if '-light-' in c and c.endswith('__inactive')]
        self.assertEqual(len(light_receded),16)
        self.assertTrue(all(blind.base.runner.boundary.web_placement_refusal(blind.base.wave.component(c.split('/',1)[1]),blind.base.wave.spec['canvas']) is None for c in cells))

    def test_descriptor_rejects_noise_and_wrong_document(self):
        cell=blind.cells()[0];profile,sid=cell.split('/',1)
        record=blind.base.load(blind.base.HERE/'preparation.json');docs=record['profiles'][profile]
        meta=dict(sceneId=sid,renderer='webgpu',engine='chromium',colorSpace='srgb',pixelSize=list(blind.base.runner.dimension(blind.base.wave,cell)),deterministic=True,repeatNoise=0)
        report=dict(fallback=None,problems=[],materialProfile=dict(sha256=record['documents'][docs['material']][:12]),recededProfile=dict(sha256=record['documents'][docs['receded']][:12]))
        blind.check_descriptor(cell,meta,report,record)
        bad=copy.deepcopy(meta);bad['repeatNoise']=1
        with self.assertRaises(ValueError):blind.check_descriptor(cell,bad,report,record)
        bad=copy.deepcopy(report);bad['recededProfile']['sha256']='0'*12
        with self.assertRaises(ValueError):blind.check_descriptor(cell,meta,bad,record)

    def test_seal_binds_metadata_and_rechecks_live_bytes(self):
        with scratch_metadata() as (root,here,record,metadata):
            blind.seal()
            sealed=blind.base.load(here/'seal.json')
            for path,key in zip(metadata,('scenesSha256','splitSha256')):
                self.assertEqual(sealed['inputs'].get(str(path.relative_to(root))),record[key])
            self.assertIn('baseline/authority-v2.json',sealed['inputs'])
            self.assertNotIn('baseline/authority.json',sealed['inputs'])
            seal_hash=blind.base.sha(here/'seal.json')
            blind.verify_seal(seal_hash)
            for path in metadata:
                with self.subTest(metadata=path.name):
                    original=path.read_bytes();path.write_bytes(original+b' ')
                    try:
                        # This is the same check run before and after each process;
                        # cached Wave membership is unchanged by a live file edit.
                        with self.assertRaisesRegex(ValueError,'live scene/split metadata changed'):
                            blind.verify_seal(seal_hash)
                    finally:path.write_bytes(original)
                    blind.verify_seal(seal_hash)

    def test_seal_refuses_metadata_changed_since_preparation(self):
        for index in (0,1):
            with self.subTest(metadata=index), scratch_metadata() as (_,here,_,metadata):
                path=metadata[index];path.write_bytes(path.read_bytes()+b' ')
                with self.assertRaisesRegex(ValueError,'live scene/split metadata changed'):
                    blind.seal()
                self.assertFalse((here/'seal.json').exists())

    def test_failed_x6_is_retained_and_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'refusal.json'
            with self.assertRaises(PermissionError):blind.require_x6(dict(verdict=dict(passes=False)),path)
            self.assertTrue(path.exists())
            self.assertFalse(blind.base.load(path)['verdict']['passes'])

if __name__=='__main__':unittest.main()
