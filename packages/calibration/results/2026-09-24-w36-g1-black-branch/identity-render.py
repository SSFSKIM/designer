"""Six endpoints against checked canonical bytes, written only to scratch (§5.179)."""
import hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import WebReader
scratch=Path.home()/'vitrea-w36/scratch/black-identity';old=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
rows=[]
for oskey in ['26.5','27.0']:
  for scheme in ['light','dark']:
    profile=f'apple-macos-{oskey}-1x-{scheme}-standard'+('-glass0.5' if oskey=='27.0' else '')
    scenes=['impulse__capsule-button__rest','impulse__capsule-button__inactive'] if oskey=='27.0' else ['photo__rrect-md__rest']
    for sid in scenes:old.admit(profile+'/'+sid)
    work=scratch/profile;work.mkdir(parents=True,exist_ok=True)
    command=['pnpm','--dir',str(ROOT),'--filter','@vitrea/calibration','--fail-if-no-match','run','compare','--','--renderer','webgpu','--set','calibration,validation','--profile',profile,'--scene',','.join(scenes),'--material-profile',str(ROOT/'packages/calibration/profiles'/(profile+'.json')),'--out-matrix',str(work/'matrix.json'),'--write-partial']
    if oskey=='27.0':command+=['--receded-profile',str(ROOT/'packages/calibration/profiles'/(profile+'-receded.json'))]
    env={**os.environ,'VITREA_WEB_CAPTURES':str(work/'web-captures'),'VITREA_SCENE_SERVER_PORT':'5197'}
    subprocess.run(['python3.12',str(HERE/'run-browser.py'),'identity-'+profile,*command],env=env,check=True)
    new=WebReader.canonical(work/'web-captures')
    for sid in scenes:
      cell=profile+'/'+sid;a=old.read(cell);b=new.read(cell);meta=json.loads(new.read(cell,'metadata'))
      row=dict(cell=cell,oldSha256=hashlib.sha256(a).hexdigest(),newSha256=hashlib.sha256(b).hexdigest(),byteIdentical=a==b,deterministic=meta['deterministic'],repeatNoise=meta['repeatNoise'],adapter=meta['gpuAdapter'])
      rows.append(row)
      if a!=b or not meta['deterministic'] or meta['repeatNoise']!=0:raise RuntimeError(str(row))
with (HERE/'identity-captures.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print('Six endpoints byte-identical:',len(rows))
