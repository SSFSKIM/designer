"""Declare W28 G0's population using JSON metadata only, before any pixel read."""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def load(path):
    return json.loads((ROOT / path).read_text())


def declaration():
    canonical = 'apps/reference-apple/fixtures/manifest.json'
    w9dir = 'packages/calibration/results/2026-09-02-w9-probe'
    checking = load('packages/calibration/results/2026-09-11-w27c-g1b/checking-bed.json')
    denied = next(g['scenes'] for g in checking['groups'] if g['id'] == 'D')
    denied_bases = {s.rsplit('__', 1)[0] for s in denied}
    rows, excluded = [], []
    sources = [
        ('canonical', canonical, 'apps/reference-apple/scenes.json', 'apps/reference-apple/fixtures'),
        ('w9', w9dir + '/last-run-manifest.json', 'apps/reference-apple/scenes-w9-probe.json', w9dir),
    ]
    for bed, manifest_path, spec_path, fixtures in sources:
        manifest, spec = load(manifest_path), load(spec_path)
        scene_map = {s['id']: s for s in spec['scenes']}
        for profile in manifest['profiles']:
            for fixture in profile['fixtures']:
                scene = scene_map[fixture['sceneId']]
                base = scene['id'].rsplit('__', 1)[0]
                reason = ('group D geometry/background on either pose' if base in denied_bases
                          else 'uniform background; check only' if spec['backgrounds'][scene['background']]['kind'] == 'solid'
                          else None)
                if reason:
                    excluded.append(dict(bed=bed, profile=profile['profileKey'], scene=scene['id'], reason=reason))
                    continue
                scale = 2 if '-2x-' in profile['profileKey'] else 1
                bgkey = f"{scene['background']}@{scale}x"
                # W9's backgrounds were not copied into the evidence directory. Its manifest
                # keys the same raster names as the canonical manifest. Assert declaration
                # equality before borrowing that committed raster; no pixel read here.
                if bed == 'w9':
                    can_spec, can_man = load('apps/reference-apple/scenes.json'), load(canonical)
                    assert manifest['backgrounds'][bgkey] == can_man['backgrounds'][bgkey]
                    def content(d): return {k:v for k,v in d.items() if not k.startswith('$')}
                    assert content(spec['backgrounds'][scene['background']]) == content(can_spec['backgrounds'][scene['background']])
                pose = 'inactive' if scene['state'] == 'inactive' else 'active'
                rows.append(dict(
                    id=f"{bed}/{profile['profileKey']}/{scene['id']}", bed=bed,
                    scene=scene['id'], pose=pose, profile=profile['profileKey'],
                    scheme=profile['colorScheme'], policy=profile['a11yMode'], scale=scale,
                    admissibleReason='structured committed native cell; background/component base is outside group D on both poses; no outcome-based filtering',
                    sceneSpec=spec_path, manifest=manifest_path,
                    fixture=f"{fixtures}/{fixture['file']}",
                    background=f"apps/reference-apple/fixtures/{manifest['backgrounds'][bgkey]}",
                    backgroundKey=bgkey, fixtureSet=fixture['fixtureSet'],
                    provenance='recovered single-run inactive' if 'recoveredProvenance' in fixture else 'manifest-attested active' if bed == 'canonical' else 'W9 seven-run majority-state (provenance.json)',
                ))
    rows.sort(key=lambda x:x['id'])
    return dict(
        gate='W28 G0 / claims §5.144', declaredBeforePixelRead=True,
        checkingAuthority='packages/calibration/results/2026-09-11-w27c-g1b/checking-bed.json',
        deniedInactiveIds=denied, exclusionRule='Compare background/component base, stripping the final state suffix, on BOTH poses (including tint/interaction variants). No D native image is opened.',
        populationRule='Every structured manifest entry in canonical six profiles plus W9, retaining tinted, pressed, groups and stacks with explicit confound flags in the reading. Historical duplicate observations stay separate and equally weighted; clean single-surface standard-policy rows are a sensitivity, not a replacement population.',
        statistics=dict(ladderFractions=[0,1/32,1/16,1/8,1/4,1/2,1],
            scaleUnits='fraction of declared minimum constituent short-side span in CSS px; group/stack rows flagged as composite',
            erosionCssPx=6, thickness='smoothstep(32,96,span); <1 thin (intermediate flagged), 1 thick',
            isotonic='equal cell weights; pool equal x to 12 decimal places before PAVA; monotone non-decreasing, in-sample RMS; group by scheme × pose × thickness, also report policy-separated and clean sensitivity',
            gaussian='encoded Rec.709 luma; separable discrete normalized Gaussian, truncate 4 sigma, edge-clamped; sigma 0 identity',
            selection='One family and scale must beat each row runner-up by >0.004 linear Y and serve both schemes. Identical predictors at zero scale are equivalent, not independent competitors. Otherwise not identifiable.',
            ordinate='mean of per-pixel LINEAR Rec.709 Y over componentRegion union eroded 6 CSS px'),
        counts=dict(total=len(rows),byBedPose=dict(Counter(r['bed']+'/'+r['pose'] for r in rows))),
        rows=rows, excluded=excluded)

if __name__ == '__main__':
    result=declaration()
    (HERE/'population.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['counts']))
