"""W42 G0 gate: what the two directional stops share (charter clause 10; stops-declaration.json).

The stops read three images per cell: Apple's native fixture, the shipped render (the canonical
capture tree) and a CANDIDATE render (a scratch capture tree). This module is the one place that
turns a (profile, scene) into pixels, and it does so under the declaration's rules:

- a native path is formed only after `scenes.json`'s split names the scene calibration or
  validation, so a holdout or recorded fixture cannot be opened by mistake;
- a capture is admitted only if its `cell__webgpu.json` names the cell it sits under (scene,
  renderer, pixel size, scale and scheme) and at least the material document that drew it;
- a shipped capture must name documents that are the files on disk, so a stale canonical tree is
  refused rather than read as "shipped";
- a candidate run names every document its captures name, one set per colour scheme, and every
  one that is not a shipped document must be declared by hash with --document; a run in which
  every scheme's captures name the shipped documents is refused, because a candidate that IS the
  shipped render passes the bar by construction and gates nothing. The one run that reads the
  shipped tree as its candidate is the baseline (`--baseline`, stamped "baseline", never
  "candidate"), and only with the candidate root equal to the shipped root (2026-09-30, the gate
  review of b151aff4, finding 10).

Everything a stop needs beyond that (rings, bands, regions, resolutions) comes from
`stops-declaration.json`, which is the declaration of record; the code reads it rather than
restating it, so the hashed declaration and the executed numbers cannot drift apart.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[3]
REPO = HERE.parents[5]
assert (CAL / "package.json").exists() and (REPO / "apps/reference-apple/scenes.json").exists(), \
    f"stops: {HERE} is not at packages/calibration/results/<wave>/gate/stops"

DECLARATION_PATH = HERE / "stops-declaration.json"
DECLARATION = json.loads(DECLARATION_PATH.read_text())
SCENES = json.loads((REPO / "apps/reference-apple/scenes.json").read_text())
FIXTURES = REPO / "apps/reference-apple/fixtures"
PROFILE_DIR = CAL / "profiles"
CANONICAL_CAPTURES = Path(
    "/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")

PROFILES: dict[str, tuple[str, int]] = {
    key: (scheme, int(scale)) for key, (scheme, scale) in DECLARATION["common"]["profiles"].items()
}
CANVAS = tuple(DECLARATION["common"]["canvasCssPx"])
READABLE = frozenset({"calibration", "validation"})
ROLE: dict[str, str] = {}
for _role, _scenes in SCENES["split"].items():
    if isinstance(_scenes, list) and not _role.startswith("$"):
        for _scene in _scenes:
            ROLE[_scene] = _role
COMPONENTS = SCENES["components"]
POSES = re.compile(r"^(rest|inactive)(-tint-[a-z-]+)?$")
DOCUMENT = re.compile(r"(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})")
W709 = np.array([0.2126, 0.7152, 0.0722])


class Refused(SystemExit):
    """A run the declaration does not admit: raised, never swallowed into a verdict."""

    def __init__(self, message: str):
        super().__init__(f"stops: refused: {message}")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rgb(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"), dtype=np.float64)


# ---------------------------------------------------------------------------------------------
# Scenes, roles and populations.

def parse_scene(scene: str) -> tuple[str, str, str]:
    backdrop, component, state = scene.split("__")
    return backdrop, component, state


def pose_of(scene: str) -> str:
    return "receded" if parse_scene(scene)[2].startswith("inactive") else "active"


def population(backdrop_kind: str, untinted_only: bool) -> list[tuple[str, str]]:
    """The declared rule: the profile's own scene list, calibration/validation, one backdrop.

    Only the ROLE is consulted here; no fixture path is formed.
    """
    cells = []
    for entry in SCENES["profiles"]:
        if entry["key"] not in PROFILES:
            continue
        for scene in entry["scenes"]:
            if ROLE.get(scene) not in READABLE:
                continue
            backdrop, _component, state = parse_scene(scene)
            if backdrop != backdrop_kind or not POSES.match(state):
                continue
            if untinted_only and "-tint-" in state:
                continue
            cells.append((entry["key"], scene))
    return sorted(cells)


def declared_population(stop: str, backdrop_kind: str, untinted_only: bool) -> list[tuple[str, str]]:
    """The stop's population as declared, refused if `scenes.json` no longer derives it."""
    declared = sorted(tuple(c) for c in DECLARATION[stop]["population"]["cells"])
    derived = population(backdrop_kind, untinted_only)
    if declared != derived:
        raise Refused(f"{stop}: scenes.json derives {len(derived)} cells, the declaration lists "
                      f"{len(declared)}; first difference "
                      f"{sorted(set(declared) ^ set(derived))[:3]}")
    return declared


def native_path(profile: str, scene: str) -> Path:
    """Apple's fixture for a cell, formed only after the split admits the scene."""
    role = ROLE.get(scene)
    if role not in READABLE:
        raise PermissionError(f"{scene} is {role}: a native read is refused before its path "
                              "is formed")
    return FIXTURES / profile / f"{scene}.png"


def native(profile: str, scene: str) -> np.ndarray:
    path = native_path(profile, scene)
    if not path.exists():
        raise Refused(f"{profile}/{scene}: no native fixture (a population cell must have one)")
    image = rgb(path)
    _scheme, scale = PROFILES[profile]
    if image.shape[:2] != (CANVAS[1] * scale, CANVAS[0] * scale):
        raise Refused(f"{path}: {image.shape[:2]} is not the {scale}x canvas")
    return image


# ---------------------------------------------------------------------------------------------
# Geometry: the shape's signed distance in CSS px at device-pixel centres.

def _rrect_sdf(xs, ys, cx, cy, w, h, r):
    qx = np.abs(xs - cx) - (w / 2 - r)
    qy = np.abs(ys - cy) - (h / 2 - r)
    return (np.hypot(np.maximum(qx, 0), np.maximum(qy, 0))
            + np.minimum(np.maximum(qx, qy), 0) - r)


def _members(component: str) -> list[tuple[float, float, float, float, float]]:
    """(cx, cy, w, h, radius) in CSS px for every rounded rect the component draws."""
    spec = COMPONENTS[component]
    cx, cy = CANVAS[0] / 2, CANVAS[1] / 2
    kind = spec["kind"]
    if kind in ("capsule", "capsule-circular"):
        w, h = spec["size"]
        return [(cx, cy, w, h, min(w, h) / 2)]
    if kind == "rrect":
        w, h = spec["size"]
        dx, dy = spec.get("offset", [0, 0])
        return [(cx + dx, cy + dy, w, h, spec["radius"])]
    if kind == "group":
        items, spacing = spec["items"], spec["spacing"]
        total = sum(i["size"][0] for i in items) + spacing * (len(items) - 1)
        x0, out = cx - total / 2, []
        for item in items:
            if item["kind"] != "capsule":
                raise Refused(f"{component}: group item kind {item['kind']} is not declared")
            w, h = item["size"]
            out.append((x0 + w / 2, cy, w, h, min(w, h) / 2))
            x0 += w + spacing
        return out
    raise Refused(f"{component}: component kind {kind} is not declared")


def sdf_at(component: str, xs, ys) -> np.ndarray:
    """Signed distance (negative inside) at CSS-px points."""
    return np.minimum.reduce([_rrect_sdf(xs, ys, *m) for m in _members(component)])


def pixel_grid(scale: int) -> tuple[np.ndarray, np.ndarray]:
    """Device-pixel centres in CSS px: ((i + 0.5) / s)."""
    ys, xs = np.mgrid[0:CANVAS[1] * scale, 0:CANVAS[0] * scale].astype(np.float64)
    return (xs + 0.5) / scale, (ys + 0.5) / scale


def depth_map(component: str, scale: int) -> np.ndarray:
    xs, ys = pixel_grid(scale)
    return -sdf_at(component, xs, ys)


def short_side(component: str) -> float:
    return min(min(w, h) for _cx, _cy, w, h, _r in _members(component))


def surfaces(component: str) -> list[dict]:
    """The members as a web report states them (bounds and radius), for the geometry proof."""
    return [dict(x=cx - w / 2, y=cy - h / 2, width=w, height=h, radius=r)
            for cx, cy, w, h, r in _members(component)]


# ---------------------------------------------------------------------------------------------
# Captures.

@dataclass
class Capture:
    image: np.ndarray
    documents: tuple[tuple[str, str, str], ...]
    png_sha256: str
    meta_sha256: str


def read_capture(root: Path, profile: str, scene: str) -> Capture | None:
    """One cell of a capture tree, or None when the tree does not hold it at all.

    A cell that is present but does not name itself, its scale, its scheme or its document is
    refused: the stops never read a capture whose provenance they cannot state.
    """
    cell = Path(root) / profile / scene
    meta_path, png_path = cell / "cell__webgpu.json", cell / f"{scene}__webgpu.png"
    if not meta_path.exists() and not png_path.exists():
        return None
    if not meta_path.exists() or not png_path.exists():
        raise Refused(f"{cell}: holds one of cell__webgpu.json and the WebGPU PNG, not both")
    meta = json.loads(meta_path.read_text())
    scheme, scale = PROFILES[profile]
    size = [CANVAS[0] * scale, CANVAS[1] * scale]
    path = meta.get("capturePath", "")
    problems = []
    if meta.get("sceneId") != scene:
        problems.append(f"sceneId {meta.get('sceneId')!r} is not the directory's {scene!r}")
    if meta.get("renderer") != "webgpu":
        problems.append(f"renderer {meta.get('renderer')!r} is not webgpu")
    if meta.get("pixelSize") != size:
        problems.append(f"pixelSize {meta.get('pixelSize')} is not {size}")
    if f"deviceScaleFactor={scale}," not in path:
        problems.append(f"capturePath does not say deviceScaleFactor={scale}")
    if f"colorScheme={scheme}," not in path:
        problems.append(f"capturePath does not say colorScheme={scheme}")
    documents = tuple(DOCUMENT.findall(path))
    if not any(kind == "materialProfile" for kind, _p, _h in documents):
        problems.append("capturePath names no materialProfile document")
    report = cell / "report.cell__webgpu.json"
    if report.exists():
        key = json.loads(report.read_text()).get("key", {})
        if key.get("profileKey") != profile or key.get("sceneId") != scene:
            problems.append(f"report.cell__webgpu.json names {key.get('profileKey')}/"
                            f"{key.get('sceneId')}")
    image = rgb(png_path)
    if list(image.shape[1::-1]) != size:
        problems.append(f"the PNG is {image.shape[1]}x{image.shape[0]}, not {size}")
    if problems:
        raise Refused(f"{cell}: " + "; ".join(problems))
    return Capture(image, documents, sha256_file(png_path), sha256_file(meta_path))


def live_hash(repo_path: str) -> str | None:
    path = REPO / repo_path
    return sha256_file(path)[:12] if path.exists() else None


def is_shipped_document(repo_path: str, digest: str) -> bool:
    """A document under packages/calibration/profiles/ whose bytes on disk carry this hash."""
    return repo_path.startswith("packages/calibration/profiles/") and live_hash(repo_path) == digest


@dataclass
class Trees:
    """The shipped and candidate roots of one run, with their admission stamps."""
    shipped_root: Path
    candidate_root: Path
    declared_documents: list[Path] = field(default_factory=list)
    baseline: bool = False
    shipped_named: dict = field(default_factory=dict)
    candidate_named: dict = field(default_factory=dict)

    def shipped(self, profile: str, scene: str) -> Capture:
        capture = read_capture(self.shipped_root, profile, scene)
        if capture is None:
            raise Refused(f"{profile}/{scene}: the shipped tree {self.shipped_root} does not "
                          "hold this population cell")
        for kind, path, digest in capture.documents:
            if not is_shipped_document(path, digest):
                raise Refused(f"{profile}/{scene}: the shipped capture names {path} "
                              f"sha256:{digest}, which is not a document under "
                              "packages/calibration/profiles/ at its bytes on disk "
                              f"({live_hash(path)}): not the shipped generation")
        self._name(self.shipped_named, profile, capture)
        return capture

    def candidate(self, profile: str, scene: str) -> Capture | None:
        capture = read_capture(self.candidate_root, profile, scene)
        if capture is not None:
            self._name(self.candidate_named, profile, capture)
        return capture

    @staticmethod
    def _name(named: dict, profile: str, capture: Capture) -> None:
        scheme = PROFILES[profile][0]
        documents = tuple(sorted(capture.documents))
        if named.setdefault(scheme, documents) != documents:
            raise Refused(f"captures of the {scheme} scheme name two document sets: "
                          f"{named[scheme]} and {documents}")

    def check_roots(self) -> None:
        """Before any read: the shipped tree is a candidate only in the baseline, and only there."""
        same = self.candidate_root == self.shipped_root
        if self.baseline and not same:
            raise Refused(f"--baseline reads the shipped tree against itself; the candidate root "
                          f"{self.candidate_root} is not the shipped root {self.shipped_root}")
        if same and not self.baseline:
            raise Refused(f"the candidate root is the shipped root {self.shipped_root}: the "
                          "shipped render passes the bar by construction and is no candidate "
                          "(--baseline records native against shipped)")
        if self.baseline and self.declared_documents:
            raise Refused("--baseline names the shipped documents; it declares no --document")

    def admission(self) -> dict:
        """The stamp: every document the candidate captures name, per scheme.

        A candidate declares every document that is not shipped by --document (with or without
        any other declaration), and a candidate whose every scheme names only shipped documents
        is refused: it is the shipped render, whatever root it was copied to. The baseline is
        stamped as such and is never a candidate.
        """
        declared = {sha256_file(p)[:12]: str(p) for p in self.declared_documents}
        documents = {}
        for scheme, named in sorted(self.candidate_named.items()):
            for kind, path, digest in named:
                entry = documents.setdefault((kind, path, digest), dict(
                    kind=kind, path=path, sha256=digest, schemes=[],
                    isShippedDocument=is_shipped_document(path, digest)))
                entry["schemes"].append(scheme)
                # A scheme the candidate leaves at the shipped documents needs no declaration;
                # every other document does, whether or not any --document was given.
                if digest not in declared and not entry["isShippedDocument"]:
                    raise Refused(f"the candidate names {path} sha256:{digest}, which is not a "
                                  "shipped document and none of the declared documents "
                                  f"{sorted(declared)}: declare it with --document")
                if digest in declared:
                    entry["matchedDeclaredFile"] = declared[digest]
        at_shipped = bool(self.candidate_named) and all(
            is_shipped_document(path, digest)
            for named in self.candidate_named.values() for _kind, path, digest in named)
        if at_shipped and not self.baseline:
            raise Refused("every scheme of the candidate names the shipped documents: it is the "
                          "shipped render, which passes the bar by construction and gates nothing")
        return dict(
            mode="baseline" if self.baseline else "candidate",
            documents=list(documents.values()),
            declaredDocuments=[dict(path=str(p), sha256=sha256_file(p)[:12])
                               for p in self.declared_documents],
            candidateNamesShippedDocuments=bool(self.candidate_named) and all(
                self.shipped_named.get(scheme) == named
                for scheme, named in self.candidate_named.items()),
        )


# ---------------------------------------------------------------------------------------------
# Verdicts.

def judge(native_value, shipped_value, candidate_value, res: float) -> dict:
    """The directional bar: |cand - nat| <= |ship - nat| + res; UNMEASURED is never a pass."""
    out = dict(native=native_value, shipped=shipped_value, candidate=candidate_value, res=res)
    if native_value is None or shipped_value is None or candidate_value is None:
        out.update(dShip=None, dCand=None, margin=None, verdict="UNMEASURED")
        return out
    d_ship = abs(shipped_value - native_value)
    d_cand = abs(candidate_value - native_value)
    out.update(dShip=d_ship, dCand=d_cand, margin=d_ship + res - d_cand,
               verdict="pass" if d_cand <= d_ship + res else "FAIL")
    return out


def combine(verdicts: list[str]) -> str:
    if any(v == "FAIL" for v in verdicts):
        return "FAIL"
    if not verdicts or any(v == "UNMEASURED" for v in verdicts):
        return "UNMEASURED"
    return "pass"


def counts(verdicts: list[str]) -> dict:
    return {v: verdicts.count(v) for v in ("pass", "FAIL", "UNMEASURED")}


_SCALAR_LIST = re.compile(r"\[\s*((?:[^\[\]{}\s][^\[\]{}]*?)?)\s*\]", re.S)


def dump_json(value) -> str:
    """indent-2 JSON with every list of scalars of at most 100 characters on one line."""
    text = json.dumps(value, indent=2, ensure_ascii=False)

    def inline(match: re.Match) -> str:
        body = re.sub(r"\s*\n\s*", " ", match.group(1)).strip()
        return f"[{body}]" if len(body) <= 100 else match.group(0)
    compact = _SCALAR_LIST.sub(inline, text) + "\n"
    assert json.loads(compact) == value, "dump_json changed the value"
    return compact


def provenance() -> dict:
    return dict(
        declaration=dict(path=str(DECLARATION_PATH.relative_to(REPO)),
                         sha256=sha256_file(DECLARATION_PATH)),
        tools={p.name: sha256_file(p) for p in sorted(HERE.glob("*.py"))},
        scenesJsonSha256=sha256_file(REPO / "apps/reference-apple/scenes.json"),
    )
