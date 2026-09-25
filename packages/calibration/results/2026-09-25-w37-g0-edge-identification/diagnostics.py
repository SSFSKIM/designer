"""Reproduce channel invariants, bars, old fits and guarded W36 black (§5.181)."""
import sys,json,gzip,io,base64,collections
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent; R=HERE.parents[3];C=R/'packages/calibration';E=C/'results/2026-09-24-w35-g0-edge-cut';A=C/'results/2026-09-23-w34-g1-contour-sitting';G=C/'results/2026-09-24-w36-g1-black-branch';O=HERE
sys.path.insert(0,str(E));import edge
wave=edge.W.default_wave();repeat=wave.reader(A/'repeat')
N=json.loads(gzip.decompress((O/'native-replay.json.gz').read_bytes()));trans=[]
for r in N['rows']:
 if '__circular-120__rest' not in r['cell']:continue
 top={q['shell']:np.array(q['rgb']) for q in r['rows'] if q['side']=='top'};s=r['scale']
 ramp=top[-s-1];slope=ramp-top[-s-2]
 for sh in range(-s,0):
  pre=ramp+(sh+s+1)*slope;out=top[sh];b=np.array(r['deep'])
  def invariants(x,y):
   with np.errstate(divide='ignore',invalid='ignore'):
    return {key:[float(v) if np.isfinite(v) and x[i]<254.5/255 and y[i]<254.5/255 else None for i,v in enumerate(value)] for key,value in {'added':y-x,'multiply':y/x,'screen':(y-x)/(1-x)}.items()}
  trans.append({'cell':r['cell'],'shell':sh,'deep':b.tolist(),'rampExtrapolated':pre.tolist(),'line':out.tolist(),'aboveExtrapolated':(out-pre).tolist(),'censoredChannels':((b>=254.5)|(out>=254.5)).tolist(),'encoded':invariants(b/255,out/255),'linear':invariants(edge.decode(b/255),edge.decode(out/255)),'rampEncoded':invariants(pre/255,out/255),'rampLinear':invariants(edge.decode(pre/255),edge.decode(out/255))})
residual=json.loads(gzip.decompress((E/'candidate-residuals.json.gz').read_bytes()));assert all(x['role'] in ('calibration','validation') for x in residual)
worst={}
for r in residual:
 if r['admissible'] and r['cell'].endswith('__rest'):worst[r['candidate']]=max(worst.get(r['candidate'],0),max(r['residualRGB']))
bars=json.loads((A/'bar.json').read_text());assert all(wave.roles[r['cell'].split('/')[1]] in ('calibration','validation') for r in bars)
barmax=max(max(x['barRGB']) for r in bars for x in r['bins']);erosion=json.loads((E/'m2-gated-attribution.json').read_text())['cells'];erows=[]
for r in erosion:
 if '-dark-' in r['cell'] and r['cell'].endswith('/photo__capsule-button__rest'):
  vals=[x['web']['stdDev'] for x in r['erosion']];erows.append({'cell':r['cell'],'stdDev':vals,'onePixelDeltaPercent':100*(vals[1]/vals[0]-1)})
black=[]
for plan in json.loads((G/'candidate-plans.json').read_text()):
 reader=edge.WebReader.w34(Path(plan['root'])/'web-captures')
 for sid in plan['scenes']:
  if not sid.startswith('grey-0__'):continue
  cell=plan['profile']+'/'+sid;meta=json.loads(reader.read(cell,'metadata'))
  crop=json.loads(gzip.decompress(repeat.read(cell,'crop')));run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal');p=edge.I.unpack(base64.b64decode(crop['states'][run['state']]))
  d,nx,ny,arc,angle,whole=edge.geometry(p);s=p['scale'];im=np.asarray(Image.open(io.BytesIO(reader.read(cell))).convert('RGB'),float)
  med=np.median(im[d<=-6*s],0);top=[]
  for sh in range(-6*s,0):
   mask=(~arc)&(ny<-.5)&(d>=sh)&(d<sh+1)
   top.append({'shell':sh,'rgb':im[mask].mean(0).tolist()})
  black.append({'cell':cell,'root':plan['root'],'deep':med.tolist(),'top':top,'metadata':meta})
summary={'transformTests':trans,'candidateWorstRecomputed':worst,'barMaximumRecomputed':barmax,'m2ErosionRecomputed':erows,'w36BlackReplay':black}
edge.save(O/'diagnostics.json',summary)
print('worst',worst,'bar',barmax,'M2',erows)
for r in trans:
 if '-2x-dark-' in r['cell'] and any('/'+x+'__' in r['cell'] for x in ['cyan','yellow','green']) and r['shell']==-1:
  print('TRANSFORM',r)
for r in black:print('BLACK',r['cell'],r['deep'],r['top'][-2:],list(r['metadata']),str(r['metadata'])[:350])
