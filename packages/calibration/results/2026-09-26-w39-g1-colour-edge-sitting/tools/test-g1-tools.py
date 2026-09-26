#!/usr/bin/env python3.12
"""Tests of W39 G1's two new producer tools on the ADMITTED preflight captures (c9a §5.185).

The preflight is the only W39 native capture admitted before the bed, and its runs have the
shape the tools meet in the bed: run 1 holds more cells than run 2 (run 2 is the phase-zero
pair repeated at the pass's end), exactly as a bed pass's run 1 holds the colour references
runs 2-7 lack. So:

- `materialize-probe.py` is driven through the canonical `cli/materialize.ts` over each
  preflight pass's run 2 (given twice, because materialize.ts needs two runs and the preflight
  has one after run 1; the bed has six), then run 1 is folded in as the further vote on the
  shared cells, then the run-1-only cells are added and the bed partitioned by a stand-in role
  map that puts a cell in each identification role. The fold is also driven with a run 1 whose
  bytes differ (recorded) and with runs 2..N that disagree (refused). And the premise of the
  fold — that run 1's declaration equals runs 2-7's on every shared cell — is checked against
  pass-spec for all four bed passes;
- `report-bars.py` reads a real archive written by G0's `w39_archive.produce` from the two
  runs of each scale's phase-zero glass cell (byte-identical across the runs, so every bar is
  exactly 0.5), and from a copy with one run lifted by three codes (every unclipped bar 2.0).

No bed cell, no holdout and nothing about vitrea is read. The preflight runs live on the
capture machine (`~/vitrea-w39/run`); elsewhere the suite skips. Run: python3.12 test-g1-tools.py
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[1] / '2026-09-26-w39-g0-colour-edge-bed'
sys.path.insert(0, str(G0))
import w39_archive  # noqa: E402
from wave import Reader  # noqa: E402

RUN = Path.home() / 'vitrea-w39/run'
PROFILE = 'apple-macos-27.0-{s}x-light-standard-glass0.5'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


M = load('w39_materialize_probe', HERE / 'materialize-probe.py')
B = load('w39_report_bars', HERE / 'report-bars.py')
PRODUCER = load('w39_archive_producer', G0 / 'archive-producer.py')


def roots(scale):
    return [RUN / f'preflight-{scale}x' / f'run-{n}' for n in (1, 2)]


@unittest.skipUnless((RUN / 'preflight-2x/run-2/admission.json').exists(), 'preflight runs not on this machine')
class Materialise(unittest.TestCase):
    def run_pass(self, scale, tmp):
        stage, logs = tmp / 'bed', tmp / 'logs'
        stage.mkdir(); logs.mkdir()
        runs = roots(scale)
        for n, root in enumerate(runs, 1): M.check_run(root, f'preflight-{scale}x', n, None)
        M.stage_stub(stage, json.loads((runs[1] / 'manifest.json').read_text()))
        code = M.materialize_pass(f'preflight-{scale}x', [runs[1], runs[1]], stage,
                                  runs[1].parent / 'scenes-run-2.json', logs)
        self.assertEqual(code, 0, (logs / f'preflight-{scale}x.txt').read_text())
        return stage, runs

    def test_declarations_agree_on_every_shared_cell(self):
        P = load('w39_pass_spec', G0 / 'pass-spec.py')
        for pose in ('active', 'inactive'):
            for scale in (1, 2):
                one, two = P.derive(pose, scale, 1, (), False), P.derive(pose, scale, 2, (), False)
                shared = {s['id'] for s in two['scenes']}
                self.assertLess(shared, {s['id'] for s in one['scenes']})
                self.assertEqual([s for s in one['scenes'] if s['id'] in shared], two['scenes'])
                for s in two['scenes']:
                    self.assertEqual(one['components'][s['component']], two['components'][s['component']])
                    self.assertEqual(one['backgrounds'][s['background']], two['backgrounds'][s['background']])
                self.assertEqual(one['canvas'], two['canvas'])
                for run in range(3, 8): self.assertEqual(P.derive(pose, scale, run, (), False), two)

    def altered(self, root, tmp, sid, bit=1, tag='altered'):
        """A copy of a run with one cell's PNG changed at one pixel (a sub-code, noise-level change)."""
        copy_root = tmp / (tag + '-' + root.name); shutil.copytree(root, copy_root)
        entry = next(f for p in json.loads((root / 'manifest.json').read_text())['profiles']
                     for f in p['fixtures'] if f['sceneId'] == sid)
        image = np.asarray(Image.open(copy_root / entry['file']).convert('RGB')).copy()
        image[0, 0, 0] ^= bit
        Image.fromarray(image).save(copy_root / entry['file'])
        return copy_root

    def test_a_tie_over_runs_two_to_n_is_decided_by_all_runs(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t); run1, run2 = roots(2); sid = 'preflight-2x-zero__rest'
            odd2 = self.altered(run2, tmp, sid)
            stage, logs = tmp / 'bed', tmp / 'logs'; stage.mkdir(); logs.mkdir()
            M.stage_stub(stage, json.loads((run2 / 'manifest.json').read_text()))
            ties, folded = M.resolve_pass('tie', [run1, run2, odd2], stage, run2.parent / 'scenes-run-2.json', logs)
            cell = PROFILE.format(s=2) + '/' + sid
            self.assertEqual(ties, [cell])                       # 1-1 over runs 2..N: materialize.ts refused
            self.assertEqual([f['verdict'] for f in folded], ['agrees'])   # the opaque twin, unanimous
            manifest = json.loads((stage / 'manifest.json').read_text())
            entry = next(f for p in manifest['profiles'] for f in p['fixtures'] if f['sceneId'] == sid)
            self.assertEqual(entry['pluralityOfAllRuns']['runs'], 2)
            self.assertEqual(entry['pluralityOfAllRuns']['of'], 3)
            self.assertEqual(M.digest(stage / entry['file']), M.digest(run2 / entry['file']))
            self.assertEqual(len(M.staged_cells(stage)), 2)
            odd1 = self.altered(run1, tmp, sid, bit=2, tag='other')
            with self.assertRaisesRegex(ValueError, 'no strict plurality'):
                M.publish_plurality(tmp / 'bed', [odd1, run2, odd2], [cell])

    def test_first_run_folds_as_the_further_vote(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t); stage, (run1, run2) = self.run_pass(2, tmp)
            shared = M.staged_cells(stage)
            sid = 'preflight-2x-zero__rest'
            base = tmp / 'base'; shutil.copytree(stage, base)
            folded = M.fold_first_run(stage, run1, [run2, run2], shared)
            self.assertEqual(sorted(f['verdict'] for f in folded), ['agrees', 'agrees'])
            entry = next(f for p in json.loads((stage / 'manifest.json').read_text())['profiles']
                         for f in p['fixtures'] if f['sceneId'] == sid)
            self.assertEqual((entry['firstRun']['verdict'], entry['runsVoting']), ('agrees', 3))
            odd1 = self.altered(run1, tmp, sid)
            differs = tmp / 'differs'; shutil.copytree(base, differs)
            folded = {f['cell'].split('/', 1)[1]: f['verdict'] for f in M.fold_first_run(differs, odd1, [run2, run2], shared)}
            self.assertEqual(folded[sid], 'differs')
            odd2 = self.altered(run2, tmp, sid)
            refused = tmp / 'refused'; shutil.copytree(base, refused)
            with self.assertRaisesRegex(ValueError, 'not unanimous'):
                M.fold_first_run(refused, odd1, [run2, odd2], shared)

    def test_order_resolves_the_common_cells_then_adds_run_one_alone(self):
        for scale in (1, 2):
            with tempfile.TemporaryDirectory() as t:
                tmp = Path(t); stage, (run1, run2) = self.run_pass(scale, tmp)
                profile = PROFILE.format(s=scale)
                staged = M.cells_of(json.loads((stage / 'manifest.json').read_text()))
                pair = {(profile, f'preflight-{scale}x-zero__rest'), (profile, f'preflight-{scale}x-zero-opaque__rest')}
                self.assertEqual(staged, pair)          # exactly the cells runs 2..N captured
                M.fold_first_run(stage, run1, [run2, run2], pair)
                for _, sid in pair:                    # published bytes are a run's own
                    self.assertEqual(M.digest(stage / profile / f'{sid}.png'), M.digest(run1 / profile / f'{sid}.png'))
                refusing = tmp / 'refusing'; shutil.copytree(stage, refusing)
                with self.assertRaisesRegex(ValueError, 'not admissible'):
                    M.add_first_run_only(refusing, run1, run2, lambda sid: False)
                added = M.add_first_run_only(stage, run1, run2, lambda sid: True)
                self.assertEqual(len(added), 16)
                manifest = json.loads((stage / 'manifest.json').read_text())
                entries = {f['sceneId']: f for p in manifest['profiles'] for f in p['fixtures']}
                self.assertEqual(len(entries), 18)
                for cell in added:
                    sid = cell.split('/', 1)[1]
                    self.assertTrue(entries[sid]['singleRun'])
                    self.assertEqual(M.digest(stage / entries[sid]['file']), M.digest(run1 / entries[sid]['file']))
                for _, sid in pair:
                    self.assertNotIn('singleRun', entries[sid])
                    self.assertEqual(entries[sid]['firstRun']['verdict'], 'agrees')
                with self.assertRaisesRegex(ValueError, 'already materialised'):
                    M.add_first_run_only(stage, run1, run2, lambda sid: True)

                roles = {sid: 'validation' for sid in entries}
                roles[f'preflight-{scale}x-zero__rest'] = 'calibration'
                roles[f'preflight-{scale}x-zero-opaque__rest'] = 'holdout'
                expected = {profile + '/' + sid for sid in entries}
                with self.assertRaisesRegex(ValueError, 'membership'):
                    M.partition(stage, tmp / 'short', roles, expected - {next(iter(expected))}, {})
                out = tmp / 'probe'
                result = M.partition(stage, out, roles, expected, dict(scenesSha256='s', splitSha256='t'))
                self.assertEqual(result['perRole'], dict(calibration=1, holdout=1, validation=16))
                inventory = json.loads((out / 'inventory.json').read_text())
                for row in inventory['entries']:
                    self.assertEqual(Path(row['path']).parts[0], row['role'])
                    self.assertEqual(M.digest(out / row['path']), row['sha256'])
                public = json.loads((out / 'manifest.json').read_text())
                self.assertNotIn('bedProvenance', public)
                held = [f for p in public['profiles'] for f in p['fixtures'] if roles[f['sceneId']] == 'holdout']
                self.assertEqual(len(held), 1)
                self.assertLessEqual(set(held[0]) - {'file'}, set(M.HOLDOUT_PUBLIC))
                self.assertNotIn('firstRun', held[0])
                self.assertTrue((out / held[0]['file']).is_file())
                self.assertTrue((out / 'holdout/full-materializer-manifest.json').is_file())
                with self.assertRaisesRegex(Exception, ''):
                    M.partition(stage, out, roles, expected, {})   # never overwrites


class FakeWave:
    """The four attributes and one method the archive and the guarded reader use."""
    def __init__(self, cells, roles):
        self.cells, self.roles, self.scenes_sha, self.split_sha = set(cells), roles, 'a' * 64, 'b' * 64

    def select(self, roles, authorization=None):
        if 'holdout' in roles: raise PermissionError('holdout requires the wave receipt')
        return sorted(s for s, r in self.roles.items() if r in roles)


def records(scale, lift=None):
    """One archive group: the phase-zero glass cell from both preflight runs of `scale`."""
    sid = f'preflight-{scale}x-zero__rest'; profile = PROFILE.format(s=scale)
    doc = json.loads((RUN / f'preflight-{scale}x/scenes-run-1.json').read_text())
    scene = next(s for s in doc['scenes'] if s['id'] == sid)
    background = doc['backgrounds'][scene['background']]
    rows = []
    for n, root in enumerate(roots(scale), 1):
        manifest = json.loads((root / 'manifest.json').read_text())
        entry = next(f for p in manifest['profiles'] for f in p['fixtures'] if f['sceneId'] == sid)
        rgb = np.asarray(Image.open(root / entry['file']).convert('RGB'), dtype=np.uint8)
        if lift is not None and n == 2:
            rgb = np.clip(rgb.astype(int) + lift, 0, 255).astype(np.uint8)
        payload = dict(sceneId=sid, profile=profile, scale=scale, scheme='light', pose=scene.get('state'),
                       background=background, backgroundKind=background['kind'],
                       component=PRODUCER.merged_component(doc['components'][scene['component']], entry),
                       nativeOnly=False, rgb=rgb)
        rows.append(dict(cell=profile + '/' + sid, run=str(root), protocol='normal', admitted=True,
                         admission=dict(run=n), payload=payload,
                         inputHashes=dict(native=hashlib.sha256(rgb.tobytes()).hexdigest(),
                                          manifest=M.digest(root / 'manifest.json'))))
    return rows


@unittest.skipUnless((RUN / 'preflight-2x/run-2/admission.json').exists(), 'preflight runs not on this machine')
class Bars(unittest.TestCase):
    def archive(self, tmp, lift=None):
        groups = [records(s, lift) for s in (1, 2)]
        wave = FakeWave([g[0]['cell'] for g in groups], {g[0]['cell'].split('/', 1)[1]: 'calibration' for g in groups})
        w39_archive.produce(groups, wave, tmp / 'archive')
        return Reader(wave, tmp / 'archive', ('calibration',), None), [g[0]['cell'] for g in groups]

    def measured(self, report):
        self.assertEqual(report['status'], 'measured')
        for m in report['members']:
            yield m['deep']
            yield from (b for b in m['bins'] if b['status'] == 'measured')

    def test_identical_runs_give_exactly_half_a_code(self):
        with tempfile.TemporaryDirectory() as t:
            reader, cells = self.archive(Path(t))
            for cell in cells:
                report = B.cell_bars(reader, cell, 'normal')
                self.assertEqual((report['runs'], report['distinctStates']), (2, 1))
                bars = list(self.measured(report))
                self.assertGreater(len(bars), 20)
                for b in bars: self.assertEqual(b['barRGB'], [0.5, 0.5, 0.5])
                deep = report['members'][0]['deep']
                self.assertEqual(len(deep['runMediansRGB']), 2)
                self.assertTrue(all(lo <= hi for lo, hi in zip(deep['spatialMinimumRGB'], deep['spatialMaximumRGB'])))
                self.assertEqual(B.cell_bars(reader, cell, 'long')['status'], 'insufficient admitted repeats')
            # One admitted run of a glass cell is short of repeats; it is never a bar.
            one = FakeWave(cells, {c.split('/', 1)[1]: 'calibration' for c in cells})
            single = [g[:1] for g in [records(s) for s in (1, 2)]]
            w39_archive.produce(single, one, Path(t) / 'single')
            reader1 = Reader(one, Path(t) / 'single', ('calibration',), None)
            for cell in cells:
                self.assertEqual(B.cell_bars(reader1, cell, 'normal')['status'], 'insufficient admitted repeats')
            headline = B.headline([B.cell_bars(reader, c, 'normal') for c in cells])
            self.assertEqual({v['deep']['max'] for v in headline.values()}, {0.5})

    def test_a_three_code_run_separation_is_a_two_code_bar(self):
        with tempfile.TemporaryDirectory() as t:
            reader, cells = self.archive(Path(t), lift=3)
            for cell in cells:
                report = B.cell_bars(reader, cell, 'normal')
                deep = report['members'][0]['deep']
                self.assertTrue(max(max(r) for r in deep['runMediansRGB']) <= 252)
                self.assertEqual(deep['barRGB'], [2.0, 2.0, 2.0])
                self.assertEqual(deep['separationRGB'], [3.0, 3.0, 3.0])
                edge = [b for b in self.measured(report)][1:]
                self.assertTrue(all(0.5 <= v <= 2.0 + 1e-9 for b in edge for v in b['barRGB']))
                self.assertTrue(any(np.allclose(b['barRGB'], 2.0) for b in edge))

    def test_holdout_is_refused_at_the_command(self):
        with self.assertRaises(SystemExit):
            B.main(['/nonexistent', '--roles', 'calibration,holdout'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
