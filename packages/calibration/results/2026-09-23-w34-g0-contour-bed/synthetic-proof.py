#!/usr/bin/env python3.12
"""Derive bin populations and resolution tests from declarations, not native fits."""
import json
from pathlib import Path
import numpy as np
import instrument as I
from wave import default_wave,native_only

HERE=Path(__file__).resolve().parent


def main():
    wave=default_wave();paths=json.loads((HERE/'supplied-paths.json').read_text());population=[]
    for name,component in wave.spec['components'].items():
        if native_only(component):continue
        for scale in [1,2]:
            c={**component,'suppliedPaths':paths[name]}
            d,nx,ny,arc=I.geometry(320*scale,200*scale,c,scale)
            bins=[dict(part=k[0],shell=k[1],bin=k[2],pixels=int(m.sum()),admissible=int(m.sum())>=4)
                  for k,m in I.strata(d,nx,ny,arc)]
            population.append(dict(component=name,scale=scale,bins=bins,
                populated=len(bins),belowFour=sum(b['pixels']<4 for b in bins)))
    alternatives=[]
    for amplitude in [1,2,4,8]:
        n=np.array([[amplitude,0,-amplitude],[-amplitude,0,amplitude]]*4,dtype=float)
        stat=I.residual(n,np.zeros_like(n));alternatives.append(dict(amplitude=amplitude,
            statistic=stat,closesAtFloor=I.closes(stat,[0,0,0]),
            separatesFromZeroAtTwoFloor=amplitude>2))
    assert next(r for r in alternatives if r['amplitude']==4)['separatesFromZeroAtTwoFloor']
    assert not next(r for r in alternatives if r['amplitude']==4)['closesAtFloor']
    result=dict(populationRoute='Supplied declaration paths, no native residuals opened',
        minimumPopulation=4,geometries=population,syntheticAlternatives=alternatives,
        unresolvedBelowFloor='One-code alternatives can close at the encoding floor; no noise-free claim.',
        discriminationScope='Four-code alternatives separate from zero in every populated synthetic stratum; actual nuisance envelopes may still make G2 insufficient resolution.')
    (HERE/'synthetic-proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print([(r['component'],r['scale'],r['populated'],r['belowFour']) for r in population])


if __name__=='__main__':main()
