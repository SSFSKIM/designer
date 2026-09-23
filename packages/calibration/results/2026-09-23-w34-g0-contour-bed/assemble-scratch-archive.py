#!/usr/bin/env python3.12
"""Archive all 42 planned repeat observations, including sentinel losing states."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
import archive
import instrument as I
from wave import Wave

HERE=Path(__file__).resolve().parent;SCRATCH=Path.home()/'vitrea-w34/scratch'

def image(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.uint8)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    records=[];scenes={};components={};profiles={};raw_results={};alignment_replays=[]
    for series,scale in [('phase-1x',1),('phase-2x',2),('sentinel-normal',2),('sentinel-long',2)]:
        controls=SCRATCH/f'controls-{scale}x/run-1';key=f'apple-macos-27.0-{scale}x-light-standard-glass0.5'
        for n in [1,2,3]:
            root=SCRATCH/series/f'run-{n}';spec=json.loads((root/'scenes.json').read_text())
            manifest=json.loads((root/'manifest.json').read_text());admission=json.loads((root/'admission.json').read_text())
            for f in manifest['profiles'][0]['fixtures']:
                original=next(s for s in spec['scenes'] if s['id']==f['sceneId'])
                sid=(f'phase-{scale}x-' if series.startswith('phase') else 'sentinel-')+original['id']
                cell=key+'/'+sid;b=original['background'];comp={**spec['components'][original['component']],'suppliedPaths':f['suppliedPaths']}
                source=root/key/(original['id']+'.png')
                no_glass=(SCRATCH/'checker-reference/run-1'/key/'checkerboard__none__rest.png'
                          if b=='checkerboard' else controls/key/f'{b}__none__rest.png')
                opaque=controls/key/'white__opaque-black__rest.png';inverse=controls/key/'black__opaque-white__rest.png'
                rgb,back=image(source),image(no_glass)
                alignment_image=rgb if b=='grey' else image(controls/key/'grey__circular__rest.png')
                alignment_background=back if b=='grey' else image(controls/key/'grey__none__rest.png')
                alignment=I.fit_alignment(alignment_image,alignment_background,comp,scale)
                payload=dict(rgb=rgb,background=back,opaque=image(opaque),opaqueInverse=image(inverse),
                    alignmentImage=alignment_image,alignmentBackground=alignment_background,
                    component=comp,scale=scale,alignment=alignment,backgroundKind=spec['backgrounds'][b]['kind'])
                decoded=I.unpack(I.pack(payload))
                replayed=I.fit_alignment(decoded['alignmentImage'],decoded['alignmentBackground'],decoded['component'],scale)
                if replayed!=alignment:raise ValueError('alignment estimator does not replay')
                alignment_replays.append(dict(cell=cell,run=f'{series}-{n}',identical=True))
                records.append(dict(cell=cell,run=f'{series}-{n}',protocol='long' if series=='sentinel-long' else 'normal',
                    admitted=admission['admitted'],payload=payload,
                    inputHashes={'native':sha(source),'noGlass':sha(no_glass),'opaque':sha(opaque),'opaqueInverse':sha(inverse),
                                 'manifest':sha(root/'manifest.json'),'sceneDeclaration':sha(root/'scenes.json')}))
                scenes[sid]={'id':sid,'component':sid};components[sid]=spec['components'][original['component']]
                profiles.setdefault(key,set()).add(sid)
    declaration=HERE/'scratch-archive-declaration';declaration.mkdir(exist_ok=True)
    doc={'components':components,'scenes':list(scenes.values()),
         'profiles':[{'key':k,'scenes':sorted(ids)} for k,ids in profiles.items()],
         'split':{'calibration':[],'validation':[],'holdout':[],'probe':sorted(scenes)}}
    write(declaration/'scenes.json',doc);write(declaration/'split.json',{'calibration':sorted(scenes),'validation':[],'holdout':[]})
    write(declaration/'pins.json',{'scenesSha256':sha(declaration/'scenes.json'),'splitSha256':sha(declaration/'split.json')})
    wave=Wave(declaration/'scenes.json',declaration/'split.json',declaration/'pins.json')
    archive.produce(records,wave,HERE/'scratch-repeat-archive')
    reader=wave.reader(HERE/'scratch-repeat-archive')
    proof=[archive.replay(reader,cell) for cell in sorted(wave.cells)]
    bars=[archive.repeat_bar(reader,cell,protocol) for cell in sorted(wave.cells)
          for protocol in sorted({r['protocol'] for r in records if r['cell']==cell})]
    write(HERE/'archive-replay.json',dict(rawObservations=len(records),cells=len(wave.cells),
        rawVsArchive=proof,alignmentEstimatorReplay=alignment_replays,
        noRawFilesNeededAfterProduction=True,scope='All planned phase and settle-sentinel repeat observations; dependencies are full-canvas lossless crops.'))
    write(HERE/'scratch-bars.json',dict(estimator='all admitted runs before plurality; protocols separate',cells=bars))
    print('archived',len(records),'observations;',len(proof),'cell replays identical')
    print('distinct states by cell/arm',[(r['cell'],r['runs'],r.get('distinctStates')) for r in bars])


if __name__=='__main__':main()
