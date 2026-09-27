"""Synthetic pixels and committed inventory metadata only; no native payload is opened."""
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

ALL_ENDPOINTS = [{'colorScheme': scheme, 'activation': pose}
                 for scheme in ('light', 'dark') for pose in ('active', 'inactive')]


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE).decode().strip()


class ExposureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='w41-exposure-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / 'repo'
        self.root.mkdir()
        git(self.root, 'init', '-q')
        git(self.root, 'config', 'user.email', 'test@example.invalid')
        git(self.root, 'config', 'user.name', 'Synthetic test')
        git(self.root, 'config', 'gc.auto', '0')
        for name in runner.X6_SOURCES:
            self.put(name, (runner.ROOT/name).read_text())
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
        from test_domain import DOMAIN, evidence
        evidence(self, self.cells if hasattr(self, 'cells') else self.rendered)
        self.put('claim.json', {'endpoints': ALL_ENDPOINTS, 'domain': DOMAIN,
                                'numericalDomain':'uniform-backdrop', 'renderedDeepDomain':'uniform-backdrop'})
        self.put(str(runner.HERE.relative_to(runner.ROOT) / 'manifest.schema.json'),
                 (runner.HERE / 'manifest.schema.json').read_text())
        self.put('parameters.json', {'gain': 1.25})
        self.put('predictions.json', {'cells': {c: [80, 90, 100] for c in self.cells}})
        images = {}
        for i, cell in enumerate(self.cells):
            Image.new('RGB', (2, 2), (80, 90, 100)).save(self.root / f'{i}.png')
            self.put(f'{i}.json', {'rgb': [80, 90, 100]})
            images[cell] = {'png': f'{i}.png', 'projection': f'{i}.json'}
        self.put('rendered.json', {'cells': images})
        self.put('survival.json', {kind: {c: True for c in self.cells}
                                  for kind in ('numerical', 'rendered', 'veto')})
        self.put('scorer.py', '# Synthetic calibration scorer implementation\n')
        self.put('declaration.txt', 'synthetic calibration stand-in, not W41 evidence')
        self.put('closure.json', {'synthetic': True})
        self.commit()
        self.candidates = [{'id': 'standin', 'parameters': 'parameters.json',
                            'predictions': 'predictions.json', 'rendered': 'rendered.json',
                            'survival': 'survival.json', 'claimScope': 'claim.json',
                            'domainEvidence':'domain-evidence.json'}]
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
        git(self.root, 'commit', '--allow-empty', '-qm', 'Synthetic stand-in')

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
                                  'worstResidualCodes': residual, **({'vetoPass': True} if kind == 'rendered' else {})}
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
                'constraintsPass': True, 'vetoPass': True}
            return scores
        result = self.run_exposure(score=censored)
        self.assertEqual(result['coverage']['standin']['rendered'],
                         {'measured': 1, 'censored': 1, 'total': 2, 'fraction': 0.5,
                          'scoredTotal': 2, 'notClaimed': 0})
        self.assertEqual(self.events(), ['begin', 'complete'])

    def test_censoring_cannot_hide_an_uncensored_or_rail_failure(self):
        def censored(request):
            scores = self.score(request)
            scores['standin']['rendered'][self.cells[0]] = {
                'status': 'UNMEASURED', 'reason': 'censored', 'passes': None,
                'constraintsPass': False, 'vetoPass': True}
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
                             {'status': 'measured', 'passes': True, 'worstResidualCodes': 0, 'vetoPass': True})
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
        config = runner.load(self.root/'config.json')
        self.put('config.json', dict(config, fixtures='generated-backdrops'))
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
                record = __import__('test_domain').records(self.wave,[identity],self.root)[identity]
                for name, value in [('cell',record['descriptor']), ('report',record['report'])]:
                    (directory / f'{name}__webgpu.json').write_text(json.dumps(value))
        config = dict(scenes=self.wave.scenes_sha, split=self.wave.split_sha,
                      generation=self.manifest['generation'], instrument='standin', closure='standin',
                      candidate='standin')
        with runner.boundary.Receipt(self.log, config).expose() as token:
            request = runner.CaptureRequest(self.wave, token, self.root, self.manifest,
                                            'standin', tuple(self.cells), self.output)
            with patch.object(runner.subprocess, 'run', side_effect=launch), \
                    patch.object(runner, 'observe_x6', side_effect=__import__('test_x6').reading):
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


    def freeze_runtime(self):
        self.put('packages/policy/dist/index.js', 'export const policy = 1;')
        self.put('packages/policy/dist/nested/rule.js', 'export const rule = 2;')
        mapping = {}
        for name in ('index.js', 'nested/rule.js'):
            actual = 'packages/policy/dist/' + name
            snapshot = 'packages/calibration/results/synthetic-runtime/' + name
            self.put(snapshot, (self.root / actual).read_text())
            mapping[actual] = snapshot
        self.put('config.json', dict(runner.load(self.root/'config.json'), runtimeArtifacts=mapping))
        self.commit()
        self.manifest = runner.freeze(self.root, self.wave, self.candidates,
                                      config='config.json', scorer='scorer.py',
                                      declaration='declaration.txt', closure='closure.json',
                                      dry_cells=self.cells)
        self.put('frozen.json', self.manifest)
        self.commit()
        return mapping

    def test_compiled_policy_bytes_are_bound_separately_from_sources(self):
        mapping = self.freeze_runtime()
        self.assertEqual(self.manifest['runtimeArtifacts'], mapping)
        for actual, snapshot in mapping.items():
            self.assertEqual(self.manifest['files'][snapshot], runner.sha(self.root / actual))
            self.assertNotIn(actual, self.manifest['sourceFiles'])
        self.run_exposure()
        renderer = json.loads(self.log.read_text().splitlines()[0])['configuration']['renderer']
        self.assertEqual(renderer['runtimeArtifacts'], mapping)

    def test_changed_compiled_policy_refused_before_begin(self):
        self.freeze_runtime()
        self.put('packages/policy/dist/index.js', 'export const policy = 999;')
        with self.assertRaisesRegex(ValueError, 'runtime artifact'):
            self.run_exposure()
        self.assertFalse(self.log.exists())
        self.assertFalse(self.calls)

    def test_added_compiled_policy_module_refused_before_begin(self):
        self.freeze_runtime()
        self.put('packages/policy/dist/extra.js', 'export const extra = 1;')
        with self.assertRaisesRegex(ValueError, 'runtime artifact'):
            self.run_exposure()
        self.assertFalse(self.log.exists())
        self.assertFalse(self.calls)

    def test_deleted_compiled_policy_module_refused_before_begin(self):
        self.freeze_runtime()
        (self.root / 'packages/policy/dist/nested/rule.js').unlink()
        with self.assertRaisesRegex(ValueError, 'runtime artifact'):
            self.run_exposure()
        self.assertFalse(self.log.exists())

    def test_uncommitted_runtime_snapshot_refused(self):
        mapping = self.freeze_runtime()
        actual, snapshot = next(iter(mapping.items()))
        self.put(actual, 'export const changed = 2;')
        self.put(snapshot, 'export const changed = 2;')
        with self.assertRaisesRegex(ValueError, 'uncommitted frozen input'):
            self.run_exposure()
        self.assertFalse(self.log.exists())

    def test_policy_mutated_in_capture_refused_before_projection(self):
        self.freeze_runtime()
        def mutate(request):
            paths = self.capture(request)
            self.put('packages/policy/dist/index.js', 'export const policy = 99;')
            return paths
        with patch.object(self, 'project', side_effect=AssertionError('projection must not run')):
            with self.assertRaisesRegex(ValueError, 'runtime artifact'):
                self.run_exposure(capture=mutate)
        self.assert_failed_evidence('runtime artifact')

    def test_policy_mutated_in_projection_refused_before_scoring(self):
        self.freeze_runtime()
        def mutate(cell, path):
            self.put('packages/policy/dist/index.js', 'export const policy = 99;')
            return {'rgb': [80, 90, 100]}
        with patch.object(self, 'project', side_effect=mutate), \
                patch.object(self, 'score', side_effect=AssertionError('score must not run')):
            with self.assertRaisesRegex(ValueError, 'runtime artifact'):
                self.run_exposure()
        self.assert_failed_evidence('runtime artifact')

    def test_policy_mutated_in_score_preserves_returned_evidence(self):
        self.freeze_runtime()
        returned = {}
        def mutate(request):
            returned.update(self.score(request))
            self.put('packages/policy/dist/index.js', 'export const policy = 99;')
            return returned
        with self.assertRaisesRegex(ValueError, 'runtime artifact'):
            self.run_exposure(score=mutate)
        self.assert_failed_evidence('runtime artifact', returned)


class ProductionScopeTests(unittest.TestCase):
    """Exercise freeze's production branch in scratch with real admission metadata.

    Only the location guards move. All cells, split, inventory bytes, coverage and
    commit checks run unchanged. PNGs/backdrops are generated solid stand-ins;
    no production exposure, receipt, archive Reader or referenced payload is used.
    """
    put = ExposureTests.put
    commit = ExposureTests.commit

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='w41-production-scope-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        git(self.root, 'init', '-q')
        git(self.root, 'config', 'user.email', 'test@example.invalid')
        git(self.root, 'config', 'user.name', 'Synthetic test')
        git(self.root, 'config', 'gc.auto', '0')
        for name in runner.X6_SOURCES:
            self.put(name, (runner.ROOT/name).read_text())
        real = runner.boundary.default_wave()
        for name, value in [('scenes.json', real.spec), ('split.json', real.split)]:
            self.put(name, value)
        self.put('pins.json', {'scenesSha256': runner.sha(self.root / 'scenes.json'),
                              'splitSha256': runner.sha(self.root / 'split.json')})
        self.wave = runner.boundary.Wave(self.root / 'scenes.json', self.root / 'split.json',
                                        self.root / 'pins.json')
        self.inventory = ('packages/calibration/results/'
                          '2026-09-26-w39-g1-colour-edge-sitting/archive/inventory.json')
        data = (runner.ROOT / self.inventory).read_bytes()
        self.assertEqual(runner.sha(runner.ROOT / self.inventory), runner.INVENTORY_SHA)
        # Read only entries[].cell; no path in this document is followed.
        admitted = {entry['cell'] for entry in json.loads(data)['entries']}
        self.put(self.inventory, data.decode())
        self.numerical = sorted(set(runner.cells_for(self.wave, runner.boundary.ROLES)) & admitted)
        self.rendered = sorted(set(runner.cells_for(self.wave, runner.boundary.ROLES, True)) & admitted)
        self.expected = {'numerical': self.numerical, 'rendered': self.rendered}
        from test_domain import DOMAIN, evidence
        evidence(self, self.cells if hasattr(self, 'cells') else self.rendered)
        self.put('claim.json', {'endpoints': ALL_ENDPOINTS, 'domain': DOMAIN,
                                'numericalDomain':'uniform-backdrop', 'renderedDeepDomain':'uniform-backdrop'})
        self.put(str(runner.HERE.relative_to(runner.ROOT) / 'manifest.schema.json'),
                 (runner.HERE / 'manifest.schema.json').read_text())
        self.put('parameters.json', {'gain': 1})
        self.put('predictions.json', {'cells': {c: [80, 90, 100] for c in self.numerical}})
        images, backgrounds = {}, {}
        for scale in (1, 2):
            size = (self.wave.spec['canvas']['width'] * scale,
                    self.wave.spec['canvas']['height'] * scale)
            Image.new('RGB', size, (80, 90, 100)).save(self.root / f'{scale}x.png')
        self.put('projection.json', {'synthetic': True})
        for cell in self.rendered:
            scale = 2 if '-2x-' in cell else 1
            images[cell] = {'png': f'{scale}x.png', 'projection': 'projection.json'}
            background = self.wave.scenes[cell.split('/', 1)[1]]['background']
            backgrounds[f'{background}@{scale}x'] = f'{scale}x.png'
        self.put('backdrops/manifest.json', {'backgrounds': backgrounds})
        for scale in (1, 2):
            (self.root / f'backdrops/{scale}x.png').write_bytes(
                (self.root / f'{scale}x.png').read_bytes())
        self.put('rendered.json', {'cells': images})
        self.put('survival.json', {kind: {c: True for c in cells
                 if self.wave.roles[c.split('/', 1)[1]] != 'holdout'}
                 for kind, cells in {**self.expected, 'veto': self.rendered}.items()})
        survival = runner.load(self.root/'survival.json')
        for cell in self.numerical:
            if self.wave.roles[cell.split('/')[1]] == 'holdout':
                continue
            background = self.wave.spec['backgrounds'][self.wave.scenes[cell.split('/')[1]]['background']]
            if background['kind'] != 'solid':
                survival['numerical'][cell] = {'status':'not claimed (structured backdrop)',
                    'passes':None, 'score':{'status':'measured','passes':False,'diagnostic':'S0'}}
                if cell in survival['rendered']:
                    survival['rendered'][cell] = {'status':'not claimed (structured backdrop)',
                        'passes':None, 'score':{'status':'measured','passes':False}}
        self.put('survival.json',survival)
        self.put('scorer.py', '# synthetic; never imported in production scope tests')
        self.here = self.root / 'packages/calibration/results/2026-09-27-w41-g1-identification/exposure'
        g0 = self.root / 'packages/calibration/results/2026-09-27-w41-g0-declaration'
        self.declaration = str((g0 / 'bounds-declaration.txt').relative_to(self.root))
        self.closure = str((g0 / 'closure.json').relative_to(self.root))
        self.put(self.declaration, 'synthetic declaration, not evidence')
        self.put(self.closure, {'boundsDeclarationSha256': runner.sha(self.root / self.declaration)})
        boundary_path = self.root / runner.BOUNDARY_PATH.relative_to(runner.ROOT)
        for path in (runner.BOUNDARY_PATH, runner.BOUNDARY_PATH.parent / 'w39_readers.py',
                     runner.BOUNDARY_PATH.parent / 'w39_archive.py',
                     runner.BOUNDARY_PATH.parent / 'pins.json', Path(runner.__file__)):
            self.put(str(path.relative_to(runner.ROOT)), path.read_text())
        self.mapping = {'packages/policy/dist/index.js':
                        'packages/calibration/results/synthetic-runtime/index.js'}
        for name in (*self.mapping, *self.mapping.values()):
            self.put(name, 'export const policy = 1;')
        self.config = {'fixtures': 'backdrops', 'runtimeArtifacts': self.mapping, 'candidates': {
            'standin': runner.load(self.root/'config.json')['candidates']['standin']}}
        self.put('config.json', self.config)
        self.candidates = [{'id': 'standin', 'parameters': 'parameters.json',
                            'predictions': 'predictions.json', 'rendered': 'rendered.json',
                            'survival': 'survival.json', 'claimScope': 'claim.json',
                            'domainEvidence':'domain-evidence.json'}]
        for name, value in [('ROOT', self.root), ('HERE', self.here),
                            ('BOUNDARY_PATH', boundary_path),
                            ('__file__', str(self.here / 'runner.py'))]:
            patcher = patch.object(runner, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.commit()

    def freeze(self):
        return runner.freeze(self.root, self.wave, self.candidates, config='config.json',
                             scorer='scorer.py', declaration=self.declaration, closure=self.closure)

    def test_production_scope_intersects_fixed_inventory_without_recutting_split(self):
        manifest = self.freeze()
        self.assertEqual(manifest['mode'], 'production')
        self.assertEqual(manifest['inventory'], self.inventory)
        self.assertEqual(manifest['files'][self.inventory], runner.INVENTORY_SHA)
        self.assertEqual(manifest['numericalCells'], self.numerical)
        self.assertEqual(manifest['renderedCells'], self.rendered)
        self.assertEqual((len(self.numerical), len(self.rendered)), (648, 600))
        for kind, cells in self.expected.items():
            holdout = [c for c in cells if self.wave.roles[c.split('/', 1)[1]] == 'holdout']
            self.assertEqual(len(holdout), 72 if kind == 'numerical' else 64)
            self.assertEqual(len(cells) - len(holdout), 576 if kind == 'numerical' else 536)
            declared = runner.cells_for(self.wave, runner.boundary.ROLES, kind == 'rendered')
            excluded = manifest['excludedCells'][kind]
            self.assertEqual(set(excluded), set(declared) - set(cells))
            self.assertEqual(len(excluded), 56 if kind == 'numerical' else 8)
            self.assertEqual(set(excluded.values()), {'not admitted by fixed archive inventory'})
            self.assertTrue(all(self.wave.roles[c.split('/', 1)[1]] == 'calibration'
                                for c in excluded))
        self.assertEqual(manifest['split'], self.wave.split_sha)
        self.assertEqual(manifest['runtimeArtifacts'], self.mapping)
        self.put('frozen.json', manifest)
        self.commit()
        self.assertEqual(runner.verify(self.root, self.wave, self.root / 'frozen.json',
                                       'production'), manifest)

    def test_missing_inventory_refuses_production_freeze(self):
        (self.root / self.inventory).unlink()
        with self.assertRaisesRegex(ValueError, 'inventory'):
            self.freeze()

    def test_committed_inventory_tampering_cannot_redefine_admission(self):
        value = runner.load(self.root / self.inventory)
        value['entries'] = value['entries'][1:]
        self.put(self.inventory, value)
        self.commit()
        with self.assertRaisesRegex(ValueError, 'inventory'):
            self.freeze()

    def test_production_rejects_admitted_prediction_or_survival_omissions(self):
        # Each branch must reach its own membership check, not fail on an earlier
        # missing generated artifact or on the old 704-cell declared scope.
        for name, kind in [('predictions.json', 'numerical'), ('rendered.json', 'rendered'),
                           ('survival.json', 'numerical'), ('survival.json', 'rendered')]:
            original = (self.root / name).read_text()
            data = json.loads(original)
            values = data[kind] if name == 'survival.json' else data['cells']
            removed = next(iter(values))
            del values[removed]
            self.put(name, data)
            self.commit()
            with self.subTest(name=name, kind=kind):
                with self.assertRaisesRegex(ValueError, kind + ' .*coverage mismatch') as error:
                    self.freeze()
                self.assertIn(removed, str(error.exception))
                self.assertNotIn('extra=[\'', str(error.exception))
            self.put(name, original)
            self.commit()

    def test_unadmitted_phase_probe_cannot_enter_predictions_or_survival(self):
        for name, kind in [('predictions.json', 'numerical'), ('rendered.json', 'rendered'),
                           ('survival.json', 'numerical'), ('survival.json', 'rendered')]:
            original = (self.root / name).read_text()
            data = json.loads(original)
            values = data[kind] if name == 'survival.json' else data['cells']
            extra = sorted(set(runner.cells_for(self.wave, runner.boundary.ROLES,
                                                kind == 'rendered')) - set(self.expected[kind]))[0]
            values[extra] = next(iter(values.values()))
            self.put(name, data)
            self.commit()
            with self.subTest(name=name, kind=kind):
                with self.assertRaisesRegex(ValueError, kind + ' .*coverage mismatch') as error:
                    self.freeze()
                self.assertIn(extra, str(error.exception))
                self.assertIn('missing=[]', str(error.exception))
            self.put(name, original)
            self.commit()

    def test_source_only_production_freeze_cannot_omit_runtime_mapping(self):
        del self.config['runtimeArtifacts']
        self.put('config.json', self.config)
        self.commit()
        with self.assertRaisesRegex(ValueError, 'runtime artifact'):
            self.freeze()

    def test_missing_policy_build_refuses_production_freeze(self):
        (self.root / 'packages/policy/dist/index.js').unlink()
        with self.assertRaisesRegex(ValueError, 'runtime artifact'):
            self.freeze()

    def test_incomplete_policy_module_inventory_refuses_production_freeze(self):
        self.put('packages/policy/dist/extra.js', 'export const extra = 1;')
        with self.assertRaisesRegex(ValueError, 'runtime artifact'):
            self.freeze()

    def test_stale_policy_build_refuses_production_freeze(self):
        self.put('packages/policy/dist/index.js', 'export const policy = 0;')
        with self.assertRaisesRegex(ValueError, 'runtime artifact'):
            self.freeze()


if __name__ == '__main__':
    unittest.main(verbosity=2)
