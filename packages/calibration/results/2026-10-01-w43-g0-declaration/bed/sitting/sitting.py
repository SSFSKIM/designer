#!/usr/bin/env python3.12
"""W43 sitting driver (charter G0 (d), G1a, G1b; clauses 3-5; X5', X6, X42, X43).

Derived from W42 G0's sitting.py (§5.195), never edited in place. It keeps W42's protocol: the
pinned side bundle only, explicit roots outside every checkout, the macOS 27.0 / 26A428 gate, the
machine read before and after every run with drift refused, a bounded wait for HID idle before
every launch, zero foreign capture processes, per-capture hidIdleSeconds >= 60, pose / window /
supplied-path attestation, every frame's bytes bound by SHA-256 at admission, the declaration
checked before any launch and re-checked before every run, launches only under the
orchestrator's trap, and a failed run QUARANTINED under a new name, never retried or overwritten.

What W43 changes, each with a red and a green case in red-green.py:

1. The census matches executables, not command lines (record-machine.py), and
2. excludes the launching chain the orchestrator records at detach.
3. The idle-wait log is `driver-idle.txt`, so the `*.log` gitignore cannot drop it from the
   per-pass commit (W42 G1 phase 1).
4. A WATCHDOG reads the session every few seconds during every launch, dumps included: HID input
   (the idle reading falls behind the wall clock), a frontmost change (the harness losing focus in
   the active pose; anything replacing the launch-time app in the receded pose), a lock or a
   permission prompt ends the launch at once, ends the native app, and quarantines the run naming
   the reading (W42 G1 stops 1 and 2 ran a doomed 12-minute dump to its end).
5. The slider is declared PER PASS (`glass` in the plan). The orchestrator writes it, through
   `slider-set`, only while no harness or dump process is alive, and records every write; a run's
   machine gate requires the defaults read to equal its pass's position exactly, and a run refuses
   if the last recorded write is not its position. `slider-as-found` and `slider-restore` are the
   trap's: the as-found value is recorded once per sitting root and restored on every exit.
6. A dump pass is a SENTINEL: every surface's `inputBlurFillNormalOpacity` in the tree must equal
   the pass's slider position, and the pose fields the launch asked for (X42).
7. The attestation `materialize` reads (`attest.read`) carries what its rules and its per-profile
   record need, the bundle pin naming the SIDE bundle among them, and `publish` runs materialize
   over a published pass's admitted runs after checking each names the side's pin and the slider.

And for the canonical bed: a pass may span several profiles (both schemes, W29's pass shape), and
the supplied-path attestation mirrors PathAttestation.swift for `group` and `stack` components,
which W42's bed never had and the canonical bed does.

The membership is pass-spec.py's reading of the declared plan; `plan` is the dry mode.
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
import signal
import struct
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
BED_DIR = HERE.parent
DECL_DIR = BED_DIR.parent
REPO = HERE.parents[5]
MAIN = Path('/Users/new/Developer/GitHub/designer')
W39_PIN_REL = 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/bundle-pin.json'
W39_PIN = REPO / W39_PIN_REL
CANONICAL_SCENES = 'apps/reference-apple/scenes.json'
DECLARATION = DECL_DIR / 'declaration.json'
DECLARATION_DIGEST = DECL_DIR / 'declaration.sha256'
PREDECLARATION_ENV = 'W43_PREDECLARATION'      # dump rehearsals before the declaration is hashed only
ORCHESTRATED_ENV = 'W43_ORCHESTRATED'          # set by sitting-orchestrate.sh around every launch
SITTING_ENV = 'W43_SITTING'                    # g1a or g1b: which declared plan the sitting runs
CUT_ENV = 'W43_CUT_AFTER'                      # the pass a STOP_AFTER cut ended at; runAfterCut passes only

OS_VERSION, OS_BUILD = '27.0', '26A428'
# The slider is not here: it is each pass's own position (`glass_problems`).
SETTINGS = {'reduceTransparency': '0', 'increaseContrast': '0', 'ButtonShapesEnabled': '0'}
SLIDER_DOMAIN, SLIDER_KEY = '-g', 'NSGlassTintAmount'
SCREEN = '7709FD0F-F423-4277-B0C8-7CA94F85723A'
MIN_IDLE_SECONDS = 60            # the harness's per-capture floor and the admission check
WAIT_IDLE_SECONDS = 75           # what every launch waits for first (W39 G1's orchestrator)
IDLE_WAIT_LIMIT = 3 * 3600       # a bounded wait; exceeding it refuses the run
IDLE_POLL_SECONDS = 15
WATCH_POLL_SECONDS = 5           # the watchdog's period during a launch
IDLE_SLACK_SECONDS = 2.0         # how far an idle reading may lag the wall clock without input
SRGB = 'kCGColorSpaceSRGB'
FRAME_SPACE = 'appkit-global-bottom-left'
PROTOCOLS = {
    'normal': dict(initialSettleSeconds=1.75, orderSeed=None, resetInterstitialSeconds=6.0,
                   resetCarriesGlass=False, minIdleSeconds=float(MIN_IDLE_SECONDS)),
    'long': dict(initialSettleSeconds=8.0, orderSeed=4242, resetInterstitialSeconds=6.0,
                 resetCarriesGlass=False, minIdleSeconds=float(MIN_IDLE_SECONDS)),
}
PROMPT_OWNERS = ('universalAccessAuthWarn',)
NORMAL_INPUT = 'inputBlurFillNormalOpacity'

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
    return module('w43_pass_spec', HERE / 'pass-spec.py')


def recorder_module():
    return module('w43_record_machine', HERE / 'record-machine.py')


def pin():
    global _PIN
    if _PIN is None:
        _PIN = json.loads(W39_PIN.read_text())
    return _PIN


def pin_sha256():
    return hashlib.sha256(W39_PIN.read_bytes()).hexdigest()


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


# ----------------------------------------------------------------- machine facts

def configuration(m):
    signature = m['side'].get('signature', {}).get('stderr', '')
    cd = re.search(r'^CDHash=(.+)$', signature, re.M)
    mode = re.findall(r'^  mode (\d+):.*<-- current mode$', m['display']['stdout'], re.M)
    return dict(os=m['os']['stdout'], settings={k: v['stdout'] for k, v in m['settings'].items()},
                mode=mode,
                displayIdentity=re.findall(r'^Persistent screen id: (.+)$', m['display']['stdout'], re.M),
                colour=m['displayColourContext']['stdout'], binary=m['side'].get('binarySha256'),
                cdhash=cd[1] if cd else None, build=m['side'].get('buildVersion', {}).get('stdout'),
                path=m['side'].get('path'), identifier=(m['side'].get('identifier') or {}).get('stdout'))


def slider_matches(read, glass):
    """The defaults read equals the declared position exactly (materialize's rule 3 is exact too)."""
    try:
        return float(read) == float(glass)
    except (TypeError, ValueError):
        return False


def validate_machine(m, scale, glass, census=True):
    """Every gate, strictly, and every failing one named in ONE refusal. `census=False` only for
    the pre-sitting dump rehearsal, which records the foreign-process census instead."""
    c = configuration(m)
    problems = []
    if not re.search(rf'ProductVersion:\s+{re.escape(OS_VERSION)}\s', c['os']) or OS_BUILD not in c['os']:
        problems.append(f'OS version/build is not the declared {OS_VERSION} / {OS_BUILD}')
    others = {k: v for k, v in c['settings'].items() if k != SLIDER_KEY}
    if others != SETTINGS:
        problems.append(f'policy/Show Borders mismatch: {others}')
    if not slider_matches(c['settings'].get(SLIDER_KEY), glass):
        problems.append(f'slider mismatch: NSGlassTintAmount reads {c["settings"].get(SLIDER_KEY)!r} and the pass '
                        f'declares {glass} (X42)')
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


# -------------------------------------------------------------------- the watchdog

def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except (TypeError, ValueError):
        return False


class Watchdog:
    """The session, read every few seconds while a launch runs (charter G0 (d); W42 G1 stops 1, 2).

    It trips on the first reading that shows any of:
    - HID input: the idle reading must grow with the wall clock from the launch-time reading, so a
      reading below (previous + elapsed - slack) means input arrived between the two reads;
    - a focus change: in the active pose, once the harness has been frontmost, any other frontmost
      app while the harness process still runs (once it has exited the run is ending); before
      that, anything but the launch-time app or the harness; in the receded pose, anything
      replacing the launch-time app, the harness included (a receded harness never activates);
    - a lock, or a permission prompt on screen;
    - a session it cannot read (nothing could then attest the launch).

    What it cannot see: input that does not reset HIDIdleTime; a focus change and its return
    inside one poll period (the per-fixture pose attestation still reads every capture); a change
    of key window inside the harness itself; overlays that take no focus.
    """

    def __init__(self, read, pose, harness_id, baseline, baseline_at, log, clock=time.monotonic,
                 is_alive=alive):
        self.read, self.pose, self.harness_id, self.log = read, pose, harness_id, log
        self.clock, self.is_alive = clock, is_alive
        self.front0 = baseline.get('frontmostIdentifier')
        self.idle_prev, self.t_prev = baseline.get('idleSeconds'), baseline_at
        self.harness_pid = None

    def check(self):
        try:
            o = self.read()
        except Exception as error:     # a reader that fails cannot attest the launch
            return f'the watchdog could not read the session ({type(error).__name__}: {error})'
        t = self.clock()
        front, fpid, idle = o.get('frontmostIdentifier'), o.get('frontmostPid'), o.get('idleSeconds')
        owners = o.get('windowOwners') or []
        self.log(f'watch: front={front} pid={fpid} idle={idle} locked={o.get("screenLocked")} owners={len(owners)}')
        if not isinstance(idle, (int, float)) or not isinstance(self.idle_prev, (int, float)):
            return f'HID idle unreadable during the launch (read {idle!r})'
        expected = self.idle_prev + (t - self.t_prev) - IDLE_SLACK_SECONDS
        if idle < expected:
            return (f'HID input during the launch: idle read {idle:.1f} s where at least {expected:.1f} s was due '
                    f'({self.idle_prev:.1f} s, {t - self.t_prev:.1f} s earlier); frontmost {front}')
        self.idle_prev, self.t_prev = idle, t
        if o.get('screenLocked') is not False:
            return 'the session locked (or its lock became unreadable) during the launch'
        prompts = [w for w in owners if w.split('|')[0] in PROMPT_OWNERS]
        if prompts:
            return f'a permission prompt appeared during the launch ({prompts})'
        if self.pose == 'active':
            if front == self.harness_id:
                self.harness_pid = fpid
            elif self.harness_pid is not None:
                if self.is_alive(self.harness_pid):
                    return (f'focus lost during the launch: frontmost became {front} (pid {fpid}) while the '
                            f'harness (pid {self.harness_pid}) still ran')
            elif front != self.front0:
                return f'focus taken during the launch: frontmost became {front} before the harness was frontmost'
        elif front != self.front0:
            return f'frontmost changed during a receded launch: {self.front0} -> {front} (pid {fpid})'
        return None


def watched(command, watchdog, timeout=None, poll=WATCH_POLL_SECONDS, end_native=lambda: None,
            sleep=time.sleep, clock=time.monotonic):
    """Run `command`, consulting `watchdog` every `poll` s. Returns (returncode, timed_out); a trip
    kills the launch and the native app at once and raises ValueError naming the reading."""
    began = clock()
    proc = subprocess.Popen(command)
    try:
        while True:
            try:
                code = proc.wait(timeout=poll)
                return code, False
            except subprocess.TimeoutExpired:
                pass
            if timeout is not None and clock() - began >= timeout:
                proc.kill()
                proc.wait()
                end_native()
                return None, True
            reason = watchdog.check()
            if reason is not None:
                proc.kill()
                proc.wait()
                end_native()
                raise ValueError('watchdog stopped the launch: ' + reason)
    except BaseException:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        raise


def end_native(app, grace=10.0):
    """End every running harness by its executable image (never by a command-line pattern)."""
    R = recorder_module()
    binary = Path(app) / 'Contents/MacOS/VitreaReference'
    targets = [p for p in R.native_processes(binary=binary) if p['executable'] == str(binary.resolve())]
    for p in targets:
        try:
            os.kill(p['pid'], signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline and any(alive(p['pid']) for p in targets):
        time.sleep(0.2)
    for p in targets:
        if alive(p['pid']):
            try:
                os.kill(p['pid'], signal.SIGKILL)
            except ProcessLookupError:
                pass
    return targets


# ------------------------------------------------------------------- the slider

def defaults_tool():
    """The `defaults` the slider is read and written through. A seam: the suites point it at a
    stub over a scratch file and never write the real global default."""
    return shlex.split(os.environ.get('VITREA_DEFAULTS', '/usr/bin/defaults'))


def slider_read():
    """{present, value, type}: the global NSGlassTintAmount as `defaults` reads it."""
    d = defaults_tool()
    got = subprocess.run([*d, 'read', SLIDER_DOMAIN, SLIDER_KEY], capture_output=True, text=True)
    if got.returncode != 0:
        return dict(present=False, value=None, type=None)
    kind = subprocess.run([*d, 'read-type', SLIDER_DOMAIN, SLIDER_KEY], capture_output=True, text=True)
    return dict(present=True, value=got.stdout.strip(), type=kind.stdout.strip().removeprefix('Type is ') or None)


def slider_log(root):
    return Path(root) / 'logs' / 'slider-writes.jsonl'


def slider_writes(root):
    path = slider_log(root)
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def slider_set(root, glass, list_native=None):
    """Write the slider, only while no harness or dump process is alive, and record it.

    A `defaults write` reaches only a freshly launched harness (W29 G0 relaunched per arm; the
    charter review's confirmation), so a native process alive across the write would carry the
    old position into the new pass: it refuses the write, and so the pass, before and after.
    """
    list_native = list_native or (lambda: recorder_module().native_processes())
    before = list_native()
    if before:
        raise ValueError(f'a harness or dump process is alive ({before}); a slider write is followed only by fresh '
                         'launches, so the pass is refused and nothing was written')
    d = defaults_tool()
    subprocess.run([*d, 'write', SLIDER_DOMAIN, SLIDER_KEY, '-float', repr(float(glass))], check=True,
                   capture_output=True)
    after_read = slider_read()
    after = list_native()
    record = dict(value=float(glass), read=after_read, at=now(), epochNs=time.time_ns(),
                  nativeAliveBefore=before, nativeAliveAfter=after)
    slider_log(root).parent.mkdir(parents=True, exist_ok=True)
    with slider_log(root).open('a') as f:
        f.write(json.dumps(record) + '\n')
    if not slider_matches(after_read['value'], glass):
        raise ValueError(f'the slider reads {after_read["value"]!r} after writing {glass}')
    if after:
        raise ValueError(f'a harness or dump process appeared across the slider write ({after}); the pass is refused')
    return record


def slider_as_found(root):
    """Record the as-found slider ONCE per sitting root: a continuation keeps the first reading, so
    a crash that left the slider moved can never become the value the trap restores."""
    path = Path(root) / 'logs' / 'slider-as-found.json'
    current = slider_read()
    path.parent.mkdir(parents=True, exist_ok=True)
    with (Path(root) / 'logs' / 'slider-reads.jsonl').open('a') as f:
        f.write(json.dumps(dict(at=now(), read=current)) + '\n')
    if path.exists():
        return json.loads(path.read_text()), current
    if current['present'] and current['type'] != 'float':
        raise ValueError(f'the as-found slider is a {current["type"]}, not a float; it could not be restored as it was '
                         'found, so nothing is written')
    record = dict(asFound=current, at=now())
    path.write_text(json.dumps(record, indent=2) + '\n')
    return record, current


def slider_restore(root, list_native=None):
    """Put the as-found slider back, and read it back: written as the float it was, or deleted if
    absent; nothing is written where it already reads as found. A write is logged with the other
    writes (value None for a deletion), so a pass after a cut's restore reads the true last write;
    it is never refused, since the trap must restore whatever is alive."""
    list_native = list_native or (lambda: recorder_module().native_processes())
    record = json.loads((Path(root) / 'logs' / 'slider-as-found.json').read_text())
    found = record['asFound']
    d = defaults_tool()
    current = slider_read()
    if current['present'] == found['present'] and current['value'] == found['value']:
        return dict(restored=True, asFound=found, read=current, written=False)
    before = list_native()
    if found['present']:
        subprocess.run([*d, 'write', SLIDER_DOMAIN, SLIDER_KEY, '-float', found['value']], check=True,
                       capture_output=True)
    else:
        subprocess.run([*d, 'delete', SLIDER_DOMAIN, SLIDER_KEY], capture_output=True)
    back = slider_read()
    entry = dict(value=float(found['value']) if found['present'] else None, read=back, at=now(), epochNs=time.time_ns(),
                 restore=True, nativeAliveBefore=before, nativeAliveAfter=list_native())
    slider_log(root).parent.mkdir(parents=True, exist_ok=True)
    with slider_log(root).open('a') as f:
        f.write(json.dumps(entry) + '\n')
    ok = back['present'] == found['present'] and (not found['present'] or back['value'] == found['value'])
    return dict(restored=ok, asFound=found, read=back, written=True)


def slider_problems(root, glass):
    """The run's position, as the sitting's own write record says it was set."""
    writes = slider_writes(root)
    if not writes:
        return []                    # never written: the as-found value is the run's, as the defaults read says
    last = writes[-1]
    problems = []
    if not slider_matches(last['value'], glass):
        problems.append(f'the last slider write set {last["value"]} and the pass declares {glass}')
    if last.get('nativeAliveBefore') or last.get('nativeAliveAfter'):
        problems.append('the last slider write had a native process alive across it')
    return problems


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


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_declaration(sitting, predeclaration=False):
    """The plan every launch runs is the declared one (clause 1; W42's B-M1, one level up).

    Returns the record every admission carries. Refuses unless the sitting's plan and every
    scenes file it names are committed at HEAD, each source's bytes are the SHA-256 the plan
    names, the plan validates, and declaration.json, committed and hashed (declaration.sha256,
    committed, its last line naming these bytes: an amended declaration appends its hash beneath the
    original), names the plan's SHA-256 in its `sitting-<sitting>` item. `predeclaration` keeps
    every check but the declaration's, whose state is recorded; only dump rehearsals then launch.
    """
    P = pass_spec()
    problems = []
    try:
        plan_raw = at_head(P.plan_path(sitting))
        plan = json.loads(plan_raw)
    except (ValueError, OSError) as error:
        raise ValueError(f'refused before any launch: the {sitting} plan is not committed ({error})') from None
    sources, named = {}, {}
    for name, s in (plan.get('sources') or {}).items():
        try:
            raw = at_head(REPO / s['path'])
        except (ValueError, OSError, KeyError, TypeError) as error:
            problems.append(f'source {name}: {error}')
            continue
        named[name] = sha(raw)
        if named[name] != s.get('sha256'):
            problems.append(f'source {name} is {named[name][:12]}; the plan names {str(s.get("sha256"))[:12]}')
        sources[name] = json.loads(raw)
    if not problems:
        try:
            P.validate_plan(plan, sources)
        except ValueError as error:
            problems.append(str(error))
    head = subprocess.run(['git', '-C', str(HERE), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    record = dict(sitting=sitting, planSha256=sha(plan_raw), sources=named, head=head.stdout.strip() or None)
    stated = []
    try:
        raw = at_head(DECLARATION)
        record['declarationSha256'] = sha(raw)
        item = next(i['declared'] for i in json.loads(raw)['items'] if i.get('id') == f'sitting-{sitting}')
        if item.get('planSha256') != record['planSha256']:
            stated.append(f'declaration.json names plan {str(item.get("planSha256"))[:12]}; the {sitting} plan is '
                          f'{record["planSha256"][:12]}')
        # declaration.sha256 is a chain (declare.py, the parent's amendment ruling): the original hash first,
        # each amendment's beneath it, and the LAST line names the bytes in force. declare.py check verifies
        # the chain itself; the launch requires that its last line is this declaration.json.
        chain = [ln.split()[0] for ln in at_head(DECLARATION_DIGEST).decode().splitlines() if ln.strip()]
        record['declarationChain'] = chain
        if not chain or chain[-1] != record['declarationSha256']:
            stated.append('declaration.sha256 does not name this declaration.json on its last line')
    except (ValueError, OSError, KeyError, StopIteration, UnicodeDecodeError, json.JSONDecodeError) as error:
        stated.append(f'the declaration is not committed and hashed: {type(error).__name__}: {error}')
    if predeclaration:
        record.update(predeclaration=True, declarationProblems=stated)
    else:
        problems += stated
    if problems:
        raise ValueError('refused before any launch: the plan is not the pinned declaration: ' + '; '.join(problems))
    return record


def pinned_snapshot(sitting, predeclaration=False):
    """(record, plan, sources) from ONE read of each file, whose bytes are exactly the ones the pin
    check accepted: every run derives from this snapshot, so a file edited mid-pass can never be
    captured under the checked hash (W42's verification round, finding 1)."""
    P = pass_spec()
    plan_raw = P.plan_path(sitting).read_bytes()
    plan = json.loads(plan_raw)
    raws = {name: (REPO / s['path']).read_bytes() for name, s in plan['sources'].items()}
    declaration = pinned_declaration(sitting, predeclaration)
    if sha(plan_raw) != declaration['planSha256'] or {n: sha(r) for n, r in raws.items()} != declaration['sources']:
        raise ValueError('refused before any launch: the plan or a source changed while it was being checked')
    sources = {n: json.loads(r) for n, r in raws.items()}
    P.validate_plan(plan, sources)
    return declaration, plan, sources


def reverify(declaration, predeclaration=False):
    """Before every run: the files on disk are still the snapshot's."""
    try:
        again = pinned_declaration(declaration['sitting'], predeclaration)
    except ValueError as error:
        raise ValueError(f'the plan on disk is no longer the one this driver validated: {error}') from None
    if (again['planSha256'], again['sources']) != (declaration['planSha256'], declaration['sources']):
        raise ValueError(f'the plan on disk is no longer the one this driver validated: plan '
                         f'{again["planSha256"][:12]} against {declaration["planSha256"][:12]}')


class Cancelled(BaseException):
    """SIGTERM, SIGINT or SIGHUP: the orchestrator's cancellation, or the operator's."""


def _cancel(signum, frame):
    raise Cancelled(f'cancelled by signal {signal.Signals(signum).name}')


def declared_by(admission, declaration):
    """An admission counts only under the plan the sitting runs on, and never a rehearsal's."""
    return (admission.get('sitting') == declaration['sitting']
            and admission.get('planSha256') == declaration['planSha256']
            and not admission.get('predeclaration'))


def frame_binding(run, manifest, doc, scale):
    """Every fixture PNG exists inside the run and decodes at the declared pixel size; returns the
    SHA-256 of each. (W43's beds seal no holdout: the canonical bed's held-out cells are published
    as fixtures, W29's practice, and the probe declares calibration and validation only, X46.)"""
    from PIL import Image
    size = (doc['canvas']['width'] * scale, doc['canvas']['height'] * scale)
    root = run.resolve()
    frames = {}
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
            frames[cell] = sha(raw)
    return dict(frames=frames)


def expectation_problems(p, frames):
    """A pass's `expect`: each named cell's frame must be one of its declared byte states."""
    out = []
    for cell, allowed in (p.get('expect') or {}).items():
        got = frames.get(cell)
        if got not in allowed:
            out.append(f'{cell} captured {str(got)[:12]}, not one of the declared {[a[:12] for a in allowed]}')
    return out


# --------------------------------------------------------------- the bridges

W42_DIR = 'packages/calibration/results/2026-09-29-w42-g0-declaration'
W42_INSTRUMENT = REPO / W42_DIR / 'instrument'
BRIDGE_REFERENCES_ENV = 'W43_BRIDGE_REFERENCES'   # a store of w42-archive reference frames, <sha256>.png


class BridgeStop(Exception):
    """An opening bridge disagreed: the run stands admitted, and the sitting stops before any capture
    away from 0.5 (charter clause 3)."""


def instrument():
    """W42's instrument, unchanged: `forward.Cell` and `regions.statistics`, the populations G0 (b)'s
    bridge read and W42 G1's repeat bar was measured on. Imported only when a bridge pass runs."""
    path = str(W42_INSTRUMENT)
    if path not in sys.path:
        sys.path.insert(0, path)
    import forward
    import regions
    return forward, regions


def decode_frame(raw):
    """RGB codes as floats. A pixel that is not opaque is MISSING (NaN): a frame carries a region
    only where it carries opaque pixels."""
    import numpy as np
    from PIL import Image
    with Image.open(io.BytesIO(raw)) as image:
        rgba = np.asarray(image.convert('RGBA'), dtype=np.float64)
    rgb = rgba[..., :3].copy()
    rgb[rgba[..., 3] < 255] = np.nan
    return rgb


def bridge_verdict(frame_raw, reference_raw, background, component, scale, scheme, pose, bars=None, cell=''):
    """Charter clause 3 for ONE run of ONE bridge cell: byte identity, or every region median within
    max(1 code, bar) of the reference's.

    AGREE (bytes) when the files are identical, AGREE (pixels) when their decoded pixels are.
    Otherwise every region statistic of W42's instrument (forward.Cell at the cell's own geometry;
    masks n and w in the active pose, n receded; regions.statistics, a median per population and
    channel) is compared with the reference's, against max(1, bar), where `bars` maps (mask,
    statistic) to the cell's measured repeat bar and a statistic with none reads at the 0.5 floor.
    DISAGREE when any statistic is outside its tolerance, when a region the reference carries is
    missing from the frame (no opaque pixel in it, or a frame of another size), and when the cell
    has no region statistic at all: then only identity can agree, as G0 (b) read it.
    """
    import warnings
    import numpy as np
    out = dict(cell=cell, frameSha256=sha(frame_raw), referenceSha256=sha(reference_raw))
    if out['frameSha256'] == out['referenceSha256']:
        return dict(out, verdict='AGREE (bytes)', agrees=True)
    frame, ref = decode_frame(frame_raw), decode_frame(reference_raw)
    if frame.shape != ref.shape:
        return dict(out, verdict='DISAGREE', agrees=False,
                    failing=[f'every region missing: the frame is {frame.shape[1]}x{frame.shape[0]}, the reference '
                             f'{ref.shape[1]}x{ref.shape[0]}'])
    if np.array_equal(frame, ref, equal_nan=True):
        return dict(out, verdict='AGREE (pixels)', agrees=True)
    F, R = instrument()
    failing, rows, masks = [], [], []
    for kernel in (('n', 'w') if pose == 'active' else ('n',)):
        c = F.Cell(f'{scale}x|{cell}', background, component, scale, scheme, 'rest' if pose == 'active' else 'inactive',
                   rgb=True, kernel=kernel)
        if c.d.shape != frame.shape[:2]:
            return dict(out, verdict='DISAGREE', agrees=False,
                        failing=[f'every region missing: the frame is not the cell\'s {c.d.shape[1]}x{c.d.shape[0]}'])
        pops = R.populations(c) if c.mask.sum() else []
        masks.append(dict(mask=kernel, populations=len(pops)))
        if not pops:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)       # an all-missing population's median is NaN
            got, want = R.statistics(c, frame, pops), R.statistics(c, ref, pops)
        for name in sorted(want):
            bar = float((bars or {}).get((kernel, name), 0.5))
            tolerance = max(1.0, bar)
            g, w = got.get(name), want[name]
            if not np.isfinite(w):
                failing.append(f'{kernel}:{name} missing from the reference')
                continue
            if g is None or not np.isfinite(g):
                failing.append(f'{kernel}:{name} missing from the frame')
                continue
            delta = float(g - w)
            rows.append(dict(mask=kernel, statistic=name, frame=float(g), reference=float(w), delta=delta, bar=bar,
                             tolerance=tolerance, agrees=abs(delta) <= tolerance + 1e-9))
            if abs(delta) > tolerance + 1e-9:
                failing.append(f'{kernel}:{name} {delta:+.1f} codes (tolerance {tolerance:g})')
    if not rows and not failing:
        failing.append('no region statistic to read (every population empty): only identity can agree')
    diff = np.abs(np.nan_to_num(frame, nan=-1000.0) - np.nan_to_num(ref, nan=-1000.0)).max(-1)
    return dict(out, verdict='DISAGREE' if failing else 'AGREE (regions)', agrees=not failing, failing=failing,
                masks=masks, statistics=len(rows), worstDelta=max((abs(r['delta']) for r in rows), default=None),
                pixelsDiffering=int((diff > 0).sum()), maxCodes=float(diff.max()), rows=rows)


def bridge_references(p):
    """Every reference frame of a bridge pass, its bytes checked against the declared SHA-256 BEFORE
    any launch: a canonical fixture by its repo path, a w42-archive frame from the store named by
    W43_BRIDGE_REFERENCES (filled by `bridge-references` from the verified archive)."""
    refs, problems = {}, []
    store = os.environ.get(BRIDGE_REFERENCES_ENV)
    for cell, spec in sorted(p['bridge']['cells'].items()):
        ref = spec['reference']
        if 'path' in ref:
            path = REPO / ref['path']
        elif store:
            path = Path(store) / f'{ref["sha256"]}.png'
        else:
            problems.append(f'{cell}: its reference is a w42-archive frame and {BRIDGE_REFERENCES_ENV} names no store')
            continue
        try:
            raw = path.read_bytes()
        except OSError as error:
            problems.append(f'{cell}: {error}')
            continue
        if sha(raw) != ref['sha256']:
            problems.append(f'{cell}: {path.name} is {sha(raw)[:12]}; the plan names {ref["sha256"][:12]}')
            continue
        refs[cell] = raw
    if problems:
        raise ValueError('refused before any launch: a bridge reference is not the declared frame: ' + '; '.join(problems))
    return refs


def bridge_bars(p):
    """{cell: {(mask, statistic): bar}} from the declared repeat-bar file, its JSON checked by SHA-256."""
    import gzip
    spec = p['bridge'].get('bars')
    if not spec:
        return {}
    raw = gzip.decompress((REPO / spec['path']).read_bytes())
    if sha(raw) != spec['sha256']:
        raise ValueError(f'refused before any launch: the bridge bars {spec["path"]} are not the declared ones')
    out = {}
    for row in json.loads(raw)['rows']:
        if row.get('status') == 'measured' and row.get('protocol') == spec['protocol'] \
                and row['cell'] in p['bridge']['cells']:
            for name, v in row['statistics'].items():
                out.setdefault(row['cell'], {})[(row['kernel'], name)] = v['bar']
    return out


def bridge_report(p, n, run, manifest, doc, refs, bars):
    """Every cell of one bridge run, read against its reference; the run agrees only if every cell does."""
    scenes = {s['id']: s for s in doc['scenes']}
    rows = []
    for profile in manifest['profiles']:
        scheme = pass_spec().scheme_of(profile['profileKey'])
        for f in profile['fixtures']:
            cell = profile['profileKey'] + '/' + f['sceneId']
            scene = scenes[f['sceneId']]
            rows.append(bridge_verdict((run / f['file']).read_bytes(), refs[cell], doc['backgrounds'][scene['background']],
                                       doc['components'][scene['component']], p['scale'], scheme, p['pose'],
                                       bars.get(cell), cell))
    return dict(schema='w43-bridge-run-1', run=n, stop=p['bridge']['stop'], agrees=all(r['agrees'] for r in rows),
                rule='byte identity, or every region median within max(1 code, bar) of the reference (charter clause 3)',
                cells=rows, **{'pass': p['name']})


def extract_bridge_references(plan, archive_root, out):
    """Copy every w42-archive reference frame a plan's bridges name into the store `out`, from the
    verified archive through W42's guarded Reader with the probe role only; each by its SHA-256."""
    out = outside_repository(out)
    A = module('w42_archive_for_bridges', REPO / W42_DIR / 'bed/sitting/w42_archive.py')
    A.verify_tree(archive_root)
    reader = A.wave_module().default_wave().reader(archive_root, roles=('probe',))
    wanted = {}
    for p in plan['passes']:
        for cell, spec in ((p.get('bridge') or {}).get('cells') or {}).items():
            if 'archive' in spec['reference']:
                wanted.setdefault(cell, set()).add(spec['reference']['sha256'])
    out.mkdir(parents=True, exist_ok=True)
    written = {}
    for cell, shas in sorted(wanted.items()):
        _, blobs = A.unbundle(reader.read(cell, 'states'))
        for digest in sorted(shas):
            if digest not in blobs:
                raise ValueError(f'{cell}: w42-archive holds no frame {digest[:12]}')
            target = out / f'{digest}.png'
            if target.exists() and sha(target.read_bytes()) != digest:
                raise ValueError(f'{target} exists with other bytes')
            target.write_bytes(blobs[digest])
            written[digest] = cell
    return written


# ------------------------------------------------------------------- the passes

def started(directory):
    return directory.is_dir() and any(c.name.startswith(('run-', 'QUARANTINE-')) for c in directory.iterdir())


def admitted(root, p, n, declaration):
    path = root / p['name'] / f'run-{n}' / 'admission.json'
    if not path.is_file():
        return False
    a = json.loads(path.read_text())
    want = 'dump' if p['kind'] == 'dump' else p['protocol']
    # An opening bridge that disagreed stands admitted as evidence but carries nothing after it:
    # the sitting stops there (charter clause 3), and only a new declaration resumes.
    stopped = (a.get('bridge') or {}).get('stop') is True and (a.get('bridge') or {}).get('agrees') is False
    return (a.get('admitted') is True and a.get('pass') == p['name'] and a.get('run') == n
            and a.get('protocol') == want and declared_by(a, declaration) and not stopped)


def check_order(root, p, run, plan, declaration, cut=None):
    """Every run of every earlier pass admitted, no later pass started, and within the pass runs
    1..run-1 admitted: the declared order is the only order.

    `cut` names the pass a STOP_AFTER cut ended the ordinary order at (X47). Only a `runAfterCut`
    pass (the closing W42 sentinel bridges) runs after it, and it is allowed past the passes the
    cut dropped; those can never be taken later, because a later pass has then started."""
    order = pass_spec().pass_order(plan)
    dropped = set()
    if cut is not None:
        at = next((q for q in order if q['name'] == cut), None)
        if at is None:
            raise ValueError(f'{p["name"]} refused: the cut names no declared pass ({cut})')
        if not p.get('runAfterCut'):
            raise ValueError(f'{p["name"]} refused: after the cut at {cut} only runAfterCut passes run')
        if at['rank'] >= p['rank']:
            raise ValueError(f'{p["name"]} refused: it does not follow the cut at {cut}')
        dropped = {q['name'] for q in order if at['rank'] < q['rank'] < p['rank'] and not q.get('runAfterCut')}
    later = [q['name'] for q in order if q['rank'] > p['rank'] and started(root / q['name'])]
    if later:
        raise ValueError(f'{p["name"]} refused: a later pass has already started ({later})')
    missing = [f'{q["name"]} run {k}' for q in order if q['rank'] < p['rank'] and q['name'] not in dropped
               for k in range(1, q['runs'] + 1) if not admitted(root, q, k, declaration)]
    if missing:
        raise ValueError(f'{p["name"]} refused: an earlier pass is not complete; not admitted: {missing}')
    missing = [k for k in range(1, run) if not admitted(root, p, k, declaration)]
    if missing:
        raise ValueError(f'{p["name"]} run {run} refused: earlier run(s) {missing} of this pass are not '
                         'admitted; a quarantined or interrupted run blocks its successors until the '
                         'operator takes it again deliberately')


# ------------------------------------------------------------------ attestation

def frame_of(shape, canvas):
    """ShapeSpec.frame(in:): position - size/2, else centred + offset."""
    w, h = shape['size']
    if shape.get('position') is not None:
        return [shape['position'][0] - w / 2, shape['position'][1] - h / 2]
    dx, dy = shape.get('offset') or [0, 0]
    return [(canvas['width'] - w) / 2 + dx, (canvas['height'] - h) / 2 + dy]


def declared_paths(component, canvas):
    """(shape, origin) per supplied path, as PathAttestation.swift's suppliedShapePaths builds them:
    none, one shape, a stack's base then over, a column's items, a group laid out left to right
    with its spacing and centred on both axes."""
    kind = component['kind']
    if kind == 'none':
        return []
    if kind == 'stack':
        return [(s, frame_of(s, canvas)) for s in (component['base'], component['over'])]
    if kind == 'column':
        return [(s, frame_of(s, canvas)) for s in component['items']]
    if kind == 'group':
        items, spacing = component['items'], component['spacing']
        left = (canvas['width'] - (sum(s['size'][0] for s in items) + (len(items) - 1) * spacing)) / 2
        out = []
        for s in items:
            out.append((s, [left, (canvas['height'] - s['size'][1]) / 2]))
            left += s['size'][0] + spacing
        return out
    return [(component, frame_of(component, canvas))]


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
            want = declared_paths(doc['components'][scenes[sid]['component']], canvas)
            got = f.get('suppliedPaths') or []
            if len(got) != len(want):
                raise ValueError('supplied path count mismatch: ' + sid)
            for (shape, origin), path in zip(want, got):
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
    if protocol != p['protocol']:
        raise ValueError(f'{p["name"]} launched the {protocol} protocol; the pass is {p["protocol"]}')
    settings = PROTOCOLS[protocol]
    recorded = manifest.get('captureProtocol') or {}
    got = {k: recorded.get(k) for k in settings}
    if got != settings:
        raise ValueError(f'manifest captureProtocol {got} is not the launched {protocol} protocol {settings}')
    if declaration.get('predeclaration'):
        raise ValueError('a capture is never admitted before the declaration is hashed')
    if len(binding['frames']) != cells:
        raise ValueError('the frame binding does not cover every admitted cell')
    return dict(schema='w43-run-admission-1', admitted=True, dry=False, protocol=protocol,
                captureProtocol=dict(settings), cells=cells, manifestSha256=manifest_sha, run=n,
                glass=p['glass'], sitting=declaration['sitting'], planSha256=declaration['planSha256'],
                declaration=declaration, frames=binding['frames'], role=p.get('role'),
                publish=bool(p.get('publish')), **{'pass': p['name']})


def portable(m, phase, *, p, n, spec, source_path, declaration, rehearsal, slider_write):
    """The run's `attest.read`: key=value lines `materialize` parses (src/run-provenance.ts) beside the
    manifest. Its rules read osProductVersion, osBuild, glassTintAmount (exact against the key),
    the two accessibility toggles and passSpecSha256 (one value across a published pass); its
    per-profile record keeps every field the runs agree on, so the bundle fields NAME THE SIDE
    BUNDLE that drew the bed (W29's fields, plus its identifier and the SHA-256 of W39's pin)."""
    c = configuration(m)
    pin_ = pin()
    build = c['build'] or ''
    minos = re.search(r'^\s*minos\s+(\S+)', build, re.M)
    sdk = re.search(r'^\s*sdk\s+(\S+)', build, re.M)
    s = c['settings']
    a11y = 'increased-contrast' if s['increaseContrast'] != '0' else (
        'reduced-transparency' if s['reduceTransparency'] != '0' else 'standard')
    product = (re.search(r'ProductVersion:\s+(\S+)', c['os']) or [None, None])[1]
    build_id = (re.search(r'BuildVersion:\s+(\S+)', c['os']) or [None, None])[1]
    fields = dict(phase=phase, readAt=m['recordedAt'], **{'pass': p['name']}, passName=p['name'], run=n,
                  sitting=declaration['sitting'], role=p.get('role'),
                  os=f'{product} {build_id}', osProductVersion=product, osBuild=build_id,
                  glassTintAmount=s[SLIDER_KEY], glassDeclared=repr(float(p['glass'])),
                  sliderWrittenAt=slider_write.get('at') if slider_write else 'as-found',
                  reduceTransparency=s['reduceTransparency'], increaseContrast=s['increaseContrast'],
                  a11yMode=a11y, showBorders=s['ButtonShapesEnabled'],
                  displayplacerMode=','.join(c['mode']), displayModeDeclaredForScale=pass_spec().MODES[p['scale']],
                  bundlePath=c['path'], bundleIdentifier=c['identifier'], bundleCdHash=c['cdhash'],
                  bundleBinarySha256=c['binary'], bundleMinOS=minos[1] if minos else None,
                  bundleRecordedSdk=sdk[1] if sdk else None, bundlePinSha256=pin_sha256(),
                  bundlePinPath=W39_PIN_REL,
                  sceneSpecSourceSha256=declaration['sources'][p['source']],
                  passSpecSha256=sha(spec.read_bytes()), planSha256=declaration['planSha256'],
                  foreignProcessCount=m['foreignProcessCount'], rehearsal=rehearsal,
                  predeclaration=bool(declaration.get('predeclaration')))
    if source_path == CANONICAL_SCENES:
        fields['sceneSpecCanonicalSha256'] = declaration['sources'][p['source']]
    return ''.join(f'{k}={v}\n' for k, v in fields.items())


# ------------------------------------------------------------- the dump sentinel

def float32(x):
    return struct.unpack('f', struct.pack('f', float(x)))[0]


def normal_opacities(node, out):
    """Every glassBackground filter's Normal input in a dump's layer tree."""
    if isinstance(node, dict):
        for f in node.get('filters') or []:
            inputs = f.get('inputs') or {}
            if NORMAL_INPUT in inputs:
                out.append(inputs[NORMAL_INPUT])
        for value in node.values():
            if isinstance(value, (dict, list)):
                normal_opacities(value, out)
    elif isinstance(node, list):
        for value in node:
            normal_opacities(value, out)
    return out


def sentinel_check(json_dir, ids, glass, pose, scale, scheme):
    """X42's second reading: the tree's own Normal fill weight is the pass's slider position.

    Every dumped scene must be present, in the asked pose (key and active, or neither), scheme
    and scale, and every glass surface's `inputBlurFillNormalOpacity` must equal `glass` at the
    tree's own float precision. A scene with no such input is a departure: an absent reading is
    not an attestation.
    """
    json_dir = Path(json_dir)
    found = {p.stem: p for p in json_dir.glob('*.json')} if json_dir.is_dir() else {}
    departures, readings = [], {}
    for sid in sorted(set(ids) | set(found)):
        if sid not in found:
            departures.append(dict(scene=sid, what='not dumped'))
            continue
        if sid not in ids:
            departures.append(dict(scene=sid, what='dumped but not declared'))
            continue
        d = json.loads(found[sid].read_text())
        active = pose == 'active'
        for field, want in (('isKeyWindow', active), ('appIsActive', active), ('backingScaleFactor', scale),
                            ('colorScheme', scheme), ('scene', sid)):
            if d.get(field) != want:
                departures.append(dict(scene=sid, what=f'{field} reads {d.get(field)!r}, want {want!r}'))
        values = normal_opacities(d.get('view'), [])
        readings[sid] = values
        if not values:
            departures.append(dict(scene=sid, what=f'no {NORMAL_INPUT} in the tree'))
        off = [v for v in values if not isinstance(v, (int, float)) or float32(v) != float32(glass)]
        if off:
            departures.append(dict(scene=sid, what=f'{NORMAL_INPUT} reads {sorted(set(map(str, off)))}, declared {glass}'))
    return dict(schema='w43-dump-sentinel-1', glass=glass, pose=pose, scale=scale, scheme=scheme,
                scenes=len(ids), surfaces=sum(len(v) for v in readings.values()),
                normalOpacities=sorted({repr(v) for vs in readings.values() for v in vs}),
                departures=departures)


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

def dry_plan(plan, sources, out=None, root='<VITREA_SITTING_DIR>', app=None):
    """Walk the whole declared sitting and describe every launch; execute nothing."""
    P = pass_spec()
    app = app or pin()['path']
    launcher = ['open', '-W']
    root = Path(root)
    passes = []
    for p in P.pass_order(plan):
        runs = []
        for n in range(1, p['runs'] + 1):
            run = root / p['name'] / f'run-{n}'
            if p['kind'] == 'dump':
                doc = P.dump_doc_from(plan, sources, p['name'])
                argv = dump_argv(launcher, app, root / p['name'] / 'scenes-dump.json', run, p['scale'],
                                 P.scheme_of(p['profile']), p['pose'], p['scenes'])
                runs.append(dict(run=n, scenes=len(p['scenes']), timeoutSeconds=dump_timeout(len(p['scenes'])),
                                 argv=argv))
                name = 'scenes-dump.json'
            else:
                doc = P.derive_from(plan, sources, p['name'], n)
                ids = P.capture_ids(doc)
                label = f'w43-{p["name"]}-{n}'
                argv = capture_argv(launcher, app, root / p['name'] / f'scenes-run-{n}.json', run, p['scale'], label,
                                    p['protocol'], ids, p['pose'])
                runs.append(dict(run=n, cells=len(P.cells(doc)), protocol=p['protocol'], label=label, argv=argv))
                name = f'scenes-run-{n}.json'
            if out is not None:
                d = Path(out) / p['name']
                d.mkdir(parents=True, exist_ok=True)
                (d / name).write_text(json.dumps(doc, indent=2) + '\n')
                (d / f'launch-run-{n}.json').write_text(json.dumps(runs[-1]['argv'], indent=2) + '\n')
        passes.append(dict(name=p['name'], kind=p['kind'], role=p.get('role'), glass=p['glass'], mode=p['mode'],
                           scale=p['scale'], pose=p['pose'], publish=bool(p.get('publish')), runs=runs))
    counts = P.plan_counts(plan, sources)
    value = dict(schema='w43-sitting-plan-walk-1', executed=False, sitting=plan['sitting'],
                 note='nothing was launched, read, written to the slider or captured; argv paths are under the '
                      'placeholder root', root=str(root), passes=passes, totals=counts['totals'])
    if out is not None:
        (Path(out) / 'plan.json').write_text(json.dumps(value, indent=2) + '\n')
    return value


# ----------------------------------------------------------------- publication

def tsx_command():
    return tool('VITREA_TSX', 'npx tsx')


def publication(root, p, declaration, source_path, fixtures=None):
    """The materialize invocation for a published pass, after the checks only a W43 run can fail.

    Every run 1..N admitted under the declaration; every run's opening `attest.read` names the
    SIDE bundle by its pinned path, identifier, cdhash and binary and the pin's own SHA-256;
    its slider read equals the pass's position and every profile key's token; one passSpecSha256
    across the runs. materialize then re-checks the provenance rules itself and votes.
    """
    P = pass_spec()
    if not p.get('publish'):
        raise ValueError(f'{p["name"]} is not a published pass')
    pin_ = pin()
    runs, problems, specs = [], [], set()
    for n in range(1, p['runs'] + 1):
        run = Path(root) / p['name'] / f'run-{n}'
        if not admitted(Path(root), p, n, declaration):
            problems.append(f'run {n} is not admitted under this declaration')
            continue
        fields = dict(line.split('=', 1) for line in (run / 'attest.read').read_text().splitlines() if '=' in line)
        want = dict(bundlePath=pin_['path'], bundleIdentifier=pin_['bundleIdentifier'], bundleCdHash=pin_['cdhash'],
                    bundleBinarySha256=pin_['binarySha256'], bundlePinSha256=pin_sha256())
        wrong = {k: fields.get(k) for k, v in want.items() if fields.get(k) != v}
        if wrong:
            problems.append(f'run {n} does not name the side bundle\'s pin: {wrong}')
        if not slider_matches(fields.get('glassTintAmount'), p['glass']):
            problems.append(f'run {n} attests slider {fields.get("glassTintAmount")!r}; the pass is {p["glass"]}')
        specs.add(fields.get('passSpecSha256'))
        runs.append(run)
    if len(specs) > 1:
        problems.append(f'the runs read {len(specs)} pass documents; materialize votes across one')
    off = [k for k in p['profiles'] if P.parse_key(k)[3] != p['glass']]
    if off:
        problems.append(f'profile keys {off} do not name slider {p["glass"]}')
    if source_path != CANONICAL_SCENES:
        problems.append(f'its source is {source_path}; W43 publishes the canonical bed only (X5\')')
    if problems:
        raise ValueError(f'{p["name"]} is not publishable: ' + '; '.join(problems))
    argv = [*tsx_command(), 'cli/materialize.ts', *[a for i, r in enumerate(runs, 1) for a in ('--run', f'r{i}={r}')],
            '--profile', ','.join(sorted(p['profiles'])), '--frequency-settle']
    env = dict(VITREA_SCENES=str(REPO / CANONICAL_SCENES))
    if fixtures is not None:
        env['VITREA_FIXTURES'] = str(fixtures)
    return dict(argv=argv, cwd=str(REPO / 'packages/calibration'), env=env)


# ------------------------------------------------------------------------ main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    pl = sub.add_parser('plan', help='the dry mode: every document and argv of the sitting; executes nothing')
    pl.add_argument('--out', type=Path, help='a new directory outside the repository for the documents')
    d = sub.add_parser('dump', help='the one dump-layers launch of a dump (sentinel) pass')
    d.add_argument('name')
    d.add_argument('--rehearse', action='store_true',
                   help='a pre-sitting dump rehearsal: the real launch and sentinel check in a rehearsal root, '
                        'never evidence; the foreign-process census is recorded, not enforced')
    c = sub.add_parser('capture', help='runs first..last of a capture pass')
    c.add_argument('name')
    c.add_argument('first', type=int, nargs='?', default=1)
    c.add_argument('last', type=int, nargs='?')
    w = sub.add_parser('wait-idle', help='wait (bounded, logged) for N s of HID idle; used before a mode switch')
    w.add_argument('seconds', type=float)
    sub.add_parser('pin-check', help='the pre-launch declaration check, as the orchestrator runs it first')
    sub.add_parser('slider-as-found', help='record the as-found slider once per sitting root (the trap restores it)')
    ss = sub.add_parser('slider-set', help='write the slider while no harness or dump process is alive; recorded')
    ss.add_argument('glass', type=float)
    sub.add_parser('slider-restore', help='restore the as-found slider and read it back (the trap)')
    pb = sub.add_parser('publish', help='check a published pass\'s runs and run materialize over them')
    pb.add_argument('name')
    pb.add_argument('--apply', action='store_true', help='pass --apply to materialize (it writes the fixtures)')
    pb.add_argument('--fixtures', type=Path, help='VITREA_FIXTURES for materialize (default: the canonical bundle)')
    en = sub.add_parser('end-native', help='end every running harness of APP by its executable image (the trap)')
    en.add_argument('app', type=Path)
    br = sub.add_parser('bridge-references', help='fill the store of w42-archive reference frames a plan names')
    br.add_argument('archive', type=Path, help='the verified w42-archive tree (w42_archive.py fetch prints it)')
    br.add_argument('--out', type=Path, required=True, help='the store W43_BRIDGE_REFERENCES will name')
    args = ap.parse_args(argv)
    if args.action == 'end-native':
        print(json.dumps([dict(pid=t['pid'], executable=t['executable']) for t in end_native(args.app)]))
        return
    if 'DRY' in os.environ:
        ap.error('DRY is W34\'s harness --dry-run, which never reaches ScreenCaptureKit. W43 has no such path: '
                 'the dry mode is `plan`.')
    sitting = os.environ.get(SITTING_ENV)
    if sitting not in pass_spec().SITTINGS:
        ap.error(f'{SITTING_ENV} must name the sitting ({", ".join(pass_spec().SITTINGS)})')
    predeclaration = os.environ.get(PREDECLARATION_ENV) == '1'
    if args.action == 'pin-check':
        print(json.dumps(pinned_declaration(sitting, predeclaration), indent=2))
        return
    if args.action == 'bridge-references':
        _, plan, _ = pinned_snapshot(sitting, predeclaration)
        print(json.dumps(extract_bridge_references(plan, args.archive, args.out), indent=2))
        return
    if args.action == 'plan':
        if args.out is not None:
            outside_repository(args.out)
            if args.out.exists():
                raise ValueError('plan output exists; keep it and name a new directory')
        plan, sources = pass_spec().load(pass_spec().plan_path(sitting))
        value = dry_plan(plan, sources, args.out)
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
    root = outside_repository(os.environ['VITREA_SITTING_DIR'])
    if args.action in ('slider-as-found', 'slider-set', 'slider-restore'):
        if os.environ.get(ORCHESTRATED_ENV) != '1':
            ap.error('the slider is written only under sitting-orchestrate.sh, whose trap restores it on every exit')
        if args.action == 'slider-as-found':
            record, current = slider_as_found(root)
            print(json.dumps(dict(asFound=record['asFound'], current=current)))
        elif args.action == 'slider-set':
            print(json.dumps(slider_set(root, args.glass)))
        else:
            result = slider_restore(root)
            print(json.dumps(result))
            if not result['restored']:
                raise SystemExit(7)
        return
    if args.action == 'publish':
        declaration, plan, _ = pinned_snapshot(sitting)
        p = pass_spec().pass_of(args.name, plan)
        job = publication(root, p, declaration, plan['sources'][p['source']]['path'], args.fixtures)
        argv_ = job['argv'] + (['--apply'] if args.apply else [])
        print(json.dumps(dict(job, argv=argv_), indent=2), flush=True)
        raise SystemExit(subprocess.run(argv_, cwd=job['cwd'], env={**os.environ, **job['env']}).returncode)
    rehearsal = args.action == 'dump' and args.rehearse
    cut = os.environ.get(CUT_ENV) or None       # set by the orchestrator only for runAfterCut passes
    if os.environ.get(ORCHESTRATED_ENV) != '1':
        ap.error('every launch runs under sitting-orchestrate.sh, whose trap restores the display mode and the '
                 'slider on every exit, rehearsals included (REHEARSAL=1 PASSES=...)')
    if predeclaration and not rehearsal:
        ap.error(f'{PREDECLARATION_ENV} admits dump rehearsals only: no evidence is launched before the declaration '
                 'is hashed')
    declaration, plan, sources = pinned_snapshot(sitting, predeclaration)
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
    watch_poll = float(os.environ.get('VITREA_WATCH_POLL', WATCH_POLL_SECONDS))
    P = pass_spec()
    p = P.pass_of(args.name, plan)
    if (args.action == 'dump') != (p['kind'] == 'dump'):
        ap.error(f'{args.name} is a {p["kind"]} pass; dump passes run through `dump`, capture passes through `capture`')
    census = not rehearsal
    if args.action == 'dump':
        first, last = 1, 1
    else:
        last = args.last if args.last is not None else p['runs']
        first = args.first
        if not 1 <= first <= last <= p['runs']:
            ap.error(f'runs must be a nonempty subset of 1..{p["runs"]}')
    scale, pose, glass = p['scale'], p['pose'], p['glass']
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
        check_order(root, p, first, plan, declaration, cut)
    # A bridge's references are read and checked before anything launches (charter clause 3).
    refs, bars = (bridge_references(p), bridge_bars(p)) if p.get('bridge') else ({}, {})
    passdir = root / name
    passdir.mkdir(exist_ok=True)
    source_path = plan['sources'][p['source']]['path']

    def read_session():
        return json.loads(subprocess.check_output(session, text=True))

    for n in range(first, last + 1):
        if not rehearsal:
            check_order(root, p, n, plan, declaration, cut)
        if p['kind'] == 'dump':
            scheme = P.scheme_of(p['profile'])
            ids = list(p['scenes'])
            spec = write_doc(passdir, 'scenes-dump.json', P.dump_doc_from(plan, sources, p['name']))
        else:
            doc = P.derive_from(plan, sources, p['name'], n)
            spec = write_doc(passdir, f'scenes-run-{n}.json', doc)
            ids = P.capture_ids(doc)
        label = f'w43-{name}-{n}'
        run = passdir / f'run-{n}'
        if run.exists():
            raise ValueError('run already exists; keep it, do not overwrite or silently resume')
        run.mkdir()
        logfile = run / 'driver-idle.txt'      # .txt: the repository ignores *.log (W42 G1 phase 1)

        def log(line, logfile=logfile):
            with logfile.open('a') as f:
                f.write(f'{now()} {line}\n')

        def watch_log(line, run=run):
            with (run / 'watchdog.txt').open('a') as f:
                f.write(f'{now()} {line}\n')

        try:
            reverify(declaration, predeclaration)
            writes = slider_writes(root)
            problems = slider_problems(root, glass)
            if problems:
                raise ValueError('slider record refused: ' + '; '.join(problems))
            wait_for_idle(read_session, log, limit=idle_limit, poll=idle_poll)

            def attest(phase):
                raw = subprocess.check_output([*recorder, f'{label}-{phase}'])
                (run / f'attest.{phase}.json').write_bytes(raw)
                return json.loads(raw)

            def record(m, phase):
                return portable(m, phase, p=p, n=n, spec=spec, source_path=source_path, declaration=declaration,
                                rehearsal=rehearsal, slider_write=writes[-1] if writes else None)

            opened = attest('open')
            (run / 'attest.read').write_text(record(opened, 'open'))
            before = read_session()
            before_at = time.monotonic()
            (run / 'session-before.json').write_text(json.dumps(before, indent=2) + '\n')
            problems = []
            try:
                start = validate_machine(opened, scale, glass, census)
            except ValueError as error:
                problems.append(str(error))
            problems += session_problems(before)
            if problems:
                raise ValueError(' | '.join(problems))
            dog = Watchdog(read_session, pose, pin()['bundleIdentifier'], before, before_at, watch_log)
            if p['kind'] == 'dump':
                command = dump_argv(launcher, app, spec, run, scale, scheme, pose, ids)
                (run / 'launch.json').write_text(json.dumps(dict(argv=command), indent=2) + '\n')
                began, load_at_launch = time.monotonic(), [round(v, 2) for v in os.getloadavg()]
                code, timed_out = watched(command, dog, timeout=dump_timeout(len(ids)), poll=watch_poll,
                                          end_native=lambda: end_native(app))
                elapsed = round(time.monotonic() - began, 1)
                # The load average beside the rate (W42's b7 note): a dump's rate is
                # settle-dominated, and a loaded machine reads it pessimistically if at all.
                timing = dict(elapsedSeconds=elapsed, timeoutSeconds=dump_timeout(len(ids)),
                              perSceneSeconds=round(elapsed / len(ids), 3), scenes=len(ids),
                              loadAverageAtLaunch=load_at_launch,
                              loadAverageAtClose=[round(v, 2) for v in os.getloadavg()])
                (run / 'timing.json').write_text(json.dumps(timing, indent=2) + '\n')
                closed = attest('close')
                (run / 'attest.close').write_text(record(closed, 'close'))
                after = read_session()
                (run / 'session-after.json').write_text(json.dumps(after, indent=2) + '\n')
                if validate_machine(closed, scale, glass, census) != start:
                    raise ValueError('opening/closing state drift')
                if timed_out:
                    raise ValueError(f'dump-layers overran {dump_timeout(len(ids))} s')
                if code != 0:
                    raise ValueError(f'dump-layers exited {code}')
                report = sentinel_check(run / 'json', ids, glass, pose, scale, scheme)
                (run / 'check.json').write_text(json.dumps(report, indent=1) + '\n')
                if report['departures']:
                    raise ValueError(f'{len(report["departures"])} departure(s) from the declared slider position '
                                     f'{glass} or pose in the tree (X42), e.g. {report["departures"][0]}')
                entry = dict(protocol='dump', run=n, scenes=len(ids), departures=0, glass=glass,
                             normalOpacities=report['normalOpacities'],
                             checkSha256=sha((run / 'check.json').read_bytes()), timing=timing,
                             sitting=declaration['sitting'], planSha256=declaration['planSha256'],
                             declaration=declaration, **{'pass': p['name']})
                if rehearsal:
                    census_read = {phase: dict(count=m['foreignProcessCount'],
                                               names=sorted({Path(f['executable']).name
                                                             for f in m.get('foreignProcesses', [])}))
                                   for phase, m in (('open', opened), ('close', closed))}
                    (run / 'rehearsal.json').write_text(json.dumps(dict(
                        schema='w43-dump-rehearsal-1', outcome='dumped-and-checked', foreignCensus=census_read,
                        **entry), indent=2) + '\n')
                else:
                    (run / 'admission.json').write_text(json.dumps(dict(
                        schema='w43-dump-admission-1', admitted=True, dry=False, **entry), indent=2) + '\n')
                print(f'{name}: dumped and checked {len(ids)} scenes in {elapsed} s; Normal reads '
                      f'{report["normalOpacities"]} at slider {glass}', flush=True)
                continue
            env = {**os.environ, 'VITREA_SCENES': str(spec), 'VITREA_FIXTURES': str(run),
                   'VITREA_SCALE': str(scale)}
            with (run / 'producer-backgrounds.out').open('w') as f:
                subprocess.run([*harness, 'backgrounds'], env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
            command = capture_argv(launcher, app, spec, run, scale, label, p['protocol'], ids, pose)
            (run / 'launch.json').write_text(json.dumps(dict(argv=command), indent=2) + '\n')
            code, _ = watched(command, dog, poll=watch_poll, end_native=lambda: end_native(app))
            if code != 0:
                raise ValueError(f'the capture launch exited {code}')
            closed = attest('close')
            (run / 'attest.close').write_text(record(closed, 'close'))
            if validate_machine(closed, scale, glass, census) != start:
                raise ValueError('opening/closing state drift')
            raw = (run / 'manifest.json').read_bytes()
            m = json.loads(raw)
            validate_manifest(m, doc, pose, scale, label)
            cells = len(P.cells(doc))
            binding = frame_binding(run, m, doc, scale)
            problems = expectation_problems(p, binding['frames'])
            if problems:
                raise ValueError('a declared frame expectation failed: ' + '; '.join(problems))
            bridge = None
            if p.get('bridge'):
                bridge = bridge_report(p, n, run, m, doc, refs, bars)
                (run / 'bridge.json').write_text(json.dumps(bridge, indent=1) + '\n')
            admission = run_admission(p, n, command, m, sha(raw), cells, declaration, binding)
            if cut is not None:
                admission['cutAfter'] = cut
            if bridge is not None:
                admission['bridge'] = dict(agrees=bridge['agrees'], stop=bridge['stop'],
                                           verdicts={r['cell']: r['verdict'] for r in bridge['cells']},
                                           reportSha256=sha((run / 'bridge.json').read_bytes()))
            (run / 'admission.json').write_text(json.dumps(admission, indent=2) + '\n')
            print(f'{name} run {n}: admitted cells={cells}', flush=True)
            if bridge is not None and not bridge['agrees']:
                failing = {r['cell']: r['failing'][:3] for r in bridge['cells'] if not r['agrees']}
                message = f'{name} run {n}: the bridge DISAGREES with its references: {failing}'
                if p['bridge']['stop']:
                    raise BridgeStop(message + '; the sitting stops before any capture away from 0.5 (charter clause 3)')
                print(message + '; recorded, voiding nothing (a closing bridge; G2 reads the sitting unbridged, X43)',
                      file=sys.stderr, flush=True)
        except BaseException as error:
            if isinstance(error, BridgeStop):
                # Not a refusal: the run is admitted evidence with its bridge report beside it.
                print('STOPPED: ' + str(error), file=sys.stderr)
                raise
            if isinstance(error, Cancelled):
                # subprocess's child is already killed; the app itself is LaunchServices', not
                # ours, so it is ended by its executable image as a watchdog trip ends it.
                end_native(app)
            (run / 'refusal.txt').write_text(f'{type(error).__name__}: {error}\n')
            quarantine = run.with_name(f'QUARANTINE-run-{n}-{time.time_ns()}')
            run.rename(quarantine)
            print('REFUSED; retained at ' + str(quarantine), file=sys.stderr)
            raise


BRIDGE_STOP_EXIT = 10    # the orchestrator names an opening bridge's disagreement by this status

if __name__ == '__main__':
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, _cancel)
    try:
        main()
    except BridgeStop:
        sys.exit(BRIDGE_STOP_EXIT)
