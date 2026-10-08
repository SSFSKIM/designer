"""The capture role through the REAL LIVE attempt/qualification journal; synthetic transports.

The transports below sit at CURRENT3's relative paths inside a temporary repository and write
the DL5h layout the real ones write (census, request, paired images/pages, pair manifest,
member-owned proof, raw record, run index). No browser, machine census, native data or real
capture tree is used. A conformance case pins the real transports' and helper's signatures.
"""
import contextlib
import hashlib
import importlib.util
import inspect
import io
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SECRET = 'NATIVE_SECRET_12345.875'
CURRENT3 = 'packages/calibration/results/2026-10-08-w50-g1-current3'


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value; spec.loader.exec_module(value); return value


K = module(HERE/'livekit.py', 'w50_capture_test_kit')

HELPER = r'''
import hashlib, json, sys, types
from pathlib import Path
S = types.SimpleNamespace(FIT=Path(__file__).resolve().parent,
    M=types.SimpleNamespace(N=types.SimpleNamespace(required_arguments=lambda inventory: set())))
def sha(raw): return hashlib.sha256(raw).hexdigest()
def _pin(path): return dict(path=str(path), sha256=sha(Path(path).read_bytes()))
def _read(pin):
    raw = Path(pin['path']).read_bytes()
    if sha(raw) != pin['sha256']: raise ValueError('Changed retained pin')
    return json.loads(raw)
def _folder(run, record):
    folder = Path(run['captureRoot'])
    if run['sceneSource'] == 'canonical': folder /= run['profile']
    return folder/record['scene']
def read_pair(context, run, record, pair_pin):
    folder = _folder(run, record)
    if pair_pin['path'] != str(folder/f'repeat__{record["renderer"]}.json'): raise ValueError('Pair aliases another member')
    pair = _read(pair_pin)
    return dict(pair=pair, pages=[_read(pair[side]['report']) for side in ('first', 'second')],
                envelope=_read(record['artifacts']['report']), identical=True, noise=0.0, folder=folder)
def receipt_binding(context, run, record, config, rows, *, needs_statistics=False):
    return dict(config=context['repeatAdmission']['config'], declaredRows=rows,
        **{name: sha(Path(context[field]).read_bytes()) for name, field in (('executionRootSha256', 'executionRoot'),
            ('contractSha256', 'contract'), ('batchSha256', 'batchPath'))})
def _body(binding, record, retained):
    return dict(schema='w50-repeat-admission-1', reading='first', scene=record['scene'], lane=record['lane'],
        manifest=record['repeatPair'], config=binding['config'], pair=retained['pair'],
        originalArtifacts={k: record['artifacts'][k] for k in ('png', 'report', 'cell')},
        declaredStatistics=[r['statistic'] for r in binding['declaredRows']],
        **{k: binding[k] for k in ('executionRootSha256', 'contractSha256', 'batchSha256')})
def retained_proof(output, run, record, retained):
    if record['repeatAdmission']['path'] != str(retained['folder']/f'repeat-admission__{run["renderer"]}.json'):
        raise ValueError('Repeat proof is not the member-owned receipt')
    return _read(record['repeatAdmission'])
def verify_pair_semantics(binding, run, record, retained, proof):
    if proof != _body(binding, record, retained): raise ValueError('Repeat receipt is not bound to this exact pair')
def admit_pair(context, run, record, pair_pin):
    dispatcher = sys.modules['w50_g1_dispatch']
    dispatcher.require_render_admission(context, run, current=record['lane'] == 'current')
    config = dispatcher.load(dispatcher.checked(context['repo'], context['repeatAdmission']['config']))
    rows = [r for r in dispatcher.load(dispatcher.checked(context['repo'], config['references']))['cells']
            if all(r[k] == record[k] for k in ('profile', 'renderer', 'scene'))]
    retained = read_pair(context, run, record, pair_pin)
    path = retained['folder']/f'repeat-admission__{run["renderer"]}.json'
    body = _body(receipt_binding(context, run, record, config, rows), {**record, 'repeatAdmission': None}, retained)
    with path.open('x') as stream: stream.write(json.dumps(body, indent=2)+'\n')
    return _pin(path)
'''

COMMON = r'''
import hashlib, json, sys, types
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
G0 = ROOT/'g0'
PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + (4).to_bytes(4, 'big') + (3).to_bytes(4, 'big') + b'synthetic'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path): return dict(path=str(path), sha256=sha(path))
def read_json(path): return json.loads(Path(path).read_text())
read = read_json
def write_new(path, value):
    with Path(path).open('x') as stream: stream.write(json.dumps(value, indent=2)+'\n')
write = write_new
def control():
    path = ROOT/'control.json'
    return read_json(path) if path.exists() else {}
def drew(run, scene, lane):
    with (ROOT/'draws.log').open('a') as log: log.write(f'{run["profile"]}|{scene}|{lane}\n')
def load_source(path, name):
    value = types.ModuleType(name); value.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec'), value.__dict__); return value
def census(output, scene, switch):
    observed = switch.get('census', {'passes': True})
    write_new(output/f'census-{scene}.json', observed)
    if observed.get('passes') is not True: raise ValueError(f'Classifying census refused: {observed.get("refusals")}')
def pair(folder, scene, tier, page):
    for side, suffix in (('first', ''), ('second', '__repeat')):
        (folder/f'{scene}__{tier}{suffix}.png').write_bytes(PNG)
        write_new(folder/f'page__{tier}__{side}.json', page)
    write_new(folder/f'report__{tier}.json', dict(page=page))
    write_new(folder/f'repeat__{tier}.json', dict(schema=1, kind='w50-retained-repeat-pair', reading='first',
        scene=scene, renderer=tier,
        first=dict(image=pin(folder/f'{scene}__{tier}.png'), report=pin(folder/f'page__{tier}__first.json')),
        second=dict(image=pin(folder/f'{scene}__{tier}__repeat.png'), report=pin(folder/f'page__{tier}__second.json'))))
'''

W50 = COMMON + r'''
def pin_file(pin, base=ROOT):
    path = (base/pin['path']).resolve()
    if sha(path) != pin['sha256']: raise ValueError('Changed pinned file')
    return path
def external(path): return Path(path).resolve()
def scene_plan(run, phase='fit'):
    scenes = ROOT/'scenes-w50.json'
    return dict(source='w50', scenesPath=str(scenes), scenesSha256=sha(scenes), canvas={'width': 4, 'height': 3},
        dpr=1, position=.25, scenes=[dict(scene=s, role='calibration', background='grey', span=2, pose='active')
                                    for s in run['scenes']])
def candidate_info(pin, position, *, current=False):
    path = pin_file(pin)
    endpoint = lambda pose: dict(path=str(path), sha256=sha(path), profileKey='synthetic-'+pose,
                                 resolvedMaterialSha256='0'*16, patch={})
    return dict(path=str(path), sha256=sha(path), endpoints={f'{pose}.{scheme}': endpoint(pose)
        for pose in ('active', 'receded') for scheme in ('light', 'dark')})
def fixture_info(run, plan):
    root = run['fixtures']['path']
    return dict(path=root, manifestSha256=run['fixtures']['manifestSha256'],
                backgrounds=[dict(key='grey@1x', path=root+'/grey.png', sha256='c'*64)])
def validate_report(envelope, run, endpoint, *, abscissa='silhouette', phase='fit'):
    page = envelope['page']
    if page.get('sceneId') not in run['scenes'] or page.get('candidate') != run['candidate']['sha256'] \
            or page.get('profileKey') != endpoint['profileKey']:
        raise ValueError('Synthetic report differs from its member')
    return [dict(scene=page['sceneId'], encodedLuminance=.5, provenance=dict(kind=abscissa))]
def admit_repeat(context, run, record):
    dispatcher = sys.modules['w50_g1_dispatch']
    helper = load_source(dispatcher.checked(ROOT, context['repeatAdmission']['entrypoint']), 'synthetic_repeat')
    return helper.admit_pair(context, run, record, record['repeatPair'])
def _capture_run(context, run, *, current):
    dispatcher = sys.modules['w50_g1_dispatch']
    dispatcher.require_render_admission(context, run, current=current)
    plan = scene_plan(run, context['phase']); lane = 'current' if current else 'candidate'
    candidate = candidate_info(run['candidate'], plan['position'], current=current)
    fixture = fixture_info(run, plan)
    for item in read_json(pin_file(run['webSourceClosure']))['sources']: pin_file(item)
    output, matrix = external(run['captureRoot']), external(run['matrixPath'])
    if output.exists() or matrix.exists(): raise ValueError('Capture root and scratch manifest are write-once')
    output.mkdir(parents=True); matrix.parent.mkdir(parents=True, exist_ok=True)
    switch = control(); records = []
    for spec in plan['scenes']:
        scene = spec['scene']; tier = run['renderer']
        census(output, scene, switch); drew(run, scene, lane)
        endpoint = candidate['endpoints'][f'{spec["pose"]}.dark']
        argv = ['node', 'capture-web.ts', '--renderer', tier, '--scale', str(plan['dpr']),
                '--candidate-document', candidate['path'], '--out', str(output), scene]
        write_new(output/f'request-{scene}.json', dict(argv=argv, sceneSource=plan['source'],
            scenesSha256=plan['scenesSha256'], candidate=run['candidate'], fixture=fixture,
            lane=switch.get('requestLane', lane)))
        (output/f'capture-{scene}.log').write_text('driver '+switch.get('print', '')+'\n')
        if switch.get('fail') == 'driver': raise ValueError('Capture refused for '+scene+switch.get('print', ''))
        folder = output/scene; folder.mkdir()
        pair(folder, scene, tier, dict(sceneId=scene, candidate=run['candidate']['sha256'],
                                       profileKey=endpoint['profileKey'], value=switch.get('print', '')))
        write_new(folder/f'cell__{tier}.json', dict(renderer=tier, colorSpace='srgb'))
        report = folder/f'report__{tier}.json'
        arguments = validate_report(read_json(report), run, endpoint, abscissa='source', phase=context['phase'])
        artifacts = {name: pin(path) for name, path in [('png', folder/f'{scene}__{tier}.png'), ('report', report),
                                                        ('cell', folder/f'cell__{tier}.json')]}
        for argument in arguments:
            argument['provenance'].update(report=artifacts['report'], capture=artifacts['png'],
                sceneSource=plan['source'], scenesSha256=plan['scenesSha256'], candidateDocument=run['candidate'],
                baseline=current, endpoint={k: v for k, v in endpoint.items() if k != 'patch'})
        record = dict(profile=run['profile'], renderer=tier, scene=scene, candidate=run['candidate'], lane=lane,
            sceneSource=plan['source'], canvas=plan['canvas'], dpr=plan['dpr'], artifacts=artifacts,
            arguments=arguments, background=fixture['backgrounds'][0])
        record['repeatPair'] = pin(folder/f'repeat__{tier}.json')
        if switch.get('fail') == 'before-admission': raise ValueError('Repeat outside the native band')
        record['repeatAdmission'] = admit_repeat(context, run, record)
        print('NATIVE '+switch.get('print', ''))
        if switch.get('fail') == 'after-admission': raise ValueError('Crash after admission '+switch.get('print', ''))
        if switch.get('rawExtra'):
            write_new(folder/'w50-capture.json', {**record, 'extra': 1}); raise ValueError('Crash after raw record')
        write_new(folder/'w50-capture.json', record); records.append(record)
        if switch.get('returnExtra'): record = records[-1] = {**record, 'extra': 1}
    write_new(matrix, dict(schema='w50-web-capture-index-1', captures=records))
    return records
'''

CANONICAL = COMMON + r'''
WEB = HERE.parent/'web'
SCENES = ROOT/'scenes.json'
def scene_plan(run, phase, document=None):
    return dict(scenes=[dict(id=s, state='rest', fixtureSet='calibration', component='c', background='bg')
                        for s in run['scenes']], dpr=1, scheme='dark', a11y='standard', position=.25,
                canvas={'width': 4, 'height': 3}, tints={}, components={'c': {'kind': 'rrect'}})
def validate_matrix(matrix, run, candidate):
    rows = matrix['cells']
    if [(r['key']['profileKey'], r['key']['web']['renderer'], r['key']['sceneId']) for r in rows] != \
            [(run['profile'], run['renderer'], s) for s in run['scenes']]:
        raise ValueError('Measured membership differs from run')
    if any(f'declarationSha256={run["candidate"]["sha256"][:12]}' not in r['key']['web']['capturePath'] for r in rows):
        raise ValueError('Candidate provenance differs')
    return rows
def validate_report(envelope, run, plan, scene, endpoint):
    page = envelope['page']
    if page.get('sceneId') != scene['id'] or page.get('candidate') != run['candidate']['sha256'] \
            or page.get('profileKey') != endpoint['profileKey']:
        raise ValueError('Synthetic canonical report differs')
def capture_artifacts(folder, scene, tier, web, dpr):
    meta = folder/f'cell__{tier}.json'; report = folder/f'report__{tier}.json'; png = folder/f'{scene["id"]}__{tier}.png'
    if read(meta) != web or web.get('renderer') != tier or web.get('colorSpace') != 'srgb':
        raise ValueError('Capture metadata differs or has wrong tier/colour space')
    header = png.read_bytes()[:24]
    if header[:8] != b'\x89PNG\r\n\x1a\n' or tuple(int.from_bytes(header[i:i+4], 'big') for i in (16, 20)) != (4*dpr, 3*dpr):
        raise ValueError('Capture dimensions differ from canonical raster')
    artifacts = {name: dict(path=str(p), sha256=sha(p)) for name, p in [('cell', meta), ('report', report), ('png', png)]}
    artifacts['files'] = [dict(path=str(p), sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()]
    return artifacts
def capture_run(context, run, *, current=False):
    dispatcher = sys.modules['w50_g1_dispatch']
    dispatcher.require_render_admission(context, run, current=current)
    plan = scene_plan(run, context['phase']); lane = 'current' if current else 'candidate'
    web = load_source(WEB/'adapter.py', 'synthetic_canonical_web')
    candidate = web.candidate_info(run['candidate'], plan['position'], current=current)
    for item in read(web.pin_file(run['webSourceClosure']))['sources']: web.pin_file(item)
    captures, matrix = web.external(run['captureRoot']), web.external(run['matrixPath'])
    captures.mkdir(parents=True); matrix.parent.mkdir(parents=True, exist_ok=True)
    write(captures/'native-request.json', dict(profile=run['profile'], scenes=run['scenes']))
    write(captures/'request.json', dict(argv=['compare'], run=run, phase=context['phase'], lane=lane,
        contractSha256=sha(context['contract']), batchSha256=sha(context['batchPath']), scenesSha256=sha(SCENES)))
    switch = control(); cells = []; tier = run['renderer']
    for scene in run['scenes']:
        census(captures, scene, switch); drew(run, scene, lane)
        paired = ['node', '--import', 'tsx', 'capture-web.ts', scene, '--renderer', tier, '--scale', '1',
                  '--candidate-document', candidate['path'], '--out', str(captures/run['profile']), '--alpha']
        write(captures/f'request-{scene}.json', dict(argv=['compare', '--scene', scene], paired=paired))
        folder = captures/run['profile']/scene; folder.mkdir(parents=True)
        (captures/f'capture-{scene}.log').write_text('paired\n')
        endpoint = candidate['endpoints']['active.dark']
        pair(folder, scene, tier, dict(sceneId=scene, candidate=run['candidate']['sha256'], profileKey=endpoint['profileKey']))
        metadata = dict(renderer=tier, colorSpace='srgb', capturePath=f'declarationSha256={run["candidate"]["sha256"][:12]}')
        write(folder/f'cell__{tier}.json', metadata)
        fresh = {str(p): sha(p) for p in folder.iterdir() if p.is_file()}
        (captures/f'compare-{scene}.log').write_text('compare\n'); write(captures/f'exit-{scene}.json', dict(returncode=0))
        write(captures/f'fresh-{scene}.json', dict(schema='w50-fresh-paired-input-1', artifacts=fresh))
        write(captures/f'native-admission-{scene}.json', {'synthetic': 'native admission'})
        cells.append(dict(key=dict(profileKey=run['profile'], sceneId=scene, web=metadata), fixtureSet='calibration'))
    write(matrix, dict(schemaVersion=5, cells=cells))
    records = []
    for row in validate_matrix(read(matrix), run, candidate['path']):
        scene = next(s for s in plan['scenes'] if s['id'] == row['key']['sceneId']); sid = scene['id']
        folder = captures/run['profile']/sid; endpoint = candidate['endpoints']['active.dark']
        validate_report(read(folder/f'report__{tier}.json'), run, plan, scene, endpoint)
        artifacts = capture_artifacts(folder, scene, tier, row['key']['web'], plan['dpr'])
        artifacts['transport'] = [pin(captures/name) for name in (f'census-{sid}.json', f'request-{sid}.json',
            f'exit-{sid}.json', f'compare-{sid}.log', f'capture-{sid}.log', f'fresh-{sid}.json', 'request.json',
            'native-request.json', f'native-admission-{sid}.json')]
        record = dict(profile=run['profile'], renderer=tier, scene=sid, sceneSource='canonical', lane=lane,
            candidate=run['candidate'], endpoint=endpoint, matrix=pin(matrix), row=row, artifacts=artifacts,
            coherenceStatus='NOT_APPLICABLE' if tier == 'webgpu' else 'MEASURED' if row.get('coherence') is not None else 'UNMEASURED')
        record['repeatPair'] = pin(folder/f'repeat__{tier}.json')
        record['repeatAdmission'] = web.admit_repeat(context, run, record)
        records.append(record)
    write(captures/'complete.json', dict(status='CAPTURED', captures=records, matrixSha256=sha(matrix)))
    return records
'''

NATIVE = '''import sys
def admit(context, config):
    sys.modules['w50_g1_dispatch'].require_native_admission(context)
def prepare(context, config):
    sys.modules['w50_g1_dispatch'].require_native_preparation(context)
    return {'ready': True, 'complete': True, 'stops': [], 'artifacts': []}
def verify(context, payload, config):
    assert payload == {'ready': True, 'complete': True, 'stops': [], 'artifacts': []}
'''
# LIVE admits the owner, metadata only, before the native marker (pre-seal review P1).
OWNER = '''import sys
def admit(context, config):
    sys.modules['w50_g1_dispatch'].require_owner_admission(context); return {'admitted': True}
def evaluate(context, captures, config):
    raise ValueError('synthetic owner is admission-only')
'''


def encoded(value): return (json.dumps(value, indent=2)+'\n').encode()


class Capture(unittest.TestCase):
    PROFILE = 'apple-macos-27.0-1x-dark-standard-glass0.25'

    def build(self, *, source='w50', phase='fit', scenes=('one', 'two'), transport_path=None):
        """A logical phase whose single run uses `source`; every pin named by the batch is fixed first."""
        files = {'candidate.json': encoded({'synthetic': 'candidate'}), 'baseline.json': encoded({'synthetic': 'baseline'}),
                 'closure.json': encoded({'sources': []})}
        pins = {name: {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()} for name, raw in files.items()}
        run = {'id': 'r', 'profile': self.PROFILE, 'renderer': 'css', 'sceneSource': source,
               'candidate': pins['candidate.json'], 'scenes': list(scenes), 'sets': ['calibration'],
               'captureRoot': 'unused', 'matrixPath': 'unused', 'webSourceClosure': pins['closure.json'],
               'fixtures': {'path': '/synthetic-fixtures', 'manifestSha256': 'f'*64, 'backgrounds': {}}}
        if phase == 'exposure': run['baselineCandidate'] = pins['baseline.json']
        kit = K.Kit(self, phase=phase, runs=[run], cohort=[pins['candidate.json']])
        for name, raw in files.items(): (kit.repo/name).write_bytes(raw)
        if transport_path: (kit.repo/transport_path).write_text(W50)
        for relative, text in ((CURRENT3+'/web/adapter.py', W50), (CURRENT3+'/canonical/adapter.py', CANONICAL),
                               ('repeat_helper.py', HELPER), ('g0/audit/numerical_guard.py',
                                'def validate_tone_values(argument):\n    assert "encodedLuminance" in argument\n')):
            path = kit.repo/relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
        kit.put('scenes.json', {'synthetic': 'canonical scenes'}); kit.put('scenes-w50.json', {'synthetic': 'w50 scenes'})
        repeat = kit.pin(kit.put('repeat-config.json', {'schema': 'w50-repeat-config-1', 'references': kit.references}))
        transports = {'canonical': kit.pin(kit.repo/CURRENT3/'canonical/adapter.py'),
                      'w50': kit.pin(kit.repo/(transport_path or CURRENT3+'/web/adapter.py'))}
        self.config = kit.pin(kit.put('capture-config.json', {'schema': 'w50-live-capture-config-1', 'transports': transports}))
        kit.doc.update(repeatAdmission={'entrypoint': kit.pin(kit.repo/'repeat_helper.py'), 'config': repeat},
                       inputs=[self.config, repeat, pins['closure.json']])
        kit.reseal()
        self.role = kit.register('capture', HERE/'capture.py', self.config)
        native = kit.repo/'native_role.py'; native.write_text(NATIVE)
        kit.register('native', native, kit.pin(kit.repo/'repeat-config.json'))
        owner = kit.repo/'owner_role.py'; owner.write_text(OWNER)
        kit.register('owner', owner, kit.pin(owner))
        self.kit = kit
        return kit

    def control(self, **value): self.kit.put('control.json', value)
    def draws(self):
        log = self.kit.repo/'draws.log'
        return log.read_text().splitlines() if log.exists() else []
    def attempt(self):
        kit = self.kit; a = kit.D.prepare_attempt(kit.root, kit.contract)
        return a, kit.D.execute_attempt(kit.root, kit.contract, a)
    def failure(self, ordinal=1):
        return json.loads((self.kit.store.attempts/f'{ordinal:06d}'/'failure.json').read_text())

    def check_checkpoints(self, count):
        kit = self.kit; rows = kit.store.checkpoints()
        self.assertEqual(len(rows), count)
        for row in rows:
            record = json.loads(Path(row['payload']['path']).read_text())
            self.assertEqual({k: record[k] for k in ('scene', 'lane')}, {'scene': row['member']['scene'], 'lane': row['member']['lane']})
            root = Path(row['member']['run']['captureRoot'])
            # Beside the member's own tree, LIVE adds the proof's root-input repeat config.
            outside = [p for p in row['artifacts'] if not Path(p['path']).is_relative_to(root.parent)]
            self.assertEqual([Path(p['path']).name for p in outside], ['repeat-config.json'])
            self.assertIn(record['repeatAdmission'], row['artifacts'])
        return rows

    def test_w50_member_is_drawn_once_verified_from_source_and_checkpointed(self):
        self.build()
        a, event = self.attempt()
        self.assertEqual(event['code'], 'ATTEMPT_COMPLETE')
        self.assertEqual(len(a['members']), 2); self.check_checkpoints(2)
        self.assertEqual(self.draws(), [f'{self.PROFILE}|one|candidate', f'{self.PROFILE}|two|candidate'])

    def test_canonical_member_reconstructs_from_its_compare_tree(self):
        self.build(source='canonical')
        self.assertEqual(self.attempt()[1]['code'], 'ATTEMPT_COMPLETE')
        record = json.loads(Path(self.check_checkpoints(2)[0]['payload']['path']).read_text())
        receipt = record['repeatAdmission']['path']
        self.assertNotIn(receipt, [p['path'] for p in record['artifacts']['files']])
        self.assertEqual(len(record['artifacts']['transport']), 9)

    def test_exposure_draws_candidate_and_current_baseline_members(self):
        self.build(phase='exposure', scenes=('one',))
        a, event = self.attempt()
        self.assertEqual(event['code'], 'ATTEMPT_COMPLETE')
        self.assertEqual(sorted(m['lane'] for m in a['members']), ['candidate', 'current'])
        records = [json.loads(Path(r['payload']['path']).read_text()) for r in self.check_checkpoints(2)]
        self.assertEqual({r['lane']: r['candidate']['path'] for r in records},
                         {'candidate': 'candidate.json', 'current': 'baseline.json'})

    def test_census_refusal_is_its_own_recoverable_stop(self):
        self.build(); self.control(census={'passes': False, 'refusals': ['captureProcessPresent', SECRET]})
        self.assertEqual(self.attempt()[1]['code'], 'CENSUS_REFUSED')
        self.assertEqual(self.failure()['code'], 'CENSUS_REFUSED'); self.assertEqual(self.draws(), [])
        (self.kit.repo/'control.json').unlink()
        b, event = self.attempt()
        self.assertEqual((b['ordinal'], len(b['members']), event['code']), (2, 2, 'ATTEMPT_COMPLETE'))

    def test_a_driver_failure_after_a_clean_census_is_an_instrument_fault(self):
        self.build(); self.control(fail='driver')
        self.assertEqual(self.attempt()[1]['code'], 'INSTRUMENT_FAULT')
        self.assertEqual(self.failure()['code'], 'INSTRUMENT_FAULT')

    def test_admitted_orphan_is_adopted_by_source_reconstruction_without_a_second_draw(self):
        self.build(); self.control(fail='after-admission')
        a, event = self.attempt()
        self.assertEqual(event['code'], 'INSTRUMENT_FAULT')
        (self.kit.repo/'control.json').unlink()
        b, event = self.attempt()
        self.assertEqual((b['ordinal'], len(b['members']), event['code']), (2, 1, 'ATTEMPT_COMPLETE'))
        adopted = [r for r in self.check_checkpoints(2) if 'revalidationClaim' in r]
        self.assertEqual([r['member'] for r in adopted], [a['members'][0]])
        self.assertEqual(self.draws(), [f'{self.PROFILE}|one|candidate', f'{self.PROFILE}|two|candidate'])

    def test_unadmitted_orphan_is_not_recovered_and_its_member_is_drawn_again(self):
        self.build(); self.control(fail='before-admission')
        self.assertEqual(self.attempt()[1]['code'], 'INSTRUMENT_FAULT')
        (self.kit.repo/'control.json').unlink()
        b, event = self.attempt()
        self.assertEqual((len(b['members']), event['code']), (2, 'ATTEMPT_COMPLETE'))
        self.assertEqual(self.draws().count(f'{self.PROFILE}|one|candidate'), 2)

    def test_admitted_orphan_that_does_not_reconstruct_is_refused_not_redrawn(self):
        for name, switch in (('foreign request', {'fail': 'after-admission', 'requestLane': 'current'}),
                             ('raw record', {'rawExtra': True})):
            with self.subTest(name):
                self.build(); self.control(**switch)
                self.assertEqual(self.attempt()[1]['code'], 'INSTRUMENT_FAULT')
                (self.kit.repo/'control.json').unlink()
                with self.assertRaisesRegex(ValueError, 'quarantined'):
                    self.kit.D.prepare_attempt(self.kit.root, self.kit.contract)
                self.assertEqual((self.kit.store.status()['retained'], len(self.kit.store._contracts())), (0, 1))

    def test_a_returned_record_that_differs_from_its_source_is_never_checkpointed(self):
        self.build(scenes=('one',)); self.control(returnExtra=True)
        self.assertEqual(self.attempt()[1]['code'], 'INSTRUMENT_FAULT')
        self.assertEqual(self.kit.store.status()['retained'], 0)

    def test_roles_refuse_outside_their_stage_and_foreign_transports(self):
        kit = self.build(scenes=('one',))
        with kit.lease():
            a, claim = kit.attempt_claim(); member = a['members'][0]
            with kit.stage('qualification', claim, [member]) as context:
                with self.assertRaisesRegex(ValueError, 'outside its LIVE stage'): self.role.capture(context, member, self.config)
                self.assertIsNone(self.role.recover(context, member, self.config))
            with kit.stage('capture', claim, [member]) as context:
                with self.assertRaisesRegex(ValueError, 'outside its LIVE stage'): self.role.recover(context, member, self.config)
            analysis = kit.analysis_claim()
            with kit.stage('analysis', analysis, [member]) as context:
                with self.assertRaisesRegex(ValueError, 'outside its LIVE stage'): self.role.verify(context, member, {}, self.config)
        self.build(scenes=('one',), transport_path='copied_adapter.py')
        self.assertEqual(self.attempt()[1]['code'], 'INSTRUMENT_FAULT'); self.assertEqual(self.draws(), [])

    def test_quarantine_canary_keeps_values_out_of_streams_events_errors_and_status(self):
        self.build(); self.control(fail='after-admission', print=SECRET)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            first = self.attempt()[1]
            (self.kit.repo/'control.json').unlink(); self.control(print=SECRET)
            second = self.attempt()[1]
            status = self.kit.D.public_status(self.kit.root, self.kit.contract)
        self.assertEqual((first['code'], second['code']), ('INSTRUMENT_FAULT', 'ATTEMPT_COMPLETE'))
        for public in (out.getvalue(), json.dumps(first), json.dumps(second), json.dumps(status),
                       json.dumps(self.failure())):
            self.assertNotIn(SECRET, public)
        log = self.kit.output/'attempts/000001/quarantine/worker.log'
        self.assertIn(SECRET, log.read_text())


class RealInterfaces(unittest.TestCase):
    """The real CURRENT3 transports and DL5h helper expose exactly what the role calls."""
    def test_signatures(self):
        repo = HERE.parents[4]
        source = lambda rel, name: module(repo/CURRENT3/rel, name)
        web, canonical = source('web/adapter.py', 'w50_capture_real_web'), source('canonical/adapter.py', 'w50_capture_real_canonical')
        helper = source('repeat/admission.py', 'w50_capture_real_repeat')
        params = lambda f: [(p.name, p.kind == p.KEYWORD_ONLY) for p in inspect.signature(f).parameters.values()]
        self.assertEqual(params(web._capture_run), [('context', False), ('run', False), ('current', True)])
        self.assertEqual(params(canonical.capture_run), [('context', False), ('run', False), ('current', True)])
        self.assertEqual(params(web.candidate_info), [('pin', False), ('position', False), ('current', True)])
        self.assertEqual(params(web.validate_report)[:3], [('envelope', False), ('run', False), ('endpoint', False)])
        self.assertEqual([n for n, _ in params(web.fixture_info)], ['run', 'plan'])
        self.assertEqual([n for n, _ in params(canonical.validate_matrix)], ['matrix', 'run', 'candidate'])
        self.assertEqual([n for n, _ in params(canonical.capture_artifacts)], ['folder', 'scene', 'tier', 'web', 'dpr'])
        self.assertEqual([n for n, _ in params(canonical.validate_report)], ['envelope', 'run', 'plan', 'scene', 'endpoint'])
        self.assertEqual([n for n, _ in params(helper.read_pair)], ['context', 'run', 'record', 'pair_pin'])
        self.assertEqual([n for n, _ in params(helper.retained_proof)], ['output', 'run', 'record', 'retained'])
        self.assertEqual(params(helper.receipt_binding)[-1], ('needs_statistics', True))
        self.assertEqual([n for n, _ in params(helper.verify_pair_semantics)], ['binding', 'run', 'record', 'retained', 'proof'])
        self.assertTrue(callable(helper.S.M.N.required_arguments) and (helper.S.FIT/'current-analysis/analysis.py').is_file())
        self.assertTrue((web.G0/'audit/numerical_guard.py').is_file() and canonical.SCENES.is_file())


if __name__ == '__main__':
    unittest.main()
