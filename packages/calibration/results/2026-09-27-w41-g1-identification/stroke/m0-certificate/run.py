"""Collect only 14 inactive neutral calibration crops, or replay SAVED evidence.

Replay never constructs an archive Reader: it verifies and decodes retained raw
bundles through the unchanged archive decoder, rebuilds supplied geometry/bins
and per-subpixel references, then checks all rational certificates without LPs.
Use --proof to point at the exact d35b4cbf source checkout if it moves.
"""
import argparse
import hashlib
import importlib
import json
from fractions import Fraction as F
from pathlib import Path
import subprocess
import sys
import numpy as np
import certificate as c

HERE=Path(__file__).resolve().parent
DATA=HERE
DECLARATION_SHA='850747c1f03781a6efe9b433bd4ce3bd6cf72b63c9befd8d5d98de9eadf7f759'
PROOF_REV='d35b4cbf43f1fcdda55063b3b8e0fa178d720a78'
LEVELS=(40,56,72,88,104,128,150)


def sha(raw): return hashlib.sha256(raw).hexdigest()

def write(path,obj):
    with path.open('x') as f: json.dump(obj,f,indent=2,allow_nan=False); f.write('\n')


def load(proof):
    if subprocess.check_output(['git','-C',str(proof),'rev-parse','HEAD'],text=True).strip()!=PROOF_REV:
        raise ValueError('proof tree revision changed')
    results=proof/'packages/calibration/results'
    g0=results/'2026-09-27-w41-g0-declaration'
    if sha((g0/'bounds-declaration.txt').read_bytes())!=DECLARATION_SHA:
        raise ValueError('sealed bounds changed')
    sys.path.insert(0,str(g0/'instrument'))
    m=importlib.import_module('instrument')
    shadow=importlib.import_module('shadow')
    mats=shadow.materials() # Original unchanged loader verifies all runtime/document pins.
    for endpoint in ('light-inactive','dark-inactive'):
        # All backdrop and span values have zero held occlusion, not just these inputs.
        s=mats[endpoint]['outerShadow']
        for leaf in ('thinOcclusionDark','thinOcclusionMid','thinOcclusionBright',
                     'thickOcclusionAt96','thickOcclusionAt128','thickOcclusionAt160',
                     'sizeGain','liftAmplitude'):
            if s[leaf]!=0: raise ValueError('inactive held shadow is not zero: '+leaf)
    sys.path.insert(0,str(m.G2))
    native=importlib.import_module('native')
    return m,native,g0


def source_hashes(proof,m,g0):
    paths={Path(module.__file__).resolve() for module in list(sys.modules.values())
           if getattr(module,'__file__',None) and proof in Path(module.__file__).resolve().parents}
    paths.update(g0/name for name in ('bounds-declaration.txt','pins.json','closure.json'))
    paths.update(m.G0/name for name in ('pins.json','split.json','supplied-paths.json'))
    paths.update([proof/'apps/reference-apple/scenes-w39-colour-edge.json',
                  m.G2/'instrument/resolved-materials.json',
                  m.G2/'instrument/resolved-materials.provenance.json'])
    side=json.loads((m.G2/'instrument/resolved-materials.provenance.json').read_text())
    paths.update(proof/row['path'] for key in ('sourceFiles','documents') for row in side[key])
    return {str(p.relative_to(proof)):sha(p.read_bytes()) for p in sorted(paths)}


def derive(records,m,native):
    """Reject non-identical actual supplied geometry or nonuniform references.

    Input LEVEL differs across neutral cells by design; after subtracting that
    level every reference subpixel is exactly the same zero field. Within each
    level every pixel and all seven reference repeats are bit-identical. No
    inferred phase, opaque registration, or named-scene geometry is substituted.
    """
    observations=[]; shared=None; common_g=None; common_xy=None
    for record in records:
        raw=(DATA/record['file']).read_bytes()
        if sha(raw)!=record['sha256']: raise ValueError('saved payload hash mismatch')
        runs,states=native.archive.unbundle(raw)
        runs=[r for r in runs if r['admitted'] and r['protocol']=='normal']
        if len(runs)!=7: raise ValueError('missing normal repeat')
        payloads=[native.archive.unpack(states[r['state']]) for r in runs]
        first=payloads[0]
        if first['pose']!='inactive' or first['scale']!=1: raise ValueError('wrong stratum')
        if first['scheme']+'-inactive'!=record['endpoint']: raise ValueError('endpoint mismatch')
        shapes=m.readers.shapes_of(first['component'])
        if len(shapes)!=1 or shapes[0].opaque: raise ValueError('requires one non-opaque member')
        if shared is None: shared=shapes
        if shapes!=shared: raise ValueError('supplied geometry differs across neutral inputs')
        geo=m.readers.geometry(first['rgb'].shape[:2],shapes,1)
        bins,labels=m.readers.edge_bins(geo,0,inner_css=0,outer_css=4)
        matches=[(i,b) for i,b in enumerate(bins)
                 if b['part']=='straight' and b['side']=='top' and b['shell']==0]
        if len(matches)!=1: raise ValueError('missing declared top exterior bin')
        bi,binrow=matches[0]; yy,xx=np.nonzero(labels==bi); xy=np.c_[xx,yy]
        if len(xy)<4: raise ValueError('population deficient')
        g=m.samples(shapes[0],xy,1,16)
        if common_g is None: common_g=g; common_xy=xy
        if not np.array_equal(common_xy,xy): raise ValueError('bin pixels differ')
        for key in g:
            if not np.array_equal(g[key],common_g[key]): raise ValueError('subpixel geometry differs')
        pixels=[]
        for p in payloads:
            if any(p[key]!=first[key] for key in ('component','pose','scheme','scale')):
                raise ValueError('geometry or endpoint differs across repeats')
            if p['rgb'].shape!=first['rgb'].shape: raise ValueError('frame differs')
            ref=p['noGlass']
            if not np.all(ref==record['b']): raise ValueError('reference not uniform declared neutral')
            subpixels=m.bilinear(ref,g['q'])
            if not np.all(subpixels==record['b']): raise ValueError('subpixel reference differs')
            pixels.append(p['rgb'][yy,xx])
        pixels=np.asarray(pixels)
        native_targets=[np.median(pixels,axis=0),*pixels]
        # This witness deliberately uses wholly uncensored bins. Mixed censoring
        # would require subset coverage, so it is refused, not averaged away.
        if np.any((pixels<=5)|(pixels>=250)): raise ValueError('witness has censored pixels')
        means=[[F(int(run[:,ch].sum()),len(xy)) for ch in range(3)] for run in pixels]
        bars=[F(1,2)+(max(row[ch] for row in means)-min(row[ch] for row in means))/2
              for ch in range(3)]
        sealed=m.score_bin(np.full((len(xy),3),record['b'],float),pixels)
        if any(float(bar)!=sealed['barRGB'][ch] for ch,bar in enumerate(bars)):
            raise ValueError('rational bar differs from sealed scorer')
        rows=[]
        for state,target in enumerate(native_targets):
            for ch in range(3):
                rows.append(dict(b=record['b'],mean=str(F(int(target[:,ch].sum()),len(xy))),
                                 bound=str(max(F(1),bars[ch])),state=state,channel=ch))
        observations.append(dict(cell=record['cell'],endpoint=record['endpoint'],b=record['b'],
            bin=binrow,xy=xy.tolist(),stateMembership=[r['state'] for r in runs],
            pixelsRGB=pixels.tolist(),barRGB=list(map(str,bars)),constraints=rows,
            geometry=first['component'],referenceShape=list(first['noGlass'].shape),
            referenceUniformRGB=[record['b']]*3,allSevenReferencesIdentical=True,
            allGeometryAndBinSubpixelsIdenticalAcrossNeutralInputs=True))
    return observations,common_g


def collect(proof,m,native,g0,include_white=False,reuse=False):
    root=Path((HERE.parent.parent/'archive-root.txt').read_text().strip()).resolve()
    if (Path.home()/'.cache/vitrea-archives') not in root.parents:
        raise ValueError('only fetched archive cache authorized')
    wave,reader=native.guarded(root,('calibration',))
    if reader.generation!=json.loads((g0/'pins.json').read_text())['archive']['inventorySha256']:
        raise ValueError('archive generation changed')
    allowed={f'neutral-{b}-colour__inactive':b for b in LEVELS}
    if include_white: allowed['g255-c-c44__inactive']=255
    records=[]; (DATA/'saved').mkdir(exist_ok=False)
    previous=json.loads((HERE/'manifest.json').read_text())['records'] if reuse else []
    prior={r['cell']:r for r in previous}
    opened=0
    for (cell,kind),entry in sorted(reader.entries.items()):
        profile,sid=cell.split('/',1)
        if kind!='crop' or sid not in allowed or '-1x-' not in profile: continue
        if sid not in reader.allowed or not entry['admitted']: raise ValueError('unadmitted cell')
        if cell in prior:
            record=dict(prior[cell]); record['file']='../'+record['file']
            if record['sha256']!=entry['sha256']: raise ValueError('reused payload differs')
            records.append(record); continue
        raw=reader.read(cell,'crop'); opened+=1
        endpoint=('dark' if '-dark-' in profile else 'light')+'-inactive'
        file=f'saved/{endpoint}-{allowed[sid]}.bundle'
        with (DATA/file).open('xb') as f:f.write(raw)
        records.append(dict(cell=cell,endpoint=endpoint,b=allowed[sid],role='calibration',
                            file=file,sha256=sha(raw),archiveEntry=entry))
    if len(records)!=2*len(allowed): raise ValueError('missing neutral calibration cells')
    observations,g=derive(records,m,native)
    write(DATA/'observations.json',observations)
    np.savez_compressed(DATA/'geometry.npz',**g)
    outcomes={}
    for endpoint in ('light-inactive','dark-inactive'):
        rows=[row for o in observations if o['endpoint']==endpoint for row in o['constraints']]
        outcomes[endpoint]=c.solve(rows)
        outcomes[endpoint]['geometryRivals']=['device','css','curvature']
        outcomes[endpoint]['binsUsed']=f'1x member0 straight top exterior shell0; {len(allowed)} neutral cells'
        outcomes[endpoint]['bounds']=sorted({row['bound'] for row in rows})
        print(endpoint,outcomes[endpoint]['status'],flush=True)
    write(DATA/'certificates.json',outcomes)
    manifest=dict(schema='w41-m0-neutral-necessary-cut-1',proofRevision=PROOF_REV,
        declarationSha256=DECLARATION_SHA,archiveGeneration=reader.generation,
        archiveRoot=str(root),roles=['calibration'],nativeCellsInEvidence=len(records),
        newNativeCellsRead=opened,reusedSavedCells=len(records)-opened,
        records=records,sourceHashes=source_hashes(proof,m,g0),
        artifacts={name:sha((DATA/name).read_bytes()) for name in
                   ('observations.json','geometry.npz','certificates.json')},
        proof='For any accepted sealed G+M0 solution, common bin-mean c maps to '
              '(c,c*t,c*k). Every sample is uniform b; geometry and bin pixels are '
              'identical. Mean coverage in [0,1] exists for each geometry rival. '
              'Jensen maps every sealed MAE<=max(1,bar) to these necessary mean '
              'intervals, including median and every repeat. Ordered regimes '
              'exhaust t>=0 clipping. Exact Farkas rejection in every regime '
              'therefore rejects only this model-endpoint, never M1 or M2.',
        continuation='Fits were not stopped or changed by this worker; parent owns determination.')
    write(DATA/'manifest.json',manifest)


def replay(proof,m,native):
    manifest=json.loads((DATA/'manifest.json').read_text())
    for name,digest in manifest['sourceHashes'].items():
        if sha((proof/name).read_bytes())!=digest: raise ValueError('proof source changed: '+name)
    for name,digest in manifest['artifacts'].items():
        if sha((DATA/name).read_bytes())!=digest: raise ValueError('saved artifact changed: '+name)
    observations,g=derive(manifest['records'],m,native)
    if observations!=json.loads((DATA/'observations.json').read_text()):
        raise ValueError('saved pixel/bin derivation changed')
    with np.load(DATA/'geometry.npz') as saved:
        if set(saved.files)!=set(g) or any(not np.array_equal(saved[k],g[k]) for k in g):
            raise ValueError('saved quadrature changed')
    outcomes=json.loads((DATA/'certificates.json').read_text())
    verified={}
    for endpoint,result in outcomes.items():
        rows=[r for o in observations if o['endpoint']==endpoint for r in o['constraints']]
        expected=c.regimes(len({F(row['b']) for row in rows}))
        if [r['regime'] for r in result['regimes']]!=expected: raise ValueError('clip regimes missing')
        count=0; weighted=[]
        for item in result['regimes']:
            if item['status']=='EXACT_INFEASIBLE':
                a,rhs,labels=c.constraints(rows,item['regime']); cert=item['certificate']
                if not c.verify(cert,a,rhs): raise ValueError('invalid exact certificate')
                wr=sum(F(w)*rhs[i] for i,w in zip(cert['indices'],cert['weights']))
                if str(wr)!=cert['weightedRhs'] or [labels[i] for i in cert['indices']]!=cert['labels']:
                    raise ValueError('certificate annotations changed')
                weighted.append(float(wr));count+=1
        rejected=count==len(expected)
        if rejected!=(result['status']=='CERTIFIED_INFEASIBLE_RELAXATION'):
            raise ValueError('unsupported endpoint determination')
        verified[endpoint]=dict(exactRegimes=count,totalRegimes=len(expected),
            rejectedM0=rejected,geometryRivals=result['geometryRivals'],
            weightedRhsRange=[min(weighted),max(weighted)] if weighted else None)
    return dict(savedReplay=True,archivePayloadReads=0,LPCalls=0,sourceHashesVerified=len(manifest['sourceHashes']),
                bundlesVerified=len(manifest['records']),geometryRecomputed=True,perPixelEvidenceRecomputed=True,
                endpoints=verified,manifestSha256=sha((DATA/'manifest.json').read_bytes()))


def main():
    global DATA
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('collect','replay'))
    parser.add_argument('--proof',type=Path,default=Path('/Users/new/vitrea-w41/pre-w41-proof'))
    parser.add_argument('--white-extension',action='store_true')
    args=parser.parse_args()
    if args.white_extension:
        DATA=HERE/'white-extension'
        DATA.mkdir(exist_ok=True)
    m,native,g0=load(args.proof)
    if args.mode=='collect': collect(args.proof,m,native,g0,args.white_extension,args.white_extension)
    else: print(json.dumps(replay(args.proof,m,native),indent=2))


if __name__=='__main__':main()
