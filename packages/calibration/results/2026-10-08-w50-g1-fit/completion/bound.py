"""Parent-called registered-input assembly; no CLI, seal, fit permission or pixel reader.

The parent prospectively registers the binding and executes this module under its source
closure. These functions verify the registered producer identities and exact content pins,
then return an assembly plan. No output path or instrument root is discovered implicitly.
"""
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import types

HERE=Path(__file__).resolve().parent
EXECUTION=HERE.parents[1]/'2026-10-08-w50-g1-current2/execution'
FIELDS={'original','manifest','currentAnalysis','currentAnalysisRoot','canonicalReferences',
        'canonicalReferencesRoot','ownerIndex','ownerContracts','ownerSource','validator',
        'sourcePins','reportedKeys','emptySupportKeys'}


def sha(raw): return hashlib.sha256(raw).hexdigest()


def path_of(repo, name):
    if not isinstance(name,str): raise ValueError('Missing registered input path')
    path=Path(name); path=path if path.is_absolute() else Path(repo)/path
    if '..' in path.parts or not path.is_absolute() or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Registered paths must be ordinary absolute paths without symlinks')
    return path


def read_pin(repo, item):
    if not isinstance(item,dict) or set(item) != {'path','sha256'} \
            or not re.fullmatch('[0-9a-f]{64}',item.get('sha256','')):
        raise ValueError('Missing exact registered content pin')
    path=path_of(repo,item['path']); raw=path.read_bytes()
    if sha(raw) != item['sha256']: raise ValueError('Changed registered input/source: '+str(path))
    return raw


def document(repo, item):
    raw=read_pin(repo,item)
    if raw.startswith(b'\x1f\x8b'): raw=gzip.decompress(raw)
    def invalid(value): raise ValueError('Nonfinite registered JSON: '+value)
    return json.loads(raw,parse_constant=invalid)


def source(path):
    module=types.ModuleType('w50_bound_'+path.stem); module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


def check_sources(repo, binding):
    if not isinstance(binding,dict) or set(binding) != FIELDS:
        raise ValueError('Incomplete or unknown registered assembly binding')
    sources=binding['sourcePins']
    if not isinstance(sources,dict) or not sources: raise ValueError('Missing parent-registered source hashes')
    checked={}
    for name,digest in sources.items():
        read_pin(repo,{'path':name,'sha256':digest}); checked[path_of(repo,name)]=digest
    for path in (Path(__file__),HERE/'assembler.py',EXECUTION/'prefit.py',
                 EXECUTION/'native_evidence.py',EXECUTION/'owner_evidence.py'):
        if checked.get(path) != sha(path.read_bytes()):
            raise ValueError('Assembler/validator source absent from registered closure')
    if path_of(repo,binding['validator']['path']) != EXECUTION/'prefit.py':
        raise ValueError('Completion must use the corrected original current2 pre-fit validator')
    read_pin(repo,binding['validator'])
    return source(HERE/'assembler.py')


def producer_sources(repo, expected, actual):
    if not isinstance(expected,dict) or not expected or actual != expected:
        raise ValueError('Registered producer source hashes differ from output')
    for name,digest in expected.items(): read_pin(repo,{'path':name,'sha256':digest})


def composed_anchors(repo, composition_pin):
    """Reconstruct ordered metadata anchors, not an execution root or capture admission.

    The registered analysis/reference producers own both-report admission. This boundary
    checks their content-pinned descriptor and every actual chain byte, including sidecars,
    so neither producer can silently name a different root/result population.
    """
    composition=document(repo,composition_pin)
    chains=composition.get('chains',[])
    if set(composition) != {'schema','originalInstrument','chains'} or \
            composition.get('schema') != 'w50-completed-current-composition-1' or \
            not isinstance(chains,list) or len(chains) != 2 or any(
                not isinstance(c,dict) or set(c) != {'instrument','batch','contract','result'} for c in chains) or \
            composition['originalInstrument'] != chains[0]['instrument'] or \
            chains[0]['instrument'] == chains[1]['instrument']:
        raise ValueError('Composition requires its two ordered actual completed chains')
    pins=[copy.deepcopy(composition_pin)]
    def actual_pin(path):
        path=path_of(repo,str(path))
        if not path.is_file():raise ValueError('Missing actual composition chain file')
        raw=path.read_bytes()
        name=str(path) if Path(composition_pin['path']).is_absolute() else str(path.relative_to(repo))
        return {'path':name,'sha256':sha(raw)}
    def add(item):
        read_pin(repo,item)
        if item not in pins:pins.append(copy.deepcopy(item))
    for chain in chains:
        root=document(repo,chain['instrument'])
        root_path=path_of(repo,chain['instrument']['path'])
        contract_path=root_path.parent/'current-instrument'/(chain['batch']['sha256']+'.json')
        if root.get('schema') != 'w50-g1-current-instrument-root-1' or \
                chain['batch'] not in root.get('currentBatches',[]):
            raise ValueError('Composition batch differs from its actual root')
        if path_of(repo,chain['contract']['path']) != contract_path or \
                path_of(repo,chain['result']['path']) != Path(str(contract_path)+'.result.json'):
            raise ValueError('Composition names a different actual phase contract/result')
        contract=document(repo,chain['contract'])
        if contract.get('schema') != 'w50-g1-phase-contract-1' or contract.get('phase') != 'current' or \
                contract.get('batch') != chain['batch'] or \
                contract.get('executionRootSha256') != chain['instrument']['sha256']:
            raise ValueError('Composition phase contract differs from its root/batch')
        for item in (chain['instrument'],chain['batch'],chain['result']):add(item)
        for path,target in ((Path(str(root_path)+'.sha256'),chain['instrument']),
                            (contract_path,None),(Path(str(contract_path)+'.sha256'),chain['contract']),
                            (Path(str(contract_path)+'.started.json'),None),
                            (Path(str(contract_path)+'.result.json.sha256'),chain['result'])):
            item=actual_pin(path)
            if target is not None and read_pin(repo,item) != \
                    f'{target["sha256"]}  {Path(target["path"]).name}\n'.encode():
                raise ValueError('Composition chain sidecar differs from actual content pin')
            add(item)
        inputs=root.get('inputs')
        if not isinstance(inputs,list):raise ValueError('Missing actual root input pins')
        for item in inputs:add(item)
    return dict(currentComposition=copy.deepcopy(composition_pin),
        currentInstruments=[copy.deepcopy(c['instrument']) for c in chains],
        currentResults=[copy.deepcopy(c['result']) for c in chains],chainPins=pins)


def composed_projection(canonical, anchors, a):
    projection=canonical.get('currentArtifactProjection')
    if not isinstance(projection,dict) or \
            projection.get('schema') != 'w50-admitted-current-reference-projection-2' or \
            'currentInstrument' in projection or any(projection.get(k) != v for k,v in anchors.items()) or \
            projection.get('originalRows') != canonical.get('originalReferences'):
        raise ValueError('Canonical projection differs from the admitted analysis composition/chains')
    originals=projection['originalRows'];rows=projection.get('rows')
    if not isinstance(rows,list) or len(rows) != len(originals):
        raise ValueError('Canonical projection changed original row population')
    completed=[]
    for original,row in zip(originals,rows,strict=True):
        if set(original) != set(row):raise ValueError('Canonical projection changed original row fields')
        changed=[]
        for name,value in original.items():
            if row[name] == value:continue
            if name not in ('currentEvidence','currentMetadata') or value is not None or \
                    row[name] is None or original.get('role') != 'gate':
                raise ValueError('Canonical projection changed a nonnull/numeric/role/history field')
            changed.append(name)
        if changed:completed.append(list(a.key(original)))
    if projection.get('completedKeys') != completed:
        raise ValueError('Canonical projection completion keys differ from original null artifact fills')


def registered_inputs(repo, binding):
    """Only later, after explicit parent registration; no pixel or statistical computation."""
    a=check_sources(repo,binding)
    original=document(repo,binding['original']); manifest=document(repo,binding['manifest'])
    a.same_pin(original.get('inputs',{}).get('bed'),binding['manifest'],repo)
    current_root=document(repo,binding['currentAnalysisRoot'])
    canonical_root=document(repo,binding['canonicalReferencesRoot'])
    if current_root.get('schema') not in ('w50-completed-current-root-1','w50-completed-current-root-2') or \
            canonical_root.get('schema') != 'w50-reference-instrument-root-1':
        raise ValueError('Unregistered upstream evidence producer root kind')
    config=document(repo,current_root['config'])
    current=document(repo,binding['currentAnalysis'])
    canonical=document(repo,binding['canonicalReferences'])
    if current.get('instrumentRootSha256') != binding['currentAnalysisRoot']['sha256'] \
            or current.get('config') != current_root['config'] \
            or path_of(repo,config['output']) != path_of(repo,binding['currentAnalysis']['path']) \
            or current.get('originals') != config['originals'] or current.get('native') != config['native']:
        raise ValueError('Current-analysis output differs from its registered producer/config/input identity')
    if current_root['schema'] == 'w50-completed-current-root-1':
        if current.get('schema') != 'w50-completed-current-evidence-1' or \
                current.get('currentInstrument') != config['current']['instrument'] or \
                current.get('currentResults') != config['current']['results']:
            raise ValueError('Current-analysis output differs from its registered current chain')
    else:
        if set(config) != {'schema','currentComposition','native','originals','output'} or \
                config.get('schema') != 'w50-composed-current-config-1' or \
                current.get('schema') != 'w50-completed-current-evidence-2' or \
                current.get('status') != 'EVIDENCE_ONLY' or 'currentInstrument' in current:
            raise ValueError('Composed analysis requires schema2 without a virtual current instrument')
        anchors=composed_anchors(repo,config['currentComposition'])
        if any(current.get(k) != v for k,v in anchors.items()):
            raise ValueError('Composed analysis differs from its ordered actual chain anchors')
        composed_projection(canonical,anchors,a)
    producer_sources(repo,current_root['closure']['sources'],current.get('sourcePins'))
    if canonical.get('instrumentRootSha256') != binding['canonicalReferencesRoot']['sha256'] \
            or canonical.get('inputs') != canonical_root['inputs'] \
            or canonical.get('batch') != canonical_root['batch'] \
            or canonical.get('contract') != canonical_root['contract']:
        raise ValueError('Canonical reference output differs from its registered producer/input identity')
    batch=document(repo,canonical_root['batch']); contract=document(repo,canonical_root['contract'])
    if batch.get('inputs') != canonical_root['inputs'] or contract.get('batch') != canonical_root['batch'] \
            or canonical.get('selectedKeys') != batch.get('selectedKeys'):
        raise ValueError('Canonical batch/contract/output selection differs')
    producer_sources(repo,canonical_root['sources'],canonical.get('sourcePins'))
    owner_index=document(repo,binding['ownerIndex']); owner_batch=document(repo,owner_index['source'])
    owner_documents={}
    for entry in owner_index.get('rows',[]):
        item=entry['evidence']; path=item['path']
        if path in owner_documents: raise ValueError('Duplicate owner index evidence file')
        owner_documents[path]=document(repo,item)
    provenance={k:copy.deepcopy(binding[k]) for k in
        ('original','currentAnalysis','canonicalReferences','ownerIndex','ownerContracts','ownerSource')}
    provenance['ownerBatch']=copy.deepcopy(owner_index['source'])
    return a,original,manifest,current,canonical,owner_index,owner_batch,owner_documents,provenance


def assemble_registered(repo, binding, *, artifact_root):
    a,original,manifest,current,canonical,index,batch,documents,provenance=registered_inputs(repo,binding)
    root=path_of(repo,str(artifact_root))
    if root.exists():
        raise ValueError('Provenance artifacts require a fresh directory, never an existing source tree')
    result=a.assemble(original,current,canonical,index,batch,documents,provenance=provenance,
        artifact_root=str(root),exemptions=binding['reportedKeys'],empty_support_keys=binding['emptySupportKeys'],repo=str(repo))
    result['sourcePins']=copy.deepcopy(binding['sourcePins'])
    result['binding']=copy.deepcopy(binding)
    result['artifactRoot']=str(root)
    return result


def materialize_artifacts(bundle):
    """Write only the already planned provenance documents, once; never a root or PASS."""
    planned=[]
    for filename,value in bundle['artifacts'].items():
        path=path_of('/',filename)
        raw=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
        digest=sha(raw)
        if path.name != digest+'.json': raise ValueError('Artifact name is not its exact content hash')
        if path.exists(): raise FileExistsError(str(path))
        planned.append((path,raw,digest))
    pins=[]
    for path,raw,digest in planned:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as handle:
            handle.write(raw);handle.flush();os.fsync(handle.fileno())
        pins.append({'path':str(path),'sha256':digest})
    return pins


def validate_registered(repo, binding, bundle):
    """Reuse the original strict validator; this is reference validation, never pre-fit permission."""
    a,original,manifest,current,canonical,index,batch,documents,provenance=registered_inputs(repo,binding)
    if bundle.get('binding') != binding or bundle.get('sourcePins') != binding['sourcePins']:
        raise ValueError('Assembly bundle changed its registered inputs/sources')
    expected=a.assemble(original,current,canonical,index,batch,documents,provenance=provenance,
        artifact_root=bundle['artifactRoot'],exemptions=binding['reportedKeys'],
        empty_support_keys=binding['emptySupportKeys'],repo=str(repo))
    expected.update(binding=copy.deepcopy(binding),sourcePins=copy.deepcopy(binding['sourcePins']),
                    artifactRoot=bundle['artifactRoot'])
    if a.encoded(bundle) != a.encoded(expected):
        raise ValueError('Bundle differs from deterministic assembly of registered source evidence')
    validator=source(EXECUTION/'prefit.py')
    validator.validate_exemptions(original,manifest,binding['reportedKeys'])
    validator.validate_empty_eligibility(original,manifest,binding['reportedKeys'],binding['emptySupportKeys'])
    owners=[list(a.key(row)) for row in original['cells'] if row['statistic']=='owner-contracts']
    validator.validate_completion(original,bundle['completed'],binding['reportedKeys'],repo,
        empty_support_keys=binding['emptySupportKeys'],owner_budget_keys=owners,
        owner_contracts=binding['ownerContracts'],owner_source=binding['ownerSource'])
    return {'status':'REFERENCE_VALIDATION_ONLY','validator':copy.deepcopy(binding['validator'])}
