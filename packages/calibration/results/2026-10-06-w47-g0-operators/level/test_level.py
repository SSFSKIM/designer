#!/usr/bin/env python3.12
"""W47 G0 (e): W46 G0's level check's red cases (`results/2026-10-05-w46-g0-declaration/level/test_level.py`),
ported by copy, with operator 1 (charter Design "Operator 1", X61, X65):

- **Operator 1 at identity, now.** At the snapshots (no far delta) `alphaBase` is `tintAlpha` exactly at
  every span and scale, `farS` is the far curve (0 at and below 96; 0.104 at 128 and 0.352 at 160 on the
  inherited top 256), and `sizedAlpha` is W46's `tintAlpha + gain·sizeK·(1 − tintAlpha)`; a candidate
  naming `tintAlphaFar1x`/`2x` at 0 evaluates the same.
- **Operator 1 graded (WAITING until operator 1 merges).** A candidate naming a non-zero far delta reads
  `alphaBase = clamp(tintAlpha + delta·farS, 0, 1)` through the runtime's `tintAlphaFarAtScale`, the 2x
  delta unread at 1x, and the clamp at 1. On a runtime without that export the arithmetic REFUSES the
  candidate as WAITING (never reads the delta as 0); the case asserts the refusal and reports a SKIP.

W46's text follows.

W46 G0 (d): the level check's red cases (charter X61; G0 (d); Design "The ladders", v1.2). Nothing here
renders; the rendered half of its test is the shipped rung's identity, read by `level.py identity` on
the control candidate's render (`level/identity/`).

- **The projection is explicit.** `measured()` removes exactly `capturedAt` and `key.web.capturePath`.
- **Identity on the published rows.** Rows built from the published `d0219cd684bf` rows with candidate
  mode's provenance, over the canonical captures, read IDENTICAL; a moved measured field, one changed
  capture byte, a foreign driver prefix, a document clause naming another candidate, an unpinned
  engine each read DIFFERS, and the provenance is retained.
- **The arithmetic.** At the shipped documents the solve is unclamped at full authority on the 0/255
  checker and the solids (excess 0); at `tintAlpha` 0.5 it clamps the checker at span 96 (+0.062 active,
  +0.068 receded) and `light-solid` (+0.227), the charter's Grounding numbers; the impulse input sits
  inside the authority fade.
- **The attribution.** A predicted rise met by a measured rise is the mechanism's; a measured move the
  arithmetic does not predict is `unexplained`.
- **The backdrop means.** The 0/255 checker reads (0.5, 0.5); `light-solid` encoded 0.95.

    python3.12 -B -m unittest test_level -v      (from this directory)
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import level as L  # noqa: E402

W, B = L.W, L.B
SCRATCH = HERE / ".test-scratch"
CELLS = ("checkerboard__rrect-md__rest", "photo__capsule-button__rest", "dark-solid__rrect-md__rest")


def fake_candidate(tmp: Path, tint=None, extra=None) -> B.Candidate:
    """A candidate folder (inside the repository, as `Candidate.read` requires) whose four endpoints are
    the snapshots, the dark pair optionally at other tintAlphas."""
    tmp.mkdir(parents=True, exist_ok=True)
    endpoints = {}
    for slot in W.SLOTS:
        body = json.loads(W.document_path(slot).read_text())
        if tint and slot in tint:
            body["patch"]["optics"]["regular"]["tintAlpha"] = tint[slot]
        if extra and slot in extra:
            body["patch"].update(extra[slot])
        path = tmp / f"{slot}.json"
        path.write_text(json.dumps(body, indent=2) + "\n")
        endpoints[slot] = dict(path=path.name, sha256=W.file_sha(path))
    (tmp / "candidate.json").write_text(json.dumps(dict(kind="vitrea-candidate-material-document", schemaVersion=1,
                                                         name="test", glassTintAmount=0.25, endpoints=endpoints)))
    return B.Candidate.read(str(tmp / "candidate.json"))


def candidate_rows(candidate: B.Candidate, published: dict) -> list:
    rows = []
    for profile in W.DARK_025:
        for sid in CELLS:
            row = json.loads(json.dumps(published[(profile, "webgpu", sid)]))
            prefix = L.DRIVER_PREFIX.match(row["key"]["web"]["capturePath"]).group(1)
            row["key"]["web"]["capturePath"] = (f"{prefix}materialProfile=candidate candidateDocument={candidate.path} "
                                                f"declarationSha256={candidate.sha256[:12]}")
            row["capturedAt"] = "2026-10-05T00:00:00.000Z"
            rows.append(row)
    return rows


class Identity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bed = B.load_published(W.REFERENCE["dark"])
        cls.published = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r for r in cls.bed.rows}
        cls.tmp = SCRATCH / "identity"
        cls.candidate = fake_candidate(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def test_the_projection_removes_exactly_the_provenance(self):
        row = next(iter(self.published.values()))
        got = L.measured(row)
        self.assertNotIn("capturedAt", got)
        self.assertNotIn("capturePath", got["key"]["web"])
        self.assertEqual(L.differing(got, row), ["capturedAt", "key.web.capturePath"])
        self.assertEqual(L.PROVENANCE, ("capturedAt", "key.web.capturePath"))

    def test_published_rows_under_candidate_provenance_read_identical(self):
        rows = candidate_rows(self.candidate, self.published)
        got = L.identity(rows, W.CANONICAL_CAPTURES, self.candidate, self.published)
        self.assertEqual(got["verdict"], "IDENTICAL", got["failures"][:2])
        self.assertTrue(all(c["provenance"]["valid"] and c["provenance"]["capturePath"] for c in got["perCell"]))

    def test_a_moved_measured_field_differs(self):
        rows = candidate_rows(self.candidate, self.published)
        rows[0]["material"]["interiorMeanWeb"]["value"] += 1e-9
        got = L.identity(rows, W.CANONICAL_CAPTURES, self.candidate, self.published)
        self.assertEqual(got["verdict"], "DIFFERS")
        self.assertIn("material.interiorMeanWeb.value", got["failures"][0]["fail"][0])

    def test_one_changed_capture_byte_differs(self):
        rows = candidate_rows(self.candidate, self.published)
        tree = SCRATCH / "tree"
        for r in rows:
            p, s = r["key"]["profileKey"], r["key"]["sceneId"]
            shutil.copytree(W.CANONICAL_CAPTURES / p / s, tree / p / s, dirs_exist_ok=True)
        png = tree / W.DARK_025[0] / CELLS[0] / f"{CELLS[0]}__webgpu.png"
        raw = bytearray(png.read_bytes())
        raw[-20] ^= 1
        png.write_bytes(bytes(raw))
        got = L.identity(rows, tree, self.candidate, self.published)
        self.assertEqual(len(got["failures"]), 1)
        self.assertTrue(got["failures"][0]["fail"][0].startswith("pixels"))

    def test_bad_provenance_differs_and_is_retained(self):
        for mutate, needle in (
            (lambda r: r["key"]["web"].__setitem__("capturePath", "x" + r["key"]["web"]["capturePath"]), "driver prefix"),
            (lambda r: r["key"]["web"].__setitem__("capturePath", r["key"]["web"]["capturePath"].replace(
                self.candidate.sha256[:12], "0" * 12)), "document clause"),
        ):
            rows = candidate_rows(self.candidate, self.published)
            mutate(rows[1])
            got = L.identity(rows, W.CANONICAL_CAPTURES, self.candidate, self.published)
            self.assertEqual(got["verdict"], "DIFFERS")
            self.assertIn(needle, " ".join(got["failures"][0]["fail"]))
            self.assertFalse(got["failures"][0]["provenance"]["valid"])
        for stamp in (None, 42, "not a timestamp", "2026-13-45T00:00:00.000Z"):
            rows = candidate_rows(self.candidate, self.published)
            rows[0]["capturedAt"] = stamp
            if stamp is None:
                del rows[0]["capturedAt"]
            got = L.identity(rows, W.CANONICAL_CAPTURES, self.candidate, self.published)
            self.assertEqual(got["verdict"], "DIFFERS", stamp)
            self.assertIn("capturedAt", " ".join(got["failures"][0]["fail"]))
        rows = candidate_rows(self.candidate, self.published)
        rows[2]["key"]["web"]["engineVersion"] = "153.0.8010.12"
        got = L.identity(rows, W.CANONICAL_CAPTURES, self.candidate, self.published)
        self.assertIn("engine", " ".join(got["failures"][0]["fail"]))

    def test_the_check_reads_no_change_on_the_published_rows(self):
        rows = candidate_rows(self.candidate, self.published)
        got = L.check(rows, self.candidate, self.bed)
        self.assertEqual(got["excesses"], [])
        self.assertTrue(all(e["delta"] == 0 for e in got["levels"]))
        self.assertTrue(got["L1"]["growthClausePasses"])


class Arithmetic(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def cells(self):
        return [dict(id=f"{n}-{p}-{s}", pose=p, span=s, encoded=e, linear=l)
                for n, e, l in (("checker", 0.5, 0.5), ("light-solid", 0.95045, 0.89097), ("dark-solid", 0.11039, 0.01171),
                                ("impulse", 0.00375, 0.00375))
                for p in ("rest", "inactive") for s in (44, 96)]

    def test_the_shipped_documents_hold_the_level(self):
        got = L.predict(L.shipped_endpoints(), self.cells())
        for key in ("checker-rest-96", "checker-inactive-96", "light-solid-rest-96", "dark-solid-inactive-44"):
            self.assertFalse(got[key]["clamped"], key)
            self.assertAlmostEqual(got[key]["excess"], 0, places=12)
        self.assertEqual(got["checker-rest-96"]["tintAlpha"], 0.9)
        self.assertEqual(got["checker-inactive-96"]["tintAlpha"], 0.89)
        self.assertLess(got["impulse-rest-44"]["authority"], 1)

    def test_tint_alpha_one_half_clamps_where_the_charter_says(self):
        c = fake_candidate(SCRATCH / "half", tint={"active.dark": 0.5, "receded.dark": 0.5})
        got = L.predict(L.candidate_endpoints(c), self.cells())
        self.assertTrue(got["checker-rest-96"]["clamped"])
        self.assertAlmostEqual(got["checker-rest-96"]["excess"], 0.062, delta=0.0015)
        self.assertAlmostEqual(got["checker-inactive-96"]["excess"], 0.068, delta=0.0015)
        self.assertAlmostEqual(got["light-solid-rest-96"]["excess"], 0.227, delta=0.002)
        self.assertFalse(got["dark-solid-rest-96"]["clamped"])
        self.assertEqual(L.mechanism(got["checker-rest-96"]), "clamp")

    def test_the_opacity_lift_is_applied(self):
        # Partial authority and a nonzero lightward lift: the impulse rrect-sm input at tintAlpha 0.5
        # (the review's case: the shader's lifted composite 0.0359831524 at both scales).
        c = fake_candidate(SCRATCH / "lift", tint={"active.dark": 0.5, "receded.dark": 0.5})
        cell = [dict(id="impulse-sm", pose="rest", span=32, encoded=0.00375, linear=0.00375)]
        got = L.predict(L.candidate_endpoints(c), cell)["impulse-sm"]
        self.assertGreater(got["alphaLift"], 0)
        self.assertLess(got["authority"], 1)
        lifted = got["sizedAlpha"] + got["alphaLift"]
        self.assertAlmostEqual(got["achieved"], (1 - lifted) * 0.00375 + lifted * got["solved"], places=15)
        self.assertAlmostEqual(got["achieved"], 0.0359831524, delta=2e-6)

    def test_the_attribution(self):
        rung = dict(collapsed=False, toneAdapt=0, clamped=True, authority=1, achieved=0.20, excess=0.02,
                    sizedAlpha=0.6, response=0.18)
        shipped = dict(collapsed=False, toneAdapt=0, clamped=False, authority=1, achieved=0.18, excess=0,
                       sizedAlpha=0.9, response=0.18)
        self.assertEqual(L.attribute(0.019, rung, shipped)["attribution"], "clamp")
        self.assertEqual(L.attribute(-0.019, rung, shipped)["attribution"], "unexplained")
        held = dict(rung, clamped=False, achieved=0.18, excess=0)
        self.assertEqual(L.attribute(0.01, held, shipped)["attribution"], "unexplained")
        low = dict(held, authority=0.4, achieved=0.19)
        self.assertEqual(L.attribute(0.01, low, shipped)["attribution"], "authority")

    def test_the_backdrop_means(self):
        self.assertEqual([round(x, 6) for x in L.backdrop_means("checkerboard__rrect-md__rest", 2, False)], [0.5, 0.5])
        e, l = L.backdrop_means("light-solid__rrect-lg__rest", 1, False)
        self.assertAlmostEqual(e, 0.9505, places=3)


class OperatorOne(unittest.TestCase):
    """Operator 1 in the arithmetic (W47). The identity reads now; the graded alpha waits on the runtime."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def cells(self):
        return [dict(id=f"{p}-{s}-{d}x", pose=p, span=s, encoded=0.5, linear=0.5, dpr=d)
                for p in ("rest", "inactive") for s in (44, 96, 128, 160) for d in (1, 2)]

    def test_at_identity_alpha_base_is_tint_alpha(self):
        for endpoints in (L.shipped_endpoints(),
                          L.candidate_endpoints(fake_candidate(SCRATCH / "zero", extra={
                              "active.dark": {"tintAlphaFar1x": 0, "tintAlphaFar2x": 0}}))):
            got = L.predict(endpoints, self.cells())
            for key, p in got.items():
                self.assertEqual(p["farDelta"], 0, key)
                self.assertEqual(p["alphaBase"], p["tintAlpha"], key)
                gain = 0.05
                self.assertAlmostEqual(p["sizedAlpha"], p["tintAlpha"] + gain * p["sizeK"] * (1 - p["tintAlpha"]),
                                       places=15)
            for d in (1, 2):
                self.assertEqual(got[f"rest-96-{d}x"]["farS"], 0)
                self.assertAlmostEqual(got[f"rest-128-{d}x"]["farS"], 0.104, places=12)
                self.assertAlmostEqual(got[f"rest-160-{d}x"]["farS"], 0.352, places=12)
            self.assertEqual(got["rest-160-2x"]["tintAlpha"], 0.9)
            self.assertEqual(got["inactive-160-2x"]["tintAlpha"], 0.89)

    def test_a_far_delta_grades_the_alpha(self):
        c = fake_candidate(SCRATCH / "far", tint={"active.dark": 0.7},
                           extra={"active.dark": {"tintAlphaFar1x": 0.2, "tintAlphaFar2x": 0.45}})
        try:
            got = L.predict(L.candidate_endpoints(c), self.cells())
        except W.Refusal as refusal:
            self.assertIn("WAITING", str(refusal))
            self.skipTest("WAITING for operator 1's runtime (G0 (a)): @vitrea/renderer-webgpu exports no "
                          "tintAlphaFarAtScale on this branch, so a non-zero far delta is refused, not evaluated")
        for d, delta in ((1, 0.2), (2, 0.45)):
            for span in (44, 96, 128, 160):
                p = got[f"rest-{span}-{d}x"]
                self.assertEqual(p["operator1"], "runtime")
                self.assertAlmostEqual(p["farDelta"], delta, places=15)
                self.assertAlmostEqual(p["alphaBase"], min(1, max(0, 0.7 + delta * p["farS"])), places=15)
                self.assertAlmostEqual(p["sizedAlpha"], p["alphaBase"] + 0.05 * p["sizeK"] * (1 - p["alphaBase"]),
                                       places=15)
            self.assertEqual(got[f"rest-96-{d}x"]["alphaBase"], 0.7)
        self.assertAlmostEqual(got["rest-160-2x"]["alphaBase"], 0.7 + 0.45 * 0.352, places=12)
        clamp = fake_candidate(SCRATCH / "clamp", extra={"active.dark": {"tintAlphaFar2x": 0.6}})
        top = L.predict(L.candidate_endpoints(clamp), [dict(id="x", pose="rest", span=256, encoded=0.5,
                                                             linear=0.5, dpr=2)])["x"]
        self.assertEqual(top["alphaBase"], 1)


if __name__ == "__main__":
    unittest.main()
