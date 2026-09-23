#!/usr/bin/env python3.12
"""W33's native-minus-web comparator beside the primary no-glass fit (§5.176).

The first family pass used zero contour against the captured backdrop. This
separate reading uses the actual shipped web pixels, matching W33's comparator;
its calibration/validation split remains W34's, not W33's in-sample population.
"""
import numpy as np
from PIL import Image
import identification as M

records,_=M.extract(M.W.default_wave())
for r in records:
    profile,sid=r['cell'].split('/',1)
    path=M.HERE/'web-captures'/profile/sid/(sid+'__webgpu.png')
    web=np.asarray(Image.open(path).convert('RGB'),float)
    r['D']=web[r['xy'][:,1],r['xy'][:,0]]
original=M.family_specs
M.family_specs=lambda:[s for s in original() if s['stage']=='W33-first']
fits=M.fit_all(records)
M.save(M.HERE/'w33-web-fits.json',fits)
M.evaluate(records,fits,'w33-web-validation')
