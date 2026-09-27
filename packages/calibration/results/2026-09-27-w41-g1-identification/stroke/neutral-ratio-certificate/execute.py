"""Build or independently replay a neutral two-bin ratio cut from SAVED crops.

No archive Reader, native capture, browser, optimizer, validation or holdout.
The raw and fetched-archive roots are denied by the unchanged inherited guard.
The saved bundles are decoded by the original d35b4cbf archive decoder.
"""
import argparse
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import numpy as np
import ratios

HERE=Path(__file__).resolve().parent
SAVED=HERE.parent/'m0-certificate/white-extension'
MANIFEST_SHA='cf536394ad212b87469b97e4b11ca34f0b5be1fe2d13bfdd3becb322d5d3b686'
BOOTSTRAP_SHA='752246375e44a046ebf5404d96e7411bfae508d0ba8f2226516d65459a1b8b19'
PROOF=Path('/Users/new/vitrea-w41/pre-w41-proof')
ENDPOINTS=('light-inactive','dark-inactive')
LEVELS=(40,56,72,88,104,128,150,255)
M2_QUOTE="M1's neutral is unchanged. If numerical roundoff puts luma outside [0,1], refuse."


def sha(raw):return hashlib.sha256(raw).hexdigest()

def write(path,data):
    raw=(json.dumps(data,indent=2,allow_nan=False)+'\n').encode()
    if path.suffix=='.gz':raw=gzip.compress(raw,mtime=0)
    with path.open('xb') as f:f.write(raw)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def boot(proof):
    raw=(SAVED/'manifest.json').read_bytes()
    if sha(raw)!=MANIFEST_SHA:raise ValueError('original saved manifest changed')
    manifest=json.loads(raw)
    bootstrap=HERE.parent/'m0-certificate/run.py'
    if sha(bootstrap.read_bytes())!=BOOTSTRAP_SHA:raise ValueError('original bootstrap changed')
    sys.path.insert(0,str(bootstrap.parent))
    spec=importlib.util.spec_from_file_location('m0_saved_bootstrap',bootstrap)
    m0=importlib.util.module_from_spec(spec);spec.loader.exec_module(m0)
    m,native,g0=m0.load(proof)
    for name,digest in manifest['sourceHashes'].items():
        if sha((proof/name).read_bytes())!=digest:raise ValueError('original proof source changed: '+name)
    guard_path=m.G0/'replay-archive.py'
    spec=importlib.util.spec_from_file_location('neutral_ratio_guard',guard_path)
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.deny(Path.home()/'vitrea-w39')
    guard.deny(Path(manifest['archiveRoot']))
    declaration=(g0/'bounds-declaration.txt').read_text()
    if M2_QUOTE not in declaration:raise ValueError('sealed M2 neutral identity missing')
    wave=native.wave.default_wave()
    expected={(ep,b) for ep in ENDPOINTS for b in LEVELS}
    actual={(r['endpoint'],r['b']) for r in manifest['records']}
    if actual!=expected or len(manifest['records'])!=16:raise ValueError('saved population differs')
    for record in manifest['records']:
        sid=record['cell'].split('/',1)[1]
        if record['role']!='calibration' or wave.roles[sid]!='calibration':
            raise PermissionError('only saved calibration cells are admitted')
        if record['sha256']!=record['archiveEntry']['sha256']:
            raise ValueError('saved bundle differs from admitted archive identity')
    return m,native,manifest,dict(bootstrapSha256=BOOTSTRAP_SHA,savedManifestSha256=MANIFEST_SHA,
        proofRevision=m0.PROOF_REV,declarationSha256=m0.DECLARATION_SHA,
        sourceHashes=dict(manifest['sourceHashes'],**{str(guard_path.relative_to(proof)):
            sha(guard_path.read_bytes())}),rawAndFetchedArchiveRootsDenied=True,
        sealedM2NeutralIdentity=M2_QUOTE)


def pixel_intervals(pixels,b,m):
    """Intersect necessary bin-mean intervals over all repeats and RGB channels.

    A channel containing any rail sample in any state is omitted in its entirety
    from this relaxation. No censored pixel is treated as a measured RGB target.
    All pixels remain saved; omitted channels cannot cause a negative result.
    """
    n=pixels.shape[1]
    if pixels.shape!=(7,n,3) or n<4:raise ValueError('seven population-admitted repeats required')
    if not np.all(pixels==pixels.astype(int)):raise ValueError('exact integer source pixels required')
    runmeans=[[F(int(run[:,ch].sum()),n) for ch in range(3)] for run in pixels]
    bars=[F(1,2)+(max(row[ch] for row in runmeans)-min(row[ch] for row in runmeans))/2
          for ch in range(3)]
    sealed=m.score_bin(np.full((n,3),b,float),pixels)
    if any(float(v)!=sealed['barRGB'][ch] for ch,v in enumerate(bars)):
        raise ValueError('exact bar disagrees with sealed scorer')
    targets=[np.median(pixels,axis=0),*pixels]
    rows=[]; omitted=[]
    for ch in range(3):
        if any(np.any((target[:,ch]<=5)|(target[:,ch]>=250)) for target in targets):
            omitted.append(dict(channel=ch,reason='rail-bearing channel; omitted from necessary cut',
                railPixelsMedianThenSeven=[int(((t[:,ch]<=5)|(t[:,ch]>=250)).sum()) for t in targets]))
            continue
        for state,target in enumerate(targets):
            mean=F(int(target[:,ch].sum()),n); bound=max(F(1),bars[ch])
            rows.append(dict(channel=ch,state=state,mean=str(mean),bar=str(bars[ch]),
                bound=str(bound),departure=[str(mean-b-bound),str(mean-b+bound)]))
    if not rows:
        return dict(status='OMITTED_NO_UNCENSORED_CHANNEL',departure=None,
                    rows=rows,omittedChannels=omitted,barRGB=list(map(str,bars)))
    low=max(F(r['departure'][0]) for r in rows); high=min(F(r['departure'][1]) for r in rows)
    return dict(status='NECESSARY_INTERVAL' if low<=high else 'EMPTY_WITHIN_BIN',
                departure=[str(low),str(high)],rows=rows,omittedChannels=omitted,
                barRGB=list(map(str,bars)))


def derive(records,m,native,scale=1,saved_root=SAVED):
    if scale not in (1,2):raise ValueError('undeclared scale')
    observations=[]; base=None; stored_geometry=None; population=None
    for record in sorted(records,key=lambda r:(r['endpoint'],r['b'])):
        path=(saved_root/record['file']).resolve()
        if (HERE.parent/'m0-certificate') not in path.parents and HERE not in path.parents:
            raise ValueError('saved payload escaped')
        raw=path.read_bytes()
        if sha(raw)!=record['sha256']:raise ValueError('saved bundle changed')
        runs,states=native.archive.unbundle(raw)
        runs=[r for r in runs if r['admitted'] and r['protocol']=='normal']
        if len(runs)!=7:raise ValueError('missing normal repeat')
        payloads=[native.archive.unpack(states[r['state']]) for r in runs]
        first=payloads[0];shape=m.readers.shapes_of(first['component'])
        if len(shape)!=1 or shape[0].opaque:raise ValueError('expected one non-opaque member')
        if first['pose']!='inactive' or first['scale']!=scale or first['scheme']+'-inactive'!=record['endpoint']:
            raise ValueError('wrong endpoint or scale')
        geo=m.readers.geometry(first['rgb'].shape[:2],shape,scale)
        bins,labels=m.readers.edge_bins(geo,0,inner_css=0,outer_css=4)
        required=[(i,b) for i,b in enumerate(bins) if b['shell'] is not None]
        keep=np.array([i for i,b in required if b['pixels']>=4])
        yy,xx=np.nonzero(np.isin(labels,keep));xy=np.c_[xx,yy];ids=labels[yy,xx]
        g=m.samples(shape[0],xy,scale,16)
        data=dict(xy=xy,binIds=ids,**g)
        if base is None:
            base=dict(shape=shape,component=first['component'],imageShape=first['rgb'].shape,
                      referenceShape=first['noGlass'].shape,bins=bins)
            stored_geometry=data
            population=[dict(index=i,**b) for i,b in required]
        if shape!=base['shape'] or first['component']!=base['component'] or bins!=base['bins']:
            raise ValueError('actual supplied geometry or required bins differ across inputs')
        if first['rgb'].shape!=base['imageShape'] or first['noGlass'].shape!=base['referenceShape']:
            raise ValueError('source frame differs across inputs')
        if any(not np.array_equal(data[k],stored_geometry[k]) for k in data):
            raise ValueError('pixel or per-subpixel geometry differs across inputs')
        allpixels=[]
        for p in payloads:
            if any(p[k]!=first[k] for k in ('component','pose','scheme','scale')):
                raise ValueError('actual geometry differs across seven repeats')
            if p['rgb'].shape!=base['imageShape'] or p['noGlass'].shape!=base['referenceShape']:
                raise ValueError('source frame differs across repeats')
            if not np.all(p['noGlass']==record['b']):raise ValueError('reference is not uniform neutral')
            allpixels.append(p['rgb'][yy,xx])
        references=m.bilinear(first['noGlass'],g['q'])
        if not np.all(references==record['b']):raise ValueError('per-subpixel reference differs')
        allpixels=np.asarray(allpixels)
        rows=[]
        for bi,binrow in required:
            if binrow['pixels']<4:
                rows.append(dict(index=bi,bin=binrow,status='UNMEASURED_POPULATION',pixelsRGB=None,
                                 constraints=None));continue
            pixels=allpixels[:,ids==bi]
            constraints=pixel_intervals(pixels,record['b'],m)
            rows.append(dict(index=bi,bin=binrow,status=constraints['status'],
                             pixelsRGB=pixels.tolist(),constraints=constraints))
        observations.append(dict(cell=record['cell'],endpoint=record['endpoint'],b=record['b'],
            stateMembership=[r['state'] for r in runs],geometry=first['component'],
            imageShape=list(first['rgb'].shape),referenceShape=list(first['noGlass'].shape),
            referenceUniformRGB=[record['b']]*3,sevenIdenticalReferences=True,
            suppliedGeometryAndQuadratureIdenticalAcrossLevels=True,bins=rows))
    return observations,stored_geometry,population


def screen(observations,population,both_orientations=False):
    outcomes={};screens={}
    for endpoint in ENDPOINTS:
        data={o['b']:o for o in observations if o['endpoint']==endpoint}
        admitted=[b['index'] for b in population if b['pixels']>=4]
        rows=[]; witnesses=[]
        pairs=itertools.permutations(admitted,2) if both_orientations else itertools.combinations(admitted,2)
        for a,b in pairs:
            entries=[]; omitted=[]
            for level,o in sorted(data.items()):
                bins={r['index']:r for r in o['bins']}
                ia=bins[a]['constraints'];ib=bins[b]['constraints']
                if ia['status']!='NECESSARY_INTERVAL' or ib['status']!='NECESSARY_INTERVAL':
                    omitted.append(dict(level=level,statuses=[ia['status'],ib['status']]))
                    continue
                entries.append(dict(level=level,numerator=ia['departure'],denominator=ib['departure']))
            proof=ratios.intersect_ratios(entries)
            row=dict(numeratorBin=a,denominatorBin=b,proof=proof,omittedBinLevels=omitted)
            rows.append(row)
            if proof['status']=='EXACT_EMPTY_INTERSECTION':witnesses.append(row)
        # A within-bin empty intersection is a different necessary obstruction;
        # report it, but this two-bin certificate never silently relabels it.
        empty_bins=[dict(level=o['b'],bin=r['index']) for o in data.values() for r in o['bins']
                    if r['status']=='EMPTY_WITHIN_BIN']
        status='CERTIFIED_INFEASIBLE_RELAXATION' if witnesses else 'NOT_DETERMINING'
        outcomes[endpoint]=dict(models={model:dict(status=status,geometryRivals=['device','css','curvature'])
                                      for model in ('M1','M2')},
            witnessPairs=len(witnesses),screenedPairs=len(rows),withinBinEmptiness=empty_bins,
            selectedWitness=witnesses[0] if witnesses else None,
            qualification='Per-endpoint two-bin necessary relaxation only; no positive survival '
                'from a nondetermining screen; no optimizer result or budget changed.')
        screens[endpoint]=rows
    return outcomes,screens


def produce(proof):
    m,native,manifest,provenance=boot(proof)
    observations,g,population=derive(manifest['records'],m,native)
    outcomes,screens=screen(observations,population)
    write(HERE/'observations.json.gz',observations)
    np.savez_compressed(HERE/'geometry.npz',**g)
    write(HERE/'population.json',population)
    write(HERE/'screens.json.gz',screens)
    write(HERE/'outcomes.json',outcomes)
    provenance.update(schema='w41-neutral-ratio-necessary-certificate-1',nativeArchiveReads=0,
        savedBundles=16,roles=['calibration'],requiredBinMinimum=4,
        artifactHashes={name:sha((HERE/name).read_bytes()) for name in
            ('observations.json.gz','geometry.npz','population.json','screens.json.gz','outcomes.json')},
        records=manifest['records'],
        proof='For either M1 or M2, arbitrary scalar neutral material S(b) gives mean(O_i)-b '
              '=c_i*(S(b)-b). Identical supplied path/bin/subpixel geometry and per-input '
              'uniform references make c_i fixed across levels. Each declared rival has '
              'nonnegative c_i. Jensen gives the recorded necessary mean-departure intervals '
              'at max(1,bar), never 1+bar. A denominator interval excluding zero rules out '
              'c_B=0. Thus r=c_A/c_B>=0 must belong to every admitted per-level ratio '
              'interval. Their exact empty intersection rejects only this model-endpoint. '
              'Censored channels and zero-containing denominators are omitted, relaxing '
              'rather than strengthening the cut. No monotonicity or material bounds are '
              'imposed, and no geometry/gauge coefficient is inferred or fitted.')
    write(HERE/'manifest.json',provenance)
    print(json.dumps(outcomes,indent=2))


def directed(proof):
    # Preserve the first unordered-pair pass. Rebuild observations from source
    # bundles, then check both ratio orientations so a zero-containing interval
    # in one bin can still be constrained with the other bin as denominator.
    m,native,manifest,provenance=boot(proof)
    observations,g,population=derive(manifest['records'],m,native)
    if observations!=read(HERE/'observations.json.gz'):raise ValueError('source observations changed')
    outcomes,screens=screen(observations,population,True)
    write(HERE/'directed-screens.json.gz',screens)
    write(HERE/'directed-outcomes.json',outcomes)
    write(HERE/'directed-manifest.json',dict(schema='w41-neutral-ratio-directed-supplement-1',
        originalManifestSha256=sha((HERE/'manifest.json').read_bytes()),
        bothOrientations=True,newArchiveReads=0,
        artifacts={name:sha((HERE/name).read_bytes()) for name in
                   ('directed-screens.json.gz','directed-outcomes.json')}))
    print(json.dumps(outcomes,indent=2))


def replay(proof):
    m,native,original,provenance=boot(proof)
    saved=read(HERE/'manifest.json')
    for key in provenance:
        if saved[key]!=provenance[key]:raise ValueError('proof provenance changed: '+key)
    if saved['records']!=original['records']:raise ValueError('saved cell inventory changed')
    for name,digest in saved['artifactHashes'].items():
        if sha((HERE/name).read_bytes())!=digest:raise ValueError('proof artifact changed: '+name)
    observations,g,population=derive(saved['records'],m,native)
    if observations!=read(HERE/'observations.json.gz'):raise ValueError('saved pixel intervals differ')
    if population!=read(HERE/'population.json'):raise ValueError('saved required-bin population differs')
    with np.load(HERE/'geometry.npz') as old:
        if set(old.files)!=set(g) or any(not np.array_equal(old[k],g[k]) for k in g):
            raise ValueError('saved subpixel geometry differs')
    outcomes,screens=screen(observations,population)
    if screens!=read(HERE/'screens.json.gz'):raise ValueError('exact ratio screen differs')
    if outcomes!=read(HERE/'outcomes.json'):raise ValueError('unsupported model-endpoint result')
    directed_path=HERE/'directed-manifest.json'
    if directed_path.exists():
        supplement=read(directed_path)
        if supplement['originalManifestSha256']!=sha((HERE/'manifest.json').read_bytes()):
            raise ValueError('directed supplement base changed')
        for name,digest in supplement['artifacts'].items():
            if sha((HERE/name).read_bytes())!=digest:raise ValueError('directed artifact changed')
        outcomes,screens=screen(observations,population,True)
        if screens!=read(HERE/'directed-screens.json.gz') or outcomes!=read(HERE/'directed-outcomes.json'):
            raise ValueError('directed screen not reproduced')
    return dict(savedEvidenceReconstructed=True,allExactRatioProofsRecomputed=True,
        nativeArchiveReads=0,optimizerCalls=0,sourceHashesVerified=len(saved['sourceHashes']),
        archiveAndRawDenied=True,savedBundlesVerified=16,
        endpoints={ep:dict(models=r['models'],witnessPairs=r['witnessPairs'],
                          screenedPairs=r['screenedPairs']) for ep,r in outcomes.items()},
        manifestSha256=sha((HERE/'manifest.json').read_bytes()))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('produce','directed','replay'))
    parser.add_argument('--proof',type=Path,default=PROOF)
    args=parser.parse_args()
    if args.mode=='produce':produce(args.proof)
    elif args.mode=='directed':directed(args.proof)
    else:print(json.dumps(replay(args.proof),indent=2))


if __name__=='__main__':main()
