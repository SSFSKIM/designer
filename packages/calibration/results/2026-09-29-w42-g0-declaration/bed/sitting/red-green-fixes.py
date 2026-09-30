#!/usr/bin/env python3.12
"""Red/green proofs of the bed review's sitting fixes (B-M1, B-M2, b2, b3) and of the verification
round's (53400aa5: findings 1-5), stubs only.

Each scenario runs twice in a throwaway Mirror checkout (test_sitting.Mirror): once with the
PRE-FIX tools and once with the fixed ones. Round 1's pre-fix tools are sitting.py,
sitting-orchestrate.sh and w42_archive.py at the fix branch's base, 9a695ec0; round 2's are
those and pass-spec.py at 3da63224, the round-1 fixes the verification review read, and, for
the exposure race, runner.claim_exposure as it stood there. RED is the defect the review named,
observed on the pre-fix tools; GREEN is the fix refusing or behaving. Nothing native is
launched: the machine recorder, session reader, harness, launcher, driver, native app and
displayplacer are the suites' stubs, and the race runs against a bare local origin.

Run: python3.12 -B red-green-fixes.py > red-green-fixes.txt    (from this directory)
Exit 0 iff every scenario is red before and green after.
"""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_sitting as T      # noqa: E402  (the suites' stubs and Mirror)
import test_archive as TA     # noqa: E402

BASE = '9a695ec0'
TOOLS = ('sitting.py', 'sitting-orchestrate.sh', 'w42_archive.py')
STALE = T.STALE_BED
results = []


def at(commit, path):
    rel = Path(path).resolve().relative_to(T.REPO)
    return subprocess.run(['git', '-C', str(T.REPO), 'show', f'{commit}:{rel}'], check=True,
                          capture_output=True).stdout


def mirror(tmp, pre_fix, extra=None, base=BASE, tools=TOOLS):
    replace = {(HERE / n).relative_to(T.REPO): at(base, HERE / n) for n in tools} if pre_fix else {}
    replace.update(extra or {})
    return T.Mirror(tmp, replace)


def record(name, red, green, red_ok, green_ok, base=BASE):
    results.append(red_ok and green_ok)
    print(f'{name}\n  RED   (pre-fix {base}): {red}  [{"defect shown" if red_ok else "NOT SHOWN"}]\n'
          f'  GREEN (fix): {green}  [{"fixed" if green_ok else "NOT FIXED"}]\n', flush=True)


print('== Round 1: the bed review of b151aff4 ==\n')


# ------------------------------------------------------------------ B-M1: the launch

def damage_one_byte(m, repin):
    T.one_byte_edit(m.bed / 'scenes-w42-body.json')
    if repin:
        m.repin()
        m.commit('a one-byte scenes edit, re-pinned')


def damage_stale_pair(m):
    for name in ('scenes-w42-body.json', 'bed.json'):
        (m.bed / name).write_bytes(at(STALE, T.BED_DIR / name))
    m.repin()
    m.commit('the previous declaration (764217e1), re-pinned')


def launch(pre_fix, damage):
    with tempfile.TemporaryDirectory() as tmp:
        m = mirror(tmp, pre_fix)
        damage(m)
        st = T.Stubs(tmp)
        root = Path(tmp) / 'rehearsal-root'
        out = m.sitting_py('capture', '2x-light-active', '--rehearse-refusal',
                           env={**st.env, 'VITREA_SITTING_DIR': str(root), 'STUB_MODE': 'tcc'})
        launched = any('capture' in c for c in st.calls_made())
        last = (out.stderr.strip().splitlines() or [''])[-1][:150]
        return launched, f'exit {out.returncode}, launched={launched}; {last}'


for name, damage in (('B-M1 scenes edited by one byte, pins.json untouched', lambda m: damage_one_byte(m, False)),
                     ('B-M1 scenes edited by one byte, re-pinned and committed', lambda m: damage_one_byte(m, True)),
                     ('B-M1 a stale bed (764217e1 scenes + bed.json), re-pinned and committed', damage_stale_pair)):
    red_launched, red = launch(True, damage)
    green_launched, green = launch(False, damage)
    record(name, red, green, red_launched, not green_launched)


# ------------------------------------------------------------ B-M1 and B-M2: produce

_ARCHIVES = {}


def archive_module(tmp, pre_fix):
    if pre_fix not in _ARCHIVES:
        m = mirror(Path(tmp) / ('pre' if pre_fix else 'fix'), pre_fix)
        _ARCHIVES[pre_fix] = T.load(f'w42_archive_{"pre" if pre_fix else "fix"}', m.sitting / 'w42_archive.py')
    return _ARCHIVES[pre_fix]


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    raw = tmp / 'raw'
    TA.sitting_tree(raw)
    wave = TA.A.wave_module().default_wave()
    wider = copy.copy(wave)
    wider.bed = copy.deepcopy(wave.bed)
    wider.bed['passes'][TA.KEY]['cells'].append('h-p1-c24-rrect-112')   # declared, never captured
    outcomes = {}
    for pre_fix in (True, False):
        A = archive_module(tmp, pre_fix)
        try:
            inv = A.produce(raw, tmp / f'out-uncaptured-{pre_fix}', wave=wider, passes=TA.PASSES)
            outcomes[pre_fix] = (True, f'archive written; uncaptured={inv["uncaptured"]}')
        except ValueError as error:
            outcomes[pre_fix] = (False, f'refused: {str(error)[:120]}')
    record('B-M1 produce with a declared cell never captured', outcomes[True][1], outcomes[False][1],
           outcomes[True][0], not outcomes[False][0])

    held = {s for s, r in wave.roles.items() if r == 'holdout'}
    stats = {}
    for pre_fix in (True, False):
        A = archive_module(tmp, pre_fix)
        out = tmp / f'out-{pre_fix}'
        inv = A.produce(raw, out, wave=wave, passes=TA.PASSES)
        leaked = sorted({k for r in inv['operational'] if r['path'].endswith('manifest.json')
                         for p in json.loads((out / r['path']).read_text())['profiles'] for f in p['fixtures']
                         if f['sceneId'] in held for k in f if k in TA.PIXEL_STATISTICS})
        guarded = len(inv.get('holdoutOperational', []))
        stats[pre_fix] = (leaked, f'operational manifests carry H pixel statistics {leaked or "none"}; '
                                  f'holdoutOperational entries {guarded}')
    record('B-M2 the operational manifests of a synthetic run', stats[True][1], stats[False][1],
           bool(stats[True][0]), not stats[False][0])


# ------------------------------------------------------------------ b2: PNG bytes

def capture_without_pngs(pre_fix):
    with tempfile.TemporaryDirectory() as tmp:
        m = mirror(tmp, pre_fix)
        st = T.Stubs(tmp, scale=1)
        st.admit_before('1x-light-active')
        doc = T.P.derive('1x-light-active', 1)
        (st.tmp / 'manifest.json').write_text(json.dumps(T.manifest(doc, 'active', 1, 'w42-1x-light-active-1')))
        out = m.sitting_py('capture', '1x-light-active', '1', '1', env={**st.env, 'STUB_MODE': 'no-png'})
        admitted = (st.root / '1x-light-active' / 'run-1' / 'admission.json').is_file()
        last = (out.stderr.strip().splitlines() or [''])[-1][:120]
        return admitted, f'exit {out.returncode}, admitted={admitted}; {last}'


red_admitted, red = capture_without_pngs(True)
green_admitted, green = capture_without_pngs(False)
record('b2 a capture run whose manifest names PNGs that do not exist', red, green, red_admitted, not green_admitted)


# --------------------------------------------------------------- b3: the orchestrator

def orchestrate(pre_fix, driver_mode='ok', extra=None):
    with tempfile.TemporaryDirectory() as tmp:
        m = mirror(tmp, pre_fix, extra)
        (m.sitting / 'run-sitting-w42.sh').write_text(T.STUB_DRIVER)
        m.commit('the stub driver')
        st = T.Stubs(tmp, scale=1)
        dp, state, _ = T.stub_displayplacer(tmp)
        calls = Path(tmp) / 'driver-calls.txt'
        env = {**T.os.environ, **st.env, 'DISPLAYPLACER': str(dp), 'STUB_IDLE': '400', 'W42_FOREGROUND': '1',
               'STUB_DRIVER_CALLS': str(calls), 'STUB_DRIVER_MODE': driver_mode}
        for k in ('W42_ORCHESTRATED', 'START_AT', 'STOP_AFTER', 'PASSES', 'REHEARSAL', 'W42_PREDECLARATION'):
            env.pop(k, None)
        out = subprocess.run(['bash', str(m.sitting / 'sitting-orchestrate.sh')], env=env, capture_output=True,
                             text=True, timeout=300)
        n = len(calls.read_text().splitlines()) if calls.exists() else 0
        status = (st.root / 'logs' / 'orchestrator-status.txt').read_text().strip().splitlines()
        verdict = next((l.split(' ', 1)[1] for l in reversed(status) if 'DONE' in l or 'STOP' in l), '')
        return out.returncode, n, f'exit {out.returncode}, driver called {n} of 24 passes; "{verdict[:90]}"'


rc, n, red = orchestrate(True, 'swallow')
grc, gn, green = orchestrate(False, 'swallow')
record('b3 a driver that reads stdin, over the whole order', red, green, rc == 0 and n < 24, grc == 0 and gn == 24)

broken = {(HERE / 'pass-spec.py').relative_to(T.REPO): b'import sys\nsys.exit(3)\n'}
rc, n, red = orchestrate(True, extra=broken)
grc, gn, green = orchestrate(False, extra=broken)
record('b3 a pass-spec.py order that fails', red, green, rc == 0, grc != 0 and gn == 0)

# ======================================================================= round 2
print('== Round 2: the verification review of the fixes (53400aa5) ==\n')
BASE2 = '3da63224'
TOOLS2 = ('sitting.py', 'pass-spec.py', 'sitting-orchestrate.sh', 'w42_archive.py')


def mirror2(tmp, pre_fix):
    return mirror(tmp, pre_fix, base=BASE2, tools=TOOLS2)


# 1. provenance: grey-128 edited between two runs of one driver invocation
def edited_between_runs(pre_fix):
    with tempfile.TemporaryDirectory() as tmp:
        m = mirror2(tmp, pre_fix)
        st = T.Stubs(tmp, scale=1)
        st.admit_before('1x-light-active')
        scenes = m.bed / 'scenes-w42-body.json'
        env = {**st.env, 'STUB_AUTO': '1', 'STUB_TEST_DIR': str(HERE), 'STUB_EDIT_SCENES': str(scenes)}
        out = m.sitting_py('capture', '1x-light-active', '1', '2', env=env)
        base = st.root / '1x-light-active'
        two = base / 'run-2' / 'admission.json'
        launches = len([c for c in st.calls_made() if 'capture' in c])
        if two.is_file():
            level = json.loads((base / 'scenes-run-2.json').read_text())['backgrounds']['grey-128']['srgb']
            recorded = json.loads(two.read_text())['scenesSha256'][:12]
            return True, (f'exit {out.returncode}; run 2 ADMITTED, its document has grey-128 {level} while the '
                          f'admission names scenes {recorded} (the pinned bytes); {launches} launches')
        q = list(base.glob('QUARANTINE-run-2-*'))
        why = (q[0] / 'refusal.txt').read_text().strip()[:110] if q else 'no record'
        return False, f'exit {out.returncode}; run 2 refused before launch ({why}); {launches} launch'


red_ok, red = edited_between_runs(True)
green_bad, green = edited_between_runs(False)
record('1. provenance: the scenes file edited (grey-128 128 -> 129) between runs 1 and 2', red, green,
       red_ok, not green_bad, BASE2)


# 2. the harness's run summary through public_log
def archive_module2(tmp, pre_fix):
    m = mirror2(Path(tmp) / ('pre2' if pre_fix else 'fix2'), pre_fix)
    return T.load(f'w42_archive_round2_{"pre" if pre_fix else "fix"}', m.sitting / 'w42_archive.py')


with tempfile.TemporaryDirectory() as tmp:
    held = {s for s, r in TA.A.wave_module().default_wave().roles.items() if r == 'holdout'}
    log = ('capturing 23 fixtures via screencapturekit at 1.0x (interleaved)\n'
           '  [1/23] apple-macos-27.0-1x-light-standard-glass0.5/h-g232-rrect-md__rest byte-stable EMPTY(==background)\n'
           'manifest → /raw/1x-light-active/run-1/manifest.json\n' + TA.CAVEAT + '\n').encode()
    kept = {pre: 'PIXEL-IDENTICAL' in archive_module2(tmp, pre).public_log(log, held).decode() for pre in (True, False)}
    record('2. the real "CAVEAT: 1 of 23 fixtures are PIXEL-IDENTICAL ..." line through public_log()',
           f'the public log keeps it: {kept[True]}', f'the public log keeps it: {kept[False]}',
           kept[True], not kept[False], BASE2)


# 3. SIGTERM mid-capture, a blocking launch at mode 69
def cancel_mid_capture(pre_fix):
    tmp = Path(tempfile.mkdtemp(prefix='w42-rg-cancel-'))
    m = mirror2(tmp, pre_fix)
    st = T.Stubs(tmp, scale=1)
    st.admit_before('1x-light-active')
    dp, state, _ = T.stub_displayplacer(tmp)
    pids = tmp / 'pids.json'
    env = {**os.environ, **st.env, 'DISPLAYPLACER': str(dp), 'STUB_IDLE': '400', 'W42_FOREGROUND': '1',
           'START_AT': '1x-light-active', 'STUB_MODE': 'block', 'STUB_PIDS': str(pids),
           'STUB_NATIVE': T.PIN['path'] + '/Contents/MacOS/VitreaReference'}
    for k in ('W42_ORCHESTRATED', 'STOP_AFTER', 'PASSES', 'REHEARSAL', 'W42_PREDECLARATION'):
        env.pop(k, None)
    proc = subprocess.Popen(['bash', str(m.sitting / 'sitting-orchestrate.sh')], env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 90
    while not pids.exists() and time.monotonic() < deadline:
        time.sleep(0.2)
    launched = json.loads(pids.read_text())
    proc.send_signal(signal.SIGTERM)
    time.sleep(12)
    alive = [n for n, pid in launched.items() if not T.gone(pid, within=0.1)]
    text = (f'12 s after SIGTERM: orchestrator {"running" if proc.poll() is None else f"exited {proc.poll()}"}, '
            f'display mode {state.read_text()}, still alive: {alive or "none"}')
    stuck = proc.poll() is None and state.read_text() == '69'
    for pid in launched.values():          # clean the red run up; the pre-fix tools never do
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    proc.wait(timeout=120)
    shutil.rmtree(tmp, ignore_errors=True)
    return stuck, text, alive


red_stuck, red, _ = cancel_mid_capture(True)
green_stuck, green, green_alive = cancel_mid_capture(False)
record('3. SIGTERM to the orchestrator mid-capture, the launch blocking, at mode 69', red, green,
       red_stuck, not green_stuck and not green_alive, BASE2)


# 4. the exposure race: two clones, one HEAD, configuration, identity and tagger second
sys.path.insert(0, str(HERE.parent / 'exposure'))
import runner  # noqa: E402
source = at(BASE2, HERE.parent / 'exposure' / 'runner.py').decode()
tree = ast.parse(source)
old_claim = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'claim_exposure')
space = dict(subprocess=subprocess, hashlib=hashlib, Path=Path, stable=runner.stable)
exec(compile(ast.Module(body=[old_claim], type_ignores=[]), 'runner@3da63224', 'exec'), space)


def race(claim, shim):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origin, a = tmp / 'origin.git', tmp / 'a'
        subprocess.run(['git', 'init', '-q', '--bare', str(origin)], check=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(a)], check=True)
        for repo in (a,):
            subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 't@example.invalid'], check=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'T'], check=True)
        (a / 'x').write_text('x\n')
        subprocess.run(['git', '-C', str(a), 'add', 'x'], check=True)
        subprocess.run(['git', '-C', str(a), 'commit', '-qm', 'x'], check=True)
        subprocess.run(['git', '-C', str(a), 'remote', 'add', 'origin', str(origin)], check=True)
        subprocess.run(['git', '-C', str(a), 'push', '-q', 'origin', 'main'], check=True)
        b = tmp / 'b'
        subprocess.run(['git', 'clone', '-q', '-b', 'main', str(origin), str(b)], check=True)
        configuration = dict(manifestSha256='m' * 64, mode='synthetic')
        stamp = {'GIT_COMMITTER_NAME': 'Same Tagger', 'GIT_COMMITTER_EMAIL': 'same@example.invalid',
                 'GIT_COMMITTER_DATE': '2026-10-01T00:00:00+0000'}
        with mock.patch.dict(os.environ, stamp):
            first = claim(a, None, 'w42-h-exposure-race', 'origin', configuration)['object']
            real = subprocess.run

            def blind(args, **kw):
                if 'fetch' in args or 'ls-remote' in args:
                    return subprocess.CompletedProcess(args, 0, '', '')
                return real(args, **kw)
            with shim(blind):
                try:
                    marker = claim(b, None, 'w42-h-exposure-race', 'origin', configuration)
                    same = 'the same object as' if marker['object'] == first else 'a different object from'
                    return True, (f'clone B CLAIMED too, exit 0 ("[up to date]"): marker {marker["object"][:12]}, '
                                  f'{same} A\'s {first[:12]}')
                except PermissionError as error:
                    text = ' '.join(re.sub(r'To \S+', '', str(error)).split())
                    return False, f'clone B refused: {text[:170]}'


class _Shim:
    def __init__(self, run):
        self.run, self.CompletedProcess = run, subprocess.CompletedProcess


def old_shim(blind):
    space['subprocess'] = _Shim(blind)
    class restore:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            space['subprocess'] = subprocess
    return restore()


red_claimed, red = race(space['claim_exposure'], old_shim)
green_claimed, green = race(runner.claim_exposure, lambda blind: mock.patch.object(runner.subprocess, 'run',
                                                                                 side_effect=blind))
record('4. the exposure race: clone B claims inside the window with a byte-identical tag object', red, green,
       red_claimed, not green_claimed, BASE2)


# 5. a quarantined run's staged manifest
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    raw = tmp / 'raw'
    TA.sitting_tree(raw)
    wave = TA.A.wave_module().default_wave()
    held = {s for s, r in wave.roles.items() if r == 'holdout'}
    leaks = {}
    for pre_fix in (True, False):
        A = archive_module2(tmp, pre_fix)
        out = tmp / f'out-staged-{pre_fix}'
        A.produce(raw, out, wave=wave, passes=TA.PASSES)
        staged = out / f'operational/{TA.KEY}/QUARANTINE-run-3-1/{TA.STAGING}/manifest.json'
        leaks[pre_fix] = sorted({k for p in json.loads(staged.read_text())['profiles'] for f in p['fixtures']
                                 if f['sceneId'] in held for k in f if k in TA.PIXEL_STATISTICS})
    record('5. a quarantined run\'s .staging-<UUID>/manifest.json', f'its public copy carries H {leaks[True]}',
           f'its public copy carries H {leaks[False] or "no pixel statistic"}', bool(leaks[True]), not leaks[False],
           BASE2)

print(f'{sum(results)} of {len(results)} scenarios red before and green after')
sys.exit(0 if all(results) else 1)
