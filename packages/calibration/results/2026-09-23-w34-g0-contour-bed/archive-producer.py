#!/usr/bin/env python3.12
"""Archive admitted W34 raw runs before plurality; disclose no holdout statistics."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
import archive
import instrument as I
from wave import default_wave,native_only


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='append',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();wave=default_wave();records=[]
    snapshots=[]
    for root in args.run:
        m=json.loads((root/'manifest.json').read_text())
        snapshots.append((root,{(p['profileKey'],f['sceneId']):f for p in m['profiles'] for f in p['fixtures']}))
    for root in args.run:
        admission=json.loads((root/'admission.json').read_text())
        if admission.get('admitted') is not True or admission.get('dry') is True:
            raise ValueError('producer input is not an admitted capture run')
        manifest=json.loads((root/'manifest.json').read_text());manifest_sha=sha(root/'manifest.json')
        entries={(p['profileKey'],f['sceneId']):f for p in manifest['profiles'] for f in p['fixtures']}
        cache={};alignments={}
        def pixels(profile,sid):
            key=(profile,sid)
            if key not in cache:
                if key in entries:
                    source_root,entry=root,entries[key]
                else:
                    # Sentinel-only runs use the matching ordinary run's
                    # no-glass/fill controls. Every dependency is archived, not
                    # assumed to be a generated raster or re-opened on replay.
                    choices=[(r,e[key]) for r,e in snapshots if key in e]
                    choices.sort(key=lambda pair:(pair[0].name!=root.name,str(pair[0])))
                    if not choices:raise ValueError('missing captured dependency '+str(key))
                    source_root,entry=choices[0]
                path=source_root/entry['file']
                cache[key]=(np.asarray(Image.open(path).convert('RGB'),dtype=np.uint8),sha(path))
            return cache[key]
        for (profile,sid),entry in entries.items():
            cell=profile+'/'+sid
            if cell not in wave.cells:raise ValueError('raw run has undeclared cell')
            scene=wave.scenes[sid];component=wave.spec['components'][scene['component']]
            if native_only(component):continue
            scale=1 if '-1x-' in profile else 2
            light=profile.replace('-dark-','-light-');pose=scene['state'];c=scene['component']
            rgb,native_sha=pixels(profile,sid)
            back,back_sha=pixels(light,f"{scene['background']}__none__{pose}")
            opaque,opaque_sha=pixels(light,f'grey-255__{c}-opaque-0__{pose}')
            inverse,inverse_sha=pixels(light,f'grey-0__{c}-opaque-255__{pose}')
            grey,grey_sha=pixels(profile,f'grey-128__{c}__{pose}')
            grey_back,grey_back_sha=pixels(light,f'grey-128__none__{pose}')
            geometry={**component,'suppliedPaths':entry['suppliedPaths']}
            akey=(profile,c)
            if akey not in alignments:alignments[akey]=I.fit_alignment(grey,grey_back,geometry,scale)
            protocol=manifest.get('captureProtocol') or {}
            arm='long' if protocol.get('initialSettleSeconds')==8 and protocol.get('orderSeed')==3401 else 'normal'
            payload=dict(rgb=rgb,background=back,opaque=opaque,opaqueInverse=inverse,
                alignmentImage=grey,alignmentBackground=grey_back,component=geometry,scale=scale,
                alignment=alignments[akey],backgroundKind=wave.spec['backgrounds'][scene['background']]['kind'])
            records.append(dict(cell=cell,run=str(root.resolve()),protocol=arm,admitted=True,payload=payload,
                inputHashes=dict(native=native_sha,noGlass=back_sha,opaque=opaque_sha,opaqueInverse=inverse_sha,
                    alignmentImage=grey_sha,alignmentBackground=grey_back_sha,manifest=manifest_sha)))
    result=archive.produce(records,wave,args.out)
    print(json.dumps(dict(admitted=True,inventory=str(args.out/'inventory.json'),
                         inventorySha256=sha(args.out/'inventory.json'),declaredCells=len({r['cell'] for r in records}))))


if __name__=='__main__':main()
