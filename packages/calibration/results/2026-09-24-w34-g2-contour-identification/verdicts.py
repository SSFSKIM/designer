#!/usr/bin/env python3.12
"""Apply G0's declared point/interval/discrimination verdict, without refitting."""
import gzip
import json
from collections import defaultdict
import identification as M


def main():
    rows=json.loads(gzip.decompress((M.HERE/'qualified-validation-forward.json.gz').read_bytes()))
    pairs=json.loads(gzip.decompress((M.HERE/'qualified-validation-discrimination.json.gz').read_bytes()))
    fits=json.loads((M.HERE/'qualified-fits.json').read_text())
    by_fit=defaultdict(list);by_pair=defaultdict(list)
    for r in rows:
        r['stratum']=f"{r['part']}/{r['shell']}/{r['bin']}"
        by_fit[r['fit']].append(r)
    for r in pairs:
        a,b=r['families'];fa,fb=fits[a],fits[b]
        # Two objectives of the same family are not independent mechanisms.
        if (fa['spec']['name'],fa['spec']['space'])==(fb['spec']['name'],fb['spec']['space']):continue
        r['stratum']=f"{r['part']}/{r['shell']}/{r['bin']}"
        by_pair[(a,b)].append(r)
    out=[]
    for index,rs in sorted(by_fit.items()):
        for part in ['arc','straight']:
            selected=[r for r in rs if r['part']==part]
            alternatives=[dict(families=list(key),rows=[r for r in value if r['part']==part])
                          for key,value in by_pair.items() if index in key]
            verdict=M.I.closure_verdict(selected,alternatives,all(r['bodyIdentified'] for r in selected))
            validation=[r for r in selected if r['role']=='validation' and r['admissible']]
            out.append(dict(fit=index,profile=fits[index]['profile'],pose=fits[index]['pose'],part=part,
                verdict=verdict,validationWorstPoint=max(max(r['maeRGB']) for r in validation),
                validationWorstInterval=max(max(r['intervalMAERGB']) for r in validation),
                validationBins=len(validation),validationPixels=sum(r['pixels'] for r in validation),
                competingPairs=len(alternatives),tau=1,
                qualifications='Finite declared perturbations, not a confidence interval or exhaustive raster-origin bound.'))
    M.save(M.HERE/'closure-verdicts.json',out)
    print(json.dumps({outcome:sum(r['verdict']['outcome']==outcome for r in out)
                      for outcome in sorted({r['verdict']['outcome'] for r in out})}))


if __name__=='__main__':main()
