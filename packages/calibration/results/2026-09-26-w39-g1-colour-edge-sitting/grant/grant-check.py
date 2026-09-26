"""W39 G1 step 3: one-cell positive check of a bundle after the grant switch (charter grant plan 4).

grant-check.py side|original <attempt-name>
The known-good scratch cell (27-only 2x light checkerboard capsule, canonical scenes.json) at
mode 68 with explicit scratch roots, as step 0 ran it. Each attempt is its own directory under
~/vitrea-w39/run/grant-checks/ and is never retried in place. The outcome is CLASSIFIED, not
asserted: 'captured-active' (materialRendered, presentedActive, deterministic true, repeatNoise
0), 'captured-inactive' (pixels but the pose attested inactive), 'captured-other',
'refused-tcc' (capture attempted, the harness's TCC-gate sentence, no manifest/PNG), or
'other'. Machine gates are the sitting's own (validate_machine, session_problems); a gate
failure refuses before launch. The TCC rows are read, read-only, before and after.
"""
import datetime, hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path
REPO = Path('/Users/new/vitrea-w39/g1')
E = REPO / 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed'
spec = importlib.util.spec_from_file_location('sitting', E / 'sitting.py')
sitting = importlib.util.module_from_spec(spec); spec.loader.exec_module(sitting)
which, name = sys.argv[1], sys.argv[2]
app = {'side': Path('/Users/new/vitrea-w39/side/VitreaReference.app'),
       'original': Path('/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app')}[which]
binary = app / 'Contents/MacOS/VitreaReference'
run = Path('/Users/new/vitrea-w39/run/grant-checks') / name
run.mkdir(parents=True, exist_ok=False)
TCC = ['sqlite3', '-readonly', '-json', '/Library/Application Support/com.apple.TCC/TCC.db',
       "select service,client,auth_value,last_modified from access where service='kTCCServiceScreenCapture' and client like '%vitrea%';"]
def dump(n, doc): (run / n).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + '\n')
def machine(phase):
    raw = subprocess.check_output(['python3.12', str(E / 'record-machine.py'), f'w39-g1-{name}-{phase}'])
    (run / f'attest.{phase}.json').write_bytes(raw); return json.loads(raw)
def session(): return json.loads(subprocess.check_output(['/Users/new/vitrea-w39/scratch/read-session'], text=True))
def tcc(phase):
    r = subprocess.run(TCC, capture_output=True, text=True)
    dump(f'tcc-{phase}.json', dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                   command=TCC, exitCode=r.returncode, stdout=r.stdout, stderr=r.stderr))
tcc('before')
opened = machine('open'); before = session(); dump('session-before.json', before)
problems = []
try: initial = sitting.validate_machine(opened, 2)
except ValueError as e: problems.append(str(e))
problems += sitting.session_problems(before)
if problems:
    (run / 'refusal.txt').write_text('gate refused before launch: ' + ' | '.join(problems) + '\n')
    print('GATE REFUSED:', problems); sys.exit(3)
doc = json.loads((REPO / 'apps/reference-apple/scenes.json').read_text()); sid = 'checkerboard__capsule-button__rest'
doc = {k: v for k, v in doc.items() if not k.startswith('$comment')}
doc['scenes'] = [s for s in doc['scenes'] if s['id'] == sid]
doc['profiles'] = [p for p in doc['profiles'] if p['key'] == 'apple-macos-27.0-2x-light-standard-glass0.5']
doc['profiles'][0]['scenes'] = [sid]
doc['backgrounds'] = {'checkerboard': doc['backgrounds']['checkerboard']}
doc['components'] = {'capsule-button': doc['components']['capsule-button']}
doc['split'] = {k: ([sid] if k == 'calibration' else []) for k in doc['split']}
dump('scenes.json', doc)
env = {**os.environ, 'VITREA_SCENES': str(run / 'scenes.json'), 'VITREA_FIXTURES': str(run), 'VITREA_SCALE': '2'}
with (run / 'backgrounds.log').open('w') as f:
    subprocess.run([str(binary), 'backgrounds'], env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
cmd = ['open', '-W']
for k in ['VITREA_SCENES', 'VITREA_FIXTURES', 'VITREA_SCALE']: cmd += ['--env', k + '=' + env[k]]
cmd += ['--stdout', str(run / 'capture.out'), '--stderr', str(run / 'capture.err'), str(app), '--args',
        'capture', '--run-label', f'w39-g1-{name}', '--reset-interstitial', '6', '--min-idle-seconds', '60',
        '--scenes', sid]
dump('command.json', dict(bundle=which, argv=cmd))
timed_out = False
try: subprocess.run(cmd, check=True, timeout=180)
except subprocess.TimeoutExpired:
    timed_out = True; subprocess.run(['pkill', '-f', str(binary)], check=False)
except subprocess.CalledProcessError as e:
    (run / 'launch-exit.txt').write_text(f'{e.returncode}\n')
closed = machine('close'); after = session(); dump('session-after.json', after); tcc('after')
drift = None
try:
    if sitting.validate_machine(closed, 2) != initial: drift = 'opening/closing machine drift'
except ValueError as e: drift = str(e)
out = (run / 'capture.out').read_text() if (run / 'capture.out').exists() else ''
err = (run / 'capture.err').read_text() if (run / 'capture.err').exists() else ''
pngs = [str(p.relative_to(run)) for p in run.rglob('*.png') if p.relative_to(run).parts[0] != 'backgrounds']
facts = dict(bundle=which, appPath=str(app), timedOut=timed_out, manifestPublished=(run / 'manifest.json').exists(),
             fixturePngs=pngs, captureAttempted='via screencapturekit' in out, tccGateText=sitting.TCC_GATE in err,
             errFirstLine=err.splitlines()[0] if err else None, machineDrift=drift,
             sessionAfterProblems=sitting.session_problems(after),
             newWindowOwners=sorted(set(after.get('windowOwners') or []) - set(before.get('windowOwners') or [])))
if facts['manifestPublished']:
    raw = (run / 'manifest.json').read_bytes(); m = json.loads(raw)
    fx = [f for p in m['profiles'] for f in p['fixtures']]
    f = fx[0] if len(fx) == 1 else {}
    facts.update(manifestSha256=hashlib.sha256(raw).hexdigest(), fixtures=len(fx),
                 captureMethod=f.get('captureMethod'), materialRendered=f.get('materialRendered'),
                 presentedActive=f.get('presentedActive'), deterministic=f.get('deterministic'),
                 repeatNoise=f.get('repeatNoise'), presentation=f.get('presentation'),
                 actualBackingScale=m['profiles'][0]['display']['actualBackingScale'])
    ok = len(fx) == 1 and f.get('captureMethod') == 'screencapturekit' and f.get('materialRendered') is True \
        and f.get('deterministic') is True and f.get('repeatNoise') == 0 and facts['actualBackingScale'] == 2
    outcome = ('captured-active' if f.get('presentedActive') is True else 'captured-inactive') if ok else 'captured-other'
elif pngs: outcome = 'captured-other'
elif facts['tccGateText'] and facts['captureAttempted'] and not timed_out: outcome = 'refused-tcc'
else: outcome = 'other'
facts['outcome'] = outcome
dump('outcome.json', facts); print(json.dumps(facts, ensure_ascii=False))
