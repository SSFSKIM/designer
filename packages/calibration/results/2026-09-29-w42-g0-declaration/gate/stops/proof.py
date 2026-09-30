#!/usr/bin/env python3
"""W42 G0 gate: the directional stops' reader proof (charter clauses 2 and 10) -> proof.txt.

The tolerances are the declaration's `proofTolerances`, written before this ran. Synthetic
images carry known answers; the end-to-end part runs `stops.py` itself on candidate trees built
in a temporary directory outside the repository from the shipped captures, moved by known
amounts, and on trees that must be refused. Natives are read only through the stops' own
role-checked loader.

    OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3.12 -B proof.py
"""
from __future__ import annotations

import json
import shutil
import statistics as pystats
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import signal

import stops_common as common
import halo
import chroma_band as cb

HERE = Path(__file__).resolve().parent
OUT = HERE / "proof.txt"
LINES: list[str] = []
FAILED: list[str] = []


def log(text: str = "") -> None:
    LINES.append(text)
    print(text, flush=True)


def check(name: str, ok: bool, detail: str) -> None:
    log(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        FAILED.append(name)


# ---------------------------------------------------------------------------------------------
# Colour helpers for the synthetic fields (the inverse of the reader's OKLab).

def srgb_encode(linear: np.ndarray) -> np.ndarray:
    x = np.clip(linear, 0, 1)
    return 255.0 * np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def oklab_to_linear(lab: np.ndarray) -> np.ndarray:
    lms = (lab @ np.linalg.inv(cb.OK_M2).T) ** 3
    return lms @ np.linalg.inv(cb.OK_M1).T


def plane_waves(scale: int, waves: list[tuple[float, float, float, float]]) -> np.ndarray:
    """sum of amp * cos(2 pi (x cos t + y sin t) / lam + phase), x, y in CSS px."""
    xs, ys = common.pixel_grid(scale)
    field = np.zeros_like(xs)
    for amp, lam, theta, phase in waves:
        field += amp * np.cos(2 * np.pi * (xs * np.cos(theta) + ys * np.sin(theta)) / lam + phase)
    return field


def random_waves(rng, count, lam_lo, lam_hi, amp):
    return [(amp, float(np.exp(rng.uniform(np.log(lam_lo), np.log(lam_hi)))),
             float(rng.uniform(0, np.pi)), float(rng.uniform(0, 2 * np.pi))) for _ in range(count)]


def response(lam: float, sigma: float) -> float:
    return float(np.exp(-2 * np.pi ** 2 * sigma ** 2 / lam ** 2))


# ---------------------------------------------------------------------------------------------

def proof_geometry() -> None:
    log("G. Geometry: scenes.json components against every shipped cell's report surfaces")
    worst, n = 0.0, 0
    for stop, kind, untinted in (("stopH", "impulse", False), ("stopP", "photo", True)):
        for profile, scene in common.declared_population(stop, kind, untinted):
            report = json.loads((common.CANONICAL_CAPTURES / profile / scene /
                                 "report__webgpu.json").read_text())
            web = sorted((s["bounds"]["x"], s["bounds"]["y"], s["bounds"]["width"],
                          s["bounds"]["height"], s["radius"]) for s in report["page"]["surfaces"])
            ours = sorted((s["x"], s["y"], s["width"], s["height"], s["radius"])
                          for s in common.surfaces(common.parse_scene(scene)[1]))
            worst = max(worst, max(abs(a - b) for u, v in zip(web, ours) for a, b in zip(u, v))
                        if len(web) == len(ours) else float("inf"))
            n += 1
    check("geometry", worst == 0.0, f"{n} population cells, largest bound/radius difference "
          f"{worst} CSS px")


def proof_admission() -> None:
    log("H-A. Admission, from geometry alone (declared list enforced by halo.admitted)")
    for component in ("capsule-button", "rrect-md"):
        extent = halo.lens_extent(component)
        for scale in (1, 2):
            got = halo.admitted(component, scale)
            check(f"admitted {component} {scale}x", list(got) == [(160.0, 104.0)],
                  f"{list(got)}; lens extent {extent:.3f} CSS px")
            depth = common.depth_map(component, scale)
            xs, ys = common.pixel_grid(scale)
            for cx, cy in halo.dots(scale):
                centre = -float(common.sdf_at(component, np.array(cx), np.array(cy)))
                if centre <= 0:
                    continue
                dmin = float(depth[np.hypot(xs - cx, ys - cy) < 10].min())
                verdict = "admitted" if dmin >= 2 and centre >= extent else "not admitted"
                log(f"      {component} {scale}x dot ({cx:.0f}, {cy:.0f}): min depth over r < 10 "
                    f"{dmin:.2f}, centroid depth {centre:.2f} -> {verdict}")


def brute_halo(image: np.ndarray, scale: int, centre) -> dict:
    """An independent per-pixel loop over a window around the dot."""
    y = image[..., 0] * 0.2126 + image[..., 1] * 0.7152 + image[..., 2] * 0.0722
    core, ann, flo = [], [], []
    cx, cy = centre
    for j in range(int((cy - 11) * scale), int((cy + 11) * scale) + 1):
        for i in range(int((cx - 11) * scale), int((cx + 11) * scale) + 1):
            r = ((((i + 0.5) / scale) - cx) ** 2 + (((j + 0.5) / scale) - cy) ** 2) ** 0.5
            (core if r < 2 else ann if r < 8 else flo if r < 10 else []).append(float(y[j, i]))
    floor = pystats.median(flo)
    return dict(peak=sum(core) / len(core) - floor, annulus=sum(ann) / len(ann) - floor,
                floor=floor)


def halo_truth(amp: float, sigma: float) -> dict:
    s2 = 2 * sigma ** 2
    core = amp * (s2 / 4) * (1 - np.exp(-4 / s2))
    floor = amp * np.exp(-((8 ** 2 + 10 ** 2) / 2) / s2)
    ann = amp * s2 * (np.exp(-4 / s2) - np.exp(-64 / s2)) / (64 - 4)
    return dict(peak=core - floor, annulus=ann - floor)


def synthetic_halo(component: str, scale: int, amp: float, sigma: float, side: float) -> np.ndarray:
    depth = common.depth_map(component, scale)
    xs, ys = common.pixel_grid(scale)
    field = np.where(depth >= 0, 120.0, 255.0)
    for cx, cy in halo.dots(scale):
        a = amp if (cx, cy) == (160.0, 104.0) else side
        field = field + np.where(depth >= 0,
                                 a * np.exp(-((xs - cx) ** 2 + (ys - cy) ** 2) / (2 * sigma ** 2)), 0)
    return np.repeat(field[..., None], 3, -1)


def proof_halo_synthetic() -> None:
    log("H-S. Synthetic halos on a flat 120-code body (255 outside the shape)")
    worst = dict(impl=0.0, quant=0.0, recovery=0.0)
    ok_recovery = True
    rows = []
    for component in ("capsule-button", "rrect-md"):
        for scale in (1, 2):
            for sigma in (1.0, 1.5, 3.0, 5.0):
                for amp in (8.0, 40.0):
                    flo = synthetic_halo(component, scale, amp, sigma, side=0.0)
                    got = halo.cell_statistics(flo, component, scale)["cell"]
                    brute = brute_halo(flo, scale, (160.0, 104.0))
                    quant = halo.cell_statistics(np.round(flo), component, scale)["cell"]
                    truth = halo_truth(amp, sigma)
                    for s in halo.STATISTICS:
                        worst["impl"] = max(worst["impl"], abs(got[s] - brute[s]))
                        worst["quant"] = max(worst["quant"], abs(quant[s] - got[s]))
                    for s in ("peak", "annulus"):
                        err = abs(quant[s] - truth[s])
                        worst["recovery"] = max(worst["recovery"], err)
                        if err > 1.0 + 0.03 * amp:
                            ok_recovery = False
                    rows.append(f"      {component:<15}{scale}x sigma {sigma:3.1f} A {amp:4.0f}: "
                                f"peak read {quant['peak']:6.2f} truth {truth['peak']:6.2f} | "
                                f"annulus read {quant['annulus']:5.2f} truth "
                                f"{truth['annulus']:5.2f}")
    check("H implementation", worst["impl"] <= 1e-9,
          f"largest |reader - per-pixel loop| over peak, annulus and floor {worst['impl']:.2e} "
          "code (tolerance 1e-9)")
    check("H quantisation", worst["quant"] <= 1.0,
          f"largest |rounded - unrounded| over peak, annulus and floor {worst['quant']:.3f} code "
          "(tolerance 1)")
    check("H recovery", ok_recovery, f"largest |read - continuous truth| {worst['recovery']:.3f} "
          "code (tolerance 1 + 0.03 A per case)")
    for row in rows:
        log(row)
    diff = 0.0
    for scale in (1, 2):
        quiet = halo.cell_statistics(np.round(synthetic_halo("rrect-md", scale, 40.0, 3.0, 0.0)),
                                     "rrect-md", scale)["cell"]
        loud = halo.cell_statistics(np.round(synthetic_halo("rrect-md", scale, 40.0, 3.0, 120.0)),
                                    "rrect-md", scale)["cell"]
        diff = max(diff, *(abs(quiet[s] - loud[s]) for s in quiet))
    check("H side dots", diff <= 1e-9, f"rrect-md side dots at 3 A change the reading by {diff:.1e}")


def proof_halo_floor() -> None:
    """G9 (the gate review of b151aff4, finding 9): a too-wide halo reads as a closer peak."""
    log("H-F. The floor statistic (version 2): a too-wide halo against a narrow Apple")
    log("      flat 120-code body; Apple sigma 1.5 A 8, shipped sigma 1.5 A 40, candidate sigma 20 "
        "A 30; rounded to codes")
    ok, rows = True, []
    for component in ("capsule-button", "rrect-md"):
        for scale in (1, 2):
            read = {name: halo.cell_statistics(np.round(synthetic_halo(component, scale, amp,
                                                                         sigma, 0.0)),
                                               component, scale)["cell"]
                    for name, (amp, sigma) in dict(native=(8.0, 1.5), shipped=(40.0, 1.5),
                                                   candidate=(30.0, 20.0)).items()}
            judged = {s: common.judge(read["native"][s], read["shipped"][s], read["candidate"][s],
                                      halo.RES) for s in halo.STATISTICS}
            verdicts = {s: j["verdict"] for s, j in judged.items()}
            cell = common.combine(list(verdicts.values()))
            ok &= (verdicts == dict(peak="pass", annulus="pass", floor="FAIL") and cell == "FAIL")
            rows.append(f"      {component:<15}{scale}x " + " | ".join(
                f"{s} nat {j['native']:6.2f} ship {j['shipped']:6.2f} cand {j['candidate']:6.2f} "
                f"margin {j['margin']:6.2f} {j['verdict']}" for s, j in judged.items())
                + f" -> cell {cell}")
    check("H floor sees a too-wide halo", ok,
          "on both shapes at both scales the sigma-20 candidate passes peak and annulus (the "
          "narrow reading it defeats) and FAILs floor, so the cell FAILs")
    for row in rows:
        log(row)


# ---------------------------------------------------------------------------------------------

def fft_band_energies(ab: np.ndarray, mask: np.ndarray, scale: int) -> dict:
    """The same masked band filter by explicit 2-D kernels and FFT convolution."""
    m = mask.astype(np.float64)
    blurs = {}
    for sigma in (1.0, 4.0, 16.0):
        sd = sigma * scale
        r = int(np.ceil(4 * sd))
        x = np.arange(-r, r + 1, dtype=np.float64)
        g = np.exp(-(x[:, None] ** 2 + x[None, :] ** 2) / (2 * sd * sd))
        g /= g.sum()
        norm = signal.fftconvolve(m, g, mode="same")
        with np.errstate(invalid="ignore", divide="ignore"):
            blurs[sigma] = np.stack([signal.fftconvolve(ab[..., c] * m, g, mode="same") / norm
                                     for c in range(2)], -1)
    out = {}
    for name, (lo, hi) in cb.BANDS.items():
        with np.errstate(invalid="ignore"):
            band = blurs[lo] - blurs[hi]
        out[name] = float(np.sqrt((band[mask] ** 2).sum(-1).mean()))
    return out


def synthetic_lab(scale: int, rng, lightness: float = 0.75) -> np.ndarray:
    waves_a = random_waves(rng, 24, 3.0, 60.0, 0.006)
    waves_b = random_waves(rng, 24, 3.0, 60.0, 0.006)
    return np.stack([np.full(common.pixel_grid(scale)[0].shape, lightness),
                     plane_waves(scale, waves_a), plane_waves(scale, waves_b)], -1)


def lab_to_codes(lab: np.ndarray) -> tuple[np.ndarray, bool]:
    linear = oklab_to_linear(lab)
    in_gamut = bool((linear >= 0).all() and (linear <= 1).all())
    return srgb_encode(linear), in_gamut


def proof_chroma_synthetic() -> None:
    log("P-S. Synthetic OKLab fields (L 0.75, 24 plane waves per channel, lambda 3-60 CSS px)")
    rng = np.random.default_rng(20260929)
    worst_impl, worst_quant_ratio, gamut = 0.0, 0.0, True
    rows = []
    for component in ("capsule-button", "rrect-md", "rrect-ml", "rrect-sm", "toolbar-group"):
        for scale in (1, 2):
            lab = synthetic_lab(scale, rng)
            codes_float, ok = lab_to_codes(lab)
            gamut &= ok
            mask = cb.region(component, scale)
            ab = lab[..., 1:]
            tool = cb.energies_of_ab(ab, mask, scale)
            fft = fft_band_energies(ab, mask, scale)
            quant_codes = np.round(codes_float)
            quant = cb.energies(quant_codes, component, scale)
            res = cb.resolution_of(quant_codes, mask, scale)
            for band in cb.BANDS:
                worst_impl = max(worst_impl, abs(tool[band] - fft[band]) / fft[band])
                worst_quant_ratio = max(worst_quant_ratio,
                                        abs(quant[band] - tool[band]) / res[band])
            rows.append(f"      {component:<15}{scale}x  F {tool['F'] * 1e3:6.3f} read "
                        f"{quant['F'] * 1e3:6.3f} (res {res['F'] * 1e3:.3f})   M "
                        f"{tool['M'] * 1e3:6.3f} read {quant['M'] * 1e3:6.3f} "
                        f"(res {res['M'] * 1e3:.3f})  x1e-3")
    check("P implementation", worst_impl <= 1e-9,
          f"largest relative |reader - FFT implementation| {worst_impl:.2e} (tolerance 1e-9)")
    check("P gamut", gamut, "every synthetic field is inside the sRGB gamut (nothing clipped)")
    check("P quantisation", worst_quant_ratio <= 1.0,
          f"largest |rounded - unrounded| / res_band {worst_quant_ratio:.3f} (tolerance 1)")
    for row in rows:
        log(row)

    log("P-R. Known band energy: plane waves on the full canvas, read >= 64 CSS px from its border")
    worst = 0.0
    ok_all = True
    for scale in (1, 2):
        xs, ys = common.pixel_grid(scale)
        region = (xs >= 64) & (xs <= 320 - 64) & (ys >= 64) & (ys <= 200 - 64)
        support = np.ones_like(region)
        for label, lo, hi, amp in (("F-band noise", 4.0, 8.0, 0.010), ("M-band noise", 20.0, 48.0, 0.012),
                                   ("broad noise", 3.0, 60.0, 0.008)):
            wa, wb = random_waves(rng, 16, lo, hi, amp), random_waves(rng, 16, lo, hi, amp)
            lab = np.stack([np.full(xs.shape, 0.75), plane_waves(scale, wa), plane_waves(scale, wb)], -1)
            codes, ok = lab_to_codes(lab)
            codes = np.round(codes)
            read_ab = cb.oklab_ab(codes)
            fields = cb.band_fields(read_ab, support, scale)
            res = cb.resolution_of(codes, region, scale)
            for band, (s_lo, s_hi) in cb.BANDS.items():
                true_a = plane_waves(scale, [(a * (response(l, s_lo) - response(l, s_hi)), l, t, p)
                                             for a, l, t, p in wa])
                true_b = plane_waves(scale, [(a * (response(l, s_lo) - response(l, s_hi)), l, t, p)
                                             for a, l, t, p in wb])
                truth = float(np.sqrt((true_a[region] ** 2 + true_b[region] ** 2).mean()))
                read = float(np.sqrt((fields[band][region] ** 2).sum(-1).mean()))
                tol = res[band] + 0.01 * truth
                worst = max(worst, abs(read - truth) / tol)
                ok_all &= ok and abs(read - truth) <= tol
                log(f"      {scale}x {label:<13} {band}: read {read * 1e3:7.3f} truth "
                    f"{truth * 1e3:7.3f} (tolerance {tol * 1e3:.3f}) x1e-3")
    check("P recovery", ok_all, f"largest |read - truth| / tolerance {worst:.3f} "
          "(tolerance res_band + 1 % of the truth)")

    log("P-Q. The analytic res_band against a 64-draw Monte Carlo of the one-code field")
    worst = 0.0
    for component, scale in (("rrect-md", 1), ("rrect-md", 2), ("capsule-button", 1)):
        codes = np.round(lab_to_codes(synthetic_lab(scale, rng))[0])
        assert codes.min() >= 1 and codes.max() <= 254, "the Monte Carlo cell must be off the rails"
        mask = cb.region(component, scale)
        analytic = cb.resolution_of(codes, mask, scale)
        base = cb.band_fields(cb.oklab_ab(codes), mask, scale)
        acc = {band: 0.0 for band in cb.BANDS}
        for _ in range(64):
            q = rng.uniform(-0.5, 0.5, codes.shape) - rng.uniform(-0.5, 0.5, codes.shape)
            moved = cb.band_fields(cb.oklab_ab(codes + q), mask, scale)
            for band in cb.BANDS:
                acc[band] += ((moved[band] - base[band])[mask] ** 2).sum(-1).mean()
        for band in cb.BANDS:
            mc = np.sqrt(acc[band] / 64)
            worst = max(worst, abs(mc - analytic[band]) / analytic[band])
            log(f"      {component:<15}{scale}x {band}: analytic {analytic[band] * 1e3:.5f} "
                f"Monte Carlo {mc * 1e3:.5f} x1e-3")
    check("P resolution", worst <= 0.05, f"largest relative difference {worst:.3f} (tolerance 0.05)")


# ---------------------------------------------------------------------------------------------
# End to end: stops.py on candidate trees.

def run_stops(candidate: Path, stop: str, out: Path, extra: list[str] | None = None,
              shipped: Path | None = None) -> tuple[int, str, dict | None]:
    cmd = [sys.executable, "-B", str(HERE / "stops.py"), "--candidate-root", str(candidate),
           "--stop", stop, "--out", str(out)] + (extra or [])
    if shipped is not None:
        cmd += ["--shipped-root", str(shipped)]
    done = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
    result = json.loads(out.read_text()) if out.exists() and done.returncode in (0, 1) \
        and "refused" not in done.stderr else None
    return done.returncode, done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "", result


class Scratch:
    """Scratch documents (copies of the shipped ones with one byte added) and candidate trees."""

    def __init__(self, root: Path):
        self.root = root
        self.documents: dict[str, tuple[str, str]] = {}

    def document(self, repo_path: str) -> tuple[str, str]:
        if repo_path not in self.documents:
            target = self.root / "documents" / Path(repo_path).name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((common.REPO / repo_path).read_bytes() + b"\n")
            self.documents[repo_path] = (str(target), common.sha256_file(target)[:12])
        return self.documents[repo_path]

    def cell(self, tree: str, profile: str, scene: str, image: np.ndarray | None = None,
             meta_edit=None, rewrite: bool = True) -> None:
        src = common.CANONICAL_CAPTURES / profile / scene
        dst = self.root / tree / profile / scene
        dst.mkdir(parents=True, exist_ok=True)
        meta = json.loads((src / "cell__webgpu.json").read_text())
        path = meta["capturePath"]
        for kind, repo_path, digest in common.DOCUMENT.findall(path) if rewrite else ():
            scratch_path, scratch_digest = self.document(repo_path)
            path = path.replace(f"{kind}={repo_path} sha256:{digest}",
                                f"{kind}={scratch_path} sha256:{scratch_digest}")
        meta["capturePath"] = path
        if meta_edit:
            meta_edit(meta)
        (dst / "cell__webgpu.json").write_text(json.dumps(meta, indent=2) + "\n")
        png = dst / f"{scene}__webgpu.png"
        if image is None:
            shutil.copyfile(src / f"{scene}__webgpu.png", png)
        else:
            assert image.min() >= 0 and image.max() <= 255
            Image.fromarray(image.astype(np.uint8), "RGB").save(png)

    def documents_args(self) -> list[str]:
        return [a for p, _h in self.documents.values() for a in ("--document", p)]


def reason(err: str) -> str:
    """A refusal's reason without the temporary directory's path."""
    tail = err.split("w42-stops-proof-")[-1]
    return tail.split("/", 1)[-1][-170:] if "/" in tail else tail[-170:]


def away(shipped: float, native: float) -> float:
    return 1.0 if shipped >= native else -1.0


def proof_end_to_end() -> None:
    log("E1. The shipped render: refused as a candidate, read as the identity and as the baseline")
    work = Path(tempfile.mkdtemp(prefix="w42-stops-proof-"))
    try:
        code, err, _run = run_stops(common.CANONICAL_CAPTURES, "both", work / "e1-refused.json")
        check("E1 shipped tree refused as a candidate",
              code == 1 and "is no candidate" in err and not (work / "e1-refused.json").exists(),
              f"the canonical tree as --candidate-root without --baseline: exit {code}, no output: "
              f"...{reason(err)}")

        scratch = Scratch(work)
        halo_cells = halo.population()
        for profile, scene in halo_cells + cb.population():
            scratch.cell("identity", profile, scene)
        code, _err, run = run_stops(work / "identity", "both", work / "e1.json",
                                    scratch.documents_args())
        stats = [s for stop in run["stops"].values() for c in stop["cells"]
                 for s in c["statistics"].values()]
        zero = all(s["dCand"] - s["dShip"] == 0.0 for s in stats)
        check("E1 identity", code == 0 and zero and run["summary"]["verdict"] == "pass"
              and run["admission"]["mode"] == "candidate"
              and not run["admission"]["candidateNamesShippedDocuments"]
              and all("matchedDeclaredFile" in d for d in run["admission"]["documents"]),
              f"the shipped captures re-named at {len(scratch.documents)} declared scratch "
              f"documents: exit {code}, {len(stats)} statistics on "
              f"{sum(len(s['cells']) for s in run['stops'].values())} cells, every "
              f"dCand - dShip == 0: {zero}, verdict {run['summary']['verdict']}, stamped "
              f"{run['admission']['mode']}")
        baseline = {(c["profile"], c["scene"]): c for stop in run["stops"].values()
                    for c in stop["cells"]}

        code, _err, run = run_stops(common.CANONICAL_CAPTURES, "both", work / "e1-baseline.json",
                                    ["--baseline"])
        stats = [s for stop in run["stops"].values() for c in stop["cells"]
                 for s in c["statistics"].values()]
        zero = all(s["dCand"] - s["dShip"] == 0.0 for s in stats)
        check("E1 baseline", code == 0 and zero and run["summary"]["verdict"] == "pass"
              and run["admission"]["mode"] == "baseline"
              and run["admission"]["candidateNamesShippedDocuments"],
              f"--baseline over the canonical tree: exit {code}, {len(stats)} statistics, every "
              f"dCand - dShip == 0: {zero}, stamped {run['admission']['mode']}")
        code, err, _run = run_stops(work / "identity", "halo", work / "e1-baseline-wrong.json",
                                    ["--baseline"])
        check("E1 baseline needs the shipped root", code == 1 and "--baseline" in err,
              f"--baseline with a candidate root that is not the shipped root: exit {code}: "
              f"...{reason(err)}")
        log("E2. Stop H moved by known amounts (captures name scratch documents)")
        for tree, shift, frac in (("h-far", 3, 1.0), ("h-within", 1, 0.5)):
            expected = {}
            for profile, scene in halo_cells:
                _s, scale = common.PROFILES[profile]
                cell = baseline[(profile, scene)]
                image = common.read_capture(common.CANONICAL_CAPTURES, profile, scene).image.copy()
                masks = halo.ring_masks(scale, (160.0, 104.0))
                flat = image.reshape(-1, 3)
                for ring, stat in (("core", "peak"), ("annulus", "annulus")):
                    s = cell["statistics"][stat]
                    idx = np.flatnonzero(masks[ring].ravel())
                    idx = idx[: int(round(len(idx) * frac))]
                    flat[idx] = np.clip(flat[idx] + shift * away(s["shipped"], s["native"]), 0, 255)
                expected[(profile, scene)] = brute_halo(image, scale, (160.0, 104.0))
                scratch.cell(tree, profile, scene, image)
            code, err, run = run_stops(work / tree, "halo", work / f"{tree}.json",
                                       scratch.documents_args())
            cells = run["stops"]["halo"]["cells"]
            exact = max(abs(c["statistics"][s]["candidate"] - expected[(c["profile"], c["scene"])][s])
                        for c in cells for s in halo.STATISTICS)
            growth = [c["statistics"][s]["dCand"] - c["statistics"][s]["dShip"]
                      for c in cells for s in ("peak", "annulus")]
            verdicts = {c["statistics"][s]["verdict"] for c in cells for s in ("peak", "annulus")}
            # The floor ring is not moved here, so the floor reads the shipped value exactly.
            floor_still = all(c["statistics"]["floor"]["dCand"] == c["statistics"]["floor"]["dShip"]
                              and c["statistics"]["floor"]["verdict"] == "pass" for c in cells)
            check(f"E2 {tree}: floor untouched", floor_still,
                  "the floor ring is not moved, and floor reads dCand - dShip == 0 and pass on "
                  f"all {len(cells)} cells")
            if tree == "h-far":
                check("E2 farther", code == 1 and verdicts == {"FAIL"} and min(growth) >= 2.0
                      and exact <= 1e-9,
                      f"exit {code}; every core and annulus moved 3 codes away from Apple in every "
                      f"channel (clipped at the rails): the distance grew by {min(growth):.3f}.."
                      f"{max(growth):.3f} codes, equal to an independent loop within {exact:.1e}, "
                      f"and every peak and annulus reads FAIL ({run['stops']['halo']['counts']})")
                docs = run["admission"]["documents"]
                check("E2 admission stamp", run["admission"]["mode"] == "candidate" and
                      len(docs) == 4 and all("matchedDeclaredFile" in d for d in docs) and
                      not run["admission"]["candidateNamesShippedDocuments"],
                      f"{len(docs)} scratch documents named and matched by hash: "
                      + ", ".join(f"{d['kind']} {d['sha256']} ({'/'.join(d['schemes'])})"
                                  for d in docs))
            else:
                check("E2 within resolution", code == 0 and verdicts == {"pass"}
                      and max(growth) <= 0.5 + 1e-9 and exact <= 1e-9,
                      f"exit {code}; half of each ring moved 1 code away: the distance grew by "
                      f"{min(growth):.3f}..{max(growth):.3f} codes (independent loop within "
                      f"{exact:.1e}) and every statistic reads pass "
                      f"({run['stops']['halo']['counts']})")

        # G9: the whole r < 10 disc moved 3 codes away from Apple's floor, in every channel.
        tree, expected, clipped = "h-floor", {}, 0
        for profile, scene in halo_cells:
            _s, scale = common.PROFILES[profile]
            s = baseline[(profile, scene)]["statistics"]["floor"]
            image = common.read_capture(common.CANONICAL_CAPTURES, profile, scene).image.copy()
            masks = halo.ring_masks(scale, (160.0, 104.0))
            disc = masks["core"] | masks["annulus"] | masks["floor"]
            moved = image[disc] + 3.0 * away(s["shipped"], s["native"])
            clipped += int(((moved < 0) | (moved > 255)).sum())
            image[disc] = np.clip(moved, 0, 255)
            expected[(profile, scene)] = brute_halo(image, scale, (160.0, 104.0))
            scratch.cell(tree, profile, scene, image)
        code, err, run = run_stops(work / tree, "halo", work / f"{tree}.json",
                                   scratch.documents_args())
        cells = run["stops"]["halo"]["cells"]
        exact = max(abs(c["statistics"][s]["candidate"] - expected[(c["profile"], c["scene"])][s])
                    for c in cells for s in halo.STATISTICS)
        still = max(abs(c["statistics"][s]["candidate"] - c["statistics"][s]["shipped"])
                    for c in cells for s in ("peak", "annulus"))
        kept = all(c["statistics"][s]["verdict"] == "pass" for c in cells for s in ("peak", "annulus"))
        grew = [c["statistics"]["floor"]["dCand"] - c["statistics"]["floor"]["dShip"] for c in cells]
        failed = all(c["statistics"]["floor"]["verdict"] == "FAIL" and c["verdict"] == "FAIL"
                     for c in cells)
        check("E2 floor farther", code == 1 and clipped == 0 and still <= 1e-9 and kept and failed
              and max(abs(g - 3.0) for g in grew) <= 1e-9 and exact <= 1e-9,
              f"exit {code}; the whole r < 10 disc moved 3 codes away from Apple's floor in every "
              f"channel ({clipped} channel values clipped): peak and annulus move by at most "
              f"{still:.1e} and pass, floor's distance grows by {min(grew):.6f}..{max(grew):.6f} "
              f"codes and FAILs on all {len(cells)} cells (independent loop within {exact:.1e}; "
              f"{run['stops']['halo']['counts']})")

        log("E3. Stop P moved by known amounts")
        photo_cells = cb.population()
        for band, lam, amp, smooth in (("F", 6.0, 0.012, 4.0), ("M", 32.0, 0.02, 16.0)):
            tree = f"p-far-{band}"
            expected = {}
            for profile, scene in photo_cells:
                _s, scale = common.PROFILES[profile]
                component = common.parse_scene(scene)[1]
                s = baseline[(profile, scene)]["statistics"][band]
                image = common.read_capture(common.CANONICAL_CAPTURES, profile, scene).image
                lab = cb.oklab(image)
                mask = cb.region(component, scale)
                ab = lab[..., 1:].copy()
                if s["shipped"] >= s["native"]:
                    wave = plane_waves(scale, [(amp, lam, 0.52, 0.0)])
                    wave_b = plane_waves(scale, [(amp, lam, 0.52, np.pi / 2)])
                    ab[..., 0] += np.where(mask, wave, 0)
                    ab[..., 1] += np.where(mask, wave_b, 0)
                else:
                    for c in range(2):
                        ab[..., c] = np.where(mask, cb.masked_blur(ab[..., c], mask,
                                                                   smooth * scale), ab[..., c])
                moved = np.concatenate([lab[..., :1], ab], -1)
                codes_float = srgb_encode(oklab_to_linear(moved))
                codes_float = np.where(mask[..., None], codes_float, image)
                expected[(profile, scene)] = cb.energies(codes_float, component, scale)[band]
                scratch.cell(tree, profile, scene, np.round(codes_float))
            code, err, run = run_stops(work / tree, "chroma", work / f"{tree}.json",
                                       scratch.documents_args())
            cells = run["stops"]["chroma"]["cells"]
            fails = sum(c["statistics"][band]["verdict"] == "FAIL" for c in cells)
            worst = max(abs(c["statistics"][band]["candidate"] - expected[(c["profile"], c["scene"])])
                        / c["statistics"][band]["res"] for c in cells)
            growth = [c["statistics"][band]["dCand"] - c["statistics"][band]["dShip"] for c in cells]
            ratio = [g / c["statistics"][band]["res"] for g, c in zip(growth, cells)]
            check(f"E3 farther in {band}", code == 1 and fails == len(cells) and worst <= 1.0,
                  f"exit {code}; {fails}/{len(cells)} cells FAIL on {band}; distance grew by "
                  f"{min(growth) * 1e3:.3f}..{max(growth) * 1e3:.3f} x1e-3 = "
                  f"{min(ratio):.1f}..{max(ratio):.1f} res; the read candidate energy is within "
                  f"{worst:.2f} res of the unrounded construction")
        tree = "p-within"
        rng = np.random.default_rng(7)
        for profile, scene in photo_cells:
            image = common.read_capture(common.CANONICAL_CAPTURES, profile, scene).image
            u = rng.uniform(0, 1, image.shape)
            q = np.where(u < 1 / 12, -1.0, np.where(u > 11 / 12, 1.0, 0.0))
            scratch.cell(tree, profile, scene, np.clip(image + q, 0, 255))
        code, err, run = run_stops(work / tree, "chroma", work / f"{tree}.json",
                                   scratch.documents_args())
        cells = run["stops"]["chroma"]["cells"]
        worst = max(abs(c["statistics"][b]["candidate"] - c["statistics"][b]["shipped"])
                    / c["statistics"][b]["res"] for c in cells for b in cb.BANDS)
        check("E3 within resolution", code == 0 and run["stops"]["chroma"]["verdict"] == "pass",
              f"exit {code}; the shipped render plus a one-code re-rounding field (variance 1/6 "
              f"per channel) reads pass on all {len(cells)} cells; largest |E_cand - E_ship| is "
              f"{worst:.3f} res")

        log("E4. Refusals and UNMEASURED")
        first = halo_cells[0]
        light = next(c for c in halo_cells if "light" in c[0])

        def refusal(name, tree, edit_cell, edit, extra=None, expect="refused"):
            for profile, scene in halo_cells:
                if (profile, scene) == edit_cell:
                    edit(scratch, tree, profile, scene)
                else:
                    scratch.cell(tree, profile, scene)
            code, err, _run = run_stops(work / tree, "halo", work / f"{tree}.json",
                                        scratch.documents_args() if extra is None else extra)
            check(name, code == 1 and expect in err, f"exit {code}: ...{reason(err)}")

        refusal("E4 scene mismatch", "r-scene", light,
                lambda s, t, p, c: s.cell(t, p, c, meta_edit=lambda m: m.update(
                    sceneId="impulse__rrect-md__rest" if c != "impulse__rrect-md__rest"
                    else "impulse__capsule-button__rest")))
        refusal("E4 scheme mismatch", "r-scheme", light,
                lambda s, t, p, c: s.cell(t, p, c, meta_edit=lambda m: m.update(
                    capturePath=m["capturePath"].replace("colorScheme=light,", "colorScheme=dark,"))))
        refusal("E4 size mismatch", "r-size", next(c for c in halo_cells if "-2x-" in c[0]),
                lambda s, t, p, c: s.cell(t, p, c, image=np.zeros((200, 320, 3))))

        def other_document(s, t, p, c):
            _path, digest = s.document(
                "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5.json")
            s.cell(t, p, c, meta_edit=lambda m: m.update(
                capturePath=m["capturePath"].replace(digest, "0123456789ab")))
        refusal("E4 mixed documents", "r-mixed", light, other_document, expect="two document sets")
        refusal("E4 undeclared document", "r-undeclared", first, lambda s, t, p, c: s.cell(t, p, c),
                extra=["--document", str(common.REPO / "packages/calibration/profiles/"
                                         "apple-macos-27.0-1x-light-standard-glass0.5.json")],
                expect="none of the declared documents")
        refusal("E4 undeclared documents, no --document", "r-nodocument", first,
                lambda s, t, p, c: s.cell(t, p, c), extra=[],
                expect="declare it with --document")
        for profile, scene in halo_cells:
            scratch.cell("partial", profile, scene, rewrite="light" in profile)
        light_docs = [a for p, _h in scratch.documents.values() if "light" in Path(p).name
                      for a in ("--document", p)]
        code, err, run = run_stops(work / "partial", "halo", work / "partial.json", light_docs)
        named = {(d["kind"], d["schemes"][0], d["isShippedDocument"]) for d in
                 run["admission"]["documents"]} if run else set()
        check("E4 shipped scheme needs no declaration", code == 0 and named == {
            ("materialProfile", "dark", True), ("recededProfile", "dark", True),
            ("materialProfile", "light", False), ("recededProfile", "light", False)},
              f"light at scratch documents declared by --document, dark left at the shipped "
              f"documents undeclared: exit {code}, admission {sorted(named)}")
        code, err, _run = run_stops(common.CANONICAL_CAPTURES, "halo", work / "r-shipped.json",
                                    shipped=work / "r-undeclared")
        check("E4 stale shipped tree", code == 1 and "not the shipped generation" in err,
              f"a shipped root whose captures name scratch documents: exit {code}: "
              f"...{reason(err)}")

        for profile, scene in halo_cells:
            if (profile, scene) != light:
                scratch.cell("missing", profile, scene)
        code, err, run = run_stops(work / "missing", "halo", work / "missing.json",
                                   scratch.documents_args())
        missing = [c for c in run["stops"]["halo"]["cells"] if c["verdict"] == "UNMEASURED"]
        check("E4 missing candidate cell", code == 1 and run["summary"]["verdict"] == "UNMEASURED"
              and [(c["profile"], c["scene"]) for c in missing] == [light],
              f"exit {code}; {light[0]}/{light[1]} absent from the candidate reads UNMEASURED and "
              f"the stop reads {run['summary']['verdict']}, not pass")

        refused = []
        for scene in ("photo__rrect-lg__rest", "impulse__rrect-ml__rest",
                      "photo__capsule-button__pressed"):
            try:
                common.native_path("apple-macos-27.0-1x-light-standard-glass0.5", scene)
                refused.append(f"{scene} NOT refused")
            except PermissionError as error:
                refused.append(str(error).split(":")[0])
        roles = [common.ROLE.get(s) for s in ("photo__rrect-lg__rest", "impulse__rrect-ml__rest",
                                               "photo__capsule-button__pressed")]
        check("E4 native role guard", all("NOT" not in r for r in refused),
              f"holdout / probe / {roles[2]} scenes raise before a path is formed: {refused}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    started = time.time()
    log("# W42 G0 gate: the directional stops' reader proof (charter clauses 2 and 10)")
    log(f"# declaration sha256:{common.sha256_file(common.DECLARATION_PATH)}")
    log("# tolerances: stops-declaration.json proofTolerances, declared before this ran")
    log("")
    proof_geometry()
    proof_admission()
    proof_halo_synthetic()
    proof_halo_floor()
    proof_chroma_synthetic()
    proof_end_to_end()
    log("")
    log(f"# {len(FAILED)} check(s) failed{': ' + ', '.join(FAILED) if FAILED else ''}; "
        f"{time.time() - started:.0f} s")
    OUT.write_text("\n".join(LINES) + "\n")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
