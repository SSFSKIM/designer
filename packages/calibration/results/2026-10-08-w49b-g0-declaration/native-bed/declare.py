#!/usr/bin/env python3.12
"""Generate/check W49b's native experiment. This program never calls a native tool."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reuse

REPO = reuse.REPO
REL = str(HERE.relative_to(REPO))
CANONICAL = 'apps/reference-apple/scenes.json'
W39_PIN = 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/bundle-pin.json'
SPANS = (44, 64, 96, 112, 128, 144, 160, 192, 224)
BLIND_SPANS = (112, 144, 224)
BRIDGE_BACKGROUNDS = ('checkerboard-32', 'impulse', 'dark-solid')
BRIDGE_COMPONENTS = ('rrect-md', 'rrect-ml', 'rrect-lg')
BRIDGE_IDS = ['checkerboard-32__rrect-lg', 'impulse__rrect-ml', 'impulse__rrect-lg',
              'dark-solid__rrect-md', 'dark-solid__rrect-lg']
LOCAL_TOOLS = ('declare.py', 'reuse.py', 'pass-spec.py', 'sitting.py', 'record-machine.py',
               'sitting-orchestrate.sh', 'run-sitting-w43.sh', 'orchestrate.py',
               'release.py', 'test_bed.py', 'RUNBOOK.txt', 'requirements.txt')
REUSED_TOOLS = ('pass-spec.py', 'sitting.py', 'record-machine.py', 'sitting-orchestrate.sh', 'timing.py')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(doc):
    return json.dumps(doc, indent=2) + '\n'


def profile(scale):
    return f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'


def scenes_doc(canvas):
    return dict(version=1, canvas=canvas, backgrounds={}, components={'none': {'kind': 'none'}},
                scenes=[], profiles=[], split={k: [] for k in ('calibration', 'validation', 'holdout',
                                                              'recorded', 'probe')})


def add_scene(doc, unit, bg, component, role):
    for state in ('rest', 'inactive'):
        sid = f'{unit}__{state}'
        doc['scenes'].append(dict(id=sid, background=bg, component=component, state=state))
        doc['split'][role].append(sid)


def finish(doc):
    ids = [s['id'] for s in doc['scenes']]
    doc['profiles'] = [dict(key=profile(scale), colorScheme='dark', a11y='standard', scenes=ids)
                       for scale in (1, 2)]
    return doc


def validate_scenes(doc):
    ids = [s['id'] for s in doc['scenes']]
    assigned = [sid for group in doc['split'].values() for sid in group]
    if len(set(ids)) != len(ids) or len(assigned) != len(set(assigned)) or set(ids) != set(assigned):
        raise ValueError('every scene must have exactly one role')
    for s in doc['scenes']:
        if s['background'] not in doc['backgrounds'] or s['component'] not in doc['components']:
            raise ValueError('scene names an undeclared background or component')
        if s['state'] not in ('rest', 'inactive') or 'label' in s:
            raise ValueError('native bed declares only reachable, unlabelled poses')
    for c in doc['components'].values():
        if c['kind'] == 'none':
            continue
        w, h = c['size']
        x, y = c.get('offset', [0, 0])
        if w <= 0 or h <= 0 or w / 2 + abs(x) > doc['canvas']['width'] / 2 \
                or h / 2 + abs(y) > doc['canvas']['height'] / 2:
            raise ValueError('supplied shape is outside the declared canvas')
    for p in doc['profiles']:
        if set(p['scenes']) != set(ids):
            raise ValueError('profile does not capture the whole source document')


def native_bed():
    doc = scenes_doc(dict(width=576, height=456))
    units = []
    core = []
    for pitch in (4, 8, 16, 32, 64):
        bg = f'checker-p{pitch}-000-255'
        doc['backgrounds'][bg] = dict(kind='checkerboard', cell=pitch, a=[0]*3, b=[255]*3)
        core.append((bg, dict(family='periodic', pitch=pitch, encodedMean=127.5, encodedContrast=255)))
    # Spacing 512 places exactly ONE impulse at (256,256) on this canvas.
    # Main shapes have offset (-32,+28), so this is their exact centre at every
    # span. Integer offsets are already supported by the pinned W39 binary.
    for name, back, front in (('impulse-positive-4', 0, 255), ('impulse-negative-4', 255, 0)):
        doc['backgrounds'][name] = dict(kind='impulse', background=[back]*3, foreground=[front]*3,
                                        size=4, spacing=512)
        core.append((name, dict(family='isolated-impulse', impulseSize=4, polarity=front-back)))
    doc['backgrounds']['photo-fit'] = dict(kind='synthetic-photo', seed=20260825)
    core.append(('photo-fit', dict(family='photo', seed=20260825)))
    for level in (0, 128, 255):
        bg = f'grey-{level}'
        doc['backgrounds'][bg] = dict(kind='solid', srgb=[level]*3)
        core.append((bg, dict(family='uniform', encodedMean=level)))
    for span in SPANS:
        doc['components'][f'rrect-s{span}'] = dict(kind='rrect', size=[1.75*span, span],
                                                  radius=.2125*span, offset=[-32, 28])

    def unit(bg, span, family=None, component=None, split=None, **axes):
        comp = component or f'rrect-s{span}'
        name = f'{bg}--{comp}'
        role = split or ('holdout' if span in BLIND_SPANS else 'calibration')
        add_scene(doc, name, bg, comp, role)
        units.append(dict(id=name, background=bg, component=comp, span=span, split=role,
                          family=family, **axes))

    for span in SPANS:
        for bg, axes in core:
            unit(bg, span, **axes)
    # Independent encoded midpoint/contrast cross at two pitches and spans.
    # Derived linear mean is NOT held by an encoded midpoint; no-glass controls
    # measure it so a fit cannot confuse the two definitions of level.
    for mean in (64, 128, 192):
        for contrast in (32, 96):
            for pitch in (16, 64):
                lo, hi = mean - contrast//2, mean + contrast//2
                bg = f'checker-p{pitch}-m{mean}-c{contrast}'
                doc['backgrounds'][bg] = dict(kind='checkerboard', cell=pitch, a=[lo]*3, b=[hi]*3)
                for span in (96, 160):
                    unit(bg, span, family='level-contrast', pitch=pitch, encodedMean=mean,
                         encodedContrast=contrast)
    # Full versus low contrast at EXACTLY midpoint 128, not 127.5 versus 128.
    for pitch in (16, 64):
        bg = f'checker-p{pitch}-m128-c254'
        doc['backgrounds'][bg] = dict(kind='checkerboard', cell=pitch, a=[1]*3, b=[255]*3)
        for span in (96, 160):
            unit(bg, span, family='matched-mean-full-contrast', pitch=pitch,
                 encodedMean=128, encodedContrast=254)
    for mean in (64, 192):
        bg = f'grey-{mean}'
        doc['backgrounds'][bg] = dict(kind='solid', srgb=[mean]*3)
        for span in (96, 160):
            unit(bg, span, family='uniform', encodedMean=mean)
    # New levels, a new contrast and a new pitch at blind spans, all crossed.
    for mean in (96, 160):
        bg = f'checker-p24-m{mean}-c64'
        doc['backgrounds'][bg] = dict(kind='checkerboard', cell=24, a=[mean-32]*3, b=[mean+32]*3)
        for span in (144, 224):
            unit(bg, span, family='blind-level-contrast', pitch=24, encodedMean=mean, encodedContrast=64)
    # Integer source/surface displacement is reachable on the old size/offset
    # actuator. Fractional phase was not (W34/W39), so none is claimed here.
    for span in (128, 160, 192):
        for axis, offset in (('x', [1, 0]), ('y', [0, 1])):
            comp = f'rrect-s{span}-shift-{axis}'
            doc['components'][comp] = dict(doc['components'][f'rrect-s{span}'],
                                           offset=[-32 + offset[0], 28 + offset[1]])
            for bg in ('impulse-positive-4', 'checker-p4-000-255', 'grey-128'):
                unit(bg, span, family='integer-grid-phase', component=comp, offset=offset)
    for size in (1, 2):
        bg = f'impulse-positive-{size}'
        doc['backgrounds'][bg] = dict(kind='impulse', background=[0]*3, foreground=[255]*3,
                                     size=size, spacing=512)
        for span in (128, 160, 192):
            unit(bg, span, family='impulse-footprint', impulseSize=size)
    # Area is crossed at fixed min-span. It is not renamed a span law before a
    # tree reading: memo F could not distinguish an area/resolution choice.
    for span in (128, 160, 192):
        comp = f'rrect-s{span}-wide'
        doc['components'][comp] = dict(kind='rrect', size=[2*span, span], radius=.2125*span, offset=[-32, 28])
        for bg in ('impulse-positive-4', 'checker-p32-000-255', 'grey-128'):
            unit(bg, span, family='fixed-span-area', component=comp, aspect=2)
    for pitch in (12, 24, 48):
        bg = f'checker-p{pitch}-000-255'
        doc['backgrounds'][bg] = dict(kind='checkerboard', cell=pitch, a=[0]*3, b=[255]*3)
        for span in (96, 160, 192):
            unit(bg, span, family='blind-pitch', split='holdout', pitch=pitch,
                 encodedMean=127.5, encodedContrast=255)
    doc['backgrounds']['photo-blind'] = dict(kind='synthetic-photo', seed=20261008)
    for span in (96, 160, 192):
        unit('photo-blind', span, family='blind-photo', split='holdout', seed=20261008)
    # Every generator gets its own no-glass read, not a single universal grey.
    blind_bg = {u['background'] for u in units if u['split'] == 'holdout'} \
        - {u['background'] for u in units if u['split'] == 'calibration'}
    for bg in doc['backgrounds']:
        add_scene(doc, f'ref-{bg}', bg, 'none', 'holdout' if bg in blind_bg else 'recorded')
    finish(doc)
    validate_scenes(doc)
    return doc, units


def transfer_bed():
    canonical = json.loads((REPO / CANONICAL).read_bytes())
    doc = scenes_doc(dict(width=576, height=456))
    doc['backgrounds'] = {bg: copy.deepcopy(canonical['backgrounds'][bg]) for bg in BRIDGE_BACKGROUNDS}
    doc['components'] = {c: copy.deepcopy(canonical['components'][c]) for c in BRIDGE_COMPONENTS}
    for name in BRIDGE_IDS:
        bg, c = name.split('__')
        add_scene(doc, name, bg, c, 'recorded')
    return finish(doc)


def source_docs(plan, generated):
    return {name: generated[Path(row['path']).name] if row['path'].startswith(REL + '/')
            else json.loads((REPO / row['path']).read_bytes()) for name, row in plan['sources'].items()}


def sitting(native, transfer):
    sources = {'canonical': dict(path=CANONICAL, sha256=sha((REPO / CANONICAL).read_bytes())),
               'native': dict(path=REL + '/scenes-native.json', sha256=sha(encode(native).encode())),
               'transfer': dict(path=REL + '/scenes-transfer.json', sha256=sha(encode(transfer).encode()))}
    passes = []

    def capture(name, role, source, scale, pose, ids, runs, **extra):
        passes.append(dict(name=name, kind='capture', role=role, glass=.25, scale=scale,
                           pose=pose, source=source, runs=runs, protocol='normal',
                           profiles={profile(scale): sorted(ids)}, **extra))

    def bridge(phase, scale, pose, source='canonical'):
        state = 'rest' if pose == 'active' else 'inactive'
        ids = [f'{name}__{state}' for name in BRIDGE_IDS]
        cells = {}
        for sid in ids:
            path = f'apps/reference-apple/fixtures/{profile(scale)}/{sid}.png'
            cells[f'{profile(scale)}/{sid}'] = dict(reference=dict(path=path, sha256=sha((REPO/path).read_bytes())))
        name = f'{phase}-{source}-{scale}x-{pose}'
        extra = dict(bridge=dict(stop=phase != 'close', cells=cells))
        if phase == 'close':
            extra['runAfterCut'] = True
        capture(name, 'bridge-canonical' if source == 'canonical' else 'bridge-canvas-transfer',
                source, scale, pose, ids, 3, **extra)

    for scale in (2, 1):
        for pose in ('active', 'receded'):
            bridge('open', scale, pose)
    for scale in (2, 1):
        for pose in ('active', 'receded'):
            # Only calibration shapes are dumped, so tree coefficients at blind
            # spans/inputs cannot leak through a supposedly pixel-free sentinel.
            dump_ids = [s['id'] for s in native['scenes'] if s['state'] == 'rest'
                        and s['id'] in native['split']['calibration']
                        and (s['background'] == 'grey-128' or
                             (s['component'] in ('rrect-s128', 'rrect-s160', 'rrect-s192') and
                              s['background'] in ('checker-p4-000-255', 'impulse-positive-4')))]
            passes.append(dict(name=f'dump-native-{scale}x-{pose}', kind='dump', role='dump-sentinel',
                               glass=.25, scale=scale, pose=pose, source='native',
                               profile=profile(scale), scenes=sorted(dump_ids)))
            bridge('transfer', scale, pose, 'transfer')
            state = 'rest' if pose == 'active' else 'inactive'
            state_ids = {s['id'] for s in native['scenes'] if s['state'] == state}
            cal = sorted(state_ids & set(native['split']['calibration']))
            blind = sorted(state_ids & set(native['split']['holdout']))
            references = {s['id'] for s in native['scenes'] if s['state'] == state and s['component'] == 'none'}
            for suffix, role, ids, runs in (
                    ('refs-cal', 'no-glass-calibration', state_ids & set(native['split']['recorded']), 3),
                    ('cal', 'native-calibration', cal, 5),
                    ('refs-blind', 'no-glass-blind', set(blind) & references, 3),
                    ('blind', 'native-blind', set(blind) - references, 5)):
                capture(f'native-{suffix}-{scale}x-{pose}', role, 'native', scale, pose, ids, runs)
    for scale in (1, 2):
        for pose in ('active', 'receded'):
            bridge('close', scale, pose)
    return dict(schema='w43-sitting-plan-1', sitting='native', sources=sources, passes=passes,
                nativeWave='W49b', blindRoles=['native-blind', 'no-glass-blind'],
                comment='No canonical publication. Cut-safe closes use the W43 contract with canonical references.')


def bridge_qualification(plan):
    """Check actual committed reference populations, not the identity shortcut."""
    import numpy as np
    S = reuse.driver()
    F, R = S.instrument()
    canonical = json.loads((REPO / CANONICAL).read_bytes())
    scenes = {s['id']: s for s in canonical['scenes']}
    seen, qualified = set(), []
    for p in plan['passes']:
        if not p['name'].startswith('open-'):
            continue
        for cell, row in p['bridge']['cells'].items():
            if cell in seen:
                continue
            seen.add(cell)
            sid = cell.split('/', 1)[1]
            scene = scenes[sid]
            frame = S.decode_frame((REPO / row['reference']['path']).read_bytes())
            count = 0
            for kernel in (('n', 'w') if p['pose'] == 'active' else ('n',)):
                c = F.Cell(cell, canonical['backgrounds'][scene['background']],
                           canonical['components'][scene['component']], p['scale'], 'dark',
                           scene['state'], rgb=True, kernel=kernel)
                pops = R.populations(c) if c.mask.sum() else []
                if not pops:
                    continue
                stats = R.statistics(c, frame, pops)
                if not all(np.isfinite(v) for v in stats.values()):
                    raise ValueError('opening bridge reference has missing region statistics: ' + cell)
                count += len(stats)
            if count == 0:
                raise ValueError('opening bridge has no region statistic: ' + cell)
            qualified.append(dict(cell=cell, statistics=count, referenceSha256=row['reference']['sha256']))
    return qualified


def build():
    native, units = native_bed()
    transfer = transfer_bed()
    plan = sitting(native, transfer)
    docs = {'scenes-native.json': native, 'scenes-transfer.json': transfer, 'sitting-native.json': plan}
    P = reuse.pass_spec()
    sources = source_docs(plan, docs)
    P.validate_plan(plan, sources)
    counts = P.plan_counts(plan, sources)
    T = reuse.timing()
    rates = T.measure()
    price = T.price(plan, sources, rates)
    pin = json.loads((REPO / W39_PIN).read_bytes())
    pin['w49bStatus'] = 'PROSPECTIVE ONLY: retired/ungranted since W43. User re-addition is required before any launch.'
    pin['sourcePinPath'] = W39_PIN
    pin['sourcePinSha256'] = sha((REPO / W39_PIN).read_bytes())
    docs['bundle-pin.json'] = pin
    manifest = dict(
        schema='w49b-native-bed-1', captureReady=False, captureAuthorised=False,
        authority='Parent DL2/DL3 in w49b-rulings.md; DL1 thick-subset scope overrides the draft.',
        axes=dict(scheme='dark', glassTintAmount=.25, poses=['active', 'receded'], scales=[1, 2],
                  spans=list(SPANS), calibrationSpans=[s for s in SPANS if s not in BLIND_SPANS],
                  blindSpans=list(BLIND_SPANS), blindPitches=[12, 24, 48]),
        canvas=native['canvas'], units=units,
        repeats=dict(glassRuns=5, noGlassRuns=3, bridgeRuns=3, independentFreshLaunches=True,
                     minimumScreenCaptureReadsPerFixture=2, maximumScreenCaptureReadsPerFixture=8,
                     settle='1.75 s initial dwell, then 1 s-spaced reads until consecutive frames agree',
                     floorCodes=.5,
                     bar='For encoded-code means, standard deviations and RGB/profile-bin medians: '
                         'max(0.5, (max(repeat statistic)-min(repeat statistic))/2). '
                         'Linear-luma statistics carry their repeat spread in linear units separately; '
                         'do not compare it directly to the one-code stop.',
                     stop='Any calibration repeat bar above 1 code, failed bridge, missing run, or missing '
                          'no-glass control stops identification. No fit to blind pixels.'),
        bridge=dict(smallCanvas=dict(width=320, height=200), largeCanvas=native['canvas'],
                    cropCss=[128, 128, 320, 200], scenes=BRIDGE_IDS,
                    rule='Every opening and transfer run: byte/pixel identity after crop, or every W42 region '
                         'median within max(1 code, measured bar); no empty-statistic opening cell. '
                         'Closing bridge disagreements are recorded, not silently voided.',
                    inputPhase='Both crop offsets are exact multiples of 64; uniform, checker32 and '
                               'impulse64 backgrounds preserve their source phase. No photo bridge is claimed.'),
        measurement=dict(
            primary='Keep the canonical full-silhouette T1 acceptance unchanged. On this new bed report '
                    'encoded RGB and linear-luma means/stddev over a fixed analytic supplied-path mask, '
                    'with disjoint 0..24 CSS px inward edge and >=24 CSS px deep cuts.',
            grid='For positive/negative impulse controls subtract the same-span uniform response, '
                 'report signed x/y and radial median profiles, ring-bin means at 1 CSS px, halo '
                 'energy and second moment within radius48 intersected with the supplied-path mask, '
                 'and body mean. Every bin names its support count and edge/deep coverage; an empty '
                 'or truncated population is UNMEASURED, not a complete annulus by extrapolation. '
                 'Read no-glass impulse area/energy rather than assume a 1-point impulse has equal '
                 'energy at both scales.',
            frequency='Read fixed-pitch gain in the >=24 CSS px deep cut, normalised by each no-glass '
                      'contrast. Report coded and linear level separately. Compare checker4/8, impulse '
                      'footprints 1/2/4 and integral x/y translations to expose alias/grid effects.',
            conditioning='Three encoded midpoints x two contrasts x two pitches at spans 96/160. '
                         'The c254/c32/c96 midpoint-128 controls share EXACT mean in encoded sRGB. '
                         'Encoded midpoint is not a fixed linear mean; no-glass references quantify both.',
            tree='Reuse dump-layers at glass0.25 for calibration spans/aspects/offsets and '
                 'ordinary-span128/160/192 impulse/checker4 controls in all four endpoints. '
                 'Read bd.scale, capture margin, face cap, blur radii and opacities beside observed pixels. '
                 'Memo F records bd.scale=.5 through s160 here; >160 and area dependence are unknown. '
                 'No blind shape or blind background is dumped before G1.',
            interpretation='A grid-quantised, phase-dependent impulse/fine response at the tree-named sampling '
                           'density distinguishes downsampling from a width-only Gaussian. A larger smooth '
                           'halo alone does not. Crossed aspect at held min-span distinguishes an area choice '
                           'from a span choice. If controls cannot distinguish the families, state UNIDENTIFIED; '
                           'do not prefer downsampling merely because the tree names it.'),
        blindness=dict(
            calibration='All six calibration spans on core inputs, crossed level/contrast, area and grid controls.',
            holdout='All core-input cells at spans112/144/224; new pitches12/24/48 at spans96/160/192; '
                    'new photo phase seed20261008 at those spans; midpoint96/160, contrast64, pitch24 '
                    'at spans144/224. Both poses/scales, with their exclusive no-glass references.',
            custody='Capture raw root is curator-only (umask077). release.py exports calibration passes '
                    'only and never opens a blind frame. Do not use W43 archive produce: it has no blind '
                    'redaction. Keep raw blind pass directories sealed until G1 freezes one point.',
            exposure='G1 hashes numerical predictions and the frozen software point before ONE blind read. '
                     'That read includes native repeat qualification; an unstable blind set is UNMEASURED '
                     'and stops the claim, never a reason to choose another point. Numbers/plots/pixels from '
                     'blind passes are never used in G0 fitting. Without this capture, read10 is non-blind.'),
        counts=counts['totals'], shapeUnits=len(units), backgroundControls=len(native['backgrounds']),
        timing=dict(source=rates['source'], rates=rates, estimate=price,
                    canvasAreaRatioToMeasuredBed=4.104, largerCanvasCadenceMeasured=False,
                    cadenceAssumption='W42 measured almost equal 1x/2x intervals despite four times '
                                      'the pixels; the settle/reset dwell dominates. Still, the new '
                                      'canvas cadence is estimated, not observed.',
                    stopLossFraction=.10,
                    exclusions='Extra HID idle, user setup, initial pin/grant checks, initial display '
                               'switch and trap restoration are not in the empirical model. Reserve '
                               'another 20 minutes for start/end and user setup. Five repeats, not W43 seven, '
                               'are prospective here; require all five and use the declared repeat stop.'),
        prerequisites=dict(
            runtime=dict(python='/Users/new/vitrea-w49/py/bin/python', version='3.14.6',
                         requirements=REL + '/requirements.txt',
                         defaultPython312='Normal user-site arm64 numpy2.3.5 imports successfully. Under -I, '
                                          'user-site is disabled and framework x86_64 numpy2.2.2 fails dlopen; '
                                          'x86_64 execution unavailable. The pinned arm64 venv is explicit.'),
            userX5Lift='Required, not granted by the charter, parent message, or this declaration.',
            bundle='A compatible, positively granted, pinned bundle. The original currently granted '
                   'bd3092e8 bundle lacks windowFrame/suppliedPaths; do NOT rebuild apps/reference-apple/build '
                   'or weaken admission to make it fit. The W39 side bundle is now ungranted.',
            atMac='User quits browsers and holds all browser automation/test suites; Universal Control '
                  'off, other device away/asleep. Accessibility lifts off. Native all-names census, '
                  '75 s HID idle per fresh launch, 60 s per fixture, pose/window/path/colour attestations '
                  'and 5 s watchdog remain W43 exactly.',
            sealing='Assemble and commit this declaration and all pinned tools before live pin-check. '
                    'Dry validation does not prove a bundle currently has a grant.'),
        bundleRoutes=[
            dict(id='regrant-w39', recommended=True,
                 bundlePath=pin['path'], bundleIdentifier=pin['bundleIdentifier'],
                 userActions='At the Mac: System Settings > Privacy & Security > Screen & System Audio '
                             'Recording (Screen Recording on releases using that title). Press +; use '
                             'the file picker Go to Folder for /Users/new/vitrea-w39/side/VitreaReference.app; '
                             'add the application and enable its toggle. Complete any macOS authentication '
                             'or Quit & Reopen request yourself. Leave the app closed until the approved '
                             'sitting. The operator verifies the exact .w39 grant and pinned identity before '
                             'first launch, and the original dev.vitrea.reference-apple grant again at close.',
                 cost='One user grant action plus identity/grant verification and opening bridges; no build '
                      'or rendering change. Reuses W43 proven path attestation, cadence and memo F. '
                      'Temporary side-bundle permission must be explicitly restored/retired by the user '
                      'if macOS displaced the original grant.',
                 reason='Lowest change and strongest existing bridge/cadence provenance. All declared '
                        'scene generators and centred/integer-offset shapes are supported by that binary.'),
            dict(id='new-current-side', recommended=False,
                 bundlePath='/Users/new/vitrea-w49/native-side/VitreaReference.app',
                 bundleIdentifier='dev.vitrea.reference-apple.w49b',
                 userActions='After a separately authorised build into /Users/new/vitrea-w49/native-side '
                             '(never apps/reference-apple/build), use the same macOS settings pane + button '
                             'to add /Users/new/vitrea-w49/native-side/VitreaReference.app and enable its '
                             'toggle. Complete authentication/Quit & Reopen yourself. No launch before this '
                             'grant is positively verified for the exact new bundle.',
                 cost='Build, sign, pin new binary/cdhash/build inputs, replace bundle-pin before pixels '
                      'and reseal this declaration; user grant; run the opening canonical and canvas '
                      'bridges on the new binary. W43 capture cadence is an estimate, not measured on '
                      'this new binary. A failed bridge needs a revised declaration, not silent adoption.',
                 reason='Use if .w39 cannot be re-granted or a required modern harness feature is absent. '
                        'It is more work, with no necessary feature gained by this declared bed.')])
    docs['manifest.json'] = manifest
    docs['timing.json'] = dict(rates=rates, estimate=price, modelSelfCheck=T.self_check(rates))
    docs['bridge-qualification.json'] = dict(executedNative=False, cells=bridge_qualification(plan))
    return docs


def sealing(docs):
    files = []
    paths = [HERE / p for p in LOCAL_TOOLS] + [reuse.W43 / p for p in REUSED_TOOLS]
    # Native executable, fixtures and the W42 instrument are independently pinned
    # by their records; every imported Python instrument file is also bound here.
    instrument = REPO / 'packages/calibration/results/2026-09-29-w42-g0-declaration/instrument'
    paths += sorted(instrument.glob('*.py'))
    paths += [REPO / W39_PIN]
    for name, doc in sorted(docs.items()):
        files.append(dict(path=REL + '/' + name, sha256=sha(encode(doc).encode())))
    for path in paths:
        files.append(dict(path=str(path.relative_to(REPO)), sha256=sha(path.read_bytes())))
    for p in docs['sitting-native.json']['passes']:
        if p['kind'] != 'capture' or 'bridge' not in p:
            continue
        for row in p['bridge']['cells'].values():
            files.append(dict(path=row['reference']['path'], sha256=row['reference']['sha256']))
    files = list({row['path']: row for row in files}.values())
    return dict(schema='w49b-native-declaration-1', state='DECLARED, NOT AUTHORISED OR CAPTURED',
                items=[dict(id='sitting-native', declared=dict(planSha256=sha(encode(docs['sitting-native.json']).encode())))],
                manifestSha256=sha(encode(docs['manifest.json']).encode()), files=sorted(files, key=lambda r: r['path']))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=('write', 'check', 'dry-run'))
    args = ap.parse_args()
    docs = build()
    docs['bed-declaration.json'] = sealing(docs)
    digest = sha(encode(docs['bed-declaration.json']).encode())
    good = True
    for name, doc in docs.items():
        text = encode(doc)
        path = HERE / name
        if args.action == 'write':
            path.write_text(text)
        else:
            good &= path.is_file() and path.read_text() == text
    line = digest + '  bed-declaration.json\n'
    if args.action == 'write':
        (HERE / 'declaration.sha256').write_text(line)
    else:
        good &= (HERE / 'declaration.sha256').read_text() == line
    if args.action == 'dry-run':
        plan = docs['sitting-native.json']
        dry = reuse.driver().dry_plan(plan, source_docs(plan, docs))
        assert dry['executed'] is False
        # Exercise every derived document, including every fresh repeated launch.
        P = reuse.pass_spec()
        for p in plan['passes']:
            for n in range(1, 1 + (p['runs'] if p['kind'] == 'capture' else 1)):
                doc = P.derive_from(plan, source_docs(plan, docs), p['name'], n) if p['kind'] == 'capture' \
                    else P.dump_doc_from(plan, source_docs(plan, docs), p['name'])
                P.validate_plan(dict(plan, passes=[dict(p, **({'runAfterCut': True} if p.get('runAfterCut') else {}))]),
                                source_docs(plan, docs))
                # A subset is not the full source profile; role/pose/membership
                # integrity is checked by W43 derive/validate, not validate_scenes.
                assert {s['id'] for s in doc['scenes']} == set(P.capture_ids(doc))
        print('Dry sitting walk: executed=false; every derived run document and argv validated')
    m = docs['manifest.json']
    print(f'{args.action}: {"PASS" if good else "MISMATCH"}; {m["shapeUnits"]} shape units, '
          f'{m["backgroundControls"]} no-glass inputs; {json.dumps(m["counts"])}')
    print(f'Cadence estimate {m["timing"]["estimate"]["totalHours"]:.2f} h; '
          f'with 10% stop loss {m["timing"]["estimate"]["withStopLossHours"]:.2f} h; no native launch')
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
