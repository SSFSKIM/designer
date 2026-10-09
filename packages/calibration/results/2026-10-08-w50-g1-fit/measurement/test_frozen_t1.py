"""Generated TS-production/NumPy regressions; no inventory or capture data is read."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
CAL = FIT.parents[1]


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


Q = source(HERE/'projection.py', 'w50_frozen_projection_tests')
S = source(HERE/'phase_sources.py', 'w50_frozen_sources_tests')


def production(images):
    """Run the actual pure production function on generated RGBA/masks, not a copied formula."""
    script = f'''import {{interiorLevel}} from {json.dumps((CAL/'src/metrics/material.ts').as_uri())};
import {{createImage}} from {json.dumps((CAL/'src/image.ts').as_uri())};
import {{readFileSync}} from 'node:fs';
const images=JSON.parse(readFileSync(0,'utf8'));
console.log(JSON.stringify(images.map(item=>interiorLevel(
  createImage(item.width,item.height,Uint8Array.from(item.rgba)),
  {{interior:{{width:item.width,height:item.height,mask:Uint8Array.from(item.mask)}}}}))));'''
    payload = []
    for rgb, mask in images:
        rgba = np.concatenate((rgb, np.full((*rgb.shape[:2], 1), 255, dtype=np.uint8)), axis=2)
        payload.append({'width': rgb.shape[1], 'height': rgb.shape[0],
                        'rgba': rgba.ravel().tolist(), 'mask': mask.astype(np.uint8).ravel().tolist()})
    result = subprocess.run(['node', '--import', str(CAL/'node_modules/tsx/dist/loader.mjs'),
        '--input-type=module', '--eval', script], input=json.dumps(payload),
        text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


class FrozenT1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(50)
        mask = np.ones((64, 64), dtype=bool)
        native = rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)
        grey = [np.repeat(rng.integers(0, 256, size=(64, 64, 1), dtype=np.uint8), 3, axis=2)
                for _ in range(24)]
        cls.images = [native, *grey]
        cls.ts = production([(rgb, mask) for rgb in cls.images])
        cls.numpy = [S.M.R.S.read_support(rgb, mask)['linearLumaStdDev'] for rgb in cls.images]
        choices = [i for i in range(1, len(cls.images)) if cls.numpy[i] > cls.ts[i]['stdDev']
                   and cls.ts[i]['stdDev'] - cls.ts[0]['stdDev'] > .01]
        if not choices: raise AssertionError('Generated pool must expose outward NumPy reduction drift')
        cls.index = choices[0]

    def row(self, position='.25', statistic='T1-full-silhouette'):
        native = self.ts[0]['stdDev']; current = self.ts[self.index]['stdDev']; budget = .01
        growth = (abs(current-native)-0)/budget
        return {'profile': 'apple-macos-27.0-1x-dark-standard-glass0'+position,
            'renderer': 'webgpu', 'scene': 'generated', 'statistic': statistic, 'role': 'gate',
            'support': 'Original declared full native silhouette.',
            'native': native, 'current': current, 'B': budget,
            'nativeEvidence': {'path': '/generated/native.png', 'sha256': 'a'*64},
            'currentEvidence': {'path': '/generated/current.png', 'sha256': 'b'*64},
            'currentDocumentPair': {'active.dark': 'c'*64, 'receded.dark': 'd'*64},
            'historical': [{'generation': 'generated-frozen', 'value': native, 'enforced': True,
                'maxGrowthInB': growth, 'frozenCurrentGrowthInB': growth,
                'documentPair': {'active.dark': 'e'*64, 'receded.dark': 'f'*64}}]}

    def projected(self):
        value = self.numpy[self.index]; native = self.numpy[0]
        return {'native': native, 'current': value, 'candidate': value,
            'units': 'linear-luma', 'support': 'full-silhouette',
            'measurementStatus': 'MEASURED', 'nativeMeasurementStatus': 'MEASURED',
            'currentMeasurementStatus': 'MEASURED', 'candidateMeasurementStatus': 'MEASURED',
            'code': .005, 'bar': .0025, 'B': .005, 'originalBudgetB': .01,
            'nativeRepeat': {'code': .005, 'bar': .0025, 'B': .005},
            'nativeSupportWitnesses': [{'pixels': 4096, 'maskShape': [64, 64], 'maskPackedBitsSha256': '1'*64}],
            'reported': False, 'eligibleEmptySupport': False, 'required': True,
            'evidence': {side: {'captureIdentity': {'kind': 'png', 'pin': {'path': '/generated/'+side+'.png',
                'sha256': digit*64}, 'digest': digit*64},
                'numericIdentity': {'captureSha256': digit*64, 'statisticSha256': '2'*64,
                    'documentPair': None if side == 'native' else
                        {'activeSha256': 'c'*64, 'recededSha256': 'd'*64}}}
                for side, digit in (('native', 'a'), ('current', 'b'), ('candidate', 'b'))}}

    def authoritative(self, *, value=None, statistic='T1-full-silhouette'):
        return {'estimator': 'PRODUCTION_TS_INTERIOR_LEVEL', 'statistic': statistic,
            'producer': 'packages/calibration/src/metrics/material.ts#interiorLevel',
            'field': 'material.interiorStdDevWeb', 'reading': 'first',
            'capture': {'path': '/generated/candidate.png', 'sha256': 'b'*64},
            'matrix': {'path': '/generated/matrix.json', 'sha256': '3'*64},
            'scene': 'generated', 'units': 'linear-luma',
            'value': self.ts[self.index]['stdDev'] if value is None else value}

    def test_genuine_ts_and_numpy_reductions_differ_on_generated_common_images(self):
        self.assertNotEqual(self.ts[0]['stdDev'], self.numpy[0])
        self.assertGreater(self.numpy[self.index], self.ts[self.index]['stdDev'])
        self.assertEqual(self.ts[self.index]['sampleCount'], 4096)

    def test_original_operands_and_production_candidate_keep_attained_cap_without_rebasing(self):
        original = self.row(); diagnostic = self.projected(); before = copy.deepcopy(diagnostic)
        result = Q.frozen_primary(original, original, diagnostic,
            self.authoritative(), {'path': 'original-inventory.json', 'sha256': '4'*64})
        self.assertEqual(result['sourceReading'], before)
        self.assertEqual(diagnostic, before)
        self.assertEqual((result['native'], result['current'], result['candidate']),
                         (original['native'], original['current'], original['current']))
        self.assertEqual((result['code'], result['bar'], result['B']), (.005, .0025, .005))
        self.assertEqual(result['originalBudgetB'], original['B'])
        self.assertEqual(result['routingOperands'], 'ORIGINAL_INVENTORY')
        historical = original['historical'][0]
        growth = (abs(result['candidate']-result['native'])-abs(historical['value']-result['native']))/original['B']
        self.assertEqual(growth, historical['maxGrowthInB'])
        wrong = (abs(diagnostic['candidate']-original['native'])-abs(historical['value']-original['native']))/original['B']
        self.assertGreater(wrong, historical['maxGrowthInB'])
        for side in ('native', 'current'):
            record = result['evidence'][side]
            self.assertEqual(record['captureIdentity']['kind'], 'frozen-reference-record')
            self.assertEqual(record['captureIdentity']['original'], original)
            self.assertEqual(record['captureIdentity']['side'], side)
            self.assertNotEqual(record['numericIdentity']['statisticSha256'], '2'*64)
        self.assertEqual(result['evidence']['candidate']['productionStatistic'], self.authoritative())
        self.assertNotEqual(result['evidence']['candidate']['numericIdentity']['statisticSha256'], '2'*64)

    def test_genuine_ts_unchanged_candidate_routes_at_attained_cap_and_actual_growth_fails(self):
        rules = source(FIT/'judge/rules.py', 'w50_frozen_joint_rules')
        original = self.row(); inventory = {'path': 'original-inventory.json', 'sha256': '4'*64}
        raw = self.projected()
        read = Q.frozen_primary(original, original, raw, self.authoritative(), inventory)
        read['evidence']['historical'] = Q.histories(original, inventory, original['statistic'])
        row = dict(original, originalReference=copy.deepcopy(original), reference=copy.deepcopy(original),
            sceneSource='canonical', family='texture', inputCode=None, span=64, scale=1, position=.25,
            pose='active', readings={original['statistic']: read})
        result = rules.route_row(row, inventory_sha256=inventory['sha256'])
        historical = [c for c in result['checks'] if c['rule'].startswith('own-history')]
        self.assertEqual(historical[0]['comparison']['status'], 'WITHIN')
        self.assertEqual(row['readings'][original['statistic']]['sourceReading'], raw)
        higher = self.authoritative(value=original['current']+.001)
        changed = Q.frozen_primary(original, original, raw, higher, inventory)
        changed['evidence']['historical'] = Q.histories(original, inventory, original['statistic'])
        row['readings'][original['statistic']] = changed
        result = rules.route_row(row, inventory_sha256=inventory['sha256'])
        historical = [c for c in result['checks'] if c['rule'].startswith('own-history')]
        self.assertEqual(historical[0]['comparison']['status'], 'EXCEEDS')

    def test_new_half_position_keeps_its_own_numpy_operands_and_budgets(self):
        row = self.row(position='.5'); diagnostic = self.projected()
        result = Q.frozen_primary(row, row, diagnostic, None,
                                 {'path': 'original-inventory.json', 'sha256': '4'*64})
        self.assertEqual(result, diagnostic)
        self.assertNotIn('sourceReading', result)

    def test_original_reference_or_named_production_identity_mismatch_is_refused(self):
        original = self.row(); diagnostic = self.projected()
        for mode in ('changed-reference', 'wrong-value-unit', 'wrong-statistic', 'missing-production'):
            with self.subTest(mode=mode):
                reference, observed = copy.deepcopy(original), self.authoritative()
                if mode == 'changed-reference': reference['current'] = diagnostic['current']
                elif mode == 'wrong-value-unit': observed['units'] = 'encoded-luma-codes'
                elif mode == 'wrong-statistic': observed['statistic'] = 'T1-low'
                else: observed = None
                with self.assertRaises(ValueError):
                    Q.frozen_primary(original, reference, diagnostic, observed,
                                     {'path': 'original-inventory.json', 'sha256': '4'*64})


if __name__ == '__main__':
    unittest.main()
