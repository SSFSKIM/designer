"""Write chosen-light.json / chosen-dark.json for the confirmation: the branch's documents with
the fingerprint stripped and the chosen ramp constants applied (the dark difference document
does not name them, so the eight are added to its copy)."""
import json, sys
far1x = float(sys.argv[1]); out = sys.argv[2]
P = '/Users/new/Developer/GitHub/designer/.claude/worktrees/w13-g1/packages/calibration/profiles/'
ramp = dict(sizeScatterRampStartThin1x=0.72, sizeScatterRampStartThick1x=0.52, sizeScatterRampStartFar1x=far1x,
            sizeScatterRampStartThin2x=0.46, sizeScatterRampStartThick2x=0.17, sizeScatterRampStartFar2x=0.15,
            sizeScatterRampReach1xPx=80, sizeScatterRampReach2xPx=100)
for name in ('light', 'dark'):
    d = json.load(open(f'{P}apple-macos-26.5-1x-{name}-standard.json'))
    keep = {k: d[k] for k in ('$comment', 'patch', 'cssTierMapping') if k in d}
    keep['patch'] = {**keep['patch'], **ramp}
    keep['$comment'] = f"W13 G1 sweep-4 confirmation document ({name}): the branch's profile with the fingerprint stripped and the chosen ramp constants applied; far1x {far1x}."
    json.dump(keep, open(f'{out}/chosen-{name}.json', 'w'), indent=2)
    print(name, 'written; patch ramp:', {k: keep['patch'][k] for k in ramp})
