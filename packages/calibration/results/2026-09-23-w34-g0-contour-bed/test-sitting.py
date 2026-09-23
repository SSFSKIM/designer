#!/usr/bin/env python3
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent


class Sitting(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('sitting',HERE/'sitting.py')
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        self.machine=json.loads((HERE/'machine-side-built.json').read_text())
        self.machine['foreignProcessCount']=0;self.machine['foreignProcesses']=[]

    def test_each_pass_requires_its_own_mode_and_machine_facts(self):
        for scale in [1,2]:
            m=copy.deepcopy(self.machine)
            if scale==1:m['display']['stdout']=m['display']['stdout'].replace('scaling:on <-- current mode','scaling:on').replace('mode 69: res:2560x1440 hz:60 color_depth:4','mode 69: res:2560x1440 hz:60 color_depth:4 <-- current mode')
            for pose in ['active','inactive']:
                self.module.validate_machine(m,scale)
                for field,value in [('reduceTransparency','1'),('increaseContrast','1'),
                                    ('NSGlassTintAmount','0.7'),('ButtonShapesEnabled','1')]:
                    bad=copy.deepcopy(m);bad['settings'][field]['stdout']=value
                    with self.assertRaises(ValueError):self.module.validate_machine(bad,scale)
                for source in ['os','display']:
                    bad=copy.deepcopy(m);bad[source]['stdout']='wrong'
                    with self.assertRaises(ValueError):self.module.validate_machine(bad,scale)
                bad=copy.deepcopy(m);bad['side']['binarySha256']='changed'
                with self.assertRaises(ValueError):self.module.validate_machine(bad,scale)
                bad=copy.deepcopy(m);bad['foreignProcessCount']=1
                with self.assertRaises(ValueError):self.module.validate_machine(bad,scale)
                self.module.validate_machine(bad,scale,require_exclusive=False)
                with self.assertRaises(ValueError):self.module.validate_machine(m,3-scale)

    def test_closing_drift_and_missing_or_wrong_pose_cells_refuse(self):
        first=self.module.configuration(self.machine)
        bad=copy.deepcopy(self.machine);bad['settings']['NSGlassTintAmount']['stdout']='0.6'
        self.assertNotEqual(first,self.module.configuration(bad))
        manifest=json.loads((HERE/'grant-side-manifest.json').read_text())
        expected={(p['profileKey'],f['sceneId']) for p in manifest['profiles'] for f in p['fixtures']}
        with self.assertRaisesRegex(ValueError,'pose'):self.module.validate_manifest(manifest,expected,'active',2)
        good=copy.deepcopy(manifest);good['profiles'][0]['fixtures'][0]['presentedActive']=True
        self.module.validate_manifest(good,expected,'active',2)
        good['profiles'][0]['fixtures']=[]
        with self.assertRaisesRegex(ValueError,'membership'):self.module.validate_manifest(good,expected,'active',2)


if __name__=='__main__':unittest.main()
