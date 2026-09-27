"""Fixed-coefficient8x8 versus16x16 prediction sensitivity; never a refit or selector."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import basis
HERE=Path(__file__).resolve().parent;cache=Path(sys.argv[1]);fine=Path(sys.argv[2])
manifest=json.loads((cache/'manifest.json').read_text());seal=json.loads((cache/'seal.json').read_text())
for row in seal['files']:
 if hashlib.sha256((cache/row['file']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('cache seal mismatch')
fm=json.loads((fine/'manifest.json').read_text())
assert fm['sourceSealSha256']==hashlib.sha256((cache/'seal.json').read_bytes()).hexdigest()
for row in fm['geometries']:
 if hashlib.sha256((fine/(row['geometry']+'.npz')).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('16x16 geometry hash mismatch')
geo={k:dict(np.load(cache/(k+'.npz'))) for k in manifest['geometries']}
g16={k:dict(np.load(fine/(k+'.npz'))) for k in geo};W=np.array([.2126,.7152,.0722])
rows=[];summaries=[]
for ep in ['light-active','light-inactive','dark-active','dark-inactive']:
 summarypath=HERE/(ep+'-gn')/'summary.json';summary=json.loads(summarypath.read_text())
 scheme,pose=ep.split('-');pose='rest' if pose=='active' else 'inactive'
 records=[r for r in manifest['records'] if r['scheme']==scheme and r['pose']==pose]
 for method,key in [('leastSquares','bestLeastSquares'),('minimax','bestMinimax')]:
  best=summary[key];q=np.array(best[method]['coefficients']).reshape(11,4)
  shape=(best['widthCSS'],best['exponent'])
  r8={k:basis.radial(g['t'],g['ny'],*shape) for k,g in geo.items()}
  r16={k:basis.radial(g['t'],g['ny'],*shape) for k,g in g16.items()}
  worstPixel=0.;worstMean=0.;worstErrorChange=0.
  for r in records:
   data=dict(np.load(cache/(r['id']+'.npz')));g=geo[r['geometry']];b=data['deep']/255;y=b@W;z=b-y
   colour=np.column_stack((np.ones(3),np.full(3,y),z,y*z));base=np.where(g['inside'][:,None],b,data['backdrop']/255)
   p8=np.clip(base+(r8[r['geometry']]@q)@colour.T,0,1)*255
   p16=np.clip(base+(r16[r['geometry']]@q)@colour.T,0,1)*255
   delta=p16-p8;counts=np.bincount(g['binids'],minlength=len(manifest['geometries'][r['geometry']]['bins']))
   reduce=lambda values:np.stack([np.bincount(g['binids'],weights=values[:,c],minlength=len(counts)) for c in range(3)],axis=1)/np.maximum(counts[:,None],1)
   mean=reduce(delta);e8=reduce(abs(p8-data['native']));e16=reduce(abs(p16-data['native']))
   worstPixel=max(worstPixel,float(abs(delta).max()));worstMean=max(worstMean,float(abs(mean).max()));worstErrorChange=max(worstErrorChange,float(abs(e16-e8).max()))
   for i,bn in enumerate(manifest['geometries'][r['geometry']]['bins']):
    rows.append({**bn,'member':r['member'],'cell':r['cell'],'role':r['role'],'endpoint':ep,'scale':r['scale'],'method':method,
       'predictionMeanChangeRGB':mean[i].tolist() if counts[i] else None,
       'absoluteResidual8RGB':e8[i].tolist() if counts[i] else None,
       'absoluteResidual16RGB':e16[i].tolist() if counts[i] else None,
       'qualification':'quadrature sensitivity only; censor-aware survival lives in edge-correction, not these diagnostics'})
  summaries.append(dict(endpoint=ep,method=method,shape=best['widthCSS'],exponent=best['exponent'],
      frozenFitSha256=hashlib.sha256(summarypath.read_bytes()).hexdigest(),maximumPixelChangeCodes=worstPixel,
      maximumBinMeanChangeCodes=worstMean,maximumBinMAEChangeCodes=worstErrorChange,refitted=False))
print(json.dumps(dict(sourceCacheSealSha256=fm['sourceSealSha256'],fineGeometryManifestSha256=hashlib.sha256((fine/'manifest.json').read_bytes()).hexdigest(),
 summaries=summaries,rows=rows),allow_nan=False))
