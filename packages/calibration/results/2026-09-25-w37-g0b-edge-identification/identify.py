"""Finite native-only search under the committed G0b budget (§5.182)."""
import gzip,hashlib,itertools,json,subprocess
import numpy as np
import law
from common import HERE,G0,ROOT,edge,oldidentify
DECLARATION='89f45616'
SHA='0ddc766612ab8f84143b7cef665e889c80437c423fc39e8253564d51b4f769bd'
CACHE={}
BARS={(r['cell'],b['part'],b['shell'],b['bin']):b['tauRGB']
      for r in json.loads(gzip.decompress((G0/'closure-bars.json.gz').read_bytes())) for b in r['bins']}

def inputs():
    records=oldidentify.inputs()
    for r in records:
        r['arc']=np.zeros(len(r['d']),bool)
        for b in r['bins']:
            if b['part']=='arc':r['arc'][b['indices']]=True
        r['geometryKey']=hashlib.sha256(b''.join(r[k].tobytes() for k in ['d','nx','ny','arc'])+str((r['span'],r['scale'])).encode()).hexdigest()
    return records

def radial(r,shape,family,order=8):
    key=(r['geometryKey'],shape['width'],shape['exponent'],family=='F2',order)
    if key not in CACHE:CACHE[key]=law.radial(r,shape,family,order)
    return CACHE[key]

def fit_population(records,scheme):
    return [r for r in records if r['active'] and r['circular'] and r['role']=='calibration' and r['scheme']==scheme]

def observations(records,shape,family):
    xs=[];ys=[];mass=0
    for r in records:
        b=r['body']/255;n=r['native']/255
        x=law.features(b,radial(r,shape,family),family);valid=(b<254.5/255)&(n<254.5/255)
        weights=np.zeros(n.shape)
        for bn in r['bins']:
            if not bn['admissible']:continue
            for c in range(3):
                ids=bn['indices'];keep=ids[valid[ids,c]]
                if len(keep):weights[keep,c]=1/len(keep);mass+=1
        keep=weights>0;sw=np.sqrt(weights[keep]);xs.append(x[keep]*sw[:,None]);ys.append((n-b)[keep]*sw)
    return np.concatenate(xs),np.concatenate(ys),mass

def search(records,family,scheme):
    population=fit_population(records,scheme);best=None;trials=[]
    for width,exponent in itertools.product([.8,1.,1.2,1.4,1.6,1.8,2.,2.2,2.4],[1,2,3,4,6]):
        shape=dict(width=width,exponent=exponent)
        x,y,mass=observations(population,shape,family)
        c,_,rank,singular=np.linalg.lstsq(x,y,rcond=None)
        mse=float(np.sum((x@c-y)**2)/mass)
        accepted=rank==x.shape[1] and float(abs(c).max())<=4096
        row=dict(shape=shape,coefficients=c.tolist(),rank=int(rank),columns=x.shape[1],
            singularValues=singular.tolist(),encodedMSE=mse,accepted=bool(accepted),
            observations=len(y),fittingMass=mass)
        trials.append(row)
        if accepted and (best is None or mse<best['encodedMSE']):best=row
    assert best is not None
    return dict(family=family,scheme=scheme,fitCells=[r['cell'] for r in population],
        thicknessFactor=1,**best),dict(family=family,scheme=scheme,trials=trials)

def score(records,fit,order=8):
    rows=[];transfer=[];family=fit['family'];shape=fit['shape'];coeff=np.asarray(fit['coefficients'])
    for r in records:
        if r['scheme']!=fit['scheme']:continue
        rad=radial(r,shape,family,order);b=r['body']/255;wb=r['webBody']/255
        c=coeff if r['active'] else np.zeros_like(coeff)
        pred=law.forward(b,law.features(b,rad,family),c,r['d'])
        web=law.forward(wb,law.features(wb,rad,family),c,r['d'])
        tr=(web-r['webBody'])-(pred-r['body']);tb=[]
        for bn in r['bins']:
            ids=bn['indices'];res=abs(pred[ids]-r['native'][ids]).mean(0)
            tau=BARS.get((r['cell'],bn['part'],bn['shell'],bn['bin']),[1,1,1])
            if r['circular']:assert (r['cell'],bn['part'],bn['shell'],bn['bin']) in BARS
            item={k:v for k,v in bn.items() if k!='indices'}
            item.update(cell=r['cell'],role=r['role'],active=r['active'],geometry=r['geometry'],
                closure=r['circular'],family=family,scheme=r['scheme'],scale=r['scale'],
                nativeExcess=(r['native'][ids]-r['body']).mean(0).tolist(),
                predictedExcess=(pred[ids]-r['body']).mean(0).tolist(),residualRGB=res.tolist(),
                signedResidualRGB=(pred[ids]-r['native'][ids]).mean(0).tolist(),
                censoredChannels=np.flatnonzero(((r['body']>=254.5)[None,:]|(r['native'][ids]>=254.5)).any(0)).tolist(),
                toleranceRGB=tau,fails=bool(bn['admissible'] and np.any(res>np.array(tau)+1e-12)))
            rows.append(item)
            tb.append(dict(part=bn['part'],shell=bn['shell'],bin=bn['bin'],admissible=bn['admissible'],
                pixels=bn['pixels'],edgeTransferRGB=tr[ids].mean(0).tolist(),
                rawOutputTransferRGB=(web[ids]-pred[ids]).mean(0).tolist()))
        transfer.append(dict(cell=r['cell'],role=r['role'],active=r['active'],family=family,scheme=r['scheme'],
            nativeDeep=r['body'].tolist(),webDeep=r['webBody'].tolist(),webOrigin=r['webOrigin'],
            edgeTransferPixelRange=[float(tr.min()),float(tr.max())],bins=tb))
    return rows,transfer

def summary(rows):
    out=[]
    for scheme,role in itertools.product(['light','dark'],['calibration','validation']):
        pool=[r for r in rows if r['scheme']==scheme and r['role']==role and r['active'] and r['admissible']]
        for name,selected in [('circular', [r for r in pool if r['closure']]),
            ('diagnostic',[r for r in pool if not r['closure']]),
            ('grey-straight',[r for r in pool if r['part']=='straight' and '/grey-' in r['cell']])]:
            if not selected:continue
            worst=max(selected,key=lambda r:max(r['residualRGB']))
            out.append(dict(family=rows[0]['family'],scheme=scheme,role=role,stratum=name,
                bins=len(selected),failedBins=sum(r['fails'] for r in selected),
                maximum=max(worst['residualRGB']),worst=worst))
    return out

def grey_closes(rows):
    chosen=[r for r in rows if r['active'] and r['admissible'] and r['role']=='calibration'
            and '/grey-' in r['cell'] and r['part']=='straight']
    assert {(r['scheme'],r['scale']) for r in chosen}=={('light',1),('dark',1),('light',2),('dark',2)}
    return not any(r['fails'] for r in chosen)

def main():
    assert hashlib.sha256((HERE/'bounds-declaration.txt').read_bytes()).hexdigest()==SHA
    subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',DECLARATION,'HEAD'],check=True)
    subprocess.run(['python3.12',str(HERE/'test-instrument.py')],check=True)
    if (HERE/'fits.json').exists():raise FileExistsError('scores are write-once')
    records=inputs();fits=[];trials=[];allrows=[];transfers=[];summaries=[];closures={}
    for family in ['F1','F2','F3']:
        if family=='F3' and any(closures.values()):break
        familyrows=[]
        for scheme in ['light','dark']:
            fit,trial=search(records,family,scheme);fits.append(fit);trials.append(trial)
            rr,tt=score(records,fit);familyrows+=rr;allrows+=rr;transfers+=tt
            print(family,scheme,'shape',fit['shape'],'rank',fit['rank'],'MSE',fit['encodedMSE'],flush=True)
        closures[family]=grey_closes(familyrows);ss=summary(familyrows);summaries+=ss
        print(family,'grey closes',closures[family],[(x['scheme'],x['role'],x['stratum'],x['maximum']) for x in ss],flush=True)
    edge.save(HERE/'fits.json',fits);edge.save(HERE/'search.json.gz',trials)
    edge.save(HERE/'residuals.json.gz',allrows);edge.save(HERE/'transfer.json.gz',transfers)
    edge.save(HERE/'family-summary.json',dict(declarationCommit=DECLARATION,declarationSha256=SHA,
        greyClosure=closures,hardStop=not any(closures.values()),rows=summaries))

if __name__=='__main__':main()
