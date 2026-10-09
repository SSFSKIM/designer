"""DL5h original-native supports and source-bound bars, without a current baseline dependency.

The pure projection functions consume arrays. I/O entrypoints are private to admission.py;
blind authority is the existing one-shot preparation chain, never a caller-supplied report.
"""
import copy
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parents[1]/'2026-10-08-w50-g1-fit'


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


C = source(HERE/'core.py', 'w50_repeat_math')
M = source(FIT/'measurement/capture.py', 'w50_repeat_native_measurement')
R = source(FIT/'references/canonical.py', 'w50_repeat_canonical_sources')


def canonical_membership(rows, *, impulse=False, solid=False):
    """Declared cuts, including BOTH text bands; owner laws supply no invented repeat metric."""
    selected = {}
    for row in rows:
        name = row['statistic']
        if name in ('T1-low', 'T1-full-silhouette'):
            selected[name] = row
            if name == 'T1-low': selected['T1-fine'] = None
        elif name == 'low-end-path-level':
            if solid:
                selected['deep8-channel-median'] = None
            elif impulse:
                for suffix in ('luma-mean','luma-median'):
                    selected['deep8-far24-'+suffix] = None
            else:
                raise C.InstrumentFault('No declared low-end repeat statistics for this backdrop')
        elif name != 'owner-contracts':
            raise C.InstrumentFault('Unknown declared canonical repeat statistic: '+name)
    return selected


def canonical_statistics(native, background, repeats, first, second, rows, *, provenance,
                         component, canvas, scale, text=False, impulse=False):
    """Use the published native supports for BOTH web images, not either web silhouette."""
    options = dict(text=text, impulse=impulse)
    published = R.M.canonical_read(native, background, component, canvas, scale, **options)
    own = [R.M.canonical_read(rgb, background, component, canvas, scale, **options) for rgb in repeats]
    evidence = R.M.evidence_reading(published, own)
    selected = canonical_membership(rows, impulse=impulse,
        solid=any(r.get('backgroundKind') == 'solid' for r in rows))
    results = []
    for image in (first, second):
        read = R.M.canonical_read(native, background, component, canvas, scale, web_rgb=image, **options)
        result = {}
        for name, row in selected.items():
            item = evidence[name]; repeat = copy.deepcopy(item['repeat'])
            if row is not None and row.get('B') is not None:
                repeat = C.bar_from_fixed_budget(row['B'], dict(provenance, reference=copy.deepcopy(row)))
            result[name] = dict(value=read['web']['statistics'][name]['value'], units=item['units'],
                support=read['supports'][item['support']], repeat=repeat or {'bar':None},
                provenance=copy.deepcopy(provenance))
        results.append(result)
    return tuple(results)


def native_statistics(first, second, cell, masks, *, renderer, provenance):
    results = []
    for image in (first, second):
        read = M.evaluate_native_supports(image, cell, masks, renderer=renderer)
        result = {}
        for name, item in read['statistics'].items():
            repeat = copy.deepcopy(item['nativeRepeat'])
            if repeat is None:
                repeat = {'bar':None}
            else:
                repeat['bar'] = repeat['barLinear'] if item['units'] == 'linear-luma' else repeat['barCodes']
                repeat['formula'] = 'max(0.5 code_step, half own-three-run spread)'
            result[name] = dict(value=item['value'], units=item['units'],
                support=item['nativeSupportWitnesses'], repeat=repeat,
                provenance=copy.deepcopy(provenance))
        results.append(result)
    return tuple(results)


def canonical_pair(config, rows, first, second):
    """Read exact own native seven-run records; intentionally never open currentEvidence."""
    if not rows or not any(r['statistic'] != 'owner-contracts' for r in rows):
        return {}, {}
    row = next(r for r in rows if r['statistic'] != 'owner-contracts')
    scenes, published = R.json_pin(config['scenes']), R.json_pin(config['publishedManifest'])
    if scenes['canvas'] != {'width':320,'height':200}:
        raise C.InstrumentFault('Canonical repeat source must be the original 320x200 bed')
    match = R.PROFILE.fullmatch(row['profile'])
    if not match or match[2] != 'dark': raise C.InstrumentFault('Unknown canonical profile')
    scale, position = int(match[1]), match[3]
    source_name = 'w29' if position == '0.5' else 'w43'
    native_source = (R.verify_w29_source if source_name == 'w29' else R.verify_w43_source)(config[source_name])
    profiles = [p for p in published['profiles'] if p['profileKey'] == row['profile']]
    declarations = [p for p in scenes['profiles'] if p['key'] == row['profile']]
    if len(profiles) != 1 or len(declarations) != 1 or row['scene'] not in declarations[0]['scenes']:
        raise C.InstrumentFault('Canonical native member is not uniquely declared')
    entries = [f for f in profiles[0]['fixtures'] if f['sceneId'] == row['scene']]
    if len(entries) != 1: raise C.InstrumentFault('Canonical native state is ambiguous')
    entry = entries[0]; scene = next(s for s in scenes['scenes'] if s['id'] == row['scene'])
    R.native_entry(entry, row['profile'], scale, scene['state'], scenes['canvas'])
    native_pin = row['nativeEvidence']
    if Path(native_pin['path']).resolve() != R.safe(config['fixtureRoot'],entry['file']).resolve():
        raise C.InstrumentFault('Canonical native evidence selected another source file')
    if any(r.get('nativeEvidence') != native_pin for r in rows if r['statistic'] != 'owner-contracts'):
        raise C.InstrumentFault('Canonical statistics disagree on their original native image')
    bg_rel = published.get('backgrounds',{}).get(f'{scene["background"]}@{scale}x')
    if bg_rel is None: raise C.InstrumentFault('Canonical source lacks same-scale no-glass')
    background_pin = R.file_pin(R.safe(config['fixtureRoot'],bg_rel))
    runs = (R._w29_repeats if source_name == 'w29' else R._w43_repeats)(
        native_source,row,scene,scenes,background_pin)
    selected = [r for r in runs if r['frame']['sha256'] == native_pin['sha256']]
    if not selected or not any(r['metadata'].get('capturedAt') == entry['capturedAt'] for r in selected):
        raise C.InstrumentFault('Published native bytes/time are not from selected source records')
    shape = (scenes['canvas']['height']*scale,scenes['canvas']['width']*scale)
    native, background = (R.decode_verified(pin,shape) for pin in (native_pin,background_pin))
    repeats = [R.decode_verified(r['frame'],shape) for r in runs]
    bg_kind = scenes['backgrounds'][scene['background']]['kind']
    enriched = [dict(r,backgroundKind=bg_kind) for r in rows]
    provenance = dict(native=native_pin,background=background_pin,scenes=config['scenes'],
        publishedManifest=config['publishedManifest'],source=source_name,runs=runs)
    return canonical_statistics(native,background,repeats,first,second,enriched,
        provenance=provenance,component=scenes['components'][scene['component']],
        canvas=scenes['canvas'],scale=scale,text=any(r['statistic']=='T1-low' for r in rows),
        impulse=bg_kind=='impulse')


def blind_cell(context, run, row, scenes):
    """Verify the actual prepared blind slot before opening its report or any PNG."""
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None: raise C.InstrumentFault('Blind repeat source requires live exposure')
    dispatcher.require_context(context)
    if context.get('phase') != 'exposure':
        raise C.InstrumentFault('Blind repeat source is exposure-only')
    E = source(FIT.parents[0]/'2026-10-08-w50-g1-current2/execution/native_evidence.py',
               'w50_repeat_blind_authority')
    P = source(FIT/'exposure/prepare.py','w50_repeat_blind_preparation')
    manifest_path = Path(context['output'])/'native-blind/artifacts.json'
    artifact_pin = R.file_pin(manifest_path)
    reader = E.NativeEvidence(context['repo'])
    artifact = reader.read(artifact_pin)
    envelope = dict(nativeExposure=artifact_pin,nativeRead=artifact['nativeRead'],
        nativeExport=dict(role='blind',root=artifact['export']['path'],
                          indexSha256=artifact['export']['indexSha256']))
    declaration, _ = reader._blind_authority(row,envelope,context)
    claim = reader.read(artifact['claim'])
    if claim['config'] != run.get('nativeExposureConfig'):
        raise C.InstrumentFault('Blind preparation differs from the admitted run config')
    config = reader.read(claim['config'])
    manifest = reader.read(config['manifest'])
    index = reader.read(dict(path=str(Path(artifact['export']['path'])/'index.json'),
                             sha256=artifact['export']['indexSha256']))
    cells, deps, found = P.selected_rows(index,manifest,scenes,declaration)
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
            or report.get('supportDefinitions') != M.R.S.SUPPORT_DEFINITIONS \
            or report.get('repeatRule') != manifest['repeatRule'] or report.get('canvas') != scenes['canvas']:
        raise C.InstrumentFault('Blind report differs from its actual prepared source')
    indexed = M.R.unique(report['cells'],'id','blind native cell')
    cell = indexed[identity]
    if any(cell.get(k) != v for k,v in cells[identity].items() if k != 'runs'):
        raise C.InstrumentFault('Blind native cell identity changed')
    if [r['run'] for r in cell['runs']] != [1,2,3] or any(
            r['evidence'] != found[(identity,r['run'])] or r['dependency'] != cell['reference']
            for r in cell['runs']):
        raise C.InstrumentFault('Blind native run source changed')
    dependency = M.R.unique(report['dependencies'],'id','blind dependency')[cell['reference']]['evidence']
    if dependency != found[(cell['reference'],1)]:
        raise C.InstrumentFault('Blind no-glass source changed')
    export = Path(artifact['export']['path'])
    for evidence in [r['evidence'] for r in cell['runs']] + [dependency]:
        reader.png(dict(path=str(M.R.safe(export,evidence['path'])),sha256=evidence['sha256']),
                   [scenes['canvas']['width']*cell['scale'],scenes['canvas']['height']*cell['scale']])
    reader.finish()
    return cell, dependency, export, dict(nativeExposure=artifact_pin,nativeRead=artifact['nativeRead'])


def newbed_pair(context, run, config, rows, first, second):
    A = source(FIT/'current-analysis/analysis.py','w50_repeat_exposed_source')
    dispatcher = sys.modules['w50_g1_dispatch']; repo = Path(context['repo'])
    native_batch = A.native_contract(repo,config['native'])
    scenes_pin = native_batch['inputs']['scenes']
    scenes = dispatcher.load(dispatcher.checked(repo,scenes_pin))
    roles = {r['role'] for r in rows}
    if len(roles) != 1: raise C.InstrumentFault('New-bed cell has mixed original native roles')
    role = roles.pop(); identity = rows[0]['profile']+'/'+rows[0]['scene']
    if role == 'blind':
        cell,dependency,export,provenance = blind_cell(context,run,rows[0],scenes)
    else:
        if role not in ('calibration','validation'):
            raise C.InstrumentFault('Unknown exposed native role')
        admitted = A.native_roles(config,native_batch,scenes)[role]
        cell = admitted['cells'][identity]; dependency = admitted['deps'][cell['reference']]['evidence']
        export = Path(admitted['export']['root'])
        provenance = dict(nativeRead=admitted['reportPin'],nativeBatch=config['native']['batch'])
    if set(cell['statistics']) != {r['statistic'] for r in rows}:
        raise C.InstrumentFault('Declared new-bed statistic membership differs from native read')
    background = M.R.read_verified_frame(export,dependency,scenes['canvas'],cell['scale'])
    scene = next(s for s in scenes['scenes'] if s['id'] == rows[0]['scene'])
    masks = M.R.S.analytical_masks(scenes['components'][scene['component']],scenes['canvas'],
        cell['scale'],first.shape[:2],background=background,
        impulse=scenes['backgrounds'][scene['background']]['kind']=='impulse')
    if cell['family']=='uniform': del masks['deep8_far24']
    provenance.update(scenes=scenes_pin,dependency=dependency,
                      runs=[r['evidence'] for r in cell['runs']])
    return native_statistics(first,second,cell,masks,renderer=run['renderer'],provenance=provenance)


def source_probe():
    """Exercise synthetic arrays and pinned authority metadata; never measured native data."""
    image=M.np.full((64,64,3),128,dtype=M.np.uint8)
    canonical_statistics(image,M.np.zeros_like(image),[image]*7,image,image,
        [{'statistic':'T1-low','B':None}],provenance={'synthetic':True},
        component={'kind':'rrect','size':[48,48],'radius':0},canvas={'width':64,'height':64},scale=1,text=True)
    M.source_probe()
    exposed = source(FIT/'current-analysis/analysis.py','w50_repeat_probe_exposed')
    # Exercise the SAME registered authority branch used by a non-identical exposed pair.
    # It checks only pinned roots/contracts/batch/source metadata and the original synthetic
    # native probe. Role reports, export indexes and image bytes are deliberately not opened.
    config = exposed.B.load(HERE.parent/'inputs/repeat-config.json')
    exposed.native_contract(exposed.REPO, config['native'])
    source(FIT.parents[0]/'2026-10-08-w50-g1-current2/execution/native_evidence.py',
           'w50_repeat_probe_blind_authority')
    source(FIT/'exposure/prepare.py','w50_repeat_probe_blind')
    return {'status':'SOURCE_ONLY'}
