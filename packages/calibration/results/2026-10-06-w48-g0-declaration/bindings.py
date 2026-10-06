"""W48 G0 (b): what binds W48 and the W47 tools it inherits BY PATH, and what refuses W44's, W45's, W46's
and W47's bindings (charter `2026-10-06-w48-dark-operators-fit.md`, Parent-Level Acceptance clause 2;
X60, X62, X64, X67-X73; Decision Logs 2, 3, 7).

W47's `bindings.py` (`results/2026-10-06-w47-g0-operators/bindings.py`), ported by copy; W47's copy is
untouched. What W48 changes, and nothing else:

- **W48's bindings**: the charter pin (the charter's merge `78d0211e0`), this evidence root, the two
  parts' files and the draft, G1's evidence directory (`results/2026-10-06-w48-g1-refit`), W48's scratch
  and stages (`~/vitrea-w48/...`), the GPU lock `/tmp/w48-gpu.lock`, the census and launcher copies
  under this root (`census-gate.py`, `with-gpu.sh`).
- **W47's tools are inherited BY PATH, not copied** (clause 2): `cuts/`, `fit/` (but its builder),
  `stage/`, `sheets/`, `referees/` and `level/` are W47's files, imported where they stand with THIS
  module installed as their `bindings` (`inherit.py`), so every place they bind through `W.*` is W48's.
  They are pinned byte-identical in `INHERITED` (a moved W47 tool refuses), as the shared inputs are in
  `SHARED`. The two TypeScript tools whose bindings are compiled-in constants (`fit/build-candidate.ts`,
  `seal/seal.ts`) are W48 copies under this root, differing from W47's only in those constants (their
  tests hold the diff to them).
- **W47's ladder evidence** (X71) is read from W47's committed files by key (`ladders/evidence.json`
  pins them and the archive `w47-ladders-archive`); W48 renders no ladder, so there is no W48 ladder
  scratch. `LADDER_CELLS` is W47's `ladders/cells.json` (the cells the evidence was rendered on);
  `LADDER_PROTOCOL` is W48's corrected protocol (Decision Log 3).
- **The snapshots (X62) are taken at THIS charter's merge** `78d0211e0` and equal W47's byte for byte
  (no 0.25 document moved since `c1f9bf84c`); `verify_documents` reads them at that commit.
- **The refusals** extend to W47: its evidence directory and scratch as a place a W48 tool reads a render
  from or writes to, its part hashes wherever a W48 part hash is expected, a declaration naming its
  charter and not W48's. Reading W47's COMMITTED evidence and tools by path is not refused where the
  charter names it (X71; clause 2).
- Everything else (the references, X64, X67, `ADMITTED`, X68's `DOMAINS`, `SHARED`) is W47's, carried
  (charter Cross-Child Contracts: X44 as narrowed by X64 and X67, X68 carried).

W47's text follows, unchanged; where it says W47 it is W48.

W47 G0 (c): what binds W47's re-bound tools to W47, and what refuses W44's, W45's and W46's bindings
(charter `2026-10-06-w47-span-graded-dark-transmission.md`, Parent-Level Acceptance clause 2; X60, X62,
X64, X67, X69, X70; Decision Log 5).

W46's `bindings.py` (`results/2026-10-05-w46-g0-declaration/bindings.py`), ported by copy with W46's
text kept where it still holds. Every W47 tool imports it before it reads anything, so the
parameterisation is one file:

- **W47's bindings**: the charter pin (the charter's merge `c1f9bf84c`), this evidence root, the two
  parts' files, G1's evidence directory, W47's scratch and stages (`~/vitrea-w47/...`), the GPU lock.
- **The starting point is four document snapshots (X62), taken at THIS charter's merge.**
  `documents/<sha12>.json` hold the dark and light 0.25 document bodies as they were at `c1f9bf84c`;
  `verify_documents` re-hashes each against its twelve-hex name and against its bytes at that commit,
  and every W47 tool builds from them. The live `profiles/` is never a start (`refuse_live_profile`).
  The bytes are W46's snapshots' (no 0.25 document moved between `b36c9990` and `c1f9bf84c`); W47
  keeps its own copies so that no W47 tool reads a W46 directory as its start.
- **The reference is one generation, by hash.** `d0219cd684bf` supplies the measured dark rows
  (the regression reference, X52's form); `ebc3d9105a4a` the light ones X60 reads.
- **The 0.5 twins are read live and checked frozen** (X44's base check; X41).
- **The leaves a dark document may add** are X64's lists (carried) and X67's (`X67`), with their
  resolved values at the snapshots; `ADMITTED` is their union per slot, which the builder admits and
  nothing else.
- **The immutable inputs shared by path, pinned byte-identical** (`SHARED`): W44 G0's bar and interior
  port, W44 G1's T1 arithmetic and band readings, W40's `matrix_store`, W43 G3's census and sheet
  helpers, W44 G0's planner and manifest (pinned unmoved, never read), and, under X69, W46's referee
  manifest `w46-referees-1`, W46's planner adapter and the frozen ladder list W46's declaration pinned,
  which W47 reads only to re-check that W46's tools still reproduce the manifest, plus W46 G2's dark
  T-band fixture.
- **The refusals** (clause 2): a path inside W44's, W45's or W46's evidence directories
  (`results/2026-10-0[35]-w4[456]-*`) or scratch (`~/vitrea-w44`…`~/vitrea-w46`) as a place a W47 tool
  reads a render from or writes to; W44's, W45's and W46's part hashes wherever a W47 part hash is
  expected; a declaration naming their charters and not W47's. Reading their COMMITTED evidence as an
  input is not refused where the charter names it (the shared files above; W46's point A candidate;
  the tools W47 ports by copy).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

G0 = Path(__file__).resolve().parent                # results/2026-10-06-w48-g0-declaration
CAL = G0.parents[1]                                  # packages/calibration
ROOT = CAL.parent.parent
RESULTS = CAL / "results"
PROFILES_DIR = CAL / "profiles"
WAVE = "W48"
CHARTER_PATH = "docs/doperpowers/specs/2026-10-06-w48-dark-operators-fit.md"
CHARTER_COMMIT = "78d0211e0"
# W47's evidence root: the tools W48 inherits by path, and the ladder evidence it reads by key (X71).
W47_G0 = RESULTS / "2026-10-06-w47-g0-operators"
CHARTER_PIN = f"{CHARTER_PATH}@{CHARTER_COMMIT}"

PART1 = G0 / "declaration.json"
PART1_DIGEST = G0 / "declaration.sha256"
PART2 = G0 / "fit-declaration.json"
PART2_DIGEST = G0 / "fit-declaration.sha256"
DRAFT = G0 / "fit-declaration-draft.json"
DECLARE = G0 / "declare.py"
CUTS_SOURCE = W47_G0 / "cuts"                        # inherited by path (bed, rule, cuts)
CUTS = G0 / "cuts"                                   # W48's launcher for a child process (cuts/cuts.py)
FIT = W47_G0 / "fit"                                 # inherited by path (its builder is W48's copy)
BUILDER = G0 / "fit" / "build-candidate.ts"
SEAL = G0 / "seal" / "seal.ts"
REFEREES = W47_G0 / "referees"                       # inherited by path
LADDERS = G0 / "ladders"
LADDER_CELLS = W47_G0 / "ladders" / "cells.json"      # the cells W47's ladder evidence was rendered on
LADDER_PROTOCOL = LADDERS / "protocol.json"          # W48's corrected protocol (Decision Log 3)
LADDER_EVIDENCE = LADDERS / "evidence.json"          # X71: W47's readings and the archive, pinned
VERDICTS = LADDERS / "verdicts.json"                 # X73: exists only after part 1's hash
REHEARSAL = G0 / "rehearsal"
WITH_GPU = G0 / "with-gpu.sh"

G1 = RESULTS / "2026-10-06-w48-g1-refit"
G1_FIT = G1 / "fit"
G1_STAGE = G1 / "stage"
G1_SEAL = G1 / "seal"
SCRATCH = Path.home() / "vitrea-w48"
FIT_SCRATCH = SCRATCH / "g1-scratch" / "fit"
STAGE = SCRATCH / "g1-stage-dark"
REHEARSAL_STAGE = SCRATCH / "g0-stage-rehearsal"
LADDER_SCRATCH = SCRATCH / "g0-ladders"              # W48 renders no ladder: this never exists (X71)
LEVEL_SCRATCH = SCRATCH / "g0-level"
CANONICAL_CAPTURES = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
GPU_LOCK = Path("/tmp/w48-gpu.lock")

# ---------------------------------------------------------------------------------------------
# The documents (X62) and the references
# ---------------------------------------------------------------------------------------------
SNAPSHOT_COMMIT = "78d0211e0"
DOCUMENTS = G0 / "documents"
DOCUMENT_KEY = {
    "active.dark": "apple-macos-27.0-1x-dark-standard-glass0.25",
    "receded.dark": "apple-macos-27.0-1x-dark-standard-glass0.25-receded",
    "active.light": "apple-macos-27.0-1x-light-standard-glass0.25",
    "receded.light": "apple-macos-27.0-1x-light-standard-glass0.25-receded",
}
DOCUMENT_SHA = {
    "active.dark": "d0219cd684bff75b2ba5c34d4f6cb2f6d49e32aab7cc27464220a05910f2638f",
    "receded.dark": "f0b36a71772a00a647c10a280ae73b92d21be1f0c65599334c4e3cdf36cb7f86",
    "active.light": "ebc3d9105a4a40565278845071113c6a5368b304910362786b8cbfb4cc66bb44",
    "receded.light": "12712d534b78017f68fee440cb9d9d451178aae1b80db36c0043fdfb1b591203",
}
# The resolved digests the snapshots record (and X64's seal pin reproduces for the dark pair).
DOCUMENT_DIGEST = {"active.dark": "b074fc6913a91c66", "receded.dark": "280f0fddf014e0f6",
                   "active.light": "3741b22934f17f4d", "receded.light": "c4ca0e1cd6791bde"}
SLOTS = ("active.light", "active.dark", "receded.light", "receded.dark")
MOVING_SLOTS = ("active.dark", "receded.dark")      # X60: the dark 0.25 material alone moves

REFERENCE = {"dark": "d0219cd684bf", "light": "ebc3d9105a4a"}
REFERENCE_FILE_SHA = {"d0219cd684bf": "6e20f04f60c4", "ebc3d9105a4a": "6e13171051de"}
# Both 0.5 generations and the frozen 26.5 file are byte-identical at every rung (X60, X41).
FROZEN_05_GENERATIONS = {"85ad7f7e3e0d": "39ac0ba98ca2", "0eac5b294cc2": "f72429653e29"}
# X41's freeze of the 0.5 documents: X44's twins, read live and checked here.
TWIN_05 = {
    "apple-macos-27.0-1x-dark-standard-glass0.5": "0eac5b294cc2",
    "apple-macos-27.0-1x-dark-standard-glass0.5-receded": "5cec8c961201",
    "apple-macos-27.0-1x-light-standard-glass0.5": "85ad7f7e3e0d",
    "apple-macos-27.0-1x-light-standard-glass0.5-receded": "30fbe05986ae",
}

DARK_025 = ("apple-macos-27.0-1x-dark-standard-glass0.25", "apple-macos-27.0-2x-dark-standard-glass0.25")
LIGHT_025 = ("apple-macos-27.0-1x-light-standard-glass0.25", "apple-macos-27.0-2x-light-standard-glass0.25")
PROFILE = {1: DARK_025[0], 2: DARK_025[1]}

# X64 (carried from W46): the inherited leaves each dark document MAY name, first at its resolved value
# (the runtime default for every leaf the snapshot does not name; for the receded the shipped active's).
X64 = {
    "active.dark": {"sizeScatterFloor2x": 1, "sizeScatterRampStartThin1x": 0.72,
                    "sizeScatterRampStartThick1x": 0.52, "sizeScatterRampStartFar1x": 0.2,
                    "sizeScatterRampStartThin2x": 0.46, "sizeScatterRampStartThick2x": 0.21,
                    "sizeScatterRampStartFar2x": 0.21, "sizeHeavySecondShareFar2x": 0},
    "receded.dark": {"sizeScatterRampStartFar1x": 0.2, "sizeScatterFloor": 0.34, "sizeScatterFloor2x": 1,
                     "sizeHeavyTapSigma": 0, "sizeHeavySecondShare": 0, "sizeHeavySecondShareFar2x": 0,
                     "sizeHeavySecondSigma": 0, "sizeHeavySecondSigma2x": 0, "sizeScatterScaleGain": -2},
}

# X67 (W47's narrowing of X44, beside X64): the leaves this wave's families read, each at its resolved
# value at the snapshots. The active patch MAY name the occlusion gain, the two span tops and operator
# 1's leaves at 0; the receded difference MAY name the body width (a nested `optics.regular` path),
# the same span tops and occlusion gain at the active's resolved values, operator 1's leaves at the
# active's values and operator 2's at 0. Operator 2 is receded-only by document (X66): the active
# names no operator-2 leaf. Materialisation at the resolved value is digest-neutral (W46 X64's
# argument), pinned by the seal test (`b074fc6913a91c66` / `280f0fddf014e0f6` with every key named).
X67 = {
    "active.dark": {"sizeOcclusionGain": 0.05, "sizeScatterSpanMax": 256, "sizeScatterSpanMax2x": 256,
                    "tintAlphaFar1x": 0, "tintAlphaFar2x": 0},
    "receded.dark": {"optics.regular.blurSigma": 1.25, "sizeScatterSpanMax": 256,
                     "sizeScatterSpanMax2x": 256, "sizeOcclusionGain": 0.05,
                     "tintAlphaFar1x": 0, "tintAlphaFar2x": 0,
                     "sizeFineTapShare": 0, "sizeFineTapSigma": 0, "sizeFineTapSigma2x": 0},
}
# What the builder admits on each dark slot beyond the snapshot's own leaves: X64's and X67's lists,
# and nothing else (X67: "the builder admits exactly these keys on the two dark 0.25 slots").
ADMITTED = {slot: {**X64[slot], **X67[slot]} for slot in MOVING_SLOTS}
OPERATOR_1 = ("tintAlphaFar1x", "tintAlphaFar2x")
OPERATOR_2 = ("sizeFineTapShare", "sizeFineTapSigma", "sizeFineTapSigma2x")

# X68: the operators' domains are the declaration's, not the shader's (the shader clamps operator 1's
# alpha and gates operator 2's texture; it bounds neither the deltas, the widths nor the share). The
# builder refuses a value outside them. Charter Design "Operator 1" and "Operator 2", "Domain and
# grid", and Design "The targets" (the transmission's rungs): an interval where the charter states the
# domain as one (`∈ [a, b]`), a set where it states only the values; every other admitted or snapshot leaf
# keeps W46's admission (a finite number at its own shape) and has no declared domain here. A domain is
# a list of parts, each `("set", values)` or `("interval", lo, hi)` (closed); a value is inside when
# some part holds it. Operator 2 is receded-only (X66): the active admits none of its leaves at all.
_SPAN_TOPS = [("set", (128, 160, 192, 256))]
_FAR = [("interval", 0, 0.6)]
_GAIN = [("interval", 0.05, 0.6)]
DOMAINS = {
    "active.dark": {"optics.regular.tintAlpha": [("set", (0.7, 0.8, 0.9))],
                    "tintAlphaFar1x": _FAR, "tintAlphaFar2x": _FAR, "sizeOcclusionGain": _GAIN,
                    "sizeScatterSpanMax": _SPAN_TOPS, "sizeScatterSpanMax2x": _SPAN_TOPS},
    "receded.dark": {"optics.regular.tintAlpha": [("set", (0.8, 0.89))],
                     # A SET: the charter states this domain only as {1.25 (inherited), 2, 3, 4} device
                     # px (Design "Operator 2", "Domain and grid"), where it states the operators' own
                     # domains as intervals; 1.75 is outside it.
                     "optics.regular.blurSigma": [("set", (1.25, 2, 3, 4))],
                     "tintAlphaFar1x": _FAR, "tintAlphaFar2x": _FAR, "sizeOcclusionGain": _GAIN,
                     "sizeScatterSpanMax": _SPAN_TOPS, "sizeScatterSpanMax2x": _SPAN_TOPS,
                     "sizeFineTapShare": [("interval", 0, 1)],
                     "sizeFineTapSigma": [("set", (0,)), ("interval", 1.5, 6)],
                     "sizeFineTapSigma2x": [("set", (0,)), ("interval", 1.5, 6)]},
}


def in_domain(slot: str, key: str, value) -> bool:
    """X68: True when `value` is inside the declared domain of `key` on `slot`, or `key` has none."""
    parts = DOMAINS.get(slot, {}).get(key)
    if parts is None:
        return True
    for part in parts:
        if part[0] == "set" and any(value == v for v in part[1]):
            return True
        if part[0] == "interval" and part[1] <= value <= part[2]:
            return True
    return False

# ---------------------------------------------------------------------------------------------
# Shared by path, pinned byte-identical
# ---------------------------------------------------------------------------------------------
W44_G0 = RESULTS / "2026-10-03-w44-g0-declaration"
W44_G1 = RESULTS / "2026-10-03-w44-g1-refit"
W45_G0 = RESULTS / "2026-10-03-w45-g0-operator"
W43_G3 = RESULTS / "2026-10-02-w43-g3-refit"
BAR_PATH = W44_G0 / "bar/t1-bar.json"
T1_PATH = W44_G1 / "cuts/t1.py"
READINGS_PATH = W44_G1 / "cuts/readings.py"
PORT = W44_G0 / "port"
CENSUS = W43_G3 / "stage/census.py"
W43_SHEETS = W43_G3 / "sheets/sheets.py"
MATRIX_STORE = RESULTS / "2026-09-26-w40-g0-generations/matrix_store.py"
W46_G0 = RESULTS / "2026-10-05-w46-g0-declaration"
W46_G1 = RESULTS / "2026-10-05-w46-g1-refit"
W46_G2 = RESULTS / "2026-10-05-w46-g2-landing"
W46_REFEREES = W46_G0 / "referees/referees.json"
W46_LADDER_CELLS = W46_G0 / "ladders/cells.json"
W46_T_BANDS = W46_G2 / "t1/t-bands-d0219cd684bf.json"
SHARED = {
    BAR_PATH: "1c3e63ad086b59cc959be67e220ceeb4b6f3d42529d295960f84d7d8fbf0932f",
    T1_PATH: "55f0a96e27b03325d4345f0f541b0b5996c7cd580573bd3e7aeb4c35835355fc",
    READINGS_PATH: "d4063705869df3933e27a0f329084e4280a472aab2103bb9873b08c5c93d1b5f",
    PORT / "interior.py": "8c5193b550b2cd627c88380b41227d6656d4fc04214f336ae8a3bcb7ee0fdd98",
    MATRIX_STORE: "3644a8c3a6d5d8d49f26ede02cd379085843a2e338cc577f8c063a2958d82992",
    CENSUS: "2f2f2dd23727269742fc0a06909c2ca5eb97e1715eed935c4cd38279da071e0a",
    W43_SHEETS: "f93887375859ad5ec232b15284fe0d1e120ad59e9628fabb423993d4478bca7a",
    # Pinned unmoved, never read by W46 (clause 3: W44's planner byte-identical and not reused).
    W44_G0 / "referees/plan.py": "f8ca80bb2153e12b7a3a4edc18b440e8f2c89a75bf0adef30e795c40c8dda8c7",
    W44_G0 / "referees/referees.json": "b1132bd0f01f318b07e1722da3fefaba6eac96679b56efbe2b451ef13bf1b60b",
    # X69: W46's frozen manifest (loaded by this hash, never re-derived from W47's ladders), the
    # adapter that derived it and the ladder list W46's declaration pinned, which is the ONLY list
    # the adapter is ever given here; and W46 G2's dark T-band fixture (the T cells' two bands).
    W46_REFEREES: "0eb8ef7712adc0f7de53290190ab1b5d903d61806cc2039de0e99fb78de4c2cf",
    W46_G0 / "referees/plan.py": "732f26487ce6725d08f36ea8e45f7e266f18c272af67ba47882b83e7d9902fe8",
    W46_LADDER_CELLS: "93a1fb4fd36c58c1c08bdc152fdee9cf033fbe22b324f7714b3a85538db13b15",
    W46_T_BANDS: "6fb61b6bc3da771e517b86805d1130a8ad6796091992fd106de5904f749c0694",
}
REFEREE_SCHEMA = "w46-referees-1"

# ---------------------------------------------------------------------------------------------
# The refusals of W44's, W45's, W46's and W47's bindings
# ---------------------------------------------------------------------------------------------
_OTHER_WAVE_DIR = re.compile(r"(^|/)2026-10-0[356]-w4[4567]-[^/]*(/|$)")
_OTHER_WAVE_SCRATCH = re.compile(r"(^|/)vitrea-w4[4567](/|$)")
OTHER_CHARTERS = ("docs/doperpowers/specs/2026-10-03-w44-texture-at-0-25.md",
                  "docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md",
                  "docs/doperpowers/specs/2026-10-05-w46-dark-texture-at-0-25.md",
                  "docs/doperpowers/specs/2026-10-06-w47-span-graded-dark-transmission.md")


def _part_hashes(*files: Path) -> frozenset:
    return frozenset(ln.split()[0] for f in files for ln in f.read_text().splitlines() if ln.strip())


OTHER_PART_HASHES = _part_hashes(W44_G0 / "declaration.sha256", W44_G0 / "fit-declaration.sha256",
                                 W45_G0 / "declaration.sha256", W45_G0 / "fit-declaration.sha256",
                                 W46_G0 / "declaration.sha256", W46_G0 / "fit-declaration.sha256",
                                 W47_G0 / "declaration.sha256")   # W47 hashed no part 2 (§5.211 §11)


class Refusal(SystemExit):
    """A refusal: the red cases assert on these."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(Path(path).read_bytes())


def resolve(path) -> Path:
    p = Path(path).expanduser()
    return p.resolve() if p.exists() or p.is_absolute() else (Path.cwd() / p).resolve()


def refuse_other_wave_path(path, what: str) -> Path:
    """`path`, resolved, unless it is inside W44's, W45's, W46's or W47's evidence, scratch or stage."""
    p = resolve(path)
    text = p.as_posix()
    if _OTHER_WAVE_DIR.search(text) or _OTHER_WAVE_SCRATCH.search(text):
        raise Refusal(f"{what}: {text} is W44's, W45's, W46's or W47's evidence, scratch or stage; W48 reads "
                      "and writes its own (clause 2)")
    return p


def refuse_other_wave_hash(digest: str | None, what: str) -> str | None:
    if digest is not None and digest in OTHER_PART_HASHES:
        raise Refusal(f"{what}: {digest[:12]}… is a W44, W45, W46 or W47 part hash, not W48's (clause 2)")
    return digest


def refuse_other_wave_text(text: str, what: str) -> str:
    """Refuse a declaration body that names W44's, W45's, W46's or W47's charter and not W48's."""
    if any(c in text for c in OTHER_CHARTERS) and CHARTER_PATH not in text:
        raise Refusal(f"{what}: names W44's, W45's, W46's or W47's charter and not W48's (clause 2)")
    return text


def refuse_live_profile(path, what: str) -> Path:
    """X62: a starting point is a snapshot, never the live `profiles/` directory."""
    p = resolve(path)
    if p == PROFILES_DIR.resolve() or PROFILES_DIR.resolve() in p.parents:
        raise Refusal(f"{what}: {p} is a live profile document; W48 builds from its snapshots "
                      "(documents/<sha12>.json, X62)")
    return p


# ---------------------------------------------------------------------------------------------
# Checks every tool runs before it reads
# ---------------------------------------------------------------------------------------------
def git_show(path: str, commit: str) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"], check=True,
                          capture_output=True).stdout


def document_path(slot: str) -> Path:
    return DOCUMENTS / f"{DOCUMENT_SHA[slot][:12]}.json"


def verify_documents(at_commit: bool = True) -> list[str]:
    """X62: each snapshot's bytes hash to its name and equal the document's bytes at `78d0211e0`."""
    out = []
    for slot, want in DOCUMENT_SHA.items():
        path = document_path(slot)
        if not path.exists():
            out.append(f"{slot}: {path.relative_to(ROOT)} is absent")
            continue
        raw = path.read_bytes()
        if sha(raw) != want:
            out.append(f"{slot}: {path.name} hashes to {sha(raw)[:12]}, not {want[:12]}")
        doc = json.loads(raw)
        if doc.get("profileKey") != DOCUMENT_KEY[slot]:
            out.append(f"{slot}: {path.name} is {doc.get('profileKey')}, not {DOCUMENT_KEY[slot]}")
        if doc.get("resolvedMaterialSha256") != DOCUMENT_DIGEST[slot]:
            out.append(f"{slot}: {path.name} records digest {doc.get('resolvedMaterialSha256')}")
        if at_commit:
            rel = f"packages/calibration/profiles/{DOCUMENT_KEY[slot]}.json"
            if git_show(rel, SNAPSHOT_COMMIT) != raw:
                out.append(f"{slot}: {path.name} is not {rel} at {SNAPSHOT_COMMIT}")
    return out


def document(slot: str) -> dict:
    """A snapshot's body, verified (hash only; `verify_documents` adds the commit check)."""
    raw = document_path(slot).read_bytes()
    if sha(raw) != DOCUMENT_SHA[slot]:
        raise Refusal(f"{slot}: the snapshot {document_path(slot).name} does not hash to its name (X62)")
    return json.loads(raw)


def twin_path(key_05: str) -> Path:
    """A 0.5 document under `profiles/`, checked at its X41-frozen hash before it is read."""
    path = PROFILES_DIR / f"{key_05}.json"
    got = file_sha(path)[:12]
    if got != TWIN_05[key_05]:
        raise Refusal(f"{path.relative_to(ROOT)} hashes to {got}, not its frozen {TWIN_05[key_05]} (X41)")
    return path


def verify_shared() -> list[str]:
    moved = []
    for path, want in SHARED.items():
        got = file_sha(path) if path.exists() else None
        if got != want:
            moved.append(f"{path.relative_to(ROOT)}: {got and got[:12]} is not the pinned {want[:12]}")
    return moved


def require_shared() -> None:
    moved = verify_shared()
    if moved:
        raise Refusal("a shared input moved (clause 1: shared by path, pinned byte-identical):\n  "
                      + "\n  ".join(moved))


def part_hash(part: int) -> str | None:
    """The CURRENT hash of W48's part 1 or 2 (the digest file's last line), or None if unhashed."""
    path = PART1_DIGEST if part == 1 else PART2_DIGEST
    if not path.exists():
        return None
    lines = [ln.split()[0] for ln in path.read_text().splitlines() if ln.strip()]
    return refuse_other_wave_hash(lines[-1], f"part {part}") if lines else None


def require_part(part: int) -> str:
    digest = part_hash(part)
    declaration = PART1 if part == 1 else PART2
    if digest is None:
        raise Refusal(f"W48 part {part} is not hashed; nothing that reads it runs before its hash")
    if not declaration.exists() or file_sha(declaration) != digest:
        raise Refusal(f"W48 part {part}: {declaration.name} is not the hashed {digest[:12]}")
    refuse_other_wave_text(declaration.read_text(), f"W48 part {part}")
    return digest


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_cuts():
    """(bed, t1, rule): W47's bed and rule from `cuts/`, T1's arithmetic shared by path from W44 G1
    (its `import bed` binds to W47's, which is first on the path)."""
    require_shared()
    require_inherited()
    if str(CUTS_SOURCE) not in sys.path:
        sys.path.insert(0, str(CUTS_SOURCE))
    import bed  # noqa: PLC0415
    if "t1" not in sys.modules:
        load_module("t1", T1_PATH)
    import rule  # noqa: PLC0415
    return bed, sys.modules["t1"], rule


def referee_plan():
    """W46's planner adapter, by path and pinned (`SHARED`), never W44's (X69). W47 gives it ONLY W46's
    frozen ladder list, as a pin that W46's tools still reproduce `w46-referees-1`; W47's own
    membership, disjointness and withholding checks live in `referees/` here."""
    require_shared()
    if "w46_plan" not in sys.modules:
        load_module("w46_plan", W46_G0 / "referees" / "plan.py")
    return sys.modules["w46_plan"]


def census():
    """W43 G3 (ii)'s classifying census, by path (§5.201 §21)."""
    return load_module("w43_census", CENSUS)


def referees():
    """W47's referee loader under X69 (`referees/referees.py`): `w46-referees-1` by hash, the derivation
    pin against W46's frozen ladder list, and W47's membership, disjointness and withholding checks.
    Every W47 consumer of the manifest (the bed, the cuts, the ladders, the stage) reads it here, in
    W46's adapter's interface."""
    require_inherited()
    if "w47_referees" not in sys.modules:
        load_module("w47_referees", REFEREES / "referees.py")
    return sys.modules["w47_referees"]


# W48 G0 renders nothing; a G1 tools render (the stage rehearsal, a level identity) would land under one
# scratch root, `~/vitrea-w48/g0-tools-scratch`, as W47's did under its own.
TOOLS_SCRATCH = SCRATCH / "g0-tools-scratch"
REHEARSAL_STAGE = TOOLS_SCRATCH / "stage-rehearsal"
LEVEL_SCRATCH = TOOLS_SCRATCH / "level"

# ---------------------------------------------------------------------------------------------
# W48: the W47 tools inherited BY PATH (clause 2), pinned byte-identical; a moved one refuses
# ---------------------------------------------------------------------------------------------
INHERITED = {
    W47_G0 / "cuts" / "bed.py": "c87493e8cc4d2b50cfbf8ff9a0195c9891b1d46ab9a12ec16a036a526572ca84",
    W47_G0 / "cuts" / "cuts.py": "7ea1fd1ae039cc86bddc43f41539c7c0675725f0d1c9b2406c75ecaf09c86577",
    W47_G0 / "cuts" / "rule.py": "ad8de5a626299f330c758719abe0e0d1e7b25ac19a1a0c5d0a2c05ad8f23b1f8",
    W47_G0 / "fit" / "fit.py": "34b20ddf169a8fd11757586d59828a03285ed1220103c0434946f7cee7ef23e0",
    W47_G0 / "fit" / "search.py": "42c4d6ae14d59382eaf0fb78d6cc82cfcd93ceca61d965a335111d417e717e31",
    W47_G0 / "fit" / "joint.py": "56ea2f738f953ddecfa516b796865c85875222a630ea203d8988ed32d13eb99d",
    W47_G0 / "fit" / "finding.py": "e07b4bc71500e645c18c7a06cd8f5b2b14a2cf78ec71f49e87c825e0e4c2cc9c",
    W47_G0 / "fit" / "recover.py": "dfd96fc02984a9d479cbe612320234659d2ff6d87d52b6f070386b80120e8a77",
    W47_G0 / "fit" / "labels.json": "09d7590592ef32ac817fc8de78d237eea8444ed458852f5a143e0a01c63bfe64",
    W47_G0 / "referees" / "referees.py": "763a2b22164071b0fd7aa9b6601ef977adee0b5c288b595e96eda9b0f9d950bf",
    W47_G0 / "stage" / "stage.py": "7aa1c2418e053646082ce5aa20d10f3a47758a1a7e4f2614c37abe88e8772df2",
    W47_G0 / "stage" / "x60.py": "4e710fda1b35fc87b30a58795b3d9f853236ec8b24597f5cb47949d320f4cf20",
    W47_G0 / "sheets" / "sheets.py": "22282a08cd0aef6102e2e2b2468605da69b53b50acdfe9f1eac25c5c44b3116e",
    W47_G0 / "level" / "level.py": "d74854ee076976c137346b5e9183eb0f72a5637c4c5465392c02f8b5dc92dab4",
    W47_G0 / "level" / "arith.ts": "7f9eb35fb4634a3863d0569fb2e07e37ddd524e820072a196a2dfdd3f351251b",
    W47_G0 / "ladders" / "read.py": "8e8a752620a976b3be3a2aad3d90e1a311c9ac666df343e5e924e597b9a0b993",
    W47_G0 / "ladders" / "ladder.py": "ae20016c857ea36bfdaa1bf1f947d71cabbd0f5657892b1b8e3831e594151d9a",
    W47_G0 / "ladders" / "part2.py": "624bf3fb90971289c7667c8cf426dc04ea0c6d3eedf92d71baec907c40c7f54a",
    W47_G0 / "rehearsal" / "rehearse.py": "138a603a2dda2f58a3c6fd17ae04ad1f50b3d1329f8e13d8364dc37ad8bcd0c1",
    W47_G0 / "rehearsal" / "port-proof.py": "b229681b2cf231e9cb82fa8b34f2f5e1ce204d7b4a5d144b215852ef7c9260c0",
}


def verify_inherited() -> list[str]:
    moved = []
    for path, want in INHERITED.items():
        got = file_sha(path) if path.exists() else None
        if got != want:
            moved.append(f"{path.relative_to(ROOT)}: {got and got[:12]} is not the pinned {want[:12]}")
    return moved


def require_inherited() -> None:
    moved = verify_inherited()
    if moved:
        raise Refusal("an inherited W47 tool moved (clause 2: inherited by path, pinned byte-identical):\n  "
                      + "\n  ".join(moved))
