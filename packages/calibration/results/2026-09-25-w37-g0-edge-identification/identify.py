"""Native-only fixed-grid identification and separately measured body transfer (§5.181).

All optical outputs are a sibling extension of edge.forward. Neither validation
nor a web pixel contributes an objective term. Tables retain every bin/channel.
"""
import base64,gzip,hashlib,io,itertools,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
import law
edge=law.edge; HERE=law.HERE; OLD=HERE.parent/'2026-09-24-w35-g0-edge-cut'
CAL=HERE.parent.parent; ROOT=CAL.parent.parent


def inputs():
    wave=edge.W.default_wave();repeat=wave.reader(edge.G1/'repeat');probe=wave.reader(edge.G1/'probe')
    old=json.loads(gzip.decompress((OLD/'profiles.json.gz').read_bytes()))
    black={r['cell']:r for r in json.loads((HERE/'diagnostics.json').read_text())['w36BlackReplay']}
    oldweb=edge.WebReader.w34()
    records=[]
    for rec in old:
        if rec['backgroundKind']!='solid':continue
        cell=rec['cell'];assert wave.roles[cell.split('/')[1]] in ('calibration','validation')
        crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
        run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
        raw=base64.b64decode(crop['states'][run['state']]);assert hashlib.sha256(raw).hexdigest()==run['state']
        p=edge.I.unpack(raw);d,nx,ny,arc,angle,whole=edge.geometry(p);s=p['scale']
        n=np.asarray(Image.open(io.BytesIO(probe.read(cell,'png'))).convert('RGB'),float)
        b=np.median(n[d<=-6*s],0);assert np.array_equal(b,rec['deep']['nativeMedian'])
        web=np.asarray(Image.open(io.BytesIO(oldweb.read(cell))).convert('RGB'),float)
        wb=np.median(web[d<=-6*s],0);assert np.array_equal(wb,rec['deep']['webMedian'])
        web_origin='W34 guarded historical web; W36 non-black branch unchanged'
        if cell in black:
            wb=np.asarray(black[cell]['deep']);web_origin='W36 preserved black price; shipped patch equivalence in provenance.json'
        circular=p['component']['kind']=='capsule-circular'
        # Noncircular arcs are not nominated as whole pixels. Exact straight
        # normals with at least half a device pixel depth have full coverage;
        # continuous-path points remain transfer diagnostics, never fit closure.
        admitted=whole if circular else (~arc)&(np.maximum(abs(nx),abs(ny))>1-1e-10)&(d<=-.5+1e-10)
        domain=(d>=-6*s)&(d<0)&admitted
        bins=[];weight=np.zeros(d.shape,float)
        for part,pm in [('arc',arc),('straight',~arc)]:
            for sh in range(-6*s,0):
                for a in range(16):
                    m=domain&pm&(d>=sh)&(d<sh+1)&(angle==a)
                    count=int(m.sum())
                    if not count:continue
                    ix=np.flatnonzero(m)
                    bins.append(dict(part=part,shell=sh,bin=a,pixels=count,indices=ix,admissible=count>=4))
                    if count>=4:weight[m]=1/count
        ix=np.flatnonzero(domain);remap=np.full(d.size,-1);remap[ix]=np.arange(len(ix))
        for r in bins:r['indices']=remap[r['indices']]
        yy,xx=np.indices(d.shape);origin=np.array(p['component']['suppliedPaths'][0]['frameOrigin'])*s+p['alignment']['translationDevicePx']
        half=np.array(p['component']['size'])*s/2
        along=np.clip(((xx+.5-origin[0]-half[0])/half[0])*((yy+.5-origin[1]-half[1])/half[1]),-1,1)
        records.append(dict(cell=cell,role=wave.roles[cell.split('/')[1]],scale=s,
            scheme='dark' if '-dark-' in cell.split('/')[0] else 'light',active=cell.endswith('__rest'),
            circular=circular,geometry=p['component']['kind'],span=min(p['component']['size']),
            body=b,webBody=wb,webOrigin=web_origin,native=n.reshape(-1,3)[ix],
            d=d.ravel()[ix]/s,ny=ny.ravel()[ix],nx=nx.ravel()[ix],along=along.ravel()[ix],
            weight=weight.ravel()[ix],bins=bins))
    return records


def search(records,space,scheme):
    fit=[r for r in records if r['active'] and r['circular'] and r['role']=='calibration' and r['scheme']==scheme]
    body=np.concatenate([np.broadcast_to(r['body']/255,r['native'].shape) for r in fit])
    native=np.concatenate([r['native']/255 for r in fit]);d=np.concatenate([r['d'] for r in fit]);ny=np.concatenate([r['ny'] for r in fit])
    weights=np.concatenate([r['weight'] for r in fit])
    valid=(body<254.5/255)&(native<254.5/255)&(weights[:,None]>0)
    if space=='linear':body=edge.decode(body);native=edge.decode(native)
    # Equal total mass per bin/channel among its uncensored pixels.
    mass=np.broadcast_to(weights[:,None],valid.shape).copy()
    start=0
    for r in fit:
        for b in r['bins']:
            ids=start+b['indices']
            for channel in range(3):
                ok=valid[ids,channel];count=int(ok.sum())
                if count:mass[ids[ok],channel]=1/count
        start+=len(r['d'])
    sw=np.sqrt(mass[valid]);y=(native-body)[valid]*sw
    best=None;trials=[]
    for width,shoulder,share,exponent in itertools.product(np.arange(.8,2.401,.2),[3.,4.5,6.],[.05,.15,.3,.5],[1.,2.,3.,4.,6.]):
        shape=dict(width=float(round(width,5)),shoulder=shoulder,share=share,exponent=exponent)
        x=law.features(body,d,ny,shape,space)[valid]*sw[:,None]
        coefficients,_,rank,singular=np.linalg.lstsq(x,y,rcond=None)
        error=float(np.mean((x@coefficients-y)**2))
        row=dict(shape=shape,coefficients=coefficients.tolist(),rank=int(rank),singularValues=singular.tolist(),ownSpaceMSE=error)
        trials.append(row)
        if best is None or error<best['ownSpaceMSE']:best=row
    return dict(space=space,scheme=scheme,fitCells=[r['cell'] for r in fit],fitScalarObservations=int(valid.sum()),
        thickness={'form':'none','factor':1,'freeParameters':0,'calibrationSpans':sorted(set(r['span'] for r in fit))},
        **best),trials


def score(records,fit):
    space=fit['space'];shape=fit['shape'];coeff=np.asarray(fit['coefficients']);rows=[];transfer=[]
    for r in records:
        if r['scheme']!=fit['scheme']:continue
        b=r['body']/255;wb=r['webBody']/255
        if space=='linear':b=edge.decode(b);wb=edge.decode(wb)
        c=coeff if r['active'] else np.zeros(5)
        n=law.forward(b,r['d'],r['ny'],shape,c,space)['encoded']
        w=law.forward(wb,r['d'],r['ny'],shape,c,space)['encoded']
        tr=(w-r['webBody'])-(n-r['body'])
        celltr=[]
        for bn in r['bins']:
            ids=bn['indices'];res=abs(n[ids]-r['native'][ids]).mean(0)
            signed=(n[ids]-r['native'][ids]).mean(0)
            nativeExcess=(r['native'][ids]-r['body']).mean(0)
            predExcess=(n[ids]-r['body']).mean(0)
            census=((r['body']>=254.5)[None,:]|(r['native'][ids]>=254.5)).any(0)
            item={k:v for k,v in bn.items() if k!='indices'}
            item.update(cell=r['cell'],role=r['role'],active=r['active'],geometry=r['geometry'],
                closure=r['circular'],space=space,scheme=r['scheme'],scale=r['scale'],
                nativeExcess=nativeExcess.tolist(),predictedExcess=predExcess.tolist(),
                residualRGB=res.tolist(),signedResidualRGB=signed.tolist(),
                censoredChannels=np.flatnonzero(census).tolist(),toleranceRGB=[1,1,1],
                fails=bn['admissible'] and bool(np.any(res>1)))
            rows.append(item)
            celltr.append(dict(part=bn['part'],shell=bn['shell'],bin=bn['bin'],pixels=bn['pixels'],admissible=bn['admissible'],
                edgeTransferRGB=tr[ids].mean(0).tolist(),rawOutputTransferRGB=(w[ids]-n[ids]).mean(0).tolist()))
        transfer.append(dict(cell=r['cell'],role=r['role'],space=space,scheme=r['scheme'],
            nativeDeep=r['body'].tolist(),webDeep=r['webBody'].tolist(),webOrigin=r['webOrigin'],
            edgeTransferPixelRange=[float(tr.min()),float(tr.max())],bins=celltr))
    return rows,transfer


def main():
    # Git ancestry pins chronological declaration, not a timestamp assertion.
    pins=json.loads((HERE/'declaration-pins.json').read_text())
    for name,sha in pins.items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==sha
    subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor','6f2e89ed','HEAD'],check=True)
    if (HERE/'fits.json').exists():raise FileExistsError('refuse to rewrite recorded scores')
    records=inputs();fits=[];trials=[];residuals=[];transfer=[];summary=[]
    for space in ['linear','encoded']:
        for scheme in ['light','dark']:
            fit,trial=search(records,space,scheme);fits.append(fit);trials.append(dict(space=space,scheme=scheme,trials=trial))
            rr,tt=score(records,fit);residuals+=rr;transfer+=tt
            for role in ['calibration','validation']:
                selected=[r for r in rr if r['active'] and r['role']==role and r['closure'] and r['admissible']]
                straight=[r for r in selected if r['part']=='straight']
                diagnostic=[r for r in rr if r['active'] and r['role']==role and not r['closure'] and r['admissible']]
                summary.append(dict(space=space,scheme=scheme,role=role,bins=len(selected),failedBins=sum(r['fails'] for r in selected),
                    maxCodes=max(max(r['residualRGB']) for r in selected),straightMaxCodes=max(max(r['residualRGB']) for r in straight),
                    diagnosticMaxCodes=max([max(r['residualRGB']) for r in diagnostic],default=None),
                    worst=max(selected,key=lambda r:max(r['residualRGB']))))
            print(space,scheme,fit,flush=True)
    edge.save(HERE/'fits.json',fits);edge.save(HERE/'search.json.gz',trials)
    edge.save(HERE/'residuals.json.gz',residuals);edge.save(HERE/'transfer.json.gz',transfer)
    eligible=[space for space in ['linear','encoded'] if all(s['maxCodes']<=1 for s in summary if s['space']==space)]
    edge.save(HERE/'family-summary.json',dict(declarationCommit='6f2e89ed',nomination='none' if not eligible else 'requires transfer review: '+','.join(eligible),rows=summary))
    print('SUMMARY',summary,flush=True)
if __name__=='__main__':main()
