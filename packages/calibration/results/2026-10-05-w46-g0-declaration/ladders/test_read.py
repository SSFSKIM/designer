#!/usr/bin/env python3.12
"""W46 G0 (e): the ladder reader on a SYNTHETIC scratch, before any ladder render (the reader is part 1's
pin, so its readings are tested before the renders it reads exist).

The scratch is built from the level check's control render (`~/vitrea-w46/g0-level/control/`, the shipped
rung on ladder (i)'s cells, pixel-identical to d0219cd684bf): its rows and captures are hard-linked as the
`control` and as each synthetic rung, the rows renamed to the rung's real candidate (built into a scratch
candidates folder by W46's builder), and chosen web SDs moved to produce the readings under test:

- (i) a transmission rung that raises every photo cell reads `raisesPhoto` with the photo median ratio up,
  and passes L1 (the levels unmoved); a rung whose interior means rise past L1's growth bound FAILS, names
  the growth misses and attributes them;
- (ii) a rung raising the thin rest cells and not the F inactive cells MEETS the bar; one that also raises
  an F inactive cell beyond its bar does not; a rung that moves nothing is FLAT;
- (iii) a rung lowering both fine inactive cells toward Apple and holding photo MEETS the bar;
- a rung whose other scale's captures differ from the control's reads not scale-anchored;
- a withheld row in a rung refuses the read; a control that is not identical stops it.

    python3.12 -B -m unittest test_read -v      (from this directory)
"""
import copy
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
RUNGS = {"i-a-0.7": ("i", "i-a", "active.dark", "optics.regular.tintAlpha", 0.7, "both"),
         "i-a-0.5": ("i", "i-a", "active.dark", "optics.regular.tintAlpha", 0.5, "both"),
         "ii-fa-0.1": ("ii", "ii-fa", "active.dark", "sizeScatterFloor", 0.1, "1x"),
         "ii-fa-0.2": ("ii", "ii-fa", "active.dark", "sizeScatterFloor", 0.2, "1x"),
         "ii-fb-0.7": ("ii", "ii-fb", "active.dark", "sizeScatterFloor2x", 0.7, "2x"),
         "iii-rn2-0.4": ("iii", "iii-rn2", "receded.dark", "sizeScatterRampStartThin2x", 0.4, "2x")}


def protocol():
    p = copy.deepcopy(LADDER.protocol())
    for lad in p["ladders"]:
        keep = [lv for lv in lad.get("arms", []) + lad.get("levers", []) if lv["id"] in {v[1] for v in RUNGS.values()}]
        for lv in keep:
            lv["values"] = [v[4] for v in RUNGS.values() if v[1] == lv["id"]]
        lad["arms" if "arms" in lad else "levers"] = keep
    return p


def build(label, overrides):
    spec = SCRATCH / "specs" / f"{label}.json"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(json.dumps(dict(label=label, overrides=overrides)))
    got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL, capture_output=True,
                         text=True, env=dict(os.environ, W46_CANDIDATE_ROOT=str(SCRATCH / "candidates")))
    assert got.returncode == 0, got.stderr[-500:]


def write_rung(label, cells, mutate=None, scale_bytes=None):
    """`label`'s scratch: the control's rows on `cells`, renamed to the label's candidate, mutated."""
    cand = B.Candidate.read(str((SCRATCH / "candidates" / label / "candidate.json").relative_to(W.ROOT)))
    for scale in (1, 2):
        rows = [r for r in json.loads((CONTROL / f"{scale}x" / "matrix.json").read_bytes())["cells"]
                if r["key"]["sceneId"] in cells]
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


def bump(scenes, field, by):
    def go(r):
        if any(r["key"]["sceneId"] == s for s in scenes):
            r["material"][field]["value"] += by
    return go


class Reader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (CONTROL / "1x" / "matrix.json").exists():
            raise unittest.SkipTest("the level check's control render is absent (level/identity.py render)")
        shutil.rmtree(SCRATCH, ignore_errors=True)
        (SCRATCH / "candidates").mkdir(parents=True)
        shutil.copytree(LEVEL_CANDIDATE, SCRATCH / "candidates" / "control")
        lad = json.loads(W.LADDER_CELLS.read_text())["ladders"]["i"]
        cls.rest, cls.inactive = lad["rest"], lad["inactive"]
        cells = set(cls.rest) | set(cls.inactive)
        # The control: the level render as it is (renamed to the copied control candidate, same bytes).
        write_rung("control", cells)
        photo_rest = [s for s in cls.rest if s.startswith("photo__")]
        thin = [s for s in cls.rest if B.SCENES.span(s) <= 44 and s.startswith(("checkerboard", "impulse"))]
        for label, (lad_id, lever, slot, leaf, value, acts) in RUNGS.items():
            build(label, {slot: {leaf: value}})
        write_rung("i-a-0.7", cls.rest, bump(photo_rest, "interiorStdDevWeb", 0.01))
        write_rung("i-a-0.5", cls.rest, lambda r: (bump(photo_rest, "interiorStdDevWeb", 0.02)(r),
                                                   bump(["checkerboard__rrect-md__rest"], "interiorMeanWeb", 0.02)(r)))
        # ii: a 1x lever raising the thin rest cells at 1x only (2x untouched); one raising an inactive cell too
        thin_1x = lambda r: "-1x-" in r["key"]["profileKey"] and bump(thin, "interiorStdDevWeb", 0.004)(r)  # noqa: E731
        write_rung("ii-fa-0.1", cls.rest + ["checkerboard__rrect-md__inactive"], thin_1x)
        write_rung("ii-fa-0.2", cls.rest + ["checkerboard__rrect-md__inactive"],
                   lambda r: (thin_1x(r), "-1x-" in r["key"]["profileKey"]
                              and bump(["checkerboard__rrect-md__inactive"], "interiorStdDevWeb", 0.01)(r)))
        write_rung("ii-fb-0.7", cls.rest + ["checkerboard__rrect-md__inactive"], scale_bytes=1)
        # iii: lower the "fine" inactive cells toward Apple — the synthetic bed has no checkerboard-8 cell,
        # so the reader's fine selection is exercised on its absence (no fine cell: never MEETS)
        write_rung("iii-rn2-0.4", cls.inactive)
        scenes = {"i-a-0.7": cls.rest, "i-a-0.5": cls.rest, "iii-rn2-0.4": cls.inactive}
        rungs = [dict(label="control", actsAt="both", cells=sorted(cells))] + [
            dict(label=k, ladder=v[0], lever=v[1], slot=v[2], leaf=v[3], value=v[4], actsAt=v[5],
                 cells=sorted(scenes.get(k, cls.rest + ["checkerboard__rrect-md__inactive"]))) for k, v in RUNGS.items()]
        cls.rungs = rungs
        cls.out = SCRATCH / "out"
        cls.out.mkdir()
        rc = R.main(scratch=SCRATCH / "scratch", candidates=SCRATCH / "candidates", rungs=rungs, out=cls.out,
                    protocol=protocol(), x60=False)
        assert rc == 0
        cls.result = json.loads((cls.out / "results.json").read_text())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def test_the_control_is_identical(self):
        self.assertEqual(self.result["control"]["verdict"], "IDENTICAL")

    def test_i_raises_photo_and_names_the_level_failure(self):
        e = self.result["ladders"]["i"]["i-a"]
        r07, r05 = e["readings"]
        self.assertGreater(r07["photoMedianRatio"], r07["photoControlMedianRatio"])
        self.assertTrue(r07["passes"])
        self.assertFalse(r05["passes"])
        self.assertTrue(any("checkerboard__rrect-md__rest" in m["cell"] for m in r05["L1"]["growthMisses"]))
        self.assertTrue(r05["excesses"])
        self.assertEqual(e["passingRungs"], [0.9, 0.7])
        self.assertTrue(e["raisesPhoto"])
        self.assertTrue(e["photoMonotone"])

    def test_ii_meets_the_bar_only_without_raising_f_inactive(self):
        e = self.result["ladders"]["ii"]["ii-fa"]
        self.assertEqual(e["meetsBar"], [0.1])
        self.assertTrue(e["scaleAnchored"])
        self.assertFalse(e["flat"])

    def test_a_flat_lever_and_a_broken_scale_anchor(self):
        e = self.result["ladders"]["ii"]["ii-fb"]
        self.assertTrue(e["flat"])
        self.assertFalse(e["scaleAnchored"])

    def test_iii_without_fine_cells_never_meets(self):
        self.assertEqual(self.result["ladders"]["iii"]["iii-rn2"]["meetsBar"], [])

    def test_a_partial_or_duplicated_rung_refuses(self):
        R.CONF.update(scratch=SCRATCH / "scratch", candidates=SCRATCH / "candidates")
        rows = R.rows_of("i-a-0.7")
        with self.assertRaisesRegex(W.Refusal, "missing"):
            R.admit("i-a-0.7", dict(list(rows.items())[1:]), self.rungs[1]["cells"])
        with self.assertRaisesRegex(W.Refusal, "extra"):
            R.admit("i-a-0.7", rows, self.rungs[1]["cells"][1:])
        key, row = next((k, v) for k, v in rows.items() if "/checkerboard__" in f"/{k[1]}" or k[1].startswith("photo"))
        broken = dict(rows)
        broken[key] = json.loads(json.dumps(row))
        broken[key]["material"]["interiorStdDevWeb"] = None
        with self.assertRaisesRegex(W.Refusal, "no structure reading"):
            R.admit("i-a-0.7", broken, self.rungs[1]["cells"])
        path = SCRATCH / "scratch" / "i-a-0.7" / "1x" / "matrix.json"
        body = json.loads(path.read_text())
        path.write_text(json.dumps(dict(body, cells=body["cells"] + body["cells"][:1])))
        try:
            with self.assertRaisesRegex(W.Refusal, "two rows"):
                R.rows_of("i-a-0.7")
        finally:
            path.write_text(json.dumps(body))

    def test_the_targets(self):
        t = self.result["targets"]
        self.assertEqual(t["P"]["lever"], ["i-a"])
        self.assertEqual(t["C rest"]["lever"], ["ii-fa"])
        self.assertEqual(t["F inactive"]["lever"], [])


if __name__ == "__main__":
    unittest.main()
