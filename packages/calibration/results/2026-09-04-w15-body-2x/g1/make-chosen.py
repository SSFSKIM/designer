"""Write chosen-light.json / chosen-dark.json for the confirmation run: the G1 branch's profile
documents with the fingerprint stripped and the chosen second-scale constants applied to BOTH
patches (the dark difference document does not name the size law, so the keys are added to its
copy; at dpr 1 every one of them is inert by construction).

    python3 make-chosen.py <chosen.json> <out dir>

`chosen.json` is a flat object of the 2x keys and their values, e.g.
{"sizeScatterGainMax2x": 5.6, "sizeScatterFloor2x": 0.7, "sizeScatterSpanMax2x": 256,
 "sizeScatterRampStartThin2x": 0.46, "sizeScatterRampStartThick2x": 0.17,
 "sizeScatterRampStartFar2x": 0.15, "sizeScatterRampReach2xPx": 100}
"""
import json, sys
chosen = json.load(open(sys.argv[1])); out = sys.argv[2]
KEYS = ("sizeScatterGainMax2x", "sizeScatterFloor2x", "sizeScatterSpanMax2x",
        "sizeScatterRampStartThin2x", "sizeScatterRampStartThick2x",
        "sizeScatterRampStartFar2x", "sizeScatterRampReach2xPx")
unknown = set(chosen) - set(KEYS)
if unknown:
    sys.exit(f"not a second-scale key: {sorted(unknown)}")
P = '/Users/new/Developer/GitHub/designer/.claude/worktrees/w15-g1/packages/calibration/profiles/'
for name in ('light', 'dark'):
    d = json.load(open(f'{P}apple-macos-26.5-1x-{name}-standard.json'))
    keep = {k: d[k] for k in ('$comment', 'patch', 'cssTierMapping') if k in d}
    keep['patch'] = {**keep['patch'], **chosen}
    keep['$comment'] = (f"W15 G1 confirmation document ({name}): the branch's profile with the fingerprint "
                        f"stripped and the chosen second-scale constants applied; {chosen}.")
    json.dump(keep, open(f'{out}/chosen-{name}.json', 'w'), indent=2)
    print(name, 'written; 2x keys in patch:', {k: keep['patch'].get(k) for k in KEYS})
