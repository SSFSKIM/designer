"""W50's analytical deep8 and central8 cuts, using W49b's W44 signed-distance convention.

Path placement/size is separately checked against each native suppliedPaths attestation by the
sitting driver. The deep cut is the declared analytical contour, not a detected L1 silhouette.
Every channel is kept; neither luma averaging nor channel cancellation can hide a level miss.
"""
import importlib.util
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
spec=importlib.util.spec_from_file_location('w50_interior', ROOT/'packages/calibration/results/2026-10-03-w44-g0-declaration/port/interior.py')
P=importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


def read(rgb, component, scale):
    canvas={'width':512,'height':384}
    distance=P.signed_distance(component, canvas, scale, rgb.shape[:2])
    yy,xx=np.indices(rgb.shape[:2], dtype=float)
    center=(np.abs((xx+.5)/scale-256)<4)&(np.abs((yy+.5)/scale-192)<4)
    result={}
    for name,mask in (('deep8',distance<=-8*scale),('center8',center)):
        values=np.asarray(rgb[mask],dtype=float)
        if not len(values) or not np.isfinite(values).all():
            raise ValueError('Required native cut is empty or unreadable')
        result[name]=dict(pixels=len(values), medianCodes=np.median(values,axis=0).tolist(),
                          meanCodes=values.mean(axis=0).tolist())
    return result


def repeat_verdict(readings):
    if len(readings)!=3:
        raise ValueError('Exactly three admitted repetitions are required; never silently add runs')
    rows={}
    for support in ('deep8','center8'):
        values=np.asarray([r[support]['medianCodes'] for r in readings],dtype=float)
        if values.shape!=(3,3) or not np.isfinite(values).all():
            raise ValueError('Per-channel repeat medians are incomplete')
        spread=np.ptp(values,axis=0)
        rows[support]=dict(spreadCodes=spread.tolist(),barCodes=np.maximum(.5,spread/2).tolist())
    return dict(passes=all(max(r['spreadCodes'])<=1 for r in rows.values()), supports=rows)


def sentinel_verdict(opened,closed):
    changes={name:(np.asarray(closed[name]['medianCodes'])-np.asarray(opened[name]['medianCodes'])).tolist()
             for name in ('deep8','center8')}
    return dict(passes=all(max(abs(v) for v in d)<=1 for d in changes.values()), deltaCodes=changes)
