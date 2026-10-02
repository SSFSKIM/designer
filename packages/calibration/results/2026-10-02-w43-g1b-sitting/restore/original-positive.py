#!/usr/bin/env python3.12
"""W42 G1 pre-grant check 1: the ORIGINAL granted bundle's positive capture (charter G1).

original-positive.py <attempt-name>

Derived from W39 G1's wave-close/grant-check-close.py (itself its grant/grant-check.py), with
W42's driver gates in place of W39's: `sitting.validate_machine` and `sitting.session_problems`
from the W42 sitting, W42's record-machine.py, and the same read-session. What it captures is
unchanged: the canonical 27-only 2x light checkerboard capsule
(`checkerboard__capsule-button__rest`, apps/reference-apple/scenes.json at this checkout's HEAD),
at mode 68, with the ORIGINAL bundle under `apps/reference-apple/build` in the main checkout,
which is never rebuilt, and explicit scratch roots under ~/vitrea-w42/g1/prechecks/<attempt>,
outside every checkout and outside Documents/Desktop/Downloads. It never writes into the
canonical fixtures. An attempt is its own directory and is never retried in place.

Before creating the attempt it WAITS, bounded and logged, for zero foreign capture processes
by the sitting's own census and >= 75 s of HID idle with no permission prompt on screen:
waiting is not a retry, since nothing has run. Once those clear it grants the ChatGPT app,
which is no gate, up to 20 minutes to be quit, and records whether it still ran at launch.
It does not change any system setting; a
display mode other than 68 is a gate refusal, not a switch. The outcome is CLASSIFIED as
W39's was ('captured-active', 'captured-inactive', 'captured-other', 'refused-tcc', 'other'),
and the capture is compared with the committed canonical fixture (byte identity, differing
pixels, the largest per-channel code). The system TCC rows are read, read-only, before and after.
This is the baseline the restore check at the sitting's end is compared against.
"""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
E = REPO / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/sitting'
spec = importlib.util.spec_from_file_location('w42_sitting', E / 'sitting.py')
sitting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sitting)
spec = importlib.util.spec_from_file_location('w42_record_machine', E / 'record-machine.py')
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)

APP = Path('/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app')
BINARY = APP / 'Contents/MacOS/VitreaReference'
SID = 'checkerboard__capsule-button__rest'
PROFILE = 'apple-macos-27.0-2x-light-standard-glass0.5'
CANONICAL = REPO / 'apps/reference-apple/fixtures' / PROFILE / (SID + '.png')
READ_SESSION = [str(Path.home() / 'vitrea-w39/scratch/read-session')]
TCC = ['sqlite3', '-readonly', '-json', '/Library/Application Support/com.apple.TCC/TCC.db',
       "select service,client,auth_value,last_modified from access where client like '%vitrea%';"]
WAIT_LIMIT, WAIT_POLL = 6 * 3600, 30

name = sys.argv[1]
root = sitting.outside_repository(Path.home() / 'vitrea-w42/g1/prechecks')
run = root / name
if run.exists():
    sys.exit(f'{run} exists; an attempt is never retried in place')


def session():
    return json.loads(subprocess.check_output(READ_SESSION, text=True))


def foreign():
    return [f[2][:120] for f in recorder.processes()]


def chatgpt():
    """Not a sitting gate: the user was asked to quit it for its Codex helpers' CPU load, so the
    baseline waits a bounded grace for it once the gates clear, and records whether it ran."""
    rows = subprocess.run(['ps', '-axo', 'command='], capture_output=True, text=True).stdout.splitlines()
    return any(r.startswith('/Applications/ChatGPT.app/Contents/MacOS/ChatGPT') for r in rows)


# The wait: nothing is created or launched until the census reads zero and the session is idle.
root.mkdir(parents=True, exist_ok=True)
waitlog = root / f'{name}-wait.log'
start, ready_since, CHATGPT_GRACE = time.monotonic(), None, 1200
while True:
    census, observed, busy = foreign(), session(), chatgpt()
    problems = sitting.session_problems(observed, sitting.WAIT_IDLE_SECONDS)
    with waitlog.open('a') as f:
        f.write(f'{datetime.datetime.now(datetime.timezone.utc).isoformat()} foreign={len(census)} '
                f'idle={observed.get("idleSeconds")} locked={observed.get("screenLocked")} '
                f'chatgpt={busy} load={os.getloadavg()[0]:.2f}\n')
    if any(o.split('|')[0] in sitting.PROMPT_OWNERS for o in observed.get('windowOwners') or []):
        sys.exit('a permission prompt is on screen; answer nothing and stop')
    ready_since = (ready_since or time.monotonic()) if not census and not problems else None
    if ready_since is not None and (not busy or time.monotonic() - ready_since >= CHATGPT_GRACE):
        break
    if time.monotonic() - start >= WAIT_LIMIT:
        sys.exit(f'the gates never cleared within {WAIT_LIMIT} s: {len(census)} foreign, {problems}')
    time.sleep(WAIT_POLL)
chatgpt_at_launch = chatgpt()

run.mkdir(parents=True, exist_ok=False)


def dump(n, doc):
    (run / n).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + '\n')


def machine(phase):
    raw = subprocess.check_output([sys.executable, str(E / 'record-machine.py'), f'w42-g1-{name}-{phase}'])
    (run / f'attest.{phase}.json').write_bytes(raw)
    return json.loads(raw)


def tcc(phase):
    r = subprocess.run(TCC, capture_output=True, text=True)
    dump(f'tcc-{phase}.json', dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                   command=TCC, exitCode=r.returncode, stdout=r.stdout, stderr=r.stderr))


def granted(m):
    g = m['granted']
    cd = re.search(r'^CDHash=(.+)$', g.get('signature', {}).get('stderr', ''), re.M)
    return dict(binarySha256=g.get('binarySha256'), cdhash=cd[1] if cd else None)


tcc('before')
opened = machine('open')
before = session()
dump('session-before.json', before)
problems = []
try:
    initial = sitting.validate_machine(opened, 2)
except ValueError as e:
    problems.append(str(e))
problems += sitting.session_problems(before)
if problems:
    (run / 'refusal.txt').write_text('gate refused before launch: ' + ' | '.join(problems) + '\n')
    print('GATE REFUSED:', problems)
    sys.exit(3)
doc = json.loads((REPO / 'apps/reference-apple/scenes.json').read_text())
doc = {k: v for k, v in doc.items() if not k.startswith('$comment')}
doc['scenes'] = [s for s in doc['scenes'] if s['id'] == SID]
doc['profiles'] = [p for p in doc['profiles'] if p['key'] == PROFILE]
doc['profiles'][0]['scenes'] = [SID]
doc['backgrounds'] = {'checkerboard': doc['backgrounds']['checkerboard']}
doc['components'] = {'capsule-button': doc['components']['capsule-button']}
doc['split'] = {k: ([SID] if k == 'calibration' else []) for k in doc['split']}
dump('scenes.json', doc)
env = {**os.environ, 'VITREA_SCENES': str(run / 'scenes.json'), 'VITREA_FIXTURES': str(run), 'VITREA_SCALE': '2'}
with (run / 'backgrounds.log').open('w') as f:
    subprocess.run([str(BINARY), 'backgrounds'], env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
cmd = ['open', '-W']
for k in ['VITREA_SCENES', 'VITREA_FIXTURES', 'VITREA_SCALE']:
    cmd += ['--env', k + '=' + env[k]]
cmd += ['--stdout', str(run / 'capture.out'), '--stderr', str(run / 'capture.err'), str(APP), '--args',
        'capture', '--run-label', f'w42-g1-{name}', '--reset-interstitial', '6', '--min-idle-seconds', '60',
        '--scenes', SID]
dump('command.json', dict(bundle='original', argv=cmd, loadAverageAtLaunch=[round(v, 2) for v in os.getloadavg()],
                          chatgptRunningAtLaunch=chatgpt_at_launch))
timed_out = False
try:
    subprocess.run(cmd, check=True, timeout=180)
except subprocess.TimeoutExpired:
    timed_out = True
    subprocess.run(['pkill', '-f', str(BINARY)], check=False)
except subprocess.CalledProcessError as e:
    (run / 'launch-exit.txt').write_text(f'{e.returncode}\n')
closed = machine('close')
after = session()
dump('session-after.json', after)
tcc('after')
drift = None
try:
    if sitting.validate_machine(closed, 2) != initial:
        drift = 'opening/closing machine drift'
except ValueError as e:
    drift = str(e)
if granted(opened) != granted(closed):
    drift = (drift + '; ' if drift else '') + 'original binary drift'
out = (run / 'capture.out').read_text() if (run / 'capture.out').exists() else ''
err = (run / 'capture.err').read_text() if (run / 'capture.err').exists() else ''
pngs = [str(p.relative_to(run)) for p in run.rglob('*.png') if p.relative_to(run).parts[0] != 'backgrounds']
facts = dict(bundle='original', appPath=str(APP), original=granted(opened), timedOut=timed_out,
             manifestPublished=(run / 'manifest.json').exists(), fixturePngs=pngs,
             captureAttempted='via screencapturekit' in out, tccGateText=sitting.TCC_GATE in err,
             errFirstLine=err.splitlines()[0] if err else None, machineDrift=drift,
             sessionAfterProblems=sitting.session_problems(after),
             newWindowOwners=sorted(set(after.get('windowOwners') or []) - set(before.get('windowOwners') or [])),
             loadAverageAtClose=[round(v, 2) for v in os.getloadavg()])
f = {}
if facts['manifestPublished']:
    raw = (run / 'manifest.json').read_bytes()
    m = json.loads(raw)
    fx = [x for p in m['profiles'] for x in p['fixtures']]
    f = fx[0] if len(fx) == 1 else {}
    facts.update(manifestSha256=hashlib.sha256(raw).hexdigest(), fixtures=len(fx),
                 captureMethod=f.get('captureMethod'), materialRendered=f.get('materialRendered'),
                 presentedActive=f.get('presentedActive'), deterministic=f.get('deterministic'),
                 repeatNoise=f.get('repeatNoise'), hidIdleSeconds=f.get('hidIdleSeconds'),
                 presentation=f.get('presentation'),
                 actualBackingScale=m['profiles'][0]['display']['actualBackingScale'])
    ok = len(fx) == 1 and f.get('captureMethod') == 'screencapturekit' and f.get('materialRendered') is True \
        and f.get('deterministic') is True and f.get('repeatNoise') == 0 and facts['actualBackingScale'] == 2
    outcome = ('captured-active' if f.get('presentedActive') is True else 'captured-inactive') if ok else 'captured-other'
elif pngs:
    outcome = 'captured-other'
elif facts['tccGateText'] and facts['captureAttempted'] and not timed_out:
    outcome = 'refused-tcc'
else:
    outcome = 'other'
facts['outcome'] = outcome
dump('outcome.json', facts)

if f.get('file') and (run / f['file']).is_file():
    import numpy as np
    from PIL import Image
    capture = run / f['file']
    shown = subprocess.run(['git', '-C', str(REPO), 'show', f'HEAD:{CANONICAL.relative_to(REPO)}'],
                           capture_output=True, check=True).stdout
    if shown != CANONICAL.read_bytes():
        sys.exit('the canonical fixture on disk is not its committed copy at HEAD')
    a = np.asarray(Image.open(capture).convert('RGBA'), dtype=np.int16)
    b = np.asarray(Image.open(CANONICAL).convert('RGBA'), dtype=np.int16)
    diff = np.abs(a - b) if a.shape == b.shape else None
    comparison = dict(capture=str(capture), captureSha256=hashlib.sha256(capture.read_bytes()).hexdigest(),
                      canonical=str(CANONICAL.relative_to(REPO)), canonicalSha256=hashlib.sha256(shown).hexdigest(),
                      shape=list(a.shape[:2]), byteIdentical=capture.read_bytes() == shown,
                      differingPixels=None if diff is None else int((diff.max(axis=2) > 0).sum()),
                      maxAbsCode=None if diff is None else int(diff.max()),
                      note='positive check of the ORIGINAL bundle against the committed canonical 2x light '
                           'fixture; a reading, not an admission')
    dump('canonical-comparison.json', comparison)
    facts['canonical'] = comparison
print(json.dumps(facts, ensure_ascii=False))
