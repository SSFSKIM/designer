#!/usr/bin/env python3.12
"""W41 step 3, on the declared calibration strip only (clause 6, DL6).

Usage: read-spatial.py selected-body.json output-directory
The body selection is explicit and retained with every result. No native holdout
or validation is opened: this bed has no spatial transfer/closure referee.
"""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import spatial

HERE=Path(__file__).resolve().parent
E=HERE.parent
G0=E.parent/'2026-09-27-w41-g0-declaration'
G2=E.parent/'2026-09-26-w39-g2-identification'
ROOT=E.parents[3]
sys.path.insert(0,str(G0/'instrument'))
import instrument as m
sys.path.insert(0,str(G2))
import native
spec=importlib.util.spec_from_file_location('body41',G0/'body-instrument/body41.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

def save(path,value):
    raw=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    if path.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
    with path.open('xb') as f:f.write(raw)

def main():
    selection_path=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()
    config=json.loads(selection_path.read_text())
    if set(config['endpoints'])!={'light-active','light-inactive','dark-active','dark-inactive'}:raise ValueError('all endpoints required')
    if out.exists():raise ValueError('new output directory required')
    declaration=G0/'bounds-declaration.txt'
    if hashlib.sha256(declaration.read_bytes()).hexdigest()!='850747c1f03781a6efe9b433bd4ce3bd6cf72b63c9befd8d5d98de9eadf7f759':raise ValueError('declaration changed')
    w,r=native.guarded(Path((E/'archive-root.txt').read_text().strip()),('calibration',))
    if r.generation!='58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61':raise ValueError('archive changed')
    scenes=set(json.loads((G0/'closure.json').read_text())['strip']['scenes'])
    rows=[]
    for cell in sorted({cell for cell,kind in r.entries if kind=='crop' and cell.split('/',1)[1] in scenes}):
        sid=cell.split('/',1)[1]
        if w.roles[sid]!='calibration':raise ValueError('spatial fitting must be calibration')
        runs,states=native.archive.unbundle(r.read(cell,'crop'))
        runs=[v for v in runs if v['admitted'] and v['protocol']=='normal']
        if len(runs)!=7:raise ValueError('seven repeats required')
        unpacked={v:native.archive.unpack(states[v]) for v in {run['state'] for run in runs}}
        payloads=[unpacked[run['state']] for run in runs];p=payloads[0]
        shape=m.readers.shapes_of(p['component'])
        if len(shape)!=1:raise ValueError('one declared shape required')
        strip=m.gradient_strip(np.array([v['rgb'] for v in payloads]),np.array([v['noGlass'] for v in payloads]),shape[0],p['scale'])
        references=np.asarray(strip['referenceRuns']);means=np.asarray(strip['groupReferenceMean'])
        if np.any(np.ptp(references,axis=0)) or np.any(np.ptp(means,axis=0)):raise ValueError('reference changed across repeats')
        rows.append(dict(cell=cell,scale=p['scale'],endpoint=p['scheme']+'-'+p['pose'],states=[v['state'] for v in runs],**strip))
    if len(rows)!=16:raise ValueError('expected all16 declared gradient cells')
    results={};tables=[];resolution=[];reflected=[]
    for endpoint,body in config['endpoints'].items():
        cells=[row for row in rows if row['endpoint']==endpoint]
        if len(cells)!=4:raise ValueError('two directions at both scales required')
        x=np.concatenate([c['reference'] for c in cells]);target=np.concatenate([c['native'] for c in cells]);bar=np.concatenate([c['bar'] for c in cells])
        means=np.concatenate([np.broadcast_to(np.asarray(c['groupReferenceMean'])[0],(len(c['yCSS']),3)) for c in cells])
        y=np.concatenate([np.asarray(c['yCSS'])/44 for c in cells])
        mass=np.concatenate([np.full(len(c['yCSS']),1/len(cells)/len(c['yCSS'])) for c in cells])
        active=endpoint.endswith('-active')
        def tone(z):return b.forward(body['family'],z,body['neutral'],body['coefficients'])
        fits={family:spatial.fit(family,x,means,y,target,mass,tone,active) for family in ('S0','S1','S2')}
        results[endpoint]=dict(body=body,fits=fits)
        predictions={}
        for family,fit in fits.items():
            for objective in ('leastSquares','minimax'):
                selected=fit[objective]
                if selected is None:
                    tables.append(dict(endpoint=endpoint,family=family,objective=objective,status='no converged local candidate'));continue
                prediction=spatial.predict(family,selected['coefficients'],x,means,y,tone,active)
                if objective=='minimax':predictions[family]=prediction
                cursor=0
                for cell in cells:
                    n=len(cell['yCSS']);p=prediction[cursor:cursor+n];cursor+=n
                    t=np.asarray(cell['native']);repeats=np.asarray(cell['runs']);bars=np.asarray(cell['bar']);errors=abs(p-t)
                    all_errors=abs(repeats-p[None,:,:]);maximum=float(max(errors.max(),all_errors.max()));ix=np.unravel_index(np.argmax(all_errors),all_errors.shape)
                    tables.append(dict(endpoint=endpoint,family=family,objective=objective,cell=cell['cell'],scale=cell['scale'],coefficients=selected['coefficients'],classification=fit['classification'],medianMaximumCodes=float(errors.max()),allRepeatMaximumCodes=float(all_errors.max()),maximumCodes=maximum,measuredChannels=int(t.size),censoredChannels=0,failedComparisons=int(np.sum(all_errors>np.maximum(1,bars)[None,:,:])),allChannelFailedRows=int(np.sum(np.all(all_errors>np.maximum(1,bars)[None,:,:],axis=2))),survives=bool(np.all(all_errors<=np.maximum(1,bars)[None,:,:])),worst=dict(run=int(ix[0]),row=int(ix[1]),channel='RGB'[ix[2]],depthCSS=cell['depthCSS'][ix[1]]),predicted=p.tolist(),medianErrors=errors.tolist(),repeatErrors=all_errors.tolist(),bar=bars.tolist()))
        for a,bb in [('S0','S1'),('S0','S2'),('S1','S2')]:
            if a not in predictions or bb not in predictions:continue
            delta=abs(predictions[a]-predictions[bb]);limit=np.maximum(3,2*bar)
            resolution.append(dict(endpoint=endpoint,pair=[a,bb],maximumSeparationCodes=float(delta.max()),verdict='separated instances' if np.any(delta>=limit) else 'insufficient resolution',survivalNotImplied=True))
        for scale in (1,2):
            pair=sorted([c for c in cells if c['scale']==scale],key=lambda c:c['cell'])
            a=next(c for c in pair if '/v90-' in c['cell']);bb=next(c for c in pair if '/v270-' in c['cell'])
            np.testing.assert_array_equal(a['reference'],np.asarray(bb['reference'])[::-1])
            delta=np.asarray(a['native'])-np.asarray(bb['native'])[::-1]
            reflected.append(dict(endpoint=endpoint,scale=scale,cells=[a['cell'],bb['cell']],equalLocalReference=True,maximumDifferenceCodes=float(abs(delta).max()),differenceCodes=delta.tolist(),depthCSS=a['depthCSS']))
    out.mkdir(parents=True)
    save(out/'observations.json.gz',dict(roles=['calibration'],inventory=r.generation,rows=rows))
    save(out/'fits.json',results)
    save(out/'scores.json.gz',tables)
    save(out/'resolution.json',resolution)
    save(out/'reflected.json',reflected)
    save(out/'provenance.json',dict(selection=config,selectionPath=str(selection_path),selectionSha256=hashlib.sha256(selection_path.read_bytes()).hexdigest(),declarationSha256=hashlib.sha256(declaration.read_bytes()).hexdigest(),archiveInventory=r.generation,rawRootDenied=str(Path.home()/'vitrea-w39'),holdoutOpened=False,spatialLeaf=False,sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'spatial.py',G0/'instrument/instrument.py',G0/'body-instrument/body41.py',G2/'native.py']}))
    print(json.dumps([dict(endpoint=t['endpoint'],family=t['family'],scale=t.get('scale'),maximum=t.get('maximumCodes'),survives=t.get('survives')) for t in tables if t['objective']=='minimax'],indent=2))

if __name__=='__main__':main()
