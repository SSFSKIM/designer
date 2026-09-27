"""Re-evaluate the same attested geometry at16x16; no coefficients are fitted."""
import dataclasses
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import native
import basis
cache=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
manifest=json.loads((cache/'manifest.json').read_text());seal=json.loads((cache/'seal.json').read_text())
for item in seal['files']:
 if hashlib.sha256((cache/item['file']).read_bytes()).hexdigest()!=item['sha256']:raise ValueError('cache identity changed')
rows=[]
for key,g in manifest['geometries'].items():
 s=g['shape'];shape=native.readers.Shape(s['kind'],tuple(s['size']),tuple(s['frame_origin']),tuple(s['elements']),s['opaque'])
 xy=np.load(cache/(key+'.npz'))['xy']
 t,ny=basis.samples(shape,xy,g['scale'],16,native.readers)
 path=out/(key+'.npz');np.savez_compressed(path,t=t,ny=ny)
 rows.append(dict(geometry=key,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 print(key,len(xy),'samples16',flush=True)
with (out/'manifest.json').open('x') as f:json.dump(dict(sourceSealSha256=hashlib.sha256((cache/'seal.json').read_bytes()).hexdigest(),quadrature=16,geometries=rows),f,indent=2)
