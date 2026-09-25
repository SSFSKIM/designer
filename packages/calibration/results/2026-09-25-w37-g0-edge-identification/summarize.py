"""Reduce recorded channel/bin tables without changing any score (§5.181)."""
import gzip,json
import numpy as np
from law import HERE,edge
rows=json.loads(gzip.decompress((HERE/'residuals.json.gz').read_bytes()))
transfer=json.loads(gzip.decompress((HERE/'transfer.json.gz').read_bytes()))
result=[]
for space in ['linear','encoded']:
 for scheme in ['light','dark']:
  for role in ['calibration','validation']:
   for population in ['circular','diagnostic-straight']:
    rr=[r for r in rows if r['space']==space and r['scheme']==scheme and r['role']==role and r['active'] and r['admissible'] and r['closure']==(population=='circular')]
    for cell in sorted(set(r['cell'] for r in rr)):
     bins=[r for r in rr if r['cell']==cell];worst=max(bins,key=lambda r:max(r['residualRGB']))
     result.append(dict(space=space,scheme=scheme,role=role,population=population,cell=cell,bins=len(bins),failedBins=sum(r['fails'] for r in bins),maximum=max(worst['residualRGB']),worst=dict(part=worst['part'],shell=worst['shell'],bin=worst['bin'],residualRGB=worst['residualRGB'])))
edge.save(HERE/'failure-cells.json',result)
tr=[]
for space in ['linear','encoded']:
 for scheme in ['light','dark']:
  tt=[r for r in transfer if r['space']==space and r['scheme']==scheme and r['cell'].endswith('__rest')]
  low=min(tt,key=lambda r:r['edgeTransferPixelRange'][0]);high=max(tt,key=lambda r:r['edgeTransferPixelRange'][1])
  values=[v for r in tt for b in r['bins'] if b['admissible'] for v in b['edgeTransferRGB']]
  tr.append(dict(space=space,scheme=scheme,pixelRange=[low['edgeTransferPixelRange'][0],high['edgeTransferPixelRange'][1]],lowCell=low['cell'],highCell=high['cell'],admittedBinMeanRange=[min(values),max(values)]))
edge.save(HERE/'transfer-summary.json',tr)
print(json.dumps(tr,indent=2))
