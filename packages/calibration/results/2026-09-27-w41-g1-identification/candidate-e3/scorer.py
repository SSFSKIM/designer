"""E3 light-inactive preparation and receipt callback; no native I/O on import.

The forward path needs NumPy/Pillow, not SciPy. The only native constructors are
explicit calibration/validation preparation and score(request)'s receipt Reader.
No renderer, exposure, fitting, or receipt-writing entry point lives here.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import PIL

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
RESULTS = G1.parent
ROOT = RESULTS.parents[2]
G0 = RESULTS / '2026-09-27-w41-g0-declaration'
W39 = RESULTS / '2026-09-26-w39-g0-colour-edge-bed'
W39_BODY = RESULTS / '2026-09-26-w39-g2-identification/instrument'
INVENTORY_SHA = '58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61'
ARCHIVE_SHA = '489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5'
ARCHIVE = Path.home() / '.cache/vitrea-archives' / ARCHIVE_SHA / 'extracted/archive'
KNOTS = np.array([40., 56., 72., 88., 104., 128., 150.])


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


base = module('e3_baseline', G1 / 'baseline/baseline.py')
runner = module('e3_runner', G1 / 'exposure/runner.py')
colour = module('e3_colour', W39_BODY / 'body.py')
m = base.m
wave = base.wave
sha = base.sha
load = base.load


def check_runtime():
    expected = load(HERE / 'runtime.json')
    observed = dict(python=list(sys.version_info[:2]), numpy=np.__version__, pillow=PIL.__version__)
    if observed != expected:
        raise RuntimeError(f'projection/scoring runtime differs: {observed}; expected {expected}')


def parameters():
    selected = load(G1 / 'body/report-1/spatial-selection.json')['endpoints']['light-inactive']
    return dict(family='E3', endpoint='light-inactive', neutral=selected['neutral'],
                coefficients=selected['coefficients'])


def e3(x, neutral, gain):
    """The sealed B1, encoded codes: F(luma)+g(luma)*(x-luma), then cube clip."""
    x = np.asarray(x, float); neutral = np.asarray(neutral, float); gain = np.asarray(gain, float)
    if (x.ndim != 2 or x.shape[1] != 3 or not len(x) or not np.all(np.isfinite(x))
            or np.any((x < 0) | (x > 255)) or neutral.shape != (7,) or gain.shape != (3,)
            or not np.all(np.isfinite(neutral)) or not np.all(np.isfinite(gain))
            or np.any((neutral < 0) | (neutral > 255)) or np.any((gain < 0) | (gain > 3))):
        raise ValueError('finite in-domain E3 inputs and coefficients required')
    y = x @ colour.W
    f = colour.curve(y, KNOTS, neutral / 255) * 255
    g = np.interp(y, [63., 93., 118.], gain)
    chroma = x - y[:, None]
    chroma[np.ptp(x, axis=1) == 0] = 0
    return np.clip(f[:, None] + chroma*g[:, None], 0, 255)


def materials():
    provenance = load(W39_BODY / 'resolved-materials.provenance.json')
    if sha(W39_BODY / 'resolved-materials.json') != provenance['materialsSha256']:
        raise ValueError('resolved shipped material sidecar changed')
    for doc in provenance['documents']:
        if sha(ROOT / doc['path']) != doc['fileSha256']:
            raise ValueError('shipped document differs from proved H2 sidecar')
    return load(W39_BODY / 'resolved-materials.json')


def identity(cell):
    profile, sid = cell.split('/', 1)
    definition = next(p for p in wave.spec['profiles'] if p['key'] == profile)
    scene = wave.scenes[sid]
    endpoint = definition['colorScheme'] + ('-inactive' if scene['state'] == 'inactive' else '-active')
    background = wave.spec['backgrounds'][scene['background']]
    return endpoint, background


def disposition(cell):
    endpoint, background = identity(cell)
    if endpoint != 'light-inactive': return 'not claimed (identity)'
    if background['kind'] != 'solid': return 'not claimed (structured backdrop)'
    return 'claimed uniform body'


def local_prediction(rgb, endpoint, span, params=None, mats=None):
    """Structured use is S0 diagnostic, not the renderer's spatial body model."""
    if endpoint == 'light-inactive':
        p = parameters() if params is None else params
        values = e3(rgb, p['neutral'], p['coefficients'])
    else:
        values = colour.h2(np.asarray(rgb, float)/255,
                           (materials() if mats is None else mats)[endpoint], span=span)*255
    return np.median(values, axis=0)


def predictions():
    """PUBLIC metadata only, including all 72 sealed numerical holdout identities."""
    check_runtime()
    admitted, _ = runner.admitted_scope(ROOT, wave)
    mats = materials(); params = parameters(); cells = {}
    for cell in admitted['numerical']:
        endpoint, background = identity(cell)
        comp, scale = base.component(cell)
        shapes = m.readers.shapes_of(comp)
        structured = background['kind'] != 'solid'
        if structured:
            rgb = base.raster(background, scale, (wave.spec['canvas']['width'], wave.spec['canvas']['height']))
            geo = m.readers.geometry(rgb.shape[:2], shapes, scale)
        members = []
        for member, shape in enumerate(shapes):
            if shape.opaque: continue
            if structured:
                mask = (geo.member == member) & (geo.d <= -m.readers.DEEP_CSS*scale)
                values = rgb[mask]
                if len(values) < 4: raise ValueError('public deep population deficient')
            else:
                values = np.array([background['srgb']], float)
            members.append(dict(member=member, spanCSS=min(shape.size),
                predictedRGB=local_prediction(values, endpoint, min(shape.size), params, mats).tolist()))
        cells[cell] = dict(endpoint=endpoint, role=wave.roles[cell.split('/',1)[1]],
            disposition=disposition(cell), uniform=not structured, members=members,
            forward='E3' if endpoint == 'light-inactive' else 'shipped H2',
            inputOrigin='public declared sRGB backdrop',
            diagnostic='S0' if structured else None,
            limitation=('local unblurred pixel law then deep median; not a spatial prediction'
                        if structured else 'deep body before boundary terms'))
    return dict(cells=cells)


def score_deep(prediction, runs, populations):
    """Per-member median AND seven repeats; hard rails have no fitted tolerance."""
    p = np.asarray(prediction, float); runs = np.asarray(runs, float)
    populations = list(populations)
    if (runs.shape != (7, 3) or p.shape not in ((3,), (7, 3)) or len(populations) != 7
            or not np.all(np.isfinite(p)) or not np.all(np.isfinite(runs))
            or np.any((p < 0) | (p > 255)) or np.any((runs < 0) | (runs > 255))):
        raise ValueError('finite RGB, seven repeats and seven populations required')
    if min(populations) < 4:
        return dict(status='UNMEASURED', reason='deep population below four',
                    pixels=populations, survives=False, heldoutCoverage=False)
    pp = np.broadcast_to(p, (7, 3)); bar = .5+.5*np.ptp(runs,axis=0)
    def compare(pred, native):
        low = native <= 5; high = native >= 250; measured = ~(low | high)
        deficit = np.where(low, np.maximum(pred-5, 0), np.where(high,np.maximum(250-pred,0),0))
        error = abs(pred-native); rail_fail = deficit > 0
        fail = rail_fail | (measured & (error > np.maximum(1,bar)))
        return dict(status=np.where(measured,'measured',np.where(rail_fail,'UNMEASURED','censored-bound-satisfied')).tolist(),
                    errorCodes=np.where(measured,error,None).tolist(), boundDeficitCodes=deficit.tolist(),
                    boundFailure=rail_fail.tolist(), failed=fail.tolist(), nativeRGB=native.tolist(),
                    predictedRGB=pred.tolist(), railChannels=(~measured).tolist())
    median = compare(np.median(pp,axis=0), np.median(runs,axis=0))
    repeats = [compare(pred,native) for pred,native in zip(pp,runs)]
    rows = [median,*repeats]
    return dict(pixels=populations, barRGB=bar.tolist(), median=median, runs=repeats,
                survives=not any(any(r['failed']) for r in rows),
                heldoutCoverage=not any(any(r['railChannels']) for r in rows))


def deep_summary(rows):
    admitted = [r for r in rows if r.get('reason') != 'deep population below four']
    counts = dict(populationDeficientMembers=len(rows)-len(admitted), admittedMembers=len(admitted))
    if not admitted:
        return dict(status='UNMEASURED', reason='deep population below four', passes=False, **counts)
    passed = all(r['survives'] for r in admitted)
    if any(not r['heldoutCoverage'] for r in admitted):
        return dict(status='UNMEASURED', reason='censored', passes=None, constraintsPass=passed, **counts)
    return dict(status='measured', passes=passed, **counts)


def veto_bin(prediction, baseline, runs, minimum=4):
    """W38 absolute-before-mean per-channel veto, median and every native repeat.

    Raw rail residuals remain readings, not accuracy claims. One-sided rail
    constraints are scored separately. A signed residual cannot cancel in a bin.
    """
    p = np.asarray(prediction,float); b = np.asarray(baseline,float); runs = np.asarray(runs,float)
    if p.ndim != 2 or p.shape[1] != 3 or b.shape != p.shape or runs.shape != (7,*p.shape):
        raise ValueError('veto needs matched RGB pixels and seven repeats')
    if not all(np.all(np.isfinite(a)) for a in (p,b,runs)): raise ValueError('nonfinite veto')
    if len(p) < minimum:
        return dict(status='UNMEASURED', reason='population below four', pixels=len(p), passes=None)
    def compare(native):
        new = abs(p-native).mean(axis=0); old = abs(b-native).mean(axis=0); delta = new-old
        return dict(candidateResidualRGB=new.tolist(), baselineResidualRGB=old.tolist(),
                    worseningRGB=delta.tolist(), vetoRGB=(delta > 1+1e-10).tolist())
    median = compare(np.median(runs,axis=0)); repeats = [compare(n) for n in runs]
    return dict(status='measured', pixels=len(p), median=median, runs=repeats,
                passes=not any(any(r['vetoRGB']) for r in [median,*repeats]),
                rule='candidate absolute residual minus shipped absolute residual <= 1 code per channel')


def project(cell, png):
    check_runtime()
    return base.project(cell, png)


def native_reader(archive, roles, authorization=None, requested_wave=None):
    """Calval has no token; holdout requires the actual runner receipt token."""
    guard = module('e3_raw_guard', W39 / 'replay-archive.py')
    guard.deny(Path.home() / 'vitrea-w39')
    selected_wave = wave if requested_wave is None else requested_wave
    if 'holdout' in roles:
        if authorization is None: raise PermissionError('holdout requires request.authorization')
        authorization.check(selected_wave, INVENTORY_SHA)
    reader = selected_wave.reader(archive, roles=roles, authorization=authorization)
    if reader.generation != INVENTORY_SHA: raise ValueError('native inventory generation mismatch')
    return reader


def payloads(reader, cell):
    archive = module('e3_archive', W39 / 'w39_archive.py')
    runs, states = archive.unbundle(reader.read(cell, 'crop'))
    runs = [r for r in runs if r['admitted'] and r['protocol'] == 'normal']
    if len(runs) != 7: raise ValueError('all seven admitted normal repeats required')
    decoded = {key: archive.unpack(states[key]) for key in {r['state'] for r in runs}}
    result = [decoded[r['state']] for r in runs]
    comp, scale = base.component(cell); endpoint, _ = identity(cell)
    expected = m.readers.shapes_of(comp)
    for p in result:
        if (m.readers.shapes_of(p['component']) != expected or p['scale'] != scale
                or p['scheme'] != endpoint.split('-')[0]
                or p['pose'] != wave.scenes[cell.split('/',1)[1]]['state']
                or tuple(np.asarray(p['rgb']).shape[:2][::-1]) != runner.dimension(wave,cell)):
            raise ValueError('native payload disagrees with public cell identity')
    return result, [r['state'] for r in runs]


def numerical(cell, prediction, native, states):
    comp, scale = base.component(cell); shapes = m.readers.shapes_of(comp)
    geo = m.readers.geometry(np.asarray(native[0]['rgb']).shape[:2], shapes, scale)
    expected = [i for i, shape in enumerate(shapes) if not shape.opaque]
    if [r['member'] for r in prediction['members']] != expected:
        raise ValueError('prediction member coverage differs')
    endpoint, background = identity(cell); structured = background['kind'] != 'solid'
    members = []
    for row in prediction['members']:
        member = row['member']; shape = shapes[member]
        deep = [m.readers.deep_body(p['rgb'],geo,member) for p in native]
        populations = [d['pixels'] for d in deep]
        if min(populations) < 4:
            score = dict(status='UNMEASURED', reason='deep population below four', pixels=populations,
                         survives=False, heldoutCoverage=False)
            members.append(dict(member=member, score=score)); continue
        runs = np.array([d['medianRGB'] for d in deep])
        pred = row['predictedRGB']
        frozen_score = score_deep(pred,runs,populations)
        if structured:
            mask = (geo.member == member) & (geo.d <= -m.readers.DEEP_CSS*scale)
            # Reference comes from the SAME guarded payload/state as its native reading.
            pred = [local_prediction(np.asarray(p['noGlass'])[mask],endpoint,min(shape.size)) for p in native]
        score = score_deep(pred,runs,populations)
        members.append(dict(member=member, score=score, frozenPublicPredictionScore=frozen_score,
                            nativeDeep=deep))
    return dict(**deep_summary([r['score'] for r in members]), members=members,
                stateMembership=states, disposition=disposition(cell),
                diagnostic='S0' if structured else None,
                referenceOrigin='guarded per-state local noGlass' if structured else 'public solid sRGB',
                claim='uniform body only; other endpoint and structured residuals are diagnostic')


def rendered_score(cell, png, baseline, native, states):
    """Score the fresh receipt capture, not its frozen numerical projection."""
    raw = base.rendered.score_capture(png, native, baseline=baseline)
    web = base.rendered.read_capture(png); shipped = base.rendered.read_capture(baseline)
    if shipped.shape != web.shape: raise ValueError('shipped/candidate frame dimensions differ')
    comp, scale = base.component(cell); shapes = m.readers.shapes_of(comp)
    geo = m.readers.geometry(web.shape[:2], shapes, scale)
    native_rgb = np.array([p['rgb'] for p in native],float)
    deeps = []; veto = []; interior = []
    for member, shape in enumerate(shapes):
        if shape.opaque: continue
        ws = m.readers.deep_body(web,geo,member); bs = m.readers.deep_body(shipped,geo,member)
        ns = [m.readers.deep_body(p['rgb'],geo,member) for p in native]
        pops = [d['pixels'] for d in ns]
        if min(pops) >= 4:
            run_medians = np.array([d['medianRGB'] for d in ns])
            deep = score_deep(ws['medianRGB'],run_medians,pops)
            # The body's statistic is its median, not a pixel-average residual.
            vv = veto_bin([ws['medianRGB']],[bs['medianRGB']],run_medians[:,None,:],minimum=1)
            vv['deepPopulations'] = pops
        else:
            deep = dict(status='UNMEASURED',reason='deep population below four',pixels=pops,
                        survives=False,heldoutCoverage=False)
            vv = dict(status='UNMEASURED',reason='deep population below four',pixels=pops,passes=None)
        deeps.append(dict(member=member,score=deep))
        veto.append(dict(member=member,part='deep',score=vv))
        bins, labels = m.readers.edge_bins(geo,member)
        for i, b in enumerate(bins):
            if b['part'] == 'boundary': continue
            mask = labels == i
            v = veto_bin(web[mask],shipped[mask],native_rgb[:,mask])
            veto.append(dict(**b,score=v))
            if b['shell'] < 0:
                interior.append(dict(**b,score=m.score_bin(web[mask],native_rgb[:,mask])))
    admitted_veto = [v for v in veto if v['score']['passes'] is not None]
    result = dict(**deep_summary([d['score'] for d in deeps]), deep=deeps,
        rawRendered=raw, interiorTransfer=interior, veto=veto,
        vetoPass=bool(admitted_veto) and all(v['score']['passes'] for v in admitted_veto),
        populationDeficientVetoBins=len(veto)-len(admitted_veto), stateMembership=states,
        disposition=disposition(cell), diagnostic='rendered structured deep' if identity(cell)[1]['kind'] != 'solid' else None,
        baselineSha256=sha(baseline), captureSha256=sha(png),
        identityBytesEqual=sha(baseline)==sha(png))
    return result


def score(request):
    """Runner-only posterior callback. Never call directly to open native holdout."""
    check_runtime()
    if request.authorization is None: raise PermissionError('missing receipt authorization')
    # Check BEFORE constructing Reader; Reader checks again at every held-out open.
    request.authorization.check(request.wave, INVENTORY_SHA)
    expected, _ = runner.admitted_scope(request.root, request.wave)
    for kind, actual in [('numerical',request.numerical_cells),('rendered',request.rendered_cells)]:
        held = {c for c in expected[kind] if request.wave.roles[c.split('/',1)[1]] == 'holdout'}
        if set(actual) != held: raise ValueError('incomplete held-out '+kind+' membership')
    reader = native_reader(ARCHIVE, ('holdout',), request.authorization, request.wave)
    result = {}
    for candidate, artifacts in request.candidates.items():
        frozen_predictions = load(request.root / artifacts['predictions'])['cells']
        settings = load(request.root / artifacts['parameters'])
        if settings['body'] != parameters(): raise ValueError('candidate E3 coefficients differ')
        baseline = load(request.root / settings['shippedBaseline'])['cells']
        result[candidate] = dict(numerical={}, rendered={})
        for cell in request.numerical_cells:
            native, states = payloads(reader,cell)
            result[candidate]['numerical'][cell] = numerical(cell,frozen_predictions[cell],native,states)
            if cell in request.rendered_cells:
                reference = request.root / baseline[cell]['png']
                if sha(reference) != baseline[cell]['pngSha256']: raise ValueError('shipped baseline changed')
                result[candidate]['rendered'][cell] = rendered_score(cell,
                    request.captures[candidate][cell],reference,native,states)
    return result
