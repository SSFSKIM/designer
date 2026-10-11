"""Declared DL5 grading deltas never waive the unchanged numerical/verdict witness."""
import ast
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
FIT = HERE.parent/'2026-10-08-w50-g1-fit'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value

class PortTests(unittest.TestCase):
    def test_differential_detects_changed_grading_not_just_a_hash(self):
        witness = load(HERE/'semantics.py', 'w51_semantics_test')
        got = witness.verify()
        self.assertEqual(got['status'], 'UNCHANGED_NUMERICS_DECLARED_DL5_RULE_AND_SCOPE')
        with tempfile.TemporaryDirectory() as folder:
            modified = Path(folder)/'judge.py'
            text = (HERE/'judge.py').read_text().replace("report['status'] = GATE_SUCCESS if not failed else 'NEITHER'",
                                                       "report['status'] = GATE_SUCCESS")
            self.assertNotEqual(text, (HERE/'judge.py').read_text())
            modified.write_text(text)
            with self.assertRaisesRegex(ValueError, 'judge'):
                witness.verify(judge=modified)

    def test_rule_witness_preserves_old_history_and_pins_new_policy_functions(self):
        witness = load(HERE/'semantics.py', 'w51_semantics_rules_test')
        with tempfile.TemporaryDirectory() as folder:
            changed = Path(folder)/'judge_rules.py'
            original = (HERE/'judge_rules.py').read_text()
            for old, new in (("component['bound'] *= policy['primaryT1GrowthMultiplier']",
                              "component['bound'] *= 200"),
                             ("if not full_union:", "if False:")):
                text = original.replace(old, new)
                self.assertNotEqual(text, original)
                changed.write_text(text)
                with self.assertRaisesRegex(ValueError, 'judge_rules'):
                    witness.verify(rules=changed)

    def test_scene_authority_accepts_only_pinned_same_content_at_bound_locations(self):
        authority = load(HERE/'semantics.py', 'w51_semantics_scene')
        with tempfile.TemporaryDirectory() as folder:
            a, b = Path(folder).resolve()/'original.json', Path(folder).resolve()/'local.json'
            a.write_text('{"radius":16}'); b.write_bytes(a.read_bytes())
            pin = {'path':str(a), 'sha256':authority.sha(a)}
            authority.same_scene(pin, b, [pin])
            b.write_text('{"radius":17}')
            with self.assertRaises(ValueError): authority.same_scene(pin, b, [pin])
            b.write_bytes(a.read_bytes())
            with self.assertRaises(ValueError): authority.same_scene(pin, b, [])
            with self.assertRaises(ValueError): authority.same_scene({**pin, 'sha256':'0'*64}, b, [pin])

if __name__ == '__main__': unittest.main()
