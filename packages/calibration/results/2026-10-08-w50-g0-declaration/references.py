"""Build the prospective reference inventory without reading blind pixels or fitting.

W49a's exposed registry supplies dark0.25 T1 values. Dark0.5's unadopted T1 population is
registered, not imputed from the other material. New native cells have identities and roles,
not fabricated hashes or successful measurements. Completion is a separate pre-fit seal.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CAL = ROOT / 'packages/calibration'
CURRENT = {'0.25': 'b2d074d2df24-940384c06f73', '0.5': '0eac5b294cc2'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pin(path):
    path = Path(path)
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            'sha256': sha(path)} if path.is_file() else None


def historical_cap(native, current, historical, budget):
    growth = (abs(current - native) - abs(historical - native)) / budget
    return max(1, growth), growth


def build():
    common = Path(subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse',
        '--path-format=absolute', '--git-common-dir'], text=True).strip()).parent
    canonical = common / 'packages/calibration/web-captures'
    fixtures = common / 'apps/reference-apple/fixtures'
    previous_path = CAL / 'results/2026-10-08-w49b-g0-declaration/references.json'
    old = json.loads(previous_path.read_text())
    scene_split = json.loads((ROOT / 'apps/reference-apple/scenes.json').read_text())['split']
    controls_path = HERE / 'evidence/dark-controls-complete.json'
    controls = {(c['profile'], c['scene']): c
                for c in json.loads(controls_path.read_text())['cells']}
    css_controls_path = HERE / 'evidence/dark-controls-css.json'
    css_controls = {(c['profile'], c['scene']): c
                    for c in json.loads(css_controls_path.read_text())['cells']}
    generations = {}
    for position, generation in CURRENT.items():
        documents = {}
        for slot, suffix in [('active.dark', ''), ('receded.dark', '-receded')]:
            path = CAL / f'profiles/apple-macos-27.0-1x-dark-standard-glass{position}{suffix}.json'
            snapshot = HERE / 'references/documents' / f'{sha(path)}.json'
            if not snapshot.is_file() or snapshot.read_bytes() != path.read_bytes():
                raise ValueError(f'Missing or changed pre-change document snapshot: {snapshot}')
            documents[slot] = {**pin(snapshot), 'source': str(path.relative_to(ROOT))}
        generations[generation] = {'matrix': pin(CAL / f'results/generations/{generation}.json'),
            'documents': documents, 'documentPair': {k: v['sha256'] for k, v in documents.items()},
            'captureTree': str(canonical)}
    for generation in ('d0219cd684bf', 'b2d074d2df24'):
        generations[generation] = old['generations'][generation]
    cells = []

    def base(profile, renderer, scene, statistic, support, role):
        position = profile.split('glass')[-1]
        generation = CURRENT[position]
        native = pin(fixtures / profile / f'{scene}.png')
        capture_root = canonical
        current = pin(capture_root / profile / scene / f'{scene}__{renderer}.png')
        # G0's named current controls fill the missing active0.5 impulse rows. The other
        # controls were verified byte-identical to canonical; no replacement generation is made.
        if renderer == 'webgpu' and (profile, scene) in controls:
            control = controls[(profile, scene)]
            if control['status'] not in ('BYTE_IDENTICAL', 'NO_PRIOR_CAPTURE'):
                raise ValueError(f'Current control is not admitted: {profile}/{scene}')
            scale = 2 if '-2x-' in profile else 1
            capture_root = Path(f'/Users/new/vitrea-w50/identity-controls-complete/{position}-{scale}x/web-captures')
            expected = capture_root / profile / scene / f'{scene}__{renderer}.png'
            if Path(control['capture']) != expected or not expected.is_file():
                raise ValueError('Current scratch control path differs from named observation')
            current = pin(expected)
        if renderer == 'css' and current is None and (profile, scene) in css_controls:
            control = css_controls[(profile, scene)]
            if control['status'] != 'NO_PRIOR_CAPTURE':
                raise ValueError(f'Missing CSS control disagrees with its evidence: {profile}/{scene}')
            scale = 2 if '-2x-' in profile else 1
            capture_root = Path(f'/Users/new/vitrea-w50/identity-controls-css/{position}-{scale}x/web-captures')
            expected = capture_root / profile / scene / f'{scene}__css.png'
            if Path(control['capture']) != expected or not expected.is_file():
                raise ValueError('CSS scratch control path differs from named observation')
            current = pin(expected)
        metadata_path = capture_root / profile / scene / f'cell__{renderer}.json'
        metadata = pin(metadata_path)
        if current and metadata:
            capture = json.loads(metadata_path.read_text())['capturePath']
            if any(f'sha256:{digest[:12]}' not in capture
                   for digest in generations[generation]['documentPair'].values()):
                raise ValueError(f'Canonical capture belongs to another generation: {profile}/{scene}')
        return {'profile': profile, 'renderer': renderer, 'scene': scene, 'statistic': statistic,
                'support': support, 'role': role, 'currentGeneration': generation,
                'currentDocumentPair': generations[generation]['documentPair'],
                'nativeEvidence': native, 'currentEvidence': current, 'currentMetadata': metadata,
                'historical': [], 'B': None, 'status': 'UNMEASURED'}

    for old_cell in old['cells']:
        role = 'historical-prediction-check' if old_cell['partition'] != 'gate' else 'gate'
        for position in ('0.25', '0.5'):
            profile = old_cell['profile'].replace('glass0.25', f'glass{position}')
            cell = base(profile, 'webgpu', old_cell['scene'], old_cell['statistic'],
                'native silhouette; T regression uses sigma4-device-px low-pass, fidelity fine residual', role)
            cell['stratum'] = old_cell['stratum']
            cell['currentMaxGrowthInB'] = 1
            if position == '0.25':
                cell.update(native=old_cell['native'], current=old_cell['current'], B=old_cell['B'],
                            fidelity=old_cell['fidelity'])
                historical = old_cell['historical']
                if historical:
                    cap, growth = historical_cap(cell['native'], cell['current'],
                                                  historical['value'], cell['B'])
                    cell['historical'] = [{**historical, 'enforced': True,
                        'maxGrowthInB': cap, 'frozenCurrentGrowthInB': growth}]
                if cell['nativeEvidence'] and cell['currentEvidence']:
                    cell['status'] = 'MEASURED'
            else:
                cell['missing'] = ['Own dark0.5 T1 reading and per-cell B',
                                   'Own dark0.5 T-band fixture for T cells']
            cells.append(cell)

    # Low-end path cuts and all existing owner axes are priced independently of T1 membership.
    for position, generation in CURRENT.items():
        matrix = json.loads((CAL / f'results/generations/{generation}.json').read_text())
        for row in matrix['cells']:
            profile, renderer, scene = row['key']['profileKey'], row['key']['web']['renderer'], row['key']['sceneId']
            historical = row['fixtureSet'] == 'holdout'
            role = 'historical-prediction-check' if historical else 'gate'
            low = ((scene.startswith('dark-solid__') and '-tint-' not in scene) or
                   scene in [f'impulse__rrect-{shape}__{pose}' for shape in ('ml','lg')
                             for pose in ('rest','inactive')])
            statistic = 'low-end-path-level' if low else 'owner-contracts'
            support = ('supplied path deep8; impulse additionally far24; mean and median encoded luma; '
                       'dark-solid per-channel median' if low else
                       'Existing M1/M2/C1/X1/L1/E2/coherence/X75/X76 applicability and exclusions unchanged')
            cell = base(profile, renderer, scene, statistic, support, role)
            cell['missing'] = ['W50 path-cut reading and bar' if low else 'Existing owner-contract referee report']
            cells.append(cell)
        # These native/current pairs are missing from the current0.5 matrix, not native targets.
        if position == '0.5':
            keys = {(c['profile'], c['renderer'], c['scene'], c['statistic']) for c in cells}
            for scale in (1, 2):
                for shape in ('ml', 'lg'):
                    profile = f'apple-macos-27.0-{scale}x-dark-standard-glass0.5'
                    scene = f'impulse__rrect-{shape}__rest'
                    for renderer in ('webgpu', 'css'):
                        key = (profile, renderer, scene, 'low-end-path-level')
                        if key not in keys:
                            cell = base(profile, renderer, scene, key[3],
                                'supplied path deep8/far24; encoded-luma mean and median',
                                'historical-prediction-check' if scene in scene_split['holdout'] else 'gate')
                            cell['missing'] = (['Required path-cut reading and native repeat bar']
                                if cell['currentEvidence'] else
                                ['Required pre-fit scratch current render and path-cut reading'])
                            cells.append(cell)
            # These two named failures belong to the original two-tier low-end price even
            # though the current generation has no CSS row. Keep its one-code growth rule;
            # adding a scratch capture is neither a fitted statistic nor a new baseline.
            profile = 'apple-macos-27.0-2x-dark-standard-glass0.5'
            for shape in ('ml', 'lg'):
                scene = f'impulse__rrect-{shape}__inactive'
                key = (profile, 'css', scene, 'low-end-path-level')
                if key not in keys:
                    cell = base(profile, 'css', scene, key[3],
                        'supplied path deep8/far24; encoded-luma mean and median; '
                        'CSS level-error growth <=1 encoded output code against current',
                        'historical-prediction-check' if scene in scene_split['holdout'] else 'gate')
                    cell['B'] = 1
                    cell['missing'] = ['Required current/native path-cut readings; no statistics imputed']
                    cells.append(cell)

    manifest = json.loads((HERE / 'bed/manifest.json').read_text())
    for native in manifest['cells']:
        for renderer in ('webgpu', 'css'):
            statistics = ['deep8-channel-median', 'central8-channel-median']
            if native['family'] != 'uniform':
                statistics += ['deep8-far24-luma-mean', 'deep8-far24-luma-median', 'T1-full-silhouette']
            for statistic in statistics:
                cell = base(native['profile'], renderer, native['scene'], statistic,
                    'supplied path >=8 CSS px inward; central8 is an independent 8x8 CSS px square; '
                    'far24 excludes within24 CSS px of impulse dots', native['role'])
                cell.update(nativeEvidence=None, currentEvidence=None,
                    nativeIdentity=native['id'], referenceIdentity=native['reference'],
                    missing=['Admitted role-isolated W50 archive and measured repeat bar',
                             'Own pre-fit current web render; no blind statistics before exposure'])
                cells.append(cell)
    cells.sort(key=lambda c: tuple(c[k] for k in ('profile', 'renderer', 'scene', 'statistic')))
    keys = [tuple(c[k] for k in ('profile', 'renderer', 'scene', 'statistic')) for c in cells]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate reference identity')
    return {'schema': 'w50-reference-inventory-1', 'stage': 'prospective-before-native',
        'inputs': {'historicalRegistry': pin(previous_path), 'bed': pin(HERE / 'bed/manifest.json'),
                   'currentScratchControls': pin(controls_path), 'currentCssScratchControls': pin(css_controls_path)},
        'generations': generations, 'cells': cells,
        'missingEvidenceBlocksFit': True,
        'blindPolicy': 'Identity and dependency hashes only until frozen single exposure; no hidden statistics',
        'completion': 'A separate pre-fit seal retains exact identities, generations, roles and known caps; '
                      'blind statistics remain unavailable until exposure, not a fit prerequisite'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = build()
    path = HERE / 'references.json'
    if args.check:
        if json.loads(path.read_text()) != result:
            raise SystemExit('Reference inventory differs from recomputation')
    else:
        if (HERE / 'declaration.sha256').exists():
            raise SystemExit('Operational seal exists; reference inventory is immutable')
        path.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'cells': len(result['cells']), 'measured': sum(c['status']=='MEASURED' for c in result['cells']),
                      'fitReady': False}))
