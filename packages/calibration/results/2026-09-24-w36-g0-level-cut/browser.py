"""W36 one scratch launch per profile, with W35 admission and X6 (§5.178 clause 2).

This projects ONLY role-admitted cells into a scratch probe declaration. Native
bytes are copied only after the unchanged guarded readers return them. The
canonical scenes and fixtures remain untouched; no holdout gets a probe alias.
"""
import base64,copy,datetime,gzip,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
from PIL import Image
from cut import HERE,ROOT,edge,save
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import W,WebReader,CanonicalNativeReader
spec=importlib.util.spec_from_file_location('w35_browser',edge.HERE/'browser.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);old.HERE=HERE
SCRATCH=Path.home()/'vitrea-w36/scratch/part-a-shared-shifts'
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def raw(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(value)

def prepare():
    wave=W.default_wave();cn=CanonicalNativeReader()
    native=wave.reader(edge.G1/'probe');repeat=wave.reader(edge.G1/'repeat')
    wmanifest=json.loads((edge.G1/'probe/manifest.json').read_text())
    cmanifest=json.loads((ROOT/'apps/reference-apple/fixtures/manifest.json').read_text())
    cw={p['profileKey']:p for p in cmanifest['profiles']};ww={p['profileKey']:p for p in wmanifest['profiles']}
    profiles=list(ww);plans=[];projection=[]
    scratchScenes=copy.deepcopy(wave.spec)
    scratchScenes['components'].update(cn.roles.spec['components'])
    scratchScenes['backgrounds'].update(cn.roles.spec['backgrounds'])
    selectedW=[f'grey-{v}__circular-120__{pose}' for v in [0,64,96,128,255] for pose in ['rest','inactive']]
    selectedC=[f'{bg}__rrect-md__{pose}' for bg in ['photo','checkerboard','impulse'] for pose in ['rest','inactive']]
    selectedC+=['hc-text-7__rrect-md__rest']
    selectedByProfile={}
    manifest={k:copy.deepcopy(v) for k,v in cmanifest.items() if k not in ['profiles','backgrounds','split','bedProvenance']}
    manifest.update(profiles=[],backgrounds={},caveats=['W36 scratch projection, guarded non-holdout only; original roles retained in projection.json'])
    fixtureRoot=SCRATCH/'native-inputs';fits=json.loads((HERE/'candidate-fit.json').read_text())
    for profile in profiles:
        scale=2 if '-2x-' in profile else 1;scheme='dark' if '-dark-' in profile else 'light'
        items=[];admitted=[]
        for origin,sids in [('w34',selectedW),('canonical',selectedC)]:
          for sid in sids:
            cell=profile+'/'+sid
            if origin=='w34':
                if sid not in wave.launch_scenes():raise PermissionError('W34 scene outside roles')
                payload=native.read(cell,'png');metadata=json.loads(native.read(cell,'statistics'))
                crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
                first=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
                p=edge.I.unpack(base64.b64decode(crop['states'][first['state']]))
                bg=wave.scenes[sid]['background'];bgpath=fixtureRoot/f'backgrounds/{bg}@{scale}x.png'
                if not bgpath.exists():
                    bgpath.parent.mkdir(parents=True,exist_ok=True)
                    Image.fromarray(p['background'].astype('uint8')).save(bgpath)
                role=wave.roles[sid];fixture=copy.deepcopy(next(x for x in ww[profile]['fixtures'] if x['sceneId']==sid))
            else:
                try:cn.roles.admit(cell)
                except ValueError:continue # A dark impulse rrect-md fixture is not declared.
                payload=cn.read(cell);metadata=copy.deepcopy(next(x for x in cw[profile]['fixtures'] if x['sceneId']==sid))
                bg=cn.roles.scenes[sid]['background'];bgpath=fixtureRoot/f'backgrounds/{bg}@{scale}x.png'
                if not bgpath.exists():raw(bgpath,cn.read(cell,'background'))
                role=cn.roles.roles[sid];fixture=copy.deepcopy(next(x for x in cw[profile]['fixtures'] if x['sceneId']==sid))
            dest=profile+'/'+sid+'.png';raw(fixtureRoot/dest,payload)
            raw(fixtureRoot/(profile+'/'+sid+'.json'),(json.dumps(metadata)+'\n').encode())
            fixture.update(file=dest,fixtureSet='probe');items.append(fixture);admitted.append(sid)
            manifest['backgrounds'][f'{bg}@{scale}x']=f'backgrounds/{bg}@{scale}x.png'
            projection.append(dict(cell=cell,origin=origin,originalRole=role,pngSha256=hashlib.sha256(payload).hexdigest()))
        mp={k:copy.deepcopy(v) for k,v in cw[profile].items() if k!='fixtures'}
        mp['fixtures']=items;manifest['profiles'].append(mp);selectedByProfile[profile]=admitted
        work=SCRATCH/profile;active=next(f for f in fits if f['scheme']==scheme and f['pose']=='rest')
        inactive=next(f for f in fits if f['scheme']==scheme and f['pose']=='inactive')
        act=dict(profileKey=profile,patch=active['patch'],claims='c9a §5.178; non-shipping shared-shift trial')
        rec=copy.deepcopy(json.loads((ROOT/f'packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded.json').read_text()))
        rec['patch'].update(inactive['patch']);rec['claims']='c9a §5.178; candidate difference over active tune'
        dump(work/'candidate.json',act);dump(work/'receded.json',rec)
        command=['pnpm','--dir',str(ROOT),'--filter','@vitrea/calibration','run','compare','--',
            '--renderer','webgpu','--set','probe','--scene',','.join(admitted),'--profile',profile,
            '--material-profile',str(work/'candidate.json'),'--receded-profile',str(work/'receded.json'),
            '--out-matrix',str(work/'matrix.json'),'--write-partial']
        environment=dict(VITREA_SCENES=str(SCRATCH/'scenes.json'),VITREA_FIXTURES=str(fixtureRoot),
            VITREA_WEB_CAPTURES=str(work/'web-captures'),VITREA_SCENE_SERVER_PORT='5197')
        plans.append(dict(profile=profile,scenes=admitted,root=str(work),command=command,environment=environment,
            active=act,receded=rec,boundsSha256=hashlib.sha256((HERE/'bounds-declaration.md').read_bytes()).hexdigest()))
    allids=set(s for ids in selectedByProfile.values() for s in ids)
    combined={**wave.scenes,**cn.roles.scenes}
    scratchScenes['scenes']=[combined[s] for s in sorted(allids)]
    scratchScenes['profiles']=[dict(key=p,colorScheme='dark' if '-dark-' in p else 'light',a11y='standard',scenes=ss) for p,ss in selectedByProfile.items()]
    scratchScenes['split']={r:[] for r in ['calibration','validation','holdout','recorded']};scratchScenes['split']['probe']=sorted(allids)
    manifest['split']=scratchScenes['split']
    dump(SCRATCH/'scenes.json',scratchScenes);dump(fixtureRoot/'manifest.json',manifest)
    save('projection.json',projection);save('candidate-plans.json',plans)

def render():
    rel=str((HERE/'bounds-declaration.md').relative_to(ROOT))
    assert subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:'+rel])==(HERE/'bounds-declaration.md').read_bytes()
    for plan in json.loads((HERE/'candidate-plans.json').read_text()):
        profile=plan['profile'];out=HERE/('candidate-'+profile+'.txt')
        if out.exists():raise RuntimeError('already attempted; no implicit retry')
        old.preflight('part-a-'+profile)
        with out.open('x') as f:
            result=subprocess.run(plan['command'],env={**os.environ,**plan['environment']},stdout=f,stderr=subprocess.STDOUT)
        old.log(dict(label='part-a-'+profile,exitCode=result.returncode,
            completed=datetime.datetime.now(datetime.timezone.utc).isoformat(),retried=False))
        w34=WebReader.w34(Path(plan['root'])/'web-captures');canonical=WebReader.canonical(Path(plan['root'])/'web-captures');checks=[]
        for sid in plan['scenes']:
            reader=w34 if '__circular-120__' in sid else canonical;cell=profile+'/'+sid
            meta=json.loads(reader.read(cell,'metadata'));report=json.loads(reader.read(cell,'report'))
            hardware=meta['gpuAdapter']=='apple/metal-3' and meta['renderer']=='webgpu' and not report['fallback']
            deterministic=meta['deterministic'] and meta['repeatNoise']==0
            checks.append(dict(cell=cell,hardware=hardware,deterministic=deterministic,used=deterministic and hardware,
                pngSha256=hashlib.sha256(reader.read(cell)).hexdigest(),metadata=meta,
                material=report['page']['material']))
        old.log(dict(label='part-a-'+profile,checks=checks,repeatFailures=sum(not c['used'] for c in checks)))
        if not all(c['used'] for c in checks):raise RuntimeError('render refused; retain, do not retry')

if __name__=='__main__':{'prepare':prepare,'render':render}[sys.argv[1]]()
