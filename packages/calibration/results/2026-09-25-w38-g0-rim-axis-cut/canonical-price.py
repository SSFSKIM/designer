"""Canonical T census and tinted held-top prediction; no shader/render claim."""
import hashlib,io,json,gzip
from pathlib import Path
from PIL import Image
import e2
from model import HERE,CAL,ROOT,edge,np,material,params,SCALE
from score import guard

def tone_of(raw):
    rgb=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),float)/255
    y=edge.decode(rgb)@np.array([.2126,.7152,.0722])
    return float(edge.decode(edge.encode(y).mean()))

if __name__=='__main__':
    guard();native=e2.repaired.old.CanonicalNativeReader();decl=json.loads((HERE/'e2-declaration.json').read_text());spec=native.roles.spec
    cache={};census=[];tinted=[]
    # Declared cells are non-holdout; native backgrounds use the same role guard.
    for ref in decl['cells']:
        cell=ref['cell'];profile,sid=native.roles.admit(cell);scene=native.roles.scenes[sid];comp=spec['components'][scene['component']];scale=2 if '-2x-' in profile else 1;scheme='dark' if '-dark-' in profile else 'light';m=material(scheme)
        sizes=[x['size'] for x in comp['items']] if comp['kind']=='group' else [comp['size']]
        spans=[min(x) for x in sizes];key=(scene['background'],scale)
        if key not in cache:
            raw=native.read(cell,'background');cache[key]=(tone_of(raw),hashlib.sha256(raw).hexdigest())
        tone,sha=cache[key];ts=[]
        for span in spans:
            u=np.clip((span-m['sizeSpanMin'])/(m['sizeSpanMax']-m['sizeSpanMin']),0,1);k=u*u*(3-2*u);x=tone+m['backdropToneSizeBias']*k
            t=np.clip((x-m['backdropToneLow'])/(m['backdropToneHigh']-m['backdropToneLow']),0,1);ts.append(float(1-t*t*(3-2*t)))
        census.append(dict(cell=cell,spans=spans,sourceTone=tone,backgroundSha256=sha,T=ts,positive=any(t>0 for t in ts),evidence='active source-tone branch; host encoded-luminance-mean decoded, span law; no author-tint condition'))
    # Top equality is independent of the spatial body and tint, so no invented
    # native-to-hidden-layer inversion is needed for the canonical tint veto.
    baseline=json.loads(gzip.decompress((HERE/'e2-baseline.json.gz').read_bytes()))
    rows=baseline['rows'] if isinstance(baseline,dict) else baseline
    cmap={r['cell']:r for r in census}
    for r in rows:
        if '-tint-' not in r['cell']:continue
        rr=[]
        for b in r['bins']:
            if b.get('side') not in ['top','bottom'] or b.get('status')!='measured':continue
            rr.append(dict(**b,C1PredictedChangeRGB=[0,0,0],C1PredictedResidualRGB=b['residualRGB'],veto=False,basis='literal held-top identity; T=0; native reference read for baseline, actual G1a render not run'))
        assert not cmap[r['cell']]['positive']
        tinted.append(dict(cell=r['cell'],T=cmap[r['cell']]['T'],bins=rr,status='analytic held-top identity; absent side bins remain UNMEASURED',warning='No scalar native deep identifies spatial/tint hidden intermediate. Arc veto is not certified from this equality; archive arcs and G1a remain independent.'))
    edge.save(HERE/'collapse-census.json',dict(rows=census,positiveCells=[r['cell'] for r in census if r['positive']],meaning='No holdout read; does not assert unsampled or future near-black controls stay T=0.'))
    edge.save(HERE/'tinted-c1-top.json.gz',tinted)
    tables=[]
    # Expected metrics are explicitly NOT fabricated from a boundary-only model.
    baseline=json.loads(gzip.decompress((HERE/'stop-baseline.json.gz').read_bytes()))
    for r in baseline['rows']:
        key=r['key'];cell=key['profileKey']+'/'+key['sceneId'];inactive=r.get('state')=='inactive'
        tables.append(dict(cell=cell,renderer=key['web']['renderer'],capturePath=key['web']['capturePath'],C1='IDENTITY predicted for receded pixels; digests change' if inactive else 'UNIDENTIFIED actual-render stop values: requires G1a',C2='No nonidentity numerical stop prediction without selected feasible candidate and G1a',actualIfClose='All existing row numbers unchanged',M1='ring changes numerator and denominator',M2='2% against pre-W38; no mask change',L1='0.055 and growth0.005 vs W33; signed per-pixel change requires rendered spatial field',exterior='C1<=.0042 / X1=0 / B1 within5%; rim may touch fractional exterior up to .5 device pixel; not certified by inner cut')))
    edge.save(HERE/'stop-price.json.gz',tables)
    print('T census',len(census),'positive',sum(r['positive'] for r in census),'tinted',len(tinted),'top bins',sum(len(r['bins']) for r in tinted))
