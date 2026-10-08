"""Mutation tests for the r2 owner-recovery witness (registered-2/witness.py; second pre-seal
review P3).

A synthetic tree laid out as the repository and the two external read directories are holds a
superseded and an r2 owner read: requests, instruments, closures, outputs, dispatch logs, the
evidence archives written by the real owner/r2/index.py, and a two-generation completed
inventory. The clean tree admits every link; each mutation below is one way a recovery could
drift, and each is listed under `unexpected`. No real evidence, capture or statistic is read.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
WITNESS = HERE/'registered-2/witness.py'
INDEX = HERE.parent/'owner/r2/index.py'
OTHER = hashlib.sha256(b'any other bytes').hexdigest()


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def sha(raw): return hashlib.sha256(raw).hexdigest()


class Tree:
    """One superseded/r2 owner read pair, consistent link by link."""

    def __init__(self, test):
        temp = tempfile.TemporaryDirectory()
        test.addCleanup(temp.cleanup)
        self.repo = Path(temp.name).resolve()
        self.fit = self.repo/'packages/calibration/results/2026-10-08-w50-g1-fit'
        self.owner = self.fit/'owner'
        self.old_read, self.new_read = self.repo/'g1-owner-read', self.repo/'g1-owner-read-r2'
        self.old_out, self.new_out = self.repo/'g1-completion', self.repo/'g1-completion-r2'
        self.here = self.fit/'completion/registered-2'
        for d in (self.owner/'r2', self.owner/'evidence', self.owner/'evidence-r2', self.old_read, self.new_read,
                  self.here, self.fit/'live-inputs',
                  self.old_out/'artifacts', self.new_out/'artifacts'):
            d.mkdir(parents=True, exist_ok=True)
        shutil.copy(INDEX, self.owner/'r2/index.py')
        self.W = source(WITNESS, f'w50_witness_under_test_{id(self)}')
        for name, value in (('HERE', self.here), ('FIT', self.fit), ('REPO', self.repo), ('OWNER', self.owner),
                            ('OLD_READ', self.old_read), ('NEW_READ', self.new_read),
                            ('OLD_OUT', self.old_out), ('NEW_OUT', self.new_out)):
            setattr(self.W, name, value)
        self.build()

    # files -----------------------------------------------------------------------------------
    def write(self, path, value):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((json.dumps(value, indent=1)+'\n').encode())
        return {'path': str(path), 'sha256': sha(path.read_bytes())}

    def read(self, path):
        raw = Path(path).read_bytes()
        return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)

    def edit(self, path, change):
        value = self.read(path)
        change(value)
        return self.write(path, value)

    def rel(self, path):
        return str(Path(path).relative_to(self.repo))

    def evidence(self, side):
        return self.owner/('evidence' if side == 'old' else 'evidence-r2')

    def output(self, side):
        return self.old_read if side == 'old' else self.new_read

    # the two reads -----------------------------------------------------------------------------
    def build(self):
        for side in ('old', 'new'):
            for name, value in (('contracts.json', {'contracts': side}), ('prepare.json', {'prepared': side})):
                pinned = self.write(self.output(side)/name, value)
                shutil.copy(pinned['path'], self.evidence(side)/name)
        self.write(self.owner/'source-closure.json', {'sources': [{'path': 'referee.ts', 'sha256': '1'*64}]})
        self.write(self.owner/'r2/source-closure.json', {'sources': [{'path': 'referee.ts', 'sha256': '2'*64}]})
        for directory, side in ((self.owner, 'old'), (self.owner/'r2', 'new')):
            self.write(directory/'contracts-request.json', {'mode': 'contracts'})
            self.write(directory/'prepare-request.json', {'mode': 'prepare'})
            self.write(directory/'projection-request.json', {
                'mode': 'project-current-batch', 'inputsPin': {'path': '/inputs', 'sha256': '3'*64},
                'completedReferencesPin': self.pin(self.evidence(side)/'prepare.json'),
                'contractsPin': self.pin(self.evidence(side)/'contracts.json')})
        for side in ('old', 'new'):
            report, contracts = self.pin(self.evidence(side)/'prepare.json'), self.pin(self.evidence(side)/'contracts.json')
            self.write(self.output(side)/'projection.json', {
                'schema': 'w50-owner-evidence-batch-1', 'reportPin': report, 'contractsPin': contracts,
                'inputsPin': {'path': '/inputs', 'sha256': '3'*64},
                'rows': [{'cellId': f'c{i}', 'row': {'profile': 'p', 'renderer': 'webgpu', 'scene': f's{i:03}',
                                                     'statistic': 'owner-contracts'},
                          'reportPin': report, 'contractsPin': contracts, 'axes': {'M1': {'state': 'NOT_APPLICABLE'}}}
                         for i in range(640)]})
        for mode, name in self.W.READS.items():
            for directory, side in ((self.owner, 'old'), (self.owner/'r2', 'new')):
                self.write(directory/f'{mode}-instrument.json', {
                    'schema': 'synthetic instrument', 'config': {'node': 'pinned'},
                    'request': self.pin(directory/f'{mode}-request.json'),
                    'closure': self.pin(directory/'source-closure.json'), 'output': str(self.output(side)/name)})
        index = source(self.owner/'r2/index.py', f'w50_witness_test_index_{id(self)}')
        for side in ('old', 'new'):
            (self.evidence(side)/'rows').mkdir()
            for path, raw in index.build(self.output(side)/'projection.json', self.evidence(side)).items():
                (self.repo/path).write_bytes(raw)
        for mode, name in self.W.READS.items():
            self.log(mode)
        rows = self.read(self.owner/'evidence/projection-index.json')['rows']
        artifact = {'old': self.old_out/'artifacts/a.json', 'new': self.new_out/'artifacts/a.json'}
        for side in ('old', 'new'):
            artifact[side].write_bytes(b'{"artifact": 1}\n')
            moved = (lambda p: p) if side == 'old' else self.W.to_r2
            self.write(self.fit/('live-inputs/completed-references.json' if side == 'old' else
                                 'live-inputs/completed-references-r2.json'), {'schema': 'synthetic', 'cells': [
                {'profile': 'p', 'renderer': 'webgpu', 'scene': 's000', 'statistic': 'owner-contracts',
                 'ownerEvidence': {'path': moved(rows[0]['evidence']['path']),
                                   'sha256': sha((self.repo/moved(rows[0]['evidence']['path'])).read_bytes())}},
                {'profile': 'p', 'renderer': 'webgpu', 'scene': 'cell', 'statistic': 'deep8',
                 'nativeEvidence': self.pin(artifact[side])}]})

    def pin(self, path):
        return {'path': str(path), 'sha256': sha(Path(path).read_bytes())}

    def log(self, read, **change):
        name = self.W.READS[read]
        entry = {'output': str(self.new_read/name), 'sha256': sha((self.new_read/name).read_bytes()),
                 'rootSha256': sha((self.owner/f'r2/{read}-instrument.json').read_bytes()),
                 'mode': self.read(self.owner/f'r2/{read}-request.json')['mode'], **change}
        (self.new_read/f'{read}-dispatch.log').write_text(json.dumps(entry)+'\n')

    # the witness ------------------------------------------------------------------------------
    def run(self, *links):
        L = self.W.Ledger()
        for link in links:
            getattr(self.W, link)(L)
        return L


LINKS = ('projections', 'instruments', 'evidence_archive', 'inventory')


class WitnessMutationTests(unittest.TestCase):
    def test_the_clean_synthetic_recovery_admits_every_link(self):
        t = Tree(self)
        L = t.run(*LINKS)
        self.assertEqual(L.unexpected, [])
        self.assertEqual(L.expected['projection reportPin'], 2*641)
        self.assertEqual(L.expected['index row evidence pin (directory and content pins)'], 640)
        self.assertEqual(L.expected['instrument: only request, closure and output replaced, each its r2 file'], 3)
        self.assertEqual(L.expected["dispatch log: the r2 instrument's output at its actual hash"], 3)
        self.assertEqual(L.expected["r2 evidence: index.py's archive of the logged projection output"], 1)
        self.assertEqual((L.expected['owner row ownerEvidence pin'], L.expected['artifact pin directory']), (2, 1))

    def test_a_moved_pin_holds_only_its_files_actual_hashes(self):
        t = Tree(self)
        old, new = t.pin(t.evidence('old')/'prepare.json'), t.pin(t.evidence('new')/'prepare.json')
        rename = t.W.evidence_files().get
        self.assertTrue(t.W.moved_pin(old, new, rename))
        for label, a, b in (('any other r2 hash', old, dict(new, sha256=OTHER)),
                            ('any other superseded hash', dict(old, sha256=OTHER), new),
                            ('the superseded hash carried over', old, dict(new, sha256=old['sha256'])),
                            ('a path that is not the successor', old, t.pin(t.evidence('new')/'contracts.json')),
                            ('a missing file with no hash', old, {'path': str(t.repo/'absent'), 'sha256': None}),
                            ('an extra field', old, dict(new, note='x'))):
            with self.subTest(label):
                self.assertFalse(t.W.moved_pin(a, b, rename))

    def test_projection_pins_name_the_r2_files_hashes(self):
        t = Tree(self)
        t.edit(t.new_read/'projection.json', lambda b: b['rows'][3]['reportPin'].update(sha256=OTHER))
        self.assertIn(['c3', 'reportPin/sha256'], t.run('projections').unexpected)
        t = Tree(self)
        t.edit(t.new_read/'projection.json', lambda b: b['contractsPin'].update(sha256=OTHER))
        self.assertIn(['batch', 'contractsPin/sha256'], t.run('projections').unexpected)

    def test_index_source_and_row_pins_name_their_files(self):
        index = lambda t: t.evidence('new')/'projection-index.json'
        t = Tree(self)
        t.edit(index(t), lambda i: i['rows'][5]['evidence'].update(sha256=OTHER))
        self.assertIn(['index', ['p', 'webgpu', 's005', 'owner-contracts']], t.run('projections').unexpected)
        t = Tree(self)
        t.edit(index(t), lambda i: i['source'].update(sha256=OTHER))
        self.assertIn(['index source'], t.run('projections').unexpected)
        # A row file whose bytes moved after the index named it.
        t = Tree(self)
        row = t.repo/t.read(index(t))['rows'][7]['evidence']['path']
        row.write_bytes(gzip.compress(b'{"changed": true}\n'))
        self.assertIn(['index', ['p', 'webgpu', 's007', 'owner-contracts']], t.run('projections').unexpected)

    def test_inventory_owner_evidence_and_artifact_pins_name_their_files(self):
        t = Tree(self)
        t.edit(t.fit/'live-inputs/completed-references-r2.json',
               lambda d: d['cells'][0]['ownerEvidence'].update(sha256=OTHER))
        self.assertIn(['p|webgpu|s000|owner-contracts', 'ownerEvidence/sha256'], t.run('inventory').unexpected)
        t = Tree(self)
        (t.new_out/'artifacts/a.json').write_bytes(b'{"artifact": 2}\n')
        self.assertIn(['p|webgpu|cell|deep8', 'nativeEvidence/path'], t.run('inventory').unexpected)

    def test_an_r2_instrument_replaces_only_request_closure_and_output(self):
        label = lambda mode: [mode, 'instrument', ['closure', 'config', 'output', 'request']]
        t = Tree(self)
        t.edit(t.owner/'r2/prepare-instrument.json', lambda i: i['config'].update(node='other'))
        self.assertIn(label('prepare'), t.run('instruments').unexpected)
        for field, change in (('request', {'sha256': OTHER}), ('closure', {'sha256': OTHER}),
                              ('request', {'path': str(t.owner/'contracts-request.json')})):
            with self.subTest(field=field, change=change):
                t = Tree(self)
                t.edit(t.owner/'r2/contracts-instrument.json', lambda i: i[field].update(change))
                self.assertIn(['contracts', 'instrument', ['closure', 'output', 'request']], t.run('instruments').unexpected)
        t = Tree(self)
        t.edit(t.owner/'r2/projection-instrument.json', lambda i: i.update(output=str(t.old_read/'projection.json')))
        self.assertIn(['projection', 'instrument', ['closure', 'request']], t.run('instruments').unexpected)

    def test_requests_move_only_the_projection_read_pins(self):
        t = Tree(self)
        t.edit(t.owner/'r2/contracts-request.json', lambda r: r.update(extra=True))
        self.assertIn(['contracts', 'request', ['extra']], t.run('instruments').unexpected)
        t = Tree(self)
        t.edit(t.owner/'r2/projection-request.json', lambda r: r['completedReferencesPin'].update(sha256=OTHER))
        self.assertIn(['projection', 'request', ['completedReferencesPin', 'contractsPin']],
                      t.run('instruments').unexpected)

    def test_a_dispatch_log_names_its_instrument_and_its_outputs_actual_hash(self):
        cases = {
            'any other output hash': lambda t: t.log('prepare', sha256=OTHER),
            'the superseded instrument as root': lambda t: t.log(
                'prepare', rootSha256=sha((t.owner/'prepare-instrument.json').read_bytes())),
            'another mode': lambda t: t.log('prepare', mode='contracts'),
            'an output that moved after the log': lambda t: (t.new_read/'prepare.json').write_bytes(b'{}\n'),
            'no log': lambda t: (t.new_read/'prepare-dispatch.log').unlink(),
        }
        for label, mutate in cases.items():
            with self.subTest(label):
                t = Tree(self)
                mutate(t)
                self.assertIn(['prepare', 'dispatch log'], t.run('instruments').unexpected)

    def test_the_r2_evidence_is_the_logged_outputs(self):
        t = Tree(self)
        (t.evidence('new')/'contracts.json').write_bytes(b'{"contracts": "edited"}\n')
        self.assertIn(['evidence copies', ['contracts.json']], t.run('evidence_archive').unexpected)
        rows = lambda t: sorted((t.evidence('new')/'rows').iterdir())
        cases = {
            'a row file': lambda t: rows(t)[0].write_bytes(gzip.compress(b'{}\n', mtime=0)),
            'the index': lambda t: (t.evidence('new')/'projection-index.json').write_bytes(b'{}\n'),
            'the whole read': lambda t: (t.evidence('new')/'projection.json.gz').write_bytes(gzip.compress(b'{}', mtime=0)),
            'an extra row file': lambda t: (t.evidence('new')/'rows/extra.json.gz').write_bytes(b''),
            'an extra file': lambda t: (t.evidence('new')/'note.txt').write_text('x'),
        }
        for label, mutate in cases.items():
            with self.subTest(label):
                t = Tree(self)
                mutate(t)
                unexpected = t.run('evidence_archive').unexpected
                self.assertEqual([u[0] for u in unexpected], ['evidence archive'])

    def test_the_prior_witness_must_reproduce_in_every_recorded_section(self):
        t = Tree(self)
        first = {'schema': 'w50-owner-recovery-witness-1', 'owner': {'closure': 1}, 'pins': {'r2': 2},
                 'admitted': {'closure referee.ts': 1}, 'unexpected': [], 'status': 'ONLY_RULED_DIFFERENCES',
                 'builder': {'path': 'w', 'sha256': '0'*64}}
        t.write(t.here/'recovery-witness.json', first)
        def check(record, counts):
            L = t.W.Ledger()
            L.expected.update(counts)
            t.W.prior(L, record)
            return L
        self.assertEqual(check({'owner': {'closure': 1}, 'pins': {'r2': 2}, 'reads': {}},
                               {'closure referee.ts': 1}).unexpected, [])
        self.assertEqual(check({'owner': {'closure': 9}, 'pins': {'r2': 2}}, {'closure referee.ts': 1}).unexpected,
                         [['prior witness', ['owner']]])
        self.assertEqual(check({'owner': {'closure': 1}, 'pins': {'r2': 2}}, {'closure referee.ts': 2}).unexpected,
                         [['prior witness', []]])


if __name__ == '__main__':
    unittest.main()
