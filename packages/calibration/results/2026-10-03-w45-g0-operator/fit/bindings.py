"""W45 G0 (b): what binds W45's ported tools to W45, and what refuses W44 (charter clause 2, X58).

Every W45 tool under `fit/`, `stage/`, `seal/` (through its own constants) and `sheets/` imports this
module instead of naming a wave in its own body, so the parameterisation is one place:

- **W45's bindings**: the charter pin, W45's G0 evidence root (this file's parent directory), the
  two parts' declarations and digest files there, G1's evidence directory and scratch, the stage.
- **The immutable inputs shared by path, pinned byte-identical** (`SHARED`): W44 G0's referee
  manifest and planner, the bar, W44 G1's T1 arithmetic and band readings, W44 G0's interior port,
  and W43 G3's census and sheet helpers. `verify_shared` re-hashes each; a tool refuses to run when
  any moved.
- **The refusals of W44's bindings** (X58): `refuse_w44_path` refuses any path inside a W44
  evidence directory (`results/2026-10-03-w44-*`) or W44's scratch and stages (`~/vitrea-w44/...`)
  as a place a W45 tool reads a render from or writes to; `refuse_w44_hash` refuses W44's charter
  and part hashes wherever a W45 part hash is expected. Reading W44's COMMITTED evidence as an
  input is not refused where the charter names it (the joint point's spec, by its declaration hash
  `66bf5a01…`, X56; the shared inputs above).
- **The cuts**: W45's cut modules live in `../cuts/` (W45's port of W44 G1's `bed.py` and
  `cuts.py`); T1's arithmetic is W44 G1's `t1.py`, shared by path. `load_cuts` puts W45's cuts
  directory first on the path, imports its `bed`, and imports `t1` from W45's cuts directory if a
  byte-identical copy is there, else from W44 G1's file, after checking its pin either way.
"""
from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from pathlib import Path

FIT = Path(__file__).resolve().parent
G0 = FIT.parent                                   # results/2026-10-03-w45-g0-operator
CAL = G0.parents[1]                               # packages/calibration
ROOT = CAL.parent.parent
RESULTS = CAL / "results"
CHARTER_PATH = "docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md"
CHARTER_PIN = f"{CHARTER_PATH}@c152b89b"
WAVE = "W45"

PART1 = G0 / "declaration.json"
PART1_DIGEST = G0 / "declaration.sha256"
PART2 = G0 / "fit-declaration.json"
PART2_DIGEST = G0 / "fit-declaration.sha256"
DECLARE = G0 / "declare.py"
CUTS = G0 / "cuts"
BUILDER = FIT / "build-candidate.ts"

G1 = RESULTS / "2026-10-03-w45-g1-refit"
G1_FIT = G1 / "fit"
G1_STAGE = G1 / "stage"
G1_SEAL = G1 / "seal"
SCRATCH = Path.home() / "vitrea-w45"
FIT_SCRATCH = SCRATCH / "g1-scratch" / "fit"
STAGE = SCRATCH / "g1-stage-light"
REHEARSAL_STAGE = SCRATCH / "g0-stage-rehearsal"
CANONICAL_CAPTURES = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")

# The two starting points (Decision Log 4, X56): c05 by its published generation and W44's joint
# point by its declaration hash.
C05 = {"light": "6d18c059eb42", "dark": "d0219cd684bf"}
C05_DOCUMENT_FILE_SHA = {
    "apple-macos-27.0-1x-light-standard-glass0.25": "6d18c059eb42",
    "apple-macos-27.0-1x-light-standard-glass0.25-receded": "4d5f23d9d312",
}
JOINT = dict(
    label="m3-t0.1",
    declarationSha256="66bf5a0192bf7f670c8a12472fa4b2f6bdbe63cc4bfb8305828e3ec1a32087e3",
    candidate=RESULTS / "2026-10-03-w44-g1-refit/fit/candidates/m3-t0.1/candidate.json",
    spec=RESULTS / "2026-10-03-w44-g1-refit/fit/specs/m3-t0.1.json",
)
PROFILE = {2: "apple-macos-27.0-2x-light-standard-glass0.25",
           1: "apple-macos-27.0-1x-light-standard-glass0.25"}
LIGHT_025 = (PROFILE[1], PROFILE[2])

# Shared by path, pinned byte-identical (X58; the charter's Grounding "What W44 left ready").
_W44_G0 = RESULTS / "2026-10-03-w44-g0-declaration"
_W44_G1 = RESULTS / "2026-10-03-w44-g1-refit"
SHARED = {
    _W44_G0 / "referees/referees.json": "b1132bd0f01f318b07e1722da3fefaba6eac96679b56efbe2b451ef13bf1b60b",
    _W44_G0 / "referees/plan.py": "f8ca80bb2153e12b7a3a4edc18b440e8f2c89a75bf0adef30e795c40c8dda8c7",
    _W44_G0 / "bar/t1-bar.json": "1c3e63ad086b59cc959be67e220ceeb4b6f3d42529d295960f84d7d8fbf0932f",
    _W44_G1 / "cuts/t1.py": "55f0a96e27b03325d4345f0f541b0b5996c7cd580573bd3e7aeb4c35835355fc",
    _W44_G1 / "cuts/readings.py": "d4063705869df3933e27a0f329084e4280a472aab2103bb9873b08c5c93d1b5f",
    _W44_G0 / "port/interior.py": "8c5193b550b2cd627c88380b41227d6656d4fc04214f336ae8a3bcb7ee0fdd98",
    RESULTS / "2026-10-02-w43-g3-refit/stage/census.py": "2f2f2dd23727269742fc0a06909c2ca5eb97e1715eed935c4cd38279da071e0a",
    RESULTS / "2026-10-02-w43-g3-refit/sheets/sheets.py": "f93887375859ad5ec232b15284fe0d1e120ad59e9628fabb423993d4478bca7a",
}
REFEREES = _W44_G0 / "referees"
T1_PATH = _W44_G1 / "cuts/t1.py"
READINGS_PATH = _W44_G1 / "cuts/readings.py"
PORT = _W44_G0 / "port"
CENSUS = RESULTS / "2026-10-02-w43-g3-refit/stage/census.py"
W43_SHEETS = RESULTS / "2026-10-02-w43-g3-refit/sheets/sheets.py"

# W44's bindings, refused (X58).
W44_CHARTER = "docs/doperpowers/specs/2026-10-03-w44-texture-at-0-25.md"
W44_PART_HASHES = frozenset({
    "fdecebbfbc895005f1c3558397989b472e664d8e20a3e359ef3fda67d4664fdd",   # part 1, as hashed
    "e6aaf6543c42f678f84e6ba51a2a3e45bb62d51958d543ce4d92fe20387315b6",   # part 1, as amended
    "443f494c94fc66d8adf41932ca0d533600676e9295c7f9f69a9785fb565685d2",   # part 2, as hashed
    "c04227e9240a0f1e890aef5c6529db412783864305b7ddbc125a00923c771175",   # part 2, as amended
})
_W44_DIR = re.compile(r"(^|/)2026-10-03-w44-[^/]*(/|$)")
_W44_SCRATCH = re.compile(r"(^|/)vitrea-w44(/|$)")


class Refusal(SystemExit):
    """A refusal: the red cases assert on these."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def refuse_w44_path(path, what: str) -> Path:
    """`path`, resolved, unless it is inside W44's evidence, scratch or stage (X58)."""
    p = Path(path).expanduser()
    p = p.resolve() if p.exists() or p.is_absolute() else (Path.cwd() / p).resolve()
    text = p.as_posix()
    if _W44_DIR.search(text) or _W44_SCRATCH.search(text):
        raise Refusal(f"{what}: {text} is W44's evidence, scratch or stage; W45 reads and writes its own (X58)")
    return p


def refuse_w44_hash(digest: str | None, what: str) -> str | None:
    if digest is not None and digest in W44_PART_HASHES:
        raise Refusal(f"{what}: {digest[:12]}… is a W44 part hash, not W45's (X58)")
    return digest


def refuse_w44_text(text: str, what: str) -> str:
    """Refuse a declaration body that names W44's charter as its own (`charter` field)."""
    if W44_CHARTER in text and CHARTER_PATH not in text:
        raise Refusal(f"{what}: names W44's charter and not W45's (X58)")
    return text


def verify_shared() -> list[str]:
    """The shared inputs whose bytes moved since W45 pinned them (empty: all hold)."""
    moved = []
    for path, want in SHARED.items():
        got = sha(path.read_bytes()) if path.exists() else None
        if got != want:
            moved.append(f"{path.relative_to(ROOT)}: {got and got[:12]} is not the pinned {want[:12]}")
    return moved


def require_shared() -> None:
    moved = verify_shared()
    if moved:
        raise Refusal("a shared input moved (X58: shared by path, pinned byte-identical):\n  " + "\n  ".join(moved))


def part_hash(part: int) -> str | None:
    """The CURRENT hash of W45's part 1 or 2 (the digest file's last line), or None if unhashed."""
    path = PART1_DIGEST if part == 1 else PART2_DIGEST
    if not path.exists():
        return None
    lines = [ln.split()[0] for ln in path.read_text().splitlines() if ln.strip()]
    return refuse_w44_hash(lines[-1], f"part {part}") if lines else None


def require_part(part: int) -> str:
    """Refuse unless W45's part `part` is hashed and the declaration on disk is the hashed bytes."""
    digest = part_hash(part)
    declaration = PART1 if part == 1 else PART2
    if digest is None:
        raise Refusal(f"W45 part {part} is not hashed ({(PART1_DIGEST if part == 1 else PART2_DIGEST).name} "
                      "absent); nothing that reads it runs before its hash")
    if not declaration.exists() or sha(declaration.read_bytes()) != digest:
        raise Refusal(f"W45 part {part}: {declaration.name} is not the hashed {digest[:12]}")
    refuse_w44_text(declaration.read_text(), f"W45 part {part}")
    return digest


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_cuts():
    """(bed, t1): W45's bed from `../cuts/`, and T1's arithmetic shared by path from W44 G1."""
    require_shared()
    if not (CUTS / "bed.py").exists():
        raise Refusal(f"{CUTS.relative_to(ROOT)}/bed.py does not exist yet (W45's cuts port)")
    if str(CUTS) not in sys.path:
        sys.path.insert(0, str(CUTS))
    import bed  # noqa: PLC0415  (W45's port, first on the path)
    if "t1" not in sys.modules:
        local = CUTS / "t1.py"
        if local.exists():
            if sha(local.read_bytes()) != SHARED[T1_PATH]:
                raise Refusal(f"{local.relative_to(ROOT)} is not W44 G1's t1.py byte for byte (X58)")
            import t1  # noqa: F401,PLC0415
        else:
            load_module("t1", T1_PATH)
    return bed, sys.modules["t1"]


def census():
    """W43 G3 (ii)'s classifying census, by path (§5.201 §21)."""
    return load_module("w43_census", CENSUS)


def referee_plan():
    if str(REFEREES) not in sys.path:
        sys.path.insert(0, str(REFEREES))
    import plan  # noqa: PLC0415
    return plan
