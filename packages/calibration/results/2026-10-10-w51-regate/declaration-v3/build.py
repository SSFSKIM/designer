"""Declare DL5's exact populations from exposed, pre-fit static evidence; no web execution.

Only the known real-4 costs supply candidate values. Every aggregate operand is native/current
reference evidence, never a gate capture or an inferred replacement for a source-owned budget.
The write-once output is a scientific declaration, not an execution seal or clearance.
"""
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
WAVE = HERE.parent
REPO = HERE.parents[4]
V2 = WAVE/'declaration-v2'
KEY = ('profile','renderer','scene','statistic')
CHANNELS = ('deep8-channel-median','central8-channel-median')
LUMA = ('deep8-far24-luma-mean','deep8-far24-luma-median')
PROFILE = re.compile(r'apple-macos-27\.0-([12])x-dark-standard-glass(0\.25|0\.5)')


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def require(condition, reason):
    if not condition:raise ValueError(reason)


def ordinary(path):
    path=Path(path).absolute()
    require(path.resolve()==path and not any(p.is_symlink() for p in (path,*path.parents)),
            'Declaration input is not an ordinary canonical path')
    return path


def pin(path):
    path=ordinary(path)
    return {'path':str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),
            'sha256':sha(path)}


def checked(item):
    path=ordinary(REPO/item['path'])
    require(sha(path)==item['sha256'],'Changed declaration source pin')
    return path


def load(path):
    raw=ordinary(path).read_bytes()
    def invalid(_):raise ValueError('Nonfinite declaration JSON')
    return json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw,
                      parse_constant=invalid)


def same_pin(a,b):
    return ordinary(REPO/a['path'])==ordinary(REPO/b['path']) and a['sha256']==b['sha256']


def read(item):return load(checked(item))
def key(row):return tuple(row[k] for k in KEY)


def indexed(rows, fields=KEY):
    result={tuple(r[k] for k in fields):r for r in rows}
    require(len(result)==len(rows),'Duplicate scientific source identity')
    return result


def number(value, *, positive=False):
    require(type(value) in (int,float) and math.isfinite(value) and value>=0 and
            (not positive or value>0),'Missing or nonfinite source-owned operand')
    return value


def unique_pins(pins):
    return sorted({(p['path'],p['sha256']):p for p in pins}.values(),key=lambda p:p['path'])


def source_selector(source, collection, identity, **fields):
    return {'source':copy.deepcopy(source),
            'selector':dict(collection=collection,key=list(identity),**fields)}


def derive_policy(data):
    """Pure source-to-declaration projection, including every priced component exactly once."""
    try:
        return _derive_policy(data)
    except (KeyError,TypeError,StopIteration) as error:
        raise ValueError('Required source member/reading is absent') from error


def _derive_policy(data):
    origin=data['dataOrigin'];require(origin in ('measured-native','synthetic'),'Unknown data origin')
    require(origin!='synthetic' or not data['exceptions'],'Synthetic policy cannot inherit real costs')
    wanted=[tuple(k) for k in data['population']['statisticKeys']]
    require(wanted==sorted(set(wanted)),'Complete population is not exact, sorted and unique')
    originals=indexed(data['inventory']['cells']);completed=indexed(data['completed']['cells'])
    canonical=indexed([r for group in data['canonical']['partitions'].values() for r in group])
    cuts=indexed([r for r in data['cut']['T1']['cells'] if r['tier']=='webgpu'],('profile','scene'))
    bed=indexed(data['manifest']['cells'],('profile','scene'))
    scenes={r['id']:r for r in data['scenes']['scenes']}
    require(len(scenes)==len(data['scenes']['scenes']),'Duplicate scene source')
    reported={tuple(k) for k in data['reportedKeys']}
    require(set(wanted)<=set(originals),'Complete population adds an original key')
    groups={}
    pins=data['pins']
    timing='gate-full' if origin=='measured-native' else 'population-full'

    def add(kind, dimensions, member):
        for lane in ('native','current'):number(member[lane])
        if kind in ('t1','newbed-t1'):number(member['epsilon'],positive=True)
        label=(kind,json.dumps(dimensions,sort_keys=True))
        groups.setdefault(label,{'kind':kind,'dimensions':dimensions,'members':[]})['members'].append(member)

    def member(identity, statistic, native, current, provenance, component=None, epsilon=None):
        result={'key':list(identity),'statistic':statistic,'component':component,
                'native':native,'current':current,'provenance':provenance}
        if epsilon is not None:result['epsilon']=epsilon
        return result

    for identity in wanted:
        original=originals[identity]
        if identity in reported or original['statistic']=='owner-contracts':continue
        match=PROFILE.fullmatch(original['profile']);require(match is not None,'Unknown profile dimension')
        dimensions={'position':float(match[2]),'scale':int(match[1]),
                    'renderer':original['renderer']}
        require(dimensions['renderer'] in ('webgpu','css'),'Unknown renderer dimension')
        newbed=original.get('nativeIdentity') is not None
        if newbed:
            declaration=bed[(original['profile'],original['scene'])]
            require(declaration['pose'] in ('active','receded'),'Unknown new-bed pose')
            dimensions['pose']='inactive' if declaration['pose']=='receded' else 'rest'
            if declaration.get('level')==64:continue
        else:
            scene=scenes[original['scene']]
            require(scene['state'] in ('rest','pressed','inactive'),'Unknown canonical pose')
            dimensions['pose']='inactive' if scene['state']=='inactive' else 'rest'
        statistic=original['statistic']
        if statistic in ('T1-full-silhouette','T1-low'):
            if newbed:
                require(declaration['family']=='structured','Unreported neutral T1 cannot enter structured aggregate')
                row=completed[identity]
                require(row['status']=='MEASURED','Structured static reference is unmeasured')
                provenance=source_selector(pins['completed'],'cells',identity,
                    nativeField=['native'],currentField=['current'])
                provenance['epsilon']=source_selector(pins['completed'],'cells',identity,
                    field=['nativeRepeat','codeStepLinear'])
                add('newbed-t1',dict(dimensions,family=declaration['family']),
                    member(identity,statistic,row['native'],row['current'],provenance,
                           epsilon=row['nativeRepeat']['codeStepLinear']))
            elif original['renderer']=='webgpu':
                stratum=original.get('stratum')
                require(stratum in ('F','T','C','P'),'Canonical T1 has no declared stratum')
                # The synthetic low-band companion on an F capture exercises routing, not
                # a second F fidelity member. Every complete key remains in completeKeys.
                if statistic!=('T1-low' if stratum=='T' else 'T1-full-silhouette'):continue
                substat='T1-fine' if stratum=='T' else statistic
                source=canonical[identity]['readings'][substat]
                require(source['status']=='MEASURED','Canonical static reference is unmeasured')
                if dimensions['position']==.25:
                    operands=original['fidelity'] if stratum=='T' else original
                    if stratum=='T':require(operands['statistic']=='T1-fine','Text fidelity has the wrong band')
                    native,current=operands['native'],operands['current']
                    provenance=source_selector(pins['inventory'],'cells',identity,
                        nativeField=['fidelity','native'] if stratum=='T' else ['native'],
                        currentField=['fidelity','current'] if stratum=='T' else ['current'])
                    cut=cuts[(original['profile'],original['scene'])]
                    cut_operands=cut['bands']['fine'] if stratum=='T' else cut
                    require(cut_operands['native']==native and cut_operands['candidate']==current,
                            'W49a cut is not the declared fidelity operand')
                    epsilon=cut['code']
                    provenance['epsilon']=source_selector(pins['cut'],'T1.cells',identity[:3],field=['code'])
                else:
                    native,current=source['native'],source['current'];epsilon=source['repeat']['code']
                    provenance=source_selector(pins['canonical'],'partitions',identity,
                        statistic=substat,nativeField=['native'],currentField=['current'])
                    provenance['epsilon']=source_selector(pins['canonical'],'partitions',identity,
                        statistic=substat,field=['repeat','code'])
                add('t1',dict(dimensions,stratum=stratum),member(identity,substat,native,current,
                                                              provenance,epsilon=epsilon))
            continue
        if newbed:
            require(statistic in CHANNELS+LUMA,'Unknown priced new-bed level statistic')
            row=completed[identity];names=(statistic,)
        else:
            require(statistic=='low-end-path-level','Unknown priced canonical level statistic')
            kind=data['scenes']['backgrounds'][scene['background']]['kind']
            require(kind in ('solid','impulse'),'Canonical level has no declared solid/impulse support')
            row=canonical[identity];names=LUMA if kind=='impulse' else (CHANNELS[0],)
        for name in names:
            source=row if newbed else row['readings'][name]
            require(source['status']=='MEASURED','Level static reference is unmeasured')
            provenance=source_selector(pins['completed'] if newbed else pins['canonical'],
                'cells' if newbed else 'partitions',identity,statistic=name,
                nativeField=['native'],currentField=['current'])
            native,current=source['native'],source['current']
            if name in CHANNELS:
                require(isinstance(native,list) and isinstance(current,list) and
                        len(native)==len(current)==3,'RGB level requires all three source components')
                for component,n,c in zip(('R','G','B'),native,current):
                    add('level',dimensions,member(identity,name,n,c,copy.deepcopy(provenance),component))
            else:add('level',dimensions,member(identity,name,native,current,provenance))
    aggregates=[]
    for group in groups.values():
        members=sorted(group['members'],key=lambda m:
            (m['key'],m['statistic'],{None:0,'R':1,'G':2,'B':3}[m['component']]))
        require(len({(tuple(m['key']),m['statistic'],m['component']) for m in members})==len(members),
                'Duplicate aggregate substatistic/component')
        reductions=('max','mean') if group['kind']=='level' else ('median-log-ratio',)
        for reduction in reductions:
            dims=group['dimensions']
            label='/'.join(f'{k}={v}' for k,v in sorted(dims.items()))
            aggregates.append(dict(group,id=group['kind']+'/'+label+'/'+reduction,
                members=members,reduction=reduction,gate=group['kind']!='newbed-t1',timing=timing,
                membershipSha256=digest(members)))
    return {'schema':'w51-dl5-policy-1','dataOrigin':origin,
            'completePopulation':copy.deepcopy(pins['population']),'completeKeys':list(map(list,wanted)),
            'primaryT1GrowthMultiplier':2,'exceptions':copy.deepcopy(data['exceptions']),
            'aggregates':sorted(aggregates,key=lambda a:a['id']),
            'sources':unique_pins(pins.values())}


def validate_policy(policy,data):
    require(policy==derive_policy(data),'Policy differs from exact source-owned members/operands/definitions')
    return policy


def ensure_pre_gate(wave=WAVE):
    """Historical rehearsal markers do not grant permission to amend an actual gate."""
    slot=Path(wave)/'execution-slots/gate.json'
    try:slot.lstat()
    except FileNotFoundError:return
    raise ValueError('Actual gate slot exists; declaration additions are forbidden')


def validate_costs(costs,report,population):
    require(costs['schema']=='w51-dl5-declared-costs-1' and costs['dataOrigin']=='measured-native',
            'Costs are not the ruled real fit evidence')
    failed={key(r):r for r in report['cells'] if r['status']=='FAIL'}
    entries=costs['exceptions'];listed={tuple(e['key']):e for e in entries}
    require(len(listed)==len(entries)==len(failed)==22 and set(listed)==set(failed),
            'Declared costs must equal all 22 real-4 failed keys')
    require(set(listed)<={tuple(k) for k in population['statisticKeys']},'A cost is outside the original gate')
    for identity,entry in listed.items():
        row=failed[identity]
        comparisons=[{k:c[k] for k in ('rule','statistic')} | {'components':[
            component for component in c['comparison']['components'] if component['status']=='EXCEEDS']}
            for c in row['route']['checks'] if c['comparison']['status']=='EXCEEDS']
        readings={name:{k:source.get(k) for k in ('B','bar','candidate','code','current','native',
                                               'originalBudgetB','support','units')}
                  for name,source in row['readings'].items()}
        require(entry['measurement']==row['evidence'] and entry['readings']==readings and
                entry['failedComparisons']==comparisons,'Changed cost operand, component ceiling or source pin')
    return entries


def verify_previous():
    result=subprocess.run([sys.executable,'-I','-B',str(V2/'check.py')],capture_output=True,text=True)
    require(result.returncode==0,'Preserved declaration-v2 verification refused')


def frozen_inputs():
    """Follow the imported fit's static chain, never authenticate an old execution root."""
    frozen=load(V2/'inputs.json');original=read(frozen['sourceRootProvenance'])
    completed=next(x for x in frozen['restorableLiveInputs'] if
                   Path(x['required']['path']).name=='completed-references-r3.json')
    compressed=checked(completed['committedArchive']).read_bytes()
    require(hashlib.sha256(gzip.decompress(compressed)).hexdigest()==completed['required']['sha256'],
            'Completed reference archive is not the frozen pre-fit bytes')
    result=read(frozen['fitEvidence']['result']);path=frozen['fitEvidence']['result']['path']
    require(path.endswith('.json.result.json'),'Unknown immutable fit contract location')
    contract_pin={'path':path[:-len('.result.json')],'sha256':result['contractSha256']}
    contract=read(contract_pin)
    require(contract['phase']=='fit' and
            contract['executionRootSha256']==frozen['sourceRootProvenance']['sha256'] and
            contract['batch']['sha256']==frozen['fitEvidence']['batch']['sha256'],
            'Pre-fit authority is not the imported fixed completed fit')
    prefit_pin=contract['preFitEvidence'];prefit=read(prefit_pin)
    proof_pin=prefit['evidence']['dark05Bands'];proof=read(proof_pin)
    config_pin=original['instruments']['measurement']['config'];config=read(config_pin)
    canonical_pin=config['canonicalReferenceEvidence']
    require(proof['status']=='PASS' and proof['kind']=='dark05Bands' and
            canonical_pin in proof['sources'] and prefit['references'] in proof['sources'] and
            same_pin(prefit['references'],completed['required']),'Canonical references are not the pre-fit band proof')
    judge=read(original['instruments']['judge']['config']);target_pin=judge['targets']
    targets=read(target_pin);cut_pin=targets['cut'];read(cut_pin)
    population=load(V2/'gate-population.json');costs=load(HERE/'declared-costs.json')
    result_pin=pin(WAVE/'evidence/real-4-complete/journals/result.json')
    rehearsal=read(result_pin)
    require(costs['rehearsalReport']==rehearsal['report'] and rehearsal['judgeCompleted'] is True and
            rehearsal['status']=='NEITHER' and
            rehearsal['identity']['population']==sha(V2/'rehearsal-population.json') and
            rehearsal['identity']['root']==sha(WAVE/'execution-root.rehearsal4.json'),
            'Declared costs are not the preserved completed real-4 rehearsal')
    report=read(costs['rehearsalReport']);exceptions=validate_costs(costs,report,population)
    for entry in exceptions:checked(entry['measurement'])
    real_pins={'population':pin(V2/'gate-population.json'),'inventory':original['references'],
        'completed':completed['committedArchive'],'canonical':canonical_pin,'cut':cut_pin,
        'manifest':original['manifest'],'scenes':pin(REPO/'apps/reference-apple/scenes.json'),
        'costs':pin(HERE/'declared-costs.json'),'costReport':costs['rehearsalReport'],
        'priorInputs':pin(V2/'inputs.json'),'sourceRoot':frozen['sourceRootProvenance'],
        'fitContract':contract_pin,'preFitEvidence':prefit_pin,'bandProof':proof_pin,
        'targets':target_pin,'rehearsalResult':result_pin}
    real_pins.update({'costMeasurement'+str(i):entry['measurement'] for i,entry in enumerate(exceptions)})
    data={'dataOrigin':'measured-native','population':population,'inventory':read(real_pins['inventory']),
        'completed':read(real_pins['completed']),'canonical':read(canonical_pin),'cut':read(cut_pin),
        'manifest':read(real_pins['manifest']),'scenes':read(real_pins['scenes']),
        'reportedKeys':original['reportedKeys'],'exceptions':exceptions,'pins':real_pins}
    synthetic=WAVE/'synthetic/generated'
    synth_pins={name:pin(synthetic/file) for name,file in
        (('population','population.json'),('inventory','inventory.json'),
         ('completed','completed-references.json'),('canonical','canonical-reference-evidence.json'),
         ('manifest','native-manifest.json'),('scenes','scenes.json'),('fixture','fixture.json'))}
    # The synthetic target config records the generated cut's actual name.
    target=load(synthetic/'targets-config.json');synth_pins['cut']=target['cut']
    fixture=read(synth_pins['fixture'])
    require(all(any(checked(p)==checked(member) and p['sha256']==member['sha256']
                    for member in fixture['files']) for p in
                    (synth_pins['inventory'],synth_pins['canonical'],synth_pins['population'])),
            'Synthetic operands are outside the sealed fixture')
    synth={'dataOrigin':'synthetic','reportedKeys':[],'exceptions':[], 'pins':synth_pins,
           **{name:read(synth_pins[name]) for name in
              ('population','inventory','completed','canonical','cut','manifest','scenes')}}
    return data,synth,frozen


def retained_artifacts():
    paths=[*sorted((WAVE/'declaration').glob('*')),*sorted(V2.glob('*')),
           *sorted(WAVE.glob('charter-seal*.json')),*sorted(WAVE.glob('execution-root*.json')),
           *sorted(WAVE.glob('execution-root*.json.sha256'))]
    return [pin(p) for p in paths if p.is_file()]


def write_once(path,value):
    with ordinary(path).open('xb') as handle:handle.write(encoded(value))


def build():
    ensure_pre_gate();verify_previous()
    real,synthetic,frozen=frozen_inputs()
    policies=[derive_policy(data) for data in (real,synthetic)]
    retained=retained_artifacts()
    for name,policy in zip(('real','synthetic'),policies):
        write_once(HERE/('landing-policy.'+name+'.json'),policy)
    policy_pins={name:pin(HERE/('landing-policy.'+name+'.json')) for name in ('real','synthetic')}
    amendment={'schema':'w51-dl5-content-amendment-1','ruling':pin(HERE/'ruling.txt'),
        'clarifications':pin(HERE/'clarifications.txt'),
        'declaredCosts':pin(HERE/'declared-costs.json'),'heldDeclaration':pin(V2/'membership-witness.json'),
        'heldScientificIdentities':{k:copy.deepcopy(frozen[k]) for k in ('candidate','fitEvidence')},
        'heldPopulations':{phase:pin(V2/(phase+'-population.json')) for phase in ('gate','exposure','rehearsal')},
        'retainedArtifacts':retained,'landingPolicies':policy_pins,
        'preGateAttestation':{'actualGateSlotAbsent':True,'namespace':str(WAVE)},
        'informedBy':'Non-blind real fit840; 501 non-fit gate cells remain unread',
        'exceptionKeysSha256':digest([e['key'] for e in real['exceptions']])}
    write_once(HERE/'amendment.json',amendment)
    files={p.name:pin(p) for p in HERE.iterdir() if p.is_file() and p.name!='membership-witness.json'}
    witness={'schema':'w51-membership-witness-3','ruling':'W51-DL5','files':files,
             'counts':{name:{'aggregates':len(p['aggregates']),
                            'completeKeys':len(p['completeKeys']),'exceptions':len(p['exceptions'])}
                       for name,p in zip(('real','synthetic'),policies)}}
    write_once(HERE/'membership-witness.json',witness)
    print('W51 DL5 declaration generated; no seal, capture or clearance.')


if __name__=='__main__':build()
