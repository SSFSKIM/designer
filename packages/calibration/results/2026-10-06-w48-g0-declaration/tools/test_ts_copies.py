"""W48 G0 (b): the copies W48 makes of W47's tools whose bindings are compiled in (charter clause 2), held
to exactly their declared diff.

- `fit/build-candidate.ts` and `seal/seal.ts` are `ts_copies.render()` of W47's files, byte for byte: W47's
  file (pinned here by SHA-256) with `ts_copies.HEADER` prepended and each `ts_copies.EDITS` line replaced
  once. Outside the header, the only remaining "W47" in either copy's code is the env var
  `W47_CANDIDATE_ROOT` (W47's `fit/fit.py`, inherited unchanged, sets it), W47's `labels.json` path (the
  label grammar, inherited), two of W47's code comments, and the refusals that name W47 as refused.
- `census-gate.py` and `with-gpu.sh` are W47's with a W48 header and, in the launcher, the lock.

    python3.12 -B -m unittest -v test_ts_copies      (from this directory)
"""
from __future__ import annotations

import hashlib
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ts_copies as C  # noqa: E402

W47_SHA = {"fit/build-candidate.ts": "eec1df4953a64a5eb05772dfe5b13c1b41678412a244d44e54fab49b8071492c",
           "seal/seal.ts": "a6489ecf1e07a044b56e56bdce5d8cc9bfd7b87afe2f32ad35da94e6f91973e9",
           "census-gate.py": "3e1a9f9d1e20dd66be2486b4dfae9fa807520e2b59bcf93acb69f863b2623ad1",
           "with-gpu.sh": "1150ba49ed2b1c732324f2b05572f763660c04e92b929c8f5d2298a1d1fd2b1e"}
ALLOWED_W47 = ("W47_CANDIDATE_ROOT", '"2026-10-06-w47-g0-operators", "fit", "labels.json"',
               "// W47: the mirrored tables", "// W47: every added leaf reads back",
               "W46's or W47's evidence or scratch; W48")     # the refusal naming W47 as refused


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Copies(unittest.TestCase):
    def test_w47s_sources_are_the_pinned_bytes(self):
        for rel, want in W47_SHA.items():
            self.assertEqual(sha(C.W47 / rel), want, rel)

    def test_each_copy_is_exactly_its_declared_diff(self):
        for name, (_, w48_rel) in C.FILES.items():
            self.assertEqual((C.G0 / w48_rel).read_text(), C.render(name), w48_rel)

    def test_no_other_w47_binding_remains_in_code(self):
        for name, (_, w48_rel) in C.FILES.items():
            text = (C.G0 / w48_rel).read_text()
            body = text[len(C.HEADER[name]):]
            code = re.sub(r"/\*\*.*?\*/", "", body, flags=re.S)       # the doc comments are W47's text
            for line in code.splitlines():
                if re.search(r"w47|W47", line) and not any(a in line for a in ALLOWED_W47):
                    self.fail(f"{w48_rel}: a W47 binding remains: {line.strip()}")

    def test_an_edit_whose_w47_line_is_absent_refuses(self):
        saved = C.EDITS["seal.ts"]
        try:
            C.EDITS["seal.ts"] = saved + [("a line W47's seal does not have", "x")]
            with self.assertRaises(SystemExit):
                C.render("seal.ts")
        finally:
            C.EDITS["seal.ts"] = saved

    def test_the_launcher_and_census_copies(self):
        w47 = (C.W47 / "with-gpu.sh").read_text()
        ours = (C.G0 / "with-gpu.sh").read_text()
        self.assertIn("LOCK=/tmp/w48-gpu.lock", ours)
        self.assertNotIn("w47-gpu.lock", ours)
        self.assertEqual([ln for ln in ours.splitlines() if not ln.startswith("#") and "LOCK=" not in ln],
                         [ln for ln in w47.splitlines() if not ln.startswith("#") and "LOCK=" not in ln])
        gate47 = (C.W47 / "census-gate.py").read_text()
        gate48 = (C.G0 / "census-gate.py").read_text()
        self.assertEqual(gate48.split('"""', 2)[2], gate47.split('"""', 2)[2])      # the code is W47's


if __name__ == "__main__":
    unittest.main()
