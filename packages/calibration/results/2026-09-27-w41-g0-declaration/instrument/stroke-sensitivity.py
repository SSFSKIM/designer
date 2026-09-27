"""Synthetic fixed-coefficient 16/32 quadrature sensitivity, no native observation."""
import json
import numpy as np
import instrument as m
import stroke_fit as f
q=np.array(json.loads((m.HERE/'stroke-synthetic-results.json').read_text())['leastSquares']['coefficients'])
shape=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.));rows=[]
for scale in (1,2):
    geo=m.readers.geometry((90*scale,170*scale),[shape],scale)
    yy,xx=np.nonzero(geo.outside&(geo.d<4*scale));xy=np.c_[xx,yy]
    maxima=np.zeros(4)
    for start in range(0,len(xy),128):
        g16=m.samples(shape,xy[start:start+128],scale,16)
        g32=m.samples(shape,xy[start:start+128],scale,32)
        for endpoint in range(4):
            predictions=[]
            for g in (g16,g32):
                b=np.full((*g['d'].shape,3),128.,float)
                predictions.append(f.predict(q,dict(endpoint=endpoint,g=g,backdrop=b,shadow=b),'M0'))
            maxima[endpoint]=max(maxima[endpoint],float(abs(predictions[0]-predictions[1]).max()))
    rows.append(dict(scale=scale,pixels=len(xy),maximumCodesByEndpoint=dict(zip(f.ENDPOINTS,maxima.tolist()))))
print(json.dumps(dict(heldCoefficients=q.tolist(),nativeFits=0,rows=rows,maximumCodes=max(max(r['maximumCodesByEndpoint'].values()) for r in rows)),indent=2))
