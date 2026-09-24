"""Native-only law diagnostics; no web residual enters any coefficient solve (§5.177)."""
import gzip,json,sys
import numpy as np
from edge import HERE,save,decode,encode,forward,recover

GREYS="--greys" in sys.argv
profiles=json.loads(gzip.decompress((HERE/'profiles.json.gz').read_bytes()))
rows=[];fits=[];synthetic={};transfer=[]
for p in profiles:
    if '__circular-120__' not in p['cell'] or p['backgroundKind']!='solid':continue
    beta=np.array(p['deep']['nativeMedian']);web=np.array(p['deep']['webMedian']);scale=p['scale']
    top={r['shell']:r for r in p['sides'] if r['side']=='top'}
    ramp0=top[-scale-1];ramp1=top[-scale-2]
    slope=np.array(ramp0['nativeRGB'])-ramp1['nativeRGB']
    line=[]
    for s in range(-scale,0):
        continuation=np.array(ramp0['nativeRGB'])+slope*(s+scale+1)
        line.append(dict(shell=s,nativeRGB=top[s]['nativeRGB'],excess=(np.array(top[s]['nativeRGB'])-beta).tolist(),
                         rampContinuation=(continuation-beta).tolist(),line=(np.array(top[s]['nativeRGB'])-continuation).tolist(),
                         topMinusBottom=(np.array(top[s]['nativeRGB'])-next(r['nativeRGB'] for r in p['sides'] if r['side']=='bottom' and r['shell']==s)).tolist(),
                         thirdsRGB=top[s]['thirdsRGB']))
    rows.append(dict(cell=p['cell'],role=p['role'],deep=p['deep'],line=line,
                     ramp=[dict(shell=s,excess=(np.array(top[s]['nativeRGB'])-beta).tolist()) for s in range(-6*scale,-scale)]))

# A calibrated runtime branch provides a nominated conditioning input, not a
# claim to observe Apple's internal material alpha or radial pre-rim field.
for scale in [1,2]:
 for scheme in ['light','dark']:
    profile=f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'
    selected=[p for p in profiles if p['cell'].startswith(profile+'/') and p['cell'].endswith('__circular-120__rest') and p['backgroundKind']=='solid']
    samples=[]
    for p in selected:
        B=decode(np.array(p['deep']['nativeMedian'])/255);WB=decode(np.array(p['deep']['webMedian'])/255)
        dy=p['alignment']['translationDevicePx'][1]
        for row in p['sides']:
            if not -6*scale<=row['shell']<0:continue
            # Native masks retain their fixed alignment; runtime evaluates its
            # nominal pixel centres. The offset is explicit, never re-fitted.
            dist=row['shell']+.5+(dy if row['side']=='top' else -dy)
            N=np.array(row['nativeRGB']);Y=decode(N/255)
            pre=forward(B,np.array(dist),scale)
            samples.append(dict(cell=p['cell'],role=p['role'],shell=row['shell'],side=row['side'],d=dist,
                body=B,webBody=WB,native=N,target=Y,level=float(pre['level']),pre=pre['linear'],
                pixels=row['pixels'],censored=N>=254.5))
    def design(width,shadow):
        X=[];Y=[]
        for s in samples:
            if s['role']!='calibration' or (GREYS and '/grey-' not in s['cell']):continue
            f=forward(s['body'],np.array(s['d']),scale,width=width,shadow_alpha=shadow)
            for c in range(3):
                if s['censored'][c]:continue
                X.append([float(f['rw']),float(f['rw']*f['level'])]);Y.append(s['target'][c]-f['linear'][c])
        return np.asarray(X),np.asarray(Y)
    candidates=[]
    for shadow in [.05,0,-.05,-.1,-.2]:
      for width in np.arange(.8,6.51,.05):
        X,Y=design(float(width),shadow);coef=np.linalg.lstsq(X,Y,rcond=None)[0]
        errors=[]
        for s in samples:
            if s['role']!='calibration' or (GREYS and '/grey-' not in s['cell']):continue
            f=forward(s['body'],np.array(s['d']),scale,a=coef[0],g=coef[1],width=width,shadow_alpha=shadow)
            errors.append(float(abs(f['encoded']-s['native']).max()))
        candidates.append(dict(width=float(width),shadowAlpha=shadow,a=float(coef[0]),g=float(coef[1]),
                               worstNativeCalibration=max(errors)))
    candidates.sort(key=lambda c:c['worstNativeCalibration'])
    best=candidates[0];ordinary=min((c for c in candidates if c['shadowAlpha']==.05),key=lambda c:c['worstNativeCalibration'])
    for name,c in [('squared-band',ordinary),('signed-shadow',best)]:
        residual=[]
        for s in samples:
            opts=dict(a=c['a'],g=c['g'],width=c['width'],shadow_alpha=c['shadowAlpha'])
            nf=forward(s['body'],np.array(s['d']),scale,**opts)
            wf=forward(s['webBody'],np.array(s['d']),scale,**opts)
            residual.append(dict(cell=s['cell'],role=s['role'],side=s['side'],shell=s['shell'],pixels=s['pixels'],
                residualRGB=abs(nf['encoded']-s['native']).tolist(),censored=s['censored'].tolist(),
                nativeConditioning=float(nf['level']),webConditioning=float(wf['level']),
                toneErrorAmplitude=c['g']*float(wf['level']-nf['level']),
                predictedTransferExcess=(wf['encoded']-255*encode(s['webBody'])).tolist(),
                nativeExcess=(s['native']-255*encode(s['body'])).tolist()))
        fits.append(dict(profile=profile,name=name,fit=c,rows=residual,
            worstValidation=max(max(r['residualRGB']) for r in residual if r['role']=='validation'),
            interpretation='effective nominated forward response; no coefficient transfer authorised'))
    # Test the same forward model against the shipped web on uniform straight
    # shells. These are diagnostic checks, not a web-side amplitude fit.
    a,g,width=(.115,-.122,6.5 if scale==1 else 5.85) if scheme=='light' else (.055,.44,2.2 if scale==1 else 1.35)
    control=[]
    for p in selected:
        wb=decode(np.array(p['deep']['webMedian'])/255)
        for s in p['sides']:
            if not -6*scale<=s['shell']<0:continue
            pred=forward(wb,np.array(s['shell']+.5),scale,a=a,g=g,width=width)
            control.append(dict(cell=p['cell'],side=s['side'],shell=s['shell'],
                                residualRGB=abs(pred['encoded']-s['webRGB']).tolist()))
    transfer.append(dict(profile=profile,worstShippedForward=max(max(r['residualRGB']) for r in control),rows=control))

# Known gain, changed baseline before all composition, and changed coefficient
# share the exact forward and recovery functions used in the native diagnostic.
b=np.repeat(np.array([.03,.12,.3,.55])[:,None],3,axis=1);d=np.full(4,-.5)
opt=dict(width=2,shadow_alpha=.1,shadow_depth=.35,shadow_reach=9.18125)
for name,B,a,g in [('known',b,.07,.23),('baseline-before',b+.03,.07,.23),('coefficient',b,.1,.23)]:
 f=forward(B,d,1,a=a,g=g,**opt);coef=recover(B,d,1,f['linear'],**opt)
 rounded=np.floor(f['encoded']+.5);qcoef=recover(B,d,1,decode(rounded/255),**opt)
 qpred=forward(B,d,1,a=qcoef[0],g=qcoef[1],**opt)
 synthetic[name]=dict(expected=[a,g],recovered=coef.tolist(),quantisedRecovered=qcoef.tolist(),
                      coefficientError=float(abs(coef-[a,g]).max()),
                      quantisedPredictionErrorCodes=float(abs(qpred['encoded']-rounded).max()),
                      excess=(f['encoded']-255*encode(B)).tolist())
 assert synthetic[name]['coefficientError']<1e-10
 assert synthetic[name]['quantisedPredictionErrorCodes']<=1
synthetic['encoded-constant-control']=dict(label='CONTROL ONLY: defective deep-subtraction instruments also pass',
    maxExcessChange=float(abs(((b+.1)-(b.mean(0)+.1))-(b-b.mean(0))).max()))
synthetic['verdict']='arithmetic recovery passes; this does not establish native latent-state recoverability'
if not GREYS: save(HERE/'line-ramp-level.json',rows)
save(HERE/('native-grey-law-fits.json' if GREYS else 'native-law-fits.json'),fits)
if not GREYS:
 save(HERE/'forward-web-check.json',transfer);save(HERE/'synthetic.json',synthetic)
print('fits',[(f['profile'],f['name'],f['fit'],f['worstValidation']) for f in fits])
print('forward web',[(f['profile'],f['worstShippedForward']) for f in transfer])
