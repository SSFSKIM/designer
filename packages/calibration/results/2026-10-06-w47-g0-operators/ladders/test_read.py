#!/usr/bin/env python3.12
"""W47 G0 (g): the ladder reader end to end on a SYNTHETIC scratch, before any ladder render (the reader
is part 1's pin, so its readings are tested before the renders it reads exist). W46 G0's
`ladders/test_read.py`, ported by copy and re-bound; `test_ladder.py` carries the bars, X70 and the
selections on synthetic readings without any render, so this file is the integration of those with real
rows, real candidates and the level check.

The scratch is built from the level check's control render (`bindings.LEVEL_SCRATCH / "control"`, the
shipped rung on ladder (i)'s cells, pixel-identical to d0219cd684bf, `level/identity.py render`): its rows
and captures are hard-linked as the `control` and as each synthetic rung, the rows renamed to the rung's
real candidate (built into a scratch folder by W47's builder), and chosen web SDs moved:

- a ladder (i) rung with every cell unmoved reads L1 passing and its bar not met (point A's thin gain is
  not kept), and is listed among the L1-passing rungs;
- a ladder (ii) rung whose 1x captures differ from the control's names them and does not meet its bar;
- a rung with no render, or one WAITING for an operator, is `notRead` and the ladder incomplete;
- a rung matrix missing one declared row refuses the read (X70).

It SKIPS, saying why, while the level control render, the level module or W47's builder is absent.

    python3.12 -B -m unittest test_read -v      (from this directory)
"""
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read as R  # noqa: E402

W, B, LADDER = R.W, R.B, R.LADDER
SCRATCH = HERE / ".test-scratch"
CONTROL = W.LEVEL_SCRATCH / "control"
LEVEL_CANDIDATE = HERE.parent / "level" / "candidates" / "control"
LABELS = ("i-a0.7", "ii-w6-d0.3-t256")


def build(label, overrides):
    spec = SCRATCH / "specs" / f"{label}.json"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(json.dumps(dict(label=label, overrides=overrides)))
    got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL, capture_output=True,
                         text=True, env=dict(os.environ, W47_CANDIDATE_ROOT=str(SCRATCH / "candidates")))
    return got.returncode, got.stderr[-500:]


def write_rung(label, cells, mutate=None, scale_bytes=None, drop=None):
    cand = B.Candidate.read(str((SCRATCH / "candidates" / label / "candidate.json").relative_to(W.ROOT)))
    for scale in (1, 2):
        rows = [r for r in json.loads((CONTROL / f"{scale}x" / "matrix.json").read_bytes())["cells"]
                if r["key"]["sceneId"] in cells and (scale, r["key"]["sceneId"]) != drop]
        for r in rows:
            path = r["key"]["web"]["capturePath"]
            r["key"]["web"]["capturePath"] = path.replace(
                B.CANDIDATE_CLAUSE.search(path).group(0),
                f"materialProfile=candidate candidateDocument={cand.path} declarationSha256={cand.sha256[:12]}")
            if mutate:
                mutate(r)
        out = SCRATCH / "scratch" / label / f"{scale}x"
        out.mkdir(parents=True, exist_ok=True)
        (out / "matrix.json").write_text(json.dumps(dict(schemaVersion=5, cells=rows)))
        for r in rows:
            p, s = r["key"]["profileKey"], r["key"]["sceneId"]
            src = CONTROL / f"{scale}x" / "web-captures" / p / s
            dst = out / "web-captures" / p / s
            dst.mkdir(parents=True, exist_ok=True)
            for f in src.iterdir():
                if not (dst / f.name).exists():
                    if scale_bytes == scale and f.name.endswith("__webgpu.png"):
                        raw = bytearray(f.read_bytes())
                        raw[-20] ^= 1
                        (dst / f.name).write_bytes(bytes(raw))
                    else:
                        os.link(f, dst / f.name)


class Reader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (CONTROL / "1x" / "matrix.json").exists() or not LEVEL_CANDIDATE.exists():
            raise unittest.SkipTest(f"WAITING: the level check's control render ({CONTROL}) or its candidate "
                                    "(level/candidates/control) is absent; level/identity.py render makes them")
        try:
            R.level()
        except Exception as error:  # noqa: BLE001
            raise unittest.SkipTest(f"WAITING: W47's level module does not import ({error})") from error
        shutil.rmtree(SCRATCH, ignore_errors=True)
        (SCRATCH / "candidates").mkdir(parents=True)
        shutil.copytree(LEVEL_CANDIDATE, SCRATCH / "candidates" / "control")
        cls.proto = LADDER.protocol()
        rungs = {r["label"]: r for r in LADDER.rungs(cls.proto)}
        for label in LABELS:
            rc, err = build(label, rungs[label]["overrides"])
            if rc:
                raise unittest.SkipTest(f"WAITING: W47's builder refused {label}: {err}")
        cells_i = json.loads(W.LADDER_CELLS.read_text())["ladders"]["i"]
        cls.union = sorted(set(cells_i["rest"]) | set(cells_i["inactive"]))
        write_rung("control", cls.union)
        write_rung("i-a0.7", rungs["i-a0.7"]["cells"])
        write_rung("ii-w6-d0.3-t256", rungs["ii-w6-d0.3-t256"]["cells"], scale_bytes=1)
        cls.rungs = [dict(label="control", actsAt="both", cells=cls.union)] + [
            dict(rungs[k], dependent=False) for k in LABELS] + [dict(rungs["i-a0.8"])]
        cls.out = SCRATCH / "out"
        cls.out.mkdir()
        rc = R.main(scratch=SCRATCH / "scratch", candidates=SCRATCH / "candidates", rungs=cls.rungs, out=cls.out,
                    protocol=cls.proto, x60=False)
        assert rc == 0
        cls.result = json.loads((cls.out / "results.json").read_text())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def test_the_control_is_identical(self):
        self.assertEqual(self.result["control"]["verdict"], "IDENTICAL")

    def test_i_unmoved_passes_l1_and_does_not_meet(self):
        e = self.result["rungs"]["i-a0.7"]
        self.assertTrue(e["level"]["L1passes"])
        self.assertFalse(e["bar"]["meets"])
        self.assertIn("i-a0.7", self.result["ladders"]["i"]["passingL1"])

    def test_ii_a_moved_1x_capture_voids_the_rung(self):
        b = self.result["rungs"]["ii-w6-d0.3-t256"]["bar"]
        self.assertTrue(b["oneXNotIdentical"])
        self.assertFalse(b["meets"])

    def test_an_unrendered_rung_is_not_read(self):
        self.assertIn("i-a0.8", self.result["notRead"])
        self.assertFalse(self.result["ladders"]["i"]["complete"])

    def test_a_missing_row_refuses_the_read(self):
        R.CONF.update(scratch=SCRATCH / "scratch", candidates=SCRATCH / "candidates")
        rung = next(r for r in self.rungs if r["label"] == "i-a0.7")
        write_rung("i-a0.7", rung["cells"], drop=(2, "photo__rrect-md__rest"))
        try:
            with self.assertRaisesRegex(W.Refusal, "X70 REFUSES the rung"):
                R.admit("i-a0.7", R.rows_of("i-a0.7"), rung["cells"], self.proto["sets"])
        finally:
            shutil.rmtree(SCRATCH / "scratch" / "i-a0.7")
            write_rung("i-a0.7", rung["cells"])


if __name__ == "__main__":
    unittest.main()
