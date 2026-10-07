"""Shared, CPU-only W49b scratch contracts. No publication or rendering on import."""
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import uuid

HERE = Path(__file__).resolve().parent
DECLARATION = HERE.parent
CAL = DECLARATION.parents[1]
ROOT = CAL.parents[1]
ENGINE_VERSION = "151.0.7922.34"
SETS = ("calibration", "validation", "recorded", "probe")
SLOTS = ("active.light", "active.dark", "receded.light", "receded.dark")
# This is an admission table, not a batch definition. Each supplied batch enumerates finite values.
MEMBERS = {"tintAlphaSpanMax", "tintAlphaSpanMax2x", "sizeHeavySecondSigmaFar1x",
           "sizeHeavySecondSigmaFar2x", "backdropCaptureScale", "sizeScatterSpanMax",
           "sizeScatterSpanMax2x", "tintAlphaFar1x", "tintAlphaFar2x",
           "sizeHeavySecondSigma", "sizeHeavySecondSigma2x", "sizeHeavySecondShare",
           "sizeHeavySecondShareFar2x", "sizeScatterScaleGain"}
LABEL = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}\Z")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_pinned(pin, base=CAL):
    path = Path(pin["path"])
    if not path.is_absolute(): path = base / path
    if sha256(path) != pin["sha256"]:
        raise ValueError(f"Changed byte snapshot: {path}")
    return json.loads(path.read_text())


def write_new_json(path, value):
    with Path(path).open("x") as handle:
        handle.write(json.dumps(value, indent=2, allow_nan=False) + "\n")


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_batch(batch):
    if batch.get("schema") == "w49b-g0-batch-1":
        if batch.get("base") != "b2d074d2df24-940384c06f73":
            raise ValueError("Finite point enumeration names a different base")
        # The supplied points ARE the finite domain. This projects their values for validation;
        # it never generates extra points or silently changes the supplied batch bytes.
        domain = {}
        for point in batch.get("points", []):
            for slot, patch in point.get("overrides", {}).items():
                for leaf, value in patch.items():
                    values = domain.setdefault(slot, {}).setdefault(leaf, [])
                    if value not in values: values.append(value)
        batch = {**batch, "schemaVersion": 1, "id": batch.get("id", "identification"), "domain": domain}
    if batch.get("schemaVersion") != 1 or not LABEL.fullmatch(batch.get("id", "")):
        raise ValueError("Batch requires schemaVersion 1 and a safe id")
    domain = batch.get("domain")
    if not isinstance(domain, dict): raise ValueError("Batch declares finite per-slot domain sets")
    for slot, leaves in domain.items():
        if slot not in ("active.dark", "receded.dark") or not isinstance(leaves, dict):
            raise ValueError(f"No admitted domain for {slot}")
        for leaf, values in leaves.items():
            if leaf not in MEMBERS or not isinstance(values, list) or not values:
                raise ValueError(f"No finite domain for {slot}.{leaf}")
            if not all(finite(v) for v in values) or len(set(values)) != len(values):
                raise ValueError(f"Invalid finite domain for {slot}.{leaf}")
            for value in values:
                if leaf.startswith("tintAlphaSpanMax") and value != 0 and value <= 96:
                    raise ValueError("D top must be zero or above the held sizeSpanMax 96")
                if leaf.startswith("sizeHeavySecondSigmaFar") and value < 0:
                    raise ValueError("W's first declared domain is nonnegative width deltas")
                if leaf == "backdropCaptureScale" and not 0 < value <= 1:
                    raise ValueError("S source-resolution multiplier must be in (0,1]")
    points = batch.get("points")
    if not isinstance(points, list) or not points: raise ValueError("Batch contains no points")
    seen = set()
    for point in points:
        label = point.get("label", "")
        if not LABEL.fullmatch(label) or label in seen: raise ValueError("Unsafe or duplicate point label")
        seen.add(label)
        scales = point.get("scales")
        if (not isinstance(scales, list) or not scales or
                any(type(s) is not int or s not in (1, 2) for s in scales) or len(set(scales)) != len(scales)):
            raise ValueError("Point scales are a nonempty unique subset of [1,2]")
        if point.get("pose") not in ("rest", "inactive", "both"):
            raise ValueError("Point pose must be rest, inactive or both")
        overrides = point.get("overrides")
        if not isinstance(overrides, dict): raise ValueError("Point explicitly declares overrides")
        for slot, patch in overrides.items():
            if slot not in domain or not isinstance(patch, dict): raise ValueError(f"Undeclared slot {slot}")
            for leaf, value in patch.items():
                if not finite(value) or value not in domain[slot].get(leaf, []):
                    raise ValueError(f"Point outside finite domain: {slot}.{leaf}={value}")
        # The builder checks that any unrequested pose resolves identically to current. Explicit
        # receded identity holds can isolate an active control, but are never added implicitly.
        if overrides.get("receded.dark") and not overrides.get("active.dark") and point["pose"] == "rest":
            raise ValueError("Receded-only overrides cannot request only rest")
    return batch


def load_registry(path=DECLARATION / "references.json"):
    registry = json.loads(Path(path).read_text())
    for pin in registry["inputs"].values(): read_pinned(pin)
    for generation in registry["generations"].values():
        read_pinned(generation["matrix"])
        for pin in generation["documents"].values(): read_pinned(pin)
    return registry


def gate_cells(registry, point, scale):
    cells = [c for c in registry["cells"] if c["partition"] == "gate" and c["scale"] == scale
             and (point["pose"] == "both" or c["pose"] == point["pose"])]
    if not cells: raise ValueError("Point requests no gate cells")
    return sorted(cells, key=lambda c: c["scene"])


def assert_membership(expected, rows):
    got = []
    for row in rows:
        key = row["key"]; web = key["web"]
        if key["sceneId"] != web["sceneId"] or row["tier"] != {"webgpu": "texture", "css": "dom"}.get(web["renderer"]):
            raise ValueError("Dishonest scene/renderer row identity")
        if web["engineVersion"] != ENGINE_VERSION:
            raise ValueError("Row browser differs from the declared browser pin")
        got.append((key["profileKey"], web["renderer"], key["sceneId"]))
    if len(set(got)) != len(got) or sorted(got) != sorted(expected):
        raise ValueError(f"Requested/planned/measured membership differs: {len(expected)} expected, {len(got)} measured")


def evaluate_cell(cell, value, fidelity_value=None):
    result = {k: cell[k] for k in ("profile", "renderer", "scene", "scale", "pose", "partition",
                                  "stratum", "role", "statistic", "B")}
    result.update(measured=value, current=cell["current"], native=cell["native"],
                  historical=cell.get("historical"), repaired=False)
    if value is None:
        result.update(currentStatus="UNMEASURED", historicalStatus="UNMEASURED",
                      growthCurrentInB=None, growthHistoricalInB=None, fidelityError=None,
                      fidelityStatus="UNMEASURED")
        return result
    if not finite(value): raise ValueError("Metric is not finite")
    growth = (abs(value - cell["native"]) - abs(cell["current"] - cell["native"])) / cell["B"]
    limit = 0 if cell["role"] == "protected" else 1
    historical = cell.get("historical")
    h = ((abs(value-cell["native"])-abs(historical["value"]-cell["native"]))/cell["B"]
         if historical else None)
    f = cell["fidelity"]
    fv = value if fidelity_value is None else fidelity_value
    if not finite(fv): raise ValueError("Fidelity metric is not finite")
    current_ok = growth <= limit + 1e-12
    historical_ok = h is not None and h <= 1 + 1e-12
    fidelity_error = abs(fv-f["native"])
    fidelity_ok = fidelity_error <= cell["B"] or (f["native"] >= cell["B"] and fidelity_error <= .1*f["native"])
    result.update(currentStatus="PASS" if current_ok else "FAIL", currentLimitInB=limit,
                  historicalStatus=("PASS" if historical_ok else "FAIL") if historical else "NOT_APPLICABLE",
                  growthCurrentInB=round(growth, 14), growthHistoricalInB=h,
                  fidelityStatistic=f["statistic"], fidelityValue=fv, fidelityNative=f["native"],
                  fidelityError=fidelity_error, fidelityStatus="within" if fidelity_ok else "miss",
                  repaired=bool(historical and historical["enforced"] and current_ok and historical_ok))
    return result


@contextmanager
def owned_lock(path):
    """An occupied lock is a stop. Only this token's directory is ever removed."""
    path = Path(path)
    path.mkdir()
    token = uuid.uuid4().hex
    owner = {"pid": os.getpid(), "token": token}
    try:
        write_new_json(path / "owner.json", owner)
    except BaseException:
        path.rmdir()
        raise
    try:
        yield owner
    finally:
        actual = json.loads((path / "owner.json").read_text())
        if actual != owner:
            raise ValueError(f"Lock ownership changed; left untouched: {path}")
        (path / "owner.json").unlink()
        path.rmdir()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3 or sys.argv[1] != "validate-batch":
        raise SystemExit("Usage: common.py validate-batch <batch.json>")
    print(json.dumps(validate_batch(json.loads(Path(sys.argv[2]).read_text())), allow_nan=False))
