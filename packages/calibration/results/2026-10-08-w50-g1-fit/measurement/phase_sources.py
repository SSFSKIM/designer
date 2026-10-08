"""Internal source-owned I/O for additive live measurements, never native preparation or a verdict.

Exposed NEWBED delegates to capture.measure_capture. Blind NEWBED uses the existing repeat
reader's ACTUAL preparation-chain validator and the immutable pure native-support evaluator;
no native statistic is remeasured and no role is relabelled. Canonical measurement consumes
original published native/backdrop pins and frozen seven-run/reference evidence, not a new
reference fit. All live pairs use both source report validators before first-image measurement.
"""
import copy
import gzip
from pathlib import Path
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


M = source(HERE/'capture.py', 'w50_phase_immutable_measurement')
W = source(CURRENT3/'web/adapter.py', 'w50_phase_paired_newbed')
C = source(CURRENT3/'canonical/adapter.py', 'w50_phase_paired_canonical')
R = source(FIT/'references/canonical.py', 'w50_phase_original_canonical')
B = source(CURRENT3/'repeat/sources.py', 'w50_phase_actual_blind_source')
V = source(CURRENT3/'execution/blind_exposure.py', 'w50_phase_blind_completeness')


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
        current = self.registered(config['completedCurrentEvidence'])
        if current.get('schema') != 'w50-completed-current-evidence-1' or current.get('status') != 'EVIDENCE_ONLY' \
                or current.get('currentInstrument') != root['currentInstrument'] \
                or current.get('currentResults') != root['currentResults'] \
                or current.get('originals', {}).get('references') != root['references']:
            raise ValueError('Current measurements differ from the root-bound completed instrument')
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
        self.reports = {}; self.canonical_cache = {}

    def registered(self, pin):
        if pin not in self.root['inputs'] or pin not in self.context['inputs']:
            raise ValueError('Source measurement document is not an admitted input')
        path = self.dispatcher.checked(self.repo, pin)
        raw = path.read_bytes()
        return M._json(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)

    def authenticate(self, run, receipt):
        self.dispatcher.require_render_admission(self.context, run, current=receipt['lane'] == 'current')
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
        M.verify_live_repeat(self.context, run, receipt, metadata)
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
        self.dispatcher.require_render_admission(self.context, run, current=receipt['lane'] == 'current')
        if run['sceneSource'] == 'w50' and any(r['role'] == 'blind' for r in rows):
            return self.blind(run, receipt, rows)
        if run['sceneSource'] == 'w50':
            plan = W.scene_plan(run, self.context['phase'])
            spec = next(s for s in plan['scenes'] if s['scene'] == receipt['scene'])
            role = spec['role']; pin = self.config['native']['reports'][role]
            measured = M.measure_capture(self.context, pin, receipt, self.config['native']['scenes'],
                                        native_batch_pin=self.config['native']['batch'])
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
        cell, dependency, export, provenance = B.blind_cell(self.context, run, rows[0], self.scenes)
        if [r['run'] for r in cell['runs']] != [1, 2, 3] or set(cell['statistics']) != {r['statistic'] for r in rows}:
            raise ValueError('Blind measurements must preserve the exact original three-run statistic population')
        background = M.R.read_verified_frame(export, dependency, self.scenes['canvas'], plan['dpr'])
        web = M.R.S.decode_png(blobs['png'])
        scene = next(s for s in self.scenes['scenes'] if s['id'] == receipt['scene'])
        masks = M.R.S.analytical_masks(self.scenes['components'][scene['component']], self.scenes['canvas'],
            plan['dpr'], web.shape[:2], background=background,
            impulse=self.scenes['backgrounds'][scene['background']]['kind'] == 'impulse')
        if cell['family'] == 'uniform': del masks['deep8_far24']
        measured = M.evaluate_native_supports(web, cell, masks, renderer=run['renderer'])
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

    def validate_blind_rows(self, rows):
        return V.validate_blind_exposure(self.context, rows)

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
                    statistics[name] = dict(copy.deepcopy(produced), measurementStatus=produced['status'],
                        nativeValue=copy.deepcopy(frozen['native']), nativeRepeat=copy.deepcopy(frozen['repeat']),
                        required=True, nativeSupportWitnesses=[witness(original_support)],
                        nativeImage=copy.deepcopy(pins['native']), nativeProvenance={
                            'referenceReport': self.config['canonicalReferenceEvidence'],
                            'native': copy.deepcopy(pins['native']), 'background': copy.deepcopy(pins['background']),
                            'scenes': copy.deepcopy(pins['scenes'])})
                    record_map[name] = item
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


def source_probe():
    """Exercise pure statistics and late Python helper imports without any authority data read."""
    M.source_probe()
    R.M.source_probe()
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
