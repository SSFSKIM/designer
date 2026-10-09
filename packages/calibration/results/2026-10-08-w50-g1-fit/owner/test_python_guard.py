"""Exercise the live Python guard in disposable processes with synthetic source only."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PYTHON = '/Users/new/vitrea-w49/py/bin/python'


class PythonGuardTests(unittest.TestCase):
    def exercise(self, operation, *, pinned=True, changed=False):
        with tempfile.TemporaryDirectory(prefix='w50-owner-python-') as tmp:
            root = Path(tmp).resolve()
            helper = root/'helper.py'
            helper.write_text('print("SIDE EFFECT")\n')
            pins = {'helper.py': hashlib.sha256(helper.read_bytes()).hexdigest()} if pinned else {}
            if changed:
                helper.write_text('print("CHANGED SIDE EFFECT")\n')
            script = f'''
import importlib.util
from pathlib import Path
run = Path({str(HERE/'run.py')!r})
namespace = {{'__file__': str(run), '__name__': 'synthetic_bootstrap'}}
exec(compile(run.read_bytes(), str(run), 'exec'), namespace)
namespace['ROOT'] = Path({str(root)!r})
namespace['live_python_guard']({pins!r})
helper = Path({str(helper)!r})
{operation}
'''
            return subprocess.run([PYTHON, '-I', '-B', '-c', script], capture_output=True, text=True)

    def test_pinned_source_executes_after_guard(self):
        result = self.exercise("exec(compile(helper.read_bytes(), str(helper), 'exec'))")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'SIDE EFFECT\n')

    def test_unregistered_import_refused_before_module_body(self):
        result = self.exercise("""spec = importlib.util.spec_from_file_location('new_helper', helper)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)""", pinned=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('SIDE EFFECT', result.stdout)
        self.assertIn('unsealed Python source', result.stderr)

    def test_unregistered_dynamic_ast_read_refused_before_compile(self):
        result = self.exercise("exec(compile(helper.read_text(), '<AST>', 'exec'))", pinned=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('SIDE EFFECT', result.stdout)
        self.assertIn('unsealed Python source', result.stderr)

    def test_changed_source_refused_before_side_effect(self):
        result = self.exercise("exec(compile(helper.read_text(), '<AST>', 'exec'))", changed=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertIn('Changed', result.stderr)


if __name__ == '__main__':
    unittest.main()
