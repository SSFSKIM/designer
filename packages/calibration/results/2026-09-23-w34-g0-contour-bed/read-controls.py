#!/usr/bin/env python3.12
"""Read control declarations, supplied paths, rendered alignment and sentinels."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
import instrument as I

HERE=Path(__file__).resolve().parent;SCRATCH=Path.home()/'vitrea-w34/scratch'

def image(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.uint8)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    controls=[];alignments=[];paths=[]
    for scale in [1,2]:
        root=SCRATCH/f'controls-{scale}x/run-1'
        admission=json.loads((root/'admission.json').read_text())
        if not admission['admitted']:raise ValueError('control run failed admission; do not use as a dependency')
        spec=json.loads((root/'scenes.json').read_text());m=json.loads((root/'manifest.json').read_text());profile=m['profiles'][0]
        key=profile['profileKey'];entries={f['sceneId']:f for f in profile['fixtures']}
        for b in ['grey','white','black','gradient','split']:
            capture=root/key/f'{b}__none__rest.png';raster=root/'backgrounds'/f'{b}@{scale}x.png'
            a=image(capture);r=image(raster);delta=np.abs(a.astype(int)-r.astype(int))
            declared=None
            if b=='gradient':
                h,w=a.shape[:2];yy,xx=np.mgrid[:h,:w];nx=ny=2**-.5
                t=np.clip(.5+(((xx+.5)/scale-160)*nx+((yy+.5)/scale-100)*ny)/(320*nx+200*ny),0,1)
                declared=np.floor(np.array([32,64,96])*(1-t[:,:,None])+np.array([224,192,160])*t[:,:,None]+.5).astype(np.uint8)
            if b=='split':
                declared=np.full_like(a,128);declared[:,:100*scale]=64
            controls.append(dict(scale=scale,backdrop=b,captureSha256=sha(capture),rasterSha256=sha(raster),
                sckEqualsRaster=bool(np.array_equal(a,r)),maximumChannelDifference=int(delta.max()),
                maeRGB=delta.mean(axis=(0,1)).tolist(),deltaFromBackground=entries[f'{b}__none__rest']['deltaFromBackground'],
                rasterMatchesDeclaredEncoding=None if declared is None else bool(np.array_equal(r,declared)),display=profile['display']))
        for name,b,fill in [('opaque-black','white',0),('opaque-white','black',255),('circular','grey',None)]:
            sid=f'{b}__{name}__rest';rgb=image(root/key/(sid+'.png'));back=image(root/key/(b+'__none__rest.png'))
            component={**spec['components'][name],'suppliedPaths':entries[sid]['suppliedPaths']}
            for space in (['encoded','linear'] if fill is not None else ['encoded']):
                alignments.append(dict(scale=scale,control=name,**I.fit_alignment(rgb,back,component,scale,fill is not None,space)))
            d,_,_,_=I.geometry(rgb.shape[1],rgb.shape[0],component,scale)
            if fill is not None:
                controls.append(dict(scale=scale,control=name,interiorExactlyFill=bool(np.all(rgb[d<=-3]==fill)),
                    farExteriorEqualsBackground=bool(np.array_equal(rgb[d>=3],back[d>=3])),
                    changedBeyondThreeDevicePx=int(np.any(rgb[d>=3]!=back[d>=3],axis=1).sum()),
                    edgeRGBRange=[int(rgb[np.abs(d)<2].min()),int(rgb[np.abs(d)<2].max())],
                    claim='Ordinary opaque fill alignment/coverage only; not a transfer to glassEffect.'))
        for name in ['continuous','circular']:
            sid=f'grey__{name}__rest';paths.append(dict(scale=scale,scene=sid,suppliedPaths=entries[sid]['suppliedPaths']))
    inactive=json.loads((SCRATCH/'inactive/run-1/manifest.json').read_text())
    inactive_rows=[]
    for p in inactive['profiles']:
        for f in p['fixtures']:
            inactive_rows.append(dict(profile=p['profileKey'],scene=f['sceneId'],presentedActive=f['presentedActive'],
                presentation=f['presentation'],materialRendered=f['materialRendered'],deterministic=f['deterministic'],
                repeatNoise=f['repeatNoise'],deltaFromBackground=f['deltaFromBackground']))
    sentinels=[];key='apple-macos-27.0-2x-light-standard-glass0.5'
    for sid in ['grey__circular__rest','checkerboard__circular__rest']:
        images={};orders={};settles={}
        for arm in ['normal','long']:
            images[arm]=[];orders[arm]=[];settles[arm]=[]
            for run in [1,2,3]:
                root=SCRATCH/f'sentinel-{arm}'/f'run-{run}'
                images[arm].append(image(root/key/(sid+'.png')))
                m=json.loads((root/'manifest.json').read_text());f=next(f for f in m['profiles'][0]['fixtures'] if f['sceneId']==sid)
                orders[arm].append(f['orderIndex']);settles[arm].append(f['settleSeconds'])
        allimages=images['normal']+images['long']
        maximum=max(int(np.abs(a.astype(int)-b.astype(int)).max()) for a in allimages for b in allimages)
        sentinels.append(dict(scene=sid,runsPerArm=3,normalInitialSettle=1.75,longInitialSettle=8,longOrderSeed=3401,
            orderIndices=orders,settleSeconds=settles,allSixByteIdentical=maximum==0,maximumChannelDifference=maximum,
            claim=('No byte difference detected in these six captures; not proof all wave cells settle.' if maximum==0 else 'A one-byte difference is observed across the retained runs/protocols; not claimed to be zero or retried away.')))
    result=dict(controls=controls,alignment=alignments,suppliedPaths=paths,inactive=inactive_rows,sentinels=sentinels)
    (HERE/'control-readings.json').write_text(json.dumps(result,indent=2)+'\n')
    print('backdrop equality',[(r['scale'],r.get('backdrop'),r.get('sckEqualsRaster')) for r in controls if 'backdrop' in r])
    print('alignment',alignments);print('sentinels',sentinels)


if __name__=='__main__':main()
