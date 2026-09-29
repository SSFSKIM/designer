"""Non-gating boundary projections: stroke contribution, never an interior body fit."""
import numpy as np
import replay as r


def straddling(observations, q, family, css, curvature, emit):
    count = 0
    maximum = 0.
    materials = r.shadow.materials()
    for o in observations:
        shapes = [part['shape'] for part in o['parts']]
        hw = o['parts'][0]['reference'].shape[:2]
        geo = r.m.readers.geometry(hw, shapes, o['scale'])
        for part in o['parts']:
            mask = (geo.member == part['member']) & ~geo.whole & ~geo.outside & (abs(geo.d) < 2)
            yy, xx = np.nonzero(mask)
            if not len(xx):
                continue
            g = r.m.samples(part['shape'], np.c_[xx, yy], o['scale'])
            b = r.m.bilinear(part['reference'], g['q'])
            fall = r.held_falloff(g, part['shape'], materials[r.ENDPOINTS[o['endpoint']]]) \
                if o['endpoint'] in (0, 2) else np.zeros_like(g['d'])
            compact = r.CompactComposite(g, b, fall)
            predicted = compact.predict(q, o['endpoint'], part['amplitude'], family, css, curvature)
            baseline = compact.mean_b-part['amplitude']*compact.mean_bfall
            contribution = predicted-baseline
            for row in part['boundary']:
                at = geo.angle[mask] == row['angle']
                if not np.any(at):
                    continue
                maximum = max(maximum, float(abs(contribution[at]).max()))
                emit(dict(cell=o['cell'], role=o['role'], endpoint=r.ENDPOINTS[o['endpoint']],
                          scale=o['scale'], member=part['member'], **row,
                          strokeContributionMeanRGB=contribution[at].mean(0).tolist(),
                          strokeContributionMinimumRGB=contribution[at].min(0).tolist(),
                          strokeContributionMaximumRGB=contribution[at].max(0).tolist(),
                          qualification='DIAGNOSTIC stroke-only increment; body on the inside '
                              'fraction is not modelled and no total-pixel accuracy is claimed'))
                count += 1
    return dict(diagnosticBins=count, maximumPixelStrokeIncrementCodes=maximum,
                usedForFit=False, usedForSurvival=False)
