"""Conformance: capture.py's source reconstruction against the REAL CURRENT3 paired transports.

verify() admits a LIVE member only if capture.reconstruct() rebuilds, field for field, the record its
transport returned. A reconstruction that drifts from the transport in any field therefore fails every
member of that scene source in the one-shot LIVE run, and a fault after the native/analysis markers
loses the one exposure (DL5k). test_capture.py meets synthetic stand-in transports only; this module
draws each member through the real bytes of web/adapter.py::_capture_run and
canonical/adapter.py::capture_run and asserts reconstruct() equals the returned record, in memory and
after the JSON round trip a retained checkpoint takes, on the candidate lane and on the exposure's
current-baseline lane (current=True), for both scene sources, at both tiers, scales and poses.

The synthetic repository holds byte-for-byte copies of every Python source the draft root's closure
executes, at their real relative paths, so the transports, the DL5h repeat helper they admit through
(current3/repeat/admission.py and its imports), the numerical guard and the canonical argument reader
all run compiled from their bytes, as capture.py loads them. The capture role is the real file,
registered through livekit.Kit with the real dispatcher context, GPU lease (a lock file in the
temporary tree), render admission and attempt journal. Every datum is synthetic: scenes, candidate and
shipped documents, backdrops and native pins live in temporary directories; no archive, checkpoint or
capture tree is opened.

Stubbed, identically for both sides, because each sits outside record assembly:
  * subprocess.run: the browser/driver (capture-web.ts) and compare (compare.ts) processes. Driver
    reads only what the real process is given (argv, env, the candidate document, the scenes file) and
    writes what it writes: pair.ts's retained pair and manifest, capture-web.ts's alpha image, cell and
    report envelope, compare.ts's native receipt and the --write-partial schema-5 matrix row. Any other
    launch fails the test, and subprocess.Popen refuses outright, so no real process can start.
  * the classifying census (2026-10-02-w43-g3-refit/stage/census.py): replaced at its path by an
    observe() that passes, because the real one reads this machine's process table. capture.py never
    runs a census; it reads the census record the transport wrote.
  * livekit.Kit's fixture boundary: root/phase admission and the numerical-admission module
    (endpoints, validate_numerical), as in test_capture.py.
Nothing in record assembly is stubbed: scene plans, candidate and fixture readers, report and matrix
validators, capture artifacts and the repeat admission receipt are the real code on both sides.
"""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

HERE = Path(__file__).resolve().parent
REAL_REPO = HERE.parents[4]
RESULTS = Path('packages/calibration/results')
CURRENT3 = RESULTS/'2026-10-08-w50-g1-current3'
FIT = RESULTS/'2026-10-08-w50-g1-fit'
G0 = RESULTS/'2026-10-08-w50-g0-declaration'
CENSUS = RESULTS/'2026-10-02-w43-g3-refit/stage/census.py'
P1 = 'apple-macos-27.0-1x-dark-standard-glass0.25'
P2 = 'apple-macos-27.0-2x-dark-standard-glass0.25'


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value; spec.loader.exec_module(value); return value


K = module(HERE/'livekit.py', 'w50_capture_conformance_kit')


def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value, indent=2)+'\n').encode()
def read(path): return json.loads(Path(path).read_text())


CENSUS_STANDIN = '''"""SYNTHETIC STAND-IN for the classifying census, which reads this machine's process table."""
def classify(rows): return {'refuse': [], 'annotate': []}
def observe():
    return dict(recordedAt='2026-10-09T00:00:00Z', x6={'synthetic': True}, refuse=[], annotate=[],
                refusals=[], passes=True)
'''

# Node/Vite closure inputs the transports require by content; never executed (subprocess.run is faked).
PLACEHOLDERS = ('pnpm-lock.yaml', 'packages/calibration/package.json', 'packages/calibration/cli/compare.ts',
                'packages/calibration/web/vite.config.ts',
                *(str(CURRENT3/'web'/n) for n in ('capture-web.ts', 'node-guard.mjs', 'vite-guard.mjs', 'host.mjs',
                                                   'pair.ts')),
                *(str(FIT/'web'/n) for n in ('node-guard.mjs', 'vite-guard.mjs')),
                str(CURRENT3/'canonical/compare.ts'), str(CURRENT3/'canonical/native-admission.ts'))
W50_SCENES = {'canvas': {'width': 512, 'height': 384},
    'components': {'span-96': {'kind': 'rrect', 'size': [96, 96], 'radius': 24},
                   'capsule-96': {'kind': 'capsule', 'size': [192, 96]}},
    'scenes': [{'id': 'cell-grey-004-s096__rest', 'background': 'grey-004', 'component': 'span-96', 'state': 'rest'},
               {'id': 'cell-grey-004-c096__inactive', 'background': 'grey-004', 'component': 'capsule-96',
                'state': 'inactive'}],
    'split': {'calibration': ['cell-grey-004-s096__rest', 'cell-grey-004-c096__inactive'], 'validation': [],
              'holdout': [], 'recorded': [], 'probe': []}}
CANONICAL_SCENES = {'canvas': {'width': 320, 'height': 200}, 'tints': {},
    'profiles': [{'key': P1, 'scenes': 'all'}, {'key': P2, 'scenes': 'all'}],
    'components': {'rrect-md': {'kind': 'rrect', 'size': [120, 44], 'radius': 12}},
    'scenes': [{'id': 'dark-solid__rrect-md__rest', 'background': 'dark-solid', 'component': 'rrect-md',
                'state': 'rest'},
               {'id': 'dark-solid__rrect-md__inactive', 'background': 'dark-solid', 'component': 'rrect-md',
                'state': 'inactive'}],
    'split': {'calibration': ['dark-solid__rrect-md__rest', 'dark-solid__rrect-md__inactive'], 'validation': [],
              'holdout': [], 'recorded': [], 'probe': []}}
SLOTS = [(pose, scheme) for pose in ('active', 'receded') for scheme in ('light', 'dark')]


def profile_key(pose, scheme, glass):
    return f'apple-macos-27.0-1x-{scheme}-standard-glass{glass}' + ('-receded' if pose == 'receded' else '')


def shipped(pose, scheme):
    return {'profileKey': profile_key(pose, scheme, '0.25'), 'resolvedMaterialSha256': sha(f'{pose}.{scheme}'.encode())[:16],
            'patch': {'tintAlpha': .7 if pose == 'active' else .8}}


def document(endpoints):
    """A complete candidate document, endpoint files pinned beside it (the driver's readCandidateDocument)."""
    files = {f'{pose}-{scheme}.json': encoded(endpoints[pose, scheme]) for pose, scheme in SLOTS}
    doc = {'kind': 'vitrea-candidate-material-document', 'schemaVersion': 1, 'glassTintAmount': .25,
           'cssTierMappingSha256': 'e'*64, 'endpoints': {f'{pose}.{scheme}': {'path': f'{pose}-{scheme}.json',
                                                                              'sha256': sha(files[f'{pose}-{scheme}.json'])}
                                                         for pose, scheme in SLOTS}}
    return {**files, 'document.json': encoded(doc)}


def candidate_endpoint(pose, scheme):
    """The fit lane's candidate: a lowEnd patch whose active dark endpoint reads the silhouette abscissa."""
    patch = {**shipped(pose, scheme)['patch'], 'lowEndStrength': 1}
    if (pose, scheme) == ('active', 'dark'): patch['backdropToneAbscissa'] = {'kind': 'silhouette'}
    return {'profileKey': profile_key(pose, scheme, '0.250'), 'resolvedMaterialSha256': sha(f'c{pose}{scheme}'.encode())[:16],
            'patch': patch}


class Driver:
    """subprocess.run for the two processes the transports launch (see the module docstring)."""
    VALUED = {'--renderer', '--scale', '--color-scheme', '--frames', '--candidate-document', '--out', '--accessibility'}

    def __init__(self): self.launches = []; self.images = {}

    def __call__(self, argv, **kwargs):
        argv = list(argv); script = next((Path(a).name for a in argv if a.endswith('.ts')), None)
        if argv[:3] != ['node', '--import', 'tsx'] or script not in ('capture-web.ts', 'compare.ts') \
                or Path(kwargs.get('cwd', '')).name != 'calibration':
            raise AssertionError(f'Unexpected process launch: {argv!r}')
        kwargs['stdout'].write(f'synthetic {script}\n')
        scene = (self.capture if script == 'capture-web.ts' else self.compare)(argv, kwargs['env'])
        self.launches.append((script, scene))
        return subprocess.CompletedProcess(argv, 0)

    def image(self, width, height, alpha=255):
        if (width, height, alpha) not in self.images:
            stream = io.BytesIO(); Image.new('RGBA', (width, height), (20, 20, 20, alpha)).save(stream, 'PNG')
            self.images[width, height, alpha] = stream.getvalue()
        return self.images[width, height, alpha]

    def capture(self, argv, env):
        """capture-web.ts: both loads retained by pair.ts, then the alpha image, cell and report envelope."""
        args = argv[next(i for i, a in enumerate(argv) if a.endswith('capture-web.ts'))+1:]
        options, scenes, i = {}, [], 0
        while i < len(args):
            if args[i] in self.VALUED: options[args[i]] = args[i+1]; i += 2
            elif args[i].startswith('--'): options[args[i]] = True; i += 1
            else: scenes.append(args[i]); i += 1
        (scene,) = scenes
        tier, dpr, scheme = options['--renderer'], int(options['--scale']), options['--color-scheme']
        doc = read(env['VITREA_SCENES']); spec = next(s for s in doc['scenes'] if s['id'] == scene)
        component, canvas = doc['components'][spec['component']], doc['canvas']
        pose = 'receded' if spec['state'] == 'inactive' else 'active'
        path = Path(options['--candidate-document']); raw = path.read_bytes(); candidate = json.loads(raw)
        endpoints = {slot: read(path.parent/item['path']) for slot, item in candidate['endpoints'].items()}
        drawn = endpoints[f'{pose}.{scheme}']
        abscissa = {**endpoints[f'active.{scheme}']['patch'], **drawn['patch']}.get('backdropToneAbscissa')
        width, height = canvas['width']*dpr, canvas['height']*dpr; w, h = component['size']
        family, radius = ('capsule', min(w, h)/2) if component['kind'] == 'capsule' else \
            ('fixed-rounded-rect', component['radius'])
        material = {'tuned': False, 'glassTintAmount': candidate['glassTintAmount'], 'profileKey': drawn['profileKey'],
                    'resolvedMaterialSha256': drawn['resolvedMaterialSha256']}
        y = .00121
        state = {'activeRenderer': tier, 'health': 'ok', 'materialDocument': dict(material),
                 'samplingBackend': 'gpu-texture' if tier == 'webgpu' else 'css-backdrop'}
        if isinstance(abscissa, dict):
            state['backdropToneAbscissae'] = [{'surfaceId': 'surface-0', 'kind': 'silhouette', 'sampleCount': 4096,
                                               'encodedLuminance': .0614, 'linearLuminance': y, 'color': [y]*3}]
        page = {'sceneId': scene, 'canvas': canvas, 'pixelSize': [width, height], 'devicePixelRatio': dpr,
            'requestedScale': dpr, 'requestedRenderer': tier, 'colorScheme': scheme, 'materialMode': 'candidate',
            'windowActivation': 'inactive' if pose == 'receded' else 'active', 'pressed': False,
            'transparentPage': False, 'frames': 32, 'canvasColorSpace': 'srgb',
            'candidateDocument': {'mode': 'candidate', 'declarationSha256': sha(raw)[:12]},
            'requestedBackdropLevel': None, 'requestedBackdropMode': 'texture',
            'accessibilityPolicy': {'reducedTransparency': False, 'increasedContrast': False, 'forcedColors': False,
                                    'reducedMotion': False},
            'background': {'id': spec['background'], 'naturalWidth': width, 'naturalHeight': height},
            'material': material,
            'groups': [{'id': 'group-0', 'configuredSource': 'texture', 'state': state,
                        'backdropTone': {'level': .0627, 'linearLuminance': y, 'rgb': [y]*3}}],
            'surfaces': [{'nodeId': 'surface-0', 'groupId': 'group-0', 'family': family, 'radius': radius,
                          'bounds': {'x': (canvas['width']-w)/2, 'y': (canvas['height']-h)/2, 'width': w, 'height': h}}]}
        folder = Path(options['--out'])/scene; folder.mkdir(parents=True)
        def save(name, data):
            with (folder/name).open('xb') as stream: stream.write(data)
            return {'path': str(folder/name), 'sha256': sha(data)}
        image, report = self.image(width, height), (json.dumps(page, indent=2)+'\n').encode()
        pair = {'schema': 1, 'kind': 'w50-retained-repeat-pair', 'reading': 'first', 'scene': scene, 'renderer': tier,
                'deterministic': True, 'repeatNoise': 0}
        for side, suffix in (('first', ''), ('second', '__repeat')):
            pair[side] = {'image': save(f'{scene}__{tier}{suffix}.png', image),
                          'report': save(f'page__{tier}__{side}.json', report)}
        save(f'repeat__{tier}.json', encoded(pair))
        if options.get('--alpha'): save(f'{scene}__{tier}__alpha.png', self.image(width, height, alpha=0))
        label = f'candidateDocument={os.path.relpath(path, env["W50_WEB_ROOT"])} declarationSha256={sha(raw)[:12]}'
        save(f'cell__{tier}.json', encoded({'engine': 'chromium', 'engineVersion': 'synthetic', 'renderer': tier,
            'samplingBackend': state['samplingBackend'], 'gpuAdapter': 'synthetic', 'colorSpace': 'srgb',
            'capturePath': f'synthetic driver deviceScaleFactor={dpr}, {label}', 'sceneId': scene,
            'pixelSize': [width, height], 'deterministic': True, 'repeatNoise': 0}))
        save(f'report__{tier}.json', encoded({'capturedAt': '2026-10-09T00:00:00.000Z', 'requestedRenderer': tier,
            'colorScheme': scheme, 'accessibility': None, 'materialProfile': None, 'recededProfile': None,
            'candidateDocument': {'declarationPath': str(path), 'declarationSha256': sha(raw)[:12]},
            'crossPosition': None, 'problems': [], 'page': page}))
        return scene

    def compare(self, argv, env):
        """compare.ts: the bounded native receipt, then the production compare's --write-partial row."""
        if argv[4] != '--admission' or argv[6] != '--receipt' or argv[8] != '--':
            raise AssertionError('Bounded admission arguments required')
        raw = Path(argv[5]).read_bytes(); request = json.loads(raw); rest = argv[9:]
        value = lambda flag: rest[rest.index(flag)+1]
        profile, tier, scene = value('--profile'), value('--renderer'), value('--scene')
        if sha(raw) != env['W50_NATIVE_REQUEST_SHA256'] or profile != request['profile'] \
                or scene not in request['scenes'] or value('--set') != ','.join(request['sets']):
            raise AssertionError('Compare arguments differ from admitted native run')
        with Path(argv[7]).open('xb') as stream:
            stream.write(encoded({'native': request['native'], 'fixtures': request['fixtures'], 'requestSha256': sha(raw)}))
        cell = read(Path(env['VITREA_WEB_CAPTURES'])/profile/scene/f'cell__{tier}.json')
        (role,) = [k for k, ids in read(env['VITREA_SCENES'])['split'].items() if scene in ids]
        row = {'key': {'profileKey': profile, 'sceneId': scene, 'web': cell,
                       'native': next(p for p in request['native'] if p['scene'] == scene)},
               'fixtureSet': role, 'metrics': {'ssim': .99, 'deltaE': .5}}
        if tier == 'css': row['coherence'] = {'deltaE': .25}
        matrix = Path(value('--out-matrix')); rows = read(matrix)['cells'] if matrix.exists() else []
        matrix.write_text(json.dumps({'schemaVersion': 5, 'cells': rows+[row]}, indent=2)+'\n')
        return scene


class TransportConformance(unittest.TestCase):
    def world(self, source, profile, renderer, scene):
        """One exposure phase whose single run draws `scene` on the candidate and current-baseline lanes."""
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup); external = Path(temp.name).resolve()
        files = {str(G0/'bed/scenes-w50.json'): encoded(W50_SCENES),
                 'apps/reference-apple/scenes.json': encoded(CANONICAL_SCENES),
                 **{p: b'// SYNTHETIC placeholder: never executed (subprocess.run is faked)\n' for p in PLACEHOLDERS}}
        closure = {'sources': [{'path': p, 'sha256': sha(raw)} for p, raw in sorted(files.items())]}
        for name, endpoints in (('candidate', {s: candidate_endpoint(*s) for s in SLOTS}),
                                ('baseline', {s: {**shipped(*s), 'profileKey': profile_key(*s, '0.250')} for s in SLOTS})):
            files.update({f'candidates/{name}/{n}': raw for n, raw in document(endpoints).items()})
        for pose, scheme in SLOTS:
            files[f'packages/calibration/profiles/{shipped(pose, scheme)["profileKey"]}.json'] = encoded(shipped(pose, scheme))
        files['closure.json'] = encoded(closure)
        pins = {name: {'path': path, 'sha256': sha(files[path])} for name, path in (
            ('candidate', 'candidates/candidate/document.json'), ('baseline', 'candidates/baseline/document.json'),
            ('closure', 'closure.json'))}
        backdrops = {f'grey-004@{n}x': f'grey-004@{n}x.png'.encode() for n in (1, 2)}
        (external/'fixtures').mkdir()
        for key, raw in backdrops.items(): (external/'fixtures'/f'{key}.png').write_bytes(b'synthetic backdrop '+raw)
        manifest = encoded({'backgrounds': {key: f'{key}.png' for key in backdrops}})
        (external/'fixtures/manifest.json').write_bytes(manifest)
        native = external/'native'/profile/f'{scene}.png'; native.parent.mkdir(parents=True)
        native.write_bytes(b'synthetic native pin, never opened\n'); (external/'native/manifest.json').write_text('{}\n')
        run = {'id': 'r', 'profile': profile, 'renderer': renderer, 'sceneSource': source, 'candidate': pins['candidate'],
               'baselineCandidate': pins['baseline'], 'scenes': [scene], 'sets': ['calibration'],
               'captureRoot': 'unused', 'matrixPath': 'unused', 'webSourceClosure': pins['closure'],
               'fixtures': {'path': str(external/'fixtures'), 'manifestSha256': sha(manifest), 'backgrounds': {
                   key: {'path': f'{key}.png', 'sha256': sha((external/'fixtures'/f'{key}.png').read_bytes())}
                   for key in backdrops}}}
        if source == 'canonical':
            run['nativeManifest'] = {'path': str(external/'native/manifest.json'), 'sha256': sha(b'{}\n')}
        kit = K.Kit(self, phase='exposure', runs=[run], cohort=[pins['candidate']])
        draft = read(K.newest_draft(REAL_REPO/FIT/'live-execution'))['closure']['sources']
        transports = [str(CURRENT3/rel) for rel in ('web/adapter.py', 'canonical/adapter.py', 'repeat/admission.py')]
        for relative in sorted({*draft, *transports}):
            target = kit.repo/relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REAL_REPO/relative, target)
        for relative, raw in files.items():
            target = kit.repo/relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        (kit.repo/CENSUS).write_text(CENSUS_STANDIN)
        cell = {'profile': profile, 'renderer': renderer, 'scene': scene, 'role': 'calibration',
                'statistic': 'deep8-channel-median' if source == 'w50' else 'low-end-path-level'}
        if source == 'canonical': cell['nativeEvidence'] = {'path': str(native), 'sha256': sha(native.read_bytes())}
        kit.references = kit.doc['references'] = kit.pin(kit.put('references.json', {
            'schema': 'w50-reference-inventory-1', 'cells': [cell]}))
        repeat = kit.pin(kit.put('repeat-config.json', {'schema': 'w50-repeat-config-1', 'references': kit.references}))
        config = kit.pin(kit.put('capture-config.json', {'schema': 'w50-live-capture-config-1', 'transports': {
            'canonical': kit.pin(kit.repo/CURRENT3/'canonical/adapter.py'), 'w50': kit.pin(kit.repo/CURRENT3/'web/adapter.py')}}))
        kit.doc.update(repeatAdmission={'entrypoint': kit.pin(kit.repo/CURRENT3/'repeat/admission.py'), 'config': repeat},
                       inputs=[config, repeat, pins['closure']])
        kit.reseal()
        for relative in transports: self.assertEqual((kit.repo/relative).read_bytes(), (REAL_REPO/relative).read_bytes())
        return kit, kit.register('capture', HERE/'capture.py', config), config

    def check(self, source, profile, renderer, scene):
        kit, role, config = self.world(source, profile, renderer, scene)
        driver = Driver()
        launches = [('capture-web.ts', scene)] + ([('compare.ts', scene)] if source == 'canonical' else [])
        refuse = mock.Mock(side_effect=AssertionError('No real process may start'))
        with mock.patch.object(subprocess, 'run', driver), mock.patch.object(subprocess, 'Popen', refuse), kit.lease():
            attempt, claim = kit.attempt_claim()
            self.assertEqual(sorted(m['lane'] for m in attempt['members']), ['candidate', 'current'])
            for member in attempt['members']:
                with self.subTest(source=source, profile=profile, lane=member['lane']), \
                        kit.stage('capture', claim, [member]) as context:
                    before = len(driver.launches)
                    record = role.capture(context, member, config)['record']
                    self.assertEqual(driver.launches[before:], launches)
                    live = sys.modules['w50_g1_dispatch']
                    rebuilt = role.reconstruct(context, member, member['run'], role.transports(context, live, config))
                    self.assertEqual(rebuilt, record)
                    # A qualification-stage verify reads the retained checkpoint back from JSON.
                    self.assertEqual(rebuilt, json.loads(json.dumps(record)))
                    role.verify(context, member, record, config)
                    self.witness(source, renderer, member, record)
        refuse.assert_not_called()

    def witness(self, source, renderer, member, record):
        """The world reached the branches it claims: the real DL5h receipt and each lane's own endpoint."""
        receipt = read(record['repeatAdmission']['path'])
        self.assertEqual((receipt['schema'], receipt['mode'], receipt['lane']),
                         ('w50-repeat-admission-1', 'byte-identical', member['lane']))
        endpoint = record['endpoint'] if source == 'canonical' else record['arguments'][0]['provenance']['endpoint']
        self.assertEqual('currentSource' in endpoint, member['lane'] == 'current')
        if source == 'w50':
            self.assertEqual(record['arguments'][0]['provenance']['kind'],
                             'silhouette' if member['lane'] == 'candidate' else 'source')
        else:
            self.assertEqual(record['coherenceStatus'], 'NOT_APPLICABLE' if renderer == 'webgpu' else 'MEASURED')

    def test_w50_reconstruction_equals_the_real_transport_record_on_both_lanes(self):
        self.check('w50', P1, 'webgpu', 'cell-grey-004-s096__rest')
        self.check('w50', P2, 'css', 'cell-grey-004-c096__inactive')

    def test_canonical_reconstruction_equals_the_real_transport_record_on_both_lanes(self):
        self.check('canonical', P1, 'webgpu', 'dark-solid__rrect-md__rest')
        self.check('canonical', P2, 'css', 'dark-solid__rrect-md__inactive')


if __name__ == '__main__':
    unittest.main()
