#!/usr/bin/env python3
"""Reduce G1a readings without opening any image (§5.171)."""
from collections import Counter, defaultdict
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
read=lambda name:json.loads((HERE/name).read_text())


def main():
    a,c,r,p,pop=[read(n+'.json') for n in ('angular','colour','radial','prices','population')]
    population={(r['profile'],r['scene']):r for r in pop['rows']}
    angles=[]
    for part in ('all','straight','arcs'):
        rs=[r for r in a['rows'] if r['part']==part]
        angles.append(dict(part=part,strata=len(rs),closed=sum(r['closesOneByte'] for r in rs),
                           choices=dict(Counter(r['selected'] for r in rs))))
    # Refined backdrop strata must be recombined BEFORE comparing to G0's
    # ceiling. A subclass is not independently assigned its parent's bar.
    bgroups=defaultdict(list); groups=defaultdict(list)
    for row in c['strata']:
        cls=row['backdropClass']
        oldcls=cls if cls in ('photo','light-solid','black-bearing') else 'dark-or-other-solid'
        bgroups[(row['profile'],row['pose'],oldcls,row['side'])].append(row)
        groups[(row['profile'],row['pose'],cls)].append(row)
    colour=[]; ceilings=[]
    for key,rs in sorted(groups.items()):
        pixels=sum(r['candidate']['pixels'] for r in rs)
        avg=lambda which,k:[sum(r[which][k][i]*r[which]['pixels'] for r in rs)/pixels for i in range(3)]
        # Local-fit means below are optimistic: fitted separately per side,
        # NOT one feasible runtime family, and still cannot prove a space.
        local={}
        for space in ('encoded','linear'):
            scores=[]
            for row in rs:
                best=min((f for f in row['localFits'] if f['space']==space),key=lambda f:f['mae'])
                scores.append((row['candidate']['pixels'],best))
            local[space]=[sum(n*f['maeRGB'][i] for n,f in scores)/pixels for i in range(3)]
        colour.append(dict(profile=key[0],pose=key[1],backdropClass=key[2],pixels=pixels,
            baselineRGB=avg('baseline','maeRGB'),candidateRGB=avg('candidate','maeRGB'),
            optimisticLocalRGB=local))
    for key,rs in sorted(bgroups.items()):
        pixels=sum(r['candidate']['pixels'] for r in rs)
        rgb=[sum(r['candidate']['maeRGB'][i]*r['candidate']['pixels'] for r in rs)/pixels for i in range(3)]
        ceilings.append(dict(profile=key[0],pose=key[1],backdropClass=key[2],side=key[3],
            pixels=pixels,maeRGB=rgb,mae=sum(rgb)/3,bound=rs[0]['g0Ceiling'],
            red=sum(rgb)/3>rs[0]['g0Ceiling']))
    price_groups=defaultdict(list)
    for row in p['rows']:
        if (row['profile'],row['scene']) not in population: continue
        meta=population[(row['profile'],row['scene'])]
        for f in row['forms']:
            key=(row['profile'],row['pose'],meta['backdropClass'],meta['span'],meta['kind'],f['name'])
            price_groups[key].append(f)
    prices=[]
    for key,rs in sorted(price_groups.items()):
        pixels=sum(r['ringPixels'] for r in rs)
        prices.append(dict(profile=key[0],pose=key[1],backdropClass=key[2],span=key[3],kind=key[4],form=key[5],
            cells=len(rs),pixels=pixels,
            maeRGB=[sum(r['maeRGB'][i]*r['ringPixels'] for r in rs)/pixels for i in range(3)],
            lossRGB=[sum(r['lossRGB'][i]*r['ringPixels'] for r in rs)/pixels for i in range(3)],
            offsets=[dict(offset=o+1,maeRGB=[sum(r['offsets'][o]['maeRGB'][i]*r['offsets'][o]['pixels'] for r in rs)/
                sum(r['offsets'][o]['pixels'] for r in rs) for i in range(3)]) for o in range(6)]))
    summary=dict(population=len(pop['rows']),angleSummary=angles,colour=colour,
        g0Ceilings=ceilings,ceilingMisses=sum(r['red'] for r in ceilings),prices=prices)
    (HERE/'tables.json').write_text(json.dumps(summary,separators=(',',':'))+'\n')
    print('Angular closures:',angles)
    print('G0 ceilings missed:',summary['ceilingMisses'],'/',len(ceilings))
    for row in colour:
        print(row['profile'],row['pose'],row['backdropClass'],
              'candidate RGB',*[round(x,3) for x in row['candidateRGB']],
              'best local encoded RGB',*[round(x,3) for x in row['optimisticLocalRGB']['encoded']],
              'linear RGB',*[round(x,3) for x in row['optimisticLocalRGB']['linear']])


if __name__=='__main__': main()
