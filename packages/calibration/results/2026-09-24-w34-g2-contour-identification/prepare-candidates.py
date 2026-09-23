#!/usr/bin/env python3.12
"""Freeze validation nominees by comparator/domain, never refit (§5.176)."""
import hashlib
import json
import subprocess
from collections import defaultdict
import identification as M


def main():
    sources=[('zero-all-shapes','no-glass','fits.json','validation-headlines.json',0,'W33-first'),
             ('zero-circular-response','no-glass','fits.json','validation-headlines.json',0,'new-axes'),
             ('W33-web-all-shapes','web','w33-web-fits.json','w33-web-validation-headlines.json',0,None),
             ('exact-body-circular','no-glass','qualified-fits.json','exact-validation-headlines.json',400,None),
             ('physical-shared-alpha','no-glass','alpha-fits.json','alpha-validation-headlines.json',0,None)]
    candidates=[];inputs=set()
    for selection,comparator,fitfile,headfile,offset,stage in sources:
        fits=json.loads((M.HERE/fitfile).read_text());heads=json.loads((M.HERE/headfile).read_text())
        inputs.update([fitfile,headfile])
        for profile,pose in sorted({(r['profile'],r['pose']) for r in heads}):
            scores=defaultdict(lambda:[0.,0.])
            for row in heads:
                i=row['fit']+offset
                if (row['profile'],row['pose'])!=(profile,pose) or row['role']!='validation':continue
                if stage is not None and fits[i]['spec']['stage']!=stage:continue
                scores[i][0]=max(scores[i][0],row['worstMAE'])
                scores[i][1]=max(scores[i][1],row['shellZeroWorstMAE'])
            best=min(scores,key=lambda i:(scores[i],i))
            fit={k:v for k,v in fits[best].items() if k!='grid'}
            candidates.append(dict(selection=selection,comparator=comparator,source=fitfile,sourceFit=best,
                validationWorstBin=scores[best][0],validationShellZeroWorstBin=scores[best][1],fit=fit))
    dependencies={name:hashlib.sha256((M.HERE/name).read_bytes()).hexdigest() for name in sorted(inputs|{
        'identification.py','forward.py','fast.py','browser.py','web-gap.py','alpha.py','w33-web.py'})}
    document=dict(schema=1,claims='§5.176, W34 clause 6 and X8',candidates=candidates,
        selection='Within each comparator/domain and endpoint: minimize worst absolute validation bin across both parts/all shells; tie-break shell zero, then stable fit index. No coefficients refitted.',
        outcomeBeforeHoldout='No nominated fit closes; the one read is retained for completeness under closure.json fitProtocol.',
        calibrationValidationCommit=subprocess.check_output(['git','-C',str(M.W.ROOT),'rev-parse','HEAD'],text=True).strip(),
        dependencies=dependencies,
        inventories={str(p.relative_to(M.W.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [M.G1/'repeat/inventory.json',M.G1/'probe/inventory.json',M.G1/'inventory.json']})
    M.save(M.HERE/'candidates.json',document)
    print('frozen nominees',len(candidates))


if __name__=='__main__':main()
