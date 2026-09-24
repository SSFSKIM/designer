"""The candidate's unchanged shadow law against B1's native windows (§5.179)."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent;ROOT=HERE.parents[3]
cut=json.loads((HERE.parent/'2026-09-20-w30-g0-cut/shadow-cut.json').read_text())['cells']
profiles=[p['key'] for p in json.loads((ROOT/'apps/reference-apple/scenes.json').read_text())['profiles'] if p['key'].startswith('apple-macos-27.0-')]
plans=json.loads((HERE/'candidate-plans.json').read_text());rows=[]
for scheme in ['light','dark']:
    doc=json.loads((CAL/'profiles'/f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json').read_text())
    sh=doc['patch']['outerShadow']
    for plan in plans:
        if '-'+scheme+'-' not in plan['profile']:continue
        assert set(plan['active']['patch'])=={'backdropToneBlackStrength','backdropToneBlackThin','backdropToneBlackThick'}
    for span in [96,128,160]:
        medians=[]
        for profile in profiles:
            if '-'+scheme+'-' not in profile:continue
            values=sorted(c['sigmaCss'] for c in cut if c['profile']==profile and c['span']==span)
            if values:medians.append(values[len(values)//2])
        lo=max(m*.95 for m in medians);hi=min(m*1.05 for m in medians)
        sigma=sh['sigmaPx']+max(sh['sigmaThinOffsetPx'],sh['sigmaSlopePerSpan']*(span-sh['sigmaSpanRefPx']))
        rows.append(dict(scheme=scheme,span=span,sigma=sigma,lower=lo,upper=hi,contributingBeds=len(medians),passStop=lo<=sigma<=hi))
with (HERE/'price-b1.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print(json.dumps(rows,indent=2));assert all(r['passStop'] for r in rows)
