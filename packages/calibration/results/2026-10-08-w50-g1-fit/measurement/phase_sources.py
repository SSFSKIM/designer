"""Internal source-owned I/O for additive LIVE measurements, never native preparation or a verdict.

Exposed NEWBED runs capture.measure_capture's own checks and pure functions on the member's own
derived run (measure_exposed). Blind NEWBED uses the existing repeat reader's ACTUAL
preparation-chain validator and the immutable pure native-support evaluator, as readiness.py's
check-for-check mirrors (below); no native statistic is remeasured and no role is relabelled.
Canonical measurement consumes original published native/backdrop pins and frozen
seven-run/reference evidence, not a new reference fit. All live pairs use both source report
validators before first-image measurement.

LIVE stages its capabilities: render admission belongs to a remaining capture member, while this
reader runs in the analysis stage over checkpointed members under read admission. The immutable
helpers that authenticate through render admission (capture.measure_capture's batch-run lookup,
the repeat helper's live verify_receipt, current3's blind_exposure) are therefore replaced here by
their own checks over the member's run: the archived pair replay of live-roles/common.py and the
mirrors below. No helper's numerical or admission rule changes.

The blind read is the exposure's native checkpoint, ready or not (DL5n). Its blind source, its
typed-evidence reader and its support evaluator are readiness.py's: the sealed ones, check for
check, except that a not-ready read is admitted with exactly its checkpointed stops, a stopped
statistic is UNMEASURED (NATIVE_NOT_READY) and is not computed, and an incomplete reported
statistic is UNMEASURED (INCOMPLETE_READING, DL5m item 4). Each is a deterministic property of
the blind data, met after the analysis marker, so it must reach the judge as a reading.
"""
import copy
import gzip
from pathlib import Path
import re
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
CURRENT3 = FIT.parent/'2026-10-08-w50-g1-current3'
KEY = ('profile', 'renderer', 'scene', 'statistic')


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


Q = source(HERE/'projection.py', 'w50_phase_source_projection')
M = source(HERE/'capture.py', 'w50_phase_immutable_measurement')
W = source(CURRENT3/'web/adapter.py', 'w50_phase_paired_newbed')
C = source(CURRENT3/'canonical/adapter.py', 'w50_phase_paired_canonical')
R = source(FIT/'references/canonical.py', 'w50_phase_original_canonical')
B = source(CURRENT3/'repeat/sources.py', 'w50_phase_actual_blind_source')
L = source(FIT/'live-roles/common.py', 'w50_phase_live_role_common')
BR = source(HERE/'readiness.py', 'w50_phase_blind_readiness')


def indexed(rows):
    result = {}
    for row in rows:
        key = tuple(row[k] for k in KEY)
        if key in result: raise ValueError('Ambiguous source measurement key')
        result[key] = row
    return result


def pair(value):
    return {'activeSha256': value['active.dark'], 'recededSha256': value['receded.dark']}


def witness(support):
    return {k: copy.deepcopy(support[k]) for k in ('maskShape', 'maskPackedBitsSha256', 'pixels')}


class PhaseSources:
    def __init__(self, context, root, config):
        self.context, self.root, self.config = context, root, config
        self.dispatcher = sys.modules.get('w50_g1_dispatch')
        if self.dispatcher is None: raise ValueError('Source measurement requires actual live capability')
        self.dispatcher.require_context(context)
        if root != self.dispatcher.sealed(context['executionRoot']):
            raise ValueError('Source reader root differs from the actual registered root')
        self.repo = Path(context['repo']); self.output = Path(context['output'])
        # The root's own composed current evidence (authority.current_authority binds its ordered
        # instrument/result chains at root admission); measured against these same native reads.
        current = self.registered(config['completedCurrentEvidence'])
        native = current.get('native') or {}
        if config['completedCurrentEvidence'] != root.get('currentEvidence') \
                or current.get('schema') != 'w50-completed-current-evidence-2' or current.get('status') != 'EVIDENCE_ONLY' \
                or 'currentInstrument' in current or current.get('currentComposition') != root.get('currentComposition') \
                or current.get('originals', {}).get('references') != root['references'] \
                or current.get('originals', {}).get('scenes') != config['native']['scenes'] \
                or native.get('batch') != config['native']['batch'] or native.get('reports') != config['native']['reports']:
            raise ValueError('Current measurements differ from the root-bound composed current evidence')
        self.current = indexed(current['referenceEvidence'])
        canonical = self.registered(config['canonicalReferenceEvidence'])
        if canonical.get('schema') != 'w50-canonical-reference-evidence-1':
            raise ValueError('Unknown original canonical reference evidence')
        self.canonical = indexed([row for rows in canonical['partitions'].values() for row in rows])
        self.scenes = self.registered(config['native']['scenes'])
        self.native_batch = self.registered(config['native']['batch'])
        if self.native_batch.get('schema') != 'w50-native-read-batch-1' \
                or self.native_batch['inputs']['scenes'] != config['native']['scenes'] \
                or self.native_batch['inputs']['manifest'] != root['manifest']:
            raise ValueError('Native source batch differs from the actual root/scene declaration')
        self.reports = {}; self.canonical_cache = {}; self._readiness = None

    def readiness(self):
        """The exposure's native checkpoint metadata, read once (readiness.native_readiness)."""
        if getattr(self, '_readiness', None) is None:
            self._readiness = BR.native_readiness(self.context, self.dispatcher)
        return self._readiness

    def registered(self, pin):
        if pin not in self.root['inputs'] or pin not in self.context['inputs']:
            raise ValueError('Source measurement document is not an admitted input')
        path = self.dispatcher.checked(self.repo, pin)
        raw = path.read_bytes()
        return M._json(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)

    def verify_repeat(self, run, receipt):
        """The archived DL5h pair replay: both retained images/reports through the transports' pure
        validators and the member-owned proof's original statistic band."""
        if not receipt.get('repeatPair') or not receipt.get('repeatAdmission'):
            raise ValueError('Every new live measurement requires both retained repeat receipts')
        return L.archived_pair(self.context, self.dispatcher, run, receipt, {'canonical': C, 'w50': W})

    def authenticate(self, run, receipt):
        self.dispatcher.require_read_admission(self.context, run, current=receipt['lane'] == 'current')
        if not receipt.get('repeatPair') or not receipt.get('repeatAdmission'):
            raise ValueError('Every new live measurement requires both retained repeat receipts')
        canonical = run['sceneSource'] == 'canonical'
        if not canonical and run['sceneSource'] != 'w50': raise ValueError('Unknown live scene source')
        plan = C.scene_plan(run, self.context['phase']) if canonical else W.scene_plan(run, self.context['phase'])
        spec = next(s for s in plan['scenes'] if s['id' if canonical else 'scene'] == receipt['scene'])
        folder = Path(run['captureRoot'])
        if canonical: folder /= run['profile']
        folder /= receipt['scene']
        blobs = {}
        for name, filename in (('png', f'{receipt["scene"]}__{receipt["renderer"]}.png'),
                               ('report', f'report__{receipt["renderer"]}.json'),
                               ('cell', f'cell__{receipt["renderer"]}.json')):
            pin = receipt['artifacts'][name]
            if pin.get('path') != str(folder/filename):
                raise ValueError('Measurement artifact aliases another admitted run/member')
            blobs[name] = M._pin_bytes(pin, self.output, external=True)
        metadata, envelope = M._json(blobs['cell']), M._json(blobs['report'])
        if metadata.get('renderer') != run['renderer'] or metadata.get('colorSpace') != 'srgb' \
                or f'declarationSha256={run["candidate"]["sha256"][:12]}' not in metadata.get('capturePath', ''):
            raise ValueError('Actual first-reading metadata differs from admitted candidate/tier')
        self.verify_repeat(run, receipt)
        if canonical:
            matrix_pin = receipt['matrix']
            if matrix_pin['path'] != run['matrixPath']: raise ValueError('Canonical matrix aliases another run')
            matrix = M._json(M._pin_bytes(matrix_pin, self.output, external=True))
            rows = C.validate_matrix(matrix, run, self.repo/run['candidate']['path'])
            row = next(r for r in rows if r['key']['sceneId'] == receipt['scene'])
            if row != receipt['row'] or metadata != row['key']['web']:
                raise ValueError('Canonical first image, metadata and matrix row differ')
        candidate = W.candidate_info(run['candidate'], plan['position'], current=receipt['lane'] == 'current')
        pose = ('receded' if spec['state'] == 'inactive' else 'active') if canonical else spec['pose']
        scheme = plan['scheme'] if canonical else 'dark'
        slot = pose+'.'+scheme
        endpoint = candidate['endpoints'][slot]
        if canonical:
            C.validate_report(envelope, run, plan, spec, endpoint)
        material = {'candidateDocument': copy.deepcopy(run['candidate']),
            'documentPair': {'activeSha256': candidate['endpoints']['active.'+scheme]['sha256'],
                             'recededSha256': candidate['endpoints']['receded.'+scheme]['sha256']},
            'endpoints': {name: {k: copy.deepcopy(value) for k, value in item.items() if k != 'patch'}
                          for name, item in candidate['endpoints'].items()},
            'drawnEndpoint': {k: copy.deepcopy(v) for k, v in endpoint.items() if k != 'patch'},
            'reportedMaterial': copy.deepcopy(envelope['page'].get('material')),
            'samplingBackends': [{ 'groupId': g['id'], 'samplingBackend': g['state']['samplingBackend']}
                                 for g in envelope['page']['groups']]}
        evidence = {'capture': copy.deepcopy(receipt['artifacts']['png']),
            'report': copy.deepcopy(receipt['artifacts']['report']), 'cell': copy.deepcopy(receipt['artifacts']['cell']),
            'repeatPair': copy.deepcopy(receipt['repeatPair']), 'repeatAdmission': copy.deepcopy(receipt['repeatAdmission']),
            'reading': 'first', 'material': material}
        return plan, spec, blobs, evidence

    def declarations(self, run, plan, spec, *, cell=None, family=None):
        if run['sceneSource'] == 'w50':
            return {'sceneSource': 'w50', 'family': cell['family'], 'inputCode': cell.get('level'),
                'span': spec['span'], 'pose': spec['pose'], 'scale': plan['dpr'], 'position': plan['position']}
        component = plan['components'][spec['component']]
        return {'sceneSource': 'canonical', 'family': family, 'inputCode': None,
            'span': min(component['size']) if 'size' in component else None,
            'pose': 'receded' if spec['state'] == 'inactive' else 'active',
            'scale': plan['dpr'], 'position': plan['position']}

    def measure_member(self, run, receipt, rows):
        self.dispatcher.require_read_admission(self.context, run, current=receipt['lane'] == 'current')
        if run['sceneSource'] == 'w50' and any(r['role'] == 'blind' for r in rows):
            return self.blind(run, receipt, rows)
        if run['sceneSource'] == 'w50':
            plan = W.scene_plan(run, self.context['phase'])
            spec = next(s for s in plan['scenes'] if s['scene'] == receipt['scene'])
            role = spec['role']; pin = self.config['native']['reports'][role]
            measured = measure_exposed(self.context, self.dispatcher, run, pin, receipt,
                self.config['native']['scenes'], native_batch_pin=self.config['native']['batch'],
                verify_repeat=self.verify_repeat)
            report = self.reports.setdefault(role, self.registered(pin))
            cell = M.R.unique(report['cells'], 'id', 'native cell')[receipt['profile']+'/'+receipt['scene']]
            _, _, _, evidence = self.authenticate(run, receipt)
            evidence.update(copy.deepcopy(measured['evidence']))
            runs = [r['evidence'] for r in cell['runs']]
            for statistic in measured['statistics'].values():
                statistic['nativeRuns'] = copy.deepcopy(runs)
                statistic['nativeProvenance'] = {k: copy.deepcopy(evidence[k]) for k in
                    ('nativeRead', 'nativeBatch', 'nativeDependency', 'scenes')}
            return {'statistics': measured['statistics'], 'evidence': evidence,
                'material': evidence['material'], 'declaration': self.declarations(run, plan, spec, cell=cell),
                'nativeCell': cell, 'arguments': measured['arguments']}
        return self.canonical_member(run, receipt, rows)

    def blind(self, run, receipt, rows):
        if self.context['phase'] != 'exposure' or any(r['role'] != 'blind' for r in rows):
            raise ValueError('Original blind population may only be measured inside exposure')
        plan, spec, blobs, evidence = self.authenticate(run, receipt)
        readiness = self.readiness()
        cell, dependency, export, provenance = BR.blind_cell(self.context, run, rows[0], self.scenes, readiness)
        if [r['run'] for r in cell['runs']] != [1, 2, 3] or set(cell['statistics']) != {r['statistic'] for r in rows}:
            raise ValueError('Blind measurements must preserve the exact original three-run statistic population')
        background = M.R.read_verified_frame(export, dependency, self.scenes['canvas'], plan['dpr'])
        web = M.R.S.decode_png(blobs['png'])
        scene = next(s for s in self.scenes['scenes'] if s['id'] == receipt['scene'])
        masks = M.R.S.analytical_masks(self.scenes['components'][scene['component']], self.scenes['canvas'],
            plan['dpr'], web.shape[:2], background=background,
            impulse=self.scenes['backgrounds'][scene['background']]['kind'] == 'impulse')
        if cell['family'] == 'uniform': del masks['deep8_far24']
        measured = BR.evaluate_supports(web, cell, masks, renderer=run['renderer'],
                                        stopped=BR.stopped(readiness, cell['id']))
        evidence.update(copy.deepcopy(provenance))
        for statistic in measured['statistics'].values():
            statistic['nativeRuns'] = [copy.deepcopy(r['evidence']) for r in cell['runs']]
            statistic['nativeProvenance'] = copy.deepcopy(provenance)
        return {'statistics': measured['statistics'], 'evidence': evidence, 'material': evidence['material'],
            'declaration': self.declarations(run, plan, spec, cell=cell), 'nativeCell': cell}

    def blind_envelope(self, row, measured):
        cell, evidence = measured['nativeCell'], measured['evidence']
        if row['role'] != 'blind' or any(row[k] != cell[k] for k in ('profile', 'scene', 'role')) \
                or row['nativeIdentity'] != cell['id'] or row['referenceIdentity'] != cell['reference'] \
                or row['statistic'] not in cell['statistics'] or [r['run'] for r in cell['runs']] != [1, 2, 3]:
            raise ValueError('Blind typed envelope differs from the exact original row/run population')
        artifact = M._json(M._pin_bytes(evidence['nativeExposure'], self.output, external=True))
        if artifact['nativeRead'] != evidence['nativeRead']:
            raise ValueError('Blind envelope substituted its actual preparation reading')
        return {'schema': 'w50-native-three-run-evidence-1',
            **{k: copy.deepcopy(row[k]) for k in
               ('profile', 'scene', 'statistic', 'nativeIdentity', 'referenceIdentity', 'role', 'support')},
            'runs': [copy.deepcopy(r['evidence']) for r in cell['runs']],
            'nativeRead': copy.deepcopy(evidence['nativeRead']), 'nativeExposure': copy.deepcopy(evidence['nativeExposure']),
            'nativeExport': {'role': 'blind', 'root': artifact['export']['path'],
                             'indexSha256': artifact['export']['indexSha256']}}

    def native_evidence(self, manifest):
        """current3's NativeEvidence, reading the native checkpoint's readiness as admitted (DL5n)."""
        module = source(CURRENT3/'execution/native_evidence.py', 'w50_phase_blind_native_evidence')
        return BR.readiness_view(module.NativeEvidence, self.readiness())(self.context['repo'], manifest)

    def validate_blind_rows(self, rows):
        """current3 execution/blind_exposure.validate_blind_exposure (DL5g), check for check, except
        that each lane is authenticated through its OWN checkpointed member: the receipt must equal
        its checkpoint (resolve_capture_run) and the member run is read-admitted, where the original
        render-admitted the batch run and its baseline_run derivative, and that native_evidence
        reads a not-ready checkpoint's readiness as admitted (DL5n)."""
        context, live = self.context, self.dispatcher
        live.require_context(context)
        if context.get('phase') != 'exposure' or context.get('batch', {}).get('phase') != 'exposure':
            raise ValueError('Blind evidence validation is exposure-only')
        root = live.sealed(context['executionRoot'])
        evidence = self.native_evidence(root['manifest'])
        original = evidence.read(root['references'])
        expected = {tuple(r[k] for k in KEY): r for r in original['cells'] if r['role'] == 'blind'}
        if not isinstance(rows, list) or not expected:
            raise ValueError('Blind exposure needs the full original reference population')
        actual = []
        for row in rows:
            if not isinstance(row, dict) or any(k not in row for k in KEY): raise ValueError('Missing blind reference identity')
            actual.append(tuple(row[k] for k in KEY))
        if len(actual) != len(set(actual)) or set(actual) != set(expected):
            raise ValueError('Blind exposure evidence must cover every original blind key exactly once')
        cohort = context['batch']['cohort']; output = Path(context['output']).resolve()
        for row in rows:
            before = expected[tuple(row[k] for k in KEY)]
            for key in ('role', 'support', 'nativeIdentity', 'referenceIdentity', 'currentGeneration', 'currentDocumentPair'):
                if row.get(key) != before.get(key): raise ValueError('Blind exposure changed original provenance')
            runs = [r for r in context['batch']['runs'] if r['profile'] == row['profile'] and
                    r['renderer'] == row['renderer'] and row['scene'] in r['scenes']]
            if len(runs) != 1: raise ValueError('Blind row is outside its exact exposure run')
            run = runs[0]
            if run['candidate'] not in cohort or run.get('baselineCandidate') not in root.get('baselineDocuments', []):
                raise ValueError('Blind row needs same-cohort candidate and registered frozen-current baseline')
            for field, lane in (('candidateCapture', 'candidate'), ('currentCapture', 'current')):
                capture = row.get(field)
                if not isinstance(capture, dict) or capture.get('lane') != lane:
                    raise ValueError('Blind capture is missing or names another scene/material/lane')
                live.require_read_admission(context, live.resolve_capture_run(context, capture), current=lane == 'current')
            evidence.validate(row, row.get('nativeEvidence'), exposure=context)
            scale = re.search(r'-([12])x-', row['profile'])
            if not scale: raise ValueError('Blind profile lacks its declared scale')
            dimensions = [512*int(scale[1]), 384*int(scale[1])]
            for field, lane, candidate in (('currentCapture', 'current', run['baselineCandidate']),
                                           ('candidateCapture', 'candidate', run['candidate'])):
                capture = row.get(field)
                if not isinstance(capture, dict) or capture.get('lane') != lane or capture.get('candidate') != candidate or any(
                        capture.get(k) != row[k] for k in KEY[:3]):
                    raise ValueError('Blind capture is missing or names another scene/material/lane')
                evidence.check(candidate)
                artifacts = capture.get('artifacts', {})
                for key in ('png', 'cell', 'report'):
                    target = evidence.check(artifacts.get(key))
                    if not target.is_relative_to(output): raise ValueError('Blind capture is outside the single exposure output')
                evidence.png(artifacts['png'], dimensions)
                metadata = evidence.read(artifacts['cell']); page = evidence.read(artifacts['report']).get('page', {})
                if (metadata.get('sceneId') != row['scene'] or metadata.get('renderer') != row['renderer'] or
                        metadata.get('pixelSize') != dimensions or page.get('sceneId') != row['scene'] or
                        page.get('requestedRenderer') != row['renderer'] or page.get('devicePixelRatio') != int(scale[1]) or
                        page.get('materialMode') != 'candidate' or page.get('candidateDocument', {}).get('mode') != 'candidate' or
                        page.get('candidateDocument', {}).get('declarationSha256') != candidate['sha256'][:12] or
                        f'declarationSha256={candidate["sha256"][:12]}' not in metadata.get('capturePath', '')):
                    raise ValueError('Blind capture metadata/report does not attest the same actual draw')
        evidence.finish(); live.require_context(context)
        return {'schema': 'w50-bound-blind-exposure-evidence-1', 'status': 'BOUND_BLIND_EVIDENCE',
                'cells': len(rows), 'candidateSha256s': sorted(p['sha256'] for p in cohort)}

    def canonical_record(self, row):
        item = self.canonical[tuple(row[k] for k in KEY)]
        reference = item['reference']
        if any(reference.get(k) != row.get(k) for k in
               (*KEY, 'role', 'support', 'currentGeneration', 'currentDocumentPair', 'historical')):
            raise ValueError('Canonical companion changed original reference provenance/history')
        if item.get('status') != 'MEASURED' or item['pins']['native'] != row['nativeEvidence']:
            raise ValueError('Canonical source is unavailable or substituted another native PNG')
        return item

    def canonical_member(self, run, receipt, rows):
        plan, spec, blobs, evidence = self.authenticate(run, receipt)
        statistics = {}; record_map = {}
        owner_only = all(r['statistic'] == 'owner-contracts' for r in rows)
        if owner_only:
            family = 'owner'
        else:
            items = [self.canonical_record(r) for r in rows if r['statistic'] != 'owner-contracts']
            pins = items[0]['pins']
            if any(item['pins']['native'] != pins['native'] or item['pins']['background'] != pins['background']
                   or item['pins']['scenes'] != pins['scenes'] for item in items):
                raise ValueError('Canonical subreadings disagree on original native/backdrop/scene pins')
            doc = R.json_pin(pins['scenes'])
            if Path(pins['scenes']['path']).resolve() != C.SCENES or doc['canvas'] != plan['canvas']:
                raise ValueError('Canonical source scene declaration was substituted')
            shape = (plan['canvas']['height']*plan['dpr'], plan['canvas']['width']*plan['dpr'])
            native, background = (R.decode_verified(pins[name], shape) for name in ('native', 'background'))
            web = M.R.S.decode_png(blobs['png'])
            kind = doc['backgrounds'][spec['background']]['kind']
            family = kind if kind in ('solid', 'impulse') else 'texture'
            measured = R.M.canonical_read(native, background, plan['components'][spec['component']],
                plan['canvas'], plan['dpr'], web_rgb=web,
                text=any(r['statistic'] == 'T1-low' for r in rows), impulse=family == 'impulse')
            for item in items:
                self.canonical_cache[tuple(item[k] for k in KEY)] = item
                for name, frozen in item['readings'].items():
                    if name not in measured['web']['statistics']: continue
                    produced = measured['web']['statistics'][name]
                    original_support = measured['supports'][produced['support']]
                    frozen_support = item['publishedReading']['supports'][produced['support']]
                    if witness(original_support) != witness(frozen_support) or measured['statistics'][name]['value'] != frozen['native']:
                        raise ValueError('Canonical native support/reading differs from the pinned reference report')
                    production = statistics.get(name, {}).get('productionStatistic')
                    statistics[name] = dict(copy.deepcopy(produced), measurementStatus=produced['status'],
                        nativeValue=copy.deepcopy(frozen['native']), nativeRepeat=copy.deepcopy(frozen['repeat']),
                        required=True, nativeSupportWitnesses=[witness(original_support)],
                        nativeImage=copy.deepcopy(pins['native']), nativeProvenance={
                            'referenceReport': self.config['canonicalReferenceEvidence'],
                            'native': copy.deepcopy(pins['native']), 'background': copy.deepcopy(pins['background']),
                            'scenes': copy.deepcopy(pins['scenes'])})
                    record_map[name] = item
                    if production is not None:
                        statistics[name]['productionStatistic'] = copy.deepcopy(production)
                    if name == item['statistic'] and Q.frozen_scope(item['reference']):
                        full = name == 'T1-full-silhouette'
                        value = produced['value']
                        if full:
                            material = receipt['row'].get('material')
                            metric = (material or {}).get('interiorStdDevWeb')
                            if metric is not None and metric.get('units') != 'luminance':
                                raise ValueError('Production full-T1 statistic has wrong units')
                            value = None if metric is None else metric['value']
                        statistics[name]['productionStatistic'] = {
                            'estimator': 'PRODUCTION_TS_INTERIOR_LEVEL' if full else 'CANONICAL_NUMPY_GAUSSIAN_LOW',
                            'statistic': name,
                            'producer': 'packages/calibration/src/metrics/material.ts#interiorLevel' if full else
                                'packages/calibration/results/2026-10-08-w50-g1-fit/references/statistics.py#canonical_read',
                            'field': 'material.interiorStdDevWeb' if full else 'web.statistics.T1-low',
                            'reading': 'first', 'capture': copy.deepcopy(evidence['capture']),
                            'matrix': copy.deepcopy(receipt['matrix']), 'scene': receipt['scene'],
                            'units': 'linear-luma', 'value': value}
            evidence.update(referenceReport=copy.deepcopy(self.config['canonicalReferenceEvidence']),
                            originalNative=copy.deepcopy(pins['native']), originalBackground=copy.deepcopy(pins['background']))
        return {'statistics': statistics, 'evidence': evidence, 'material': evidence['material'],
            'declaration': self.declarations(run, plan, spec, family=family)}

    def current_measurement(self, row, *, name):
        if row.get('nativeIdentity'):
            item = self.current[tuple(row[k] for k in KEY)]
            if item['originalReference'] != row:
                raise ValueError('Frozen current measurement changed its original reference row')
            statistic = copy.deepcopy(item['measurement'])
            cell_evidence = item['nativeEvidenceEnvelope']
            statistic['nativeRuns'] = copy.deepcopy(cell_evidence['runs'])
            statistic['nativeProvenance'] = copy.deepcopy(cell_evidence)
            evidence = copy.deepcopy(item['provenance'])
            evidence['material'] = {'documentPair': pair(row['currentDocumentPair']),
                                    'originalDocumentPair': copy.deepcopy(row['currentDocumentPair'])}
            evidence['completedCurrentEvidence'] = copy.deepcopy(self.config['completedCurrentEvidence'])
            return statistic, evidence
        item = self.canonical_record(row)
        frozen = item['readings'][name]
        support = item['publishedReading']['supports'][frozen['support']]
        statistic = {'status': frozen['status'], 'measurementStatus': frozen['status'],
            'value': copy.deepcopy(frozen['current']), 'nativeValue': copy.deepcopy(frozen['native']),
            'nativeRepeat': copy.deepcopy(frozen['repeat']), 'support': frozen['support'], 'units': frozen['units'],
            'required': True, 'nativeSupportWitnesses': [witness(support)],
            'nativeImage': copy.deepcopy(item['pins']['native'])}
        if statistic['value'] is None: statistic['measurementStatus'] = 'UNMEASURED'
        evidence = {'capture': copy.deepcopy(item['pins']['current']),
            'cell': copy.deepcopy(item['pins']['currentMetadata']),
            'canonicalReferenceEvidence': copy.deepcopy(self.config['canonicalReferenceEvidence']),
            'material': {'documentPair': pair(row['currentDocumentPair']),
                         'originalDocumentPair': copy.deepcopy(row['currentDocumentPair'])}}
        return statistic, evidence


def measure_exposed(context, live, run, native_report_pin, receipt, scenes_pin, *, native_batch_pin, verify_repeat):
    """capture.measure_capture, step for step, on the member's OWN derived run.

    measure_capture finds its run in context['batch'] (or its baseline_run derivative) under
    render admission and requires artifacts beneath THAT run's captureRoot; a LIVE member lives
    beneath its own per-attempt root and is read under read admission. Every other check, pure
    function and output field is capture.py's own. verify_repeat is the archived pair replay,
    and every LIVE member carries a fresh pair, so no legacy true/zero attestation is admitted.
    """
    live.require_context(context)
    if context['phase'] not in ('fit', 'gate', 'exposure'):
        raise ValueError('Completed-current measurements require their separate evidence bootstrap')
    if native_report_pin not in context['inputs'] or native_batch_pin not in context['inputs']:
        raise ValueError('Native report/batch pins are not admitted root inputs')
    if not all(receipt.get(k) == run[k] for k in ('profile', 'renderer', 'candidate')) \
            or receipt.get('scene') not in run['scenes'] or receipt.get('lane') not in ('candidate', 'current'):
        raise ValueError('Capture receipt differs from exact admitted run/candidate/member')
    live.require_read_admission(context, run, current=receipt['lane'] == 'current')
    if receipt.get('sceneSource') != 'w50' or run.get('sceneSource') != 'w50':
        raise ValueError('Only the W50 512x384 scene source is supported')
    plan = M.A.scene_plan(run, context['phase'])
    spec = next(s for s in plan['scenes'] if s['scene'] == receipt['scene'])
    if receipt.get('canvas') != plan['canvas'] or receipt.get('dpr') != plan['dpr']:
        raise ValueError('Receipt canvas/scale differs from its declared profile')
    doc = M._scene_document(context, scenes_pin, live)
    raw = M._pin_bytes(native_report_pin, Path(context['repo']))
    report = M._json(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)
    cell = M._native_cell(report, receipt, plan, spec, doc)
    batch = M._json(M._pin_bytes(native_batch_pin, Path(context['repo'])))
    if batch.get('schema') != 'w50-native-read-batch-1' or batch['inputs'].get('scenes') != scenes_pin \
            or batch['inputs']['declaration']['sha256'] != report['declarationSha256']:
        raise ValueError('Native batch scene/declaration pins differ from the report')
    exports = [e for e in batch['exports'] if e['role'] == report['role']]
    if len(exports) != 1 or exports[0]['indexSha256'] != report['indexSha256']:
        raise ValueError('Native report index differs from its admitted role export')
    export = Path(exports[0]['root'])
    if not export.is_absolute() or export.is_symlink() or not export.is_dir():
        raise ValueError('Native dependency requires the original ordinary role export root')
    index = M._json(M._pin_bytes(dict(path='index.json', sha256=report['indexSha256']), export))
    deps = M.R.unique(report['dependencies'], 'id', 'native dependency')
    dependency = deps.get(cell['reference'])
    if dependency is None or any(r['dependency'] != cell['reference'] for r in cell['runs']):
        raise ValueError('Native cell lacks its original no-glass dependency')
    evidence = dependency['evidence']
    if index.get('schema') != 'w50-role-archive-1' or evidence not in index['files'] \
            or evidence.get('cell') != cell['reference'] or evidence.get('roles') != [report['role']] \
            or evidence.get('run') != 1 or evidence.get('kind') != 'frame':
        raise ValueError('Original no-glass row differs from the pinned role report/export')
    dependency_raw = M._pin_bytes(dict(path=evidence['path'], sha256=evidence['sha256']), export)
    artifacts = receipt['artifacts']
    blobs = {}
    for name, filename in (('png', f'{receipt["scene"]}__{receipt["renderer"]}.png'),
                           ('report', f'report__{receipt["renderer"]}.json'),
                           ('cell', f'cell__{receipt["renderer"]}.json')):
        expected = Path(run['captureRoot'])/receipt['scene']/filename
        if artifacts[name].get('path') != str(expected):
            raise ValueError('Artifact path differs from exact admitted capture member')
        blobs[name] = M._pin_bytes(artifacts[name], Path(context['output']), external=True)
    metadata = M._json(blobs['cell'])
    if metadata.get('renderer') != run['renderer'] or metadata.get('colorSpace') != 'srgb' \
            or f'declarationSha256={run["candidate"]["sha256"][:12]}' not in metadata.get('capturePath', ''):
        raise ValueError('Capture metadata differs from admitted candidate/tier')
    verify_repeat(run, receipt)
    candidate = M.A.candidate_info(run['candidate'], plan['position'])
    endpoint = candidate['endpoints'][spec['pose']+'.dark']
    resolved = {**candidate['endpoints']['active.dark']['patch'], **endpoint['patch']}
    abscissa = resolved.get('backdropToneAbscissa', 'source')
    abscissa = 'silhouette' if isinstance(abscissa, dict) else abscissa
    arguments = M.A.validate_report(M._json(blobs['report']), run, endpoint,
                                    abscissa=abscissa, phase=context['phase'])
    for argument in arguments:
        M.N.validate_tone_values(argument)
    png_raw = blobs['png']
    pixels = (doc['canvas']['width']*plan['dpr'], doc['canvas']['height']*plan['dpr'])
    if png_raw[:8] != b'\x89PNG\r\n\x1a\n' or len(png_raw) < 24 \
            or tuple(int.from_bytes(png_raw[i:i+4], 'big') for i in (16, 20)) != pixels:
        raise ValueError('Pinned web PNG dimensions differ from the native canvas/profile')
    background = M.R.S.decode_png(dependency_raw)
    web = M.R.S.decode_png(png_raw)
    shape = (pixels[1], pixels[0], 3)
    if background.shape != shape or web.shape != shape:
        raise ValueError('Actual PNG dimensions differ from the declared native canvas/profile')
    scene = next(s for s in doc['scenes'] if s['id'] == receipt['scene'])
    masks = M.R.S.analytical_masks(doc['components'][scene['component']], doc['canvas'], plan['dpr'],
        web.shape[:2], background=background, impulse=doc['backgrounds'][scene['background']]['kind'] == 'impulse')
    if cell['family'] == 'uniform':
        del masks['deep8_far24']
    result = M.evaluate_native_supports(web, cell, masks, renderer=run['renderer'])
    provenance = dict(nativeRead=copy.deepcopy(native_report_pin), nativeBatch=copy.deepcopy(native_batch_pin),
        scenes=copy.deepcopy(scenes_pin), nativeDependency=copy.deepcopy(evidence),
        capture=copy.deepcopy(artifacts['png']), report=copy.deepcopy(artifacts['report']),
        cell=copy.deepcopy(artifacts['cell']), candidateDocument=copy.deepcopy(run['candidate']))
    provenance.update(repeatAdmission=copy.deepcopy(receipt['repeatAdmission']),
                      repeatPair=copy.deepcopy(receipt['repeatPair']), reading='first')
    for argument in arguments:
        argument['provenance'].update(report=copy.deepcopy(artifacts['report']),
            capture=copy.deepcopy(artifacts['png']), sceneSource='w50', scenesSha256=scenes_pin['sha256'],
            candidateDocument=copy.deepcopy(run['candidate']), baseline=receipt['lane'] == 'current',
            endpoint={k: copy.deepcopy(v) for k, v in endpoint.items() if k != 'patch'})
    result.update(evidence=provenance, arguments=arguments)
    live.require_context(context)
    return result


def source_probe():
    """Exercise pure statistics and late Python helper imports without any authority data read."""
    M.source_probe()
    R.M.source_probe()
    BR.source_probe()
    source(CURRENT3/'repeat/admission.py', 'w50_phase_probe_live_repeat')
    source(CURRENT3/'execution/native_evidence.py', 'w50_phase_probe_native_validator')
    source(FIT.parent/'2026-10-08-w50-g1-current2/execution/native_evidence.py',
           'w50_phase_probe_actual_blind_validator')
    source(FIT/'exposure/prepare.py', 'w50_phase_probe_prepared_native').source_probe()
    source(FIT/'current-analysis/analysis.py', 'w50_phase_probe_frozen_current').source_probe()
    source(FIT/'native/run.py', 'w50_phase_probe_original_native_bootstrap')
    source(FIT.parent/'2026-10-08-w50-g0-declaration/audit/next_wave.py',
           'w50_phase_probe_original_native_referee')
    return {'status': 'SOURCE_ONLY'}
