"""Synthetic calibration stand-ins only: no native inventory or capture is opened."""
import json
import os
import signal
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import runner


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE).decode().strip()


class ExposureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='w41-exposure-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        git(self.root, 'init', '-q')
        git(self.root, 'config', 'user.email', 'test@example.invalid')
        git(self.root, 'config', 'user.name', 'Synthetic test')
        real = runner.boundary.default_wave()  # Metadata only; never constructs a Reader.
        self.put('scenes.json', real.spec)
        self.put('split.json', real.split)
        self.put('pins.json', {'scenesSha256': runner.sha(self.root / 'scenes.json'),
                              'splitSha256': runner.sha(self.root / 'split.json')})
        self.wave = runner.boundary.Wave(self.root / 'scenes.json', self.root / 'split.json',
                                        self.root / 'pins.json')
        allowed = self.wave.launch_scenes(('calibration',))
        self.cells = sorted(c for c in self.wave.cells if c.split('/', 1)[1] in allowed)[:2]
        self.put('packages/renderer-webgpu/src/standin.txt', 'synthetic renderer revision 1')
        self.put('config.json', {'profiles': {}})
        self.put('parameters.json', {'gain': 1.25})
        self.put('predictions.json', {'cells': {c: [80, 90, 100] for c in self.cells}})
        images = {}
        for i, cell in enumerate(self.cells):
            Image.new('RGB', (2, 2), (80, 90, 100)).save(self.root / f'{i}.png')
            self.put(f'{i}.json', {'rgb': [80, 90, 100]})
            images[cell] = {'png': f'{i}.png', 'projection': f'{i}.json'}
        self.put('rendered.json', {'cells': images})
        self.put('survival.json', {kind: {c: True for c in self.cells}
                                  for kind in ('numerical', 'rendered')})
        self.put('scorer.py', '# Synthetic calibration scorer implementation\n')
        self.put('declaration.txt', 'synthetic calibration stand-in, not W41 evidence')
        self.put('closure.json', {'synthetic': True})
        self.commit()
        self.candidates = [{'id': 'standin', 'parameters': 'parameters.json',
                            'predictions': 'predictions.json', 'rendered': 'rendered.json',
                            'survival': 'survival.json'}]
        self.manifest = runner.freeze(self.root, self.wave, self.candidates,
                                      config='config.json', scorer='scorer.py',
                                      declaration='declaration.txt', closure='closure.json',
                                      dry_cells=self.cells)
        self.put('frozen.json', self.manifest)
        self.commit()
        self.log = Path(self.tmp.name) / 'scratch-receipt.jsonl'
        self.output = Path(self.tmp.name) / 'capture'
        self.score_report = self.log.with_name(self.log.stem + '-scores.json')
        self.calls = []

    def put(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if not isinstance(value, str) else value)

    def commit(self):
        git(self.root, 'add', '.')
        git(self.root, 'commit', '-qm', 'Synthetic stand-in')

    def capture(self, request):
        request.authorization.check(self.wave)
        self.assertEqual(self.events(), ['begin'])
        with self.assertRaises(PermissionError):
            request.authorization.check(self.wave, runner.INVENTORY_SHA)
        self.calls.append(request)
        answer = {}
        for index, cell in enumerate(request.cells):
            path = request.output / f'{index}.png'
            Image.new('RGB', (2, 2), (80, 90, 100)).save(path)
            answer[cell] = path
        return answer

    def project(self, cell, path):
        with Image.open(path) as image:
            return {'rgb': list(image.convert('RGB').getpixel((0, 0)))}

    def score(self, request):
        request.authorization.check(self.wave)
        self.assertEqual(self.events(), ['begin'])
        # A numerical prediction AND each freshly written image are measured
        # against independent synthetic RGB observations; no native payload exists.
        result = {}
        for candidate, artifact in request.candidates.items():
            numerical = runner.load(request.root / artifact['predictions'])['cells']
            result[candidate] = {}
            for kind, cells in [('numerical', request.numerical_cells),
                                ('rendered', request.rendered_cells)]:
                rows = {}
                for cell in cells:
                    value = (numerical[cell] if kind == 'numerical' else
                             self.project(cell, request.captures[candidate][cell])['rgb'])
                    residual = max(abs(a - b) for a, b in zip(value, [80, 90, 100], strict=True))
                    rows[cell] = {'status': 'measured', 'passes': residual <= 1,
                                  'worstResidualCodes': residual}
                result[candidate][kind] = rows
        return result

    def events(self):
        return [json.loads(line)['event'] for line in self.log.read_text().splitlines()]

    def run_exposure(self, capture=None, score=None):
        return runner.run_synthetic(self.root, self.wave, self.root / 'frozen.json',
                                    self.log, self.output, capture or self.capture,
                                    self.project, score or self.score)

    def test_capture_and_score_are_inside_authorization_and_receipt_binds_renderer(self):
        result = self.run_exposure()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['renderedCells'], 2)
        self.assertEqual(self.events(), ['begin', 'complete'])
        with self.assertRaises(PermissionError):
            self.calls[0].authorization.check(self.wave)
        record = json.loads(self.log.read_text().splitlines()[0])['configuration']
        self.assertEqual(record['renderer']['revision'], self.manifest['revision'])
        self.assertEqual(record['renderer']['configuration'], self.manifest['files']['config.json'])
        self.assertIn('0.png', record['frozenFiles'])
        self.assertIn('parameters.json', record['frozenFiles'])

    def test_backend_failure_spends_scratch_and_retry_never_captures(self):
        def fail(request):
            self.calls.append(request)
            raise RuntimeError('synthetic backend failed')
        with self.assertRaisesRegex(RuntimeError, 'backend failed'):
            self.run_exposure(capture=fail)
        self.assertEqual(self.events(), ['begin', 'failed'])
        with self.assertRaises(PermissionError):
            self.run_exposure()
        self.assertEqual(len(self.calls), 1)

    def test_source_config_and_prediction_mutations_refused_before_begin(self):
        for name in ['packages/renderer-webgpu/src/standin.txt', 'config.json',
                     'predictions.json', '0.png', 'scorer.py']:
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                with self.assertRaises(ValueError):
                    self.run_exposure()
                self.assertFalse(self.log.exists())
                self.assertFalse(self.calls)
                path.write_bytes(original)

    def test_added_renderer_source_refused_before_begin(self):
        self.put('packages/renderer-webgpu/src/unfrozen.ts', 'export const changed = true;')
        with self.assertRaises(ValueError):
            self.run_exposure()
        self.assertFalse(self.log.exists())

    def test_wrong_or_missing_capture_cells_spend_attempt(self):
        def wrong(request):
            return {'not/a/declared-cell': request.output / 'missing.png'}
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.run_exposure(capture=wrong)
        self.assertEqual(self.events(), ['begin', 'failed'])

    def test_changed_render_refuses_even_if_projection_would_hide_it(self):
        def changed(request):
            paths = self.capture(request)
            Image.new('RGB', (2, 2), (81, 90, 100)).save(next(iter(paths.values())))
            return paths
        with self.assertRaisesRegex(ValueError, 'rendered prediction'):
            self.run_exposure(capture=changed)
        self.assertEqual(self.events(), ['begin', 'failed'])

    def test_missing_native_score_is_not_closure(self):
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.run_exposure(score=lambda request: {})
        self.assertEqual(self.events(), ['begin', 'failed'])

    def test_unmeasured_or_failed_score_never_closes(self):
        def unmeasured(request):
            scores = self.score(request)
            scores['standin']['rendered'][self.cells[0]] = {'status': 'UNMEASURED', 'passes': True}
            return scores
        with self.assertRaisesRegex(ValueError, 'UNMEASURED'):
            self.run_exposure(score=unmeasured)
        self.assertEqual(self.events(), ['begin', 'failed'])

    def test_censored_holdout_summary_is_excluded_and_coverage_reported(self):
        def censored(request):
            scores = self.score(request)
            scores['standin']['rendered'][self.cells[0]] = {
                'status': 'UNMEASURED', 'reason': 'censored', 'passes': None,
                'constraintsPass': True}
            return scores
        result = self.run_exposure(score=censored)
        self.assertEqual(result['coverage']['standin']['rendered'],
                         {'measured': 1, 'censored': 1, 'total': 2, 'fraction': 0.5})
        self.assertEqual(self.events(), ['begin', 'complete'])

    def test_censoring_cannot_hide_an_uncensored_or_rail_failure(self):
        def censored(request):
            scores = self.score(request)
            scores['standin']['rendered'][self.cells[0]] = {
                'status': 'UNMEASURED', 'reason': 'censored', 'passes': None,
                'constraintsPass': False}
            return scores
        with self.assertRaisesRegex(ValueError, 'closure failed'):
            self.run_exposure(score=censored)
        self.assertEqual(self.events(), ['begin', 'failed'])

    def test_wrong_numerical_prediction_fails_even_with_matching_render(self):
        self.put('predictions.json', {'cells': {c: [82, 90, 100] for c in self.cells}})
        self.commit()
        self.manifest = runner.freeze(self.root, self.wave, self.candidates,
                                      config='config.json', scorer='scorer.py',
                                      declaration='declaration.txt', closure='closure.json',
                                      dry_cells=self.cells)
        self.put('frozen.json', self.manifest)
        self.commit()
        with self.assertRaisesRegex(ValueError, 'closure failed'):
            self.run_exposure()
        self.assertEqual(self.events(), ['begin', 'failed'])

    def test_projection_mismatch_spends_attempt(self):
        with self.assertRaisesRegex(ValueError, 'projection'):
            runner.run_synthetic(self.root, self.wave, self.root / 'frozen.json',
                                 self.log, self.output, self.capture,
                                 lambda cell, path: {'rgb': [80, 90, 101]}, self.score)
        self.assertEqual(self.events(), ['begin', 'failed'])

    def test_mutation_during_scoring_cannot_change_successful_capture(self):
        def mutate(request):
            scores = self.score(request)
            path = next(iter(request.captures['standin'].values()))
            Image.new('RGB', (2, 2), (80, 90, 101)).save(path)
            return scores
        with self.assertRaisesRegex(ValueError, 'capture mutated'):
            self.run_exposure(score=mutate)
        self.assertEqual(self.events(), ['begin', 'failed'])

    def assert_failed_evidence(self, reason, scores=None):
        result = runner.load(self.output / 'result.json')
        self.assertEqual(result['status'], 'failed')
        self.assertIn(reason, result['error']['message'])
        self.assertEqual(result['manifestSha256'], runner.sha(self.root / 'frozen.json'))
        self.assertEqual(self.events(), ['begin', 'failed'])
        if scores is None:
            self.assertNotIn('scores', result)
            self.assertFalse(self.score_report.exists())
        else:
            self.assertEqual(result['scores'], scores)
            report = runner.load(self.score_report)
            self.assertEqual(report['scores'], scores)
            self.assertEqual(report['manifestSha256'], result['manifestSha256'])
            self.assertEqual(set(report['captures']['standin']), set(self.cells))
        with self.assertRaises(PermissionError):
            self.run_exposure()
        return result

    def test_full_failed_score_is_fsynced_before_aggregation(self):
        returned = {}
        synced = set()
        original_fsync, original_coverage = os.fsync, runner.coverage
        def fsync(fd):
            original_fsync(fd)
            synced.add(os.fstat(fd).st_ino)
        def coverage(actual, expected, label):
            if label == 'native candidate scores':
                report = self.score_report
                self.assertEqual(runner.load(report)['scores'], returned)
                self.assertIn(report.stat().st_ino, synced)
            return original_coverage(actual, expected, label)
        def fail(request):
            returned.update(self.score(request))
            returned['standin']['rendered'][self.cells[0]].update(
                passes=False, worstResidualCodes=3,
                bins=[{'population': 3, 'status': 'UNMEASURED',
                       'repeats': [81, 82, 83, 84, 85, 86, 87]}])
            return returned
        with patch.object(runner.os, 'fsync', side_effect=fsync), \
                patch.object(runner, 'coverage', side_effect=coverage):
            with self.assertRaisesRegex(ValueError, 'closure failed'):
                self.run_exposure(score=fail)
        self.assert_failed_evidence('closure failed', returned)

    def test_process_kill_after_score_persistence_retains_authoritative_report(self):
        original_coverage = runner.coverage
        def kill_before_verdict(actual, expected, label):
            if label == 'native candidate scores':
                os.kill(os.getpid(), signal.SIGKILL)
            return original_coverage(actual, expected, label)
        pid = os.fork()
        if pid == 0:
            try:
                with patch.object(runner, 'coverage', side_effect=kill_before_verdict):
                    self.run_exposure()
            finally:
                os._exit(1)
        _, status = os.waitpid(pid, 0)
        self.assertTrue(os.WIFSIGNALED(status))
        self.assertEqual(os.WTERMSIG(status), signal.SIGKILL)
        report = runner.load(self.score_report)
        self.assertEqual(report['status'], 'scored')
        self.assertEqual(report['manifestSha256'], runner.sha(self.root / 'frozen.json'))
        self.assertEqual(set(report['scores']['standin']['rendered']), set(self.cells))
        for cell in self.cells:
            self.assertEqual(report['scores']['standin']['rendered'][cell],
                             {'status': 'measured', 'passes': True, 'worstResidualCodes': 0})
            capture = report['captures']['standin'][cell]
            self.assertEqual(capture['sha256'], runner.sha(capture['path']))
        self.assertEqual(self.events(), ['begin'])
        self.assertFalse((self.output / 'result.json').exists())
        with self.assertRaises(PermissionError):
            self.run_exposure()

    def test_freeze_verification_failure_preserves_returned_score(self):
        returned = {}
        def mutate(request):
            returned.update(self.score(request))
            self.put('parameters.json', {'gain': 2})
            return returned
        with self.assertRaises(ValueError):
            self.run_exposure(score=mutate)
        self.assert_failed_evidence('parameters.json', returned)

    def test_scorer_exception_has_failed_verdict_without_invented_scores(self):
        def fail(request):
            raise RuntimeError('synthetic scorer interrupted')
        with self.assertRaisesRegex(RuntimeError, 'scorer interrupted'):
            self.run_exposure(score=fail)
        result = self.assert_failed_evidence('scorer interrupted')
        self.assertEqual(result['error']['type'], 'RuntimeError')
        self.assertEqual(set(result['captures']['standin']), set(self.cells))

    def test_capture_and_callback_expected_hash_mutation_cannot_complete(self):
        returned = {}
        def mutate(request):
            returned.update(self.score(request))
            cell = self.cells[0]
            path = request.captures['standin'][cell]
            Image.new('RGB', (2, 2), (80, 90, 101)).save(path)
            artifact = runner.load(request.root / request.candidates['standin']['rendered'])
            request.manifest['files'][artifact['cells'][cell]['png']] = runner.sha(path)
            return returned
        with self.assertRaisesRegex(ValueError, 'mutated'):
            self.run_exposure(score=mutate)
        self.assert_failed_evidence('mutated', returned)

    def test_candidate_mapping_mutation_cannot_erase_required_scores(self):
        def mutate(request):
            request.candidates.clear()
            return {}
        with self.assertRaisesRegex(ValueError, 'mutated'):
            self.run_exposure(score=mutate)
        self.assert_failed_evidence('mutated', {})

    def test_capture_mapping_mutation_cannot_replace_scored_image(self):
        returned = {}
        def mutate(request):
            returned.update(self.score(request))
            path = request.captures['standin'][self.cells[0]]
            Image.new('RGB', (2, 2), (80, 90, 101)).save(path)
            request.captures['standin'][self.cells[0]] = self.root / '0.png'
            return returned
        with self.assertRaisesRegex(ValueError, 'mutated'):
            self.run_exposure(score=mutate)
        result = self.assert_failed_evidence('mutated', returned)
        path = Path(result['captures']['standin'][self.cells[0]]['path'])
        self.assertTrue(path.is_relative_to(self.output.resolve()))

    def test_capture_backend_cannot_rewrite_manifest_hash(self):
        def mutate(request):
            paths = self.capture(request)
            path = paths[self.cells[0]]
            with Image.open(path) as image:
                image.putpixel((1, 1), (80, 90, 101))
                image.save(path)
            request.manifest['files']['0.png'] = runner.sha(path)
            return paths
        with self.assertRaisesRegex(ValueError, 'mutated'):
            self.run_exposure(capture=mutate)
        self.assert_failed_evidence('mutated')

    def test_real_backend_launches_web_only_driver_inside_receipt(self):
        profiles = {cell.split('/', 1)[0]: {'material': 'parameters.json',
                                           'receded': 'parameters.json'} for cell in self.cells}
        self.put('config.json', {'fixtures': 'generated-backdrops',
                                 'candidates': {'standin': {'profiles': profiles}}})
        self.output.mkdir()
        invocations = []
        def launch(command, env, check):
            # Stand in for the process, not for capture_web: this exercises its
            # command, file parsing, profile grouping and provenance checks.
            self.assertEqual(self.events(), ['begin'])
            self.assertIn('scripts/capture-web.ts', command)
            self.assertNotIn('compare', command)
            self.assertEqual(env['VITREA_ALLOW_FALLBACK_ADAPTER'], '0')
            invocations.append(command)
            destination = Path(command[command.index('--out') + 1])
            for identity in self.cells:
                profile, sid = identity.split('/', 1)
                directory = destination / sid
                directory.mkdir(parents=True)
                Image.new('RGB', runner.dimension(self.wave, identity), (80, 90, 100)).save(
                    directory / (sid + '__webgpu.png'))
                (directory / 'cell__webgpu.json').write_text(json.dumps(dict(
                    sceneId=sid, renderer='webgpu', engine='chromium', colorSpace='srgb',
                    pixelSize=runner.dimension(self.wave, identity), deterministic=True, repeatNoise=0)))
                material = {'sha256': self.manifest['files']['parameters.json'][:12]}
                (directory / 'report__webgpu.json').write_text(json.dumps(dict(
                    fallback=None, problems=[], materialProfile=material, recededProfile=material)))
        config = dict(scenes=self.wave.scenes_sha, split=self.wave.split_sha,
                      generation=self.manifest['generation'], instrument='standin', closure='standin',
                      candidate='standin')
        with runner.boundary.Receipt(self.log, config).expose() as token:
            request = runner.CaptureRequest(self.wave, token, self.root, self.manifest,
                                            'standin', tuple(self.cells), self.output)
            with patch.object(runner.subprocess, 'run', side_effect=launch):
                paths = runner.capture_web(request)
        self.assertEqual(set(paths), set(self.cells))
        self.assertEqual(len(invocations), 1)
        with patch.object(runner.subprocess, 'run') as process:
            with self.assertRaises(PermissionError):
                runner.capture_web(request)
            process.assert_not_called()

    def test_synthetic_mode_cannot_open_production_log(self):
        with self.assertRaises(PermissionError):
            runner.run_synthetic(self.root, self.wave, self.root / 'frozen.json',
                                 runner.PRODUCTION_LOG, self.output, self.capture,
                                 self.project, self.score)
        self.assertFalse(self.calls)

    def test_freeze_rejects_missing_predictions_and_nonfinite_payload(self):
        for value in [{'cells': {}}, {'cells': {c: [float('nan')] for c in self.cells}}]:
            self.put('predictions.json', value)
            self.commit()
            with self.assertRaises(ValueError):
                runner.freeze(self.root, self.wave, self.candidates,
                              config='config.json', scorer='scorer.py',
                              declaration='declaration.txt', closure='closure.json',
                              dry_cells=self.cells)


if __name__ == '__main__':
    unittest.main(verbosity=2)
