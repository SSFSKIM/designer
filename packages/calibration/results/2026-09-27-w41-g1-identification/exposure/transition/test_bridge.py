"""Synthetic transition checks; no native reader, browser or exposure is invoked."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('transition_bridge',Path(__file__).with_name('bridge.py'))
bridge=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


class TransitionTests(unittest.TestCase):
    def test_only_declared_guard_functions_can_change(self):
        old='VALUE=1\ndef score(x): return x+1\ndef guard(): return False\n'
        new='VALUE=1\ndef score(x): return x+1\ndef guard(): return True\ndef wait(): pass\n'
        result=bridge.function_transition(old,new,{'guard'},{'wait'},{})
        self.assertEqual(result['changedFunctions'],['guard'])
        with self.assertRaisesRegex(ValueError,'unapproved'):
            bridge.function_transition(old,new.replace('x+1','x+2'),{'guard'},{'wait'},{})
        with self.assertRaisesRegex(ValueError,'assignment'):
            bridge.function_transition(old,new.replace('VALUE=1','VALUE=2'),{'guard'},{'wait'},{})

    def test_unapproved_top_level_execution_is_not_hidden_by_function_identity(self):
        old='VALUE=1\ndef score(): return VALUE\n'
        new=old+'perform_native_read()\n'
        with self.assertRaisesRegex(ValueError,'top-level'):
            bridge.function_transition(old,new,set(),set(),{})

    def test_historical_runner_exception_does_not_exempt_other_source_changes(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);(root/'runner.py').write_bytes(b'new guard');(root/'scorer.py').write_bytes(b'old score')
            sha=lambda b:hashlib.sha256(b).hexdigest()
            pins={'runner.py':sha(b'old guard'),'scorer.py':sha(b'old score')}
            result=bridge.check_witnesses(root,pins,'runner.py',sha(b'old guard'),sha(b'new guard'))
            self.assertEqual(result['changed'],['runner.py'])
            (root/'scorer.py').write_bytes(b'changed score')
            with self.assertRaisesRegex(ValueError,'source changed'):
                bridge.check_witnesses(root,pins,'runner.py',sha(b'old guard'),sha(b'new guard'))

    def test_wrong_old_runner_hash_cannot_be_relabelled_as_transition(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);(root/'runner.py').write_bytes(b'new')
            with self.assertRaisesRegex(ValueError,'historical runner'):
                bridge.check_witnesses(root,{'runner.py':'f'*64},'runner.py','a'*64,
                    hashlib.sha256(b'new').hexdigest())

    def test_artifact_hash_changes_fail_even_when_source_bridge_is_allowed(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);(root/'reading.json').write_bytes(b'original')
            pins={'reading.json':hashlib.sha256(b'original').hexdigest()}
            self.assertEqual(bridge.check_artifacts(root,pins),1)
            (root/'reading.json').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'artifact changed'):bridge.check_artifacts(root,pins)

    def test_published_bridge_is_exclusive(self):
        with tempfile.TemporaryDirectory() as name:
            path=Path(name)/'reading.json';bridge.save(path,{'one':1})
            with self.assertRaises(FileExistsError):bridge.save(path,{'two':2})


if __name__=='__main__':unittest.main()
