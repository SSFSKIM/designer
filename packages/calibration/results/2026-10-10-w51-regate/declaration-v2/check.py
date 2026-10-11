"""Read-only verification of W51's immutable scientific declaration inputs.

This checks source membership, content pins and candidate identity, not an execution seal.
It imports no W50 execution code and opens no capture, unread gate measurement or blind
native frame. The original inventory/root are metadata; the initializer is exposed fit data.
Run with python3 -I -B check.py. Source provenance is historical, not a W51 source closure.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FIELDS = ('profile', 'renderer', 'scene', 'statistic')
PHASES = ('gate', 'exposure', 'rehearsal')


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    def invalid(_):
        raise ValueError('Nonfinite JSON constant in declaration metadata')
    return json.loads(Path(path).read_bytes(), parse_constant=invalid)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def physical(keys):
    return sorted({tuple(k[:3]) for k in keys})


def validate_membership(root, inventory, fit_batch, populations):
    """Pure original-key equality, including every statistic companion on each physical cell."""
    by = {tuple(row[k] for k in FIELDS): row for row in inventory['cells']}
    require(len(by) == len(inventory['cells']), 'Duplicate original inventory key')
    gate = sorted(tuple(k) for k in root['phaseDependencies']['gateKeys'])
    exposure = sorted(tuple(k) for k in root['phaseDependencies']['exposureKeys'])
    require(set(gate).isdisjoint(exposure), 'Gate/exposure statistic keys overlap')
    require(set(physical(gate)).isdisjoint(physical(exposure)), 'Gate/exposure physical cells overlap')
    require(set(gate)|set(exposure) == set(by), 'Gate/exposure union differs from original inventory')
    fit = {(r['profile'], r['renderer'], scene) for r in fit_batch['runs'] for scene in r['scenes']}
    require(fit <= set(physical(gate)), 'Original fit contains a non-gate physical cell')
    rehearsal = [k for k in gate if k[:3] in fit]
    expected = dict(gate=gate, exposure=exposure, rehearsal=rehearsal)
    require(set(populations) == set(PHASES), 'Unexpected declaration population')
    for phase, wanted in expected.items():
        doc = populations[phase]
        require(doc['schema'] == 'w51-population-1' and doc['phase'] == phase,
                'Population schema/phase mismatch')
        actual = [tuple(k) for k in doc['statisticKeys']]
        require(actual == wanted and len(actual) == len(set(actual)), 'Original statistic keys differ')
        require([tuple(k) for k in doc['physicalCells']] == physical(wanted), 'Physical projection differs')
        require(doc['physicalCount'] == len(physical(wanted)) and doc['statisticCount'] == len(wanted),
                'Population count differs')
        metadata = [dict(zip(FIELDS, k), role=by[k]['role'], support=by[k]['support'],
                         sceneSource='w50' if by[k].get('nativeIdentity') else 'canonical') for k in wanted]
        require(doc['originalMetadata'] == metadata, 'Original metadata changed or relabelled')
    require(len(fit) == 840 and len(rehearsal) == 1856 and len(physical(rehearsal)) == 840,
            'Real rehearsal no longer equals original fit840 only')
    require(set(physical(rehearsal)) == fit, 'Non-fit real gate identity reached rehearsal')
    withheld = {(g['profile'], g['scene']) for g in root['phaseDependencies']['groups'] if g['withheldKeys']}
    require(not {(p, s) for p, _, s in physical(rehearsal)} & withheld,
            'Withheld physical dependency reached rehearsal')
    require(not any(by[k]['role'] in ('blind', 'historical-prediction-check') for k in rehearsal),
            'Withheld original role reached rehearsal')
    doc = populations['rehearsal']
    require(doc['additions'] == {} and doc['populationClass'] == 'REAL_FIT_ONLY',
            'Real rehearsal includes additions or relabels a real cell as synthetic')
    for field, original in (('reportedKeys', 'reportedKeys'), ('eligibleEmptySupportKeys', 'emptySupportKeys')):
        require(doc['coverage'][field] == len(set(rehearsal)&{tuple(k) for k in root[original]}),
                'Optional-statistic coverage differs')


def validate_amendment(amendment, inputs, real, previous):
    """Validate the DL3 removal and bounded historical pre-pixel attestation, not a live census."""
    require(amendment['schema'] == 'w51-prepixel-amendment-1' and amendment['ruling'] == 'W51-DL3',
            'Amendment does not name DL3')
    require(amendment['heldScientificIdentities'] == {
        'candidate': inputs['candidate'], 'fitEvidence': inputs['fitEvidence']},
        'Amendment changes the frozen candidate or fit')
    real_cells = {tuple(k) for k in real['physicalCells']}
    removed_cells = [k for k in previous['physicalCells'] if tuple(k) not in real_cells]
    removed_keys = [k for k in previous['statisticKeys'] if tuple(k[:3]) not in real_cells]
    require(len(removed_cells) == 12 and len(removed_keys) == 24 and
            amendment['removedRealPhysicalCells'] == removed_cells and
            amendment['removedRealStatisticKeys'] == removed_keys, 'Amendment removal differs')
    require(amendment['counts'] == {'previousRealRehearsal': [852, 1880], 'realRehearsal': [840, 1856],
                                  'protectedNonfitGate': 501, 'gate': [1341, 2553], 'exposure': [322, 974]},
            'Amendment population counts differ')
    require(amendment['syntheticPopulation']['status'] == 'SEPARATE_NOT_DECLARED_HERE' and
            amendment['syntheticPopulation']['realCellsRelabelled'] is False,
            'Real scientific identities were relabelled synthetic')
    state = amendment['prePixelAttestation']
    require(state['namespaceDirectories'] == ['g0'] and state['executionRootDocuments'] == [] and
            state['captureOrAnalysisMarkers'] == [] and state['noW51ExecutionRootSealed'] is True and
            state['noW51OutputDirectoriesInReservedNamespace'] is True and
            state['noW51PixelsOrAnalysisMarkersInSource'] is True and
            state['excludesHistoricalW50Artifacts'] is True, 'Pre-pixel attestation contains execution state')


def checked(item):
    path = Path(item['path'])
    require(path.is_absolute() and path.resolve() == path and path.is_relative_to(REPO),
            'Content pin is outside this checkout or resolves through a symlink')
    require(path.is_file() and digest(path.read_bytes()) == item['sha256'], 'Content pin mismatch')
    return path


def main():
    witness = load(HERE/'membership-witness.json')
    require(witness['schema'] == 'w51-membership-witness-2' and witness['ruling'] == 'W51-DL3',
            'Membership witness does not name the DL3 amendment')
    for name, item in witness['files'].items():
        require(Path(item['path']) == HERE/name, 'Witness names another declaration file')
        checked(item)
    inputs = load(HERE/'inputs.json')
    provenance = load(HERE/'provenance.json')
    root_path = checked(witness['sourceRoot'])
    inventory_path = checked(witness['sourceInventory'])
    require(inputs['sourceRootProvenance'] == witness['sourceRoot'] == provenance['sourceRoot'],
            'Original membership root differs across declaration files')
    for item in inputs['staticInputs']:
        checked(item)
    for item in provenance['sources']+provenance['populationSources']:
        checked(item)
    for item in inputs['restorableLiveInputs']:
        raw = gzip.decompress(checked(item['committedArchive']).read_bytes())
        require(digest(raw) == item['required']['sha256'] == item['decompressedSha256'],
                'Restorable input archive has different bytes')
    candidate = inputs['candidate']
    initializer = load(checked(candidate['initializer']))
    proposal = digest(json.dumps(initializer, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())
    require(proposal == candidate['proposalDigest'], 'Proposal digest differs from frozen initializer')
    for member in candidate['cohort']:
        checked(member['declaration'])
        for item in member['documents'].values():
            checked(item)
    fit = inputs['fitEvidence']
    for field in ('record', 'batch', 'result', 'captureUnion'):
        checked(fit[field])
    result = load(Path(fit['result']['path']))
    record = load(Path(fit['record']['path']))
    require(result['report']['status'] == fit['status'] == 'CAPTURED' and
            len(result['captures']['captures']) == fit['physicalCount'] == 840,
            'Frozen fit completion differs')
    require(record['completed'][0]['sha256'] == fit['result']['sha256'] and
            result['captureUnion']['sha256'] == fit['captureUnion']['sha256'], 'Fit evidence links differ')
    populations = {phase: load(HERE/(phase+'-population.json')) for phase in PHASES}
    root, inventory = load(root_path), load(inventory_path)
    validate_membership(root, inventory, load(Path(fit['batch']['path'])), populations)
    require(populations['rehearsal']['sourceFitBatch'] == fit['batch'], 'Real rehearsal names another fit')
    amendment = load(HERE/'amendment.json')
    require(amendment['realRehearsal'] == witness['files']['rehearsal-population.json'],
            'Amendment names another successor rehearsal')
    previous = load(checked(amendment['supersedesRealRehearsal']))
    validate_amendment(amendment, inputs, populations['rehearsal'], previous)
    for item in amendment['retainedPreviousArtifacts']:
        checked(item)
    copied = amendment['byteIdenticalCopies']
    require({Path(p['successor']['path']).name for p in copied} == {
        'inputs.json', 'gate-population.json', 'exposure-population.json', 'provenance.json'},
        'Amendment changed the set of held declaration files')
    for item in copied:
        require(item['previous']['sha256'] == item['successor']['sha256'] and
                checked(item['previous']).read_bytes() == checked(item['successor']).read_bytes(),
                'Held scientific declaration bytes differ')
    for phase, doc in populations.items():
        require(doc['sourceRoot'] == witness['sourceRoot'] and doc['sourceInventory'] == witness['sourceInventory'],
                'Population source provenance differs')
        require(witness['counts'][phase] == {'physical': doc['physicalCount'], 'statistics': doc['statisticCount']},
                'Witness population count differs')
        require(witness['identityArraySha256'][phase] == {
            field: digest(encoded(doc[field])) for field in ('physicalCells', 'statisticKeys')},
            'Witness identity-array hash differs')
    require(all(v is True for v in witness['checks'].values()), 'Membership witness contains a failed check')
    print('W51 DL3 declaration intact: gate 1341/2553, exposure 322/974, real rehearsal 840/1856; synthetic separate; no execution seal.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('W51 declaration refused: '+str(error), file=sys.stderr)
        raise SystemExit(1)
