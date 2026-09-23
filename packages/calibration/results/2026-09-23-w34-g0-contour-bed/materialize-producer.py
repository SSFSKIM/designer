#!/usr/bin/env python3
"""Materialise all four seven-run passes after their repeat archive exists.

Native rows and pixels are partitioned by identification role before the output
is exposed. Materialize's state/frequency diagnostics go to holdout/producer-logs,
never to G1 reporting. The canonical material holdout recorder is untouched.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from wave import default_wave
from sitting import PASS, validate_manifest

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def partition(source,target,wave):
    source,target=Path(source),Path(target)
    if target.exists():raise ValueError('refuse to overwrite published evidence')
    manifest=json.loads((source/'manifest.json').read_text())
    cells=[p['profileKey']+'/'+f['sceneId'] for p in manifest['profiles'] for f in p['fixtures']]
    if set(cells)!=wave.cells or len(cells)!=len(wave.cells):
        raise ValueError('published membership must cover the complete declared bed exactly once')
    target.mkdir(parents=True)
    public=copy.deepcopy(manifest)
    # Run-level plurality summaries include holdout state diagnostics too.
    for key in ['bedProvenance','caveats']:public.pop(key,None)
    inventory=[]
    if (source/'backgrounds').exists():shutil.copytree(source/'backgrounds',target/'backgrounds')
    for profile in public['profiles']:
        profile.pop('caveats',None)
        fixtures=[]
        for entry in profile['fixtures']:
            sid=entry['sceneId'];cell=profile['profileKey']+'/'+sid
            if cell not in wave.cells:raise ValueError('publication contains undeclared cell')
            role=wave.roles[sid];base=Path(role)/profile['profileKey'];(target/base).mkdir(parents=True,exist_ok=True)
            image=base/(sid+'.png');meta=base/(sid+'.metadata.json')
            shutil.copyfile(source/entry['file'],target/image)
            (target/meta).write_text(json.dumps(entry,indent=2)+'\n')
            for kind,path in [('png',image),('statistics',meta)]:
                inventory.append(dict(cell=cell,kind=kind,path=str(path),sha256=digest(target/path),admitted=True))
            if role=='holdout':
                # Inventory and admission only; original channel/settle/state
                # readings stay in the guarded metadata payload.
                allowed=['sceneId','fixtureSet','captureMethod','materialRendered','width','height',
                         'presentedActive','presentation','deterministic']
                entry={k:entry[k] for k in allowed if k in entry}
            entry['file']=str(image);fixtures.append(entry)
        profile['fixtures']=fixtures
    (target/'manifest.json').write_text(json.dumps(public,indent=2)+'\n')
    (target/'inventory.json').write_text(json.dumps(dict(schema=1,entries=inventory,
        scenesSha256=wave.scenes_sha,splitSha256=wave.split_sha),indent=2)+'\n')
    (target/'holdout').mkdir(exist_ok=True)
    (target/'holdout/full-materializer-manifest.json').write_bytes((source/'manifest.json').read_bytes())
    if (source/'producer-logs').exists():shutil.copytree(source/'producer-logs',target/'holdout/producer-logs')
    return dict(admitted=True,cells=len(inventory)//2,inventorySha256=digest(target/'inventory.json'))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--pass',dest='passes',action='append',required=True)
    ap.add_argument('--archive-inventory',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();wave=default_wave()
    if args.out.exists():raise ValueError('output already exists')
    if ROOT/'apps/reference-apple/fixtures' in args.out.resolve().parents:raise ValueError('canonical fixtures forbidden')
    passes=dict(x.split('=',1) for x in args.passes)
    if set(passes)!={'active-1x','inactive-1x','active-2x','inactive-2x'}:raise ValueError('all four declared passes required')
    evidence=json.loads(args.archive_inventory.read_text())
    if evidence.get('scenesSha256')!=wave.scenes_sha or evidence.get('splitSha256')!=wave.split_sha:
        raise ValueError('repeat archive does not identify this declaration')
    runs={name:[Path(root)/f'run-{n}' for n in range(1,8)] for name,root in passes.items()}
    for name,paths in runs.items():
        pose,scale_token=name.split('-');scale=int(scale_token[0])
        declaration=PASS.derive(pose,scale)
        expected={(p['key'],sid) for p in declaration['profiles'] for sid in p['scenes']}
        expected_sha=hashlib.sha256((json.dumps(declaration,indent=2)+'\n').encode()).hexdigest()
        for root in paths:
            admission=json.loads((root/'admission.json').read_text())
            if admission.get('admitted') is not True or admission.get('dry') is True:raise ValueError('unadmitted run')
            if digest(root/'manifest.json') not in evidence.get('sourceManifests',[]):raise ValueError('run missing from pre-plurality archive')
            validate_manifest(json.loads((root/'manifest.json').read_text()),expected,pose,scale)
            fields=dict(line.split('=',1) for line in (root/'attest.read').read_text().splitlines() if '=' in line)
            if fields.get('passSpecSha256')!=expected_sha:raise ValueError('run declaration does not match the named pass')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='w34-materialize-',dir=args.out.parent) as tmp:
        stage=Path(tmp);(stage/'backgrounds').mkdir();(stage/'producer-logs').mkdir()
        first=json.loads(next(iter(runs.values()))[0].joinpath('manifest.json').read_text())
        first['profiles']=[];first['backgrounds']={};first.pop('bedProvenance',None)
        (stage/'manifest.json').write_text(json.dumps(first))
        for name,paths in runs.items():
            command=['pnpm','--dir',str(ROOT),'--filter','@vitrea/calibration','exec','tsx','cli/materialize.ts',
                     '--set','probe','--frequency-settle','--apply']
            for n,root in enumerate(paths,1):command+=['--run',f'run-{n}={root.resolve()}']
            env={**os.environ,'VITREA_SCENES':str(wave.scenes_path),'VITREA_FIXTURES':str(stage)}
            with (stage/'producer-logs'/f'{name}.txt').open('w') as f:
                result=subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT)
            if result.returncode:
                # Preserve failed diagnostics privately; do not dump their state
                # values into a pre-holdout report or discard them with tempdir.
                failed=args.out.with_name(args.out.name+'-FAILED')/'holdout/producer-logs'
                shutil.copytree(stage/'producer-logs',failed)
                raise SystemExit('Publication refused; diagnostics retained behind holdout boundary')
        print(json.dumps(partition(stage,args.out,wave)))


if __name__=='__main__':main()
