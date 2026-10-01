#!/usr/bin/env python3.12
"""W43 G0 (c): memo F's driver proved on a stub, red and green (writes proof.txt beside this file).

    python3.12 -B proof.py [case ...]

Every case builds a throwaway tools directory under /tmp from `stub/tool.py` (see its docstring)
and runs `memo_f.py run … --foreground` with `MEMO_F_TOOLS` naming it and `MEMO_F_FAST=1`. The
slider lives in a sandbox defaults domain written through the REAL /usr/bin/defaults, so the
as-found read, the writes and the exact restore are the real tool's; the global domain is never
written, the side bundle is never launched and the display is never switched. As a witness, the
proof reads (only reads) the machine's real `NSGlassTintAmount` and display mode before the first
case and after the last, and requires both unchanged.
"""
import json
import os
from pathlib import Path
import plistlib
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
DRIVER = HERE / 'memo_f.py'
GROUNDING = REPO / 'packages/calibration/results/2026-09-29-w42-grounding/scratch-sha256.txt'
TOOL_NAMES = ('defaults', 'open', 'displayplacer', 'read-session', 'sw_vers', 'codesign')
HARNESS = 'VitreaReferenceStub'
A11Y = [['com.apple.universalaccess', 'reduceTransparency'], ['com.apple.universalaccess', 'increaseContrast'],
        ['com.apple.Accessibility', 'ButtonShapesEnabled']]
PLAN = json.loads((HERE / 'plan.json').read_text())
LAUNCHES = sum(len(b['launches']) for b in PLAN['blocks'])


def stub_binary(path):
    """The stub harness: /bin/sleep under the stub's name, re-signed ad hoc. A platform binary copied
    elsewhere is killed at exec (SIGKILL), so an unsigned copy would never run and every liveness
    case would pass vacuously; the proof checks below that the stub harness really runs."""
    shutil.copy('/bin/sleep', path)
    subprocess.run(['codesign', '-f', '-s', '-', str(path)], check=True, capture_output=True)
    if subprocess.run([str(path), '0'], capture_output=True).returncode != 0:
        raise SystemExit(f'the stub harness {path} does not run')


def real_witness():
    """Read-only: the machine's real slider (exact) and display mode."""
    out = subprocess.run(['/usr/bin/defaults', 'export', '-g', '-'], capture_output=True, check=True).stdout
    value = plistlib.loads(out).get('NSGlassTintAmount')
    listing = subprocess.run(['/opt/homebrew/bin/displayplacer', 'list'], capture_output=True, text=True).stdout
    mode = [ln for ln in listing.splitlines() if ln.endswith('<-- current mode')]
    return dict(slider=None if value is None else repr(value), sliderType=type(value).__name__,
                mode=mode[0].split(':')[0].strip() if mode else None)


class Case:
    def __init__(self, name):
        self.name = name
        self.tmp = Path(tempfile.mkdtemp(prefix=f'memo-f-proof-{name}-'))
        self.tools = self.tmp / 'tools'
        self.root = self.tmp / 'run'
        self.sandbox = f'dev.vitrea.w43.memo-f-proof.{name}.{os.getpid()}'
        self.tools.mkdir()
        for n in TOOL_NAMES:
            shutil.copy(HERE / 'stub/tool.py', self.tools / n)
            (self.tools / n).chmod(0o755)
        (self.tools / 'harness-name').write_text(HARNESS + '\n')
        macos = self.tools / 'VitreaReference.app/Contents/MacOS'
        macos.mkdir(parents=True)
        stub_binary(macos / HARNESS)
        shutil.copy(GROUNDING, self.tools / 'scratch-sha256.txt')
        import hashlib
        binary = hashlib.sha256((macos / HARNESS).read_bytes()).hexdigest()
        (self.tools / 'bundle-pin.json').write_text(json.dumps(dict(
            path=str(self.tools / 'VitreaReference.app'), bundleIdentifier='dev.vitrea.memo-f.stub',
            binarySha256=binary, cdhash='0123456789abcdef0123456789abcdef01234567')))
        self.state = dict(sandbox=self.sandbox, a11yKeys=A11Y, a11y={f'{d} {k}': '0' for d, k in A11Y}, mode=68,
                          session=dict(idleSeconds=9999.0, screenLocked=False, frontmostIdentifier='com.apple.finder',
                                       frontmostPid=1, windowOwners=['Dock|20', 'Window Server|24']),
                          build='26A428', product='27.0', identifier='dev.vitrea.memo-f.stub',
                          cdhash='0123456789abcdef0123456789abcdef01234567', faults={})
        self.save()
        subprocess.run(['/usr/bin/defaults', 'write', self.sandbox, 'MemoFProofSandbox', '-int', '1'], check=True)

    def save(self):
        (self.tools / 'state.json').write_text(json.dumps(self.state, indent=1))

    def as_found(self, xml_value):
        if xml_value is None:
            subprocess.run(['/usr/bin/defaults', 'delete', self.sandbox, 'NSGlassTintAmount'], capture_output=True)
        else:
            subprocess.run(['/usr/bin/defaults', 'write', self.sandbox, 'NSGlassTintAmount', xml_value], check=True)

    def slider(self):
        out = subprocess.run(['/usr/bin/defaults', 'export', self.sandbox, '-'], capture_output=True, check=True).stdout
        return plistlib.loads(out).get('NSGlassTintAmount', 'ABSENT')

    def env(self):
        return {**os.environ, 'MEMO_F_TOOLS': str(self.tools), 'MEMO_F_FAST': '1', 'MEMO_F_WAIT_CAP': '3'}

    def run(self, *extra, root=None):
        r = subprocess.run([sys.executable, '-B', str(DRIVER), 'run', str(root or self.root), '--foreground', *extra],
                           capture_output=True, text=True, env=self.env())
        return r.returncode, r.stdout + r.stderr

    def spawn(self, *extra):
        return subprocess.Popen([sys.executable, '-B', str(DRIVER), 'run', str(self.root), '--foreground', *extra],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=self.env())

    def calls(self, tool=None):
        p = self.tools / 'calls.log'
        rows = [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []
        return [r for r in rows if tool is None or r['tool'] == tool]

    def slider_writes(self):
        return [c['argv'] for c in self.calls('defaults') if c['argv'][:1] in (['write'], ['delete'])
                and 'NSGlassTintAmount' in c['argv']]

    def admissions(self):
        return sorted(p.parent.name for p in (self.root / 'runs').glob('*/admission.json')) \
            if (self.root / 'runs').exists() else []

    def restore(self):
        p = self.root / 'restore.json'
        return json.loads(p.read_text()) if p.exists() else None

    def mode(self):
        return json.loads((self.tools / 'state.json').read_text())['mode']

    def alive(self):
        out = subprocess.run(['ps', '-axo', 'pid=,comm='], capture_output=True, text=True).stdout
        return [ln for ln in out.splitlines() if ln.strip().endswith('/' + HARNESS)]

    def close(self):
        for pid_line in self.alive():
            try:
                os.kill(int(pid_line.split()[0]), signal.SIGKILL)
            except (ProcessLookupError, ValueError):
                pass
        subprocess.run(['/usr/bin/defaults', 'delete', self.sandbox], capture_output=True)
        (Path.home() / f'Library/Preferences/{self.sandbox}.plist').unlink(missing_ok=True)
        shutil.rmtree(self.tmp, ignore_errors=True)


def wait_for(path, text, proc, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        if path.exists() and text in path.read_text():
            return True
        if proc.poll() is not None:
            return False
        time.sleep(0.05)
    return False


RESULTS = []


def expect(case, what, ok, detail=''):
    RESULTS.append((case, what, bool(ok), detail))


def green_full(name, as_found, want):
    c = Case(name)
    try:
        c.as_found(as_found)
        rc, out = c.run()
        rest = c.restore()
        expect(name, 'exit 0, every launch admitted', rc == 0 and len(c.admissions()) == LAUNCHES,
               f'rc {rc}, {len(c.admissions())} of {LAUNCHES} admitted')
        expect(name, 'the slider is back at its as-found bytes', c.slider() == want, f'{c.slider()!r}')
        expect(name, 'restore.json verified, display at 68', rest and rest['verified'] and c.mode() == 68)
        one = json.loads((c.root / 'runs/x0.25-1x-dark-inactive/machine-open.json').read_text())
        expect(name, 'the 1x block ran at mode 69 with the slider at 0.25', one['mode'] == 69
               and one['slider']['value'] == 0.25)
        memo = json.loads((c.root / 'runs/x0.5-2x-light-active/admission.json').read_text())['memoD']
        expect(name, 'x = 0.5 reproduces memo D (zero departures)', memo and memo['departures'] == 0)
        writes = c.slider_writes()
        expect(name, 'one write per block, then the restore', len(writes) == len(PLAN['blocks']) + (
            0 if c.slider() == 0.25 else 1), f'{len(writes)} slider writes')
        expect(name, 'no harness left running', not c.alive())
        return c, out
    finally:
        c.close()


def red(name, setup, *, phase, run_args=(), check=None):
    """A refusal: phase 'pre' changes nothing; phase 'run' stops and restores."""
    c = Case(name)
    try:
        c.as_found('<real>0.5</real>')
        setup(c)
        c.save()
        mode0 = c.mode()
        rc, out = c.run(*run_args)
        rest = c.restore()
        if phase == 'pre':
            expect(name, 'refused, and no slider write at all', rc in (2, 3) and not c.slider_writes()
                   and 'nothing was changed' in out or rc == 2 and not c.slider_writes(), f'rc {rc}: {out.strip()[-160:]}')
            expect(name, 'slider and display untouched', c.slider() == 0.5 and c.mode() == mode0,
                   f'{c.slider()!r}, mode {mode0} -> {c.mode()}')
        else:
            expect(name, 'stopped, restored and verified', rc == 3 and rest and rest['verified'],
                   f'rc {rc}: {out.strip()[-200:]}')
            expect(name, 'slider back at 0.5, display at 68, no harness alive',
                   c.slider() == 0.5 and c.mode() == 68 and not c.alive(), f'{c.slider()!r} {c.mode()} {c.alive()}')
        if check:
            check(c, rc, out)
        return rc, out
    finally:
        c.close()


def fault(**kw):
    def setup(c):
        c.state['faults'].update(kw)
    return setup


def signal_case(name, launch, sig):
    c = Case(name)
    try:
        c.as_found('<real>0.5</real>')
        c.state['faults'] = dict(slow=launch)
        c.save()
        proc = c.spawn()
        label = [ln['label'] for b in PLAN['blocks'] for ln in b['launches']][launch - 1]
        started = wait_for(c.tools / 'calls.log', '"open"', proc) and _wait_launch(c, launch, proc)
        time.sleep(0.5)
        live = c.alive()
        proc.send_signal(sig)
        out, _ = proc.communicate(timeout=60)
        rest = c.restore()
        expect(name, f'{signal.Signals(sig).name} during launch {launch} ({label}) stops the run', started
               and proc.returncode == 3 and f'signal {signal.Signals(sig).name}' in out, out.strip()[-200:])
        expect(name, 'the stub harness was really running when the signal came', bool(live), str(live))
        expect(name, 'restored: harness ended, slider 0.5, display 68, all verified', rest and rest['verified']
               and c.slider() == 0.5 and c.mode() == 68 and not c.alive(), json.dumps(rest)[:200] if rest else '')
    finally:
        c.close()


def _wait_launch(c, n, proc, timeout=120):
    end = time.time() + timeout
    while time.time() < end:
        if len(c.calls('open')) >= n:
            return True
        if proc.poll() is not None:
            return False
        time.sleep(0.05)
    return False


def main(selected):
    witness = real_witness()
    cases = {
        'green-present': lambda: green_full('green-present', '<real>0.5</real>', 0.5),
        'green-absent': lambda: green_full('green-absent', None, 'ABSENT'),
        'green-odd': lambda: green_full('green-odd', '<real>0.5459057092666626</real>', 0.5459057092666626),
        'red-build': lambda: red('red-build', lambda c: c.state.update(build='26A429'), phase='pre'),
        'red-a11y': lambda: red('red-a11y', lambda c: c.state['a11y'].update(
            {'com.apple.universalaccess reduceTransparency': '1'}), phase='pre'),
        'red-a11y-absent': lambda: red('red-a11y-absent', lambda c: c.state['a11y'].pop(
            'com.apple.Accessibility ButtonShapesEnabled'), phase='pre'),
        'red-pin': lambda: red('red-pin', lambda c: c.state.update(cdhash='f' * 40), phase='pre'),
        'red-mode-at-start': lambda: red('red-mode-at-start', lambda c: c.state.update(mode=69), phase='pre'),
        'red-universal-control': lambda: red('red-universal-control', lambda c: c.state['session'].update(
            frontmostIdentifier='com.apple.universalcontrol'), phase='pre'),
        'red-prompt': lambda: red('red-prompt', lambda c: c.state['session'].update(
            windowOwners=['universalAccessAuthWarn|0']), phase='pre'),
        'red-locked': lambda: red('red-locked', lambda c: c.state['session'].update(screenLocked=True),
                                  phase='pre'),
        'red-idle-cap': lambda: red('red-idle-cap', lambda c: c.state['session'].update(idleSeconds=10.0),
                                    phase='pre'),
        'red-harness-alive-at-start': red_alive_at_start,
        'red-string-as-found': red_string_as_found,
        'red-orphan': lambda: red('red-orphan', fault(orphan=2), phase='run', check=lambda c, rc, out: expect(
            'red-orphan', 'the outliving harness is named, and the next write never happens',
            'outlived its launch' in out and len(c.slider_writes()) == 1, f'{len(c.slider_writes())} writes')),
        'red-stale': lambda: red('red-stale', fault(stale=5), phase='run', check=lambda c, rc, out: expect(
            'red-stale', 'a dump at the previous slider is refused by its tree reading (X42)',
            'inputBlurFillNormalOpacity 0.5, slider 0.25' in out and any(
                p.name.startswith('QUARANTINE-x0.25-2x-light-active') for p in (c.root / 'runs').iterdir()))),
        'red-unkey': lambda: red('red-unkey', fault(unkey=1), phase='run', check=lambda c, rc, out: expect(
            'red-unkey', 'a lost focus is refused by the pose attestation', 'isKeyWindow reads False' in out)),
        'red-depart': lambda: red('red-depart', fault(depart=3), phase='run', check=lambda c, rc, out: expect(
            'red-depart', 'at x = 0.5 a departure from memo D refuses', 'does not reproduce memo D' in out)),
        'red-missing': lambda: red('red-missing', fault(missing=7), phase='run', check=lambda c, rc, out: expect(
            'red-missing', 'a missing scene file refuses', 'are not the declared' in out)),
        'red-fail': lambda: red('red-fail', fault(fail=4), phase='run', check=lambda c, rc, out: expect(
            'red-fail', 'a nonzero open -W refuses', 'open -W exited 1' in out)),
        'red-mode-sticks': lambda: red('red-mode-sticks', fault(modeSticks=True), phase='run',
                                       check=lambda c, rc, out: expect(
            'red-mode-sticks', 'a display switch that does not take refuses before the 1x write',
            'display mode 69 did not take' in out and len(c.slider_writes()) == len(PLAN['blocks']))),
        'red-restore-fails': red_restore_fails,
        'red-sigterm': lambda: signal_case('red-sigterm', 6, signal.SIGTERM),
        'red-sigint-1x': lambda: signal_case('red-sigint-1x', LAUNCHES - 1, signal.SIGINT),
        'red-sighup': lambda: signal_case('red-sighup', 2, signal.SIGHUP),
        'green-continue': green_continue,
        'red-root-in-repo': red_root_in_repo,
        'red-real-tool': red_real_tool,
        'red-fast-real': red_fast_real,
    }
    for name in (selected or cases):
        try:
            cases[name]()
        except Exception as err:  # noqa: BLE001 (a crashed case is a failed case)
            expect(name, 'the case ran', False, repr(err))
    after = real_witness()
    expect('witness', "the machine's real slider and display mode are unchanged", witness == after,
           f'{witness} -> {after}')
    lines = [f'memo F driver proof: {sum(ok for *_, ok, _ in RESULTS)} of {len(RESULTS)} expectations hold '
             f'over {len({c for c, *_ in RESULTS})} cases', f'real witness before {witness}, after {after}', '']
    for case, what, ok, detail in RESULTS:
        lines.append(f"{'PASS' if ok else 'FAIL'}  {case:28s} {what}" + (f'  [{detail}]' if detail and not ok else ''))
    text = '\n'.join(lines) + '\n'
    if not selected:
        (HERE / 'proof.txt').write_text(text)
    print(text)
    return 0 if all(ok for *_, ok, _ in RESULTS) else 1


def red_alive_at_start():
    name = 'red-harness-alive-at-start'
    c = Case(name)
    try:
        c.as_found('<real>0.5</real>')
        stray = c.tmp / 'stray' / HARNESS
        stray.parent.mkdir()
        stub_binary(stray)
        p = subprocess.Popen([str(stray), '20'])
        try:
            rc, out = c.run()
        finally:
            p.kill()
            p.wait()
        expect(name, 'a live harness refuses before any write', rc == 3 and 'a harness process is alive' in out
               and not c.slider_writes() and c.slider() == 0.5, out.strip()[-160:])
    finally:
        c.close()


def red_string_as_found():
    name = 'red-string-as-found'
    c = Case(name)
    try:
        c.as_found('<string>0.5</string>')
        rc, out = c.run()
        expect(name, 'an as-found it cannot restore exactly refuses before any write',
               rc == 3 and 'only a real is restorable' in out and not c.slider_writes(), out.strip()[-160:])
        expect(name, 'the string is untouched', c.slider() == '0.5')
    finally:
        c.close()


def red_restore_fails():
    name = 'red-restore-fails'
    c = Case(name)
    try:
        c.as_found('<real>0.5</real>')
        c.state['faults'] = dict(unkey=5, restoreFails=True)
        c.save()
        rc, out = c.run()
        rest = c.restore()
        expect(name, 'a failed restore exits 7 and says RESTORE FAILED', rc == 7 and 'RESTORE FAILED' in out
               and rest and not rest['verified'], out.strip()[-160:])
        c.state['faults'] = {}
        c.save()
        r = subprocess.run([sys.executable, '-B', str(DRIVER), 'restore', str(c.root)], capture_output=True,
                           text=True, env=c.env())
        expect(name, '`memo_f.py restore` by hand then restores and verifies', r.returncode == 0
               and c.slider() == 0.5 and c.mode() == 68, r.stdout[-160:])
    finally:
        c.close()


def green_continue():
    name = 'green-continue'
    c = Case(name)
    try:
        c.as_found('<real>0.5</real>')
        c.state['faults'] = dict(stale=9)
        c.save()
        rc1, out1 = c.run()
        first = c.admissions()
        c.state['faults'] = {}
        c.save()
        rc2, out2 = c.run('--continue')
        expect(name, 'the first run stops at launch 9 after 8 admissions', rc1 == 3 and len(first) == 8,
               f'rc {rc1}, {len(first)}')
        expect(name, 'the continuation skips them and completes', rc2 == 0 and len(c.admissions()) == LAUNCHES
               and out2.count('admitted earlier; skipped') >= 2, out2.strip()[-200:])
        expect(name, 'the quarantine is kept under its own name',
               any(p.name.startswith('QUARANTINE-x1-2x-light-active') for p in (c.root / 'runs').iterdir()))
        expect(name, 'restored after the continuation', c.slider() == 0.5 and c.mode() == 68)
        c2 = Case(name + '-unrestored')
        try:
            c2.as_found('<real>0.5</real>')
            c2.state['faults'] = dict(stale=5)
            c2.save()
            c2.run()
            c2.as_found('<real>0.25</real>')          # as if the restore had not held
            rc3, out3 = c2.run('--continue')
            expect(name, 'a continuation refuses when the slider is not at its recorded as-found value',
                   rc3 == 3 and 'did not hold' in out3, out3.strip()[-160:])
        finally:
            c2.close()
    finally:
        c.close()


def red_root_in_repo():
    name = 'red-root-in-repo'
    c = Case(name)
    try:
        rc, out = c.run(root=HERE / 'not-a-run-root')
        expect(name, 'a run root inside the checkout refuses', rc != 0 and 'inside a checkout' in out
               and not (HERE / 'not-a-run-root').exists() and not c.calls(), out.strip()[-120:])
    finally:
        c.close()


def red_real_tool():
    name = 'red-real-tool'
    c = Case(name)
    try:
        (c.tools / 'defaults').unlink()
        (c.tools / 'defaults').symlink_to('/usr/bin/defaults')
        rc, out = c.run()
        expect(name, 'a stub tools directory holding a real tool refuses', rc == 2 and 'must be a stub' in out,
               out.strip()[-160:])
    finally:
        c.close()


def red_fast_real():
    name = 'red-fast-real'
    env = {k: v for k, v in os.environ.items() if k != 'MEMO_F_TOOLS'}
    env['MEMO_F_FAST'] = '1'
    root = Path(tempfile.mkdtemp(prefix='memo-f-proof-fast-')) / 'run'
    r = subprocess.run([sys.executable, '-B', str(DRIVER), 'run', str(root), '--foreground'], capture_output=True,
                       text=True, env=env)
    expect(name, 'the shortened waits refuse outside stub mode, before any tool runs',
           r.returncode == 2 and 'stub mode only' in r.stdout and not root.exists(), r.stdout[-160:])
    shutil.rmtree(root.parent, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
