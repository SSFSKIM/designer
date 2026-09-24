"""The memo's centre-column estimand beside the full straight-span reading."""
import io,json,sys
import numpy as np
from PIL import Image
from edge import HERE,save
from w35_readers import CanonicalNativeReader,WebReader
reader=CanonicalNativeReader();web=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
rows=[]
for scale in [1,2]:
 for scheme in ['light','dark']:
  cell=f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5/dark-solid__rrect-md__rest'
  n=np.asarray(Image.open(io.BytesIO(reader.read(cell))).convert('RGB'))
  w=np.asarray(Image.open(io.BytesIO(web.read(cell))).convert('RGB'))
  top=(n.shape[0]-96*scale)//2;x=n.shape[1]//2
  if '--left' in sys.argv:x-=1
  rows.append(dict(cell=cell,xDevice=x,estimator='one centre-column pixel, not the 1.6-radius-excluded side mean',
    samples=[dict(shell=s,nativeRGB=n[top-s-1,x].tolist(),webRGB=w[top-s-1,x].tolist()) for s in [-6,-3,-2,-1]]))
save(HERE/('canonical-centre-left.json' if '--left' in sys.argv else 'canonical-centre.json'),rows);print(json.dumps(rows,indent=2))
