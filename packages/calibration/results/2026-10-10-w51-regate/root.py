"""W51's literal root and explicit population authority; no historical execution admission."""
import argparse
import copy
import hashlib
import gzip
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
FIT = HERE.parent/'2026-10-08-w50-g1-fit'
CURRENT = HERE.parent/'2026-10-08-w50-g1-current3'
KEY = ('profile', 'renderer', 'scene', 'statistic')
POPULATIONS = ('real-rehearsal', 'synthetic-rehearsal', 'gate')


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(encoded(value)).hexdigest()


def load(path):
    def invalid(_): raise ValueError('Nonfinite JSON')
    raw=Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw, parse_constant=invalid)


def source(path, name):
    path = Path(path).resolve()
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def ordinary(path):
    path = Path(path).absolute()
    if path.resolve() != path or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Symlink or noncanonical evidence path')
    return path


def checked(repo, item):
    path = ordinary(Path(repo)/item['path'])
    if not path.is_file() or sha(path) != item['sha256']:
        raise ValueError('Changed content pin: '+str(path))
    return path


def pin(path):
    path = ordinary(path)
    return {'path': str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),
            'sha256': sha(path)}


def sealed(path):
    path = ordinary(path)
    if Path(str(path)+'.sha256').read_text() != f'{sha(path)}  {path.name}\n':
        raise ValueError('Changed document seal')
    return load(path)


def population_dependencies(rows, dependencies, population):
    """Keep the full owner/exposure authority; restrict only this run's exposed gate keys."""
    physical = [tuple(k) for k in population['physicalCells']]
    keys = [tuple(k) for k in population['statisticKeys']]
    if (len(physical) != len(set(physical)) or len(keys) != len(set(keys)) or
            len(physical) != population['physicalCount'] or len(keys) != population['statisticCount']):
        raise ValueError('Duplicate or inconsistent population')
    withheld = {(g['profile'], g['scene']) for g in dependencies['groups'] if g['withheldKeys']}
    if any((p, s) in withheld for p, _, s in physical):
        raise ValueError('A withheld physical dependency reached gate execution')
    wanted = {tuple(r[k] for k in KEY) for r in rows if tuple(r[k] for k in KEY[:3]) in set(physical)}
    if set(keys) != wanted or {k[:3] for k in keys} != set(physical):
        raise ValueError('Population omitted or invented an original companion')
    if not set(keys) <= {tuple(k) for k in dependencies['gateKeys']}:
        raise ValueError('Population lies outside original exposed gate')
    result = copy.deepcopy(dependencies)
    result['gateKeys'] = [k for k in dependencies['gateKeys'] if tuple(k) in set(keys)]
    return result


def dataset(doc, name):
    if name not in POPULATIONS: raise ValueError('Exposure is not an executable W51 population')
    binding = doc['populations'][name]
    item = doc['datasets'][binding['dataset']]
    if item not in doc['inputs']: raise ValueError('Dataset is not a prospective root input')
    value = load(checked(doc['repo'], item))
    if value['repo'] != doc['repo'] or value['closure'] != doc['closure']:
        raise ValueError('Dataset differs from actual root environment/source closure')
    if any(pin not in doc['inputs'] for pin in value['inputs']):
        raise ValueError('Dataset input is not a root input')
    return value


def population_authority(doc, name):
    science = dataset(doc, name)
    population = load(checked(doc['repo'], doc['populations'][name]['manifest']))
    rows = load(checked(doc['repo'], science['references']))['cells']
    dependencies = population_dependencies(rows, science['phaseDependencies'], population)
    expected = [{k: r[k] for k in KEY} for r in rows
                if tuple(r[k] for k in KEY) in {tuple(k) for k in population['statisticKeys']}]
    return population, dependencies, expected


def validate_context_population(context, doc, science):
    """Judge's changed authority seam: authenticate a literal dataset and its population."""
    actual = dataset(doc, context['population'])
    _, dependencies, expected = population_authority(doc, context['population'])
    binding = doc['populations'][context['population']]
    if (science != actual or context['datasetPin'] != doc['datasets'][binding['dataset']] or
            context['populationPin'] != binding['manifest'] or
            context['phaseDependencies'] != dependencies or context['expectedCells'] != expected):
        raise ValueError('Context changed its declared population authority')


def prepare(root_path, population, output):
    """Read-only complete root admission. The caller fences before calling this function."""
    path = ordinary(root_path)
    return validate_body(path, sealed(path), population, output)


def validate_body(path, doc, population, output):
    """Shared draft/root admission; it grants no context or execution capability."""
    path = ordinary(path)
    if (doc.get('schema') != 'w51-execution-root-1' or Path(doc['repo']) != REPO or
            doc.get('rootPath') != str(path)):
        raise ValueError('Wrong W51 root')
    for item in doc['inputs']: checked(REPO, item)
    for relative, expected in doc['closure']['sources'].items():
        checked(REPO, {'path': relative, 'sha256': expected})
    if doc['charter']!=pin(HERE/'charter-seal-dl5.json'):
        raise ValueError('Root must bind the approved W51 declaration')
    verify_charter(doc['charter'])
    if doc['populations']!=load(checked(REPO,doc['charter']))['populations']:
        raise ValueError('Named population bindings differ from the sealed charter')
    differential=source(HERE/'semantics.py', 'w51_semantic_admission').verify()
    if load(checked(REPO,doc['sourceDifferential']))!=differential:
        raise ValueError('Recorded scientific source differential changed')
    verify_imported_fit(doc)
    science = dataset(doc, population)
    static=source(HERE/'static.py','w51_static_admission')
    static.bound_numerical_inventory(doc,science,science['inputs'])
    static.bound_landing_policy(doc,science,science['inputs'])
    static.canonical_authority(doc,science,load(checked(REPO,science['measurementConfig'])))
    if set(science['instruments'])!={'capture','measurement','judge'}:
        raise ValueError('W51 exposes exactly three scientific roles')
    for role,component in science['instruments'].items():
        if checked(REPO,component['entrypoint'])!=HERE/(role+'.py'):
            raise ValueError('Scientific role bypasses the prospective instrument')
    manifest, dependencies, expected = population_authority(doc, population)
    batch = load(checked(REPO, doc['batches'][population]))
    if batch['phase'] != 'gate' or batch['cohort'] != doc['cohort']:
        raise ValueError('Batch changed frozen candidate or judge phase')
    actual = [(r['profile'], r['renderer'], s) for r in batch['runs'] for s in r['scenes']]
    if len(actual) != len(set(actual)) or set(actual) != {tuple(k) for k in manifest['physicalCells']}:
        raise ValueError('Batch changed fixed physical population')
    if any(r['candidate'] not in doc['cohort'] or r['numericalReferee'] != doc['numerical']
           for r in batch['runs']):
        raise ValueError('Run changed frozen candidate/numerical admission')
    destination = ordinary(output)
    if destination.is_relative_to(REPO): raise ValueError('Execution output must be external')
    verify_web_sources(doc, batch)
    for run in batch['runs']:
        if run['webSourceClosure'] not in science['inputs']:
            raise ValueError('Run source closure is not dataset-bound')
        if run['sceneSource'] == 'canonical' and run['scenesDocument'] != science['scenes']:
            raise ValueError('Run selected another canonical scene document')
        transport = source(HERE/'canonical/adapter.py' if run['sceneSource']=='canonical' else
                           CURRENT/'web/adapter.py', 'w51_metadata_transport')
        transport.scene_plan(run, 'gate')
    return {'root': doc, 'rootPath': str(path), 'population': population, 'manifest': manifest,
            'populationPin':doc['populations'][population]['manifest'], 'dataset':science,
            'datasetPin':doc['datasets'][doc['populations'][population]['dataset']],
            'batch': batch, 'batchPath': str(checked(REPO, doc['batches'][population])),
            'expectedCells': expected, 'phaseDependencies': dependencies, 'output': str(destination)}


def verify_web_sources(doc, batch):
    observed=set()
    for run in batch['runs']:
        item=run['webSourceClosure']
        if item['sha256'] in observed:continue
        observed.add(item['sha256'])
        if item not in doc['inputs']:raise ValueError('Renderer closure is not root-bound')
        for source_pin in load(checked(REPO,item))['sources']:checked(REPO,source_pin)


def verify_charter(item):
    import subprocess
    authority = load(checked(REPO,item)); charter = authority['charter']
    raw = subprocess.run(['git','-C',str(REPO),'show',charter['commit']+':'+charter['path']],
                         check=True,capture_output=True).stdout
    if hashlib.sha256(raw).hexdigest()!=charter['sha256']: raise ValueError('Committed charter differs')
    rule=authority['landingRule'];raw=checked(REPO,rule['source']).read_bytes()
    start=raw.index(rule['startHeading'].encode());end=raw.index(rule['endHeadingExclusive'].encode(),start)
    part=raw[start:end]
    if len(part)!=rule['bytes'] or hashlib.sha256(part).hexdigest()!=rule['sha256']:
        raise ValueError('Landing-rule byte slice differs')
    for item in authority['artifacts']: checked(REPO,item)


def verify_imported_fit(doc):
    if doc['importedFit']!=pin(HERE/'declaration-v2/inputs.json'):
        raise ValueError('Imported fit must be the unchanged W51 frozen-input declaration')
    frozen=load(checked(REPO,doc['importedFit']))
    candidate=frozen['candidate'];initializer=load(checked(REPO,candidate['initializer']))
    raw=json.dumps(initializer,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    if hashlib.sha256(raw).hexdigest()!=candidate['proposalDigest']:raise ValueError('Frozen initializer differs')
    if sorted(p['sha256'] for p in doc['cohort'])!=sorted(m['declaration']['sha256'] for m in candidate['cohort']):
        raise ValueError('Root selected a different frozen candidate')
    for member in candidate['cohort']:
        checked(REPO,member['declaration'])
        for item in member['documents'].values():checked(REPO,item)
    fit=frozen['fitEvidence']
    for name in ('record','batch','result','captureUnion'):checked(REPO,fit[name])
    record,result=load(checked(REPO,fit['record'])),load(checked(REPO,fit['result']))
    if (record['completed'][0]['sha256']!=fit['result']['sha256'] or result['report']['status']!='CAPTURED' or
            len(result['captures']['captures'])!=840 or result['captureUnion']['sha256']!=fit['captureUnion']['sha256']):
        raise ValueError('Imported fit is not the fixed completed 840-cell evidence')


def clearance(doc, population, path):
    value=load(path);binding=doc['populations'][population]
    if (value.get('rootSha256')!=sha(doc['rootPath']) or value.get('populationSha256')!=binding['manifest']['sha256'] or
            value.get('sourceClosureSha256')!=digest(doc['closure']) or value.get('purpose')!=population or
            not value.get('reviewEvidence')):
        raise ValueError('Missing or mismatched coordinator clearance')
    reviews=[load(checked(REPO,p)) for p in value['reviewEvidence']]
    if population=='gate':
        if not any(r.get('kind')=='reviewer-high' and r.get('status')=='APPROVE' and
                   r.get('rootSha256')==value['rootSha256'] for r in reviews):
            raise ValueError('Gate requires exact-root high-review clearance')
        if set(value.get('rehearsals',{}))!={'real-rehearsal','synthetic-rehearsal'}:
            raise ValueError('Gate needs both completed rehearsals')
        journal=source(HERE/'journal.py','w51_clearance_journal')
        for name,pin in value['rehearsals'].items():
            result=load(checked(REPO,pin));output=Path(pin['path']).parent
            if (journal.terminal(output)!=result or result.get('judgeCompleted') is not True or
                    result['identity']['root']!=value['rootSha256'] or
                    result['identity']['population']!=doc['populations'][name]['manifest']['sha256']):
                raise ValueError('Rehearsal completion is not this exact root/population')
            if name=='real-rehearsal' and result['status']!='PASS_EXPOSED_OWNER_PENDING':
                raise ValueError('DL5 real rehearsal must PASS its per-cell clauses')
            witness=load(checked(REPO,result['witness']))
            if witness['sourceClosureSha256']!=value['sourceClosureSha256']:
                raise ValueError('Rehearsal source closure differs')
            expected=doc['populations'][name]
            if (witness['executionRoot']!={'path':doc['rootPath'],'sha256':value['rootSha256']} or
                    witness['population']!=expected['manifest'] or
                    witness['dataset']!=doc['datasets'][expected['dataset']]):
                raise ValueError('Rehearsal witness names another authority')
            marker_path=journal.checked(witness['analysisClaim'])
            if marker_path!=Path(str(output/'contract.json')+'.phase/analysis.started.json'):
                raise ValueError('Rehearsal has no own exclusive analysis marker')
            marker=load(marker_path);contract=load(journal.checked(marker['logicalContract']))
            union=load(journal.checked(witness['captureUnion']))
            population_doc=load(checked(REPO,expected['manifest']))
            members=[(r['member']['run']['profile'],r['member']['run']['renderer'],r['member']['scene'])
                     for r in union['members']]
            if (contract['executionRootSha256']!=value['rootSha256'] or marker['captures']!=witness['captureUnion'] or
                    union['logicalContract']!=marker['logicalContract'] or len(members)!=len(set(members)) or
                    set(members)!={tuple(k) for k in population_doc['physicalCells']} or
                    witness['physicalCount']!=population_doc['physicalCount'] or
                    witness['statisticCount']!=population_doc['statisticCount']):
                raise ValueError('Rehearsal marker/complete population witness differs')
            for member in union['members']:
                journal.checked(member['payload'])
                for artifact in member['artifacts']:journal.checked(artifact)
            if name=='synthetic-rehearsal' and (any(not witness['branches'].get(k)
                    for k in ('producerCarry','textBands')) or not any(
                    row.get('producer')=='CANONICAL_NUMPY_GAUSSIAN_LOW' for row in witness['branches']['textBands'])):
                raise ValueError('Synthetic rehearsal lacks actual producer/frozen-low/text branch evidence')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'verify'))
    parser.add_argument('--out', type=Path)
    parser.add_argument('--root', type=Path)
    args = parser.parse_args()
    if args.command == 'build':
        if args.out is None: parser.error('build needs --out (draft only, no seal)')
        source(HERE/'build.py', 'w51_build').build(args.out)
    else:
        if args.root is None: parser.error('verify needs --root')
        for population in POPULATIONS: prepare(args.root, population, Path('/tmp/w51-admission-only'))
        print('W51 root and both exposed population bindings verified; no execution.')

if __name__ == '__main__': main()
