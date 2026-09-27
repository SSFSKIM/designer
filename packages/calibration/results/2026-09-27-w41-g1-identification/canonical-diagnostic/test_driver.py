import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('canonical_driver_test', HERE / 'driver.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Commands(unittest.TestCase):
    def cells(self):
        return [dict(profileKey='apple-macos-26.5-1x-light-reduced-transparency',
                     sceneId='checkerboard__capsule-button__inactive', role='calibration', pose=['deviceScaleFactor=1',
                     'colorScheme=light', 'accessibility=reducedTransparency (others explicitly off)'],
                     documents=[dict(kind='materialProfile', path='doc.json', sha256='abc')])]

    def test_command_exact_scene_policy_and_no_receded_invention(self):
        command = m.command_for(self.cells(), m.CAPTURES / 'run' / 'profile')
        self.assertIn('scripts/capture-web.ts', command)
        self.assertIn('checkerboard__capsule-button__inactive', command)
        self.assertEqual(command[command.index('--accessibility') + 1], 'reduced-transparency')
        self.assertNotIn('--receded-profile', command)
        self.assertNotIn('--set', command)
        self.assertNotIn('compare', command)

    def test_holdout_probe_mixedprofile_and_unsafe_destination_refused(self):
        cell = self.cells()[0]
        for cells in [[dict(cell, role='holdout')], [dict(cell, role='probe')],
                      [cell, dict(cell, profileKey='other')]]:
            with self.assertRaises(ValueError): m.command_for(cells, m.CAPTURES / 'run')
        with self.assertRaises(ValueError): m.command_for([cell], m.ROOT / 'packages/calibration/web-captures')

class Attestation(unittest.TestCase):
    def fixture(self):
        cell = dict(sceneId='checkerboard__capsule-button__inactive', state='inactive',
            canvas={'width': 320, 'height': 200},
            pose=['deviceScaleFactor=1', 'colorScheme=light', 'accessibility=browser-preferences'],
            documents=[{'kind': 'materialProfile'}, {'kind': 'recededProfile'}],
            runtimeRecededPatch=None, selectedEndpoint=dict(name='test', platform='macOS 27.0',
                profileKey='active-light', resolvedMaterialSha256='active-endpoint'))
        material = dict(cell['selectedEndpoint'], tuned=True)
        descriptor = dict(sceneId=cell['sceneId'], renderer='webgpu', engine='chromium',
            colorSpace='srgb', samplingBackend='gpu-texture', pixelSize=[320, 200],
            deterministic=True, repeatNoise=0)
        active = dict(sha256='active-file', patch={'bodyAlpha': .5}, cssTierMapping=None)
        receded = dict(sha256='candidate-file', patch={'bodyE3Strength': 1})
        report = dict(colorScheme='light', fallback=None, problems=[], accessibility=None,
            materialProfile=active, recededProfile=receded,
            page=dict(sceneId=cell['sceneId'], canvas=cell['canvas'], pixelSize=[320, 200],
                requestedScale=1, devicePixelRatio=1, colorScheme='light', problems=[],
                requestedBackdropMode='texture', requestedBackdropLevel=None,
                adapter={'ok': True, 'isFallback': False}, accessibilityOverrides=None,
                accessibilityPolicy=dict(reducedTransparency=False, increasedContrast=False,
                                         reducedMotion=False, forcedColors=False),
                materialProfile={'bodyAlpha': .5, 'bodyE3Strength': 1},
                candidateRecededMaterialProfile={'bodyE3Strength': 1}, recededMaterialProfile=None,
                windowActivation='active', cssTierMapping=None, material=material,
                groups=[dict(configuredSource='texture', state=dict(activeRenderer='webgpu',
                    samplingBackend='gpu-texture', materialDocument=material))]))
        return cell, descriptor, report, {'materialProfile': active, 'recededProfile': receded}

    def test_tuned_candidate_attests_patch_and_active_endpoint_separately(self):
        from unittest.mock import patch
        from copy import deepcopy
        cell, descriptor, report, docs = self.fixture()
        with patch.object(m, 'document', side_effect=lambda d: docs[d['kind']]):
            m.validate_report(cell, descriptor, report)
            for field, value in [('materialProfile', {'bodyE3Strength': 0}),
                                 ('windowActivation', 'inactive'),
                                 ('material', dict(report['page']['material'], resolvedMaterialSha256='candidate-file')),
                                 ('adapter', {'ok': True, 'isFallback': True}),
                                 ('accessibilityPolicy', {'reducedTransparency': True})]:
                changed = deepcopy(report); changed['page'][field] = value
                with self.assertRaises(ValueError): m.validate_report(cell, descriptor, changed)
            changed = deepcopy(report); changed['recededProfile']['sha256'] = 'different'
            with self.assertRaises(ValueError): m.validate_report(cell, descriptor, changed)

    def test_runtime_receded26_has_no_invented_digest(self):
        from unittest.mock import patch
        cell, descriptor, report, docs = self.fixture()
        cell.update(documents=[{'kind': 'materialProfile'}], runtimeRecededPatch={'bodyAlpha': .2},
                    selectedEndpoint={'name': 'test26', 'platform': 'macOS 26.5'})
        material = dict(cell['selectedEndpoint'], tuned=True)
        report.update(recededProfile=None)
        report['page'].update(windowActivation='inactive', candidateRecededMaterialProfile=None,
            recededMaterialProfile={'bodyAlpha': .2}, materialProfile={'bodyAlpha': .5}, material=material)
        report['page']['groups'][0]['state']['materialDocument'] = material
        with patch.object(m, 'document', side_effect=lambda d: docs[d['kind']]):
            m.validate_report(cell, descriptor, report)
            report['page']['material'] = dict(material, resolvedMaterialSha256='invented')
            with self.assertRaises(ValueError): m.validate_report(cell, descriptor, report)

if __name__ == '__main__': unittest.main()
