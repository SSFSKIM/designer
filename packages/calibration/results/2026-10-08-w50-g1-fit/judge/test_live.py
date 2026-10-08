"""Synthetic LIVE judge tests: a temporary repository, fake dispatcher capability, no real data.

The World below builds a miniature original inventory with every routed row family, its
DL5d physical closure, a W49a-shaped cut, owner contracts and referee output, and checks each
report against current3's unchanged validate_report. No inventory, capture, native read or
blind statistic of the wave is opened.
"""
import base64
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
CURRENT3 = FIT.parent/'2026-10-08-w50-g1-current3'
P1 = 'apple-macos-27.0-1x-dark-standard-glass0.25'
P2 = 'apple-macos-27.0-2x-dark-standard-glass0.25'
KEY = ('profile', 'renderer', 'scene', 'statistic')
CANARY = 87.654321
CANARY_TEXT = '87.654321'
CURRENT_GENERATION = 'b2d074d2df24-940384c06f73'


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


F = source(HERE/'test_rules.py', 'w50_judge_live_test_fixtures')
D = source(CURRENT3/'execution/dispatch.py', 'w50_judge_live_test_current3')
Q = source(FIT/'live-execution/quarantine.py', 'w50_judge_live_test_quarantine')


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def key(item):
    return tuple(item[k] for k in KEY)


class World:
    """One synthetic repository holding every authenticated input a judge/fit call reads."""

    def __init__(self, test):
        temp = tempfile.TemporaryDirectory()
        test.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.repo = self.base/'repo'
        self.repo.mkdir()
        self.output_root = self.base/'out'
        self.output_root.mkdir()
        self.judge = source(HERE/'live.py', 'w50_judge_live_under_test')
        self.cohort = [self.candidate_document(.25, 'candidate'), self.candidate_document(.5, 'candidate')]
        self.baselines = [self.candidate_document(.25, 'baseline'), self.candidate_document(.5, 'baseline')]
        self.rows = self.build_rows()
        self.inventory_doc = {'schema': 'synthetic', 'generations': {
            CURRENT_GENERATION: {'documentPair': {'active.dark': 'a'*64, 'receded.dark': 'b'*64}},
            'd0219cd684bf': {'documentPair': {'active.dark': '1'*64, 'receded.dark': '2'*64}}},
            'cells': [copy.deepcopy(r['originalReference']) for r in self.rows]}
        self.references = self.write('g0/references.json', self.inventory_doc)
        # Frozen canonical T1 operands bind the actual original inventory's content hash.
        F.INVENTORY = self.references['sha256']
        for item in self.rows:
            if item['originalReference'].get('stratum'):
                F.frozen_operands(item)
        self.dependencies = D.derive_phase_dependencies(self.inventory_doc['cells'])
        self.reported = [list(key(r)) for r in self.rows if r.get('reported')]
        self.empty = [list(key(r)) for r in self.rows if r.get('empty')]
        self.owner_contracts = self.write('owner/contracts.json', self.contracts())
        self.binding = self.write('binding.json', {'original': self.references, 'reportedKeys': self.reported,
            'emptySupportKeys': self.empty, 'ownerContracts': self.owner_contracts})
        self.cut = self.write('cut.json', {'T1': {'cells': self.cut_cells()}})
        self.targets = self.write('judge/targets-config.json', {'schema': 'w50-target-contract-config-1',
            'inventory': self.references, 'cut': self.cut, 'currentGeneration': CURRENT_GENERATION,
            'w48Generation': 'd0219cd684bf'})
        self.config = self.write('judge/config.json', {'schema': 'w50-judge-config-1', 'references': self.references,
            'binding': self.binding, 'ownerContracts': self.owner_contracts, 'targets': self.targets})
        self.part_two = self.write('g0/fit-declaration.json', {'selection': [
            'Minimum worst exposed low-end level error', 'Minimum mean absolute low-end level error',
            'Minimum squared normalized coefficient distance from current over range[0,1]',
            'Lexicographic candidate id'], 'candidateDomain': {
            'endpoints': ['active.dark.0.25', 'receded.dark.0.25', 'active.dark.0.5', 'receded.dark.0.5'],
            'rows': [44, 96, 160], 'inputCodes': [0, 8, 28, 40], 'rankingNormalisationRange': 1}})
        self.fit_config = self.write('fit/analysis-config.json', {'schema': 'w50-fit-analysis-config-1',
            'partTwo': self.part_two, 'references': self.references})
        self.numerical = self.write('numerical.json', {'status': 'PASS', 'fixedJoinPass': True,
            'candidateSha256s': sorted(p['sha256'] for p in self.cohort)})
        (self.repo/'exec').mkdir()
        (self.repo/'exec/dispatch.py').write_text('# synthetic bootstrap\n')
        shutil.copy(FIT/'live-execution/prefit.py', self.repo/'exec/prefit.py')
        self.bootstrap = {'path': 'exec/dispatch.py', 'sha256': sha_bytes((self.repo/'exec/dispatch.py').read_bytes())}
        self.root = {'repo': str(self.repo), 'references': self.references, 'reportedKeys': self.reported,
            'emptySupportKeys': self.empty, 'ownerContracts': self.owner_contracts, 'partTwo': self.part_two,
            'phaseDependencies': self.dependencies, 'bootstrap': self.bootstrap,
            'baselineDocuments': self.baselines,
            'inputs': [self.config, self.binding, self.targets, self.cut, self.fit_config, self.owner_contracts]}
        self.root_path = self.repo/'live/execution-root.json'
        self.write('live/execution-root.json', self.root)
        self.active = None
        self.count = 0
        self.native = {'ready': True, 'nativeExposure': {'emptySupportWitnesses': []}, 'artifacts': []}
        self.dispatcher = self.fake_dispatcher()
        self.empty_witnesses()

    # files ---------------------------------------------------------------------------------
    def write(self, relative, value):
        path = self.repo/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(value, sort_keys=True, indent=1)+'\n').encode()
        path.write_bytes(raw)
        return {'path': relative, 'sha256': sha_bytes(raw)}

    def absolute(self, path, value):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(value, sort_keys=True, indent=1)+'\n').encode()
        path.write_bytes(raw)
        return {'path': str(path), 'sha256': sha_bytes(raw)}

    def candidate_document(self, position, kind):
        folder = f'docs/{kind}-{position}'
        endpoints = {}
        chart = {'lowEndStrength': 1, 'lowEnd44': [.1, .1, .2, .25], 'lowEnd96': [.1, .1, .2, .25],
                 'lowEnd160': [.1, .1, .2, .25]} if kind == 'candidate' else {}
        for slot in ('active.light', 'active.dark', 'receded.light', 'receded.dark'):
            patch = dict(chart) if slot == 'active.dark' else {}
            endpoints[slot] = self.write(f'{folder}/{slot}.json', {'patch': patch})
            endpoints[slot]['path'] = f'{slot}.json'
        return self.write(f'{folder}/candidate.json', {'glassTintAmount': position, 'endpoints': endpoints})

    # rows ----------------------------------------------------------------------------------
    def tag(self, item, profile=P1, role=None):
        for holder in (item, item['originalReference'], item['reference']):
            holder['profile'] = profile
            if role: holder['role'] = role
        if role: item['role'] = role
        return item

    def uniform(self, scene, code, statistic='deep8-channel-median', renderer='webgpu', role='calibration'):
        return self.tag(F.row(statistic, renderer=renderer, input_code=code, scene=scene), role=role)

    def span(self, scene, code, role):
        """A DL5a/DL5c span control's level row: it gates normally beside the reported rows."""
        item = self.tag(F.row(family='span', input_code=code, scene=scene), role=role)
        return item

    def owner(self, scene, profile, role='gate'):
        item = F.row(source='canonical', family='solid', scene=scene)
        item['statistic'] = 'owner-contracts'
        item['readings'] = {}
        for holder in (item['originalReference'], item['reference']):
            holder['statistic'] = 'owner-contracts'
        return self.tag(item, profile, role)

    def reported_row(self, scene, statistic, role, *, empty=False):
        item = self.tag(F.row(statistic, family='span', scene=scene, input_code=0 if empty else 28,
                              native=20 if not empty else .25, current=20 if not empty else .25,
                              candidate=21 if not empty else .25), role=role)
        value = item['readings'][statistic]
        value.update(reported=True, required=False, B=None)
        item['reported'] = True
        if empty:
            value.update(eligibleEmptySupport=True, measurementStatus='UNMEASURED_EMPTY_SUPPORT',
                nativeMeasurementStatus='UNMEASURED_EMPTY_SUPPORT', currentMeasurementStatus='UNMEASURED_EMPTY_SUPPORT',
                candidateMeasurementStatus='UNMEASURED_EMPTY_SUPPORT', native=None, current=None, candidate=None)
            mask = sha_bytes(bytes(384*512//8))
            value['nativeSupportWitnesses'] = [dict(run=r, pixels=0, maskShape=[384, 512], maskPackedBitsSha256=mask)
                                               for r in (1, 2, 3)]
            item['empty'] = True
        return item

    def target(self, scene, profile, stratum, role='gate', candidate=.375):
        item = F.row('T1-full-silhouette', source='canonical', family='texture', input_code=None, scene=scene,
                     native=.25, current=.375, candidate=candidate)
        self.tag(item, profile, role)
        fidelity = {'statistic': 'T1-full-silhouette', 'native': .25, 'current': .375, 'reference': .75}
        for holder in (item, item['originalReference'], item['reference']):
            holder['currentGeneration'] = CURRENT_GENERATION
        for holder in (item['originalReference'], item['reference']):
            holder.update(B=.0625, stratum=stratum, fidelity=copy.deepcopy(fidelity), native=.25, current=.375)
        item['readings']['T1-full-silhouette']['originalBudgetB'] = .0625
        return item

    def build_rows(self):
        return [
            self.uniform('cell-grey-004-s096__rest', 4),
            self.uniform('cell-grey-004-s096__rest', 4, 'central8-channel-median'),
            self.uniform('cell-grey-004-s096__rest', 4, renderer='css'),
            self.uniform('cell-grey-064-s096__rest', 64),
            self.reported_row('cell-grey-028-s128__rest', 'deep8-far24-luma-mean', 'validation'),
            self.span('cell-grey-028-s128__rest', 28, 'validation'),
            self.reported_row('cell-grey-000-s128__inactive', 'T1-full-silhouette', 'validation', empty=True),
            self.owner('checkerboard__rrect-md__rest', P1),
            self.target('checkerboard__rrect-md__rest', P1, 'C'),
            self.target('checkerboard__rrect-md__rest', P2, 'C'),
            self.target('checkerboard-8__rrect-lg__inactive', P1, 'F'),
            self.target('checkerboard-8__rrect-lg__inactive', P2, 'F'),
            self.target('photo__rrect-md__rest', P1, 'P'),
            self.target('photo__rrect-md__inactive', P2, 'P'),
            self.uniform('cell-grey-007-s096__rest', 7, role='blind'),
            self.reported_row('cell-grey-000-s224__inactive', 'T1-full-silhouette', 'blind', empty=True),
            self.span('cell-grey-000-s224__inactive', 0, 'blind'),
            self.target('photo__rrect-md__rest', P2, 'P', role='historical-prediction-check'),
            self.owner('photo__rrect-md__rest', P2),
        ]

    def cut_cells(self):
        cells = []
        for item in self.rows:
            original = item['originalReference']
            if original.get('stratum'):
                cells.append({'profile': original['profile'], 'tier': 'webgpu', 'scene': original['scene'],
                    'stratum': original['stratum'], 'scale': 2 if '-2x-' in original['profile'] else 1,
                    'pose': 'inactive' if '__inactive' in original['scene'] else 'rest',
                    'native': original['native'], 'candidate': original['current'],
                    'reference': original['fidelity']['reference'], 'B': original['B'], 'code': .0625, 'bar': .03125})
        return cells

    def contracts(self):
        schema = {'requiredFinite': [], 'requiredArrays': [], 'conditionalFinite': [], 'unmeasuredExceptions': [],
                  'aggregate': None}
        axes = {name: {'readingSchema': copy.deepcopy(schema)} for name in self.judge.AXES}
        axes['M1']['readingSchema']['requiredFinite'] = ['R']
        axes['L1']['readingSchema']['unmeasuredExceptions'] = [{'kind': 'named-cell', 'identity': 'profile/scene',
            'keys': [f'{P1}/dark-solid__rrect-lg__inactive'], 'evidenceEquals': {'namedExclusion': True}}]
        return {'schema': 'w50-owner-contracts-1', 'axes': axes}

    def empty_witnesses(self):
        packed = bytes(384*512//8)
        for item in self.rows:
            if not item.get('empty'):
                continue
            role = item['role']
            run = {'readings': {'supports': {'full-silhouette': {'status': 'UNMEASURED_EMPTY_SUPPORT', 'pixels': 0,
                   'maskShape': [384, 512], 'maskPackedBitsSha256': sha_bytes(packed),
                   'maskPackedBitsBase64': base64.b64encode(packed).decode()}},
                   'statistics': {'T1-full-silhouette': {'status': 'UNMEASURED_EMPTY_SUPPORT', 'value': None}}}}
            read = self.absolute(self.base/f'native/{role}-{item["scene"]}.json', {
                'schema': 'w50-native-role-read-1', 'role': role, 'canvas': {'width': 512, 'height': 384},
                'cells': [{'profile': item['profile'], 'scene': item['scene'], 'role': role,
                           'runs': [dict(run, run=r) for r in (1, 2, 3)]}]})
            witness = self.absolute(self.base/f'native/witness-{item["scene"]}.json', {
                'schema': 'w50-empty-native-support-witness-1', 'profile': item['profile'],
                'scene': item['scene'], 'role': role, 'nativeRead': read})
            if role == 'blind':
                self.native['nativeExposure']['emptySupportWitnesses'].append({'profile': item['profile'], 'scene': item['scene'],
                                                             'pin': witness})
            else:
                item['reference']['emptySupportWitness'] = witness

    # capability ----------------------------------------------------------------------------
    def fake_dispatcher(self):
        world = self
        live = types.ModuleType('w50_g1_dispatch')

        def require_context(context):
            if world.active is None or context is not world.active:
                raise ValueError('No genuine live context')
            return context

        def checked(repo, pin):
            path = (Path(repo)/pin['path']).resolve()
            if not path.is_file() or sha_bytes(path.read_bytes()) != pin['sha256']:
                raise ValueError('Changed pinned input')
            return path

        live.require_context = require_context
        live.checked = checked
        live.sealed = lambda path: json.loads(Path(path).read_text())
        live.sha = lambda path: sha_bytes(Path(path).read_bytes())
        live.admission_module = lambda root: types.SimpleNamespace(
            validate_numerical=lambda doc, batch: world.numerical)
        live.qualification_native = lambda context: copy.deepcopy(world.native)
        return live

    def install(self, test):
        previous = sys.modules.get('w50_g1_dispatch')
        sys.modules['w50_g1_dispatch'] = self.dispatcher
        def restore():
            if previous is None: sys.modules.pop('w50_g1_dispatch', None)
            else: sys.modules['w50_g1_dispatch'] = previous
        test.addCleanup(restore)

    # phases --------------------------------------------------------------------------------
    def keys(self, phase):
        if phase == 'exposure':
            return {tuple(k) for k in self.dependencies['exposureKeys']}
        return {tuple(k) for k in self.dependencies['gateKeys']}

    def context(self, phase, rows=None, gate=None, name=None):
        self.count += 1
        name = f'{name or phase}-{self.count}'
        output = self.output_root/name
        output.mkdir()
        contract = self.repo/f'live/{name}-contract.json'
        contract.write_text('{}\n')
        batch = self.repo/f'live/{name}-batch.json'
        batch.write_text(json.dumps({'phase': phase}))
        marker = Path(str(contract)+'.phase/analysis.started.json')
        marker.parent.mkdir(parents=True)
        marker.write_text('{"analysis": true}\n')
        logical = self.absolute(str(contract)+'.started.json', {'numericalAdmission': self.numerical})
        selected = self.keys(phase) if rows is None else rows
        expected = [{k: c[k] for k in KEY} for c in self.inventory_doc['cells'] if key(c) in selected]
        context = {'repo': str(self.repo), 'executionRoot': str(self.root_path), 'contract': str(contract),
            'batchPath': str(batch), 'batch': {'phase': phase, 'cohort': copy.deepcopy(self.cohort), 'runs': []},
            'phase': phase, 'stage': 'analysis', 'output': str(output), 'logicalClaim': logical,
            'executionClaim': {'path': str(marker), 'sha256': sha_bytes(marker.read_bytes())},
            'inputs': copy.deepcopy(self.root['inputs']), 'expectedCells': expected,
            'baselineDocuments': copy.deepcopy(self.baselines), 'phaseDependencies': copy.deepcopy(self.dependencies),
            'ownerUnionKeys': copy.deepcopy(self.dependencies['ownerUnionKeys']),
            'unionExpectedCells': [{k: c[k] for k in KEY} for c in self.inventory_doc['cells']],
            'gateResult': None, 'gateCaptures': None, 'gateReport': None}
        if gate is not None:
            context.update(gateResult=gate['pin'], gateReport=gate['report'], gateCaptures={'status': 'CAPTURED'})
        return context

    def measured(self, context, overrides=None):
        rows = []
        for item in self.rows:
            if key(item) not in {key(c) for c in context['expectedCells']}:
                continue
            row = copy.deepcopy(item)
            for flag in ('reported', 'empty'):
                row.pop(flag, None)
            if overrides and key(item) in overrides:
                overrides[key(item)](row)
            if row['role'] == 'blind':
                row['nativeEvidence'] = self.absolute(Path(context['output'])/f'measurement/native-{len(rows)}.json',
                                                      {'blind': True})
            rows.append(row)
        body = {'schema': 'w50-phase-measurement-evidence-1', 'status': 'EVIDENCE_ONLY', 'phase': context['phase'],
                'candidateSha256s': sorted(p['sha256'] for p in self.cohort), 'cohort': copy.deepcopy(self.cohort),
                'config': {'path': 'measurement.json', 'sha256': 'c'*64}, 'referenceInventory': self.references,
                'completedReferences': {'path': 'completed.json', 'sha256': 'd'*64},
                'expectedKeys': [list(k) for k in sorted(key(c) for c in context['expectedCells'])],
                'rows': rows, 'gateResult': copy.deepcopy(context.get('gateResult')),
                'executionClaim': copy.deepcopy(context['executionClaim'])}
        for name, field in (('executionRoot', 'executionRoot'), ('contract', 'contract'), ('batch', 'batchPath')):
            body[name] = {'path': context[field], 'sha256': sha_bytes(Path(context[field]).read_bytes())}
        body['snapshot'] = self.absolute(Path(context['output'])/'measurement/phase.json', body)
        return body

    def captures(self):
        return {'status': 'CAPTURED', 'candidateSha256s': sorted(p['sha256'] for p in self.cohort), 'captures': []}

    def owner_report(self, context, mutate=None):
        def axes():
            out = {name: {'state': 'NOT_APPLICABLE', 'reason': 'synthetic'} for name in self.judge.AXES}
            out['M1'] = {'state': 'MEASURED', 'verdict': 'within', 'R': 1.0}
            return out
        cells = {'/'.join(k[:3]): axes() for k in self.dependencies['ownerUnionKeys']}
        cells[f'{P1}/webgpu/dark-solid__rrect-lg__rest'] = axes()
        report = {'cells': cells, 'aggregates': {'C1': {'state': 'MEASURED', 'verdict': 'within'},
                  'M1/0.25/dark/rest': {'state': 'MEASURED', 'verdict': 'within'}},
                  'intrinsic': {'X75': {f'endpoint-{i:02}': {'state': 'MEASURED', 'verdict': 'within'} for i in range(12)},
                                'X76': {p: {'state': 'MEASURED', 'verdict': 'within'} for p in ('0.25', '0.5')}},
                  'provenance': {}, 'noNewTrade': 'synthetic'}
        if mutate:
            mutate(report)
        output = Path(context['output'])
        snapshot = self.absolute(output/'owner-candidate.snapshot.json', {'snapshot': True})
        gate = context['gateResult']
        report['liveUnion'] = {'ownerKeys': copy.deepcopy(context['ownerUnionKeys']), 'cohort': copy.deepcopy(self.cohort),
            'gateResult': {'path': str(self.repo/gate['path']), 'sha256': gate['sha256']}, 'snapshot': snapshot}
        self.absolute(output/'owner-candidate.report.json', report)
        return {'report': report, 'snapshot': snapshot}

    def run(self, context, measured, owner=None):
        self.active = context
        try:
            return self.judge.evaluate(context, {'measurement': measured, 'owner': owner,
                                                 'captures': self.captures()}, self.config)
        finally:
            self.active = None

    def gate(self, overrides=None):
        context = self.context('gate')
        report = self.run(context, self.measured(context, overrides))
        return context, report

    def qualified_gate(self, overrides=None):
        context, report = self.gate(overrides)
        pin = self.write('live/gate-contract.json.result.json', {'report': report})
        return {'pin': pin, 'report': json.loads(json.dumps(report)), 'context': context}

    def exposure(self, gate, overrides=None, owner=None):
        context = self.context('exposure', gate=gate)
        measured = self.measured(context, overrides)
        return context, self.run(context, measured, self.owner_report(context, owner))

    def validate(self, context, report):
        doc = {'repo': str(self.repo), 'references': self.references, 'phaseDependencies': self.dependencies,
               'reportedKeys': self.reported, 'emptySupportKeys': self.empty, 'bootstrap': self.bootstrap}
        D.validate_report(doc, context['batch'], context['expectedCells'], report, gate_result=context.get('gateResult'))


def candidate(name, value):
    def change(row):
        reading = row['readings'][name]
        reading['candidate'] = value
        production = reading['evidence']['candidate'].get('productionStatistic')
        if production is not None:
            production['value'] = value
    return change


def unmeasured(name):
    def change(row):
        row['readings'][name].update(candidate=None, candidateMeasurementStatus='UNMEASURED',
                                     measurementStatus='UNMEASURED', candidateReason='synthetic gap')
    return change


def cell_of(report, profile, scene, statistic, renderer='webgpu'):
    return next(c for c in report['cells'] if key(c) == (profile, renderer, scene, statistic))


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.world = World(self)
        self.world.install(self)

    def test_gate_success_is_exposed_only_with_owners_and_targets_pending(self):
        w = self.world
        context, report = w.gate()
        self.assertEqual(report['status'], 'PASS_EXPOSED_OWNER_PENDING')
        self.assertEqual(report['ownerChecks'], 'PENDING_FULL_UNION')
        self.assertEqual(report['pendingOwnerKeys'], w.dependencies['pendingOwnerKeys'])
        self.assertEqual(report['pendingOwnerKeys'], [[P2, 'webgpu', 'photo__rrect-md__rest', 'owner-contracts']])
        self.assertEqual(report['targetChecks'], 'PENDING_FULL_UNION')
        self.assertEqual([t['status'] for t in report['targets']], ['PENDING_FULL_UNION']*6)
        self.assertEqual({key(c) for c in report['cells']}, w.keys('gate'))
        self.assertEqual(cell_of(report, P1, 'checkerboard__rrect-md__rest', 'owner-contracts')['status'],
                         'PENDING_OWNER_UNION')
        reported = cell_of(report, P1, 'cell-grey-028-s128__rest', 'deep8-far24-luma-mean')
        self.assertEqual((reported['status'], reported['B']), ('REPORTED', None))
        empty = cell_of(report, P1, 'cell-grey-000-s128__inactive', 'T1-full-silhouette')
        self.assertEqual(empty['status'], 'UNMEASURED_EMPTY_SUPPORT')
        self.assertTrue(all(empty[k] is None for k in ('native', 'current', 'candidate', 'fidelity', 'value', 'B')))
        held = cell_of(report, P1, 'cell-grey-064-s096__rest', 'deep8-channel-median')
        self.assertEqual((held['status'], held['joinIdentity'], held['heldDifference']), ('PASS', True, [0, 0, 0]))
        w.validate(context, report)

    def test_any_single_failing_or_unmeasured_exposed_row_is_neither_at_the_gate(self):
        w = self.world
        cases = {
            'level': ((P1, 'webgpu', 'cell-grey-004-s096__rest', 'deep8-channel-median'),
                      candidate('deep8-channel-median', [23, 20, 20]), 'FAIL'),
            'css growth': ((P1, 'css', 'cell-grey-004-s096__rest', 'deep8-channel-median'),
                           candidate('deep8-channel-median', [17, 20, 20]), 'FAIL'),
            'unmeasured': ((P1, 'webgpu', 'cell-grey-004-s096__rest', 'central8-channel-median'),
                           unmeasured('central8-channel-median'), 'UNMEASURED'),
            'canonical T1': ((P1, 'webgpu', 'photo__rrect-md__rest', 'T1-full-silhouette'),
                             candidate('T1-full-silhouette', .5), 'FAIL'),
            'reported gap': ((P1, 'webgpu', 'cell-grey-028-s128__rest', 'deep8-far24-luma-mean'),
                             unmeasured('deep8-far24-luma-mean'), 'UNMEASURED'),
        }
        for label, (item, change, status) in cases.items():
            with self.subTest(label):
                world = World(self); world.install(self)
                context, report = world.gate({item: change})
                self.assertEqual(report['status'], 'NEITHER')
                self.assertEqual(next(c for c in report['cells'] if key(c) == item)['status'], status)
                world.validate(context, report)

    def test_dl5c_eligible_blind_key_is_reported_when_its_support_is_not_empty_and_levels_still_gate(self):
        def measured_support(row):
            value = row['readings']['T1-full-silhouette']
            value.update(measurementStatus='MEASURED', nativeMeasurementStatus='MEASURED',
                         currentMeasurementStatus='MEASURED', candidateMeasurementStatus='MEASURED',
                         native=.25, current=.25, candidate=.3, nativeSupportWitnesses=[])
        blind_t1 = (P1, 'webgpu', 'cell-grey-000-s224__inactive', 'T1-full-silhouette')
        blind_level = (P1, 'webgpu', 'cell-grey-000-s224__inactive', 'deep8-channel-median')
        w = self.world
        context, report = w.exposure(w.qualified_gate(), {blind_t1: measured_support})
        cell = next(c for c in report['cells'] if key(c) == blind_t1)
        self.assertEqual((cell['status'], cell['B'], cell['candidate']), ('REPORTED', None, .3))
        self.assertEqual(report['status'], 'PASS')
        w.validate(context, report)
        world = World(self); world.install(self)
        context, report = world.exposure(world.qualified_gate(), {blind_level: unmeasured('deep8-channel-median')})
        self.assertEqual(next(c for c in report['cells'] if key(c) == blind_level)['status'], 'UNMEASURED')
        self.assertEqual(report['status'], 'NEITHER')
        world.validate(context, report)
        world = World(self); world.install(self)
        level = (P1, 'webgpu', 'cell-grey-028-s128__rest', 'deep8-channel-median')
        context, report = world.gate({level: candidate('deep8-channel-median', [24, 20, 20])})
        self.assertEqual(next(c for c in report['cells'] if key(c) == level)['status'], 'FAIL')
        self.assertEqual(report['status'], 'NEITHER')

    def test_held64_identity_is_the_admitted_numerical_join_not_a_rendered_bound(self):
        w = self.world
        far = {(P1, 'webgpu', 'cell-grey-064-s096__rest', 'deep8-channel-median'):
               candidate('deep8-channel-median', [200, 200, 200])}
        _, report = w.gate(far)
        held = cell_of(report, P1, 'cell-grey-064-s096__rest', 'deep8-channel-median')
        self.assertEqual((report['status'], held['status'], held['heldDifference']),
                         ('PASS_EXPOSED_OWNER_PENDING', 'PASS', [180, 180, 180]))
        w.numerical = w.write('numerical-moved.json', {'status': 'PASS', 'fixedJoinPass': False,
                              'candidateSha256s': sorted(p['sha256'] for p in w.cohort)})
        context, report = w.gate()
        self.assertEqual(cell_of(report, P1, 'cell-grey-064-s096__rest', 'deep8-channel-median')['status'], 'FAIL')
        self.assertEqual(report['status'], 'NEITHER')
        w.validate(context, report)

    def test_complete_union_all_within_is_pass_and_binds_the_gate(self):
        w = self.world
        gate = w.qualified_gate()
        context, report = w.exposure(gate)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual((report['ownerChecks'], report['targetChecks'], report['pendingOwnerKeys']),
                         ('FULL_UNION', 'FULL_UNION', []))
        self.assertEqual(report['gateResult'], gate['pin'])
        self.assertEqual(len(report['cells']), len(w.rows))
        self.assertEqual([t['status'] for t in report['targets']], ['WITHIN']*6)
        self.assertEqual(cell_of(report, P2, 'photo__rrect-md__rest', 'owner-contracts')['status'], 'PASS')
        blind_empty = cell_of(report, P1, 'cell-grey-000-s224__inactive', 'T1-full-silhouette')
        self.assertEqual(blind_empty['status'], 'UNMEASURED_EMPTY_SUPPORT')
        self.assertEqual(blind_empty['emptySupportWitness'], w.native['nativeExposure']['emptySupportWitnesses'][0]['pin'])
        w.validate(context, report)

    def test_any_single_blind_owner_or_target_failure_is_neither_on_the_union(self):
        def failing_axis(report):
            report['cells'][f'{P2}/webgpu/photo__rrect-md__rest']['M1'] = {'state': 'MEASURED', 'verdict': 'failure', 'R': 2.0}
        def failing_context(report):
            report['cells'][f'{P1}/webgpu/dark-solid__rrect-lg__rest']['X1'] = {'state': 'MEASURED', 'verdict': 'failure'}
        def failing_aggregate(report):
            report['aggregates']['C1']['verdict'] = 'failure'
        def failing_intrinsic(report):
            report['intrinsic']['X76']['0.5'] = {'state': 'UNMEASURED', 'reason': 'synthetic'}
        def widened(report):
            report['cells'][f'{P2}/webgpu/photo__rrect-md__rest']['M2'] = {'state': 'MEASURED',
                'verdict': 'named-miss', 'wouldRequireNewOwnerRecord': True}
        exposure = {
            'blind': ({(P1, 'webgpu', 'cell-grey-007-s096__rest', 'deep8-channel-median'):
                       candidate('deep8-channel-median', [25, 20, 20])}, None),
            'historical check': ({(P2, 'webgpu', 'photo__rrect-md__rest', 'T1-full-silhouette'):
                                  candidate('T1-full-silhouette', .5)}, None),
            'owner axis': (None, failing_axis), 'owner context': (None, failing_context),
            'owner aggregate': (None, failing_aggregate), 'intrinsic': (None, failing_intrinsic),
            'widened exclusion': (None, widened),
        }
        for label, (overrides, owner) in exposure.items():
            with self.subTest(label):
                world = World(self); world.install(self)
                context, report = world.exposure(world.qualified_gate(), overrides, owner)
                self.assertEqual(report['status'], 'NEITHER')
                world.validate(context, report)
        # A target worsens while every member stays within its own per-cell budget.
        world = World(self); world.install(self)
        gate = world.qualified_gate({(P1, 'webgpu', 'photo__rrect-md__rest', 'T1-full-silhouette'):
                                     candidate('T1-full-silhouette', .4)})
        self.assertEqual(gate['report']['status'], 'PASS_EXPOSED_OWNER_PENDING')
        context, report = world.exposure(gate)
        self.assertEqual(report['status'], 'NEITHER')
        self.assertEqual([(t['target'], t['scale']) for t in report['targets'] if t['status'] != 'WITHIN'], [('P', 1)])
        world.validate(context, report)

    def test_source_owned_owner_exception_passes_and_unexcepted_gap_blocks(self):
        def excepted(report):
            report['cells'][f'{P1}/webgpu/dark-solid__rrect-lg__inactive'] = {name: {'state': 'NOT_APPLICABLE', 'reason': 'x'}
                for name in self.world.judge.AXES}
            report['cells'][f'{P1}/webgpu/dark-solid__rrect-lg__inactive']['L1'] = {
                'state': 'UNMEASURED', 'reason': 'Missing fixed-native mean', 'namedExclusion': True}
        w = self.world
        _, report = w.exposure(w.qualified_gate(), owner=excepted)
        self.assertEqual(report['status'], 'PASS')
        def gap(report):
            report['cells'][f'{P1}/webgpu/checkerboard__rrect-md__rest']['E2'] = {'state': 'UNMEASURED', 'reason': 'x'}
        world = World(self); world.install(self)
        _, report = world.exposure(world.qualified_gate(), owner=gap)
        self.assertEqual(report['status'], 'NEITHER')
        self.assertEqual(cell_of(report, P1, 'checkerboard__rrect-md__rest', 'owner-contracts')['status'], 'UNMEASURED')

    def test_blind_row_without_exposure_content_pin_blocks(self):
        w = self.world
        gate = w.qualified_gate()
        context = w.context('exposure', gate=gate)
        measured = w.measured(context)
        for row in measured['rows']:
            if row['role'] == 'blind' and row['statistic'] == 'deep8-channel-median':
                Path(row['nativeEvidence']['path']).write_text('{"changed": true}\n')
        report = w.run(context, measured, w.owner_report(context))
        self.assertEqual(cell_of(report, P1, 'cell-grey-007-s096__rest', 'deep8-channel-median')['status'], 'UNMEASURED')
        self.assertEqual(report['status'], 'NEITHER')

    def test_refusals_never_issue_a_verdict(self):
        w = self.world
        context = w.context('gate')
        measured = w.measured(context)
        with self.assertRaises(ValueError):
            w.judge.evaluate(context, {'measurement': measured, 'owner': None, 'captures': w.captures()}, w.config)
        Path(context['executionClaim']['path']).unlink()
        w.active = context
        with self.assertRaises(ValueError):
            w.judge.evaluate(context, {'measurement': measured, 'owner': None, 'captures': w.captures()}, w.config)
        w.active = None
        context = w.context('gate')
        measured = w.measured(context)
        measured['rows'][0]['readings']['deep8-channel-median']['candidate'] = [20, 20, 21]
        with self.assertRaises(ValueError):
            w.run(context, measured)
        context = w.context('gate')
        with self.assertRaises(ValueError):
            w.run(context, w.measured(context), owner={'report': {}, 'snapshot': {}})
        gate = w.qualified_gate()
        context = w.context('exposure', gate=gate)
        with self.assertRaises(ValueError):
            w.run(context, w.measured(context), None)
        unqualified = copy.deepcopy(gate)
        unqualified['report']['status'] = 'NEITHER'
        context = w.context('exposure', gate=unqualified, name='exposure')
        with self.assertRaises(ValueError):
            w.run(context, w.measured(context), w.owner_report(context))

    def test_quarantine_canaries_hold_in_streams_errors_and_public_summary(self):
        w = self.world
        canary = {(P1, 'webgpu', 'cell-grey-004-s096__rest', 'deep8-channel-median'):
                  candidate('deep8-channel-median', [CANARY, 20, 20])}
        log = w.base/'quarantine/judge.log'
        def work():
            return w.gate(canary)
        ok, (context, report) = Q.run_private(log, work)
        self.assertTrue(ok)
        self.assertIn(CANARY_TEXT, json.dumps(report))
        self.assertEqual(log.read_text(), '')
        summary = w.judge.public_summary(report)
        self.assertNotIn(CANARY_TEXT, json.dumps(summary))
        self.assertEqual(summary['status'], 'NEITHER')
        self.assertEqual(summary['blockingKeys'], [[P1, 'webgpu', 'cell-grey-004-s096__rest', 'deep8-channel-median']])
        # Refusals raised with the canary inside the evidence keep it out of every message.
        loud = {(P1, 'webgpu', 'cell-grey-004-s096__rest', 'deep8-channel-median'):
                candidate('deep8-channel-median', [CANARY*10, 20, 20])}
        tampered = lambda measured: measured['rows'][0]['originalReference'].update(B=CANARY)
        for index, (overrides, change) in enumerate(((loud, None), (canary, tampered))):
            context = w.context('gate', name='canary-error')
            measured = w.measured(context, overrides)
            if change: change(measured)
            public = io.StringIO()
            with contextlib.redirect_stdout(public), contextlib.redirect_stderr(public):
                with self.assertRaises(ValueError) as caught:
                    w.run(context, measured)
            self.assertNotIn(CANARY_TEXT, str(caught.exception)+public.getvalue())
            self.assertNotIn('876.54321', str(caught.exception))
            error_log = w.base/f'quarantine/judge-error-{index}.log'
            ok, value = Q.run_private(error_log, lambda: w.run(context, measured))
            self.assertFalse(ok)
            self.assertEqual(value, {'code': 'INSTRUMENT_FAULT'})
            self.assertIn('Traceback', error_log.read_text())
            self.assertNotIn(CANARY_TEXT, error_log.read_text())
            self.assertNotIn('876.54321', error_log.read_text())


if __name__ == '__main__':
    unittest.main()
