"""Safety and archive boundary tests. Synthetic pixels only; no native launch."""
import importlib.util
import io
import json
from pathlib import Path
import signal
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

class SafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = load('w50_safety_tests', HERE/'safety.py')

    def test_absent_denied_wrong_client_and_duplicate_grants_refuse(self):
        row = dict(service='kTCCServiceScreenCapture', client='dev.vitrea.reference-apple.w39',
                   client_type=0, auth_value=2, csreq='ABCD')
        self.assertTrue(self.s.grant_row([row])['positive'])
        for rows in ([], [dict(row, auth_value=0)], [dict(row, client='dev.vitrea.reference-apple')],
                     [row, row], [dict(row, csreq='')]):
            self.assertFalse(self.s.grant_row(rows)['positive'])

    def test_positive_grant_validates_compiled_requirement_and_keeps_failures(self):
        import hashlib
        import subprocess
        compiled=b'compiled TCC requirement fixture'
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); app=root/'Reference.app'
            binary=app/'Contents/MacOS/VitreaReference'; binary.parent.mkdir(parents=True)
            binary.write_bytes(b'unchanged binary')
            pin=root/'pin.json'
            pin.write_text(json.dumps({'binarySha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
                                      'cdhash':'pinned-cdhash'}))
            row=dict(service='kTCCServiceScreenCapture',client=self.s.CLIENT,client_type=0,
                     auth_value=2,csreq=compiled.hex(),last_modified=123)
            for force_failure in (False,True):
                with self.subTest(requirement_failure=force_failure):
                    def command(argv,**kwargs):
                        code,out,error=0,'',''
                        if argv[0]=='sqlite3':out=json.dumps([row])
                        elif argv[:2]==['codesign','-dvvv']:error='CDHash=pinned-cdhash\n'
                        elif argv[0]=='csreq':out='cdhash H"pinned-cdhash"'
                        elif argv[:3]==['codesign','-v','-R']:
                            path=Path(argv[3])
                            if not path.is_file() or path.read_bytes()!=compiled:
                                code,error=1,'requirement interpreted as missing filename'
                            elif force_failure:code,error=1,'signature does not satisfy requirement'
                        else:raise AssertionError(argv)
                        return subprocess.CompletedProcess(argv,code,out,error)
                    with patch.object(self.s,'APP',app),patch.object(self.s,'PIN',pin), \
                            patch.object(self.s.subprocess,'run',side_effect=command):
                        result=self.s.grant_check()
                    self.assertEqual(result['positive'],not force_failure)
                    if force_failure:
                        self.assertIn('signature does not satisfy requirement',result['error'])
                        self.assertNotIn('re-grant',result['reason'])

    def test_classifying_census_uses_executable_and_entry_not_shell_arguments(self):
        rows = [dict(pid=1, executable='/bin/bash', argv=['bash', '-c', 'VitreaReference']),
                dict(pid=2, executable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                     argv=['Google Chrome']),
                dict(pid=3, executable='/bin/node', argv=['node', '/pkg/@playwright/cli/cli.js']),
                dict(pid=4, executable='/side/VitreaReference.app/Contents/MacOS/VitreaReference',
                     argv=['VitreaReference'])]
        got = self.s.classify(rows)
        self.assertEqual([r['pid'] for r in got['refuse']], [4])
        self.assertEqual([r['pid'] for r in got['annotate']], [2, 3])
        rows[1]['argv'] += ['--remote-debugging-pipe']
        got = self.s.classify(rows)
        self.assertEqual([r['pid'] for r in got['refuse']], [2, 3, 4])

    def test_automated_chrome_variants_and_helpers_refuse_but_user_family_is_annotated(self):
        for variant in ('Google Chrome for Testing', 'Chrome for Testing', 'Google Chrome Canary'):
            with self.subTest(variant=variant):
                main=f'/Applications/{variant}.app/Contents/MacOS/{variant}'
                helper=f'/Applications/{variant}.app/Contents/Frameworks/Helper.app/Contents/MacOS/Google Chrome Helper'
                user='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                user_helper='/Applications/Google Chrome.app/Contents/Frameworks/Helper.app/Contents/MacOS/Google Chrome Helper'
                def row(pid, exe, *args):
                    return dict(pid=pid,ppid=1,start='same-start',executable=exe,argv=[exe,*args])
                rows=[row(2,main,'--enable-automation','--remote-debugging-pipe'),row(3,helper),
                      row(4,user),row(5,user_helper),row(6,'/bin/node','/pkg/@playwright/cli/cli.js')]
                foreign,_=self.s.recorder().census(rows=rows,me=999,chain_file='')
                self.assertEqual({r['pid'] for r in foreign},{2,3,4,5,6})
                got=self.s.classify(rows)
                self.assertEqual([r['pid'] for r in got['refuse']],[2,3,6])
                self.assertEqual([r['pid'] for r in got['annotate']],[4,5])

    def test_restore_ignores_repeated_signals_and_attempts_both_resources(self):
        events = []
        def slider():
            self.assertEqual(signal.getsignal(signal.SIGTERM), signal.SIG_IGN)
            signal.raise_signal(signal.SIGTERM)
            signal.raise_signal(signal.SIGHUP)
            events.append('slider')
            raise ValueError('slider restoration failed')
        def display():
            self.assertEqual(signal.getsignal(signal.SIGINT), signal.SIG_IGN)
            signal.raise_signal(signal.SIGINT)
            events.append('display')
            return {'restored': True}
        prior = signal.getsignal(signal.SIGTERM)
        result = self.s.restore(slider, display)
        self.assertEqual(events, ['slider', 'display'])
        self.assertFalse(result['restored'])
        self.assertEqual(signal.getsignal(signal.SIGTERM), prior)

    def test_idle_watchdog_detects_input_and_preserves_log(self):
        d = self.s.driver()
        logs = []
        readings = iter([{'idleSeconds': 20, 'screenLocked': False, 'frontmostIdentifier': 'owner',
                          'frontmostPid': 7, 'windowOwners': []}])
        dog = d.Watchdog(lambda: next(readings), 'receded', 'harness',
                        {'idleSeconds': 80, 'frontmostIdentifier': 'owner'}, 0, logs.append,
                        clock=lambda: 5)
        self.assertIn('HID input', dog.check())
        self.assertEqual(len(logs), 1)

    def test_wrong_bridge_pixels_are_rejected_not_just_hash_recorded(self):
        from PIL import Image
        d = self.s.driver()
        def png(level):
            out = io.BytesIO()
            Image.new('RGB', (320, 200), (level,)*3).save(out, format='PNG')
            return out.getvalue()
        bg = {'kind': 'solid', 'srgb': [28, 28, 30]}
        component = {'kind': 'rrect', 'size': [280, 160], 'radius': 34}
        self.assertTrue(d.bridge_verdict(png(40), png(40), bg, component, 1, 'dark', 'receded')['agrees'])
        self.assertFalse(d.bridge_verdict(png(50), png(40), bg, component, 1, 'dark', 'receded')['agrees'])

class ArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = load('w50_archive_tests', HERE/'archive.py')

    def test_exposed_export_has_only_its_dependency_closed_role(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root/'raw'; source.mkdir()
            rows = []
            for name, roles in [('fit', ['calibration']), ('hold', ['blind']),
                                ('shared', ['calibration', 'blind']), ('blind-ref', ['blind'])]:
                raw = name.encode(); (source/name).write_bytes(raw)
                rows.append(dict(path=name, sha256=self.a.sha(raw), roles=roles, kind='frame'))
            self.a.write_archive(source, root/'archive', rows)
            self.a.export_role(root/'archive', root/'fit', 'calibration')
            index = self.a.verify_archive(root/'fit')
            self.assertEqual({r['path'] for r in index['files']}, {'fit', 'shared'})
            self.assertFalse((root/'fit'/'hold').exists())
            with self.assertRaisesRegex(ValueError, 'blind'):
                self.a.export_role(root/'archive', root/'holdout', 'blind')
            (root/'fit'/'fit').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'hash'):
                self.a.verify_archive(root/'fit')

    def test_producer_rejects_relabelled_repetition_before_counting_it(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve(); directory=root/'main'/'run-1'; directory.mkdir(parents=True)
            raw=json.dumps({'profiles':[{'profileKey':'p','fixtures':[{'sceneId':'s','file':'s.png'}]}]}).encode()
            (directory/'manifest.json').write_bytes(raw)
            (directory/'s.png').write_bytes(b'synthetic')
            admission=dict(admitted=True,dry=False,run=2,**{'pass':'main'},
                planSha256=self.a.sha((HERE.parent/'sitting-g1.json').read_bytes()),
                declaration={'declarationSha256':'sealed'},manifestSha256=self.a.sha(raw),
                frames={'p/s':self.a.sha(b'synthetic')})
            (directory/'admission.json').write_text(json.dumps(admission))
            with self.assertRaisesRegex(ValueError,'Run identity'):
                self.a.collect(root,{'cells':[],'references':[]},
                    {'passes':[{'name':'main','runs':1,'profiles':{'p':['s']}}]},'sealed')

    def test_path_escape_symlink_and_duplicate_are_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source=root/'raw'; source.mkdir()
            (root/'secret').write_bytes(b'x'); (source/'link').symlink_to(root/'secret')
            for name in ('../secret', 'link', '/tmp/absolute'):
                with self.assertRaises(ValueError):
                    self.a.write_archive(source, root/'out', [dict(path=name, sha256=self.a.sha(b'x'),
                                                                    roles=['calibration'], kind='frame')])
            (source/'okay').write_bytes(b'x')
            row=dict(path='okay', sha256=self.a.sha(b'x'), roles=['calibration'], kind='frame')
            with self.assertRaises(ValueError):
                self.a.write_archive(source, root/'out', [row, row])

if __name__ == '__main__':
    unittest.main()
