"""Offline W41 E3 preparation. No renderer, exposure or holdout-read command."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import scorer as s


def read(path):
    path=Path(path); raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def save(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    if path.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
    with path.open('xb') as f:f.write(raw)


def scope(kind):
    admitted,_=s.runner.admitted_scope(s.ROOT,s.wave)
    return [c for c in admitted[kind] if s.wave.roles[c.split('/',1)[1]]!='holdout']


def admission(cell,raw):
    disposition=s.disposition(cell)
    if disposition!='claimed uniform body':
        return dict(status=disposition,passes=None,score=raw)
    return raw['passes'] is True or (raw.get('reason')=='censored' and raw.get('constraintsPass') is True)


def source_inputs():
    """Explicit supplementary freeze inputs; runner also binds W39/G0 source trees."""
    paths=[s.HERE/'scorer.py',Path(__file__),s.HERE/'runtime.json',
           s.G1/'baseline/baseline.py',s.G1/'x6/observe.py',
           s.G1/'body/report-1/spatial-selection.json',
           s.G1/'exposure/runner.py',s.G1/'exposure/manifest.schema.json',
           s.G1/'exposure/body-e3-claim-scope.json',
           s.W39_BODY/'body.py',s.W39_BODY/'resolved-materials.json',
           s.W39_BODY/'resolved-materials.provenance.json',
           s.W39/'supplied-paths.json',s.wave.scenes_path,s.wave.split_path,
           s.G0/'bounds-declaration.txt',s.G0/'instrument/instrument.py',
           s.G0/'instrument/rendered.py',s.W39/'w39_readers.py',s.W39/'w39_archive.py',
           s.W39/'wave.py',s.W39/'replay-archive.py']
    paths += sorted(s.G1.glob('parent-ruling-*.json'))
    paths += sorted(s.HERE.glob('parent-ruling-*.json'))
    return {str(p.relative_to(s.ROOT)):s.sha(p) for p in paths}


def public(out):
    s.check_runtime()
    predictions=s.predictions()
    out=Path(out); out.mkdir(parents=True,exist_ok=False)
    save(out/'numerical.json',predictions)
    save(out/'parameters.json',dict(body=s.parameters(),
        shippedBaseline=str((s.HERE/'shipped-baseline.json').relative_to(s.ROOT)),
        parameterOrigin='unchanged body/report-1/spatial-selection.json light-inactive',
        otherEndpoints='identity: shipped H2, not a claim'))
    cells=predictions['cells']
    save(out/'provenance.json',dict(schema='w41-e3-public-predictions-1',
        sources=source_inputs(),runtime=read(s.HERE/'runtime.json'),nativePayloadReads=0,
        holdoutOpened=False,fitsPerformed=0,cells=len(cells),
        roles=dict(Counter(r['role'] for r in cells.values())),
        dispositions=dict(Counter(r['disposition'] for r in cells.values())),
        limitations=['Structured public raster local law is diagnostic only.',
                    'Shipped H2 describes uniform deep body, not boundary contributions.',
                    'No rendered PNG, calval survival or exposure result inferred.']))
    print('PUBLIC',len(cells),'native payloads 0')


def numerical_calval(predictions,out):
    s.check_runtime(); predictions_path=Path(predictions)
    predictions=read(predictions_path)['cells']
    expected=scope('numerical')
    if not set(expected)<=set(predictions):raise ValueError('numerical membership incomplete')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    rows={}
    for role in ('calibration','validation'):
        reader=s.native_reader(s.ARCHIVE,(role,))
        for cell in expected:
            if s.wave.roles[cell.split('/',1)[1]]!=role:continue
            native,states=s.payloads(reader,cell)
            rows[cell]=s.numerical(cell,predictions[cell],native,states)
    save(out/'scores.json.gz',rows)
    entries={c:admission(c,r) for c,r in rows.items()}
    save(out/'numerical-admission.json',entries)
    counts=Counter(s.disposition(c) for c in rows)
    failed=[c for c,r in entries.items() if r is False]
    save(out/'summary.json',dict(schema='w41-e3-calval-numerical-1',
        cells=len(rows),dispositions=dict(counts),claimedFailures=failed,
        predictedInputSha256=s.sha(predictions_path),sources=source_inputs(),
        archiveInventorySha256=s.INVENTORY_SHA,archive=str(s.ARCHIVE),
        rawRootDenied=str(Path.home()/'vitrea-w39'),roles=['calibration','validation'],
        fitsPerformed=0,holdoutOpened=False,renderedScored=False,
        note='Numerical admission only, not a composite survival document. Full raw scores retained.'))
    print('NUMERICAL CALVAL',len(rows),'claimed failures',len(failed))


def baseline_map(out, *, sources=None, root=None, candidate_dir=None, expected=None, projector=None):
    """Join frozen captures and preserve external shipped PNG bytes inside the candidate."""
    root=s.ROOT if root is None else Path(root)
    candidate_dir=s.HERE if candidate_dir is None else Path(candidate_dir)
    sources=(s.G1/'baseline/frozen-baseline.json',
             s.G1/'blind-baseline/frozen-blind-baseline.json') if sources is None else sources
    projector=s.project if projector is None else projector
    source={str(Path(p).relative_to(root)):s.sha(p) for p in sources}
    cells={}; payloads={}
    for path in sources:
        for cell,row in read(path)['captures'].items():
            if cell in cells:raise ValueError('overlapping shipped baseline cells')
            ref=Path(row['png']); png=root/ref
            data=png.read_bytes()
            digest=hashlib.sha256(data).hexdigest()
            if digest!=row['pngSha256']:raise ValueError('baseline PNG changed')
            projection=root/row['projection']
            if s.sha(projection)!=row['projectionSha256']:raise ValueError('baseline projection changed')
            if projector(cell,png)!=read(projection):raise ValueError('projection runtime differs')
            entry={k:row[k] for k in ('png','pngSha256','projection','projectionSha256')}
            if ref.is_absolute():
                snapshot=candidate_dir/'shipped-payloads'/f'{digest}.png'
                if digest in payloads and payloads[digest]!=data:
                    raise ValueError('baseline PNG hash collision')
                payloads[digest]=data
                entry['png']=str(snapshot.relative_to(root))
            cells[cell]=entry
    if expected is None:
        admitted,_=s.runner.admitted_scope(root,s.wave)
        expected=admitted['rendered']
    if set(cells)!=set(expected):raise ValueError('shipped baseline membership incomplete')
    for digest,data in payloads.items():
        snapshot=candidate_dir/'shipped-payloads'/f'{digest}.png'
        snapshot.parent.mkdir(parents=True,exist_ok=True)
        try:
            with snapshot.open('xb') as file:file.write(data)
        except FileExistsError:
            existing=snapshot.read_bytes()
            if existing!=data or hashlib.sha256(existing).hexdigest()!=digest:
                raise ValueError('shipped payload collision: '+str(snapshot))
    save(out,dict(cells=cells,source=source))


def render_calval(captures,baseline,out):
    """Offline scoring of supplied candidate PNGs, never creates or recaptures any."""
    s.check_runtime()
    capture_path=Path(captures);baseline_path=Path(baseline)
    captures=read(capture_path)['cells']; baselines=read(baseline_path)['cells']
    expected=scope('rendered')
    if not set(expected)<=set(captures) or not set(expected)<=set(baselines):
        raise ValueError('rendered candidate/baseline membership incomplete')
    # Validate every referenced PNG before constructing any native Reader.
    for cell in expected:
        for row in (captures[cell],baselines[cell]):
            if s.sha(s.ROOT/row['png'])!=row['pngSha256']:raise ValueError('PNG hash mismatch')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    rows={}
    for role in ('calibration','validation'):
        reader=s.native_reader(s.ARCHIVE,(role,))
        for cell in expected:
            if s.wave.roles[cell.split('/',1)[1]]!=role:continue
            native,states=s.payloads(reader,cell)
            rows[cell]=s.rendered_score(cell,s.ROOT/captures[cell]['png'],
                                       s.ROOT/baselines[cell]['png'],native,states)
    save(out/'scores.json.gz',rows)
    save(out/'rendered-admission.json',{c:admission(c,r) for c,r in rows.items()})
    save(out/'veto.json',{c:r['vetoPass'] for c,r in rows.items()})
    save(out/'summary.json',dict(schema='w41-e3-calval-rendered-1',cells=len(rows),
        claimedDeepFailures=[c for c,r in rows.items() if admission(c,r) is False],
        vetoFailures=[c for c,r in rows.items() if not r['vetoPass']],
        identityByteFailures=[c for c,r in rows.items() if s.disposition(c)=='not claimed (identity)'
                              and not r['identityBytesEqual']],
        captureMapSha256=s.sha(capture_path),baselineMapSha256=s.sha(baseline_path),
        sources=source_inputs(),archiveInventorySha256=s.INVENTORY_SHA,
        holdoutOpened=False,browsersLaunched=0,
        qualification='Full body/edge/deep veto scores, not exposure or freeze authorization.'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='operation',required=True)
    pub=sub.add_parser('public');pub.add_argument('out',type=Path)
    cal=sub.add_parser('numerical-calval');cal.add_argument('predictions',type=Path);cal.add_argument('out',type=Path)
    base=sub.add_parser('baseline-map');base.add_argument('out',type=Path)
    render=sub.add_parser('render-calval');render.add_argument('captures',type=Path)
    render.add_argument('baseline',type=Path);render.add_argument('out',type=Path)
    args=parser.parse_args()
    if args.operation=='public':public(args.out)
    elif args.operation=='numerical-calval':numerical_calval(args.predictions,args.out)
    elif args.operation=='baseline-map':baseline_map(args.out)
    else:render_calval(args.captures,args.baseline,args.out)


if __name__=='__main__':main()
