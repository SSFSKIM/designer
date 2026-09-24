"""W35 existing-leaf feasibility: one guarded launch per profile (§5.177, X6).

The parent directed leaving the unrelated foreign session alone and recording it;
repeat nondeterminism excludes the affected render without a retry. No native
capture and no new leaf can be supplied through this tune path.
"""
import datetime,hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
G0=HERE.parent/'2026-09-23-w34-g0-contour-bed'
sys.path.insert(0,str(G0));from w35_readers import W,WebReader
spec=importlib.util.spec_from_file_location('machine',G0/'record-machine.py')
machine=importlib.util.module_from_spec(spec);spec.loader.exec_module(machine)
SCRATCH=Path.home()/'vitrea-w35/scratch/existing-leaves'


def log(row):
    with (HERE/'browser-runs.txt').open('a') as f:
        f.write(json.dumps(row,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())


def preflight(label):
    settings={}
    for domain,key,expected in [('com.apple.universalaccess','reduceTransparency',0),
        ('com.apple.universalaccess','increaseContrast',0),('-g','NSGlassTintAmount',.5),
        ('com.apple.Accessibility','ButtonShapesEnabled',0)]:
        value=subprocess.check_output(['defaults','read',domain,key],text=True).strip()
        settings[key]=value
        if float(value)!=expected:raise RuntimeError('X6 setting mismatch: '+key)
    raw=subprocess.check_output(['ioreg','-c','IOHIDSystem'],text=True)
    idle=int(re.search(r'"HIDIdleTime"\s*=\s*(\d+)',raw)[1])/1e9
    foreign=machine.processes()
    log(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),label=label,settings=settings,
        idleSeconds=idle,foreignProcessCount=len(foreign),foreignProcesses=foreign,admitted=idle>=60,
        rule='Parent foreign-session ruling; no foreign process closed; deterministic repeat required',
        captureProcessesToLaunch=1,renderer='webgpu',channel='chromium'))
    if idle<60:raise RuntimeError('X6 idle refusal before launch')


def main():
    # Domain must be committed before the very first candidate rendering.
    rel=str((HERE/'domain.json').relative_to(ROOT))
    committed=subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:'+rel])
    if committed!=(HERE/'domain.json').read_bytes():raise RuntimeError('domain is not frozen')
    fits=json.loads((HERE/'native-grey-law-fits.json').read_text());wave=W.default_wave()
    allowed=set(wave.launch_scenes())
    selected=[f'grey-{v}__circular-120__rest' for v in [0,32,64,96,128,160,255]]
    selected+=['grey-128__circular-120__inactive']
    if not set(selected)<=allowed:raise PermissionError('scene outside role-filtered launcher')
    SCRATCH.mkdir(parents=True,exist_ok=True)
    plans=[]
    for f in fits:
        profile=f['profile'];c=f['fit'];label=f['name']+'-'+profile
        work=SCRATCH/label;work.mkdir(exist_ok=True)
        patch={'optics':{'regular':{'rimAlpha':c['a'],'rimLevelGain':c['g'],
               'rimWidth':c['width'],'rimWidth2x':c['width'],'shadowAlpha':c['shadowAlpha']}}}
        active=dict(profileKey=profile,patch=patch,claims='c9a §5.177; non-shipping grey-only feasibility; no transfer authority')
        scheme='dark' if '-dark-' in profile else 'light'
        receded=json.loads((ROOT/f'packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded.json').read_text())
        candidate=work/'candidate.json';recede=work/'receded.json'
        for dest,value in [(candidate,active),(recede,receded)]:
            raw=(json.dumps(value,indent=2)+'\n').encode()
            if dest.exists() and dest.read_bytes()!=raw:raise RuntimeError('candidate bytes changed')
            if not dest.exists():dest.write_bytes(raw)
        plan=json.loads(subprocess.check_output(['python3.12',str(G0/'wave.py'),'plan','--roles','calibration,validation',
            '--fixtures',str(HERE.parent/'2026-09-24-w34-g2-contour-identification/compare-fixtures'),
            '--out-matrix',str(work/'matrix.json'),'--captures',str(work/'web-captures')],text=True))
        command=plan['command'];command[command.index('--scene')+1]=','.join(selected)
        command+=['--profile',profile,'--material-profile',str(candidate),'--receded-profile',str(recede)]
        environment={**plan['environment'],'VITREA_SCENE_SERVER_PORT':'5197'}
        plan=dict(label=label,command=command,environment=environment,active=active,receded=receded,
                  domainSha256=hashlib.sha256(committed).hexdigest(),fitSource='native-grey-law-fits.json',
                  profile=profile,scenes=selected,root=str(work))
        plans.append(plan)
    target=HERE/'candidate-plans.json'
    if target.exists():raise RuntimeError('candidate plans already recorded; no implicit resume or retry')
    target.write_text(json.dumps(plans,indent=2)+'\n')
    for plan in plans:
        out=HERE/('candidate-'+plan['label']+'.txt')
        if out.exists():raise RuntimeError('already attempted: '+plan['label'])
        preflight(plan['label'])
        with out.open('x') as f:
            result=subprocess.run(plan['command'],env={**os.environ,**plan['environment']},stdout=f,stderr=subprocess.STDOUT)
        log(dict(label=plan['label'],exitCode=result.returncode,completed=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        reader=WebReader.w34(Path(plan['root'])/'web-captures');checks=[]
        for sid in plan['scenes']:
            cell=plan['profile']+'/'+sid
            meta=json.loads(reader.read(cell,'metadata'));report=json.loads(reader.read(cell,'report'))
            hardware=meta['gpuAdapter']=='apple/metal-3' and meta['renderer']=='webgpu' and not report['fallback']
            deterministic=meta['deterministic'] and meta['repeatNoise']==0
            if not hardware:raise RuntimeError('candidate is not real WebGPU')
            checks.append(dict(cell=cell,hardware=hardware,deterministic=deterministic,used=deterministic,
                pngSha256=hashlib.sha256(reader.read(cell)).hexdigest(),metadata=meta,material=report['page']['material']))
        # Standard metric refusal does not erase a captured image. Retain the
        # actual return and use only deterministic captures in the edge referee.
        log(dict(label=plan['label'],checks=checks,repeatFailures=sum(not c['used'] for c in checks),retried=False))

if __name__=='__main__':main()
