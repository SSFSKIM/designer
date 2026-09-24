"""Actual tune-path renders on the frozen domain; no fitting to their residuals."""
import base64,gzip,hashlib,io,itertools,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from edge import HERE,G1,W,WebReader,I,geometry,save
wave=W.default_wave();probe=wave.reader(G1/'probe');repeat=wave.reader(G1/'repeat')
plans=json.loads((HERE/'candidate-plans.json').read_text());rows=[];summaries=[];receded=[]
expected={c['cell']+r['label']:c for r in map(json.loads,(HERE/'browser-runs.txt').read_text().splitlines()) for c in r.get('checks',[])}
for plan in plans:
 reader=WebReader.w34(Path(plan['root'])/'web-captures');pr=[]
 for sid in plan['scenes']:
  cell=plan['profile']+'/'+sid;check=expected[cell+plan['label']]
  if not check['used']:continue
  raw=reader.read(cell)
  if hashlib.sha256(raw).hexdigest()!=check['pngSha256']:raise ValueError('candidate bytes moved')
  w=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),float)
  n=np.asarray(Image.open(io.BytesIO(probe.read(cell,'png'))).convert('RGB'),float)
  if sid.endswith('__inactive'):
   shipped=np.asarray(Image.open(io.BytesIO(WebReader.w34().read(cell))).convert('RGB'),float)
   receded.append(dict(candidate=plan['label'],cell=cell,changedPixels=int(np.any(w!=shipped,axis=2).sum()),maxDelta=int(abs(w-shipped).max())))
  crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
  runs=[r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal']
  states={k:I.unpack(base64.b64decode(crop['states'][k])) for k in {r['state'] for r in runs}}
  p=states[runs[0]['state']];d,nx,ny,arc,bins,whole=geometry(p);scale=p['scale']
  deep=d<=-6*scale;nb=np.median(n[deep],0);wb=np.median(w[deep],0)
  for part,m in [('arc',arc),('straight',~arc)]:
   for shell in range(-6*scale,0):
    for angle in range(16):
     mask=m&whole&(d>=shell)&(d<shell+1)&(bins==angle)
     if not mask.any():continue
     pairs=[abs(a['rgb'][mask].astype(float)-b['rgb'][mask]).mean(0) for a,b in itertools.combinations(states.values(),2)]
     bar=np.max(pairs,0) if pairs else np.zeros(3)
     err=(n[mask]-nb)-(w[mask]-wb);mae=abs(err).mean(0)
     value=dict(candidate=plan['label'],cell=cell,role=wave.roles[sid],part=part,shell=shell,bin=angle,
        pixels=int(mask.sum()),admissible=int(mask.sum())>=4,barRGB=bar.tolist(),tauRGB=np.maximum(1,bar).tolist(),
        residualRGB=mae.tolist(),signedRGB=err.mean(0).tolist(),
        nativeExcess=(n[mask]-nb).mean(0).tolist(),webExcess=(w[mask]-wb).mean(0).tolist(),
        nativeDeep=nb.tolist(),webDeep=wb.tolist(),pointCloses=bool(np.all(mae<=np.maximum(1,bar))) and int(mask.sum())>=4)
     rows.append(value);pr.append(value)
  if sid=='grey-128__circular-120__rest' and '-2x-' in plan['profile'] and plan['label'].startswith('signed-shadow'):
   old=Image.open(io.BytesIO(WebReader.w34().read(cell))).convert('RGB')
   images=[Image.fromarray(n.astype('uint8')),old,Image.fromarray(w.astype('uint8'))]
   panel=Image.new('RGB',(images[0].width,3*(images[0].height+24)),(255,255,255));draw=ImageDraw.Draw(panel)
   for i,(label,image) in enumerate(zip(['Native','Shipped WebGPU','Existing-leaf candidate'],images)):
    y=i*(image.height+24);draw.text((8,y+5),label,fill=(0,0,0));panel.paste(image,(0,y+24))
   panel.save(HERE/('eye-'+plan['profile']+'.png'))
 measured=[r for r in pr if r['admissible']];active=[r for r in measured if r['cell'].endswith('__rest')]
 inactive=[r for r in measured if r['cell'].endswith('__inactive')]
 summaries.append(dict(candidate=plan['label'],profile=plan['profile'],admittedBins=len(measured),
   deficientBins=sum(not r['admissible'] for r in pr),
   worstActive=max(max(r['residualRGB']) for r in active),
   worstGrey96=max(max(r['residualRGB']) for r in active if '/grey-96__' in r['cell']),
   worstInactive=max(max(r['residualRGB']) for r in inactive),
   inactiveWebExcess=max(max(abs(v) for v in r['webExcess']) for r in inactive),
   worstByPart={part:max(max(r['residualRGB']) for r in active if r['part']==part) for part in ['arc','straight']},
   witness=max(active,key=lambda r:max(r['residualRGB'])),
   closes=all(r['pointCloses'] for r in measured)))
save(HERE/'receded-composition.json',receded)
save(HERE/'candidate-residuals.json.gz',rows);save(HERE/'candidate-verdicts.json',summaries)
print(json.dumps([{k:v for k,v in r.items() if k!='witness'} for r in summaries],indent=2))
