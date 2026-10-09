"""The preflight boundary refuses writes and numerical JSON parsing, not just the happy path."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
P = types.ModuleType('attempt2_preflight_tests'); P.__file__ = str(HERE/'attempt2_preflight.py')
sys.modules[P.__name__] = P
exec(compile(Path(P.__file__).read_bytes(), P.__file__, 'exec'), P.__dict__)


class ReadOnlyTests(unittest.TestCase):
    def test_forbidden_writes_are_denied_before_side_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve(); source = home/'source'; source.write_bytes(b'original')
            fd = os.open(source, os.O_WRONLY)
            try:
                calls = [lambda: (home/'new').write_bytes(b'new'), lambda: source.write_text('edit'),
                    lambda: source.unlink(), lambda: source.rename(home/'moved'),
                    lambda: (home/'directory').mkdir(), lambda: os.chmod(source, 0o600),
                    lambda: os.utime(source, None), lambda: os.link(source, home/'link'),
                    lambda: os.symlink(source, home/'symbolic'), lambda: os.truncate(source, 0),
                    lambda: os.write(fd, b'changed'), lambda: os.ftruncate(fd, 0)]
                for callback in calls:
                    with self.subTest(callback=callback), self.assertRaises(ValueError):
                        with P.ReadOnly(): callback()
                    self.assertEqual(list(home.iterdir()), [source])
                    self.assertEqual(source.read_bytes(), b'original')
            finally: os.close(fd)

    def test_payload_raw_hash_allowed_but_json_parser_refuses(self):
        raw = b'{"numeric": 12.125}\n'; digest = hashlib.sha256(raw).hexdigest()
        with P.ReadOnly({digest}):
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
            for value in (raw, raw.decode()):
                with self.assertRaises(ValueError): json.loads(value)
            self.assertEqual(json.loads('{"metadata": true}'), {'metadata': True})
        self.assertEqual(json.loads(raw), {'numeric': 12.125})

    def test_stdlib_environment_probe_can_use_identified_devnull(self):
        import platform
        import subprocess
        from unittest.mock import patch
        with P.ReadOnly():
            self.assertIsInstance(platform._Processor.from_subprocess(), str)
            with self.assertRaises(ValueError): os.open('/dev/null', os.O_RDWR)
            with self.assertRaises(ValueError): open('/dev/null', 'w')
            with self.assertRaises(ValueError):
                subprocess.run(['uname', '-a'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        with P.ReadOnly():
            real = os.lstat
            def changed(path, *args, **kwargs):
                if str(path) == '/dev/null':
                    values = list(real(path, *args, **kwargs)); values[1] += 1
                    return os.stat_result(values)
                return real(path, *args, **kwargs)
            with patch.object(os, 'lstat', side_effect=changed), self.assertRaises(ValueError):
                platform._Processor.from_subprocess()

    def test_read_only_refuses_network_and_unrestricted_subprocess(self):
        import subprocess
        with P.ReadOnly(), self.assertRaises(ValueError):
            subprocess.run([sys.executable, '-c', 'pass'], check=True)


class CompletePlanTests(unittest.TestCase):
    @contextlib.contextmanager
    def fixture(self):
        runner = types.ModuleType('attempt2_complete_plan_test'); runner.__file__ = str(HERE/'attempt2_run.py')
        sys.modules[runner.__name__] = runner
        exec(compile(Path(runner.__file__).read_bytes(), runner.__file__, 'exec'), runner.__dict__)
        W = runner.W
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve(); old = home/'old'; old.mkdir()
            payload = old/'payload.json'; payload.write_bytes(b'{"syntheticNumeric": 123}\n')
            pin = W.pin(payload)
            union = {'members': [{'payload': pin, 'artifacts': [pin]}]}
            manifest = {'count': 1, 'files': [pin]}
            fields = ('MANIFEST', 'UNION', 'ROOT', 'CONTRACT', 'AUTHORITY_PATH',
                      'VIEW_PATH', 'CONTRACT_PATH', 'REVIEW')
            a = types.SimpleNamespace(**{name: home/name for name in fields},
                OLD_OUTPUT=old, OUTPUT=home/'output', NEW_MARKER=home/'phase'/'analysis.started.json',
                REPO=home, PREPARATION=2, PREFLIGHT=home/'preflight', AUDIT_COMMIT='audit-commit', RULING='ruling-commit')
            for name in fields: getattr(a, name).write_bytes(W.encode({}))
            a.MANIFEST.write_bytes(W.encode(manifest)); a.UNION.write_bytes(W.encode(union))
            a.MARKER = home/'spent'; a.MARKER.write_bytes(b'{}\n')
            a.OLD = types.SimpleNamespace(MANIFEST_SHA=W.sha(a.MANIFEST), UNION_SHA=W.sha(a.UNION))
            claim = Path(str(a.CONTRACT)+'.started.json')
            claim.write_bytes(W.encode({'numericalAdmission': {}}))
            for name in ('LOGICAL', 'TERMINAL', 'COMPLETE', 'PENDING', 'FAILED', 'INVOCATION'):
                setattr(runner, name, home/name)
            runner.PREVIOUS = ()
            calls = []
            def called(name, result):
                def call(*args, **kwargs): calls.append(name); return result
                return call
            guard = types.SimpleNamespace(enforce=called('closure', None))
            a.verify_seal = called('seal', ({}, {}, {}, {}, manifest,
                                  {'closure': {'sources': {}, 'environment': {}}}, guard))
            real_live, real_core = runner.modules()
            runner.A = a
            core = {'C': types.SimpleNamespace(D=types.SimpleNamespace(GPU_LOCK=home/'lease')),
                    'A': real_core['A']}
            helper = types.SimpleNamespace(S=object())
            common = types.SimpleNamespace(_REPEAT={},
                _repeat_binding=called('repeat-binding', (helper, {}, {})))
            primitive = types.SimpleNamespace(_pin_bytes=lambda *args, **kwargs: None)
            measurement = types.SimpleNamespace(evaluate=lambda *args: self.fail('No measure'),
                P=types.SimpleNamespace(inputs=called('measurement-inputs', None),
                    S=types.SimpleNamespace(L=common, M=primitive)))
            judge = types.SimpleNamespace(evaluate=lambda *args: self.fail('No judge'),
                root_of=called('judge-root', {}), originals=called('judge-originals', ({}, {})),
                inputs=called('judge-inputs', ({}, {}, {}, {})), preflight=called('judge-preflight', None))
            context = {'phase': 'gate'}
            live = types.SimpleNamespace(_template=called('template', (context, [])),
                _component=lambda view, name: (measurement if name == 'measurement' else judge, {}),
                checked=lambda *args: home/'REVIEW',
                admission_module=called('read-admission', types.SimpleNamespace(validate_captures=lambda: None)))
            runner.modules = called('modules', (live, core))
            (home/'batch').write_bytes(b'{}\n')
            runner.admit = called('admit', (({}, {}, home/'batch', {}, [], None), union))
            yield runner, calls, home, primitive

    def test_complete_plan_exercises_all_setup_without_writes_or_payload_reads(self):
        with self.fixture() as (runner, calls, home, primitive):
            before = {str(p): p.read_bytes() for p in home.rglob('*') if p.is_file()}
            plan = P.prepare(runner)
            self.assertEqual(calls, ['seal', 'closure', 'modules', 'admit', 'template',
                'measurement-inputs', 'repeat-binding', 'read-admission', 'judge-root',
                'judge-originals', 'judge-inputs', 'judge-preflight'])
            self.assertIsInstance(primitive._pin_bytes, runner.R.PinReader)
            self.assertEqual(before, {str(p): p.read_bytes() for p in home.rglob('*') if p.is_file()})
            self.assertFalse(runner.A.OUTPUT.exists())
            self.assertFalse(runner.A.NEW_MARKER.exists())
            self.assertEqual(plan['proof']['writes'], 0)
            self.assertIn(str(runner.A.NEW_MARKER.parent), plan['proof']['paths']['absent'])
            self.assertEqual(plan['proof']['payloadsParsed'], 0)

    def test_any_new_admission_write_or_payload_parse_fails_under_same_plan(self):
        for fault in ('seal-write', 'admit-write', 'admit-parse'):
            with self.subTest(fault=fault), self.fixture() as (runner, calls, home, primitive):
                def write(*args): (home/'forbidden').write_bytes(b'not allowed')
                def parse(*args): return json.loads((home/'old'/'payload.json').read_bytes())
                if fault == 'seal-write': runner.A.verify_seal = write
                else: runner.admit = parse if fault == 'admit-parse' else write
                with self.assertRaises(ValueError): P.prepare(runner)
                self.assertFalse((home/'forbidden').exists())
                self.assertFalse(runner.A.NEW_MARKER.exists())


if __name__ == '__main__': unittest.main()
