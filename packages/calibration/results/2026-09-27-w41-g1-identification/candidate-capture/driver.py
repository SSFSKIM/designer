"""Web-only E3 candidate capture preparation. No native reader or exposure entry point."""
import argparse
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
from types import FunctionType, ModuleType
import uuid

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
spec = importlib.util.spec_from_file_location('candidate_capture_base', G1 / 'baseline/baseline.py')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
ROOT = base.ROOT
runner = base.load_module('candidate_capture_runner', G1 / 'exposure/runner.py')
wave = base.wave
CAPTURES = Path('/Users/new/vitrea-w41/g1-captures/candidate-e3')
CLAIM = G1 / 'exposure/body-e3-claim-scope.json'


def relative(path): return str(Path(path).relative_to(ROOT))


def source_inventory(root, namespace=None):
    """Keep the runtime frontier, but bind only this driver's imported Python graph.

    Walk module objects rather than sys.modules alone: the inherited boundary is
    loaded without registration. Function globals also retain from-import helpers.
    No imports are executed by this inventory; the candidate scorer stays unopened.
    The exposure runner's broader instrument frontier is unchanged.
    """
    root = Path(root).resolve()
    instruments = tuple(name + '/' for name in runner.INSTRUMENT_ROOTS)
    files = {name for name in runner.sources(root) if not name.startswith(instruments)}
    pending = [globals() if namespace is None else namespace]
    seen = set()
    while pending:
        scope = pending.pop()
        if id(scope) in seen: continue
        seen.add(id(scope))
        filename = scope.get('__file__')
        if not filename: continue
        path = Path(filename).resolve()
        if not path.is_relative_to(root) or path.suffix != '.py': continue
        files.add(str(path.relative_to(root)))
        for value in tuple(scope.values()):
            if isinstance(value, ModuleType): pending.append(vars(value))
            elif isinstance(value, FunctionType): pending.append(value.__globals__)
            elif isinstance(value, type):
                module = sys.modules.get(value.__module__)
                if module is not None: pending.append(vars(module))
    return sorted(files)


def snapshot(source, directory):
    source = Path(source)
    target = directory / (runner.sha(source) + source.suffix)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_bytes() != source.read_bytes(): raise ValueError('payload collision')
    else:
        with target.open('xb') as f: f.write(source.read_bytes())
    return target


def check_hashes(root, pins):
    for name, digest in pins.items():
        if runner.sha(root / name) != digest: raise ValueError('input changed: ' + name)


def batches(cells, roles):
    return [(kind, profile, [c.split('/', 1)[1] for c in cells
                             if c.startswith(profile + '/') and
                             (roles[c.split('/', 1)[1]] == 'holdout') == blind])
            for kind, blind in [('calval', False), ('blind', True)]
            for profile in sorted({c.split('/', 1)[0] for c in cells})
            if any(c.startswith(profile + '/') and
                   (roles[c.split('/', 1)[1]] == 'holdout') == blind for c in cells)]


def compare_identity(root, captures, shipped, identities):
    rows = {cell: {key + 'Equal': (root / captures[cell][key]).read_bytes() ==
                  (root / shipped[cell][key]).read_bytes() for key in ('png', 'projection')}
            for cell in identities}
    return dict(cells=rows, failures=[c for c, row in rows.items() if not all(row.values())])


def check_runtime():
    import numpy
    import PIL
    actual = dict(python=list(sys.version_info[:2]), numpy=numpy.__version__, pillow=PIL.__version__)
    if actual != runner.load(G1 / 'candidate-e3/runtime.json'):
        raise ValueError('projection runtime mismatch: ' + str(actual))


def shipped_freezes(cells):
    """Old renderer bytes need not equal the candidate; verify old committed evidence instead."""
    result = {}; dependencies = {}
    for directory, filename, role in [('baseline', 'frozen-baseline.json', False),
                                      ('blind-baseline', 'frozen-blind-baseline.json', True)]:
        path = G1 / directory / filename
        dependencies[relative(path)] = runner.committed(ROOT, relative(path))
        frozen = runner.load(path)
        expected = [c for c in cells if (wave.roles[c.split('/', 1)[1]] == 'holdout') == role]
        runner.coverage(frozen['captures'], expected, 'complete shipped ' + directory)
        authority = G1 / directory / ('seal.json' if role else 'authority-v2.json')
        field = 'sealSha256' if role else 'authoritySha256'
        if runner.committed(ROOT, relative(authority)) != frozen[field]:
            raise ValueError('shipped authority changed')
        dependencies[relative(authority)] = frozen[field]
        if not role:
            preparation = G1 / directory / 'preparation.json'
            if runner.committed(ROOT, relative(preparation)) != frozen['preparationSha256']:
                raise ValueError('shipped preparation changed')
            dependencies[relative(preparation)] = frozen['preparationSha256']
        for cell, row in frozen['captures'].items():
            if cell in result: raise ValueError('overlapping shipped freezes')
            for key in ('png', 'projection'):
                path = ROOT / row[key]
                if runner.sha(path) != row[key + 'Sha256']: raise ValueError('shipped bytes changed')
                if key == 'projection': runner.committed(ROOT, relative(path))
            raw = Path(row.get('primaryCapture', row['png']))
            for key, filename in [('cellSha256', 'cell__webgpu.json'),
                                  ('reportSha256', 'report__webgpu.json')]:
                if runner.sha(raw.parent / filename) != row[key]:
                    raise ValueError('shipped descriptor changed')
            result[cell] = row
    return result, dependencies


def attestation():
    chain = {
        'packages/calibration/web/scene.ts':
            'Registers every host variant regular without present override, publishes no materialization '
            'animation; reports actual policy and group sampling, with explicit candidate root-active pose.',
        'packages/platform-web/src/root.ts':
            'registerHost seeds presence and presencePublished to 1 unless present false, writes the '
            'materialization property; frame publishes that driver and forwards readHostChannels to nodes.',
        'packages/platform-web/src/channels.ts':
            'readHostChannels reads and clamps the materialization property; the idle fallback is 1.',
        'packages/platform-web/src/renderer-bridge.ts':
            'toSurfaceInput forwards node.channels to renderer surfaces without replacing materialization.',
        'packages/renderer-webgpu/src/instances.ts':
            'resolveSurfaces bounds materialization, and packInstances writes it at instance lane17.',
        'packages/renderer-webgpu/src/wgsl/field.ts':
            'WGSL_INSTANCE_STRUCT.mat is at byte offset68 (CPU lane17); eval_instance copies '
            's.mat into m.mat. The union interpolates member mat, all 1 here, and writes '
            'acc.mat to the presence target. Empty-field presence is also 1.',
        'packages/renderer-webgpu/src/wgsl/optics.ts':
            'Samples the presence target as mat and uses it for E3 replacement interpolation; '
            'at mat1 the replacement is the identified full-presence law.',
        'packages/renderer-webgpu/src/renderer.ts':
            'Packs effective E3 strength conditioned on regular variant, nominal material policy and '
            'actual backdrop texture. Those actual policy/sampling axes are separately report-validated.',
    }
    return dict(basis='source-derived', variant='regular', presence=1,
        effectivePresenceBasis='The static host registration, published channel, bridge, instance lane, '
            'field fold and optics read form the full chain. Every member has materialization1; '
            'the field interpolates ones, independently of coverage. No scene retargets presence.',
        limitations='Regular variant and presence1 are source-derived, NOT report-observed GPU values. '
            'Actual policy, sampling, renderer and root-active candidate pose are report-observed. '
            'Intermediate presence is unmeasured; native survival is not established here.',
        sourceChain=[dict(path=p, sha256=runner.sha(ROOT / p), claim=claim) for p, claim in chain.items()])


def assemble(name):
    check_runtime()
    directory = attempt(name)
    if directory.exists(): raise FileExistsError('attempt already exists')
    reviewed = runner.load(HERE / 'reviewed-inputs.json')['files']
    check_hashes(ROOT, reviewed)
    for path in reviewed: runner.committed(ROOT, path)
    admitted, _ = runner.admitted_scope(ROOT, wave)
    cells = admitted['rendered']
    if len(cells) != 600 or sum(wave.roles[c.split('/', 1)[1]] != 'holdout' for c in cells) != 536:
        raise ValueError('admitted public membership changed')
    shipped, dependency = shipped_freezes(cells)  # Before creating an attempt or candidate input.
    old = runner.load(G1 / 'baseline/preparation.json')
    profiles = {p: {k: relative(G1 / 'body-leaf/candidate' / Path(v).name)
                    for k, v in pair.items()} for p, pair in old['profiles'].items()}
    for profile, pair in profiles.items():
        for key, path in pair.items():
            if not ('-light-' in profile and key == 'receded'):
                if (ROOT / path).read_bytes() != (ROOT / old['profiles'][profile][key]).read_bytes():
                    raise ValueError('unclaimed document is not an identity byte copy')
    sources = source_inventory(ROOT)
    extra = [HERE / 'reviewed-inputs.json', CLAIM, G1 / 'candidate-e3/runtime.json',
             base.W39 / 'supplied-paths.json', wave.scenes_path, wave.split_path,
             ROOT / runner.INVENTORY_PATH, G1 / 'baseline/preparation.json',
             ROOT / old['backdrops'] / 'manifest.json']
    extra += [ROOT / old['backdrops'] / n for n in old['generatedBackgrounds']]
    pins = {p: runner.committed(ROOT, p) for p in set(sources) | set(reviewed) |
            {relative(p) for p in extra} | set(dependency)}
    directory.mkdir(parents=True)
    runtime = {str(p.relative_to(ROOT)): relative(snapshot(p, directory / 'policy-runtime'))
               for p in (ROOT / runner.POLICY_DIST).rglob('*')
               if p.is_file() and p.suffix in ('.js', '.mjs', '.cjs')}
    if runner.POLICY_DIST + '/index.js' not in runtime: raise ValueError('build policy first')
    base.save(directory / 'attestation.json', attestation())
    baseline = {}
    for cell, row in shipped.items():
        baseline[cell] = {key: relative(snapshot(ROOT / row[key], directory / 'shipped-payloads'))
                          for key in ('png', 'projection')}
        baseline[cell].update({key + 'Sha256': row[key + 'Sha256'] for key in ('png', 'projection')})
    base.save(directory / 'shipped-map.json', dict(cells=baseline, source=dependency))
    base.save(directory / 'runtime.json', dict(fixtures=old['backdrops'], runtimeArtifacts=runtime,
              candidates={'body-e3': dict(profiles=profiles)}))
    owned = {relative(p): runner.sha(p) for p in directory.rglob('*') if p.is_file()}
    base.save(directory / 'seal.json', dict(schema='w41-e3-web-pre-render-1', cells=cells,
        sourceRevision=runner.git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
        sources=sources, inputs={**pins, **owned}, profiles=profiles, fixtures=old['backdrops'],
        runtimeArtifacts=runtime, claimScope=relative(CLAIM), nativePayloadReads=0,
        note='Pre-render inputs only; no candidate pixels, survival or exposure claimed.'))
    print('ASSEMBLED', directory, 'Commit the entire attempt before capture.')


def attempt(name):
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', name): raise ValueError('unsafe attempt name')
    return HERE / name


def verify(name):
    check_runtime()
    directory = attempt(name)
    runner.committed(ROOT, relative(directory / 'seal.json'))
    sealed = runner.load(directory / 'seal.json')
    runner.coverage(source_inventory(ROOT), sealed['sources'], 'source inventory')
    check_hashes(ROOT, sealed['inputs'])
    for path in sealed['inputs']: runner.committed(ROOT, path)
    runner.verify_runtime_artifacts(ROOT, sealed['runtimeArtifacts'], required=True)
    return directory, sealed


def launch(directory, command, env, verify_inputs):
    """Only an X6 refusal is resumable. Once launched, a missing completion is a STOP."""
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / 'started.json').exists(): raise ValueError('already launched; preserve failure, stop')
    verify_inputs()
    check = base.x6.observe()
    base.save(directory / ('x6-' + uuid.uuid4().hex + '.json'), check)
    if not check['verdict']['passes']: raise PermissionError('X6 refused; no process launched; may recheck')
    base.save(directory / 'started.json', dict(at=base.stamp(), argv=command,
        environment={k: v for k, v in env.items() if k.startswith('VITREA_')}))
    try:
        with (directory / 'process.txt').open('x') as log:
            subprocess.run(command, env=env, check=True, stdout=log, stderr=subprocess.STDOUT)
    except BaseException as error:
        base.save(directory / 'failure.json', dict(at=base.stamp(), error=repr(error)))
        raise


def validate_batch(rows, sealed):
    for cell, row in rows.items():
        for key in ('png', 'projection', 'descriptor', 'report'):
            if runner.sha(ROOT / row[key]) != row[key + 'Sha256']:
                raise ValueError('completed capture changed: ' + cell)
        profile = cell.split('/', 1)[0]
        runner.validate_domain(wave, cell, runner.load(ROOT / row['descriptor']),
            runner.load(ROOT / row['report']), runner.domain_documents(ROOT, sealed['profiles'][profile]))


def capture(name):
    directory, sealed = verify(name)
    if (directory / 'frozen.json').exists(): raise FileExistsError('already frozen; no recapture')
    seal_sha = runner.sha(directory / 'seal.json')
    def guard():
        verify(name)
        if runner.sha(directory / 'seal.json') != seal_sha: raise ValueError('seal changed')
    env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
    env.update(VITREA_SCENES=str(wave.scenes_path), VITREA_FIXTURES=str(ROOT / sealed['fixtures']),
               VITREA_WEB_CAPTURES=str(CAPTURES / name), VITREA_ALLOW_FALLBACK_ADAPTER='0')
    all_rows = {}
    for kind, profile, ids in batches(sealed['cells'], wave.roles):
        guard()
        batch = directory / 'processes' / (kind + '-' + profile)
        if (batch / 'complete.json').exists():
            rows = runner.load(batch / 'complete.json')['cells']
            runner.coverage(rows, [profile + '/' + sid for sid in ids], 'completed batch')
            validate_batch(rows, sealed)
            all_rows.update(rows)
            continue
        out = CAPTURES / name / kind / profile
        if out.exists(): raise FileExistsError('raw capture destination exists; stop without overwriting')
        documents = sealed['profiles'][profile]
        definition = next(p for p in wave.spec['profiles'] if p['key'] == profile)
        command = ['pnpm', '--dir', str(ROOT / 'packages/calibration'), 'exec', 'tsx',
                   'scripts/capture-web.ts', *ids, '--renderer', 'webgpu', '--color-scheme',
                   definition['colorScheme'], '--scale', re.search(r'-(1|2)x-', profile)[1],
                   '--out', str(out), '--material-profile', str(ROOT / documents['material']),
                   '--receded-profile', str(ROOT / documents['receded'])]
        launch(batch, command, env, guard)
        guard()
        rows = {}
        for sid in ids:
            cell = profile + '/' + sid
            raw = out / sid
            descriptor = raw / 'cell__webgpu.json'; report = raw / 'report__webgpu.json'
            runner.validate_domain(wave, cell, runner.load(descriptor), runner.load(report),
                                   runner.domain_documents(ROOT, documents))
            png = raw / (sid + '__webgpu.png')
            projection = batch / 'projections' / (sid + '.json')
            base.save(projection, base.project(cell, png))
            row = dict(primaryCapture=str(png))
            for key, path in [('png', png), ('projection', projection),
                              ('descriptor', descriptor), ('report', report)]:
                row[key] = relative(snapshot(path, directory / 'capture-payloads'))
                row[key + 'Sha256'] = runner.sha(path)
            rows[cell] = row
        guard()
        validate_batch(rows, sealed)
        base.save(batch / 'complete.json', dict(cells=rows))
        all_rows.update(rows)
    guard()
    runner.coverage(all_rows, sealed['cells'], 'all actual candidate captures')
    baseline = runner.load(directory / 'shipped-map.json')['cells']
    selected = runner.claim_scope(ROOT, wave, dict(claimScope=sealed['claimScope']))
    identities = [c for c in sealed['cells'] if runner.endpoint(wave, c) not in selected]
    equality = compare_identity(ROOT, all_rows, baseline, identities)
    base.save(directory / 'raw-inventory.json', dict(cells=all_rows, sealSha256=seal_sha))
    base.save(directory / 'rendered.json', dict(cells={c: {k: row[k] for k in
        ('png', 'pngSha256', 'projection', 'projectionSha256')} for c, row in all_rows.items()}))
    base.save(directory / 'domain-evidence.json', dict(attestation=relative(directory / 'attestation.json'),
        cells={c: dict(descriptor=runner.load(ROOT / row['descriptor']),
                       report=runner.load(ROOT / row['report'])) for c, row in all_rows.items()}))
    base.save(directory / 'identity-equality.json', equality)
    if equality['failures']: raise ValueError('unclaimed rendered identity differs; preserve evidence, STOP')
    base.save(directory / 'frozen.json', dict(schema='w41-e3-web-pixels-1', frozenAt=base.stamp(),
        sealSha256=seal_sha, cells=600, nativePayloadReads=0,
        files={relative(p): runner.sha(p) for p in directory.rglob('*') if p.is_file()},
        note='Complete web predictions, not survival or permission to expose. Commit all payloads.'))
    print('CAPTURED 600 web predictions; no native reads or survival claim.', directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['assemble', 'verify', 'capture'])
    parser.add_argument('attempt')
    args = parser.parse_args()
    {'assemble': assemble, 'verify': verify, 'capture': capture}[args.operation](args.attempt)


if __name__ == '__main__': main()
