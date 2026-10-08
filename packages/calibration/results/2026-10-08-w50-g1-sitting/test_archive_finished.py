"""Synthetic archive rehearsal: no native pixels, processes or settings are used."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
TOOL = HERE / 'archive_finished.py'
BED = HERE.parent / '2026-10-08-w50-g0-declaration/bed'


def load_tool():
    spec = importlib.util.spec_from_file_location('archive_finished', TOOL)
    module = importlib.util.module_from_spec(spec)
    exec(compile(TOOL.read_bytes(), str(TOOL), 'exec'), module.__dict__)
    return module


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class FinishedArchiveTests(unittest.TestCase):
    def setUp(self):
        self.a = load_tool()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.raw = self.base / 'raw'
        self.raw.mkdir()
        self.plan = json.loads((BED / 'sitting-g1.json').read_bytes())
        self.manifest = json.loads((BED / 'manifest.json').read_bytes())
        self.frames = []
        for p in self.plan['passes']:
            for run in range(1, p['runs'] + 1):
                directory = self.raw / p['name'] / f'run-{run}'
                directory.mkdir(parents=True)
                profiles, frames = [], {}
                for profile, ids in p['profiles'].items():
                    ids = list(ids) + (p.get('run1Only', {}).get(profile, []) if run == 1 else [])
                    fixtures = []
                    for sid in ids:
                        name = f'{profile}/{sid}.png'
                        cell = f'{profile}/{sid}'
                        # Intentionally not a decodable image: packaging must treat bytes as opaque.
                        data = f'opaque synthetic {cell} run {run}'.encode()
                        path = directory / name
                        path.parent.mkdir(exist_ok=True)
                        path.write_bytes(data)
                        self.frames.append(path)
                        frames[cell] = sha(data)
                        fixtures.append(dict(sceneId=sid, file=name, synthetic=True))
                    profiles.append(dict(profileKey=profile, fixtures=fixtures))
                native = json.dumps(dict(profiles=profiles)).encode()
                (directory / 'manifest.json').write_bytes(native)
                admission = dict(admitted=True, dry=False, run=run,
                                 planSha256=sha((BED / 'sitting-g1.json').read_bytes()),
                                 declaration=dict(declarationSha256=self.a.DECLARATION_SHA),
                                 manifestSha256=sha(native), frames=frames)
                admission['pass'] = p['name']
                admission['schema'] = 'w43-run-admission-1'
                if p.get('bridge'):
                    report = dict(schema='w43-bridge-run-1', run=run, stop=p['bridge']['stop'],
                                  agrees=True, cells=[dict(cell=cell, agrees=True,
                                      verdict='AGREE (pixels)', frameSha256=frames[cell],
                                      referenceSha256=spec['reference']['sha256'])
                                      for cell, spec in p['bridge']['cells'].items()],
                                  rule='byte identity, or every region median within max(1 code, bar) '
                                       'of the reference (charter clause 3)')
                    report['pass'] = p['name']
                    report_raw = (json.dumps(report, indent=1) + '\n').encode()
                    (directory / 'bridge.json').write_bytes(report_raw)
                    admission['bridge'] = dict(agrees=True, stop=report['stop'],
                        verdicts={r['cell']: r['verdict'] for r in report['cells']},
                        reportSha256=sha(report_raw))
                (directory / 'admission.json').write_text(json.dumps(admission))
                (directory / 'watchdog.jsonl').write_text('opaque watchdog log\n')
            logs = self.raw / p['name'] / 'logs'
            logs.mkdir()
            (logs / 'driver.txt').write_text('pass driver evidence\n')
        logs = self.raw / 'logs'
        logs.mkdir()
        (logs / 'restore.json').write_text(json.dumps(dict(restored=True,
            slider=dict(restored=True), display=dict(restored=True, mode=68))))
        (logs / 'slider-as-found.json').write_text('{"value":0.5}')
        (logs / 'as-found-mode.json').write_text('{"mode":68}')
        (logs / 'preflight.json').write_text('{"synthetic":true}')
        (self.raw / 'console.txt').write_text('finished console evidence\n')

    def bridge_directory(self, *, stopping=True):
        p = next(p for p in self.plan['passes']
                 if p.get('bridge', {}).get('stop') is stopping)
        return self.raw / p['name'] / 'run-1'

    def write_bridge(self, directory, report, admission, *, bind=True):
        raw = (json.dumps(report, indent=1) + '\n').encode()
        (directory / 'bridge.json').write_bytes(raw)
        if bind:
            admission['bridge']['reportSha256'] = sha(raw)
        (directory / 'admission.json').write_text(json.dumps(admission))

    def forge_tree(self, out):
        # A self-consistent archive index is not itself proof of valid bridge evidence.
        sealed, manifest, plan = self.a.sources()
        rows = sealed.collect(self.raw, manifest, plan, self.a.DECLARATION_SHA)
        known = {r['path'] for r in rows}
        for path in self.raw.rglob('*'):
            rel = str(path.relative_to(self.raw))
            if path.is_file() and rel not in known:
                rows.append(dict(path=rel, sha256=sha(path.read_bytes()),
                                 roles=['operational'], kind='attestation'))
        return sealed, sealed.write_archive(self.raw, out, rows)

    def assert_bridge_refused(self, label):
        out = self.base / ('refused-' + label)
        with self.subTest(path='produce'):
            with self.assertRaisesRegex(ValueError, '[Bb]ridge'):
                self.a.produce(self.raw, out, finished=True)
            self.assertFalse(out.exists(), 'Bridge refusal must precede output and role exports')
        tree = self.base / ('forged-' + label)
        sealed, index_sha = self.forge_tree(tree)
        with self.subTest(path='verify'):
            with self.assertRaisesRegex(ValueError, '[Bb]ridge'):
                self.a.verify_tree(sealed, tree, self.manifest, self.plan, index_sha)

    def disagree(self, directory):
        report = json.loads((directory / 'bridge.json').read_bytes())
        admission = json.loads((directory / 'admission.json').read_bytes())
        report['cells'][0].update(agrees=False, verdict='DISAGREE',
                                  failing=['synthetic operational disagreement'])
        report['agrees'] = admission['bridge']['agrees'] = False
        admission['bridge']['verdicts'][report['cells'][0]['cell']] = 'DISAGREE'
        self.write_bridge(directory, report, admission)

    def test_missing_bridge_report_and_changed_report_hash_refuse_produce_and_verify(self):
        directory = self.bridge_directory()
        report_path = directory / 'bridge.json'
        original = report_path.read_bytes()
        for case in ('missing-report', 'changed-report-hash'):
            with self.subTest(case=case):
                if case == 'missing-report':
                    report_path.unlink()
                else:
                    report_path.write_bytes(original + b'\n')
                self.assert_bridge_refused(case)

    def test_wrong_bridge_identity_membership_and_summary_refuse_produce_and_verify(self):
        directory = self.bridge_directory()
        original_report = (directory / 'bridge.json').read_bytes()
        original_admission = (directory / 'admission.json').read_bytes()
        cases = ('schema', 'pass', 'run', 'boolean-run', 'stop', 'nonboolean-stop',
                 'missing-cell', 'extra-cell', 'duplicate-cell', 'nonboolean-cell-agrees',
                 'summary', 'nonboolean-summary', 'cell-verdict', 'frame-hash', 'reference-hash')
        for case in cases:
            with self.subTest(case=case):
                report = json.loads(original_report)
                admission = json.loads(original_admission)
                if case in ('schema', 'pass'):
                    report[case] = 'wrong'
                elif case == 'run':
                    report['run'] = 2
                elif case == 'boolean-run':
                    report['run'] = True
                elif case == 'stop':
                    report['stop'] = False
                elif case == 'nonboolean-stop':
                    report['stop'] = 1
                elif case == 'missing-cell':
                    report['cells'].pop()
                elif case == 'extra-cell':
                    report['cells'].append(dict(cell='undeclared', agrees=True, verdict='AGREE (pixels)'))
                elif case == 'duplicate-cell':
                    report['cells'].append(report['cells'][0])
                elif case == 'nonboolean-cell-agrees':
                    report['cells'][0]['agrees'] = 1
                elif case == 'summary':
                    report['agrees'] = False
                    admission['bridge']['agrees'] = False
                elif case == 'nonboolean-summary':
                    report['agrees'] = 1
                elif case == 'cell-verdict':
                    report['cells'][0]['verdict'] = 'DISAGREE'
                    admission['bridge']['verdicts'][report['cells'][0]['cell']] = 'DISAGREE'
                elif case == 'frame-hash':
                    report['cells'][0]['frameSha256'] = '0' * 64
                elif case == 'reference-hash':
                    report['cells'][0]['referenceSha256'] = '0' * 64
                self.write_bridge(directory, report, admission)
                self.assert_bridge_refused(case)

    def test_wrong_admission_bridge_bindings_refuse_produce_and_verify(self):
        directory = self.bridge_directory()
        report = json.loads((directory / 'bridge.json').read_bytes())
        original = (directory / 'admission.json').read_bytes()
        cases = ('missing-bridge', 'missing-report-hash', 'agrees', 'nonboolean-agrees',
                 'stop', 'nonboolean-stop', 'verdict', 'missing-verdict', 'extra-verdict')
        for case in cases:
            with self.subTest(case=case):
                admission = json.loads(original)
                bridge = admission['bridge']
                if case == 'missing-bridge':
                    del admission['bridge']
                elif case == 'missing-report-hash':
                    del bridge['reportSha256']
                elif case in ('agrees', 'stop'):
                    bridge[case] = False
                elif case == 'nonboolean-agrees':
                    bridge['agrees'] = 1
                elif case == 'nonboolean-stop':
                    bridge['stop'] = 1
                elif case == 'verdict':
                    bridge['verdicts'][report['cells'][0]['cell']] = 'DISAGREE'
                elif case == 'missing-verdict':
                    bridge['verdicts'].pop(report['cells'][0]['cell'])
                elif case == 'extra-verdict':
                    bridge['verdicts']['undeclared'] = 'AGREE (pixels)'
                self.write_bridge(directory, report, admission, bind=False)
                self.assert_bridge_refused('admission-' + case)

    def test_stopping_bridge_disagreement_refuses_produce_and_verified_asset(self):
        self.disagree(self.bridge_directory())
        self.assert_bridge_refused('stopping-disagreement')
        tree = self.base / 'forged-stopping-disagreement'
        index_sha = sha((tree / 'index.json').read_bytes())
        tar = self.base / 'stopping.tar'
        with tarfile.open(tar, 'w') as handle:
            for path in sorted(tree.rglob('*')):
                if path.is_file():
                    handle.add(path, arcname=str(path.relative_to(tree)), recursive=False)
        asset = self.base / 'stopping.tar.zst'
        with asset.open('wb') as handle:
            subprocess.run(['zstd', '-q', '-c', str(tar)], stdout=handle, check=True)
        with self.assertRaisesRegex(ValueError, '[Bb]ridge'):
            self.a.verify_asset(asset, self.base / 'rejected', sha(asset.read_bytes()), index_sha)
        self.assertFalse((self.base / 'rejected').exists())

    def test_nonstopping_closing_disagreement_is_accepted_and_reported_in_pack_and_replay(self):
        closing = [p for p in self.plan['passes'] if p.get('bridge', {}).get('stop') is False]
        # Distinct failures at both scales must all remain visible, in declared pass order.
        names = [closing[0]['name'], closing[-1]['name']]
        for name in names:
            self.disagree(self.raw / name / 'run-1')
        product = self.base / 'unbridged'
        result = self.a.produce(self.raw, product, finished=True)
        pack = json.loads((product / 'pack.json').read_bytes())
        replay = self.a.verify_asset(product / result['asset'], self.base / 'unbridged-replay',
                                     result['sha256'], result['indexSha256'])
        for record in (result, pack, replay):
            self.assertEqual(record['bridgeStatus'], 'unbridged')
            self.assertEqual(record['unbridgedClosingPasses'], names)
        for role in ('calibration', 'validation'):
            self.assertTrue((product / role / 'index.json').is_file())

    def test_roundtrip_preserves_every_byte_and_exports_only_declared_dependencies(self):
        result = self.a.produce(self.raw, self.base / 'product', finished=True)
        self.assertEqual(result['frames'], 1600)
        product = self.base / 'product'
        tree = product / 'tree'
        expected = {str(p.relative_to(self.raw)): p.read_bytes()
                    for p in self.raw.rglob('*') if p.is_file()}
        actual = {str(p.relative_to(tree)): p.read_bytes()
                  for p in tree.rglob('*') if p.is_file() and p.name not in ('index.json', 'index.sha256')}
        self.assertEqual(actual, expected)
        for role in ('calibration', 'validation'):
            allowed = {r['id'] for r in self.manifest['cells'] if r['role'] == role}
            allowed |= {r['id'] for r in self.manifest['references'] if role in r['roles']}
            exported = json.loads((product / role / 'index.json').read_bytes())['files']
            self.assertEqual({r['cell'] for r in exported}, allowed)
            self.assertTrue(all(r['kind'] == 'frame' and r['roles'] == [role] for r in exported))
            expected_paths = {str(path.relative_to(self.raw)) for path in self.frames
                              if '/'.join(path.parts[-2:])[:-4] in allowed}
            self.assertEqual({r['path'] for r in exported}, expected_paths)
        replay = self.a.verify_asset(product / result['asset'], self.base / 'fetched',
                                     result['sha256'], result['indexSha256'])
        self.assertEqual(replay['frames'], 1600)
        for record in (result, replay):
            self.assertEqual(record['bridgeStatus'], 'bridged')
            self.assertEqual(record['unbridgedClosingPasses'], [])
        self.assertEqual(result['tag'], 'w50-archive')
        self.assertIn('gh release create', result['releaseRecipe'])
        self.assertFalse((product / 'blind').exists())

    def test_completion_and_restore_are_required_before_output(self):
        for finished in (False,):
            with self.assertRaisesRegex(ValueError, 'finished'):
                self.a.produce(self.raw, self.base / 'out', finished=finished)
        self.assertFalse((self.base / 'out').exists())
        (self.raw / 'logs/restore.json').write_text('{"restored":false}')
        with self.assertRaisesRegex(ValueError, 'restor'):
            self.a.produce(self.raw, self.base / 'out', finished=True)
        self.assertFalse((self.base / 'out').exists())

    def test_missing_or_changed_frame_and_wrong_declaration_refuse(self):
        path = self.frames[0]
        original = path.read_bytes()
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.a.produce(self.raw, self.base / 'out', finished=True)
        path.write_bytes(original)
        admission = next(self.raw.glob('*/run-1/admission.json'))
        doc = json.loads(admission.read_bytes())
        doc['declaration']['declarationSha256'] = 'another declaration'
        admission.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, 'admitted'):
            self.a.produce(self.raw, self.base / 'out', finished=True)
        self.assertFalse((self.base / 'out').exists())

    def test_quarantine_extra_run_and_symlink_are_not_folded_into_admitted_archive(self):
        extra = self.raw / self.plan['passes'][0]['name'] / 'QUARANTINE-run-1'
        extra.mkdir()
        with self.assertRaisesRegex(ValueError, 'Unexpected|quarantine'):
            self.a.produce(self.raw, self.base / 'out', finished=True)
        extra.rmdir()
        extra = extra.with_name('run-99')
        extra.mkdir()
        with self.assertRaisesRegex(ValueError, 'Unexpected'):
            self.a.produce(self.raw, self.base / 'out', finished=True)
        extra.rmdir()
        (self.raw / 'logs/link').symlink_to(self.raw / 'console.txt')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.a.produce(self.raw, self.base / 'out', finished=True)

    def test_no_overwrite_or_output_inside_source(self):
        with self.assertRaisesRegex(ValueError, 'overlap'):
            self.a.produce(self.raw, self.raw / 'archive', finished=True)
        out = self.base / 'exists'
        out.mkdir()
        with self.assertRaisesRegex(ValueError, 'exists'):
            self.a.produce(self.raw, out, finished=True)

    def test_asset_hash_and_unsafe_tar_members_refuse_before_extraction(self):
        tar = self.base / 'bad.tar'
        with tarfile.open(tar, 'w') as handle:
            info = tarfile.TarInfo('../escape')
            info.size = 0
            handle.addfile(info)
        asset = self.base / 'bad.tar.zst'
        with asset.open('wb') as handle:
            subprocess.run(['zstd', '-q', '-c', str(tar)], stdout=handle, check=True)
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.a.verify_asset(asset, self.base / 'extract', '0' * 64, '0' * 64)
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.a.verify_asset(asset, self.base / 'extract', sha(asset.read_bytes()), '0' * 64)
        self.assertFalse((self.base / 'escape').exists())


if __name__ == '__main__':
    unittest.main()
