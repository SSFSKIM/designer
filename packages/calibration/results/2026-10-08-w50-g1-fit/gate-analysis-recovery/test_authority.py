"""Source-only synthetic authority tests: no gate, config or capture payload is opened."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('successor_authority', HERE/'authority.py')
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)


class AuthorityTests(unittest.TestCase):
    def test_carry_accepts_exact_three_lines_only(self):
        old = b'prefix\n'+A.BEFORE_ONE+b'middle\n'+A.BEFORE_TWO+b'suffix\n'
        new = A.carry(old)
        self.assertEqual(new.count(b'production = '), 1)
        A.source_delta({'changed.py': A.digest(old), 'held.py': A.digest(b'held')},
                       {'changed.py': new, 'held.py': b'held'}, 'changed.py', old)
        for changed, held in ((new+b'\n', b'held'), (new, b'changed'), (old, b'held')):
            with self.assertRaises(ValueError):
                A.source_delta({'changed.py': A.digest(old), 'held.py': A.digest(b'held')},
                               {'changed.py': changed, 'held.py': held}, 'changed.py', old)
        with self.assertRaises(ValueError):
            A.source_delta({'changed.py': A.digest(old)},
                           {'changed.py': new, 'extra.py': b'extra'}, 'changed.py', old)

    def test_successor_view_cannot_substitute_any_input_or_membership(self):
        original = {'closure': {'sources': {'changed.py': 'old'}, 'environment': {}},
                    'inputs': [{'path': 'config', 'sha256': 'same'}],
                    'phaseDependencies': {'gateKeys': [['one']]}, 'candidateDomain': {'held': 1}}
        sources = {'changed.py': 'new'}
        view = A.successor_view(original, sources, {'path': 'oldroot', 'sha256': 'old'})
        A.check_view(original, view, sources, {'path': 'oldroot', 'sha256': 'old'})
        for field in ('inputs', 'phaseDependencies', 'candidateDomain'):
            changed = copy.deepcopy(view); changed[field] = None
            with self.assertRaises(ValueError):
                A.check_view(original, changed, sources, {'path': 'oldroot', 'sha256': 'old'})
        self.assertEqual(original['closure']['sources'], {'changed.py': 'old'})

    def test_original_live_bootstrap_still_refuses_changed_source(self):
        live = A.source(HERE.parent/'live-execution/dispatch.py', 'analysis2_old_refusal_test')
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'execution-root.json'
            original = A.git_bytes(A.REPO/A.SOURCE)
            bootstrap = HERE.parent/'live-execution/dispatch.py'
            doc = {'repo': str(A.REPO),
                   'bootstrap': {'path': str(bootstrap.relative_to(A.REPO)), 'sha256': A.sha(bootstrap)},
                   'closure': {'sources': {A.SOURCE: A.digest(original)}}}
            p.write_bytes(A.W.encode(doc))
            Path(str(p)+'.sha256').write_text(f'{A.sha(p)}  {p.name}\n')
            with self.assertRaisesRegex(ValueError, 'Unregistered source bytes'):
                live.root_doc(p)

    def test_held_candidate_and_config_bytes_cannot_be_relabelled(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('candidate.json', 'measurement-config.json'):
                p = Path(tmp)/name; p.write_bytes(b'{"original":true}')
                item = A.pin(p); p.write_bytes(b'{"substituted":true}')
                with self.assertRaises(ValueError): A.checked(tmp, item)

    def test_original_source_pin_refuses_the_carry(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'source.py'
            old = A.BEFORE_ONE+A.BEFORE_TWO
            p.write_bytes(A.carry(old))
            with self.assertRaises(ValueError):
                A.checked(tmp, {'path': 'source.py', 'sha256': A.digest(old)})


if __name__ == '__main__': unittest.main()
