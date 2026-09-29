#!/usr/bin/env python3.12
"""Red/green proofs of the bed review's sitting fixes (B-M1, B-M2, b2, b3), stubs only.

Each scenario runs twice in a throwaway Mirror checkout (test_sitting.Mirror): once with the
PRE-FIX tools (sitting.py, sitting-orchestrate.sh and w42_archive.py at the fix branch's base,
9a695ec0) and once with the fixed ones. RED is the defect the review named, observed on the
pre-fix tools; GREEN is the fix refusing or behaving. Nothing native is launched: the machine
recorder, session reader, harness, launcher, driver and displayplacer are the suites' stubs.

Run: python3.12 -B red-green-fixes.py > red-green-fixes.txt    (from this directory)
Exit 0 iff every scenario is red before and green after.
"""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

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


def mirror(tmp, pre_fix, extra=None):
    replace = {(HERE / n).relative_to(T.REPO): at(BASE, HERE / n) for n in TOOLS} if pre_fix else {}
    replace.update(extra or {})
    return T.Mirror(tmp, replace)


def record(name, red, green, red_ok, green_ok):
    results.append(red_ok and green_ok)
    print(f'{name}\n  RED   (pre-fix {BASE}): {red}  [{"defect shown" if red_ok else "NOT SHOWN"}]\n'
          f'  GREEN (fix): {green}  [{"fixed" if green_ok else "NOT FIXED"}]\n', flush=True)


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

print(f'{sum(results)} of {len(results)} scenarios red before and green after')
sys.exit(0 if all(results) else 1)
