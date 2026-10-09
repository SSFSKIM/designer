"""DL5e checks source-owned CURRENT owner evidence, never invents a scalar owner B.

Bounds, exclusions and reading shapes are data from owner/witness.ts's source-generated
snapshot. This checker binds that snapshot to G0's owner source, the prepared report and
its exact original row. It checks readable finite evidence, not whether a current miss is
within a fidelity bound. The original owner evaluator still owns candidate judgments.
"""
import gzip
import hashlib
import json
import math
import re
from pathlib import Path

AXES = {'M1', 'M2', 'C1', 'X1', 'L1', 'E2', 'coherence'}
INTRINSIC = {'X75', 'X76'}
KEY = ('profile', 'renderer', 'scene', 'statistic')


def same(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def at(value, path):
    for key in path.split('.'):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def finite_tree(value):
    if type(value) in (int, float) and not math.isfinite(value):
        raise ValueError('Nonfinite owner evidence')
    if isinstance(value, dict):
        for child in value.values(): finite_tree(child)
    elif isinstance(value, list):
        for child in value: finite_tree(child)


def require_numbers(value, paths):
    for path in paths:
        reading = at(value, path)
        if type(reading) not in (int, float) or not math.isfinite(reading):
            raise ValueError(f'Missing finite source-owned owner reading: {path}')


class OwnerEvidence:
    """One completion pass shares pinned reports; each file is rechecked at the end."""
    def __init__(self, repo, contracts, owner_source):
        self.repo = Path(repo).resolve()
        self.pins, self.json = {}, {}
        self.contracts_pin = contracts
        self.snapshot = self.read(contracts)
        source = self.check(owner_source, external=False)
        if self.snapshot.get('schema') != 'w50-owner-contracts-1' or \
                self.check(self.snapshot.get('ownerSource'), external=False) != source or \
                set(self.snapshot.get('axes', {})) != AXES or set(self.snapshot.get('intrinsic', {})) != INTRINSIC:
            raise ValueError('Owner snapshot/source/axis population differs from original owner contracts')
        readers = self.snapshot.get('readerSources')
        if not isinstance(readers, dict) or not readers:
            raise ValueError('Owner snapshot lacks source-owned reader pins')
        for pin in readers.values(): self.check(pin, external=False)
        finite_tree(self.snapshot)
        for axis in self.snapshot['axes'].values():
            if not axis.get('sourceSelectors') or any(not isinstance(axis.get(k), dict)
                    for k in ('limits', 'applicability', 'exclusions', 'readingSchema')):
                raise ValueError('Owner snapshot lacks limits, applicability, exclusions or reading schema')
            schema = axis['readingSchema']
            if any(not isinstance(schema.get(k), list) for k in
                   ('requiredFinite', 'requiredArrays', 'conditionalFinite', 'unmeasuredExceptions')) or \
                    'aggregate' not in schema:
                raise ValueError('Incomplete source-owned owner reading schema')

    def check(self, pin, external=True):
        if not isinstance(pin, dict) or not isinstance(pin.get('path'), str) or not isinstance(pin.get('sha256'), str):
            raise ValueError('Missing owner evidence content pin')
        path = (self.repo/pin['path']).resolve()
        if not external and not path.is_relative_to(self.repo):
            raise ValueError('Owner source escapes the repository')
        digest = pin['sha256']
        if path in self.pins:
            if self.pins[path] != digest: raise ValueError('Conflicting owner evidence pins')
        else:
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('Changed or missing owner evidence/source')
            self.pins[path] = digest
        return path

    def read(self, pin):
        path = self.check(pin)
        if path not in self.json:
            raw = path.read_bytes()
            self.json[path] = json.loads(gzip.decompress(raw) if path.name.endswith('.json.gz') else raw)
        return self.json[path]

    def all_pins(self, value):
        if isinstance(value, dict):
            if 'path' in value and 'sha256' in value: self.check(value)
            for child in value.values(): self.all_pins(child)
        elif isinstance(value, list):
            for child in value: self.all_pins(child)

    def axis(self, row, evidence, contract):
        if not isinstance(evidence, dict): raise ValueError('Missing owner axis evidence')
        finite_tree(evidence)
        state = evidence.get('state')
        if state == 'NOT_APPLICABLE':
            if not evidence.get('reason'): raise ValueError('Missing source-owned applicability reason')
            return
        schema = contract['readingSchema']
        if state == 'UNMEASURED':
            allowed = False
            for exception in schema['unmeasuredExceptions']:
                kind = exception.get('kind')
                if kind not in ('named-cell', 'diagnostic-only'):
                    raise ValueError('Unknown source-owned owner exception shape')
                if kind == 'named-cell' and (exception.get('identity') != 'profile/scene' or
                        f'{row["profile"]}/{row["scene"]}' not in exception.get('keys', [])):
                    continue
                equality = exception.get('evidenceEquals')
                if isinstance(equality, dict) and equality and all(
                        same(at(evidence, k), v) for k, v in equality.items()):
                    allowed = True
            if not allowed or not evidence.get('reason'):
                raise ValueError('Owner UNMEASURED has no matching source-owned exception')
            return
        if state != 'MEASURED': raise ValueError('Invalid owner evidence state')
        require_numbers(evidence, schema['requiredFinite'])
        for path in schema['requiredArrays']:
            value = at(evidence, path)
            if not isinstance(value, list) or not value:
                raise ValueError('Missing nonempty owner reading array')
            finite_tree(value)
        for rule in schema['conditionalFinite']:
            if not same(at(evidence, rule['unless']['field']), rule['unless']['equals']):
                require_numbers(evidence, rule['paths'])

    def bind_current_reference(self, row, source, matrix_input, inputs, cell_id):
        """Identity alone does not select a generation: bind both roles and actual pixels."""
        profile = re.fullmatch(r'apple-macos-27\.0-[12]x-(light|dark)-standard-glass0\.(25|5)', row['profile'])
        if not profile:
            raise ValueError('Owner current reference profile is outside its original material scope')
        pair = row.get('currentDocumentPair', {})
        scheme = profile[1]
        expected = {'materialProfile': pair.get(f'active.{scheme}'),
                    'recededProfile': pair.get(f'receded.{scheme}')}
        if any(not isinstance(v, str) or not re.fullmatch(r'[0-9a-f]{64}', v) for v in expected.values()):
            raise ValueError('Original owner reference lacks its full role-bound document pair')
        active, receded = expected['materialProfile'], expected['recededProfile']
        # Ordinary and receded-only generation identities are both evidence conventions.
        # The short name never substitutes for the full pair comparison below.
        if row.get('currentGeneration') not in (active[:12], active[:12]+'-'+receded[:12]):
            raise ValueError('Original owner generation identity differs from its document pair')
        web = source['key']['web']
        descriptors = re.findall(r'(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})(?![0-9a-f])',
                                 web.get('capturePath', ''))
        if len(descriptors) != 2 or {r[0] for r in descriptors} != set(expected):
            raise ValueError('Current matrix lacks exactly one descriptor for each document role')
        capture = inputs.get('captures', {}).get(cell_id)
        if not isinstance(capture, dict):
            raise ValueError('Owner current reference lacks its original captured evidence')
        for role, path, short in descriptors:
            digest = expected[role]
            if short != digest[:12] or matrix_input.get('documents', {}).get(path) != digest or \
                    capture.get('documents', {}).get(path) != digest:
                raise ValueError('Owner current matrix/capture document pair differs from original reference')
            self.check({'path': path, 'sha256': digest})
        for field, original in (('web', 'currentEvidence'), ('metadata', 'currentMetadata'),
                                ('native', 'nativeEvidence')):
            actual_pin, original_pin = capture.get(field), row.get(original)
            actual_path, original_path = self.check(actual_pin), self.check(original_pin)
            if actual_path != original_path or actual_pin['sha256'] != original_pin['sha256']:
                raise ValueError(f'Owner {field} capture pin differs from original {original}')
        if not same(self.read(capture['metadata']), web):
            raise ValueError('Original captured metadata differs from the selected current matrix row')

    def validate(self, row, evidence_pin):
        projection = self.read(evidence_pin)
        identity = {k: row[k] for k in KEY}
        cell_id = '/'.join(row[k] for k in KEY[:3])
        if projection.get('schema') != 'w50-owner-evidence-1' or projection.get('row') != identity or \
                projection.get('cellId') != cell_id or row['statistic'] != 'owner-contracts':
            raise ValueError('Owner evidence does not match the exact original reference key')
        if self.check(projection.get('contractsPin')) != self.check(self.contracts_pin) or \
                self.check(projection.get('ownerSource'), external=False) != self.check(self.snapshot['ownerSource'], external=False):
            raise ValueError('Owner projection does not bind the root-owned contracts/source')
        inputs = self.read(projection.get('inputsPin')); self.all_pins(inputs)
        report = self.read(projection.get('reportPin')); finite_tree(report)
        provenance = report.get('provenance', {})
        if self.check(provenance.get('owner'), external=False) != self.check(self.snapshot['ownerSource'], external=False) or \
                not same(provenance.get('current'), inputs.get('current')) or \
                not same(provenance.get('fixedReferences'), inputs.get('references')) or \
                not same(provenance.get('declaration'), inputs.get('declaration')):
            raise ValueError('Prepared owner report differs from its pinned input/source provenance')
        source_rows = []
        for item in inputs.get('current', []):
            matrix = self.read(item['matrix'])
            if matrix.get('schemaVersion') != 5 or not isinstance(matrix.get('cells'), list):
                raise ValueError('Owner inputs require the original schema-5 current matrices')
            source_rows += [(r, item) for r in matrix['cells'] if r['key']['profileKey'] == row['profile'] and
                           r['key']['web']['renderer'] == row['renderer'] and r['key']['sceneId'] == row['scene']]
        if len(source_rows) != 1:
            raise ValueError('Owner reference is absent or ambiguous in pinned current matrices')
        source_row, matrix_input = source_rows[0]
        self.bind_current_reference(row, source_row, matrix_input, inputs, cell_id)
        raw = report.get('cells', {}).get(cell_id)
        if not isinstance(raw, dict) or set(raw) != AXES or set(projection.get('axes', {})) != AXES:
            raise ValueError('Owner evidence adds or drops an original axis')
        for name in AXES:
            supplied = projection['axes'][name]; contract = self.snapshot['axes'][name]
            expected = {'evidence': raw[name], **{k: contract[k] for k in
                        ('limits', 'applicability', 'exclusions', 'readingSchema')}}
            if not same(supplied, expected):
                raise ValueError('Owner projection changes source limits, exclusions or measured values')
            self.axis(row, raw[name], contract)
        aggregates = []
        if raw['M1']['state'] != 'NOT_APPLICABLE':
            position = .25 if row['profile'].endswith('-glass0.25') else .5
            scheme = 'dark' if '-dark-' in row['profile'] else 'light'
            aggregates.append(f'M1/{position}/{scheme}/{source_row["state"]}')
        if raw['C1']['state'] != 'NOT_APPLICABLE': aggregates.append('C1')
        if projection.get('aggregateKeys') != aggregates:
            raise ValueError('Owner projection omits or changes a required complete-bed aggregate')
        for key in aggregates:
            aggregate = report.get('aggregates', {}).get(key)
            if not isinstance(aggregate, dict) or aggregate.get('state') != 'MEASURED':
                raise ValueError('Owner aggregate is missing or incomplete')
            schema = self.snapshot['axes']['C1' if key == 'C1' else 'M1']['readingSchema']['aggregate']
            if not isinstance(schema, dict): raise ValueError('Missing source-owned aggregate schema')
            require_numbers(aggregate, schema['requiredFinite'])
            for field in schema['nonemptyObjects']:
                values = at(aggregate, field['field'])
                if not isinstance(values, dict) or not values:
                    raise ValueError('Missing complete owner aggregate population')
                for value in values.values(): require_numbers(value, field['requiredFinite'])
        expected_intrinsic = {name: {'contract': self.snapshot['intrinsic'][name],
            'evidence': report.get('intrinsic', {}).get(name), 'referenceReading': 'NOT_APPLICABLE',
            'candidateCheckRequired': True} for name in INTRINSIC}
        if not same(projection.get('intrinsic'), expected_intrinsic) or any(
                report.get('intrinsic', {}).get(name) is None for name in INTRINSIC):
            raise ValueError('Intrinsic owner contracts are missing or replaced with scalar reference readings')

    def finish(self):
        for path, digest in self.pins.items():
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('Owner evidence changed during completion validation')
