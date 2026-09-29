"""Bounded 2x extension: same eight calibration levels, never pooled with 1x.

Collection alone uses the inherited guarded calibration Reader. Thereafter the
independent saved-evidence replay denies both the raw and fetched archive roots.
No extension beyond this scale is implicit in a nondetermining result.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import execute as e

OUT=e.HERE/'scale2'


def collect(proof):
    # Do not call saved-replay boot: it denies the archive by design. This is
    # the separately authorized bounded calibration collection, not a replay.
    manifest=e.read(e.SAVED/'manifest.json')
    if e.sha((e.SAVED/'manifest.json').read_bytes())!=e.MANIFEST_SHA:
        raise ValueError('original saved manifest changed')
    path=e.HERE.parent/'m0-certificate/run.py'
    if e.sha(path.read_bytes())!=e.BOOTSTRAP_SHA:raise ValueError('original bootstrap changed')
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location('m0_scale2_bootstrap',path)
    m0=importlib.util.module_from_spec(spec);spec.loader.exec_module(m0)
    m,native,g0=m0.load(proof)
    for name,digest in manifest['sourceHashes'].items():
        if e.sha((proof/name).read_bytes())!=digest:raise ValueError('original source changed')
    root=Path((e.HERE.parent.parent/'archive-root.txt').read_text().strip()).resolve()
    if (Path.home()/'.cache/vitrea-archives') not in root.parents or str(root)!=manifest['archiveRoot']:
        raise ValueError('requires the same fetched archive')
    wave,reader=native.guarded(root,('calibration',))
    if reader.generation!=manifest['archiveGeneration']:raise ValueError('archive generation changed')
    allowed={f'neutral-{b}-colour__inactive':b for b in e.LEVELS if b!=255}
    allowed['g255-c-c44__inactive']=255
    records=[];OUT.mkdir(exist_ok=False);(OUT/'saved').mkdir()
    for (cell,kind),entry in sorted(reader.entries.items()):
        profile,sid=cell.split('/',1)
        if kind!='crop' or sid not in allowed or '-2x-' not in profile:continue
        if sid not in reader.allowed or not entry['admitted']:raise ValueError('unadmitted 2x cell')
        raw=reader.read(cell,'crop')
        endpoint=('dark' if '-dark-' in profile else 'light')+'-inactive'
        name=f'saved/{endpoint}-{allowed[sid]}.bundle'
        with (OUT/name).open('xb') as f:f.write(raw)
        records.append(dict(cell=cell,endpoint=endpoint,b=allowed[sid],role='calibration',
                            file=name,sha256=e.sha(raw),archiveEntry=entry))
    if len(records)!=16:raise ValueError('missing 2x cell')
    observations,g,population=e.derive(records,m,native,2,OUT)
    outcomes,screens=e.screen(observations,population,True)
    e.write(OUT/'observations.json.gz',observations)
    np.savez_compressed(OUT/'geometry.npz',**g)
    e.write(OUT/'population.json',population)
    e.write(OUT/'screens.json.gz',screens)
    e.write(OUT/'outcomes.json',outcomes)
    guard=m.G0/'replay-archive.py'
    e.write(OUT/'manifest.json',dict(schema='w41-neutral-ratio-2x-extension-1',scale=2,
        originalOneScaleManifestSha256=e.sha((e.HERE/'manifest.json').read_bytes()),
        originalSavedManifestSha256=e.MANIFEST_SHA,proofRevision=m0.PROOF_REV,
        declarationSha256=m0.DECLARATION_SHA,archiveRoot=str(root),archiveGeneration=reader.generation,
        newNativeArchiveReads=16,roles=['calibration'],records=records,
        sourceHashes=dict(manifest['sourceHashes'],**{str(guard.relative_to(proof)):e.sha(guard.read_bytes())}),
        artifacts={name:e.sha((OUT/name).read_bytes()) for name in
                   ('observations.json.gz','geometry.npz','population.json','screens.json.gz','outcomes.json')},
        termination='Both scales remain separate. Nondetermining stops this helper; no new levels, '
                    'validation or holdout reads, or altered fits follow.'))
    print(json.dumps(outcomes,indent=2))


def replay(proof):
    m,native,_,base=e.boot(proof) # Inherited guard denies raw AND fetched archive.
    manifest=e.read(OUT/'manifest.json')
    if manifest['sourceHashes']!=base['sourceHashes']:raise ValueError('proof sources differ')
    if manifest['originalOneScaleManifestSha256']!=e.sha((e.HERE/'manifest.json').read_bytes()):
        raise ValueError('initial 1x evidence changed')
    wave=native.wave.default_wave()
    if {(r['endpoint'],r['b']) for r in manifest['records']}!={(ep,b) for ep in e.ENDPOINTS for b in e.LEVELS}:
        raise ValueError('2x cell membership differs')
    for record in manifest['records']:
        if record['role']!='calibration' or wave.roles[record['cell'].split('/',1)[1]]!='calibration':
            raise PermissionError('only saved calibration cells admitted')
        if record['sha256']!=record['archiveEntry']['sha256']:raise ValueError('original payload identity differs')
    for name,digest in manifest['artifacts'].items():
        if e.sha((OUT/name).read_bytes())!=digest:raise ValueError('2x artifact differs')
    observations,g,population=e.derive(manifest['records'],m,native,2,OUT)
    if observations!=e.read(OUT/'observations.json.gz') or population!=e.read(OUT/'population.json'):
        raise ValueError('2x pixels or bins differ')
    with np.load(OUT/'geometry.npz') as old:
        if set(old.files)!=set(g) or any(not np.array_equal(old[k],g[k]) for k in g):
            raise ValueError('2x subpixel geometry differs')
    outcomes,screens=e.screen(observations,population,True)
    if screens!=e.read(OUT/'screens.json.gz') or outcomes!=e.read(OUT/'outcomes.json'):
        raise ValueError('2x exact ratio outcome differs')
    return dict(scale=2,savedEvidenceReconstructed=True,exactRatioProofsRecomputed=True,
        nativeArchiveReads=0,optimizerCalls=0,rawAndArchiveDenied=True,
        sourceHashesVerified=len(manifest['sourceHashes']),savedBundlesVerified=len(manifest['records']),
        endpoints={ep:dict(models=r['models'],witnessPairs=r['witnessPairs'],
                          screenedPairs=r['screenedPairs']) for ep,r in outcomes.items()},
        manifestSha256=e.sha((OUT/'manifest.json').read_bytes()))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('collect','replay'))
    parser.add_argument('--proof',type=Path,default=e.PROOF)
    args=parser.parse_args()
    if args.mode=='collect':collect(args.proof)
    else:print(json.dumps(replay(args.proof),indent=2))


if __name__=='__main__':main()
