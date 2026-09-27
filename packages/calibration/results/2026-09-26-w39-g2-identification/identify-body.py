"""Step3: frozen-neutral body families on calibration; validation is transfer only.

Censored deep cells never enter RGB inversion. Their admitted channels retain
forward residuals; rails are one-sided bounds. Every repeat is scored against
the same frozen prediction. Span64/96 rows are separate thick transfer, never fit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import native

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'instrument'))
import body
import fitting
p=argparse.ArgumentParser();p.add_argument('archive');args=p.parse_args()
materials=json.loads((HERE/'instrument/resolved-materials.json').read_text())
neutral=json.loads((HERE/'neutral/curves.json').read_text())
neutral_sha=hashlib.sha256((HERE/'neutral/curves.json').read_bytes()).hexdigest()
curves={(r['scheme'],r['pose']):np.array([k['leastSquaresCode'] for k in r['knots']])/255 for r in neutral['curves']}
# Load numerical optimizer code before the raw-root audit hook is armed.
fitting.fit(lambda q:np.array([[q[0]]]),np.array([[1.]]),[0.])
w,reader=native.guarded(args.archive,('calibration','validation'))
selected=[]
for c,k in reader.entries:
 if k!='crop':continue
 sid=c.split('/',1)[1]
 if sid not in reader.allowed:continue
 comp=w.component(sid);scene=w.scenes[sid];bg=w.spec['backgrounds'][scene['background']]
 if comp['kind']=='none' or comp.get('opaque') or bg['kind']!='solid':continue
 colour='-colour__' in sid
 thick=min(comp.get('size',[0,0])) in (64,96)
 if colour or thick:selected.append((c,'colour' if colour else 'thick-transfer'))
rows=[]
for c,population in sorted(selected):
 r=native.cell(reader,c);sid=c.split('/',1)[1]
 r.update(population=population,inputCodes=w.spec['backgrounds'][w.scenes[sid]['background']]['srgb'],span=min(w.component(sid)['size']))
 rows.append(r)
fits=[];scores=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  ep=scheme+'-'+('active' if pose=='rest' else 'inactive');m=materials[ep];f=curves[(scheme,pose)]
  population=[r for r in rows if r['scheme']==scheme and r['pose']==pose]
  calibration=[r for r in population if r['role']=='calibration' and r['population']=='colour' and not r['members'][0]['censoredChannels']]
  x=np.array([r['inputCodes'] for r in calibration])/255;y=np.array([r['members'][0]['medianRGB'] for r in calibration])/255
  for family in ['H1','H2','H2prime','H3','H3prime']:
   if family=='H2prime':
    fn=lambda q:body.h2(x,m,q=q)
    fitted=fitting.fit(fn,y,np.r_[m['bodyChromaRetention'],m['backdropToneResponseThin']],[(0,1)]*5,monotone_start=1)
   elif family=='H3':fitted=fitting.fit(lambda q:body.h3(x,f,q),y,[1,0,0,1,0,0])
   elif family=='H3prime':fitted=fitting.fit(lambda q:body.h3prime(x,f,q),y,[1,0,0,1])
   else:fitted={name:dict(coefficients=[],converged=True,parameters=0,rank=0,singularValues=[]) for name in ['leastSquares','minimax']}
   fits.append(dict(endpoint=ep,family=family,fitCells=[r['cell'] for r in calibration],
       neutralOrdinatesCodes=(f*255).tolist(),neutralFitCells=[r['cell'] for r in neutral['rows'] if r['scheme']==scheme and r['pose']==pose],
       **fitted))
   print(ep,family,[(k,v.get('maximum'),v['converged']) for k,v in fitted.items()],file=sys.stderr,flush=True)
   for method,fit in fitted.items():
    q=np.array(fit['coefficients'])
    for r in population:
     xx=np.array([r['inputCodes']])/255;span=r['span']
     if family=='H1':pred=body.h1(xx,f)[0]*255
     elif family=='H2':pred=body.h2(xx,m,span)[0]*255
     elif family=='H2prime':pred=body.h2(xx,m,span,q)[0]*255
     elif family=='H3':pred=body.h3(xx,f,q)[0]*255
     else:pred=body.h3prime(xx,f,q)[0]*255
     deep=r['members'][0];obs=np.array(deep['medianRGB']);tau=np.maximum(1,deep['barRGB'])
     def residual(values):
      values=np.asarray(values);absolute=abs(pred-values)
      return np.where(values>=250,np.maximum(250-pred,0),np.where(values<=5,np.maximum(pred-5,0),absolute))
     err=residual(obs);runs=np.array(deep['runMediansRGB']);perrun=residual(runs)
     scores.append(dict(cell=r['cell'],endpoint=ep,scale=r['scale'],role=r['role'],population=r['population'],
      family=family,method=method,converged=fit['converged'],predictedRGB=pred.tolist(),nativeRGB=obs.tolist(),
      residualRGB=err.tolist(),absoluteDiagnosticRGB=abs(pred-obs).tolist(),toleranceRGB=tau.tolist(),
      censoredChannels=deep['censoredChannels'],censorRule='one-sided threshold bound; entire cell excluded from RGB inversion',
      failedChannels=np.flatnonzero(err>tau+1e-8).tolist(),repeatResidualRGB=perrun.tolist(),
      repeatFailedChannels=[np.flatnonzero(e>tau+1e-8).tolist() for e in perrun]))
summary=[]
for family in ['H1','H2','H2prime','H3','H3prime']:
 for ep in ['light-active','light-inactive','dark-active','dark-inactive']:
  for scale in [1,2]:
   for method in ['leastSquares','minimax']:
    rr=[r for r in scores if r['family']==family and r['endpoint']==ep and r['scale']==scale and r['method']==method and r['population']=='colour']
    worst=max(rr,key=lambda r:max(r['residualRGB']))
    failed=[r for r in rr if r['failedChannels'] or any(r['repeatFailedChannels'])]
    summary.append(dict(family=family,endpoint=ep,scale=scale,method=method,cells=len(rr),failedCells=len(failed),
      failedChannels=sum(len(r['failedChannels']) for r in rr),allChannelFailedCells=sum(len(r['failedChannels'])==3 for r in rr),
      status='survived' if not failed and all(r['converged'] for r in rr) else 'failed',
      worstCell=worst['cell'],worstRole=worst['role'],worstChannel=int(np.argmax(worst['residualRGB'])),maximumCodes=max(worst['residualRGB'])))
print(json.dumps(dict(inventorySha256=reader.generation,neutralSha256=neutral_sha,rawRootDenied=str(Path.home()/'vitrea-w39'),
 rows=rows,fits=fits,scores=scores,survival=summary),allow_nan=False))
