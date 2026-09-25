#!/usr/bin/env python3.12
"""W39 sitting driver (c9a §5.184; charter clauses 4-6, X6 and X22 as carried).

Derived from W34 G0's sitting.py, never edited in place. It keeps W34's protocol:
the pinned side bundle only, explicit roots outside the repository, the macOS
27.0 / 26A428 gate, the machine read before and after every run with drift
refused, at least sixty seconds of independent HID idle, and a failed run
QUARANTINED under a new name, never retried or overwritten. What W39 changes:

- The passes and their order: preflight-1x/2x (light active; run 1 is the nine
  preflight geometries x glass/opaque, 18 captures; run 2 the phase-zero pair
  repeated at the pass's END),
  then active-1x, active-2x, inactive-1x and inactive-2x (seven runs; run 1 also
  carries the colour no-glass references), then the long-protocol sentinels
  (three runs each). A pass refuses if a later pass has started or an earlier one
  has not, and no bed pass starts without the frozen preflight verdict, whose
  admitted phase scenes it re-derives from pass-spec.py and must agree with.
- X6 holds strictly: a foreign capture process refuses every launch, including a
  rehearsal. W34 G0 carried a user exception for its no-pixel dry runs; W39 has no
  such exception, so there is no flag that relaxes the census.
- The manifest is checked for the W39 attestations: the window's requested and
  actual SCREEN frame (actual must equal requested, at the pass's backing scale),
  and every supplied path's frameOrigin against the declared position - size/2.
- A REFUSAL REHEARSAL replaces W34's DRY=1. W34's dry run passed --dry-run to the
  harness, which presents every cell and captures nothing, so it never reached
  ScreenCaptureKit. W39's rehearsal is the REAL capture launch, with argv identical
  to the real pass's run 1, from the ungranted side bundle: the expected outcome is
  the harness's own TCC-gate refusal with no manifest, no fixture PNG and no staging
  directory left. A published manifest means the side bundle holds a grant it must
  not hold in G0; a hang or a new on-screen window is a pending permission prompt;
  anything else is a refusal for another reason. All three are quarantined.

Capture logs can carry holdout-role cells' diagnostics and stay producer-only.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
MAIN = Path('/Users/new/Developer/GitHub/designer')

OS_VERSION, OS_BUILD = '27.0', '26A428'
SETTINGS = {'reduceTransparency': '0', 'increaseContrast': '0', 'NSGlassTintAmount': '0.5',
            'ButtonShapesEnabled': '0'}
MODES = {1: '69', 2: '68'}          # displayplacer modes: 2560x1440 unscaled (1x) / HiDPI (2x)
SCREEN = '7709FD0F-F423-4277-B0C8-7CA94F85723A'
MIN_IDLE_SECONDS = 60
SRGB = 'kCGColorSpaceSRGB'
FRAME_SPACE = 'appkit-global-bottom-left'
RESET_INTERSTITIAL = '6'
# The long protocol's settle and seed. 3901 is W39's own choice, not inherited: W34
# used 3401, and nothing here depends on the two agreeing.
SENTINEL_SETTLE, SENTINEL_SEED = '8', '3901'
BED = ('active-1x', 'active-2x', 'inactive-1x', 'inactive-2x')
RUNS = {'preflight': 2, 'bed': 7, 'sentinel': 3}
# The harness's own words when SCShareableContent is refused (Capture.swift). The
# localised system text beside them varies with the language; this line does not.
TCC_GATE = 'This is the Screen Recording (TCC) gate'
REHEARSAL_TIMEOUT = 180
# The process that draws macOS's permission prompts. An unanswered prompt on screen
# makes a refusal ambiguous, so no launch starts while one is there.
PROMPT_OWNERS = ('universalAccessAuthWarn',)

_PIN = None
_PASS = None


def pin():
    global _PIN
    if _PIN is None:
        _PIN = json.loads((HERE / 'bundle-pin.json').read_text())
    return _PIN


def pass_spec():
    global _PASS
    if _PASS is None:
        spec = importlib.util.spec_from_file_location('w39_pass_spec', HERE / 'pass-spec.py')
        _PASS = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_PASS)
    return _PASS


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


def validate_machine(m, scale):
    """Every X6 fact, strictly, and EVERY failing gate named in one refusal, so an
    opening refusal records the whole machine state rather than its first fault.
    There is deliberately no exclusivity exception."""
    c = configuration(m)
    problems = []
    if not re.search(rf'ProductVersion:\s+{re.escape(OS_VERSION)}\s', c['os']) or OS_BUILD not in c['os']:
        problems.append(f'OS version/build is not the declared {OS_VERSION} / {OS_BUILD}')
    if c['settings'] != SETTINGS:
        problems.append(f'policy/slider/Show Borders mismatch: {c["settings"]}')
    if c['mode'] != [MODES[scale]] or c['displayIdentity'] != [SCREEN]:
        problems.append(f'display mode/identity mismatch for {scale}x (want mode {MODES[scale]}): '
                        f'{c["mode"]} {c["displayIdentity"]}')
    p = pin()
    # The recorder strips vtool's stdout and the pin keeps it raw (trailing newline):
    # the same LC_BUILD_VERSION, compared without its surrounding whitespace.
    build = (c['build'] or '').strip()
    if (c['binary'], c['cdhash'], build) != (p['binarySha256'], p['cdhash'], p['buildVersion'].strip()):
        problems.append('side bundle identity changed (binary, cdhash or LC_BUILD_VERSION); '
                        'a rebuild is a new pin and a new grant')
    if m['foreignProcessCount'] != 0:
        problems.append(f'{m["foreignProcessCount"]} foreign capture process(es); X6 admits none')
    if problems:
        raise ValueError('machine gate refused: ' + '; '.join(problems))
    return c


def session_problems(observed):
    """The independent session gates; every failing one is named."""
    problems = []
    idle = observed.get('idleSeconds')
    if not isinstance(idle, (int, float)) or idle < MIN_IDLE_SECONDS:
        problems.append(f'no launch: {MIN_IDLE_SECONDS}s of HID idle required, read {idle}')
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


# ------------------------------------------------------------------- the passes

def pass_name(kind, scale, sentinel):
    return f'{kind}-{scale}x' + ('-sentinel' if sentinel else '')


def rank(name):
    if name.startswith('preflight-'):
        return 0
    if name.endswith('-sentinel'):
        return 5
    return 1 + BED.index(name)


def started(directory):
    return directory.is_dir() and any(c.name.startswith(('run-', 'QUARANTINE-'))
                                      for c in directory.iterdir())


def check_order(root, name):
    """Declared order: preflight (either scale first), the four bed passes, sentinels."""
    mine = rank(name)
    names = [f'preflight-{s}x' for s in (1, 2)] + list(BED) + [b + '-sentinel' for b in BED]
    later = [n for n in names if rank(n) > mine and started(root / n)]
    if later:
        raise ValueError(f'{name} refused: a later pass has already started ({later})')
    missing = [n for n in names if rank(n) < mine and not started(root / n)]
    if missing:
        raise ValueError(f'{name} refused: an earlier pass has not started ({missing})')


def phase_scenes(axes):
    """The phase scenes `axes` admits over the empty branch, across all four passes."""
    P = pass_spec()
    out = set()
    for pose in ('active', 'inactive'):
        for scale in (1, 2):
            ids = lambda doc: {s['id'] for s in doc['scenes']}
            out |= ids(P.derive(pose, scale, 1, tuple(axes))) - ids(P.derive(pose, scale, 1, ()))
    return out


def load_verdict(root, path):
    """The frozen preflight verdict, bound to this root's preflight manifests."""
    if not path.is_file():
        raise ValueError(f'no bed pass without the frozen preflight verdict ({path})')
    raw = path.read_bytes()
    verdict = json.loads(raw)
    if verdict.get('schema') != 'w39-preflight-verdict-1':
        raise ValueError('not a W39 preflight verdict')
    for scale in (1, 2):
        for run in (1, 2):
            manifest = root / f'preflight-{scale}x/run-{run}/manifest.json'
            want = verdict['inputs'][f'{scale}x'][f'run{run}ManifestSha256']
            if not manifest.is_file() or hashlib.sha256(manifest.read_bytes()).hexdigest() != want:
                raise ValueError(f'the verdict was not computed from this root\'s {manifest}')
    axes = tuple(verdict['reachableAxes'])
    if set(verdict['admittedScenes']) != phase_scenes(axes):
        raise ValueError('the verdict\'s admitted phase scenes disagree with pass-spec.py')
    digest = hashlib.sha256(raw).hexdigest()
    pinned = root / 'verdict-pin.json'
    if pinned.exists():
        if json.loads(pinned.read_text())['sha256'] != digest:
            raise ValueError('the preflight verdict changed after the bed began')
    else:
        pinned.write_text(json.dumps(dict(sha256=digest, path=str(path), reachableAxes=list(axes)),
                                     indent=2) + '\n')
    return axes, digest


def pass_doc(kind, scale, run, axes, sentinel):
    P = pass_spec()
    if kind == 'preflight':
        doc = P.preflight(scale)
        profiles = [p['key'] for p in doc['profiles']]
        if profiles != [f'apple-macos-27.0-{scale}x-light-standard-glass0.5']:
            raise ValueError(f'preflight is light active at one scale, got {profiles}')
        if run == 2:
            # The END repeat: the phase-zero pair again, so drift over the pass is
            # measured apart from what the actuator does.
            keep = {s['id'] for s in doc['scenes'] if s.get('$phaseAxis') == 'zero'}
            if len(keep) != 2:
                raise ValueError('the preflight end repeat is the phase-zero glass/opaque pair')
            doc['scenes'] = [s for s in doc['scenes'] if s['id'] in keep]
            for p in doc['profiles']:
                p['scenes'] = [s for s in p['scenes'] if s in keep]
            doc['split']['probe'] = sorted(keep)
        return doc
    return P.derive(kind, scale, run, tuple(axes), sentinel)


# ------------------------------------------------------------------ attestation

def shapes(component):
    if component['kind'] == 'none':
        return []
    return component['items'] if component['kind'] == 'column' else [component]


def declared_origin(shape, canvas):
    """ShapeSpec.frame(in:) in SceneSpec.swift: position - size/2, else centred + offset."""
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
            if f['captureMethod'] != 'screencapturekit' or not f['materialRendered'] \
                    or not f.get('deterministic'):
                raise ValueError('material/repeat attestation failed: ' + sid)
            if [f['width'], f['height']] != pixels:
                raise ValueError('fixture pixel size mismatch: ' + sid)
            if f.get('presentedActive') != (pose == 'active'):
                raise ValueError('pose attestation failed: ' + sid)
            if pose == 'inactive':
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


def classify_refusal(run, before, after, timed_out):
    """The rehearsal's outcome. Only 'refused-tcc' is the expected evidence."""
    out = (run / 'producer-capture.out').read_text() if (run / 'producer-capture.out').exists() else ''
    err = (run / 'producer-capture.err').read_text() if (run / 'producer-capture.err').exists() else ''
    fixtures = [str(p.relative_to(run)) for p in run.rglob('*.png')
                if p.relative_to(run).parts[0] != 'backgrounds']
    staging = [p.name for p in run.glob('.staging-*')]
    appeared = sorted(set((after or {}).get('windowOwners') or []) -
                      set((before or {}).get('windowOwners') or []))
    facts = dict(timedOut=timed_out, manifestPublished=(run / 'manifest.json').exists(),
                 fixturePngs=fixtures, stagingLeft=staging, newWindowOwners=appeared,
                 captureAttempted=bool(re.search(r'^capturing \d+ fixtures via screencapturekit', out, re.M)),
                 tccGateText=TCC_GATE in err,
                 errSha256=hashlib.sha256(err.encode()).hexdigest(),
                 errFirstLine=err.splitlines()[0] if err else None)
    if facts['manifestPublished'] or fixtures:
        outcome = 'captured'
    elif timed_out or appeared or any(o.split('|')[0] in PROMPT_OWNERS
                                      for o in (after or {}).get('windowOwners') or []):
        outcome = 'prompt-pending'
    elif facts['tccGateText'] and facts['captureAttempted'] and not staging:
        outcome = 'refused-tcc'
    else:
        outcome = 'refused-other'
    return dict(outcome=outcome, **facts)


def tool(name, default):
    return shlex.split(os.environ.get(name, default))


def inside(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('kind', choices=['preflight', 'active', 'inactive'])
    ap.add_argument('scale', type=int, choices=[1, 2])
    ap.add_argument('first', type=int, nargs='?', default=1)
    ap.add_argument('last', type=int, nargs='?')
    ap.add_argument('--sentinel', action='store_true', help='the long-protocol sentinel pass')
    ap.add_argument('--rehearse-refusal', action='store_true',
                    help='G0: the real run-1 launch from the ungranted bundle, expected TCC-refused')
    ap.add_argument('--verdict', type=Path, help='frozen preflight verdict (default ROOT/preflight-verdict.json)')
    args = ap.parse_args(argv)
    if 'DRY' in os.environ:
        ap.error('DRY is W34\'s harness --dry-run, which never reaches ScreenCaptureKit. W39 has no dry '
                 'run; a G0 rehearsal is --rehearse-refusal, a real launch expected to be refused.')
    if args.sentinel and args.kind == 'preflight':
        ap.error('the preflight has no sentinel pass; its end repeat is run 2')
    rehearsal = args.rehearse_refusal
    limit = RUNS['preflight' if args.kind == 'preflight' else 'sentinel' if args.sentinel else 'bed']
    last = args.last if args.last is not None else (1 if rehearsal else limit)
    if not 1 <= args.first <= last <= limit:
        ap.error(f'runs must be a nonempty subset of 1..{limit}')
    if rehearsal and (args.first, last) != (1, 1):
        ap.error('a refusal rehearsal is exactly one launch: run 1')

    if 'VITREA_SITTING_DIR' not in os.environ:
        ap.error('VITREA_SITTING_DIR must name the sitting root explicitly (outside the repository)')
    root = Path(os.environ['VITREA_SITTING_DIR']).expanduser().resolve()
    if inside(root, REPO) or inside(root, MAIN):
        raise ValueError('sitting output must be outside every checkout of the repository')
    root.mkdir(parents=True, exist_ok=True)
    app = Path(os.environ.get('VITREA_APP', pin()['path'])).resolve()
    if str(app) != pin()['path']:
        raise ValueError('this sitting is pinned to the side bundle')
    harness = tool('VITREA_HARNESS', str(app.parent / 'harness'))
    recorder = tool('VITREA_RECORD_MACHINE', f'{sys.executable} {HERE}/record-machine.py')
    launcher = tool('VITREA_LAUNCHER', 'open -W')
    session = tool('VITREA_SESSION_READER', str(Path.home() / 'vitrea-w39/scratch/read-session'))

    base = pass_name(args.kind, args.scale, args.sentinel)
    others = [c.name for c in root.iterdir() if c.is_dir() and not c.name.startswith('.')]
    if rehearsal:
        # Rehearsals and evidence never share a root, so no reader can mistake one
        # for the other.
        if any(not n.startswith('rehearsal-') for n in others):
            raise ValueError('a rehearsal root holds rehearsals only')
        name, axes, verdict_sha = 'rehearsal-' + base, (), None
    else:
        if any(n.startswith('rehearsal-') for n in others):
            raise ValueError('an evidence root holds no rehearsal')
        name = base
        check_order(root, name)
        axes, verdict_sha = ((), None) if args.kind == 'preflight' else \
            load_verdict(root, (args.verdict or root / 'preflight-verdict.json').resolve())
    pose = 'active' if args.kind == 'preflight' else args.kind
    passdir = root / name
    passdir.mkdir(exist_ok=True)

    for n in range(args.first, last + 1):
        doc = pass_doc(args.kind, args.scale, n, axes, args.sentinel)
        spec = passdir / f'scenes-run-{n}.json'
        encoded = json.dumps(doc, indent=2) + '\n'
        if spec.exists() and spec.read_text() != encoded:
            raise ValueError(f'existing declaration {spec} differs')
        if not spec.exists():
            spec.write_text(encoded)
        label = f'w39-{name}-{n}'
        run = passdir / f'run-{n}'
        if run.exists():
            raise ValueError('run already exists; keep it, do not overwrite or silently resume')
        run.mkdir()
        try:
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
                    bundleBinarySha256=c['binary'],
                    foreignProcessCount=m['foreignProcessCount'],
                    passSpecSha256=hashlib.sha256(spec.read_bytes()).hexdigest(),
                    preflightVerdictSha256=verdict_sha, reachableAxes=','.join(axes),
                    rehearsal=rehearsal)
                return ''.join(f'{k}={v}\n' for k, v in fields.items())

            # Both reads are recorded before either is judged, and every failing gate
            # is named in one refusal: an opening refusal is evidence of the whole state.
            opened = attest('open')
            (run / 'attest.read').write_text(portable(opened, 'open'))
            before = json.loads(subprocess.check_output(session, text=True))
            (run / 'session-before.json').write_text(json.dumps(before, indent=2) + '\n')
            problems = []
            try:
                start = validate_machine(opened, args.scale)
            except ValueError as error:
                problems.append(str(error))
            problems += session_problems(before)
            if problems:
                raise ValueError(' | '.join(problems))
            env = {**os.environ, 'VITREA_SCENES': str(spec), 'VITREA_FIXTURES': str(run),
                   'VITREA_SCALE': str(args.scale)}
            with (run / 'producer-backgrounds.out').open('w') as f:
                subprocess.run([*harness, 'backgrounds'], env=env, stdout=f, stderr=subprocess.STDOUT,
                               check=True)
            if pose == 'inactive':
                # W34's inactive pre-check, kept: the harness's tint doctor over the
                # canonical manifest, read-only. W39 declares no tint, so it measures
                # no pair; it runs so the inactive path is the one W34 attested.
                rehearse = {**env, 'VITREA_FIXTURES': os.environ.get(
                    'VITREA_REHEARSAL_FIXTURES', str(MAIN / 'apps/reference-apple/fixtures'))}
                with (run / 'producer-rehearse-tints.out').open('w') as f:
                    subprocess.run([*harness, 'rehearse-tints', '--pose', 'inactive'], env=rehearse,
                                   stdout=f, stderr=subprocess.STDOUT, check=True)
            ids = sorted({s for p in doc['profiles'] for s in p['scenes']})
            command = [*launcher]
            for key in ['VITREA_SCENES', 'VITREA_FIXTURES', 'VITREA_SCALE']:
                command += ['--env', key + '=' + env[key]]
            command += ['--stdout', str(run / 'producer-capture.out'),
                        '--stderr', str(run / 'producer-capture.err'), str(app),
                        '--args', 'capture', '--run-label', label,
                        '--reset-interstitial', RESET_INTERSTITIAL,
                        '--min-idle-seconds', str(MIN_IDLE_SECONDS), '--scenes', ','.join(ids)]
            if args.sentinel:
                command += ['--initial-settle', SENTINEL_SETTLE, '--order-seed', SENTINEL_SEED]
            if pose == 'inactive':
                command += ['--inactive']
            (run / 'launch.json').write_text(json.dumps(dict(argv=command, rehearsal=rehearsal), indent=2) + '\n')
            timed_out = False
            try:
                subprocess.run(command, check=True, timeout=REHEARSAL_TIMEOUT if rehearsal else None)
            except subprocess.TimeoutExpired:
                timed_out = True
                binary = str(app / 'Contents/MacOS/VitreaReference')
                subprocess.run(['pkill', '-f', binary], check=False)
            closed = attest('close')
            (run / 'attest.close').write_text(portable(closed, 'close'))
            if validate_machine(closed, args.scale) != start:
                raise ValueError('opening/closing state drift')
            if rehearsal:
                after = json.loads(subprocess.check_output(session, text=True))
                (run / 'session-after.json').write_text(json.dumps(after, indent=2) + '\n')
                verdict = classify_refusal(run, before, after, timed_out)
                (run / 'rehearsal.json').write_text(json.dumps(verdict, indent=2) + '\n')
                if verdict['outcome'] == 'captured':
                    raise ValueError('the UNGRANTED side bundle published a capture: it holds a grant G0 '
                                     'must not give it. These pixels are not evidence. Stop.')
                if verdict['outcome'] != 'refused-tcc':
                    raise ValueError(f'rehearsal outcome {verdict["outcome"]}, not the expected TCC refusal')
                print(f'{name}: refused by the TCC gate as expected; no manifest, no fixture', flush=True)
            else:
                if timed_out:
                    raise ValueError('unreachable: a real run has no timeout')
                m = json.loads((run / 'manifest.json').read_text())
                validate_manifest(m, doc, pose, args.scale, label)
                cells = sum(len(p['scenes']) for p in doc['profiles'])
                (run / 'admission.json').write_text(json.dumps(dict(
                    admitted=True, cells=cells, passName=name, run=n,
                    reachableAxes=list(axes), preflightVerdictSha256=verdict_sha)) + '\n')
                print(f'{name} run {n}: admitted cells={cells}', flush=True)
        except BaseException as error:
            (run / 'refusal.txt').write_text(f'{type(error).__name__}: {error}\n')
            quarantine = run.with_name(f'QUARANTINE-run-{n}-{time.time_ns()}')
            run.rename(quarantine)
            print('REFUSED; retained at ' + str(quarantine), file=sys.stderr)
            raise


if __name__ == '__main__':
    main()
