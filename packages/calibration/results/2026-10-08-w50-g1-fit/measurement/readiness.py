"""The exposure's completed native blind read, admitted ready or not (W50 DL5n, DL5m item 4).

LIVE checkpoints a COMPLETED native blind read whether or not its sealed readiness holds: a
required blind statistic that is unmeasurable, or whose native spread passes the sealed one-code
stop, is a stop recorded as metadata (cell, statistic, reason), and the affected required rows
reach the judge UNMEASURED. Measurement runs after LIVE's irreversible analysis marker, so a
refusal there would lose the one exposure without a verdict. The sealed readers refuse such a
read outright: current3 repeat/sources.blind_cell and NativeEvidence._blind_authority/validate
(current2/current3 execution/native_evidence.py, byte-equal to live-execution's) require ready
true and no stop, and capture.evaluate_native_supports (pinned in the canonical3/current
closures) raises on an empty required support and on a reported T1 empty in only some runs.
None of those files changes. This module is their LIVE counterpart:

* native_readiness reads the checkpoint's metadata through the dispatcher (ready, stops and the
  two documents that carry readiness), never the native read itself.
* readiness_view(NativeEvidence, readiness) reads exactly those two checkpointed documents with
  their readiness admitted, and only when the read's own stops, without their repeat values, are
  the checkpoint's stops. A ready checkpoint changes nothing. Every other byte, document and
  check is the sealed reader's.
* blind_cell is current3's, check for check, reading through that view. checkpointed_blind_cell
  is the same function under the sealed signature, for the DL5h repeat helper's own instance.
* evaluate_supports is capture.evaluate_native_supports, check for check, except that a stopped
  statistic is not computed (UNMEASURED, NATIVE_NOT_READY) and a reported statistic whose reading
  is incomplete is recorded (UNMEASURED, INCOMPLETE_READING) instead of raising.

Nothing here prints or formats a value; errors name fields and kinds only (DL5k).
"""
import copy
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
CURRENT2 = FIT.parent/'2026-10-08-w50-g1-current2'
CURRENT3 = FIT.parent/'2026-10-08-w50-g1-current3'
STOP = ('cell', 'statistic', 'reason')
STOP_REASONS = ('UNMEASURED_UNAUTHORISED_POPULATION', 'NATIVE_SPREAD_EXCEEDS_ONE_CODE')
NOT_READY = 'NATIVE_NOT_READY'
INCOMPLETE = 'INCOMPLETE_READING'


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


B = source(CURRENT3/'repeat/sources.py', 'w50_readiness_sealed_blind_source')
M = B.M


def native_readiness(context, live):
    """The exposure's native checkpoint as metadata: {ready, stops, artifactManifest, nativeRead}.

    The payload is the native role's {ready, complete, stops, nativeExposure, artifacts}, which LIVE
    hash-checks with every listed artifact before handing it out. ready is true exactly when there
    is no stop; a stop is metadata on one statistic. The two readiness documents must be the
    preparation's own layout under this exposure's output and among the checkpointed artifacts."""
    payload = live.qualification_native(context)
    if not isinstance(payload, dict) or payload.get('complete') is not True or type(payload.get('ready')) is not bool \
            or not isinstance(payload.get('stops'), list) or payload['ready'] != (payload['stops'] == []) \
            or not isinstance(payload.get('nativeExposure'), dict) or not isinstance(payload.get('artifacts'), list):
        raise ValueError('Exposure native checkpoint is not one complete preparation')
    seen = set()
    for stop in payload['stops']:
        if not isinstance(stop, dict) or set(stop) != set(STOP) or stop['reason'] not in STOP_REASONS \
                or not isinstance(stop['cell'], str) or stop['cell'].count('/') != 1 \
                or not isinstance(stop['statistic'], str) or (stop['cell'], stop['statistic']) in seen:
            raise ValueError('Native checkpoint stop is not metadata on one statistic')
        seen.add((stop['cell'], stop['statistic']))
    artifacts = payload['nativeExposure']
    destination = (Path(context['output'])/'native-blind').resolve()
    documents = {'artifactManifest': destination/'artifacts.json', 'nativeRead': destination/'native-read.json'}
    if artifacts.get('ready') is not payload['ready'] or any(
            not isinstance(artifacts.get(name), dict) or artifacts[name].get('path') != str(path)
            or artifacts[name] not in payload['artifacts'] for name, path in documents.items()):
        raise ValueError('Native checkpoint names another preparation layout')
    return {'ready': payload['ready'], 'stops': copy.deepcopy(payload['stops']),
            **{name: copy.deepcopy(artifacts[name]) for name in documents}}


def stopped(readiness, identity):
    """The statistics the checkpoint stops on one native cell (profile/scene)."""
    return {stop['statistic'] for stop in readiness['stops'] if stop['cell'] == identity}


def admitted(name, value, stops):
    """One not-ready readiness document as its complete view, after its own readiness is matched
    against the checkpoint's stops; nothing but the readiness fields differs."""
    if not isinstance(value, dict) or value.get('ready') is not False:
        raise ValueError('Native readiness differs from its checkpoint')
    if name == 'artifactManifest':
        return dict(value, ready=True)
    own = value.get('stops')
    if not isinstance(own, list) or any(not isinstance(s, dict) or set(s) != {*STOP, 'repeat'} for s in own) \
            or [{k: s[k] for k in STOP} for s in own] != stops:
        raise ValueError('Native read stops differ from its checkpoint')
    return dict(value, ready=True, stops=[])


def readiness_view(base, readiness):
    """The sealed NativeEvidence class, reading the checkpoint's two readiness documents as admitted.

    A ready checkpoint returns the sealed class's reading untouched, so its own checks decide. A
    not-ready one substitutes ONLY the artifact manifest's ready flag and the native read's
    ready/stops, for exactly the checkpointed bytes, and only after admitted() matched them. The
    view is cached per document, as the sealed reader caches its parse."""
    if readiness['ready']:
        return base
    documents = {Path(readiness[name]['path']).resolve(): (name, readiness[name]['sha256'])
                 for name in ('artifactManifest', 'nativeRead')}

    class CheckpointedNativeEvidence(base):
        def read(self, pin):
            value = super().read(pin)
            path = self.check(pin)
            if path not in documents:
                return value
            name, digest = documents[path]
            if pin['sha256'] != digest:
                raise ValueError('Native readiness document differs from its checkpoint')
            views = self.__dict__.setdefault('_checkpointed', {})
            if path not in views:
                views[path] = admitted(name, value, readiness['stops'])
            return views[path]

    return CheckpointedNativeEvidence


def blind_cell(context, run, row, scenes, readiness):
    """current3 repeat/sources.blind_cell, check for check, reading through readiness_view.

    The artifact manifest must also be the checkpoint's own. A ready checkpoint reads exactly as
    the sealed function does; a not-ready one is admitted only with its own stops."""
    C, R, MR = B.C, B.R, M.R
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None: raise C.InstrumentFault('Blind repeat source requires live exposure')
    dispatcher.require_context(context)
    if context.get('phase') != 'exposure':
        raise C.InstrumentFault('Blind repeat source is exposure-only')
    E = source(CURRENT2/'execution/native_evidence.py', 'w50_readiness_blind_authority')
    P = source(FIT/'exposure/prepare.py', 'w50_readiness_blind_preparation')
    manifest_path = Path(context['output'])/'native-blind/artifacts.json'
    artifact_pin = R.file_pin(manifest_path)
    if artifact_pin != readiness['artifactManifest']:
        raise C.InstrumentFault('Blind preparation differs from its native checkpoint')
    reader = readiness_view(E.NativeEvidence, readiness)(context['repo'])
    artifact = reader.read(artifact_pin)
    envelope = dict(nativeExposure=artifact_pin, nativeRead=artifact['nativeRead'],
        nativeExport=dict(role='blind', root=artifact['export']['path'],
                          indexSha256=artifact['export']['indexSha256']))
    declaration, _ = reader._blind_authority(row, envelope, context)
    claim = reader.read(artifact['claim'])
    if claim['config'] != run.get('nativeExposureConfig'):
        raise C.InstrumentFault('Blind preparation differs from the admitted run config')
    config = reader.read(claim['config'])
    manifest = reader.read(config['manifest'])
    index = reader.read(dict(path=str(Path(artifact['export']['path'])/'index.json'),
                             sha256=artifact['export']['indexSha256']))
    cells, deps, found = P.selected_rows(index, manifest, scenes, declaration)
    identity = row['profile']+'/'+row['scene']
    if identity not in cells: raise C.InstrumentFault('Blind cell is outside original membership')
    for key, record in found.items():
        if record != reader.blind_original_rows.get(key):
            raise C.InstrumentFault('Blind export differs from original archived row')
    report = reader.read(artifact['nativeRead'])
    if report.get('schema') != 'w50-native-role-read-1' or report.get('role') != 'blind' \
            or report.get('ready') is not True or report.get('stops') != [] \
            or report.get('indexSha256') != artifact['export']['indexSha256'] \
            or report.get('declarationSha256') != declaration \
            or report.get('supportDefinitions') != MR.S.SUPPORT_DEFINITIONS \
            or report.get('repeatRule') != manifest['repeatRule'] or report.get('canvas') != scenes['canvas']:
        raise C.InstrumentFault('Blind report differs from its actual prepared source')
    indexed = MR.unique(report['cells'], 'id', 'blind native cell')
    cell = indexed[identity]
    if any(cell.get(k) != v for k, v in cells[identity].items() if k != 'runs'):
        raise C.InstrumentFault('Blind native cell identity changed')
    if [r['run'] for r in cell['runs']] != [1, 2, 3] or any(
            r['evidence'] != found[(identity, r['run'])] or r['dependency'] != cell['reference']
            for r in cell['runs']):
        raise C.InstrumentFault('Blind native run source changed')
    dependency = MR.unique(report['dependencies'], 'id', 'blind dependency')[cell['reference']]['evidence']
    if dependency != found[(cell['reference'], 1)]:
        raise C.InstrumentFault('Blind no-glass source changed')
    export = Path(artifact['export']['path'])
    for evidence in [r['evidence'] for r in cell['runs']] + [dependency]:
        reader.png(dict(path=str(MR.safe(export, evidence['path'])), sha256=evidence['sha256']),
                   [scenes['canvas']['width']*cell['scale'], scenes['canvas']['height']*cell['scale']])
    reader.finish()
    return cell, dependency, export, dict(nativeExposure=artifact_pin, nativeRead=artifact['nativeRead'])


def checkpointed_blind_cell(context, run, row, scenes):
    """blind_cell under the sealed signature, its readiness read from the live checkpoint.

    For an instance of the root-bound DL5h repeat helper, whose newbed_pair calls its sources'
    blind_cell(context, run, row, scenes) for a non-identical blind pair."""
    live = sys.modules.get('w50_g1_dispatch')
    if live is None: raise B.C.InstrumentFault('Blind repeat source requires live exposure')
    live.require_context(context)
    return blind_cell(context, run, row, scenes, native_readiness(context, live))


def evaluate_supports(rgb, native_cell, analytical_masks, *, renderer, stopped=frozenset()):
    """capture.evaluate_native_supports, check for check, with the DL5n and DL5m (4) policy.

    `stopped` names the cell's statistics the native checkpoint stops (DL5n); each must be one of
    the cell's REQUIRED statistics. A stopped statistic is not computed: its support witnesses are
    still checked against the original masks, a support no other statistic reads is not read, and
    its value, run values, native value and native repeat are null, status UNMEASURED, reason
    NATIVE_NOT_READY. A REPORTED statistic (DL5a/b/c, required false) whose three-run reading is
    incomplete is recorded with value null, status UNMEASURED_REPORTED, reason INCOMPLETE_READING,
    unless it is a full-silhouette T1 empty in all three runs, which stays the sealed
    UNMEASURED_EMPTY_SUPPORT reading for the projection's exact DL5c eligibility. Everything else,
    including every refusal and the output of a read with neither case, is the sealed evaluator's."""
    np, LEVELS = M.np, M.LEVELS
    rgb = M.R.S.checked_rgb(rgb)
    if renderer not in ('webgpu', 'css'):
        raise ValueError('An exact measured renderer is required')
    runs = native_cell['runs']
    if [run['run'] for run in runs] != [1, 2, 3]:
        raise ValueError('Exactly three ordered original native run supports are required')
    names = set(native_cell['statistics'])
    expected = set(LEVELS) if native_cell['family'] != 'uniform' else set(list(LEVELS)[:2])
    if names != expected or any(set(run['readings']['statistics']) != names for run in runs):
        raise ValueError('Native statistic population differs from its declared family')
    stopped = set(stopped)
    if not stopped <= names or any(native_cell['statistics'][name].get('required') is not True for name in stopped):
        raise ValueError('A native stop names no required statistic of its cell')
    supports = {LEVELS[name][0] for name in names}
    if set(analytical_masks) != supports-{'full-silhouette'}:
        raise ValueError('Exact original analytical support membership is required')
    for name in names:
        support, units, _ = LEVELS[name]
        for item in [native_cell['statistics'][name]] + [r['readings']['statistics'][name] for r in runs]:
            if item.get('support') != support or item.get('units') != units:
                raise ValueError('Native statistic support or units differ from the sealed reader')

    measured = names-stopped
    read = {LEVELS[name][0] for name in measured}
    measured_runs, witnesses = [], {name: [] for name in names}
    for run in runs:
        original = run['readings']['supports']
        masks = dict(analytical_masks)
        if 'full-silhouette' in supports:
            masks['full-silhouette'] = M.R.S.decode_support(original['full-silhouette'])
        readings = {}
        for support in sorted(supports):
            mask = np.asarray(masks[support])
            if mask.shape != rgb.shape[:2] or mask.dtype != np.bool_:
                raise ValueError('Original native support dimensions differ from web PNG')
            witness = M._witness(original[support], mask)
            if support in read:
                readings[support] = M.R.S.read_support(rgb, mask)
            for name in names:
                if LEVELS[name][0] == support:
                    witnesses[name].append(dict(run=run['run'], **witness))
        statistics = {}
        for name in sorted(measured):
            support, units, field = LEVELS[name]
            reading = readings[support]
            statistics[name] = dict(status=reading['status'], support=support, units=units,
                                    value=reading.get(field))
        measured_runs.append(dict(run=run['run'], nativeEvidence=copy.deepcopy(run['evidence']),
                                  readings=dict(supports=readings, statistics=statistics)))

    statistics = {}
    for name in sorted(names):
        native = native_cell['statistics'][name]
        support, units = LEVELS[name][:2]
        if name in stopped:
            statistics[name] = dict(status='UNMEASURED', measurementStatus='UNMEASURED', reason=NOT_READY,
                required=True, support=support, units=units, value=None, runValues=None,
                aggregation='coordinatewise-median-of-three-run-statistics', nativeValue=None,
                nativeRepeat=None, nativeSupportWitnesses=witnesses[name])
            continue
        values = [run['readings']['statistics'][name]['value'] for run in measured_runs]
        complete = all(value is not None for value in values)
        required = native['required']
        if not complete and required:
            raise ValueError('An empty required native support cannot certify a measurement')
        if not complete and (name != 'T1-full-silhouette' or any(w['pixels'] for w in witnesses[name])):
            statistics[name] = dict(status='UNMEASURED_REPORTED', measurementStatus='UNMEASURED',
                reason=INCOMPLETE, required=False, support=support, units=units, value=None,
                runValues=values, aggregation='coordinatewise-median-of-three-run-statistics',
                nativeValue=copy.deepcopy(native['value']), nativeRepeat=copy.deepcopy(native['repeat']),
                nativeSupportWitnesses=witnesses[name], B=None)
            continue
        value = np.median(np.asarray(values, dtype=float), axis=0).tolist() if complete else None
        statistics[name] = dict(status=('UNMEASURED_EMPTY_SUPPORT' if not complete else
                                'REPORTED' if not required else 'MEASURED'),
            measurementStatus='MEASURED' if complete else 'UNMEASURED_EMPTY_SUPPORT',
            required=required, support=support, units=units, value=value,
            runValues=values, aggregation='coordinatewise-median-of-three-run-statistics',
            nativeValue=copy.deepcopy(native['value']), nativeRepeat=copy.deepcopy(native['repeat']),
            nativeSupportWitnesses=witnesses[name])
        if not required:
            statistics[name]['B'] = None
    return dict(schema='w50-web-native-support-read-1', status='MEASURED',
        profile=native_cell['profile'], renderer=renderer, scene=native_cell['scene'],
        role=native_cell['role'], pose=native_cell['pose'], scale=native_cell['scale'],
        statistics=statistics, runs=measured_runs)


def source_probe():
    """Load the late sealed sources blind_cell executes; no checkpoint, report or image is read."""
    source(CURRENT2/'execution/native_evidence.py', 'w50_readiness_probe_blind_authority')
    source(FIT/'exposure/prepare.py', 'w50_readiness_probe_blind_preparation')
    return {'status': 'SOURCE_ONLY'}
