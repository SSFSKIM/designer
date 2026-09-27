"""Compare preserved exploratory predictions only; never fit or open native payloads."""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
families={k:{} for k in ['B0','B1','B2','B3']}
for f in json.loads((HERE/'readings/body/h3.json').read_text()):
    for r in f['rows']: families['B0'][r['cell']]=r
mapping={'encoded-Y3':'B1','encoded-hue6':'B2','OKLab-L-matrix3':'B3'}
for f in json.loads((HERE/'readings/body/exploratory.json').read_text()):
    if f['family'] in mapping:
        for r in f['scores']: families[mapping[f['family']]][r['cell']]=r
pairs=[]
for a,b in itertools.combinations(families,2):
    common=sorted(set(families[a])&set(families[b])); rows=[]
    for cell in common:
        ra,rb=families[a][cell],families[b][cell]
        delta=np.abs(np.asarray(ra['pred'])-rb['pred']); c=int(np.argmax(delta))
        rows.append(dict(cell=cell,channel='RGB'[c],separationCodes=float(delta[c]),
                         predictions=[ra['pred'][c],rb['pred'][c]],
                         bridge=ra['sid'].startswith(('red-','green-'))))
    separators=[r for r in rows if r['separationCodes']>=3]
    ordinary=[r for r in rows if not r['bridge']]
    pairs.append(dict(pair=[a,b],commonCells=len(common),thresholdCodes=3,
                      separatorCells=len(separators),bridgeOnly=bool(separators) and all(r['bridge'] for r in separators),
                      maximum=max(rows,key=lambda r:r['separationCodes']),
                      ordinaryMaximum=max(ordinary,key=lambda r:r['separationCodes']),
                      witnesses=separators,
                      verdict='separates these exploratory instances' if separators else 'insufficient resolution for these instances',
                      limitation='No survival implied; B0 excluded whole censored cells; O12 was an unbounded local LS exploratory candidate, not the declared bounded G1 fit.'))
x=json.loads((HERE/'readings/body/readings.json').read_text())
counts=dict(cells=len(x['rows']),uncensoredChannels=sum(sum(5<v<250 for v in r['median']) for r in x['rows']),railBounds=sum(sum(v<=5 or v>=250 for v in r['median']) for r in x['rows']),w39WholeCellFit=sum(all(5<v<250 for v in r['median']) for r in x['rows']))
report=dict(schema='w41-twin-audit-1',nativePayloadsOpened=0,nativeFits=0,
    sourceSha256={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'readings/body/h3.json',HERE/'readings/body/exploratory.json',HERE/'readings/body/readings.json']},body=pairs,populations=counts,
    spatial=[dict(pair=['S0','S1'],verdict='insufficient resolution for prior inactive instances',maximumSeparationCodes={'light-inactive':1.15,'dark-inactive':2.03},source='charter v2.1 Design spatial discriminators; prior reviewer reading, not recomputed fit',oneCode='separation exceeds one code, but does not reach the three-code identification rule'),dict(pair=['S1','S2'],verdict='admitted active reflected-row observational discriminator, not a fitted S2 success',cellPair=['v90-c-c44__rest','v270-c-c44__rest'],scheme='light',depthCSS=14.5,scales=[1,2],differenceCodes=3,limitation='signed interior term versus long boundary tail unresolved'),dict(pair=['S0','S2'],verdict='same reflected-row observational discriminator; no frozen S2 prediction in copied readings',differenceCodes=3,limitation='No new fit in G0; family survival and exact prediction separation await G1')],
    stroke=[dict(pair=['M0','M1'],verdict='neutral-knot affine LS miss, not certified minimax',lightInactiveTopCodes=4.271,darkInactiveTopCodes=6.397,source='memo B section3'),dict(pair=['M0','M2'],verdict='same neutral-knot witness; M2 contextual correction is zero on neutrals',source='memo B sections3/5'),dict(pair=['M1','M2'],verdict='bridge-only observed contextual discriminator, not a fitted M2 success',cells=['red-colour__inactive','green-colour__inactive'],scheme='dark',inputWeakCode=32,topOutputs=[21,14],differenceCodes=7),dict(pair=['G','G-css'],verdict='scale-dependent support discriminator',scales=[1,2],alignedStraight='shell0 footprint at both scales; inactive shell1 zero',arc='2x oblique shell1 occupied; also some 1x shell1 arcs occupied',source='memo B section1'),dict(pair=['G','G-curvature'],verdict='admitted 2x shape contrast; curvature-only attribution not established',scenePair=['g128-c-c44__rest','g128-c-rrect-120x44__rest'],scheme='light',scale=2,arcBin=0,departuresCodes=[-47.5,-38.75],populations=[14,4],oneXrrect=dict(population=2,status='UNMEASURED'),limitation='path family and angular sample positions change with nominal curvature'),dict(pair=['G-css','G-curvature'],verdict='width-unit discriminator still present; no frozen crossed-family predictions',limitation='do not mistake an observed shape contrast for a universal family separation')],
    spatialLimit='No structured holdout; no spatial leaf. Blend and wide blur remain confounded; boundary-tail alternative remains.',
    unfitFamilies='Stroke families have not been fitted in the grounding readings. Their audit nominates observational discriminators, never manufactures predictions or a survival verdict.')
print(json.dumps(report,indent=2,allow_nan=False))
