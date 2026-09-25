"""Per-bin old-treatment comparison, failure strata and transfer summaries."""
import collections,gzip,json
import numpy as np
from common import HERE,G0,edge

def read(name):
    p=HERE/name;return json.loads(gzip.decompress(p.read_bytes()) if name.endswith('.gz') else p.read_text())

def main():
    old=json.loads(gzip.decompress((G0/'old-rim.json.gz').read_bytes()))['rows']
    key=lambda r:(r['cell'],r['part'],r['shell'],r['bin'])
    lookup={key(r):r for r in old};res=read('residuals.json.gz');comparisons=[];aggregates=[]
    for r in res:
        if not r['active'] or not r['admissible']:continue
        o=lookup[key(r)]
        assert np.max(abs(np.array(o['nativeExcessRGB'])-r['nativeExcess']))<1e-10
        before=abs(np.array(o['oldExcessRGB'])-o['nativeExcessRGB'])
        after=abs(np.array(r['predictedExcess'])-r['nativeExcess']);delta=after-before
        labels=['worse' if v>.5 else 'better' if v<-.5 else 'same' for v in delta]
        comparisons.append(dict(family=r['family'],cell=r['cell'],scheme=r['scheme'],role=r['role'],
            geometry=r['geometry'],part=r['part'],shell=r['shell'],bin=r['bin'],
            nativeExcess=r['nativeExcess'],oldExcess=o['oldExcessRGB'],oldRimAlone=o['rimContributionRGB'],
            predictedExcess=r['predictedExcess'],oldMeanError=before.tolist(),newMeanError=after.tolist(),
            errorChange=delta.tolist(),classificationRGB=labels))
    for family in ['F1','F2','F3']:
        pool=[r for r in comparisons if r['family']==family]
        if not pool:continue
        scopes=[('all',pool)]+[(f'{s}/{role}/{geo}',[r for r in pool if r['scheme']==s and r['role']==role and r['geometry']==geo])
            for s,role,geo in sorted({(r['scheme'],r['role'],r['geometry']) for r in pool})]
        for scope,selected in scopes:
            counts=collections.Counter(x for r in selected for x in r['classificationRGB'])
            worst=sorted(selected,key=lambda r:max(r['errorChange']),reverse=True)[:10]
            aggregates.append(dict(family=family,scope=scope,channelBins=sum(counts.values()),
                counts=dict(counts),worstWorsenings=worst))
    edge.save(HERE/'old-rim-comparison.json.gz',comparisons);edge.save(HERE/'old-rim-summary.json',aggregates)
    failures=[]
    for family,cell in sorted({(r['family'],r['cell']) for r in res if r['active']}):
        selected=[r for r in res if r['family']==family and r['cell']==cell and r['admissible']]
        worst=max(selected,key=lambda r:max(r['residualRGB']))
        failures.append(dict(family=family,cell=cell,role=worst['role'],scheme=worst['scheme'],
            bins=len(selected),failedBins=sum(r['fails'] for r in selected),maximum=max(worst['residualRGB']),worst=worst))
    edge.save(HERE/'failure-cells.json',failures)
    trans=read('transfer.json.gz');ts=[]
    for family in sorted({r['family'] for r in trans}):
        selected=[r for r in trans if r['family']==family and r['active']]
        ts.append(dict(family=family,pixelRange=[min(r['edgeTransferPixelRange'][0] for r in selected),max(r['edgeTransferPixelRange'][1] for r in selected)],
            binMeanRange=[min(v for r in selected for b in r['bins'] if b['admissible'] for v in b['edgeTransferRGB']),
                          max(v for r in selected for b in r['bins'] if b['admissible'] for v in b['edgeTransferRGB'])]))
    edge.save(HERE/'transfer-summary.json',ts)
    print(json.dumps(dict(oldRim=[r for r in aggregates if r['scope']=='all'],transfer=ts),indent=2))

if __name__=='__main__':main()
