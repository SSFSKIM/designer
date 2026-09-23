#!/usr/bin/env python3.12
"""Read retained phase runs without fitting a contour law (§5.174)."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
SCRATCH=Path.home()/'vitrea-w34/scratch'


def image(path):return np.asarray(Image.open(path).convert('RGB'),dtype=np.int16)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows=[];repeats=[];classes=[]
    for scale in [1,2]:
        profile=f'apple-macos-27.0-{scale}x-light-standard-glass0.5'
        states={name:[] for name in ['p0','x25','x50','x75','xy25']}
        for run in [1,2,3]:
            root=SCRATCH/f'phase-{scale}x'/f'run-{run}'
            admission=json.loads((root/'admission.json').read_text())
            if not admission['admitted']:raise ValueError('phase attempt not admitted; do not infer a snap from it')
            base=image(root/profile/'grey__p0__rest.png')
            for name in states:
                path=root/profile/f'grey__{name}__rest.png';a=image(path);states[name].append(a)
                candidates=[]
                for dy in range(-2,3):
                    for dx in range(-2,3):
                        # Compare an interior crop, far outside any glass/shadow
                        # support but away from canvas boundaries shifted away.
                        actual=a[10:-10,10:-10]
                        prediction=base[10-dy:base.shape[0]-10-dy,10-dx:base.shape[1]-10-dx]
                        candidates.append((float(np.abs(actual-prediction).mean()),dx,dy))
                error,dx,dy=min(candidates)
                # Raw RGB and signed apparent body contrast, not an assertion
                # that glass's stroke/body mixture is ordinary fill coverage.
                x0,y0=100*scale,78*scale;cx,cy=160*scale,100*scale
                body=np.median(base[90*scale:110*scale,130*scale:190*scale],axis=(0,1))
                arc=a[cy-2:cy+3,x0-3:x0+5].mean(axis=0)
                straight=a[y0-3:y0+5,cx-10:cx+10].mean(axis=1)
                denominator=np.where(body==128,1,body-128)
                rows.append(dict(scale=scale,run=run,phase=name,inputSha256=sha(path),
                    manifestSha256=sha(root/'manifest.json'),suppliedOffsetCss={
                        'p0':[0,0],'x25':[.25/scale,0],'x50':[.5/scale,0],
                        'x75':[.75/scale,0],'xy25':[.25/scale,.25/scale]}[name],
                    changedPixels=int(np.any(a!=base,axis=2).sum()),bestIntegerTranslation=[dx,dy],
                    translatedMAE=error,arcApexColumnRGB=arc.tolist(),straightNormalRowRGB=straight.tolist(),
                    arcApparentContrast=((arc-128)/denominator).tolist(),
                    straightApparentContrast=((straight-128)/denominator).tolist()))
        for run in range(3):
            classes.append(dict(scale=scale,run=run+1,
                zeroEqualsQuarter=bool(np.array_equal(states['p0'][run],states['x25'][run])),
                zeroEqualsJointQuarter=bool(np.array_equal(states['p0'][run],states['xy25'][run])),
                halfEqualsThreeQuarter=bool(np.array_equal(states['x50'][run],states['x75'][run]))))
        for name,images in states.items():
            repeats.append(dict(scale=scale,phase=name,maximumChannelDifference=int(max(
                np.abs(images[i]-images[j]).max() for i in range(3) for j in range(i)))))
    snapped=all(all(c[k] for k in ['zeroEqualsQuarter','zeroEqualsJointQuarter','halfEqualsThreeQuarter']) for c in classes) and all(r['bestIntegerTranslation']==(
        [1,0] if r['phase'] in ['x50','x75'] else [0,0]) for r in rows)
    result=dict(verdict='UNREACHABLE at 1x and 2x' if snapped else 'NOT ESTABLISHED',
        meaning='Device-quarter phases collapse to two byte-states: quarter and joint-quarter equal zero; half equals three-quarter with best integer translation +1 x pixel. The shifted state is NOT exactly an integer translation; its small residual is retained. No window-origin fallback.',
        qualification='Apparent contrast transects are not an identified glass coverage law. Within-class byte identity establishes the collapsed phase axis; nonzero integer-translation residual qualifies the grid-shift interpretation. phase-reading-initial.json retains the overly strict exact-translation criterion, which did not pass.',
        rows=rows,phaseEquivalence=classes,threeRunRepeatDifferences=repeats)
    (HERE/'phase-reading.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['verdict']);print(repeats)


if __name__=='__main__':main()
