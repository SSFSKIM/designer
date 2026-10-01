#!/usr/bin/env python3.12
"""W43 G0 (c): memo F's driver — Apple's declared glass tree at nine slider positions (clause 2).

    python3.12 -B memo_f.py run <run-root>              # detaches; follow <run-root>/logs/status.txt
    python3.12 -B memo_f.py run <run-root> --continue   # the parent's explicit continuation after a stop
    python3.12 -B memo_f.py restore <run-root>          # by hand, only after a SIGKILL or a power loss
    python3.12 -B memo_f.py check <launch-dir> --x X --scale S --scheme light|dark --pose active|inactive \
        --expect id,id,...                                # one launch's admission check (the driver runs it)

What it does, in `plan.json`'s order (written by `plan.py`; RUNBOOK.md is the operator's page):

1. **Nothing changes until the as-found slider is recorded.** The preflight reads the machine and
   refuses before any write: the build (macOS 27.0, 26A428), Reduce Transparency, Increase
   Contrast and Show Borders all 0, the display at mode 68, the side bundle's binary, cdhash and
   identifier against W39's `bundle-pin.json`, no harness process alive, the screen unlocked, no
   permission prompt and Universal Control not frontmost, then at least 300 s of HID idle. The
   as-found value of `NSGlassTintAmount` in the global domain is then read EXACTLY (`defaults
   export -g -` through `plutil -extract … xml1`, so a double that `-float` would round is kept
   bit for bit, and an absent key is recorded as absent) and written to `as-found.json` with an
   fsync, before the first write.
2. **One restore path, reached from every exit.** After the as-found record exists, the run is
   one `try … finally`. SIGHUP, SIGINT and SIGTERM raise inside it (further signals are ignored
   while it restores), as does every refusal and every unexpected error, so the restore runs on
   every path the process can see: it ends any harness process still running from the side
   bundle's binary, puts the slider back to the as-found bytes (or deletes the key if it was
   absent) and verifies the exported value byte for byte, returns the display to mode 68 and
   verifies it, and writes `restore.json`. Only SIGKILL or a power loss escapes it; then
   `memo_f.py restore <run-root>` does the same from `as-found.json` (RUNBOOK.md).
3. **A slider write is followed only by fresh launches.** A running application has already read
   its preferences (W29 G0's sweep; the charter review's confirmation), so before every write and
   every launch the driver refuses if any process whose executable is the harness is alive, and
   after every launch it refuses if the harness outlived it.
4. **Per block** (one slider position at one scale): the display mode (a switch waits for 300 s of
   HID idle first, memo D's rule), the harness-liveness check, `defaults write -g
   NSGlassTintAmount -float x`, and the read-back. Then **per endpoint**, one launch: HID idle at
   least 60 s (otherwise a pause until 300 s, all pauses capped together), the liveness check, the
   opening machine read (the X6 facts and the slider at x), `open -W` of the side bundle's
   `dump-layers` exactly as memo D launched it (`--settle 8`, `--require-key` or `--inactive`,
   an empty fixtures root), a 10-second session trace during the launch, memo D's overrun bound,
   the closing machine read, and `check`.
5. **`check`, the admission** (X42's second reading): exactly the expected scene files; each
   attests the declared scheme, scale, build and pose (`isKeyWindow` and `appIsActive` true when
   active, false when receded); every surface reads `inputBlurFillNormalOpacity` = x; and at
   x = 0.5 every surface reproduces memo D (`dumpcheck.py` against `dump-reference.json`, zero
   departures). A refusal quarantines the launch under its own name and stops the run; nothing is
   retried. A continuation is the parent's explicit act (`--continue`), which skips admitted
   launches and re-reads the as-found value, which must equal the record.

Stub mode, for the proof only: `MEMO_F_TOOLS=<dir>` replaces EVERY external tool and the bundle
together (`defaults`, `open`, `displayplacer`, `read-session`, `sw_vers`, `codesign`, the app,
its pin and the harness's executable name). None of them may resolve to a system or homebrew
binary or to the side bundle, and only in stub mode may the waits be shortened (`MEMO_F_FAST`).
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import signal
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PLAN = HERE / 'plan.json'
DUMPCHECK = REPO / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/dumps'
W39_PIN = REPO / 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/bundle-pin.json'
SCREEN = '7709FD0F-F423-4277-B0C8-7CA94F85723A'
BUILD, PRODUCT = '26A428', '27.0'
KEY = 'NSGlassTintAmount'
A11Y = (('com.apple.universalaccess', 'reduceTransparency'), ('com.apple.universalaccess', 'increaseContrast'),
        ('com.apple.Accessibility', 'ButtonShapesEnabled'))
PROMPTS = ('universalAccessAuthWarn',)
EXIT_DONE, EXIT_STOP, EXIT_REFUSED, EXIT_RESTORE_FAILED = 0, 3, 2, 7


class Refusal(Exception):
    """A gate, a check or a tool said no: the run stops here, and the restore runs."""


class Interrupted(Exception):
    pass


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with open(tmp, 'w') as f:
        f.write(json.dumps(value, indent=1, sort_keys=True) + '\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# ------------------------------------------------------------------ the tools

class Tools:
    def __init__(self):
        stub = os.environ.get('MEMO_F_TOOLS')
        self.stub = bool(stub)
        if stub:
            t = Path(stub).resolve()
            self.defaults, self.open, self.displayplacer = t / 'defaults', t / 'open', t / 'displayplacer'
            self.read_session, self.sw_vers, self.codesign = t / 'read-session', t / 'sw_vers', t / 'codesign'
            self.app, self.pin_file = t / 'VitreaReference.app', t / 'bundle-pin.json'
            self.harness = (t / 'harness-name').read_text().strip()
            forbidden = ('/usr/', '/bin/', '/sbin/', '/opt/homebrew/', '/System/', str(Path.home() / 'vitrea-w39'))
            for tool in (self.defaults, self.open, self.displayplacer, self.read_session, self.sw_vers, self.codesign,
                         self.app):
                real = os.path.realpath(tool)
                if not Path(real).exists() or any(real.startswith(f) for f in forbidden):
                    raise Refusal(f'stub mode: {tool} must be a stub, and resolves to {real}')
            if self.harness == 'VitreaReference':
                raise Refusal('stub mode: the stub harness may not carry the real harness name')
            fast = os.environ.get('MEMO_F_FAST') == '1'
        else:
            self.defaults, self.open = Path('/usr/bin/defaults'), Path('/usr/bin/open')
            self.displayplacer = Path('/opt/homebrew/bin/displayplacer')
            self.read_session = Path.home() / 'vitrea-w39/scratch/read-session'
            self.sw_vers, self.codesign = Path('/usr/bin/sw_vers'), Path('/usr/bin/codesign')
            self.pin_file = W39_PIN
            self.app = Path(json.loads(W39_PIN.read_text())['path'])
            self.harness = 'VitreaReference'
            fast = False
            if os.environ.get('MEMO_F_FAST'):
                raise Refusal('MEMO_F_FAST shortens the waits and is admitted in stub mode only')
        self.binary = self.app / 'Contents/MacOS' / self.harness
        self.poll = 0.2 if fast else 60.0           # the idle poll
        self.trace = 0.2 if fast else 10.0          # the session trace during a launch
        self.switch_settle = 0.0 if fast else 6.0   # displayplacer's settle
        self.kill_grace = 0.5 if fast else 5.0
        self.idle_start, self.idle_launch, self.idle_resume = 300.0, 60.0, 300.0
        # Every idle wait of a run (the start, the pauses, the switch) spends from one cap, memo D's 3 h.
        self.wait_cap = float(os.environ.get('MEMO_F_WAIT_CAP', 10800))

    def run(self, *args, check=False):
        r = subprocess.run([str(a) for a in args], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if check and r.returncode != 0:
            raise Refusal(f'{args[0]} {" ".join(map(str, args[1:3]))} exited {r.returncode}: {r.stderr.strip()[:200]}')
        return r

    # The slider, exactly: the exported XML of the one key, or None when the key is absent.
    def slider_xml(self):
        exported = subprocess.run([str(self.defaults), 'export', '-g', '-'], capture_output=True,
                                  stdin=subprocess.DEVNULL)
        if exported.returncode != 0:
            raise Refusal(f'defaults export -g failed: {exported.stderr.decode()[:200]}')
        domain = plistlib.loads(exported.stdout)
        if KEY not in domain:
            return None
        return plistlib.dumps(domain[KEY], fmt=plistlib.FMT_XML).decode()

    def slider_value(self):
        xml = self.slider_xml()
        return None if xml is None else plistlib.loads(xml.encode())

    def write_slider(self, x):
        self.run(self.defaults, 'write', '-g', KEY, '-float', repr(float(x)), check=True)

    def mode(self):
        out = self.run(self.displayplacer, 'list').stdout
        m = re.findall(r'^  mode (\d+):.*<-- current mode$', out, flags=re.M)
        return int(m[0]) if len(m) == 1 else None

    def set_mode(self, mode):
        self.run(self.displayplacer, f'id:{SCREEN} mode:{mode}')
        time.sleep(self.switch_settle)
        return self.mode()

    def session(self):
        r = self.run(self.read_session)
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            raise Refusal(f'read-session gave no reading: {r.stdout[:120]!r} {r.stderr[:120]!r}')

    def harness_alive(self):
        """Every process whose EXECUTABLE is the harness (never a command line that merely names it)."""
        out = self.run('ps', '-axo', 'pid=,comm=').stdout
        rows = [line.strip().split(None, 1) for line in out.splitlines() if line.strip()]
        return [(int(p), c) for p, c in (r for r in rows if len(r) == 2) if os.path.basename(c) == self.harness]

    def end_harness(self):
        """End every process running the side bundle's (or the stub's) binary; True if none remains."""
        target = os.path.realpath(self.binary)
        mine = [p for p, c in self.harness_alive() if os.path.realpath(c) == target]
        for sig in (signal.SIGTERM, signal.SIGKILL):
            for pid in mine:
                try:
                    os.kill(pid, sig)
                except ProcessLookupError:
                    pass
            deadline = time.time() + self.kill_grace
            while time.time() < deadline and any(p in mine for p, _ in self.harness_alive()):
                time.sleep(0.1)
            mine = [p for p, c in self.harness_alive() if os.path.realpath(c) == target]
            if not mine:
                return True
        return not mine


# ------------------------------------------------------------- the machine read

def machine(tools, phase):
    """The X6 facts as memo D and W42 read them, plus the slider read exactly and the session."""
    product = tools.run(tools.sw_vers, '-productVersion').stdout.strip()
    build = tools.run(tools.sw_vers, '-buildVersion').stdout.strip()
    a11y = {}
    for domain, key in A11Y:
        r = tools.run(tools.defaults, 'read', domain, key)
        a11y[f'{domain} {key}'] = r.stdout.strip() if r.returncode == 0 else None
    binary = tools.binary.read_bytes() if tools.binary.is_file() else b''
    sign = tools.run(tools.codesign, '-dvvv', tools.app)
    found = dict(re.findall(r'^(CDHash|Identifier)=(\S+)$', sign.stderr + sign.stdout, flags=re.M))
    appearance = tools.run(tools.defaults, 'read', '-g', 'AppleInterfaceStyle')
    return dict(phase=phase, at=now(), product=product, build=build, a11y=a11y,
                slider=dict(xml=tools.slider_xml(), value=tools.slider_value()),
                systemAppearance=appearance.stdout.strip() if appearance.returncode == 0 else 'Light',
                mode=tools.mode(), binarySha256=sha(binary) if binary else None, cdhash=found.get('CDHash'),
                identifier=found.get('Identifier'), harnessAlive=tools.harness_alive(), session=tools.session())


def gate(m, pin, want_mode, want_x):
    """The reasons a machine read refuses (an empty list admits)."""
    bad = []
    if (m['product'], m['build']) != (PRODUCT, BUILD):
        bad.append(f"OS {m['product']} {m['build']}, not {PRODUCT} {BUILD}")
    for name, value in m['a11y'].items():
        if value != '0':
            bad.append(f'{name} reads {value!r}, not 0')
    if m['mode'] != want_mode:
        bad.append(f"display mode {m['mode']}, not {want_mode}")
    for field, want in (('binarySha256', pin['binarySha256']), ('cdhash', pin['cdhash']),
                        ('identifier', pin['bundleIdentifier'])):
        if m[field] != want:
            bad.append(f'side bundle {field} {m[field]!r}, pinned {want!r}')
    if m['harnessAlive']:
        bad.append(f"a harness process is alive: {m['harnessAlive']}")
    if want_x is not None and m['slider']['value'] != want_x:
        bad.append(f"slider reads {m['slider']['value']!r}, declared {want_x!r}")
    s = m['session']
    if s.get('screenLocked'):
        bad.append('the screen is locked')
    owners = [o.split('|')[0] for o in s.get('windowOwners', [])]
    if any(p in owners for p in PROMPTS):
        bad.append(f'a permission prompt is on screen: {owners}')
    if s.get('frontmostIdentifier') == 'com.apple.universalcontrol':
        bad.append('Universal Control is frontmost')
    return bad


# ------------------------------------------------------------------ the check

def check_launch(directory, x, scale, scheme, pose, expect):
    """X42's tree reading and the pose, per scene file; at x = 0.5, memo D reproduced exactly."""
    sys.path.insert(0, str(DUMPCHECK))
    import dumpcheck as DC
    directory = Path(directory)
    files = {p.stem: p for p in sorted((directory / 'json').glob('*.json'))}
    reasons, surfaces = [], []
    if sorted(files) != sorted(expect):
        reasons.append(f'scene files {sorted(files)} are not the declared {sorted(expect)}')
    active = pose == 'active'
    for sid, path in sorted(files.items()):
        raw = json.loads(path.read_text())
        for field, want in (('colorScheme', scheme), ('backingScaleFactor', scale), ('isKeyWindow', active),
                            ('appIsActive', active), ('a11y', 'standard'), ('settleSeconds', 8)):
            if raw.get(field) != want:
                reasons.append(f'{sid}: {field} reads {raw.get(field)!r}, declared {want!r}')
        if BUILD not in str(raw.get('os')):
            reasons.append(f"{sid}: os {raw.get('os')!r}")
        recs = DC.records(path)
        if not recs:
            reasons.append(f'{sid}: no glass surface in the tree')
        for r in recs:
            normal = r.get('glassBackground.inputBlurFillNormalOpacity')
            ok = isinstance(normal, (int, float)) and abs(normal - x) <= 1e-6
            if not ok:
                reasons.append(f"{sid} surface {r['surface']}: inputBlurFillNormalOpacity {normal!r}, slider {x!r}")
            surfaces.append(dict(scene=sid, surface=r['surface'], normal=normal, sha256=sha(path.read_bytes())))
    memo_d = None
    if abs(x - 0.5) < 1e-12 and not reasons:
        reference = json.loads((DUMPCHECK / 'dump-reference.json').read_text())
        report = DC.check_dir(directory / 'json', scheme, 'active' if active else 'receded', scale, reference, expect)
        memo_d = dict(departures=report['departures'], unpredicted=report['unpredicted'],
                      referenceSha256=sha((DUMPCHECK / 'dump-reference.json').read_bytes()))
        if report['departures']:
            first = [d for s in report['surfaces'] for d in s['departures']][:5]
            reasons.append(f"x = 0.5 does not reproduce memo D: {report['departures']} departure(s), e.g. {first}")
    return dict(directory=str(directory), x=x, scale=scale, scheme=scheme, pose=pose, files=len(files),
                surfaces=surfaces, memoD=memo_d, admitted=not reasons, reasons=reasons)


# ------------------------------------------------------------------ the run

class Run:
    def __init__(self, root, tools, plan, cont):
        self.root, self.tools, self.plan, self.cont = Path(root), tools, plan, cont
        self.logs = self.root / 'logs'
        self.pin = json.loads(tools.pin_file.read_text())
        self.as_found = None
        self.changed = False      # True from the first slider write on
        self.switched = False     # True from the first display switch on
        self.restoring = False

    def say(self, text):
        line = f'{now()} {text}'
        with open(self.logs / 'status.txt', 'a') as f:
            f.write(line + '\n')
        print(line, flush=True)

    def interrupt(self, signum, _frame):
        if self.restoring:
            return
        raise Interrupted(signal.Signals(signum).name)

    def wait_idle(self, minimum, why, budget):
        """Wait for HID idle >= minimum, the screen unlocked and no prompt; spend from the shared budget."""
        start = time.time()
        while True:
            s = self.tools.session()
            owners = [o.split('|')[0] for o in s.get('windowOwners', [])]
            if any(p in owners for p in PROMPTS):
                raise Refusal(f'a permission prompt is on screen ({why}): {owners}')
            if s.get('idleSeconds', 0) >= minimum and not s.get('screenLocked'):
                return time.time() - start
            if time.time() - start >= budget[0]:
                raise Refusal(f'HID idle never reached {minimum:g} s within the wait cap ({why})')
            self.say(f'waiting for {minimum:g} s of HID idle ({why}): idle {s.get("idleSeconds", 0):.0f} s, '
                     f'locked {s.get("screenLocked")}')
            time.sleep(self.tools.poll)

    def idle_gate(self, budget, why):
        """memo D's gate.sh: pass at >= 60 s idle; otherwise pause until >= 300 s, from the shared cap."""
        s = self.tools.session()
        if s.get('idleSeconds', 0) >= self.tools.idle_launch and not s.get('screenLocked'):
            return
        self.say(f'idle {s.get("idleSeconds", 0):.0f} s < {self.tools.idle_launch:g} s before {why}: pausing until '
                 f'{self.tools.idle_resume:g} s')
        spent = self.wait_idle(self.tools.idle_resume, why, budget)
        budget[0] -= spent

    def record_as_found(self):
        path = self.root / 'as-found.json'
        xml = self.tools.slider_xml()
        if xml is not None:
            value = plistlib.loads(xml.encode())
            if not isinstance(value, float):
                raise Refusal(f'the as-found {KEY} is a {type(value).__name__} ({xml.strip()[:80]}); only a real is '
                              'restorable by this tool')
        record = dict(key=KEY, domain='NSGlobalDomain', present=xml is not None, xml=xml,
                      value=None if xml is None else plistlib.loads(xml.encode()), readAt=now())
        if self.cont:
            old = json.loads(path.read_text())
            if (old['present'], old['xml']) != (record['present'], record['xml']):
                raise Refusal(f"continuation: the slider reads {record['value']!r}, the recorded as-found "
                              f"{old['value']!r}: the last restore did not hold; restore by hand first")
            self.as_found = old
            self.say(f"continuation: the slider reads its recorded as-found value ({old['value']!r})")
            return
        write_json(path, record)
        self.as_found = record
        self.say(f"as-found {KEY}: {'absent' if xml is None else repr(record['value'])} (as-found.json, fsynced)")

    def restore(self, reason):
        """The one restore path: the harness ended, the slider and the display put back and verified."""
        self.restoring = True
        for s in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            signal.signal(s, signal.SIG_IGN)
        out = dict(reason=reason, at=now(), steps=[])
        ok = True
        try:
            ended = self.tools.end_harness()
            out['steps'].append(dict(step='harness', ended=ended, alive=self.tools.harness_alive()))
            ok &= ended
        except Exception as err:  # noqa: BLE001 (the restore continues past any one failure)
            out['steps'].append(dict(step='harness', error=repr(err)))
            ok = False
        if self.as_found is not None:
            try:
                current = self.tools.slider_xml()
                want = self.as_found['xml']
                if current != want:
                    if want is None:
                        self.tools.run(self.tools.defaults, 'delete', '-g', KEY, check=True)
                    else:
                        self.tools.run(self.tools.defaults, 'write', '-g', KEY, want.split('<plist version="1.0">')[1]
                                       .split('</plist>')[0].strip(), check=True)
                after = self.tools.slider_xml()
                held = after == want
                out['steps'].append(dict(step='slider', before=current, asFound=want, after=after, verified=held,
                                         wrote=current != want))
                ok &= held
            except Exception as err:  # noqa: BLE001
                out['steps'].append(dict(step='slider', error=repr(err)))
                ok = False
        try:
            mode = self.tools.mode()
            if mode != 68:
                mode = self.tools.set_mode(68)
            out['steps'].append(dict(step='display', mode=mode, verified=mode == 68))
            ok &= mode == 68
        except Exception as err:  # noqa: BLE001
            out['steps'].append(dict(step='display', error=repr(err)))
            ok = False
        out['verified'] = bool(ok)
        write_json(self.root / ('restore.json' if not (self.root / 'restore.json').exists()
                                else f'restore-{time.time_ns()}.json'), out)
        self.say(('restore: VERIFIED — ' if ok else 'RESTORE FAILED — ') +
                 '; '.join(f"{s['step']} {'ok' if s.get('verified', s.get('ended')) else s}" for s in out['steps']))
        return ok

    def launch(self, block, launch, budget):
        x, scale, scenes = block['x'], block['scale'], block['scenes']
        d = self.root / 'runs' / launch['label']
        if (d / 'admission.json').exists():
            self.say(f"{launch['label']}: admitted earlier; skipped")
            return
        if d.exists():
            raise Refusal(f'{d} exists without an admission: quarantine it by hand before a continuation')
        self.idle_gate(budget, launch['label'])
        alive = self.tools.harness_alive()
        if alive:
            raise Refusal(f'a harness process is alive before {launch["label"]}: {alive} (fresh launches only)')
        d.mkdir(parents=True)
        (d / 'no-fixtures').mkdir()
        opened = machine(self.tools, 'open')
        write_json(d / 'machine-open.json', opened)
        bad = gate(opened, self.pin, block['mode'], x)
        if bad:
            self.quarantine(d, launch, f'opening read refused: {bad}')
        argv = [str(self.tools.open), '-W']
        for k, v in (('VITREA_SCALE', scale), ('VITREA_SCENES', self.root / 'scenes.json'),
                     ('VITREA_FIXTURES', d / 'no-fixtures')):
            argv += ['--env', f'{k}={v}']
        argv += ['--stdout', str(d / 'dump.out'), '--stderr', str(d / 'dump.err'), str(self.tools.app), '--args',
                 'dump-layers', '--scenes', ','.join(scenes), '--settle', str(self.plan['settle']), '--scheme',
                 launch['scheme'], '--inactive' if launch['pose'] == 'inactive' else '--require-key',
                 '--out', str(d / 'json')]
        write_json(d / 'launch.json', dict(argv=argv, at=now()))
        limit = len(scenes) * (self.plan['settle'] + 1.5) + 90
        stop = threading.Event()

        def trace():
            with open(d / 'session-trace.jsonl', 'a') as f:
                while not stop.wait(self.tools.trace):
                    try:
                        f.write(json.dumps(dict(at=now(), **self.tools.session())) + '\n')
                        f.flush()
                    except Exception as err:  # noqa: BLE001 (a trace read never stops a launch)
                        f.write(json.dumps(dict(at=now(), error=repr(err))) + '\n')
        tracer = threading.Thread(target=trace, daemon=True)
        start = time.time()
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tracer.start()
        try:
            try:
                rc = proc.wait(timeout=limit)
            except subprocess.TimeoutExpired:
                self.tools.end_harness()
                proc.kill()
                proc.wait()
                self.quarantine(d, launch, f'dump-layers overran {limit:.0f} s')
        except Interrupted:
            proc.kill()
            raise
        finally:
            stop.set()
            tracer.join(timeout=2)
        seconds = time.time() - start
        time.sleep(0 if self.tools.stub else 1.0)
        outlived = self.tools.harness_alive()
        closed = machine(self.tools, 'close')
        write_json(d / 'machine-close.json', closed)
        if rc != 0:
            self.quarantine(d, launch, f'open -W exited {rc}')
        if outlived:
            self.quarantine(d, launch, f'the harness outlived its launch: {outlived}')
        bad = gate(closed, self.pin, block['mode'], x)
        if bad:
            self.quarantine(d, launch, f'closing read refused: {bad}')
        result = check_launch(d, x, scale, launch['scheme'], launch['pose'], scenes)
        write_json(d / 'check.json', result)
        if not result['admitted']:
            self.quarantine(d, launch, f"check refused: {result['reasons'][:4]}")
        write_json(d / 'admission.json', dict(label=launch['label'], x=x, scale=scale, scheme=launch['scheme'],
                                              pose=launch['pose'], scenes=len(scenes), seconds=round(seconds, 2),
                                              admittedAt=now(), memoD=result['memoD']))
        self.say(f"{launch['label']}: admitted, {len(scenes)} scenes in {seconds:.1f} s"
                 + (f", memo D reproduced ({result['memoD']['departures']} departures)" if result['memoD'] else ''))

    def quarantine(self, d, launch, why):
        q = d.with_name(f"QUARANTINE-{launch['label']}-{time.time_ns()}")
        d.rename(q)
        write_json(q / 'quarantine.json', dict(label=launch['label'], reason=why, at=now()))
        raise Refusal(f"{launch['label']} QUARANTINED ({q.name}): {why}")

    def block(self, block, budget):
        todo = [ln for ln in block['launches'] if not (self.root / 'runs' / ln['label'] / 'admission.json').exists()]
        if not todo:
            self.say(f"{block['label']}: admitted earlier; skipped")
            return
        if self.tools.mode() != block['mode']:
            self.say(f"{block['label']}: display to mode {block['mode']} after {self.tools.idle_resume:g} s of idle")
            budget[0] -= self.wait_idle(self.tools.idle_resume, f"the switch to mode {block['mode']}", budget)
            self.switched = True
            got = self.tools.set_mode(block['mode'])
            if got != block['mode']:
                raise Refusal(f"display mode {block['mode']} did not take (reads {got})")
        alive = self.tools.harness_alive()
        if alive:
            raise Refusal(f'a harness process is alive before the slider write: {alive} (fresh launches only)')
        self.changed = True
        self.tools.write_slider(block['x'])
        back = self.tools.slider_value()
        if back != block['x']:
            raise Refusal(f"the slider reads back {back!r} after writing {block['x']!r}")
        self.say(f"{block['label']}: slider {block['x']!r} written and read back")
        for launch in block['launches']:
            self.launch(block, launch, budget)

    def go(self):
        signal.signal(signal.SIGHUP, self.interrupt)
        signal.signal(signal.SIGINT, self.interrupt)
        signal.signal(signal.SIGTERM, self.interrupt)
        code, reason = EXIT_DONE, 'complete'
        self.say(f"memo F pid {os.getpid()}, plan {sha(PLAN.read_bytes())[:12]}, stub={self.tools.stub}, "
                 f"continue={self.cont}")
        try:
            pre = machine(self.tools, 'preflight')
            write_json(self.root / ('preflight.json' if not self.cont else f'preflight-{time.time_ns()}.json'), pre)
            bad = gate(pre, self.pin, 68, None)
            if bad:
                raise Refusal(f'preflight refused before any write: {bad}')
            spec = self.root / 'scenes.json'
            want = self.plan['scenesFile']
            raw = subprocess.run(['git', '-C', str(REPO), 'show', f"{want['commit']}:{want['path']}"],
                                 capture_output=True, check=True).stdout
            if sha(raw) != want['sha256']:
                raise Refusal('the scenes file at the pinned commit is not the pinned bytes')
            if spec.exists() and spec.read_bytes() != raw:
                raise Refusal('the run root holds another scenes file')
            spec.write_bytes(raw)
            budget = [self.tools.wait_cap]
            budget[0] -= self.wait_idle(self.tools.idle_start, 'the first write', budget)
            self.record_as_found()
            for block in self.plan['blocks']:
                self.block(block, budget)
            self.say('ALL BLOCKS ADMITTED')
        except Refusal as err:
            code, reason = EXIT_STOP, f'STOP: {err}'
            self.say(reason)
        except Interrupted as err:
            code, reason = EXIT_STOP, f'STOP: signal {err}'
            self.say(reason)
        except Exception as err:  # noqa: BLE001 (any error still reaches the restore)
            code, reason = EXIT_STOP, f'STOP: unexpected {err!r}'
            self.say(reason)
        finally:
            if self.as_found is not None or self.switched:
                if not self.restore(reason):
                    code = EXIT_RESTORE_FAILED
            else:
                self.say('nothing was changed: no as-found record yet, no write, no display switch')
        return code


def run_main(args):
    tools = Tools()
    root = Path(args.root).resolve()
    if str(root).startswith(str(REPO)) or str(root).startswith('/Users/new/Developer/'):
        raise SystemExit(f'REFUSE: the run root {root} is inside a checkout')
    plan = json.loads(PLAN.read_text())
    if args.cont:
        if not (root / 'as-found.json').exists():
            raise SystemExit('REFUSE: --continue needs the run root of a run that recorded its as-found value')
    elif args.detached_child:
        # The launcher below made this root and its logs/ a moment ago and nothing else: a fresh run's root
        # holds only logs/, never an as-found record or a run.
        if sorted(x.name for x in root.iterdir()) != ['logs']:
            raise SystemExit(f'REFUSE: {root} holds more than the launcher\'s logs/ (a new run takes a new root)')
    elif root.exists():
        raise SystemExit(f'REFUSE: {root} exists (a new run takes a new root; a continuation says --continue)')
    (root / 'logs').mkdir(parents=True, exist_ok=True)
    if not args.foreground:
        argv = [sys.executable, '-B', str(Path(__file__).resolve()), 'run', str(root), '--foreground']
        argv.append('--continue' if args.cont else '--detached-child')
        with open(root / 'logs' / 'console.txt', 'a') as console:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=console, stderr=subprocess.STDOUT,
                                     start_new_session=True)
        (root / 'logs' / 'driver.pid').write_text(f'{child.pid}\n')
        print(f'memo F: detached as pid {child.pid} in its own session; follow {root}/logs/status.txt')
        return 0
    return Run(root, tools, plan, args.cont).go()


def restore_main(args):
    root = Path(args.root).resolve()
    run = Run(root, Tools(), json.loads(PLAN.read_text()), cont=False)
    run.as_found = json.loads((root / 'as-found.json').read_text())
    return EXIT_DONE if run.restore('by hand (memo_f.py restore)') else EXIT_RESTORE_FAILED


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    r = sub.add_parser('run')
    r.add_argument('root')
    r.add_argument('--continue', dest='cont', action='store_true')
    r.add_argument('--foreground', action='store_true')
    r.add_argument('--detached-child', action='store_true', help=argparse.SUPPRESS)
    s = sub.add_parser('restore')
    s.add_argument('root')
    c = sub.add_parser('check')
    c.add_argument('directory')
    c.add_argument('--x', type=float, required=True)
    c.add_argument('--scale', type=int, choices=(1, 2), required=True)
    c.add_argument('--scheme', choices=('light', 'dark'), required=True)
    c.add_argument('--pose', choices=('active', 'inactive'), required=True)
    c.add_argument('--expect', required=True)
    args = ap.parse_args(argv)
    try:
        if args.action == 'run':
            return run_main(args)
        if args.action == 'restore':
            return restore_main(args)
        result = check_launch(args.directory, args.x, args.scale, args.scheme, args.pose, args.expect.split(','))
        print(json.dumps(result, indent=1))
        return 0 if result['admitted'] else 1
    except Refusal as err:
        print(f'REFUSE: {err}')
        return EXIT_REFUSED


if __name__ == '__main__':
    sys.exit(main())
