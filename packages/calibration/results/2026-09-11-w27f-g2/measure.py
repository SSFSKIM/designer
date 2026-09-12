"""W27f G2: the landing gate's read — the same measurement, at the landing head.

This is `2026-09-10-w27f-g1-measure.py` with three changes and no new opinion
about anything it measures. G1 derived the page material and recorded its
envelope; G2 decides whether the landing head is where G1 measured it, against
a bound declared before this file was run (`declaration.md` beside it). Reusing
G1's runner rather than writing a second one is the point: a landing gate that
re-implemented the instrument could not tell a material change from a reader
change.

What differs from the G1 runner, all of it mechanism:

* `porcelain_paths` preserves `git status --porcelain`'s two status columns.
  G1 stripped the whole output before slicing at offset 3, so a first entry
  whose status began with a space lost a path character. The tracker required
  this fix before the runner was reused; the historical manifest keeps what it
  recorded.
* `SCENE_SERVER_PORT` reads `VITREA_SCENE_SERVER_PORT`. This gate may not use
  5189 — another worker holds this machine's native capture path — and before
  W27f G2 no override existed in either the server or this waiter.
* `ROOT`, the scratch-root variable and the frozen-commit variable are this
  gate's (`W27F_G2_OUT`, `W27F_G2_SOURCE_COMMIT`).

Everything else, including every metric, every freshness rule and the holdout
guard, is G1's unchanged. The reading it writes therefore carries a different
`runnerSha256` from G1's, which is honest: it is a different file.

    python packages/calibration/results/2026-09-11-w27f-g2/measure.py \
        capture --phase candidate --out /tmp/w27f-g2
    python packages/calibration/results/2026-09-11-w27f-g2/measure.py \
        read    --phase candidate --out /tmp/w27f-g2
    #  … the two stack cells, which are holdout members (declaration.md §0) …
    python packages/calibration/results/2026-09-11-w27f-g2/measure.py \
        capture --phase holdout --out /tmp/w27f-g2 \
        --scenes checkerboard__glass-over-glass__rest,photo__glass-over-glass__rest
    python packages/calibration/results/2026-09-11-w27f-g2/measure.py \
        read    --phase holdout --out /tmp/w27f-g2

Everything it writes goes under one scratch root (`--out`, or `W27F_G2_OUT`,
default `/tmp/w27f-g2`). Nothing here writes the canonical matrix or the
canonical capture tree: `cli/compare.ts` refuses a probe run that would, and
every invocation below redirects both.

Run each phase from the tree that is being measured, and read it from the same
tree: the reading digests the sources that decided what drew, so a candidate
read from a frozen tree would name the wrong material. The baseline's tree is
therefore a FROZEN COPY — `git archive HEAD` into scratch, plus the workspace's
`node_modules` and a `pnpm -r build` for the private packages, which resolve
through `dist` — because the edit that G1 makes lands in the working tree while
the baseline is still being captured, and a capture reads source: the calibration
scene server aliases every vitrea package to `src`. `W27F_G1_SOURCE_COMMIT`
tells such a copy which commit it is.

Five rules it holds itself to, four of them inherited from the G0 reader
(`2026-09-10-w27f-g0-read.py`), which is imported rather than reimplemented —
the region instrument, the OKLab conversion, the declared-bounds check and the
W23 contour reader are that file's, and this one adds no second opinion about
any of them.

* **The measured region is the DECLARATION**, from `scripts/declared-geometry.ts`,
  never the bounds the capture being measured reports.
* **An arm's route and hint are not taken from the directory it was written to.**
  Captures taken after G0 state their own axes (`requestedBackdropMode`,
  `requestedBackdropLevel`); those are required here and checked against the
  resolved `configuredSource`, `samplingBackend` and `backdropTone`.
* **The hint is a measured level, never a chosen one.** Each phase derives it
  from its own texture-sampled arm, and for the light scenes G0 already read it
  is checked against the committed G0 evidence to the bit. A hint that moved is
  a sampled path that moved, which is a stop rather than a new baseline.
* **The texture path is expected byte-identical.** W27f's acceptance is that the
  sampled path does not move, so every texture-route arm's PNG digest is
  compared against the same arm's recorded digest — G0's for light, the
  baseline phase's for dark — and the verdict is reported per scene.
* **Holdout is read once per frozen configuration.** The two stack cells are
  the only native cells on this path, they are read by the `holdout` phase and
  by nothing else, and that phase records what it was spent on and refuses to
  run a second time.

The scene set is read from the declared split in `apps/reference-apple/scenes.json`,
never named here: the calibration phases measure the declared calibration
scenes and the holdout phase measures the declared holdout scenes whose
component is the stacked one. Both colour schemes capture the same scenes. The
dark 1x native bed is thinner than the light one — it holds fixtures for nine of
the twenty calibration scenes and for one of the two stacked cells — so the
scenes it cannot referee are captured through `capture-web` directly, their rows
say `nativeFixture: false`, and their ΔE to Apple is null. Everything those rows
still answer is the comparison between arms, which is most of what this gate
turns on.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "packages/calibration"
SCENES = ROOT / "apps/reference-apple/scenes.json"
FIXTURES = ROOT / "apps/reference-apple/fixtures"
GEOMETRY = PACKAGE / "scripts/declared-geometry.ts"
G0_READ = PACKAGE / "results/2026-09-10-w27f-g0-read.py"
G0_EVIDENCE = PACKAGE / "results/2026-09-10-w27f-g0-unsampled.json"

# Who this runner is, stamped into every reading it writes. It is a constant
# because it is the one thing a copied runner must change and the easiest thing
# to miss: this copy inherited `2026-09-10` / `W27f G1` from the file it was
# copied out of, so `stack-reading.json` and `ordinary-reading.json` — this
# gate's own evidence — open by naming the gate that did not take them. Those two
# files are left as they were written and the misattribution is disclosed in
# claims §5.135 §9; from here the stamp travels with the runner.
GATE_DATE = "2026-09-11"
GATE = "W27f G2"

_spec = importlib.util.spec_from_file_location("w27f_g0", G0_READ)
g0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g0)

# Every source tree that can change what drew, digested into each reading so a
# number names the code that produced it and not just the profile document it
# was asked to apply — a document's `resolvedMaterialSha256` was computed before
# any of this gate's edits.
#
# Whole trees, deliberately. The first form of this list named four files —
# material.ts, the WGSL, optics.ts, css-tier.ts — and missed renderer.ts,
# passes.ts, root.ts and renderer-bridge.ts, which is exactly where the DOM
# material and its lift are wired: a fingerprint that omits the file a gate is
# editing is a fingerprint that certifies the wrong thing. A list of trees
# cannot go stale the way a list of files does, and the cost is only that an
# unrelated edit inside one of them shows as a different configuration, which is
# the safe direction.
MATERIAL_SOURCES_SCOPE = "runtime-src-trees-2026-09-10"
MATERIAL_SOURCES = [
    "packages/renderer-webgpu/src",
    "packages/platform-web/src",
    "packages/core/src",
    "packages/policy/src",
    "packages/geometry/src",
    "packages/motion/src",
]


class Scheme:
    """One colour scheme's bed: the native profile and the material document."""

    def __init__(self, name, profile, document):
        self.name = name
        self.profile = profile
        # Relative to the calibration package, which is where `compare` resolves it.
        self.document = document

    @property
    def document_path(self):
        return PACKAGE / self.document


SCHEMES = {
    "light": Scheme("light", "apple-macos-26.5-1x-light-standard",
                    "profiles/apple-macos-26.5-1x-light-standard.json"),
    "dark": Scheme("dark", "apple-macos-26.5-1x-dark-standard",
                   "profiles/apple-macos-26.5-1x-dark-standard.json"),
}


class Arm:
    """One web configuration: which tier drew, which route, and whether it hinted.

    `g0` names the same configuration in the committed G0 evidence where one
    exists; `css-nohint` has none, because G0 recorded the CSS tier's page
    content only at the hint. The stack overlay is `dom` in every arm and is
    never handed the raw-raster hint — it sees rendered glass — so the route and
    hint expectations below describe the base groups.
    """

    def __init__(self, name, tier, mode, hinted, g0):
        self.name = name
        self.tier = tier
        self.mode = mode
        self.hinted = hinted
        self.g0 = g0

    @property
    def texture(self):
        return self.mode == "texture"


# Ordered: the texture-sampled arm runs first in every phase because its
# resolved backdrop tone is where the hint the other arms author comes from.
ARMS = [
    Arm("sampled", "webgpu", "texture", False, "sampledToday"),
    Arm("sampled-hint", "webgpu", "texture", True, "sampled-hint"),
    Arm("unsampled-nohint", "webgpu", "dom", False, "unsampled-nohint"),
    Arm("unsampled-hint", "webgpu", "dom", True, "unsampled"),
    Arm("css-today", "css", "texture", False, "css-today"),
    Arm("css-nohint", "css", "dom", False, None),
    Arm("css-hint", "css", "dom", True, "css"),
]
ARMS_BY_NAME = {arm.name: arm for arm in ARMS}

PHASES = ("baseline", "candidate", "holdout")
TOLERANCE = 1e-12


# ---------------------------------------------------------------------------
# The bed
# ---------------------------------------------------------------------------


def digest(path):
    """SHA-256 over a file, or over a directory's files in sorted path order."""
    path = Path(path)
    if path.is_dir():
        h = hashlib.sha256()
        for child in sorted(p for p in path.rglob("*") if p.is_file()):
            h.update(child.relative_to(path).as_posix().encode())
            h.update(child.read_bytes())
        return h.hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scene_spec():
    return json.loads(SCENES.read_text())


def native_manifest():
    return json.loads((FIXTURES / "manifest.json").read_text())


def declared_scenes(phase, spec):
    """The scene ids a phase measures, from the declared split and nothing else.

    The whole declared set, either way: the calibration phases take the declared
    calibration scenes and the holdout phase takes the declared holdout scenes.
    Nothing narrows the holdout to the two stacked cells, because a holdout read
    once against a frozen configuration should be the whole held-out bed — the
    stacks are the only cells with a NATIVE reading of the overlay, which is a
    statement about what those two answer, not about which cells to look at.
    """
    return sorted(spec["split"]["holdout" if phase == "holdout" else "calibration"])


def fixtures_for(profile_key, manifest):
    """Which scenes the native bed actually holds for this profile."""
    for profile in manifest["profiles"]:
        if profile["profileKey"] == profile_key:
            return {f["sceneId"]: f for f in profile["fixtures"]}
    raise ValueError(f"the native manifest has no profile {profile_key}")


def bed_for(scheme, phase, spec, manifest, only=None):
    """This scheme's scenes, split by whether the native bed can referee them.

    Every scene of the phase is captured on every scheme, because the arms are
    compared with each other as much as with Apple: the hinted page against the
    same scene's texture-sampled render is a measurement whether or not a native
    fixture of that scene exists in this colour scheme. What a missing fixture
    costs is the native ΔE, and that cost is named — the scene is captured
    through `capture-web` directly, its row records `nativeFixture: false` and
    its distance to Apple is null rather than absent.
    """
    wanted = declared_scenes(phase, spec)
    if only is not None:
        unknown = [s for s in only if s not in wanted]
        if unknown:
            raise ValueError(f"--scenes names {unknown}, which this phase does not measure")
        wanted = [s for s in wanted if s in only]
    have = fixtures_for(scheme.profile, manifest)
    return [s for s in wanted if s in have], [s for s in wanted if s not in have]


# ---------------------------------------------------------------------------
# Capture
# ---------------------------------------------------------------------------


def phase_dir(out, phase):
    return out / phase


def arm_root(out, phase, scheme, arm):
    return phase_dir(out, phase) / scheme.name / arm.name


def capture_dir_under(phase_root, scheme, arm, scene):
    """Where one capture lives beneath a phase's root, wherever that root is.

    Taken apart from `capture_dir` because a comparison is not always inside the
    same scratch root: a baseline captured on a frozen configuration is a
    separate run in a separate tree, and the reading it wrote records its own
    `captureRoot`. Reading that field is what lets the two be compared without
    either being moved.
    """
    return Path(phase_root) / scheme.name / arm.name / scheme.profile / scene


def capture_dir(out, phase, scheme, arm, scene):
    return capture_dir_under(phase_dir(out, phase), scheme, arm, scene)


def fixture_set_for(phase):
    return "holdout" if phase == "holdout" else "calibration"


def arm_env(out, phase, scheme, arm, levels_path):
    """The probe axes for one arm, as `capture-web` reads them.

    The canonical request — texture route, no authored level — sets neither
    variable, so the sampled arm's cell key is byte-identical to a canonical
    capture's and its digest may be compared with one. Any other arm sets both
    what it varies and, through `VITREA_WEB_CAPTURES`, a scratch destination:
    `probeCanonicalOutputRefusal` requires exactly that of a probe run.
    """
    env = dict(os.environ, VITREA_WEB_CAPTURES=str(arm_root(out, phase, scheme, arm)))
    if not (arm.texture and not arm.hinted):
        env["VITREA_BACKDROP_MODE"] = arm.mode
    if arm.hinted:
        env["VITREA_BACKDROP_LEVELS"] = str(levels_path)
    return env


# Read from the same variable the scene server binds, so the waiter and the
# server cannot disagree about which port this run owns. G1 held a second copy
# of 5189 here; W27f G2 made the port overridable because this gate is forbidden
# to use 5189 at all — another worker holds this machine's native capture path.
SCENE_SERVER_PORT = int(os.environ.get("VITREA_SCENE_SERVER_PORT", "5189"))


def wait_for_scene_server_port(timeout=1800, poll=10):
    """Block until the scene server's port is free.

    `web/vite.config.ts` binds this port with `strictPort`, so two capture runs
    that chose the same one cannot overlap — and on this machine they routinely
    try to, because sibling worktrees run their own gates. Waiting is the honest
    response: the alternative is a capture that fails for a reason having
    nothing to do with the material, halfway through a sweep. Choosing a free
    port is now possible too, and is what this gate does; the wait stays because
    a free port can still be taken between the check and the bind.
    """
    deadline = time.time() + timeout
    while True:
        with socket.socket() as probe:
            probe.settimeout(1)
            if probe.connect_ex(("127.0.0.1", SCENE_SERVER_PORT)) != 0:
                return
        if time.time() > deadline:
            raise SystemExit(
                f"Port {SCENE_SERVER_PORT} has been held by another capture run for "
                f"{timeout}s. The scene server binds it with strictPort, so this run cannot "
                "start until that one finishes."
            )
        print(f"    waiting for the scene server port {SCENE_SERVER_PORT}", flush=True)
        time.sleep(poll)


def run_capture(command, cwd, log, env, attempts=3):
    """Run a capture command, waiting out a busy scene-server port and retrying."""
    log.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(attempts):
        wait_for_scene_server_port()
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=cwd, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT)
        if result.returncode == 0 or "is already in use" not in log.read_text():
            return result.returncode
        print(f"    the port was taken mid-run; retrying ({attempt + 1}/{attempts})", flush=True)
    return result.returncode


def artefacts_of(arm, scene):
    """The three files a capture of one scene must leave, all read by this gate."""
    return (f"{scene}__{arm.tier}.png", f"cell__{arm.tier}.json", f"report__{arm.tier}.json")


def clear_scene_outputs(out, phase, scheme, arm, scenes, matrix=None):
    """Remove what a previous attempt left for exactly these scenes.

    An arm is re-run after a port collision, a demotion or a crash, and the
    capture commands write per scene: whatever the failed attempt produced for
    the scenes being re-captured is still on disk under the names the next
    attempt will be looked for under. Cleared here so that "the file is there"
    can mean "this invocation wrote it".
    """
    for scene in scenes:
        shutil.rmtree(capture_dir(out, phase, scheme, arm, scene), ignore_errors=True)
    if matrix is not None:
        matrix.unlink(missing_ok=True)


def stale_or_missing(out, phase, scheme, arm, scenes, since):
    """Which required artefacts this invocation did not write. Empty is the pass.

    Existence is not the test — modification time against the moment the command
    started is, because the failure this guards against is a run that produced
    nothing and left an older file to be read as its result.
    """
    faults = []
    for scene in scenes:
        directory = capture_dir(out, phase, scheme, arm, scene)
        for name in artefacts_of(arm, scene):
            path = directory / name
            if not path.exists():
                faults.append(f"{scene}/{name} (absent)")
            elif path.stat().st_mtime < since:
                faults.append(f"{scene}/{name} (older than this run)")
    return faults


def run_compare(out, phase, scheme, arm, scenes, levels_path, dry_run):
    """One `compare` invocation: one tier, one profile, one route, one hint set.

    Both outputs go to scratch — the capture tree through `VITREA_WEB_CAPTURES`
    and the matrix through `--out-matrix`. `--write-partial` keeps a matrix on
    disk even when a cell fails to measure, and the exit status is recorded
    rather than raised on: a probe arm is expected to miss adopted bounds, and
    losing the whole sweep to that would throw away the evidence the gate is
    being run for. A missing PNG is a different matter and does stop the run.
    """
    matrix = phase_dir(out, phase) / scheme.name / f"{arm.name}-matrix.json"
    log = phase_dir(out, phase) / scheme.name / f"{arm.name}.log"
    env = arm_env(out, phase, scheme, arm, levels_path)
    command = [
        "pnpm", "--fail-if-no-match", "--filter", "@vitrea/calibration", "run", "compare", "--",
        "--profile", scheme.profile,
        "--material-profile", scheme.document,
        "--renderer", arm.tier,
        "--set", fixture_set_for(phase),
        "--scene", ",".join(scenes),
        "--out-matrix", str(matrix),
        "--write-partial",
    ]
    if dry_run:
        print(f"    would run: {' '.join(command)}")
        return {"arm": arm.name, "route": "compare", "dryRun": True, "scenes": list(scenes)}
    started = time.time()
    clear_scene_outputs(out, phase, scheme, arm, scenes, matrix)
    code = run_capture(command, ROOT, log, env)
    faults = stale_or_missing(out, phase, scheme, arm, scenes, started)
    if faults:
        raise SystemExit(f"{scheme.name}/{arm.name}: this run did not write {faults} "
                         f"(exit {code}); see {log}. A demoted tier writes the other tier's "
                         "names, which is the usual cause.")
    return {"arm": arm.name, "route": "compare", "exitCode": code, "matrix": str(matrix),
            "log": str(log), "scenes": list(scenes), "capturedAfter": started}


def run_direct(out, phase, scheme, arm, scenes, levels_path, dry_run):
    """`capture-web` alone, for scenes this profile's native bed does not hold.

    `compare` plans its cells from the native manifest, so a scene with no
    fixture in this colour scheme is not a cell it can measure at all. The web
    side is still perfectly capturable — the scene page needs the background
    raster, which every scheme shares — and those captures answer every
    question that does not involve Apple: the hinted page against the sampled
    render, against the unhinted page, against the same arm before the change.
    Written into the same `<profileKey>/<scene>` layout `compare` uses, so one
    reader walks both.
    """
    log = phase_dir(out, phase) / scheme.name / f"{arm.name}-direct.log"
    env = arm_env(out, phase, scheme, arm, levels_path)
    command = [
        "npx", "tsx", "scripts/capture-web.ts", *scenes,
        "--renderer", arm.tier,
        "--color-scheme", scheme.name,
        "--scale", "1",
        "--out", str(arm_root(out, phase, scheme, arm) / scheme.profile),
        "--material-profile", str(scheme.document_path),
    ]
    if dry_run:
        print(f"    would run: {' '.join(command)}")
        return {"arm": arm.name, "route": "capture-web", "dryRun": True, "scenes": list(scenes)}
    started = time.time()
    clear_scene_outputs(out, phase, scheme, arm, scenes)
    code = run_capture(command, PACKAGE, log, env)
    faults = stale_or_missing(out, phase, scheme, arm, scenes, started)
    if faults:
        raise SystemExit(f"{scheme.name}/{arm.name}: this direct run did not write {faults} "
                         f"(exit {code}); see {log}. A demoted tier writes the other tier's "
                         "names, which is the usual cause.")
    return {"arm": arm.name, "route": "capture-web", "exitCode": code, "log": str(log),
            "scenes": list(scenes), "capturedAfter": started}


def sampled_levels(out, phase, scheme, scenes):
    """The measured backdrop level per scene, off the texture-sampled arm.

    The level a hinted arm authors has to be the one the sampled path resolved
    on the same scene, or the two are not the same configuration seen twice.
    The overlay of a stack samples rendered glass through the DOM even in this
    arm, so only the texture-configured groups are read, and they are required
    to agree: two texture groups at different levels would make "the scene's
    level" a choice rather than a measurement.
    """
    levels = {}
    for scene in scenes:
        directory = capture_dir(out, phase, scheme, ARMS_BY_NAME["sampled"], scene)
        report = json.loads((directory / "report__webgpu.json").read_text())
        found = [group["backdropTone"]["level"] for group in report["page"]["groups"]
                 if group["configuredSource"] == "texture"]
        if not found:
            raise ValueError(f"{scene}: the sampled arm resolved no texture-sourced group")
        if max(found) - min(found) > TOLERANCE:
            raise ValueError(f"{scene}: texture groups resolved {found} levels, not one")
        levels[scene] = found[0]
    return levels


def background_levels(spec, levels):
    """The measured level per BACKGROUND, from a phase's per-scene levels.

    A texture-sampled group's resolved `backdropTone.level` is a property of the
    raster and of nothing else: across G0's twenty-two scenes and this gate's two
    colour schemes, every scene sharing a background resolved the same level to
    the bit, over five components and four sizes. So a level measured on one
    scene is a measurement for every scene over the same raster — which is what
    lets a later phase author the hint without re-drawing the sampled arm. Any
    disagreement inside a background would falsify that and is refused here
    rather than averaged away.
    """
    background = {s["id"]: s["background"] for s in spec["scenes"]}
    grouped = {}
    for scene, level in levels.items():
        grouped.setdefault(background[scene], []).append((scene, level))
    out = {}
    for name, members in grouped.items():
        values = [level for _, level in members]
        if max(values) - min(values) > TOLERANCE:
            raise SystemExit(
                f"The scenes over background '{name}' resolved different sampled levels "
                f"({members}). A level is only inheritable because the raster decides it."
            )
        out[name] = {"level": values[0], "measuredOn": sorted(s for s, _ in members)}
    return out


def inherited_levels(spec, scenes, sources):
    """Levels for scenes this phase did not sample, from the same backgrounds.

    Returns the levels and their per-scene provenance, or refuses. A background
    no earlier phase measured is an INPUT GAP, not an occasion to pick a number:
    the holdout bed's `hc-text` and `mid-dark-solid` rasters appear in no
    calibration scene, so a holdout run that authors a hint over them has to
    capture the texture-sampled arm for those scenes (put `sampled` in --arms)
    or be given the levels explicitly (--levels).
    """
    background = {s["id"]: s["background"] for s in spec["scenes"]}
    levels, provenance, missing = {}, {}, {}
    for scene in scenes:
        name = background[scene]
        source = next((s for s in sources if name in s["levels"]), None)
        if source is None:
            missing.setdefault(name, []).append(scene)
            continue
        levels[scene] = source["levels"][name]["level"]
        provenance[scene] = {"background": name, "from": source["name"],
                             "measuredOn": source["levels"][name]["measuredOn"]}
    if missing:
        named = "; ".join(f"'{name}' ({', '.join(scenes)})" for name, scenes in missing.items())
        raise SystemExit(
            f"No measured backdrop level for {named}. These backgrounds appear in no phase "
            "this run can read, so the hint over them would be invented. Capture the "
            "texture-sampled arm for those scenes (--arms sampled,...) or pass --levels."
        )
    return levels, provenance


def check_levels_against_sources(spec, measured, sources):
    """A level measured here against the same raster's level measured elsewhere.

    A run that captures its own texture-sampled arm does not need to inherit,
    but where an earlier phase measured the same raster the two numbers must be
    the same number: that is what makes a separately captured run comparable
    with the phase it sits beside, rather than merely adjacent to it. A
    disagreement is a stop, because it means the sampled analysis moved between
    the two runs and every hinted arm in them authored a different backdrop.
    """
    if not measured or not sources:
        return None
    here = background_levels(spec, measured)
    agrees = []
    for source in sources:
        shared = [name for name in here if name in source["levels"]]
        for name in shared:
            theirs = source["levels"][name]["level"]
            if abs(theirs - here[name]["level"]) > TOLERANCE:
                raise SystemExit(
                    f"Over background '{name}' this run's texture-sampled arm resolved "
                    f"{here[name]['level']!r} where {source['name']} recorded {theirs!r}. The "
                    "sampled analysis has moved between the two runs, so their hinted arms did "
                    "not author the same backdrop and cannot be read together."
                )
        if shared:
            agrees.append({"source": source["name"], "backgrounds": sorted(shared)})
    return agrees


def check_levels_against_g0(levels):
    """The light hint levels against the committed G0 evidence, to the bit.

    Returned rather than raised on for scenes G0 never read; a disagreement on
    a scene it did read is a stop, because it means the texture-sampled analysis
    moved and every "same hint" comparison across the two gates is void.
    """
    evidence = json.loads(G0_EVIDENCE.read_text())
    recorded = {row["scene"]: row["hintedBackdropLevel"] for row in evidence["rows"]}
    checked, unknown = [], []
    for scene, level in levels.items():
        if scene not in recorded:
            unknown.append(scene)
            continue
        if abs(recorded[scene] - level) > TOLERANCE:
            raise SystemExit(
                f"{scene}: the sampled backdrop level is {level!r} where G0 recorded "
                f"{recorded[scene]!r}. The texture-sampled analysis has moved, so this run "
                "cannot be read beside G0's."
            )
        checked.append(scene)
    return {"checkedAgainstG0": sorted(checked), "notInG0": sorted(unknown)}


def holdout_guard(out, scenes):
    """Holdout is read once per frozen configuration, and the record says so.

    Written before the first capture, not after the last: the spend happens when
    the cells are drawn, and a run that crashed halfway has still seen them.
    """
    marker = out / "holdout-spent.json"
    if marker.exists():
        previous = json.loads(marker.read_text())
        raise SystemExit(
            f"The holdout has already been read under this scratch root, at "
            f"{previous.get('spentAt')} on commit {previous.get('commit')} with material sources "
            f"{previous.get('materialSourcesSha256')}. Reading it again is a new spend and a "
            f"user decision: delete {marker} deliberately, or point --out somewhere else."
        )
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(
        {"spentAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
         # The file that actually ran, not a name baked in when it was written:
         # this runner is a copy, and a spend marker naming the wrong program is
         # exactly the provenance the marker exists to supply. The marker this
         # gate's own run wrote still carries the inherited literal, and stays
         # that way — claims §5.135 records it rather than rewriting evidence.
         "spentBy": f"{Path(__file__).name} capture --phase holdout",
         "scenes": scenes, **configuration()}, indent=2) + "\n")
    return marker


def porcelain_paths(stdout):
    """The paths out of `git status --porcelain`, status columns intact.

    Porcelain's first two columns are the index and worktree status, and either
    may be a space: an unstaged modification prints " M path". The G1 runner
    stripped the whole output before slicing each line at offset 3, so a first
    line whose status began with a space lost its first path character and the
    candidate manifest recorded `ackages/platform-web/src/optics.ts`
    (tech-debt-tracker, "A first line whose status starts with a space…").
    The historical reading keeps what it recorded; this copy does not repeat it.

    Renames print `R  old -> new`; the new path is the one that exists, so it is
    the one reported. Quoted paths are left exactly as git printed them rather
    than half-decoded here — and git quotes any path containing a space whatever
    `core.quotePath` says, which this repository reaches on `Figma Design/`. The
    bound on that: a quoted path whose own text contains a literal " -> " would
    be split at the wrong place and reported truncated. Nothing downstream
    breaks, because these paths feed `dirtyPaths` in a reading's provenance and
    no fingerprint, digest or measured number is taken from them; a
    misreported dirty path would misdescribe the tree a reading was taken from,
    which is worth knowing and is not worth a quoted-string parser here.
    """
    paths = []
    for line in stdout.split("\n"):
        if not line.strip():
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return paths


def git_state():
    """The source tree's commit and dirty paths, where the tree is a checkout.

    A baseline is expected to be captured from a FROZEN COPY of the source —
    `git archive` into scratch — so that the tree cannot move while the run is
    in flight. Such a copy is not a checkout, and the commit it was taken from
    is then supplied as `W27F_G2_SOURCE_COMMIT` rather than invented here. A
    reading that can name neither says so.
    """
    def out(*args):
        return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True,
                              text=True).stdout
    try:
        return {"sourceRoot": str(ROOT), "commit": out("rev-parse", "HEAD").strip(),
                "dirtyPaths": porcelain_paths(out("status", "--porcelain"))}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"sourceRoot": str(ROOT),
                "commit": os.environ.get("W27F_G2_SOURCE_COMMIT"),
                "dirtyPaths": None,
                "note": "Not a git checkout: a frozen source copy. The commit is whatever "
                        "W27F_G2_SOURCE_COMMIT stated, and null where it stated nothing."}


def configuration():
    """Everything that decides what drew, digested. The reading's provenance."""
    return {
        **git_state(),
        "sceneManifestSha256": digest(SCENES),
        "nativeManifestSha256": digest(FIXTURES / "manifest.json"),
        "declaredGeometryScriptSha256": digest(GEOMETRY),
        "contourInstrumentSha256": digest(ROOT / "packages/calibration/results/"
                                          "2026-09-08-w23-collapsed-rim/g0/read-contour.py"),
        "g0ReaderSha256": digest(G0_READ),
        "runnerSha256": digest(Path(__file__)),
        "materialSourcesScope": MATERIAL_SOURCES_SCOPE,
        "materialSourcesSha256": {name: digest(ROOT / name) for name in MATERIAL_SOURCES},
        "materialProfileSha256": {
            scheme.name: digest(scheme.document_path) for scheme in SCHEMES.values()
        },
        "resolvedMaterialSha256": {
            scheme.name: json.loads(scheme.document_path.read_text()).get("resolvedMaterialSha256")
            for scheme in SCHEMES.values()
        },
    }


def level_sources(args, spec):
    """Where a phase that does not sample may inherit its hint levels from.

    Ordered, and every entry names itself in the reading: an explicit `--levels`
    file first, then the phase named by `--compare-phase` — for a holdout run
    that is the candidate calibration phase, whose sampled arm measured the same
    rasters under the same configuration.
    """
    sources = []
    if args.levels is not None:
        supplied = json.loads(args.levels.read_text())
        sources.append({"name": f"--levels {args.levels}",
                        "levels": background_levels(spec, supplied)})
    if args.compare_phase is not None:
        for scheme in args.schemes:
            path = phase_dir(args.out, args.compare_phase) / scheme / "levels.json"
            if path.exists():
                sources.append({"name": f"{args.compare_phase} phase ({scheme})",
                                "levels": background_levels(spec, json.loads(path.read_text()))})
    return sources


def stacked_scenes(geometry, scenes):
    """Which of these scenes place a surface above the base plane.

    From the declaration, not from a name. It matters to the arm plan: on a
    stack the OVERLAY is DOM-backed on every route — it samples rendered glass,
    not the raster — so a texture-labelled capture of a stack still contains the
    page-content material this gate is changing. "The sampled path is
    byte-identical" is a statement about texture-sourced groups and does not
    reach those composites, which is why the texture controls are captured for
    stacks even in a phase that skips them everywhere else.
    """
    return [scene for scene in scenes
            if len({s["plane"] for s in geometry["scenes"][scene]["surfaces"]}) > 1]


def capture(args):
    out = args.out
    spec, manifest = scene_spec(), native_manifest()
    geometry = g0.declared_geometry()
    arms = [ARMS_BY_NAME[name] for name in args.arms]
    inherit = level_sources(args, spec)
    beds = {}
    for name in args.schemes:
        refereed, unrefereed = bed_for(SCHEMES[name], args.phase, spec, manifest, args.scenes)
        if not refereed and not unrefereed:
            raise SystemExit(f"{name}: this phase declares no scene to measure")
        beds[name] = (refereed, unrefereed)
        print(f"{name}: {len(refereed) + len(unrefereed)} scene(s), {len(refereed)} with a "
              f"{SCHEMES[name].profile} native fixture")
        if unrefereed:
            print(f"  captured without a native reference: {', '.join(unrefereed)}")
    # Before the first capture: drawing the cells is the spend, so a run that
    # dies halfway has still spent them.
    if args.phase == "holdout" and not args.dry_run:
        holdout_guard(out, {name: sum(beds[name], []) for name in beds})
    plan = {"phase": args.phase, "schemes": {}}
    for name in args.schemes:
        scheme = SCHEMES[name]
        refereed, unrefereed = beds[name]
        scenes = refereed + unrefereed
        # Per scheme, not once for the run: schemes are captured in separate
        # invocations often enough, and a merged manifest that carried one
        # configuration for all of them would attribute the earlier scheme's
        # pixels to the later scheme's material.
        stacks = stacked_scenes(geometry, scenes)
        # Scenes whose raster no earlier phase measured. Their hint cannot be
        # inherited, so the texture-sampled arm has to measure it here even in a
        # run that skips that arm — the holdout bed's hc-text and mid-dark-solid
        # rasters are in no calibration scene, and this is the difference between
        # measuring a level and choosing one.
        background = {s["id"]: s["background"] for s in spec["scenes"]}
        inheritable = {name for source in inherit for name in source["levels"]}
        unmeasured = [s for s in scenes if background[s] not in inheritable]
        # Which scenes each arm covers. An arm the run asked for covers the whole
        # bed; a texture control the run skipped is still taken over the stacks —
        # a stack's overlay is DOM-backed on every route, so its composite is not
        # covered by the sampled path's identity — and the sampled arm is taken
        # over any scene whose level would otherwise have to be invented.
        needs_sampling = sorted(set(stacks) | set(unmeasured))
        coverage = {}
        for arm in ARMS:
            if arm in arms:
                coverage[arm.name] = scenes
            elif arm.texture and stacks:
                coverage[arm.name] = stacks
            elif arm.name == "sampled" and needs_sampling:
                coverage[arm.name] = needs_sampling
        if ARMS_BY_NAME["sampled"].name in coverage and unmeasured:
            coverage["sampled"] = sorted(set(coverage["sampled"]) | set(unmeasured),
                                         key=scenes.index)
            print(f"  the texture-sampled arm also covers {len(unmeasured)} scene(s) whose "
                  f"backdrop raster no earlier phase measured: {', '.join(unmeasured)}")
        record = {"profile": scheme.profile, "materialProfile": scheme.document,
                  "capturedWith": configuration(),
                  "armNames": [a.name for a in ARMS if a.name in coverage],
                  "armCoverage": coverage,
                  "requestedArms": [a.name for a in arms],
                  "stackedScenes": stacks,
                  "scenes": scenes, "nativeRefereed": refereed,
                  "capturedWithoutNative": unrefereed, "arms": []}
        levels_path = phase_dir(out, args.phase) / name / "levels.json"

        def take(arm):
            covered = coverage[arm.name]
            here = [s for s in refereed if s in covered]
            there = [s for s in unrefereed if s in covered]
            print(f"  {arm.name} ({arm.tier}, {arm.mode}, hint={arm.hinted}), "
                  f"{len(covered)} scene(s)", flush=True)
            if here:
                record["arms"].append(run_compare(out, args.phase, scheme, arm, here,
                                                  levels_path, args.dry_run))
            if there:
                record["arms"].append(run_direct(out, args.phase, scheme, arm, there,
                                                 levels_path, args.dry_run))

        # The texture-sampled arm first wherever it is captured at all: its
        # resolved tone is the level every hinted arm authors. What it does not
        # cover is inherited by background raster from a phase that measured the
        # same raster, and a raster no phase measured stops the run rather than
        # being given a number.
        sampled = ARMS_BY_NAME["sampled"]
        provenance = {}
        measured = {}
        if sampled.name in coverage:
            take(sampled)
            if not args.dry_run:
                measured = sampled_levels(out, args.phase, scheme, coverage[sampled.name])
                provenance["measuredHere"] = {
                    "source": "this phase's texture-sampled arm", "scenes": sorted(measured)}
                if name == "light":
                    provenance["measuredHere"].update(check_levels_against_g0(measured))
                # Measured here, and held to the same number an earlier phase
                # measured over the same raster — the check that lets a
                # separately captured run be read beside the phase it belongs to.
                agrees = check_levels_against_sources(spec, measured, inherit)
                if agrees:
                    provenance["measuredHere"]["agreesWith"] = agrees
        # What the sampled arm covers is measured, not inherited — in a dry run
        # it has not been measured yet, and inheriting it would report a gap this
        # plan already closes.
        sampled_here = set(coverage.get(sampled.name, []))
        rest = [scene for scene in scenes if scene not in measured and scene not in sampled_here]
        borrowed, per_scene = ({}, {}) if not rest else inherited_levels(spec, rest, inherit)
        if borrowed:
            provenance["inherited"] = {
                "source": "inherited by background raster from an earlier phase; this phase did "
                          "not capture the texture-sampled arm over these scenes",
                "perScene": per_scene}
        record["levels"] = {**measured, **borrowed}
        record["levelProvenance"] = provenance
        if not args.dry_run:
            levels_path.parent.mkdir(parents=True, exist_ok=True)
            levels_path.write_text(json.dumps(record["levels"], indent=2) + "\n")
            print(f"    hint levels → {levels_path} "
                  f"({len(measured)} measured here, {len(borrowed)} inherited)")
        for arm in ARMS:
            if arm.name in coverage and arm is not sampled:
                take(arm)
        plan["schemes"][name] = record
    manifest_path = phase_dir(out, args.phase) / "capture-manifest.json"
    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        # Merged, because a phase is often captured one scheme at a time — the
        # light and dark runs cannot share the scene server anyway. Overwriting
        # would leave the reader with a manifest describing half the captures on
        # disk, which is the one thing a manifest exists to prevent.
        if manifest_path.exists():
            previous = json.loads(manifest_path.read_text())
            plan["schemes"] = {**previous.get("schemes", {}), **plan["schemes"]}
        manifest_path.write_text(json.dumps(plan, indent=2) + "\n")
        print(f"\ncapture manifest → {manifest_path}")


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------


def check_axes(where, arm, page, level, structured, overlay_groups):
    """The arm's declaration against the report's own recorded state.

    Captures taken from W27f G0 onward state the axes they were asked for, so
    those fields are required here rather than inferred: this gate's runs are
    all after that landing, and an inference would be exactly the "the directory
    it was written to" provenance G0's reader refused. The resolved state is
    then checked to agree with the request, which is the half that says the
    request actually reached the material.
    """
    if "requestedBackdropMode" not in page:
        raise ValueError(f"{where}: the report states no requestedBackdropMode")
    if page["requestedBackdropMode"] != arm.mode:
        raise ValueError(f"{where}: report requests {page['requestedBackdropMode']}, "
                         f"expected {arm.mode}")
    expected_level = level if arm.hinted else None
    if page.get("requestedBackdropLevel") != expected_level:
        raise ValueError(f"{where}: report authors {page.get('requestedBackdropLevel')}, "
                         f"expected {expected_level}")
    undiscriminable = []
    for group in page["groups"]:
        # The overlay of a stack derives its tone from the glass already rendered
        # beneath it, so it is `dom` in every arm and never carries the raw
        # raster's hint. Its base is what an arm's label describes. Which group
        # is the overlay comes from the DECLARATION — the group of a surface on a
        # plane above the base — not from its id.
        overlay = group["id"] in overlay_groups
        want_mode = "dom" if overlay else arm.mode
        want_backend = ("gpu-texture" if arm.tier == "webgpu" and want_mode == "texture"
                        else "css-backdrop")
        if group["configuredSource"] != want_mode:
            raise ValueError(f"{where}/{group['id']}: configuredSource "
                             f"{group['configuredSource']}, expected {want_mode}")
        if group["state"]["samplingBackend"] != want_backend:
            raise ValueError(f"{where}/{group['id']}: samplingBackend "
                             f"{group['state']['samplingBackend']}, expected {want_backend}")
        signature = g0.hint_signature(group["backdropTone"], level)
        if arm.hinted and not overlay:
            if not signature:
                raise ValueError(f"{where}/{group['id']}: no authored hint in the resolved tone "
                                 f"{group['backdropTone']}")
        elif signature:
            # Over a uniform backdrop a sampled tone and a hint taken from it are
            # the same three numbers, so the record cannot separate them. Named
            # rather than raised, and refused where the raster has structure.
            if structured:
                raise ValueError(f"{where}/{group['id']}: the resolved tone carries the hint "
                                 "but this arm authored none")
            undiscriminable.append(group["id"])
    return {
        "provenance": "Stated by the capture's own report (requestedBackdropMode / "
                      "requestedBackdropLevel) and checked against the resolved group state.",
        "expectedBackdropMode": arm.mode,
        "expectedAuthoredLevel": expected_level,
        "reportedBackdropMode": page["requestedBackdropMode"],
        "reportedAuthoredLevel": page.get("requestedBackdropLevel"),
        "hintUndiscriminableGroups": undiscriminable,
    }


def region(data, native, surfaces, distances, selected):
    """The declared-region reading, with the native distance dropped where there is none.

    `read_region` measures a distance to the native fixture, so a scene this
    colour scheme has no fixture for needs that one field to become null rather
    than to be silently computed against something else. Every other quantity —
    interior level and spread, rim, footprint — is a property of the capture
    alone and survives the absence intact.
    """
    result = g0.read_region(data, native if native is not None else data, surfaces, distances,
                            selected)
    if native is None:
        result["deltaEAgainstNative"] = None
    return result


def changed_pixels(path, other, surfaces, distances, decidable):
    """WHERE two captures of the same scene differ, counted against the declared masks.

    Equal aggregate terms do not locate a difference: two different sets of
    pixels can carry the same interior mean, the same rim mean and the same
    shadow count. So when a digest moves, the pixels themselves are compared and
    the counts are reported — inside the declared footprint, inside the eroded
    interior, and outside every declared shape — rather than a spatial claim
    being inferred from metrics that never made one.
    """
    left = np.asarray(Image.open(path).convert("RGB"), dtype=int)
    right = np.asarray(Image.open(other).convert("RGB"), dtype=int)
    if left.shape != right.shape:
        return {"comparable": False, "why": f"{left.shape} against {right.shape}"}
    difference = np.abs(left - right)
    differs = difference.max(axis=-1) > 0
    union = np.minimum.reduce(distances)
    footprint, interior = union <= 0, union <= -6
    return {
        "comparable": True,
        "changedPixels": int(differs.sum()),
        "changedInsideDeclaredFootprint": int((differs & footprint).sum()),
        "changedInsideDeclaredInterior": int((differs & interior).sum()),
        "changedOutsideEveryDeclaredShape": int((differs & ~footprint).sum()),
        "changedInsideTheDecidableExterior": int((differs & decidable).sum()),
        "maxChannelDifference": int(difference.max()),
    }


def read_capture(path, arm, scene, background_id, native, surfaces, distances, decidable,
                 background_lum, tint, level, structured, overlay_groups, control):
    """One arm's PNG under the declared masks, with its report's provenance beside it.

    Two distances, not one. `deltaEAgainstNative` is the distance to Apple and is
    null where this colour scheme has no fixture; `deltaEAgainstSampledToday` is
    the distance to the texture-sampled render of the same scene, in the same
    units over the same declared footprint, and it exists wherever that render's
    PIXELS do. On the dark scenes with no native fixture it is the only ΔE there
    is, and it is what changes between the phases — which is why it is named
    apart from any delta of the native error.
    """
    data = g0.image(path)
    result = region(data, native, surfaces, distances, range(len(surfaces)))
    result["deltaEAgainstSampledToday"] = None if control is None else region(
        data, control, surfaces, distances, range(len(surfaces)))["deltaEAgainstNative"]
    result["outerShadowExteriorPixels"] = int((decidable & (
        (background_lum - data[1]) / np.maximum(background_lum, .00001) > .01)).sum())
    result["decidableExteriorPixels"] = int(decidable.sum())
    result["sha256"] = g0.digest(path)
    result["perSurface"] = {}
    for i, surface in enumerate(surfaces):
        per = region(data, native, surfaces, distances, [i])
        per["deltaEAgainstSampledToday"] = None if control is None else region(
            data, control, surfaces, distances, [i])["deltaEAgainstNative"]
        result["perSurface"][surface["nodeId"]] = per
    report = json.loads((path.parent / f"report__{arm.tier}.json").read_text())
    where = f"{arm.name}/{scene}"
    result["measuredBoundsExcess"] = g0.check_declared_bounds(
        where, surfaces, report["page"]["surfaces"], exact=arm.tier == "webgpu")
    if report["page"]["background"]["id"] != background_id:
        raise ValueError(f"{where}: composited '{report['page']['background']['id']}' where the "
                         f"declaration places '{background_id}'")
    result["requestedAxes"] = check_axes(where, arm, report["page"], level, structured,
                                         overlay_groups)
    result["surfaceRefraction"] = {s["nodeId"]: s["refraction"] for s in report["page"]["surfaces"]}
    result["groups"] = report["page"]["groups"]
    result["capturedAt"] = report["capturedAt"]
    result["adapter"] = report["page"]["adapter"]
    result["diagnostics"] = report["page"]["diagnostics"]
    result["colorScheme"] = report["colorScheme"]
    result["materialProfileApplied"] = None if report["materialProfile"] is None else {
        "path": report["materialProfile"]["path"], "sha256": report["materialProfile"]["sha256"]}
    if report["problems"] or report["page"]["problems"]:
        raise ValueError(f"{where}: {report['problems'] or report['page']['problems']}")
    if any(group["state"]["activeRenderer"] != arm.tier for group in result["groups"]):
        raise ValueError(f"{where}: the runtime resolved a tier this arm did not ask for")
    cell = json.loads((path.parent / f"cell__{arm.tier}.json").read_text())
    # Recorded and carried up as a caveat rather than raised on. Determinism is
    # measured per cell from two independent page loads, and a cell that is not
    # byte-identical over them is one whose digest cannot decide identity and
    # whose metrics carry that much noise — which is a fact about that cell, not
    # a reason to lose the other 279. The reading names every one of them.
    result["deterministic"] = cell["deterministic"]
    result["repeatNoise"] = cell["repeatNoise"]
    if arm.tier == "webgpu" and result["adapter"].get("isFallback") is not False:
        raise ValueError(f"{where}: a GPU-tier claim needs a measured hardware adapter")
    result["apparentPaintShade"] = None
    if tint is not None and tint.get("alpha", 1) == 1:
        # At full author opacity, projection onto the declared linear seed
        # identifies the observed shade; a half tint mixes the body and is
        # deliberately not interpreted as an isolated shade.
        seed = g0.w23.linearise(np.asarray(tint["srgb"], dtype=float))
        mean_rgb = np.asarray(result["interiorLinearRgbMean"])
        shade = float(np.dot(mean_rgb, seed) / np.dot(seed, seed))
        result["apparentPaintShade"] = shade
        result["paintOffSeedRgbNorm"] = float(np.linalg.norm(mean_rgb - shade * seed))
    return result


def delta(after, before, fields):
    """After minus before on the named scalars, with a null where either is absent."""
    out = {}
    for field in fields:
        a, b = after.get(field), before.get(field)
        out[f"{field}Delta"] = None if a is None or b is None else a - b
    return out


COMPARED = ("deltaEAgainstNative", "deltaEAgainstSampledToday", "interiorOklabLMean",
            "interiorOklabLStddev", "rimBandLinearMean", "rimLocalExcessMean",
            "interiorLinearLuminanceMean", "outerShadowExteriorPixels")


def g0_rows():
    return {row["scene"]: row for row in json.loads(G0_EVIDENCE.read_text())["rows"]}


def sampled_control_image(out, phase, scheme, scene, g0_scratch, g0_evidence):
    """The sampled-today PNG this scene's arms are measured against, and its provenance.

    This phase's own texture-sampled arm where it took one. Otherwise G0's
    scratch snapshot, and only when the file on disk digests to exactly the
    sha256 the committed G0 evidence recorded for that arm — the evidence
    carries the number, not the pixels, so a snapshot that cannot prove it is
    the same capture is not used. Nothing is synthesised: where neither exists
    the distance is null and the reading says the control is unknown.
    """
    own = capture_dir(out, phase, scheme, ARMS_BY_NAME["sampled"], scene) / f"{scene}__webgpu.png"
    if own.exists():
        return own, "this phase's texture-sampled arm"
    recorded = (g0_evidence.get(scene) or {}).get("readings", {}).get("sampledToday")
    if scheme.name == "light" and recorded is not None and g0_scratch is not None:
        snapshot = g0_scratch / scheme.profile / scene / f"{scene}__webgpu.png"
        if snapshot.exists() and g0.digest(snapshot) == recorded["sha256"]:
            return snapshot, (f"G0 scratch snapshot {snapshot}, digest "
                              f"{recorded['sha256'][:12]} matching the committed G0 evidence")
    return None, None


# What has to agree for two schemes' captures to be one phase: the commit, the
# sources that draw, and the material documents they were given. Deliberately not
# the working tree's dirty paths — an unrelated edit elsewhere in the repo does
# not change what the renderer drew, and refusing on it would make a two-part
# capture impossible on a tree anyone is working in.
FINGERPRINT = ("commit", "materialSourcesScope", "materialSourcesSha256", "materialProfileSha256")


def with_legacy_provenance(captured):
    """A manifest written before per-scheme provenance, read for what it does say.

    The baseline phase cannot be re-captured — its whole point is that it was
    taken before the runtime changed — so a reader that refused its manifest
    would destroy the evidence it exists to protect. Instead the phase-level
    provenance it does carry is attached to each scheme and LABELLED as
    phase-level: those runs took both schemes in one invocation, which is what
    makes the attribution true, and the label is what stops it being read as a
    per-scheme claim it never made. Nothing is upgraded: a fingerprint recorded
    under the old narrow scope keeps that scope and compares only with itself.
    """
    schemes = {}
    for name, record in captured.get("schemes", {}).items():
        record = dict(record)
        if "capturedWith" not in record and "capturedWith" in captured:
            record["capturedWith"] = {**captured["capturedWith"]}
            record["provenanceAttribution"] = (
                "phase-level: this manifest predates per-scheme provenance, and its schemes were "
                "captured in one invocation")
        else:
            record.setdefault("provenanceAttribution", "per-scheme")
        if "armNames" not in record:
            record["armNames"] = [arm.name for arm in ARMS]
            record["armNamesSource"] = (
                "assumed: this manifest predates the recorded arm set, and every phase written "
                "under it captured all seven arms")
        record.setdefault("armCoverage",
                          {name: record.get("scenes", []) for name in record["armNames"]})
        schemes[name] = record
    return schemes


def check_one_configuration(schemes):
    """One phase is one configuration, and a merged manifest has to prove it.

    Schemes are captured in separate invocations often enough — they cannot share
    the scene server — so the manifest carries each scheme's own provenance and
    this is where the two are held to being the same material. Without it a
    reading merged across a runtime change would attribute the earlier scheme's
    pixels to the later scheme's material and say so nowhere.
    """
    seen = {}
    for name, record in schemes.items():
        provenance = record.get("capturedWith")
        if provenance is None:
            raise SystemExit(
                f"The capture of scheme '{name}' records no capturedWith provenance. It predates "
                "per-scheme provenance and cannot be shown to be this phase's configuration; "
                "re-capture it."
            )
        seen[name] = {key: provenance.get(key) for key in FINGERPRINT}
    if len({json.dumps(f, sort_keys=True) for f in seen.values()}) > 1:
        scopes = {name: f["materialSourcesScope"] for name, f in seen.items()}
        if len(set(scopes.values())) > 1:
            raise SystemExit(
                f"These schemes record their sources under different fingerprint scopes {scopes}. "
                "A narrower scope is not a weaker version of a wider one — it digested different "
                "files — so the two cannot be compared. Re-capture the one on the old scope; a "
                "reading already written under it stays as it was recorded."
            )
        detail = "; ".join(f"{name}: {json.dumps(fingerprint, sort_keys=True)}"
                           for name, fingerprint in seen.items())
        raise SystemExit(
            "The schemes of this phase were captured on different configurations, so they are "
            f"not one phase: {detail}. Re-capture the stale scheme, or read them separately "
            "with --schemes."
        )


def read(args):
    out = args.out
    phase = args.phase
    manifest_path = phase_dir(out, phase) / "capture-manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"No capture manifest at {manifest_path}. Run `capture --phase {phase}`.")
    captured = {**json.loads(manifest_path.read_text())}
    captured["schemes"] = with_legacy_provenance(captured)
    spec = scene_spec()
    scene_specs = {s["id"]: s for s in spec["scenes"]}
    geometry = g0.declared_geometry()
    g0_evidence = g0_rows()
    before = None
    if args.compare_reading is not None or args.compare_phase is not None:
        before_path = (args.compare_reading if args.compare_reading is not None
                       else phase_dir(out, args.compare_phase) / "reading.json")
        if not before_path.exists():
            raise SystemExit(f"No reading at {before_path} to compare against.")
        before = json.loads(before_path.read_text())

    check_one_configuration({name: record for name, record in captured["schemes"].items()
                             if name in args.schemes})
    document = {
        "date": GATE_DATE,
        "gate": GATE,
        "phase": phase,
        "captureRoot": str(phase_dir(out, phase).resolve()),
        "comparePhase": args.compare_phase,
        "comparedAgainst": None if before is None else {
            "reading": str(before_path.resolve()), "phase": before.get("phase"),
            "captureRoot": before.get("captureRoot")},
        "arms": {arm.name: {"tier": arm.tier, "backdropMode": arm.mode, "authorsHint": arm.hinted,
                            "g0Arm": arm.g0} for arm in ARMS},
        "declaredGeometrySource": geometry["source"],
        "method": METHOD,
        "schemes": {},
    }

    for scheme_name, record in captured["schemes"].items():
        if scheme_name not in args.schemes:
            continue
        scheme = SCHEMES[scheme_name]
        levels = record["levels"]
        refereed = set(record["nativeRefereed"])
        # Exactly what this phase captured, in the declared order. A phase may
        # legitimately take fewer arms than the seven — a holdout run whose
        # texture control is already established elsewhere — and the reading
        # then describes the arms that exist rather than failing on the ones
        # that do not.
        arms = [a for a in ARMS if a.name in record["armNames"]]
        coverage = record["armCoverage"]
        noisy = []
        before_rows = {} if before is None else {
            row["scene"]: row for row in
            (before.get("schemes", {}).get(scheme_name) or {}).get("rows", [])}
        css_excess = set()
        rows = []
        for scene in record["scenes"]:
            declared = geometry["scenes"][scene]
            surfaces = declared["surfaces"]
            native_path = FIXTURES / scheme.profile / f"{scene}.png"
            native = g0.image(native_path) if scene in refereed else None
            background_path = FIXTURES / "backgrounds" / f"{declared['backgroundId']}@1x.png"
            background = g0.image(background_path)
            # Structure in the raster, measured rather than inferred from the id:
            # it is what decides whether a sampled tone and a hint drawn from it
            # are separable in the record at all.
            structured = float(background[1].std()) > 0
            distances = [g0.distance(s, background[1].shape) for s in surfaces]
            union = np.minimum.reduce(distances)
            decidable = (union > 0) & (background[1] >= .05)
            tint = spec["tints"].get(scene_specs[scene].get("tint"))
            # Which sampling group is a stack's overlay, from the declaration: the
            # group of any surface the declaration places above the base plane.
            overlay_groups = {s["groupId"] for s in surfaces if s["plane"] != "base"}
            control_path, control_source = sampled_control_image(
                out, phase, scheme, scene, args.g0_scratch, g0_evidence)
            control = None if control_path is None else g0.image(control_path)
            row = {"scene": scene, "hintedBackdropLevel": levels[scene], "surfaces": surfaces,
                   "backgroundSha256": g0.digest(background_path),
                   "nativeFixture": scene in refereed,
                   "nativeSha256": g0.digest(native_path) if scene in refereed else None,
                   "sampledTodayControl": None if control_path is None else {
                       "source": control_source, "sha256": g0.digest(control_path)},
                   "readings": {}}
            if native is None:
                # Named, not omitted: this scheme's bed holds no fixture for this
                # scene, so every ΔE below is null and the row's evidence is the
                # arms against each other.
                row["readings"]["native"] = None
            else:
                native_reading = g0.read_region(native, native, surfaces, distances,
                                                range(len(surfaces)))
                native_reading["sha256"] = row["nativeSha256"]
                native_reading["perSurface"] = {
                    s["nodeId"]: g0.read_region(native, native, surfaces, distances, [i])
                    for i, s in enumerate(surfaces)}
                native_reading["outerShadowExteriorPixels"] = int((decidable & (
                    (background[1] - native[1]) / np.maximum(background[1], .00001) > .01)).sum())
                native_reading["decidableExteriorPixels"] = int(decidable.sum())
                row["readings"]["native"] = native_reading

            for arm in arms:
                if scene not in coverage[arm.name]:
                    continue
                path = (capture_dir(out, phase, scheme, arm, scene) /
                        f"{scene}__{arm.tier}.png")
                reading = read_capture(path, arm, scene, declared["backgroundId"], native,
                                       surfaces, distances, decidable, background[1], tint,
                                       levels[scene], structured, overlay_groups, control)
                if arm.tier == "css":
                    css_excess.add(tuple(reading["measuredBoundsExcess"]))
                if not reading["deterministic"] or reading["repeatNoise"] != 0:
                    noisy.append({"scene": scene, "arm": arm.name,
                                  "repeatNoise": reading["repeatNoise"]})
                # Every arm against the texture-sampled render of the same scene:
                # on a scheme with no native fixture this is the whole of the
                # evidence, and on one with a fixture it is what separates "the
                # page-content path is wrong" from "the material is wrong".
                #
                # The control is this phase's own sampled arm where it took one.
                # Where it did not, the committed G0 evidence supplies it for the
                # light scenes it read — legitimately, because the sampled path
                # is proven byte-identical on this configuration by the
                # calibration phase's identity verdict, and the control names
                # which of the two it is either way.
                against, against_source = row["readings"].get("sampled"), "this phase"
                if against is None and scheme_name == "light" and scene in g0_evidence:
                    against = g0_evidence[scene]["readings"]["sampledToday"]
                    against_source = "G0 committed evidence (sampledToday)"
                comparisons = {
                    "sampledControl": None if against is None or arm.name == "sampled"
                    else against_source,
                    "vsSampledToday": None if against is None or arm.name == "sampled"
                    else delta(reading, against, COMPARED),
                }
                # The committed G0 evidence carries both the numbers and each
                # arm's PNG digest, so the light "before" needs no re-capture:
                # identity is decided against the recorded digest, and every
                # metric against the recorded metric.
                g0_row = g0_evidence.get(scene)
                if scheme_name == "light" and arm.g0 is not None and g0_row is not None:
                    g0_reading = g0_row["readings"][arm.g0]
                    comparisons["vsG0"] = {
                        "arm": arm.g0,
                        "pixelIdentical": g0_reading["sha256"] == reading["sha256"],
                        "g0Sha256": g0_reading["sha256"],
                        **delta(reading, g0_reading, COMPARED),
                    }
                else:
                    comparisons["vsG0"] = None
                comparisons["vsComparePhase"] = None
                if before is not None:
                    prior_row = before_rows.get(scene)
                    if prior_row is not None:
                        prior_reading = prior_row["readings"].get(arm.name)
                        if prior_reading is not None:
                            identical = prior_reading["sha256"] == reading["sha256"]
                            comparisons["vsComparePhase"] = {
                                "phase": before.get("phase", args.compare_phase),
                                "capturedWith": (before["schemes"][scheme_name]
                                                 .get("capturedWith", {}).get("commit")),
                                "pixelIdentical": identical,
                                "sha256": prior_reading["sha256"],
                                **delta(reading, prior_reading, COMPARED),
                            }
                            # Where the digest moved, WHERE it moved — measured
                            # against the masks, because equal terms locate
                            # nothing. Only then, and only when the compared
                            # run's PNG is still on disk; its root comes from the
                            # reading itself, so a comparison across two scratch
                            # roots resolves as readily as one inside a phase.
                            prior_png = (capture_dir_under(before["captureRoot"], scheme, arm,
                                                           scene) / f"{scene}__{arm.tier}.png")
                            if not identical and prior_png.exists():
                                comparisons["vsComparePhase"]["changedPixelGeometry"] = (
                                    changed_pixels(path, prior_png, surfaces, distances,
                                                   decidable))
                reading["comparisons"] = comparisons
                row["readings"][arm.name] = reading

            planes = {s["plane"] for s in surfaces}
            if len(planes) > 1:
                # A stack: the overlay is the only surface on this path with a
                # native cell of its own, so it is lifted out by plane rather
                # than by node id.
                overlay = [s for s in surfaces if s["plane"] != "base"]
                row["stackOverlay"] = {
                    "surfaces": [s["nodeId"] for s in overlay],
                    "readings": {name: {s["nodeId"]: reading["perSurface"][s["nodeId"]]
                                        for s in overlay}
                                 for name, reading in row["readings"].items()
                                 if reading is not None},
                }
            rows.append(row)

        if len(css_excess) != 1:
            raise SystemExit(f"{scheme_name}: the CSS arms do not share one measured size "
                             f"excess: {sorted(css_excess)}")
        document["schemes"][scheme_name] = {
            "capturedWith": record["capturedWith"],
            "provenanceAttribution": record["provenanceAttribution"],
            "readWith": configuration(),
            "armNames": record["armNames"],
            "armNamesSource": record.get("armNamesSource", "recorded by the capture"),
            "profile": scheme.profile,
            "materialProfile": record["materialProfile"],
            "nativeRefereed": record["nativeRefereed"],
            "capturedWithoutNative": record["capturedWithoutNative"],
            "levels": levels,
            "levelProvenance": record.get("levelProvenance"),
            "cssTierMeasuredSizeExcessCssPx": list(sorted(css_excess)[0]),
            "nonDeterministicCaptures": noisy,
            "armCoverage": coverage,
            "textureIdentity": texture_identity(rows, arms),
            "rows": rows,
        }

    destination = args.reading or phase_dir(out, phase) / "reading.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Merged for the same reason the capture manifest is: one scheme at a time
    # is how these runs happen, and a reading that dropped the other scheme
    # would look like a run that never measured it.
    if destination.exists():
        previous = json.loads(destination.read_text())
        if previous.get("phase") == phase:
            document["schemes"] = {**previous.get("schemes", {}), **document["schemes"]}
            # The same rule the manifest is held to, at the other door: a merge
            # across two `read` runs may not quietly join two configurations.
            check_one_configuration(document["schemes"])
    destination.write_text(json.dumps(g0.clean(document), indent=2, allow_nan=False) + "\n")
    summarise(document)
    print(f"\nreading → {destination}")


def texture_identity(rows, arms):
    """Did the texture-sampled arms draw the same pixels as the recorded run?

    W27f's acceptance is that the sampled path is byte-identical, so this is a
    verdict and not a metric: per texture-route arm, which scenes matched the
    digest they are compared against and which moved. `moved` is STRICTLY every
    digest that differs, and nothing is promoted out of it: a capture whose
    pixels changed is not byte-identical, whatever else is true of it, and a
    verdict that reclassified such a cell would be reporting an acceptance the
    evidence does not support. What is added instead is annotation, so a reader
    can see the difference's character without the verdict having decided it:
    whether any COMPARED TERM moved with it — which does not locate anything,
    since equal aggregates can cover different pixels — whether the cell is even
    byte-deterministic over two loads of the same page, and, where the compared
    PNG is still on disk, the measured count of changed pixels inside and
    outside the declared masks, which is the only spatial claim here that is a
    measurement. `undecided` is nothing recorded to compare against at all, and
    is never counted as a pass.
    """
    verdict = {}
    for arm in arms:
        if not arm.texture:
            continue
        identical, moved, undecided = [], [], []
        for row in rows:
            reading = row["readings"].get(arm.name)
            if reading is None:
                continue
            against = reading["comparisons"]["vsComparePhase"] or reading["comparisons"]["vsG0"]
            if against is None:
                undecided.append(row["scene"])
            elif against["pixelIdentical"]:
                identical.append(row["scene"])
            else:
                deltas = {key: value for key, value in against.items()
                          if key.endswith("Delta") and value is not None}
                moved.append({
                    "scene": row["scene"],
                    "sha256": reading["sha256"],
                    "comparedWith": against.get("sha256") or against.get("g0Sha256"),
                    "measuredTermsUnchanged": all(value == 0 for value in deltas.values()),
                    "movedTerms": {k: v for k, v in deltas.items() if v != 0},
                    "captureIsByteDeterministic": reading["deterministic"]
                    and reading["repeatNoise"] == 0,
                    "repeatNoise": reading["repeatNoise"],
                    "changedPixelGeometry": against.get("changedPixelGeometry"),
                })
        verdict[arm.name] = {"identical": identical, "moved": moved, "undecided": undecided}
    return verdict


def summarise(document):
    """Both distances per arm per scene, and the texture-identity verdict.

    Two tables rather than one: the distance to Apple is null on a scene this
    scheme's bed does not hold, and on exactly those scenes the distance to the
    texture-sampled render is the whole measurement.
    """
    for scheme_name, scheme in document["schemes"].items():
        names = [name for name in scheme["armNames"]]
        for field, title in (("deltaEAgainstNative", "ΔE to the native fixture"),
                             ("deltaEAgainstSampledToday", "ΔE to the sampled-today render")):
            print(f"\n{scheme_name} — {scheme['profile']}  ({title}; '—' where there is none)")
            print("  " + "scene".ljust(46) + "".join(n[:13].rjust(15) for n in names))
            for row in scheme["rows"]:
                cells = ""
                for name in names:
                    reading = row["readings"].get(name)
                    value = None if reading is None else reading[field]
                    # A blank column is an arm this phase did not take over this
                    # scene; an em dash is an arm that has no such distance.
                    cells += (" " * 15 if reading is None else
                              "              —" if value is None else f"{value:15.5f}")
                print("  " + row["scene"].ljust(46) + cells)
        for arm, verdict in scheme["textureIdentity"].items():
            moved = (" — " + ", ".join(case["scene"] for case in verdict["moved"])
                     if verdict["moved"] else "")
            print(f"  texture identity {arm}: {len(verdict['identical'])} identical, "
                  f"{len(verdict['moved'])} moved{moved}, "
                  f"{len(verdict['undecided'])} undecided")
            for case in verdict["moved"]:
                notes = [f"NOT byte-identical ({(case['comparedWith'] or '?')[:12]} → "
                         f"{case['sha256'][:12]})"]
                notes.append("every compared term unchanged" if case["measuredTermsUnchanged"]
                             else f"moved terms {case['movedTerms']}")
                if not case["captureIsByteDeterministic"]:
                    notes.append("this cell is not byte-deterministic over two loads, repeat "
                                 f"noise {case['repeatNoise']:.3e}")
                geometry = case["changedPixelGeometry"]
                if geometry is not None and geometry.get("comparable"):
                    notes.append(
                        f"{geometry['changedPixels']} px changed, "
                        f"{geometry['changedInsideDeclaredFootprint']} inside the declared "
                        f"footprint, {geometry['changedOutsideEveryDeclaredShape']} outside every "
                        f"declared shape, max channel difference "
                        f"{geometry['maxChannelDifference']}")
                print(f"    {case['scene']}: " + "; ".join(notes))
        if scheme["capturedWithoutNative"]:
            print(f"  captured without a native reference on this profile: "
                  f"{', '.join(scheme['capturedWithoutNative'])}")
        for noisy in scheme["nonDeterministicCaptures"]:
            print(f"  NOT byte-deterministic over two page loads: {noisy['arm']}/"
                  f"{noisy['scene']}, mean absolute channel difference {noisy['repeatNoise']:.3e}")


METHOD = {
    "geometry": "Every measured region is the DECLARATION, resolved by "
                "scripts/declared-geometry.ts over apps/reference-apple/scenes.json; every "
                "report's measured surface identity, radius and ORIGIN are checked against it, "
                "and the CSS tier's border-box excess is reported once per scheme rather than "
                "tolerated per capture.",
    "requestedAxes": "Each arm's route and authored level are required to be STATED by the "
                     "capture's own report and are checked against the resolved "
                     "configuredSource, samplingBackend and backdropTone. Over a uniform raster "
                     "a sampled tone and a hint taken from it are the same numbers; those groups "
                     "are named undiscriminable rather than asserted.",
    "hint": "The authored level is the level the texture-sampled arm of the SAME phase resolved, "
            "and for every light scene G0 read it is checked against the committed G0 evidence to "
            "the bit. A phase that does not capture that arm inherits the level by BACKGROUND "
            "RASTER from a phase that did — every scene over one raster resolves one level, to "
            "the bit, across components, sizes and both schemes — and a raster no phase measured "
            "stops the run instead of being given a number. levelProvenance names which it was.",
    "deltaEAgainstSampledToday": "Mean Euclidean OKLab distance to the texture-sampled render of "
                                 "the same scene, over the same declared footprint as the native "
                                 "ΔE. It exists wherever that render's pixels do, so it is the "
                                 "measurement on the scenes a colour scheme has no fixture for, "
                                 "and it is a distance between images — never a difference of two "
                                 "native errors. The control is this phase's sampled arm, or G0's "
                                 "scratch snapshot when its PNG digests to the sha256 the "
                                 "committed G0 evidence recorded; otherwise null.",
    "provenance": "Each scheme records the configuration it was CAPTURED with — commit, the "
                  "digest of every runtime source tree under a named scope, and the material "
                  "documents — and a phase whose schemes disagree is refused rather than read as "
                  "one. A reading is never retroactively restated under a wider scope than the "
                  "one it was recorded with.",
    "freshness": "Every capture command clears exactly the scenes it is about to take and is then "
                 "required to have written all three artefacts — PNG, cell and report — after it "
                 "started. A tolerated non-zero exit from compare (a probe arm missing an adopted "
                 "bound) can therefore never be a run whose files came from an earlier attempt.",
    "footprint": "Declared circular rounded-box SDF at pixel centres, visible union; the base "
                 "excludes a covering overlay.",
    "interior": "Declared footprint eroded 6 CSS px; mean and population standard deviation of "
                "per-pixel OKLab L.",
    "deltaE": "Mean Euclidean OKLab distance to the native fixture over the declared visible "
              "footprint, not the full canvas. Null on a scene this colour scheme's native bed "
              "does not hold: those scenes are captured through capture-web directly and are "
              "read against the other arms only.",
    "rim": "Unchanged W23 contour_read: first 2 CSS px, corner factor 1.6; raw linear row mean "
           "and local excess. Empty straight spans are null.",
    "shadow": "Scene-wide count outside ALL declared shapes with background linear luminance "
              ">=0.05 and relative occlusion >0.01. Black pixels are undecidable; a stack "
              "overlay's own exterior shadow cannot be separated from its base's.",
    "identity": "Texture-route arms are compared by PNG digest against the recorded run — the "
                "committed G0 evidence for light, the baseline phase for dark — because W27f's "
                "acceptance is that the sampled path does not move. Byte equality is reported "
                "independently of any attribution: every differing digest is `moved`, and the "
                "character of the difference travels as annotation — whether any compared term "
                "moved with it, whether the cell is byte-deterministic at all, and the measured "
                "count of changed pixels inside and outside the declared masks. Equal aggregate "
                "terms do not locate a difference and are never read as one; only the absence of "
                "anything to compare against is undecidable.",
    "determinism": "Every capture is taken twice from two independent page loads. A cell that "
                   "is not byte-identical over them is listed in nonDeterministicCaptures with "
                   "its mean absolute channel difference and keeps its metrics: its digest "
                   "cannot decide identity and its numbers carry that much noise.",
    "holdout": "The whole declared holdout set is read by the holdout phase alone, once per "
               "frozen configuration, and the spend is recorded at the scratch root. The two "
               "stacked cells are the only ones with a native reading of an overlay; that is what "
               "they answer, not a reason to narrow the set.",
}


# ---------------------------------------------------------------------------


def main():
    default_out = Path(os.environ.get("W27F_G2_OUT", "/tmp/w27f-g2"))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("capture", "read"))
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--out", type=Path, default=default_out)
    parser.add_argument("--schemes", default="light,dark",
                        help="comma-separated: light, dark")
    parser.add_argument("--scenes", default=None,
                        help="comma-separated subset of the phase's declared scenes, for a "
                             "smoke run; a full reading names every scene the bed carries")
    parser.add_argument("--arms", default=",".join(arm.name for arm in ARMS),
                        help="comma-separated arms to capture; a phase whose texture control is "
                             "already established may take fewer, and then authors its hint from "
                             "levels inherited by background raster")
    parser.add_argument("--levels", type=Path, default=None,
                        help="capture: a scene→level file to author hints from, instead of "
                             "measuring or inheriting them")
    parser.add_argument("--compare-phase", choices=PHASES, default=None,
                        help="read: also compare every arm against this phase's reading under "
                             "the same --out. capture: the phase to inherit hint levels from")
    parser.add_argument("--compare-reading", type=Path, default=None,
                        help="read: compare against this reading instead, wherever it lives — "
                             "how a run captured in its own scratch root, on its own frozen "
                             "configuration, is read beside the one it belongs to")
    parser.add_argument("--g0-scratch", type=Path, default=Path("/tmp/w27f-g0/sampled"),
                        help="read: G0's texture-sampled capture tree, used as the sampled-today "
                             "control on light scenes this phase did not sample, and only when a "
                             "PNG digests to the committed G0 evidence's recorded sha256")
    parser.add_argument("--reading", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    args.arms = [name.strip() for name in args.arms.split(",") if name.strip()]
    unknown = [name for name in args.arms if name not in ARMS_BY_NAME]
    if unknown:
        raise SystemExit(f"--arms does not know {unknown}; it takes {list(ARMS_BY_NAME)}")
    if not args.g0_scratch.exists():
        args.g0_scratch = None
    args.schemes = [s.strip() for s in args.schemes.split(",") if s.strip()]
    unknown = [s for s in args.schemes if s not in SCHEMES]
    if unknown:
        raise SystemExit(f"--schemes does not know {unknown}; it takes {sorted(SCHEMES)}")
    if args.scenes is not None:
        args.scenes = [s.strip() for s in args.scenes.split(",") if s.strip()]
    if args.command == "capture":
        capture(args)
    else:
        read(args)


if __name__ == "__main__":
    main()
