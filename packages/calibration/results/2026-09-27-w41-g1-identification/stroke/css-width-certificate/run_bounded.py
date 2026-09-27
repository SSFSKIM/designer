"""Add the approved sealed-range constraint beside, never over, the first screen."""
import argparse
import json
from pathlib import Path
import bounded_cut
import run

HERE=Path(__file__).resolve().parent


def derive():
    meta,arrays=run.derive() # Independently reconstruct saved observations through unchanged law.
    assert meta==json.loads((HERE/'unbounded/observations.json').read_text())
    with run.np.load(HERE/'unbounded/pixels-and-geometry.npz',allow_pickle=False) as saved:
        assert set(saved.files)==set(arrays)
        for key,value in arrays.items():assert run.np.array_equal(saved[key],value)
    unbounded=json.loads((HERE/'unbounded/certificate.json').read_text())
    assert unbounded=={ep:run.cut.solve(meta['thresholds'],groups) for ep,groups in meta['groups'].items()}
    outcomes={ep:bounded_cut.solve(meta['thresholds'],groups) for ep,groups in meta['groups'].items()}
    sources=run.SOURCE/'packages/calibration/results/2026-09-27-w41-g0-declaration/instrument/instrument.py'
    return dict(schema='w41-css-width-bounded-necessary-certificate-1',
        declarationSha256=run.DECLARATION_SHA,
        unboundedCertificateSha256=run.sha((HERE/'unbounded/certificate.json').read_bytes()),
        savedObservationsSha256=run.sha((HERE/'unbounded/observations.json').read_bytes()),
        clarificationSha256=run.sha((HERE.parent/'css-width-z-bound-clarification.json').read_bytes()),
        unchangedLawSha256=run.sha(sources.read_bytes()),
        sourceProof={'angular':'instrument.angular returns clip(normalized angular numerator,0,1); '
                                'beta[0,1],gamma0 gives maximum1 and A(top)=1-beta.',
                     'M0':'instrument.material M0 returns clip(t*b+k,0,255).',
                     'M1':'instrument.material M1 uses255*body.curve, which clips to[0,1].',
                     'M2':'instrument.material M2 returns255*body.encode(gamut_at_luma(colour)); '
                          'encode clips linear inputs to[0,1]. Full neutral RGB makes '
                          'Y-D(b_j)=0 mathematically, so the contextual correction is identity.',
                     'product':'If0<=A<=1 and0<=S<=255, then-b<=A*(S-b)<=255-b for every b∈[0,255]. '
                               'Independent product values per input/channel relax all coefficient '
                               'coupling; beta1/A0 and width0 remain included.'},
        alias='The arbitrary-real-z screen leaves w in(1/32,3/64] CSSpx feasible. '
              'Its occupancy fractions are1/16,1/16,0 on1x-shell0,2x-shell0,2x-shell1. '
              'The bounded extension is separate and retains the exact sealed output range; '
              'no width, coefficient, support, reference, population or tolerance changes.',
        endpointModelDecisions={ep:{model:('REJECTED_CSS_WIDTH_BY_NECESSARY_CUT' if
            result['status']=='CERTIFIED_INFEASIBLE_RELAXATION' else 'NOT_REJECTED_BY_THIS_CUT')
            for model in ('M0','M1','M2')} for ep,result in outcomes.items()},
        geometryScope='CSS-width only. Device-width and nominal-curvature are not rejected by this certificate.',
        nativeScope='Saved calibration observations only; no new archive reads, no validation or holdout.',
        optimizerScope='No fit stopped, budget changed, or optimizer outcome substituted.',
        outcomes=outcomes)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    args=parser.parse_args();result=derive();out=HERE/'bounded'
    if args.check:
        assert result==json.loads((out/'certificate.json').read_text())
        print('Bounded saved replay PASS; both external pixel trees denied.')
    else:
        out.mkdir(exist_ok=False);run.write(out/'certificate.json',result)
    print(json.dumps(dict(decisions=result['endpointModelDecisions'],outcomes={ep:dict(
        status=v['status'],states=v['stateCount'],feasible=v['feasibleStateIndices'],
        individuallyDecidingInputLevels=v['independentlyRejectingInputLevels'])
        for ep,v in result['outcomes'].items()}),indent=2))


if __name__=='__main__':main()
