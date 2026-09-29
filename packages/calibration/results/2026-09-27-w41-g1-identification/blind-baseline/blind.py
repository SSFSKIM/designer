"""Blind pre-W41 WEB predictions, charter v2.3; never a native holdout reader.

The public metadata supplies geometry and generated backdrops. These shipped
renders are identity witnesses for the unclaimed endpoints of a later candidate.
No authorization token is fabricated, no archive Reader is constructed, and the
production receipt remains untouched. Cal/val baseline ownership must be released
before a human coordinator invokes this capture command.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('w41_blind_baseline_helpers',HERE.parent/'baseline/baseline.py')
base=importlib.util.module_from_spec(spec);sys.modules[spec.name]=base;spec.loader.exec_module(base)
ROOT=base.ROOT
CAPTURES=Path('/Users/new/vitrea-w41/g1-captures/blind-baseline')


def cells():
    admitted,_=base.runner.admitted_scope(ROOT,base.wave)
    selected=sorted(c for c in admitted['rendered'] if base.wave.roles[c.split('/',1)[1]]=='holdout')
    if len(selected)!=64:raise ValueError('public admitted blind web scope changed')
    return selected


def check_descriptor(identity,cell,report,record):
    profile,sid=identity.split('/',1);documents=record['profiles'][profile]
    if (cell['sceneId']!=sid or cell['renderer']!='webgpu' or cell['engine']!='chromium'
            or cell['colorSpace']!='srgb' or cell['pixelSize']!=list(base.runner.dimension(base.wave,identity))
            or cell['deterministic'] is not True or cell['repeatNoise']!=0
            or report['fallback'] is not None or report['problems']):
        raise ValueError('invalid actual blind WebGPU descriptor: '+identity)
    for key,field in [('material','materialProfile'),('receded','recededProfile')]:
        if report[field]['sha256']!=record['documents'][documents[key]][:12]:
            raise ValueError('blind capture drew different shipped document')


def require_x6(check,path):
    base.save(path,check)
    if not check['verdict']['passes']:raise PermissionError('X6 refused; no browser launched')


def inputs(record):
    # Bind the public metadata too: the subprocess rereads scenes while the
    # projection uses the cached Wave. verify_preparation checks live bytes against
    # preparation at sealing and at every pre/post-process verify_seal call.
    return [Path(__file__),base.HERE/'preparation.json',base.authority_path(),
            base.HERE/'baseline.py',base.HERE.parent/'x6/observe.py',
            ROOT/record['backdrops']/'manifest.json',base.W39/'supplied-paths.json',
            base.wave.scenes_path,base.wave.split_path]


def seal():
    record=base.load(base.HERE/'preparation.json')
    base.verify_preparation(record);base.verify_authority(record)
    hashes={str(path.relative_to(ROOT)):base.runner.committed(ROOT,str(path.relative_to(ROOT)))
            for path in inputs(record)}
    base.save(HERE/'seal.json',dict(schema='w41-blind-shipped-1',sealedAt=base.stamp(),
              sourceRevision=record['sourceRevision'],cells=cells(),inputs=hashes,
              nativePayloadReads=0,claim='blind shipped web identity witness, not native evidence'))


def verify_seal(expected=None):
    if expected is not None and base.sha(HERE/'seal.json')!=expected:
        raise ValueError('blind seal changed during capture')
    base.runner.committed(ROOT,str((HERE/'seal.json').relative_to(ROOT)))
    sealed=base.load(HERE/'seal.json');record=base.load(base.HERE/'preparation.json')
    base.verify_preparation(record);base.verify_authority(record)
    if sealed['cells']!=cells():raise ValueError('blind membership changed')
    expected={str(path.relative_to(ROOT)) for path in inputs(record)}
    if set(sealed['inputs'])!=expected:raise ValueError('blind source inventory changed')
    for name,digest in sealed['inputs'].items():
        if base.sha(ROOT/name)!=digest:raise ValueError('blind input changed: '+name)
    return sealed,record


def snapshot(png):
    digest=base.sha(png);target=HERE/'capture-payloads'/(digest+'.png')
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if base.sha(target)!=digest:raise ValueError('content-addressed payload collision')
    else:
        with target.open('xb') as f:f.write(png.read_bytes())
    return str(target.relative_to(ROOT)),digest


def capture():
    sealed,record=verify_seal()
    # A completed committed536-cell baseline is the ownership/dependency frontier.
    frozen=base.load(base.HERE/'frozen-baseline.json')
    base.verify_frozen(record,frozen)
    if CAPTURES.exists():raise FileExistsError('blind capture destination already reserved')
    env={key:value for key,value in os.environ.items() if not key.startswith('VITREA_')}
    env.update(VITREA_SCENES=str(base.wave.scenes_path),VITREA_FIXTURES=str(ROOT/record['backdrops']),
               VITREA_WEB_CAPTURES=str(CAPTURES),VITREA_ALLOW_FALLBACK_ADAPTER='0')
    started=base.stamp();records={};seal_hash=base.sha(HERE/'seal.json')
    for profile,documents in sorted(record['profiles'].items()):
        verify_seal(seal_hash)
        definition=next(p for p in base.wave.spec['profiles'] if p['key']==profile)
        scale=int(re.search(r'-(1|2)x-',profile)[1])
        ids=[c.split('/',1)[1] for c in sealed['cells'] if c.startswith(profile+'/')]
        command=['pnpm','--dir',str(ROOT/'packages/calibration'),'exec','tsx','scripts/capture-web.ts',
                 *ids,'--renderer','webgpu','--color-scheme',definition['colorScheme'],'--scale',str(scale),
                 '--out',str(CAPTURES/profile),'--material-profile',str(ROOT/documents['material']),
                 '--receded-profile',str(ROOT/documents['receded'])]
        require_x6(base.x6.observe(),HERE.parent/'x6'/f'prelaunch-blind-{profile}-{uuid.uuid4().hex}.json')
        verify_seal(seal_hash)
        if not CAPTURES.exists():CAPTURES.mkdir(parents=True,exist_ok=False)
        base.save(HERE/f'command-{profile}.json',dict(at=base.stamp(),argv=command,
                  environment={k:v for k,v in env.items() if k.startswith('VITREA_')}))
        with (HERE/f'capture-{profile}.txt').open('x') as log:
            subprocess.run(command,env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
        verify_seal(seal_hash)
        for sid in ids:
            directory=CAPTURES/profile/sid;identity=profile+'/'+sid
            check_descriptor(identity,base.load(directory/'cell__webgpu.json'),
                             base.load(directory/'report__webgpu.json'),record)
            png=directory/(sid+'__webgpu.png')
            projection=HERE/'projections'/profile/(sid+'.json')
            base.save(projection,base.project(identity,png))
            payload,digest=snapshot(png)
            records[identity]=dict(png=payload,pngSha256=digest,primaryCapture=str(png),
                                   projection=str(projection.relative_to(ROOT)),projectionSha256=base.sha(projection),
                                   cellSha256=base.sha(directory/'cell__webgpu.json'),
                                   reportSha256=base.sha(directory/'report__webgpu.json'))
    verify_seal(seal_hash)
    if set(records)!=set(sealed['cells']):raise ValueError('incomplete blind web baseline')
    base.save(HERE/'frozen-blind-baseline.json',dict(schema='w41-blind-shipped-1',startedAt=started,
              frozenAt=base.stamp(),sealSha256=seal_hash,sourceRevision=sealed['sourceRevision'],
              captures=records,nativePayloadReads=0,exposureOpened=False))
    print('FROZEN BLIND WEB',len(records),base.sha(HERE/'frozen-blind-baseline.json'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['seal','capture']);args=parser.parse_args()
    {'seal':seal,'capture':capture}[args.operation]()

if __name__=='__main__':main()
