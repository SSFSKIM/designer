"""W42 one-exposure runner, proved on a SYNTHETIC holdout that is not Apple's.

Every test builds a toy W42-format declaration (scenes file with its own split and
holdout, bed.json, pins) inside a temporary Git repository, loads it through bed/wave.py's
Wave class, writes a synthetic archive (generated PNGs + a W39-Reader inventory) OUTSIDE
that repository, and runs the exposure with injected capture/project/score backends and a
scratch receipt log. No native payload, Apple pixel, browser, GUI or production receipt is
touched; the one test that reads the real W42 declaration reads metadata only.

Run: python3.12 -m unittest discover -s <this dir> -p test_runner.py -v
"""
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import runner

L2, D2 = 'apple-macos-27.0-2x-light-standard-glass0.5', 'apple-macos-27.0-2x-dark-standard-glass0.5'
APPLE = (80, 90, 100)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE).decode().strip()


def toy_declaration():
    """Five glass cells in three endpoints: calibration c1 (light and dark active),
    validation v1, holdout h1 (light active, dark receded) and h2 (dark receded), and the
    bridge f1 (probe). References follow the W42 rank rule."""
    rrect = dict(kind='rrect', size=[160, 96], radius=20)
    backgrounds = {'grey-a': dict(kind='solid', srgb=[100] * 3), 'grey-b': dict(kind='solid', srgb=[200] * 3),
                   'chk': dict(kind='checkerboard', cell=16, a=[0] * 3, b=[255] * 3)}
    glass = [('c1__rest', 'grey-a'), ('v1__rest', 'grey-a'), ('h1__rest', 'grey-b'), ('h1__inactive', 'grey-b'),
             ('h2__inactive', 'chk'), ('f1__rest', 'chk')]
    refs = ['ref-grey-a__rest', 'ref-grey-b__rest', 'ref-grey-b__inactive', 'ref-chk__rest', 'ref-chk__inactive']
    scenes = [dict(id=sid, background=bg, component='rrect-md', state=sid.split('__')[1]) for sid, bg in glass]
    scenes += [dict(id=r, background=r[4:].split('__')[0], component='none', state=r.split('__')[1]) for r in refs]
    split = dict(calibration=['c1__rest', 'ref-grey-a__rest', 'ref-chk__rest', 'ref-chk__inactive'],
                 validation=['v1__rest'],
                 holdout=['h1__rest', 'h1__inactive', 'h2__inactive', 'ref-grey-b__rest', 'ref-grey-b__inactive'],
                 recorded=[], probe=['f1__rest'])
    profiles = [dict(key=L2, colorScheme='light', a11y='standard',
                     scenes=['c1__rest', 'v1__rest', 'h1__rest', 'f1__rest', 'ref-grey-a__rest',
                             'ref-grey-b__rest', 'ref-chk__rest']),
                dict(key=D2, colorScheme='dark', a11y='standard',
                     scenes=['c1__rest', 'h1__inactive', 'h2__inactive', 'ref-grey-a__rest',
                             'ref-grey-b__inactive', 'ref-chk__inactive'])]
    spec = dict(version=1, canvas=dict(width=320, height=200), backgrounds=backgrounds,
                components={'rrect-md': rrect, 'none': dict(kind='none')}, tints={}, scenes=scenes,
                profiles=profiles, split=split)
    bed = dict(schema='w42-bed-1-synthetic', passes={},
               cells={c: dict(role=r) for c, r in [('c1', 'calibration'), ('v1', 'validation'), ('h1', 'holdout'),
                                                   ('h2', 'holdout'), ('f1', 'probe')]})
    return spec, bed


class Exposure(unittest.TestCase):
    """One toy declaration, one archive, two candidates; knobs select the scenario."""

    law_error = {}          # cell -> codes added to the law's numerical prediction
    native_error = {}       # cell -> codes added to candidate-2's render (its own prediction moves too)
    landed_offset = 3       # candidate-1's landed T sits 3 codes off Apple everywhere (the level miss)
    claimed = ('light-active', 'dark-receded')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='w42-exposure-test-')
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.root = base / 'repo'
        self.root.mkdir()
        git(self.root, 'init', '-q')
        git(self.root, 'config', 'user.email', 'test@example.invalid')
        git(self.root, 'config', 'user.name', 'Synthetic test')
        spec, bed = toy_declaration()
        self.put('decl/toy-scenes.json', spec)
        self.put('decl/toy-bed.json', bed)
        self.put('decl/toy-pins.json', {'toy-scenes.json': runner.sha(self.root / 'decl/toy-scenes.json'),
                                        'toy-bed.json': runner.sha(self.root / 'decl/toy-bed.json')})
        self.wave = runner.boundary.Wave(self.root / 'decl/toy-scenes.json', self.root / 'decl/toy-bed.json',
                                         self.root / 'decl/toy-pins.json')
        self.archive = base / 'archive'
        entries = []
        for cell in sorted(self.wave.cells):
            profile, sid = cell.split('/', 1)
            role = self.wave.roles[sid]
            rel = f'{role}/{profile}/{sid}.png'
            (self.archive / rel).parent.mkdir(parents=True, exist_ok=True)
            Image.new('RGB', runner.dimension(self.wave, cell), APPLE).save(self.archive / rel)
            kind = 'noGlass' if sid.startswith('ref-') else 'glass'
            entries.append(dict(cell=cell, kind=kind, path=rel, sha256=runner.sha(self.archive / rel)))
        inventory = dict(schema='w42-archive-inventory-synthetic', scenesSha256=self.wave.scenes_sha,
                         splitSha256=self.wave.split_sha, entries=entries)
        (self.archive / 'inventory.json').write_text(json.dumps(inventory))
        self.put('archive/inventory.json', (self.archive / 'inventory.json').read_text())
        self.glass = sorted(c for c in self.wave.cells if not c.split('/', 1)[1].startswith(('ref-', 'f1')))
        self.holdout = [c for c in self.glass if self.wave.roles[c.split('/', 1)[1]] == 'holdout']
        self.calval = [c for c in self.glass if c not in self.holdout]
        self.put('packages/renderer-webgpu/src/standin.txt', 'synthetic renderer revision 1')
        self.put('config.json', {'profiles': {}})
        self.put('law/parameters.json', {'k': 2.035, 'lambda': 0.68})
        self.put('law/predictions.json', {'cells': {c: self.shift(APPLE, self.law_error.get(c, 0))
                                                    for c in self.glass}})
        self.put('law/survival.json', {'numerical': {c: True for c in self.calval}})
        self.candidates = []
        for cid, role in (('candidate-1', 'landed-T'), ('candidate-2', 'native-T')):
            images = {}
            predictions = {}
            for i, cell in enumerate(self.glass):
                rgb = self.rgb_for(role, cell)
                predictions[cell] = rgb
                Image.new('RGB', runner.dimension(self.wave, cell), tuple(rgb)).save(self.root / f'{cid}-{i}.png')
                self.put(f'{cid}-{i}.json', {'rgb': rgb})
                images[cell] = {'png': f'{cid}-{i}.png', 'projection': f'{cid}-{i}.json'}
            self.put(f'{cid}/parameters.json', {'k': 2.035, 'T': role})
            self.put(f'{cid}/predictions.json', {'cells': predictions})
            self.put(f'{cid}/rendered.json', {'cells': images})
            self.put(f'{cid}/survival.json', {kind: {c: True for c in self.calval} for kind in ('numerical', 'rendered')})
            self.candidates.append({'id': cid, 'role': role, 'parameters': f'{cid}/parameters.json',
                                    'predictions': f'{cid}/predictions.json', 'rendered': f'{cid}/rendered.json',
                                    'survival': f'{cid}/survival.json'})
        self.law = {'parameters': 'law/parameters.json', 'predictions': 'law/predictions.json',
                    'survival': 'law/survival.json'}
        self.put('scorer.py', '# synthetic scorer stand-in; the tests inject score()\n')
        self.put('declaration.txt', 'synthetic W42 declaration stand-in, not W42 evidence')
        self.put('closure.json', {'synthetic': True})
        self.commit()
        self.manifest = self.freeze()
        self.put('frozen.json', self.manifest)
        self.commit()
        self.log = base / 'scratch-receipt.jsonl'
        self.output = base / 'capture'
        self.score_report = self.log.with_name(self.log.stem + '-scores.json')
        self.calls, self.readers = [], []

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def shift(rgb, codes):
        return [v + codes for v in rgb]

    def rgb_for(self, role, cell):
        if role == 'landed-T':
            return self.shift(APPLE, self.landed_offset)
        return self.shift(APPLE, self.native_error.get(cell, 0))

    def put(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if not isinstance(value, str) else value)

    def commit(self):
        git(self.root, 'add', '.')
        git(self.root, 'commit', '-qm', 'Synthetic stand-in')

    def freeze(self, **overrides):
        kwargs = dict(law=self.law, config='config.json', scorer='scorer.py', declaration='declaration.txt',
                      closure='closure.json', inventory='archive/inventory.json',
                      claimed_endpoints=list(self.claimed), mode='synthetic')
        kwargs.update(overrides)
        return runner.freeze(self.root, self.wave, self.candidates, **kwargs)

    def events(self):
        return [json.loads(line)['event'] for line in self.log.read_text().splitlines()]

    def capture(self, request):
        request.authorization.check(self.wave)
        self.assertEqual(self.events(), ['begin'])
        self.calls.append(request)
        role = next(c['role'] for c in request.manifest['candidates'] if c['id'] == request.candidate)
        answer = {}
        for index, cell in enumerate(request.cells):
            path = request.output / f'{index}.png'
            Image.new('RGB', runner.dimension(self.wave, cell), tuple(self.rgb_for(role, cell))).save(path)
            answer[cell] = path
        return answer

    def project(self, cell, path):
        with Image.open(path) as image:
            return {'rgb': list(image.convert('RGB').getpixel((0, 0)))}

    def score(self, request):
        """Reads Apple's (synthetic) held-out pixels through the guarded Reader and scores:
        the law's numerical prediction and candidate-2's render against them; candidate-1's
        render against its own frozen prediction, with the gap to Apple as the level miss."""
        request.authorization.check(self.wave)
        reader = request.wave.reader(self.archive, ('holdout',), request.authorization)
        self.readers.append(reader)
        apple = {}
        for cell in request.numerical_cells:
            path = self.archive / next(e['path'] for e in reader.report_inventory()
                                       if e['cell'] == cell and e['kind'] == 'glass')
            reader.read(cell, 'glass')   # the guarded read; the pixel below is the same bytes
            with Image.open(path) as image:
                apple[cell] = list(image.convert('RGB').getpixel((0, 0)))
        law = runner.load(request.root / request.manifest['law']['predictions'])['cells']
        worst = lambda a, b: max(abs(x - y) for x, y in zip(a, b, strict=True))
        out = {'law': {'numerical': {c: {'status': 'measured', 'passes': worst(law[c], apple[c]) <= 1,
                                         'worstResidualCodes': worst(law[c], apple[c])}
                                     for c in request.numerical_cells}},
               'candidates': {}}
        for cid, artifact in request.candidates.items():
            own = runner.load(request.root / artifact['predictions'])['cells']
            rows = {}
            for cell in request.rendered_cells:
                rgb = self.project(cell, request.captures[cid][cell])['rgb']
                if artifact['role'] == 'landed-T':
                    rows[cell] = {'status': 'measured', 'passes': worst(rgb, own[cell]) <= 1,
                                  'levelMiss': {'codes': worst(rgb, apple[cell])}}
                else:
                    rows[cell] = {'status': 'measured', 'passes': worst(rgb, apple[cell]) <= 1}
            out['candidates'][cid] = {'rendered': rows}
        return out

    def run_exposure(self, capture=None, score=None, project=None):
        return runner.run_synthetic(self.root, self.wave, self.root / 'frozen.json', self.log, self.output,
                                    capture or self.capture, project or self.project, score or self.score)


class Lifecycle(Exposure):
    def test_both_candidates_and_the_law_are_bound_in_one_receipt(self):
        result = self.run_exposure()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(self.events(), ['begin', 'complete'])
        lines = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual(len({line['configurationSha256'] for line in lines}), 1)
        config = lines[0]['configuration']
        self.assertEqual([c['id'] for c in config['candidate']], ['candidate-1', 'candidate-2'])
        self.assertEqual({c['role'] for c in config['candidate']}, {'landed-T', 'native-T'})
        self.assertEqual(config['law']['predictions'], 'law/predictions.json')
        self.assertEqual(config['claimedEndpoints'], ['dark-receded', 'light-active'])
        self.assertIn('candidate-2-0.png', config['frozenFiles'])
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(result['verdict']['landable'], ['candidate-1', 'candidate-2'])
        self.assertEqual(result['verdict']['selectedByX40'], 'candidate-2')
        self.assertTrue(result['verdict']['law']['closes'])

    def test_holdout_reader_refused_outside_receipt_admitted_inside(self):
        with self.assertRaises(PermissionError):
            self.wave.reader(self.archive, ('holdout',))
        calval = self.wave.reader(self.archive, ('calibration', 'validation'))
        with self.assertRaises(PermissionError):
            calval.read(self.holdout[0], 'glass')
        self.run_exposure()
        self.assertEqual(len(self.readers), 1)
        with self.assertRaises(PermissionError):   # the receipt's token is dead after it
            self.readers[0].read(self.holdout[0], 'glass')

    def test_holdout_only_is_exposed_and_probe_is_excluded_with_reason(self):
        self.run_exposure()
        self.assertEqual(sorted(self.calls[0].cells), self.holdout)
        excluded = self.manifest['excludedCells']
        self.assertIn(f'{L2}/f1__rest', excluded['numerical'])
        self.assertIn('probe', excluded['numerical'][f'{L2}/f1__rest'])
        self.assertNotIn(f'{L2}/f1__rest', self.manifest['numericalCells'] + self.manifest['renderedCells'])

    def test_second_attempt_refused_once_spent(self):
        self.run_exposure()
        with self.assertRaises(PermissionError):
            runner.run_synthetic(self.root, self.wave, self.root / 'frozen.json', self.log,
                                 Path(self.tmp.name) / 'capture-2', self.capture, self.project, self.score)
        self.assertEqual(len(self.calls), 2)

    def test_scores_are_persisted_before_aggregation(self):
        def malformed(request):
            scores = self.score(request)
            del scores['candidates']['candidate-1']['rendered'][self.holdout[0]]['levelMiss']
            return scores
        with self.assertRaisesRegex(ValueError, 'levelMiss'):
            self.run_exposure(score=malformed)
        self.assertEqual(self.events(), ['begin', 'failed'])
        record = json.loads(self.score_report.read_text())
        self.assertEqual(record['status'], 'scored')
        self.assertIn(self.holdout[0], record['scores']['law']['numerical'])
        result = json.loads((self.output / 'result.json').read_text())
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['scoreReport']['sha256'], runner.sha(self.score_report))

    def test_scorer_exception_fails_without_invented_scores(self):
        def broken(request):
            raise RuntimeError('synthetic scorer crashed')
        with self.assertRaisesRegex(RuntimeError, 'crashed'):
            self.run_exposure(score=broken)
        self.assertEqual(self.events(), ['begin', 'failed'])
        self.assertFalse(self.score_report.exists())
        self.assertNotIn('scores', json.loads((self.output / 'result.json').read_text()))

    def test_changed_frozen_png_fails_and_spends(self):
        def changed(request):
            paths = self.capture(request)
            first = next(iter(paths.values()))
            Image.new('RGB', (640, 400), (81, 90, 100)).save(first)
            return paths
        with self.assertRaisesRegex(ValueError, 'rendered prediction'):
            self.run_exposure(capture=changed)
        self.assertEqual(self.events(), ['begin', 'failed'])
        with self.assertRaises(PermissionError):
            runner.run_synthetic(self.root, self.wave, self.root / 'frozen.json', self.log,
                                 Path(self.tmp.name) / 'capture-2', self.capture, self.project, self.score)

    def test_changed_projection_fails_and_spends(self):
        with self.assertRaisesRegex(ValueError, 'projection'):
            self.run_exposure(project=lambda cell, path: {'rgb': [0, 0, 0]})
        self.assertEqual(self.events(), ['begin', 'failed'])

    def test_frozen_input_mutation_refused_before_begin(self):
        for name in ['packages/renderer-webgpu/src/standin.txt', 'law/predictions.json',
                     'candidate-2/predictions.json', 'candidate-1-0.png', 'archive/inventory.json']:
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                with self.assertRaises(ValueError):
                    self.run_exposure()
                self.assertFalse(self.log.exists())
                path.write_bytes(original)

    def test_score_callback_mutation_is_refused(self):
        def mutate(request):
            scores = self.score(request)
            request.captures['candidate-1'].clear()
            return scores
        with self.assertRaisesRegex(ValueError, 'mutated'):
            self.run_exposure(score=mutate)
        self.assertEqual(self.events(), ['begin', 'failed'])
        self.assertTrue(self.score_report.exists())

    def test_process_kill_after_persistence_leaves_scores_without_retry(self):
        pid = os.fork()
        if pid == 0:   # pragma: no cover - child
            def kill_after(request):
                scores = self.score(request)
                real = runner.persist
                def persist_then_die(path, value):
                    real(path, value)
                    if value.get('status') == 'scored':
                        os.kill(os.getpid(), signal.SIGKILL)
                runner.persist = persist_then_die
                return scores
            try:
                self.run_exposure(score=kill_after)
            finally:
                os._exit(3)
        _, status = os.waitpid(pid, 0)
        self.assertTrue(os.WIFSIGNALED(status))
        self.assertEqual(json.loads(self.score_report.read_text())['status'], 'scored')
        self.assertEqual(self.events(), ['begin'])
        with self.assertRaises(PermissionError):
            self.run_exposure()


class CandidateTwoFails(Exposure):
    native_error = {f'{L2}/h1__rest': 6}     # its render AND its own prediction move; Apple does not

    def test_candidate_2_failing_does_not_fail_candidate_1(self):
        result = self.run_exposure()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(self.events(), ['begin', 'complete'])
        verdict = result['verdict']
        self.assertTrue(verdict['law']['closes'])
        self.assertFalse(verdict['candidates']['candidate-2']['passes'])
        self.assertTrue(verdict['candidates']['candidate-1']['passes'])
        self.assertEqual(verdict['landable'], ['candidate-1'])
        self.assertEqual(verdict['selectedByX40'], 'candidate-1')
        # The landed-T candidate's gap to Apple is the named level miss, not a failure.
        misses = verdict['candidates']['candidate-1']['levelMiss']
        self.assertEqual({v['codes'] for v in misses.values()}, {3})


class LawFails(Exposure):
    law_error = {f'{D2}/h2__inactive': 4}

    def test_numerical_law_failure_leaves_nothing_landable(self):
        result = self.run_exposure()
        self.assertEqual(result['status'], 'complete')
        verdict = result['verdict']
        self.assertFalse(verdict['law']['closes'])
        self.assertEqual(verdict['law']['endpoints']['claimed']['dark-receded']['failed'], 1)
        self.assertEqual(verdict['landable'], [])
        self.assertIsNone(verdict['selectedByX40'])
        # The renders still passed their own checks; closure is the law's, not theirs.
        self.assertTrue(verdict['candidates']['candidate-2']['passes'])


class UnclaimedEndpoint(Exposure):
    claimed = ('light-active',)
    law_error = {f'{D2}/h2__inactive': 5}

    def test_unclaimed_endpoint_is_scored_and_reported_not_claimed(self):
        result = self.run_exposure()
        verdict = result['verdict']
        self.assertTrue(verdict['law']['closes'])
        unclaimed = verdict['law']['endpoints']['notClaimed']['dark-receded']
        self.assertEqual(unclaimed['status'], 'not claimed (identity)')
        self.assertEqual(unclaimed['failed'], 1)
        self.assertEqual(verdict['landable'], ['candidate-1', 'candidate-2'])
        self.assertEqual(verdict['claimedEndpoints'], ['light-active'])


class UnadmittedHeldOutCell(Exposure):
    claimed = ('dark-receded',)

    def setUp(self):
        super().setUp()
        inventory = runner.load(self.root / 'archive/inventory.json')
        inventory['entries'] = [e for e in inventory['entries'] if e['cell'] != f'{L2}/h1__rest']
        self.put('archive/inventory.json', inventory)   # the archive's own copy moves with it,
        (self.archive / 'inventory.json').write_text((self.root / 'archive/inventory.json').read_text())
        for name in ('law/predictions.json', 'candidate-1/predictions.json', 'candidate-2/predictions.json',
                     'candidate-1/rendered.json', 'candidate-2/rendered.json'):
            value = runner.load(self.root / name)
            value['cells'].pop(f'{L2}/h1__rest')
            self.put(name, value)
        self.commit()
        self.manifest = self.freeze()
        self.put('frozen.json', self.manifest)
        self.commit()

    def test_a_quarantined_held_out_capture_is_excluded_not_a_procedural_failure(self):
        self.assertEqual(self.manifest['excludedCells']['rendered'][f'{L2}/h1__rest'],
                         'not admitted by the bound archive inventory')
        result = self.run_exposure()
        self.assertEqual(result['status'], 'complete')
        self.assertNotIn(f'{L2}/h1__rest', self.calls[0].cells)
        self.assertTrue(result['verdict']['law']['closes'])


class Censoring(Exposure):
    def censor(self, constraints):
        def scorer(request):
            scores = self.score(request)
            scores['law']['numerical'][self.holdout[0]] = {'status': 'UNMEASURED', 'reason': 'censored',
                                                           'passes': None, 'constraintsPass': constraints}
            return scores
        return scorer

    def test_censored_cell_is_neither_pass_nor_coverage(self):
        result = self.run_exposure(score=self.censor(True))
        endpoint = runner.endpoint_of(self.wave, self.holdout[0])
        row = result['verdict']['law']['endpoints']['claimed'][endpoint]
        self.assertEqual(row['censored'], 1)
        self.assertEqual(row['measured'], row['passed'])
        self.assertLess(row['measured'], row['total'])

    def test_censoring_cannot_hide_a_binding_miss(self):
        result = self.run_exposure(score=self.censor(False))
        self.assertFalse(result['verdict']['law']['closes'])

    def test_other_unmeasured_is_a_procedural_failure(self):
        def other(request):
            scores = self.score(request)
            scores['law']['numerical'][self.holdout[0]] = {'status': 'UNMEASURED', 'reason': 'population',
                                                           'passes': None}
            return scores
        with self.assertRaisesRegex(ValueError, 'UNMEASURED'):
            self.run_exposure(score=other)
        self.assertEqual(self.events(), ['begin', 'failed'])


class Freeze(Exposure):
    def test_one_landed_t_candidate_is_required_and_roles_are_unique(self):
        for candidates in ([self.candidates[1]], [self.candidates[0], dict(self.candidates[0], id='again')],
                           [dict(self.candidates[0], role='other')]):
            with self.subTest(roles=[c['role'] for c in candidates]):
                with self.assertRaises(ValueError):
                    runner.freeze(self.root, self.wave, candidates, law=self.law, config='config.json',
                                  scorer='scorer.py', declaration='declaration.txt', closure='closure.json',
                                  inventory='archive/inventory.json', claimed_endpoints=['light-active'],
                                  mode='synthetic')
        alone = runner.freeze(self.root, self.wave, [self.candidates[0]], law=self.law, config='config.json',
                              scorer='scorer.py', declaration='declaration.txt', closure='closure.json',
                              inventory='archive/inventory.json', claimed_endpoints=['light-active'],
                              mode='synthetic')
        self.assertEqual([c['id'] for c in alone['candidates']], ['candidate-1'])

    def test_claims_must_name_endpoints_with_holdout_cells(self):
        for claimed in ([], ['light-receded'], ['bogus'], ['light-active', 'light-active']):
            with self.subTest(claimed=claimed):
                with self.assertRaises(ValueError):
                    self.freeze(claimed_endpoints=claimed)

    def test_failed_pre_exposure_survival_refuses_freeze(self):
        self.put('candidate-2/survival.json', {'numerical': {c: True for c in self.calval},
                                               'rendered': {c: (c != self.calval[0]) for c in self.calval}})
        self.commit()
        with self.assertRaisesRegex(ValueError, 'survive'):
            self.freeze()

    def test_missing_prediction_refuses_freeze(self):
        cells = runner.load(self.root / 'law/predictions.json')['cells']
        cells.pop(self.holdout[0])
        self.put('law/predictions.json', {'cells': cells})
        self.commit()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.freeze()

    def test_inventory_admission_bounds_the_scope(self):
        original = runner.load(self.root / 'archive/inventory.json')
        for dropped, message in ((f'{D2}/h2__inactive', 'coverage'),     # predictions name an unadmitted cell
                                 (f'{L2}/h1__rest', 'claimed endpoint')):  # the claim loses its only H cell
            with self.subTest(dropped=dropped):
                inventory = dict(original, entries=[e for e in original['entries'] if e['cell'] != dropped])
                self.put('archive/inventory.json', inventory)
                self.commit()
                with self.assertRaisesRegex(ValueError, message):
                    self.freeze()

    def test_synthetic_mode_refuses_the_production_declaration_and_log(self):
        real = runner.boundary.default_wave()
        with self.assertRaisesRegex(ValueError, 'production'):
            runner.freeze(self.root, real, self.candidates, law=self.law, config='config.json',
                          scorer='scorer.py', declaration='declaration.txt', closure='closure.json',
                          inventory='archive/inventory.json', claimed_endpoints=['light-active'],
                          mode='synthetic')
        with self.assertRaises(PermissionError):
            runner.run_synthetic(self.root, self.wave, self.root / 'frozen.json', runner.PRODUCTION_LOG,
                                 self.output, self.capture, self.project, self.score)
        self.assertFalse(runner.PRODUCTION_LOG.exists())

    def test_production_freeze_refuses_without_the_g1_inventory_pin(self):
        pins = runner.load(runner.PIN_PATH)
        self.assertIsNone(pins['inventorySha256'])
        with self.assertRaisesRegex(ValueError, 'G1'):
            runner.freeze(runner.ROOT, runner.boundary.default_wave(), self.candidates, law=self.law,
                          config='config.json', scorer='scorer.py', declaration='declaration.txt',
                          closure='closure.json', inventory='archive/inventory.json',
                          claimed_endpoints=['light-active'], mode='production')
        with self.assertRaisesRegex(ValueError, 'G1'):
            runner.run_production(Path('/nonexistent/frozen.json'), Path(self.tmp.name) / 'never')
        self.assertFalse(runner.PRODUCTION_LOG.exists())

    def test_real_backend_is_w41s_capture_web_on_the_w42_scenes_file(self):
        self.assertIs(runner.capture_web, runner.w41.capture_web)
        profiles = {cell.split('/', 1)[0]: {'material': 'law/parameters.json', 'receded': 'law/parameters.json'}
                    for cell in self.holdout}
        manifest = dict(self.manifest, config='runtime.json')
        manifest['files'] = dict(manifest['files'], **{'law/parameters.json': runner.sha(self.root / 'law/parameters.json')})
        self.put('runtime.json', {'fixtures': 'backdrops', 'candidates': {'candidate-1': {'profiles': profiles}}})
        self.output.mkdir()
        seen = []

        def launch(command, env, check):
            self.assertEqual(env['VITREA_SCENES'], str(self.wave.scenes_path))
            self.assertEqual(env['VITREA_ALLOW_FALLBACK_ADAPTER'], '0')
            seen.append(command)
            destination = Path(command[command.index('--out') + 1])
            for identity in self.holdout:
                if not identity.startswith(destination.name + '/'):
                    continue
                sid = identity.split('/', 1)[1]
                directory = destination / sid
                directory.mkdir(parents=True)
                Image.new('RGB', runner.dimension(self.wave, identity), APPLE).save(directory / (sid + '__webgpu.png'))
                (directory / 'cell__webgpu.json').write_text(json.dumps(dict(
                    sceneId=sid, renderer='webgpu', engine='chromium', colorSpace='srgb',
                    pixelSize=runner.dimension(self.wave, identity), deterministic=True, repeatNoise=0)))
                material = {'sha256': manifest['files']['law/parameters.json'][:12]}
                (directory / 'report__webgpu.json').write_text(json.dumps(dict(
                    fallback=None, problems=[], materialProfile=material, recededProfile=material)))
        config = dict(scenes=self.wave.scenes_sha, split=self.wave.split_sha, generation=self.manifest['generation'],
                      instrument='standin', closure='standin', candidate='standin')
        with runner.boundary.Receipt(self.log, config).expose() as token:
            request = runner.CaptureRequest(self.wave, token, self.root, manifest, 'candidate-1',
                                            tuple(self.holdout), self.output)
            with patch.object(runner.w41.subprocess, 'run', side_effect=launch):
                paths = runner.capture_web(request)
        self.assertEqual(set(paths), set(self.holdout))
        self.assertEqual(len(seen), 2)   # one launch per profile


class RealDeclarationScope(unittest.TestCase):
    """Metadata only: the real W42 declaration's exposure scope (no inventory exists yet)."""

    def test_scope_of_the_declared_bed(self):
        wave = runner.boundary.default_wave()
        numerical, excluded = runner.declared_scope(wave, web=False)
        rendered, web_excluded = runner.declared_scope(wave, web=True)
        holdout = [c for c in numerical if wave.roles[c.split('/', 1)[1]] == 'holdout']
        self.assertEqual(len(holdout), 4 * 8 + 4 * 2)          # H: 8 per 2x pass, 2 per 1x pass
        self.assertEqual(rendered, numerical)                  # every glass cell is web-plannable
        self.assertEqual(len(excluded), 4 * 4 + 4 * 2)          # F: 4 per 2x pass, 2 per 1x pass
        self.assertTrue(all('probe' in reason for reason in excluded.values()))
        self.assertEqual({runner.endpoint_of(wave, c) for c in holdout}, set(runner.ENDPOINTS))
        # 2x 95 / 92 / 109 / 107 and 1x 15 / 16 / 15 / 16: the charter's bed plus the s = 32
        # receded rows (gate rehearsal), the instrument stream's ruled cells and ruling 3's
        # active guard rows.
        self.assertEqual(len(numerical), 403 + 62 - len(excluded))


if __name__ == '__main__':
    unittest.main()
