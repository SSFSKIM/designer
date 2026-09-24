"""Physical straight-side profiles beside the actual integer-ring W29 replay."""
import io,json,sys,base64,subprocess
import numpy as np
from PIL import Image
from edge import HERE,save
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import CanonicalNativeReader,WebReader
native=CanonicalNativeReader();web=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
metrics=json.loads((HERE/'canonical-metrics.json').read_text())['rows'];rows=[]
for scale in [1,2]:
 for scheme in ['light','dark']:
  profile=f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'
  for background in ['light-solid','dark-solid','mid-dark-solid','mid-light-solid','mid-chroma-solid']:
   sid=background+'__rrect-md__rest';cell=profile+'/'+sid
   if cell not in native.roles.cells:
    rows.append(dict(cell=cell,status='unavailable: no declared canonical scene'));continue
   n=np.asarray(Image.open(io.BytesIO(native.read(cell))).convert('RGB'),float)
   try:w=np.asarray(Image.open(io.BytesIO(web.read(cell))).convert('RGB'),float)
   except FileNotFoundError:w=None
   D=np.asarray(Image.open(io.BytesIO(native.read(cell,'background'))).convert('RGB'),float)
   comp=native.roles.spec['components']['rrect-md'];cw,ch=comp['size'];radius=comp['radius']
   h,width=n.shape[:2];x0=(width-cw*scale)/2;y0=(h-ch*scale)/2
   # A physical inward row depth, not a distance-transform ring. The corner
   # exclusion is W23's converged 1.6 radii, declared rather than image-selected.
   xs=np.arange(int(np.ceil(x0+1.6*radius*scale)),int(np.floor(x0+(cw-1.6*radius)*scale)))
   transects=[]
   for shell in range(-int(ch*scale/2),4):
    y=int(y0-shell-1)
    transects.append(dict(shell=shell,deviceDepth=-shell-.5,pixels=len(xs),
       nativeRGB=n[y,xs].mean(0).tolist(),webRGB=w[y,xs].mean(0).tolist() if w is not None else None,backgroundRGB=D[y,xs].mean(0).tolist()))
   record=next((r for r in metrics if r['cell']==cell),None)
   if record is None:
    payload=dict(native=base64.b64encode(native.read(cell)).decode(),
      background=base64.b64encode(native.read(cell,'background')).decode(),
      component=comp,canvas=native.roles.spec['canvas'],scale=scale)
    run=subprocess.run(['pnpm','--dir',str(HERE.parents[3]),'--filter','@vitrea/calibration',
      'exec','tsx',str(HERE/'rim-stdin.ts')],input=json.dumps(payload),text=True,capture_output=True,check=True)
    record=dict(nativeRim=json.loads(run.stdout),webRim=None)
   rows.append(dict(cell=cell,role=native.roles.roles[sid],scale=scale,physicalTop=transects,
      nativeIntegerRing=record['nativeRim'],webIntegerRing=record['webRim']))
save(HERE/'canonical-solids.json',rows)
print([(r['cell'],r.get('nativeIntegerRing',{}).get('fwhmPx'),r.get('status')) for r in rows])
