"""Synthetic end-to-end: the real LIVE dispatcher and all seven real role sources, fit to exposure.

A judge exception after the irreversible analysis marker leaves no result, and LIVE refuses a
second analysis, so the whole chain is run once here before any real use: create_phase,
prepare_attempt, execute_attempt and execute_analysis for the fit, the frozen gate and the one
exposure, with every role loaded by the dispatcher from the root's own registration
(livekit.EndToEnd lists the stand-in seams). Every report is checked again by the dispatcher's
report validator; each test asserts the seam shapes the judge reads from measurement, owner and
native.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import unittest.mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w50_end_to_end_kit', HERE/'livekit.py')
K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
KEY = K.KEY
EXECUTED = []
ACTIVE = []


def _audit(event, args):
    if ACTIVE and event == 'exec' and hasattr(args[0], 'co_filename'):
        EXECUTED.append(args[0].co_filename)


sys.addaudithook(_audit)
BLIND = (K.P5, 'webgpu', 'cell-grey-007-s044__rest', 'deep8-channel-median')
GATED = (K.P1, 'webgpu', 'cell-grey-004-s096__rest', 'deep8-channel-median')
REPORTED = (K.P5, 'webgpu', 'cell-grey-028-s224__rest', 'deep8-far24-luma-mean')


def key(cell): return tuple(cell[k] for k in KEY)


class EndToEnd(unittest.TestCase):
    def setUp(self):
        EXECUTED.clear(); ACTIVE.append(True)
        self.addCleanup(ACTIVE.clear)

    def validate(self, world, contract, result):
        """The dispatcher's own report validation of a sealed result, again, from its files."""
        body = world.C.D.sealed(contract)
        batch, expected = world.C.D.validate_batch(world.doc, world.repo/body['batch']['path'], body['phase'])
        world.C.validate_report(world.doc, batch, expected, result['report'], gate_result=body.get('gateResult'))
        if any(c['status'] == 'UNMEASURED_REPORTED' for c in result['report']['cells']):
            # current3's sealed validator knows no such status; only LIVE's DL5m wrapper admits it.
            with self.assertRaisesRegex(ValueError, 'complete phase/owner intersection'):
                world.C.D.validate_report(world.doc, batch, expected, result['report'], gate_result=body.get('gateResult'))
        else:
            world.C.D.validate_report(world.doc, batch, expected, result['report'], gate_result=body.get('gateResult'))

    def fit_and_gate(self, world):
        fit, fitted = world.phase('fit')
        analysis = fitted['report']['analysis']
        record_path, record = world.fit_record(fit)
        gate, gated = world.phase('gate', record_path)
        return fit, fitted, analysis, record, gate, gated

    def test_fit_gate_and_exposure_pass_on_an_all_within_population(self):
        world = K.EndToEnd(self)
        fit, fitted, analysis, record, gate, gated = self.fit_and_gate(world)

        # Fit: the fit role's analysis of the one rendered point, and a record with no verdict.
        self.assertEqual(fitted['report']['status'], 'CAPTURED')
        self.assertEqual(analysis['schema'], 'w50-fit-analysis-1')
        self.assertEqual(analysis['status'], 'FIT_ANALYSIS_ONLY')
        self.assertEqual(analysis['candidateSha256s'], sorted(p['sha256'] for p in world.cohort))
        self.assertEqual(analysis['selection']['levelComponents'], 6)
        self.assertEqual(analysis['selection']['worstLowEndLevelErrorCodes'], 0)
        self.assertEqual(record['schema'], 'w50-g1-fit-record-1')
        self.assertEqual(record['selected'], world.cohort)
        for document in (analysis, record):
            self.assertFalse({'PASS', 'NEITHER', 'PASS_EXPOSED_OWNER_PENDING'} & set(json.dumps(document).split('"')))

        # Gate: PASS on the exposed cells, owner rows pending, targets pending the full union.
        report = gated['report']
        self.assertEqual(report['status'], 'PASS_EXPOSED_OWNER_PENDING')
        self.assertEqual(report['pendingOwnerKeys'], world.dependencies['pendingOwnerKeys'])
        self.assertEqual({t['status'] for t in report['targets']}, {'PENDING_FULL_UNION'})
        statuses = {key(c): c['status'] for c in report['cells']}
        self.assertEqual(set(statuses), {tuple(k) for k in world.dependencies['gateKeys']})
        for renderer in ('webgpu', 'css'):
            self.assertEqual(statuses[(K.P1, renderer, 'checkerboard__rrect-md__rest', 'owner-contracts')],
                             'PENDING_OWNER_UNION')
        self.assertEqual({s for k, s in statuses.items() if k[3] != 'owner-contracts'}, {'PASS'})
        self.validate(world, gate, gated)
        world.C.checked_gate_result(world.root, world.doc)

        # Exposure: the complete same-candidate union PASSes.
        exposure, exposed = world.phase('exposure')
        report = exposed['report']
        self.assertEqual(report['status'], 'PASS', json.dumps([[list(key(c)), c['status']] for c in report['cells']
                         if c['status'] not in ('PASS', 'REPORTED', 'UNMEASURED_EMPTY_SUPPORT')]))
        self.assertEqual((report['ownerChecks'], report['targetChecks'], report['pendingOwnerKeys']),
                         ('FULL_UNION', 'FULL_UNION', []))
        self.validate(world, exposure, exposed)
        cells = {key(c): c for c in report['cells']}
        self.assertEqual(set(cells), {key(c) for c in world.rows})

        # Targets: all six W48 aggregates over the complete union, the self-check reading WITHIN.
        self.assertEqual(sorted((t['target'], t['scale'], t['status']) for t in report['targets']),
                         sorted((n, s, 'WITHIN') for n in ('C rest', 'F inactive', 'P') for s in (1, 2)))

        # Owner: the frozen engine read the intrinsic records at the gate's creation and at each
        # exposure admission (creation, before the native marker, before the analysis marker),
        # always before any marker (second pre-seal review P1).
        self.assertEqual(world.intrinsic_requests, ['gate', 'exposure', 'exposure', 'exposure'])
        # Owner: the referee ran once, on this union, and graded every owner key and aggregate.
        self.assertEqual(len(world.child), 1)
        self.assertEqual(world.child[0]['ownerUnionKeys'], world.dependencies['ownerUnionKeys'])
        for owner in world.dependencies['ownerUnionKeys']:
            self.assertEqual(cells[tuple(owner)]['status'], 'PASS')
            self.assertEqual(set(cells[tuple(owner)]['owner']), {'M1', 'M2', 'C1', 'X1', 'L1', 'E2', 'coherence'})
        self.assertEqual({a['status'] for a in report['owner']['aggregates']+report['owner']['intrinsic']}, {'PASS'})

        # Native: the real preparation's witnesses and envelopes reach the judge and validator.
        checkpoint = json.loads((Path(str(exposure)+'.phase')/'native.complete.json').read_text())
        payload = json.loads(Path(checkpoint['payload']['path']).read_text())
        witnesses = {(w['profile'], w['scene']): w['pin'] for w in payload['nativeExposure']['emptySupportWitnesses']}
        empty = {tuple(k) for k in world.empty}
        self.assertTrue(empty)
        for item in empty:
            self.assertEqual(cells[item]['status'], 'UNMEASURED_EMPTY_SUPPORT')
            self.assertEqual(cells[item]['emptySupportWitness'], witnesses[(item[0], item[2])])
        reported = {tuple(k) for k in world.reported} - empty
        self.assertEqual({cells[k]['status'] for k in reported}, {'REPORTED'})
        for item, cell in cells.items():
            if cell['role'] == 'blind':
                envelope = json.loads(Path(cell['nativeEvidence']['path']).read_text())
                self.assertEqual(envelope['nativeRead'], payload['nativeExposure']['nativeRead'])
                self.assertEqual(envelope['statistic'], item[3])

        # Every repository source the chain executed is a byte-identical member of the draft
        # root's closure, or a named stand-in at its seam.
        executed = {str(Path(f).resolve().relative_to(world.repo)) for f in EXECUTED
                    if Path(f).is_absolute() and Path(f).resolve().is_relative_to(world.repo)}
        standins = {str(p) for p in world.standins}
        self.assertEqual(executed - set(world.copied) - standins, set())
        self.assertTrue({str(K.REL_FIT/p) for p in ('judge/live.py', 'fit/live.py', 'live-roles/native.py',
                         'live-roles/owner.py', 'live-roles/measurement.py', 'live-roles/capture.py')} <= executed)

    def test_one_failing_blind_row_makes_the_exposure_neither(self):
        world = K.EndToEnd(self, offsets={'|'.join(BLIND): 10})
        *_, gate, gated = self.fit_and_gate(world)
        self.assertEqual(gated['report']['status'], 'PASS_EXPOSED_OWNER_PENDING')
        exposure, exposed = world.phase('exposure')
        report = exposed['report']
        self.assertEqual(report['status'], 'NEITHER')
        failing = [list(key(c)) for c in report['cells']
                   if c['status'] not in ('PASS', 'REPORTED', 'UNMEASURED_EMPTY_SUPPORT')]
        self.assertEqual(failing, [list(BLIND)])
        self.assertEqual(next(c for c in report['cells'] if key(c) == BLIND)['route']['failures'],
                         ['absolute-level:deep8-channel-median'])
        self.assertEqual({t['status'] for t in report['targets']}, {'WITHIN'})
        self.validate(world, exposure, exposed)

    def test_an_out_of_domain_reported_reading_is_unmeasured_reported_and_still_passes(self):
        world = K.EndToEnd(self, offsets={'|'.join(REPORTED): 1000})
        self.fit_and_gate(world)
        exposure, exposed = world.phase('exposure')
        report = exposed['report']
        self.assertEqual(report['status'], 'PASS')
        cell = next(c for c in report['cells'] if key(c) == REPORTED)
        self.assertEqual(cell['status'], 'UNMEASURED_REPORTED')
        self.assertEqual(cell['cause']['kind'], 'OUT_OF_DOMAIN_READING')
        self.assertEqual(cell['cause']['sides'], ['candidate'])
        self.assertEqual([cell[k] for k in ('native', 'current', 'candidate', 'B')], [None]*4)
        self.validate(world, exposure, exposed)

    def test_an_empty_reported_native_silhouette_is_unmeasured_reported_and_still_passes(self):
        """DL5m item 4 through the real native role: a non-eligible reported T1 whose native
        silhouette reads nothing (the span-224 body drawn at its own grey-028 backdrop) is
        recorded, never a stop; the read stays ready and the exposure still PASSes."""
        cell = K.P5+'/cell-grey-028-s224__rest'
        world = K.EndToEnd(self, levels={(cell, n): -22 for n in (1, 2, 3)})
        self.fit_and_gate(world)
        exposure, exposed = world.phase('exposure')
        checkpoint = json.loads((Path(str(exposure)+'.phase')/'native.complete.json').read_text())
        payload = json.loads(Path(checkpoint['payload']['path']).read_text())
        self.assertEqual((payload['ready'], payload['stops']), (True, []))
        report = exposed['report']
        self.assertEqual(report['status'], 'PASS')
        for renderer in ('webgpu', 'css'):
            item = next(c for c in report['cells'] if key(c) == (K.P5, renderer, 'cell-grey-028-s224__rest', 'T1-full-silhouette'))
            self.assertEqual(item['status'], 'UNMEASURED_REPORTED')
            self.assertEqual(item['cause']['kind'], 'INCOMPLETE_READING')
            self.assertIn('native', item['cause']['sides'])
        self.validate(world, exposure, exposed)

    def test_a_fault_inside_the_native_read_stops_and_is_never_replayed(self):
        """DL5k/DL5n boundary: a disk or integrity fault after native.started.json is an
        operational stop with no checkpoint and no verdict, and the read is never replayed."""
        world = K.EndToEnd(self)
        self.fit_and_gate(world)
        contract = Path(world.D.create_phase(world.root, world.batches['exposure'], world.outputs['exposure']))
        attempt = world.D.prepare_attempt(world.root, contract)
        read = Path.read_bytes
        def faulty(path):
            if 'native-blind/role-export/' in str(path) and path.suffix == '.png':
                raise OSError('synthetic disk fault')
            return read(path)
        with unittest.mock.patch.object(Path, 'read_bytes', faulty):
            event = world.D.execute_attempt(world.root, contract, attempt)
        home = Path(str(contract)+'.phase')
        self.assertEqual(event['code'], 'INSTRUMENT_FAULT')
        self.assertTrue((home/'native.started.json').is_file())
        self.assertFalse((home/'native.complete.json').exists())
        self.assertIn('synthetic disk fault', (world.outputs['exposure']/'attempts/000001/quarantine/worker.log').read_text())
        with self.assertRaisesRegex(ValueError, 'cannot be replayed'):
            world.D.prepare_attempt(world.root, contract)
        self.assertFalse(Path(str(contract)+'.result.json').exists())

    def test_a_not_ready_native_read_is_neither_with_its_stopped_rows_unmeasured(self):
        """DL5n end to end: a native spread past one code on a required blind statistic completes
        the read not ready; LIVE checkpoints it, the stopped rows reach the judge UNMEASURED on
        both tiers, and the verdict is NEITHER through the normal path, with no value published."""
        cell = K.P5+'/'+BLIND[2]
        world = K.EndToEnd(self, levels={(cell, 3): 23})
        self.fit_and_gate(world)
        exposure, exposed = world.phase('exposure')
        checkpoint = json.loads((Path(str(exposure)+'.phase')/'native.complete.json').read_text())
        payload = json.loads(Path(checkpoint['payload']['path']).read_text())
        self.assertEqual((payload['ready'], payload['complete']), (False, True))
        self.assertEqual([(s['cell'], s['statistic'], s['reason']) for s in payload['stops']],
                         [(cell, name, 'NATIVE_SPREAD_EXCEEDS_ONE_CODE') for name in ('central8-channel-median', 'deep8-channel-median')])
        report = exposed['report']
        self.assertEqual(report['status'], 'NEITHER')
        stopped = {(K.P5, renderer, BLIND[2], name) for renderer in ('webgpu', 'css')
                   for name in ('central8-channel-median', 'deep8-channel-median')}
        cells = {key(c): c for c in report['cells']}
        self.assertEqual({k for k, c in cells.items() if c['status'] not in ('PASS', 'REPORTED', 'UNMEASURED_EMPTY_SUPPORT')}, stopped)
        for item in stopped:
            self.assertEqual(cells[item]['status'], 'UNMEASURED')
            self.assertEqual(cells[item]['cause'], {'kind': 'NATIVE_NOT_READY', 'reason': 'NATIVE_SPREAD_EXCEEDS_ONE_CODE'})
            self.assertEqual([cells[item][k] for k in ('native', 'current', 'candidate', 'B')], [None]*4)
        # The spread is the one native value a stop carries; it stays in the quarantined read.
        native = json.loads(Path(payload['nativeExposure']['nativeRead']['path']).read_text())
        spreads = {repr(v) for s in native['stops'] for v in s['repeat']['spreadCodes'] if v > 1}
        self.assertTrue(spreads)
        self.assertFalse([v for v in spreads if v in json.dumps(payload['stops'])+json.dumps(checkpoint)])
        self.validate(world, exposure, exposed)

    def test_a_failing_gate_row_is_neither_and_admits_no_exposure(self):
        world = K.EndToEnd(self, offsets={'|'.join(GATED): 10})
        *_, gate, gated = self.fit_and_gate(world)
        self.assertEqual(gated['report']['status'], 'NEITHER')
        failing = [list(key(c)) for c in gated['report']['cells'] if c['status'] not in ('PASS', 'PENDING_OWNER_UNION')]
        self.assertEqual(failing, [list(GATED)])
        self.validate(world, gate, gated)
        with self.assertRaisesRegex(ValueError, 'Only PASS on exposed cells'):
            world.D.create_phase(world.root, world.batches['exposure'], world.outputs['exposure'])
        self.assertFalse(world.outputs['exposure'].exists())

    def test_the_initializer_is_admitted_by_the_root_that_registers_it(self):
        world = K.EndToEnd(self)
        execution, state = world.initializer()
        self.assertEqual(state['config']['completedCurrent'], world.doc['currentEvidence'])
        self.assertEqual(state['prefit'], world.prefit)
        self.assertEqual(state['completed']['schema'], 'w50-completed-current-evidence-2')
        self.assertTrue(state['output'].is_relative_to(world.fit_dir/'fit'))
        root = copy.deepcopy(world.doc)
        root['inputs'] = [p for p in root['inputs'] if p != world.configs['initializer']]
        with self.assertRaisesRegex(ValueError, 'initializer fit source and config'):
            execution._admit.__globals__['_bootstrap'] = lambda path: type('D', (), {
                'root_doc': staticmethod(lambda p: root), 'verify_prefit': staticmethod(lambda p, d: world.prefit)})
            execution._admit(world.root)


if __name__ == '__main__':
    unittest.main()
