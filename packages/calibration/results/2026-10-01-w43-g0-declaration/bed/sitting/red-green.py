#!/usr/bin/env python3.12
"""Red/green proofs of W43 G0 (d)'s sitting changes, stubs and scratch roots only.

Each scenario runs the defect on the tools before the change and the fix on W43's. Scenarios 1-9
run it on W42's COMMITTED tools (results/2026-09-29-w42-g0-declaration/bed/sitting/, loaded from
their files, never edited). Scenarios 10 and 11, the coordinator's rulings after the first 11 of
11, run it on W43's own tools as accepted at d92190b4, read from Git; each RED line names which.
RED is the defect W42 G1's stops, the charter or a ruling named, observed; GREEN is W43 behaving. Nothing native is launched,
the display is never touched, and the machine's real NSGlassTintAmount is only READ, before and
after, to show that nothing here wrote it. The census scenarios run real processes whose command
lines carry the census words (and copies of node under browser and harness names), so this runs
only when no sitting is running.

Run: python3.12 -B red-green.py > red-green.txt    (from this directory)
Exit 0 iff every scenario is red before and green after.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_sitting as T          # noqa: E402  (the W43 suite's stubs, mirror and fixtures)

REPO = T.REPO
W42 = REPO / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/sitting'
W42_G1 = REPO / 'packages/calibration/results/2026-09-30-w42-g1-sitting'
S, R, P = T.S, T.R, T.P
results = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def record(name, red, green, red_ok, green_ok, before='W42'):
    results.append(red_ok and green_ok)
    print(f'{name}\n  RED   ({before}): {red}  [{"defect shown" if red_ok else "NOT SHOWN"}]\n'
          f'  GREEN (W43): {green}  [{"fixed" if green_ok else "NOT FIXED"}]\n', flush=True)


def real_slider():
    out = subprocess.run(['/usr/bin/defaults', 'read', '-g', 'NSGlassTintAmount'], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else '(absent)'


def spawn(argv):
    p = subprocess.Popen([str(a) for a in argv], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    return p


SLIDER_BEFORE = real_slider()
R42 = load('w42_record_machine_red', W42 / 'record-machine.py')
print('== W43 G0 (d): the sitting tooling, red on W42 and green on W43 ==\n')
print(f'The machine\'s NSGlassTintAmount before: {SLIDER_BEFORE} (read only)\n')

# ------------------------------------------------- 1. the census by executable

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp).resolve()
    stub = tmp / 'w39-test-side/VitreaReference.app'
    benign = {
        "a shell holding a pgrep pattern (stop 4)": ['/bin/sh', '-c', 'sleep 20; pgrep -fl "Chromium|playwright" || true'],
        'a grep for a browser helper': ['/bin/sh', '-c', 'sleep 20; grep -c "Google Chrome Helper" /dev/null || true'],
        "a test stub's launch naming the harness (stop 5)": [
            T.PYTHON, '-c', 'import time; time.sleep(20)', '--env', f'VITREA_FIXTURES={tmp}', str(stub), '--args',
            'capture', str(stub / 'Contents/MacOS/VitreaReference')],
    }
    real = {}
    if T.NODE is not None:
        for label, rel in (('Chromium', 'Chromium.app/Contents/MacOS/Chromium'),
                           ('a Chrome renderer helper', 'Google Chrome.app/Contents/Frameworks/Helpers/'
                            'Google Chrome Helper (Renderer).app/Contents/MacOS/Google Chrome Helper (Renderer)'),
                           ('Chrome for Testing', 'Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'),
                           ('a headless shell', 'chrome-headless-shell-mac-arm64/chrome-headless-shell'),
                           ('a harness', 'Other.app/Contents/MacOS/VitreaReference')):
            real[label] = [T.fake_executable(tmp / 'exe' / rel), *T.SLEEP_JS]
        script = tmp / 'node_modules/playwright-core/cli.js'
        script.parent.mkdir(parents=True)
        script.write_text('setTimeout(() => {}, 20000)\n')
        real['Playwright (node + playwright-core/cli.js)'] = [T.fake_executable(tmp / 'bin/node'), script]
    procs = {label: spawn(argv) for label, argv in {**benign, **real}.items()}
    try:
        w42 = {int(r[0]) for r in R42.processes()}
        w43 = {f['pid'] for f in R.census(chain_file='')[0]}
        red_counts = {k: procs[k].pid in w42 for k in benign}
        green_counts = {k: procs[k].pid in w43 for k in benign}
        still = {k: (procs[k].pid in w42, procs[k].pid in w43) for k in real}
    finally:
        for p in procs.values():
            p.kill()
            p.wait()
    record('1. the census matches executables, not whole command lines',
           f'counted {sum(red_counts.values())} of {len(benign)} non-browser processes: '
           + '; '.join(f'{k}: {v}' for k, v in red_counts.items()),
           f'counted {sum(green_counts.values())} of {len(benign)} of them; still counts every real one '
           f'({sum(g for _, g in still.values())} of {len(real)}: ' + ', '.join(still) + ')',
           all(red_counts.values()), not any(green_counts.values()) and real and all(g for _, g in still.values()))

# -------------------------------------------- 2. the launching chain excluded

READER = r'''
import importlib.util, json, sys, time
time.sleep(1.0)                       # the intermediate shell has exited: reparented to launchd
spec = importlib.util.spec_from_file_location('census', sys.argv[1]); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
if hasattr(m, 'census'):
    foreign, excluded = m.census()
    out = dict(counted=[f['pid'] for f in foreign], excluded=[e['pid'] for e in excluded])
else:
    out = dict(counted=[int(r[0]) for r in m.processes()], excluded=[])
open(sys.argv[2], 'w').write(json.dumps(out))
'''


def detached_census(tmp, census_module, launcher_argv, chain):
    """The orchestrator's detach, reproduced: a launching process starts an intermediate shell that
    (optionally) records the launcher chain, starts the reader under nohup + setsid, and exits; the
    launching process lives on. Returns (launcher pid, the reader's census)."""
    reader, out = tmp / 'reader.py', tmp / f'out-{time.time_ns()}.json'
    reader.write_text(READER)
    record_chain = (f'"{T.PYTHON}" "{HERE / "record-machine.py"}" launcher-chain > "{tmp}/chain.json"; '
                    f'export VITREA_LAUNCHER_CHAIN="{tmp}/chain.json"; ') if chain else 'unset VITREA_LAUNCHER_CHAIN; '
    intermediate = (record_chain + f'nohup "{T.PYTHON}" -c "import os, sys; os.setsid(); '
                    f'os.execvp(sys.argv[1], sys.argv[1:])" "{T.PYTHON}" "{reader}" "{census_module}" "{out}" '
                    '</dev/null >/dev/null 2>&1 & exit 0')
    (tmp / 'intermediate.sh').write_text(intermediate)
    proc = subprocess.Popen([str(a) for a in launcher_argv] + [str(tmp / 'intermediate.sh')],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 30
    while not out.exists() and time.monotonic() < deadline:
        time.sleep(0.2)
    pid = proc.pid
    proc.kill()
    proc.wait()
    return pid, json.loads(out.read_text())


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp).resolve()
    shell = ['/bin/bash', '-c', 'bash "$0"; sleep 6; : pgrep -fl "Chromium|playwright"']
    red_pid, red_census = detached_census(tmp, W42 / 'record-machine.py', shell, chain=False)
    red_ok = red_pid in red_census['counted']
    green_ok, green = False, 'node absent: not run'
    if T.NODE is not None:
        script = tmp / 'node_modules/@playwright/cli/launch.js'
        script.parent.mkdir(parents=True)
        script.write_text("require('child_process').execFileSync('/bin/bash', [process.argv[2]]);"
                          "setTimeout(() => {}, 6000);\n")
        node = [T.fake_executable(tmp / 'bin/node'), script]
        unchained_pid, unchained = detached_census(tmp, HERE / 'record-machine.py', node, chain=False)
        chained_pid, chained = detached_census(tmp, HERE / 'record-machine.py', node, chain=True)
        green_ok = (unchained_pid in unchained['counted'] and chained_pid not in chained['counted']
                    and chained_pid in chained['excluded'])
        green = (f'a launching process the census DOES count by executable (node + @playwright/cli script), '
                 f'detached the same way: counted without the recorded chain ({unchained_pid in unchained["counted"]}), '
                 f'excluded with it ({chained_pid in chained["excluded"]}, counted {chained_pid in chained["counted"]})')
    record('2. the launching shell\'s chain is excluded, through the setsid detach',
           f'the launching shell (pid {red_pid}, alive after the detach, census words on its command line) is '
           f'counted by the detached reader: {red_ok}', green, red_ok, green_ok)

# ------------------------------------------------------- 3. the idle log as .txt


def committed_after_collect(collect, idle_name):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        repo = tmp / 'repo'
        repo.mkdir()
        (repo / '.gitignore').write_bytes((REPO / '.gitignore').read_bytes())
        T.git(repo, 'init', '-q')
        T.git(repo, 'config', 'user.email', 'test@example.invalid')
        T.git(repo, 'config', 'user.name', 'red-green')
        run = tmp / 'root' / 'p' / 'run-1'
        run.mkdir(parents=True)
        (run / idle_name).write_text('idle-wait: idle=400\n')
        (run / 'admission.json').write_text('{}\n')
        env = {**os.environ, 'VITREA_SITTING_DIR': str(tmp / 'root'), 'W42_EVIDENCE': str(repo / 'ev'),
               'W43_EVIDENCE': str(repo / 'ev')}
        subprocess.run([sys.executable, str(collect), 'p'], check=True, capture_output=True, env=env)
        T.git(repo, 'add', '--', 'ev')            # the orchestrator's per-pass `git add -- "$EVIDENCE"`
        T.git(repo, 'commit', '-qm', 'a pass')
        return [f for f in T.git(repo, 'ls-files').split() if 'driver-idle' in f]


w42_runs = sorted(p for p in (W42_G1 / 'attest').glob('*/run-*') if p.is_dir())
w42_idle = [p for p in w42_runs if any(p.glob('driver-idle.*'))]
ignored = subprocess.run(['git', '-C', str(REPO), 'check-ignore', '-v',
                          'packages/calibration/results/2026-09-30-w42-g1-sitting/attest/x/run-1/driver-idle.log'],
                         capture_output=True, text=True).stdout.strip()
red_files = committed_after_collect(W42 / 'collect-pass.py', 'driver-idle.log')
green_driver = T.Stubs(tempfile.mkdtemp(prefix='w43-rg-'))
green_driver.admit_before('bed-1x-active')
with contextlib.redirect_stdout(io.StringIO()):
    green_driver.run('capture', 'bed-1x-active', '1', '1')
written = sorted(p.name for p in (green_driver.root / 'bed-1x-active' / 'run-1').glob('driver-idle.*'))
green_files = committed_after_collect(HERE / 'collect-pass.py', written[0])
record('3. the idle log is kept as .txt',
       f'W42 G1\'s committed evidence holds {len(w42_idle)} idle logs over {len(w42_runs)} admitted runs '
       f'({ignored}); W42\'s collect-pass + git add commits {red_files}',
       f'the driver writes {written}; W43\'s collect-pass + git add commits {green_files}',
       not w42_idle and not red_files and bool(ignored), written == ['driver-idle.txt'] and green_files ==
       ['ev/attest/p/run-1/driver-idle.txt'])
shutil.rmtree(green_driver.tmp, ignore_errors=True)

# ------------------------------------------- 4. the watchdog and the UC check

T42 = load('w42_test_sitting_red', W42 / 'test_sitting.py')
EVENT_LAUNCHER = r'''
import json, os, subprocess, sys, time
from pathlib import Path
began = time.time()
time.sleep(2.0)
Path(os.environ['STUB_EVENT']).write_text(json.dumps(dict(at=time.time(), since_launch=time.time() - began)))
state = Path(os.environ.get('STUB_SESSION_FILE', '/nonexistent'))
if state.exists():
    s = json.loads(state.read_text()); s.update(frontmostIdentifier='com.apple.universalcontrol', inputAt=time.time())
    state.write_text(json.dumps(s))
time.sleep(float(os.environ.get('STUB_AFTER_EVENT', '3')))
os.execv(sys.executable, [sys.executable, os.environ['STUB_REAL_LAUNCHER'], *sys.argv[1:]])
'''

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    st = T42.Stubs(tmp, scale=1)
    st.admit_before('1x-light-active')
    doc = T42.P.derive('1x-light-active', 1)
    (st.tmp / 'manifest.json').write_text(json.dumps(T42.manifest(doc, 'active', 1, 'w42-1x-light-active-1')))
    (tmp / 'event-launcher.py').write_text(EVENT_LAUNCHER)
    began = time.monotonic()
    with contextlib.redirect_stdout(io.StringIO()):
        st.run('capture', '1x-light-active', '1', '1', STUB_MODE='manifest',
               VITREA_LAUNCHER=f'{sys.executable} {tmp / "event-launcher.py"}', STUB_EVENT=str(tmp / 'event.json'),
               STUB_REAL_LAUNCHER=str(tmp / 'launcher.py'))
    took = time.monotonic() - began
    admitted = (st.root / '1x-light-active' / 'run-1' / 'admission.json').exists()
    event = json.loads((tmp / 'event.json').read_text())
red = (f'focus went to com.apple.universalcontrol with HID input {event["since_launch"]:.1f} s into the launch; '
       f'the driver read nothing until the launch ended ({took:.1f} s) and ADMITTED the run: {admitted}')
red_ok = admitted

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    st = T.Stubs(tmp)
    st.admit_before('bed-1x-active')
    (tmp / 'event-launcher.py').write_text(EVENT_LAUNCHER)
    st.session(frontmostIdentifier='com.apple.finder')
    began = time.monotonic()
    try:
        st.run('capture', 'bed-1x-active', '1', '1', VITREA_LAUNCHER=f'{sys.executable} {tmp / "event-launcher.py"}',
               STUB_EVENT=str(tmp / 'event.json'), STUB_REAL_LAUNCHER=str(tmp / 'launcher.py'), STUB_AFTER_EVENT='30')
        refusal = None
    except ValueError as error:
        refusal = str(error)
    took = time.monotonic() - began
    event = json.loads((tmp / 'event.json').read_text())
    q = list((st.root / 'bed-1x-active').glob('QUARANTINE-run-1-*'))
    lag = took - event['since_launch']
green = (f'the same event {event["since_launch"]:.1f} s in; the watchdog (period 0.3 s here, 5 s in a sitting) ended '
         f'the launch {lag:.1f} s later and quarantined the run: "{(refusal or "")[:150]}"')
green_ok = bool(refusal and 'watchdog stopped the launch' in refusal and q and lag < 5)
uc = R.universal_control()
record('4a. a watchdog on frontmost and HID idle during every launch', red, green, red_ok, green_ok)
record('4b. a pre-sitting Universal Control check',
       'W42 reads nothing about Universal Control: its census does not name the agent and its gates read HID idle '
       'at launch only (record-machine.py has no such read)',
       f'THIS machine, read-only: agent {"running" if uc["agentActive"] else "absent"} '
       f'({[a["pid"] for a in uc["agent"]]}), Disable key {uc["disableSetting"]!r}, Bluetooth '
       f'{uc["bluetoothControllerState"]}, awdl0 {uc["awdlFlags"]}, Wi-Fi {uc["wifiPower"]!r}: input path '
       f'{"REACHABLE" if uc["inputPathReachable"] else "down"}. Cannot detect: ' + '; '.join(uc['cannotDetect']),
       'universalcontrol' not in (W42 / 'record-machine.py').read_text().lower(),
       isinstance(uc['agentActive'], bool) and isinstance(uc['inputPathReachable'], bool))

# ------------------------------------------------------- 5. the slider per pass

w42_sitting = load('w42_sitting_red', W42 / 'sitting.py')
w42_sitting._PIN = dict(T42.PIN)
try:
    w42_sitting.validate_machine(T42.machine(1, NSGlassTintAmount='0.25'), 1)
    w42_refused = None
except ValueError as error:
    w42_refused = str(error)
w42_slider = 'NSGlassTintAmount' in (W42 / 'sitting-orchestrate.sh').read_text()
red = (f'W42 hard-codes the slider at 0.5: a 0.25 machine is refused by its gate ("{w42_refused[:90]}"), no '
       f'pass can declare a position, and its orchestrator never reads, writes or restores it '
       f'(mentions NSGlassTintAmount: {w42_slider})')
red_ok = bool(w42_refused) and not w42_slider

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    case = T.Orchestrator('test_the_whole_order_writes_the_slider_per_pass_and_restores_both')
    case.tmp = tmp
    case.setup()
    out = case.orchestrate()
    writes = [w['value'] for w in S.slider_writes(case.st.root) if not w.get('restore')]
    restored = case.stored()
    calls = (case.st.store.with_name(case.st.store.name + '.calls')).read_text().splitlines()
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    case = T.Orchestrator('test_a_native_process_alive_at_a_slider_write_stops_the_sitting')
    case.tmp = tmp
    case.setup()
    T.fake_executable(T.SIDE / 'Contents/MacOS/VitreaReference')
    stale = case.orchestrate(STUB_DRIVER_MODE='native')
    stale_status = case.status()
    stale_restored = case.stored()
    for p in R.native_processes(binary=T.SIDE / 'Contents/MacOS/VitreaReference'):
        os.kill(p['pid'], signal.SIGKILL)
green = (f'the stand-in G1a order (as-found 0.5459057) wrote {writes} at its pass boundaries with no native process '
         f'alive, exit {out.returncode}, and restored {restored["value"]} as found ({len(calls)} stub `defaults` '
         f'calls); a stand-in harness left alive across the 0.25 write refused the pass (exit {stale.returncode}: '
         f'"{[l for l in stale_status.splitlines() if "slider write" in l][0][21:110]}") and restored '
         f'{stale_restored["value"]}')
green_ok = (out.returncode == 0 and writes == [0.5, 0.25, 0.5] and restored['value'] == '0.5459057'
            and stale.returncode == 9 and stale_restored['value'] == '0.5459057')
record('5. the slider declared per pass, the as-found value restored, fresh launches only', red, green, red_ok,
       green_ok)

# -------------------------------------------- 6. the dump sentinel's Normal = x

memo_d = T.MEMO_D / '2x-light-active' / 'json'
if memo_d.is_dir():
    DC = load('w42_dumpcheck_red', W42.parent / 'dumps/dumpcheck.py')
    reference = json.loads((W42.parent / 'dumps/dump-reference.json').read_text())
    ids = sorted(p.stem for p in memo_d.glob('*.json'))

    def normal_departures(report):
        return sum(1 for s in report['surfaces'] for d in s['departures'] if 'BlurFillNormalOpacity' in d['field'])

    def renormal(node, x):
        if isinstance(node, dict):
            return {k: (x if k == 'inputBlurFillNormalOpacity' else renormal(v, x)) for k, v in node.items()}
        return [renormal(v, x) for v in node] if isinstance(node, list) else node

    with tempfile.TemporaryDirectory() as tmp:
        right = Path(tmp)       # the same trees as a pass at 0.25 should read them: Normal 0.25
        for f in memo_d.glob('*.json'):
            (right / f.name).write_text(json.dumps(renormal(json.loads(f.read_text()), 0.25)))
        stale42 = normal_departures(DC.check_dir(memo_d, 'light', 'active', 2, reference))
        right42 = normal_departures(DC.check_dir(right, 'light', 'active', 2, reference))
        stale43 = S.sentinel_check(memo_d, ids, 0.25, 'active', 2, 'light')
        right43 = S.sentinel_check(right, ids, 0.25, 'active', 2, 'light')
    record('6. the dump sentinel checks the Normal blend opacity against the declared position',
           f'W42\'s dumpcheck has no position input (its reference is memo D\'s 0.5): over memo D\'s real 2x light '
           f'active dumps (24 scenes) it finds {stale42} Normal departure(s) in the trees taken at 0.5, which a 0.25 '
           f'pass must refuse as stale, and {right42} in the same trees at Normal 0.25, which it must accept',
           f'the sentinel at declared 0.25 departs on {len(stale43["departures"])} of {len(ids)} stale scenes '
           f'(Normal {stale43["normalOpacities"]}) and on {len(right43["departures"])} of the 0.25 trees '
           f'({right43["surfaces"]} surfaces read)',
           stale42 == 0 and right42 > 0, len(stale43['departures']) == len(ids) and not right43['departures'])
else:
    record('6. the dump sentinel checks the Normal blend opacity against the declared position',
           "SKIPPED: memo D's dumps are absent", 'SKIPPED', False, False)

# ---------------------------------- 7. the canonical publication path, side bundle

MAIN_MODULES = T.MAIN_MODULES
if (MAIN_MODULES / '.bin/tsx').exists():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pub = T.Publication('test_the_published_bed_names_the_side_bundle_and_the_slider')
        pub.tmp = tmp
        # RED: W42 G1's own committed attest.read for 2x-light-active runs 1-7, each beside a run of
        # the shape materialize reads (one stub cell; provenance is judged before any PNG is opened).
        runs = []
        for n in range(1, 8):
            run = tmp / 'w42' / f'run-{n}'
            (run / T.L2_05).mkdir(parents=True)
            shutil.copy(W42_G1 / 'attest/2x-light-active' / f'run-{n}' / 'attest.read', run / 'attest.read')
            (run / 'manifest.json').write_text(json.dumps(dict(
                hardware=dict(osBuild='26A428', osVersion='Version 27.0 (Build 26A428)'),
                profiles=[dict(profileKey=T.L2_05, fixtures=[dict(sceneId='x', deterministic=True)])],
                backgrounds={})))
            runs.append(run)
        out42 = pub.materialize(runs, tmp / 'red' / 'fixtures')
        fields42 = dict(l.split('=', 1) for l in (runs[1] / 'attest.read').read_text().splitlines())
        missing = [k for k in ('bundlePath', 'bundleIdentifier', 'bundlePinSha256') if k not in fields42]
        red = (f'materialize over W42 G1\'s seven committed 2x-light-active attestations exits {out42.returncode}: '
               f'"{[l for l in out42.stderr.splitlines() if "scene declarations" in l][0].strip()[:120]}..."; and '
               f'they never name {missing}')
        red_ok = out42.returncode != 0 and 'different scene declarations' in out42.stderr and len(missing) == 3
        # GREEN: two W43 runs of a two-scheme canonical pass at 0.25, published.
        (tmp / 'g').mkdir()
        st = T.Stubs(tmp / 'g')
        st.admit_before('bed-1x-active')
        with contextlib.redirect_stdout(io.StringIO()):
            st.run('capture', 'bed-1x-active', '1', '2')
        job = S.publication(st.root, P.pass_of('bed-1x-active', T.PLAN), T.DECLARATION, T.SI.CANONICAL)
        out43 = pub.materialize([st.root / 'bed-1x-active' / f'run-{n}' for n in (1, 2)], tmp / 'green' / 'fixtures')
        published = json.loads((tmp / 'green' / 'fixtures' / 'manifest.json').read_text())
        entry = next(p for p in published['profiles'] if p['profileKey'] == T.L1)['attestation']
        bad = tmp / 'bad'
        shutil.copytree(st.root, bad)
        read = bad / 'bed-1x-active' / 'run-2' / 'attest.read'
        read.write_text(read.read_text().replace('glassTintAmount=0.25', 'glassTintAmount=0.5'))
        try:
            S.publication(bad, P.pass_of('bed-1x-active', T.PLAN), T.DECLARATION, T.SI.CANONICAL)
            refused = None
        except ValueError as error:
            refused = str(error)
        green = (f'materialize publishes both schemes (exit {out43.returncode}); the profile record names '
                 f'bundlePath={entry["bundlePath"]}, bundleIdentifier={entry["bundleIdentifier"]}, '
                 f'bundlePinSha256={entry["bundlePinSha256"][:12]}…, glassTintAmount={entry["glassTintAmount"]}, '
                 f'runs={entry["runs"]}; `publish` builds {" ".join(job["argv"][2:5])} … and refuses a run at another '
                 f'slider ("{refused[:80]}")')
        green_ok = (out43.returncode == 0 and entry['bundlePath'] == T.PIN['path']
                    and entry['bundlePinSha256'] == S.pin_sha256() and entry['glassTintAmount'] == '0.25'
                    and refused and 'attests slider' in refused)
    record('7. the canonical publication path for side-bundle runs', red, green, red_ok, green_ok)
else:
    record('7. the canonical publication path for side-bundle runs', 'SKIPPED: no tsx', 'SKIPPED', False, False)

# The canonical bed's group and stack components, which W42's path attestation never met.
canonical = json.loads(T.CANONICAL_RAW)
doc = P.subset(canonical, {T.L1: ['checkerboard__toolbar-group__rest', 'checkerboard__glass-over-glass__rest']})
faithful = T.manifest(doc, 'active', 1, 'l')
shifted = T.manifest(doc, 'active', 1, 'l', origin_shift='checkerboard__toolbar-group__rest')
try:
    w42_sitting.validate_manifest(faithful, doc, 'active', 1, 'l')
    w42_result = 'accepted'
except ValueError as error:
    w42_result = f'refused: {error}'
verdicts = []
for m in (faithful, shifted):
    try:
        S.validate_manifest(m, doc, 'active', 1, 'l')
        verdicts.append('accepted')
    except ValueError as error:
        verdicts.append(f'refused: {str(error)[:70]}')
record('7b. the supplied-path attestation of the canonical bed\'s group and stack components',
       f'W42\'s driver on a faithful toolbar-group + glass-over-glass manifest: {w42_result[:90]} (every canonical '
       f'pass holding them would quarantine)',
       f'faithful: {verdicts[0]}; a group item shifted by 1 pt: {verdicts[1]}',
       w42_result.startswith('refused'), verdicts[0] == 'accepted' and verdicts[1].startswith('refused'))

# --------------------------------------------------- 8 and 9: the forks' cases

for module in ('red_green_archive.py', 'red_green_timing.py'):
    case = load(module[:-3] + '_rg', HERE / module).scenario()
    record(case['name'], case['red'], case['green'], case['red_ok'], case['green_ok'])

# ------------------------------------------------------- the coordinator's rulings
# The pre-ruling tools are W43's own as accepted at d92190b4 (the 11 of 11 above), read from Git.

ACCEPTED = 'd92190b4'


def accepted_tool(name, tmp):
    path = Path(tmp) / f'accepted-{name}'
    path.write_bytes(subprocess.run(['git', '-C', str(HERE), 'show', f'{ACCEPTED}:./{name}'], check=True,
                                    capture_output=True).stdout)
    return path


with tempfile.TemporaryDirectory() as tmp:
    S0 = load('w43_sitting_accepted', accepted_tool('sitting.py', tmp))
    case = T.BridgeVerdict('test_identity_agrees')
    T.BridgeVerdict.setUpClass()
    edge, n_edge = case.edge_frame()
    shifted, name, sign = case.shifted_frame(2)
    import numpy as np  # noqa: E402
    rgba = np.dstack([case.img, np.full(case.img.shape[:2], 255, np.int16)]).reshape(-1, 4)
    rgba[case.pops['n'][0][2], 3] = 0
    frames = {'1 code on edge pixels, medians equal': T.png_bytes(edge),
              f'one region median moved {sign}2 codes': T.png_bytes(shifted),
              f'a missing region ({case.pops["n"][0][0]}, no opaque pixel)': T.png_bytes(
                  rgba.reshape(*case.img.shape[:2], 4), 'RGBA')}
    pass0 = dict(expect={case.cell: [hashlib.sha256(case.ref).hexdigest()]})
    before = {k: 'refused' if S0.expectation_problems(pass0, {case.cell: hashlib.sha256(raw).hexdigest()})
              else 'passed' for k, raw in frames.items()}
    after = {k: S.bridge_verdict(raw, case.ref, case.bg, case.comp, 2, 'dark', 'active', None, case.cell)
             for k, raw in frames.items()}
w42_reads = re.search(r'def \w*(bridge|expect)\w*\(', (W42 / 'sitting.py').read_text()) is not None
record('10. the opening bridge: byte identity, or every region median within max(1 code, bar), run by run',
       f'on (e)\'s declared bridge cell {case.cell} against its real 0.5 fixture: W42\'s driver compares a sentinel '
       f'with nothing ({not w42_reads}); W43 as accepted gates by byte identity only: '
       + '; '.join(f'{k}: {v}' for k, v in before.items()) + ' (the first is a false stop)',
       '; '.join(f'{k}: {v["verdict"]}' + (f' ({v["failing"][0]})' if v['failing'] else
                                           f' ({v["pixelsDiffering"]} px differ by {v["maxCodes"]:g}, worst median '
                                           f'delta {v["worstDelta"]:g})') for k, v in after.items()),
       list(before.values()) == ['refused'] * 3 and not w42_reads,
       [v['verdict'] for v in after.values()] == ['AGREE (regions)', 'DISAGREE', 'DISAGREE'],
       before=f'W42, and W43 as accepted at {ACCEPTED}')

E = T.e_g1b()
if E is not None:
    plan, files = E
    names = [p['name'] for p in plan['passes']]
    closing = [x for x in names if x.startswith('close-')]
    with tempfile.TemporaryDirectory() as tmp:
        old = {(T.HERE / n).relative_to(T.REPO): accepted_tool(n, tmp).read_bytes()
               for n in ('sitting.py', 'pass-spec.py', 'sitting-orchestrate.sh')}
        red_rows = []
        for cut in (names[0], 'probe-0.25-2x-active', closing[0]):
            _, out, ran, status, _ = T.g1b_cut(cut, replace=old)
            red_rows.append((cut, out.returncode, [c for c in closing if c in ran]))
    green_rows = []
    for cut in names:
        _, out, ran, status, stored = T.g1b_cut(cut)
        upto = names[:names.index(cut) + 1]
        green_rows.append((cut, out.returncode == 0 and ran == upto + [c for c in closing if c not in upto]
                           and stored['value'] == '0.5459057'))
    record('11a. a cut never drops the close: G1b\'s order (e94b2ed2, with the two fields) cut at each pass',
           '; '.join(f'cut after {c}: exit {rc}, close passes run {len(r)} of {len(closing)}' for c, rc, r in red_rows),
           f'{sum(ok for _, ok in green_rows)} of {len(green_rows)} cuts ran every pass up to the cut, then the slider '
           f'restored and mode 68, then each of the {len(closing)} close passes not yet run, in order, and restored '
           f'the slider as found' + ('' if all(ok for _, ok in green_rows) else
                                     f'; FAILED at {[c for c, ok in green_rows if not ok]}'),
           all(len(r) < len(closing) for _, _, r in red_rows[:2]),
           all(ok for _, ok in green_rows), before=f'W43 as accepted at {ACCEPTED}')

    with tempfile.TemporaryDirectory() as tmp:
        P0 = load('w43_pass_spec_accepted', accepted_tool('pass-spec.py', tmp))
    sources = {k: json.loads(files[s['path']]) for k, s in plan['sources'].items()}
    lacking = json.loads(json.dumps(plan))
    del next(p for p in lacking['passes'] if p['name'] == closing[-1])['runAfterCut']
    carrying = json.loads(json.dumps(plan))
    next(p for p in carrying['passes'] if p['name'] == 'probe-0.25-2x-active')['runAfterCut'] = True

    def verdict(module, candidate):
        try:
            module.validate_plan(candidate, sources)
            return 'accepted'
        except ValueError as error:
            return 'refused: ' + str(error).split(': ', 1)[1][:110]
    red = {k: verdict(P0, c) for k, c in (('close lacking it', lacking), ('a probe pass carrying it', carrying))}
    green = {k: verdict(P, c) for k, c in (('close lacking it', lacking), ('a probe pass carrying it', carrying))}
    record('11b. runAfterCut is required on every closing W42 sentinel bridge and refused on any other pass',
           '; '.join(f'{k}: {v}' for k, v in red.items()), '; '.join(f'{k}: {v}' for k, v in green.items()),
           set(red.values()) == {'accepted'}, all(v.startswith('refused') for v in green.values()),
           before=f'W43 as accepted at {ACCEPTED}')
else:
    record("11. a cut never drops the close", "SKIPPED: (e)'s plans are absent", 'SKIPPED', False, False)

T.tearDownModule()
SLIDER_AFTER = real_slider()
print(f'The machine\'s NSGlassTintAmount after: {SLIDER_AFTER} (read only; '
      f'{"unchanged" if SLIDER_AFTER == SLIDER_BEFORE else "CHANGED"})\n')
results.append(SLIDER_AFTER == SLIDER_BEFORE)
print(f'{sum(results[:-1])} of {len(results) - 1} scenarios red before and green after; the real slider '
      f'{"untouched" if results[-1] else "MOVED"}')
sys.exit(0 if all(results) else 1)
