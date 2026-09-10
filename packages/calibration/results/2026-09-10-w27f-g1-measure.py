"""W27f G1: the gate's measurement runner — capture the arms, then read them.

G0 measured the page-content path once, with a capture driver that lived in
scratch and a reader that was committed. G1 changes what the unsampled path
draws, so the same measurement has to be taken twice — before the edit and
after it — on two colour schemes, and the two runs have to be the same
measurement. That is what this file is: the capture plan and the reading are
one declaration, so a reading can never describe captures some other
configuration produced.

    python 2026-09-10-w27f-g1-measure.py capture --phase baseline
    python 2026-09-10-w27f-g1-measure.py read    --phase baseline
    #  … the runtime change lands …
    python 2026-09-10-w27f-g1-measure.py capture --phase candidate
    python 2026-09-10-w27f-g1-measure.py read    --phase candidate --compare-phase baseline
    #  … the configuration is frozen, once, at the end …
    python 2026-09-10-w27f-g1-measure.py capture --phase holdout
    python 2026-09-10-w27f-g1-measure.py read    --phase holdout --compare-phase candidate

Everything it writes goes under one scratch root (`--out`, or `W27F_G1_OUT`,
default `/tmp/w27f-g1`). Nothing here writes the canonical matrix or the
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
import socket
import subprocess
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "packages/calibration"
SCENES = ROOT / "apps/reference-apple/scenes.json"
FIXTURES = ROOT / "apps/reference-apple/fixtures"
GEOMETRY = PACKAGE / "scripts/declared-geometry.ts"
G0_READ = PACKAGE / "results/2026-09-10-w27f-g0-read.py"
G0_EVIDENCE = PACKAGE / "results/2026-09-10-w27f-g0-unsampled.json"

_spec = importlib.util.spec_from_file_location("w27f_g0", G0_READ)
g0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g0)

# The sources that decide what the material draws. Digested into every reading's
# header so a number names the code that produced it, not just the profile
# document it was asked to apply — G1 edits the unsampled path in these files,
# and a profile document's `resolvedMaterialSha256` was computed before that.
MATERIAL_SOURCES = [
    "packages/renderer-webgpu/src/material.ts",
    "packages/renderer-webgpu/src/wgsl",
    "packages/platform-web/src/optics.ts",
    "packages/platform-web/src/css-tier.ts",
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

    The calibration phases take the declared calibration set. The holdout phase
    takes the declared holdout scenes whose component is the stacked one: they
    are the only native cells on the page-content path (claims §5.129), and
    naming them here rather than reading them from the split is exactly the
    hard-coding the split exists to prevent.
    """
    split = spec["split"]
    if phase == "holdout":
        component = {s["id"]: s["component"] for s in spec["scenes"]}
        stacked = sorted(i for i in split["holdout"] if "glass-over-glass" in component[i])
        if not stacked:
            raise ValueError("no stacked holdout scene in the declared split")
        return stacked
    return sorted(split["calibration"])


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


def capture_dir(out, phase, scheme, arm, scene):
    return arm_root(out, phase, scheme, arm) / scheme.profile / scene


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


SCENE_SERVER_PORT = 5189


def wait_for_scene_server_port(timeout=1800, poll=10):
    """Block until the scene server's port is free.

    `web/vite.config.ts` binds 5189 with `strictPort`, so two capture runs on
    one machine cannot overlap — and on this machine they routinely try to,
    because sibling worktrees run their own gates. Waiting is the honest
    response: the alternative is a capture that fails for a reason having
    nothing to do with the material, halfway through a sweep.
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


def captured_scenes(out, phase, scheme, arm, scenes):
    return [s for s in scenes
            if (capture_dir(out, phase, scheme, arm, s) / f"{s}__{arm.tier}.png").exists()]


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
    code = run_capture(command, ROOT, log, env)
    captured = captured_scenes(out, phase, scheme, arm, scenes)
    missing = [s for s in scenes if s not in captured]
    if missing:
        raise SystemExit(f"{scheme.name}/{arm.name}: no capture for {missing} (exit {code}); "
                         f"see {log}")
    return {"arm": arm.name, "route": "compare", "exitCode": code, "matrix": str(matrix),
            "log": str(log), "scenes": captured}


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
    code = run_capture(command, PACKAGE, log, env)
    captured = captured_scenes(out, phase, scheme, arm, scenes)
    missing = [s for s in scenes if s not in captured]
    if missing:
        raise SystemExit(f"{scheme.name}/{arm.name}: no direct capture for {missing} "
                         f"(exit {code}); see {log}")
    return {"arm": arm.name, "route": "capture-web", "exitCode": code, "log": str(log),
            "scenes": captured}


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
         "spentBy": "2026-09-10-w27f-g1-measure.py capture --phase holdout",
         "scenes": scenes, **configuration()}, indent=2) + "\n")
    return marker


def git_state():
    """The source tree's commit and dirty paths, where the tree is a checkout.

    A baseline is expected to be captured from a FROZEN COPY of the source —
    `git archive` into scratch — so that the tree cannot move while the run is
    in flight. Such a copy is not a checkout, and the commit it was taken from
    is then supplied as `W27F_G1_SOURCE_COMMIT` rather than invented here. A
    reading that can name neither says so.
    """
    def out(*args):
        return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True,
                              text=True).stdout.strip()
    try:
        return {"sourceRoot": str(ROOT), "commit": out("rev-parse", "HEAD"),
                "dirtyPaths": [line[3:] for line in out("status", "--porcelain").splitlines()]}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"sourceRoot": str(ROOT),
                "commit": os.environ.get("W27F_G1_SOURCE_COMMIT"),
                "dirtyPaths": None,
                "note": "Not a git checkout: a frozen source copy. The commit is whatever "
                        "W27F_G1_SOURCE_COMMIT stated, and null where it stated nothing."}


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
        "materialSourcesSha256": {name: digest(ROOT / name) for name in MATERIAL_SOURCES},
        "materialProfileSha256": {
            scheme.name: digest(scheme.document_path) for scheme in SCHEMES.values()
        },
        "resolvedMaterialSha256": {
            scheme.name: json.loads(scheme.document_path.read_text()).get("resolvedMaterialSha256")
            for scheme in SCHEMES.values()
        },
    }


def capture(args):
    out = args.out
    spec, manifest = scene_spec(), native_manifest()
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
    plan = {"phase": args.phase, "capturedWith": configuration(), "schemes": {}}
    for name in args.schemes:
        scheme = SCHEMES[name]
        refereed, unrefereed = beds[name]
        scenes = refereed + unrefereed
        record = {"profile": scheme.profile, "materialProfile": scheme.document,
                  "scenes": scenes, "nativeRefereed": refereed,
                  "capturedWithoutNative": unrefereed, "arms": []}
        levels_path = phase_dir(out, args.phase) / name / "levels.json"
        for arm in ARMS:
            print(f"  {arm.name} ({arm.tier}, {arm.mode}, hint={arm.hinted})", flush=True)
            runs = []
            if refereed:
                runs.append(run_compare(out, args.phase, scheme, arm, refereed,
                                        levels_path, args.dry_run))
            if unrefereed:
                runs.append(run_direct(out, args.phase, scheme, arm, unrefereed,
                                       levels_path, args.dry_run))
            record["arms"].extend(runs)
            if arm.name == "sampled" and not args.dry_run:
                levels = sampled_levels(out, args.phase, scheme, scenes)
                levels_path.write_text(json.dumps(levels, indent=2) + "\n")
                record["levels"] = levels
                if name == "light":
                    record["levelProvenance"] = check_levels_against_g0(levels)
                print(f"    measured hint levels → {levels_path}")
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


def read_capture(path, arm, scene, background_id, native, surfaces, distances, decidable,
                 background_lum, tint, level, structured, overlay_groups):
    """One arm's PNG under the declared masks, with its report's provenance beside it."""
    data = g0.image(path)
    result = region(data, native, surfaces, distances, range(len(surfaces)))
    result["outerShadowExteriorPixels"] = int((decidable & (
        (background_lum - data[1]) / np.maximum(background_lum, .00001) > .01)).sum())
    result["decidableExteriorPixels"] = int(decidable.sum())
    result["sha256"] = g0.digest(path)
    result["perSurface"] = {s["nodeId"]: region(data, native, surfaces, distances, [i])
                            for i, s in enumerate(surfaces)}
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


COMPARED = ("deltaEAgainstNative", "interiorOklabLMean", "interiorOklabLStddev",
            "rimBandLinearMean", "rimLocalExcessMean", "interiorLinearLuminanceMean",
            "outerShadowExteriorPixels")


def g0_rows():
    return {row["scene"]: row for row in json.loads(G0_EVIDENCE.read_text())["rows"]}


def read(args):
    out = args.out
    phase = args.phase
    manifest_path = phase_dir(out, phase) / "capture-manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"No capture manifest at {manifest_path}. Run `capture --phase {phase}`.")
    captured = json.loads(manifest_path.read_text())
    spec = scene_spec()
    scene_specs = {s["id"]: s for s in spec["scenes"]}
    geometry = g0.declared_geometry()
    g0_evidence = g0_rows()
    before = None
    if args.compare_phase is not None:
        before_path = phase_dir(out, args.compare_phase) / "reading.json"
        if not before_path.exists():
            raise SystemExit(f"No reading at {before_path} to compare against.")
        before = json.loads(before_path.read_text())

    document = {
        "date": "2026-09-10",
        "gate": "W27f G1",
        "phase": phase,
        "captureRoot": str(phase_dir(out, phase).resolve()),
        "capturedWith": captured["capturedWith"],
        "comparePhase": args.compare_phase,
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
            row = {"scene": scene, "hintedBackdropLevel": levels[scene], "surfaces": surfaces,
                   "backgroundSha256": g0.digest(background_path),
                   "nativeFixture": scene in refereed,
                   "nativeSha256": g0.digest(native_path) if scene in refereed else None,
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

            for arm in ARMS:
                path = (capture_dir(out, phase, scheme, arm, scene) /
                        f"{scene}__{arm.tier}.png")
                reading = read_capture(path, arm, scene, declared["backgroundId"], native,
                                       surfaces, distances, decidable, background[1], tint,
                                       levels[scene], structured, overlay_groups)
                if arm.tier == "css":
                    css_excess.add(tuple(reading["measuredBoundsExcess"]))
                if not reading["deterministic"] or reading["repeatNoise"] != 0:
                    noisy.append({"scene": scene, "arm": arm.name,
                                  "repeatNoise": reading["repeatNoise"]})
                # Every arm against the texture-sampled render of the same scene:
                # on a scheme with no native fixture this is the whole of the
                # evidence, and on one with a fixture it is what separates "the
                # page-content path is wrong" from "the material is wrong".
                sampled = row["readings"].get("sampled")
                comparisons = {"vsSampledToday": None if sampled is None or arm.name == "sampled"
                               else delta(reading, sampled, COMPARED)}
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
                            comparisons["vsComparePhase"] = {
                                "phase": args.compare_phase,
                                "pixelIdentical":
                                    prior_reading["sha256"] == reading["sha256"],
                                "sha256": prior_reading["sha256"],
                                **delta(reading, prior_reading, COMPARED),
                            }
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
            "readWith": configuration(),
            "profile": scheme.profile,
            "materialProfile": record["materialProfile"],
            "nativeRefereed": record["nativeRefereed"],
            "capturedWithoutNative": record["capturedWithoutNative"],
            "levels": levels,
            "levelProvenance": record.get("levelProvenance"),
            "cssTierMeasuredSizeExcessCssPx": list(sorted(css_excess)[0]),
            "nonDeterministicCaptures": noisy,
            "textureIdentity": texture_identity(rows),
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
    destination.write_text(json.dumps(g0.clean(document), indent=2, allow_nan=False) + "\n")
    summarise(document)
    print(f"\nreading → {destination}")


def texture_identity(rows):
    """Did the texture-sampled arms draw the same pixels as the recorded run?

    W27f's acceptance is that the sampled path is byte-identical, so this is a
    verdict and not a metric: per texture-route arm, which scenes matched the
    digest they are compared against and which moved. `undecided` is reported
    where there is nothing recorded to compare with — a dark scheme before its
    own baseline exists — rather than counted as a pass.
    """
    verdict = {}
    for arm in ARMS:
        if not arm.texture:
            continue
        identical, moved, undecided = [], [], []
        for row in rows:
            comparisons = row["readings"][arm.name]["comparisons"]
            against = comparisons["vsComparePhase"] or comparisons["vsG0"]
            if against is None:
                undecided.append(row["scene"])
            elif against["pixelIdentical"]:
                identical.append(row["scene"])
            else:
                moved.append(row["scene"])
        verdict[arm.name] = {"identical": identical, "moved": moved, "undecided": undecided}
    return verdict


def summarise(document):
    """The per-scene native ΔE per arm, and the texture-identity verdict."""
    for scheme_name, scheme in document["schemes"].items():
        names = [arm.name for arm in ARMS]
        print(f"\n{scheme_name} — {scheme['profile']}  (ΔE to the native fixture; "
              f"'—' where this scheme has none)")
        print("  " + "scene".ljust(46) + "".join(n[:13].rjust(15) for n in names))
        for row in scheme["rows"]:
            cells = "".join(
                "              —" if row["readings"][n]["deltaEAgainstNative"] is None
                else f"{row['readings'][n]['deltaEAgainstNative']:15.5f}" for n in names)
            print("  " + row["scene"].ljust(46) + cells)
        for arm, verdict in scheme["textureIdentity"].items():
            moved = f" — {', '.join(verdict['moved'])}" if verdict["moved"] else ""
            print(f"  texture identity {arm}: {len(verdict['identical'])} identical, "
                  f"{len(verdict['moved'])} moved{moved}, "
                  f"{len(verdict['undecided'])} undecided")
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
    "hint": "The authored level is the level the texture-sampled arm of the SAME phase "
            "resolved, and for every light scene G0 read it is checked against the committed "
            "G0 evidence to the bit.",
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
                "acceptance is that the sampled path does not move.",
    "determinism": "Every capture is taken twice from two independent page loads. A cell that "
                   "is not byte-identical over them is listed in nonDeterministicCaptures with "
                   "its mean absolute channel difference and keeps its metrics: its digest "
                   "cannot decide identity and its numbers carry that much noise.",
    "holdout": "The two stacked holdout cells are read by the holdout phase alone, once per "
               "frozen configuration, and the spend is recorded at the scratch root.",
}


# ---------------------------------------------------------------------------


def main():
    default_out = Path(os.environ.get("W27F_G1_OUT", "/tmp/w27f-g1"))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("capture", "read"))
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--out", type=Path, default=default_out)
    parser.add_argument("--schemes", default="light,dark",
                        help="comma-separated: light, dark")
    parser.add_argument("--scenes", default=None,
                        help="comma-separated subset of the phase's declared scenes, for a "
                             "smoke run; a full reading names every scene the bed carries")
    parser.add_argument("--compare-phase", choices=PHASES, default=None,
                        help="read: also compare every arm against this phase's reading")
    parser.add_argument("--reading", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
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
