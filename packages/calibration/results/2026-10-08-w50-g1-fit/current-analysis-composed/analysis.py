"""DL5k composed-current reader over two genuine completed instrument chains.

Only chain loading and orchestration are new. The immutable current3 analyzer remains the
single implementation of repeat binding, BOTH-page capture validation, native masks,
statistics, argument extraction and additive projection. No aggregate execution root or
live context is created. A member always names its actual instrument and claimed result.
"""
import copy
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
FIT=HERE.parent
REPO=HERE.parents[4]
CANONICAL3=FIT.parent/'2026-10-08-w50-g1-canonical3'
CURRENT3=FIT.parent/'2026-10-08-w50-g1-current3'
KEY=('profile','renderer','scene','statistic')
MEMBER_FIELDS=('instrument','run','receipt','output','batch','contract','claim','result')


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


A=source(FIT/'current-analysis/analysis.py','w50_composed_immutable_analysis')
B=A.B
C=source(CANONICAL3/'execution/composition.py','w50_composed_actual_chains')


def pin_key(item):
    B.pin_shape(item)
    return item['path'],item['sha256']


def member_key(member): return tuple(member['receipt'][k] for k in KEY[:3])


def index_composition(validated, manifest, composition_pin):
    """Index an authenticated composition without erasing either chain's ownership.

    The production caller obtains `validated` only from validate_completed_current. This
    pure indexing boundary also rejects inconsistent or mutated ownership before any repeat
    object is bound. It never validates an incomplete historical root as an execution root.
    """
    B.pin_shape(composition_pin)
    if manifest.get('schema')!='w50-completed-current-composition-1' or len(manifest.get('chains',[]))!=2:
        raise ValueError('Composed analysis needs its original two-chain descriptor')
    raw=copy.deepcopy(validated);chains=manifest['chains']
    roots=raw.get('roots',[]);results=raw.get('resultDocuments',[])
    if [r.get('pin') for r in roots]!=[c['instrument'] for c in chains] or \
            [r.get('pin') for r in results]!=[c['result'] for c in chains] or \
            manifest.get('originalInstrument')!=chains[0]['instrument']:
        raise ValueError('Actual root/result order differs from composition chains')
    root_map={pin_key(r['pin']):r['document'] for r in roots}
    result_map={pin_key(r['pin']):r['document'] for r in results}
    if len(root_map)!=2 or len(result_map)!=2:
        raise ValueError('Composition collapsed distinct actual roots or results')
    if composition_pin not in raw.get('chainPins',[]):
        raise ValueError('Composition descriptor is absent from its authenticated chain pins')
    for root in roots:
        if root['document'].get('baselineDocuments')!=raw['candidates']:
            raise ValueError('Actual roots do not retain the same original gate0 documents')
    snapshots={}
    for member in raw.get('members',[]):
        if set(member)!=set(MEMBER_FIELDS):
            raise ValueError('Unexpected fields in authenticated current member')
        root_identity=pin_key(member['instrument'])
        if root_identity not in root_map: raise ValueError('Current member names an unauthenticated instrument')
        chain=chains[[pin_key(r['pin']) for r in roots].index(root_identity)]
        if any(member[k]!=chain[k] for k in ('instrument','batch','contract','result')):
            raise ValueError('Current member changed its actual chain ownership')
        contract_path=Path(member['contract']['path'])
        if member['claim']['path']!=str(Path(str(contract_path)+'.started.json')):
            raise ValueError('Current member claim is not its actual contract claim')
        result=result_map[pin_key(member['result'])]
        if result.get('contractSha256')!=member['contract']['sha256'] or \
                result.get('claimSha256')!=member['claim']['sha256'] or \
                result.get('report',{}).get('status')!='CAPTURED':
            raise ValueError('Current member is not bound to its completed actual result')
        matches=[r for r in result['captures']['captures'] if all(
            r.get(k)==member['receipt'][k] for k in KEY[:3])]
        if matches!=[member['receipt']]:
            raise ValueError('Current member receipt differs from completed actual result')
        key=member_key(member)
        if key in snapshots: raise ValueError('Duplicate composed current member')
        snapshots[key]=copy.deepcopy(member)
    if not snapshots: raise ValueError('Empty completed-current composition')
    raw.update(composition=copy.deepcopy(composition_pin),manifest=copy.deepcopy(manifest),
        originalInstrument=copy.deepcopy(manifest['originalInstrument']),originalRoot=roots[0]['document'],
        _roots=root_map,_results=result_map,_members=snapshots,_dispatchers={})
    return raw


def anchors(admitted):
    return dict(currentComposition=copy.deepcopy(admitted['composition']),
        currentInstruments=[copy.deepcopy(r['pin']) for r in admitted['roots']],
        currentResults=[copy.deepcopy(r['pin']) for r in admitted['resultDocuments']],
        chainPins=copy.deepcopy(admitted['chainPins']))


def dispatcher(admitted, root_pin):
    key=pin_key(root_pin)
    if key not in admitted['_roots']: raise ValueError('Unknown actual composed instrument')
    if key not in admitted['_dispatchers']:
        path=B.checked(REPO,admitted['_roots'][key]['bootstrap'])
        admitted['_dispatchers'][key]=source(path,'w50_composed_dispatch_'+root_pin['sha256'][:12])
    return admitted['_dispatchers'][key]


def candidate_map(admitted):
    """The same gate0 identity checks as the immutable single-root loader, on real originals."""
    root=admitted['originalRoot'];d=dispatcher(admitted,admitted['originalInstrument'])
    part=d.load(d.checked(REPO,root['partTwo']));original_pins={p['path']:p for p in part['sources']}
    result={}
    for candidate_pin in admitted['candidates']:
        position=d.admission_module(root).endpoints(root,candidate_pin,current=True)
        path=B.checked(REPO,candidate_pin);document=B.load(path);endpoints={};pair={}
        for slot,item in document['endpoints'].items():
            pose,scheme=slot.split('.');suffix='-receded' if pose=='receded' else ''
            original_path=FIT.parents[1]/'profiles'/f'apple-macos-27.0-1x-{scheme}-standard-glass{position}{suffix}.json'
            original_pin=original_pins[str(original_path.relative_to(REPO))]
            original=B.load(B.checked(REPO,original_pin))
            endpoint_path=B.ordinary(path.parent/item['path'])
            if not endpoint_path.is_relative_to(REPO): raise ValueError('Endpoint escaped original repository')
            endpoint_pin={'path':str(endpoint_path.relative_to(REPO)),'sha256':item['sha256']}
            actual=B.load(B.checked(REPO,endpoint_pin))
            if {k:v for k,v in actual.items() if k!='profileKey'}!={k:v for k,v in original.items() if k!='profileKey'}:
                raise ValueError('Composed gate0 endpoint differs from original document outside namespace')
            endpoints[slot]=dict(actual,source=original_pin,candidateEndpoint=endpoint_pin)
            if scheme=='dark': pair[slot]=original_pin['sha256']
        result[candidate_pin['sha256']]=dict(document=candidate_pin,endpoints=endpoints,
            originalDocumentPair=pair,position=position)
    return result


def admit_composition(repo, composition_pin):
    if Path(repo).resolve()!=REPO:
        raise ValueError('Composed analysis uses the original same-repository immutable readers')
    # No native, report-statistic or analytical capture read precedes this complete two-chain check.
    validated=C.validate_completed_current(repo,composition_pin)
    manifest=B.load(B.checked(repo,composition_pin))
    admitted=index_composition(validated,manifest,composition_pin)
    admitted['candidates']=candidate_map(admitted)
    return admitted


def bind_member(admitted, member, original_rows):
    expected=admitted['_members'].get(member_key(member))
    actual={k:member.get(k) for k in MEMBER_FIELDS}
    if expected is None or actual!=expected:
        raise ValueError('Actual member changed after completed composition authentication')
    if '_repeat' in member:
        A.bound_repeat(member)
        return
    root=admitted['_roots'][pin_key(member['instrument'])]
    result=admitted['_results'][pin_key(member['result'])]
    A.bind_completed_repeat(root,member['instrument'],member,original_rows,
        dispatcher=dispatcher(admitted,member['instrument']),result=result)


def member_provenance(admitted, member):
    if {k:member.get(k) for k in MEMBER_FIELDS}!=admitted['_members'].get(member_key(member)):
        raise ValueError('Actual member provenance changed after composition admission')
    return dict(currentComposition=copy.deepcopy(admitted['composition']),
        instrument=copy.deepcopy(member['instrument']),batch=copy.deepcopy(member['batch']),
        contract=copy.deepcopy(member['contract']),claim=copy.deepcopy(member['claim']),result=copy.deepcopy(member['result']))


def read_completed(config):
    admitted=admit_composition(REPO,config['currentComposition'])
    native_batch=A.native_contract(REPO,config['native'])
    inventory=B.load(B.checked(REPO,config['originals']['references']))
    scenes=B.load(B.checked(REPO,config['originals']['scenes']))
    rows=inventory['cells'];keys=[tuple(r[k] for k in KEY) for r in rows]
    if len(keys)!=len(set(keys)): raise ValueError('Original G0 references contain duplicate keys')
    required=A.M.N.required_arguments(inventory)
    routes=A.current_routes(admitted['members'],rows,required)
    newbed={member_key(m) for m in admitted['members'] if m['run']['sceneSource']=='w50'}
    if any(r['role'] in ('blind','historical-prediction-check') for r in rows if tuple(r[k] for k in KEY[:3]) in newbed):
        raise ValueError('Closed native physical population is not composed current evidence')
    roles=A.native_roles(config,native_batch,scenes)
    evidence=[];arguments=[];extras=[];background_cache={};by_scene={s['id']:s for s in scenes['scenes']}
    for member in admitted['members']:
        receipt=member['receipt'];triple=member_key(member)
        candidate=admitted['candidates'][receipt['candidate']['sha256']]
        originals=[r for r in rows if tuple(r[k] for k in KEY[:3])==triple]
        if not originals or any(r['currentDocumentPair']!=candidate['originalDocumentPair'] for r in originals):
            raise ValueError('Composed gate0 draw differs from original current document pair')
        route=routes['|'.join(triple)]
        bind_member(admitted,member,rows)
        plan,spec,png,measured_arguments,provenance=A.capture_inputs(member,candidate,
            argument_required=route['requiredArgument'])
        actual=member_provenance(admitted,member);provenance.update(actual)
        for argument in measured_arguments: argument['provenance'].update(copy.deepcopy(actual))
        if route['requiredArgument']:arguments.extend(measured_arguments)
        else:
            extras.append(dict(profile=triple[0],renderer=triple[1],scene=triple[2],
                originalReferences=copy.deepcopy(route['originalReferences']),provenance=provenance,
                status='ARTIFACTS_ONLY_USE_EXISTING_CANONICAL_REFERENCE_READER'))
        if member['run']['sceneSource']!='w50': continue
        role=roles[spec['role']];cell=role['cells'][receipt['profile']+'/'+receipt['scene']]
        if any(cell[k]!=spec[k] for k in ('pose','span','background')) or cell['scale']!=plan['dpr'] \
                or cell['glass']!=plan['position']:
            raise ValueError('Original native cell differs from composed scene geometry')
        dependency=role['deps'][cell['reference']]['evidence'];cache_key=(spec['role'],cell['reference'])
        if cache_key not in background_cache:
            background_cache[cache_key]=A.M.R.read_verified_frame(Path(role['export']['root']),dependency,
                                                                scenes['canvas'],plan['dpr'])
        scene=by_scene[receipt['scene']]
        measured=A.measure_pixels(A.M.R.S.decode_png(png),background_cache[cache_key],cell,
            scenes['components'][scene['component']],scenes['canvas'],
            impulse=scenes['backgrounds'][scene['background']]['kind']=='impulse',renderer=receipt['renderer'])
        provenance.update(nativeRead=role['reportPin'],nativeBatch=config['native']['batch'],
            nativeInstrument=config['native']['instrument'],nativeContract=config['native']['contract'],
            nativeExport=role['export'],nativeDependency=copy.deepcopy(dependency),scenes=config['originals']['scenes'])
        evidence.extend(A.project_native_rows(rows,measured,provenance,cell))
    if len(extras)!=12: raise ValueError('Composed T1 artifact route must contain exactly twelve captures')
    return dict(schema='w50-completed-current-evidence-2',status='EVIDENCE_ONLY',**anchors(admitted),
        originals=copy.deepcopy(config['originals']),native=copy.deepcopy(config['native']),
        referenceEvidence=sorted(evidence,key=lambda r:tuple(r[k] for k in KEY)),
        arguments=A.argument_population(arguments,required),canonicalMissingT1=extras,
        policy='ACTUAL_MULTI_ROOT_CHAINS_ADDITIVE_ORIGINAL_KEYS_NO_PREFIT_PASS_NO_CANDIDATE_REBIND')


def source_probe(repo=REPO, composition_pin=None):
    """Only source metadata/probes and generated arrays; never authenticate real result chains."""
    repo=Path(repo).resolve()
    if composition_pin is None:
        probes=[CURRENT3/'current_probe.py',CANONICAL3/'current_probe.py']
    else:
        manifest=B.load(B.checked(repo,composition_pin))
        if manifest.get('schema')!='w50-completed-current-composition-1' or len(manifest.get('chains',[]))!=2:
            raise ValueError('Source probe needs the actual two-root descriptor')
        probes=[]
        for chain in manifest['chains']:
            root=B.load(B.checked(repo,chain['instrument']))
            for path,digest in root['closure']['sources'].items():B.checked(repo,{'path':path,'sha256':digest})
            for entry in ('bootstrap','probe'):
                path=B.checked(repo,root[entry])
                if root['closure']['sources'].get(root[entry]['path'])!=root[entry]['sha256']:
                    raise ValueError('Configured source probe/bootstrap is outside actual root closure')
            probes.append(B.checked(repo,root['probe']))
    for i,path in enumerate(probes):source(path,f'w50_composed_original_source_probe_{i}')
    A.source_probe()
    return {'status':'SOURCE_ONLY'}
