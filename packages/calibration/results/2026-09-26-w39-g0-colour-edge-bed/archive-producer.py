#!/usr/bin/env python3.12
"""Archive admitted W39 runs before plurality; disclose no holdout statistic (§5.184).

Derived from W34 G0's `archive-producer.py`. Each `--run` root is one capture
process's output (`manifest.json`, `admission.json`, the PNGs). Pass them in
sitting order — for a pass, runs 1..7, then its sentinel runs — because a
dependency a run did not capture itself (the colour `none` references exist in
run 1 only; a sentinel run captures only its sentinel ids) is taken from the
first run in that order that did capture it, and the source is recorded by hash.

A run's protocol arm is the sitting's to name: `admission.json` must carry
`protocol: normal | long`, and the producer checks it against the settings the
sitting declares for that arm (`sitting.PROTOCOLS`), the admission's own
`captureProtocol` echo and the harness manifest's `captureProtocol`, and that a
long run is a sentinel pass. A missing, unknown or disagreeing arm is refused; no
signature is inferred from the manifest (W34's seed-3401 test named W34's arm and
would call every W39 sentinel normal).

Every glass cell's state carries its own frame and the frames of the
dependencies `split.json` names for it, plus its opaque control's OWN no-glass
reference (`opaqueNoGlass`: the control's background and pose, which for a colour
cell's borrowed grey control is not the colour reference); every native-only cell
is archived as itself. Output goes to a new directory outside the repository; stdout is the
inventory's path, digest and counts, never a statistic.
"""
import argparse
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w39_archive  # noqa: E402
from wave import RANK, ROOT, default_wave, native_only  # noqa: E402


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@functools.cache
def sitting_protocols():
    """The arms' capture settings as the sitting declares them: one source, not a copy."""
    spec = importlib.util.spec_from_file_location('w39_sitting_protocols', HERE / 'sitting.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.PROTOCOLS


def protocol_of(admission, manifest, manifest_sha=None, protocols=None):
    """The arm the sitting admitted this run under, checked against what the harness did."""
    protocols = protocols if protocols is not None else sitting_protocols()
    arm = admission.get('protocol')
    if arm not in ('normal', 'long') or arm not in protocols:
        raise ValueError(f'admission names no protocol arm (normal | long): {arm!r}')
    declared = protocols[arm]
    if admission.get('captureProtocol') != declared:
        raise ValueError(f'admission captureProtocol disagrees with the sitting\'s {arm} settings')
    captured = manifest.get('captureProtocol') or {}
    seen = {k: captured.get(k) for k in declared}
    if seen != declared:
        raise ValueError(f'manifest captureProtocol {seen} is not the {arm} arm {declared}')
    if (arm == 'long') != str(admission.get('pass', '')).endswith('-sentinel'):
        raise ValueError('the long arm is exactly the sentinel passes')
    if manifest_sha is not None and admission.get('manifestSha256') != manifest_sha:
        raise ValueError('admission names a different manifest')
    return arm


def attestation(entry): return {k: v for k, v in entry.items() if k != 'file'}


def merged_component(declared, entry):
    component = dict(declared)
    for key in ('suppliedPaths', 'frameOrigin'):
        if key in entry: component[key] = entry[key]
    return component


def load_runs(roots):
    runs = []
    for root in roots:
        root = Path(root).resolve()
        admission = json.loads((root / 'admission.json').read_text())
        if admission.get('admitted') is not True or admission.get('dry') is True:
            raise ValueError('producer input is not an admitted capture run: ' + str(root))
        manifest = json.loads((root / 'manifest.json').read_text())
        manifest_sha = sha(root / 'manifest.json')
        protocol = protocol_of(admission, manifest, manifest_sha)
        entries = {}
        for profile in manifest['profiles']:
            for fixture in profile['fixtures']:
                key = (profile['profileKey'], fixture['sceneId'])
                if key in entries: raise ValueError('run captured one cell twice: ' + str(key))
                entries[key] = fixture
        runs.append(dict(root=root, admission=admission, manifest=manifest, protocol=protocol,
                         manifestSha=manifest_sha, entries=entries))
    if len({r['root'] for r in runs}) != len(runs): raise ValueError('a run root is named twice')
    return runs


def groups_from(runs, wave):
    """Yield one record list per captured cell, in cell order, with every dependency's frame."""
    canvas = wave.spec['canvas']

    @functools.lru_cache(maxsize=256)
    def decode(path):
        with Image.open(path) as image:
            if image.mode not in ('RGB', 'RGBA'): raise ValueError('unexpected PNG mode ' + image.mode)
            pixels = np.asarray(image.convert('RGB'), dtype=np.uint8)
        pixels.setflags(write=False)
        return pixels, sha(path)

    def frame(run, key):
        if key in run['entries']: source = run
        else:
            # The first run in sitting order that captured the dependency.
            source = next((r for r in runs if key in r['entries']), None)
            if source is None: raise ValueError('missing captured dependency ' + str(key))
        path = source['root'] / source['entries'][key]['file']
        pixels, digest = decode(path)
        scale = 1 if '-1x-' in key[0] else 2
        if pixels.shape != (canvas['height'] * scale, canvas['width'] * scale, 3):
            raise ValueError('frame dimensions disagree with the declared canvas and scale: ' + str(path))
        return pixels, digest, source['entries'][key], str(source['root'])

    def record(run, profile, sid, entry):
        scene = wave.scenes[sid]; declared = wave.component(sid)
        background = wave.spec['backgrounds'][scene['background']]
        payload = dict(sceneId=sid, profile=profile, scale=1 if '-1x-' in profile else 2,
                       scheme='dark' if '-dark-' in profile else 'light', pose=scene.get('state'),
                       background=background, backgroundKind=background['kind'],
                       component=merged_component(declared, entry), nativeOnly=native_only(declared))
        payload['rgb'], native_sha, _, _ = frame(run, (profile, sid))
        hashes = dict(native=native_sha, manifest=run['manifestSha'])
        # Per-capture attestations (times, window frame, settle, idle) and the run each
        # frame came from belong to the run row; the state holds only what an
        # estimator reads, so byte-stable repeats de-duplicate.
        attested, origins = dict(native=attestation(entry)), dict(native=str(run['root']))
        if not payload['nativeOnly']:
            deps = dict(wave.dependencies[sid])
            # The control's coverage is calibrated on ITS background, never the
            # dependent's: carry that reference as a dependency of its own.
            reference = reference_of(wave, deps['opaque'])
            if reference is not None: deps['opaqueNoGlass'] = reference
        elif declared['kind'] == 'none': deps = {}
        else:
            # An opaque control's coverage is calibrated against the no-glass
            # reference of its own background and pose, when the bed has one.
            reference = reference_of(wave, sid)
            deps = {} if reference is None else {'noGlass': reference}
        sources = {}
        for name, dep in deps.items():
            if RANK[wave.roles[dep]] > RANK[wave.roles[sid]]:
                raise PermissionError('dependency role ranks above its dependent: ' + dep)
            payload[name], hashes[name], dep_entry, origins[name] = frame(run, (profile, dep))
            attested[name] = attestation(dep_entry)
            sources[name] = dict(sceneId=dep, component=merged_component(wave.component(dep), dep_entry))
        if sources: payload['dependencies'] = sources
        admission = {k: run['admission'][k] for k in ('pass', 'run', 'protocol') if k in run['admission']}
        return dict(cell=profile + '/' + sid, run=str(run['root']), admitted=True, admission=admission,
                    protocol=run['protocol'], payload=payload, inputHashes=hashes,
                    attestation=attested, sources=origins)

    cells = sorted({key for run in runs for key in run['entries']})
    for profile, sid in cells:
        if profile + '/' + sid not in wave.cells: raise ValueError('raw run has undeclared cell ' + profile + '/' + sid)
    for profile, sid in cells:
        yield [record(run, profile, sid, run['entries'][(profile, sid)])
               for run in runs if (profile, sid) in run['entries']]


def reference_of(wave, sid):
    scene = wave.scenes[sid]
    found = [s for s, other in wave.scenes.items() if wave.component(s)['kind'] == 'none'
             and other['background'] == scene['background'] and other.get('state') == scene.get('state')]
    if len(found) > 1: raise ValueError('ambiguous no-glass reference for ' + sid)
    return found[0] if found else None


def refuse_repository(path):
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError('the archive of record is a release asset; write it outside the repository')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--run', action='append', type=Path, required=True, help='admitted run root, in sitting order')
    ap.add_argument('--out', type=Path, required=True, help='new directory outside the repository')
    args = ap.parse_args(argv)
    refuse_repository(args.out)
    wave = default_wave()
    runs = load_runs(args.run)
    captured = {profile + '/' + sid for run in runs for profile, sid in run['entries']}
    result = w39_archive.produce(groups_from(runs, wave), wave, args.out, captured=captured)
    print(json.dumps(dict(admitted=True, inventory=str(args.out / 'inventory.json'),
                          inventorySha256=sha(args.out / 'inventory.json'),
                          declaredCells=result['declaredCells'], archivedCells=result['archivedCells'],
                          uncaptured=len(result['uncaptured'])), indent=2))


if __name__ == '__main__': main()
