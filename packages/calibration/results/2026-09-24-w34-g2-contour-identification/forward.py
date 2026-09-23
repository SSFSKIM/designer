#!/usr/bin/env python3.12
"""Qualified body-aware follow-up, with geometry and baseline nuisance (§5.176).

Only solids and affine-gradient circular cells identify a proposed body field.
Structured cells retain the model-free effective-response table; ordinary fill
coverage never supplies the glass body's coverage. This module does not fit.
"""
import json
from pathlib import Path
import numpy as np
import identification as M


def baseline(record, space, translation, samples=64, cov=None):
    """The declared body's actual pixel integral, including nonlinear encoding."""
    component=record['component'];scale=record['scale'];D=record['D']/255
    origin=np.array(component['suppliedPaths'][0]['frameOrigin'])*scale+translation
    size=np.array(component['size'])*scale;rect=[*origin,*(origin+size)]
    offsets=(np.arange(samples)+.5)/samples
    oy,ox=np.meshgrid(offsets,offsets,indexing='ij');ox=ox.ravel();oy=oy.ravel()
    body=record['body'];outputs=[];lo=[];hi=[]
    if 'coefficients' not in body:
        if cov is None:cov=M.coverage(record['xy'],component,scale,translation,samples)
        a=cov['body'][:,None];B=np.array(body['betaRGB'])/255;U=np.array(body['uncertaintyRGB'])/255
        low,high=np.clip(B-U,0,1),np.clip(B+U,0,1)
        if space=='linear':B,low,high,D=[M.decode(v) for v in [B,low,high,D]]
        return (1-a)*D+a*B,(1-a)*D+a*low,(1-a)*D+a*high
    for start in range(0,len(D),64):
        xy=record['xy'][start:start+64]
        x=xy[:,0,None]+ox;y=xy[:,1,None]+oy
        a=M.I.stadium(x,y,rect,min(size)/2)[0]<0
        if 'coefficients' in body:
            beta=np.array(body['coefficients'])/255
            bx,by=M.body_coordinates(x,y,scale)
            B=beta[0]+bx[:,:,None]*beta[1]+by[:,:,None]*beta[2]
        else:B=np.broadcast_to(np.array(body['betaRGB'])/255,(*x.shape,3))
        U=np.array(body['uncertaintyRGB'])/255
        low,high=np.clip(B-U,0,1),np.clip(B+U,0,1);B=np.clip(B,0,1)
        back=np.broadcast_to(D[start:start+64,None,:],B.shape)
        if space=='linear':B,low,high,back=[M.decode(v) for v in [B,low,high,back]]
        outputs.extend(np.mean(np.where(a[:,:,None],B,back),axis=1))
        lo.extend(np.mean(np.where(a[:,:,None],low,back),axis=1))
        hi.extend(np.mean(np.where(a[:,:,None],high,back),axis=1))
    return np.array(outputs),np.array(lo),np.array(hi)


def prediction(record, spec, coefficients, cov, base):
    D=record['D']/255
    if spec['space']=='linear':D=M.decode(D)
    g=cov['band'];q=cov['q'+str(spec.get('power',2.))]
    result=base.copy()
    for c in range(3):
        coef=np.array(coefficients[c])
        X=np.c_[g*D[:,c],g,q*D[:,c],q] if 'even' in spec['name'] else np.c_[g*D[:,c],g]
        result[:,c]+=X@coef
    result=np.clip(result,0,1)
    return 255*(M.encode(result) if spec['space']=='linear' else result)


def reference_uncertainty(record,spec,coefficients,cov,nominal):
    """Propagate the captured backdrop's half-code through the actual response.

    For a physical stroke this is (1-s)*(1-a). The unrestricted affine diagnostic
    can amplify a backdrop perturbation, so a constant half-code is not its bound.
    Encoding is propagated at both interval endpoints, not by a gamma multiplier.
    """
    D=record['D']/255
    low=np.clip(D-.5/255,0,1);high=np.clip(D+.5/255,0,1)
    value=nominal/255
    if spec['space']=='linear':D,low,high,value=[M.decode(v) for v in [D,low,high,value]]
    weight=np.tile((1-cov['body'])[:,None],(1,3))
    for c,coef in enumerate(coefficients):
        weight[:,c]+=cov['band']*coef[0]
        if 'even' in spec['name']:weight[:,c]+=cov['q'+str(spec['power'])]*coef[2]
    errors=[]
    for endpoint in [low,high]:
        shifted=np.clip(value+(endpoint-D)*weight,0,1)
        if spec['space']=='linear':shifted=M.encode(shifted)
        errors.append(abs(255*shifted-nominal))
    return np.maximum(*errors)


def verify(records,fitrows,prefix):
    """Re-evaluate nominated forward fits; never refit against validation.

    The earlier compact-family tables are retained. This table replaces no
    recorded value: it adds the exact body integral and separately tabulates
    body, reference, geometry and 64/128 numerical prediction envelopes.
    """
    rows=[];cache={};predictions={};summary=[]
    selected=[(i,f) for i,f in enumerate(fitrows) if f['spec'].get('exactBody')]
    for record in records:
        if record['cov'] is None or record['backgroundKind'] not in ['solid','linear-gradient']:continue
        physical=record['backgroundKind'] in ['solid','linear-gradient']
        for index,fit in selected:
            if (record['profile'],record['pose'])!=(fit['profile'],fit['pose']):continue
            spec=fit['spec'];space=spec['space'];align=np.array(record['alignment']['translationDevicePx'])
            k=(record['cell'],space)
            if k not in cache:cache[k]=baseline(record,space,align,cov=record['cov'])
            base,bodylo,bodyhi=cache[k]
            nominal=prediction(record,spec,fit['coefficients'],record['cov'],base)
            lower=prediction(record,spec,fit['coefficients'],record['cov'],bodylo)
            upper=prediction(record,spec,fit['coefficients'],record['cov'],bodyhi)
            body_unc=np.maximum(abs(nominal-lower),abs(upper-nominal))
            # Physical alignment is an isoresponse fit, not a measured hidden
            # origin. Sample its declared half-pixel envelope at all eight
            # cardinal/corner perturbations; include radius-scaled path error
            # as a separate recorded bound on the displacement amplitude.
            u=record['alignment'].get('physicalContourUncertaintyDevicePx')
            geometry_unc=np.zeros_like(nominal)
            if u is not None:
                for sx,sy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                    shifted=align+np.array([sx,sy])*u
                    ck=json.dumps([record['component'],record['scale'],shifted.tolist()],sort_keys=True)
                    if ck not in cache:cache[ck]=M.coverage(record['xy'],record['component'],record['scale'],shifted)
                    cov=cache[ck]
                    # Uniform body fields integrate exactly from area. Gradient
                    # fields are integrated separately at the perturbed path.
                    bk=(record['cell'],space,sx,sy)
                    if bk not in cache:cache[bk]=baseline(record,space,shifted,cov=cov)[0]
                    moved=prediction(record,spec,fit['coefficients'],cov,cache[bk])
                    geometry_unc=np.maximum(geometry_unc,abs(moved-nominal))
            nk=json.dumps([record['component'],record['scale'],align.tolist(),'128'],sort_keys=True)
            if nk not in cache:cache[nk]=M.coverage(record['xy'],record['component'],record['scale'],align,samples=128)
            bk=(record['cell'],space,'128')
            if bk not in cache:cache[bk]=baseline(record,space,align,samples=128,cov=cache[nk])[0]
            highres=prediction(record,spec,fit['coefficients'],cache[nk],cache[bk])
            numerical=abs(highres-nominal)
            quant=reference_uncertainty(record,spec,fit['coefficients'],record['cov'],nominal)
            unc=body_unc+geometry_unc+numerical+quant
            rounded=np.floor(nominal+.5)
            predictions[(record['cell'],index)]=(rounded,unc)
            for key,mask in record['masks']:
                row=dict(cell=record['cell'],role=record['role'],fit=index,part=key[0],shell=key[1],bin=key[2],
                    bodyIdentified=physical,
                    routing='qualified body field' if physical else 'effective response: structured boundary unidentified',
                    bodyUncertaintyRGB=body_unc[mask].mean(axis=0).tolist(),
                    geometryUncertaintyRGB=geometry_unc[mask].mean(axis=0).tolist(),
                    numericalUncertaintyRGB=numerical[mask].mean(axis=0).tolist(),
                    referenceUncertaintyRGB=quant[mask].mean(axis=0).tolist(),
                    **M.bin_residual(record['n'][mask],rounded[mask],unc[mask],record['bar'][key]['barRGB']))
                rows.append(row)
            print('forward verified',record['cell'],index,flush=True)
    # Discrimination among nominated forward alternatives, within the exact
    # same cell/mask and using the sum of both full nuisance-envelope widths.
    pairs=[]
    for record in records:
        ids=sorted(i for c,i in predictions if c==record['cell'])
        for ai,a in enumerate(ids):
            for b in ids[ai+1:]:
                pa,ua=predictions[(record['cell'],a)];pb,ub=predictions[(record['cell'],b)]
                for key,mask in record['masks']:
                    if mask.sum()<4:continue
                    delta=abs(pa[mask]-pb[mask]).mean(axis=0)
                    width=(2*(ua[mask]+ub[mask])).mean(axis=0)
                    tau=np.maximum(1,record['bar'][key]['barRGB'])
                    pairs.append(dict(cell=record['cell'],role=record['role'],families=[a,b],part=key[0],
                        shell=key[1],bin=key[2],pixels=int(mask.sum()),separationRGB=delta.tolist(),
                        nuisanceWidthRGB=width.tolist(),tauRGB=tau.tolist(),
                        discriminated=bool(np.any(delta>2*tau+width))))
    M.save(M.HERE/(prefix+'-forward.json.gz'),rows)
    M.save(M.HERE/(prefix+'-discrimination.json.gz'),pairs)
    return rows,pairs


def main():
    records,controls=M.extract(M.W.default_wave())
    eligible=[r for r in records if r['cov'] is not None and r['backgroundKind'] in ['solid','linear-gradient']]
    for r in eligible:
        r['exactBaselines']={space:baseline(r,space,r['alignment']['translationDevicePx'],cov=r['cov'])[0]
                             for space in ['encoded','linear']}
    fits=json.loads((M.HERE/'fits.json').read_text())
    for space in ['encoded','linear']:
        for name in ['body-forward-affine','body-forward-even-affine']:
            for profile,pose in sorted({(r['profile'],r['pose']) for r in eligible}):
                calibration=[r for r in eligible if r['role']=='calibration' and (r['profile'],r['pose'])==(profile,pose)]
                for method in ['least-squares','minimax']:
                    best=None;grid=[]
                    for power in M.POWERS if 'even' in name else [2.]:
                        spec=dict(name=name,space=space,stage='new-axes',power=power,exactBody=True,
                                  domain='circular solid and affine gradient; structured boundary declined')
                        coef,objective=M.fit_spec(calibration,spec,method)
                        grid.append(dict(power=power,objective=objective))
                        if best is None or objective<best[0]:best=(objective,spec,coef)
                    fits.append(dict(profile=profile,pose=pose,method=method,spec=best[1],coefficients=best[2],
                                     calibrationObjective=best[0],calibrationCells=len(calibration),grid=grid))
                    print('exact fit',len(fits),profile,pose,name,space,method,flush=True)
    M.save(M.HERE/'qualified-fits.json',fits)
    M.evaluate(eligible,fits[400:],'exact-validation')
    verify(eligible,fits,'qualified-validation')


if __name__=='__main__':main()
