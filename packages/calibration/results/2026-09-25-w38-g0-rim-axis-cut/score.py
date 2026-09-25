"""Predeclared minimax subject to veto, with native-only inputs (§5.183)."""
import itertools,subprocess,hashlib,json
from model import HERE,ROOT,edge,np,inputs,params,predict,stratum

def guard():
    receipt=json.loads((HERE/'declaration-receipt.json').read_text())
    subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',receipt['commit'],'HEAD'],check=True)
    for file,sha in receipt['sha256'].items():assert hashlib.sha256((HERE/file).read_bytes()).hexdigest()==sha,file
    return receipt

def grid(scheme):
    g=json.loads((HERE/'search-grid.json').read_text())
    for p,w,a,v,l,k in itertools.product(g['exponent'],g['widthPairs'][scheme],g['a'][scheme],g['g'][scheme],g['along'],g['shadowProduct']):
        yield dict(axis=[0,-1],exponent=p,widths=w,a=a,g=v,along=l,shadowProduct=k)
    yield g['extraPoint']

def packed(records):
    # Pack pixels in bin order so reduceat is an independent absolute-before-mean
    # reduction, not the old-rim artifact's absolute signed-mean error.
    values={k:[] for k in ['body','native','d','nx','ny','along','scale','reach','old']};starts=[];counts=[];labels=[];censors=[];horizontal=[];n=0
    for r in records:
        old=predict(r,params(r['scheme']))
        for b in r['bins']:
            if not b['admissible']:continue
            ix=b['indices'];count=len(ix);starts.append(n);n+=count;counts.append(count);labels.append(stratum(r,b));horizontal.append(b['bin'] in (0,8))
            censors.append(((r['body']>=254.5)[None,:]|(r['native'][ix]>=254.5)).any(0))
            for key,x in [('body',np.broadcast_to(edge.decode(r['body']/255),r['native'].shape)),('native',r['native']),('old',old),('d',r['d']),('nx',r['nx']),('ny',r['ny']),('along',r['k']*r['along']),('scale',np.full(len(r['d']),r['scale'])),('reach',np.full(len(r['d']),r['reach']))]:values[key].append(x[ix])
    data={k:np.concatenate(v) for k,v in values.items()};data.update(starts=np.array(starts),counts=np.array(counts),labels=np.array(labels),censored=np.array(censors),horizontal=np.array(horizontal))
    data['oldError']=reduce(data,abs(data['old']-data['native']));return data

def reduce(d,v):return np.add.reduceat(v,d['starts'],axis=0)/d['counts'][:,None]

def forward(d,p):
    return edge.forward(d['body'],d['d'],1,a=p['a'],g=p['g'],width=np.where(d['scale']==1,p['widths'][0],p['widths'][1]),shadow_depth=p['shadowProduct'],shadow_alpha=1,shadow_reach=d['reach'],lit=np.maximum(abs(d['nx']*p['axis'][0]+d['ny']*p['axis'][1])*np.sqrt(2),1e-6)**p['exponent'],along=np.maximum(1+p['along']*d['along'],0))['encoded']

def constraints(d,error):
    old=d['oldError'];veto=float(np.max(error-old));h=float(np.max(error[d['horizontal']]))
    stats=[]
    for s in sorted(set(d['labels'])):
        mask=d['labels']==s;x=error[mask];o=old[mask]
        stats.append(dict(stratum=s,bins=int(mask.sum()),maximum=float(x.max()),mean=float(x.mean()),oldMaximum=float(o.max()),oldMean=float(o.mean())))
    stratumExcess=max(max(r['maximum']-r['oldMaximum']-.5,r['mean']-r['oldMean']-.5) for r in stats)
    excess=max(0,veto-1,h-2,stratumExcess)
    objective=float(error[~d['censored']].max())
    return dict(minimax=objective,maximumWorsening=veto,horizontalMaximum=h,maximumConstraintExcess=excess,feasible=excess<=1e-10,strata=stats)

def search(records,scheme,independent=False):
    fit=[r for r in records if r['scheme']==scheme and r['circular'] and r['backgroundKind']=='solid'];assert len(fit)==28
    d=packed(fit);trials=[];best=None;failed=None
    for index,p in enumerate(grid(scheme)):
        error=reduce(d,abs(forward(d,p)-d['native']));c=constraints(d,error);row=dict(index=index,parameters=p,**{k:v for k,v in c.items() if k!='strata'});trials.append(row)
        if c['feasible'] and (best is None or c['minimax']<best['minimax']):best=row
        if failed is None or (c['maximumConstraintExcess'],c['minimax'])<(failed['maximumConstraintExcess'],failed['minimax']):failed=row
    return dict(scheme=scheme,fitCells=[r['cell'] for r in fit],points=len(trials),feasiblePoints=sum(r['feasible'] for r in trials),selected=best,failureWitness=failed),trials

def score_records(records,pmap,candidate):
    bins=[];transfers=[]
    for r in records:
        p=pmap[r['scheme']];pred=predict(r,p);old=predict(r,params(r['scheme']));tr=None
        if r['webBody'] is not None:tr=(predict(r,p,r['webBody'])-r['webBody'])-(pred-r['body'])
        tb=[]
        for b in r['bins']:
            ix=b['indices'];res=abs(pred[ix]-r['native'][ix]).mean(0);ores=abs(old[ix]-r['native'][ix]).mean(0)
            row={k:v for k,v in b.items() if k!='indices'}
            row.update(candidate=candidate,cell=r['cell'],scheme=r['scheme'],stratum=stratum(r,b),nativeExcess=(r['native'][ix]-r['body']).mean(0).tolist(),oldExcess=(old[ix]-r['body']).mean(0).tolist(),predictedExcess=(pred[ix]-r['body']).mean(0).tolist(),residualRGB=res.tolist(),oldResidualRGB=ores.tolist(),worseningRGB=(res-ores).tolist(),vetoRGB=(res-ores>1+1e-10).tolist(),veto=bool(b['admissible'] and np.any(res-ores>1+1e-10)),censoredChannels=np.flatnonzero(((r['body']>=254.5)[None,:]|(r['native'][ix]>=254.5)).any(0)).tolist())
            bins.append(row)
            if tr is not None:tb.append(dict(part=b['part'],bin=b['bin'],shell=b['shell'],admissible=b['admissible'],edgeTransferRGB=tr[ix].mean(0).tolist()))
        if tr is not None:transfers.append(dict(candidate=candidate,cell=r['cell'],nativeDeep=r['body'].tolist(),webDeep=r['webBody'].tolist(),webOrigin=r['webOrigin'],pixelRange=[float(tr.min()),float(tr.max())],bins=tb))
    summaries=[]
    for scheme in ['light','dark']:
        for st in sorted(set(b['stratum'] for b in bins)):
            rr=[b for b in bins if b['scheme']==scheme and b['stratum']==st and b['admissible']]
            if not rr:continue
            errors=np.array([b['residualRGB'] for b in rr]);old=np.array([b['oldResidualRGB'] for b in rr]);delta=errors-old
            hh=[b for b in rr if b['bin'] in (0,8)]
            summaries.append(dict(candidate=candidate,scheme=scheme,stratum=st,bins=len(rr),maximum=float(errors.max()),mean=float(errors.mean()),oldMaximum=float(old.max()),oldMean=float(old.mean()),vetoChannels=int((delta>1+1e-10).sum()),maximumWorsening=float(delta.max()),better=int((delta<-.5).sum()),same=int((abs(delta)<=.5).sum()),worse=int((delta>.5).sum()),horizontalMaximum=max((max(b['residualRGB']) for b in hh),default=None),worst=max(rr,key=lambda b:max(b['worseningRGB']))))
    return bins,summaries,transfers

if __name__=='__main__':
    receipt=guard();assert not (HERE/'candidate-summary.json').exists(),'no rewriting scores'
    native=inputs(structured=True,web=False);fits=[];trials=[]
    for scheme in ['light','dark']:
        fit,tt=search(native,scheme);fits.append(fit);trials.append(dict(scheme=scheme,trials=tt));print('SEARCH',json.dumps(fit),flush=True)
    # Only AFTER selection, open independently recorded web bodies for transfer.
    records=inputs(structured=True,web=True);allbins=[];summary=[];transfer=[]
    for label,pmap in [('C1',{s:params(s,'C1') for s in ['light','dark']}),('C2',{f['scheme']:(f['selected'] or f['failureWitness'])['parameters'] for f in fits})]:
        b,s,t=score_records(records,pmap,label);allbins+=b;summary+=s;transfer+=t
    edge.save(HERE/'search-results.json.gz',trials);edge.save(HERE/'fits.json',fits);edge.save(HERE/'candidate-bins.json.gz',allbins);edge.save(HERE/'transfer.json.gz',transfer)
    result=dict(declarationCommit=receipt['commit'],nomination='none' if any(f['selected'] is None for f in fits) or any(s['vetoChannels'] for s in summary if s['candidate']=='C2') else 'C2 requires all other constraints and canonical reading',C2TableMeaning='selected feasible point where available, otherwise explicitly failed minimum-constraint-excess witness',rows=summary)
    edge.save(HERE/'candidate-summary.json',result);print('DONE',result['nomination'],[(s['candidate'],s['scheme'],s['stratum'],s['maximum'],s['vetoChannels']) for s in summary],flush=True)
