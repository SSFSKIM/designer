#!/usr/bin/env python3.12
"""Append non-holdout review corrections; never nominate or expose again (§5.176)."""
import argparse
import copy
import gzip
import json
from pathlib import Path
import numpy as np
from PIL import Image
import identification as M
import forward as F
import fast
import verdicts as V

E=M.HERE
OUT=E/'review-fix'


def coordinates(records):
    # Re-evaluate published stroke coefficients. No frozen nominee, coefficient
    # file, original reading or held result is replaced by these corrected cuts.
    originals=json.loads((E/'fits.json').read_text())
    compact=[(i,f) for i,f in enumerate(originals) if f['spec']['name'].startswith('body-forward')]
    M.save(OUT/'coordinate-compact-index.json',[dict(fit=i,originalFit=j) for i,(j,f) in enumerate(compact)])
    M.evaluate(records,[f for j,f in compact],'coordinate-compact')
    eligible=[r for r in records if r['cov'] is not None and r['backgroundKind'] in ['solid','linear-gradient']]
    offsets=[]
    for r in eligible:
        r['exactBaselines']={s:F.baseline(r,s,r['alignment']['translationDevicePx'],cov=r['cov'])[0]
                             for s in ['encoded','linear']}
        if 'coefficients' in r['body']:
            beta=np.array(r['body']['coefficients'])
            shift=beta[1]/(2*320*r['scale'])+beta[2]/(2*200*r['scale'])
            offsets.append(dict(cell=r['cell'],oldMinusCorrectedEncodedRGB=shift.tolist()))
    M.save(OUT/'coordinate-offsets.json',offsets)
    qualified=json.loads((E/'qualified-fits.json').read_text())
    M.evaluate(eligible,qualified[400:],'coordinate-exact')
    M.evaluate(eligible,json.loads((E/'alpha-fits.json').read_text()),'coordinate-alpha')
    F.verify(eligible,qualified,'coordinate-qualified')
    V.main(prefix='coordinate-qualified',fits_path=E/'qualified-fits.json',
           output='coordinate-closure-verdicts.json')


def bases(records):
    original=M.family_specs
    selected={'gradient','colour-gradient','rotated-axis','isotropic-two-axis'}
    M.family_specs=lambda:[dict(s,w33Reference=True) for s in original() if s['name'] in selected]
    for comparator in ['no-glass','web']:
        rs=[r.copy() for r in records]
        if comparator=='web':
            for r in rs:
                profile,sid=r['cell'].split('/',1)
                web=np.asarray(Image.open(E/'web-captures'/profile/sid/(sid+'__webgpu.png')).convert('RGB'),float)
                r['D']=web[r['xy'][:,1],r['xy'][:,0]]
        fits=M.fit_all(rs)
        M.save(OUT/f'w33-reference-{comparator}-fits.json',fits)
        M.evaluate(rs,fits,f'w33-reference-{comparator}')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['coordinates','bases'])
    action=ap.parse_args().action
    fast.activate()
    wave=M.W.default_wave()
    records,_=M.extract(wave,roles=('calibration','validation'))
    assert len(records)==336 and all(r['role']!='holdout' for r in records)
    M.HERE=OUT
    if action=='coordinates':coordinates(records)
    else:bases(records)


if __name__=='__main__':main()
