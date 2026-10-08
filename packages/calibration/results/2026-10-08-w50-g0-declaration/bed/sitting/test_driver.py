"""W50 entrypoint and ownership tests: no native launcher."""
import importlib.util
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent

def module():
    spec=importlib.util.spec_from_file_location('w50_driver_test', HERE/'w50.py')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.dry_imports()                          # explicit trusted test path, not a CLI bypass
    return m

class DriverTests(unittest.TestCase):
    def test_direct_entrypoint_refuses_unsealed_batch_before_any_launch(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'substituted.json'; p.write_text('{}')
            result=subprocess.run(['/Users/new/vitrea-w49/py/bin/python', '-I', '-B', str(HERE/'w50.py'),
                                   str(p), 'plan'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('sealed', result.stderr.lower())

    def test_changed_early_helper_is_rejected_before_its_marker_executes(self):
        import hashlib
        import json
        digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        for changed in ('build.py','sitting/safety.py'):
            with self.subTest(helper=changed), tempfile.TemporaryDirectory() as td:
                root=Path(td)/'repo'
                decl=root/'packages/calibration/results/w50'
                bed=decl/'bed'; (bed/'sitting').mkdir(parents=True)
                audit=decl/'audit'; audit.mkdir()
                entry=bed/'sitting/w50.py'; entry.write_bytes((HERE/'w50.py').read_bytes())
                (bed/'build.py').write_text('# original helper\n')
                (bed/'sitting/safety.py').write_text('# original helper\n')
                for name in ('next_wave.py','closure.py'):
                    (audit/name).write_text('# original guard\n')
                batch=bed/'sitting-g1.json'; batch.write_text('{}')
                rel=lambda p:str(p.relative_to(root))
                sources={rel(p):digest(p) for p in (entry,bed/'build.py',bed/'sitting/safety.py',
                                                   audit/'next_wave.py',audit/'closure.py')}
                contract=bed/'execution-contract.json'
                contract.write_text(json.dumps(dict(schema='batch-import-closure-1',
                    batch={'path':rel(batch),'sha256':digest(batch)}, renderer=rel(entry),
                    closure={'sources':sources}, guardSources={n:digest(audit/n) for n in ('next_wave.py','closure.py')})))
                Path(str(contract)+'.sha256').write_text(f'{digest(contract)}  {contract.name}\n')
                pins=[{'path':p,'sha256':h} for p,h in sources.items()]
                pins += [{'path':rel(p),'sha256':digest(p)} for p in (batch,contract,Path(str(contract)+'.sha256'))]
                one=decl/'declaration.json'
                one.write_text(json.dumps({'schema':'w50-declaration-1','sources':pins}))
                two=decl/'fit-declaration.json'
                two.write_text(json.dumps({'schema':'w50-fit-declaration-1','sources':pins,
                                           'partOneSha256':digest(one)}))
                for p in (one,two):p.with_suffix('.sha256').write_text(f'{digest(p)}  {p.name}\n')
                marker=Path(td)/'executed'
                (bed/changed).write_text(f'from pathlib import Path\nPath({str(marker)!r}).write_text("EXECUTED")\n')
                result=subprocess.run(['/Users/new/vitrea-w49/py/bin/python','-I','-B',str(entry),str(batch),'plan'],
                                      capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(marker.exists(),'changed repository helper executed before refusal')
                self.assertIn('source',result.stderr.lower())

    def test_source_only_loader_ignores_a_timestamp_valid_stale_pyc(self):
        import os
        import py_compile
        w=module()
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'helper.py'; marker=Path(td)/'executed'
            evil=f'from pathlib import Path\nPath({str(marker)!r}).write_text("EXECUTED")\n'
            safe='SAFE = True\n'+' '*(len(evil)-len('SAFE = True\n'))
            path.write_text(evil); stamp=path.stat().st_mtime
            py_compile.compile(str(path),doraise=True)
            path.write_text(safe); os.utime(path,(stamp,stamp))
            # Prove the fixture really fools Python's default loader, even under -B.
            spec=importlib.util.spec_from_file_location('unsafe_loader_fixture',path)
            legacy=importlib.util.module_from_spec(spec); spec.loader.exec_module(legacy)
            self.assertTrue(marker.exists()); marker.unlink()
            result=w.load('source_only_fixture',path)
            self.assertTrue(result.SAFE)
            self.assertFalse(marker.exists())

    def test_cut_still_runs_every_closing_bridge(self):
        w=module(); _, _, plan=w.B.build()
        selected=w.selected_passes(plan, 'bed-x0.5-1x-active')
        self.assertEqual([p['name'] for p in selected[:2]], ['open-x0.5-1x-active', 'bed-x0.5-1x-active'])
        self.assertEqual(len(selected), 10)
        self.assertTrue(all(p['runAfterCut'] for p in selected[2:]))
        with self.assertRaises(ValueError):
            w.selected_passes(plan, 'not-declared')

    def test_foreign_capture_refuses_before_display_write_or_output(self):
        from types import SimpleNamespace
        w=module()
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'sitting'
            stub=SimpleNamespace(pinned_declaration=lambda _: {}, outside_repository=lambda p:p)
            with patch.object(w,'configure',return_value=stub), \
                    patch.object(w.S,'machine',return_value={'foreignProcessCount':1}), \
                    patch.object(w,'read_mode',side_effect=AssertionError('display touched')):
                with self.assertRaisesRegex(ValueError,'preflight'):
                    w.run(HERE.parent/'sitting-g1.json',out)
            self.assertFalse(out.exists())

    def test_owner_token_and_pid_start_are_required_before_signal(self):
        w=module()
        owner=w.Ownership('/side/VitreaReference', ['capture', '--run-label', 'unique-owner'])
        own=dict(pid=12, start='start-A', executable='/side/VitreaReference',
                 argv=['/side/VitreaReference', 'capture', '--run-label', 'unique-owner'])
        other=dict(own, pid=13, argv=['/side/VitreaReference', 'capture', '--run-label', 'someone-else'])
        owner.observe([own, other])
        self.assertEqual(owner.targets([own, other]), [own])
        self.assertEqual(owner.targets([dict(own, start='reused')]), [])
        self.assertEqual(owner.targets([dict(own, argv=other['argv'])]), [])

if __name__=='__main__':
    unittest.main()
