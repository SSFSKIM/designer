#!/usr/bin/env python3.12
"""Read today's rendered gap on exactly G0's native fixed masks (§5.176)."""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image
import identification as M


def run(records, prefix="web"):
    rows=[];notches=[];provenance=[]
    for r in records:
        profile,sid=r['cell'].split('/',1)
        root=M.HERE/'web-captures'/profile/sid
        web=np.asarray(Image.open(root/(sid+'__webgpu.png')).convert('RGB'),float)
        report=json.loads((root/'report__webgpu.json').read_text())
        meta=json.loads((root/'cell__webgpu.json').read_text())
        if meta['renderer']!='webgpu' or meta['gpuAdapter']!='apple/metal-3':raise ValueError('Not real GPU')
        if report['page']['material']['name']!='apple-macos-27.0-glass0.5':raise ValueError('Wrong selected material')
        if report['page']['material']['tuned']:raise ValueError('Tuned material, not shipped')
        xy=r['xy'];sample=web[xy[:,1],xy[:,0]]
        for key,mask in r['masks']:
            rows.append(dict(cell=r['cell'],role=r['role'],part=key[0],shell=key[1],bin=key[2],
                **M.bin_residual(r['n'][mask],sample[mask],np.zeros_like(sample[mask]),r['bar'][key]['barRGB'])))
        for part in ['arc','straight']:
            means=[]
            for shell in [-1,0,1]:
                masks=[m for (p,s,b),m in r['masks'] if p==part and s==shell]
                mask=np.logical_or.reduce(masks)
                means.append(float((sample[mask]@np.array([.2126,.7152,.0722])).mean()))
            notches.append(dict(cell=r['cell'],part=part,notch=means[1]-min(means[0],means[2])))
        provenance.append(dict(cell=r['cell'],material=report['page']['material'],web=meta,
            pngSha256=M.hashlib.sha256((root/(sid+'__webgpu.png')).read_bytes()).hexdigest()))
    M.save(M.HERE/(prefix+'-gap.json.gz'),rows)
    M.save(M.HERE/(prefix+'-notches.json'),notches)
    M.save(M.HERE/(prefix+'-provenance.json'),provenance)


if __name__=='__main__':
    records,_=M.extract(M.W.default_wave())
    run(records)
