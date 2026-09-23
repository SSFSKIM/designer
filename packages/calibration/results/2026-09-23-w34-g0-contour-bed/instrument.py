#!/usr/bin/env python3.12
"""W34 contour instrument and lossless replay representation (§5.174).

All geometry and closure choices are in closure.json, declared before fitting.
This module receives already-authorised payloads; wave.Reader owns file access.
"""
import base64
import gzip
import json
import math
import numpy as np


def residual(native,predicted):
    delta=np.asarray(native,dtype=float)-np.asarray(predicted,dtype=float)
    return dict(pixels=len(delta),signedRGB=delta.mean(axis=0).tolist(),
                maeRGB=np.abs(delta).mean(axis=0).tolist())


def closes(stat,bar):
    return stat['pixels']>=4 and all(e<=max(1.,b) for e,b in zip(stat['maeRGB'],bar))


def pairwise_bar(images):
    if len(images)<2:raise ValueError('a repeat bar needs at least two admitted runs')
    return np.max([np.abs(np.asarray(images[i],float)-images[j]).mean(axis=0)
                   for i in range(len(images)) for j in range(i)],axis=0).tolist()


def stadium(x,y,rect,radius):
    x0,y0,x1,y1=rect
    dx=x-(x0+x1)/2;dy=y-(y0+y1)/2
    qx=np.abs(dx)-(x1-x0)/2+radius;qy=np.abs(dy)-(y1-y0)/2+radius
    vx,vy=np.maximum(qx,0),np.maximum(qy,0)
    length=np.hypot(vx,vy)
    d=length+np.minimum(np.maximum(qx,qy),0)-radius
    safe=np.maximum(length,1e-12)
    nx,ny=vx/safe*np.sign(dx),vy/safe*np.sign(dy)
    inner=length==0
    nx=np.where(inner,np.where(qx>qy,np.sign(dx),0),nx)
    ny=np.where(inner,np.where(qx>qy,0,np.sign(dy)),ny)
    return d,nx,ny,(qx>0)&(qy>0)


def segments(elements):
    """Flatten supplied curves with a <=1/1024 CSS-pixel chord bound."""
    previous=None;start=None;out=[]
    for e in elements:
        points=[np.asarray(p,float) for p in e['points']]
        if e['type']==0:previous=points[0];start=previous;continue
        if e['type']==4:points=[start]
        if previous is None:raise ValueError('path segment before move')
        if e['type'] in [1,4]:samples=[previous,*points];arc=False
        else:
            if e['type']==2:
                p0,p1,p2=previous,*points
                bound=float(np.linalg.norm(2*(p2-2*p1+p0)))
                n=max(1,math.ceil(math.sqrt(bound*1024/8)))
                t=np.linspace(0,1,n+1)[:,None]
                samples=(1-t)**2*p0+2*(1-t)*t*p1+t*t*p2
            elif e['type']==3:
                p0,p1,p2,p3=previous,*points
                bound=6*max(np.linalg.norm(p2-2*p1+p0),np.linalg.norm(p3-2*p2+p1))
                n=max(1,math.ceil(math.sqrt(bound*1024/8)))
                t=np.linspace(0,1,n+1)[:,None]
                samples=(1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3
            else:raise ValueError('unknown supplied element')
            arc=True
        for a,b in zip(samples,samples[1:]):
            if np.linalg.norm(b-a)>1e-10:out.append((a,b,arc))
        previous=points[-1]
    return out


def geometry(width,height,component,scale,translation=(0,0)):
    path=component['suppliedPaths'][0]
    origin=np.array(path['frameOrigin'])*scale+translation
    size=np.array(component['size'])*scale
    rect=[*origin,*(origin+size)]
    radius=(min(component['size'])/2 if component['kind'].startswith('capsule') else component['radius'])*scale
    y,x=np.mgrid[:height,:width]
    d,nx,ny,arc=stadium(x+.5,y+.5,rect,radius)
    if component['kind']=='capsule-circular':return d,nx,ny,arc
    # Deep interior/exterior classification is unchanged by the subpixel path
    # difference; only the contour neighbourhood needs the supplied curve solve.
    near=np.abs(d)<8*scale
    yy,xx=np.where(near);q=np.column_stack((xx+.5,yy+.5))
    nearest=np.full(len(q),np.inf);signed=np.zeros(len(q));normal=np.zeros((len(q),2));parts=np.zeros(len(q),bool)
    for a,b,is_arc in segments(path['elements']):
        a=a*scale+origin;b=b*scale+origin;v=b-a
        t=np.clip(((q-a)@v)/(v@v),0,1)
        delta=q-(a+t[:,None]*v)
        distance=np.linalg.norm(delta,axis=1)
        outward=np.array([v[1],-v[0]])/np.linalg.norm(v)
        update=distance<nearest
        nearest[update]=distance[update]
        signed[update]=distance[update]*np.where(delta[update]@outward>=0,1,-1)
        normal[update]=outward;parts[update]=is_arc
    d[near]=signed;nx[near]=normal[:,0];ny[near]=normal[:,1];arc[near]=parts
    return d,nx,ny,arc


def strata(d,nx,ny,arc):
    bins=np.floor(np.mod(np.arctan2(ny,nx),2*np.pi)/(2*np.pi/16)+.5).astype(int)%16
    result=[]
    for part,m in [('arc',arc),('straight',~arc)]:
        for shell in range(-2,4):
            for angle in range(16):
                mask=m&(d>=shell)&(d<shell+1)&(bins==angle)
                if mask.any():result.append(((part,shell,angle),mask))
    return result


def fit_alignment(rgb,background,component,scale,opaque=False,space='encoded'):
    """Fit an isoresponse contour; the nuisance outset is NOT a stroke width."""
    h,w=rgb.shape[:2]
    d,_,_,_=geometry(w,h,component,scale)
    native=np.asarray(rgb,float)/255;back=np.asarray(background,float)/255
    decode=lambda a:np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
    if space=='linear':native,back=decode(native),decode(back)
    body=np.median(native[d<=-6],axis=0)
    contrast=(body-back)
    signal=np.sum((native-back)*contrast,axis=2)/np.maximum(np.sum(contrast*contrast,axis=2),1e-12)
    inside=(signal>=.5)&(d<3)
    # Midpoints across inside/outside neighbours are measured boundary samples.
    points=[]
    for axis in [0,1]:
        changed=np.diff(inside.astype(int),axis=axis)!=0
        yy,xx=np.where(changed)
        pts=np.column_stack((xx+.5,yy+.5)).astype(float);pts[:,1-axis]+=.5
        points.extend(pts.tolist())
    if len(points)<4:
        return dict(status='insufficient alignment signal',translationDevicePx=[0,0],
                    physicalContourUncertaintyDevicePx=None,
                    interpretation='nominal supplied-origin cut only; physical alignment unidentified')
    points=np.asarray(points);path=component['suppliedPaths'][0]
    origin=np.array(path['frameOrigin'])*scale;size=np.array(component['size'])*scale
    if component['kind']!='capsule-circular':
        # Linearise signed distance at measured boundary points against the
        # supplied curve, not a stadium masquerading as a continuous corner.
        nearest=np.full(len(points),np.inf);dist=np.zeros(len(points));normals=np.zeros((len(points),2))
        for a,b,_ in segments(path['elements']):
            a=a*scale+origin;b=b*scale+origin;v=b-a
            t=np.clip(((points-a)@v)/(v@v),0,1);delta=points-(a+t[:,None]*v)
            length=np.linalg.norm(delta,axis=1);normal=np.array([v[1],-v[0]])/np.linalg.norm(v)
            mask=length<nearest;nearest[mask]=length[mask]
            dist[mask]=length[mask]*np.where(delta[mask]@normal>=0,1,-1);normals[mask]=normal
        coefficients=np.linalg.lstsq(np.column_stack((normals,np.ones(len(points)))),dist,rcond=None)[0]
        translation=coefficients[:2]
        if np.max(np.abs(translation))>1:
            return dict(status='alignment outside declared one-pixel search',translationDevicePx=[0,0],
                        physicalContourUncertaintyDevicePx=None)
        error=dist-normals@translation-coefficients[2]
        return dict(status='measured supplied-path isoresponse, linearised distance',
            translationDevicePx=translation.tolist(),nuisanceOutsetDevicePx=float(coefficients[2]),
            rmseDevicePx=float(np.sqrt(np.mean(error*error))),pixels=len(points),space=space,
            interpretation='ordinary fill only' if opaque else 'glass half-interior-contrast contour, not hidden raster origin',
            physicalContourUncertaintyDevicePx=.5+scale/1024)
    radius=min(component['size'])/2*scale
    best=None
    for dx in np.arange(-1,1.001,.0625):
        for dy in np.arange(-1,1.001,.0625):
            o=origin+[dx,dy];rect=[*o,*(o+size)]
            values=stadium(points[:,0],points[:,1],rect,radius)[0]
            outset=float(np.median(values));rmse=float(np.sqrt(np.mean((values-outset)**2)))
            candidate=(rmse,abs(dx)+abs(dy),float(dx),float(dy),outset)
            if best is None or candidate<best:best=candidate
    return dict(status='measured isoresponse',translationDevicePx=list(best[2:4]),
        nuisanceOutsetDevicePx=best[4],rmseDevicePx=best[0],pixels=len(points),space=space,
        interpretation='ordinary fill only' if opaque else 'glass half-interior-contrast contour, not hidden raster origin',
        searchStepDevicePx=.0625,physicalContourUncertaintyDevicePx=.5+.006*(min(component['size'])/2)/22*scale)


def body_baseline(rgb,d,kind):
    domain=d<=-6
    body=rgb[domain]
    if not len(body):raise ValueError('no stroke-free interior population')
    beta=np.median(body,axis=0)
    envelope=np.max(np.abs(body-beta),axis=0)+.5
    result=dict(samples=len(body),betaRGB=beta.tolist(),uncertaintyRGB=envelope.tolist(),
                outcome='uniform constrained baseline')
    if kind=='linear-gradient':
        h,w=d.shape;y,x=np.mgrid[:h,:w]
        design=np.stack([np.ones_like(x),x/w-.5,y/h-.5],axis=2)
        coef=np.linalg.lstsq(design[domain],body,rcond=None)[0]
        prediction=np.clip(design@coef,0,255)
        boundary=np.abs(d)<4
        alternatives=[]
        for sx,sy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            kept=domain&~(((x-w/2)*sx>=0)&((y-h/2)*sy>=0))
            fit=np.linalg.lstsq(design[kept],rgb[kept],rcond=None)[0]
            alternatives.append(np.clip(design[boundary]@fit,0,255))
        uncertainty=np.max(np.abs(np.asarray(alternatives)-prediction[boundary]),axis=(0,1))
        uncertainty+=np.max(np.abs(rgb[domain]-prediction[domain]),axis=0)+.5
        result.update(coefficients=coef.tolist(),uncertaintyRGB=uncertainty.tolist(),
                      outcome='affine interior extrapolation, boundary envelope qualified')
    elif kind!='solid':
        result['outcome']='effective rendered contour response; structured body boundary unidentified'
    return result


def analyse(payload):
    rgb=np.asarray(payload['rgb'],float);back=np.asarray(payload['background'],float)
    h,w=rgb.shape[:2];component=payload['component'];scale=payload['scale']
    expected=(int(200*scale),int(320*scale),3)
    if rgb.shape!=expected or back.shape!=expected:
        raise ValueError('payload dimensions disagree with the declared canvas and scale')
    alignment=payload.get('alignment') or {'translationDevicePx':[0,0],'status':'supplied origin; not measured'}
    d,nx,ny,arc=geometry(w,h,component,scale,alignment['translationDevicePx'])
    body=body_baseline(rgb,d,payload.get('backgroundKind','solid'))
    rows=[]
    for (part,shell,angle),mask in strata(d,nx,ny,arc):
        n,b=rgb[mask],back[mask]
        rows.append(dict(part=part,shell=shell,bin=angle,pixels=len(n),admissible=len(n)>=4,
            nativeRGB=n.mean(axis=0).tolist(),backgroundRGB=b.mean(axis=0).tolist(),
            nativeMin=n.min(axis=0).tolist(),nativeMax=n.max(axis=0).tolist(),
            effectiveResponse=residual(n,b)))
    return dict(schema=1,scale=scale,width=w,height=h,alignment=alignment,
        body=body,
        bins=rows)


def pack(payload):
    pixel_keys=['rgb','background','opaque','opaqueInverse','alignmentImage','alignmentBackground']
    value={k:v for k,v in payload.items() if k not in pixel_keys}
    value['pixels']={}
    for name in pixel_keys:
        if name not in payload: continue
        array=np.asarray(payload[name],dtype=np.uint8)
        value['pixels'][name]=dict(shape=list(array.shape),crop=[0,0,array.shape[1],array.shape[0]],
                                  encoding='uint8 RGB row-major base64',data=base64.b64encode(array.tobytes()).decode())
    return gzip.compress(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode(),mtime=0)


def unpack(raw):
    value=json.loads(gzip.decompress(raw))
    pixels=value.pop('pixels')
    for name,row in pixels.items():
        array=np.frombuffer(base64.b64decode(row['data']),dtype=np.uint8).reshape(row['shape']).copy()
        if row['crop'] != [0,0,array.shape[1],array.shape[0]]:raise ValueError('unsupported crop placement')
        value[name]=array
    return value


def synthetic_payload():
    component={'kind':'capsule-circular','size':[120,44],
               'suppliedPaths':[{'frameOrigin':[100,78],'rect':[0,0,120,44],'elements':[]}]}
    d,_,_,_=geometry(320,200,component,1)
    background=np.full((200,320,3),128,dtype=np.uint8)
    rgb=background.copy();rgb[d<0]=180;rgb[(d>=0)&(d<1)]=100
    opaque=np.full_like(rgb,255);opaque[d<0]=0
    return dict(rgb=rgb,background=background,opaque=opaque,component=component,scale=1,
                alignment={'status':'synthetic declared','translationDevicePx':[0,0]})


def forward_circular(pixels,component,scale,background,body,stroke,centre=.5,width=1,
                     samples=64,space='encoded',translation=(0,0)):
    """Subpixel body/stroke composition, with caller-supplied constrained fields.

    Fields return RGB in [0,255]; stroke returns (alpha,target RGB). The body
    value is its already-composited interior endpoint, not a fitted opacity.
    Circular geometry only: continuous candidates must supply their path model
    rather than quietly inherit a circular forward model.
    """
    if component['kind']!='capsule-circular':raise ValueError('circular forward model only')
    path=component['suppliedPaths'][0];origin=np.array(path['frameOrigin'])*scale+translation
    size=np.array(component['size'])*scale;rect=[*origin,*(origin+size)];radius=min(size)/2
    offset=(np.arange(samples)+.5)/samples
    yy,xx=np.meshgrid(offset,offset,indexing='ij');xx=xx.ravel();yy=yy.ravel()
    decode=lambda a:np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
    encode=lambda a:np.where(a<=.0031308,12.92*a,1.055*np.maximum(a,0)**(1/2.4)-.055)
    result=[]
    for x,y in pixels:
        u,v=x+xx,y+yy;d,nx,ny,_=stadium(u,v,rect,radius)
        D=np.asarray(background(u,v),float)/255;B=np.asarray(body(u,v),float)/255
        alpha,target=stroke(u,v,nx,ny);T=np.asarray(target,float)/255
        if space=='linear':D,B,T=decode(D),decode(B),decode(T)
        elif space!='encoded':raise ValueError('unknown composition space')
        a=(d<0)[:,None]
        s=(np.asarray(alpha)*((d>=centre-width/2)&(d<centre+width/2)))[:,None]
        composed=((1-s)*((1-a)*D+a*B)+s*T).mean(axis=0)
        if space=='linear':composed=encode(composed)
        result.append(np.floor(np.clip(composed,0,1)*255+.5))
    return np.asarray(result)


def closure_verdict(rows,candidate_pairs,body_identified):
    """Apply closure AND discrimination; a small point residual alone is not a law.

    Each pair carries predictions from committed candidate families, evaluated
    in both calibration and validation. The caller computes interval residuals
    from the forward-model nuisance envelope, never by increasing the floor.
    Holdout repeats the frozen verdict through the receipt, not a second fit.
    """
    if not rows or any(r['pixels']<4 for r in rows):
        return dict(outcome='insufficient resolution',reason='empty or under-populated required stratum')
    roles={r['role'] for r in rows}
    if not {'calibration','validation'}<=roles:
        return dict(outcome='insufficient resolution',reason='calibration and validation are both required')
    if not candidate_pairs:
        return dict(outcome='insufficient resolution',reason='no competing-family discrimination supplied')
    for pair in candidate_pairs:
        for role in ['calibration','validation']:
            separated={r['stratum'] for r in pair['rows'] if r['role']==role and any(
                delta>2*tau+width for delta,tau,width in zip(
                    r['separationRGB'],r['tauRGB'],r['nuisanceWidthRGB']))}
            if len(separated)<2:
                return dict(outcome='insufficient resolution',reason='families not separated in two strata per fitting role')
    point=all(all(error<=max(1,bar) for error,bar in zip(r['maeRGB'],r['barRGB'])) for r in rows)
    interval=all(all(error<=max(1,bar) for error,bar in zip(r['intervalMAERGB'],r['barRGB'])) for r in rows)
    if point and body_identified:
        return dict(outcome='identified within declared families',reason='point closure and discrimination; holdout still required')
    if point or interval:
        return dict(outcome='effective rendered contour response',reason='compatibility does not identify the body/coverage decomposition')
    return dict(outcome='tested families rejected',reason='absolute channel/shell residual fails even its nuisance interval')
