"""Re-derive X1 from the new matrix-named captures, through the role guard (§5.179)."""
import hashlib,io,json,re,sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import WebReader,CanonicalNativeReader
native=CanonicalNativeReader();web=WebReader.canonical(CAL/'web-captures')
BLACK=['checkerboard','checkerboard-4','checkerboard-8','checkerboard-32','checkerboard-64','impulse','hc-text','hc-text-7','hc-text-28']
def image(raw):return np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'))
rows=[]
for c in json.loads((CAL/'results/matrix.json').read_text())['cells']:
    profile,sid=c['key']['profileKey'],c['key']['sceneId'];scene=native.roles.scenes[sid];role=native.roles.roles[sid];comp=native.roles.spec['components'][scene['component']]
    if not (profile.startswith('apple-macos-27.0-') and '-standard-' in profile and c['tier']=='texture' and c['key']['web']['renderer']=='webgpu' and role in ['calibration','validation','probe'] and scene['state'] in ['rest','inactive'] and scene['background'] in BLACK and comp['kind'] in ['rrect','capsule']):continue
    cell=profile+'/'+sid;meta=json.loads(web.read(cell,'metadata'));assert meta['capturePath']==c['key']['web']['capturePath']
    docs=re.findall(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})',meta['capturePath']);assert len(docs)==2
    for path,sha in docs:assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12]==sha
    n=image(native.read(cell));bg=image(native.read(cell,'background'));w=image(web.read(cell));scale=2 if '-2x-' in profile else 1
    width,height=comp['size'];dx,dy=comp.get('offset',[0,0]);x0=((320-width)/2+dx)*scale;y0=((200-height)/2+dy)*scale;x1=x0+width*scale;y1=y0+height*scale
    y,x=np.indices(n.shape[:2]);black=np.all(bg==0,2);nat=np.all(n==0,2);maximum=w.max(2)
    masks=dict(integer=np.maximum.reduce([x0-x,x-(x1-1),y0-y,y-(y1-1)])>=2*scale,
      analytic=np.hypot(np.maximum.reduce([x0-(x+.5),x+.5-x1,np.zeros_like(x)]),np.maximum.reduce([y0-(y+.5),y+.5-y1,np.zeros_like(y)]))>=2*scale)
    row=dict(profile=profile,scene=sid,role=role,span=min(width,height),pose=scene['state'],background=scene['background'],capturePath=meta['capturePath'])
    for name,mask in masks.items():
        eligible=mask&black&nat;pixels=int(eligible.sum());zero=int(np.sum(eligible&(maximum>0)))
        row[name]=dict(backdropBlack=int(np.sum(mask&black)),nativeNonzero=int(np.sum(mask&black&~nat)),pixels=pixels,aboveZero=zero,aboveOne=int(np.sum(eligible&(maximum>1))),fraction=zero/pixels if pixels else None)
    rows.append(row)
rows.sort(key=lambda r:(r['profile'],r['scene']))
result=dict(atDocuments='shipped',withHoldout=False,blackBackdrops=BLACK,targets=dict(blackFraction=0,aboveOne=0),missed=[],cells=rows)
with (HERE/'black-cut.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('X1 cells',len(rows))
for mask in ['integer','analytic']:print(mask,{k:sum(r[mask][k] for r in rows) for k in ['pixels','aboveZero','aboveOne']})
assert len(rows)==218 and all(r[m]['fraction']==0 and r[m]['aboveOne']==0 for r in rows for m in ['integer','analytic'])
