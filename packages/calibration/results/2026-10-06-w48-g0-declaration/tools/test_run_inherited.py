"""W48 G0 (b): the runner that runs W47's tests under W48's bindings (`run_inherited.py`) and the suite
helper (`inherited_suite.py`): a path outside W47's root refuses, the bindings an inherited test reads are
W48's, and a write into W47's directory is refused by the audit hook (as a relative path under
`shutil.rmtree`'s `dir_fd` too) while a write elsewhere is not.

    python3.12 -B -m unittest -v test_run_inherited      (from this directory)
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "run_inherited.py"
W47 = HERE.parent.parent / "2026-10-06-w47-g0-operators"


def py(code: str):
    return subprocess.run([sys.executable, "-B", "-c", code], cwd=HERE, capture_output=True, text=True)


class Runner(unittest.TestCase):
    def test_a_path_outside_w47_refuses(self):
        for rel in ("../2026-10-06-w48-g0-declaration/test_bindings.py", "cuts/rule.py"):
            got = subprocess.run([sys.executable, "-B", str(RUN), rel], capture_output=True, text=True)
            self.assertNotEqual(got.returncode, 0, rel)
            self.assertIn("is not a W47 test module", got.stdout + got.stderr)

    def test_an_inherited_test_reads_w48s_bindings(self):
        got = subprocess.run([sys.executable, "-B", str(RUN), "referees/test_referees.py"], capture_output=True, text=True)
        self.assertEqual(got.returncode, 0, got.stdout[-800:] + got.stderr[-800:])
        self.assertIn("2026-10-06-w48-g0-declaration/bindings.py", got.stdout)
        self.assertRegex(got.stdout, r"Ran \d+ tests")

    def test_the_hook_refuses_a_write_into_w47_and_admits_one_elsewhere(self):
        code = ("import sys, os, tempfile, shutil; sys.path.insert(0, '.'); import run_inherited as R; sys.addaudithook(R._audit)\n"
                f"w47 = {str(W47)!r}\n"
                "for what, fn in (('open', lambda: open(os.path.join(w47, '.probe'), 'w')),\n"
                "                 ('mkdir', lambda: os.mkdir(os.path.join(w47, '.probe-dir')))):\n"
                "    try:\n        fn(); print('ADMITTED', what)\n    except PermissionError:\n        print('refused', what)\n"
                "fd = os.open(w47, os.O_RDONLY)\n"
                "try:\n    os.remove('.probe', dir_fd=fd); print('ADMITTED dir_fd')\n"
                "except PermissionError:\n    print('refused dir_fd')\n"
                "except FileNotFoundError:\n    print('ADMITTED dir_fd')\n"
                "t = tempfile.mkdtemp(); open(os.path.join(t, 'x'), 'w').close(); shutil.rmtree(t); print('admitted tmp')\n")
        got = py(code)
        self.assertEqual(got.returncode, 0, got.stderr)
        self.assertEqual(got.stdout.split(), ["refused", "open", "refused", "mkdir", "refused", "dir_fd", "admitted", "tmp"])
        self.assertFalse((W47 / ".probe").exists())
        self.assertFalse((W47 / ".probe-dir").exists())


if __name__ == "__main__":
    unittest.main()
