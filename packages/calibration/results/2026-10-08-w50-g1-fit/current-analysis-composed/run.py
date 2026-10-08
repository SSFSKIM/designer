#!/usr/bin/env python3
"""Prospective schema2 analytical bootstrap, never a capture/composition authority.

The explicit composition is authored only after both actual instruments complete. This
bootstrap binds that descriptor, original native/G0 inputs and a synthetic source closure.
A later read requires the externally registered analysis-root hash and writes its fixed
result once. No config, composition, root, result or permission is created on import.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import types

HERE=Path(__file__).resolve().parent
FIT=HERE.parent
REPO=HERE.parents[4]
G0=FIT.parent/'2026-10-08-w50-g0-declaration'
GUARD=G0/'audit/closure.py'
CONFIG=HERE/'read-config.json'
INSTRUMENT=HERE/'instrument-root.json'
PROBE=HERE/'probe.py'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    def invalid(value):raise ValueError('Nonfinite JSON: '+value)
    return json.loads(Path(path).read_bytes(),parse_constant=invalid)


def ordinary(path):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Only ordinary absolute paths without symlinks are admitted')
    return path


def pin_shape(item):
    if not isinstance(item,dict) or set(item)!={'path','sha256'} or not isinstance(item['path'],str) \
            or not re.fullmatch('[0-9a-f]{64}',item.get('sha256','')):
        raise ValueError('Missing exact content pin')


def checked(repo,item):
    pin_shape(item);relative=Path(item['path'])
    if relative.is_absolute() or '..' in relative.parts:raise ValueError('Repository pin escaped its root')
    path=ordinary(Path(repo)/relative)
    if not path.is_file() or sha(path)!=item['sha256']:raise ValueError('Changed or missing pinned input/source')
    return path


def pin(repo,path):return {'path':str(Path(path).relative_to(repo)),'sha256':sha(path)}


def sidecar(path):
    path=ordinary(path);side=ordinary(Path(str(path)+'.sha256'))
    if side.read_text()!=f'{sha(path)}  {path.name}\n':raise ValueError('Changed prospective source/root sidecar')
    return side


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


def write_once(path,value):
    raw=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    with ordinary(path).open('xb') as handle:
        handle.write(raw);handle.flush();os.fsync(handle.fileno())


def composition_metadata(repo,composition_pin):
    """Source metadata only. Result/claim/capture paths are NOT opened by discovery/sealing."""
    manifest=load(checked(repo,composition_pin))
    if set(manifest)!={'schema','originalInstrument','chains'} \
            or manifest['schema']!='w50-completed-current-composition-1' \
            or not isinstance(manifest['chains'],list) or len(manifest['chains'])!=2:
        raise ValueError('Composed source metadata needs its exact two-chain descriptor')
    chains=manifest['chains'];roots=[]
    if any(set(c)!={'instrument','batch','contract','result'} for c in chains) \
            or chains[0]['instrument']!=manifest['originalInstrument'] \
            or chains[0]['instrument']==chains[1]['instrument']:
        raise ValueError('Composed source metadata changed actual root ownership/order')
    for chain in chains:
        for item in chain.values():pin_shape(item)
        path=checked(repo,chain['instrument']);sidecar(path);root=load(path)
        if root.get('schema')!='w50-g1-current-instrument-root-1' or root.get('repo')!=str(Path(repo).resolve()):
            raise ValueError('Only actual same-repository current instruments may compose')
        sources=root['closure']['sources']
        for name,digest in sources.items():checked(repo,{'path':name,'sha256':digest})
        for name in ('bootstrap','probe'):
            target=checked(repo,root[name])
            if sources.get(root[name]['path'])!=root[name]['sha256']:
                raise ValueError('Actual instrument entrypoint/probe is outside its sealed source closure')
            if name=='bootstrap' and target!=path.parent/'dispatch.py':
                raise ValueError('Actual instrument bootstrap selection differs')
        roots.append({'pin':chain['instrument'],'document':root})
    return manifest,roots


def metadata(config):
    """Fixed composition/native/G0 selection, without reading optical reports or pixels."""
    if set(config)!={'schema','currentComposition','native','originals','output'} \
            or config['schema']!='w50-composed-current-config-1':
        raise ValueError('Unknown composed-current configuration; no single-root substitute is admitted')
    manifest,roots=composition_metadata(REPO,config['currentComposition'])
    original=roots[0]['document']
    native=config['native']
    if set(native)!={'instrument','contract','batch','reports'} or set(native['reports'])!={'calibration','validation'}:
        raise ValueError('Only the two exact exposed native role reports are admitted')
    for item in native['reports'].values():
        pin_shape(item)
        if Path(item['path']).is_absolute() or '..' in Path(item['path']).parts or not item['path'].endswith('.json.gz'):
            raise ValueError('Native reports require exact repository gzip pins')
    paths={}
    for name,filename in (('instrument','instrument-root.json'),('contract','execution-contract.json'),('batch','read-batch.json')):
        paths[name]=checked(REPO,native[name])
        if paths[name]!=FIT/'native'/filename:raise ValueError('Original native source selection changed')
    sidecar(paths['instrument']);sidecar(paths['contract'])
    nroot=load(paths['instrument']);contract=load(paths['contract']);batch=load(paths['batch'])
    if nroot.get('schema')!='w50-native-instrument-root-1' or nroot['batch']!=native['batch'] \
            or nroot['contract']!=native['contract'] or contract['batch']!=native['batch'] \
            or nroot['inputs']!=batch['inputs']:
        raise ValueError('Original native instrument/contract/input chain differs')
    for name,digest in nroot['sources'].items():checked(REPO,{'path':name,'sha256':digest})
    if [e['role'] for e in batch['exports']]!=['calibration','validation']:
        raise ValueError('Blind native role I/O is closed')
    originals=config['originals']
    if set(originals)!={'references','scenes','canonicalScenes'} \
            or originals['references']!=original['references'] or originals['scenes']!=batch['inputs']['scenes']:
        raise ValueError('Composed analysis changed original G0 reference/scene identities')
    for item in originals.values():checked(REPO,item)
    if checked(REPO,originals['canonicalScenes'])!=REPO/'apps/reference-apple/scenes.json':
        raise ValueError('Canonical scene declaration changed')
    for name in ('partOne','partTwo'):
        part=load(checked(REPO,original[name]))
        if any(item not in part['sources'] for item in originals.values()):
            raise ValueError('Original scene/reference pins absent from immutable G0 declarations')
    output=ordinary(Path(config['output']))
    if output.is_relative_to(REPO) or any(output.is_relative_to(ordinary(Path(e['root']))) for e in batch['exports']):
        raise ValueError('Composed result must be fresh external scratch outside original source trees')
    return manifest,roots,batch


def discover(composition_pin=None):
    if composition_pin is not None:composition_metadata(REPO,composition_pin)
    guard=source(GUARD,'w50_composed_source_discovery')
    name='W50_COMPOSED_CURRENT_COMPOSITION';previous=os.environ.get(name)
    try:
        if composition_pin is None:os.environ.pop(name,None)
        else:os.environ[name]=json.dumps(composition_pin)
        closure=guard.discover(REPO,PROBE)
    finally:
        if previous is None:os.environ.pop(name,None)
        else:os.environ[name]=previous
    closure['sources'][str(GUARD.relative_to(REPO))]=sha(GUARD)
    return closure


def enforce(closure):
    for name,digest in closure['sources'].items():checked(REPO,{'path':name,'sha256':digest})
    relative=str(GUARD.relative_to(REPO))
    if closure['sources'].get(relative)!=sha(GUARD):raise ValueError('Source guard is not prospectively pinned')
    guard=source(GUARD,'w50_composed_live_source_guard')
    if guard.environment()!=closure['environment']:raise ValueError('Composed interpreter/package environment changed')
    guard.enforce(REPO,closure['sources'])


def build_template(composition_pin,native_reports,output):
    """Return concrete prospective metadata from an explicitly supplied completed descriptor.

    The descriptor is created by the parent only after both authentic results exist. This
    builder reads no result/statistic/PNG. Full composition authentication belongs to the
    externally admitted analytical execution below, before any measured evidence is opened.
    """
    manifest,roots=composition_metadata(REPO,composition_pin)
    for chain in manifest['chains']:
        for name in ('batch','contract','result'):
            item=chain[name];path=REPO/item['path']
            if Path(item['path']).is_absolute() or '..' in Path(item['path']).parts or not ordinary(path).is_file():
                raise ValueError('Cannot finalize composed config before both actual completed result chains exist')
    original=roots[0]['document'];part=load(checked(REPO,original['partOne']))
    canonical=next(p for p in part['sources'] if p['path']=='apps/reference-apple/scenes.json')
    batch_pin=pin(REPO,FIT/'native/read-batch.json');batch=load(checked(REPO,batch_pin))
    config=dict(schema='w50-composed-current-config-1',currentComposition=composition_pin,
        native=dict(instrument=pin(REPO,FIT/'native/instrument-root.json'),
            contract=pin(REPO,FIT/'native/execution-contract.json'),batch=batch_pin,reports=native_reports),
        originals=dict(references=original['references'],scenes=batch['inputs']['scenes'],canonicalScenes=canonical),
        output=str(output))
    metadata(config)
    return config


def seal_config():
    if INSTRUMENT.exists() or Path(str(INSTRUMENT)+'.sha256').exists():raise ValueError('Existing composed analysis seal; no amendment')
    config=load(ordinary(CONFIG));metadata(config);closure=discover(config['currentComposition'])
    root=dict(schema='w50-completed-current-root-2',config=pin(REPO,CONFIG),entrypoint=pin(REPO,Path(__file__)),
              probe=pin(REPO,PROBE),closure=closure)
    write_once(INSTRUMENT,root)
    with Path(str(INSTRUMENT)+'.sha256').open('x') as handle:
        handle.write(f'{sha(INSTRUMENT)}  {INSTRUMENT.name}\n');handle.flush();os.fsync(handle.fileno())
    return {'instrumentRootSha256':sha(INSTRUMENT)}


def admit_root(path,external_sha256,*,repo=REPO):
    path=ordinary(path)
    if not re.fullmatch('[0-9a-f]{64}',external_sha256) or sha(path)!=external_sha256:
        raise ValueError('Composed analysis root differs from external registered hash')
    sidecar(path);root=load(path)
    if root.get('schema')!='w50-completed-current-root-2':raise ValueError('Wrong composed analysis root schema')
    for item in (root['config'],root['entrypoint'],root['probe']):checked(repo,item)
    sources=root['closure']['sources']
    for name,digest in sources.items():checked(repo,{'path':name,'sha256':digest})
    for item in (root['entrypoint'],root['probe']):
        if sources.get(item['path'])!=item['sha256']:raise ValueError('Composed entrypoint/probe absent from exercised closure')
    if str(GUARD.relative_to(REPO)) not in sources:raise ValueError('Composed source guard is missing')
    return root


def execute(external_sha256):
    root=admit_root(INSTRUMENT,external_sha256)
    if checked(REPO,root['config'])!=CONFIG or checked(REPO,root['entrypoint'])!=Path(__file__) \
            or checked(REPO,root['probe'])!=PROBE:raise ValueError('Composed root substituted its fixed entry/config/probe')
    config=load(CONFIG);metadata(config)
    output=ordinary(Path(config['output']))
    if output.exists():raise ValueError('Composed result exists; never overwrite evidence')
    enforce(root['closure'])
    reader=source(HERE/'analysis.py','w50_bound_composed_current')
    report=reader.read_completed(config)
    report.update(instrumentRootSha256=external_sha256,config=root['config'],sourcePins=root['closure']['sources'])
    write_once(output,report)
    return {'status':'EVIDENCE_ONLY','output':str(output),'sha256':sha(output)}


def source_probe(composition_pin=None):
    return source(HERE/'analysis.py','w50_composed_probe_reader').source_probe(REPO,composition_pin)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('probe','seal','read'));parser.add_argument('--root-sha256')
    args=parser.parse_args()
    if args.command=='probe':result=discover()
    elif args.command=='seal':result=seal_config()
    elif args.root_sha256:result=execute(args.root_sha256)
    else:parser.error('read requires the externally registered --root-sha256')
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
