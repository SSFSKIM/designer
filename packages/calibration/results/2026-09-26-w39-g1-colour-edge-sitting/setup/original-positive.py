import datetime, hashlib, importlib.util, json, os, subprocess, time
from pathlib import Path
REPO=Path('/Users/new/vitrea-w39/g1')
E=REPO/'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed'
spec=importlib.util.spec_from_file_location('sitting',E/'sitting.py'); sitting=importlib.util.module_from_spec(spec);spec.loader.exec_module(sitting)
run=Path('/Users/new/vitrea-w39/run/preconditions/original-positive-1');run.mkdir(parents=True,exist_ok=False)
app=Path('/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app')
binary=app/'Contents/MacOS/VitreaReference'
def dump(name,doc): (run/name).write_text(json.dumps(doc,indent=2)+'\n')
def machine(phase):
    raw=subprocess.check_output(['python3.12',str(E/'record-machine.py'),'w39-g1-original-positive-'+phase]);(run/f'attest.{phase}.json').write_bytes(raw);return json.loads(raw)
try:
    opened=machine('open'); before=json.loads(subprocess.check_output(['/Users/new/vitrea-w39/scratch/read-session'],text=True));dump('session-before.json',before)
    initial=sitting.validate_machine(opened,2)
    assert not sitting.session_problems(before),sitting.session_problems(before)
    doc=json.loads((REPO/'apps/reference-apple/scenes.json').read_text());sid='checkerboard__capsule-button__rest'
    doc={k:v for k,v in doc.items() if not k.startswith('$comment')}
    doc['scenes']=[s for s in doc['scenes'] if s['id']==sid]
    doc['profiles']=[p for p in doc['profiles'] if p['key']=='apple-macos-27.0-2x-light-standard-glass0.5']
    doc['profiles'][0]['scenes']=[sid]
    doc['backgrounds']={'checkerboard':doc['backgrounds']['checkerboard']}
    doc['components']={'capsule-button':doc['components']['capsule-button']}
    doc['split']={k:([sid] if k=='calibration' else []) for k in doc['split']}
    dump('scenes.json',doc)
    env={**os.environ,'VITREA_SCENES':str(run/'scenes.json'),'VITREA_FIXTURES':str(run),'VITREA_SCALE':'2'}
    with (run/'backgrounds.log').open('w') as f:subprocess.run([str(binary),'backgrounds'],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    cmd=['open','-W']
    for k in ['VITREA_SCENES','VITREA_FIXTURES','VITREA_SCALE']:cmd+=['--env',k+'='+env[k]]
    cmd+=['--stdout',str(run/'capture.out'),'--stderr',str(run/'capture.err'),str(app),'--args','capture','--run-label','w39-g1-original-positive-1','--reset-interstitial','6','--min-idle-seconds','60','--scenes',sid]
    dump('command.json',cmd);subprocess.run(cmd,check=True)
    closed=machine('close');after=json.loads(subprocess.check_output(['/Users/new/vitrea-w39/scratch/read-session'],text=True));dump('session-after.json',after)
    assert sitting.validate_machine(closed,2)==initial,'opening/closing machine drift'
    assert opened['granted']['binarySha256']==closed['granted']['binarySha256'],'original binary drift'
    assert not sitting.session_problems(after),sitting.session_problems(after)
    m=json.loads((run/'manifest.json').read_text());fixtures=[f for p in m['profiles'] for f in p['fixtures']]
    assert len(fixtures)==1
    f=fixtures[0]
    for k in ['materialRendered','presentedActive','deterministic']:assert f.get(k) is True,(k,f.get(k))
    assert f.get('repeatNoise')==0,f.get('repeatNoise')
    assert f['captureMethod']=='screencapturekit'
    assert m['profiles'][0]['display']['actualBackingScale']==2
    admission=dict(admitted=True,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),cells=1,manifestSha256=hashlib.sha256((run/'manifest.json').read_bytes()).hexdigest(),materialRendered=f['materialRendered'],presentedActive=f['presentedActive'],deterministic=f['deterministic'],repeatNoise=f['repeatNoise'])
    dump('admission.json',admission);print(json.dumps(admission))
except BaseException as e:
    (run/'refusal.txt').write_text(f'{type(e).__name__}: {e}\n'); dest=run.with_name('QUARANTINE-'+run.name+'-'+str(time.time_ns()));run.rename(dest);print('STOP; retained at',dest,flush=True);raise
