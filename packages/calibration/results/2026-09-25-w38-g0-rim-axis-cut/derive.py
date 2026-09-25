"""Lossless reductions of the failed candidates and frozen pre-W38 baselines."""
import gzip,json,hashlib
from model import HERE,ROOT,edge,np,inputs,params,SCALE
from score import guard
if __name__=='__main__':
    guard();bins=json.loads(gzip.decompress((HERE/'candidate-bins.json.gz').read_bytes()));lookup={(b['cell'],b['part'],b['shell'],b['bin']):b for b in bins if b['candidate']=='C1'}
    arcs=[]
    for r in inputs(structured=False,web=False):
        old=params(r['scheme']);lit=np.maximum(abs(r['nx']*old['axis'][0]+r['ny']*old['axis'][1])*2**.5,1e-6)**.85
        new=np.maximum(abs(r['ny'])*2**.5,1e-6)**.85
        for b in r['bins']:
            if b['part']!='arc':continue
            ix=b['indices'];ref=lookup[(r['cell'],b['part'],b['shell'],b['bin'])]
            arcs.append(dict(**ref,oldAngularMean=float(lit[ix].mean()),C1RawAngularMean=float(new[ix].mean()),C1OrdinaryEffectiveAngularMean=float((SCALE*new[ix]).mean()),collapsedRatioMean=float((new[ix]/lit[ix]).mean())))
    edge.save(HERE/'c1-angular-bins.json.gz',arcs)
    transfer=json.loads(gzip.decompress((HERE/'transfer.json.gz').read_bytes()));ts=[]
    for candidate in ['C1','C2']:
        for scheme in ['light','dark']:
            for domain in ['all-calibration','solid-calibration']:
                rr=[r for r in transfer if r['candidate']==candidate and '-'+scheme+'-' in r['cell']]
                if domain=='solid-calibration':
                    solid={b['cell'] for b in bins if b['stratum']!='structured-diagnostic'};rr=[r for r in rr if r['cell'] in solid]
                ts.append(dict(candidate=candidate,scheme=scheme,domain=domain,cells=len(rr),pixelRange=[min(r['pixelRange'][0] for r in rr),max(r['pixelRange'][1] for r in rr)],binMeanRange=[min(min(b['edgeTransferRGB']) for r in rr for b in r['bins'] if b['admissible']),max(max(b['edgeTransferRGB']) for r in rr for b in r['bins'] if b['admissible'])]))
    edge.save(HERE/'transfer-summary.json',ts)
    verdict=[]
    for candidate in ['C1','C2']:
        bb=[b for b in bins if b['candidate']==candidate and b['admissible']];delta=np.array([b['worseningRGB'] for b in bb]);worst=max(bb,key=lambda b:max(b['worseningRGB']))
        verdict.append(dict(candidate=candidate,admittedBins=len(bb),vetoBins=sum(b['veto'] for b in bb),vetoChannels=int((delta>1+1e-10).sum()),better=int((delta<-.5).sum()),same=int((abs(delta)<=.5).sum()),worse=int((delta>.5).sum()),worst=worst))
    edge.save(HERE/'verdict.json',dict(recommendation='close W38 at the finding',rows=verdict,C2='No selected point: tabled C2 points are failed constraint-minimizing witnesses, not nominations.'))
    css=[]
    for scheme in ['light','dark']:
        old=params(scheme);A=old['a']+old['g']*.2
        for t in [0,.5,1]:
            for tint in [0,1]:
                collapsed=.038*(1-tint)+.52*tint
                prior=.64*(A*(1-t)+collapsed*t);new=.64*(SCALE*A*(1-t)+collapsed*t)*2**(.85/2)
                css.append(dict(scheme=scheme,referenceLinearLevel=.2,T=t,tintK=tint,oldBorderAlpha=prior,C1BorderAlpha=new,delta=new-prior))
    diag=json.loads((HERE.parent/'2026-09-25-w37-g0-edge-identification/diagnostics.json').read_text())
    width=json.loads((HERE.parent/'2026-09-25-w37-g0-edge-identification/static-audit.json').read_text())['widths']
    edge.save(HERE/'css-and-stop-notes.json',dict(css=css,clear='exponent0 and unchanged shared constants; lobe factor1',strongBorder='exponent0; existing direct boundary alpha mapping unchanged',M2Correction='The declaration mislabels erosion deltas as light/dark. Both are DARK photo capsule: 1x -60.02832691048684%, 2x -48.43312779842039%. This correction changes no value, bound or candidate selection.',M2=diag['m2ErosionRecomputed'],historicalFwhm=width,FwhmStatus='Historical native rimIntensity rows, not a physical width; no post-fit render or inferred FWHM.'))
    print(json.dumps(dict(verdict=[{k:v for k,v in x.items() if k!='worst'} for x in verdict],transfer=ts),indent=2))
