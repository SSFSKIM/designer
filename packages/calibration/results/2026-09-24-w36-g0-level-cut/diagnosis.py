"""Joint diagnosis, never a nominated Part B operator (§5.178 clauses 1–3)."""
import json
import numpy as np
from cut import HERE,lin,enc,lab,W,save,LEVELS
solid=json.loads((HERE/'solid-cut.json').read_text());chroma=json.loads((HERE/'chroma-cut.json').read_text())
deep=json.loads((HERE/'deep-cut.json').read_text());out=[];summary=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
    rows=[r for r in solid if f'-1x-{scheme}-' in r['cell'].split('/')[0] and r['cell'].endswith('__'+pose)]
    grey={int(r['cell'].split('/grey-')[1].split('__')[0]):r for r in rows if '/grey-' in r['cell']}
    gx=np.array(LEVELS)/255;gy=[float(lin(grey[v]['nativeMedian'])@W) for v in LEVELS]
    for r in rows:
        if r['censoredChannels']:continue
        yn=float(lin(r['nativeMedian'])@W);a=r['abscissa'];old=a['encodedChannelsMean'];new=a['encodeLumaMean']
        out.append(dict(cell=r['cell'],scheme=scheme,pose=pose,
            domain='same W28 circular silhouette, no source-domain substitution',
            encodedChannelSum=old,encodedLuma=new,shortfall=new-old,nativeLuma=yn,
            nativeEquivalentGreyX=float(np.interp(yn,gy,gx)),
            oldFormulaGreyCurveLuma=float(np.interp(old,gx,gy)),
            newFormulaGreyCurveLuma=float(np.interp(new,gx,gy)),
            oldFormulaError=float(np.interp(old,gx,gy)-yn),newFormulaError=float(np.interp(new,gx,gy)-yn)))
    rr=[r for r in chroma if r['scheme']==scheme and r['pose']==pose and r['scale']==1 and r['nativeRetention'] is not None]
    summary.append(dict(scheme=scheme,pose=pose,uncensoredColours=len(rr),
        impliedRetentionRange=[min(r['nativeRetention'] for r in rr),max(r['nativeRetention'] for r in rr)],
        requiredOperatorRange=[min(r['operatorRetentionRequired'] for r in rr),max(r['operatorRetentionRequired'] for r in rr)],
        secantM1Range=[min(r['oldToneM1Extrapolated'] for r in rr),max(r['oldToneM1Extrapolated'] for r in rr)],
        maxNativeHueRotationDegrees=max(abs(r['nativeHueDeltaDegrees']) for r in rr),
        maxWebHueRotationDegrees=max(abs(r['webHueDeltaDegrees']) for r in rr)))
structure=[]
for r in deep:
    if 'photo__capsule-button' not in r['cell'] and 'checkerboard__capsule-button' not in r['cell']:continue
    nl,wl=lab(r['nativeMedian']),lab(r['webMedian'])
    structure.append(dict(cell=r['cell'],nativeMedian=r['nativeMedian'],webMedian=r['webMedian'],
        nativeDeepChroma=float(np.linalg.norm(nl[1:])),webDeepChroma=float(np.linalg.norm(wl[1:]))))
save('abscissa-comparison.json',out)
save('joint-diagnosis.json',dict(summary=summary,structure=structure,
    partB='UNIDENTIFIED. No operator nominated. Retention alone misses M1 under the old-tone secant, some solids require r>1, and it cannot raise dark luma. A plate-mean term is not inferred from that failure.',
    abscissaDecisionDraft='Keep the silhouette domain. Sum linear RGB to Y before encoding each pixel, then average over that SAME domain, is closer on uncensored receded colours and identical on greys. It does not explain the dark chromatic level excess; G1 still needs structured regression checks.'))
print(json.dumps(summary,indent=2))
for scheme in ['light','dark']:
 rr=[r for r in out if r['scheme']==scheme and r['pose']=='inactive' and '/grey-' not in r['cell']]
 print(scheme,'inactive formula errors old/new',[(r['cell'].split('/')[1].split('__')[0],round(r['shortfall'],4),round(r['oldFormulaError'],4),round(r['newFormulaError'],4)) for r in rr])
