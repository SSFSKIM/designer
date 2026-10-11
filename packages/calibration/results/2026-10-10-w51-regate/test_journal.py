"""A surviving success file cannot permit a retry or hide a late instrument fault."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent

def module():
    spec = importlib.util.spec_from_file_location('w51_journal_test', HERE/'journal.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

class JournalTests(unittest.TestCase):
    def setUp(self):
        self.j = module(); self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup); self.out = Path(self.temp.name).resolve()/'run'
        self.identity = {'root':'a'*64,'population':'b'*64,'clearance':'c'*64}

    def publish(self, output, report, witness, identity):
        return self.j.commit(self.j.prepare(output, report, witness, identity))

    def test_fence_is_durable_before_substantive_admission_and_history_is_retained(self):
        first = self.j.fence(self.out, self.identity)
        self.assertTrue(Path(first['path']).is_file())
        second = self.j.fence(self.out, self.identity)
        self.assertNotEqual(first, second)
        self.assertEqual(len(list((self.out/'fences').glob('*.json'))), 2)
        with self.assertRaises(ValueError): self.j.fence(self.out, {**self.identity,'root':'d'*64})

    def test_storage_failure_before_install_leaves_no_torn_authoritative_name(self):
        target=self.out/'contract.json'
        with patch.object(self.j.os,'fsync',side_effect=OSError('simulated storage failure')):
            with self.assertRaises(OSError):self.j.write_once(target,{'candidate':'held'})
        self.assertFalse(target.exists())
        self.j.write_once(target,{'candidate':'held'})
        self.assertEqual(self.j.load(target),{'candidate':'held'})
        with self.assertRaises(FileExistsError):self.j.write_once(target,{'candidate':'other'})
        self.assertEqual(self.j.load(target),{'candidate':'held'})

    def test_storage_failure_after_install_preserves_complete_bytes_but_never_overwrites(self):
        target=self.out/'contract.json'
        with patch.object(self.j,'sync_directory',side_effect=OSError('simulated post-install failure')):
            with self.assertRaises(OSError):self.j.write_once(target,{'candidate':'held'})
        self.assertEqual(self.j.load(target),{'candidate':'held'})
        with self.assertRaises(FileExistsError):self.j.write_once(target,{'candidate':'other'})
        self.assertEqual(self.j.load(target),{'candidate':'held'})

    def test_operational_stop_sidecar_does_not_break_the_next_fence(self):
        first=self.j.fence(self.out,self.identity)
        self.j.write_once(Path(first['path']+'.stop.json'),{'status':'OPERATIONAL_STOP'})
        second=self.j.fence(self.out,self.identity)
        self.assertEqual(Path(second['path']).name,'000002.json')
        self.assertTrue(Path(first['path']+'.stop.json').is_file())

    def test_symlinked_output_subtree_cannot_write_outside_its_namespace(self):
        self.out.mkdir();elsewhere=self.out.parent/'elsewhere';elsewhere.mkdir()
        (self.out/'sub').symlink_to(elsewhere,target_is_directory=True)
        with self.assertRaises(ValueError):self.j.write_once(self.out/'sub/record.json',{})
        self.assertFalse((elsewhere/'record.json').exists())

    def test_partial_success_is_not_a_terminal_verdict(self):
        self.j.fence(self.out, self.identity)
        self.j.write_once(self.out/'result.json', {'status':'PASS_EXPOSED_OWNER_PENDING'})
        self.assertIsNone(self.j.terminal(self.out))
        self.j.fail(self.out, 'AFTER_MARKER', self.identity)
        got = self.j.terminal(self.out)
        self.assertEqual(got['status'], 'NEITHER')
        self.assertFalse(got['judgeCompleted'])

    def test_fault_request_cannot_revoke_an_existing_terminal_commit(self):
        self.j.fence(self.out, self.identity)
        self.publish(self.out, {'status':'PASS_EXPOSED_OWNER_PENDING'}, {'status':'COMPLETE'}, self.identity)
        before=self.j.terminal(self.out)
        self.assertEqual(self.j.fail(self.out, 'LATER_INVOCATION_IO', self.identity),before)
        self.assertEqual(self.j.terminal(self.out),before)
        self.assertFalse((self.out/'fault.json').exists())
        self.assertTrue((self.out/'result.json').is_file())
        with self.assertRaises(FileExistsError):
            self.publish(self.out, {'status':'NEITHER'}, {'status':'COMPLETE'}, self.identity)

    def test_final_directory_flush_failure_is_committed_not_revoked(self):
        self.j.fence(self.out, self.identity)
        sync = self.j.sync_directory
        def fail_after_terminal(path):
            if (self.out/'terminal.json').exists():
                raise OSError('post-install flush failed')
            return sync(path)
        # This reproduces the old install-then-fsync failure without relying on fault.json.
        with patch.object(self.j, 'sync_directory', side_effect=fail_after_terminal):
            publication=self.publish(self.out, {'status':'PASS_EXPOSED_OWNER_PENDING'},
                                     {'status':'COMPLETE'}, self.identity)
        self.assertEqual(publication, 'COMMITTED_WITH_DURABILITY_ERROR')
        self.assertEqual(self.j.terminal(self.out)['status'], 'PASS_EXPOSED_OWNER_PENDING')

    def test_changed_report_invalidates_a_terminal_success(self):
        self.j.fence(self.out, self.identity)
        self.publish(self.out, {'status':'NEITHER'}, {'status':'COMPLETE'}, self.identity)
        (self.out/'report.json').write_text('{}')
        with self.assertRaises(ValueError): self.j.terminal(self.out)

if __name__ == '__main__': unittest.main()
