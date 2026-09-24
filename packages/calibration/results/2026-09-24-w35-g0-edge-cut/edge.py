"""W35 full-profile instrument. Only guarded readers open image payloads (§5.177)."""
import base64
import gzip
import hashlib
import io
import itertools
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
G0=HERE.parent/'2026-09-23-w34-g0-contour-bed'
G1=HERE.parent/'2026-09-23-w34-g1-contour-sitting'
sys.path.insert(0,str(G0))
from w35_readers import W, WebReader
import instrument as I
DOMAIN=json.loads((HERE/'domain.json').read_text())


def save(path,value):
    raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    if str(path).endswith('.gz'):raw=gzip.compress(raw,mtime=0)
    with Path(path).open('xb') as f:f.write(raw)


def decode(v):
    v=np.asarray(v,float)
    return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)


def encode(v):
    v=np.maximum(np.asarray(v,float),0)
    return np.where(v<=.0031308,12.92*v,1.055*v**(1/2.4)-.055)


def forward(body,d,scale,a=0,g=0,width=2,shadow_alpha=.05,shadow_depth=.35,
            shadow_reach=9.18125,ramp=0,ramp_reach=6,alpha=1,tone=0,coverage=1,lit=1,along=1):
    """Sampled-texture branch at mat=present=1, no tint; ramp precedes shadow.

    body and outputs before encoding are linear sRGB. Alpha is explicit for the
    counterfactual but native identification nominates opaque A=1; final native
    RGB cannot identify a translucent layer's unpremultiplied colour and alpha.
    """
    d=np.asarray(d,float)/scale;body=np.asarray(body,float)
    r=np.maximum(1-np.maximum(-d,0)/ramp_reach,0)**2*ramp
    c=body+r[...,None]
    k=1-np.clip(1-np.maximum(-d,0)/shadow_reach,0,1)**2*shadow_depth*shadow_alpha
    ap=1-k*(1-alpha)
    pre=c*(k*alpha/np.maximum(ap,1e-6))[...,None]
    level=ap*(pre@np.array([.2126,.7152,.0722]))+(1-ap)*tone
    rw=np.maximum(1-abs(d)/width,0)**2
    amplitude=a+g*level
    light=rw*lit*along*amplitude
    linear=pre+light[...,None]
    cov=np.broadcast_to(coverage,np.shape(level))
    composite=cov[...,None]*(ap[...,None]*linear)+(1-cov*ap)[...,None]*tone
    return dict(linear=composite,pre=pre,alpha=ap,level=level,rw=rw,light=light,
                encoded=255*encode(np.clip(composite,0,1)))


def recover(body,d,scale,target,**options):
    base=forward(body,d,scale,**options)
    X=np.c_[base['rw'],base['rw']*base['level']]
    excess=np.mean(target-base['linear'],axis=-1)
    return np.linalg.lstsq(X,excess,rcond=None)[0]


def bar(images):return np.max([abs(a.astype(float)-b).mean(0)
    for a,b in itertools.combinations(images,2)],axis=0)


def whole_pixel(component,scale,translation,shape):
    """Convex stadium: all corners inside proves its exact body integral is one."""
    if component['kind']!='capsule-circular':return np.zeros(shape,bool)
    o=np.array(component['suppliedPaths'][0]['frameOrigin'])*scale+translation
    size=np.array(component['size'])*scale;rect=[*o,*(o+size)]
    y,x=np.indices(shape);mask=np.ones(shape,bool)
    for dx,dy in [(0,0),(0,1),(1,0),(1,1)]:
        mask &= I.stadium(x+dx,y+dy,rect,min(size)/2)[0]<=0
    return mask


_GEOMETRY={}
def geometry(p):
    comp=p['component'];scale=p['scale'];t=p['alignment']['translationDevicePx']
    key=json.dumps([comp,scale,t],sort_keys=True)
    if key not in _GEOMETRY:
        h,w=p['rgb'].shape[:2]
        d,nx,ny,arc=I.geometry(w,h,comp,scale,t)
        # W34 only solves the continuous supplied path within 8 CSS px. Deep
        # shells require the same exact path solve throughout the body.
        if comp['kind']!='capsule-circular':
            y,x=np.where(d<=-8*scale);q=np.c_[x+.5,y+.5]
            origin=np.array(comp['suppliedPaths'][0]['frameOrigin'])*scale+t
            nearest=np.full(len(q),np.inf)
            for a,b,isarc in I.segments(comp['suppliedPaths'][0]['elements']):
                a=a*scale+origin;b=b*scale+origin;v=b-a
                u=np.clip(((q-a)@v)/(v@v),0,1);delta=q-(a+u[:,None]*v)
                distance=np.linalg.norm(delta,axis=1);normal=np.array([v[1],-v[0]])/np.linalg.norm(v)
                update=distance<nearest;nearest[update]=distance[update]
                yy,xx=y[update],x[update]
                d[yy,xx]=distance[update]*np.where(delta[update]@normal>=0,1,-1)
                nx[yy,xx]=normal[0];ny[yy,xx]=normal[1];arc[yy,xx]=isarc
        angle=np.floor(np.mod(np.arctan2(ny,nx),2*np.pi)/(2*np.pi/16)+.5).astype(int)%16
        _GEOMETRY[key]=(d,nx,ny,arc,angle,whole_pixel(comp,scale,t,d.shape))
    return _GEOMETRY[key]


def cells(web_root=None):
    wave=W.default_wave();repeat=wave.reader(G1/'repeat');probe=wave.reader(G1/'probe')
    web=WebReader.w34(web_root)
    allowed=set(wave.launch_scenes())
    for cell in sorted(c for c in wave.cells if c.split('/')[1] in allowed):
        crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
        states={}
        for run in crop['runs']:
            if not run['admitted']:continue
            key=run['state']
            if key not in states:
                raw=base64.b64decode(crop['states'][key])
                if hashlib.sha256(raw).hexdigest()!=key:raise ValueError('state hash mismatch')
                states[key]=I.unpack(raw)
        normal=[r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal']
        p=states[normal[0]['state']]
        native=np.asarray(Image.open(io.BytesIO(probe.read(cell,'png'))).convert('RGB'),float)
        rendered=np.asarray(Image.open(io.BytesIO(web.read(cell))).convert('RGB'),float)
        if native.shape!=rendered.shape:raise ValueError('canvas mismatch')
        yield dict(cell=cell,role=wave.roles[cell.split('/')[1]],payload=p,states=states,
                   runs=crop['runs'],native=native,web=rendered,geo=geometry(p))


def stats(image,mask):
    a=image[mask]
    return dict(pixels=len(a),mean=a.mean(0).tolist(),minimum=a.min(0).tolist(),maximum=a.max(0).tolist())


def extract():
    profiles=[];bars=[];summary=[]
    for r in cells():
        p=r['payload'];scale=p['scale'];d,nx,ny,arc,angle,whole=r['geo']
        H=int(min(p['component']['size'])*scale/2)
        n,w,D=r['native'],r['web'],p['background'].astype(float)
        deep=d<=-6*scale;beta=np.median(n[deep],0);wbeta=np.median(w[deep],0)
        rec=dict(cell=r['cell'],role=r['role'],scale=scale,geometry=p['component']['kind'],H=H,
                 backgroundKind=p.get('backgroundKind','solid'),alignment=p['alignment'],
                 deep=dict(pixels=int(deep.sum()),nativeMedian=beta.tolist(),webMedian=wbeta.tolist(),
                     nativeMinimum=n[deep].min(0).tolist(),nativeMaximum=n[deep].max(0).tolist(),
                     nativeEnvelope=(abs(n[deep]-beta).max(0)+.5).tolist(),
                     levelMiss=(wbeta-beta).tolist(),memoNativeMedian=np.median(n[d<=-6],0).tolist(),
                     memoWebMedian=np.median(w[d<=-6],0).tolist()),rows=[],angular=[])
        masks=[]
        for part,m in [('arc',arc),('straight',~arc)]:
            for s in range(-H,4):
                shell=m&(d>=s)&(d<s+1)
                if not shell.any():continue
                for label,sel in [('all',shell),('whole',shell&whole)]:
                    if not sel.any():continue
                    nr,wr,dr=[stats(im,sel) for im in [n,w,D]]
                    rec['rows'].append(dict(part=part,shell=s,domain=label,pixels=nr['pixels'],
                        nativeRGB=nr['mean'],webRGB=wr['mean'],backgroundRGB=dr['mean'],
                        nativeExcess=(n[sel].mean(0)-beta).tolist(),webExcess=(w[sel].mean(0)-wbeta).tolist(),
                        gapRGB=(n[sel]-w[sel]).mean(0).tolist(),gapMAERGB=abs(n[sel]-w[sel]).mean(0).tolist(),
                        nativeMinimum=nr['minimum'],nativeMaximum=nr['maximum']))
                for b in range(16):
                    mask=shell&(angle==b)
                    if not mask.any():continue
                    masks.append(((part,s,b),mask))
                    if -6*scale<=s<0:
                        full=mask&whole
                        rec['angular'].append(dict(part=part,shell=s,bin=b,pixels=int(mask.sum()),
                            wholePixels=int(full.sum()),nativeRGB=n[mask].mean(0).tolist(),
                            wholeNativeRGB=n[full].mean(0).tolist() if full.any() else None))
        # Per-side readings keep top/bottom and thirds explicit; no angular pooling.
        rec['sides']=[]
        for label,sel in [('top',~arc&(ny<-.5)),('bottom',~arc&(ny>.5))]:
            for s in range(-H,4):
                mask=sel&(d>=s)&(d<s+1)
                if not mask.any():continue
                yy,xx=np.where(mask);order=np.argsort(xx)
                thirds=[n[yy[ix],xx[ix]].mean(0).tolist() for ix in np.array_split(order,3) if len(ix)]
                rec['sides'].append(dict(side=label,shell=s,pixels=len(xx),nativeRGB=n[mask].mean(0).tolist(),
                    webRGB=w[mask].mean(0).tolist(),backgroundRGB=D[mask].mean(0).tolist(),thirdsRGB=thirds))
        for protocol in ['normal','long']:
            runs=[x for x in r['runs'] if x['admitted'] and x['protocol']==protocol]
            br=dict(cell=r['cell'],role=r['role'],H=H,protocol=protocol,runs=len(runs),bins=[],
                    status='observed envelope' if len(runs)>=2 else 'insufficient repeats')
            if len(runs)>=2:
                # Identical admitted states have zero pair difference; deduplicate
                # only arithmetic, never select the plurality or omit run mapping.
                ids=sorted({x['state'] for x in runs})
                pairs=list(itertools.combinations(ids,2));br['runStates']=[x['state'] for x in runs]
                for key,mask in masks:
                    values=[abs(r['states'][a]['rgb'][mask].astype(float)-r['states'][b]['rgb'][mask]).mean(0)
                            for a,b in pairs]
                    rgb=np.max(values,axis=0) if values else np.zeros(3)
                    br['bins'].append(dict(part=key[0],shell=key[1],bin=key[2],pixels=int(mask.sum()),
                        admissible=int(mask.sum())>=4,barRGB=rgb.tolist()))
            bars.append(br)
        profiles.append(rec)
        summary.append(dict(cell=r['cell'],H=H,rows=len(rec['rows']),deep=rec['deep']))
        print('cut',r['cell'],flush=True)
    save(HERE/'profiles.json.gz',profiles);save(HERE/'deep-bars.json.gz',bars)
    save(HERE/'profile-index.json',summary)


if __name__=='__main__':extract()
