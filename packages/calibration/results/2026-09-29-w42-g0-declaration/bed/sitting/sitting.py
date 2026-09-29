#!/usr/bin/env python3.12
"""W42 sitting driver (charter clauses 4-5, G1; X6 as carried; X5 for the W42 bed only).

Derived from W39 G0's sitting.py (§5.184, with W39 G1's two gate corrections, §5.185),
never edited in place. It keeps W39's protocol: the pinned side bundle only, explicit roots
outside every checkout, the macOS 27.0 / 26A428 gate, the machine read before and after
every run with drift refused, independent HID idle, zero foreign capture processes (by
name, Google Chrome and Playwright included), per-capture hidIdleSeconds >= 60 as an
admission check, pose / window-frame / supplied-path attestation, and a failed run
QUARANTINED under a new name, never retried or overwritten. What W42 changes:

- The passes are pass-spec.py's: the DUMP STEP first (one `dump-layers` launch per
  (scale, scheme, pose) over bed.json's dumpList, each checked by ../dumps/dumpcheck.py;
  a departure from memo D's declared configuration stops the sitting before its first
  capture, clause 4), then the four 2x passes (7 runs), their long-protocol sentinels (3
  runs), the four 1x passes and their sentinels. One profile per pass. No preflight.
- Every run, dump launches included, first WAITS (bounded, logged) for >= 75 s of HID idle
  and no permission prompt; waiting is not a retry. Then every gate is read and judged.
- The shapes are placed by integer `offset` (never `position`): the attested frameOrigin
  must equal the centred frame plus the offset exactly.
- The long protocol is settle 8 s with W42's own order seed, 4242.
- `plan` is the dry mode: it writes every derived scenes document and every launch argv
  of the whole sitting and executes NOTHING (no machine read, no launcher, no harness).
  There is still no harness `--dry-run` path (W39: it never reaches ScreenCaptureKit, so it
  proves nothing about the grant); the TCC-refusal rehearsal is `--rehearse-refusal`, the
  real run-1 launch of an ungranted bundle, and is G1's first runbook step.

The fixes of the bed review of b151aff4 (the parent's dispositions):

- B-M1: before any launch the bed must be the pinned declaration (`pinned_declaration`):
  bed/wave.py's Wave checks scenes-w42-body.json and bed.json against pins.json, both files
  must equal their committed copies at HEAD, and declaration.json, committed and hashed by
  declaration.sha256, must name both SHA-256s. Every admission carries both SHA-256s; an
  admission naming others is not admitted, so no later pass can build on it, and the archive
  producer refuses it. `pin-check` is the same check for the orchestrator's start.
- b2: a capture run is admitted only if every fixture PNG the manifest names exists inside the
  run and decodes at the declared pixel size; admission.json records each frame's SHA-256
  (held-out cells as one digest, so no per-run H state frequency is published) and the
  archive producer compares them.
- b4: a launch happens only under the orchestrator (W42_ORCHESTRATED), whose trap restores
  the display mode on every exit; the refusal and dump rehearsals run through it too.
- b6: the receded passes no longer run `rehearse-tints` (no W42 cell is tinted, and it read
  the main checkout's canonical fixture manifest).
- `dump K --rehearse` is the pre-sitting dump rehearsal (G0's b7): the real launch and
  dumpcheck in a rehearsal root, never evidence, with the foreign-process census RECORDED
  rather than enforced, as G0's no-pixel dumps did; the evidence dumps still enforce it.
- W42_PREDECLARATION=1 is for rehearsals before the declaration is re-pinned and hashed: the
  pins and HEAD checks hold, the declaration's state is recorded, only rehearsals launch.

Capture logs and manifests can carry holdout-role cells' diagnostics and stay producer-only
under the raw root until the archive producer files them: redacted for H under operational/,
whole under holdout/operational/, readable only through the receipt (B-M2).
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
BED_DIR = HERE.parent
REPO = HERE.parents[5]
MAIN = Path('/Users/new/Developer/GitHub/designer')
W39_PIN = REPO / 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/bundle-pin.json'
DECLARATION = BED_DIR.parent / 'declaration.json'
DECLARATION_DIGEST = BED_DIR.parent / 'declaration.sha256'
PREDECLARATION_ENV = 'W42_PREDECLARATION'      # rehearsals before the declaration is hashed only
ORCHESTRATED_ENV = 'W42_ORCHESTRATED'          # set by sitting-orchestrate.sh around every launch

OS_VERSION, OS_BUILD = '27.0', '26A428'
SETTINGS = {'reduceTransparency': '0', 'increaseContrast': '0', 'NSGlassTintAmount': '0.5',
            'ButtonShapesEnabled': '0'}
SCREEN = '7709FD0F-F423-4277-B0C8-7CA94F85723A'
MIN_IDLE_SECONDS = 60            # the harness's per-capture floor and the admission check
WAIT_IDLE_SECONDS = 75           # what every launch waits for first (W39 G1's orchestrator)
IDLE_WAIT_LIMIT = 3 * 3600       # a bounded wait; exceeding it refuses the run
IDLE_POLL_SECONDS = 15
SRGB = 'kCGColorSpaceSRGB'
FRAME_SPACE = 'appkit-global-bottom-left'
PROTOCOLS = {
    'normal': dict(initialSettleSeconds=1.75, orderSeed=None, resetInterstitialSeconds=6.0,
                   resetCarriesGlass=False, minIdleSeconds=float(MIN_IDLE_SECONDS)),
    'long': dict(initialSettleSeconds=8.0, orderSeed=4242, resetInterstitialSeconds=6.0,
                 resetCarriesGlass=False, minIdleSeconds=float(MIN_IDLE_SECONDS)),
}
TCC_GATE = 'This is the Screen Recording (TCC) gate'
REHEARSAL_TIMEOUT = 180
PROMPT_OWNERS = ('universalAccessAuthWarn',)

_PIN = None
_MODULES = {}


def module(name, path):
    if name not in _MODULES:
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _MODULES[name] = m
    return _MODULES[name]


def pass_spec():
    return module('w42_pass_spec', HERE / 'pass-spec.py')


def dumpcheck():
    return module('w42_dumpcheck', BED_DIR / 'dumps/dumpcheck.py')


def wave_module():
    return module('w42_wave_for_sitting', BED_DIR / 'wave.py')


def pin():
    global _PIN
    if _PIN is None:
        _PIN = json.loads(W39_PIN.read_text())
    return _PIN


# ----------------------------------------------------------------- machine facts

def configuration(m):
    signature = m['side'].get('signature', {}).get('stderr', '')
    cd = re.search(r'^CDHash=(.+)$', signature, re.M)
    mode = re.findall(r'^  mode (\d+):.*<-- current mode$', m['display']['stdout'], re.M)
    return dict(os=m['os']['stdout'], settings={k: v['stdout'] for k, v in m['settings'].items()},
                mode=mode,
                displayIdentity=re.findall(r'^Persistent screen id: (.+)$', m['display']['stdout'], re.M),
                colour=m['displayColourContext']['stdout'], binary=m['side'].get('binarySha256'),
                cdhash=cd[1] if cd else None, build=m['side'].get('buildVersion', {}).get('stdout'))


def validate_machine(m, scale, census=True):
    """Every gate, strictly, and every failing one named in ONE refusal. `census=False` only for
    the pre-sitting dump rehearsal, which records the foreign-process census instead."""
    c = configuration(m)
    problems = []
    if not re.search(rf'ProductVersion:\s+{re.escape(OS_VERSION)}\s', c['os']) or OS_BUILD not in c['os']:
        problems.append(f'OS version/build is not the declared {OS_VERSION} / {OS_BUILD}')
    if c['settings'] != SETTINGS:
        problems.append(f'policy/slider/Show Borders mismatch: {c["settings"]}')
    mode = pass_spec().MODES[scale]
    if c['mode'] != [mode] or c['displayIdentity'] != [SCREEN]:
        problems.append(f'display mode/identity mismatch for {scale}x (want mode {mode}): '
                        f'{c["mode"]} {c["displayIdentity"]}')
    p = pin()
    build = (c['build'] or '').strip()
    if (c['binary'], c['cdhash'], build) != (p['binarySha256'], p['cdhash'], p['buildVersion'].strip()):
        problems.append('side bundle identity changed (binary, cdhash or LC_BUILD_VERSION); '
                        'a rebuild is a new pin and a new grant')
    if census and m['foreignProcessCount'] != 0:
        problems.append(f'{m["foreignProcessCount"]} foreign capture process(es); X6 admits none')
    if problems:
        raise ValueError('machine gate refused: ' + '; '.join(problems))
    return c


def session_problems(observed, need=MIN_IDLE_SECONDS):
    problems = []
    idle = observed.get('idleSeconds')
    if not isinstance(idle, (int, float)) or idle < need:
        problems.append(f'no launch: {need}s of HID idle required, read {idle}')
    if observed.get('screenLocked') is not False:
        problems.append('no launch: the session must read unlocked (an unreadable lock is not unlocked)')
    owners = observed.get('windowOwners')
    if owners is None:
        problems.append('no launch: the on-screen window owners are unreadable')
    else:
        prompts = [o for o in owners if o.split('|')[0] in PROMPT_OWNERS]
        if prompts:
            problems.append(f'no launch: a permission prompt is on screen ({prompts}); answer nothing, '
                            'and resolve it before any capture')
    return problems


def wait_for_idle(read, log, need=WAIT_IDLE_SECONDS, limit=IDLE_WAIT_LIMIT, poll=IDLE_POLL_SECONDS,
                  sleep=time.sleep, clock=time.monotonic):
    """Wait, bounded, until the session reads `need` s of HID idle, unlocked, no prompt.

    Waiting before a launch is not a retry: nothing has run. A permission prompt stops the
    wait at once (nobody clicks it); exceeding `limit` refuses the run.
    """
    start = clock()
    while True:
        observed = read()
        idle = observed.get('idleSeconds')
        owners = observed.get('windowOwners') or []
        log(f'idle-wait: idle={idle} locked={observed.get("screenLocked")} owners={len(owners)}')
        if any(o.split('|')[0] in PROMPT_OWNERS for o in owners):
            raise ValueError('a permission prompt is on screen; answer nothing and stop')
        if not session_problems(observed, need):
            return observed
        if clock() - start >= limit:
            raise ValueError(f'HID idle never reached {need}s within {limit}s; the run is not launched')
        sleep(poll)


# ------------------------------------------------------------ the declaration

def at_head(path):
    """The file's bytes, refusing unless they equal its committed copy at HEAD."""
    path = Path(path)
    raw = path.read_bytes()
    shown = subprocess.run(['git', '-C', str(path.parent), 'show', f'HEAD:./{path.name}'], capture_output=True)
    if shown.returncode != 0:
        raise ValueError(f'{path.name} is not committed at HEAD')
    if shown.stdout != raw:
        raise ValueError(f'{path.name} differs from its committed copy at HEAD')
    return raw


def pinned_declaration(predeclaration=False):
    """The bed every launch captures is the declared one (clause 1's stop; the bed review's B-M1).

    Returns the record every admission carries. Refuses unless bed/wave.py's Wave accepts the
    scenes file and bed.json against pins.json, both equal their committed copies at HEAD, and
    declaration.json, committed and hashed (declaration.sha256, committed), names both SHA-256s
    in its `split` item. `predeclaration` keeps every check but the declaration's, whose state is
    recorded instead; the driver then launches rehearsals only, and the producer refuses it.
    """
    try:
        wave = wave_module().Wave()
    except ValueError as error:
        raise ValueError(f'refused before any launch: the bed is not its pins ({error})') from None
    problems = []
    for path in (wave.scenes_path, wave.split_path):
        try:
            at_head(path)
        except (ValueError, OSError) as error:
            problems.append(str(error))
    head = subprocess.run(['git', '-C', str(BED_DIR), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    record = dict(scenesSha256=wave.scenes_sha, splitSha256=wave.split_sha, head=head.stdout.strip() or None)
    stated = []
    try:
        raw = at_head(DECLARATION)
        record['declarationSha256'] = hashlib.sha256(raw).hexdigest()
        split = next(i['declared'] for i in json.loads(raw)['items'] if i.get('id') == 'split')
        named = (split.get('scenesSha256'), split.get('splitSha256'))
        if named != (wave.scenes_sha, wave.split_sha):
            stated.append(f'declaration.json names scenes {str(named[0])[:12]} and bed {str(named[1])[:12]}; '
                          f'the files are {wave.scenes_sha[:12]} and {wave.split_sha[:12]}')
        digest = at_head(DECLARATION_DIGEST).decode().split()
        if not digest or digest[0] != record['declarationSha256']:
            stated.append('declaration.sha256 does not name this declaration.json')
    except (ValueError, OSError, KeyError, StopIteration, UnicodeDecodeError, json.JSONDecodeError) as error:
        stated.append(f'the declaration is not committed and hashed: {type(error).__name__}: {error}')
    if predeclaration:
        record.update(predeclaration=True, declarationProblems=stated)
    else:
        problems += stated
    if problems:
        raise ValueError('refused before any launch: the bed is not the pinned declaration: ' + '; '.join(problems))
    return record


def declared_by(admission, declaration):
    """An admission counts only under the declaration the sitting runs on, and never a rehearsal's."""
    return (admission.get('scenesSha256') == declaration['scenesSha256']
            and admission.get('splitSha256') == declaration['splitSha256']
            and not admission.get('predeclaration'))


def holdout_digest(frames):
    return hashlib.sha256(json.dumps(frames, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def frame_binding(run, manifest, doc, scale):
    """b2: every fixture PNG exists inside the run and decodes at the declared pixel size.

    Returns the SHA-256 of each non-holdout frame and ONE digest over the held-out frames
    (admission.json is published with the G1 evidence; per-run H frame hashes would publish
    H's state frequencies, which W39 G1 kept behind the receipt)."""
    from PIL import Image
    roles = {sid: role for role, ids in doc['split'].items() for sid in ids}
    size = (doc['canvas']['width'] * scale, doc['canvas']['height'] * scale)
    root = run.resolve()
    frames, held = {}, {}
    for profile in manifest['profiles']:
        for f in profile['fixtures']:
            cell = profile['profileKey'] + '/' + f['sceneId']
            path = (run / f['file']).resolve()
            if root not in path.parents or not path.is_file() or path.is_symlink():
                raise ValueError('fixture PNG missing or outside its run: ' + cell)
            raw = path.read_bytes()
            try:
                with Image.open(io.BytesIO(raw)) as image:
                    image.load()
                    ok = image.format == 'PNG' and image.size == size and image.mode in ('RGB', 'RGBA')
            except Exception as error:
                raise ValueError(f'fixture PNG does not decode: {cell} ({error})') from None
            if not ok:
                raise ValueError(f'fixture PNG is not an RGB(A) PNG of {size[0]}x{size[1]}: {cell}')
            digest = hashlib.sha256(raw).hexdigest()
            (held if roles.get(f['sceneId']) == 'holdout' else frames)[cell] = digest
    return dict(frames=frames, holdoutFrames=dict(count=len(held), sha256=holdout_digest(held)))


# ------------------------------------------------------------------- the passes

def started(directory):
    return directory.is_dir() and any(c.name.startswith(('run-', 'QUARANTINE-')) for c in directory.iterdir())


def protocol_of_pass(p):
    return {'dump': 'dump', 'bed': 'normal', 'sentinel': 'long'}[p['kind']]


def admitted(root, p, n, declaration):
    path = root / p['name'] / f'run-{n}' / 'admission.json'
    if not path.is_file():
        return False
    a = json.loads(path.read_text())
    return (a.get('admitted') is True and a.get('pass') == p['name'] and a.get('run') == n
            and a.get('protocol') == protocol_of_pass(p) and declared_by(a, declaration))


def check_order(root, p, run, bed, declaration):
    """Every run of every earlier pass admitted, no later pass started, and within the pass
    runs 1..run-1 admitted: the dumps precede every capture by construction."""
    order = pass_spec().pass_order(bed)
    later = [q['name'] for q in order if q['rank'] > p['rank'] and started(root / q['name'])]
    if later:
        raise ValueError(f'{p["name"]} refused: a later pass has already started ({later})')
    missing = [f'{q["name"]} run {k}' for q in order if q['rank'] < p['rank']
               for k in range(1, q['runs'] + 1) if not admitted(root, q, k, declaration)]
    if missing:
        raise ValueError(f'{p["name"]} refused: an earlier pass is not complete; not admitted: {missing}')
    missing = [k for k in range(1, run) if not admitted(root, p, k, declaration)]
    if missing:
        raise ValueError(f'{p["name"]} run {run} refused: earlier run(s) {missing} of this pass are not '
                         'admitted; a quarantined or interrupted run blocks its successors until the '
                         'operator takes it again deliberately')


# ------------------------------------------------------------------ attestation

def shapes(component):
    if component['kind'] == 'none':
        return []
    return component['items'] if component['kind'] == 'column' else [component]


def declared_origin(shape, canvas):
    """ShapeSpec.frame(in:): position - size/2, else centred + offset (the W42 bed: offset)."""
    w, h = shape['size']
    if shape.get('position') is not None:
        return [shape['position'][0] - w / 2, shape['position'][1] - h / 2]
    dx, dy = shape.get('offset') or [0, 0]
    return [(canvas['width'] - w) / 2 + dx, (canvas['height'] - h) / 2 + dy]


def validate_manifest(m, doc, pose, scale, label):
    expected = {(p['key'], s) for p in doc['profiles'] for s in p['scenes']}
    actual = {(p['profileKey'], f['sceneId']) for p in m['profiles'] for f in p['fixtures']}
    if actual != expected:
        raise ValueError(f'capture membership is incomplete or unexpected: '
                         f'{len(expected - actual)} missing, {len(actual - expected)} extra')
    if m['hardware']['osBuild'] != OS_BUILD:
        raise ValueError('captured OS build mismatch')
    if (m.get('captureProtocol') or {}).get('runLabel') != label:
        raise ValueError('run label mismatch')
    canvas = doc['canvas']
    pixels = [canvas['width'] * scale, canvas['height'] * scale]
    scenes = {s['id']: s for s in doc['scenes']}
    for profile in m['profiles']:
        d = profile['display']
        if d['actualBackingScale'] != scale or d['requestedScale'] != scale or d['pixelSize'] != pixels:
            raise ValueError('captured backing scale / pixel size mismatch')
        if d['colorSpace'] != SRGB:
            raise ValueError(f'capture colour space is {d["colorSpace"]}, not sRGB')
        for f in profile['fixtures']:
            sid = f['sceneId']
            if f['captureMethod'] != 'screencapturekit' or not f['materialRendered'] or not f.get('deterministic'):
                raise ValueError('material/repeat attestation failed: ' + sid)
            if [f['width'], f['height']] != pixels:
                raise ValueError('fixture pixel size mismatch: ' + sid)
            if f.get('presentedActive') != (pose == 'active'):
                raise ValueError('pose attestation failed: ' + sid)
            idle = f.get('hidIdleSeconds')
            if not isinstance(idle, (int, float)) or idle < MIN_IDLE_SECONDS:
                raise ValueError(f'per-capture HID idle failed: {sid} recorded {idle}; '
                                 f'{MIN_IDLE_SECONDS}s required on every capture')
            if pose == 'receded':
                p = f.get('presentation') or {}
                if p.get('observedPose') != 'inactive' or p.get('isKeyWindow') is not False \
                        or p.get('appIsActive') is not False:
                    raise ValueError('inactive presentation fields failed: ' + sid)
            frame = f.get('windowFrame')
            if not frame:
                raise ValueError('no window frame attestation: ' + sid)
            if frame.get('coordinateSpace') != FRAME_SPACE or frame.get('actual') != frame.get('requested') \
                    or frame.get('backingScaleFactor') != scale \
                    or list(frame['requested'][2:]) != [canvas['width'], canvas['height']]:
                raise ValueError(f'window frame attestation failed: {sid} {frame}')
            want = shapes(doc['components'][scenes[sid]['component']])
            got = f.get('suppliedPaths') or []
            if len(got) != len(want):
                raise ValueError('supplied path count mismatch: ' + sid)
            for shape, path in zip(want, got):
                origin = declared_origin(shape, canvas)
                if any(abs(a - b) > 1e-9 for a, b in zip(path['frameOrigin'], origin)) \
                        or list(path['rect'][2:]) != list(shape['size']) \
                        or bool(path['opaque']) != bool(shape.get('opaque')):
                    raise ValueError(f'supplied path attestation failed: {sid} {path["frameOrigin"]} '
                                     f'!= declared {origin}')


def launch_settings(argv):
    args = argv[argv.index('--args') + 1:] if '--args' in argv else list(argv)

    def value(flag):
        if args.count(flag) > 1:
            raise ValueError(f'{flag} is given twice in the launch')
        return args[args.index(flag) + 1] if flag in args else None

    settle, seed = value('--initial-settle'), value('--order-seed')
    reset, idle = value('--reset-interstitial'), value('--min-idle-seconds')
    return dict(initialSettleSeconds=1.75 if settle is None else float(settle),
                orderSeed=None if seed is None else int(seed),
                resetInterstitialSeconds=None if reset is None else float(reset),
                resetCarriesGlass='--reset-glass' in args,
                minIdleSeconds=None if idle is None else float(idle))


def launch_protocol(argv):
    settings = launch_settings(argv)
    found = [name for name, want in PROTOCOLS.items() if settings == want]
    if len(found) != 1:
        raise ValueError(f'the launch settings {settings} are neither declared protocol')
    return found[0]


def protocol_argv(protocol):
    p = PROTOCOLS[protocol]
    out = ['--reset-interstitial', f'{p["resetInterstitialSeconds"]:g}',
           '--min-idle-seconds', f'{p["minIdleSeconds"]:g}']
    if p['initialSettleSeconds'] != PROTOCOLS['normal']['initialSettleSeconds']:
        out += ['--initial-settle', f'{p["initialSettleSeconds"]:g}']
    if p['orderSeed'] is not None:
        out += ['--order-seed', str(p['orderSeed'])]
    return out


def run_admission(p, n, argv, manifest, manifest_sha, cells, declaration, binding):
    protocol = launch_protocol(argv)
    if protocol != protocol_of_pass(p):
        raise ValueError(f'{p["name"]} launched the {protocol} protocol; the pass is {protocol_of_pass(p)}')
    settings = PROTOCOLS[protocol]
    recorded = manifest.get('captureProtocol') or {}
    got = {k: recorded.get(k) for k in settings}
    if got != settings:
        raise ValueError(f'manifest captureProtocol {got} is not the launched {protocol} protocol {settings}')
    if declaration.get('predeclaration'):
        raise ValueError('a capture is never admitted before the declaration is hashed')
    if len(binding['frames']) + binding['holdoutFrames']['count'] != cells:
        raise ValueError('the frame binding does not cover every admitted cell')
    return dict(schema='w42-run-admission-2', admitted=True, dry=False, protocol=protocol,
                captureProtocol=dict(settings), cells=cells, manifestSha256=manifest_sha, run=n,
                scenesSha256=declaration['scenesSha256'], splitSha256=declaration['splitSha256'],
                declaration=declaration, frames=binding['frames'], holdoutFrames=binding['holdoutFrames'],
                **{'pass': p['name'], 'key': p['key']})


def classify_refusal(run, before, after, timed_out):
    """The rehearsal's outcome. Only 'refused-tcc' is the expected evidence (W39, unchanged)."""
    out = (run / 'producer-capture.out').read_text() if (run / 'producer-capture.out').exists() else ''
    err = (run / 'producer-capture.err').read_text() if (run / 'producer-capture.err').exists() else ''
    fixtures = [str(q.relative_to(run)) for q in run.rglob('*.png') if q.relative_to(run).parts[0] != 'backgrounds']
    staging = [q.name for q in run.glob('.staging-*')]
    appeared = sorted(set((after or {}).get('windowOwners') or []) - set((before or {}).get('windowOwners') or []))
    facts = dict(timedOut=timed_out, manifestPublished=(run / 'manifest.json').exists(),
                 fixturePngs=fixtures, stagingLeft=staging, newWindowOwners=appeared,
                 captureAttempted=bool(re.search(r'^capturing \d+ fixtures via screencapturekit', out, re.M)),
                 tccGateText=TCC_GATE in err, errSha256=hashlib.sha256(err.encode()).hexdigest(),
                 errFirstLine=err.splitlines()[0] if err else None)
    if facts['manifestPublished'] or fixtures:
        outcome = 'captured'
    elif timed_out or appeared or any(o.split('|')[0] in PROMPT_OWNERS for o in (after or {}).get('windowOwners') or []):
        outcome = 'prompt-pending'
    elif facts['tccGateText'] and facts['captureAttempted'] and not staging:
        outcome = 'refused-tcc'
    else:
        outcome = 'refused-other'
    return dict(outcome=outcome, **facts)


# ------------------------------------------------------------------ launch pieces

def tool(name, default):
    return shlex.split(os.environ.get(name, default))


def inside(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def outside_repository(path):
    path = Path(path).expanduser().resolve()
    for forbidden in (REPO, MAIN, Path.home() / 'Documents', Path.home() / 'Desktop', Path.home() / 'Downloads'):
        if path == forbidden.resolve() or inside(path, forbidden.resolve()):
            raise ValueError(f'{path} is inside {forbidden}: sitting output lives outside every checkout and '
                             'outside Documents/Desktop/Downloads (W39 G1\'s Files-and-Folders prompt)')
    return path


def write_doc(passdir, name, doc):
    spec = passdir / name
    encoded = json.dumps(doc, indent=2) + '\n'
    if spec.exists() and spec.read_text() != encoded:
        raise ValueError(f'existing declaration {spec} differs')
    if not spec.exists():
        spec.write_text(encoded)
    return spec


def capture_argv(launcher, app, spec, run, scale, label, protocol, ids, pose):
    command = [*launcher]
    for key, value in (('VITREA_SCENES', spec), ('VITREA_FIXTURES', run), ('VITREA_SCALE', scale)):
        command += ['--env', f'{key}={value}']
    command += ['--stdout', str(run / 'producer-capture.out'), '--stderr', str(run / 'producer-capture.err'),
                str(app), '--args', 'capture', '--run-label', label, *protocol_argv(protocol),
                '--scenes', ','.join(ids)]
    if pose == 'receded':
        command += ['--inactive']
    return command


def dump_argv(launcher, app, spec, run, scale, scheme, pose, ids):
    command = [*launcher]
    for key, value in (('VITREA_SCALE', scale), ('VITREA_SCENES', spec), ('VITREA_FIXTURES', run / 'no-fixtures')):
        command += ['--env', f'{key}={value}']
    command += ['--stdout', str(run / 'dump.out'), '--stderr', str(run / 'dump.err'), str(app), '--args',
                'dump-layers', '--scenes', ','.join(ids), '--settle', str(pass_spec().DUMP_SETTLE),
                '--scheme', scheme, '--inactive' if pose == 'receded' else '--require-key',
                '--out', str(run / 'json')]
    return command


def dump_timeout(n):
    """memo D's run-one.sh overrun bound: n (settle + 1.5) + 90 s."""
    return int(n * (pass_spec().DUMP_SETTLE + 1.5) + 90)


# ------------------------------------------------------------------------ plan

def dry_plan(out=None, root='<VITREA_SITTING_DIR>', app=None):
    """Walk the whole sitting and describe every launch; execute nothing."""
    P = pass_spec()
    spec_doc, bed = P.load()
    app = app or pin()['path']
    launcher = ['open', '-W']
    root = Path(root)
    passes = []
    for p in P.pass_order(bed):
        scale, scheme, pose = P.endpoint(p['key'])
        runs = []
        for n in range(1, p['runs'] + 1):
            run = root / p['name'] / f'run-{n}'
            if p['kind'] == 'dump':
                ids = P.dump_ids(p['key'])
                profile = next(x for x in spec_doc['profiles'] if x['key'] == bed['passes'][p['key']]['profile'])
                doc = P.subset(spec_doc, ids, profile)
                argv = dump_argv(launcher, app, root / p['name'] / 'scenes-dump.json', run, scale, scheme, pose, ids)
                runs.append(dict(run=n, scenes=len(ids), timeoutSeconds=dump_timeout(len(ids)), argv=argv))
                name = 'scenes-dump.json'
            else:
                protocol = protocol_of_pass(p)
                doc = P.derive(p['key'], n, p['kind'] == 'sentinel')
                ids = sorted(s['id'] for s in doc['scenes'])
                label = f'w42-{p["name"]}-{n}'
                argv = capture_argv(launcher, app, root / p['name'] / f'scenes-run-{n}.json', run, scale, label,
                                    protocol, ids, pose)
                refs = sum(1 for s in ids if s.startswith('ref-'))
                runs.append(dict(run=n, cells=len(ids), glass=len(ids) - refs, references=refs, protocol=protocol,
                                 label=label, argv=argv))
                name = f'scenes-run-{n}.json'
            if out is not None:
                d = Path(out) / p['name']
                d.mkdir(parents=True, exist_ok=True)
                (d / name).write_text(json.dumps(doc, indent=2) + '\n')
                (d / f'launch-run-{n}.json').write_text(json.dumps(runs[-1]['argv'], indent=2) + '\n')
        passes.append(dict(name=p['name'], kind=p['kind'], mode=p['mode'], scale=scale, scheme=scheme, pose=pose,
                           runs=runs))
    totals = dict(dumpLaunches=sum(len(p['runs']) for p in passes if p['kind'] == 'dump'),
                  dumpScenes=sum(r['scenes'] for p in passes if p['kind'] == 'dump' for r in p['runs']),
                  captureLaunches=sum(len(p['runs']) for p in passes if p['kind'] != 'dump'),
                  glass=sum(r['glass'] for p in passes if p['kind'] == 'bed' for r in p['runs']),
                  references=sum(r['references'] for p in passes if p['kind'] == 'bed' for r in p['runs']),
                  sentinels=sum(r['cells'] for p in passes if p['kind'] == 'sentinel' for r in p['runs']))
    totals['captures'] = totals['glass'] + totals['references'] + totals['sentinels']
    value = dict(schema='w42-sitting-plan-1', executed=False,
                 note='nothing was launched, read or captured; argv paths are under the placeholder root',
                 root=str(root), passes=passes, totals=totals)
    if out is not None:
        (Path(out) / 'plan.json').write_text(json.dumps(value, indent=2) + '\n')
    return value


# ------------------------------------------------------------------------ main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    pl = sub.add_parser('plan', help='the dry mode: every document and argv of the sitting; executes nothing')
    pl.add_argument('--out', type=Path, help='a new directory outside the repository for the documents')
    d = sub.add_parser('dump', help='the one dump-layers launch of dump pass dump-<key>')
    d.add_argument('key')
    d.add_argument('--rehearse', action='store_true',
                   help='the pre-sitting dump rehearsal: the real launch and dumpcheck in a rehearsal root, '
                        'never evidence; the foreign-process census is recorded, not enforced')
    c = sub.add_parser('capture', help='runs first..last of a bed or sentinel pass')
    c.add_argument('key')
    c.add_argument('first', type=int, nargs='?', default=1)
    c.add_argument('last', type=int, nargs='?')
    c.add_argument('--sentinel', action='store_true')
    c.add_argument('--rehearse-refusal', action='store_true',
                   help='G1 step 1: the real run-1 launch from the ungranted bundle, expected TCC-refused')
    w = sub.add_parser('wait-idle', help='wait (bounded, logged) for N s of HID idle; used before a mode switch')
    w.add_argument('seconds', type=float)
    sub.add_parser('pin-check', help='the pre-launch declaration check (B-M1), as the orchestrator runs it first')
    args = ap.parse_args(argv)
    if 'DRY' in os.environ:
        ap.error('DRY is W34\'s harness --dry-run, which never reaches ScreenCaptureKit. W42 has no such path: '
                 'the dry mode is `plan`, and the TCC rehearsal is `capture --rehearse-refusal`.')
    predeclaration = os.environ.get(PREDECLARATION_ENV) == '1'
    if args.action == 'pin-check':
        print(json.dumps(pinned_declaration(predeclaration), indent=2))
        return
    if args.action == 'plan':
        if args.out is not None:
            outside_repository(args.out)
            if args.out.exists():
                raise ValueError('plan output exists; keep it and name a new directory')
        value = dry_plan(args.out)
        print(json.dumps(dict(totals=value['totals'], passes=len(value['passes'])), indent=2))
        return
    if args.action == 'wait-idle':
        session = tool('VITREA_SESSION_READER', str(Path.home() / 'vitrea-w39/scratch/read-session'))
        wait_for_idle(lambda: json.loads(subprocess.check_output(session, text=True)),
                      lambda line: print(line, flush=True), need=args.seconds,
                      limit=float(os.environ.get('VITREA_IDLE_LIMIT', IDLE_WAIT_LIMIT)),
                      poll=float(os.environ.get('VITREA_IDLE_POLL', IDLE_POLL_SECONDS)))
        return
    if 'VITREA_SITTING_DIR' not in os.environ:
        ap.error('VITREA_SITTING_DIR must name the sitting root explicitly (outside the repository)')
    rehearsal = (args.action == 'capture' and args.rehearse_refusal) or (args.action == 'dump' and args.rehearse)
    if os.environ.get(ORCHESTRATED_ENV) != '1':
        ap.error('every launch runs under sitting-orchestrate.sh, whose trap restores the display mode on every '
                 'exit, rehearsals included (REHEARSAL=1 PASSES=...); the bed review\'s b4')
    if predeclaration and not rehearsal:
        ap.error(f'{PREDECLARATION_ENV} admits rehearsals only: no evidence is launched before the declaration is '
                 'hashed')
    declaration = pinned_declaration(predeclaration)
    root = outside_repository(os.environ['VITREA_SITTING_DIR'])
    root.mkdir(parents=True, exist_ok=True)
    app = Path(os.environ.get('VITREA_APP', pin()['path'])).resolve()
    if str(app) != pin()['path']:
        raise ValueError('this sitting is pinned to the side bundle')
    harness = tool('VITREA_HARNESS', str(app.parent / 'harness'))
    recorder = tool('VITREA_RECORD_MACHINE', f'{sys.executable} {HERE}/record-machine.py')
    launcher = tool('VITREA_LAUNCHER', 'open -W')
    session = tool('VITREA_SESSION_READER', str(Path.home() / 'vitrea-w39/scratch/read-session'))
    idle_limit = float(os.environ.get('VITREA_IDLE_LIMIT', IDLE_WAIT_LIMIT))
    idle_poll = float(os.environ.get('VITREA_IDLE_POLL', IDLE_POLL_SECONDS))
    P = pass_spec()
    spec_doc, bed = P.load()
    census = not (rehearsal and args.action == 'dump')
    if args.action == 'dump':
        p = P.pass_of('dump-' + args.key, bed)
        first, last = 1, 1
    else:
        p = P.pass_of(args.key + ('-sentinel' if args.sentinel else ''), bed)
        if p['kind'] == 'dump':
            ap.error('dump passes run through `dump`')
        last = args.last if args.last is not None else (1 if rehearsal else p['runs'])
        first = args.first
        if not 1 <= first <= last <= p['runs']:
            ap.error(f'runs must be a nonempty subset of 1..{p["runs"]}')
        if rehearsal and ((first, last) != (1, 1) or p['kind'] != 'bed'):
            ap.error('a refusal rehearsal is exactly one launch: run 1 of a bed pass')
    scale, scheme, pose = P.endpoint(p['key'])
    others = [q.name for q in root.iterdir() if q.is_dir() and not q.name.startswith('.')
              and q.name not in ('logs',)]
    if rehearsal:
        if any(not n.startswith('rehearsal-') for n in others):
            raise ValueError('a rehearsal root holds rehearsals only')
        name = 'rehearsal-' + p['name']
    else:
        if any(n.startswith('rehearsal-') for n in others):
            raise ValueError('an evidence root holds no rehearsal')
        name = p['name']
        check_order(root, p, first, bed, declaration)
    passdir = root / name
    passdir.mkdir(exist_ok=True)

    def read_session():
        return json.loads(subprocess.check_output(session, text=True))

    for n in range(first, last + 1):
        if not rehearsal:
            check_order(root, p, n, bed, declaration)
        if p['kind'] == 'dump':
            ids = P.dump_ids(p['key'])
            profile = next(x for x in spec_doc['profiles'] if x['key'] == bed['passes'][p['key']]['profile'])
            spec = write_doc(passdir, 'scenes-dump.json', P.subset(spec_doc, ids, profile))
            label = f'w42-{name}-{n}'
        else:
            doc = P.derive(p['key'], n, p['kind'] == 'sentinel')
            spec = write_doc(passdir, f'scenes-run-{n}.json', doc)
            ids = sorted({s for q in doc['profiles'] for s in q['scenes']})
            label = f'w42-{name}-{n}'
        run = passdir / f'run-{n}'
        if run.exists():
            raise ValueError('run already exists; keep it, do not overwrite or silently resume')
        run.mkdir()
        logfile = run / 'driver-idle.log'

        def log(line):
            with logfile.open('a') as f:
                f.write(f'{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} {line}\n')

        try:
            wait_for_idle(read_session, log, limit=idle_limit, poll=idle_poll)

            def attest(phase):
                raw = subprocess.check_output([*recorder, f'{label}-{phase}'])
                (run / f'attest.{phase}.json').write_bytes(raw)
                return json.loads(raw)

            def portable(m, phase):
                c = configuration(m)
                fields = dict(phase=phase, readAt=m['recordedAt'], passName=name, run=n,
                              osProductVersion=(re.search(r'ProductVersion:\s+(\S+)', c['os']) or [None, None])[1],
                              osBuild=(re.search(r'BuildVersion:\s+(\S+)', c['os']) or [None, None])[1],
                              glassTintAmount=c['settings']['NSGlassTintAmount'],
                              reduceTransparency=c['settings']['reduceTransparency'],
                              increaseContrast=c['settings']['increaseContrast'],
                              showBorders=c['settings']['ButtonShapesEnabled'],
                              displayplacerMode=','.join(c['mode']), bundleCdHash=c['cdhash'],
                              bundleBinarySha256=c['binary'], foreignProcessCount=m['foreignProcessCount'],
                              passSpecSha256=hashlib.sha256(spec.read_bytes()).hexdigest(), rehearsal=rehearsal,
                              scenesSha256=declaration['scenesSha256'], splitSha256=declaration['splitSha256'],
                              predeclaration=bool(declaration.get('predeclaration')))
                return ''.join(f'{k}={v}\n' for k, v in fields.items())

            opened = attest('open')
            (run / 'attest.read').write_text(portable(opened, 'open'))
            before = read_session()
            (run / 'session-before.json').write_text(json.dumps(before, indent=2) + '\n')
            problems = []
            try:
                start = validate_machine(opened, scale, census)
            except ValueError as error:
                problems.append(str(error))
            problems += session_problems(before)
            if problems:
                raise ValueError(' | '.join(problems))
            if p['kind'] == 'dump':
                command = dump_argv(launcher, app, spec, run, scale, scheme, pose, ids)
                (run / 'launch.json').write_text(json.dumps(dict(argv=command), indent=2) + '\n')
                timed_out = False
                began = time.monotonic()
                try:
                    result = subprocess.run(command, timeout=dump_timeout(len(ids)))
                except subprocess.TimeoutExpired:
                    timed_out = True
                    subprocess.run(['pkill', '-f', str(app / 'Contents/MacOS/VitreaReference')], check=False)
                elapsed = round(time.monotonic() - began, 1)
                timing = dict(elapsedSeconds=elapsed, timeoutSeconds=dump_timeout(len(ids)),
                              perSceneSeconds=round(elapsed / len(ids), 3), scenes=len(ids))
                (run / 'timing.json').write_text(json.dumps(timing, indent=2) + '\n')
                closed = attest('close')
                (run / 'attest.close').write_text(portable(closed, 'close'))
                after = read_session()
                (run / 'session-after.json').write_text(json.dumps(after, indent=2) + '\n')
                if validate_machine(closed, scale, census) != start:
                    raise ValueError('opening/closing state drift')
                if timed_out:
                    raise ValueError(f'dump-layers overran {dump_timeout(len(ids))} s')
                if result.returncode != 0:
                    raise ValueError(f'dump-layers exited {result.returncode}')
                DC = dumpcheck()
                reference = json.loads((BED_DIR / 'dumps/dump-reference.json').read_text())
                report = DC.check_dir(run / 'json', scheme, pose, scale, reference, expected=ids)
                report['referenceSha256'] = hashlib.sha256((BED_DIR / 'dumps/dump-reference.json').read_bytes()).hexdigest()
                (run / 'check.json').write_text(json.dumps(report, indent=1, default=list) + '\n')
                if report['departures']:
                    raise ValueError(f'{report["departures"]} departure(s) from memo D\'s declared configuration: '
                                     'clause 4 stops the sitting before its first capture')
                record = dict(protocol='dump', run=n, scenes=len(ids), departures=0,
                              unpredicted=report['unpredicted'],
                              checkSha256=hashlib.sha256((run / 'check.json').read_bytes()).hexdigest(),
                              timing=timing, scenesSha256=declaration['scenesSha256'],
                              splitSha256=declaration['splitSha256'], declaration=declaration,
                              **{'pass': p['name'], 'key': p['key']})
                if rehearsal:
                    # Never evidence: no admission.json; the census is what G0's dumps recorded.
                    census_read = {phase: dict(count=m['foreignProcessCount'],
                                               names=sorted({re.sub(r'^.*/', '', f[2].split(' --')[0])
                                                             for f in m.get('foreignProcesses', [])}))
                                   for phase, m in (('open', opened), ('close', closed))}
                    (run / 'rehearsal.json').write_text(json.dumps(dict(
                        schema='w42-dump-rehearsal-1', outcome='dumped-and-checked', foreignCensus=census_read,
                        **record), indent=2) + '\n')
                else:
                    (run / 'admission.json').write_text(json.dumps(dict(
                        schema='w42-dump-admission-2', admitted=True, dry=False, **record), indent=2) + '\n')
                print(f'{name}: dumped and checked {len(ids)} scenes in {elapsed} s ({timing["perSceneSeconds"]} s '
                      f'a scene, timeout {timing["timeoutSeconds"]} s); unpredicted fields {report["unpredicted"]}',
                      flush=True)
                continue
            env = {**os.environ, 'VITREA_SCENES': str(spec), 'VITREA_FIXTURES': str(run),
                   'VITREA_SCALE': str(scale)}
            with (run / 'producer-backgrounds.out').open('w') as f:
                subprocess.run([*harness, 'backgrounds'], env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
            protocol = protocol_of_pass(p)
            command = capture_argv(launcher, app, spec, run, scale, label, protocol, ids, pose)
            (run / 'launch.json').write_text(json.dumps(dict(argv=command, rehearsal=rehearsal), indent=2) + '\n')
            timed_out = False
            try:
                subprocess.run(command, check=True, timeout=REHEARSAL_TIMEOUT if rehearsal else None)
            except subprocess.TimeoutExpired:
                timed_out = True
                subprocess.run(['pkill', '-f', str(app / 'Contents/MacOS/VitreaReference')], check=False)
            closed = attest('close')
            (run / 'attest.close').write_text(portable(closed, 'close'))
            if validate_machine(closed, scale, census) != start:
                raise ValueError('opening/closing state drift')
            if rehearsal:
                after = read_session()
                (run / 'session-after.json').write_text(json.dumps(after, indent=2) + '\n')
                verdict = classify_refusal(run, before, after, timed_out)
                (run / 'rehearsal.json').write_text(json.dumps(verdict, indent=2) + '\n')
                if verdict['outcome'] == 'captured':
                    raise ValueError('the UNGRANTED side bundle published a capture: it holds a grant it must not '
                                     'hold. These pixels are not evidence. Stop.')
                if verdict['outcome'] != 'refused-tcc':
                    raise ValueError(f'rehearsal outcome {verdict["outcome"]}, not the expected TCC refusal')
                print(f'{name}: refused by the TCC gate as expected; no manifest, no fixture', flush=True)
            else:
                raw = (run / 'manifest.json').read_bytes()
                m = json.loads(raw)
                validate_manifest(m, doc, pose, scale, label)
                cells = sum(len(q['scenes']) for q in doc['profiles'])
                binding = frame_binding(run, m, doc, scale)
                admission = run_admission(p, n, command, m, hashlib.sha256(raw).hexdigest(), cells, declaration,
                                          binding)
                (run / 'admission.json').write_text(json.dumps(admission, indent=2) + '\n')
                print(f'{name} run {n}: admitted cells={cells}', flush=True)
        except BaseException as error:
            (run / 'refusal.txt').write_text(f'{type(error).__name__}: {error}\n')
            quarantine = run.with_name(f'QUARANTINE-run-{n}-{time.time_ns()}')
            run.rename(quarantine)
            print('REFUSED; retained at ' + str(quarantine), file=sys.stderr)
            raise


if __name__ == '__main__':
    main()
