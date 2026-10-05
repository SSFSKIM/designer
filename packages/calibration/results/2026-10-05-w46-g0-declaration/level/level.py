#!/usr/bin/env python3.12
"""W46 G0 (d): the level check (charter X61; G0 (d); Design "The ladders", v1.2). A CHECK, not a solver:
no W46 tool writes a re-solve of the tone ordinates into a document. For a candidate rendered on ladder
(i)'s cells it reads, against the published `d0219cd684bf` generation:

  1. **L1** on its declared population (the dark calibration and validation scenes, both scales,
     WebGPU), through the cuts' own `cut_l1` (absolute |web − native| ≤ 0.055; growth against the
     reference's error ≤ 0.005), on the cells the rung rendered;
  2. **the level rows**: every rendered cell's interior-mean change against the reference row,
     the solid and impulse probes among them;
  3. **the attribution**: each excess (an L1 growth or absolute miss, or a level change beyond
     L1's growth bound) is attributed to the stand-down the shader's own arithmetic predicts for
     that cell at that rung — `clamp` (the neutral clamped at 0, the composite left above its
     target), `authority` (between black and the dark anchor the solve has partial authority),
     `collapse` (toneAdapt owns the pixel) — or named `unexplained` when the arithmetic predicts
     no move of that sign. The arithmetic is `arith.ts`, the runtime's exported functions, on the
     backdrop's encoded and linear means from the background fixture (the whole source; the
     silhouette's for a document whose `backdropToneAbscissa` is `silhouette`).

**Identity** (`identity`): the shipped rung (`tintAlpha` 0.9 active, 0.89 receded, every ordinate held)
must reproduce the published generation on every cell it rendered as PIXEL identity — the candidate
capture's PNG and alpha PNG byte-equal to the canonical tree's — and MEASUREMENT identity — every
measured row field equal under the explicit projection `measured()`, which removes exactly the
provenance fields: `capturedAt`, and `key.web.capturePath`, which candidate mode stamps with the
candidate document (`scripts/capture-web.ts`) even at identical pixels. The provenance is VALIDATED
and retained: the path's driver prefix (browser, viewport, scale, scheme, frames) must equal the
published row's, its document clause must name this candidate's declaration at its hash, and the
engine must be the pinned Chromium (`census-gate.pinned_engine`).

    python3.12 -B level.py identity --candidate DIR --matrix M.json [--matrix M2.json] --captures ROOT [--out F]
    python3.12 -B level.py check --candidate DIR --matrix M.json [...] --captures ROOT [--pose rest|inactive] [--out F]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
import bindings as W  # noqa: E402

B, T1, RULE = W.load_cuts()
sys.path.insert(1, str(W.W44_G1 / "cuts"))
import cuts as C  # noqa: E402  (W46's cuts; its L1 arithmetic and constants)

P = W.load_module("w46_level_interior", W.PORT / "interior.py")
CENSUS = W.load_module("w46_census_gate", EVIDENCE / "census-gate.py")
ARITH = HERE / "arith.ts"
BACKGROUNDS = W.ROOT / "apps/reference-apple/fixtures/backgrounds"
PROVENANCE = ("capturedAt", "key.web.capturePath")
SOLIDS = ("dark-solid", "mid-dark-solid", "mid-light-solid", "light-solid", "mid-chroma-solid")
LEVEL_TOLERANCE = C.L1_GROWTH         # a level change is an excess past L1's own growth bound
DRIVER_PREFIX = re.compile(r"^(.*?)(materialProfile=.*)$")


def sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


# ---------------------------------------------------------------------------------------------
# Identity: pixels, the measurement projection, the provenance
# ---------------------------------------------------------------------------------------------
def measured(row: dict) -> dict:
    """The explicit equality projection: the row without its provenance fields (`PROVENANCE`)."""
    out = json.loads(json.dumps(row))
    out.pop("capturedAt", None)
    out["key"]["web"].pop("capturePath", None)
    return out


def differing(a, b, prefix="") -> list[str]:
    """The leaf paths at which two JSON values differ (for the record of a failed projection)."""
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for k in sorted(set(a) | set(b)) for p in differing(a.get(k), b.get(k), f"{prefix}.{k}" if prefix else k)]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in differing(x, y, f"{prefix}[{i}]")]
    return [] if a == b else [prefix]


def provenance(row: dict, published: dict, candidate: B.Candidate) -> list[str]:
    """Why a candidate row's provenance is not candidate mode's stamp of this candidate over the
    published row's driver (empty when it is)."""
    why = []
    path, ref = row["key"]["web"]["capturePath"], published["key"]["web"]["capturePath"]
    mine, theirs = DRIVER_PREFIX.match(path), DRIVER_PREFIX.match(ref)
    if mine is None or theirs is None or mine.group(1) != theirs.group(1):
        why.append("the driver prefix is not the published row's")
    m = B.CANDIDATE_CLAUSE.search(path)
    if m is None or m.group(1) != candidate.path or m.group(2) != candidate.sha256[:12]:
        why.append(f"the document clause does not name {candidate.path} sha256:{candidate.sha256[:12]}")
    if "crossPosition=" in path:
        why.append("a cross-position stamp")
    why += [f"engine: {x}" for x in CENSUS.pinned_engine([row])]
    return why


def identity(rows: list, captures: Path, candidate: B.Candidate, reference: dict,
             canonical: Path = W.CANONICAL_CAPTURES) -> dict:
    """Pixel and measurement identity of every candidate row with the published row of its cell."""
    cells = []
    for row in rows:
        k = (row["key"]["profileKey"], row["key"]["web"]["renderer"], row["key"]["sceneId"])
        twin = reference.get(k)
        entry = dict(cell=" ".join(k))
        if twin is None:
            entry["fail"] = ["no published row"]
            cells.append(entry)
            continue
        fail = []
        for suffix in ("", "__alpha"):
            name = f"{k[2]}__{k[1]}{suffix}.png"
            mine, theirs = sha(captures / k[0] / k[2] / name), sha(canonical / k[0] / k[2] / name)
            entry[f"png{suffix or ''}"] = dict(candidate=mine, canonical=theirs)
            if mine is None or mine != theirs:
                fail.append(f"pixels: {name} {mine and mine[:12]} vs canonical {theirs and theirs[:12]}")
        diff = differing(measured(row), measured(twin))
        if diff:
            fail.append(f"measurement: {len(diff)} field(s) differ: {diff[:6]}")
        why = provenance(row, twin, candidate)
        entry["provenance"] = dict(capturePath=row["key"]["web"]["capturePath"], capturedAt=row.get("capturedAt"),
                                   valid=not why, why=why)
        if why:
            fail.append("provenance: " + "; ".join(why))
        entry["fail"] = fail
        cells.append(entry)
    failed = [c for c in cells if c["fail"]]
    return dict(cells=len(cells), pixelAndMeasurementIdentical=len(cells) - len(failed),
                failures=failed, verdict="IDENTICAL" if cells and not failed else "DIFFERS",
                projection=f"every field but {', '.join(PROVENANCE)}", perCell=cells)


# ---------------------------------------------------------------------------------------------
# The arithmetic's inputs and the attribution
# ---------------------------------------------------------------------------------------------
def encode(x: float) -> float:
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def decode(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def backdrop_means(sid: str, scale: int, silhouette: bool) -> tuple[float, float]:
    """(encodedInput, linear mean) of the scene's backdrop, as the host measures the tone: over the
    whole source, the level the Rec. 709 luminance of the per-channel decoded ENCODED means
    (`backdrop-tone.ts`); over the silhouette, the decoded mean of the encoded luma. The linear mean is
    the luminance of the linear channel means. The solve reads `encode(level)`."""
    image = P.read(BACKGROUNDS / f"{B.SCENES.by_id[sid]['background']}@{scale}x.png")
    if silhouette:
        mask = P.signed_distance(B.SCENES.component(sid), B.SCENES.canvas, scale, image.shape[:2]) < 0
        pixels = image[mask]
    else:
        pixels = image.reshape(-1, 3)
    enc = pixels / 255.0
    lin = _decode_array(enc)
    linear = float(np.dot(lin.mean(axis=0), (0.2126, 0.7152, 0.0722)))
    if silhouette:
        level = decode(float(np.dot(enc, (0.2126, 0.7152, 0.0722)).mean()))
    else:
        level = float(np.dot([decode(v) for v in enc.mean(axis=0)], (0.2126, 0.7152, 0.0722)))
    return encode(level), linear


def _decode_array(v: np.ndarray) -> np.ndarray:
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def abscissa_silhouette(document: dict) -> bool:
    a = document.get("patch", {}).get("backdropToneAbscissa")
    return isinstance(a, dict) and a.get("kind") == "silhouette"


def predict(endpoints: dict, cells: list[dict]) -> dict:
    """`arith.ts` on (endpoints, cells): the solve per cell, keyed by id."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "in.json"
        path.write_text(json.dumps(dict(endpoints=endpoints, cells=cells)))
        got = subprocess.run(["pnpm", "exec", "tsx", str(ARITH), str(path)], cwd=W.CAL, capture_output=True,
                             text=True)
    if got.returncode:
        raise W.Refusal(f"arith.ts: {got.stderr[-800:]}")
    return {c["id"]: c for c in json.loads(got.stdout)}


def arithmetic_cells(scenes: list[tuple[str, str]], silhouette: dict) -> list[dict]:
    out = []
    for profile, sid in scenes:
        scale, pose = B.scale_of(profile), ("inactive" if B.SCENES.inactive(sid) else "rest")
        e, l = backdrop_means(sid, scale, silhouette[pose])
        out.append(dict(id=f"{profile}/{sid}", pose=pose, span=B.SCENES.span(sid), encoded=e, linear=l, dpr=scale))
    return out


def mechanism(p: dict) -> str:
    if p["collapsed"] or p["toneAdapt"] > 0:
        return "collapse"
    if p["clamped"]:
        return "clamp"
    if p["authority"] < 0.999:
        return "authority"
    return "held"


def attribute(measured_delta: float | None, rung: dict, shipped: dict) -> dict:
    """The stand-down the arithmetic predicts for a cell between the shipped rung and this one."""
    predicted = rung["achieved"] - shipped["achieved"]
    mech = mechanism(rung) if mechanism(rung) != "held" else mechanism(shipped)
    out = dict(predictedDelta=predicted, mechanism=mech, clampedAtRung=rung["clamped"],
               authority=rung["authority"], excessAtRung=rung["excess"], sizedAlpha=rung["sizedAlpha"],
               response=rung["response"])
    if measured_delta is None:
        out["attribution"] = "UNMEASURED"
    elif mech == "held" or abs(predicted) < 1e-6 or (predicted > 0) != (measured_delta > 0):
        out["attribution"] = "unexplained"
    else:
        out["attribution"] = mech
    return out


# ---------------------------------------------------------------------------------------------
# The check
# ---------------------------------------------------------------------------------------------
def candidate_endpoints(candidate: B.Candidate) -> dict:
    return {"active": candidate.endpoints["active.dark"][0], "receded": candidate.endpoints["receded.dark"][0]}


def shipped_endpoints() -> dict:
    return {"active": str(W.document_path("active.dark")), "receded": str(W.document_path("receded.dark"))}


def check(rows: list, candidate: B.Candidate, reference_bed: B.Bed) -> dict:
    reference = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r for r in reference_bed.rows}
    rows = [r for r in rows if r["key"]["profileKey"] in W.DARK_025 and r["key"]["web"]["renderer"] == "webgpu"]
    bed = B.Bed("candidate", rows, [], candidate)
    l1 = C.cut_l1(bed, reference_bed, "webgpu")
    dark = lambda label: any(label.startswith(p) for p in W.DARK_025)  # noqa: E731
    l1_cells = [c for c in l1["cells"] if dark(c["cell"])]
    rendered = {(r["key"]["profileKey"], r["key"]["sceneId"]) for r in rows}
    l1_missing = sorted(f"{p}/{s}" for p in W.DARK_025 for s in B.SCENES.declared(p)
                        if B.SCENES.role[s] in ("calibration", "validation") and (p, s) not in rendered)
    docs = {pose: json.loads(Path(path).read_text()) for pose, path in candidate_endpoints(candidate).items()}
    silhouette = {"rest": abscissa_silhouette(docs["active"]),
                  "inactive": abscissa_silhouette(docs["receded"]) or abscissa_silhouette(docs["active"])}
    scenes = sorted(rendered)
    cells = arithmetic_cells(scenes, silhouette)
    at_rung = predict(candidate_endpoints(candidate), cells)
    at_shipped = predict(shipped_endpoints(), cells)
    levels, excesses = [], []
    l1_by = {c["cell"]: c for c in l1_cells}
    for profile, sid in scenes:
        key = f"{profile}/{sid}"
        row, ref = next(r for r in rows if (r["key"]["profileKey"], r["key"]["sceneId"]) == (profile, sid)), \
            reference[(profile, "webgpu", sid)]
        web, ref_web = B.value(row, "material", "interiorMeanWeb"), B.value(ref, "material", "interiorMeanWeb")
        delta = None if web is None or ref_web is None else web - ref_web
        entry = dict(cell=key, background=B.SCENES.by_id[sid]["background"], role=B.SCENES.role[sid],
                     web=web, reference=ref_web, native=B.value(row, "material", "interiorMeanNative"),
                     delta=delta, **attribute(delta, at_rung[key], at_shipped[key]))
        l1c = l1_by.get(key)
        why = []
        if l1c is not None and l1c["growth"] is not None and l1c["growth"] > C.L1_GROWTH:
            why.append(f"L1 growth {l1c['growth']:+.4f}")
        if l1c is not None and l1c["error"] is not None and l1c["error"] > C.L1_ABSOLUTE:
            why.append(f"L1 absolute {l1c['error']:.4f}")
        if delta is not None and abs(delta) > LEVEL_TOLERANCE:
            why.append(f"level {delta:+.4f}")
        entry["excess"] = why
        levels.append(entry)
        if why:
            excesses.append(entry)
    unexplained = [e["cell"] for e in excesses if e["attribution"] == "unexplained"]
    return dict(
        candidate=dict(path=candidate.path, sha256=candidate.sha256,
                       tintAlpha={pose: d["patch"]["optics"]["regular"]["tintAlpha"] for pose, d in docs.items()}),
        L1=dict(cells=len(l1_cells), notRenderedAtThisRung=l1_missing,
                absoluteMisses=[c for c in l1["absoluteMisses"] if dark(c["cell"])],
                growthMisses=[c for c in l1["growthMisses"] if dark(c["cell"])],
                maxError=max((c["error"] for c in l1_cells if c["error"] is not None), default=None),
                maxGrowth=max((c["growth"] for c in l1_cells if c["growth"] is not None), default=None),
                unmeasured=[c for c in l1["unmeasured"] if dark(c)],
                growthClausePasses=not any(dark(c["cell"]) for c in l1["growthMisses"]),
                absoluteClausePasses=not any(dark(c["cell"]) for c in l1["absoluteMisses"]),
                cellsRead=l1_cells),
        levels=levels, excesses=[dict(cell=e["cell"], excess=e["excess"], attribution=e["attribution"],
                                      predictedDelta=e["predictedDelta"], delta=e["delta"]) for e in excesses],
        unexplained=unexplained, tolerance=LEVEL_TOLERANCE,
        note="the attribution is the shader's arithmetic on group means (arith.ts): a prediction the rows test, "
             "not a measurement")


def load_rows(matrices: list[str]) -> list:
    rows = []
    for m in matrices:
        rows += json.loads(W.refuse_other_wave_path(m, "--matrix").read_bytes())["cells"]
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=("identity", "check"))
    ap.add_argument("--candidate", required=True, type=Path)
    ap.add_argument("--matrix", action="append", required=True)
    ap.add_argument("--captures", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    W.require_shared()
    folder = W.refuse_other_wave_path(args.candidate, "--candidate")
    candidate = B.Candidate.read(str(folder / "candidate.json"))
    rows = load_rows(args.matrix)
    for r in rows:
        why = B._admit_candidate(r, candidate)
        if why:
            raise W.Refusal(f"{r['key']['sceneId']}: {why}")
        if (r["key"]["profileKey"], r["key"]["sceneId"]) in B.referee_plan.referee_cells(B.referee_plan.load_manifest()) \
                or B.SCENES.role[r["key"]["sceneId"]] == "holdout":
            raise W.Refusal(f"{r['key']['sceneId']}: a withheld cell; no ladder renders one")
    reference_bed = B.load_published(W.REFERENCE["dark"])
    if args.verb == "identity":
        if args.captures is None:
            raise W.Refusal("identity reads the candidate's captures (--captures)")
        reference = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r for r in reference_bed.rows}
        result = identity(rows, W.refuse_other_wave_path(args.captures, "--captures"), candidate, reference)
        result["levelCheck"] = check(rows, candidate, reference_bed)
        ok = result["verdict"] == "IDENTICAL" and not result["levelCheck"]["excesses"] \
            and all(abs(e["delta"] or 0) == 0 for e in result["levelCheck"]["levels"])
        result["readsNoChange"] = ok
    else:
        result = check(rows, candidate, reference_bed)
        ok = True
    text = json.dumps(result, indent=1) + "\n"
    if args.out:
        W.refuse_other_wave_path(args.out, "--out").write_text(text)
    summary = {k: v for k, v in result.items() if k not in ("perCell", "levels", "levelCheck")}
    if "levelCheck" in result:
        summary["levelCheck"] = {k: v for k, v in result["levelCheck"].items() if k not in ("levels",)}
        summary["levelCheck"]["L1"] = {k: v for k, v in summary["levelCheck"]["L1"].items() if k != "cellsRead"}
    else:
        summary["L1"] = {k: v for k, v in summary["L1"].items() if k != "cellsRead"}
    print(json.dumps(summary, indent=1)[:6000])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
