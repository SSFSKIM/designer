"""Content-bound static scientific evidence, independent of historical execution shells."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[4]
KEY = ('profile','renderer','scene','statistic')


def pinned_bytes(item, repo=REPO):
    path = Path(repo)/item['path']
    if path.resolve() != path or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Static scientific input is not an ordinary bound location')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != item['sha256']: raise ValueError('Changed static scientific input')
    return raw


def read(item, repo=REPO):
    raw = pinned_bytes(item, repo)
    return json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)


def declaration_authority(root, seal):
    directory = (Path(root['repo'])/root['charter']['path']).parent/'declaration-v3'
    pins = [p for p in seal['artifacts'] if (Path(root['repo'])/p['path']).is_relative_to(directory)]
    if not pins: raise ValueError('Landing policy lacks its sealed declaration artifacts')
    return pins


def landing_policy_pins(root, science):
    """The small declaration authorities rehashed throughout a live capability's lifetime.

    Source operands stay registered static inputs. Their scientific reconstruction belongs to
    the pre-seal declaration checker, not to a runtime reader of known candidate payloads.
    """
    seal = read(root['charter'], root['repo'])
    policy = read(science['landingPolicy'], root['repo'])
    pins = [root['charter'], science['landingPolicy'], policy['completePopulation'],
            science['instruments']['judge']['config'], *declaration_authority(root, seal)]
    return list({(p['path'], p['sha256']):p for p in pins}.values())


def bound_landing_policy(root, science, inputs):
    """Authenticate the prospective rule through its seal, dataset, config and membership."""
    repo = root['repo']
    seal = read(root['charter'], repo)
    origin = science.get('dataOrigin')
    name = {'measured-native':'real', 'synthetic':'synthetic'}.get(origin)
    item = science.get('landingPolicy')
    if name is None or not isinstance(item, dict) or item != seal.get('landingPolicies', {}).get(name):
        raise ValueError('Landing policy differs from its sealed dataset authority')
    policy = read(item, repo)
    config_pin = science['instruments']['judge']['config']
    if read(config_pin, repo).get('landingPolicy') != item:
        raise ValueError('Judge config differs from dataset landing policy')
    if policy.get('schema') != 'w51-dl5-policy-1' or policy.get('dataOrigin') != origin:
        raise ValueError('Landing policy belongs to another dataset')
    complete = policy['completePopulation']
    population_name = 'gate' if name == 'real' else 'synthetic-rehearsal'
    binding = root['populations'][population_name]
    if binding['dataset'] != name or complete != binding['manifest']:
        raise ValueError('Landing policy changed its complete population')
    population = read(complete, repo)
    keys = population['statisticKeys']
    if policy.get('completeKeys') != keys or len({tuple(k) for k in keys}) != len(keys):
        raise ValueError('Landing policy differs from declared complete membership')
    required = [root['charter'], config_pin, item, complete, *policy['sources'],
                *declaration_authority(root, seal)]
    if (item not in seal['artifacts'] or complete not in seal['artifacts'] or
            any(p not in seal['artifacts'] for p in policy['sources'] + declaration_authority(root, seal)) or
            any(p not in registered for p in required for registered in
                (root['inputs'], science['inputs'], inputs))):
        raise ValueError('Unregistered landing policy declaration authority')
    # Small declaration bytes, never the reconstruction builder or historical gate evidence.
    for pin in declaration_authority(root, seal): pinned_bytes(pin, repo)
    if policy.get('primaryT1GrowthMultiplier') != 2 or (name == 'synthetic' and policy['exceptions']):
        raise ValueError('Landing policy changed the declared rule')
    ids = set(); complete_keys = {tuple(k) for k in keys}
    for group in policy['aggregates']:
        members = group['members']
        raw = (json.dumps(members, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
        identities = [(tuple(m['key']), m['statistic'], m['component']) for m in members]
        if (group['id'] in ids or not members or len(set(identities)) != len(identities) or
                any(key not in complete_keys for key, _, _ in identities) or
                hashlib.sha256(raw).hexdigest() != group['membershipSha256']):
            raise ValueError('Landing policy aggregate membership changed')
        ids.add(group['id'])
    return policy


def bound_numerical_inventory(root, science, inputs):
    """The fixed numerical fit owns argument membership; a dataset owns repeat statistics."""
    item=root.get('numericalInventory')
    if (not isinstance(item,dict) or item!=science.get('numericalInventory') or
            any(item not in registered for registered in (root['inputs'],science['inputs'],inputs))):
        raise ValueError('Unbound numerical argument inventory')
    report=read(root['numerical'],root['repo'])
    if item!=report.get('referenceInventory'):
        raise ValueError('Numerical argument inventory differs from the imported fixed referee')
    return read(item,root['repo'])


def numerical_inventory(context):
    live=sys.modules['w50_g1_dispatch'];live.require_context(context)
    return bound_numerical_inventory(live.sealed(context['executionRoot']),
                                    live.scientific_inputs(context),context['inputs'])


def same_pin(a, b, repo):
    return (Path(repo)/a['path'] == Path(repo)/b['path'] and a['sha256'] == b['sha256'])


def prefit_canonical_authority(root):
    """Follow content witnesses from the completed fit, never execute an old root's admission."""
    repo=root['repo'];charter=read(root['charter'],repo)
    if root['importedFit'] not in charter['artifacts']:
        raise ValueError('Canonical pre-fit authority is not the charter-bound imported fit')
    frozen=read(root['importedFit'],repo)
    fit_pin=frozen['fitEvidence']['result'];result=read(fit_pin,repo)
    path=fit_pin['path']
    if not path.endswith('.json.result.json'):raise ValueError('Unknown pre-fit contract location')
    contract_pin={'path':path[:-len('.result.json')],'sha256':result['contractSha256']}
    contract=read(contract_pin,repo)
    if (contract.get('phase')!='fit' or
            contract['executionRootSha256']!=frozen['sourceRootProvenance']['sha256'] or
            contract['batch']['sha256']!=frozen['fitEvidence']['batch']['sha256']):
        raise ValueError('Canonical pre-fit authority is not the imported completed fit')
    prefit_pin=contract['preFitEvidence'];prefit=read(prefit_pin,repo)
    proof_pin=prefit['evidence']['dark05Bands'];proof=read(proof_pin,repo)
    if (proof.get('schema')!='w50-prefit-proof-1' or proof.get('kind')!='dark05Bands' or
            proof.get('status')!='PASS' or prefit['references'] not in proof['sources']):
        raise ValueError('Canonical pre-fit band proof is not the sealed successful reference')
    return [contract_pin,prefit_pin,proof_pin],proof


def canonical_authority(root, science, config):
    """A registered replacement is not a pre-fit reference or a declared synthetic fixture."""
    repo=root['repo'];item=config['canonicalReferenceEvidence']
    if science['dataOrigin']=='synthetic':
        charter=read(root['charter'],repo)
        if root['syntheticFixture'] not in charter['artifacts']:
            raise ValueError('Canonical authority is not the sealed synthetic fixture')
        fixture=read(root['syntheticFixture'],repo)
        if fixture.get('dataOrigin')!='synthetic' or any(not any(same_pin(pin,p,repo)
                for p in fixture['files']) for pin in (item,science['references'])):
            raise ValueError('Canonical reference differs from the sealed synthetic fixture')
    elif science['dataOrigin']=='measured-native':
        pins,proof=prefit_canonical_authority(root)
        if any(not any(same_pin(pin,p,repo) for p in proof['sources'])
                for pin in (item,science['references'])):
            raise ValueError('Canonical reference differs from the imported pre-fit band proof')
        if any(pin not in inputs for pin in pins for inputs in (root['inputs'],science['inputs'])):
            raise ValueError('Canonical pre-fit authority is not registered')
    else:raise ValueError('Unknown canonical reference authority')


def native_batch(context, config):
    live = sys.modules['w50_g1_dispatch']; live.require_context(context)
    if config['batch'] not in context['inputs']: raise ValueError('Unbound exposed native batch')
    batch = read(config['batch'], context['repo'])
    if batch.get('schema') != 'w50-native-read-batch-1' or any(
            e['role'] not in ('calibration','validation') for e in batch['exports']):
        raise ValueError('Static native repeat source must be entirely exposed')
    return batch


def canonical_pair(config, rows):
    """Use the prospectively pinned reference's actual seven frames, not a source-root replay.

    The source bundle preserves the original report/row and every original frame hash. For a
    synthetic dataset that same schema names its independently generated seven reference frames.
    No historical current image is opened to qualify a fresh pair.
    """
    report = read(config['referenceEvidence'])
    indexed = {tuple(r[k] for k in KEY):r for group in report['partitions'].values() for r in group}
    selected = [indexed[tuple(r[k] for k in KEY)] for r in rows if r['statistic'] != 'owner-contracts']
    if not selected: raise ValueError('Canonical repeat lacks declared statistic references')
    for row in rows:
        if row['statistic'] != 'owner-contracts' and indexed[tuple(row[k] for k in KEY)]['reference'] != row:
            raise ValueError('Canonical repeat reference changed original operands')
    first = selected[0]; pins = first['pins']; runs = first['runs']
    if len(runs) != 7 or any(len(item['runs']) != 7 or any(item['pins'][k] != pins[k]
            for k in ('native','background','scenes')) or item['runs'] != runs for item in selected):
        raise ValueError('Canonical repeat companions disagree on native supports or seven frames')
    scenes = read(pins['scenes'])
    if config['scenes']['sha256'] != pins['scenes']['sha256'] or read(config['scenes']) != scenes:
        raise ValueError('Canonical repeat scene bytes differ from dataset declaration')
    scene = next(s for s in scenes['scenes'] if s['id'] == first['scene'])
    match = re.fullmatch(r'apple-macos-27\.0-([12])x-dark-standard-glass(0\.25|0\.5)',first['profile'])
    if not match: raise ValueError('Unknown canonical reference scale/position')
    return {'scenes':scenes,'scene':scene,'scale':int(match[1]),'native':pins['native'],
            'background':pins['background'],'runs':runs,'provenance':{
                'native':copy.deepcopy(pins['native']),'background':copy.deepcopy(pins['background']),
                'scenes':copy.deepcopy(pins['scenes']),'referenceEvidence':copy.deepcopy(config['referenceEvidence']),
                'source':first['source'],'runs':copy.deepcopy(runs)}}
