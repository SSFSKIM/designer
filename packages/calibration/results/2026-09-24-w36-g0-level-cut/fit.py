"""The predeclared three-shift family, not free thick ordinates (§5.178 clause 2).

Only native calibration greys and admitted canonical neutral anchors enter LS.
The old impulse knot, abscissae and thin-minus-thick differences are frozen.
Validation and structure never contribute an objective term.
"""
import copy,json
import numpy as np
from scipy.optimize import least_squares
from cut import HERE,material,response,lin,enc,W,save
solid=json.loads((HERE/'solid-cut.json').read_text())
canonical=json.loads((HERE/'canonical-solids.json').read_text())
fits=[]
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
    m=material(scheme,pose);targets=[];validation=[]
    for r in solid:
        if '-1x-' not in r['cell'] or f'-{scheme}-' not in r['cell'].split('/')[0] or not r['cell'].endswith('__'+pose):continue
        bg=r['cell'].split('/')[1].split('__')[0]
        if not bg.startswith('grey-') or bg=='grey-0' or r['censoredChannels']:continue
        v=int(bg.split('-')[1]);point=dict(cell=r['cell'],role=r['role'],x=v/255,
            target=float(lin(r['nativeMedian'])@W),size=.09228515625)
        (targets if r['role']=='calibration' else validation).append(point)
    for r in canonical:
        if not r['cell'].startswith('apple-macos-27.0-1x-') or f'-{scheme}-' not in r['cell'].split('/')[0] or not r['cell'].endswith('__'+pose):continue
        if 'mid-chroma' in r['cell'] or r['censoredChannels']:continue
        # Neutral canonical RGB are slightly blue, so use their actual no-glass
        # abscissa rather than inventing a perfectly grey anchor.
        b=np.array(r['background']);x=float(enc(lin(b)@W)/255) if pose=='rest' else float(b@W/255)
        targets.append(dict(cell=r['cell'],role=r['role'],x=x,target=r['nativeLuma'],size=1))
    def patched(delta):
        out=copy.deepcopy(m)
        for key in ['backdropToneResponseThin','backdropToneResponseThick']:
            out[key]=[m[key][0],*[float(m[key][i+1]+delta[i]) for i in range(3)]]
        return out
    def residual(delta):
        pm=patched(delta)
        return [response(t['x'],pm,t['size'])-t['target'] for t in targets]
    low=[max(-m[k][i] for k in ['backdropToneResponseThin','backdropToneResponseThick']) for i in [1,2,3]]
    high=[min(1-m[k][i] for k in ['backdropToneResponseThin','backdropToneResponseThick']) for i in [1,2,3]]
    fit=least_squares(residual,[0,0,0],bounds=(low,high),xtol=1e-13,ftol=1e-13,gtol=1e-13)
    pm=patched(fit.x);sv=np.linalg.svd(fit.jac,compute_uv=False)
    readings=[]
    for t in targets+validation:
        yp=response(t['x'],pm,t['size'])
        readings.append({**t,'predicted':yp,'missCodes':float(enc(yp)-enc(t['target']))})
    black=next(r for r in solid if f'-1x-{scheme}-' in r['cell'] and r['cell'].endswith('/grey-0__circular-120__'+pose))
    fits.append(dict(scheme=scheme,pose=pose,fitParameters=3,sharedShifts=fit.x.tolist(),
        jacobianRank=int(np.linalg.matrix_rank(fit.jac)),singularValues=sv.tolist(),
        patch={k:pm[k] for k in ['backdropToneResponseThin','backdropToneResponseThick']},
        blackLevel=float(lin(black['nativeMedian'])@W),blackRenderExpressible=False,
        readings=readings,objectiveLinearSSE=float(sum(v*v for v in fit.fun)),
        maximumCalibrationMissCodes=max(abs(t['missCodes']) for t in readings if t['role']!='validation'),
        grey96MissCodes=next(t['missCodes'] for t in readings if t['role']=='validation')))
    print(scheme,pose,'shifts',fit.x,'rank',np.linalg.matrix_rank(fit.jac),
          'max cal',fits[-1]['maximumCalibrationMissCodes'],'grey96',fits[-1]['grey96MissCodes'])
save('candidate-fit.json',fits)
