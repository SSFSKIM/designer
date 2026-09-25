"""Canonical fixed-reference E1 baseline and native author-tint placement (§5.181)."""
import hashlib,io,json,re,sys
from pathlib import Path
import numpy as np
from PIL import Image
import law
HERE=law.HERE;CAL=HERE.parent.parent;ROOT=CAL.parent.parent
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import CanonicalNativeReader,WebReader


def geometry(shape,component,scale):
    h,w=shape;cw,ch=component['size'];radius=component.get('radius',min(cw,ch)/2)
    x0=(w-cw*scale)/2;y0=(h-ch*scale)/2
    y,x=np.indices(shape);px=x+.5;py=y+.5
    def sdf(x,y):
        qx=abs(x-w/2)-(cw/2-radius)*scale;qy=abs(y-h/2)-(ch/2-radius)*scale
        return np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-radius*scale
    d=sdf(px,py);whole=np.ones(shape,bool)
    for dx,dy in [(0,0),(0,1),(1,0),(1,1)]:whole&=sdf(x+dx,y+dy)<=0
    # The frozen corner exclusion is stricter than tangent identification.
    xs=(px>=x0+1.6*radius*scale)&(px<=x0+(cw-1.6*radius)*scale)
    ys=(py>=y0+1.6*radius*scale)&(py<=y0+(ch-1.6*radius)*scale)
    sides={'top':xs&(py<h/2),'bottom':xs&(py>=h/2),'left':ys&(px<w/2),'right':ys&(px>=w/2)}
    bins=[]
    for side,m in sides.items():
        for sh in range(-6*scale,0):
            mask=m&whole&(d>=sh)&(d<sh+1)
            if mask.any():bins.append((dict(side=side,shell=sh,pixels=int(mask.sum()),admissible=int(mask.sum())>=4),mask))
    return d,bins


def native_cell(reader,cell):
    profile,sid=reader.roles.admit(cell);raw=reader.read(cell)
    image=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),float)
    scale=2 if '-2x-' in profile else 1
    comp=reader.roles.spec['components'][reader.roles.scenes[sid]['component']]
    d,bins=geometry(image.shape[:2],comp,scale);deep=np.median(image[d<=-6*scale],0)
    return image,d,bins,deep,hashlib.sha256(raw).hexdigest(),scale


def generation(reader,cell,row):
    meta=json.loads(reader.read(cell,'metadata'))
    assert meta['capturePath']==row['key']['web']['capturePath']
    docs=re.findall(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})',meta['capturePath'])
    assert len(docs)==2
    for name,sha in docs:assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()[:12]==sha
    assert meta['deterministic'] and meta['repeatNoise']==0
    assert row['key']['web']['renderer']=='webgpu' and row['key']['web']['samplingBackend']=='gpu-texture'
    return meta


def main():
    native=CanonicalNativeReader();web=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
    decl=json.loads((HERE/'e1-declaration.json').read_text());matrix=json.loads((CAL/'results/matrix.json').read_text())
    allowed=set(decl['cells']);mapped={r['key']['profileKey']+'/'+r['key']['sceneId']:r for r in matrix['cells'] if r['key']['web']['renderer']=='webgpu' and r['key']['profileKey']+'/'+r['key']['sceneId'] in allowed}
    e1=[]
    for cell in decl['cells']:
        n,d,bins,deep,sha,scale=native_cell(native,cell);assert sha==decl['nativeReferences'][cell]
        generation(web,cell,mapped[cell]);w=np.asarray(Image.open(io.BytesIO(web.read(cell))).convert('RGB'),float)
        wd=np.median(w[d<=-6*scale],0);rr=[]
        for info,m in bins:
            error=abs((w[m]-wd)-(n[m]-deep)).mean(0)
            rr.append(dict(**info,nativeExcess=(n[m]-deep).mean(0).tolist(),webExcess=(w[m]-wd).mean(0).tolist(),residualRGB=error.tolist(),fails=info['admissible'] and bool(np.any(error>1))))
        e1.append(dict(cell=cell,nativeDeep=deep.tolist(),webDeep=wd.tolist(),bins=rr,
            maximum=max(max(r['residualRGB']) for r in rr if r['admissible']),status='measured',capturePath=mapped[cell]['key']['web']['capturePath']))
    law.edge.save(HERE/'e1-baseline.json',e1)
    placement=[]
    scenes=[b+'__capsule-button__rest-tint-orange' for b in ['dark-solid','impulse','checkerboard','photo','light-solid']]+['photo__capsule-button__rest-tint-blue','photo__capsule-button__rest-tint-orange-half']
    for profile in [p['key'] for p in native.roles.spec['profiles'] if p['key'].startswith('apple-macos-27.0-') and 'standard' in p['key']]:
        for sid in scenes:
            cell=profile+'/'+sid;untinted=profile+'/'+sid.split('-tint-')[0]
            if cell not in native.roles.cells or untinted not in native.roles.cells:
                placement.append(dict(cell=cell,status='UNMEASURED: declared profile lacks this tinted/untinted pair'));continue
            n,d,bins,deep,sha,scale=native_cell(native,cell)
            u,ud,ubins,udeep,usha,_=native_cell(native,untinted)
            rr=[]
            for info,m in bins:
                if info['side'] not in ['top','bottom']:continue
                rr.append(dict(**info,tintedRGB=n[m].mean(0).tolist(),tintedExcess=(n[m]-deep).mean(0).tolist(),untintedRGB=u[m].mean(0).tolist(),untintedExcess=(u[m]-udeep).mean(0).tolist()))
            placement.append(dict(cell=cell,untinted=untinted,status='measured',role=native.roles.roles[sid],scale=scale,
                nativeSha=sha,untintedSha=usha,tintedDeep=deep.tolist(),untintedDeep=udeep.tolist(),rows=rr))
    law.edge.save(HERE/'placement.json',placement)
    print('E1',len(e1),'max',max(r['maximum'] for r in e1),'tint measured',sum(r['status']=='measured' for r in placement))
    for r in placement:
        if r['status']=='measured' and 'dark-solid' in r['cell']:
            print(r['cell'],r['tintedDeep'],[x for x in r['rows'] if x['side']=='top' and x['shell']>=-r['scale']])
if __name__=='__main__':main()
